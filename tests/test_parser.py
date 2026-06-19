from pfl.ast_nodes import Document
from pfl.parser import parse_document, parse_predicate_call


def test_parses_empty_document() -> None:
    assert parse_document("") == Document()


def test_parses_empty_theory() -> None:
    document = parse_document("theory ExampleTheory {}")

    assert len(document.theories) == 1
    assert document.theories[0].name == "ExampleTheory"
    assert document.theories[0].kinds == ()


def test_parses_multiple_empty_theories() -> None:
    document = parse_document(
        """
        theory First {
        }
        theory Second {}
        """
    )

    assert [theory.name for theory in document.theories] == ["First", "Second"]


def test_parses_multiple_kind_declarations() -> None:
    document = parse_document(
        """
        theory ExampleTheory {
            kind Subject
            kind Option
        }
        """
    )

    assert [kind.name for kind in document.theories[0].kinds] == [
        "Subject",
        "Option",
    ]


def test_parses_posit_signature_arguments_in_order() -> None:
    document = parse_document(
        """
        theory ExampleTheory {
            kind Subject
            kind Option
            posit chooses(actor: Subject, option: Option)
        }
        """
    )

    posit = document.theories[0].posits[0]
    assert posit.name == "chooses"
    assert [(arg.name, arg.kind) for arg in posit.args] == [
        ("actor", "Subject"),
        ("option", "Option"),
    ]
    assert posit.reads is None


def test_parses_optional_reads_template_exactly() -> None:
    document = parse_document(
        """
        theory ExampleTheory {
            kind Subject
            kind Option
            posit chooses(actor: Subject, option: Option)
                reads "{actor} chooses {option}"
        }
        """
    )

    assert document.theories[0].posits[0].reads == "{actor} chooses {option}"


def test_parses_canonical_predicate_call() -> None:
    predicate = parse_predicate_call("prefers(actor, option)")

    assert predicate.name == "prefers"
    assert predicate.args == ("actor", "option")


def test_parses_derive_with_canonical_body() -> None:
    document = parse_document(
        """
        theory ExampleTheory {
            kind Subject
            kind Option

            derive favourable_outcome(actor: Subject, option: Option):
                prefers(actor, option)
                chooses(actor, option)
        }
        """
    )

    derive = document.theories[0].derives[0]
    assert derive.name == "favourable_outcome"
    assert [(arg.name, arg.kind) for arg in derive.args] == [
        ("actor", "Subject"),
        ("option", "Option"),
    ]
    assert [(predicate.name, predicate.args) for predicate in derive.body] == [
        ("prefers", ("actor", "option")),
        ("chooses", ("actor", "option")),
    ]


def test_parses_empty_case_under_theory() -> None:
    document = parse_document(
        """
        theory ExampleTheory {}
        case SpecificChoiceCase under ExampleTheory {}
        """
    )

    assert len(document.cases) == 1
    assert document.cases[0].name == "SpecificChoiceCase"
    assert document.cases[0].theory_name == "ExampleTheory"
    assert document.cases[0].facts == ()
