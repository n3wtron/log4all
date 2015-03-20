package utils

import "regexp"

var tagNameRegexp = "[\\+]{0,1}[\\w|.|-]+"
var tagRegexp = "(#" + tagNameRegexp + ")"
var srcTagRegexp = "([#]{0,1}" + tagNameRegexp + ")"

var valueRegexp = "([a-z|A-Z|0-9|,|.|:|;|_|\\-]+|\"[a-z|A-Z|0-9|,|_|.|\\-|:|;| ]+\")"

var addLogRegexp = tagRegexp + "((:)" + valueRegexp + ")?"

var operatorRegexp = "(=|>|<|>=|<=|!=|\\?=|<<|!<)"
var searchRegexp = tagRegexp + "(" + operatorRegexp + valueRegexp + "){0,1}"

var searchMatcher *regexp.Regexp
var addLogMatcher *regexp.Regexp

func init(){
	addLogMatcher = regexp.MustCompile(addLogRegexp)
	searchMatcher = regexp.MustCompile(searchRegexp)
}

func AddLogMatcher() *regexp.Regexp{
	return addLogMatcher
}

func SearchLogMatcher() *regexp.Regexp{
	return searchMatcher
}