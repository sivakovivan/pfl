import pytest

from pfl.ast_nodes import (
    DeriveDecl,
    Document,
    KindDecl,
    PositDecl,
    TheoryDecl,
)
from pfl.diagnostics import DiagnosticCode, DiagnosticError
from pfl.symbols import build_symbol_table


def test_builds_theory_symbol_registries() -> None:
    theory = TheoryDecl(
        "ExampleTheory",
        kinds=(KindDecl("Subject"),),
        posits=(PositDecl("chooses", ()),),
        derives=(DeriveDecl("favourable_outcome", (), ()),),
    )

    symbols = build_symbol_table(Document(theories=(theory,)))

    theory_symbols = symbols.theories["ExampleTheory"]
    assert list(theory_symbols.kinds) == ["Subject"]
    assert list(theory_symbols.posits) == ["chooses"]
    assert list(theory_symbols.derives) == ["favourable_outcome"]


def test_rejects_duplicate_kind() -> None:
    theory = TheoryDecl(
        "ExampleTheory",
        kinds=(KindDecl("Subject"), KindDecl("Subject")),
    )

    with pytest.raises(DiagnosticError) as raised:
        build_symbol_table(Document(theories=(theory,)))

    assert raised.value.diagnostic.code is DiagnosticCode.DUPLICATE_TERM
    assert "Duplicate kind" in raised.value.diagnostic.message


def test_rejects_duplicate_term_across_posit_and_derive() -> None:
    theory = TheoryDecl(
        "ExampleTheory",
        posits=(PositDecl("chooses", ()),),
        derives=(DeriveDecl("chooses", (), ()),),
    )

    with pytest.raises(DiagnosticError) as raised:
        build_symbol_table(Document(theories=(theory,)))

    assert raised.value.diagnostic.code is DiagnosticCode.DUPLICATE_TERM
    assert "Duplicate term" in raised.value.diagnostic.message
