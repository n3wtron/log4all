package controllers

import(
"github.com/revel/revel"

)

type App struct {
	*revel.Controller
}


func (c App) Index() revel.Result {
	params := make(map[string]string)
	params["test"]="Ciao Igor"
	return c.Render(params)
}

