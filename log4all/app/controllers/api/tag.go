package api

import (
	"github.com/n3wtron/log4all/log4all/app/controllers"
	"github.com/n3wtron/log4all/log4all/app/models"
	"github.com/revel/revel"
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
