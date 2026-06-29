import pytest

from pfl.ast_nodes import (
    ArgDecl,
    CaseDecl,
    DeriveDecl,
    Document,
    KindDecl,
    LetDecl,
    PositDecl,
    PredicateCall,
    TheoryDecl,
)
from pfl.checker import check_document
from pfl.diagnostics import DiagnosticCode, DiagnosticError


def test_accepts_known_kinds_in_term_signatures() -> None:
    theory = TheoryDecl(
        "ExampleTheory",
        kinds=(KindDecl("Subject"),),
        posits=(PositDecl("chooses", (ArgDecl("actor", "Subject"),)),),
        derives=(
            DeriveDecl(
                "acts",
                (ArgDecl("actor", "Subject"),),
                (),
            ),
        ),
    )

    symbols = check_document(Document(theories=(theory,)))

    assert "ExampleTheory" in symbols.theories


@pytest.mark.parametrize(
    "theory",
    [
        TheoryDecl(
            "ExampleTheory",
            posits=(PositDecl("chooses", (ArgDecl("actor", "Subject"),)),),
        ),
        TheoryDecl(
            "ExampleTheory",
            derives=(
                DeriveDecl("acts", (ArgDecl("actor", "Subject"),), ()),
            ),
        ),
    ],
)
def test_rejects_unknown_kinds_in_term_signatures(theory: TheoryDecl) -> None:
    with pytest.raises(DiagnosticError) as raised:
        check_document(Document(theories=(theory,)))

    assert raised.value.diagnostic.code is DiagnosticCode.UNKNOWN_KIND
    assert 'Unknown kind "Subject"' in raised.value.diagnostic.message


def test_rejects_case_under_unknown_theory() -> None:
    case = CaseDecl("SpecificChoiceCase", "MissingTheory")

    with pytest.raises(DiagnosticError) as raised:
        check_document(Document(cases=(case,)))

    assert raised.value.diagnostic.code is DiagnosticCode.UNKNOWN_THEORY
    assert 'unknown theory "MissingTheory"' in raised.value.diagnostic.message


def test_rejects_unknown_kind_in_case_let() -> None:
    theory = TheoryDecl("ExampleTheory", kinds=(KindDecl("Subject"),))
    case = CaseDecl(
        "SpecificChoiceCase",
        "ExampleTheory",
        lets=(LetDecl("optionA", "Option"),),
    )

    with pytest.raises(DiagnosticError) as raised:
        check_document(Document(theories=(theory,), cases=(case,)))

    assert raised.value.diagnostic.code is DiagnosticCode.UNKNOWN_KIND
    assert 'instance "optionA"' in raised.value.diagnostic.message


def test_rejects_duplicate_case_let_name() -> None:
    theory = TheoryDecl("ExampleTheory", kinds=(KindDecl("Subject"),))
    case = CaseDecl(
        "SpecificChoiceCase",
        "ExampleTheory",
        lets=(
            LetDecl("alice", "Subject"),
            LetDecl("alice", "Subject"),
        ),
    )

    with pytest.raises(DiagnosticError) as raised:
        check_document(Document(theories=(theory,), cases=(case,)))

    assert raised.value.diagnostic.code is DiagnosticCode.DUPLICATE_TERM
    assert 'Duplicate let declaration "alice"' in raised.value.diagnostic.message


def test_accepts_well_typed_canonical_case_fact() -> None:
    theory = TheoryDecl(
        "ExampleTheory",
        kinds=(KindDecl("Subject"), KindDecl("Option")),
        posits=(
            PositDecl(
                "prefers",
                (ArgDecl("actor", "Subject"), ArgDecl("option", "Option")),
            ),
        ),
    )
    case = CaseDecl(
        "SpecificChoiceCase",
        "ExampleTheory",
        lets=(LetDecl("alice", "Subject"), LetDecl("optionA", "Option")),
        facts=(PredicateCall("prefers", ("alice", "optionA")),),
    )

    check_document(Document(theories=(theory,), cases=(case,)))


def test_rejects_wrong_argument_kind_in_canonical_case_fact() -> None:
    theory = TheoryDecl(
        "ExampleTheory",
        kinds=(KindDecl("Subject"), KindDecl("Option")),
        posits=(
            PositDecl(
                "prefers",
                (ArgDecl("actor", "Subject"), ArgDecl("option", "Option")),
            ),
        ),
    )
    case = CaseDecl(
        "SpecificChoiceCase",
        "ExampleTheory",
        lets=(LetDecl("alice", "Subject"), LetDecl("bob", "Subject")),
        facts=(PredicateCall("prefers", ("alice", "bob")),),
    )

    with pytest.raises(DiagnosticError) as raised:
        check_document(Document(theories=(theory,), cases=(case,)))

    assert raised.value.diagnostic.code is DiagnosticCode.TYPE_MISMATCH
    assert 'expects argument "option" to have kind "Option"' in (
        raised.value.diagnostic.message
    )
