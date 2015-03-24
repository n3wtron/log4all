package log

import (
	"github.com/revel/revel"
	"io/ioutil"
	"encoding/json"
	"log4all/app/models"
	"log4all/app/utils"
	"time"
	"strings"
)

type LogSearchParam struct{
	Applications 	string 
	Levels			[]string
	DtSince			int64	`json:"dt_since"`
	DtTo			int64	`json:"dt_to"`
	Query			string
	Page			int
	MaxResult		int		`json:"max_result"`
	SortField		string	`json:"sort_field"`
	SortAscending	bool	`json:"sort_ascending"`
}

func parseQuery(query string, mongoDbQuery map[string]interface{}){
	srcs := utils.SearchLogMatcher().FindAllStringSubmatch(query,-1)
	//var tagName string
	for i:=0; i<len(srcs); i++ {
		filter := srcs[i]
		tagName := filter[1][1:]
		if len(filter[4]) == 0{
			// no value
			mongoDbQuery["tags."+tagName] = map[string]bool {"$exists" : true,}
		}else{
			// with value
			operator := filter[3]
			value := filter[4]
			switch operator{
				case "=":
					mongoDbQuery["tags."+tagName] = value
				case "?=":
					mongoDbQuery["tags."+tagName] = map[string]string {"$regex" : value}
				case "!=":
					mongoDbQuery["tags."+tagName] = map[string]string {"$ne" : value}
				case "<":
					mongoDbQuery["tags."+tagName] = map[string]string {"$lt" : value}
				case ">":
					mongoDbQuery["tags."+tagName] = map[string]string {"$gt" : value}
				case "<=":
					mongoDbQuery["tags."+tagName] = map[string]string {"$lte" : value}
				case ">=":
					mongoDbQuery["tags."+tagName] = map[string]string {"$gte" : value}
				case "<<":
					mongoDbQuery["tags."+tagName] = map[string]([]string) {"$in" : strings.Split(value,",")}
				case "!<":
					mongoDbQuery["tags."+tagName] = map[string]map[string]([]string) {"$not":{"$in" : strings.Split(value,",")}}
			}
		}
	}
}

func getQuery(srcParams *LogSearchParam) map[string]interface{} {
	// date conversion
	revel.TRACE.Printf("orig:%v",srcParams)
	dtSince := time.Unix(srcParams.DtSince,0)
	dtTo := time.Unix(srcParams.DtTo,0)
	applicationLst := strings.Split(srcParams.Applications,",")
	
	query := map[string]interface{}{
		"application" : map[string]([]string){
			"$in" :  applicationLst,
		},
		"date" :map[string]time.Time{
			"$gte" : dtSince,
			"$lte" : dtTo,
		},
	}
	if len(srcParams.Levels) > 0{
		query["level"] = map[string]([]string){
			"$in" : srcParams.Levels,
		}
	}
	parseQuery(srcParams.Query, query)
	revel.TRACE.Printf("%v",query)
	
	return query
}

func (ctrl ApiLog) Search() revel.Result{
	result := make(map[string]interface{})
	byteBody, _ := ioutil.ReadAll(ctrl.Request.Body)
	srcParams := new (LogSearchParam)
	err := json.Unmarshal(byteBody, srcParams)
	var logs []models.Log
	if err == nil{
		logs,err = models.SearchLog(ctrl.Db, getQuery(srcParams),srcParams.SortField, srcParams.SortAscending, srcParams.Page, srcParams.MaxResult)
	}
	
	if err != nil{
		result["success"] = false
		result["message"] = err.Error()
	}else{
		result["success"] = true
		result["result"] = logs
	}
	
	return ctrl.RenderJson(result)
}