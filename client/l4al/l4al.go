package main

import (
	"fmt"
	"github.com/n3wtron/log4all/client"
	"github.com/n3wtron/log4all/commons"
	"gopkg.in/alecthomas/kingpin.v2"
	"io/ioutil"
	"os"
	"time"
)

var (
	app              = kingpin.New("l4al", "Log4All Client")
	log4allUrl       = app.Flag("log4allUrl", "Log4All Server url").Short('s').Required().String()
	addCommand       = app.Command("add", "add a log")
	application      = addCommand.Flag("application", "Application name").Short('a').Required().String()
	level            = addCommand.Flag("level", "Application name").Short('l').Required().String()
	applicationToken = addCommand.Arg("applicationToken", "Application Token").String()
	message          = addCommand.Flag("message", "message").Short('m').String()
)

func main() {
	switch kingpin.MustParse(app.Parse(os.Args[1:])) {
	case addCommand.FullCommand():
		cl, err := client.NewClient(*log4allUrl, *application, *applicationToken)
		if err != nil {
			fmt.Printf("Error: %s\n", err.Error())
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
		lg, err := commons.NewLog(time.Now().UnixNano()/1000000, *level, *message, stack)
		if err != nil {
			fmt.Printf("Error: %s\n", err.Error())
			os.Exit(1)
		}
		cl.AddLog(lg)
	}

}
