import pytest

from pfl.ast_nodes import Document
from pfl.parser import parse_document


@pytest.mark.parametrize("source", ["", "  \n\t"])
def test_parses_empty_document(source: str) -> None:
    assert parse_document(source) == Document()


def test_nonempty_document_is_not_supported_by_scaffold() -> None:
    with pytest.raises(NotImplementedError):
        parse_document("theory ExampleTheory {}")
