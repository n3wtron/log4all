#!/usr/bin/env python2
import json
from optparse import OptionParser
import sys
import urllib
import urllib2


def main():
    parser = OptionParser()
    parser.add_option("-l", "--log4all-host", dest="host", action="store", help="log4all server url",
                      default="http://localhost:6543")
    (options, args) = parser.parse_args(sys.argv)
    host = options.host+"/api/logs/add"
    msg = args[1]
    data = json.dumps({'log': msg})
    req = urllib2.Request(host, data, {'Content-Type': 'application/json'})
    res = urllib2.urlopen(req)
    result = json.loads(res.read())
    if result['result'] == 'success':
        print("Log added")
    else:
        print("Log not added:"+result['result'])

if __name__ == '__main__':
    main()
