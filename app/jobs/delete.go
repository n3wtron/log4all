package jobs

import (
	"github.com/revel/revel"
	"gopkg.in/mgo.v2"
	"log4all/app/models"
	"reflect"
)

type DeleteJob struct {
	Db *mgo.Database
}

func (j DeleteJob) Run() {
	revel.INFO.Println("delete job started")
	// get the applications
	apps, _ := models.GetApplications(j.Db)
	for a := range apps {
		revel.INFO.Printf("cleaning %s application logs", apps[a].Name)
		appConf := apps[a].Configuration
		cnfEl := reflect.ValueOf(appConf)
		for l := 0; l < cnfEl.NumField(); l++ {
			fld := cnfEl.Field(l)
			fldType := reflect.TypeOf(appConf).Field(l)
			level := fldType.Tag.Get("json")
			err := models.DeleteLog(j.Db, apps[a].Name, level, fld.Interface().(models.LevelConfiguration).DeleteDays)
			if err != nil {
				revel.ERROR.Println(err.Error())
			}
		}
	}
	revel.INFO.Println("delete job finished")
}
