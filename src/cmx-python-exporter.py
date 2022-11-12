#!/usr/bin/env python

import re
from BaseHTTPServer import BaseHTTPRequestHandler
from SocketServer import TCPServer
from json import dump as json_dump
import logging

import ctypes, os
ctypes.CDLL('librt.so', mode=ctypes.RTLD_GLOBAL)

import cmx

logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger("cmxhttp")

class CMXHTTPServer(TCPServer):
    allow_reuse_address = True

def render_html(stream):
    stream.write("""<!DOCTYPE html>
<html>
<head><title>CMX Exporter</title></head>
<body>
<a href="/json">view in JSON format</a>
<a href="/metrics">view in Prometheus format</a>
</body>
</html>""")

def render_prometheus(stream):

        for component in cmx.Registry.list():
                if component.name() == "_":
                        continue

                labels = []

                for metric in component.list():
                    if isinstance(metric, cmx.CmxImmutableString):
                        if metric.name() == "prometheus_labels":
                            labels = metric.value().split(" ")
                            labels = filter(lambda label: isValidLabel(label), labels)
                
                labels.append('component="%s"' %component.name().replace("\"", "_"))

                for metric in component.list():

                        if isinstance(metric, cmx.CmxImmutableString):
                                continue

                        name = preparePrometheusMetricName(metric.name())

                        if not isValidMetricName(name):
                                continue

                        stream.write('%s{%s} %d\n' %(name, ", ".join(labels) , metric.value()))

def isValidMetricName(name):
    return re.match(r'^[a-zA-Z_:][a-zA-Z0-9_:]*$', name)

def isValidLabel(label):
    return re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*="[^"]*"$', label)

def preparePrometheusMetricName(string):
        return string.replace(" ","_").replace(".", "_")

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
        elif self.path == "/metrics":
            self.send_response(200, "OK")
            self.send_header("Content-type", "text")
            self.end_headers()
            render_prometheus(self.wfile)
        else:
            self.send_response(404, "Not implemented.")
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write("404 Not found.")

CMXHTTPServer(("", 9976), CMXHTTPHandler).serve_forever()
