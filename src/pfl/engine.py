"""Fact storage and deterministic inference for PFL."""

from collections.abc import Iterable, Iterator

from pfl.ast_nodes import CaseDecl, PredicateCall
from pfl.canonicalize import canonicalize_predicate
from pfl.diagnostics import Diagnostic, DiagnosticCode, DiagnosticError
from pfl.ir import Fact, Predicate
from pfl.symbols import TheorySymbols


class FactStore:
    """An insertion-ordered set of canonical facts."""

    def __init__(self, facts: Iterable[Fact] = ()) -> None:
        self._facts: dict[Predicate, Fact] = {}
        for fact in facts:
            self.add(fact)

    def add(self, fact: Fact) -> bool:
        if fact.predicate in self._facts:
            return False
        self._facts[fact.predicate] = fact
        return True

    def __contains__(self, predicate: object) -> bool:
        if isinstance(predicate, Fact):
            predicate = predicate.predicate
        return predicate in self._facts

    def __iter__(self) -> Iterator[Fact]:
        return iter(self._facts.values())

    def __len__(self) -> int:
        return len(self._facts)

    def facts_for(self, predicate_name: str) -> tuple[Fact, ...]:
        return tuple(
            fact
            for fact in self._facts.values()
            if fact.predicate.name == predicate_name
        )


def compile_case_facts(case: CaseDecl, theory: TheorySymbols) -> FactStore:
    """Compile canonical case facts into a fact store."""

    store = FactStore()
    for expression in case.facts:
        if not isinstance(expression, PredicateCall):
            raise DiagnosticError(
                Diagnostic(
                    DiagnosticCode.UNDEFINED_TERM,
                    f'Case "{case.name}" contains an unreadable fact that '
                    "has not been desugared.",
                )
            )
        store.add(Fact(canonicalize_predicate(expression, theory)))
    return store
