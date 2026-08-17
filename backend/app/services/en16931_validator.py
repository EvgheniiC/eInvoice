import logging
import re
import subprocess
import tempfile
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import List, Optional
from xml.etree.ElementTree import ParseError as EtParseError

from app.core.config import settings
from app.core.error_events import log_event, log_timeout
from app.helper_functions.safe_xml import UnsafeXmlError, parse_xml
from app.schemas.invoice import (
    InvoiceParseResponse,
    ValidationIssue,
    ValidationStatus,
)


@dataclass
class ValidationResult:
    """Outcome of EN 16931 / XRechnung validation pass."""

    status: ValidationStatus
    issues: List[ValidationIssue] = field(default_factory=list)
    engine: str = "business_rules"


def validate_invoice(
    xml_text: str,
    parsed: InvoiceParseResponse,
    *,
    request_id: Optional[str] = None,
) -> ValidationResult:
    """
    Validate invoice XML against business rules and optionally KoSIT.

    Full Schematron/XRechnung CIUS rules require the official KoSIT validator.
    Without it we still run structural + semantic business checks and label them clearly.
    """
    issues: List[ValidationIssue] = []
    issues.extend(_check_well_formed_xml(xml_text))
    issues.extend(_check_profile_hint(xml_text))
    issues.extend(_check_required_business_fields(parsed))
    issues.extend(_check_amount_consistency(parsed))

    kosit_issues: List[ValidationIssue] = _run_kosit_if_configured(
        xml_text,
        request_id=request_id,
    )
    kosit_completed: bool = any(
        issue.code in {"KOSIT_OK", "KOSIT_FAILED"} for issue in kosit_issues
    )
    if kosit_issues:
        issues.extend(kosit_issues)
    if not settings.kosit_validator_jar or not settings.kosit_scenarios_xml:
        issues.append(
            ValidationIssue(
                level="info",
                category="info",
                code="KOSIT_NOT_CONFIGURED",
                message=(
                    "Vollständige EN 16931 / XRechnung-Schematron-Prüfung (KoSIT) ist nicht "
                    "konfiguriert. Geprüft wurden Struktur und fachliche Pflichtfelder. "
                    "Kein Nachweis für Vorsteuerabzug."
                ),
            )
        )

    engine: str = "kosit" if kosit_completed else "business_rules"
    status: ValidationStatus = _status_from_issues(
        issues,
        full_validation_completed=kosit_completed,
    )
    return ValidationResult(status=status, issues=issues, engine=engine)


def _check_well_formed_xml(xml_text: str) -> List[ValidationIssue]:
    try:
        parse_xml(xml_text)
        return []
    except UnsafeXmlError as exc:
        return [
            ValidationIssue(
                level="error",
                category="schema",
                code="UNSAFE_XML",
                message=str(exc),
            )
        ]
    except EtParseError as exc:
        return [
            ValidationIssue(
                level="error",
                category="schema",
                code="XML_NOT_WELL_FORMED",
                message=f"XML ist nicht wohlgeformt: {exc}",
            )
        ]


def _check_profile_hint(xml_text: str) -> List[ValidationIssue]:
    """Detect EN 16931 / XRechnung / ZUGFeRD profile identifiers when present."""
    issues: List[ValidationIssue] = []
    lowered: str = xml_text.lower()
    has_en16931: bool = "en16931" in lowered or "en 16931" in lowered
    has_xrechnung: bool = "xrechnung" in lowered
    has_zugferd: bool = "zugferd" in lowered or "factur-x" in lowered or "facturx" in lowered

    if not (has_en16931 or has_xrechnung or has_zugferd):
        issues.append(
            ValidationIssue(
                level="warning",
                category="business",
                code="PROFILE_UNKNOWN",
                message=(
                    "Kein EN-16931-/XRechnung-/ZUGFeRD-Profilkennzeichen gefunden. "
                    "Bitte prüfen, ob die Datei dem Standard entspricht."
                ),
            )
        )
    return issues


