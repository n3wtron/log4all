package models

import(
	"gopkg.in/mgo.v2"
	"gopkg.in/mgo.v2/bson"
	"io"
	"encoding/hex"
	"crypto/md5"
	"time"
	"log"
)

type User struct{
	BasicModel						`bson:"-"`
	Id			bson.ObjectId		`json:"_id" bson:"_id"`
	Email		string				`json:"email"`
	Name		string				`json:"name"`
	Password	string				`json:"password"`
	Groups		[]string			`json:"groups"`
	Permissions	[]string			`json:"permissions"`	
	DtInsert	time.Time
}

func CreateUserIndexes(db *mgo.Database) error{
	index := mgo.Index{
		Key: []string{"email"},
		Unique: true,
		DropDups: true,
		Background: true,
	}
	return db.C("users").EnsureIndex(index)
}

func (this *User) Save(db *mgo.Database) error{
	this.Id = bson.NewObjectId()
	md5Pwd := md5.New()
	io.WriteString(md5Pwd,this.Password)
	this.Password = hex.EncodeToString(md5Pwd.Sum(nil))
	return db.C("users").Insert(this)
}

func (this *User) updatePermissions(db *mgo.Database) error{
	permissions:=make(map[string]interface{})
	groups:=make([]string, 0, len(this.Groups))
	for g:=range(this.Groups){
		log.Printf(this.Groups[g])
		group,err := GetGroupByName(db,this.Groups[g])
		if err == nil{
			groups = append(groups,group.Name)
			for p:=range(group.Permissions){
				perm := group.Permissions[p]
				permissions[perm]=nil
			}
		}
	}
	this.Groups = groups
	this.Permissions = make([]string,0,len(permissions))
	for perm:=range permissions {
		this.Permissions = append(this.Permissions,perm)
	}
	return nil
}

func (this *User) Update(db *mgo.Database,id string) error{
	dbUser,err := GetUserById(db,id)
	if err != nil{
		return err
	}
	if dbUser.Password != this.Password{
		md5Pwd := md5.New()
		io.WriteString(md5Pwd,this.Password)
		this.Password = hex.EncodeToString(md5Pwd.Sum(nil))
	}
	err = this.updatePermissions(db)
	if err != nil{
		return err
	}
	return db.C("users").Update(bson.M{"_id":bson.ObjectIdHex(id)},this)
}

func DeleteUser(db *mgo.Database, id string) error{
	err := db.C("users").Remove(bson.M{"_id":bson.ObjectIdHex(id)})
	return err
}

func GetUsers(db *mgo.Database) ([]User,error){
	var result []User
	err := db.C("users").Find(bson.M{}).All(&result)
	return result,err
}

func GetUserById(db *mgo.Database, id string) (User,error){
	var result User
	err := db.C("users").Find(bson.M{"_id":bson.ObjectIdHex(id)}).One(&result)
	return result,err
}

func FindUser(db *mgo.Database, qry map[string]interface{}) (*User,error) {
	result := new(User)
	err := db.C("users").Find(qry).One(&result);
	return result,err
}

func FindUsers(db *mgo.Database, qry map[string]interface{}) ([]User,error) {
	var result []User
	err := db.C("users").Find(qry).All(&result);
	return result,err
}
