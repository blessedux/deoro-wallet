#!/usr/bin/env python3
"""Local static preview + Ticket 4 install URL (no Apple certs required to run)."""

from __future__ import annotations

import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from issuer.package import issue_response  # noqa: E402


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def _handle_pass(self, send_body: bool) -> bool:
        parsed = urlparse(self.path)
        if parsed.path not in ("/api/pass", "/api/pass/"):
            return False
        serial = (parse_qs(parsed.query).get("serial") or [""])[0]
        status, content_type, body, headers = issue_response(serial)
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        for key, value in headers.items():
            self.send_header(key, value)
        self.end_headers()
        if send_body:
            self.wfile.write(body)
        return True

    def do_GET(self) -> None:
        if self._handle_pass(send_body=True):
            return
        super().do_GET()

    def do_HEAD(self) -> None:
        if self._handle_pass(send_body=False):
            return
        super().do_HEAD()


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 4173
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"http://127.0.0.1:{port}/")
    print(f"  preview  http://127.0.0.1:{port}/preview/")
    print(f"  counter  http://127.0.0.1:{port}/counter/")
    print(f"  install  http://127.0.0.1:{port}/install/")
    print(f"  pass     http://127.0.0.1:{port}/api/pass?serial=DEORO-10001")
    server.serve_forever()


if __name__ == "__main__":
    main()
