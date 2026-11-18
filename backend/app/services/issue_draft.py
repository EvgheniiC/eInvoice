"""Read a plain PDF into an editable draft and check it before XML generation."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from io import BytesIO
from typing import Any, Callable, Final, List, Optional

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

_LABELED_INVOICE_NUMBER_RE: Final[re.Pattern[str]] = re.compile(
    r"(?:Rechnungs?(?:nummer|-?\s*Nr\.?)|Rechn?\.-Nr\.?|Re\.?-Nr\.?|Belegnummer|Beleg-Nr\.?|"
    r"Invoice\s*(?:No\.?|Number))"
    r"\s*[:.]?\s*([A-Z0-9][A-Z0-9./\-]{1,40})",
    re.IGNORECASE,
)
_BARE_INVOICE_NUMBER_RE: Final[re.Pattern[str]] = re.compile(
    r"(?<![A-Za-zÄÖÜäöüß])Rechnung(?!s)\s*[:.]?\s*([A-Z0-9][A-Z0-9./\-]{1,40})",
    re.IGNORECASE,
)
_COLUMN_INVOICE_HEADER_RE: Final[re.Pattern[str]] = re.compile(
    r"^(?:Rechn?\.-Nr\.?|Rechnungs?-?Nr\.?)$",
    re.IGNORECASE,
)
_GLUED_CUSTOMER_INVOICE_RE: Final[re.Pattern[str]] = re.compile(r"^(\d{6})(\d{10})$")
_DATE_RE: Final[re.Pattern[str]] = re.compile(
    r"(?<![A-Za-zÄÖÜäöüß])(?:Rechnungsdatum|Belegdatum|Datum)\s*[:.]?\s*"
    r"(\d{2})\.(\d{2})\.(\d{2}(?:\d{2})?)",
    re.IGNORECASE,
)
_DATE_HEADER_RE: Final[re.Pattern[str]] = re.compile(
    r"^(?:Rechnungsdatum|Rechn\.-Datum|Belegdatum):?$",
    re.IGNORECASE,
)
_DUE_DATE_RE: Final[re.Pattern[str]] = re.compile(
    r"(?:Fälligkeit(?:sdatum)?|Zahlbar\s+bis(?:\s+zum)?)\s*[:.]?\s*"
    r"(\d{2})\.(\d{2})\.(\d{2}(?:\d{2})?)",
    re.IGNORECASE,
)
_SERVICE_DATE_RE: Final[re.Pattern[str]] = re.compile(
    r"(?:Leistungsdatum|Lieferdatum)\s*[:.]?\s*(\d{2})\.(\d{2})\.(\d{2}(?:\d{2})?)",
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
    r"(?:Leitweg[-\s]?ID|Käuferreferenz|Buyer reference|Bestell(?:nummer|-Nr\.?)|"
    r"Auftrags(?:nummer|-Nr\.?)|Ihre\s+Auftragsnr\.?)"
    r"\s*[:.]?\s*([A-Z0-9][A-Z0-9./\-]{1,40})",
    re.IGNORECASE,
)
_AMOUNT_RE: Final[re.Pattern[str]] = re.compile(
    r"([0-9]{1,3}(?:\.[0-9]{3})*,\d{2}|[0-9]+,\d{2})"
)
_SKIP_LINE_RE: Final[re.Pattern[str]] = re.compile(
    r"(Summe|Gesamt|Nettobetrag|Brutto|Zwischensumme|Endbetrag|Endsumme|"
    r"Übertrag|Uebertrag|Rechnungsbetrag|Rabatt)",
    re.IGNORECASE,
)
_DOC_TAX_RE: Final[re.Pattern[str]] = re.compile(
    r"(?:MwSt(?:-Satz)?|Umsatzsteuer|USt|Steuersatz)[^0-9%]{0,12}(\d{1,2})(?:[.,]\d{1,2})?\s*%"
    r"|(\d{1,2})(?:[.,]\d{1,2})?\s*%[^A-Za-zÄÖÜäöüß%]{0,10}(?:MwSt|USt|Umsatzsteuer)",
    re.IGNORECASE,
)
_MONEY_TOKEN: Final[str] = (
    r"(?:\d{1,3}(?:\.\d{3})+,\d{2}|\d+,\d{2,4}|\d+\.\d{2})(?:\s*(?:€|EUR))?"
)
_RATE_TOKEN: Final[str] = r"\d{1,2}(?:[.,]\d{1,2})?\s*%"
_PARTS_LINE_RE: Final[re.Pattern[str]] = re.compile(
    rf"^(?P<article>\d{{5,}})\s+(?P<desc>.+?)\s+(?P<qty>\d+(?:,\d+)?)\s+"
    rf"(?P<list>{_MONEY_TOKEN})(?P<discount>\d{{1,2}},\d+)%(?P<net>{_MONEY_TOKEN})\*?$"
)
_STUECK_LINE_RE: Final[re.Pattern[str]] = re.compile(
    rf"(?P<desc>[A-Za-zÄÖÜäöüß][A-Za-zÄÖÜäöüß0-9 ./\-]{{1,80}}?)\s+"
    rf"(?P<list>{_MONEY_TOKEN})\s+(?P<qty>\d+,\d{{2}})\s+(?:Stück|Stk\.?)\s+"
    rf"\d+,\d{{2}}%\s+\S+\s+(?P<net>{_MONEY_TOKEN})$",
    re.IGNORECASE,
)
_QTY_DESC_LINE_RE: Final[re.Pattern[str]] = re.compile(
    rf"^(?P<qty>\d+(?:,\d+)?)\s+(?P<desc>[A-Za-zÄÖÜäöüß].{{2,120}}?)\s+"
    rf"(?P<price>{_MONEY_TOKEN})\s+(?:{_RATE_TOKEN}\s+)?"
    rf"(?P<total>{_MONEY_TOKEN})(?:\s+{_RATE_TOKEN})?$"
)
_DESC_QTY_LINE_RE: Final[re.Pattern[str]] = re.compile(
    rf"^(?P<desc>[A-Za-zÄÖÜäöüß][A-Za-zÄÖÜäöüß0-9 ./\-]{{1,80}}?)\s+"
    rf"(?P<qty>\d+(?:,\d+)?)\s+(?P<price>{_MONEY_TOKEN})\s+"
    rf"(?:{_RATE_TOKEN}\s+)?(?P<total>{_MONEY_TOKEN})(?:\s+{_RATE_TOKEN})?$"
)
_INDEXED_TOTAL_RE: Final[re.Pattern[str]] = re.compile(
    rf"^\d+\s+\d{{5,}}\s+(?P<desc>.+?)\s+(?:#\d+\s+)?(?P<net>{_MONEY_TOKEN})$"
)
_AW_LINE_RE: Final[re.Pattern[str]] = re.compile(
    rf"^(?:\d+\s+)?(?:\d{{5,}}\s+)?(?P<desc>[A-Za-zÄÖÜäöüß].+?)\s+\d+,\d{{2}}\s+AW\s+"
    rf"(?P<qty>\d+(?:,\d+)?)\s+(?P<net>{_MONEY_TOKEN})$",
    re.IGNORECASE,
)
_UNIT_PRICE_LINE_RE: Final[re.Pattern[str]] = re.compile(
    rf"^(?P<desc>.+?)\s+(?P<qty>\d+(?:,\d+)?)\s+(?P<unit>Stk\.?|Stück|ST|Jahr|Monate|Monat)\s+"
    rf"(?:\d+\s+)?(?P<price>{_MONEY_TOKEN})\s+(?P<total>{_MONEY_TOKEN})$",
    re.IGNORECASE,
)
_UNIT_AFTER_RE: Final[re.Pattern[str]] = re.compile(
    rf"^(?P<desc>.+?)\s+(?P<unit>Jahr|Monate|Monat|Stück|Stk\.?|ST)\s+"
    rf"(?P<qty>\d+(?:,\d+)?)\s+(?P<price>{_MONEY_TOKEN})\s+(?P<total>{_MONEY_TOKEN})$",
    re.IGNORECASE,
)
_DATED_ITEM_RE: Final[re.Pattern[str]] = re.compile(
    rf"^(?P<desc>.+?)\s+(?P<qty>\d+,\d{{2}})\s+\d+\s+(?P<price>{_MONEY_TOKEN})\s+"
    rf"(?P<total>{_MONEY_TOKEN})\s+\d{{2}}\.\d{{2}}\.\d{{2}}\s+(?P<tax>7|19)\b"
)
_EUR_ITEM_RE: Final[re.Pattern[str]] = re.compile(
    rf"^(?P<desc>.+?)\s+(?P<price>{_MONEY_TOKEN})\s+EUR\s+EUR\s+\S+\s+"
    rf"(?P<total>{_MONEY_TOKEN})\s+(?P<qty>\d+)\s*$",
    re.IGNORECASE,
)
_QTY_DESC_PREFIX_RE: Final[re.Pattern[str]] = re.compile(
    rf"^(?P<qty>\d+(?:,\d+)?)\s+(?P<desc>[A-Za-zÄÖÜäöüß].{{2,160}}?)\s+"
    rf"(?P<price>{_MONEY_TOKEN})\s+(?:{_RATE_TOKEN}\s+)?"
    rf"(?P<total>{_MONEY_TOKEN})(?=\s|$)"
)
_ARTICLE_FACTOR_RE: Final[re.Pattern[str]] = re.compile(
    rf"^(?P<qty>\d+)\s+(?P<desc>.+?)\s+\d{{5,}}\s+(?P<price>{_MONEY_TOKEN})\s+"
    rf"\d+\s+(?P<total>{_MONEY_TOKEN})$"
)
_FACTOR_LINE_RE: Final[re.Pattern[str]] = re.compile(
    rf"^(?P<idx>\d+)\s+(?P<qty>\d+,\d+)\s+x\s+(?P<price>\d+,\d+)\s+(?P<tax>\d+,\d+)\s+"
    rf"(?P<total>{_MONEY_TOKEN})(?:\s+(?P<desc>.+))?$"
)
_SURCHARGE_LINE_RE: Final[re.Pattern[str]] = re.compile(
    rf"(?P<base>{_MONEY_TOKEN})\s+x\s+(?P<pct>\d+)\s*%\s+(?P<desc>.+?)\s+"
    rf"\d+,\d+\s+(?P<total>{_MONEY_TOKEN})$",
    re.IGNORECASE,
)
_EQUAL_AMOUNTS_RE: Final[re.Pattern[str]] = re.compile(
    rf"^(?P<desc>[A-Za-zÄÖÜäöüß].{{2,180}}?)\s+(?P<net>{_MONEY_TOKEN})\s+(?P=net)$"
)
_GLUE_LABEL_RE: Final[re.Pattern[str]] = re.compile(
    r"(?<=[\dA-Za-zÄÖÜäöüß])(Rechnungsdatum|Rechnungsnummer|Kundennummer|Leistungsdatum|"
    r"Lieferdatum|Belegdatum|Fälligkeitsdatum|Fälligkeit)",
    re.IGNORECASE,
)
_DATE_TOKEN_RE: Final[re.Pattern[str]] = re.compile(r"\d{2}\.\d{2}\.\d{2}(?:\d{2})?")
_PLZ_CITY_GLUE_RE: Final[re.Pattern[str]] = re.compile(r"(\d{5})([A-ZÄÖÜ])")
_COUNTRY_GLUE_RE: Final[re.Pattern[str]] = re.compile(r"([A-Za-zÄÖÜäöüß])(Deutschland|Germany)\b")
_STREET_SUFFIX_RE: Final[str] = (
    r"(?:straße|strasse|str\.|weg|allee|platz|gasse|ring|damm|ufer|markt)"
)
_HOUSE_PLZ_RE: Final[re.Pattern[str]] = re.compile(
    rf"(?P<head>(?:[A-Za-zÄÖÜäöüß]|-)*(?:{_STREET_SUFFIX_RE}))"
    rf"\s*(?P<house>\d{{1,4}}[A-Za-z]?)"
    rf"(?P<postcode>\d{{5}})"
    rf"(?=\s+[A-ZÄÖÜ])",
    re.IGNORECASE,
)
_CENT_FOOTNOTE_RE: Final[re.Pattern[str]] = re.compile(r"(?<=,\d{2})\d+(?=\s*\(\d{2}\))")
_FOOTNOTE_RE: Final[re.Pattern[str]] = re.compile(r"\s*\(\d{2}\)")
_WORD_MONEY_GLUE_RE: Final[re.Pattern[str]] = re.compile(
    rf"([A-Za-zÄÖÜäöüß]\.?)(?={_MONEY_TOKEN})"
)
_LABEL_GLUE_RE: Final[re.Pattern[str]] = re.compile(
    r"([a-zäöüß])(?=Lieferempfänger|Rechnungsempfänger|Leistungsempfänger|Rechnungs)",
    re.IGNORECASE,
)
_COUNTRY_POSTCODE_RE: Final[re.Pattern[str]] = re.compile(r"\bD-(\d{5})\b")
_DATE_RATE_RE: Final[re.Pattern[str]] = re.compile(r"\d{2}\.\d{2}\.\d{2}\s+(7|19)\b")
_PLACE_DATE_RE: Final[re.Pattern[str]] = re.compile(
    r"[A-ZÄÖÜ][A-Za-zÄÖÜäöüß.\-]{2,},\s*(\d{2})\.(\d{2})\.(\d{4})"
)
_STANDALONE_INVOICE_TOKEN_RE: Final[re.Pattern[str]] = re.compile(
    r"^[A-Z]{1,4}\d{0,4}-?\d{5,}$",
    re.IGNORECASE,
)
_CITY_STOP_RE: Final[re.Pattern[str]] = re.compile(
    r"Nr\.?|Tel|Fax|Seite|GmbH|@|:|Liefer|Rechnung|Auftrag|Kunde|Betriebs",
    re.IGNORECASE,
)
_CITY_CONNECTORS: Final[frozenset[str]] = frozenset(
    {"a.", "a", "d.", "d", "am", "im", "an", "der", "den", "auf"}
)
_COUNTRY_WORDS: Final[frozenset[str]] = frozenset({"deutschland", "germany"})
_ARTICLE_HEAD_RE: Final[re.Pattern[str]] = re.compile(r"^\d+\s+\d{5,}\s+\S")
_FACTOR_HEAD_RE: Final[re.Pattern[str]] = re.compile(r"^\d+\s+\d+,\d+\s+x\s+")
_QTY_TEXT_HEAD_RE: Final[re.Pattern[str]] = re.compile(r"^\d{1,3}\s+[A-ZÄÖÜ]")
_GENERIC_NAME_RE: Final[re.Pattern[str]] = re.compile(
    r"^(?:Reparaturen|Firma|Lieferanschrift|Seite|Deutschland|Rechnung|Kunden)$",
    re.IGNORECASE,
)
_STREET_NOISE_RE: Final[re.Pattern[str]] = re.compile(
    r"\s+(?:Tel\.?|Telefon|Fax|E-Mail|Email)\b",
    re.IGNORECASE,
)
_RATE_BASIS_RE: Final[re.Pattern[str]] = re.compile(
    rf"(\d{{1,2}})(?:[.,]0{{1,2}})?\s*%\s+(?:(?:€|EUR)\s+)?({_MONEY_TOKEN})",
    re.IGNORECASE,
)
_COMPANY_RE: Final[re.Pattern[str]] = re.compile(r"GmbH|\bAG\b|\bKG\b|\bUG\b", re.IGNORECASE)
_DELIVERY_RE: Final[re.Pattern[str]] = re.compile(
    r"Abholadresse|Lieferadresse|Lieferempfänger",
    re.IGNORECASE,
)
_REJECT_PARTY_RE: Final[re.Pattern[str]] = re.compile(
    r"^(?:Abholadresse|Lieferadresse|Lieferempfänger|inkl\.|Von\s)",
    re.IGNORECASE,
)
_FRAGMENT_NAME_RE: Final[re.Pattern[str]] = re.compile(
    r"^(?:KG\b|Co\.\s*KG|GmbH\b|&)|^(?!.*\s)\S{3,}$",
    re.IGNORECASE,
)
_JOB_SITE_RE: Final[re.Pattern[str]] = re.compile(
    r"Einsatzort|Zielort|Schadennummer|^(?:Auftrag\s+\d)",
    re.IGNORECASE,
)
_QTY_BARE_HEAD_RE: Final[re.Pattern[str]] = re.compile(
    r"^\d+(?:,\d+)?\s+[A-Za-zÄÖÜäöüß]"
)
_TAX_HEAD_RE: Final[re.Pattern[str]] = re.compile(
    r"^(?:MWSt|Umsatzsteuer|USt)\b",
    re.IGNORECASE,
)
_PACK_GLUE_RE: Final[re.Pattern[str]] = re.compile(r"([a-zäöüß])(?=Inhalt\b)")
_NAME_LABEL_RE: Final[re.Pattern[str]] = re.compile(
    r"\s+(?:Auftrags-Nr|Abnehmer-Gruppe|Kunden-Nr|Kd\.-Nr|Betriebs-Nr|Rechnungs-Nr)\b",
    re.IGNORECASE,
)
_SECOND_STREET_RE: Final[re.Pattern[str]] = re.compile(
    rf"(.+?{_STREET_SUFFIX_RE}\.?\s+\d{{1,4}}[A-Za-z]?)",
    re.IGNORECASE,
)
_LEADING_ROLE_RE: Final[re.Pattern[str]] = re.compile(
    r"^(?:>+\s*)?(?:Deutschland\s*)?(?:Rechnungs-\s*und\s*)?"
    r"(?:Leistungsempfänger|Rechnungsempfänger|Lieferempfänger)\s+",
    re.IGNORECASE,
)
_LINE_Y_TOLERANCE: Final[float] = 3.0
_TWO_DIGIT_YEAR_PIVOT: Final[int] = 70
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
_STANDARD_RATE_RE: Final[re.Pattern[str]] = re.compile(
    r"(?<![\d.,])(\d{1,2})(?:[.,]0{1,2})?\s*%"
)
_POSTAL_RE: Final[re.Pattern[str]] = re.compile(
    r"^(?P<postcode>\d{5})\s+(?P<city>[A-ZÄÖÜ][A-Za-zÄÖÜäöüß.\-]*(?:\s+[A-Za-zÄÖÜäöüß.\-]+){0,3})$"
)
_INLINE_ADDRESS_RE: Final[re.Pattern[str]] = re.compile(
    r"^(?P<name>[^·|]{2,80}?)\s*[·|]\s*(?P<street>[^·|]{2,80}?)\s*[·|]\s*"
    r"(?P<postcode>\d{5})\s+(?P<city>[A-ZÄÖÜ][A-Za-zÄÖÜäöüß.\-]*(?:\s+[A-Za-zÄÖÜäöüß.\-]+){0,3})$"
)
_STREET_HINT_RE: Final[re.Pattern[str]] = re.compile(
    r"(?:straße|strasse|str\.|weg|platz|allee|gasse|ring|damm|ufer|markt|hof|\d)",
    re.IGNORECASE,
)
_BUYER_LABEL_RE: Final[re.Pattern[str]] = re.compile(
    r"^(?:Rechnungsempfänger|Auftraggeber|Leistungsempfänger|Rechnung\s+an|"
    r"Lieferadresse|Käufer|Kunde|Empfänger)\s*[:.]?\s*$",
    re.IGNORECASE,
)
_SELLER_LABEL_RE: Final[re.Pattern[str]] = re.compile(
    r"^(?:Rechnungssteller|Verkäufer|Absender|Leistungserbringer)\s*[:.]?\s*$",
    re.IGNORECASE,
)
_NAME_REJECT_RE: Final[re.Pattern[str]] = re.compile(
    r"^(?:Rechnung|Rechnungsnummer|Rechnungsdatum|Datum|Leistungsdatum|MwSt|Umsatzsteuer|"
    r"USt|IBAN|Summe|Gesamt|Netto|Brutto|Position|Menge|Seite|Tel|Telefon|E-Mail|Email|Leitweg)\b",
    re.IGNORECASE,
)
_PHONE_RE: Final[re.Pattern[str]] = re.compile(
    r"(?:Tel\.?|Telefon|Phone)\s*[:.]?\s*(\+?\d[\d() /\-]{5,24}\d)",
    re.IGNORECASE,
)
_CONTACT_RE: Final[re.Pattern[str]] = re.compile(
    r"(?:Ansprechpartner|Sachbearbeiter|Kontakt)\s*[:.]?\s*"
    r"([A-ZÄÖÜ][A-Za-zÄÖÜäöüß.\-]+(?:\s+[A-ZÄÖÜ][A-Za-zÄÖÜäöüß.\-]+){0,3})",
)


@dataclass(frozen=True)
class _TextPiece:
    """One text run with its baseline position on the page."""

    text: str
    x: float
    y: float
    font_size: float


@dataclass(frozen=True)
class SellerSeed:
    """Issuer defaults from the organization. Name, VAT, IBAN and seller contact win over the PDF."""

    name: Optional[str] = None
    vat_id: Optional[str] = None
    iban: Optional[str] = None
    contact_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    buyer_email: Optional[str] = None
    buyer_reference: Optional[str] = None


@dataclass(frozen=True)
class _FoundAddress:
    """One postal block read from the PDF text."""

    name: str
    street: str
    postcode: str
    city: str
    role: Optional[str]
    line_index: int


@dataclass(frozen=True)
class _PdfContacts:
    """Contact details found near the parties, before profile defaults are applied."""

    seller_email: Optional[str]
    buyer_email: Optional[str]
    phone: Optional[str]
    contact_name: Optional[str]


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
    due_date: date
    delivery_date: date
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
    buyer_email: str
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
    buyer_email: str = _clean(draft.buyer.email, max_length=254)
    buyer_reference: str = _clean(draft.buyer_reference, max_length=50)
    due_date: Optional[date] = _parse_iso_date(draft.due_date) if _clean(draft.due_date, max_length=10) else None
    delivery_date: Optional[date] = (
        _parse_iso_date(draft.delivery_date) if _clean(draft.delivery_date, max_length=10) else None
    )

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
    if buyer_email and not _EMAIL_RE.fullmatch(buyer_email):
        blocking.append(_issue("BT-49_INVALID", "E-Mail des Käufers ist ungültig.", field="buyer.email"))
    if _clean(draft.due_date, max_length=10) and due_date is None:
        blocking.append(_issue("BT-9_INVALID", "Fälligkeitsdatum ist ungültig.", field="due_date"))
    if _clean(draft.delivery_date, max_length=10) and delivery_date is None:
        blocking.append(
            _issue("BT-72_INVALID", "Liefer-/Leistungsdatum ist ungültig.", field="delivery_date")
        )
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
        due_date=due_date or issue_date,
        delivery_date=delivery_date or issue_date,
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
        buyer_email=buyer_email,
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
    text = _prepare_text(text)
    invoice_number: Optional[str] = _invoice_number(text)
    if invoice_number:
        hints.append(FieldHint(field="invoice_number", source="pdf", message="Rechnungsnummer aus dem PDF-Text."))

    issue_date: Optional[str] = _iso_from_german_date(text)
    if issue_date:
        hints.append(FieldHint(field="issue_date", source="pdf", message="Rechnungsdatum aus dem PDF-Text."))
    due_date: Optional[str] = _iso_from_due_date(text)
    if due_date:
        hints.append(FieldHint(field="due_date", source="pdf", message="Fälligkeitsdatum aus dem PDF-Text."))
    delivery_date: Optional[str] = _iso_from_service_date(text)
    if delivery_date:
        hints.append(
            FieldHint(field="delivery_date", source="pdf", message="Leistungsdatum aus dem PDF-Text.")
        )

    text_lines: List[str] = text.splitlines()
    seller_name: Optional[str] = seller.name if seller and seller.name else None
    seller_block, buyer_block = _assign_party_addresses(_address_blocks(text_lines), seller_name)
    contacts: _PdfContacts = _pdf_contacts(text_lines, None if buyer_block is None else buyer_block.line_index)

    pdf_reference: Optional[str] = _pdf_buyer_reference(text)
    profile_reference: Optional[str] = seller.buyer_reference if seller else None
    buyer_reference: Optional[str] = _prefer_pdf(
        pdf_reference,
        profile_reference,
        field="buyer_reference",
        pdf_message="Käuferreferenz aus dem PDF-Text.",
        profile_message="Käuferreferenz aus dem Organisationsprofil.",
        hints=hints,
    )

    pdf_vat: Optional[str] = _labeled_vat(text)
    pdf_iban: Optional[str] = _first_iban(text)
    seller_party: IssueParty = _seller_party(
        seller=seller,
        pdf_vat=pdf_vat,
        pdf_iban=pdf_iban,
        pdf_email=contacts.seller_email,
        pdf_phone=contacts.phone,
        pdf_contact=contacts.contact_name,
        address=_address_from_block(seller_block),
        hints=hints,
        warnings=warnings,
    )
    if seller_block is not None and not seller_party.name:
        seller_party.name = seller_block.name
        hints.append(FieldHint(field="seller.name", source="pdf", message="Verkäufername aus dem PDF-Text."))
    if seller_block is not None:
        hints.append(
            FieldHint(field="seller.address.line", source="pdf", message="Adresse des Verkäufers aus dem PDF-Text.")
        )

    buyer_party: IssueParty = _buyer_party(
        block=buyer_block,
        pdf_email=contacts.buyer_email,
        profile_email=seller.buyer_email if seller else None,
        hints=hints,
    )
    amount_note: Optional[str] = _amount_note(text)
    if amount_note:
        warnings.append(amount_note)
    lines: List[IssueLineInput] = _lines_from_text(text)
    if lines:
        warnings.append("Positionen aus dem PDF-Text. Bitte Menge, Preis und Steuersatz prüfen.")
        hints.append(FieldHint(field="lines", source="pdf", message="Positionen aus dem PDF-Text."))
        if any(line.tax_rate is None for line in lines) and len(_document_tax_rates(text)) > 1:
            warnings.append("Im PDF stehen mehrere MwSt-Sätze. Positionen ohne eigenen Satz bitte ergänzen.")
    else:
        warnings.append(
            "Positionen werden nicht automatisch übernommen. Bitte Menge, Preis und Steuersatz eintragen."
        )
        lines = [IssueLineInput(unit_code="C62", tax_rate=Decimal("19"))]
    return IssueDraft(
        invoice_number=invoice_number,
        issue_date=issue_date,
        delivery_date=delivery_date,
        currency="EUR",
        due_date=due_date,
        buyer_reference=buyer_reference,
        seller=seller_party,
        buyer=buyer_party,
        lines=lines,
    )


def _seller_party(
    *,
    seller: Optional[SellerSeed],
    pdf_vat: Optional[str],
    pdf_iban: Optional[str],
    pdf_email: Optional[str],
    pdf_phone: Optional[str],
    pdf_contact: Optional[str],
    address: IssueAddress,
    hints: List[FieldHint],
    warnings: List[str],
) -> IssueParty:
    name: Optional[str] = seller.name if seller and seller.name else None
    if name:
        hints.append(FieldHint(field="seller.name", source="organization", message="Verkäufername aus der Organisation."))

    vat_id: Optional[str] = _prefer_profile(
        seller.vat_id if seller else None,
        pdf_vat,
        field="seller.vat_id",
        profile_message="USt-IdNr. aus der Organisation.",
        pdf_message="USt-IdNr. aus dem PDF-Text.",
        differ_message="USt-IdNr. im PDF weicht vom Organisationsprofil ab. Das Profil bleibt eingetragen.",
        hints=hints,
        warnings=warnings,
        same=_same_compact,
    )
    iban: Optional[str] = _prefer_profile(
        seller.iban if seller else None,
        pdf_iban,
        field="seller.iban",
        profile_message="IBAN aus der Organisation.",
        pdf_message="IBAN aus dem PDF-Text.",
        differ_message="IBAN im PDF weicht vom Organisationsprofil ab. Das Profil bleibt eingetragen.",
        hints=hints,
        warnings=warnings,
        same=_same_compact,
    )
    email: Optional[str] = _prefer_profile(
        seller.email if seller else None,
        pdf_email,
        field="seller.email",
        profile_message="E-Mail des Verkäufers aus der Organisation.",
        pdf_message="E-Mail aus dem PDF-Text. Bitte prüfen.",
        differ_message="E-Mail im PDF weicht vom Organisationsprofil ab. Das Profil bleibt eingetragen.",
        hints=hints,
        warnings=warnings,
        same=_same_text,
    )
    phone: Optional[str] = _prefer_profile(
        seller.phone if seller else None,
        pdf_phone,
        field="seller.phone",
        profile_message="Telefon aus der Organisation.",
        pdf_message="Telefon aus dem PDF-Text.",
        differ_message="Telefon im PDF weicht vom Organisationsprofil ab. Das Profil bleibt eingetragen.",
        hints=hints,
        warnings=warnings,
        same=_same_text,
    )
    contact_name: Optional[str] = _prefer_profile(
        seller.contact_name if seller else None,
        pdf_contact,
        field="seller.contact_name",
        profile_message="Ansprechpartner aus der Organisation.",
        pdf_message="Ansprechpartner aus dem PDF-Text.",
        differ_message="Ansprechpartner im PDF weicht vom Organisationsprofil ab. Das Profil bleibt eingetragen.",
        hints=hints,
        warnings=warnings,
        same=_same_text,
    )
    return IssueParty(
        name=name,
        address=address,
        vat_id=vat_id,
        email=email,
        contact_name=contact_name,
        phone=phone,
        iban=iban,
    )


def _buyer_party(
    *,
    block: Optional[_FoundAddress],
    pdf_email: Optional[str],
    profile_email: Optional[str],
    hints: List[FieldHint],
) -> IssueParty:
    address: IssueAddress = _address_from_block(block)
    name: Optional[str] = None if block is None else block.name
    if name:
        hints.append(FieldHint(field="buyer.name", source="pdf", message="Name des Käufers aus dem PDF-Text."))
    if block is not None:
        hints.append(FieldHint(field="buyer.address.line", source="pdf", message="Adresse des Käufers aus dem PDF-Text."))
    email: Optional[str] = _prefer_pdf(
        pdf_email,
        profile_email,
        field="buyer.email",
        pdf_message="E-Mail des Käufers aus dem PDF-Text.",
        profile_message="E-Mail des Käufers aus dem Organisationsprofil.",
        hints=hints,
    )
    return IssueParty(name=name, address=address, email=email)


def _prefer_profile(
    profile_value: Optional[str],
    pdf_value: Optional[str],
    *,
    field: str,
    profile_message: str,
    pdf_message: str,
    differ_message: str,
    hints: List[FieldHint],
    warnings: List[str],
    same: Callable[[str, str], bool],
) -> Optional[str]:
    """Organization value wins. The PDF fills the field only when the profile is empty."""
    chosen: Optional[str] = _clean(profile_value, max_length=254) or None
    if chosen:
        hints.append(FieldHint(field=field, source="organization", message=profile_message))
        if pdf_value and not same(pdf_value, chosen):
            warnings.append(differ_message)
        return chosen
    if pdf_value:
        hints.append(FieldHint(field=field, source="pdf", message=pdf_message))
        return pdf_value
    return None


def _prefer_pdf(
    pdf_value: Optional[str],
    profile_value: Optional[str],
    *,
    field: str,
    pdf_message: str,
    profile_message: str,
    hints: List[FieldHint],
) -> Optional[str]:
    """A value printed on this invoice wins. The profile is only the fallback."""
    if pdf_value:
        hints.append(FieldHint(field=field, source="pdf", message=pdf_message))
        return pdf_value
    chosen: Optional[str] = _clean(profile_value, max_length=254) or None
    if chosen:
        hints.append(FieldHint(field=field, source="organization", message=profile_message))
        return chosen
    return None


def _address_from_block(block: Optional[_FoundAddress]) -> IssueAddress:
    if block is None:
        return IssueAddress(country="DE")
    return IssueAddress(
        line=_clean(block.street, max_length=200),
        postcode=_clean(block.postcode, max_length=20),
        city=_clean(block.city, max_length=80),
        country="DE",
    )


def _address_blocks(lines: List[str]) -> List[_FoundAddress]:
    """Letterhead and window addresses. A 5-digit postcode line anchors each block."""
    found: List[_FoundAddress] = []
    consumed: set[int] = set()
    for index, raw_line in enumerate(lines):
        line: str = " ".join(raw_line.split())
        if not line or index in consumed or _AMOUNT_RE.search(line):
            continue
        inline_block: Optional[_FoundAddress] = _inline_address(line, _role_before(lines, index), index)
        if inline_block is not None:
            found.append(inline_block)
            consumed.add(index)
            continue
        street_plz: Optional[tuple[str, str, str]] = _street_with_postal(line)
        if street_plz is not None:
            name_at: Optional[tuple[int, str]] = _party_name_before(lines, index, consumed)
            if name_at is not None:
                street_block: Optional[_FoundAddress] = _make_address(
                    name=name_at[1],
                    street=street_plz[0],
                    postcode=street_plz[1],
                    city=street_plz[2],
                    role=_role_before(lines, name_at[0]),
                    line_index=name_at[0],
                    source=line,
                )
                if street_block is not None:
                    found.append(street_block)
                    consumed.update({name_at[0], index})
                    continue
        postal: Optional[tuple[str, str]] = _leading_postal(line)
        if postal is None:
            continue
        street_at: Optional[tuple[int, str]] = _previous_content(lines, index, consumed)
        street_text: str = "" if street_at is None else _first_street(_trim_contact_noise(street_at[1]))
        if street_at is None or not _plausible_street(street_text):
            continue
        named_at: Optional[tuple[int, str]] = _party_name_before(lines, street_at[0], consumed)
        if named_at is None:
            continue
        block: Optional[_FoundAddress] = _make_address(
            name=named_at[1],
            street=street_text,
            postcode=postal[0],
            city=postal[1],
            role=_role_before(lines, named_at[0]),
            line_index=named_at[0],
            source=line,
        )
        if block is None:
            continue
        found.append(block)
        consumed.update({named_at[0], street_at[0], index})
    return found


def _inline_address(line: str, role: Optional[str], line_index: int) -> Optional[_FoundAddress]:
    for separator in (" • ", " · ", " | ", " - ", ", ", "•"):
        parts: List[str] = [part.strip(" -") for part in line.split(separator) if part.strip(" -")]
        if len(parts) < 3:
            continue
        postal: Optional[tuple[str, str]] = _leading_postal(parts[-1])
        if postal is None:
            continue
        name: str = parts[0] if len(parts) == 3 else separator.join(parts[:-2])
        return _make_address(
            name=name,
            street=parts[-2],
            postcode=postal[0],
            city=postal[1],
            role=role,
            line_index=line_index,
            source=line,
        )
    return None


def _trim_contact_noise(value: str) -> str:
    return _STREET_NOISE_RE.split(value, maxsplit=1)[0].strip(" -•·,")


def _plausible_street(street: str) -> bool:
    if not street or "@" in street or street.startswith("+"):
        return False
    if re.search(r"\d{6,}", street):
        return False
    return _STREET_HINT_RE.search(street) is not None


def _leading_postal(line: str) -> Optional[tuple[str, str]]:
    """Postcode and city at the start of a line. Trailing labels stay outside the city."""
    match: Optional[re.Match[str]] = re.match(r"^(\d{5})\s+(\S.*)$", line.strip())
    if match is None:
        return None
    city: Optional[str] = _city_words(match.group(2))
    if city is None:
        return None
    return match.group(1), city


def _city_words(tail: str) -> Optional[str]:
    words: List[str] = []
    for raw_word in tail.split():
        word: str = raw_word.strip(",;")
        if not word or word.casefold() in _COUNTRY_WORDS or _CITY_STOP_RE.search(word):
            break
        if re.search(r"\d", word):
            break
        if words and word.casefold() not in _CITY_CONNECTORS and not re.match(r"[A-ZÄÖÜ]", word):
            break
        if not words and word.casefold() in _CITY_CONNECTORS:
            break
        words.append(word)
        if len(words) == 5:
            break
    if not words or not re.match(r"[A-ZÄÖÜ]", words[0]):
        return None
    return " ".join(words)


def _street_with_postal(line: str) -> Optional[tuple[str, str, str]]:
    match: Optional[re.Match[str]] = re.match(
        r"^(?P<street>.+?[A-Za-zÄÖÜäöüß.])\s+(?P<house>\d{1,4}[A-Za-z]?)\s+(?P<rest>\d{5}\s+\S.*)$",
        line,
    )
    if match is None:
        return None
    postal: Optional[tuple[str, str]] = _leading_postal(match.group("rest"))
    if postal is None:
        return None
    street: str = _first_street(f"{match.group('street')} {match.group('house')}")
    return street, postal[0], postal[1]


def _first_street(street: str) -> str:
    """Keep the first house number when two window columns share one line."""
    match: Optional[re.Match[str]] = _SECOND_STREET_RE.match(street)
    if match is None:
        return street
    remainder: str = street[match.end() :]
    if not remainder.strip() or re.match(r"\s*[–\-]\s*\d", remainder):
        return street
    return match.group(1)


def _clean_party_name(name: str) -> str:
    trimmed: str = _trim_contact_noise(name).lstrip("> ").strip()
    trimmed = _LEADING_ROLE_RE.sub("", trimmed)
    trimmed = _NAME_LABEL_RE.split(trimmed, maxsplit=1)[0]
    return trimmed.strip(" -/|>,")


def _party_name_before(
    lines: List[str],
    index: int,
    consumed: set[int],
) -> Optional[tuple[int, str]]:
    """Prefer the company line when the line above a street is only a wrapped fragment."""
    immediate: Optional[tuple[int, str]] = _previous_content(lines, index, consumed)
    if immediate is None:
        return None
    cleaned: str = _clean_party_name(immediate[1])
    if _COMPANY_RE.search(cleaned) and not _FRAGMENT_NAME_RE.match(cleaned):
        return immediate[0], cleaned
    if not _FRAGMENT_NAME_RE.match(cleaned):
        return immediate[0], cleaned
    cursor: int = immediate[0]
    for _step in range(3):
        earlier: Optional[tuple[int, str]] = _previous_content(lines, cursor, consumed)
        if earlier is None:
            break
        earlier_name: str = _clean_party_name(earlier[1])
        if _COMPANY_RE.search(earlier_name):
            return earlier[0], earlier_name
        cursor = earlier[0]
    return immediate[0], cleaned


def _make_address(
    *,
    name: str,
    street: str,
    postcode: str,
    city: str,
    role: Optional[str],
    line_index: int,
    source: str = "",
) -> Optional[_FoundAddress]:
    cleaned_name: str = _clean(_clean_party_name(name), max_length=200)
    cleaned_street: str = _clean(_first_street(_trim_contact_noise(street)), max_length=200)
    if (
        not cleaned_name
        or not _plausible_street(cleaned_street)
        or _NAME_REJECT_RE.match(cleaned_name)
        or _GENERIC_NAME_RE.match(cleaned_name)
        or _REJECT_PARTY_RE.match(cleaned_name)
        or _JOB_SITE_RE.search(cleaned_name)
        or _JOB_SITE_RE.search(cleaned_street)
    ):
        return None
    chosen_role: Optional[str] = role
    if chosen_role is None and (_DELIVERY_RE.search(cleaned_name) or _DELIVERY_RE.search(source)):
        chosen_role = "delivery"
    return _FoundAddress(
        name=cleaned_name,
        street=cleaned_street,
        postcode=postcode,
        city=_clean(city, max_length=80),
        role=chosen_role,
        line_index=line_index,
    )


def _previous_content(
    lines: List[str],
    index: int,
    consumed: set[int],
) -> Optional[tuple[int, str]]:
    cursor: int = index - 1
    while cursor >= 0:
        if cursor not in consumed:
            text: str = " ".join(lines[cursor].split())
            if text and not _is_role_label(text):
                return cursor, text
        cursor -= 1
    return None


def _is_role_label(text: str) -> bool:
    return _BUYER_LABEL_RE.match(text) is not None or _SELLER_LABEL_RE.match(text) is not None


def _role_before(lines: List[str], name_index: int) -> Optional[str]:
    cursor: int = name_index - 1
    steps: int = 0
    while cursor >= 0 and steps < 4:
        text: str = " ".join(lines[cursor].split())
        if text:
            if _BUYER_LABEL_RE.match(text):
                return "buyer"
            if _SELLER_LABEL_RE.match(text):
                return "seller"
            steps += 1
        cursor -= 1
    return None


def _assign_party_addresses(
    blocks: List[_FoundAddress],
    seller_name: Optional[str],
) -> tuple[Optional[_FoundAddress], Optional[_FoundAddress]]:
    """Seller is the named or first letterhead block. The other block is the buyer."""
    seller: Optional[_FoundAddress] = _first_role(blocks, "seller")
    buyer: Optional[_FoundAddress] = _first_role(blocks, "buyer")
    named: Optional[_FoundAddress] = _block_matching_name(blocks, seller_name)
    if named is not None:
        seller = named
    used: set[int] = set()
    if seller is not None:
        used.add(seller.line_index)
    if buyer is not None and (buyer.line_index in used or buyer.role == "delivery"):
        buyer = None
    if buyer is not None:
        used.add(buyer.line_index)
    remaining: List[_FoundAddress] = [
        block
        for block in blocks
        if block.line_index not in used and block.role != "delivery"
    ]
    if seller is None and not seller_name and remaining:
        seller = remaining.pop(0)
    if seller is not None:
        remaining = [block for block in remaining if not _name_matches(block.name, seller.name)]
    if buyer is None and remaining:
        companies: List[_FoundAddress] = [block for block in remaining if _COMPANY_RE.search(block.name)]
        buyer = companies[0] if companies else remaining[0]
    return seller, buyer


def _first_role(blocks: List[_FoundAddress], role: str) -> Optional[_FoundAddress]:
    for block in blocks:
        if block.role == role:
            return block
    return None


def _block_matching_name(blocks: List[_FoundAddress], seller_name: Optional[str]) -> Optional[_FoundAddress]:
    if not seller_name:
        return None
    for block in blocks:
        if _name_matches(block.name, seller_name):
            return block
    return None


def _name_matches(block_name: str, seller_name: str) -> bool:
    left: str = " ".join(block_name.casefold().split())
    right: str = " ".join(seller_name.casefold().split())
    if len(left) < 4 or len(right) < 4:
        return left == right
    return left in right or right in left


def _pdf_contacts(lines: List[str], buyer_index: Optional[int]) -> _PdfContacts:
    buyer_emails: List[str] = []
    other_emails: List[str] = []
    buyer_end: int = -1 if buyer_index is None else buyer_index + 8
    for index, line in enumerate(lines):
        emails: List[str] = _EMAIL_RE.findall(line)
        target: List[str] = buyer_emails if buyer_index is not None and buyer_index <= index < buyer_end else other_emails
        for email in emails:
            if email not in target and email not in buyer_emails and email not in other_emails:
                target.append(email)
    joined: str = "\n".join(lines)
    buyer_email: Optional[str] = buyer_emails[0] if buyer_emails else None
    seller_email: Optional[str] = other_emails[0] if other_emails else None
    if buyer_email and seller_email and _same_text(buyer_email, seller_email):
        buyer_email = None
    return _PdfContacts(
        seller_email=seller_email,
        buyer_email=buyer_email,
        phone=_labeled_phone(joined),
        contact_name=_labeled_contact(joined),
    )


def _labeled_phone(text: str) -> Optional[str]:
    match: Optional[re.Match[str]] = _PHONE_RE.search(text)
    if match is None:
        return None
    return _clean(match.group(1), max_length=40) or None


def _labeled_contact(text: str) -> Optional[str]:
    match: Optional[re.Match[str]] = _CONTACT_RE.search(text)
    if match is None:
        return None
    return _clean(match.group(1), max_length=200) or None


def _same_text(left: str, right: str) -> bool:
    return " ".join(left.casefold().split()) == " ".join(right.casefold().split())


def _same_compact(left: str, right: str) -> bool:
    return _compact_upper(left) == _compact_upper(right)


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
    if not invoice.buyer_email:
        gaps.append(
            _issue(
                "BT-49_MISSING",
                "XRechnung braucht eine E-Mail des Käufers als elektronische Adresse (BT-49).",
                field="buyer.email",
            )
        )
    return gaps


def _read_pdf_text(content: bytes) -> tuple[str, Optional[str]]:
    try:
        reader: PyPDF2.PdfReader = PyPDF2.PdfReader(BytesIO(content))
        parts: List[str] = []
        for page in reader.pages:
            laid_out: str = _layout_text(page)
            if laid_out:
                parts.append(laid_out)
                continue
            extracted: Optional[str] = page.extract_text()
            if extracted:
                parts.append(extracted)
        return "\n".join(parts), None
    except Exception:
        return "", "PDF-Text konnte nicht gelesen werden."


def _layout_text(page: PyPDF2.PageObject) -> str:
    """Rebuild lines from text positions so table columns stay on one row."""
    pieces: List[_TextPiece] = []

    def _remember(text: Any, cm: Any, tm: Any, font_dict: Any, font_size: Any) -> None:
        del font_dict
        if not isinstance(text, str):
            return
        # A text run often ends with the line break from the content stream.
        token: str = " ".join(text.split())
        if not token:
            return
        if not isinstance(tm, (list, tuple)) or len(tm) < 6:
            return
        transform: tuple[float, ...] = _matrix(cm)
        x: float = transform[0] * float(tm[4]) + transform[2] * float(tm[5]) + transform[4]
        y: float = transform[1] * float(tm[4]) + transform[3] * float(tm[5]) + transform[5]
        size: float = float(font_size) if isinstance(font_size, (int, float)) and font_size else 10.0
        piece: _TextPiece = _TextPiece(text=token, x=x, y=y, font_size=size)
        if pieces and _same_run(pieces[-1], piece):
            return
        pieces.append(piece)

    page.extract_text(visitor_text=_remember)
    if not pieces:
        return ""
    return "\n".join(_join_line(line) for line in _group_lines(pieces))


def _matrix(cm: Any) -> tuple[float, float, float, float, float, float]:
    if isinstance(cm, (list, tuple)) and len(cm) >= 6:
        return (
            float(cm[0]),
            float(cm[1]),
            float(cm[2]),
            float(cm[3]),
            float(cm[4]),
            float(cm[5]),
        )
    return (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)


def _same_run(previous: _TextPiece, piece: _TextPiece) -> bool:
    return (
        previous.text == piece.text
        and abs(previous.x - piece.x) < 0.5
        and abs(previous.y - piece.y) < 0.5
    )


def _group_lines(pieces: List[_TextPiece]) -> List[List[_TextPiece]]:
    ordered: List[_TextPiece] = sorted(pieces, key=lambda piece: (-piece.y, piece.x))
    lines: List[List[_TextPiece]] = []
    for piece in ordered:
        if lines and abs(lines[-1][0].y - piece.y) <= _LINE_Y_TOLERANCE:
            lines[-1].append(piece)
            continue
        lines.append([piece])
    for line in lines:
        line.sort(key=lambda piece: piece.x)
    return lines


def _join_line(pieces: List[_TextPiece]) -> str:
    parts: List[str] = [pieces[0].text]
    previous: _TextPiece = pieces[0]
    for piece in pieces[1:]:
        # A narrow width estimate keeps a real column gap from being swallowed.
        min_end: float = previous.x + len(previous.text) * previous.font_size * 0.35
        if piece.x - min_end > previous.font_size * 0.3:
            parts.append(" ")
        parts.append(piece.text)
        previous = piece
    return "".join(parts).strip()


def _lines_from_text(text: str) -> List[IssueLineInput]:
    document_rates: List[Decimal] = _document_tax_rates(text)
    fallback: Optional[Decimal] = document_rates[0] if len(document_rates) == 1 else None
    found: List[IssueLineInput] = []
    for line in _fold_item_lines(text.splitlines()):
        if not line or _SKIP_LINE_RE.search(line):
            continue
        parsed_lines: List[IssueLineInput] = _items_on_line(line)
        for parsed in parsed_lines:
            parsed.tax_rate = _tax_for_line(line, fallback)
            found.append(parsed)
            if len(found) >= MAX_LINES:
                return found
    return found


def _document_tax_rates(text: str) -> List[Decimal]:
    found: List[Decimal] = []
    for match in _DOC_TAX_RE.finditer(text):
        raw: str = match.group(1) or match.group(2)
        rate: Optional[Decimal] = _standard_rate(raw)
        if rate is not None and rate not in found:
            found.append(rate)
    charged: List[Decimal] = _charged_tax_rates(text)
    if charged:
        return charged
    return found


def _charged_tax_rates(text: str) -> List[Decimal]:
    """Keep a rate only when a following amount shows that something was taxed."""
    found: List[Decimal] = []
    for match in _RATE_BASIS_RE.finditer(text):
        rate: Optional[Decimal] = _standard_rate(match.group(1))
        basis: Optional[Decimal] = _parse_de_decimal(match.group(2))
        if rate is None or basis is None or basis == 0:
            continue
        if rate not in found:
            found.append(rate)
    return found


def _tax_for_line(line: str, fallback: Optional[Decimal]) -> Optional[Decimal]:
    on_line: Optional[Decimal] = _standard_rate_on_line(line)
    if on_line is not None:
        return on_line
    return fallback


def _standard_rate_on_line(line: str) -> Optional[Decimal]:
    found: List[Decimal] = []
    for match in _STANDARD_RATE_RE.finditer(line):
        rate: Optional[Decimal] = _standard_rate(match.group(1))
        if rate is not None and rate not in found:
            found.append(rate)
    dated_rate: Optional[re.Match[str]] = _DATE_RATE_RE.search(line)
    if dated_rate is not None:
        from_date: Optional[Decimal] = _standard_rate(dated_rate.group(1))
        if from_date is not None and from_date not in found:
            found.append(from_date)
    if len(found) == 1:
        return found[0]
    return None


def _standard_rate(raw: str) -> Optional[Decimal]:
    rate: Decimal = Decimal(raw).quantize(Decimal("1.00"))
    if rate in STANDARD_TAX_RATES:
        return rate
    return None


def _prepare_text(text: str) -> str:
    """Split labels, dates and postcodes that a PDF drew without a space."""
    prepared: List[str] = []
    for raw_line in text.splitlines():
        line: str = " ".join(raw_line.split())
        if not line:
            prepared.append("")
            continue
        line = _GLUE_LABEL_RE.sub(r" \1", line)
        line = _LABEL_GLUE_RE.sub(r"\1 ", line)
        line = _DATE_TOKEN_RE.sub(lambda match: f" {match.group(0)} ", line)
        line = _PLZ_CITY_GLUE_RE.sub(r"\1 \2", line)
        line = _COUNTRY_GLUE_RE.sub(r"\1 \2", line)
        line = _COUNTRY_POSTCODE_RE.sub(r"\1", line)
        line = _CENT_FOOTNOTE_RE.sub("", line)
        line = _FOOTNOTE_RE.sub("", line)
        line = _PACK_GLUE_RE.sub(r"\1 ", line)
        line = _WORD_MONEY_GLUE_RE.sub(r"\1 ", line)
        line = _HOUSE_PLZ_RE.sub(r"\g<head> \g<house> \g<postcode>", line)
        prepared.append(" ".join(line.split()))
    return "\n".join(prepared)


def _invoice_number(text: str) -> Optional[str]:
    for match in _LABELED_INVOICE_NUMBER_RE.finditer(text):
        number: Optional[str] = _clean_invoice_number(match.group(1))
        if number:
            return number
    column: Optional[str] = _column_value(text, _COLUMN_INVOICE_HEADER_RE)
    if column:
        number = _clean_invoice_number(column)
        if number:
            return number
    glued: Optional[str] = _glued_customer_invoice(text)
    if glued:
        return glued
    bare_match: re.Match[str]
    for bare_match in _BARE_INVOICE_NUMBER_RE.finditer(text):
        bare_number: Optional[str] = _clean_invoice_number(bare_match.group(1))
        if bare_number:
            return bare_number
    return _invoice_token_near_label(text)


def _clean_invoice_number(raw: str) -> Optional[str]:
    token: str = raw.strip(" .-")
    if len(token) < 2 or not any(char.isdigit() for char in token):
        return None
    if _DATE_TOKEN_RE.fullmatch(token):
        return None
    return token[:50]


def _invoice_token_near_label(text: str) -> Optional[str]:
    """A number printed on its own line next to the word Rechnung."""
    rows: List[str] = [row.strip() for row in text.splitlines() if row.strip()]
    for index, row in enumerate(rows):
        if not re.fullmatch(r"Rechnung", row, re.IGNORECASE):
            continue
        for neighbor_index in (index - 1, index + 1):
            if neighbor_index < 0 or neighbor_index >= len(rows):
                continue
            token: str = rows[neighbor_index].split()[0]
            if _STANDALONE_INVOICE_TOKEN_RE.fullmatch(token):
                return token[:50]
    return None


def _pdf_buyer_reference(text: str) -> Optional[str]:
    for match in _BUYER_REFERENCE_RE.finditer(text):
        token: str = match.group(1).strip(" .-")
        if len(token) < 2 or not any(char.isdigit() for char in token):
            continue
        return token[:50]
    return None


def _glued_customer_invoice(text: str) -> Optional[str]:
    """Some repair prints put customer number and invoice number in one digit string."""
    if not re.search(r"KD-?\s*NR", text, re.IGNORECASE) or not re.search(r"Rechnung", text, re.IGNORECASE):
        return None
    for token in text.split():
        match: Optional[re.Match[str]] = _GLUED_CUSTOMER_INVOICE_RE.match(token)
        if match is not None:
            return match.group(2)
    return None


def _column_value(text: str, header_re: re.Pattern[str]) -> Optional[str]:
    rows: List[str] = [row.strip() for row in text.splitlines() if row.strip()]
    for index, row in enumerate(rows[:-1]):
        headers: List[str] = row.split()
        values: List[str] = rows[index + 1].split()
        if len(headers) != len(values):
            continue
        for column, header in enumerate(headers):
            if "Kunden" in header or header.upper().startswith("KD"):
                continue
            if header_re.search(header):
                return values[column]
    return None


def _fold_item_lines(lines: List[str]) -> List[str]:
    """Join a wrapped position with the next line that holds its amount or text."""
    folded: List[str] = []
    usable: List[str] = [" ".join(line.split()) for line in lines]
    index: int = 0
    while index < len(usable):
        line: str = usable[index]
        if not line:
            index += 1
            continue
        if _EUR_ITEM_RE.search(line) and index + 1 < len(usable):
            followup: Optional[str] = _leading_description(usable[index + 1])
            if followup:
                folded.append(f"{followup} {line}".strip())
                index += 2
                continue
        if (
            _ARTICLE_HEAD_RE.match(line)
            and not _ends_with_money(line)
            and index + 1 < len(usable)
            and _one_item(usable[index + 1]) is None
        ):
            folded.append(f"{line} {usable[index + 1]}".strip())
            index += 2
            continue
        if (
            _QTY_TEXT_HEAD_RE.match(line)
            and not _contains_money(line)
            and index + 1 < len(usable)
            and _contains_money(usable[index + 1])
            and _one_item(usable[index + 1]) is None
            and _TAX_HEAD_RE.match(usable[index + 1]) is None
        ):
            folded.append(f"{line} {usable[index + 1]}".strip())
            index += 2
            continue
        if (
            _QTY_BARE_HEAD_RE.match(line)
            and not _money_after_opening_quantity(line)
            and index + 1 < len(usable)
            and _contains_money(usable[index + 1])
            and _one_item(usable[index + 1]) is None
            and _TAX_HEAD_RE.match(usable[index + 1]) is None
            and _SKIP_LINE_RE.search(usable[index + 1]) is None
        ):
            folded.append(f"{line} {usable[index + 1]}".strip())
            index += 2
            continue
        if _FACTOR_HEAD_RE.match(line):
            extras: List[str] = []
            cursor: int = index + 1
            while cursor < len(usable) and len(extras) < 3:
                nxt: str = usable[cursor]
                if not nxt or _FACTOR_HEAD_RE.match(nxt) or _SKIP_LINE_RE.search(nxt) or _POSTAL_RE.match(nxt):
                    break
                if re.search(r"\d{5}", nxt):
                    break
                extras.append(nxt)
                cursor += 1
            folded.append(" ".join([line, *extras]))
            index = cursor
            continue
        folded.append(line)
        index += 1
    return folded


def _leading_description(line: str) -> Optional[str]:
    """Product name in front of a pack size on the line after a scrambled price row."""
    if not line or _SKIP_LINE_RE.search(line) or re.match(r"Inhalt\b|Gesamt\b", line, re.IGNORECASE):
        return None
    head: str = re.split(r"\s+Inhalt\b|\s+\d+[.,]\d", line, maxsplit=1, flags=re.IGNORECASE)[0].strip()
    if not head or not re.match(r"[A-Za-zÄÖÜäöüß]", head):
        return None
    return head


def _one_item(line: str) -> Optional[IssueLineInput]:
    return (
        _parts_line(line)
        or _stueck_line(line)
        or _aw_line(line)
        or _indexed_total_line(line)
        or _unit_price_line(line)
        or _unit_after_line(line)
        or _dated_item_line(line)
        or _eur_item_line(line)
        or _article_factor_line(line)
        or _factor_line(line)
        or _surcharge_line(line)
        or _qty_desc_line(line)
        or _desc_qty_line(line)
        or _equal_amounts_line(line)
    )


def _items_on_line(line: str) -> List[IssueLineInput]:
    """One position, or a position whose price is followed by a second charge on the same line."""
    prefix: Optional[re.Match[str]] = _QTY_DESC_PREFIX_RE.match(line)
    if prefix is not None and _contains_money(line[prefix.end() :]):
        first_split: Optional[IssueLineInput] = _priced_line(
            prefix.group("desc"),
            prefix.group("qty"),
            prefix.group("price"),
            prefix.group("total"),
        )
        if first_split is not None:
            items: List[IssueLineInput] = [first_split]
            second_split: Optional[IssueLineInput] = _one_item(line[prefix.end() :].strip())
            if second_split is not None:
                items.append(second_split)
            return items
    single: Optional[IssueLineInput] = _one_item(line)
    if single is not None:
        return [single]
    if prefix is None:
        return []
    first: Optional[IssueLineInput] = _priced_line(
        prefix.group("desc"),
        prefix.group("qty"),
        prefix.group("price"),
        prefix.group("total"),
    )
    if first is None:
        return []
    items: List[IssueLineInput] = [first]
    rest: str = line[prefix.end() :].strip()
    if not rest:
        return items
    second: Optional[IssueLineInput] = _one_item(rest)
    if second is not None:
        items.append(second)
    return items


def _ends_with_money(line: str) -> bool:
    return re.search(rf"{_MONEY_TOKEN}$", line) is not None


def _contains_money(line: str) -> bool:
    return re.search(_MONEY_TOKEN, line) is not None


def _money_after_opening_quantity(line: str) -> bool:
    """A leading 1,00 is a quantity. Money later on the line is a price."""
    remainder: str = re.sub(r"^\d+(?:,\d+)?\s+", "", line, count=1)
    return _contains_money(remainder)


def _search_at_boundary(pattern: re.Pattern[str], line: str) -> Optional[re.Match[str]]:
    start: int = 0
    while start < len(line):
        match: Optional[re.Match[str]] = pattern.search(line, start)
        if match is None:
            return None
        if match.start() == 0 or not line[match.start() - 1].isalnum():
            return match
        start = match.start() + 1
    return None


def _parts_line(line: str) -> Optional[IssueLineInput]:
    match: Optional[re.Match[str]] = _PARTS_LINE_RE.match(line)
    if match is None:
        return None
    priced: Optional[tuple[Decimal, Decimal]] = _price_from_net(match.group("net"), match.group("qty"))
    if priced is None:
        return None
    quantity, unit_price = priced
    description: str = _clean(match.group("desc"), max_length=200)
    if not description:
        return None
    return _line(description, quantity, unit_price)


def _stueck_line(line: str) -> Optional[IssueLineInput]:
    match: Optional[re.Match[str]] = _search_at_boundary(_STUECK_LINE_RE, line)
    if match is None:
        return None
    priced: Optional[tuple[Decimal, Decimal]] = _price_from_net(match.group("net"), match.group("qty"))
    if priced is None:
        return None
    quantity, unit_price = priced
    description: str = _clean(re.sub(r"^[A-ZÄÖÜ]\s+", "", match.group("desc")), max_length=200)
    if not description:
        return None
    return _line(description, quantity, unit_price)


def _aw_line(line: str) -> Optional[IssueLineInput]:
    match: Optional[re.Match[str]] = _AW_LINE_RE.match(line)
    if match is None:
        return None
    return _net_line(match.group("desc"), match.group("qty"), match.group("net"))


def _indexed_total_line(line: str) -> Optional[IssueLineInput]:
    match: Optional[re.Match[str]] = _INDEXED_TOTAL_RE.match(line)
    if match is None:
        return None
    return _net_line(match.group("desc"), "1", match.group("net"))


def _unit_price_line(line: str) -> Optional[IssueLineInput]:
    match: Optional[re.Match[str]] = _UNIT_PRICE_LINE_RE.match(line)
    if match is None:
        return None
    return _priced_line(
        match.group("desc"),
        match.group("qty"),
        match.group("price"),
        match.group("total"),
        unit_code=_unit_code_for(match.group("unit")),
    )


def _unit_after_line(line: str) -> Optional[IssueLineInput]:
    match: Optional[re.Match[str]] = _UNIT_AFTER_RE.match(line)
    if match is None:
        return None
    return _priced_line(
        match.group("desc"),
        match.group("qty"),
        match.group("price"),
        match.group("total"),
        unit_code=_unit_code_for(match.group("unit")),
    )


def _dated_item_line(line: str) -> Optional[IssueLineInput]:
    match: Optional[re.Match[str]] = _DATED_ITEM_RE.match(line)
    if match is None:
        return None
    return _priced_line(match.group("desc"), match.group("qty"), match.group("price"), match.group("total"))


def _eur_item_line(line: str) -> Optional[IssueLineInput]:
    match: Optional[re.Match[str]] = _EUR_ITEM_RE.match(line)
    if match is None:
        return None
    description: str = re.sub(
        r"\s+Pro\s+\d+\s+St\S*(?:\s+\d+)?\s*$",
        "",
        match.group("desc"),
        flags=re.IGNORECASE,
    )
    return _priced_line(description, match.group("qty"), match.group("price"), match.group("total"))


def _unit_code_for(word: str) -> str:
    if word.casefold().rstrip(".") in {"jahr", "monat", "monate"}:
        return "MON"
    return "C62"


def _article_factor_line(line: str) -> Optional[IssueLineInput]:
    match: Optional[re.Match[str]] = _ARTICLE_FACTOR_RE.match(line)
    if match is None:
        return None
    return _priced_line(match.group("desc"), match.group("qty"), match.group("price"), match.group("total"))


def _factor_line(line: str) -> Optional[IssueLineInput]:
    match: Optional[re.Match[str]] = _FACTOR_LINE_RE.match(line)
    if match is None:
        return None
    description: str = match.group("desc") or "Leistung"
    return _priced_line(description, match.group("qty"), match.group("price"), match.group("total"))


def _surcharge_line(line: str) -> Optional[IssueLineInput]:
    match: Optional[re.Match[str]] = _SURCHARGE_LINE_RE.search(line)
    if match is None:
        return None
    description: str = f"{match.group('pct')} % {match.group('desc')}"
    return _net_line(description, "1", match.group("total"))


def _equal_amounts_line(line: str) -> Optional[IssueLineInput]:
    match: Optional[re.Match[str]] = _EQUAL_AMOUNTS_RE.match(line)
    if match is None:
        return None
    return _net_line(match.group("desc"), "1", match.group("net"))


def _net_line(description_raw: str, qty_raw: str, net_raw: str) -> Optional[IssueLineInput]:
    priced: Optional[tuple[Decimal, Decimal]] = _price_from_net(net_raw, qty_raw)
    if priced is None:
        return None
    quantity, unit_price = priced
    description: str = _clean(_tidy_description(description_raw), max_length=200)
    if not description:
        return None
    return _line(description, quantity, unit_price)


def _strip_position_prefix(description: str) -> str:
    return re.sub(r"^(?:\d+\s+){1,3}", "", description.strip())


def _tidy_description(description: str) -> str:
    text: str = _strip_position_prefix(description)
    text = re.sub(r"\s+\d+\s*KM\s+\S+\s*$", "", text, flags=re.IGNORECASE)
    return re.split(r"\s+im Sinne\b", text, maxsplit=1, flags=re.IGNORECASE)[0]


def _desc_qty_line(line: str) -> Optional[IssueLineInput]:
    match: Optional[re.Match[str]] = _DESC_QTY_LINE_RE.match(line)
    if match is None:
        return None
    return _priced_line(
        match.group("desc"),
        match.group("qty"),
        match.group("price"),
        match.group("total"),
    )


def _qty_desc_line(line: str) -> Optional[IssueLineInput]:
    match: Optional[re.Match[str]] = _QTY_DESC_LINE_RE.match(line)
    if match is None:
        return None
    return _priced_line(
        match.group("desc"),
        match.group("qty"),
        match.group("price"),
        match.group("total"),
    )


def _priced_line(
    description_raw: str,
    qty_raw: str,
    price_raw: str,
    total_raw: str,
    unit_code: str = "C62",
) -> Optional[IssueLineInput]:
    quantity: Optional[Decimal] = _parse_de_quantity(qty_raw)
    unit_price: Optional[Decimal] = _parse_de_decimal(price_raw)
    total: Optional[Decimal] = _parse_de_decimal(total_raw)
    if quantity is None or unit_price is None or total is None:
        return None
    if not _amounts_match(unit_price, quantity, total):
        return None
    description: str = _clean(_tidy_description(description_raw), max_length=200)
    if not description:
        return None
    return _line(description, quantity, unit_price, unit_code)


def _line(
    description: str,
    quantity: Decimal,
    unit_price: Decimal,
    unit_code: str = "C62",
) -> IssueLineInput:
    return IssueLineInput(
        description=description,
        quantity=quantity,
        unit_code=unit_code,
        unit_price=unit_price,
        tax_rate=None,
    )


def _price_from_net(net_raw: str, qty_raw: str) -> Optional[tuple[Decimal, Decimal]]:
    net: Optional[Decimal] = _parse_de_decimal(net_raw)
    quantity: Optional[Decimal] = _parse_de_quantity(qty_raw)
    if net is None or quantity is None:
        return None
    net_cents: Decimal = net.quantize(MONEY_QUANT)
    for places in (4, 2):
        unit_price: Decimal = (net / quantity).quantize(Decimal("1").scaleb(-places))
        if (unit_price * quantity).quantize(MONEY_QUANT) == net_cents:
            return quantity, unit_price
    return None


def _amounts_match(unit_price: Decimal, quantity: Decimal, total: Decimal) -> bool:
    return (unit_price * quantity).quantize(MONEY_QUANT) == total.quantize(MONEY_QUANT)


def _parse_de_quantity(raw: str) -> Optional[Decimal]:
    cleaned: str = raw.strip().replace(".", "").replace(",", ".")
    try:
        parsed: Decimal = Decimal(cleaned)
    except InvalidOperation:
        return None
    if parsed <= 0:
        return None
    return parsed


def _iso_from_german_date(text: str) -> Optional[str]:
    match: Optional[re.Match[str]] = _DATE_RE.search(text)
    if match is not None:
        return _iso_from_date_parts(match.group(1), match.group(2), match.group(3))
    column: Optional[str] = _column_value(text, _DATE_HEADER_RE)
    if column is not None:
        parts: Optional[re.Match[str]] = _DATE_TOKEN_RE.fullmatch(column)
        if parts is not None:
            day_text: str
            month_text: str
            year_text: str
            day_text, month_text, year_text = column.split(".")
            return _iso_from_date_parts(day_text, month_text, year_text)
    beside_number: Optional[str] = _date_after_invoice_number(text)
    if beside_number is not None:
        return beside_number
    placed: Optional[re.Match[str]] = _PLACE_DATE_RE.search(text[:1200])
    if placed is None:
        return None
    return _iso_from_date_parts(placed.group(1), placed.group(2), placed.group(3))


def _date_after_invoice_number(text: str) -> Optional[str]:
    number: Optional[str] = _invoice_number(text)
    if not number:
        return None
    found: Optional[re.Match[str]] = re.search(
        rf"{re.escape(number)}\s+(\d{{2}})\.(\d{{2}})\.(\d{{2}}(?:\d{{2}})?)",
        text,
    )
    if found is None:
        return None
    return _iso_from_date_parts(found.group(1), found.group(2), found.group(3))


def _iso_from_due_date(text: str) -> Optional[str]:
    match: Optional[re.Match[str]] = _DUE_DATE_RE.search(text)
    if match is None:
        return None
    return _iso_from_date_parts(match.group(1), match.group(2), match.group(3))


def _iso_from_service_date(text: str) -> Optional[str]:
    match: Optional[re.Match[str]] = _SERVICE_DATE_RE.search(text)
    if match is None:
        return None
    return _iso_from_date_parts(match.group(1), match.group(2), match.group(3))


def _iso_from_date_parts(day: str, month: str, year: str) -> Optional[str]:
    year_number: int = int(year)
    if len(year) == 2:
        year_number = 2000 + year_number if year_number < _TWO_DIGIT_YEAR_PIVOT else 1900 + year_number
    try:
        return date(year_number, int(month), int(day)).isoformat()
    except ValueError:
        return None


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


def _parse_de_decimal(raw: str) -> Optional[Decimal]:
    cleaned: str = raw.strip().replace("€", "").replace("EUR", "").replace("*", "").strip()
    if not cleaned:
        return None
    if "," in cleaned and "." in cleaned:
        cleaned = cleaned.replace(".", "").replace(",", ".")
    elif "," in cleaned:
        cleaned = cleaned.replace(",", ".")
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None


def _parse_de_amount(raw: str) -> Optional[Decimal]:
    parsed: Optional[Decimal] = _parse_de_decimal(raw)
    if parsed is None:
        return None
    return parsed.quantize(MONEY_QUANT)


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
