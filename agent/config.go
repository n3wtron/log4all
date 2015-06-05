package agent

import (
	"encoding/json"
	"io/ioutil"
	/*"log"*/)

type Config struct {
	Log4allUrl       string            `json:"log4allUrl"`
	Application      string            `json:"application"`
	ApplicationToken string            `json:"applicationToken"`
	LogPath          string            `json:"logPath"`
	LogFileFormat    string            `json:"logFileFormat"`
	StatusFilePath   string            `json:"statusFilePath"`
	NewLineFormat    string            `json:"newLineFormat"`
	RegExp           map[string]string `json:"regexp"`
	DateFormat       string            `json:"dateFormat"`
}

var currConfig *Config = nil

func ReadConfig(configFile string) (*Config, error) {
	configContent, err := ioutil.ReadFile(configFile)
	if err != nil {
		return nil, err
	}

	currConfig = new(Config)
	err = json.Unmarshal(configContent, currConfig)
	return currConfig, err
}

func GetConfig() *Config {
	return currConfig
}
