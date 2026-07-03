"""Evaluation of PFL ask statements."""

from dataclasses import dataclass
from enum import Enum

from pfl.ast_nodes import AskDecl, CaseDecl, PredicateCall
from pfl.canonicalize import canonicalize_predicate
from pfl.diagnostics import Diagnostic, DiagnosticCode, DiagnosticError
from pfl.engine import FactStore
from pfl.ir import Predicate
from pfl.symbols import TheorySymbols


class QueryStatus(str, Enum):
    TRUE = "true"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class QueryResult:
    predicate: Predicate
    status: QueryStatus


def evaluate_ask(
    ask: AskDecl,
    theory: TheorySymbols,
    facts: FactStore,
) -> QueryResult:
    """Evaluate one canonical ask against the final fact store."""

    if not isinstance(ask.expression, PredicateCall):
        raise DiagnosticError(
            Diagnostic(
                DiagnosticCode.UNKNOWN_ASK_TERM,
                "Ask expression has not been desugared to a canonical predicate.",
            )
        )

    predicate = canonicalize_predicate(ask.expression, theory)
    status = QueryStatus.TRUE if predicate in facts else QueryStatus.UNKNOWN
    return QueryResult(predicate, status)


def evaluate_case_asks(
    case: CaseDecl,
    theory: TheorySymbols,
    facts: FactStore,
) -> tuple[QueryResult, ...]:
    return tuple(evaluate_ask(ask, theory, facts) for ask in case.asks)
