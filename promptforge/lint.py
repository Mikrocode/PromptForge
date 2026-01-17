"""Lint engine for PromptForge."""

from __future__ import annotations

from typing import Iterable

from promptforge.issues import Issue
from promptforge.rules import Rule, RULES


class Linter:
    def __init__(self, rules: Iterable[Rule] | None = None) -> None:
        self._rules = list(rules) if rules is not None else list(RULES)

    def lint(self, content: str) -> list[Issue]:
        issues: list[Issue] = []
        for rule in self._rules:
            issues.extend(rule.check(content))
        return issues
