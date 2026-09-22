"""A status service: it reports which version is running and logs at LOG_LEVEL."""

import logging
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

logging.basicConfig(level=os.environ["LOG_LEVEL"].upper())
log = logging.getLogger("status")
VERSION = os.environ["APP_VERSION"]


class Status(BaseHTTPRequestHandler):
    def do_GET(self):
        body = f"version {VERSION}\n".encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    log.info("starting version %s", VERSION)
    HTTPServer(("0.0.0.0", 8080), Status).serve_forever()
