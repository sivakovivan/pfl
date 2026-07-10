"""Command-line interface for the PFL interpreter."""

import argparse
from collections.abc import Iterable, Sequence
from pathlib import Path
import sys

from pfl.checker import check_document
from pfl.diagnostics import DiagnosticError
from pfl.parser import parse_document


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pfl",
        description="Interpret Philosophy Formalization Language files.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    check = commands.add_parser("check", help="parse and validate a PFL file")
    check.add_argument("file", type=Path)
    check.set_defaults(handler=_check_command)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except DiagnosticError as error:
        print(error, file=sys.stderr)
        return 1
    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


def _check_command(args: argparse.Namespace) -> int:
    document = parse_document(args.file.read_text(encoding="utf-8"))
    check_document(document)

    print(f"OK: {args.file}")
    print("\nTheories:")
    _print_names(theory.name for theory in document.theories)
    print("\nCases:")
    _print_names(case.name for case in document.cases)
    return 0


def _print_names(names: Iterable[str]) -> None:
    values = tuple(names)
    if not values:
        print("- none")
        return
    for name in values:
        print(f"- {name}")


if __name__ == "__main__":
    raise SystemExit(main())
