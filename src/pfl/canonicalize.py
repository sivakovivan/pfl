"""Conversion from parsed calls to canonical predicate representations."""

from typing import TypeAlias

from pfl.ast_nodes import DeriveDecl, PositDecl, PredicateCall
from pfl.diagnostics import Diagnostic, DiagnosticCode, DiagnosticError
from pfl.ir import Predicate, PredicatePattern
from pfl.symbols import TheorySymbols


TermDecl: TypeAlias = PositDecl | DeriveDecl


def resolve_term(theory: TheorySymbols, name: str) -> TermDecl:
    """Resolve a posit or derived term under a theory."""

    term = theory.posits.get(name) or theory.derives.get(name)
    if term is None:
        raise DiagnosticError(
            Diagnostic(
                DiagnosticCode.UNDEFINED_TERM,
                f'Term "{name}" is not defined under theory '
                f'"{theory.declaration.name}".',
            )
        )
    return term


def canonicalize_predicate(
    call: PredicateCall,
    theory: TheorySymbols,
) -> Predicate:
    _validate_arity(call, resolve_term(theory, call.name))
    return Predicate(call.name, call.args)


def canonicalize_pattern(
    call: PredicateCall,
    theory: TheorySymbols,
) -> PredicatePattern:
    _validate_arity(call, resolve_term(theory, call.name))
    return PredicatePattern(call.name, call.args)


def _validate_arity(call: PredicateCall, term: TermDecl) -> None:
    expected = len(term.args)
    received = len(call.args)
    if expected == received:
        return
    raise DiagnosticError(
        Diagnostic(
            DiagnosticCode.TYPE_MISMATCH,
            f'Term "{call.name}" expects {expected} argument(s), '
            f"but received {received}.",
        )
    )
