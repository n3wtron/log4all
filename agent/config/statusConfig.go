package config

import (
	"encoding/json"
	"io/ioutil"
	"os"
	"strconv"
)

type LogRecord struct {
	Inode  uint64 `json:"inode"`
	Readed uint64 `json:"readed"`
	Name   string `json:"name"`
}

type StatusConfig struct {
	LogMap map[string]LogRecord `json:"logs"`
}

var statusConfig *StatusConfig = nil
var statusConfigFile string

func ReadStatusConfig(configFile string) (*StatusConfig, error) {
	var configContent []byte
	configContent, err := ioutil.ReadFile(configFile)
	if err != nil {
		if os.IsNotExist(err) {
			configContent = []byte("{}")
			err = ioutil.WriteFile(configFile, configContent, 0777)
			if err != nil {
				return nil, err
			}
		} else {
			return nil, err
		}
	}
	statusConfigFile = configFile
	statusConfig = new(StatusConfig)
	err = json.Unmarshal(configContent, statusConfig)
	if statusConfig.LogMap == nil {
		statusConfig.LogMap = make(map[string]LogRecord)
	}
	return statusConfig, err
}

func GetStatusConfig() *StatusConfig {
	return statusConfig
}

func (statusCnf *StatusConfig) Save() error {
	statusCnfJson, err := json.Marshal(statusCnf)
	if err != nil {
		return err
	}
	err = ioutil.WriteFile(statusConfigFile, statusCnfJson, 0777)
	return err
}

func (statusCnf *StatusConfig) LogReaded(inode uint64, name string, readed uint64) {
	logRecord := new(LogRecord)
	logRecord.Inode = inode
	logRecord.Readed = readed
	logRecord.Name = name
	statusCnf.LogMap[strconv.FormatUint(inode, 10)] = *logRecord
}
