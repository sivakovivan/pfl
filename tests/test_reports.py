from pfl.ast_nodes import (
    ArgDecl,
    AskDecl,
    CaseDecl,
    DeriveDecl,
    Document,
    KindDecl,
    PositDecl,
    PredicateCall,
    TheoryDecl,
)
from pfl.reports import build_semantic_report, format_semantic_report


def test_builds_basic_semantic_report() -> None:
    parameters = (
        ArgDecl("actor", "Subject"),
        ArgDecl("option", "Option"),
    )
    theory = TheoryDecl(
        "ExampleTheory",
        kinds=(KindDecl("Subject"), KindDecl("Option")),
        posits=(PositDecl("prefers", parameters), PositDecl("chooses", parameters)),
        derives=(DeriveDecl("favourable_outcome", parameters, ()),),
    )
    case = CaseDecl(
        "SpecificChoiceCase",
        "ExampleTheory",
        asks=(
            AskDecl(PredicateCall("favourable_outcome", ("alice", "optionA"))),
        ),
    )

    report = build_semantic_report(
        Document(theories=(theory,), cases=(case,)),
        "ExampleTheory",
    )
    output = format_semantic_report(report)

    assert "Theory: ExampleTheory" in output
    assert "- Subject" in output
    assert "- prefers(actor: Subject, option: Option)" in output
    assert "- favourable_outcome(actor: Subject, option: Option)" in output
    assert "- SpecificChoiceCase under ExampleTheory" in output
    assert "- favourable_outcome(alice, optionA)" in output
