from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional
from xml.etree.ElementTree import Element

from ..data_class import XmlInvoiceHeader
from ..helper_functions import (
    find_data_within_element,
    find_data_within_element_with_len,
    get_xml_tree,
    get_tags_from_json,
    find_tax_data,
    get_field_value,
    find_attribute_within_element,
    normalize_header_amount,
    optional_string_to_decimal,
    parse_decimal,
    quantize_money,
    parse_xml_date,
)
from ..services.logger_adapter import InvoiceLogger


@dataclass(frozen=True)
class HeaderXmlRoots:
    """Resolved XML roots for UBL or CII (ZUGFeRD) header parsing."""

    tree: Element
    exchanged_document: Element
    invoice_head: Element
    invoice_head_money: Element
    supplier_data: Element


@dataclass(frozen=True)
class HeaderTagSet:
    """XPath tag lists used by the header parser."""

    invoice_number: List[str]
    order_id: List[str]
    contract_id: List[str]
    invoice_date: List[str]
    due_date: List[str]
    delivery_date: List[str]
    delivery_date_till: List[str]
    currency: List[str]
    invoice_amount: List[str]
    line_extension_amount: List[str]
    tax_exclusive_amount: List[str]
    total_amount: List[str]
    total_tax_amount: List[str]
    supplier: List[str]
    iban: List[str]
    tax_amount1: List[str]
    tax_rate1: List[str]
    kind_of_invoice: List[str]
    cost_center: List[str]
    client_vat_id: List[str]
    discount: List[str]
    charge_total: List[str]
    client_with_attribute: List[str]

    @classmethod
    def load(cls) -> HeaderTagSet:
        return cls(
            invoice_number=get_tags_from_json("tags_to_search_invoice_number"),
            order_id=get_tags_from_json("tags_to_search_order_id"),
            contract_id=get_tags_from_json("tags_to_search_contract_id"),
            invoice_date=get_tags_from_json("tags_to_search_invoice_date"),
            due_date=get_tags_from_json("tags_to_search_due_date"),
            delivery_date=get_tags_from_json("tags_to_search_delivery_date"),
            delivery_date_till=get_tags_from_json("tags_to_search_delivery_date_till"),
            currency=get_tags_from_json("tags_to_search_currency"),
            invoice_amount=get_tags_from_json("tags_to_search_invoice_amount"),
            line_extension_amount=get_tags_from_json("tags_to_search_line_extension_amount"),
            tax_exclusive_amount=get_tags_from_json("tags_to_search_tax_exclusive_amount"),
            total_amount=get_tags_from_json("tags_to_search_total_amount"),
            total_tax_amount=get_tags_from_json("tags_to_search_total_tax_amount"),
            supplier=get_tags_from_json("tags_to_search_supplier"),
            iban=get_tags_from_json("tags_to_search_iban"),
            tax_amount1=get_tags_from_json("tags_to_search_tax_amount1"),
            tax_rate1=get_tags_from_json("tags_to_search_tax_rate1"),
            kind_of_invoice=get_tags_from_json("tags_to_search_kind_of_invoice"),
            cost_center=get_tags_from_json("tags_to_search_cost_center"),
            client_vat_id=get_tags_from_json("tags_to_search_client_vat_id"),
            discount=get_tags_from_json("tags_to_search_discount"),
            charge_total=get_tags_from_json("tags_to_search_charge_total_amount"),
            client_with_attribute=get_tags_from_json("tags_to_search_client_with_attribute"),
        )


def get_xml_header(
    xml_text: str, xml_invoice_data: XmlInvoiceHeader, logger: InvoiceLogger
) -> XmlInvoiceHeader:
    """Parse invoice header fields from UBL / CII (ZUGFeRD) XML."""
    logger.info_log(f"START get_xml_header invoice_id={xml_invoice_data.invoice_id}")

    if not xml_text:
        return xml_invoice_data

    roots: HeaderXmlRoots = _resolve_xml_roots(get_xml_tree(xml_text))
    tags: HeaderTagSet = HeaderTagSet.load()

    xml_invoice_data.invoice_number = find_data_within_element(
        roots.exchanged_document, tags.invoice_number
    )
    _parse_dates(xml_invoice_data, roots, tags, logger)
    _parse_references(xml_invoice_data, roots, tags)
    _parse_amounts(xml_invoice_data, roots, tags)
    _parse_taxes(xml_invoice_data, roots.tree, tags)
    _parse_parties(xml_invoice_data, roots, tags)
    _parse_iban(xml_invoice_data, roots, tags, logger)
    _parse_document_meta(xml_invoice_data, roots, tags)

    xml_invoice_data.correct_data()

    logger.info_log(f"Finish get_xml_header invoice_id={xml_invoice_data.invoice_id}")
    return xml_invoice_data


