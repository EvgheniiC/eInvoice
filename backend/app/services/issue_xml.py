"""Render a checked invoice as EN 16931 CII for XRechnung or Factur-X."""

from __future__ import annotations

import re
from decimal import Decimal
from typing import Final, Literal
from xml.etree import ElementTree as ET

from app.services.issue_draft import MONEY_QUANT, ReadyInvoice, ReadyLine, TaxGroup

CiiProfile = Literal["xrechnung", "facturx"]

NS_RSM: Final[str] = "urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100"
NS_RAM: Final[str] = (
    "urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100"
)
NS_UDT: Final[str] = "urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100"
XRECHNUNG_GUIDELINE: Final[str] = (
    "urn:cen.eu:en16931:2017#compliant#urn:xeinkauf.de:kosit:xrechnung_3.0"
)
FACTURX_GUIDELINE: Final[str] = "urn:cen.eu:en16931:2017#compliant#urn:factur-x.eu:1p0:en16931"
XRECHNUNG_PROCESS: Final[str] = "urn:fdc:peppol.eu:2017:poacc:billing:01:1.0"
VAT_TYPE: Final[str] = "VAT"
STANDARD_CATEGORY: Final[str] = "S"
CREDIT_TRANSFER: Final[str] = "58"


def render_cii(invoice: ReadyInvoice, profile: CiiProfile) -> str:
    """Build CII XML. Totals come from the checked invoice, not from the PDF text."""
    ET.register_namespace("rsm", NS_RSM)
    ET.register_namespace("ram", NS_RAM)
    ET.register_namespace("udt", NS_UDT)

    root: ET.Element = ET.Element(_q(NS_RSM, "CrossIndustryInvoice"))
    _write_context(root, profile)
    _write_document(root, invoice)
    transaction: ET.Element = ET.SubElement(root, _q(NS_RSM, "SupplyChainTradeTransaction"))
    for line in invoice.lines:
        _write_line(transaction, line)
    _write_agreement(transaction, invoice)
    ET.SubElement(transaction, _q(NS_RAM, "ApplicableHeaderTradeDelivery"))
    _write_settlement(transaction, invoice)

    xml_bytes: bytes = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    return xml_bytes.decode("utf-8")


def safe_invoice_filename(invoice_number: str, suffix: str) -> str:
    """File name derived from the invoice number, without path characters."""
    cleaned: str = re.sub(r"[^A-Za-z0-9._-]", "_", invoice_number).strip("._") or "rechnung"
    return f"{cleaned[:40]}{suffix}"


def _write_context(root: ET.Element, profile: CiiProfile) -> None:
    context: ET.Element = ET.SubElement(root, _q(NS_RSM, "ExchangedDocumentContext"))
    if profile == "xrechnung":
        process: ET.Element = ET.SubElement(
            context,
            _q(NS_RAM, "BusinessProcessSpecifiedDocumentContextParameter"),
        )
        ET.SubElement(process, _q(NS_RAM, "ID")).text = XRECHNUNG_PROCESS
    guideline: ET.Element = ET.SubElement(
        context,
        _q(NS_RAM, "GuidelineSpecifiedDocumentContextParameter"),
    )
    guideline_id: str = XRECHNUNG_GUIDELINE if profile == "xrechnung" else FACTURX_GUIDELINE
    ET.SubElement(guideline, _q(NS_RAM, "ID")).text = guideline_id


def _write_document(root: ET.Element, invoice: ReadyInvoice) -> None:
    document: ET.Element = ET.SubElement(root, _q(NS_RSM, "ExchangedDocument"))
    ET.SubElement(document, _q(NS_RAM, "ID")).text = invoice.invoice_number
    ET.SubElement(document, _q(NS_RAM, "TypeCode")).text = "380"
    issue: ET.Element = ET.SubElement(document, _q(NS_RAM, "IssueDateTime"))
    stamp: ET.Element = ET.SubElement(issue, _q(NS_UDT, "DateTimeString"))
    stamp.set("format", "102")
    stamp.text = invoice.issue_date.strftime("%Y%m%d")


