package controllers

import (
	"github.com/revel/revel"
	"gopkg.in/mgo.v2"
	"log"
)

type DbController struct {
	*revel.Controller
	Db *mgo.Database
}

var mongoDb *mgo.Database

func InitDB() {
	mongoSession, err := mgo.Dial("localhost")
	if err != nil {
		log.Fatal("Error Initializing DB")
		panic(err)
	}
	mongoDb = mongoSession.DB("log4all")
	log.Printf("Db initialized")
	
	
}

func (c *DbController) Begin() revel.Result {
	c.Db = mongoDb
	return nil
}

func init() {
	revel.OnAppStart(InitDB)
	revel.InterceptMethod((*DbController).Begin, revel.BEFORE)
}
