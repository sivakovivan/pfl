from pfl.ast_nodes import ArgDecl
from pfl.engine import FactStore
from pfl.ir import Fact, Predicate, PredicatePattern, Rule
from pfl.matcher import match_predicate, match_rule_body


def test_matches_predicate_pattern_to_fact() -> None:
    bindings = match_predicate(
        PredicatePattern("prefers", ("actor", "option")),
        Predicate("prefers", ("alice", "optionA")),
        {"actor", "option"},
    )

    assert bindings == {"actor": "alice", "option": "optionA"}


def test_respects_existing_bindings() -> None:
    pattern = PredicatePattern("chooses", ("actor", "option"))
    predicate = Predicate("chooses", ("bob", "optionA"))

    assert (
        match_predicate(
            pattern,
            predicate,
            {"actor", "option"},
            {"actor": "alice"},
        )
        is None
    )


def test_matches_literal_pattern_argument_exactly() -> None:
    pattern = PredicatePattern("chooses", ("actor", "optionA"))

    assert match_predicate(
        pattern,
        Predicate("chooses", ("alice", "optionA")),
        {"actor"},
    ) == {"actor": "alice"}


def test_matches_all_rule_premises() -> None:
    rule = Rule(
        "favourable_outcome",
        (ArgDecl("actor", "Subject"), ArgDecl("option", "Option")),
        (
            PredicatePattern("prefers", ("actor", "option")),
            PredicatePattern("chooses", ("actor", "option")),
        ),
        PredicatePattern("favourable_outcome", ("actor", "option")),
    )
    store = FactStore(
        (
            Fact(Predicate("prefers", ("alice", "optionA"))),
            Fact(Predicate("chooses", ("alice", "optionA"))),
            Fact(Predicate("chooses", ("bob", "optionB"))),
        )
    )

    assert match_rule_body(rule, store) == ({"actor": "alice", "option": "optionA"},)


def test_rule_body_requires_every_premise() -> None:
    rule = Rule(
        "favourable_outcome",
        (ArgDecl("actor", "Subject"),),
        (
            PredicatePattern("prefers", ("actor",)),
            PredicatePattern("chooses", ("actor",)),
        ),
        PredicatePattern("favourable_outcome", ("actor",)),
    )
    store = FactStore((Fact(Predicate("prefers", ("alice",))),))

    assert match_rule_body(rule, store) == ()
