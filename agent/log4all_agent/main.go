package main

import (
	"fmt"
	"github.com/n3wtron/log4all/agent/config"
	"github.com/n3wtron/log4all/agent/log"
	"github.com/n3wtron/log4all/agent/util"
	_log "log"
	"os"
	"strconv"
	"sync"
)

func usage() string {
	usage := "Usage\n" + os.Args[0] + " [configFile]"
	return usage
}

func elabLog(wg *sync.WaitGroup, logFileInfo *util.LogFileInfo, cnf *config.Config, statusCnf *config.StatusConfig) {
	var exist bool
	var toRead bool = false
	var logRecord config.LogRecord
	var readFrom uint64

	defer logFileInfo.File.Close()

	_log.Printf("elaborating %s \n", logFileInfo)

	if logRecord, exist = statusCnf.LogMap[strconv.FormatUint(logFileInfo.Inode, 10)]; exist && logRecord.Readed < logFileInfo.Size {
		//partially readed
		_log.Printf("Partially readed readed:%d size:%d\n", logRecord.Readed, logFileInfo.Size)
		readFrom = logRecord.Readed
		toRead = true
	} else {
		if !exist {
			_log.Println("Not readed")
			readFrom = 0
			toRead = true
		}
	}
	if toRead {
		logFile, err := log.NewLogFile(cnf, logFileInfo.File, readFrom)
		if err != nil {
			_log.Fatalf("Error opening %s:%s", logFileInfo, err.Error())
		} else {
			logs, err := logFile.Parse()
			_log.Printf("logs readed:%d\n", len(logs))
			statusCnf.LogReaded(logFileInfo.Inode, logFileInfo.Name, logFile.Readed)
			if err != nil {
				_log.Printf("Error: %s\n", err.Error())
			}
		}
	}
	wg.Done()
}

func main() {

	var logFileInfos []*util.LogFileInfo
	var statusCnf *config.StatusConfig

	var wg sync.WaitGroup

	if len(os.Args) < 2 {
		fmt.Println(usage())
		return
	}
	configFile := os.Args[1]
	cnf, err := config.ReadConfig(configFile)
	if err != nil {
		goto finish
	}
	statusCnf, err = config.ReadStatusConfig(cnf.StatusFilePath)
	if err != nil {
		goto finish
	}

	//scan logfolder
	logFileInfos, err = util.ScanDir(cnf.LogPath, cnf.LogFileFormat)
	if err != nil {
		goto finish
	}

	for _, logFileInfo := range logFileInfos {
		wg.Add(1)
		go elabLog(&wg, logFileInfo, cnf, statusCnf)
	}
	wg.Wait()
	err = statusCnf.Save()

finish:
	if err != nil {
		_log.Fatalf("Error: %s\n", err.Error())
		os.Exit(1)
	}
}
