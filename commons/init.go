package commons

import (
	"time"
)

type Log struct {
	Date    int64  `json:"date"`
	Level   string `json:"level"`
	Message string `json:"message"`
	Stack   string `json:"stack"`
}

type DbLog struct {
	Application string                 `json:"application" bson:"application"`
	Level       string                 `json:"level" bson:"level"`
	Message     string                 `json:"message" bson:"message"`
	Stack       string                 `json:"-" bson:"-"`
	Date        time.Time              `json:"date" bson:"date"`
	Tags        map[string]interface{} `json:"tags" bson:"tags"`
	StackSha    string                 `json:"stack_sha" bson:"stack_sha"`
	DtInsert    time.Time              `json:"-" bson:"_dt_insert"`
}

func NewLog(date int64, level string, message, stack string) (*Log, error) {
	l := new(Log)
	l.Date = date
	l.Level = level
	l.Message = message
	l.Stack = stack
	return l, nil
}

type SingleLog struct {
	Log
	Application      string `json:"application"`
	ApplicationToken string `json:"application_token"`
}

type MultiLog struct {
	Application      string      `json:"application"`
	ApplicationToken string      `json:"application_token"`
	Logs             []SingleLog `json:"logs"`
}

type GenericResponse struct {
	Success bool   `json:"success"`
	Message string `json:"message"`
}

type AddLogResponse struct {
	GenericResponse
}

type SearchResponse struct {
	GenericResponse
	Result []DbLog `json:"result"`
}

type LogSearchParam struct {
	Applications  []string `json:"applications"`
	Levels        []string `json:"levels"`
	DtSince       int64    `json:"dt_since"`
	DtTo          int64    `json:"dt_to"`
	Query         string   `json:"query"`
	Page          int      `json:"page"`
	MaxResult     int      `json:"max_result"`
	SortField     string   `json:"sort_field"`
	SortAscending bool     `json:"sort_ascending"`
}
