package log

type Log struct {
	Date    int64  `json:"date"`
	Level   string `json:"level"`
	Message string `json:"message"`
	Stack   string `json:"stack"`
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

type AddLogResponse struct {
	Success bool   `json:"success"`
	Message string `json:"message"`
}

func NewLog(date int64, level string, message, stack string) (*Log, error) {
	l := new(Log)
	l.Date = date
	l.Level = level
	l.Message = message
	l.Stack = stack
	return l, nil
}
