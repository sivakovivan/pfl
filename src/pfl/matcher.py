"""Predicate and rule matching for forward-chaining inference."""

from collections.abc import Mapping, Set
from typing import TYPE_CHECKING, TypeAlias

from pfl.ir import Predicate, PredicatePattern, Rule

if TYPE_CHECKING:
    from pfl.engine import FactStore


Bindings: TypeAlias = dict[str, str]


def match_predicate(
    pattern: PredicatePattern,
    predicate: Predicate,
    variables: Set[str],
    bindings: Mapping[str, str] | None = None,
) -> Bindings | None:
    """Match one predicate pattern while respecting existing bindings."""

    if pattern.name != predicate.name or len(pattern.args) != len(predicate.args):
        return None

    matched = dict(bindings or {})
    for pattern_arg, value in zip(pattern.args, predicate.args, strict=True):
        if pattern_arg not in variables:
            if pattern_arg != value:
                return None
            continue

        existing = matched.get(pattern_arg)
        if existing is not None and existing != value:
            return None
        matched[pattern_arg] = value
    return matched


def match_rule_body(rule: Rule, facts: "FactStore") -> tuple[Bindings, ...]:
    """Return every substitution satisfying all predicates in a rule body."""

    variables = {parameter.name for parameter in rule.parameters}
    candidates: list[Bindings] = [{}]

    for pattern in rule.body:
        matched_candidates: list[Bindings] = []
        for bindings in candidates:
            for fact in facts.facts_for(pattern.name):
                matched = match_predicate(
                    pattern,
                    fact.predicate,
                    variables,
                    bindings,
                )
                if matched is not None and matched not in matched_candidates:
                    matched_candidates.append(matched)
        candidates = matched_candidates
        if not candidates:
            break

    return tuple(candidates)
