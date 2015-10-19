package api

import (
	"encoding/json"
	"github.com/n3wtron/log4all/log4all/app/controllers"
	"github.com/n3wtron/log4all/log4all/app/models"
	"github.com/revel/revel"
	"io/ioutil"
)

type AdminApi struct {
	controllers.AuthenticatedController
}

func init() {
}

func (ctrl *AdminApi) Add(modelType string) revel.Result {
	result := make(map[string]interface{})
	byteBody, _ := ioutil.ReadAll(ctrl.Request.Body)

	var modelObj interface{}
	switch modelType {
	case "application":
		modelObj = new(models.Application)
	}
	err := json.Unmarshal(byteBody, &modelObj)
	if err != nil {
		goto finish
	}
	err = modelObj.(models.BasicModel).Save(ctrl.Db)

finish:
	result["success"] = err == nil
	if err != nil {
		revel.ERROR.Printf("%v", err)
		result["message"] = err.Error()
	} else {
		result["result"] = modelObj
	}
	return ctrl.RenderJson(result)
}

func (ctrl *AdminApi) Update(modelType string, id string) revel.Result {
	result := make(map[string]interface{})
	byteBody, _ := ioutil.ReadAll(ctrl.Request.Body)
	var modelObj interface{}
	switch modelType {
	case "application":
		modelObj = new(models.Application)
	}

	err := json.Unmarshal(byteBody, &modelObj)
	if err != nil {
		goto finish
	}
	err = modelObj.(models.BasicModel).Update(ctrl.Db, id)

finish:
	result["success"] = err == nil
	if err != nil {
		revel.ERROR.Printf("%v", err)
		result["message"] = err.Error()
	} else {
		result["result"] = modelObj
	}
	return ctrl.RenderJson(result)
}

func (ctrl *AdminApi) Delete(modelType string, id string) revel.Result {
	result := make(map[string]interface{})
	var err error
	switch modelType {
	case "application":
		err = models.DeleteApplication(ctrl.Db, id)
	}
	result["success"] = err == nil
	if err != nil {
		revel.ERROR.Printf("%v", err)
		result["message"] = err.Error()
	}
	return ctrl.RenderJson(result)
}

func (ctrl *AdminApi) List(modelType string) revel.Result {
	result := make(map[string]interface{})

	var modelObjs interface{}
	var err error
	switch modelType {
	case "application":
		modelObjs, err = models.GetApplications(ctrl.Db)
	}
	result["success"] = err == nil
	if err != nil {
		revel.ERROR.Println(err)
		result["message"] = err.Error()
	} else {
		result["result"] = modelObjs
	}
	return ctrl.RenderJson(result)
}

func (ctrl *AdminApi) Get(modelType string, id string) revel.Result {
	result := make(map[string]interface{})

	var modelObj interface{}
	var err error
	switch modelType {
	case "application":
		modelObj, err = models.GetApplicationById(ctrl.Db, id)
	}
	result["success"] = err == nil
	if err != nil {
		revel.ERROR.Printf("%v", err)
		result["message"] = err.Error()
	} else {
		result["result"] = modelObj
	}
	return ctrl.RenderJson(result)
}
