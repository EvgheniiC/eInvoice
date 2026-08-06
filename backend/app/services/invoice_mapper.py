from datetime import datetime
from typing import Any, Dict, List, Optional

from app.data_class.XmlInvoiceHeader import XmlInvoiceHeader
from app.helper_functions.einvoice_helper import string_to_float
from app.schemas.invoice import (
    InvoiceParseResponse,
    InvoiceTotals,
    LineItem,
    PartyInfo,
    ParseStatus,
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
        invoice_number=header.invoice_number,
        issue_date=_format_date(header.invoice_date),
        due_date=_format_date(header.delivery_date_till),
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
        steps.append("Andere Datei wählen (XRechnung-XML oder ZUGFeRD-PDF) und erneut hochladen.")
        return steps

    if response.validation_status == ValidationStatus.INVALID:
        steps.append("Lieferanten um korrigierte Rechnung bitten (Validierungsfehler).")
    elif response.validation_status == ValidationStatus.WARNING:
        steps.append("Warnungen prüfen; bei Unsicherheit Steuerberater fragen.")

    if response.mismatch_fields and any(not item.matched for item in response.mismatch_fields):
        steps.append(
            "PDF und XML weichen ab — Lieferanten kontaktieren, bevor Sie zahlen oder buchen."
        )
    elif response.file_type == "zugferd_pdf" and not any(
        not item.matched for item in response.mismatch_fields
    ):
        steps.append("PDF und XML stimmen überein — Betrag und IBAN vor Zahlung nochmals prüfen.")

    if response.totals and response.totals.gross is not None:
        steps.append("Bei Freigabe: Betrag zahlen und für die Buchhaltung exportieren (folgt).")
    else:
        steps.append("Daten unvollständig — Export erst nach Klärung der Beträge.")

    steps.append(
        "Hinweis: Diese Prüfung ersetzt keine steuerliche Beurteilung des Vorsteuerabzugs."
    )
    return steps


def _map_line_items(header: XmlInvoiceHeader) -> List[LineItem]:
    items: List[LineItem] = []
    for position_dict in header.get_positions_map():
        net_amount: Optional[float] = _as_float(position_dict.get("total_net_price"))
        tax_rate: Optional[float] = _as_float(position_dict.get("tax_rate"))
        gross_amount: Optional[float] = None
        if net_amount is not None and tax_rate is not None:
            gross_amount = round(net_amount * (1.0 + tax_rate / 100.0), 2)

        unit_value: object = position_dict.get("quantity_unit")
        unit: Optional[str] = str(unit_value) if unit_value not in (None, "") else None

        items.append(
            LineItem(
                position=_as_int(position_dict.get("item_pos")),
                description=position_dict.get("position_text"),
                quantity=_as_float(position_dict.get("quantity")),
                unit=unit,
                unit_price=_as_float(position_dict.get("single_net_price")),
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
        net=_as_float(header.invoice_amount),
        tax=_as_float(header.total_tax_amount),
        gross=_as_float(header.total_amount),
        currency=header.currency,
    )


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


def _as_float(value: object) -> Optional[float]:
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return float(value)
    parsed: object = string_to_float(str(value))
    if parsed is None or parsed == "":
        return None
    try:
        return float(parsed)
    except (TypeError, ValueError):
        return None


def _as_int(value: object) -> Optional[int]:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