def _check_required_business_fields(parsed: InvoiceParseResponse) -> List[ValidationIssue]:
    """Mandatory semantic fields inspired by EN 16931 BTs (not a full ruleset)."""
    issues: List[ValidationIssue] = []

    if not parsed.invoice_number:
        issues.append(
            ValidationIssue(
                level="error",
                category="business",
                code="BT-1_MISSING",
                message="Pflichtfeld fehlt: Rechnungsnummer (BT-1).",
            )
        )
    if not parsed.issue_date:
        issues.append(
            ValidationIssue(
                level="error",
                category="business",
                code="BT-2_MISSING",
                message="Pflichtfeld fehlt: Rechnungsdatum (BT-2).",
            )
        )
    if not parsed.totals or not parsed.totals.currency:
        issues.append(
            ValidationIssue(
                level="error",
                category="business",
                code="BT-5_MISSING",
                message="Pflichtfeld fehlt: Währungscode (BT-5).",
            )
        )
    if not parsed.seller or not parsed.seller.name:
        issues.append(
            ValidationIssue(
                level="error",
                category="business",
                code="BG-4_MISSING",
                message="Pflichtfeld fehlt: Name des Verkäufers (BG-4 / BT-27).",
            )
        )
    if not parsed.buyer or not parsed.buyer.name:
        issues.append(
            ValidationIssue(
                level="warning",
                category="business",
                code="BG-7_MISSING",
                message="Käufername fehlt oder konnte nicht gelesen werden (BG-7).",
            )
        )
    if not parsed.totals or parsed.totals.gross is None:
        issues.append(
            ValidationIssue(
                level="error",
                category="business",
                code="BT-112_MISSING",
                message="Pflichtfeld fehlt: Rechnungsgesamtbetrag brutto (BT-112).",
            )
        )
    if not parsed.line_items:
        issues.append(
            ValidationIssue(
                level="error",
                category="business",
                code="BG-25_MISSING",
                message="Keine Rechnungspositionen gefunden (BG-25).",
            )
        )
    return issues


def _check_amount_consistency(parsed: InvoiceParseResponse) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []
    if not parsed.totals:
        return issues

    net: Optional[Decimal] = parsed.totals.net
    tax: Optional[Decimal] = parsed.totals.tax
    gross: Optional[Decimal] = parsed.totals.gross

    if net is not None and tax is not None and gross is not None:
        expected: Decimal = (net + tax).quantize(Decimal("0.01"))
        if abs(expected - gross.quantize(Decimal("0.01"))) > Decimal("0.05"):
            issues.append(
                ValidationIssue(
                    level="warning",
                    category="business",
                    code="AMOUNT_INCONSISTENT",
                    message=(
                        f"Summenprüfung: Netto ({net}) + MwSt ({tax}) = {expected}, "
                        f"aber Brutto ist {gross}. Bitte Lieferanten kontaktieren."
                    ),
                )
            )

    line_sum: Decimal = Decimal("0")
    has_line_nets: bool = False
    for item in parsed.line_items:
        if item.net_amount is not None:
            line_sum += item.net_amount
            has_line_nets = True
    rounded_line_sum: Decimal = line_sum.quantize(Decimal("0.01"))
    if (
        has_line_nets
        and net is not None
        and abs(rounded_line_sum - net.quantize(Decimal("0.01"))) > Decimal("0.10")
    ):
        issues.append(
            ValidationIssue(
                level="warning",
                category="business",
                code="LINE_SUM_MISMATCH",
                message=(
                    f"Summe der Positionen ({rounded_line_sum}) weicht vom Nettobetrag "
                    f"({net}) ab. Kann durch Zu-/Abschläge bedingt sein."
                ),
            )
        )
    return issues


