package log

import "github.com/n3wtron/log4all/log4all/app/controllers"

type ApiAddLog struct {
	controllers.DbController
}

type ApiSearchLog struct {
	controllers.AuthenticatedController
}
