package controllers

import (
	"github.com/revel/revel"
)

type App struct {
	*revel.Controller
}

func (c App) Index() revel.Result {
	var log4allServicePath string
	if revel.Config.BoolDefault("mode.dev", true) {
		log4allServicePath = "/public/components/angular-log4all/dist/log4AllService.js"
	} else {
		log4allServicePath = "/public/components/angular-log4all/dist/log4AllService.min.js"
	}
	return c.Render(log4allServicePath)
}
