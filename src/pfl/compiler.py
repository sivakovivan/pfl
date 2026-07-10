"""Compilation from validated PFL AST declarations to canonical IR."""

from pfl.ast_nodes import (
    ArgDecl,
    DeriveDecl,
    Expression,
    PredicateCall,
    SomeExpression,
    SurfaceStatement,
)
from pfl.canonicalize import canonicalize_pattern
from pfl.desugar import desugar_surface_statement
from pfl.diagnostics import Diagnostic, DiagnosticCode, DiagnosticError
from pfl.ir import PredicatePattern, Rule
from pfl.symbols import TheorySymbols


def compile_derive(derive: DeriveDecl, theory: TheorySymbols) -> Rule:
    """Compile one derive declaration into a forward-chaining rule."""

    body: list[PredicatePattern] = []
    local_variables: list[ArgDecl] = []
    for expression in derive.body:
        if isinstance(expression, SomeExpression):
            if expression.var_kind not in theory.kinds:
                raise DiagnosticError(
                    Diagnostic(
                        DiagnosticCode.UNKNOWN_KIND,
                        f'Unknown kind "{expression.var_kind}" for some '
                        f'variable "{expression.var_name}".',
                    )
                )
            local_variables.append(ArgDecl(expression.var_name, expression.var_kind))
            body.extend(
                _compile_expression(item, derive, theory) for item in expression.body
            )
        else:
            body.append(_compile_expression(expression, derive, theory))

    head = PredicatePattern(derive.name, tuple(arg.name for arg in derive.args))
    return Rule(
        derive.name,
        derive.args,
        tuple(body),
        head,
        local_variables=tuple(local_variables),
    )


def compile_theory_rules(theory: TheorySymbols) -> tuple[Rule, ...]:
    return tuple(
        compile_derive(derive, theory) for derive in theory.derives.values()
    )


def _compile_expression(
    expression: Expression,
    derive: DeriveDecl,
    theory: TheorySymbols,
) -> PredicatePattern:
    if isinstance(expression, SurfaceStatement):
        expression = desugar_surface_statement(expression, theory)
    if not isinstance(expression, PredicateCall):
        raise DiagnosticError(
            Diagnostic(
                DiagnosticCode.MALFORMED_DERIVE,
                f'Derive "{derive.name}" contains an unsupported expression.',
            )
        )
    return canonicalize_pattern(expression, theory)
