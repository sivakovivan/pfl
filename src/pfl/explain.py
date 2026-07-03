"""Human-readable explanations for inferred PFL facts."""

from pfl.engine import FactStore
from pfl.ir import Predicate


def format_explanation(predicate: Predicate, facts: FactStore) -> str:
    """Format a recursive derivation tree for a predicate."""

    lines: list[str] = []
    _append_explanation(predicate, facts, lines, 0, set())
    return "\n".join(lines)


def _append_explanation(
    predicate: Predicate,
    facts: FactStore,
    lines: list[str],
    depth: int,
    active: set[Predicate],
) -> None:
    indent = "  " * depth
    lines.append(f"{indent}{predicate}")

    fact = facts.get(predicate)
    if fact is None:
        lines.append(
            f"{indent}  unknown because no rule or case fact derived this predicate."
        )
        return
    if fact.derivation is None:
        lines.append(f"{indent}  given in case")
        return
    if predicate in active:
        lines.append(f"{indent}  derivation already shown")
        return

    derivation = fact.derivation
    lines.append(f"{indent}  derived by {derivation.rule_name}")
    if derivation.bindings:
        lines.append(f"{indent}  with:")
        for variable, value in derivation.bindings:
            lines.append(f"{indent}    {variable} = {value}")
    lines.append(f"{indent}  because:")

    active.add(predicate)
    for premise in derivation.premises:
        _append_explanation(premise, facts, lines, depth + 2, active)
    active.remove(predicate)
