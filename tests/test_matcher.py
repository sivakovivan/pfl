from pfl.ir import Predicate, PredicatePattern
from pfl.matcher import match_predicate


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
