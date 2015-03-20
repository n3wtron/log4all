package models

import (
	"gopkg.in/mgo.v2"
)

type Tag struct{
	Name string `json:tag_name`
}


func (this *Tag) ToJson() map[string]interface{}{
	json := make (map[string]interface{})
	json["tag_name"] = this.Name
	return json
}

func (this *Tag) Save(db *mgo.Database) error{
	return db.C("tags").Insert(this.ToJson())
}

func CreateTagIndexes(db *mgo.Database) error{
	index := mgo.Index{
		Key: []string{"tag_name"},
		Unique: true,
		DropDups: true,
		Background: true,
	}
	return db.C("tags").EnsureIndex(index)
}