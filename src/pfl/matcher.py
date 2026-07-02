"""Predicate and rule matching for forward-chaining inference."""

from collections.abc import Mapping, Set
from typing import TypeAlias

from pfl.ir import Predicate, PredicatePattern


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
