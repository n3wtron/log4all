package controllers

import (
	"github.com/revel/revel"
	"gopkg.in/mgo.v2"
	app "log4all/app"
)

type DbController struct {
	*revel.Controller
	Db *mgo.Database
}

func (c *DbController) Begin() revel.Result {
	c.Db = app.MongoDb
	return nil
}
func init() {
	revel.InterceptMethod((*DbController).Begin, revel.BEFORE)
}
