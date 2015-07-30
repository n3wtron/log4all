package log

import (
	"encoding/json"
	"github.com/n3wtron/log4all/commons"
	"github.com/n3wtron/log4all/log4all/app/models"
	"github.com/n3wtron/log4all/log4all/app/utils"
	"github.com/revel/revel"
	"io/ioutil"
	"strings"
	"time"
)

func parseQuery(query string, mongoDbQuery map[string]interface{}) {
	srcs := utils.SearchLogMatcher().FindAllStringSubmatch(query, -1)
	//var tagName string
	for i := 0; i < len(srcs); i++ {
		filter := srcs[i]
		tagName := filter[1][1:]
		if len(filter[4]) == 0 {
			// no value
			mongoDbQuery["tags."+tagName] = map[string]bool{"$exists": true}
		} else {
			// with value
			operator := filter[3]
			value := filter[4]
			switch operator {
			case "=":
				mongoDbQuery["tags."+tagName] = value
			case "?=":
				mongoDbQuery["tags."+tagName] = map[string]string{"$regex": value}
			case "!=":
				mongoDbQuery["tags."+tagName] = map[string]string{"$ne": value}
			case "<":
				mongoDbQuery["tags."+tagName] = map[string]string{"$lt": value}
			case ">":
				mongoDbQuery["tags."+tagName] = map[string]string{"$gt": value}
			case "<=":
				mongoDbQuery["tags."+tagName] = map[string]string{"$lte": value}
			case ">=":
				mongoDbQuery["tags."+tagName] = map[string]string{"$gte": value}
			case "<<":
				mongoDbQuery["tags."+tagName] = map[string]([]string){"$in": strings.Split(value, ",")}
			case "!<":
				mongoDbQuery["tags."+tagName] = map[string]map[string]([]string){"$not": {"$in": strings.Split(value, ",")}}
			}
		}
	}
}

func getQuery(srcParams *commons.LogSearchParam, tail bool) map[string]interface{} {
	// date conversion
	revel.TRACE.Printf("orig:%v", srcParams)
	dtSince := time.Unix(srcParams.DtSince/1000, 0)
	dtTo := time.Unix(srcParams.DtTo/1000, 0)
	var query map[string]interface{}
	if tail {
		query = map[string]interface{}{
			"_dt_insert": map[string]time.Time{
				"$gte": dtSince,
				"$lte": dtTo,
			},
		}
	} else {
		query = map[string]interface{}{
			"date": map[string]time.Time{
				"$gte": dtSince,
				"$lte": dtTo,
			},
		}
	}
	if len(srcParams.Applications) > 0 {
		query["application"] = map[string]([]string){
			"$in": srcParams.Applications,
		}
	}
	if len(srcParams.Levels) > 0 {
		query["level"] = map[string]([]string){
			"$in": srcParams.Levels,
		}
	}
	parseQuery(srcParams.Query, query)
	return query
}

func (ctrl ApiSearchLog) SearchOptions() revel.Result {
	ctrl.Response.Out.Header().Add("Access-Control-Allow-Methods", "POST")
	ctrl.Response.Out.Header().Add("Access-Control-Allow-Headers", "Content-Type")

	return ctrl.RenderText("")
}

func (ctrl ApiSearchLog) Search(tail bool) revel.Result {
	result := new(commons.SearchResponse)
	byteBody, _ := ioutil.ReadAll(ctrl.Request.Body)
	revel.INFO.Printf("SrcParams:%s", byteBody)
	srcParams := new(commons.LogSearchParam)
	err := json.Unmarshal(byteBody, srcParams)
	var logs []models.Log
	if err == nil {
		query := getQuery(srcParams, tail)
		revel.INFO.Printf("query:%v", query)
		logs, err = models.SearchLog(ctrl.Db, tail, query, srcParams.SortField, srcParams.SortAscending, srcParams.Page, srcParams.MaxResult)
	}

	result.Success = err == nil
	if err != nil {
		revel.ERROR.Printf("ApiLog.Search Error:%v", err)
		result.Message = err.Error()
	} else {
		result.Result = make([]commons.DbLog, len(logs))
		for i, dbLog := range logs {
			result.Result[i] = dbLog.DbLog
		}
	}
	return ctrl.RenderJson(result)
}