def _resolve_xml_roots(xml_tree: Element) -> HeaderXmlRoots:
    """Pick CII roots when present; otherwise fall back to the document root (UBL)."""
    exchanged_document: Optional[Element] = xml_tree.find("./ExchangedDocument")
    invoice_head: Optional[Element] = xml_tree.find(
        "./SupplyChainTradeTransaction/ApplicableHeaderTradeSettlement"
    )
    invoice_head_money: Optional[Element] = xml_tree.find(
        "./SupplyChainTradeTransaction/ApplicableHeaderTradeSettlement/"
        "SpecifiedTradeSettlementHeaderMonetarySummation"
    )
    supplier_data: Optional[Element] = xml_tree.find("./SupplyChainTradeTransaction")

    if invoice_head is None:
        return HeaderXmlRoots(
            tree=xml_tree,
            exchanged_document=xml_tree,
            invoice_head=xml_tree,
            invoice_head_money=xml_tree,
            supplier_data=xml_tree,
        )

    return HeaderXmlRoots(
        tree=xml_tree,
        exchanged_document=exchanged_document if exchanged_document is not None else xml_tree,
        invoice_head=invoice_head,
        invoice_head_money=invoice_head_money if invoice_head_money is not None else xml_tree,
        supplier_data=supplier_data if supplier_data is not None else xml_tree,
    )


def _parse_dates(
    header: XmlInvoiceHeader,
    roots: HeaderXmlRoots,
    tags: HeaderTagSet,
    logger: InvoiceLogger,
) -> None:
    invoice_date: Optional[datetime] = parse_xml_date(
        find_data_within_element(roots.exchanged_document, tags.invoice_date)
    )
    if invoice_date is None:
        logger.error_log("Invoice date was not found")
    header.invoice_date = invoice_date

    header.due_date = parse_xml_date(
        find_data_within_element(roots.invoice_head, tags.due_date)
    )

    delivery_date: Optional[datetime] = parse_xml_date(
        find_data_within_element(roots.invoice_head, tags.delivery_date)
    )
    if delivery_date is None:
        logger.error_log("Delivery date was not found")
    header.delivery_date = delivery_date

    delivery_date_till: Optional[datetime] = parse_xml_date(
        find_data_within_element(roots.invoice_head, tags.delivery_date_till)
    )
    if delivery_date_till is None:
        logger.error_log("delivery_date_till was not found")
    header.delivery_date_till = delivery_date_till


def _parse_references(
    header: XmlInvoiceHeader, roots: HeaderXmlRoots, tags: HeaderTagSet
) -> None:
    currency_value: Optional[str] = find_data_within_element(roots.invoice_head, tags.currency)
    header.currency = currency_value if currency_value else "EUR"

    header.order_id = find_data_within_element(roots.tree, tags.order_id)
    if not header.order_id:
        header.order_id = find_data_within_element(roots.supplier_data, tags.order_id)
    if not header.order_id:
        header.order_id = find_data_within_element(roots.exchanged_document, tags.order_id)

    header.contract_id = find_data_within_element(roots.tree, tags.contract_id)
    if not header.contract_id:
        header.contract_id = find_data_within_element(roots.supplier_data, tags.contract_id)


