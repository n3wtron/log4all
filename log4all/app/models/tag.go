package models

import (
	"gopkg.in/mgo.v2"
	"gopkg.in/mgo.v2/bson"
)

type Tag struct {
	Name string `json:"name" bson:"name"`
}

func (this *Tag) Save(db *mgo.Database) error {
	return db.C("tags").Insert(this)
}

func CreateTagIndexes(db *mgo.Database) error {
	index := mgo.Index{
		Key:        []string{"name"},
		Unique:     true,
		DropDups:   true,
		Background: true,
	}
	return db.C("tags").EnsureIndex(index)
}

func GetTags(db *mgo.Database) ([]Tag, error) {
	var result []Tag
	err := db.C("tags").Find(bson.M{}).All(&result)
	return result, err
}
