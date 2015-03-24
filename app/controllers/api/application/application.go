package application

import (
	"github.com/revel/revel"
//	"io/ioutil"
	"log4all/app/models"
	"log4all/app/controllers"
)

type ApplicationApi struct{
	controllers.AuthenticatedController
}


func init(){
}

func (ctrl *ApplicationApi) List() revel.Result{
	result := make (map[string]interface{})
	applications,err := models.GetApplications(ctrl.Db)
	if err != nil{
		revel.ERROR.Println(err)
		result["success"] = false
		result["message"] = err.Error()
	}else{
		result["success"] = true
		result["result"] = applications
	}
	return ctrl.RenderJson(result)
}