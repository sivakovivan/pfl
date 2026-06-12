import pytest

from pfl.diagnostics import (
    Diagnostic,
    DiagnosticCode,
    DiagnosticError,
    Severity,
)


def test_formats_error_diagnostic() -> None:
    diagnostic = Diagnostic(
        DiagnosticCode.UNDEFINED_TERM,
        'Term "desires" is not defined.',
    )

    assert str(diagnostic) == 'Error PFL001: Term "desires" is not defined.'


def test_diagnostic_error_exposes_diagnostic() -> None:
    diagnostic = Diagnostic(
        DiagnosticCode.UNUSED_KIND,
        'Kind "State" is not used.',
        Severity.WARNING,
    )

    with pytest.raises(DiagnosticError) as raised:
        raise DiagnosticError(diagnostic)

    assert raised.value.diagnostic is diagnostic
    assert str(raised.value) == 'Warning PFL101: Kind "State" is not used.'
