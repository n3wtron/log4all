package controllers

import (
	"github.com/revel/revel"
	"io/ioutil"
	"log"
	"log4all/app/models"
)

type ApiLog struct {
	DbController
}

func (c ApiLog) Add() revel.Result {
	result := make(map[string]interface{})
	byteBody, _ := ioutil.ReadAll(c.Request.Body)
	log.Printf("%s",byteBody)
	logToAdd := models.UnmarshalLog(byteBody)
	// add stack
	if logToAdd.Stack != ""{
		stack := &models.Stack{Stacktrace:logToAdd.Stack}
		stack.Save(c.Db)
		logToAdd.StackSha = stack.Sha
	}
	
	err := logToAdd.Save(c.Db)
	if err != nil {
		result["success"] = false
	} else {
		
		result["success"] = true
	}
	
	
	
	return c.RenderJson(result)
}

