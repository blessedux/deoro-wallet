"""Vercel serverless install URL: GET /api/pass?serial=DEORO-10001"""

from __future__ import annotations

import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from issuer.package import issue_response  # noqa: E402


class handler(BaseHTTPRequestHandler):
    def log_message(self, *_args) -> None:
        return

    def do_GET(self) -> None:
        query = parse_qs(urlparse(self.path).query)
        serial = (query.get("serial") or [""])[0]
        status, content_type, body, headers = issue_response(serial)
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        for key, value in headers.items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)
