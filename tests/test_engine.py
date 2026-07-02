from pfl.ast_nodes import (
    ArgDecl,
    CaseDecl,
    Document,
    PositDecl,
    PredicateCall,
    TheoryDecl,
)
from pfl.engine import FactStore, compile_case_facts, run_inference
from pfl.ir import Fact, Predicate, PredicatePattern, Rule
from pfl.symbols import build_symbol_table


def test_compiles_canonical_case_facts_into_store() -> None:
    theory = TheoryDecl(
        "ExampleTheory",
        posits=(
            PositDecl(
                "prefers",
                (ArgDecl("actor", "Subject"), ArgDecl("option", "Option")),
            ),
        ),
    )
    case = CaseDecl(
        "SpecificChoiceCase",
        "ExampleTheory",
        facts=(PredicateCall("prefers", ("alice", "optionA")),),
    )
    symbols = build_symbol_table(Document(theories=(theory,)))

    store = compile_case_facts(case, symbols.theories["ExampleTheory"])

    assert Predicate("prefers", ("alice", "optionA")) in store
    assert [str(fact) for fact in store] == ["prefers(alice, optionA)"]


def test_fact_store_ignores_duplicate_facts() -> None:
    fact = Fact(Predicate("chooses", ("alice", "optionA")))
    store = FactStore((fact,))

    assert store.add(fact) is False
    assert len(store) == 1


def test_forward_chaining_derives_favourable_outcome() -> None:
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
    store = FactStore(
        (
            Fact(Predicate("prefers", ("alice", "optionA"))),
            Fact(Predicate("chooses", ("alice", "optionA"))),
        )
    )

    run_inference(store, (rule,))

    assert Predicate("favourable_outcome", ("alice", "optionA")) in store
    assert len(store) == 3


def test_forward_chaining_repeats_until_fixed_point() -> None:
    parameter = (ArgDecl("actor", "Subject"),)
    second_rule = Rule(
        "endorsed",
        parameter,
        (PredicatePattern("favourable", ("actor",)),),
        PredicatePattern("endorsed", ("actor",)),
    )
    first_rule = Rule(
        "favourable",
        parameter,
        (PredicatePattern("chosen", ("actor",)),),
        PredicatePattern("favourable", ("actor",)),
    )
    store = FactStore((Fact(Predicate("chosen", ("alice",))),))

    run_inference(store, (second_rule, first_rule))

    assert Predicate("endorsed", ("alice",)) in store
