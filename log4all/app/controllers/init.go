package controllers

import (
	app "github.com/n3wtron/log4all/log4all/app"
	"github.com/revel/revel"
	"gopkg.in/mgo.v2"
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
