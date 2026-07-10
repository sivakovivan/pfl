"""Command-line interface for the PFL interpreter."""

import argparse
from collections.abc import Iterable, Sequence
from pathlib import Path
import sys

from pfl.ast_nodes import CaseDecl, Document
from pfl.checker import check_document
from pfl.compiler import compile_theory_rules
from pfl.diagnostics import DiagnosticError
from pfl.engine import FactStore, compile_case_facts, run_inference
from pfl.explain import format_explanation
from pfl.parser import parse_document
from pfl.query import QueryResult, evaluate_case_asks
from pfl.symbols import SymbolTable


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pfl",
        description="Interpret Philosophy Formalization Language files.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    check = commands.add_parser("check", help="parse and validate a PFL file")
    check.add_argument("file", type=Path)
    check.set_defaults(handler=_check_command)

    run = commands.add_parser("run", help="run all cases and ask statements")
    run.add_argument("file", type=Path)
    run.set_defaults(handler=_run_command)

    explain = commands.add_parser(
        "explain",
        help="run cases and explain ask results",
    )
    explain.add_argument("file", type=Path)
    explain.set_defaults(handler=_explain_command)
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
    document, _ = _load_program(args.file)

    print(f"OK: {args.file}")
    print("\nTheories:")
    _print_names(theory.name for theory in document.theories)
    print("\nCases:")
    _print_names(case.name for case in document.cases)
    return 0


def _run_command(args: argparse.Namespace) -> int:
    document, symbols = _load_program(args.file)
    for index, case in enumerate(document.cases):
        if index:
            print()
        _, results = _run_case(case, symbols)
        print(f"Case: {case.name}")
        print(f"Theory: {case.theory_name}")
        for result in results:
            print(f"\nask {result.predicate}")
            print(f"Result: {result.status.value}")
    return 0


def _explain_command(args: argparse.Namespace) -> int:
    document, symbols = _load_program(args.file)
    for index, case in enumerate(document.cases):
        if index:
            print()
        facts, results = _run_case(case, symbols)
        print(f"Case: {case.name}")
        print(f"Theory: {case.theory_name}")
        for result in results:
            print(f"\nask {result.predicate}")
            print(f"Result: {result.status.value}")
            print("\nExplanation:")
            print(format_explanation(result.predicate, facts))
    return 0


def _load_program(path: Path) -> tuple[Document, SymbolTable]:
    document = parse_document(path.read_text(encoding="utf-8"))
    return document, check_document(document)


def _run_case(
    case: CaseDecl,
    symbols: SymbolTable,
) -> tuple[FactStore, tuple[QueryResult, ...]]:
    theory = symbols.theories[case.theory_name]
    facts = compile_case_facts(case, theory)
    run_inference(facts, compile_theory_rules(theory))
    return facts, evaluate_case_asks(case, theory, facts)


def _print_names(names: Iterable[str]) -> None:
    values = tuple(names)
    if not values:
        print("- none")
        return
    for name in values:
        print(f"- {name}")


if __name__ == "__main__":
    raise SystemExit(main())
