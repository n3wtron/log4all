package client

import (
	"code.google.com/p/go-uuid/uuid"
	commonsLog "github.com/n3wtron/log4all/commons"
	"testing"
	"time"
)

func addLog(goTestId string) error {
	cl, err := NewClient("http://localhost:9000", "test", "")
	if err != nil {
		return err
	}

	now := time.Now()
	log, err := commonsLog.NewLog(now.UnixNano()/1000000, "DEBUG", "test go #go #goTestId:"+goTestId, "")
	if err != nil {
		return err
	}
	err = cl.AddLog(log)
	if err != nil {
		return err
	}
	return nil
}

func TestSearch(t *testing.T) {
	cl, err := NewClient("http://localhost:9000", "test", "")
	if err != nil {
		t.Error(err.Error())
	}
	now := time.Now()
	goTestId := uuid.New()
	err = addLog(goTestId)
	if err != nil {
		t.Error(err.Error())
	}

	srcQuery := new(commonsLog.LogSearchParam)
	srcQuery.Applications = []string{"test"}
	srcQuery.DtSince = now.UnixNano() / 1000000
	srcQuery.DtTo = (now.UnixNano() / 1000000) + 10000 //+10sec
	srcQuery.Levels = []string{"DEBUG"}
	srcQuery.Query = "#goTestId=" + goTestId
	logs, err := cl.Search(srcQuery)
	if err != nil {
		t.Error(err.Error())
	}
	if len(logs) != 1 {
		t.Errorf("expected 1 logs, founded %d", len(logs))
	}
}
