"""Utility helpers for API handlers."""

from __future__ import annotations

from dataclasses import asdict
import difflib
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler

from promptforge.lint import Linter
from promptforge.rules import RULES
from promptforge.storage import list_versions, load_text, save_version


def read_json(handler: BaseHTTPRequestHandler) -> dict:
    length = int(handler.headers.get("Content-Length", "0"))
    raw = handler.rfile.read(length)
    if not raw:
        return {}
    return json.loads(raw.decode("utf-8"))


def write_json(handler: BaseHTTPRequestHandler, payload: dict, status: int = 200) -> None:
    data = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


def lint_payload(text: str) -> dict:
    linter = Linter()
    issues = [asdict(issue) for issue in linter.lint(text)]
    return {"issues": issues}


def rules_payload() -> dict:
    return {
        "rules": [
            {"rule_id": rule.rule_id, "name": rule.name, "description": rule.description}
            for rule in RULES
        ]
    }


def list_versions_payload() -> dict:
    return {"versions": list_versions()}


def save_version_payload(label: str, text: str) -> dict:
    if not label:
        return {"error": "Label is required"}
    file_id = save_version(label, text)
    return {"id": file_id}


def diff_versions_payload(file_a: str | None, file_b: str | None) -> tuple[dict, int]:
    if not file_a or not file_b:
        return {"error": "Both version ids are required"}, HTTPStatus.BAD_REQUEST
    try:
        text_a = load_text(file_a).splitlines(keepends=True)
        text_b = load_text(file_b).splitlines(keepends=True)
    except ValueError:
        return {"error": "Invalid version id"}, HTTPStatus.BAD_REQUEST
    except FileNotFoundError:
        return {"error": "Version not found"}, HTTPStatus.NOT_FOUND
    diff = difflib.unified_diff(text_a, text_b, fromfile=file_a, tofile=file_b)
    return {"diff": "".join(diff)}, HTTPStatus.OK
