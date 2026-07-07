"""Desugaring of readable PFL statements into canonical calls."""

from dataclasses import dataclass
import re

from pfl.ast_nodes import PositDecl
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
            f'missing placeholder(s): {", ".join(missing)}',
        )
    if duplicates:
        raise _malformed_reads(
            posit,
            f'duplicate placeholder(s): {", ".join(duplicates)}',
        )
    return ReadsMatcher(posit.name, argument_names, tuple(tokens))


def compile_theory_reads(theory: TheorySymbols) -> tuple[ReadsMatcher, ...]:
    return tuple(
        compile_reads_template(posit)
        for posit in theory.posits.values()
        if posit.reads is not None
    )


def _malformed_reads(posit: PositDecl, detail: str) -> DiagnosticError:
    return DiagnosticError(
        Diagnostic(
            DiagnosticCode.MALFORMED_POSIT,
            f'Malformed reads template for posit "{posit.name}": {detail}.',
        )
    )
