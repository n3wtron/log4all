package app

import (
	"errors"
	log4allJobs "github.com/n3wtron/log4all/log4all/app/jobs"
	"github.com/n3wtron/log4all/log4all/app/models"
	"github.com/revel/modules/jobs/app/jobs"
	"github.com/revel/revel"
	"gopkg.in/mgo.v2"
	"log"
	"os"
)

var MongoDb *mgo.Database

func InitDB() {
	var err error
	var mongoSession *mgo.Session
	var collections []string
	var userCollectionFound bool
	var c int

	dbConnectionUrl, found := revel.Config.String("db.connectionUrl")
	if !found {
		dbConnectionUrl = os.Getenv("L4AL_DB_CONNECTION")
	}

	if dbConnectionUrl == "" {
		err = errors.New("No MongoDB connection Url found on config file (db.ConnectionUrl) or in the L4AL_DB_CONNECTION env variable")
		goto finish
	}

	mongoSession, err = mgo.Dial(dbConnectionUrl)
	if err != nil {
		goto finish
	}

	MongoDb = mongoSession.DB("")

	//check if users table exists
	collections, err = MongoDb.CollectionNames()
	userCollectionFound = false
	if err != nil {
		goto finish
	}
	for c = range collections {
		if collections[c] == "users" {
			userCollectionFound = true
			break
		}
	}
	//add default admin user
	if !userCollectionFound {
		u := new(models.User)
		u.Name = "Admin User"
		u.Email = "admin"
		u.Password = "admin"
		u.Save(MongoDb)
		revel.INFO.Println("default admin user created with password admin")
	}

	// Create Collection index
	err = models.CreateTailTable(MongoDb)
	if err != nil {
		goto finish
	}
	models.CreateLogIndexes(MongoDb)
	models.CreateTagIndexes(MongoDb)
	models.CreateStackIndexes(MongoDb)
	models.CreateApplicationIndexes(MongoDb)
	models.CreateGroupIndexes(MongoDb)
	models.CreateUserIndexes(MongoDb)

finish:
	if err != nil {
		revel.ERROR.Println("Error Initializing DB")
		revel.ERROR.Panic(err)
	} else {
		log.Printf("Db initialized")
	}
}

func InitJobs() {
	jobs.Schedule("cron.deleteJobScheduler", log4allJobs.DeleteJob{Db: MongoDb})
}

func init() {
	// Filters is the default set of global filters.
	revel.Filters = []revel.Filter{
		revel.PanicFilter,             // Recover from panics and display an error page instead.
		revel.RouterFilter,            // Use the routing table to select the right Action
		revel.FilterConfiguringFilter, // A hook for adding or removing per-Action filters.
		revel.ParamsFilter,            // Parse parameters into Controller.Params.
		revel.SessionFilter,           // Restore and write the session cookie.
		revel.FlashFilter,             // Restore and write the flash cookie.
		revel.ValidationFilter,        // Restore kept validation errors and save new ones from cookie.
		revel.I18nFilter,              // Resolve the requested language
		HeaderFilter,                  // Add some security based headers
		revel.InterceptorFilter,       // Run interceptors around the action.
		revel.CompressFilter,          // Compress the result.
		revel.ActionInvoker,           // Invoke the action.
	}

	// register startup functions with OnAppStart
	// ( order dependent )
	//revel.OnAppStart(InitDB)
	// revel.OnAppStart(FillCache)
	revel.OnAppStart(InitDB)
	revel.OnAppStart(InitJobs)
}

// TODO turn this into revel.HeaderFilter
// should probably also have a filter for CSRF
// not sure if it can go in the same filter or not
var HeaderFilter = func(c *revel.Controller, fc []revel.Filter) {
	// Add some common security headers
	/*c.Response.Out.Header().Add("X-Frame-Options", "SAMEORIGIN")
	c.Response.Out.Header().Add("X-XSS-Protection", "1; mode=block")
	c.Response.Out.Header().Add("X-Content-Type-Options", "nosniff")*/
	c.Response.Out.Header().Add("Access-Control-Allow-Origin", "*")

	fc[0](c, fc[1:]) // Execute the next filter stage.
}
