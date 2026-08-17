"""Plain-language German copy for validation issues, including BT/BG codes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from app.schemas.invoice import ValidationIssue
from app.services.validation_profile import extract_bt_code


@dataclass(frozen=True)
class IssueCopy:
    """Human-readable explanation attached to a validation code."""

    explanation: str
    bt_code: Optional[str] = None
    field: Optional[str] = None


_DEFAULT_ERROR_EXPLANATION: str = (
    "Bitte den Lieferanten um eine korrigierte Rechnung bitten und die Datei "
    "danach erneut prüfen."
)

ISSUE_COPY: Dict[str, IssueCopy] = {
    "BT-1_MISSING": IssueCopy(
        explanation=(
            "Ohne Rechnungsnummer kann die Rechnung nicht eindeutig zugeordnet werden."
        ),
        bt_code="BT-1",
        field="invoice_number",
    ),
    "MISSING_INVOICE_NUMBER": IssueCopy(
        explanation=(
            "Ohne Rechnungsnummer kann die Rechnung nicht eindeutig zugeordnet werden."
        ),
        bt_code="BT-1",
        field="invoice_number",
    ),
    "BT-2_MISSING": IssueCopy(
        explanation="Ohne Rechnungsdatum fehlt ein Pflichtfeld der EN 16931.",
        bt_code="BT-2",
        field="issue_date",
    ),
    "BT-5_MISSING": IssueCopy(
        explanation="Ohne Währungscode können Beträge nicht korrekt gebucht werden.",
        bt_code="BT-5",
        field="currency",
    ),
    "BG-4_MISSING": IssueCopy(
        explanation="Ohne Verkäufernamen ist unklar, an wen gezahlt werden soll.",
        bt_code="BT-27",
        field="seller",
    ),
    "BG-7_MISSING": IssueCopy(
        explanation="Der Käufername fehlt oder konnte nicht gelesen werden.",
        bt_code="BT-44",
        field="buyer",
    ),
    "BT-31_MISSING": IssueCopy(
        explanation=(
            "USt-IdNr. des Verkäufers fehlt. Für deutsche XRechnungen ist eine "
            "steuerliche Kennung des Verkäufers üblicherweise erforderlich."
        ),
        bt_code="BT-31",
        field="seller_vat_id",
    ),
    "BT-84_MISSING": IssueCopy(
        explanation=(
            "Keine IBAN gefunden. Prüfen Sie, ob die Zahlungsdaten vollständig sind, "
            "bevor Sie überweisen."
        ),
        bt_code="BT-84",
        field="iban",
    ),
    "BT-112_MISSING": IssueCopy(
        explanation="Ohne Bruttobetrag kann nicht entschieden werden, wie viel zu zahlen ist.",
        bt_code="BT-112",
        field="gross",
    ),
    "BG-25_MISSING": IssueCopy(
        explanation="Ohne Positionen ist die Rechnung unvollständig.",
        bt_code="BG-25",
        field="line_items",
    ),
    "MISSING_LINE_ITEMS": IssueCopy(
        explanation="Ohne Positionen ist die Rechnung unvollständig.",
        bt_code="BG-25",
        field="line_items",
    ),
    "MISSING_AMOUNTS": IssueCopy(
        explanation="Beträge konnten nicht gelesen werden. Bitte Datei und Lieferanten prüfen.",
        bt_code="BT-112",
        field="gross",
    ),
    "AMOUNT_INCONSISTENT": IssueCopy(
        explanation=(
            "Netto plus MwSt muss dem Bruttobetrag entsprechen (BR-CO-15 / BT-109, "
            "BT-110, BT-112). Nicht zahlen, bevor der Lieferant korrigiert."
        ),
        bt_code="BT-112",
        field="gross",
    ),
    "LINE_SUM_MISMATCH": IssueCopy(
        explanation=(
            "Die Summe der Positionen weicht vom Nettobetrag ab. Das kann durch "
            "Zu-/Abschläge entstehen — bitte visuell prüfen."
        ),
        bt_code="BT-106",
        field="net",
    ),
    "TAX_BREAKDOWN_MISMATCH": IssueCopy(
        explanation=(
            "Die Summe der MwSt-Zeilen weicht vom ausgewiesenen MwSt-Betrag ab."
        ),
        bt_code="BT-110",
        field="tax",
    ),
    "PROFILE_UNKNOWN": IssueCopy(
        explanation=(
            "Es wurde kein EN-16931-/XRechnung-/ZUGFeRD-Profil gefunden. "
            "Bitte prüfen, ob die Datei dem Standard entspricht."
        ),
    ),
    "BR-CO-15": IssueCopy(
        explanation=(
            "Rechnungsbetrag mit Umsatzsteuer (BT-112) muss der Summe aus Netto "
            "(BT-109) und MwSt (BT-110) entsprechen."
        ),
        bt_code="BT-112",
        field="gross",
    ),
    "BR-DE-1": IssueCopy(
        explanation="Eine deutsche XRechnung muss Zahlungsanweisungen enthalten.",
        bt_code="BG-16",
    ),
    "BR-DE-15": IssueCopy(
        explanation="Für XRechnung in Deutschland ist eine Leitweg-ID (BT-10) erforderlich.",
        bt_code="BT-10",
    ),
    "BR-DE-16": IssueCopy(
        explanation="Der Verkäufer muss eine steuerliche Kennung angeben.",
        bt_code="BT-31",
        field="seller_vat_id",
    ),
    "KOSIT_NOT_CONFIGURED": IssueCopy(
        explanation=(
            "Es wurden nur Struktur und fachliche Pflichtfelder geprüft. "
            "Das ist kein Nachweis für Vorsteuerabzug."
        ),
    ),
    "KOSIT_REQUIRED_UNAVAILABLE": IssueCopy(
        explanation=(
            "In Produktion muss die volle KoSIT-Prüfung laufen. "
            "Bitte Administrator: Validator-JAR und aktuelle Szenarien konfigurieren."
        ),
    ),
    "KOSIT_PATH_INVALID": IssueCopy(
        explanation="KoSIT-Pfade prüfen: JAR und scenarios.xml müssen existieren.",
    ),
    "JAVA_NOT_FOUND": IssueCopy(
        explanation="Java muss installiert und KOSIT_JAVA_BIN korrekt gesetzt sein.",
    ),
    "KOSIT_TIMEOUT": IssueCopy(
        explanation="Die Prüfung hat zu lange gedauert. Bitte später erneut versuchen.",
    ),
    "KOSIT_ERROR": IssueCopy(
        explanation="KoSIT konnte nicht ausgeführt werden. Bitte Administrator informieren.",
    ),
    "XML_NOT_WELL_FORMED": IssueCopy(
        explanation="Die XML-Datei ist beschädigt. Bitten Sie den Lieferanten um eine neue Datei.",
    ),
    "UNSAFE_XML": IssueCopy(
        explanation="Die Datei wurde aus Sicherheitsgründen abgelehnt.",
    ),
}


def enrich_issue(issue: ValidationIssue) -> ValidationIssue:
    """Fill explanation, BT-code, and field when they can be derived."""
    catalog: Optional[IssueCopy] = ISSUE_COPY.get(issue.code or "")
    bt_code: Optional[str] = issue.bt_code
    field: Optional[str] = issue.field
    explanation: Optional[str] = issue.explanation

    if catalog is not None:
        bt_code = bt_code or catalog.bt_code
        field = field or catalog.field
        explanation = explanation or catalog.explanation

    if bt_code is None:
        bt_code = extract_bt_code(issue.code, issue.message)

    if explanation is None and issue.level == "error" and issue.category in {"schema", "business"}:
        explanation = _DEFAULT_ERROR_EXPLANATION

    if (
        bt_code == issue.bt_code
        and field == issue.field
        and explanation == issue.explanation
    ):
        return issue

    return issue.model_copy(
        update={
            "bt_code": bt_code,
            "field": field,
            "explanation": explanation,
        }
    )
