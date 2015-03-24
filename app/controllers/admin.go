package controllers

import(
"github.com/revel/revel"

)

type Admin struct {
	*revel.Controller
}

func (this *Admin) Index() revel.Result{
	return this.Render()
}
