package api

import (
	"github.com/revel/revel"
	"log4all/app/controllers"
	"log4all/app/models"
)

type StackApi struct {
	controllers.DbController
}

func (ctrl *StackApi) Get(sha string) revel.Result {
	revel.INFO.Printf("get stack with sha:%s", sha)
	result := make(map[string]interface{})
	stack, err := models.GetStackBySha(ctrl.Db, sha)
	result["success"] = err == nil
	if err != nil {
		revel.ERROR.Println(err.Error())
		result["message"] = err.Error()
	} else {
		result["result"] = stack
	}
	return ctrl.RenderJson(result)
}
