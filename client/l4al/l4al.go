package main

import (
	"encoding/json"
	"fmt"
	"github.com/mgutz/ansi"
	"github.com/n3wtron/log4all/client"
	"github.com/n3wtron/log4all/commons"
	"gopkg.in/alecthomas/kingpin.v2"
	"io/ioutil"
	"os"
	"strings"
	"time"
)

var (
	app = kingpin.New("l4al", "Log4All Client")

	// Add Command Options
	addCommand              = app.Command("add", "add a log")
	addCmd_Url              = addCommand.Flag("log4allUrl", "Log4All Server url").Short('u').Required().String()
	addCmd_Application      = addCommand.Flag("application", "Application name").Short('a').Required().String()
	addCmd_ApplicationToken = addCommand.Flag("applicationToken", "Application Token").String()
	addCmd_Level            = addCommand.Flag("level", "Application name").Short('l').Required().String()
	addCmd_Message          = addCommand.Arg("message", "message").String()

	// Search Command Options
	searchCommand          = app.Command("search", "search logs")
	searchCmd_Url          = searchCommand.Flag("log4allUrl", "Log4All Server url").Short('u').Required().String()
	searchCmd_Since        = searchCommand.Flag("since", "Since").Short('s').Required().String()
	searchCmd_To           = searchCommand.Flag("to", "To").Short('t').Required().String()
	searchCmd_Applications = searchCommand.Flag("applications", "Application list").Short('a').Strings()
	searchCmd_Levels       = searchCommand.Flag("levels", "Level list").Short('l').Strings()
	searchCmd_MaxResult    = searchCommand.Flag("maxResult", "max result").Short('m').Default("20").Int()
	searchCmd_Page         = searchCommand.Flag("page", "page").Short('p').Default("0").Int()
	searchCmd_SortField    = searchCommand.Flag("orderBy", "order by Field").Short('o').Default("date").String()
	searchCmd_Reverse      = searchCommand.Flag("ascending", "ascending").Short('r').Bool()
	searchCmd_Format       = searchCommand.Flag("format", "output format [json|jsonIntended|plain]").Short('f').Default("json").String()
	searchCmd_Query        = searchCommand.Arg("query", "Query").String()
)

func addCommandExec() {
	cl, err := client.NewClient(*addCmd_Url, *addCmd_Application, *addCmd_ApplicationToken)
	if err != nil {
		printError("Error: %s", err.Error())
		os.Exit(1)
	}
	stat, _ := os.Stdin.Stat()
	stack := ""
	if (stat.Mode() & os.ModeCharDevice) == 0 {
		stackBytes, err := ioutil.ReadAll(os.Stdin)
		if err == nil {
			stack = string(stackBytes)
		}
	}
	lg, err := commons.NewLog(time.Now().UnixNano()/1000000, *addCmd_Level, *addCmd_Message, stack)
	if err != nil {
		printError("Error: %s", err.Error())
		os.Exit(1)
	}
	cl.AddLog(lg)
}

func printError(errMessageFormat string, args ...interface{}) {
	fmt.Println(ansi.Color(fmt.Sprintf(errMessageFormat, args...), "red+h"))
}

func searchCommandExec() {
	if !strings.EqualFold(*searchCmd_Format, "json") && !strings.EqualFold(*searchCmd_Format, "jsonIndented") && !strings.EqualFold(*searchCmd_Format, "plain") {
		printError("Error: format %s not supported", *searchCmd_Format)
		os.Exit(1)
	}

	cl, err := client.NewClient(*searchCmd_Url, *addCmd_Application, *addCmd_ApplicationToken)
	if err != nil {
		printError("Error: %s", err.Error())
		os.Exit(1)
	}
	srcQuery := new(commons.LogSearchParam)
	srcQuery.Applications = *searchCmd_Applications
	dtSince, err := time.Parse("2006-01-02 15:04:05", *searchCmd_Since)
	if err != nil {
		printError("Error: %s", err.Error())
		os.Exit(1)
	}
	srcQuery.DtSince = dtSince.UnixNano() / 1000000
	dtTo, err := time.Parse("2006-01-02 15:04:05", *searchCmd_To)
	if err != nil {
		printError("Error: %s", err.Error())
		os.Exit(1)
	}
	srcQuery.DtTo = dtTo.UnixNano() / 1000000
	srcQuery.Levels = *searchCmd_Levels
	srcQuery.Query = *searchCmd_Query
	srcQuery.MaxResult = *searchCmd_MaxResult
	srcQuery.Page = *searchCmd_Page
	srcQuery.SortField = *searchCmd_SortField
	srcQuery.SortAscending = !(*searchCmd_Reverse)

	logs, err := cl.Search(srcQuery)
	if err != nil {
		printError("Error: %s", err.Error())
		os.Exit(1)
	}
	var result []byte

	if strings.EqualFold(*searchCmd_Format, "json") {
		result, err = json.Marshal(logs)
	}
	if strings.EqualFold(*searchCmd_Format, "jsonIndented") {
		result, err = json.MarshalIndent(logs, "", "\t")
	}
	if strings.EqualFold(*searchCmd_Format, "plain") {
		var plainLogs string
		for _, log := range logs {
			plainLogs = plainLogs + "[" + log.Application + "]: " + log.Date.String() + " " + log.Level + " " + log.Message + "\n"
			if len(log.Stack) > 0 {
				plainLogs = plainLogs + log.Stack
			}
		}
		result = []byte(plainLogs)
	}
	if err != nil {
		printError("Error: %s", err.Error())
		os.Exit(1)
	}
	fmt.Printf("%s\n", string(result))
}

func main() {
	switch kingpin.MustParse(app.Parse(os.Args[1:])) {
	case addCommand.FullCommand():
		addCommandExec()
	case searchCommand.FullCommand():
		searchCommandExec()
	}
}
