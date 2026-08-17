from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from app.data_class.XmlInvoiceHeader import XmlInvoiceHeader
from app.helper_functions.einvoice_helper import parse_decimal, quantize_money
from app.schemas.invoice import (
    InvoiceParseResponse,
    InvoiceTotals,
    LineItem,
    PartyInfo,
    ParseStatus,
    TaxBreakdown,
    ValidationIssue,
    ValidationStatus,
)


def map_to_parse_response(
    *,
    filename: str,
    file_type: str,
    header: XmlInvoiceHeader,
    vendor_data: Dict[str, Any],
) -> InvoiceParseResponse:
    """Map internal parser models to the public API DTO."""
    issues: List[ValidationIssue] = []
    line_items: List[LineItem] = _map_line_items(header)
    seller: PartyInfo = _map_seller(header=header, vendor_data=vendor_data)
    buyer: PartyInfo = _map_buyer(vendor_data=vendor_data)
    totals: InvoiceTotals = _map_totals(header=header)

    if not header.invoice_number:
        issues.append(
            ValidationIssue(
                level="warning",
                category="business",
                code="MISSING_INVOICE_NUMBER",
                message="Rechnungsnummer konnte nicht gelesen werden.",
            )
        )
    if totals.gross is None and totals.net is None:
        issues.append(
            ValidationIssue(
                level="warning",
                category="business",
                code="MISSING_AMOUNTS",
                message="Beträge (Netto/Brutto) konnten nicht gelesen werden.",
            )
        )
    if not line_items:
        issues.append(
            ValidationIssue(
                level="warning",
                category="business",
                code="MISSING_LINE_ITEMS",
                message="Keine Positionen gefunden.",
            )
        )

    has_core: bool = bool(header.invoice_number or seller.name or totals.gross is not None)
    if not has_core:
        status: ParseStatus = ParseStatus.ERROR
        message: str = "Rechnung konnte nicht gelesen werden. Bitte Dateiformat prüfen."
    elif issues:
        status = ParseStatus.PARTIAL
        message = "Rechnung teilweise gelesen. Bitte Warnungen prüfen."
    else:
        status = ParseStatus.SUCCESS
        message = "Rechnung erfolgreich gelesen."

    return InvoiceParseResponse(
        status=status,
        message=message,
        filename=filename,
        file_type=file_type,
        document_type="credit_note" if header.kind_of_invoice == "GU" else "invoice",
        invoice_number=header.invoice_number,
        issue_date=_format_date(header.invoice_date),
        due_date=_format_date(header.due_date),
        seller=seller,
        buyer=buyer,
        totals=totals,
        line_items=line_items,
        payment_reference=_payment_reference(vendor_data),
        validation_status=ValidationStatus.NOT_CHECKED,
        validation_issues=issues,
        mismatch_warnings=[],
        mismatch_fields=[],
        next_steps=[],
    )


def build_next_steps(response: InvoiceParseResponse) -> List[str]:
    """German UX hints for what the user should do next."""
    steps: List[str] = []
    if response.status == ParseStatus.ERROR:
        issue_codes: set[str] = {
            issue.code for issue in response.validation_issues if issue.code
        }
        if "UNSUPPORTED_OPENTRANS" in issue_codes:
            steps.append(
                "Lieferanten um XRechnung (UBL/CII) oder ZUGFeRD-PDF bitten — "
                "openTRANS wird hier noch nicht verarbeitet."
            )
        elif "UNSUPPORTED_XML_FORMAT" in issue_codes:
            steps.append(
                "Bitte prüfen, ob die Datei eine XRechnung ist "
                "(UBL Invoice/CreditNote oder CII CrossIndustryInvoice)."
            )
        elif "NOT_ZUGFERD" in issue_codes:
            steps.append(
                "PDF ohne eingebettetes Rechnungs-XML: separates XRechnung-XML hochladen "
                "oder ein ZUGFeRD-/Factur-X-PDF anfordern."
            )
        else:
            steps.append(
                "Andere Datei wählen (XRechnung-XML oder ZUGFeRD-PDF) und erneut hochladen."
            )
        return steps

    if response.validation_status == ValidationStatus.INVALID:
        steps.append("Lieferanten um korrigierte Rechnung bitten (Validierungsfehler).")
    elif response.validation_status == ValidationStatus.WARNING:
        steps.append("Warnungen prüfen; bei Unsicherheit Steuerberater fragen.")
    elif response.validation_status == ValidationStatus.NOT_CHECKED:
        if any(
            issue.code == "KOSIT_REQUIRED_UNAVAILABLE"
            for issue in response.validation_issues
        ):
            steps.append(
                "Die volle KoSIT-Prüfung ist hier Pflicht, wurde aber nicht ausgeführt. "
                "Rechnung nicht als gültig behandeln."
            )
        else:
            steps.append(
                "Die vollständige KoSIT-Prüfung ist nicht verfügbar. "
                "Rechnung vor Zahlung oder Buchung anderweitig vollständig prüfen."
            )

    if response.mismatch_fields and any(not item.matched for item in response.mismatch_fields):
        steps.append(
            "PDF und XML weichen ab — Lieferanten kontaktieren, bevor Sie zahlen oder buchen."
        )
    elif response.file_type == "zugferd_pdf" and not any(
        not item.matched for item in response.mismatch_fields
    ):
        steps.append("PDF und XML stimmen überein — Betrag und IBAN vor Zahlung nochmals prüfen.")

    if response.totals and response.totals.gross is not None:
        steps.append(
            "Bei Freigabe: Betrag zahlen und „Paket für Steuerberater“ "
            "(Excel + DATEV + PDF) herunterladen."
        )
    else:
        steps.append("Daten unvollständig — Export erst nach Klärung der Beträge.")

    steps.append(
        "Hinweis: Diese Prüfung ersetzt keine steuerliche Beurteilung des Vorsteuerabzugs."
    )
    return steps