def _write_line(parent: ET.Element, line: ReadyLine) -> None:
    item: ET.Element = ET.SubElement(parent, _q(NS_RAM, "IncludedSupplyChainTradeLineItem"))
    document: ET.Element = ET.SubElement(item, _q(NS_RAM, "AssociatedDocumentLineDocument"))
    ET.SubElement(document, _q(NS_RAM, "LineID")).text = line.line_id
    product: ET.Element = ET.SubElement(item, _q(NS_RAM, "SpecifiedTradeProduct"))
    ET.SubElement(product, _q(NS_RAM, "Name")).text = line.description

    agreement: ET.Element = ET.SubElement(item, _q(NS_RAM, "SpecifiedLineTradeAgreement"))
    price: ET.Element = ET.SubElement(agreement, _q(NS_RAM, "NetPriceProductTradePrice"))
    ET.SubElement(price, _q(NS_RAM, "ChargeAmount")).text = _money(line.unit_price)

    delivery: ET.Element = ET.SubElement(item, _q(NS_RAM, "SpecifiedLineTradeDelivery"))
    quantity: ET.Element = ET.SubElement(delivery, _q(NS_RAM, "BilledQuantity"))
    quantity.set("unitCode", line.unit_code)
    quantity.text = f"{line.quantity:.4f}"

    settlement: ET.Element = ET.SubElement(item, _q(NS_RAM, "SpecifiedLineTradeSettlement"))
    tax: ET.Element = ET.SubElement(settlement, _q(NS_RAM, "ApplicableTradeTax"))
    ET.SubElement(tax, _q(NS_RAM, "TypeCode")).text = VAT_TYPE
    ET.SubElement(tax, _q(NS_RAM, "CategoryCode")).text = STANDARD_CATEGORY
    ET.SubElement(tax, _q(NS_RAM, "RateApplicablePercent")).text = _money(line.tax_rate)
    summation: ET.Element = ET.SubElement(
        settlement,
        _q(NS_RAM, "SpecifiedTradeSettlementLineMonetarySummation"),
    )
    ET.SubElement(summation, _q(NS_RAM, "LineTotalAmount")).text = _money(line.line_net)


def _write_agreement(parent: ET.Element, invoice: ReadyInvoice) -> None:
    agreement: ET.Element = ET.SubElement(parent, _q(NS_RAM, "ApplicableHeaderTradeAgreement"))
    if invoice.buyer_reference:
        ET.SubElement(agreement, _q(NS_RAM, "BuyerReference")).text = invoice.buyer_reference
    seller: ET.Element = ET.SubElement(agreement, _q(NS_RAM, "SellerTradeParty"))
    ET.SubElement(seller, _q(NS_RAM, "Name")).text = invoice.seller_name
    _write_contact(seller, invoice)
    _write_address(
        seller,
        line=invoice.seller_street,
        postcode=invoice.seller_postcode,
        city=invoice.seller_city,
        country=invoice.seller_country,
    )
    if invoice.seller_email:
        endpoint: ET.Element = ET.SubElement(seller, _q(NS_RAM, "URIUniversalCommunication"))
        uri: ET.Element = ET.SubElement(endpoint, _q(NS_RAM, "URIID"))
        uri.set("schemeID", "EM")
        uri.text = invoice.seller_email
    registration: ET.Element = ET.SubElement(seller, _q(NS_RAM, "SpecifiedTaxRegistration"))
    vat: ET.Element = ET.SubElement(registration, _q(NS_RAM, "ID"))
    vat.set("schemeID", "VA")
    vat.text = invoice.seller_vat_id

    buyer: ET.Element = ET.SubElement(agreement, _q(NS_RAM, "BuyerTradeParty"))
    ET.SubElement(buyer, _q(NS_RAM, "Name")).text = invoice.buyer_name
    _write_address(
        buyer,
        line=invoice.buyer_street,
        postcode=invoice.buyer_postcode,
        city=invoice.buyer_city,
        country=invoice.buyer_country,
    )


