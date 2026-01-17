"""Issue definitions for PromptForge."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Issue:
    rule_id: str
    message: str
    line: int

    def format(self) -> str:
        return f"ERROR [{self.rule_id}] line {self.line}: {self.message}"
