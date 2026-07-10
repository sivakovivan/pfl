"""Canonical intermediate representation used by the PFL interpreter."""

from dataclasses import dataclass

from pfl.ast_nodes import ArgDecl


def _format_call(name: str, args: tuple[str, ...]) -> str:
    return f"{name}({', '.join(args)})"


@dataclass(frozen=True)
class Predicate:
    name: str
    args: tuple[str, ...]

    def __str__(self) -> str:
        return _format_call(self.name, self.args)


@dataclass(frozen=True)
class PredicatePattern:
    name: str
    args: tuple[str, ...]

    def __str__(self) -> str:
        return _format_call(self.name, self.args)


@dataclass(frozen=True)
class Rule:
    name: str
    parameters: tuple[ArgDecl, ...]
    body: tuple[PredicatePattern, ...]
    head: PredicatePattern
    local_variables: tuple[ArgDecl, ...] = ()

    def __str__(self) -> str:
        premises = ", ".join(str(predicate) for predicate in self.body)
        return f"{self.head} :- {premises}"


@dataclass(frozen=True)
class Fact:
    predicate: Predicate
    derivation: "Derivation | None" = None

    def __str__(self) -> str:
        return str(self.predicate)

    @property
    def is_given(self) -> bool:
        return self.derivation is None


@dataclass(frozen=True)
class Derivation:
    rule_name: str
    premises: tuple[Predicate, ...]
    bindings: tuple[tuple[str, str], ...]
