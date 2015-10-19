package app

import (
	"github.com/dgrijalva/jwt-go"
	"github.com/fatih/structs"
	"github.com/revel/revel"
	"time"
)

type AuthUser struct {
	Username   string
	Groups     []string
	CommonName string
	Email      string
	Exp        int64
	ExtraData  map[string]interface{}
}

type AuthInterface interface {
	Name() string
	Login(username, password string) (error, *AuthUser)
	Logout(user AuthUser)
	Initialize()
}

func (user *AuthUser) ToJWT() (string, error) {
	//JWT token
	jwtToken := jwt.New(jwt.SigningMethodHS256)
	jwtToken.Claims = structs.Map(user)
	jwtToken.Claims["exp"] = time.Now().Add(time.Hour * 24).Unix()
	return jwtToken.SignedString([]byte(revel.Config.StringDefault("jwt.secret", "")))
}

var authSystem AuthInterface

func Register(authImpl AuthInterface) {
	revel.INFO.Println("Register new auth plugin")
	authSystem = authImpl
}

func GetAuthSystem() AuthInterface {
	return authSystem
}
