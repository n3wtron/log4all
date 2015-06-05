package agent

import (
	"bufio"
	"fmt"
	commonsLog "github.com/n3wtron/log4all/commons"
	"os"
	"regexp"
	"strings"
	"time"
)

type LogFile struct {
	File          *os.File
	StartFrom     uint64
	NewLineRegExp *regexp.Regexp
	FieldPos      map[string]int
	Readed        uint64
}

func NewLogFile(cnf *Config, logFile *os.File, readFrom uint64) (*LogFile, error) {
	var err error
	lgf := new(LogFile)
	lgf.File = logFile
	lgf.FieldPos = make(map[string]int)
	lgf.StartFrom = readFrom
	lgf.Readed = readFrom
	newLineFormat := cnf.NewLineFormat
	newLineFormat = strings.Replace(newLineFormat, "${{DATE}}", "(?P<date>"+cnf.RegExp["DATE"]+")", -1)
	newLineFormat = strings.Replace(newLineFormat, "${{CLASS}}", "(?P<class>"+cnf.RegExp["CLASS"]+")", -1)
	newLineFormat = strings.Replace(newLineFormat, "${{LEVEL}}", "(?P<level>"+cnf.RegExp["LEVEL"]+")", -1)
	newLineFormat = strings.Replace(newLineFormat, "${{MESSAGE}}", "(?P<message>"+cnf.RegExp["MESSAGE"]+")", -1)
	lgf.NewLineRegExp = regexp.MustCompile(newLineFormat)

	for i := range lgf.NewLineRegExp.SubexpNames() {
		lgf.FieldPos[lgf.NewLineRegExp.SubexpNames()[i]] = i
	}
	if e := recover(); e != nil {
		err = fmt.Errorf("Error parsing regexp:%s", e)
	}
	return lgf, err
}

func (lgf *LogFile) Parse() ([]*commonsLog.Log, error) {
	var err error
	lgf.File.Seek(int64(lgf.StartFrom), 0)

	logScanner := bufio.NewReader(lgf.File)
	logs := make([]*commonsLog.Log, 0)
	var singleLog *commonsLog.Log
	var line string
	var strDate string
	var readed uint64
	for line, err = logScanner.ReadString('\n'); err == nil; line, err = logScanner.ReadString('\n') {
		if lgf.NewLineRegExp.MatchString(line) {
			//log line
			if singleLog != nil {
				lgf.Readed += readed
				readed = 0
				logs = append(logs, singleLog)
			}
			singleLog = new(commonsLog.Log)
			singleLog.Message = lgf.NewLineRegExp.FindStringSubmatch(line)[lgf.FieldPos["message"]]
			singleLog.Level = lgf.NewLineRegExp.FindStringSubmatch(line)[lgf.FieldPos["level"]]
			//singleLog.Class = lgf.NewLineRegExp.FindStringSubmatch(line)[lgf.FieldPos["class"]]
			strDate = lgf.NewLineRegExp.FindStringSubmatch(line)[lgf.FieldPos["date"]]
			dtLog, err := time.Parse(GetConfig().DateFormat, strDate)
			if err != nil {
				return nil, err
			}
			singleLog.Date = dtLog.UnixNano() / 1000000
			readed = uint64(len(line))
		} else {
			//multiple line
			if singleLog != nil {
				readed += uint64(len(line))
				singleLog.Stack += line
			}
		}
	}
	//end log file
	return logs, nil
}
