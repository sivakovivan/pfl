"""Structured semantic reports for PFL theories."""

from dataclasses import dataclass

from pfl.ast_nodes import (
    ArgDecl,
    Document,
    Expression,
    PredicateCall,
    SurfaceStatement,
    TheoryDecl,
)
from pfl.diagnostics import Diagnostic, DiagnosticCode, DiagnosticError


@dataclass(frozen=True)
class SemanticReport:
    theory_name: str
    kinds: tuple[str, ...]
    posits: tuple[str, ...]
    derives: tuple[str, ...]
    cases: tuple[str, ...]
    asks: tuple[str, ...]


def build_semantic_report(document: Document, theory_name: str) -> SemanticReport:
    """Collect the declarations and uses associated with one theory."""

    theory = _find_theory(document, theory_name)
    cases = tuple(case for case in document.cases if case.theory_name == theory_name)
    return SemanticReport(
        theory_name=theory.name,
        kinds=tuple(kind.name for kind in theory.kinds),
        posits=tuple(_format_signature(posit.name, posit.args) for posit in theory.posits),
        derives=tuple(
            _format_signature(derive.name, derive.args) for derive in theory.derives
        ),
        cases=tuple(f"{case.name} under {case.theory_name}" for case in cases),
        asks=tuple(
            _format_expression(ask.expression)
            for case in cases
            for ask in case.asks
        ),
    )


def format_semantic_report(report: SemanticReport) -> str:
    sections = [
        f"Theory: {report.theory_name}",
        _format_section("Kinds", report.kinds),
        _format_section("Posits", report.posits),
        _format_section("Derived terms", report.derives),
        _format_section("Cases", report.cases),
        _format_section("Ask statements", report.asks),
    ]
    return "\n\n".join(sections)


def _find_theory(document: Document, theory_name: str) -> TheoryDecl:
    for theory in document.theories:
        if theory.name == theory_name:
            return theory
    raise DiagnosticError(
        Diagnostic(
            DiagnosticCode.UNKNOWN_THEORY,
            f'Unknown theory "{theory_name}".',
        )
    )


def _format_signature(name: str, args: tuple[ArgDecl, ...]) -> str:
    formatted_args = ", ".join(f"{arg.name}: {arg.kind}" for arg in args)
    return f"{name}({formatted_args})"


def _format_expression(expression: Expression) -> str:
    if isinstance(expression, PredicateCall):
        return f"{expression.name}({', '.join(expression.args)})"
    if isinstance(expression, SurfaceStatement):
        return expression.text
    return str(expression)


def _format_section(title: str, values: tuple[str, ...]) -> str:
    lines = [f"{title}:"]
    lines.extend(f"- {value}" for value in values)
    if not values:
        lines.append("- none")
    return "\n".join(lines)
