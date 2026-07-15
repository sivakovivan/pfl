from pfl.ast_nodes import (
    ArgDecl,
    AskDecl,
    CaseDecl,
    DeriveDecl,
    Document,
    KindDecl,
    PositDecl,
    PredicateCall,
    SurfaceStatement,
    TheoryDecl,
)
from pfl.diagnostics import DiagnosticCode, Severity
from pfl.reports import (
    build_semantic_report,
    format_semantic_report,
    semantic_debt_diagnostics,
)


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
        asks=(AskDecl(PredicateCall("favourable_outcome", ("alice", "optionA"))),),
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


def test_reports_derived_term_dependencies() -> None:
    parameters = (
        ArgDecl("actor", "Subject"),
        ArgDecl("option", "Option"),
    )
    theory = TheoryDecl(
        "ExampleTheory",
        derives=(
            DeriveDecl(
                "favourable_outcome",
                parameters,
                (
                    PredicateCall("prefers", ("actor", "option")),
                    PredicateCall("chooses", ("actor", "option")),
                ),
            ),
        ),
    )

    report = build_semantic_report(Document(theories=(theory,)), "ExampleTheory")
    output = format_semantic_report(report)

    assert report.dependencies[0].dependencies == ("prefers", "chooses")
    assert "- favourable_outcome\n  depends on:" in output
    assert "  - prefers" in output
    assert "  - chooses" in output


def test_reports_unknown_terms_as_semantic_debt() -> None:
    derive = DeriveDecl(
        "satisfied",
        (ArgDecl("actor", "Subject"),),
        (PredicateCall("desires", ("actor",)),),
    )
    theory = TheoryDecl("ExampleTheory", derives=(derive,))

    report = build_semantic_report(Document(theories=(theory,)), "ExampleTheory")
    diagnostics = semantic_debt_diagnostics(report)

    assert report.semantic_debt[0].term_name == "desires"
    assert '- desires (derive "satisfied")' in format_semantic_report(report)
    assert diagnostics[0].code is DiagnosticCode.SEMANTIC_DEBT
    assert diagnostics[0].severity is Severity.WARNING


def test_reports_dependencies_from_readable_derive_body() -> None:
    parameter = (ArgDecl("actor", "Subject"),)
    theory = TheoryDecl(
        "ActionTheory",
        posits=(PositDecl("acts", parameter, "{actor} acts"),),
        derives=(
            DeriveDecl(
                "acknowledged",
                parameter,
                (SurfaceStatement("actor acts"),),
            ),
        ),
    )

    report = build_semantic_report(Document(theories=(theory,)), "ActionTheory")

    assert report.dependencies[0].dependencies == ("acts",)
