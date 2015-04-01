package api

import (
	"github.com/revel/revel"
	"log4all/app/controllers"
	"log4all/app/models"
)

type TagApi struct {
	controllers.DbController
}

func (ctrl *TagApi) List() revel.Result {
	result := make(map[string]interface{})
	tags, err := models.GetTags(ctrl.Db)
	result["success"] = err == nil
	if err != nil {
		result["message"] = err.Error()
	} else {
		result["result"] = tags
	}
	return ctrl.RenderJson(result)
}
