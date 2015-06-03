package log

import (
	"bufio"
	"fmt"
	"github.com/log4all/agent/config"
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

type SingleLog struct {
	Date    time.Time
	Level   string
	Class   string
	Message string
	Size    int
	Lines   []string
}

func NewLogFile(cnf *config.Config, logFile *os.File, readFrom uint64) (*LogFile, error) {
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

func (lgf *LogFile) Parse() ([]*SingleLog, error) {
	var err error
	lgf.File.Seek(int64(lgf.StartFrom), 0)

	logScanner := bufio.NewReader(lgf.File)
	logs := make([]*SingleLog, 0)
	var singleLog *SingleLog
	var line string
	var strDate string
	for line, err = logScanner.ReadString('\n'); err == nil; line, err = logScanner.ReadString('\n') {
		if lgf.NewLineRegExp.MatchString(line) {
			//log line
			if singleLog != nil {
				lgf.Readed += uint64(singleLog.Size)
			}
			singleLog = new(SingleLog)
			singleLog.Lines = make([]string, 0)
			singleLog.Message = lgf.NewLineRegExp.FindStringSubmatch(line)[lgf.FieldPos["message"]]
			singleLog.Level = lgf.NewLineRegExp.FindStringSubmatch(line)[lgf.FieldPos["level"]]
			singleLog.Class = lgf.NewLineRegExp.FindStringSubmatch(line)[lgf.FieldPos["class"]]
			strDate = lgf.NewLineRegExp.FindStringSubmatch(line)[lgf.FieldPos["date"]]
			singleLog.Date, err = time.Parse(config.GetConfig().DateFormat, strDate)
			if err != nil {
				return nil, err
			}
			singleLog.Size = len(line)
			logs = append(logs, singleLog)
		} else {
			//multiple line
			if singleLog != nil {
				singleLog.Size += len(line)
				singleLog.Lines = append(singleLog.Lines, line)
			}
		}
	}
	//end log file
	return logs, nil
}
