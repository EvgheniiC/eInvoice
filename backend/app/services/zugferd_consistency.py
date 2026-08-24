import re
from decimal import Decimal
from io import BytesIO
from typing import List, Optional, Tuple

import PyPDF2

from app.schemas.invoice import InvoiceParseResponse, MismatchField, ValidationIssue


def compare_pdf_with_xml(
    pdf_content: bytes,
    parsed: InvoiceParseResponse,
) -> Tuple[List[MismatchField], List[str], List[ValidationIssue]]:
    """
    Compare key fields from visible PDF text against parsed XML values.

    Returns mismatch field details, user-facing warning strings, and validation issues.
    """
    pdf_text: str = _extract_pdf_text(pdf_content)
    if not pdf_text.strip():
        warning: str = (
            "PDF-Text konnte nicht gelesen werden — Abgleich PDF↔XML nicht möglich. "
            "Bitte visuelle Prüfung der PDF und Lieferanten kontaktieren bei Unsicherheit."
        )
        return (
            [],
            [warning],
            [
                ValidationIssue(
                    level="warning",
                    category="mismatch",
                    code="PDF_TEXT_EMPTY",
                    message=warning,
                )
            ],
        )

    fields: List[MismatchField] = []
    fields.append(
        _compare_invoice_number(
            pdf_text=pdf_text,
            xml_value=parsed.invoice_number,
        )
    )
    fields.append(
        _compare_date(
            pdf_text=pdf_text,
            xml_value=parsed.issue_date,
            field_name="issue_date",
            label="Rechnungsdatum",
        )
    )
    fields.append(
        _compare_amount(
            pdf_text=pdf_text,
            xml_value=parsed.totals.gross if parsed.totals else None,
            field_name="gross",
            label="Bruttobetrag",
        )
    )
    fields.append(
        _compare_amount(
            pdf_text=pdf_text,
            xml_value=parsed.totals.tax if parsed.totals else None,
            field_name="tax",
            label="MwSt-Betrag",
        )
    )
    seller_iban: Optional[str] = parsed.seller.iban if parsed.seller else None
    fields.append(_compare_iban(pdf_text=pdf_text, xml_value=seller_iban))

    comparable: List[MismatchField] = [item for item in fields if item.pdf_value is not None or item.xml_value]
    mismatches: List[MismatchField] = [item for item in comparable if not item.matched]
    warnings: List[str] = []
    issues: List[ValidationIssue] = []

    if not mismatches and comparable:
        warnings.append("PDF und XML stimmen in den geprüften Schlüsselfeldern überein.")
        issues.append(
            ValidationIssue(
                level="info",
                category="mismatch",
                code="PDF_XML_MATCH",
                message="ZUGFeRD-Abgleich: keine Abweichungen in Nummer, Datum, Beträgen, IBAN.",
            )
        )
    elif mismatches:
        for item in mismatches:
            msg: str = (
                f"Abweichung {item.label}: XML={item.xml_value or '—'} / "
                f"PDF={item.pdf_value or 'nicht gefunden'}. Bitte Lieferanten kontaktieren."
            )
            warnings.append(msg)
            issues.append(
                ValidationIssue(
                    level="warning",
                    category="mismatch",
                    code=f"MISMATCH_{item.field.upper()}",
                    message=msg,
                )
            )

    return fields, warnings, issues


def _extract_pdf_text(content: bytes) -> str:
    try:
        reader: PyPDF2.PdfReader = PyPDF2.PdfReader(BytesIO(content))
        parts: List[str] = []
        for page in reader.pages:
            text: Optional[str] = page.extract_text()
            if text:
                parts.append(text)
        return "\n".join(parts)
    except Exception:
        return ""


def _compare_invoice_number(*, pdf_text: str, xml_value: Optional[str]) -> MismatchField:
    label: str = "Rechnungsnummer"
    if not xml_value:
        return MismatchField(
            field="invoice_number",
            label=label,
            xml_value=None,
            pdf_value=None,
            matched=True,
        )

    normalized_xml: str = _normalize_token(xml_value)
    found: bool = normalized_xml in _normalize_token(pdf_text)
    pdf_value: Optional[str] = xml_value if found else _find_nearby_invoice_candidate(pdf_text)
    return MismatchField(
        field="invoice_number",
        label=label,
        xml_value=xml_value,
        pdf_value=pdf_value if found else pdf_value,
        matched=found,
    )


