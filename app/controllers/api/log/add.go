package log

import (
	"encoding/json"
	"errors"
	"github.com/revel/revel"
	"gopkg.in/mgo.v2"
	"io/ioutil"
	"log"
	"log4all/app/models"
	"log4all/app/utils"
	"strings"
	"time"
)

type RawLog struct {
	Application      string `json:"application"`
	ApplicationToken string `json:"application_token"`
	Level            string
	Message          string
	Stack            string
	Date             int64
}

type MultiLog struct {
	Application      string `json:"application"`
	ApplicationToken string `json:"application_token"`
	Logs             []RawLog
}

/*
	Convert a RawLog to models.Log
*/
func NewLogFromRawLog(rawLog *RawLog) *models.Log {
	logResult := new(models.Log)
	logResult.Tags = make(map[string]interface{})
	logResult.Level = rawLog.Level
	logResult.Application = rawLog.Application
	logResult.Stack = rawLog.Stack
	//add dtInsert if is missing
	if rawLog.Date != 0 {
		logResult.Date = time.Unix(rawLog.Date/1000, 0)
	} else {
		logResult.Date = time.Now()
	}
	//extract tags from message
	rawTags := utils.AddLogMatcher().FindAllStringSubmatch(rawLog.Message, -1)
	for i := 0; i < len(rawTags); i++ {
		tagName := rawTags[i][1][1:]
		if len(rawTags[i][4]) > 0 {
			tagValue := rawTags[i][4]
			logResult.Tags[tagName] = strings.Replace(tagValue, "\"", "", -1)
		} else {
			logResult.Tags[tagName] = true
		}
	}

	//arrange message
	logResult.Message = strings.Replace(rawLog.Message, "##", "", -1)
	logResult.Message = utils.AddLogMatcher().ReplaceAllString(logResult.Message, "")

	return logResult
}

func addTags(db *mgo.Database, logToAdd *models.Log) {
	//add tags
	for tag := range logToAdd.Tags {
		dbTag := &models.Tag{Name: tag}
		if err := dbTag.Save(db); err != nil && !mgo.IsDup(err) {
			log.Println("Error inserting tag " + tag + " error:" + err.Error())
		}
	}
}

func (ctrl ApiLog) dbAdd(logToAdd *models.Log) error {
	// add stack
	if logToAdd.Stack != "" {
		stack := &models.Stack{Stacktrace: logToAdd.Stack}
		stack.Save(ctrl.Db)
		logToAdd.StackSha = stack.Sha
	}

	//add Log
	err := logToAdd.Save(ctrl.Db)
	if err != nil {
		return errors.New("Cannot insert log")
	} else {
		go addTags(ctrl.Db, logToAdd)
		return nil
	}
}

// add a single log
func (ctrl ApiLog) CheckApplication(applicationName string, applicationToken string) error {
	//search application
	var err error
	if applicationToken != "" {
		_, err = models.GetApplicationByToken(ctrl.Db, applicationName, applicationToken)
	} else {
		_, err = models.GetApplicationByName(ctrl.Db, applicationName)
	}
	if err != nil {
		if err == mgo.ErrNotFound {
			return errors.New("No Application found:" + applicationName + " with token:" + applicationToken)
		} else {
			return err
		}
	}
	return nil
}

// API: add single log
func (ctrl ApiLog) AddLog() revel.Result {
	revel.INFO.Println("addLog")
	result := make(map[string]interface{})
	byteBody, _ := ioutil.ReadAll(ctrl.Request.Body)
	rawLog := new(RawLog)
	json.Unmarshal(byteBody, rawLog)
	var logToAdd *models.Log
	var err error
	err = ctrl.CheckApplication(rawLog.Application, rawLog.ApplicationToken)
	if err != nil {
		goto addLogFinish
	}

	logToAdd = NewLogFromRawLog(rawLog)
	err = ctrl.dbAdd(logToAdd)

addLogFinish:
	if err != nil {
		result["success"] = false
		result["message"] = err.Error()
	} else {
		result["success"] = true
	}
	revel.INFO.Printf("addLog:%v", result)
	return ctrl.RenderJson(result)
}

// API: add multiple log
func (ctrl ApiLog) AddLogs() revel.Result {

	result := make(map[string]interface{})
	byteBody, _ := ioutil.ReadAll(ctrl.Request.Body)
	logs := new(MultiLog)
	json.Unmarshal(byteBody, logs)

	err := ctrl.CheckApplication(logs.Application, logs.ApplicationToken)

	if err != nil {
		result["success"] = false
		result["message"] = err.Error()
		return ctrl.RenderJson(result)
	}

	allAdded := true
	addErrors := make([]error, 0, len(logs.Logs))
	for i := 0; i < len(logs.Logs); i++ {
		logs.Logs[i].Application = logs.Application
		logs.Logs[i].ApplicationToken = logs.ApplicationToken
		logToAdd := NewLogFromRawLog(&logs.Logs[i])

		addError := ctrl.dbAdd(logToAdd)
		if addError != nil {
			addErrors = append(addErrors, addError)
			allAdded = false
		}
	}
	result["success"] = allAdded
	if !allAdded {
		var strError string
		for i := range addErrors {
			strError += addErrors[i].Error() + " "
		}
		result["message"] = strError
	}

	return ctrl.RenderJson(result)
}
