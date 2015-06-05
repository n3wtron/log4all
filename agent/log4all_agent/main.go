package main

import (
	"fmt"
	"github.com/n3wtron/log4all/agent"
	"github.com/n3wtron/log4all/client"
	_log "log"
	"os"
	"strconv"
	"sync"
)

func usage() string {
	usage := "Usage\n" + os.Args[0] + " [configFile]"
	return usage
}

func elabLog(wg *sync.WaitGroup, logFileInfo *agent.LogFileInfo, cnf *agent.Config, statusCnf *agent.StatusConfig) {
	var exist bool
	var toRead bool = false
	var logRecord agent.LogRecord
	var readFrom uint64

	defer logFileInfo.File.Close()

	_log.Printf("elaborating %s \n", logFileInfo)

	log4allClient, err := client.NewClient(cnf.Log4allUrl, cnf.Application, cnf.ApplicationToken)

	if err != nil {
		_log.Fatalf("Error creating client %s\n", err.Error())
		return
	}

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
		logFile, err := agent.NewLogFile(cnf, logFileInfo.File, readFrom)
		if err != nil {
			_log.Fatalf("Error opening %s:%s", logFileInfo, err.Error())
		} else {
			//parse log file
			logs, err := logFile.Parse()
			if err != nil {
				_log.Printf("Error: %s\n", err.Error())
			}
			//send log to server
			err = log4allClient.AddLogs(logs)
			if err != nil {
				_log.Printf("Error: %s\n", err.Error())
			}
			_log.Printf("logs readed:%d\n", len(logs))
			statusCnf.LogReaded(logFileInfo.Inode, logFileInfo.Name, logFile.Readed)
		}
	}
	wg.Done()
}

func main() {

	var logFileInfos []*agent.LogFileInfo
	var statusCnf *agent.StatusConfig
	var inodes []uint64
	var wg sync.WaitGroup

	if len(os.Args) < 2 {
		fmt.Println(usage())
		return
	}
	configFile := os.Args[1]
	cnf, err := agent.ReadConfig(configFile)
	if err != nil {
		goto finish
	}

	statusCnf, err = agent.ReadStatusConfig(cnf.StatusFilePath)
	if err != nil {
		goto finish
	}

	//scan logfolder
	logFileInfos, err = agent.ScanDir(cnf.LogPath, cnf.LogFileFormat)
	if err != nil {
		goto finish
	}

	inodes = make([]uint64, len(logFileInfos))
	for i, logFileInfo := range logFileInfos {
		wg.Add(1)
		inodes[i] = logFileInfo.Inode
		go elabLog(&wg, logFileInfo, cnf, statusCnf)
	}
	wg.Wait()
	err = statusCnf.Save(inodes)

finish:
	if err != nil {
		_log.Fatalf("Error: %s\n", err.Error())
		os.Exit(1)
	}
}