def _write_contact(seller: ET.Element, invoice: ReadyInvoice) -> None:
    if not invoice.seller_contact_name and not invoice.seller_phone and not invoice.seller_email:
        return
    contact: ET.Element = ET.SubElement(seller, _q(NS_RAM, "DefinedTradeContact"))
    if invoice.seller_contact_name:
        ET.SubElement(contact, _q(NS_RAM, "PersonName")).text = invoice.seller_contact_name
    if invoice.seller_phone:
        phone: ET.Element = ET.SubElement(contact, _q(NS_RAM, "TelephoneUniversalCommunication"))
        ET.SubElement(phone, _q(NS_RAM, "CompleteNumber")).text = invoice.seller_phone
    if invoice.seller_email:
        email: ET.Element = ET.SubElement(contact, _q(NS_RAM, "EmailURIUniversalCommunication"))
        ET.SubElement(email, _q(NS_RAM, "URIID")).text = invoice.seller_email


def _write_address(
    party: ET.Element,
    *,
    line: str,
    postcode: str,
    city: str,
    country: str,
) -> None:
    address: ET.Element = ET.SubElement(party, _q(NS_RAM, "PostalTradeAddress"))
    ET.SubElement(address, _q(NS_RAM, "PostcodeCode")).text = postcode
    ET.SubElement(address, _q(NS_RAM, "LineOne")).text = line
    ET.SubElement(address, _q(NS_RAM, "CityName")).text = city
    ET.SubElement(address, _q(NS_RAM, "CountryID")).text = country


def _write_settlement(parent: ET.Element, invoice: ReadyInvoice) -> None:
    settlement: ET.Element = ET.SubElement(parent, _q(NS_RAM, "ApplicableHeaderTradeSettlement"))
    ET.SubElement(settlement, _q(NS_RAM, "InvoiceCurrencyCode")).text = invoice.currency
    means: ET.Element = ET.SubElement(settlement, _q(NS_RAM, "SpecifiedTradeSettlementPaymentMeans"))
    ET.SubElement(means, _q(NS_RAM, "TypeCode")).text = CREDIT_TRANSFER
    account: ET.Element = ET.SubElement(means, _q(NS_RAM, "PayeePartyCreditorFinancialAccount"))
    ET.SubElement(account, _q(NS_RAM, "IBANID")).text = invoice.seller_iban
    for group in invoice.tax_groups:
        _write_tax(settlement, group)
    summation: ET.Element = ET.SubElement(
        settlement,
        _q(NS_RAM, "SpecifiedTradeSettlementHeaderMonetarySummation"),
    )
    ET.SubElement(summation, _q(NS_RAM, "LineTotalAmount")).text = _money(invoice.line_total)
    ET.SubElement(summation, _q(NS_RAM, "TaxBasisTotalAmount")).text = _money(invoice.line_total)
    tax_total: ET.Element = ET.SubElement(summation, _q(NS_RAM, "TaxTotalAmount"))
    tax_total.set("currencyID", invoice.currency)
    tax_total.text = _money(invoice.tax_total)
    ET.SubElement(summation, _q(NS_RAM, "GrandTotalAmount")).text = _money(invoice.grand_total)
    ET.SubElement(summation, _q(NS_RAM, "DuePayableAmount")).text = _money(invoice.grand_total)


def _write_tax(parent: ET.Element, group: TaxGroup) -> None:
    tax: ET.Element = ET.SubElement(parent, _q(NS_RAM, "ApplicableTradeTax"))
    ET.SubElement(tax, _q(NS_RAM, "CalculatedAmount")).text = _money(group.amount)
    ET.SubElement(tax, _q(NS_RAM, "TypeCode")).text = VAT_TYPE
    ET.SubElement(tax, _q(NS_RAM, "BasisAmount")).text = _money(group.basis)
    ET.SubElement(tax, _q(NS_RAM, "CategoryCode")).text = STANDARD_CATEGORY
    ET.SubElement(tax, _q(NS_RAM, "RateApplicablePercent")).text = _money(group.rate)


def _money(value: Decimal) -> str:
    return f"{value.quantize(MONEY_QUANT):.2f}"


def _q(namespace: str, tag: str) -> str:
    return f"{{{namespace}}}{tag}"
