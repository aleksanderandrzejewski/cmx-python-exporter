#!/usr/bin/env python
# encoding: utf-8
# pylint: disable-msg=C0111,W0141
"""python CMX web api"""
# CMX (c) Copyright 2013 CERN
# This software is distributed under the terms of the GNU Lesser General Public Licence version 3
# (LGPL Version 3), copied verbatim in the file .COPYING..
# In applying this licence, CERN does not waive the privileges and immunities granted to it by virtue of its
# status as an Intergovernmental Organization or submit itself to any jurisdiction.
from BaseHTTPServer import BaseHTTPRequestHandler
from SocketServer import TCPServer
from json import dump as json_dump
from cgi import escape
from os import uname
import datetime
from datetime import datetime
import logging

import ctypes, os
ctypes.CDLL('librt.so', mode=ctypes.RTLD_GLOBAL)

import cmx

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger("cmxhttp")
hostinfo = ";".join(uname())

class CMXHTTPServer(TCPServer):
    allow_reuse_address = True

def render_html(stream):
    stream.write("""<!DOCTYPE html>
<html>
<head><title>Simple CMX Webinterface</title></head>
<body>
<pre>{file} running on {host}.
Page generated at {ctime}</pre>
<a href="/json">view in JSON formt</a>""".format(
        file=escape(__file__), host=escape(hostinfo), ctime=datetime.now().ctime() ))

    for component in cmx.Registry.list():
        stream.write("""
<table border=2>
<tr><th colspan=4>{name} ({processId})</th></tr>
<tr><th>Name</th><th>Value</th><th>update</th><th>type</th></tr>""".format(
                name=escape(component.name()), processId=component.processId()))
        for value in component.list():
                stream.write("""
                        <tr>
                                <td>{name}</td>
                                <td class="value"><textarea rows=2 cols=80>{value}</textarea></td>
                                <td>{update}<br />{updateRel}</td>
                                <td>{type}</td>
                        </tr>""".format(name=escape(value.name()),
                                        type=escape(value.__class__.__name__),
                                        value=value.value(),
                                        update=datetime.fromtimestamp(value.mtime()/10.0**6),
                                        updateRel=datetime.now()-datetime.fromtimestamp(value.mtime()/10.0**6)
                                ))
        stream.write("</table>\n<br/>\n")
    stream.write("</body>\n</html>")


class Process:
        def __init__(self, processId, processName, hostName, startTime):
                self.processId = processId
                self.processName = processName
                self.hostName = hostName
                self.startTime = startTime
                self.metrics = {}
        def getName(self):
                return self.processName
        def getProcessId(self):
                return self.processId
        def getHostName(self):
                return self.hostName
        def getStartTime(self):
                return self.startTime

        def getMetrics(self):
                return self.metrics

        def __str__(self):
                return "Process %s (%s)" %(self.processName, self.processId, str(self.metrics))


def buildProcessList():
        # build process map
        processes = {}
        for component in cmx.Registry.list():
                if component.name() == "_":
                        procName = "N/A"
                        hostname = "N/A"
                        startTime = "0"
                        for info in component.list():
                                if info.name() == "process_name":
                                        procName = info.value()
                                elif info.name() == "hostname":
                                        host = info.value()
                                elif info.name() == "start_time":
                                        startTime = info.value()

                        processes[component.processId()] = Process(component.processId(), procName, host, startTime)

        return processes

def render_prometheus(stream):

        processes = buildProcessList()

        for process in processes.values():
                stream.write('start_time{process="%s", host="%s"} %s\n' %(process.getName(), process.getHostName(), process.getStartTime()))

        for component in cmx.Registry.list():
                if component.name() == "_":
                        continue

                try:
                        process_name = processes[component.processId()].getName()
                except:
                        process_name="N/A"

                for metric in component.list():

                        name = metric.name()

                        if isinstance(metric, cmx.CmxImmutableString):
                                continue

                        if "=" in name or "(" in name or "*" in name or "\\" in name:
                                continue

                        stream.write('%s{process="%s", host="%s", component="%s"} %d\n' %(preparePrometheusMetricName(name), process_name, process.getHostName(), preparePrometheusMetricName(component.name()), metric.value()))


def preparePrometheusMetricName(string):
        return string.replace("::", "_").replace(" ","_").replace(".", "_")

def render_json(stream):
    components = map(lambda comp: { "processId" : comp.processId(),
                                    "name" : comp.name(),
                                    "metrics" : map(lambda value: {"name":value.name(),
                                                                   "value":value.value(),
                                                                   "mtime":value.mtime()},
                                                        comp.list()) },
                                cmx.Registry.list())
    return json_dump(components, stream, sort_keys=True, indent=4, separators=(',', ': '))

class CMXHTTPHandler(BaseHTTPRequestHandler):
    def log_message(self, formatstr, *a):
        LOGGER.info(formatstr % a)
    def do_GET(self):
        if self.path == "/":
            self.send_response(200, "OK")
            self.send_header("Content-type", "text/html")
            self.end_headers()
            render_html(self.wfile)
        elif self.path == "/json":
            self.send_response(200, "OK")
            self.send_header("Content-type", "application/json")
            self.end_headers()
            render_json(self.wfile)
        elif self.path == "/prometheus":
            self.send_response(200, "OK")
            self.send_header("Content-type", "text")
            self.end_headers()
            render_prometheus(self.wfile)
        else:
            self.send_response(404, "Not implemented.")
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write("404 Not found.")

print "Listening *:8080"
CMXHTTPServer(("", 8080), CMXHTTPHandler).serve_forever()

# Local Variables:
# python-indent: 4
# indent-tabs-mode: nil
# End:
