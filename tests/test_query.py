from pfl.ast_nodes import (
    ArgDecl,
    AskDecl,
    DeriveDecl,
    Document,
    PredicateCall,
    TheoryDecl,
)
from pfl.engine import FactStore
from pfl.ir import Fact, Predicate
from pfl.query import QueryStatus, evaluate_ask
from pfl.symbols import TheorySymbols, build_symbol_table


def _theory_symbols() -> TheorySymbols:
    theory = TheoryDecl(
        "ExampleTheory",
        derives=(
            DeriveDecl(
                "favourable_outcome",
                (ArgDecl("actor", "Subject"), ArgDecl("option", "Option")),
                (),
            ),
        ),
    )
    return build_symbol_table(Document(theories=(theory,))).theories["ExampleTheory"]


def test_evaluates_derived_ask_as_true() -> None:
    predicate = Predicate("favourable_outcome", ("alice", "optionA"))
    facts = FactStore((Fact(predicate),))
    ask = AskDecl(PredicateCall("favourable_outcome", ("alice", "optionA")))

    result = evaluate_ask(ask, _theory_symbols(), facts)

    assert result.predicate == predicate
    assert result.status is QueryStatus.TRUE


def test_evaluates_known_but_underived_ask_as_unknown() -> None:
    ask = AskDecl(PredicateCall("favourable_outcome", ("alice", "optionA")))

    result = evaluate_ask(ask, _theory_symbols(), FactStore())

    assert result.status is QueryStatus.UNKNOWN
