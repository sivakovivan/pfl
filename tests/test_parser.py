from pfl.ast_nodes import Document
from pfl.parser import parse_document


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
