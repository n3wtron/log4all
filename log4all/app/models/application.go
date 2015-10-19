package models

import (
	"gopkg.in/mgo.v2"
	"gopkg.in/mgo.v2/bson"
)

type LevelConfiguration struct {
	ArchiveDays int `json:"archive"`
	DeleteDays  int `json:"delete"`
}

type ApplicationPermission struct {
	Username   string `json:"username" bson:"username"`
	Permission string `json:"permission" bson:"permission`
}

type RetentionConfiguration struct {
	Debug   LevelConfiguration `json:"debug" bson:"debug"`
	Info    LevelConfiguration `json:"info" bson:"info"`
	Warning LevelConfiguration `json:"warning" bson:"warning"`
	Error   LevelConfiguration `json:"error" bson:"error"`
}

type ApplicationConfiguration struct {
	Retention RetentionConfiguration `json:"retention" bson:"retention"`
	WriteSafe bool                   `json:"writeSafe" bson:"writeSafe"`
}

type Application struct {
	BasicModel    `bson:"-"`
	Id            bson.ObjectId            `json:"_id" bson:"_id"`
	Name          string                   `json:"name" bson:"name"`
	Description   string                   `json:"description" bson:"description"`
	Token         string                   `json:"token" bson:"token"`
	Configuration ApplicationConfiguration `json:"configuration" bson:"configuration"`
	Permissions   []ApplicationPermission  `json:"permissions" bson:"permissions"`
}

func CreateApplicationIndexes(db *mgo.Database) error {
	index := mgo.Index{
		Key:        []string{"name"},
		Unique:     true,
		DropDups:   true,
		Background: true,
	}
	return db.C("applications").EnsureIndex(index)
}

func (this *Application) Save(db *mgo.Database) error {
	this.Id = bson.NewObjectId()
	return db.C("applications").Insert(this)
}

func (this *Application) Update(db *mgo.Database, id string) error {
	app, err := GetApplicationById(db, id)
	if err == nil {
		err = db.C("applications").Update(bson.M{"_id": bson.ObjectIdHex(id)}, this)
		if this.Name != app.Name {
			//rename all logs for this application
			_, err = db.C("logs").UpdateAll(bson.M{"application": app.Name}, bson.M{"$set": bson.M{"application": this.Name}})
		}
	}
	return err
}

func DeleteApplication(db *mgo.Database, id string) error {
	app, err := GetApplicationById(db, id)
	if err == nil {
		err = db.C("applications").Remove(bson.M{"_id": bson.ObjectIdHex(id)})
	}
	if err == nil {
		_, err = db.C("logs").RemoveAll(bson.M{"application": app.Name})
	}
	return err
}

func GetApplicationById(db *mgo.Database, id string) (Application, error) {
	var result Application
	err := db.C("applications").Find(bson.M{"_id": bson.ObjectIdHex(id)}).One(&result)
	return result, err
}

func GetApplications(db *mgo.Database) ([]Application, error) {
	var result []Application
	err := db.C("applications").Find(bson.M{}).All(&result)
	return result, err
}

func GetApplicationByName(db *mgo.Database, name string) (*Application, error) {
	result := new(Application)
	err := db.C("applications").Find(bson.M{"name": name}).One(&result)
	return result, err
}

func GetApplicationByToken(db *mgo.Database, name string, token string) (*Application, error) {
	result := new(Application)
	err := db.C("applications").Find(bson.M{"name": name, "token": token}).One(&result)
	return result, err
}

func FindApplications(db *mgo.Database, query map[string]interface{}) ([]Application, error) {
	var result []Application
	err := db.C("applications").Find(query).All(&result)
	return result, err
}
