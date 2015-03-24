package models

import (
	
//	"log"
	"time"
	
	"gopkg.in/mgo.v2"
	
	//"gopkg.in/mgo.v2/bson"
)


type Log struct {
	Application string `bson:"application"`
	Level       string `bson:"level"`
	Message     string `bson:"message"`
	Stack       string `json:"-" bson:"-"`
	Date		time.Time `bson:"date"`
	Tags        map[string]interface{} `bson:"tags"`
	StackSha	string `json:"stack_sha"`
}

func (this *Log) Save(db *mgo.Database) error{
	err := db.C("logs").Insert(this)
	return err
}



func SearchLog(db *mgo.Database,query map[string]interface{}, sortField string, sortAscending bool, page int, maxResult int) ([]Log,error) {
	var sort string
	if !sortAscending{
		sort = "-" + sortField
	}else{
		sort = sortField
	}
	if sort == "" || sort == "-"{
		sort = "-date"
	}
	var queryResult []Log
	err := db.C("logs").Find(query).Sort(sort).Skip(page*maxResult).Limit(maxResult).All(&queryResult)
	return queryResult,err
}