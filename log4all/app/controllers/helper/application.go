package helper

import (
	"github.com/n3wtron/log4all/log4all/app/controllers"
	"github.com/n3wtron/log4all/log4all/app/models"
	"github.com/revel/revel"
	"strings"
)

type ApplicationHelper struct {
	controllers.DbController
}

/*
helper function for angucompleta-alt
*/
func (ctrl *ApplicationHelper) Autocomplete(currText string) revel.Result {
	var resultApplications []interface{}

	currentApps := strings.Split(currText, " ")
	prefixApp := strings.Join(currentApps[:len(currentApps)-1], " ")
	if prefixApp != "" {
		prefixApp = prefixApp + " "
	}

	query := make(map[string]interface{})
	query["$and"] = []map[string]interface{}{
		map[string]interface{}{
			"name": map[string]interface{}{
				"$regex": currentApps[len(currentApps)-1],
			},
		}, map[string]interface{}{
			"name": map[string]interface{}{
				"$not": map[string]interface{}{
					"$in": currentApps[:len(currentApps)-1],
				},
			},
		},
	}

	applications, err := models.FindApplications(ctrl.Db, query)
	if err == nil {
		for a := range applications {
			appNames := prefixApp + applications[a].Name
			resultApplications = append(resultApplications, map[string]interface{}{"name": appNames, "description": applications[a].Description})
		}
	} else {
		revel.ERROR.Printf("ApplicationHelper.Autocomplete Error:%v", err)
	}
	result := map[string]interface{}{"results": resultApplications}
	return ctrl.RenderJson(result)
}
