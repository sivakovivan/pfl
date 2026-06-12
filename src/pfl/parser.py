"""Parser entrypoint for PFL source text."""

from pfl.ast_nodes import Document


def parse_document(source: str) -> Document:
    """Parse PFL source into a document AST.

    The initial parser scaffold accepts an empty document. Language constructs
    are introduced incrementally by the parser commits that follow.
    """

    if source.strip():
        raise NotImplementedError("PFL declarations are not supported yet")
    return Document()
