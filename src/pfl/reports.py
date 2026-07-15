"""Structured semantic reports for PFL theories."""

from dataclasses import dataclass

from pfl.ast_nodes import (
    ArgDecl,
    CaseDecl,
    Document,
    Expression,
    PredicateCall,
    SomeExpression,
    SurfaceStatement,
    TheoryDecl,
)
from pfl.desugar import desugar_surface_statement
from pfl.diagnostics import (
    Diagnostic,
    DiagnosticCode,
    DiagnosticError,
    Severity,
)
from pfl.symbols import TheorySymbols, build_symbol_table


@dataclass(frozen=True)
class SemanticReport:
    theory_name: str
    kinds: tuple[str, ...]
    posits: tuple[str, ...]
    derives: tuple[str, ...]
    cases: tuple[str, ...]
    asks: tuple[str, ...]
    dependencies: tuple["DerivedDependencies", ...] = ()
    semantic_debt: tuple["SemanticDebt", ...] = ()


@dataclass(frozen=True)
class DerivedDependencies:
    term_name: str
    dependencies: tuple[str, ...]


@dataclass(frozen=True)
class SemanticDebt:
    term_name: str
    context: str


def build_semantic_report(document: Document, theory_name: str) -> SemanticReport:
    """Collect the declarations and uses associated with one theory."""

    theory = _find_theory(document, theory_name)
    theory_symbols = build_symbol_table(document).theories[theory_name]
    cases = tuple(case for case in document.cases if case.theory_name == theory_name)
    known_terms = {posit.name for posit in theory.posits} | {
        derive.name for derive in theory.derives
    }
    return SemanticReport(
        theory_name=theory.name,
        kinds=tuple(kind.name for kind in theory.kinds),
        posits=tuple(
            _format_signature(posit.name, posit.args) for posit in theory.posits
        ),
        derives=tuple(
            _format_signature(derive.name, derive.args) for derive in theory.derives
        ),
        cases=tuple(f"{case.name} under {case.theory_name}" for case in cases),
        asks=tuple(
            _format_expression(ask.expression) for case in cases for ask in case.asks
        ),
        dependencies=tuple(
            DerivedDependencies(
                derive.name,
                tuple(
                    dict.fromkeys(
                        call.name
                        for expression in derive.body
                        for call in _predicate_calls(expression, theory_symbols)
                    )
                ),
            )
            for derive in theory.derives
        ),
        semantic_debt=_find_semantic_debt(
            theory,
            cases,
            known_terms,
            theory_symbols,
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
        _format_dependencies(report.dependencies),
        _format_semantic_debt(report.semantic_debt),
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


def _format_dependencies(dependencies: tuple[DerivedDependencies, ...]) -> str:
    lines = ["Dependencies:"]
    if not dependencies:
        lines.append("- none")
        return "\n".join(lines)

    for derived in dependencies:
        lines.append(f"- {derived.term_name}")
        lines.append("  depends on:")
        if derived.dependencies:
            lines.extend(f"  - {name}" for name in derived.dependencies)
        else:
            lines.append("  - none")
    return "\n".join(lines)


def semantic_debt_diagnostics(report: SemanticReport) -> tuple[Diagnostic, ...]:
    return tuple(
        Diagnostic(
            DiagnosticCode.SEMANTIC_DEBT,
            f'Unknown term "{debt.term_name}" appears in {debt.context}.',
            Severity.WARNING,
        )
        for debt in report.semantic_debt
    )


def _find_semantic_debt(
    theory: TheoryDecl,
    cases: tuple[CaseDecl, ...],
    known_terms: set[str],
    theory_symbols: TheorySymbols,
) -> tuple[SemanticDebt, ...]:
    debt: list[SemanticDebt] = []
    for derive in theory.derives:
        for expression in derive.body:
            _record_unknown(
                expression,
                known_terms,
                f'derive "{derive.name}"',
                debt,
                theory_symbols,
            )
    for case in cases:
        for expression in case.facts:
            _record_unknown(
                expression,
                known_terms,
                f'case "{case.name}"',
                debt,
                theory_symbols,
            )
        for ask in case.asks:
            _record_unknown(
                ask.expression,
                known_terms,
                f'ask in case "{case.name}"',
                debt,
                theory_symbols,
            )
    return tuple(dict.fromkeys(debt))


def _record_unknown(
    expression: Expression,
    known_terms: set[str],
    context: str,
    debt: list[SemanticDebt],
    theory: TheorySymbols,
) -> None:
    for call in _predicate_calls(expression, theory):
        if call.name not in known_terms:
            debt.append(SemanticDebt(call.name, context))


def _predicate_calls(
    expression: Expression,
    theory: TheorySymbols,
) -> tuple[PredicateCall, ...]:
    if isinstance(expression, PredicateCall):
        return (expression,)
    if isinstance(expression, SurfaceStatement):
        try:
            return (desugar_surface_statement(expression, theory),)
        except DiagnosticError:
            return ()
    if isinstance(expression, SomeExpression):
        return tuple(
            call
            for child in expression.body
            for call in _predicate_calls(child, theory)
        )
    return ()


def _format_semantic_debt(debt: tuple[SemanticDebt, ...]) -> str:
    lines = ["Semantic debt:"]
    if debt:
        lines.extend(f"- {item.term_name} ({item.context})" for item in debt)
    else:
        lines.append("- none")
    return "\n".join(lines)
