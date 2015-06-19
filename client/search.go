package client

import (
	"bytes"
	"encoding/json"
	"github.com/n3wtron/log4all/commons"
	"io/ioutil"
	"net/http"
	/*"time"*/)

func (client *Client) Search(srcQuery *commons.LogSearchParam) ([]commons.DbLog, error) {
	jsonSrcQuery, err := json.Marshal(srcQuery)
	if err != nil {
		return nil, err
	}
	resp, err := http.Post(client.Url+"/api/logs/search", "application/json", bytes.NewReader(jsonSrcQuery))
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	jsResponse, err := ioutil.ReadAll(resp.Body)

	var searchResponse commons.SearchResponse
	err = json.Unmarshal(jsResponse, &searchResponse)
	if err != nil {
		return nil, err
	}
	if !searchResponse.Success {
		return nil, NewClientError(ERR_SEARCH_LOG, searchResponse.Message)
	}
	return searchResponse.Result, nil
}
