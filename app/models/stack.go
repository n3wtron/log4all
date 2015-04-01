package models

import (
	"crypto/sha1"
	"encoding/hex"
	"gopkg.in/mgo.v2"
	"gopkg.in/mgo.v2/bson"
	"io"
)

type Stack struct {
	Stacktrace string `json:"stacktrace"`
	Sha        string `json:"sha"`
}

func CreateStackIndexes(db *mgo.Database) error {
	index := mgo.Index{
		Key:        []string{"sha"},
		Unique:     true,
		DropDups:   true,
		Background: true,
	}
	return db.C("stacktraces").EnsureIndex(index)
}

func (this *Stack) ToJson() map[string]interface{} {
	result := make(map[string]interface{})
	result["stacktrace"] = this.Stacktrace
	h := sha1.New()
	io.WriteString(h, this.Stacktrace)
	this.Sha = hex.EncodeToString(h.Sum(nil))
	result["sha"] = this.Sha
	return result
}

func (this *Stack) Save(db *mgo.Database) error {
	err := db.C("stacktraces").Insert(this.ToJson())
	return err
}

func GetStackBySha(db *mgo.Database, sha string) (*Stack, error) {
	result := new(Stack)
	err := db.C("stacktraces").Find(bson.M{"sha": sha}).One(&result)
	return result, err
}
