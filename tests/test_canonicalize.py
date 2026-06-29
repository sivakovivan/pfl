import pytest

from pfl.ast_nodes import ArgDecl, Document, PositDecl, PredicateCall, TheoryDecl
from pfl.canonicalize import canonicalize_pattern, canonicalize_predicate
from pfl.diagnostics import DiagnosticCode, DiagnosticError
from pfl.ir import Predicate, PredicatePattern
from pfl.symbols import TheorySymbols, build_symbol_table


def _theory_symbols() -> TheorySymbols:
    theory = TheoryDecl(
        "ExampleTheory",
        posits=(
            PositDecl(
                "prefers",
                (ArgDecl("actor", "Subject"), ArgDecl("option", "Option")),
            ),
        ),
    )
    return build_symbol_table(Document(theories=(theory,))).theories["ExampleTheory"]


def test_canonicalizes_known_predicate_call() -> None:
    call = PredicateCall("prefers", ("alice", "optionA"))

    assert canonicalize_predicate(call, _theory_symbols()) == Predicate(
        "prefers", ("alice", "optionA")
    )
    assert canonicalize_pattern(call, _theory_symbols()) == PredicatePattern(
        "prefers", ("alice", "optionA")
    )


def test_rejects_wrong_predicate_arity() -> None:
    with pytest.raises(DiagnosticError) as raised:
        canonicalize_predicate(PredicateCall("prefers", ("alice",)), _theory_symbols())

    assert raised.value.diagnostic.code is DiagnosticCode.TYPE_MISMATCH
    assert "expects 2 argument(s)" in raised.value.diagnostic.message


def test_rejects_unknown_predicate_term() -> None:
    with pytest.raises(DiagnosticError) as raised:
        canonicalize_predicate(PredicateCall("desires", ()), _theory_symbols())

    assert raised.value.diagnostic.code is DiagnosticCode.UNDEFINED_TERM
