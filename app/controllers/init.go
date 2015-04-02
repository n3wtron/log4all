package controllers

import (
	"errors"
	"github.com/revel/revel"
	"gopkg.in/mgo.v2"
	"log"
	"log4all/app/models"
	"os"
)

type DbController struct {
	*revel.Controller
	Db *mgo.Database
}

var mongoDb *mgo.Database

func InitDB() {
	var err error
	var mongoSession *mgo.Session
	var collections []string
	var userCollectionFound bool
	var c int
	dbConnectionUrl, found := revel.Config.String("db.connectionUrl")
	if !found {
		dbConnectionUrl = os.Getenv("L4AL_DB_CONNECTION")
	}
	if dbConnectionUrl == "" {
		err = errors.New("No MongoDB connection Url found on config file (db.ConnectionUrl) or in the L4AL_DB_CONNECTION env variable")
		goto finish
	}
	mongoSession, err = mgo.Dial(dbConnectionUrl)
	if err != nil {
		goto finish
	}
	mongoDb = mongoSession.DB("")

	//check if users table exists
	collections, err = mongoDb.CollectionNames()
	userCollectionFound = false

	if err != nil {
		goto finish
	}
	for c = range collections {
		if collections[c] == "users" {
			userCollectionFound = true
			break
		}
	}
	//add default admin user
	if !userCollectionFound {
		u := new(models.User)
		u.Name = "Admin User"
		u.Email = "admin"
		u.Password = "admin"
		u.Save(mongoDb)
		revel.INFO.Println("default admin user created with password admin")
	}

	err = models.CreateTailTable(mongoDb)
	if err != nil {
		goto finish
	}
	models.CreateTagIndexes(mongoDb)
	models.CreateStackIndexes(mongoDb)
	models.CreateApplicationIndexes(mongoDb)
	models.CreateGroupIndexes(mongoDb)
	models.CreateUserIndexes(mongoDb)

finish:
	if err != nil {
		revel.ERROR.Println("Error Initializing DB")
		revel.ERROR.Panic(err)
	} else {
		log.Printf("Db initialized")
	}
}

func (c *DbController) Begin() revel.Result {
	c.Db = mongoDb
	return nil
}

func init() {
	revel.OnAppStart(InitDB)
	revel.InterceptMethod((*DbController).Begin, revel.BEFORE)
}
