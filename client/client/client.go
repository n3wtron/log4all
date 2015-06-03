package client

import (
	"bytes"
	"encoding/json"
	"github.com/jinzhu/copier"
	"github.com/n3wtron/log4all_go_client/errors"
	"io/ioutil"
	"net/http"
)

type Client struct {
	Url              string
	Application      string
	ApplicationToken string
}

type AddLogRequest struct {
	Log
	Application      string `json:"application"`
	ApplicationToken string `json:"application_token"`
}

type AddLogsRequest struct {
	Logs             []*Log `json:"logs"`
	Application      string `json:"application"`
	ApplicationToken string `json:"application_token"`
}

type AddLogResponse struct {
	Success bool   `json:"success"`
	Message string `json:"message"`
}

func NewClient(url, application, applicationToken string) (*Client, error) {
	cl := new(Client)
	if len(url) == 0 {
		return nil, errors.NewClientError(errors.ERR_URL_MANDATORY)
	}
	if len(application) == 0 {
		return nil, errors.NewClientError(errors.ERR_APPLICATION_MANDATORY)
	}
	cl.Application = application
	cl.ApplicationToken = applicationToken
	cl.Url = url
	return cl, nil
}

func commonsCall(request *http.Request) error {
	httpClient := &http.Client{}
	resp, err := httpClient.Do(request)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	jsResponse, err := ioutil.ReadAll(resp.Body)
	var addLogResponse AddLogResponse
	err = json.Unmarshal(jsResponse, &addLogResponse)
	if err != nil {
		return err
	}
	if !addLogResponse.Success {
		return errors.NewClientError(errors.ERR_ADD_LOG, addLogResponse.Message)
	}
	return nil
}

func (client *Client) AddLog(log *Log) error {
	var addLogRequestData AddLogRequest
	copier.Copy(&addLogRequestData, log)
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

func (client *Client) AddLogs(logs []*Log) error {
	var addLogsRequestData AddLogsRequest
	addLogsRequestData.Application = client.Application
	addLogsRequestData.ApplicationToken = client.ApplicationToken
	addLogsRequestData.Logs = logs
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
