package client

import (
	"bytes"
	"encoding/json"
	"github.com/jinzhu/copier"
	commonsLog "github.com/n3wtron/log4all/commons"
	"io/ioutil"
	"net/http"
)

func commonsCall(request *http.Request) error {
	httpClient := &http.Client{}
	resp, err := httpClient.Do(request)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	jsResponse, err := ioutil.ReadAll(resp.Body)
	var addLogResponse commonsLog.AddLogResponse
	err = json.Unmarshal(jsResponse, &addLogResponse)
	if err != nil {
		return err
	}
	if !addLogResponse.Success {
		return NewClientError(ERR_ADD_LOG, addLogResponse.Message)
	}
	return nil
}

func (client *Client) AddLog(log *commonsLog.Log) error {
	var addLogRequestData commonsLog.SingleLog
	copier.Copy(&addLogRequestData, log)
	if len(client.Application) == 0 {
		return NewClientError(ERR_APPLICATION_MANDATORY)
	}
	addLogRequestData.Application = client.Application
	addLogRequestData.ApplicationToken = client.ApplicationToken
	addLogRequestDataJson, err := json.Marshal(addLogRequestData)
	if err != nil {
		return err
	}
	addLogRequest, err := http.NewRequest("PUT", client.Url+"/api/log", bytes.NewReader(addLogRequestDataJson))
	if err != nil {
		return err
	}
	return commonsCall(addLogRequest)
}

func (client *Client) AddLogs(logs []*commonsLog.Log) error {
	var addLogsRequestData commonsLog.MultiLog
	if len(client.Application) == 0 {
		return NewClientError(ERR_APPLICATION_MANDATORY)
	}
	addLogsRequestData.Application = client.Application
	addLogsRequestData.ApplicationToken = client.ApplicationToken
	copier.Copy(&addLogsRequestData.Logs, logs)
	addLogsRequestDataJson, err := json.Marshal(addLogsRequestData)
	if err != nil {
		return err
	}

	addLogRequest, err := http.NewRequest("PUT", client.Url+"/api/logs", bytes.NewReader(addLogsRequestDataJson))
	if err != nil {
		return err
	}
	return commonsCall(addLogRequest)
}
