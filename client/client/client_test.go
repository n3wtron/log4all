package client

import (
	"github.com/n3wtron/log4all/client/errors"
	commonsLog "github.com/n3wtron/log4all/commons/log"
	"testing"
	"time"
)

func TestBasic(t *testing.T) {
	_, err := NewClient("http://localhost:9000", "test", "")
	if err != nil {
		t.Error(err.Error())
	}
}

func TestUrlEmpty(t *testing.T) {
	_, err := NewClient("", "test", "")
	if err == nil {
		t.Error("expect url is mandatory")
	}
	if err.(errors.ClientError).ErrorType != errors.ERR_URL_MANDATORY {
		t.Error("expect url is mandatory but received:" + err.Error())
	}
}

func TestApplicationEmpty(t *testing.T) {
	_, err := NewClient("http://localhost:9000", "", "")
	if err == nil {
		t.Error("expect application is mandatory")
	}
	if err.(errors.ClientError).ErrorType != errors.ERR_APPLICATION_MANDATORY {
		t.Error("expect application is mandatory but received:" + err.Error())
	}
}

func TestAddLog(t *testing.T) {
	cl, err := NewClient("http://localhost:9000", "test", "")
	if err != nil {
		t.Error(err.Error())
	}
	now := time.Now()
	log, err := commonsLog.NewLog(now.UnixNano()/1000000, "DEBUG", "test max da go #go", "")
	if err != nil {
		t.Error(err.Error())
	}
	err = cl.AddLog(log)
	if err != nil {
		t.Error(err.Error())
	}
}

func TestAddLogs(t *testing.T) {
	cl, err := NewClient("http://localhost:9000", "test", "")
	if err != nil {
		t.Error(err.Error())
	}
	logs := make([]*commonsLog.Log, 2)
	now := time.Now()
	logs[0], err = commonsLog.NewLog(now.UnixNano()/1000000, "DEBUG", "test da go log1/2 #go", "")
	if err != nil {
		t.Error(err.Error())
	}
	now = time.Now()
	logs[1], err = commonsLog.NewLog(now.UnixNano()/1000000, "DEBUG", "test da go log2/2 #go", "")
	if err != nil {
		t.Error(err.Error())
	}
	err = cl.AddLogs(logs)
	if err != nil {
		t.Error(err.Error())
	}
}