def _compare_date(
    *,
    pdf_text: str,
    xml_value: Optional[str],
    field_name: str,
    label: str,
) -> MismatchField:
    if not xml_value:
        return MismatchField(
            field=field_name,
            label=label,
            xml_value=None,
            pdf_value=None,
            matched=True,
        )

    variants: List[str] = _date_variants(xml_value)
    found_variant: Optional[str] = None
    for variant in variants:
        if variant in pdf_text.replace(" ", ""):
            found_variant = variant
            break
        if variant in pdf_text:
            found_variant = variant
            break

    return MismatchField(
        field=field_name,
        label=label,
        xml_value=xml_value,
        pdf_value=found_variant,
        matched=found_variant is not None,
    )


def _compare_amount(
    *,
    pdf_text: str,
    xml_value: Optional[Decimal],
    field_name: str,
    label: str,
) -> MismatchField:
    if xml_value is None:
        return MismatchField(
            field=field_name,
            label=label,
            xml_value=None,
            pdf_value=None,
            matched=True,
        )

    xml_str: str = f"{xml_value:.2f}"
    de_str: str = xml_str.replace(".", ",")
    compact_pdf: str = re.sub(r"\s+", "", pdf_text)
    matched: bool = de_str in compact_pdf or xml_str in compact_pdf

    # Also accept thousand separators: 1.234,56 / 1,234.56
    if not matched:
        de_thousands: str = _format_de_thousands(xml_value)
        matched = de_thousands in compact_pdf

    return MismatchField(
        field=field_name,
        label=label,
        xml_value=xml_str,
        pdf_value=de_str if matched else None,
        matched=matched,
    )


def _compare_iban(*, pdf_text: str, xml_value: Optional[str]) -> MismatchField:
    label: str = "IBAN"
    if not xml_value:
        return MismatchField(
            field="iban",
            label=label,
            xml_value=None,
            pdf_value=None,
            matched=True,
        )

    xml_iban: str = xml_value.replace(" ", "").upper()
    pdf_ibans: List[str] = re.findall(r"\b([A-Z]{2}\d{2}[A-Z0-9]{10,30})\b", pdf_text.replace(" ", "").upper())
    matched: bool = xml_iban in pdf_ibans or xml_iban in pdf_text.replace(" ", "").upper()
    pdf_value: Optional[str] = xml_iban if matched else (pdf_ibans[0] if pdf_ibans else None)
    return MismatchField(
        field="iban",
        label=label,
        xml_value=xml_iban,
        pdf_value=pdf_value,
        matched=matched,
    )


def _date_variants(iso_date: str) -> List[str]:
    match: Optional[re.Match[str]] = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", iso_date)
    if not match:
        return [iso_date]
    year, month, day = match.group(1), match.group(2), match.group(3)
    short_year: str = year[-2:]
    numeric_month: str = str(int(month))
    numeric_day: str = str(int(day))
    return [
        iso_date,
        f"{day}.{month}.{year}",
        f"{day}/{month}/{year}",
        f"{day}-{month}-{year}",
        f"{day}{month}{year}",
        f"{year}{month}{day}",
        f"{numeric_day}/{numeric_month}/{year}",
        f"{numeric_day}/{numeric_month}/{short_year}",
        f"{numeric_month}/{numeric_day}/{year}",
        f"{numeric_month}/{numeric_day}/{short_year}",
    ]


def _format_de_thousands(value: Decimal) -> str:
    formatted: str = f"{value:,.2f}"
    # 1,234.56 -> 1.234,56
    return formatted.replace(",", "X").replace(".", ",").replace("X", ".")


def _normalize_token(value: str) -> str:
    return re.sub(r"[\s/\-_.]", "", value).upper()


def _find_nearby_invoice_candidate(pdf_text: str) -> Optional[str]:
    patterns: List[str] = [
        r"(?:Rechnung(?:snummer)?|Invoice\s*(?:No\.?|number)?|Nr\.?)\s*[:#]?\s*([A-Za-z0-9\-/]{3,})",
    ]
    for pattern in patterns:
        match = re.search(pattern, pdf_text, re.IGNORECASE)
        if match:
            return match.group(1)
    return None
