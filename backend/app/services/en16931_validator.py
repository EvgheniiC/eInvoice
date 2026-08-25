import logging
import os
import subprocess
import tempfile
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set
from xml.etree.ElementTree import ParseError as EtParseError

from app.core.config import settings
from app.core.error_events import log_event, log_timeout
from app.helper_functions.safe_xml import UnsafeXmlError, parse_xml
from app.schemas.invoice import (
    InvoiceParseResponse,
    ValidationIssue,
    ValidationStatus,
)
from app.services.kosit_report import (
    KositReport,
    engine_version_from_jar,
    find_kosit_report,
    parse_kosit_report,
    read_scenarios_label,
)
from app.services.validation_messages import enrich_issue
from app.services.validation_profile import InvoiceProfile, extract_invoice_profile

_UNAVAILABLE_CODES: Set[str] = {
    "KOSIT_NOT_CONFIGURED",
    "KOSIT_REQUIRED_UNAVAILABLE",
    "KOSIT_PATH_INVALID",
    "JAVA_NOT_FOUND",
    "KOSIT_TIMEOUT",
    "KOSIT_ERROR",
}


@dataclass
class ValidationResult:
    """Outcome of EN 16931 / XRechnung validation pass."""

    status: ValidationStatus
    issues: List[ValidationIssue] = field(default_factory=list)
    engine: str = "business_rules"
    engine_version: Optional[str] = None
    scenarios_version: Optional[str] = None
    standard_version: Optional[str] = None
    profile: Optional[str] = None
    profile_id: Optional[str] = None
    full_check_completed: bool = False


@dataclass
class KositRunResult:
    """Result of an optional/required KoSIT CLI invocation."""

    completed: bool
    issues: List[ValidationIssue]
    engine_version: Optional[str] = None
    scenarios_version: Optional[str] = None


def validate_invoice(
    xml_text: str,
    parsed: InvoiceParseResponse,
    *,
    request_id: Optional[str] = None,
) -> ValidationResult:
    """
    Validate invoice XML against business rules and KoSIT when configured.

    Production always requires the official KoSIT validator. Without a completed
    KoSIT run the status never becomes VALID.
    """
    issues: List[ValidationIssue] = []
    profile: InvoiceProfile = extract_invoice_profile(xml_text)
    issues.extend(_check_well_formed_xml(xml_text))
    if not profile.profile_id:
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
    issues.extend(_check_required_business_fields(parsed))
    issues.extend(_check_amount_consistency(parsed))

    kosit: KositRunResult = _run_kosit(xml_text, request_id=request_id)
    issues.extend(kosit.issues)

    enriched: List[ValidationIssue] = [enrich_issue(issue) for issue in issues]
    status: ValidationStatus = _status_from_issues(
        enriched,
        full_validation_completed=kosit.completed,
    )
    return ValidationResult(
        status=status,
        issues=enriched,
        engine="kosit" if kosit.completed else "business_rules",
        engine_version=kosit.engine_version,
        scenarios_version=kosit.scenarios_version,
        standard_version=profile.standard_version,
        profile=profile.profile,
        profile_id=profile.profile_id,
        full_check_completed=kosit.completed,
    )


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
                    level="error",
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

    breakdown_amounts: List[Decimal] = [
        item.amount for item in parsed.totals.tax_breakdown if item.amount is not None
    ]
    if breakdown_amounts and tax is not None:
        breakdown_sum: Decimal = sum(breakdown_amounts, Decimal("0")).quantize(Decimal("0.01"))
        if abs(breakdown_sum - tax.quantize(Decimal("0.01"))) > Decimal("0.05"):
            issues.append(
                ValidationIssue(
                    level="warning",
                    category="business",
                    code="TAX_BREAKDOWN_MISMATCH",
                    message=(
                        f"Summe der MwSt-Zeilen ({breakdown_sum}) weicht vom "
                        f"MwSt-Betrag ({tax}) ab."
                    ),
                )
            )
    return issues


