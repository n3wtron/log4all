package models

import "gopkg.in/mgo.v2"

type BasicModel interface{
	Save(db *mgo.Database) error
	Update(db *mgo.Database, id string) error
}