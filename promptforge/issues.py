"""Issue definitions for PromptForge."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Issue:
    rule_id: str
    severity: str
    message: str
    line: int | None = None
    column: int | None = None

    def format(self) -> str:
        location = ""
        if self.line is not None:
            location = f" line {self.line}"
            if self.column is not None:
                location += f":{self.column}"
        return f"{self.severity.upper()} [{self.rule_id}]{location}: {self.message}"