def _run_kosit(
    xml_text: str,
    *,
    request_id: Optional[str] = None,
) -> KositRunResult:
    """
    Invoke official KoSIT validator via Java CLI when configured.

    Never logs invoice XML contents or report payloads.
    """
    scenarios_label: Optional[str] = read_scenarios_label(settings.kosit_scenarios_xml)
    jar_version: Optional[str] = engine_version_from_jar(settings.kosit_validator_jar)

    if not settings.kosit_validator_jar or not settings.kosit_scenarios_xml:
        return KositRunResult(
            completed=False,
            issues=_unavailable_issues(configured=False),
            engine_version=jar_version,
            scenarios_version=scenarios_label,
        )

    jar: str = settings.kosit_validator_jar
    scenarios: str = settings.kosit_scenarios_xml
    if not Path(jar).is_file() or not Path(scenarios).is_file():
        log_event(
            logging.WARNING,
            "kosit_path_invalid",
            fields={"request_id": request_id},
        )
        return KositRunResult(
            completed=False,
            issues=_unavailable_issues(configured=True, path_invalid=True),
            engine_version=jar_version,
            scenarios_version=scenarios_label,
        )

    try:
        with tempfile.TemporaryDirectory(prefix="kosit_") as tmp_dir:
            xml_path: Path = Path(tmp_dir) / "invoice.xml"
            xml_path.write_text(xml_text, encoding="utf-8")
            command: List[str] = build_kosit_command(
                java_bin=settings.kosit_java_bin,
                jar=jar,
                scenarios=scenarios,
                output_dir=tmp_dir,
                xml_path=str(xml_path),
                max_heap_mb=settings.kosit_java_max_heap_mb,
            )
            run_kwargs: Dict[str, Any] = {
                "capture_output": True,
                "stdin": subprocess.DEVNULL,
                "text": True,
                "timeout": settings.kosit_timeout_seconds,
                "check": False,
            }
            preexec: Optional[Callable[[], None]] = kosit_preexec_fn(
                timeout_seconds=settings.kosit_timeout_seconds,
            )
            if preexec is not None:
                run_kwargs["preexec_fn"] = preexec
            completed: subprocess.CompletedProcess[str] = subprocess.run(
                command,
                **run_kwargs,
            )
            report_path: Optional[Path] = find_kosit_report(Path(tmp_dir))
            report: Optional[KositReport] = None
            if report_path is not None:
                report = parse_kosit_report(report_path.read_text(encoding="utf-8"))

            engine_version: Optional[str] = (
                report.engine_version if report is not None else None
            ) or jar_version
            scenarios_version: Optional[str] = (
                report.scenario_name if report is not None else None
            ) or scenarios_label

            issues: List[ValidationIssue] = []
            if report is not None:
                issues.extend(report.issues)

            if completed.returncode == 0:
                if not any(issue.code == "KOSIT_OK" for issue in issues):
                    issues.append(
                        ValidationIssue(
                            level="info",
                            category="schema",
                            code="KOSIT_OK",
                            message="KoSIT-Validator: Rechnung akzeptiert (Schematron/Schema).",
                        )
                    )
                return KositRunResult(
                    completed=True,
                    issues=issues,
                    engine_version=engine_version,
                    scenarios_version=scenarios_version,
                )

            log_event(
                logging.WARNING,
                "kosit_failed",
                fields={
                    "request_id": request_id,
                    "returncode": completed.returncode,
                    "issue_count": len(issues),
                },
            )
            if not issues:
                issues.append(
                    ValidationIssue(
                        level="error",
                        category="schema",
                        code="KOSIT_FAILED",
                        message="KoSIT-Validator: Rechnung entspricht nicht den Prüfregeln.",
                    )
                )
            return KositRunResult(
                completed=True,
                issues=issues,
                engine_version=engine_version,
                scenarios_version=scenarios_version,
            )
    except FileNotFoundError:
        log_event(
            logging.ERROR,
            "kosit_java_missing",
            fields={"request_id": request_id},
        )
        return KositRunResult(
            completed=False,
            issues=[
                ValidationIssue(
                    level="warning",
                    category="info",
                    code="JAVA_NOT_FOUND",
                    message="Java-Binary nicht gefunden. KoSIT-Prüfung nicht ausgeführt.",
                ),
                *_required_unavailable_issue(),
            ],
            engine_version=jar_version,
            scenarios_version=scenarios_label,
        )
    except subprocess.TimeoutExpired:
        log_timeout(
            component="kosit",
            request_id=request_id,
            timeout_seconds=settings.kosit_timeout_seconds,
        )
        return KositRunResult(
            completed=False,
            issues=[
                ValidationIssue(
                    level="warning",
                    category="info",
                    code="KOSIT_TIMEOUT",
                    message="KoSIT-Validator-Timeout. Vollständige Prüfung nicht abgeschlossen.",
                ),
                *_required_unavailable_issue(),
            ],
            engine_version=jar_version,
            scenarios_version=scenarios_label,
        )
    except Exception:
        log_event(
            logging.ERROR,
            "kosit_error",
            fields={"request_id": request_id, "exc_type": "Exception"},
        )
        return KositRunResult(
            completed=False,
            issues=[
                ValidationIssue(
                    level="warning",
                    category="info",
                    code="KOSIT_ERROR",
                    message="KoSIT konnte nicht ausgeführt werden.",
                ),
                *_required_unavailable_issue(),
            ],
            engine_version=jar_version,
            scenarios_version=scenarios_label,
        )


