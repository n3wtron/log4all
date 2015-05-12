package api

import (
	"github.com/revel/revel"
	"gopkg.in/mgo.v2"
	"log4all/app/controllers"
	"strings"
)

type IndexesApi struct {
	controllers.DbController
}

func (ctrl *IndexesApi) getTagIndexes() ([]string, error) {
	indexes, err := ctrl.Db.C("logs").Indexes()
	resultIndexes := make([]string, 0)
	for i := range indexes {
		if len(indexes[i].Key) == 1 && strings.Contains(indexes[i].Key[0], "tags.") {
			resultIndexes = append(resultIndexes, strings.TrimPrefix(indexes[i].Key[0], "tags."))
		}
	}
	return resultIndexes, err
}

func (ctrl *IndexesApi) List() revel.Result {
	result := make(map[string]interface{})
	var err error
	result["indexes"], err = ctrl.getTagIndexes()
	result["success"] = err == nil
	if err != nil {
		result["message"] = err.Error()
	}
	return ctrl.RenderJson(result)
}

func (ctrl *IndexesApi) Add(indexKey string) revel.Result {
	result := make(map[string]interface{})

	tagIndex := mgo.Index{
		Key:        []string{"tags." + indexKey},
		Unique:     false,
		DropDups:   false,
		Background: true,
		Sparse:     true,
	}
	err := ctrl.Db.C("logs").EnsureIndex(tagIndex)
	result["success"] = err == nil
	result["indexKey"] = tagIndex
	result["indexes"], _ = ctrl.getTagIndexes()
	if err != nil {
		result["message"] = err.Error()
	}
	return ctrl.RenderJson(result)
}

func (ctrl *IndexesApi) Delete(indexKey string) revel.Result {
	result := make(map[string]interface{})
	err := ctrl.Db.C("logs").DropIndex("tags." + indexKey)
	result["success"] = err == nil
	result["indexes"], _ = ctrl.getTagIndexes()
	if err != nil {
		result["message"] = err.Error()
	}
	return ctrl.RenderJson(result)
}