def _map_line_items(header: XmlInvoiceHeader) -> List[LineItem]:
    items: List[LineItem] = []
    for position_dict in header.get_positions_map():
        net_amount: Optional[Decimal] = _as_decimal(position_dict.get("total_net_price"))
        tax_rate: Optional[Decimal] = _as_decimal(position_dict.get("tax_rate"))
        gross_amount: Optional[Decimal] = None
        if net_amount is not None and tax_rate is not None:
            gross_amount = quantize_money(
                net_amount * (Decimal("1") + tax_rate / Decimal("100"))
            )

        unit_value: object = position_dict.get("quantity_unit")
        unit: Optional[str] = str(unit_value) if unit_value not in (None, "") else None

        items.append(
            LineItem(
                position=_as_int(position_dict.get("item_pos")),
                description=position_dict.get("position_text"),
                quantity=_as_decimal(position_dict.get("quantity")),
                unit=unit,
                unit_price=_as_decimal(position_dict.get("single_net_price")),
                tax_rate=tax_rate,
                net_amount=net_amount,
                gross_amount=gross_amount,
            )
        )
    return items


def _map_seller(*, header: XmlInvoiceHeader, vendor_data: Dict[str, Any]) -> PartyInfo:
    name: Optional[str] = vendor_data.get("seller_name")
    iban: Optional[str] = header.iban or vendor_data.get("seller_iban")
    vat_id: Optional[str] = vendor_data.get("seller_vat_id")
    address: Optional[str] = _join_address(
        street=vendor_data.get("seller_street"),
        postcode=vendor_data.get("seller_postcode"),
        city=vendor_data.get("seller_city"),
        country=vendor_data.get("seller_country"),
    )
    return PartyInfo(name=name, address=address, vat_id=vat_id, iban=iban)


def _map_buyer(vendor_data: Dict[str, Any]) -> PartyInfo:
    name: Optional[str] = (
        vendor_data.get("buyer_name_billing")
        or vendor_data.get("buyer_name")
        or vendor_data.get("buyer_name_delivery")
    )
    vat_id: Optional[str] = vendor_data.get("buyer_vat_id")
    address: Optional[str] = _join_address(
        street=vendor_data.get("buyer_street_billing") or vendor_data.get("buyer_street_delivery"),
        postcode=vendor_data.get("buyer_postcode_billing") or vendor_data.get("buyer_postcode_delivery"),
        city=vendor_data.get("buyer_city_billing") or vendor_data.get("buyer_city_delivery"),
        country=vendor_data.get("buyer_country_billing") or vendor_data.get("buyer_country_delivery"),
    )
    return PartyInfo(name=name, address=address, vat_id=vat_id, iban=None)


def _map_totals(header: XmlInvoiceHeader) -> InvoiceTotals:
    return InvoiceTotals(
        net=_as_decimal(header.invoice_amount),
        tax=_as_decimal(header.total_tax_amount),
        gross=_as_decimal(header.total_amount),
        currency=header.currency,
        allowance=_as_decimal(header.discount),
        charge=_as_decimal(header.charge_total),
        tax_breakdown=_map_tax_breakdown(header),
    )


def _map_tax_breakdown(header: XmlInvoiceHeader) -> List[TaxBreakdown]:
    breakdown: List[TaxBreakdown] = []
    for index in range(1, 6):
        rate: Optional[Decimal] = _as_decimal(getattr(header, f"tax_rate{index}"))
        amount: Optional[Decimal] = _as_decimal(getattr(header, f"tax_amount{index}"))
        if rate is None:
            continue
        breakdown.append(TaxBreakdown(rate=rate, amount=amount))
    return breakdown


def _join_address(
    *,
    street: Optional[str],
    postcode: Optional[str],
    city: Optional[str],
    country: Optional[str],
) -> Optional[str]:
    city_line_parts: List[str] = [part for part in [postcode, city] if part]
    city_line: Optional[str] = " ".join(city_line_parts) if city_line_parts else None
    parts: List[str] = [part for part in [street, city_line, country] if part]
    if not parts:
        return None
    return ", ".join(parts)


def _payment_reference(vendor_data: Dict[str, Any]) -> Optional[str]:
    payment_means: object = vendor_data.get("payment_means")
    if not isinstance(payment_means, list) or not payment_means:
        return None
    first: object = payment_means[0]
    if not isinstance(first, dict):
        return None
    payment_id: object = first.get("PaymentID")
    if payment_id is None or str(payment_id).strip() == "":
        return None
    return str(payment_id)


def _format_date(value: object) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d")
    return str(value)


def _as_decimal(value: object) -> Optional[Decimal]:
    if value is None or value == "":
        return None
    if isinstance(value, Decimal):
        return value
    return parse_decimal(str(value))


def _as_int(value: object) -> Optional[int]:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
