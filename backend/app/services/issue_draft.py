"""Read a plain PDF into an editable draft and check it before XML generation."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from io import BytesIO
from typing import Final, List, Optional

import PyPDF2

from app.schemas.invoice import ValidationIssue
from app.schemas.issue import (
    FieldHint,
    IssueAddress,
    IssueDraft,
    IssueDraftResponse,
    IssueLineInput,
    IssueParty,
)

MONEY_QUANT: Final[Decimal] = Decimal("0.01")
MAX_LINES: Final[int] = 100
UNIT_CODES: Final[frozenset[str]] = frozenset(
    {"C62", "HUR", "DAY", "KGM", "MTR", "LTR", "SET", "MON"}
)
STANDARD_TAX_RATES: Final[frozenset[Decimal]] = frozenset(
    {Decimal("7.00"), Decimal("19.00")}
)

_INVOICE_NUMBER_RE: Final[re.Pattern[str]] = re.compile(
    r"(?:Rechnungs?(?:nummer|nr\.?|-Nr\.?)|Invoice\s*(?:No\.?|Number))"
    r"\s*[:.]?\s*([A-Z0-9][A-Z0-9./\-]{1,40})",
    re.IGNORECASE,
)
_DATE_RE: Final[re.Pattern[str]] = re.compile(
    r"(?:Rechnungsdatum|Datum)\s*[:.]?\s*(\d{2})\.(\d{2})\.(\d{4})",
    re.IGNORECASE,
)
_VAT_RE: Final[re.Pattern[str]] = re.compile(
    r"(?:USt-?IdNr\.?|Umsatzsteuer-?ID|VAT)\s*[:.]?\s*([A-Z]{2}\s?[0-9A-Z]{8,12})",
    re.IGNORECASE,
)
_IBAN_RE: Final[re.Pattern[str]] = re.compile(
    r"IBAN\s*[:.]?[ \t]*([A-Z]{2}\d{2}(?:[ \t]*[A-Z0-9]+)+)",
    re.IGNORECASE,
)
_EMAIL_RE: Final[re.Pattern[str]] = re.compile(
    r"[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}",
    re.IGNORECASE,
)
_BUYER_REFERENCE_RE: Final[re.Pattern[str]] = re.compile(
    r"(?:Leitweg[-\s]?ID|Käuferreferenz|Buyer reference|Bestellnummer)"
    r"\s*[:.]?\s*([A-Z0-9][A-Z0-9./\-]{1,40})",
    re.IGNORECASE,
)
_AMOUNT_RE: Final[re.Pattern[str]] = re.compile(
    r"([0-9]{1,3}(?:\.[0-9]{3})*,\d{2}|[0-9]+,\d{2})"
)
_LABELED_AMOUNT: Final[dict[str, re.Pattern[str]]] = {
    "Netto": re.compile(
        r"(?:Netto(?:betrag)?|Zwischensumme)\s*[:.]?\s*" + _AMOUNT_RE.pattern,
        re.IGNORECASE,
    ),
    "MwSt": re.compile(
        r"(?:MwSt\.?|Umsatzsteuer|USt\.?)\s*(?:\d{1,2}\s*%)?\s*[:.]?\s*" + _AMOUNT_RE.pattern,
        re.IGNORECASE,
    ),
    "Brutto": re.compile(
        r"(?:Brutto(?:betrag)?|Gesamt(?:betrag)?|Rechnungsbetrag|Endbetrag)"
        r"\s*[:.]?\s*" + _AMOUNT_RE.pattern,
        re.IGNORECASE,
    ),
}


@dataclass(frozen=True)
class SellerSeed:
    """Seller fields copied from the signed-in organization. Never taken from the PDF."""

    name: Optional[str] = None
    vat_id: Optional[str] = None
    iban: Optional[str] = None


@dataclass(frozen=True)
class ReadyLine:
    """One line with amounts already rounded for EN 16931."""

    line_id: str
    description: str
    quantity: Decimal
    unit_code: str
    unit_price: Decimal
    line_net: Decimal
    tax_rate: Decimal


@dataclass(frozen=True)
class TaxGroup:
    """VAT total for one rate."""

    rate: Decimal
    basis: Decimal
    amount: Decimal


@dataclass(frozen=True)
class ReadyInvoice:
    """Draft that passed the issuer checks and can be rendered as CII."""

    invoice_number: str
    issue_date: date
    currency: str
    buyer_reference: str
    seller_name: str
    seller_street: str
    seller_postcode: str
    seller_city: str
    seller_country: str
    seller_vat_id: str
    seller_email: str
    seller_contact_name: str
    seller_phone: str
    seller_iban: str
    buyer_name: str
    buyer_street: str
    buyer_postcode: str
    buyer_city: str
    buyer_country: str
    lines: tuple[ReadyLine, ...]
    tax_groups: tuple[TaxGroup, ...]
    line_total: Decimal
    tax_total: Decimal
    grand_total: Decimal


@dataclass(frozen=True)
class PreparedIssue:
    """Either a renderable invoice, or the reasons generation must stop."""

    invoice: Optional[ReadyInvoice]
    blocking: List[ValidationIssue]
    xrechnung_gaps: List[ValidationIssue]


def extract_draft_from_pdf(
    content: bytes,
    filename: str,
    seller: Optional[SellerSeed] = None,
) -> IssueDraftResponse:
    """Build a draft from the PDF text layer. Scans stay empty for manual entry."""
    text, read_error = _read_pdf_text(content)
    hints: List[FieldHint] = []
    warnings: List[str] = []
    if read_error:
        warnings.append(read_error)
    elif not text.strip():
        warnings.append(
            "Im PDF wurde kein Text gefunden. Gescannte Rechnungen müssen von Hand eingetragen werden."
        )

    draft: IssueDraft = _draft_from_text(text, seller=seller, hints=hints, warnings=warnings)
    if not draft.lines:
        draft.lines = [IssueLineInput(unit_code="C62", tax_rate=Decimal("19"))]
    return IssueDraftResponse(
        filename=filename,
        text_found=bool(text.strip()),
        draft=draft,
        hints=hints,
        warnings=warnings,
    )


def prepare_invoice(draft: IssueDraft, *, confirmed: bool) -> PreparedIssue:
    """Check required fields and recompute totals from the lines."""
    blocking: List[ValidationIssue] = []
    if not confirmed:
        blocking.append(
            _issue(
                "CONFIRMED_REQUIRED",
                "Bitte bestätigen, dass Sie der Rechnungsaussteller sind und die Angaben stimmen.",
                field="confirmed",
            )
        )

    invoice_number: str = _clean(draft.invoice_number, max_length=50)
    if not invoice_number:
        blocking.append(_issue("BT-1_MISSING", "Pflichtfeld fehlt: Rechnungsnummer (BT-1).", field="invoice_number"))

    issue_date: Optional[date] = _parse_iso_date(draft.issue_date)
    if issue_date is None:
        blocking.append(_issue("BT-2_MISSING", "Pflichtfeld fehlt: Rechnungsdatum (BT-2).", field="issue_date"))

    currency: str = _clean(draft.currency, max_length=3).upper() or "EUR"
    if currency != "EUR":
        blocking.append(_issue("BT-5_UNSUPPORTED", "In dieser Version ist nur EUR möglich.", field="currency"))

    seller_name: str = _clean(draft.seller.name, max_length=200)
    seller_street: str = _clean(draft.seller.address.line, max_length=200)
    seller_postcode: str = _clean(draft.seller.address.postcode, max_length=20)
    seller_city: str = _clean(draft.seller.address.city, max_length=80)
    seller_country: str = _country(draft.seller.address.country)
    seller_vat: str = _compact_upper(draft.seller.vat_id)
    seller_email: str = _clean(draft.seller.email, max_length=254)
    seller_contact: str = _clean(draft.seller.contact_name, max_length=200)
    seller_phone: str = _clean(draft.seller.phone, max_length=40)
    seller_iban: str = _compact_upper(draft.seller.iban)
    buyer_name: str = _clean(draft.buyer.name, max_length=200)
    buyer_street: str = _clean(draft.buyer.address.line, max_length=200)
    buyer_postcode: str = _clean(draft.buyer.address.postcode, max_length=20)
    buyer_city: str = _clean(draft.buyer.address.city, max_length=80)
    buyer_country: str = _country(draft.buyer.address.country)
    buyer_reference: str = _clean(draft.buyer_reference, max_length=50)

    _require(blocking, seller_name, "BT-27_MISSING", "Pflichtfeld fehlt: Name des Verkäufers (BT-27).", "seller.name")
    _require(blocking, seller_street, "BT-35_MISSING", "Pflichtfeld fehlt: Straße des Verkäufers (BT-35).", "seller.address.line")
    _require(blocking, seller_postcode, "BT-38_MISSING", "Pflichtfeld fehlt: PLZ des Verkäufers (BT-38).", "seller.address.postcode")
    _require(blocking, seller_city, "BT-37_MISSING", "Pflichtfeld fehlt: Ort des Verkäufers (BT-37).", "seller.address.city")
    _require(blocking, seller_country, "BT-40_MISSING", "Pflichtfeld fehlt: Land des Verkäufers (BT-40).", "seller.address.country")
    _require(blocking, seller_vat, "BT-31_MISSING", "Pflichtfeld fehlt: USt-IdNr. des Verkäufers (BT-31).", "seller.vat_id")
    _require(blocking, seller_iban, "BT-84_MISSING", "Pflichtfeld fehlt: IBAN (BT-84).", "seller.iban")
    _require(blocking, buyer_name, "BT-44_MISSING", "Pflichtfeld fehlt: Name des Käufers (BT-44).", "buyer.name")
    _require(blocking, buyer_street, "BT-50_MISSING", "Pflichtfeld fehlt: Straße des Käufers (BT-50).", "buyer.address.line")
    _require(blocking, buyer_postcode, "BT-53_MISSING", "Pflichtfeld fehlt: PLZ des Käufers (BT-53).", "buyer.address.postcode")
    _require(blocking, buyer_city, "BT-52_MISSING", "Pflichtfeld fehlt: Ort des Käufers (BT-52).", "buyer.address.city")
    _require(blocking, buyer_country, "BT-55_MISSING", "Pflichtfeld fehlt: Land des Käufers (BT-55).", "buyer.address.country")

    if seller_vat and not re.fullmatch(r"[A-Z]{2}[A-Z0-9]{2,12}", seller_vat):
        blocking.append(_issue("BT-31_INVALID", "USt-IdNr. hat kein erkennbares Format.", field="seller.vat_id"))
    if seller_iban and not re.fullmatch(r"[A-Z]{2}\d{2}[A-Z0-9]{11,30}", seller_iban):
        blocking.append(_issue("BT-84_INVALID", "IBAN hat kein erkennbares Format.", field="seller.iban"))
    if seller_email and not _EMAIL_RE.fullmatch(seller_email):
        blocking.append(_issue("BT-43_INVALID", "E-Mail des Verkäufers ist ungültig.", field="seller.email"))
    if seller_country and len(seller_country) != 2:
        blocking.append(_issue("BT-40_INVALID", "Land des Verkäufers muss ein zweistelliger Code sein, z. B. DE.", field="seller.address.country"))
    if buyer_country and len(buyer_country) != 2:
        blocking.append(_issue("BT-55_INVALID", "Land des Käufers muss ein zweistelliger Code sein, z. B. DE.", field="buyer.address.country"))

    lines, line_issues = _ready_lines(draft.lines)
    blocking.extend(line_issues)
    if blocking or issue_date is None:
        return PreparedIssue(invoice=None, blocking=blocking, xrechnung_gaps=[])

    tax_groups: tuple[TaxGroup, ...] = _tax_groups(lines)
    line_total: Decimal = sum((line.line_net for line in lines), Decimal("0.00"))
    tax_total: Decimal = sum((group.amount for group in tax_groups), Decimal("0.00"))
    grand_total: Decimal = (line_total + tax_total).quantize(MONEY_QUANT)

    invoice: ReadyInvoice = ReadyInvoice(
        invoice_number=invoice_number,
        issue_date=issue_date,
        currency=currency,
        buyer_reference=buyer_reference,
        seller_name=seller_name,
        seller_street=seller_street,
        seller_postcode=seller_postcode,
        seller_city=seller_city,
        seller_country=seller_country,
        seller_vat_id=seller_vat,
        seller_email=seller_email,
        seller_contact_name=seller_contact,
        seller_phone=seller_phone,
        seller_iban=seller_iban,
        buyer_name=buyer_name,
        buyer_street=buyer_street,
        buyer_postcode=buyer_postcode,
        buyer_city=buyer_city,
        buyer_country=buyer_country,
        lines=tuple(lines),
        tax_groups=tax_groups,
        line_total=line_total.quantize(MONEY_QUANT),
        tax_total=tax_total.quantize(MONEY_QUANT),
        grand_total=grand_total,
    )
    return PreparedIssue(
        invoice=invoice,
        blocking=[],
        xrechnung_gaps=_xrechnung_gaps(invoice),
    )


def _draft_from_text(
    text: str,
    *,
    seller: Optional[SellerSeed],
    hints: List[FieldHint],
    warnings: List[str],
) -> IssueDraft:
    number_match: Optional[re.Match[str]] = _INVOICE_NUMBER_RE.search(text)
    invoice_number: Optional[str] = number_match.group(1) if number_match else None
    if invoice_number:
        hints.append(FieldHint(field="invoice_number", source="pdf", message="Rechnungsnummer aus dem PDF-Text."))

    issue_date: Optional[str] = _iso_from_german_date(text)
    if issue_date:
        hints.append(FieldHint(field="issue_date", source="pdf", message="Rechnungsdatum aus dem PDF-Text."))

    buyer_match: Optional[re.Match[str]] = _BUYER_REFERENCE_RE.search(text)
    buyer_reference: Optional[str] = buyer_match.group(1) if buyer_match else None
    if buyer_reference:
        hints.append(FieldHint(field="buyer_reference", source="pdf", message="Käuferreferenz aus dem PDF-Text."))

    email_match: Optional[re.Match[str]] = _EMAIL_RE.search(text)
    email: Optional[str] = email_match.group(0) if email_match else None

    pdf_vat: Optional[str] = _labeled_vat(text)
    pdf_iban: Optional[str] = _first_iban(text)
    seller_party: IssueParty = _seller_party(
        seller=seller,
        pdf_vat=pdf_vat,
        pdf_iban=pdf_iban,
        email=email,
        hints=hints,
        warnings=warnings,
    )
    amount_note: Optional[str] = _amount_note(text)
    if amount_note:
        warnings.append(amount_note)
    warnings.append(
        "Positionen werden nicht automatisch übernommen. Bitte Menge, Preis und Steuersatz eintragen."
    )
    return IssueDraft(
        invoice_number=invoice_number,
        issue_date=issue_date,
        currency="EUR",
        buyer_reference=buyer_reference,
        seller=seller_party,
        buyer=IssueParty(address=IssueAddress(country="DE")),
        lines=[IssueLineInput(unit_code="C62", tax_rate=Decimal("19"))],
    )


def _seller_party(
    *,
    seller: Optional[SellerSeed],
    pdf_vat: Optional[str],
    pdf_iban: Optional[str],
    email: Optional[str],
    hints: List[FieldHint],
    warnings: List[str],
) -> IssueParty:
    name: Optional[str] = seller.name if seller and seller.name else None
    if name:
        hints.append(FieldHint(field="seller.name", source="organization", message="Verkäufername aus der Organisation."))

    vat_id: Optional[str] = seller.vat_id if seller and seller.vat_id else pdf_vat
    if seller and seller.vat_id:
        hints.append(FieldHint(field="seller.vat_id", source="organization", message="USt-IdNr. aus der Organisation."))
        if pdf_vat and _compact_upper(pdf_vat) != _compact_upper(seller.vat_id):
            warnings.append("USt-IdNr. im PDF weicht vom Organisationsprofil ab. Das Profil bleibt eingetragen.")
    elif pdf_vat:
        hints.append(FieldHint(field="seller.vat_id", source="pdf", message="USt-IdNr. aus dem PDF-Text."))

    iban: Optional[str] = seller.iban if seller and seller.iban else pdf_iban
    if seller and seller.iban:
        hints.append(FieldHint(field="seller.iban", source="organization", message="IBAN aus der Organisation."))
        if pdf_iban and _compact_upper(pdf_iban) != _compact_upper(seller.iban):
            warnings.append("IBAN im PDF weicht vom Organisationsprofil ab. Das Profil bleibt eingetragen.")
    elif pdf_iban:
        hints.append(FieldHint(field="seller.iban", source="pdf", message="IBAN aus dem PDF-Text."))

    if email:
        hints.append(FieldHint(field="seller.email", source="pdf", message="E-Mail aus dem PDF-Text. Bitte prüfen."))

    return IssueParty(
        name=name,
        address=IssueAddress(country="DE"),
        vat_id=vat_id,
        email=email,
        iban=iban,
    )


def _ready_lines(lines: List[IssueLineInput]) -> tuple[List[ReadyLine], List[ValidationIssue]]:
    issues: List[ValidationIssue] = []
    if not lines:
        issues.append(_issue("BG-25_MISSING", "Mindestens eine Position ist erforderlich (BG-25).", field="lines"))
        return [], issues
    if len(lines) > MAX_LINES:
        issues.append(_issue("BG-25_TOO_MANY", f"Höchstens {MAX_LINES} Positionen.", field="lines"))
        return [], issues

    ready: List[ReadyLine] = []
    for index, line in enumerate(lines, start=1):
        prefix: str = f"lines.{index}"
        description: str = _clean(line.description, max_length=200)
        unit_code: str = _clean(line.unit_code, max_length=3).upper() or "C62"
        if not description:
            issues.append(_issue("BT-153_MISSING", f"Position {index}: Bezeichnung fehlt.", field=f"{prefix}.description"))
        if unit_code not in UNIT_CODES:
            issues.append(
                _issue(
                    "BT-130_UNSUPPORTED",
                    f"Position {index}: Einheit {unit_code} wird nicht unterstützt.",
                    field=f"{prefix}.unit_code",
                )
            )
        quantity: Optional[Decimal] = _positive_decimal(line.quantity, places=4)
        unit_price: Optional[Decimal] = _non_negative_decimal(line.unit_price)
        tax_rate: Optional[Decimal] = _tax_rate(line.tax_rate)
        if quantity is None:
            issues.append(_issue("BT-129_MISSING", f"Position {index}: Menge fehlt oder ist ungültig.", field=f"{prefix}.quantity"))
        if unit_price is None:
            issues.append(_issue("BT-146_MISSING", f"Position {index}: Einzelpreis fehlt oder ist ungültig.", field=f"{prefix}.unit_price"))
        if tax_rate is None:
            issues.append(
                _issue(
                    "BT-152_UNSUPPORTED",
                    f"Position {index}: nur 7 % oder 19 % MwSt. 0 % braucht einen Befreiungsgrund und ist hier nicht enthalten.",
                    field=f"{prefix}.tax_rate",
                )
            )
        if description and quantity is not None and unit_price is not None and tax_rate is not None and unit_code in UNIT_CODES:
            line_net: Decimal = (quantity * unit_price).quantize(MONEY_QUANT)
            ready.append(
                ReadyLine(
                    line_id=str(index),
                    description=description,
                    quantity=quantity,
                    unit_code=unit_code,
                    unit_price=unit_price.quantize(MONEY_QUANT),
                    line_net=line_net,
                    tax_rate=tax_rate,
                )
            )
    return ready, issues


def _tax_groups(lines: List[ReadyLine]) -> tuple[TaxGroup, ...]:
    bases: dict[Decimal, Decimal] = {}
    for line in lines:
        bases[line.tax_rate] = bases.get(line.tax_rate, Decimal("0.00")) + line.line_net
    groups: List[TaxGroup] = []
    for rate in sorted(bases):
        basis: Decimal = bases[rate].quantize(MONEY_QUANT)
        amount: Decimal = (basis * rate / Decimal("100")).quantize(MONEY_QUANT)
        groups.append(TaxGroup(rate=rate, basis=basis, amount=amount))
    return tuple(groups)


def _xrechnung_gaps(invoice: ReadyInvoice) -> List[ValidationIssue]:
    gaps: List[ValidationIssue] = []
    if not invoice.buyer_reference:
        gaps.append(
            _issue(
                "BT-10_MISSING",
                "XRechnung braucht eine Käuferreferenz, z. B. Leitweg-ID (BT-10).",
                field="buyer_reference",
            )
        )
    if not invoice.seller_contact_name:
        gaps.append(
            _issue(
                "BT-41_MISSING",
                "XRechnung braucht einen Ansprechpartner des Verkäufers (BT-41).",
                field="seller.contact_name",
            )
        )
    if not invoice.seller_phone:
        gaps.append(
            _issue(
                "BT-42_MISSING",
                "XRechnung braucht eine Telefonnummer des Verkäufers (BT-42).",
                field="seller.phone",
            )
        )
    if not invoice.seller_email:
        gaps.append(
            _issue(
                "BT-43_MISSING",
                "XRechnung braucht eine E-Mail des Verkäufers (BT-43).",
                field="seller.email",
            )
        )
    return gaps


def _read_pdf_text(content: bytes) -> tuple[str, Optional[str]]:
    try:
        reader: PyPDF2.PdfReader = PyPDF2.PdfReader(BytesIO(content))
        parts: List[str] = []
        for page in reader.pages:
            extracted: Optional[str] = page.extract_text()
            if extracted:
                parts.append(extracted)
        return "\n".join(parts), None
    except Exception:
        return "", "PDF-Text konnte nicht gelesen werden."


def _iso_from_german_date(text: str) -> Optional[str]:
    match: Optional[re.Match[str]] = _DATE_RE.search(text)
    if match is None:
        return None
    try:
        parsed: datetime = datetime.strptime(
            f"{match.group(1)}.{match.group(2)}.{match.group(3)}",
            "%d.%m.%Y",
        )
    except ValueError:
        return None
    return parsed.date().isoformat()


def _labeled_vat(text: str) -> Optional[str]:
    match: Optional[re.Match[str]] = _VAT_RE.search(text)
    if match is None:
        return None
    return re.sub(r"\s+", "", match.group(1)).upper()


def _first_iban(text: str) -> Optional[str]:
    match: Optional[re.Match[str]] = _IBAN_RE.search(text)
    if match is None:
        return None
    compact: str = re.sub(r"[^A-Z0-9]", "", match.group(1).upper())
    if re.fullmatch(r"[A-Z]{2}\d{2}[A-Z0-9]{11,30}", compact):
        return compact
    return None


def _amount_note(text: str) -> Optional[str]:
    found: List[str] = []
    for label, pattern in _LABELED_AMOUNT.items():
        match: Optional[re.Match[str]] = pattern.search(text)
        if match is None:
            continue
        amount: Optional[Decimal] = _parse_de_amount(match.group(1))
        if amount is not None:
            found.append(f"{label} {_format_de(amount)}")
    if not found:
        return None
    joined: str = ", ".join(found)
    return (
        f"Im PDF gelesene Summen (nicht automatisch übernommen): {joined}. "
        "Die XML-Summen werden aus den Positionen berechnet."
    )


def _parse_de_amount(raw: str) -> Optional[Decimal]:
    cleaned: str = raw.strip().replace(".", "").replace(",", ".")
    try:
        return Decimal(cleaned).quantize(MONEY_QUANT)
    except InvalidOperation:
        return None


def _format_de(amount: Decimal) -> str:
    text: str = f"{amount.quantize(MONEY_QUANT):.2f}"
    whole, fraction = text.split(".")
    return f"{whole},{fraction}"


def _parse_iso_date(value: Optional[str]) -> Optional[date]:
    cleaned: str = _clean(value, max_length=10)
    if not cleaned:
        return None
    try:
        return datetime.strptime(cleaned, "%Y-%m-%d").date()
    except ValueError:
        return None


def _positive_decimal(value: Optional[Decimal], *, places: int) -> Optional[Decimal]:
    if value is None:
        return None
    try:
        parsed: Decimal = Decimal(value)
    except InvalidOperation:
        return None
    if parsed <= 0:
        return None
    quant: Decimal = Decimal("1").scaleb(-places)
    return parsed.quantize(quant)


def _non_negative_decimal(value: Optional[Decimal]) -> Optional[Decimal]:
    if value is None:
        return None
    try:
        parsed: Decimal = Decimal(value)
    except InvalidOperation:
        return None
    if parsed < 0:
        return None
    return parsed.quantize(MONEY_QUANT)


def _tax_rate(value: Optional[Decimal]) -> Optional[Decimal]:
    parsed: Optional[Decimal] = _non_negative_decimal(value)
    if parsed is None or parsed not in STANDARD_TAX_RATES:
        return None
    return parsed


def _country(value: Optional[str]) -> str:
    return _clean(value, max_length=16).upper()


def _compact_upper(value: Optional[str]) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", "", value).upper()


def _clean(value: Optional[str], *, max_length: int) -> str:
    if value is None:
        return ""
    collapsed: str = " ".join(value.split())
    return collapsed[:max_length]


def _require(
    issues: List[ValidationIssue],
    value: str,
    code: str,
    message: str,
    field: str,
) -> None:
    if not value:
        issues.append(_issue(code, message, field=field))


def _issue(code: str, message: str, *, field: str) -> ValidationIssue:
    return ValidationIssue(
        level="error",
        category="business",
        code=code,
        message=message,
        field=field,
    )
