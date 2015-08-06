#!/usr/bin/env python

import datetime
import os
import posixpath
import urllib
import SimpleHTTPServer
import SocketServer
from subprocess import call

import cgi

from adoddler import configuration, settings

class AdoddlerHandler( SimpleHTTPServer.SimpleHTTPRequestHandler ) :

    def get_action(self) :
        # Remove the parameters, and then check if this url requires special treatment
        bare_path = self.path.split('?',1)[0]
        return configuration.registered_actions.get( bare_path )

    def end_headers( self ) :
        if self.serving_static :
            self.send_header("Cache-Control", "public, max-age=86400" )
            expires = datetime.datetime.today() + datetime.timedelta(days=1)
            expires = expires.strftime("%a, %d %b %Y %H:%M:%S GMT")
            self.send_header("Expires", expires )

        SimpleHTTPServer.SimpleHTTPRequestHandler.end_headers( self )

    def do_HEAD(self) :
        action = self.get_action()
        if action :
            self.serving_static = False
            action.do_HEAD(self)
        else :
            self.serving_static = True
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_HEAD(self)
        
    def do_GET(self) :
        query = self.path.find('?')
        if query >= 0 :
            self.parameters = cgi.parse_qs(self.path[query+1:], keep_blank_values=1)
        else :
            self.parameters = dict()

        action = self.get_action()
        if action :
            self.serving_static = False
            action.do_GET(self)
        else :
            self.serving_static = True
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)
    
    def do_POST(self) :

        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        if ctype == 'multipart/form-data':
            self.parameters = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers.getheader('content-length'))
            self.parameters = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
        else:
            self.parameters = {}

        action = self.get_action()
        if action :
            self.serving_static = False
            action.do_POST(self)
        else :
            self.serving_static = True
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)


    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.

        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored.
        NOTE. This method was copied from SimpleHTTPServer.py, with one alteration (see below)
        BTW. This code is EVIL, it uses the variable 'path' for two completely different things.

        """
        # abandon query parameters
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        # Don't forget explicit trailing slash when normalizing. Issue17324
        trailing_slash = path.rstrip().endswith('/')
        path = posixpath.normpath(urllib.unquote(path))
        words = path.split('/')
        words = filter(None, words)

        # Serve files from a CUSTOM directory instead of the current directory.
        #path = os.getcwd()
        path = configuration.base_dir

        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir): continue
            path = os.path.join(path, word)
        if trailing_slash:
            path += '/'
        return path

class MyServer(SocketServer.TCPServer):

    # Apparently this is the magic, which allows ctrl+C to kill the server. Grrr.
    allow_reuse_address = True

httpd = MyServer(("", configuration.port), AdoddlerHandler )


print "Adoddle started serving at port : ", configuration.port
httpd.serve_forever()

