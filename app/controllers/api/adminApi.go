package api

import (
	"encoding/json"
	"github.com/revel/revel"
	"io/ioutil"
	"log4all/app/controllers"
	"log4all/app/models"
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
	case "group":
		modelObj = new(models.Group)
	case "user":
		modelObj = new(models.User)
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
	case "group":
		modelObj = new(models.Group)
	case "user":
		modelObj = new(models.User)
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
		app, err := models.DeleteApplication(ctrl.Db, id)
		if err == nil {
			err = models.DeleteLogsByApplication(ctrl.Db, app.Name)
		}
	case "group":
		err = models.DeleteGroup(ctrl.Db, id)
	case "user":
		err = models.DeleteUser(ctrl.Db, id)
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
	case "group":
		modelObjs, err = models.GetGroups(ctrl.Db)
	case "user":
		modelObjs, err = models.GetUsers(ctrl.Db)
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
	case "group":
		modelObj, err = models.GetGroupById(ctrl.Db, id)
	case "user":
		modelObj, err = models.GetUserById(ctrl.Db, id)
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
