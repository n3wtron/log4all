package models

import(
	"gopkg.in/mgo.v2"
	"time"
)

type User struct{
	Email		string
	Name		string
	Password	string
	Groups		[]string
	Permissions	[]string
	DtInsert	time.Time
}

func (this *User) Save(db *mgo.Database){
	db.C("users").Insert(this)
}

func GetUser(db *mgo.Database, qry map[string]interface{}) (*User,error) {
	result := new(User)
	err := db.C("users").Find(qry).One(&result);
	return result,err
}
