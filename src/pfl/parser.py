"""Parser entrypoint for PFL source text."""

import ast
from dataclasses import dataclass
import re

from pfl.ast_nodes import (
    ArgDecl,
    AskDecl,
    CaseDecl,
    DeriveDecl,
    Document,
    Expression,
    KindDecl,
    LetDecl,
    PositDecl,
    PredicateCall,
    SomeExpression,
    SurfaceStatement,
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
    line: int
    column: int


def _tokenize(source: str) -> tuple[_Token, ...]:
    tokens: list[_Token] = []
    line = 1
    column = 1
    for match in _TOKEN_PATTERN.finditer(source):
        kind = match.lastgroup
        value = match.group()
        if kind == "whitespace":
            newline_count = value.count("\n")
            if newline_count:
                line += newline_count
                column = len(value.rsplit("\n", 1)[1]) + 1
            else:
                column += len(value)
            continue
        if kind == "invalid":
            raise ValueError(f"Unexpected character {value!r}")
        if kind is None:
            raise AssertionError("Token pattern produced an unclassified match")
        tokens.append(_Token(kind, value, line, column))
        column += len(value)
    return tuple(tokens)


class _Parser:
    def __init__(self, tokens: tuple[_Token, ...]) -> None:
        self.tokens = tokens
        self.position = 0

    def parse_document(self) -> Document:
        theories: list[TheoryDecl] = []
        cases: list[CaseDecl] = []
        while not self.at_end:
            if self.current_token().value == "theory":
                theories.append(self.parse_theory())
            elif self.current_token().value == "case":
                cases.append(self.parse_case())
            else:
                token = self.current_token()
                raise ValueError(f"Unexpected top-level declaration {token.value!r}")
        return Document(theories=tuple(theories), cases=tuple(cases))

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

    def parse_case(self) -> CaseDecl:
        self.expect_value("case")
        name = self.expect_kind("identifier").value
        self.expect_value("under")
        theory_name = self.expect_kind("identifier").value
        self.expect_value("{")
        lets: list[LetDecl] = []
        facts: list[Expression] = []
        asks: list[AskDecl] = []
        while self.current_token().value != "}":
            if self.current_token().value == "let":
                lets.append(self.parse_let())
            elif self.current_token().value == "ask":
                asks.append(self.parse_ask())
            elif self.peek_value(1) == "(":
                facts.append(self.parse_predicate_call())
            else:
                facts.append(self.parse_surface_statement())
        self.expect_value("}")
        return CaseDecl(
            name,
            theory_name,
            lets=tuple(lets),
            facts=tuple(facts),
            asks=tuple(asks),
        )

    def parse_let(self) -> LetDecl:
        self.expect_value("let")
        name = self.expect_kind("identifier").value
        self.expect_value(":")
        kind = self.expect_kind("identifier").value
        return LetDecl(name, kind)

    def parse_ask(self) -> AskDecl:
        self.expect_value("ask")
        return AskDecl(self.parse_predicate_call())

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
        derive_token = self.expect_value("derive")
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

        body: list[Expression] = []
        declaration_starters = {"kind", "posit", "derive", "}"}
        while (
            self.current_token().value not in declaration_starters
            and self.current_token().column > derive_token.column
        ):
            if self.current_token().value == "some":
                body.append(self.parse_some())
            elif self.peek_value(1) == "(":
                body.append(self.parse_predicate_call())
            else:
                body.append(self.parse_surface_statement())

        return DeriveDecl(name, tuple(args), tuple(body))

    def parse_some(self) -> SomeExpression:
        some_token = self.expect_value("some")
        var_name = self.expect_kind("identifier").value
        self.expect_value(":")
        var_kind = self.expect_kind("identifier").value
        self.expect_value("where")
        self.expect_value(":")

        body: list[Expression] = []
        while (
            self.current_token().value != "}"
            and self.current_token().column > some_token.column
        ):
            if self.peek_value(1) == "(":
                body.append(self.parse_predicate_call())
            else:
                body.append(self.parse_surface_statement())
        if not body:
            raise ValueError("A some block must contain at least one expression")
        return SomeExpression(var_name, var_kind, tuple(body))

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

    def parse_surface_statement(self) -> SurfaceStatement:
        line = self.current_token().line
        parts: list[str] = []
        while not self.at_end and self.current_token().line == line:
            if self.current_token().value == "}":
                break
            parts.append(self.current_token().value)
            self.position += 1
        if not parts:
            raise ValueError("Expected a readable surface statement")
        return SurfaceStatement(" ".join(parts))

    def peek_value(self, offset: int) -> str | None:
        position = self.position + offset
        if position >= len(self.tokens):
            return None
        return self.tokens[position].value

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
