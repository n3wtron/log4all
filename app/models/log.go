package models

import (
	"errors"
	"github.com/revel/revel"
	"gopkg.in/mgo.v2"
	"strings"
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
	DtInsert    time.Time              `json:"-" bson:"_dt_insert"`
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
	this.DtInsert = time.Now()
	db.C("tail_logs").Insert(this)
	return db.C("logs").Insert(this)
}

func SearchLog(db *mgo.Database, tail bool, query map[string]interface{}, sortField string, sortAscending bool, page int, maxResult int) ([]Log, error) {
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
	var err error
	if !tail {
		err = db.C("logs").Find(query).Sort(sort).Skip(page * maxResult).Limit(maxResult).All(&queryResult)
	} else {
		err = db.C("tail_logs").Find(query).Sort("date").All(&queryResult)
	}
	return queryResult, err
}

func DeleteLog(db *mgo.Database, application string, level string, beforeDays int) error {
	if beforeDays <= 0 {
		return errors.New("delete before days configuration of app " + application + " for level " + level + " has to be >0")
	}
	now := time.Now()
	uxDelLimit := now.Unix() - int64(beforeDays*24*60*60)
	delLimit := time.Unix(uxDelLimit, 0)
	delQuery := map[string]interface{}{
		"application": application,
		"level":       strings.ToUpper(level),
		"date": map[string]interface{}{
			"$lte": delLimit,
		},
	}
	revel.TRACE.Printf("delquery %v", delQuery)
	changeInfo, err := db.C("logs").RemoveAll(delQuery)
	if err == nil {
		revel.INFO.Printf("deleted %d records", changeInfo.Removed)
	}
	return err
}
