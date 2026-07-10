import pytest

from pfl.ast_nodes import (
    ArgDecl,
    Document,
    PositDecl,
    PredicateCall,
    SurfaceStatement,
    TheoryDecl,
)
from pfl.desugar import (
    ReadsMatcher,
    ReadsToken,
    compile_reads_template,
    desugar_surface_statement,
    match_reads_template,
)
from pfl.diagnostics import DiagnosticCode, DiagnosticError
from pfl.symbols import build_symbol_table


def test_compiles_reads_template_into_tokens() -> None:
    posit = PositDecl(
        "prefers",
        (ArgDecl("actor", "Subject"), ArgDecl("option", "Option")),
        "{actor} prefers {option}",
    )

    matcher = compile_reads_template(posit)

    assert matcher == ReadsMatcher(
        "prefers",
        ("actor", "option"),
        (
            ReadsToken("actor", is_placeholder=True),
            ReadsToken("prefers"),
            ReadsToken("option", is_placeholder=True),
        ),
    )


def test_rejects_placeholder_without_matching_posit_argument() -> None:
    posit = PositDecl(
        "prefers",
        (ArgDecl("actor", "Subject"),),
        "{actor} prefers {option}",
    )

    with pytest.raises(DiagnosticError) as raised:
        compile_reads_template(posit)

    assert raised.value.diagnostic.code is DiagnosticCode.MALFORMED_POSIT
    assert 'placeholder "option"' in raised.value.diagnostic.message


def test_matches_surface_statement_to_canonical_call() -> None:
    matcher = ReadsMatcher(
        "prefers",
        ("actor", "option"),
        (
            ReadsToken("actor", is_placeholder=True),
            ReadsToken("prefers"),
            ReadsToken("option", is_placeholder=True),
        ),
    )

    assert match_reads_template(
        SurfaceStatement("alice prefers optionA"), matcher
    ) == PredicateCall("prefers", ("alice", "optionA"))


def test_desugars_statement_through_theory_reads_templates() -> None:
    posit = PositDecl(
        "chooses",
        (ArgDecl("actor", "Subject"), ArgDecl("option", "Option")),
        "{actor} chooses {option}",
    )
    theory = TheoryDecl("ExampleTheory", posits=(posit,))
    symbols = build_symbol_table(Document(theories=(theory,)))

    call = desugar_surface_statement(
        SurfaceStatement("alice chooses optionA"),
        symbols.theories["ExampleTheory"],
    )

    assert call == PredicateCall("chooses", ("alice", "optionA"))


def test_rejects_ambiguous_reads_templates() -> None:
    parameters = (
        ArgDecl("actor", "Subject"),
        ArgDecl("option", "Option"),
    )
    theory = TheoryDecl(
        "ExampleTheory",
        posits=(
            PositDecl("prefers", parameters, "{actor} likes {option}"),
            PositDecl("favours", parameters, "{actor} likes {option}"),
        ),
    )
    symbols = build_symbol_table(Document(theories=(theory,)))

    with pytest.raises(DiagnosticError) as raised:
        desugar_surface_statement(
            SurfaceStatement("alice likes optionA"),
            symbols.theories["ExampleTheory"],
        )

    assert raised.value.diagnostic.code is DiagnosticCode.AMBIGUOUS_READS
    assert "prefers, favours" in raised.value.diagnostic.message
