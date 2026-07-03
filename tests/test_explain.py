from pfl.engine import FactStore
from pfl.explain import format_explanation
from pfl.ir import Derivation, Fact, Predicate


def test_explains_derived_fact_recursively() -> None:
    prefers = Predicate("prefers", ("alice", "optionA"))
    chooses = Predicate("chooses", ("alice", "optionA"))
    conclusion = Predicate("favourable_outcome", ("alice", "optionA"))
    derivation = Derivation(
        "favourable_outcome",
        (prefers, chooses),
        (("actor", "alice"), ("option", "optionA")),
    )
    facts = FactStore(
        (Fact(prefers), Fact(chooses), Fact(conclusion, derivation))
    )

    explanation = format_explanation(conclusion, facts)

    assert explanation == "\n".join(
        [
            "favourable_outcome(alice, optionA)",
            "  derived by favourable_outcome",
            "  with:",
            "    actor = alice",
            "    option = optionA",
            "  because:",
            "    prefers(alice, optionA)",
            "      given in case",
            "    chooses(alice, optionA)",
            "      given in case",
        ]
    )


def test_explains_unknown_predicate() -> None:
    explanation = format_explanation(Predicate("acts", ("alice",)), FactStore())

    assert "unknown because no rule or case fact" in explanation
