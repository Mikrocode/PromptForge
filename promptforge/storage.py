"""Storage helpers for PromptForge versions."""

from __future__ import annotations

import datetime as dt
import os
from pathlib import Path

DATA_DIR = Path(os.getenv("PROMPTFORGE_DATA_DIR", "/tmp/promptforge-data"))


def sanitize_label(label: str) -> str:
    cleaned = "".join(ch for ch in label if ch.isalnum() or ch in ("-", "_", " ")).strip()
    return cleaned.replace(" ", "_") or "untitled"


def version_path(file_id: str) -> Path:
    return DATA_DIR / file_id


def list_versions() -> list[dict]:
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


def load_text(file_id: str) -> str:
    path = version_path(file_id)
    if not path.exists():
        raise FileNotFoundError(file_id)
    return path.read_text(encoding="utf-8")


def save_version(label: str, text: str) -> str:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = dt.datetime.utcnow().strftime("%Y%m%d%H%M%S")
    safe_label = sanitize_label(label)
    filename = f"{timestamp}_{safe_label}.txt"
    path = version_path(filename)
    path.write_text(text, encoding="utf-8")
    return filename
