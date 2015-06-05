package controllers

import (
	"github.com/revel/revel"
)

type Admin struct {
	*revel.Controller
}

func (this *Admin) Index() revel.Result {
	var log4allAdminServicePath string
	if revel.Config.BoolDefault("mode.dev", true) {
		log4allAdminServicePath = "/public/components/angular-log4all/dist/log4AllAdminService.js"
	} else {
		log4allAdminServicePath = "/public/components/angular-log4all/dist/log4AllAdminService.min.js"
	}
	return this.Render(log4allAdminServicePath)
}
