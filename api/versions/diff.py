"""Vercel serverless handler for diffing versions."""

from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler

from promptforge.api_utils import diff_versions_payload, read_json, write_json


class handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        try:
            payload = read_json(self)
        except json.JSONDecodeError:
            write_json(self, {"error": "Invalid JSON"}, status=HTTPStatus.BAD_REQUEST)
            return
        file_a = payload.get("a")
        file_b = payload.get("b")
        payload, status = diff_versions_payload(file_a, file_b)
        write_json(self, payload, status=status)

    def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        self.send_error(HTTPStatus.METHOD_NOT_ALLOWED, "Method Not Allowed")

    def log_message(self, format: str, *args: object) -> None:
        return
