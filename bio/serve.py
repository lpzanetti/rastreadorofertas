#!/usr/bin/env python3
"""Static server + proxy GCS com CORS para desenvolvimento local."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

REMOTE_URL = "https://storage.googleapis.com/rastreador-ofertas-lp/produtos/atual.json"
PROXY_PATH = "/proxy/atual.json"
PORT = 8765


class Handler(SimpleHTTPRequestHandler):
    def end_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, HEAD, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.end_headers()

    def do_GET(self) -> None:
        if self.path.split("?", 1)[0] == PROXY_PATH:
            self.proxy_remote()
            return
        super().do_GET()

    def proxy_remote(self) -> None:
        try:
            request = urllib.request.Request(
                REMOTE_URL,
                headers={"User-Agent": "rastreador-bio-proxy/1.0"},
            )
            with urllib.request.urlopen(request, timeout=10) as response:
                body = response.read()
                content_type = response.headers.get("Content-Type", "application/json")
            # valida JSON para falhar cedo se o feed vier quebrado
            json.loads(body.decode("utf-8"))
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, UnicodeDecodeError) as error:
            message = json.dumps({"error": str(error)}).encode("utf-8")
            self.send_response(502)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(message)))
            self.end_headers()
            self.wfile.write(message)


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Serving on http://127.0.0.1:{PORT}")
    print(f"GCS proxy on http://127.0.0.1:{PORT}{PROXY_PATH}")
    server.serve_forever()
