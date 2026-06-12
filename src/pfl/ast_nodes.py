"""Abstract syntax tree nodes for PFL source documents."""

from dataclasses import dataclass


class Expression:
    """Base class for expressions that may appear in rules and cases."""


@dataclass(frozen=True)
class NamedArg:
    name: str
    value: str


@dataclass(frozen=True)
class PredicateCall(Expression):
    name: str
    args: tuple[str, ...]
    named_args: tuple[NamedArg, ...] = ()


@dataclass(frozen=True)
class SurfaceStatement(Expression):
    text: str


@dataclass(frozen=True)
class SomeExpression(Expression):
    var_name: str
    var_kind: str
    body: tuple[Expression, ...]


@dataclass(frozen=True)
class ArgDecl:
    name: str
    kind: str


@dataclass(frozen=True)
class KindDecl:
    name: str


@dataclass(frozen=True)
class PositDecl:
    name: str
    args: tuple[ArgDecl, ...]
    reads: str | None = None


@dataclass(frozen=True)
class DeriveDecl:
    name: str
    args: tuple[ArgDecl, ...]
    body: tuple[Expression, ...]


@dataclass(frozen=True)
class TheoryDecl:
    name: str
    kinds: tuple[KindDecl, ...] = ()
    posits: tuple[PositDecl, ...] = ()
    derives: tuple[DeriveDecl, ...] = ()


@dataclass(frozen=True)
class LetDecl:
    name: str
    kind: str


@dataclass(frozen=True)
class AskDecl:
    expression: Expression


@dataclass(frozen=True)
class CaseDecl:
    name: str
    theory_name: str
    lets: tuple[LetDecl, ...] = ()
    facts: tuple[Expression, ...] = ()
    asks: tuple[AskDecl, ...] = ()


@dataclass(frozen=True)
class Document:
    theories: tuple[TheoryDecl, ...] = ()
    cases: tuple[CaseDecl, ...] = ()
