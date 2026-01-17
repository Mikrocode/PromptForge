"""Vercel serverless handler for saving versions."""

from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler

from promptforge.api_utils import read_json, save_version_payload, write_json


class handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        try:
            payload = read_json(self)
        except json.JSONDecodeError:
            write_json(self, {"error": "Invalid JSON"}, status=HTTPStatus.BAD_REQUEST)
            return
        label = payload.get("label", "")
        text = payload.get("text", "")
        if not label:
            write_json(self, {"error": "Label is required"}, status=HTTPStatus.BAD_REQUEST)
            return
        write_json(self, save_version_payload(label, text))

    def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        self.send_error(HTTPStatus.METHOD_NOT_ALLOWED, "Method Not Allowed")

    def log_message(self, format: str, *args: object) -> None:
        return
