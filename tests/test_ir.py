from pfl.ast_nodes import ArgDecl
from pfl.ir import Fact, Predicate, PredicatePattern, Rule


def test_formats_predicate_and_fact_stably() -> None:
    predicate = Predicate("prefers", ("alice", "optionA"))

    assert str(predicate) == "prefers(alice, optionA)"
    assert str(Fact(predicate)) == "prefers(alice, optionA)"


def test_formats_rule_stably() -> None:
    parameters = (
        ArgDecl("actor", "Subject"),
        ArgDecl("option", "Option"),
    )
    rule = Rule(
        "favourable_outcome",
        parameters,
        (
            PredicatePattern("prefers", ("actor", "option")),
            PredicatePattern("chooses", ("actor", "option")),
        ),
        PredicatePattern("favourable_outcome", ("actor", "option")),
    )

    assert str(rule) == (
        "favourable_outcome(actor, option) :- "
        "prefers(actor, option), chooses(actor, option)"
    )
