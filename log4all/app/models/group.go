package models

import (
	"gopkg.in/mgo.v2"
	"gopkg.in/mgo.v2/bson"
	//"log"
)

type Group struct {
	BasicModel						`bson:"-"`
	Id				bson.ObjectId	`json:"_id" bson:"_id"`
	Name 			string 			`json:"name"`
	Description 	string			`json:"description"`
	Permissions		[]string		`json:"permissions"`			
}

func CreateGroupIndexes(db *mgo.Database) error{
	index := mgo.Index{
		Key: []string{"name"},
		Unique: true,
		DropDups: true,
		Background: true,
	}
	return db.C("groups").EnsureIndex(index)
}

func (this *Group) Save(db *mgo.Database) error{
	this.Id = bson.NewObjectId()
	return db.C("groups").Insert(this)
}

func (this *Group) Update(db *mgo.Database,id string) error{
	oldGroup,err := GetGroupById(db,id)
	if err != nil {
		return err
	}
	grpUpdErr := db.C("groups").Update(bson.M{"_id":bson.ObjectIdHex(id)},this)
	
	if grpUpdErr !=nil{
		return grpUpdErr
	}
	
	//update users
	users,err := FindUsers(db,bson.M{"groups":bson.M{"$in":[]string{oldGroup.Name}}})
	if err == nil {
		for i:=range(users){
			user := users[i]
			for g:=range(user.Groups){
				uGroup := user.Groups[g]
				if uGroup == oldGroup.Name{
					user.Groups[g] = this.Name
				}
			}
			user.Update(db,user.Id.Hex())
		}
	}
	return err
}

func DeleteGroup(db *mgo.Database, id string) error{
	oldGroup,err := GetGroupById(db,id)
	if err != nil {
		return err
	}
	err = db.C("groups").Remove(bson.M{"_id":bson.ObjectIdHex(id)})
	if err!=nil{
		return err
	}
	users,err := FindUsers(db,bson.M{"groups":bson.M{"$in":[]string{oldGroup.Name}}})
	if err == nil {
		for u:= range(users){
			users[u].Update(db, users[u].Id.Hex())
		}
	}
	return err
}

func GetGroups(db *mgo.Database) ([]Group,error){
	var result []Group
	err := db.C("groups").Find(bson.M{}).All(&result)
	return result,err
}

func GetGroupById(db *mgo.Database, id string) (Group,error){
	var result Group
	err := db.C("groups").Find(bson.M{"_id":bson.ObjectIdHex(id)}).One(&result)
	return result,err
}

func GetGroupByName(db *mgo.Database, name string) (Group,error){
	var result Group
	err := db.C("groups").Find(bson.M{"name":name}).One(&result)
	return result,err
}

