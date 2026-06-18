"""Parser entrypoint for PFL source text."""

import ast
from dataclasses import dataclass
import re

from pfl.ast_nodes import (
    ArgDecl,
    DeriveDecl,
    Document,
    KindDecl,
    PositDecl,
    PredicateCall,
    TheoryDecl,
)


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
        posits: list[PositDecl] = []
        derives: list[DeriveDecl] = []
        while self.current_token().value != "}":
            if self.current_token().value == "kind":
                kinds.append(self.parse_kind())
            elif self.current_token().value == "posit":
                posits.append(self.parse_posit())
            elif self.current_token().value == "derive":
                derives.append(self.parse_derive())
            else:
                token = self.current_token()
                raise ValueError(f"Unexpected theory declaration {token.value!r}")
        self.expect_value("}")
        return TheoryDecl(
            name,
            kinds=tuple(kinds),
            posits=tuple(posits),
            derives=tuple(derives),
        )

    def parse_kind(self) -> KindDecl:
        self.expect_value("kind")
        return KindDecl(self.expect_kind("identifier").value)

    def parse_posit(self) -> PositDecl:
        self.expect_value("posit")
        name = self.expect_kind("identifier").value
        self.expect_value("(")

        args: list[ArgDecl] = []
        if self.current_token().value != ")":
            args.append(self.parse_arg_decl())
            while self.current_token().value == ",":
                self.expect_value(",")
                args.append(self.parse_arg_decl())

        self.expect_value(")")
        reads = self.parse_reads() if self.current_token().value == "reads" else None
        return PositDecl(name, tuple(args), reads)

    def parse_reads(self) -> str:
        self.expect_value("reads")
        token = self.expect_kind("string")
        value = ast.literal_eval(token.value)
        if not isinstance(value, str):
            raise AssertionError("String token did not evaluate to a string")
        return value

    def parse_derive(self) -> DeriveDecl:
        self.expect_value("derive")
        name = self.expect_kind("identifier").value
        self.expect_value("(")

        args: list[ArgDecl] = []
        if self.current_token().value != ")":
            args.append(self.parse_arg_decl())
            while self.current_token().value == ",":
                self.expect_value(",")
                args.append(self.parse_arg_decl())

        self.expect_value(")")
        self.expect_value(":")

        body: list[PredicateCall] = []
        declaration_starters = {"kind", "posit", "derive", "}"}
        while self.current_token().value not in declaration_starters:
            body.append(self.parse_predicate_call())

        return DeriveDecl(name, tuple(args), tuple(body))

    def parse_arg_decl(self) -> ArgDecl:
        name = self.expect_kind("identifier").value
        self.expect_value(":")
        kind = self.expect_kind("identifier").value
        return ArgDecl(name, kind)

    def parse_predicate_call(self) -> PredicateCall:
        name = self.expect_kind("identifier").value
        self.expect_value("(")

        args: list[str] = []
        if self.current_token().value != ")":
            args.append(self.expect_kind("identifier").value)
            while self.current_token().value == ",":
                self.expect_value(",")
                args.append(self.expect_kind("identifier").value)

        self.expect_value(")")
        return PredicateCall(name, tuple(args))

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


def parse_predicate_call(source: str) -> PredicateCall:
    """Parse one canonical predicate call."""

    parser = _Parser(_tokenize(source))
    predicate = parser.parse_predicate_call()
    if not parser.at_end:
        raise ValueError(f"Unexpected token {parser.current_token().value!r}")
    return predicate
