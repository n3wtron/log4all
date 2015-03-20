package models

import (
	"encoding/json"
//	"log"
	"time"
	"strings"
	"gopkg.in/mgo.v2"
	"log4all/app/utils"
	//"gopkg.in/mgo.v2/bson"
)

type RawLog struct{
	Application string `json:"application"`
	Level       string
	Message     string
	Stack       string
	Date		int64
}

type Log struct {
	Application string `bson:"application"`
	Level       string `bson:"level"`
	Message     string `bson:"message"`
	Stack       string `json:"-" bson:"-"`
	Date		time.Time `bson:"date"`
	Tags        map[string]interface{} `bson:"tags"`
	StackSha	string `json:"stack_sha"`
}



func UnmarshalLog(jsonData []byte) *Log {
	rawLog := new(RawLog)
	json.Unmarshal(jsonData, rawLog)
	return NewLogFromRawLog(rawLog)
}

func NewLogFromRawLog(rawLog *RawLog)*Log {
	logResult := new(Log)
	logResult.Tags = make(map[string]interface{})
	logResult.Level = rawLog.Level
	logResult.Application = rawLog.Application
	logResult.Stack = rawLog.Stack
	//add dtInsert if is missing
	if rawLog.Date != 0 {
		logResult.Date = time.Unix(rawLog.Date/1000,0)
	}else{
		logResult.Date = time.Now()
	}
	//extract tags from message
	rawTags := utils.AddLogMatcher().FindAllStringSubmatch(rawLog.Message, -1)
	for i:=0; i<len(rawTags); i++{
		tagName := rawTags[i][1][1:]
		if len(rawTags[i][4])>0{
			tagValue := rawTags[i][4]
			logResult.Tags[tagName]=strings.Replace(tagValue,"\"","",-1)
		}else{
			logResult.Tags[tagName]=true
		}
	}
	
	//arrange message
	logResult.Message = strings.Replace(rawLog.Message,"##","", -1)
	logResult.Message = utils.AddLogMatcher().ReplaceAllString(logResult.Message, "")
	
	return logResult
}

func (this *Log) Save(db *mgo.Database) error{
	err := db.C("logs").Insert(this)
	return err
}



func SearchLog(db *mgo.Database,query map[string]interface{}, sortField string, sortAscending bool, page int, maxResult int) ([]Log,error) {
	var sort string
	if !sortAscending{
		sort = "-" + sortField
	}else{
		sort = sortField
	}
	if sort == "" || sort == "-"{
		sort = "-date"
	}
	var queryResult []Log
	err := db.C("logs").Find(query).Sort(sort).Skip(page*maxResult).Limit(maxResult).All(&queryResult)
	return queryResult,err
}