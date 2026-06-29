"""Semantic validation for PFL documents."""

from pfl.ast_nodes import ArgDecl, Document
from pfl.diagnostics import Diagnostic, DiagnosticCode, DiagnosticError
from pfl.symbols import SymbolTable, TheorySymbols, build_symbol_table


def check_document(document: Document) -> SymbolTable:
    """Validate a document and return its resolved symbols."""

    symbols = build_symbol_table(document)
    for theory in symbols.theories.values():
        _check_term_kinds(theory)
    _check_case_theories(document, symbols)
    return symbols


def _check_case_theories(document: Document, symbols: SymbolTable) -> None:
    for case in document.cases:
        if case.theory_name in symbols.theories:
            continue
        raise DiagnosticError(
            Diagnostic(
                DiagnosticCode.UNKNOWN_THEORY,
                f'Case "{case.name}" references unknown theory '
                f'"{case.theory_name}".',
            )
        )


def _check_term_kinds(theory: TheorySymbols) -> None:
    for posit in theory.posits.values():
        for arg in posit.args:
            _require_known_kind(theory, arg, f'posit "{posit.name}"')

    for derive in theory.derives.values():
        for arg in derive.args:
            _require_known_kind(theory, arg, f'derive "{derive.name}"')


def _require_known_kind(
    theory: TheorySymbols,
    arg: ArgDecl,
    context: str,
) -> None:
    if arg.kind in theory.kinds:
        return
    raise DiagnosticError(
        Diagnostic(
            DiagnosticCode.UNKNOWN_KIND,
            f'Unknown kind "{arg.kind}" for argument "{arg.name}" in {context}.',
        )
    )
