package tests

import (
	"bytes"
	"encoding/json"
	"github.com/n3wtron/log4all/commons/log"
	"github.com/revel/revel/testing"
)

type AddLogTest struct {
	testing.TestSuite
}

func (t *AddLogTest) TestBadToken() {
	lg := new(log.SingleLog)
	lg.Application = "test"
	lg.ApplicationToken = "badToken"
	lg.Level = "ERROR"
	lg.Message = "If you see this there is a problem"
	bJson, _ := json.Marshal(lg)
	println(string(bJson))

	t.Put("/api/log", "application/json", bytes.NewReader(bJson))
	t.AssertContainsRegex("\"success\"[ ]*:[ ]*false")
	t.AssertStatus(200)
	t.AssertContentType("application/json; charset=utf-8")
}
