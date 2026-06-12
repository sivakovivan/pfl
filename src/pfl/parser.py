"""Parser entrypoint for PFL source text."""

from dataclasses import dataclass
import re

from pfl.ast_nodes import Document, KindDecl, TheoryDecl


_TOKEN_PATTERN = re.compile(
    r"(?P<whitespace>\s+)"
    r'|(?P<string>"(?:[^"\\]|\\.)*")'
    r"|(?P<identifier>[A-Za-z_][A-Za-z0-9_]*)"
    r"|(?P<punctuation>[{}():,])"
    r"|(?P<invalid>.)",
)


@dataclass(frozen=True)
class _Token:
    kind: str
    value: str


def _tokenize(source: str) -> tuple[_Token, ...]:
    tokens: list[_Token] = []
    for match in _TOKEN_PATTERN.finditer(source):
        kind = match.lastgroup
        if kind == "whitespace":
            continue
        if kind == "invalid":
            raise ValueError(f"Unexpected character {match.group()!r}")
        if kind is None:
            raise AssertionError("Token pattern produced an unclassified match")
        tokens.append(_Token(kind, match.group()))
    return tuple(tokens)


class _Parser:
    def __init__(self, tokens: tuple[_Token, ...]) -> None:
        self.tokens = tokens
        self.position = 0

    def parse_document(self) -> Document:
        theories: list[TheoryDecl] = []
        while not self.at_end:
            theories.append(self.parse_theory())
        return Document(theories=tuple(theories))

    def parse_theory(self) -> TheoryDecl:
        self.expect_value("theory")
        name = self.expect_kind("identifier").value
        self.expect_value("{")
        kinds: list[KindDecl] = []
        while self.current_token().value != "}":
            kinds.append(self.parse_kind())
        self.expect_value("}")
        return TheoryDecl(name, kinds=tuple(kinds))

    def parse_kind(self) -> KindDecl:
        self.expect_value("kind")
        return KindDecl(self.expect_kind("identifier").value)

    @property
    def at_end(self) -> bool:
        return self.position == len(self.tokens)

    def expect_value(self, value: str) -> _Token:
        token = self.current_token()
        if token.value != value:
            raise ValueError(f"Expected {value!r}, found {token.value!r}")
        self.position += 1
        return token

    def expect_kind(self, kind: str) -> _Token:
        token = self.current_token()
        if token.kind != kind:
            raise ValueError(f"Expected {kind}, found {token.value!r}")
        self.position += 1
        return token

    def current_token(self) -> _Token:
        if self.at_end:
            raise ValueError("Unexpected end of PFL source")
        return self.tokens[self.position]


def parse_document(source: str) -> Document:
    """Parse PFL source into a document AST."""

    return _Parser(_tokenize(source)).parse_document()
