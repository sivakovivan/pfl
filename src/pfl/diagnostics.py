"""Diagnostic types shared by the PFL frontend and interpreter."""

from dataclasses import dataclass
from enum import Enum


class DiagnosticCode(str, Enum):
    """Stable identifiers for PFL errors and warnings."""

    UNDEFINED_TERM = "PFL001"
    TYPE_MISMATCH = "PFL002"
    UNKNOWN_KIND = "PFL003"
    UNKNOWN_THEORY = "PFL004"
    DUPLICATE_TERM = "PFL005"
    AMBIGUOUS_READS = "PFL006"
    MALFORMED_POSIT = "PFL007"
    MALFORMED_DERIVE = "PFL008"
    UNKNOWN_ASK_TERM = "PFL009"

    UNUSED_KIND = "PFL101"
    UNUSED_POSIT = "PFL102"
    UNUSED_DERIVED_TERM = "PFL103"
    SEMANTIC_DEBT = "PFL104"
    CIRCULAR_DERIVE = "PFL105"
    READS_COLLISION = "PFL106"


class Severity(str, Enum):
    ERROR = "Error"
    WARNING = "Warning"


@dataclass(frozen=True)
class Diagnostic:
    code: DiagnosticCode
    message: str
    severity: Severity = Severity.ERROR

    def __str__(self) -> str:
        return f"{self.severity.value} {self.code.value}: {self.message}"


class DiagnosticError(Exception):
    """Raised when a diagnostic prevents further interpretation."""

    def __init__(self, diagnostic: Diagnostic) -> None:
        self.diagnostic = diagnostic
        super().__init__(str(diagnostic))
