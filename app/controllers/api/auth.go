package api

import (
	"crypto/md5"
	"encoding/hex"
	"encoding/json"
	"github.com/dgrijalva/jwt-go"
	"github.com/fatih/structs"
	"github.com/revel/revel"
	"gopkg.in/mgo.v2"
	"io"
	"io/ioutil"
	"log4all/app/controllers"
	"log4all/app/models"
	"time"
)

type AuthApi struct {
	controllers.DbController
}

type LoginRequest struct {
	Username string
	Password string
}

func init() {
}

func (this *AuthApi) Login() revel.Result {
	result := make(map[string]interface{})
	byteBody, _ := ioutil.ReadAll(this.Request.Body)
	loginReq := new(LoginRequest)
	err := json.Unmarshal(byteBody, &loginReq)
	revel.INFO.Printf("login :%v", loginReq)
	srcUserQry := make(map[string]interface{})
	srcUserQry["email"] = loginReq.Username
	md5Pwd := md5.New()
	io.WriteString(md5Pwd, loginReq.Password)
	srcUserQry["password"] = hex.EncodeToString(md5Pwd.Sum(nil))
	revel.INFO.Printf("src User :%v", srcUserQry)
	user, err := models.FindUser(this.Db, srcUserQry)

	if err != nil {
		result["success"] = false
		if err == mgo.ErrNotFound {
			result["message"] = "Authentication failed"
		} else {
			result["message"] = err.Error()
		}
	} else {
		//JWT token
		jwtToken := jwt.New(jwt.SigningMethodHS256)
		jwtToken.Claims = structs.Map(user)
		jwtToken.Claims["exp"] = time.Now().Add(time.Hour * 24).Unix()
		jwtStr, err := jwtToken.SignedString([]byte(revel.Config.StringDefault("jwt.secret", "")))
		if err != nil {
			revel.ERROR.Println(jwtToken)
			result["success"] = false
			result["message"] = err.Error()
		} else {
			result["success"] = true
			result["result"] = jwtStr
		}
	}

	return this.RenderJson(result)
}

func (this *AuthApi) GetPermissions() revel.Result {
	result := make([]string, 1)
	result[0] = "admin"

	return this.RenderJson(result)
}
