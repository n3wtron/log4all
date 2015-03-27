package models

import (
	"gopkg.in/mgo.v2"
	"time"
)

type Log struct {
	Application string                 `json:"application" bson:"application"`
	Level       string                 `json:"level" bson:"level"`
	Message     string                 `json:"message" bson:"message"`
	Stack       string                 `json:"-" bson:"-"`
	Date        time.Time              `json:"date" bson:"date"`
	Tags        map[string]interface{} `json:"tags" bson:"tags"`
	StackSha    string                 `json:"stack_sha" bson:"stack_sha"`
}

func CreateTailTable(db *mgo.Database) error {
	collections, err := db.CollectionNames()
	if err != nil {
		return err
	}

	for c := range collections {
		if collections[c] == "tail_logs" {
			return nil
		}
	}

	tailInfo := mgo.CollectionInfo{
		DisableIdIndex: false,
		ForceIdIndex:   false,
		Capped:         true,
		MaxBytes:       256 * 1024 * 1024,
		MaxDocs:        10000,
	}
	return db.C("tail_logs").Create(&tailInfo)
}

func (this *Log) Save(db *mgo.Database) error {
	//insert on tail_logs
	db.C("tail_logs").Insert(this)
	return db.C("logs").Insert(this)
}

func SearchLog(db *mgo.Database, query map[string]interface{}, sortField string, sortAscending bool, page int, maxResult int) ([]Log, error) {
	var sort string
	if !sortAscending {
		sort = "-" + sortField
	} else {
		sort = sortField
	}
	if sort == "" || sort == "-" {
		sort = "-date"
	}
	var queryResult []Log
	err := db.C("logs").Find(query).Sort(sort).Skip(page * maxResult).Limit(maxResult).All(&queryResult)
	return queryResult, err
}
