"""Semantic validation for PFL documents."""

from pfl.ast_nodes import (
    ArgDecl,
    CaseDecl,
    Document,
    Expression,
    PredicateCall,
    SomeExpression,
    SurfaceStatement,
)
from pfl.canonicalize import canonicalize_predicate, resolve_term
from pfl.desugar import desugar_surface_statement
from pfl.diagnostics import Diagnostic, DiagnosticCode, DiagnosticError
from pfl.symbols import SymbolTable, TheorySymbols, build_symbol_table


def check_document(document: Document) -> SymbolTable:
    """Validate a document and return its resolved symbols."""

    symbols = build_symbol_table(document)
    for theory in symbols.theories.values():
        _check_term_kinds(theory)
        _check_derive_variable_scopes(theory)
    _check_case_theories(document, symbols)
    _check_case_lets(document, symbols)
    _check_case_facts(document, symbols)
    _check_case_asks(document, symbols)
    return symbols


def _check_case_theories(document: Document, symbols: SymbolTable) -> None:
    for case in document.cases:
        if case.theory_name in symbols.theories:
            continue
        raise DiagnosticError(
            Diagnostic(
                DiagnosticCode.UNKNOWN_THEORY,
                f'Case "{case.name}" references unknown theory "{case.theory_name}".',
            )
        )


def _check_case_lets(document: Document, symbols: SymbolTable) -> None:
    for case in document.cases:
        theory = symbols.theories[case.theory_name]
        instance_names: set[str] = set()
        for let in case.lets:
            if let.name in instance_names:
                raise DiagnosticError(
                    Diagnostic(
                        DiagnosticCode.DUPLICATE_TERM,
                        f'Duplicate let declaration "{let.name}" in case '
                        f'"{case.name}".',
                    )
                )
            instance_names.add(let.name)

            if let.kind not in theory.kinds:
                raise DiagnosticError(
                    Diagnostic(
                        DiagnosticCode.UNKNOWN_KIND,
                        f'Unknown kind "{let.kind}" for instance "{let.name}" '
                        f'in case "{case.name}".',
                    )
                )


def _check_case_facts(document: Document, symbols: SymbolTable) -> None:
    for case in document.cases:
        theory = symbols.theories[case.theory_name]
        instance_kinds = {let.name: let.kind for let in case.lets}
        for fact in case.facts:
            if isinstance(fact, SurfaceStatement):
                fact = desugar_surface_statement(fact, theory)
            if isinstance(fact, PredicateCall):
                _check_case_call(fact, case, theory, instance_kinds)


def _check_case_asks(document: Document, symbols: SymbolTable) -> None:
    for case in document.cases:
        theory = symbols.theories[case.theory_name]
        instance_kinds = {let.name: let.kind for let in case.lets}
        for ask in case.asks:
            if isinstance(ask.expression, PredicateCall):
                _check_case_call(ask.expression, case, theory, instance_kinds)


def _check_case_call(
    call: PredicateCall,
    case: CaseDecl,
    theory: TheorySymbols,
    instance_kinds: dict[str, str],
) -> None:
    canonicalize_predicate(call, theory)
    term = resolve_term(theory, call.name)
    for value, parameter in zip(call.args, term.args, strict=True):
        received_kind = instance_kinds.get(value)
        if received_kind is None:
            raise DiagnosticError(
                Diagnostic(
                    DiagnosticCode.TYPE_MISMATCH,
                    f'Value "{value}" in {call.name} is not declared with '
                    f'let in case "{case.name}".',
                )
            )
        if received_kind != parameter.kind:
            raise DiagnosticError(
                Diagnostic(
                    DiagnosticCode.TYPE_MISMATCH,
                    f'Term "{call.name}" expects argument "{parameter.name}" '
                    f'to have kind "{parameter.kind}", but "{value}" has '
                    f'kind "{received_kind}".',
                )
            )


def _check_term_kinds(theory: TheorySymbols) -> None:
    for posit in theory.posits.values():
        for arg in posit.args:
            _require_known_kind(theory, arg, f'posit "{posit.name}"')

    for derive in theory.derives.values():
        for arg in derive.args:
            _require_known_kind(theory, arg, f'derive "{derive.name}"')


def _check_derive_variable_scopes(theory: TheorySymbols) -> None:
    for derive in theory.derives.values():
        scope = {arg.name: arg.kind for arg in derive.args}
        _check_derive_expressions(derive.name, derive.body, theory, scope)


def _check_derive_expressions(
    derive_name: str,
    expressions: tuple[Expression, ...],
    theory: TheorySymbols,
    scope: dict[str, str],
) -> None:
    for expression in expressions:
        if isinstance(expression, SomeExpression):
            if expression.var_kind not in theory.kinds:
                raise DiagnosticError(
                    Diagnostic(
                        DiagnosticCode.UNKNOWN_KIND,
                        f'Unknown kind "{expression.var_kind}" for some '
                        f'variable "{expression.var_name}".',
                    )
                )
            if expression.var_name in scope:
                raise DiagnosticError(
                    Diagnostic(
                        DiagnosticCode.MALFORMED_DERIVE,
                        f'Some variable "{expression.var_name}" is already '
                        f'declared in derive "{derive_name}".',
                    )
                )
            local_scope = dict(scope)
            local_scope[expression.var_name] = expression.var_kind
            _check_derive_expressions(
                derive_name,
                expression.body,
                theory,
                local_scope,
            )
            continue

        was_surface = isinstance(expression, SurfaceStatement)
        if was_surface:
            expression = desugar_surface_statement(expression, theory)
        if not isinstance(expression, PredicateCall):
            continue
        for variable in expression.args:
            if variable not in scope:
                raise DiagnosticError(
                    Diagnostic(
                        DiagnosticCode.MALFORMED_DERIVE,
                        f'Variable "{variable}" in derive "{derive_name}" '
                        "is not declared in its header or local some block.",
                    )
                )
        if was_surface:
            term = resolve_term(theory, expression.name)
            for variable, argument in zip(expression.args, term.args, strict=True):
                if scope[variable] != argument.kind:
                    raise DiagnosticError(
                        Diagnostic(
                            DiagnosticCode.TYPE_MISMATCH,
                            f'Variable "{variable}" has kind '
                            f'"{scope[variable]}", but readable term '
                            f'"{expression.name}" expects "{argument.kind}".',
                        )
                    )


def _require_known_kind(
    theory: TheorySymbols,
    arg: ArgDecl,
    context: str,
) -> None:
    if arg.kind in theory.kinds:
        return
    raise DiagnosticError(
        Diagnostic(
            DiagnosticCode.UNKNOWN_KIND,
            f'Unknown kind "{arg.kind}" for argument "{arg.name}" in {context}.',
        )
    )
