"""Minimal web UI for PromptForge."""

from __future__ import annotations

from dataclasses import asdict
import datetime as dt
import difflib
import json
from pathlib import Path
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

from promptforge.lint import Linter
from promptforge.rules import RULES

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "web_assets"
DATA_DIR = BASE_DIR.parent / "data"


def _read_json(handler: BaseHTTPRequestHandler) -> dict:
    length = int(handler.headers.get("Content-Length", "0"))
    raw = handler.rfile.read(length)
    if not raw:
        return {}
    return json.loads(raw.decode("utf-8"))


def _write_json(handler: BaseHTTPRequestHandler, payload: dict, status: int = 200) -> None:
    data = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


def _sanitize_label(label: str) -> str:
    cleaned = "".join(ch for ch in label if ch.isalnum() or ch in ("-", "_", " ")).strip()
    return cleaned.replace(" ", "_") or "untitled"


def _version_path(file_id: str) -> Path:
    return DATA_DIR / file_id


def _list_versions() -> list[dict]:
    versions: list[dict] = []
    if not DATA_DIR.exists():
        return versions
    for path in sorted(DATA_DIR.glob("*.txt")):
        parts = path.stem.split("_", 1)
        timestamp = parts[0]
        label = parts[1] if len(parts) > 1 else "untitled"
        try:
            parsed_time = dt.datetime.strptime(timestamp, "%Y%m%d%H%M%S")
            timestamp_display = parsed_time.isoformat(timespec="seconds")
        except ValueError:
            timestamp_display = timestamp
        versions.append({"id": path.name, "label": label, "timestamp": timestamp_display})
    return versions


def _load_text(file_id: str) -> str:
    path = _version_path(file_id)
    if not path.exists():
        raise FileNotFoundError(file_id)
    return path.read_text(encoding="utf-8")


class PromptForgeHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler signature
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            index_path = ASSETS_DIR / "index.html"
            content = index_path.read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return
        if parsed.path == "/rules":
            rules_payload = [
                {"rule_id": rule.rule_id, "name": rule.name, "description": rule.description}
                for rule in RULES
            ]
            _write_json(self, {"rules": rules_payload})
            return
        if parsed.path == "/versions/list":
            _write_json(self, {"versions": _list_versions()})
            return
        self.send_error(HTTPStatus.NOT_FOUND, "Not Found")

    def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler signature
        parsed = urlparse(self.path)
        try:
            payload = _read_json(self)
        except json.JSONDecodeError:
            _write_json(self, {"error": "Invalid JSON"}, status=HTTPStatus.BAD_REQUEST)
            return

        if parsed.path == "/lint":
            text = payload.get("text", "")
            linter = Linter()
            issues = [asdict(issue) for issue in linter.lint(text)]
            _write_json(self, {"issues": issues})
            return

        if parsed.path == "/versions/save":
            label = payload.get("label", "")
            text = payload.get("text", "")
            if not label:
                _write_json(self, {"error": "Label is required"}, status=HTTPStatus.BAD_REQUEST)
                return
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            timestamp = dt.datetime.utcnow().strftime("%Y%m%d%H%M%S")
            safe_label = _sanitize_label(label)
            filename = f"{timestamp}_{safe_label}.txt"
            path = _version_path(filename)
            path.write_text(text, encoding="utf-8")
            _write_json(self, {"id": filename})
            return

        if parsed.path == "/versions/diff":
            file_a = payload.get("a")
            file_b = payload.get("b")
            if not file_a or not file_b:
                _write_json(self, {"error": "Both version ids are required"}, status=HTTPStatus.BAD_REQUEST)
                return
            try:
                text_a = _load_text(file_a).splitlines(keepends=True)
                text_b = _load_text(file_b).splitlines(keepends=True)
            except FileNotFoundError:
                _write_json(self, {"error": "Version not found"}, status=HTTPStatus.NOT_FOUND)
                return
            diff = difflib.unified_diff(text_a, text_b, fromfile=file_a, tofile=file_b)
            _write_json(self, {"diff": "".join(diff)})
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Not Found")

    def log_message(self, format: str, *args: object) -> None:
        return


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    server = HTTPServer(("127.0.0.1", 8000), PromptForgeHandler)
    print("PromptForge web UI running at http://127.0.0.1:8000")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
