import pytest

from pfl.ast_nodes import ArgDecl, PositDecl
from pfl.desugar import ReadsMatcher, ReadsToken, compile_reads_template
from pfl.diagnostics import DiagnosticCode, DiagnosticError


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
