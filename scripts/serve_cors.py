#!/usr/bin/env python3
"""Serve a directory over HTTP with permissive CORS so a Feishu page can fetch
local .drawio files (used by the whiteboard import workflow).

    python3 serve_cors.py [port] [directory]

Runs in the foreground; stop it with Ctrl-C or `pkill -f serve_cors.py`.
"""

import http.server
import os
import socketserver
import sys


class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *args):
        pass


def main(argv):
    port = int(argv[1]) if len(argv) > 1 else 8766
    directory = argv[2] if len(argv) > 2 else os.getcwd()
    os.chdir(directory)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", port), Handler) as httpd:
        print(f"serving {directory} at http://127.0.0.1:{port}", flush=True)
        httpd.serve_forever()


if __name__ == "__main__":
    main(sys.argv)
