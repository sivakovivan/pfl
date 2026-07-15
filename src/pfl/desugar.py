"""Desugaring of readable PFL statements into canonical calls."""

from dataclasses import dataclass
import re

from pfl.ast_nodes import PositDecl, PredicateCall, SurfaceStatement
from pfl.diagnostics import Diagnostic, DiagnosticCode, DiagnosticError
from pfl.symbols import TheorySymbols


_PLACEHOLDER = re.compile(r"^\{([A-Za-z_][A-Za-z0-9_]*)\}$")


@dataclass(frozen=True)
class ReadsToken:
    value: str
    is_placeholder: bool = False


@dataclass(frozen=True)
class ReadsMatcher:
    term_name: str
    argument_names: tuple[str, ...]
    tokens: tuple[ReadsToken, ...]


def compile_reads_template(posit: PositDecl) -> ReadsMatcher:
    """Compile a posit's reads text into literal and placeholder tokens."""

    if posit.reads is None:
        raise _malformed_reads(posit, "a reads template is required")

    argument_names = tuple(arg.name for arg in posit.args)
    tokens: list[ReadsToken] = []
    placeholders: list[str] = []
    for raw_token in posit.reads.split():
        placeholder = _PLACEHOLDER.fullmatch(raw_token)
        if placeholder is None:
            tokens.append(ReadsToken(raw_token))
            continue
        name = placeholder.group(1)
        if name not in argument_names:
            raise _malformed_reads(
                posit,
                f'placeholder "{name}" is not a declared argument',
            )
        placeholders.append(name)
        tokens.append(ReadsToken(name, is_placeholder=True))

    missing = [name for name in argument_names if name not in placeholders]
    duplicates = [name for name in argument_names if placeholders.count(name) > 1]
    if missing:
        raise _malformed_reads(
            posit,
            f"missing placeholder(s): {', '.join(missing)}",
        )
    if duplicates:
        raise _malformed_reads(
            posit,
            f"duplicate placeholder(s): {', '.join(duplicates)}",
        )
    return ReadsMatcher(posit.name, argument_names, tuple(tokens))


def compile_theory_reads(theory: TheorySymbols) -> tuple[ReadsMatcher, ...]:
    return tuple(
        compile_reads_template(posit)
        for posit in theory.posits.values()
        if posit.reads is not None
    )


def match_reads_template(
    statement: SurfaceStatement,
    matcher: ReadsMatcher,
) -> PredicateCall | None:
    """Match a readable statement against one compiled template."""

    values = statement.text.split()
    if len(values) != len(matcher.tokens):
        return None

    bindings: dict[str, str] = {}
    for value, token in zip(values, matcher.tokens, strict=True):
        if not token.is_placeholder:
            if value != token.value:
                return None
            continue
        existing = bindings.get(token.value)
        if existing is not None and existing != value:
            return None
        bindings[token.value] = value

    return PredicateCall(
        matcher.term_name,
        tuple(bindings[name] for name in matcher.argument_names),
    )


def desugar_surface_statement(
    statement: SurfaceStatement,
    theory: TheorySymbols,
) -> PredicateCall:
    """Resolve a readable statement to a canonical predicate call."""

    matches = [
        call
        for matcher in compile_theory_reads(theory)
        if (call := match_reads_template(statement, matcher)) is not None
    ]
    if not matches:
        raise DiagnosticError(
            Diagnostic(
                DiagnosticCode.UNDEFINED_TERM,
                f'No reads template matches "{statement.text}" under theory '
                f'"{theory.declaration.name}".',
            )
        )
    if len(matches) > 1:
        names = ", ".join(call.name for call in matches)
        raise DiagnosticError(
            Diagnostic(
                DiagnosticCode.AMBIGUOUS_READS,
                f'Readable statement "{statement.text}" matches multiple '
                f"terms: {names}.",
            )
        )
    return matches[0]


def _malformed_reads(posit: PositDecl, detail: str) -> DiagnosticError:
    return DiagnosticError(
        Diagnostic(
            DiagnosticCode.MALFORMED_POSIT,
            f'Malformed reads template for posit "{posit.name}": {detail}.',
        )
    )
