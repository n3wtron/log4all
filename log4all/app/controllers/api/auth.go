package api

import (
	"encoding/json"
	"github.com/n3wtron/log4all/log4all/app"
	"github.com/n3wtron/log4all/log4all/app/controllers"
	"github.com/revel/revel"
	"io/ioutil"
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

	err, authUser := app.GetAuthSystem().Login(loginReq.Username, loginReq.Password)

	if err != nil {
		result["success"] = false
		result["message"] = err.Error()
	} else {
		jwtStr, err := authUser.ToJWT()
		if err != nil {
			revel.ERROR.Println(jwtStr)
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
	result := []string{"admin"}

	return this.RenderJson(result)
}
