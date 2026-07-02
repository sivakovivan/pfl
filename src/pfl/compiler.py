"""Compilation from validated PFL AST declarations to canonical IR."""

from pfl.ast_nodes import DeriveDecl, PredicateCall
from pfl.canonicalize import canonicalize_pattern
from pfl.diagnostics import Diagnostic, DiagnosticCode, DiagnosticError
from pfl.ir import PredicatePattern, Rule
from pfl.symbols import TheorySymbols


def compile_derive(derive: DeriveDecl, theory: TheorySymbols) -> Rule:
    """Compile one derive declaration into a forward-chaining rule."""

    body: list[PredicatePattern] = []
    for expression in derive.body:
        if not isinstance(expression, PredicateCall):
            raise DiagnosticError(
                Diagnostic(
                    DiagnosticCode.MALFORMED_DERIVE,
                    f'Derive "{derive.name}" contains an unreadable '
                    "expression that has not been desugared.",
                )
            )
        body.append(canonicalize_pattern(expression, theory))

    head = PredicatePattern(derive.name, tuple(arg.name for arg in derive.args))
    return Rule(derive.name, derive.args, tuple(body), head)


def compile_theory_rules(theory: TheorySymbols) -> tuple[Rule, ...]:
    return tuple(
        compile_derive(derive, theory) for derive in theory.derives.values()
    )
