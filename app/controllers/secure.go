package controllers

import (
	"errors"
	"github.com/dgrijalva/jwt-go"
	"github.com/revel/revel"
)

type AuthenticatedController struct {
	DbController
	User map[string]interface{}
}

func (ctrl *AuthenticatedController) checkAuthentication() revel.Result {
	token, err := jwt.ParseFromRequest(ctrl.Request.Request, func(t *jwt.Token) (interface{}, error) {
		return []byte(revel.Config.StringDefault("jwt.secret", "")), nil
	})
	if err != nil {
		revel.ERROR.Println(err)
		return ctrl.RenderError(errors.New("401: Not authorized"))
	} else {
		ctrl.User = token.Claims
		return nil
	}
}

func init() {
	revel.InterceptMethod((*AuthenticatedController).checkAuthentication, revel.BEFORE)
}
