package client

import (
	"time"
)

type Log struct {
	Date    time.Time `json:"date"`
	Level   string    `json:"level"`
	Message string    `json:"message"`
	Stack   string    `json:"stack"`
}

func NewLog(date time.Time, level string, message, stack string) (*Log, error) {
	l := new(Log)
	l.Date = date
	l.Level = level
	l.Message = message
	l.Stack = stack
	return l, nil
}
