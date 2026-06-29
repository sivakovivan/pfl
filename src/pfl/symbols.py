"""Symbol tables for declarations in a PFL document."""

from dataclasses import dataclass

from pfl.ast_nodes import DeriveDecl, Document, KindDecl, PositDecl, TheoryDecl
from pfl.diagnostics import Diagnostic, DiagnosticCode, DiagnosticError


@dataclass(frozen=True)
class TheorySymbols:
    declaration: TheoryDecl
    kinds: dict[str, KindDecl]
    posits: dict[str, PositDecl]
    derives: dict[str, DeriveDecl]


@dataclass(frozen=True)
class SymbolTable:
    theories: dict[str, TheorySymbols]


def build_symbol_table(document: Document) -> SymbolTable:
    """Register declarations and reject duplicate names."""

    theories: dict[str, TheorySymbols] = {}
    for theory in document.theories:
        if theory.name in theories:
            _raise_duplicate("theory", theory.name)
        theories[theory.name] = _build_theory_symbols(theory)
    return SymbolTable(theories)


def _build_theory_symbols(theory: TheoryDecl) -> TheorySymbols:
    kinds: dict[str, KindDecl] = {}
    for kind in theory.kinds:
        if kind.name in kinds:
            _raise_duplicate("kind", kind.name)
        kinds[kind.name] = kind

    posits: dict[str, PositDecl] = {}
    derives: dict[str, DeriveDecl] = {}
    for posit in theory.posits:
        if posit.name in posits or posit.name in derives:
            _raise_duplicate("term", posit.name)
        posits[posit.name] = posit
    for derive in theory.derives:
        if derive.name in posits or derive.name in derives:
            _raise_duplicate("term", derive.name)
        derives[derive.name] = derive

    return TheorySymbols(theory, kinds, posits, derives)


def _raise_duplicate(declaration_type: str, name: str) -> None:
    raise DiagnosticError(
        Diagnostic(
            DiagnosticCode.DUPLICATE_TERM,
            f'Duplicate {declaration_type} declaration "{name}".',
        )
    )
