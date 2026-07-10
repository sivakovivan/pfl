from pfl.ast_nodes import (
    ArgDecl,
    DeriveDecl,
    Document,
    KindDecl,
    PositDecl,
    PredicateCall,
    SomeExpression,
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


def test_compiles_some_body_as_existential_rule_premises() -> None:
    derive = DeriveDecl(
        "avoidable_setback",
        (
            ArgDecl("P", "Subject"),
            ArgDecl("Actor", "Subject"),
            ArgDecl("A", "Option"),
        ),
        (
            PredicateCall("chooses", ("Actor", "A")),
            SomeExpression(
                "B",
                "Option",
                (
                    PredicateCall("available_to", ("B", "Actor")),
                    PredicateCall("option_worse_for", ("P", "A", "B")),
                ),
            ),
        ),
    )
    theory = TheoryDecl(
        "MinimalPreferenceEthics",
        kinds=(KindDecl("Subject"), KindDecl("Option")),
        posits=(
            PositDecl(
                "chooses",
                (ArgDecl("actor", "Subject"), ArgDecl("option", "Option")),
            ),
            PositDecl(
                "available_to",
                (ArgDecl("option", "Option"), ArgDecl("subject", "Subject")),
            ),
        ),
        derives=(
            DeriveDecl(
                "option_worse_for",
                (
                    ArgDecl("P", "Subject"),
                    ArgDecl("A", "Option"),
                    ArgDecl("B", "Option"),
                ),
                (),
            ),
            derive,
        ),
    )
    symbols = build_symbol_table(Document(theories=(theory,)))

    rule = compile_derive(derive, symbols.theories["MinimalPreferenceEthics"])

    assert rule.local_variables == (ArgDecl("B", "Option"),)
    assert [pattern.name for pattern in rule.body] == [
        "chooses",
        "available_to",
        "option_worse_for",
    ]
