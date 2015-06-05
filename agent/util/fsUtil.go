package util

import (
	"encoding/json"
	"io/ioutil"
	"os"
	"path/filepath"
	"regexp"
	"syscall"
)

type LogFileInfo struct {
	Inode uint64
	Name  string
	Path  string
	File  *os.File
	Size  uint64
}

func (logInfo *LogFileInfo) String() string {
	res, _ := json.Marshal(logInfo)
	return string(res)
}

func ScanDir(dirPath string, filenameFormat string) ([]*LogFileInfo, error) {
	var filenameRegExp *regexp.Regexp
	var logs []*LogFileInfo
	//get the dir content
	dirContent, err := ioutil.ReadDir(dirPath)
	if err != nil {
		goto finish
	}
	//create the filenameRegexp
	filenameRegExp, err = regexp.Compile(filenameFormat)
	if err != nil {
		goto finish
	}
	logs = make([]*LogFileInfo, 0, len(dirContent))
	//filter the file by the filenameFormat
	for _, fI := range dirContent {
		if !fI.IsDir() && filenameRegExp.MatchString(fI.Name()) {
			logDesc := new(LogFileInfo)
			logDesc.Inode = fI.Sys().(*syscall.Stat_t).Ino
			logDesc.Path = filepath.Clean(dirPath + fI.Name())
			logDesc.Name = fI.Name()
			//open file
			logDesc.File, err = os.Open(logDesc.Path)
			if err != nil {
				goto finish
			}
			logDesc.Size = uint64(fI.Size())
			logs = append(logs, logDesc)
		}
	}
finish:
	if err != nil {
		return nil, err
	}
	return logs, nil
}
