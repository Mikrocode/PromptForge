"""CLI entry point for PromptForge."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from promptforge.lint import Linter


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="promptforge", description="PromptForge prompt linter.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    lint_parser = subparsers.add_parser("lint", help="Lint a prompt file.")
    lint_parser.add_argument("file", type=Path, help="Path to the prompt text file.")

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "lint":
        linter = Linter()
        try:
            content = args.file.read_text(encoding="utf-8")
        except FileNotFoundError:
            print(f"ERROR: file not found: {args.file}")
            sys.exit(2)

        issues = linter.lint(content)
        if issues:
            for issue in issues:
                print(issue.format())
            sys.exit(1)

        print("No lint errors found.")
        sys.exit(0)


if __name__ == "__main__":
    main()
