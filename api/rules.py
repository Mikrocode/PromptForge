"""Vercel serverless handler for rules."""

from __future__ import annotations

from http import HTTPStatus
from http.server import BaseHTTPRequestHandler

from promptforge.api_utils import rules_payload, write_json


class handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        write_json(self, rules_payload())

    def do_POST(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        self.send_error(HTTPStatus.METHOD_NOT_ALLOWED, "Method Not Allowed")

    def log_message(self, format: str, *args: object) -> None:
        return
