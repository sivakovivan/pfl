from pfl.ast_nodes import (
    ArgDecl,
    CaseDecl,
    Document,
    PositDecl,
    PredicateCall,
    TheoryDecl,
)
from pfl.engine import FactStore, compile_case_facts
from pfl.ir import Fact, Predicate
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
