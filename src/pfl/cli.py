"""Command-line interface for the PFL interpreter."""

import argparse
import sys
from collections.abc import Iterable, Sequence
from pathlib import Path

from pfl.ast_nodes import CaseDecl, Document, PredicateCall
from pfl.canonicalize import canonicalize_predicate
from pfl.checker import check_document
from pfl.compiler import compile_theory_rules
from pfl.diagnostics import DiagnosticError
from pfl.engine import FactStore, compile_case_facts, run_inference
from pfl.explain import format_explanation
from pfl.parser import parse_document
from pfl.query import QueryResult, evaluate_case_asks
from pfl.reports import build_semantic_report, format_semantic_report
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

    report = commands.add_parser("report", help="print semantic reports")
    report.add_argument("file", type=Path)
    report.set_defaults(handler=_report_command)

    desugar = commands.add_parser("desugar", help="print canonical PFL forms")
    desugar.add_argument("file", type=Path)
    desugar.set_defaults(handler=_desugar_command)
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


def _report_command(args: argparse.Namespace) -> int:
    document, _ = _load_program(args.file)
    for index, theory in enumerate(document.theories):
        if index:
            print()
        report = build_semantic_report(document, theory.name)
        print(format_semantic_report(report))
    return 0


def _desugar_command(args: argparse.Namespace) -> int:
    document, symbols = _load_program(args.file)
    for index, theory_decl in enumerate(document.theories):
        if index:
            print()
        theory = symbols.theories[theory_decl.name]
        print(f"Theory: {theory_decl.name}")
        print("Rules:")
        rules = compile_theory_rules(theory)
        _print_names(str(rule) for rule in rules)

        cases = tuple(
            case for case in document.cases if case.theory_name == theory_decl.name
        )
        for case in cases:
            print(f"\nCase: {case.name}")
            print("Facts:")
            facts = compile_case_facts(case, theory)
            _print_names(str(fact) for fact in facts)
            print("Asks:")
            canonical_asks = (
                canonicalize_predicate(ask.expression, theory)
                for ask in case.asks
                if isinstance(ask.expression, PredicateCall)
            )
            _print_names(str(ask) for ask in canonical_asks)
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
