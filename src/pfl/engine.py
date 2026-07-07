"""Fact storage and deterministic inference for PFL."""

from collections.abc import Iterable, Iterator

from pfl.ast_nodes import CaseDecl, PredicateCall, SurfaceStatement
from pfl.canonicalize import canonicalize_predicate
from pfl.diagnostics import Diagnostic, DiagnosticCode, DiagnosticError
from pfl.desugar import desugar_surface_statement
from pfl.ir import Derivation, Fact, Predicate, PredicatePattern, Rule
from pfl.matcher import Bindings, match_rule_body
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

    def get(self, predicate: Predicate) -> Fact | None:
        return self._facts.get(predicate)


def compile_case_facts(case: CaseDecl, theory: TheorySymbols) -> FactStore:
    """Compile canonical case facts into a fact store."""

    store = FactStore()
    for expression in case.facts:
        if isinstance(expression, SurfaceStatement):
            expression = desugar_surface_statement(expression, theory)
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


def run_inference(
    facts: FactStore,
    rules: Iterable[Rule],
    *,
    max_iterations: int = 100,
) -> FactStore:
    """Apply rules until the fact store reaches a fixed point."""

    compiled_rules = tuple(rules)
    for _ in range(max_iterations):
        added_fact = False
        for rule in compiled_rules:
            variables = {parameter.name for parameter in rule.parameters}
            for bindings in match_rule_body(rule, facts):
                predicate = _instantiate(rule.head, variables, bindings)
                premises = tuple(
                    _instantiate(pattern, variables, bindings)
                    for pattern in rule.body
                )
                ordered_bindings = tuple(
                    (parameter.name, bindings[parameter.name])
                    for parameter in rule.parameters
                    if parameter.name in bindings
                )
                derivation = Derivation(rule.name, premises, ordered_bindings)
                added_fact = facts.add(Fact(predicate, derivation)) or added_fact
        if not added_fact:
            return facts

    raise RuntimeError(
        f"Inference did not reach a fixed point after {max_iterations} iterations"
    )


def _instantiate(
    pattern: PredicatePattern,
    variables: set[str],
    bindings: Bindings,
) -> Predicate:
    args: list[str] = []
    for arg in pattern.args:
        if arg not in variables:
            args.append(arg)
            continue
        try:
            args.append(bindings[arg])
        except KeyError as error:
            raise RuntimeError(f'Rule variable "{arg}" is not bound') from error
    return Predicate(pattern.name, tuple(args))
