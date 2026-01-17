"""Rule definitions for PromptForge linting."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable

from promptforge.issues import Issue


@dataclass(frozen=True)
class Rule:
    rule_id: str
    name: str
    description: str

    def check(self, content: str) -> list[Issue]:
        raise NotImplementedError


def _line_number(content: str, index: int) -> int:
    return content.count("\n", 0, index) + 1


@dataclass(frozen=True)
class MissingOutputFormatRule(Rule):
    format_markers: tuple[str, ...] = (
        "json",
        "yaml",
        "csv",
        "markdown",
        "table",
        "bullet",
        "bulleted",
        "list",
        "prose",
        "paragraph",
        "paragraphs",
    )

    def check(self, content: str) -> list[Issue]:
        lowered = content.lower()
        if any(marker in lowered for marker in self.format_markers):
            return []
        return [
            Issue(
                rule_id=self.rule_id,
                severity="error",
                message="Missing explicit output format (e.g., bullets, JSON, prose).",
                line=1,
            )
        ]


@dataclass(frozen=True)
class VagueVerbsRule(Rule):
    vague_verbs: tuple[str, ...] = ("improve", "optimize", "enhance", "better")

    def check(self, content: str) -> list[Issue]:
        issues: list[Issue] = []
        for verb in self.vague_verbs:
            pattern = re.compile(rf"\b{re.escape(verb)}\b", re.IGNORECASE)
            for match in pattern.finditer(content):
                issues.append(
                    Issue(
                        rule_id=self.rule_id,
                        severity="error",
                        message=f"Vague verb '{match.group(0)}' found; be specific.",
                        line=_line_number(content, match.start()),
                    )
                )
        return issues


@dataclass(frozen=True)
class ContradictoryConstraintsRule(Rule):
    concise_markers: tuple[str, ...] = (
        "concise",
        "brief",
        "short",
        "succinct",
    )
    detailed_markers: tuple[str, ...] = (
        "in detail",
        "detailed",
        "thorough",
        "comprehensive",
        "explain in detail",
    )

    def check(self, content: str) -> list[Issue]:
        lowered = content.lower()
        has_concise = any(marker in lowered for marker in self.concise_markers)
        has_detailed = any(marker in lowered for marker in self.detailed_markers)
        if has_concise and has_detailed:
            return [
                Issue(
                    rule_id=self.rule_id,
                    severity="error",
                    message="Contradictory constraints: concise and detailed requirements conflict.",
                    line=1,
                )
            ]
        return []


@dataclass(frozen=True)
class MissingAudienceRule(Rule):
    audience_markers: tuple[str, ...] = (
        "audience",
        "target audience",
        "intended for",
        "aimed at",
    )
    role_markers: tuple[str, ...] = (
        "beginner",
        "expert",
        "engineer",
        "developer",
        "manager",
        "student",
        "customer",
        "stakeholder",
        "user",
        "reader",
    )

    def check(self, content: str) -> list[Issue]:
        lowered = content.lower()
        if any(marker in lowered for marker in self.audience_markers):
            return []
        role_pattern = re.compile(
            rf"\bfor\s+(?:a|an|the)?\s*(?:{'|'.join(self.role_markers)})\b",
            re.IGNORECASE,
        )
        if role_pattern.search(content):
            return []
        return [
            Issue(
                rule_id=self.rule_id,
                severity="error",
                message="Missing audience definition (who the prompt is for).",
                line=1,
            )
        ]


@dataclass(frozen=True)
class MissingLengthConstraintRule(Rule):
    length_markers: tuple[str, ...] = (
        "word",
        "words",
        "sentence",
        "sentences",
        "paragraph",
        "paragraphs",
        "bullet",
        "bullets",
        "character",
        "characters",
        "max",
        "maximum",
        "limit",
        "at most",
        "no more than",
        "under",
        "less than",
        "brief",
        "concise",
        "short",
        "succinct",
    )

    def check(self, content: str) -> list[Issue]:
        lowered = content.lower()
        numeric_pattern = re.compile(r"\b\d+\b")
        has_numeric = bool(numeric_pattern.search(content))
        has_marker = any(marker in lowered for marker in self.length_markers)
        if has_numeric or has_marker:
            return []
        return [
            Issue(
                rule_id=self.rule_id,
                severity="error",
                message="Missing length or scope constraint (e.g., word count, max length).",
                line=1,
            )
        ]


RULES: Iterable[Rule] = (
    MissingOutputFormatRule(
        "PF001",
        "Output format",
        "Prompt must request an explicit output format.",
    ),
    VagueVerbsRule(
        "PF002",
        "Vague verbs",
        "Prompt must avoid vague verbs without measurable targets.",
    ),
    ContradictoryConstraintsRule(
        "PF003",
        "Contradictory constraints",
        "Prompt must not contain conflicting constraints.",
    ),
    MissingAudienceRule(
        "PF004",
        "Audience definition",
        "Prompt must define the intended audience.",
    ),
    MissingLengthConstraintRule(
        "PF005",
        "Length or scope",
        "Prompt must include length or scope constraints.",
    ),
)