def _run_kosit_if_configured(
    xml_text: str,
    *,
    request_id: Optional[str] = None,
) -> List[ValidationIssue]:
    """
    Optionally invoke official KoSIT validator via Java CLI.

    Requires settings.kosit_validator_jar and settings.kosit_scenarios_xml.
    Never logs invoice XML contents.
    """
    jar: Optional[str] = settings.kosit_validator_jar
    scenarios: Optional[str] = settings.kosit_scenarios_xml
    if not jar or not scenarios:
        return []
    if not Path(jar).is_file() or not Path(scenarios).is_file():
        log_event(
            logging.WARNING,
            "kosit_path_invalid",
            fields={"request_id": request_id},
        )
        return [
            ValidationIssue(
                level="warning",
                category="info",
                code="KOSIT_PATH_INVALID",
                message="KoSIT-Pfade sind gesetzt, aber JAR/Szenarien-Datei nicht gefunden.",
            )
        ]

    tmp_xml: Optional[Path] = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".xml", delete=False, mode="w", encoding="utf-8") as handle:
            handle.write(xml_text)
            tmp_xml = Path(handle.name)

        command: List[str] = [
            settings.kosit_java_bin,
            "-jar",
            jar,
            "-s",
            scenarios,
            "-o",
            str(tmp_xml.parent),
            str(tmp_xml),
        ]
        completed: subprocess.CompletedProcess[str] = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=settings.kosit_timeout_seconds,
            check=False,
        )
        combined: str = f"{completed.stdout}\n{completed.stderr}"
        if completed.returncode == 0:
            return [
                ValidationIssue(
                    level="info",
                    category="schema",
                    code="KOSIT_OK",
                    message="KoSIT-Validator: Rechnung akzeptiert (Schematron/Schema).",
                )
            ]

        detail: str = _extract_kosit_message(combined) or "KoSIT meldet Validierungsfehler."
        log_event(
            logging.WARNING,
            "kosit_failed",
            fields={"request_id": request_id, "detail": detail},
        )
        return [
            ValidationIssue(
                level="error",
                category="schema",
                code="KOSIT_FAILED",
                message=f"KoSIT-Validator: {detail}",
            )
        ]
    except FileNotFoundError:
        log_event(
            logging.ERROR,
            "kosit_java_missing",
            fields={"request_id": request_id, "java_bin": settings.kosit_java_bin},
        )
        return [
            ValidationIssue(
                level="warning",
                category="info",
                code="JAVA_NOT_FOUND",
                message=f"Java-Binary nicht gefunden ({settings.kosit_java_bin}).",
            )
        ]
    except subprocess.TimeoutExpired:
        log_timeout(
            component="kosit",
            request_id=request_id,
            timeout_seconds=settings.kosit_timeout_seconds,
        )
        return [
            ValidationIssue(
                level="warning",
                category="info",
                code="KOSIT_TIMEOUT",
                message="KoSIT-Validator-Timeout.",
            )
        ]
    except Exception as exc:
        log_event(
            logging.ERROR,
            "kosit_error",
            fields={"request_id": request_id, "exc_type": type(exc).__name__},
        )
        return [
            ValidationIssue(
                level="warning",
                category="info",
                code="KOSIT_ERROR",
                message="KoSIT konnte nicht ausgeführt werden.",
            )
        ]
    finally:
        if tmp_xml is not None:
            tmp_xml.unlink(missing_ok=True)


def _extract_kosit_message(output: str) -> Optional[str]:
    lines: List[str] = [line.strip() for line in output.splitlines() if line.strip()]
    for line in lines:
        if re.search(r"error|fehler|failed|invalid", line, re.IGNORECASE):
            return line[:400]
    if lines:
        return lines[-1][:400]
    return None


def _status_from_issues(
    issues: List[ValidationIssue],
    *,
    full_validation_completed: bool,
) -> ValidationStatus:
    has_error: bool = any(issue.level == "error" for issue in issues)
    has_warning: bool = any(issue.level == "warning" for issue in issues)
    if has_error:
        return ValidationStatus.INVALID
    if not full_validation_completed:
        return ValidationStatus.NOT_CHECKED
    if has_warning:
        return ValidationStatus.WARNING
    return ValidationStatus.VALID
