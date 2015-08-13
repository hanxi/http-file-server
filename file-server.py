#!/usr/bin/env python
# coding: utf-8

import os
import sys
import urllib
import codecs
import glob
import commands
import time
import re
import BaseHTTPServer
import SocketServer
import mimetypes
import json

reload(sys)
sys.setdefaultencoding('utf-8')
mimetypes.init()

g_filepath = sys.argv[1]
if g_filepath[-1]!=os.sep:
    g_filepath += os.sep

def transDicts(params):
    dicts={}
    if len(params)==0:
        return
    params = params.split('&')
    for param in params:
        keyvalue = param.split('=')
        key = keyvalue[0]
        value = keyvalue[1]
        value = urllib.unquote_plus(value).decode("utf-8", 'ignore')
        dicts[key] = value
    return dicts

class HTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def end_headers (self):
        self.send_header('access-control-allow-origin', '*')
        BaseHTTPServer.BaseHTTPRequestHandler.end_headers(self)

    def do_GET(self):
        query = urllib.splitquery(self.path)
        path = query[0]
        queryParams = {}

        if '?' in self.path:
            if query[1]:
                queryParams = transDicts(query[1])

        fn = "%s%s" % (g_filepath, path)
        fn = urllib.unquote_plus(fn).decode("utf-8", 'ignore')
        fn = fn.replace("/",os.sep)

        content = ""
        self.send_response(200)
        self.send_header("content-type","application/json")
        if os.path.isfile(fn):
            f = open(fn, "rb")
            content = f.read()
            f.close()
            contenttype,_ = mimetypes.guess_type(fn)
            if contenttype:
                self.send_header("content-type",contenttype)
        elif os.path.isdir(fn):
            filelist = []
            for filename in os.listdir(fn):
                if filename[0] != ".":
                    filepath = "%s/%s" % (fn, filename)
                    if os.path.isdir(filepath):
                        filename += os.sep
                    filelist.append(filename)
            content = json.dumps(filelist)

        self.end_headers()
        self.wfile.write(content)

    def do_POST(self):
        query = urllib.splitquery(self.path)
        path = query[0]
        queryParams = {}

        if '?' in self.path:
            if query[1]:
                queryParams = transDicts(query[1])

        content = "{result=0, msg = 'OK'}"
        if path=='/upload':
            if queryParams.has_key("name"):
                filesize = int(self.headers['content-length'])
                filecontent = self.rfile.read(filesize)
                fn = queryParams["name"]
                fn = "%s%s" % (g_filepath, fn)
                dirname = os.path.dirname(fn)
                if not os.path.exists(dirname):
                    os.makedirs(dirname)
                if os.path.isdir(fn):
                    content = "{result=1, msg = 'File name is directory.'}"
                else:
                    f = open(fn,'wb')
                    f.write(filecontent)
                    f.close()
            else:
                content = "{result=2, msg = 'Need file name.'}"
        else:
            content = "{result=3, msg = 'No this API.'}"

        self.send_response(200)
        self.send_header("content-type","application/json")
        self.end_headers()
        self.wfile.write(content)

class ThreadingHTTPServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
    pass

def run(port):
    print 'HTTP File Server Started at port:', port
    server_address = ('', port)
    httpd = ThreadingHTTPServer(('', port), HTTPRequestHandler)
    httpd.serve_forever()

if __name__=='__main__':
    port = 8000
    if len(sys.argv)==3:
        port = int(sys.argv[2])

    run(port)

