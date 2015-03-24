package models

import (
	"gopkg.in/mgo.v2"
	"gopkg.in/mgo.v2/bson"
)


type LevelConfiguration struct{
	ArchiveDays		int		`json:"archive"`
	DeleteDays		int		`json:"delete"`
}

type ApplicationConfiguration struct{
	Debug	LevelConfiguration	`json:"debug"`
	Info	LevelConfiguration	`json:"info"`
	Warning	LevelConfiguration	`json:"warning"`
	Error	LevelConfiguration	`json:"error"`
}

type Application struct{
	Name 			string 						`json:"name"`
	Description 	string						`json:"description"`
	Token			string						`json:"token"`
	Configuration	ApplicationConfiguration	`json:"configuration"`
}

func CreateApplicationIndexes(db *mgo.Database) error{
	index := mgo.Index{
		Key: []string{"name"},
		Unique: true,
		DropDups: true,
		Background: true,
	}
	return db.C("applications").EnsureIndex(index)
}

func (this *Application) Save(db *mgo.Database){
	db.C("applications").Insert(this)
}

func GetApplications(db *mgo.Database) ([]Application,error){
	var result []Application
	err := db.C("applications").Find(bson.M{}).All(&result)
	return result,err
}

func GetApplicationByName(db* mgo.Database,name string)(*Application,error){
	result := new(Application)
	err := db.C("applications").Find(bson.M{"name":name}).One(&result)
	return result,err
}

func GetApplicationByToken(db* mgo.Database,name string, token string)(*Application,error){
	result := new(Application)
	err := db.C("applications").Find(bson.M{"name":name,"token":token}).One(&result)
	return result,err
}