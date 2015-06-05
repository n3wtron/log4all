package jobs

import (
	"github.com/n3wtron/log4all/log4all/app/models"
	"github.com/revel/revel"
	"gopkg.in/mgo.v2"
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
		appRetentionConf := apps[a].Configuration.Retention
		cnfEl := reflect.ValueOf(appRetentionConf)
		for l := 0; l < cnfEl.NumField(); l++ {
			fld := cnfEl.Field(l)
			fldType := reflect.TypeOf(appRetentionConf).Field(l)
			level := fldType.Tag.Get("json")
			err := models.DeleteLog(j.Db, apps[a].Name, level, fld.Interface().(models.LevelConfiguration).DeleteDays)
			if err != nil {
				revel.ERROR.Println(err.Error())
			}
		}
	}
	revel.INFO.Println("delete job finished")
}