def _parse_amounts(
    header: XmlInvoiceHeader, roots: HeaderXmlRoots, tags: HeaderTagSet
) -> None:
    # EN 16931: TaxExclusiveAmount reflects document-level allowances/charges; LineExtensionAmount does not.
    line_extension_amount: Optional[str] = find_data_within_element(
        roots.invoice_head_money, tags.line_extension_amount
    )
    tax_exclusive_amount: Optional[str] = find_data_within_element(
        roots.invoice_head_money, tags.tax_exclusive_amount
    )
    use_tax_exclusive_for_net: bool = bool(
        line_extension_amount
        and tax_exclusive_amount
        and parse_decimal(line_extension_amount) != parse_decimal(tax_exclusive_amount)
    )
    raw_invoice_amount: Optional[str]
    if use_tax_exclusive_for_net:
        raw_invoice_amount = tax_exclusive_amount
    else:
        raw_invoice_amount = find_data_within_element(
            roots.invoice_head_money, tags.invoice_amount
        )

    discount_raw: Optional[str] = find_data_within_element(
        roots.invoice_head_money, tags.discount
    )
    header.discount = optional_string_to_decimal(discount_raw)
    header.charge_total = optional_string_to_decimal(
        find_data_within_element(roots.invoice_head_money, tags.charge_total)
    )

    net_amount: Optional[Decimal] = optional_string_to_decimal(raw_invoice_amount)
    if header.discount and not use_tax_exclusive_for_net and net_amount is not None:
        net_amount = quantize_money(net_amount - header.discount)

    header.invoice_amount = normalize_header_amount(net_amount)
    header.total_amount = normalize_header_amount(
        find_data_within_element(roots.invoice_head_money, tags.total_amount)
    )
    header.total_tax_amount = normalize_header_amount(
        find_data_within_element(roots.invoice_head_money, tags.total_tax_amount)
    )


def _parse_taxes(header: XmlInvoiceHeader, xml_tree: Element, tags: HeaderTagSet) -> None:
    tax_amount: Dict[str, Optional[str]] = find_tax_data(
        xml_tree, tags.tax_amount1, "tax_amount"
    )
    header.tax_amount1 = normalize_header_amount(tax_amount["tax_amount1"])
    header.tax_amount2 = normalize_header_amount(tax_amount["tax_amount2"])
    header.tax_amount3 = normalize_header_amount(tax_amount["tax_amount3"])
    header.tax_amount4 = normalize_header_amount(tax_amount["tax_amount4"])
    header.tax_amount5 = normalize_header_amount(tax_amount["tax_amount5"])

    tax_rate: Dict[str, Optional[str]] = find_tax_data(xml_tree, tags.tax_rate1, "tax_rate")
    header.tax_rate1 = optional_string_to_decimal(tax_rate["tax_rate1"])
    header.tax_rate2 = optional_string_to_decimal(tax_rate["tax_rate2"])
    header.tax_rate3 = optional_string_to_decimal(tax_rate["tax_rate3"])
    header.tax_rate4 = optional_string_to_decimal(tax_rate["tax_rate4"])
    header.tax_rate5 = optional_string_to_decimal(tax_rate["tax_rate5"])


def _parse_parties(
    header: XmlInvoiceHeader, roots: HeaderXmlRoots, tags: HeaderTagSet
) -> None:
    header.supplier = find_data_within_element(roots.supplier_data, tags.supplier)
    header.buyer_vat_id = find_data_within_element(roots.tree, tags.client_vat_id)
    if not header.buyer_vat_id:
        header.buyer_vat_id = find_data_within_element(roots.supplier_data, tags.client_vat_id)

    header.client = find_attribute_within_element(
        roots.tree, tags.client_with_attribute, "schemeID"
    )
    if not header.client:
        header.client = get_field_value(roots.tree, "legal_entity")
    if header.client:
        header.client = header.client.lstrip("0")


def _parse_iban(
    header: XmlInvoiceHeader,
    roots: HeaderXmlRoots,
    tags: HeaderTagSet,
    logger: InvoiceLogger,
) -> None:
    iban_22: Optional[str] = find_data_within_element_with_len(
        roots.supplier_data, tags.iban, 22
    )
    header.iban = iban_22.replace(" ", "") if iban_22 else None

    if header.iban:
        logger.info_log(f"IBAN was found = {header.iban}")
        if len(header.iban) < 22:
            header.iban = find_data_within_element(roots.supplier_data, tags.iban)

    if not header.iban:
        iban_16: Optional[str] = find_data_within_element_with_len(
            roots.supplier_data, tags.iban, 16
        )
        header.iban = iban_16.replace(" ", "") if iban_16 else None


def _parse_document_meta(
    header: XmlInvoiceHeader, roots: HeaderXmlRoots, tags: HeaderTagSet
) -> None:
    # UBL CreditNote is identified by its root; CII code 381 is a credit note.
    type_code: Optional[str] = find_data_within_element(
        roots.exchanged_document, tags.kind_of_invoice
    )
    root_name: str = roots.tree.tag.split("}")[-1]
    header.kind_of_invoice = "GU" if root_name == "CreditNote" or type_code == "381" else "RE"

    header.cost_center = find_data_within_element(roots.exchanged_document, tags.cost_center)
    if not header.cost_center:
        header.cost_center = get_field_value(roots.tree, "cost_center")
