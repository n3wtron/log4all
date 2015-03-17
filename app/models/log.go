package models

import (
	"encoding/json"
	"log"
	"regexp"
	"time"
	"strings"
	"gopkg.in/mgo.v2"
	//"gopkg.in/mgo.v2/bson"
)

var tagNameRegexp = "[\\+]{0,1}[\\w|.|-]+"
var tagRegexp = "(#" + tagNameRegexp + ")"
var srcTagRegexp = "([#]{0,1}" + tagNameRegexp + ")"

var valueRegexp = "([a-z|A-Z|0-9|,|.|:|;|_|\\-]+|\"[a-z|A-Z|0-9|,|_|.|\\-|:|;| ]+\")"

var addLogRegexp = tagRegexp + "((:)" + valueRegexp + ")?"

var addLogMatcher = regexp.MustCompile(addLogRegexp)

type RawLog struct{
	Application string
	Level       string
	Message     string
	Stack       string
	Date		int64
}

type Log struct {
	RawLog		
	Tags        map[string]interface{}
	DtInsert  time.Time
	StackSha	string `json:stack_sha`
}

func UnmarshalLog(jsonData []byte) *Log {
	rawLog := new(RawLog)
	log.Printf("%v",rawLog)
	json.Unmarshal(jsonData, rawLog)
	logResult := new(Log)
	logResult.Tags = make(map[string]interface{})
	logResult.Level = rawLog.Level
	logResult.Application = rawLog.Application
	logResult.Stack = rawLog.Stack
	//add dtInsert if is missing
	if rawLog.Date != 0 {
		logResult.DtInsert = time.Unix(rawLog.Date,0)
	}else{
		logResult.DtInsert = time.Now()
	}
	//extract tags from message
	rawTags := addLogMatcher.FindAllStringSubmatch(rawLog.Message, -1)
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
	logResult.Message = addLogMatcher.ReplaceAllString(logResult.Message, "")
	log.Printf("%v",logResult)
	
	return logResult
}

func (this *Log) ToJson() map[string]interface{}{
	result := make(map[string]interface{})
	result["application"] = this.Application
	result["level"] = this.Level
	result["message"] = this.Message
	result["tags"] = this.Tags
	result["_dt_insert"] = this.DtInsert
	result["stack_sha"] = this.StackSha
	return result
}

func (this *Log) Save(db *mgo.Database) error{
	err := db.C("logs").Insert(this.ToJson())
	return err
}