def _unavailable_issues(*, configured: bool, path_invalid: bool = False) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []
    if path_invalid:
        issues.append(
            ValidationIssue(
                level="warning",
                category="info",
                code="KOSIT_PATH_INVALID",
                message="KoSIT-Pfade sind gesetzt, aber JAR/Szenarien-Datei nicht gefunden.",
            )
        )
    elif not configured:
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
    issues.extend(_required_unavailable_issue())
    return issues


def _required_unavailable_issue() -> List[ValidationIssue]:
    if not settings.require_kosit:
        return []
    return [
        ValidationIssue(
            level="warning",
            category="info",
            code="KOSIT_REQUIRED_UNAVAILABLE",
            message=(
                "In dieser Umgebung ist die volle EN-16931-/XRechnung-Prüfung mit KoSIT "
                "Pflicht, steht aber nicht zur Verfügung. Das Ergebnis gilt nicht als gültig."
            ),
        )
    ]


def _status_from_issues(
    issues: List[ValidationIssue],
    *,
    full_validation_completed: bool,
) -> ValidationStatus:
    has_error: bool = any(
        issue.level == "error" and issue.code not in _UNAVAILABLE_CODES for issue in issues
    )
    has_warning: bool = any(issue.level == "warning" for issue in issues)
    if has_error:
        return ValidationStatus.INVALID
    if not full_validation_completed:
        return ValidationStatus.NOT_CHECKED
    if has_warning:
        return ValidationStatus.WARNING
    return ValidationStatus.VALID


def build_kosit_command(
    *,
    java_bin: str,
    jar: str,
    scenarios: str,
    output_dir: str,
    xml_path: str,
    max_heap_mb: int,
) -> List[str]:
    """Build the KoSIT CLI with a bounded JVM heap. JVM flags must precede -jar."""
    heap_mb: int = max(64, max_heap_mb)
    return [
        java_bin,
        f"-Xmx{heap_mb}m",
        "-Xms32m",
        "-Djava.awt.headless=true",
        "-jar",
        jar,
        "-s",
        scenarios,
        "-o",
        output_dir,
        xml_path,
    ]


def kosit_preexec_fn(
    *,
    timeout_seconds: int,
) -> Optional[Callable[[], None]]:
    """Return a POSIX preexec hook that caps CPU and disables core dumps."""
    if os.name != "posix":
        return None
    try:
        import resource
    except ImportError:
        return None

    cpu_limit: int = max(5, timeout_seconds + 5)

    def _apply_limits() -> None:
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_limit, cpu_limit))
        # RLIMIT_AS prevents the JVM from reserving compressed class space.
        # Heap and total resident memory are bounded by -Xmx and systemd MemoryMax.
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))

    return _apply_limits
