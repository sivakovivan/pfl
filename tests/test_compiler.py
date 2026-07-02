from pfl.ast_nodes import (
    ArgDecl,
    DeriveDecl,
    Document,
    KindDecl,
    PositDecl,
    PredicateCall,
    TheoryDecl,
)
from pfl.compiler import compile_derive
from pfl.ir import PredicatePattern, Rule
from pfl.symbols import build_symbol_table


def test_compiles_derive_into_rule() -> None:
    parameters = (
        ArgDecl("actor", "Subject"),
        ArgDecl("option", "Option"),
    )
    derive = DeriveDecl(
        "favourable_outcome",
        parameters,
        (
            PredicateCall("prefers", ("actor", "option")),
            PredicateCall("chooses", ("actor", "option")),
        ),
    )
    theory = TheoryDecl(
        "ExampleTheory",
        kinds=(KindDecl("Subject"), KindDecl("Option")),
        posits=(
            PositDecl("prefers", parameters),
            PositDecl("chooses", parameters),
        ),
        derives=(derive,),
    )
    symbols = build_symbol_table(Document(theories=(theory,)))

    rule = compile_derive(derive, symbols.theories["ExampleTheory"])

    assert rule == Rule(
        "favourable_outcome",
        parameters,
        (
            PredicatePattern("prefers", ("actor", "option")),
            PredicatePattern("chooses", ("actor", "option")),
        ),
        PredicatePattern("favourable_outcome", ("actor", "option")),
    )
