package log

import (
	"github.com/revel/revel"
	"io/ioutil"
	"log"
	"log4all/app/models"
	"gopkg.in/mgo.v2"
	"errors"
	"encoding/json"
)


type MultiLog struct{
	Application string `json:application`
	ApplicationToken string `json:application_token`
	Logs []models.RawLog
}


func addTags(db *mgo.Database, logToAdd *models.Log){
	//add tags
	for tag := range logToAdd.Tags{
		dbTag := &models.Tag{Name:tag}
		if err := dbTag.Save(db); err != nil && !mgo.IsDup(err){
			log.Println("Error inserting tag "+tag+ " error:"+err.Error())
		}
	}
}

func dbAdd(db *mgo.Database, logToAdd *models.Log) error{
	// add stack
	if logToAdd.Stack != ""{
		stack := &models.Stack{Stacktrace:logToAdd.Stack}
		stack.Save(db)
		logToAdd.StackSha = stack.Sha
	}
	
	//add Log
	err := logToAdd.Save(db)
	if err != nil {
		return errors.New("Cannot insert log")
	} else {
		go addTags(db, logToAdd)
		return nil
	}
}


// API: add single log
func (ctrl ApiLog) AddLog() revel.Result {
	result := make(map[string]interface{})
	byteBody, _ := ioutil.ReadAll(ctrl.Request.Body)
	logToAdd := models.UnmarshalLog(byteBody)
	err := dbAdd(ctrl.Db, logToAdd)
	if err != nil{
		result["success"] = false
		result["message"] = err.Error()
	}else{
		result["success"] = true
	}
	return ctrl.RenderJson(result)
}

// API: add multiple log
func (ctrl ApiLog) AddLogs() revel.Result {
	result := make(map[string]interface{})
	byteBody, _ := ioutil.ReadAll(ctrl.Request.Body)
	logs:=new (MultiLog)
	json.Unmarshal(byteBody,logs)
	
	allAdded := true
	var addError error
	for i:=0;i<len(logs.Logs);i++{
		logToAdd := models.NewLogFromRawLog(&logs.Logs[i])
		logToAdd.Application = logs.Application
		addError := dbAdd(ctrl.Db, logToAdd)
		if addError != nil{
			allAdded = false
		}
	}
	result["success"] = allAdded
	if !allAdded {
		result["message"] = addError.Error()
	}
	
	return ctrl.RenderJson(result)
}


