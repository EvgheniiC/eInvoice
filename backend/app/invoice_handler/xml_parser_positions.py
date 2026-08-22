import re
from decimal import Decimal
from typing import Optional, Tuple
from xml.etree.ElementTree import Element

from ..data_class import XmlInvoiceHeader, XmlInvoicePosition
from ..helper_functions import (
    get_xml_tree,
    find_data_within_element,
    get_tags_from_json,
    decimal_non_negative,
    parse_decimal,
    build_description_from_item,
    is_ubl_placeholder_text,
    document_charge_description,
    get_document_level_charges,
    get_header_trade_allowance_discount,
    HeaderTradeAdjustment,
    _is_gu_document,
)
from ..services.logger_adapter import InvoiceLogger


def get_xml_positions(
    xml_text: str, xml_invoice_data: XmlInvoiceHeader, logger: InvoiceLogger
) -> XmlInvoiceHeader:
    """Parse invoice line items from UBL / CII (ZUGFeRD) XML."""
    logger.info_log(f"START get_xml_positions invoice_id={xml_invoice_data.invoice_id}")

    xml_tree: Element = get_xml_tree(xml_text)
    is_gu_document: bool = _is_gu_document(xml_tree, xml_invoice_data.kind_of_invoice)
    xml_positions_data_zugpferd: Element = xml_tree.find("./SupplyChainTradeTransaction")
    xml_positions_data: list = xml_tree.findall("./InvoiceLine")
    item_position: int = 1
    tags_to_search_additional_description_name: list = get_tags_from_json(
        "tags_to_search_additional_description_name"
    )
    tags_to_search_additional_description_sellers_item_identification: list = get_tags_from_json(
        "tags_to_search_additional_description_sellers_item_identification"
    )
    tags_to_search_tax_rate: list = get_tags_from_json("tags_to_search_tax_rate")
    tags_to_search_quantity: list = get_tags_from_json("tags_to_search_quantity")
    tags_to_search_single_net_price: list = get_tags_from_json("tags_to_search_single_net_price")
    tags_to_search_total_net_price: list = get_tags_from_json("tags_to_search_total_net_price")
    tags_to_search_order_line_reference: list = get_tags_from_json("tags_to_search_order_line_reference")
    tags_to_search_discount: list = get_tags_from_json("tags_to_search_discount")
    tags_to_search_charge_total_amount: list = get_tags_from_json("tags_to_search_charge_total_amount")
    tags_to_search_line_extension_amount: list = get_tags_from_json("tags_to_search_line_extension_amount")
    tags_to_search_tax_exclusive_amount: list = get_tags_from_json("tags_to_search_tax_exclusive_amount")

    xml_invoice_head_money: Element = xml_tree

    if xml_positions_data_zugpferd is None and not xml_positions_data:
        xml_positions_data = xml_tree.findall("./CreditNoteLine")

    if not xml_positions_data:
        xml_positions_data = xml_tree.findall("./Invoice/InvoiceLine")

    reference_tax_rate: Optional[Decimal] = None
    last_line_tax_rate: Optional[Decimal] = None

    for position in (
        xml_positions_data_zugpferd.iter("IncludedSupplyChainTradeLineItem")
        if xml_positions_data_zugpferd is not None
        else xml_positions_data
    ):
        description_raw: str = build_description_from_item(position) or ""
        description_text: str = description_raw.strip()[:1000] if description_raw.strip() else "Default text"

        additional_description_name: str = ""
        name_value: Optional[str] = find_data_within_element(position, tags_to_search_additional_description_name)
        if name_value:
            additional_description_name = name_value[0:1000]

        additional_description_sellers_item_identification: str = ""
        sellers_id: Optional[str] = find_data_within_element(
            position, tags_to_search_additional_description_sellers_item_identification
        )
        if sellers_id:
            additional_description_sellers_item_identification = sellers_id[0:1000]

        if (
            additional_description_name
            and not is_ubl_placeholder_text(additional_description_name)
            and description_text != additional_description_name
        ):
            description_text = description_text + "\n" + additional_description_name

        if (
            additional_description_sellers_item_identification
            and not is_ubl_placeholder_text(additional_description_sellers_item_identification)
            and description_text != additional_description_sellers_item_identification
        ):
            description_text = description_text + "\n" + additional_description_sellers_item_identification

        tax_rate: Decimal = parse_decimal(
            find_data_within_element(position, tags_to_search_tax_rate)
        ) or Decimal("0")
        last_line_tax_rate = tax_rate
        if reference_tax_rate is None:
            reference_tax_rate = tax_rate

        quantity_raw, quantity_unit = _find_quantity(position, tags_to_search_quantity)
        quantity: Decimal = parse_decimal(quantity_raw) or Decimal("1")
        single_raw: Optional[str] = find_data_within_element(position, tags_to_search_single_net_price)
        total_raw: Optional[str] = find_data_within_element(position, tags_to_search_total_net_price)
        if is_gu_document:
            single_net_price = decimal_non_negative(single_raw)
            total_net_price = decimal_non_negative(total_raw)
        else:
            single_net_price = parse_decimal(single_raw)
            total_net_price = parse_decimal(total_raw)
        order_pos_id = find_data_within_element(position, tags_to_search_order_line_reference)

        article_number: str = ""
        try:
            oe_matches = re.findall(r"OE\s*\w{9,}", description_text)
            if oe_matches:
                article_number = oe_matches[0].replace("OE", "").replace(" ", "")
        except Exception:
            logger.error_log("Article number could not be parsed")

        xml_invoice_data.add_position(
            XmlInvoicePosition(
                item_pos=item_position,
                position_text=description_text,
                quantity=quantity,
                quantity_unit=quantity_unit,
                single_net_price=single_net_price,
                tax_rate=tax_rate,
                total_net_price=total_net_price,
                invoice_id=xml_invoice_data.invoice_id,
                article_number=article_number,
                order_pos_id=order_pos_id,
            )
        )
        item_position += 1

    document_charges: list[HeaderTradeAdjustment] = get_document_level_charges(xml_tree)
    if document_charges:
        for charge in document_charges:
            charge_tax_rate: Decimal
            if charge.tax_rate is not None:
                charge_tax_rate = charge.tax_rate
            elif reference_tax_rate is not None:
                charge_tax_rate = reference_tax_rate
            else:
                charge_tax_rate = Decimal("0")
            xml_invoice_data.add_position(
                XmlInvoicePosition(
                    item_pos=item_position,
                    position_text=charge.description[:1000],
                    quantity=Decimal("1"),
                    single_net_price=charge.amount,
                    tax_rate=charge_tax_rate,
                    total_net_price=charge.amount,
                    invoice_id=xml_invoice_data.invoice_id,
                    article_number="",
                    order_pos_id="",
                    tax_code=charge.tax_category,
                )
            )
            item_position += 1
    else:
        charge_total_str: Optional[str] = find_data_within_element(
            xml_invoice_head_money, tags_to_search_charge_total_amount
        )
        charge_total_value: Optional[Decimal] = parse_decimal(charge_total_str)
        if charge_total_value is not None and charge_total_value <= 0:
            charge_total_value = None

        line_ext_str: Optional[str] = find_data_within_element(
            xml_invoice_head_money, tags_to_search_line_extension_amount
        )
        tax_exc_str: Optional[str] = find_data_within_element(
            xml_invoice_head_money, tags_to_search_tax_exclusive_amount
        )
        line_ext_val: Optional[Decimal] = parse_decimal(line_ext_str)
        tax_exc_val: Optional[Decimal] = parse_decimal(tax_exc_str)
        add_document_charge_line: bool = bool(
            charge_total_value
            and line_ext_val is not None
            and tax_exc_val is not None
            and tax_exc_val > line_ext_val
        )

        if add_document_charge_line:
            charge_position_text: str = document_charge_description(xml_tree)
            fallback_tax_rate: Decimal = (
                reference_tax_rate if reference_tax_rate is not None else Decimal("0")
            )
            xml_invoice_data.add_position(
                XmlInvoicePosition(
                    item_pos=item_position,
                    position_text=charge_position_text,
                    quantity=Decimal("1"),
                    single_net_price=charge_total_value,
                    tax_rate=fallback_tax_rate,
                    total_net_price=charge_total_value,
                    invoice_id=xml_invoice_data.invoice_id,
                    article_number="",
                    order_pos_id="",
                )
            )
            item_position += 1

    header_allowance: Optional[HeaderTradeAdjustment] = get_header_trade_allowance_discount(
        xml_tree
    )
    discount_amount_str: Optional[str] = find_data_within_element(xml_invoice_head_money, tags_to_search_discount)
    discount_amount: Optional[Decimal] = None
    discount_position_text: str = "description_text"
    discount_tax_rate: Decimal = Decimal("0")

    if header_allowance is not None:
        discount_amount = header_allowance.amount
        discount_position_text = header_allowance.description[:1000]
        header_vat: Optional[Decimal] = header_allowance.tax_rate
        if header_vat is not None:
            discount_tax_rate = header_vat
        elif reference_tax_rate is not None:
            discount_tax_rate = reference_tax_rate
        elif last_line_tax_rate is not None:
            discount_tax_rate = last_line_tax_rate
    elif discount_amount_str:
        parsed_from_tags: Decimal = parse_decimal(discount_amount_str) or Decimal("0")
        if parsed_from_tags > 0:
            discount_amount = parsed_from_tags
            if reference_tax_rate is not None:
                discount_tax_rate = reference_tax_rate
            elif last_line_tax_rate is not None:
                discount_tax_rate = last_line_tax_rate

    if discount_amount is not None and discount_amount > 0:
        net_price_val: Decimal = -discount_amount
        xml_invoice_data.add_position(
            XmlInvoicePosition(
                item_pos=item_position,
                position_text=discount_position_text,
                quantity=Decimal("1"),
                single_net_price=net_price_val,
                tax_rate=discount_tax_rate,
                total_net_price=net_price_val,
                invoice_id=xml_invoice_data.invoice_id,
            )
        )

    return xml_invoice_data


def _find_quantity(position: Element, tags: list[str]) -> Tuple[Optional[str], Optional[str]]:
    """Return quantity text and its UN/ECE unit code from a UBL or CII line."""
    for tag in tags:
        element: Optional[Element] = position.find(tag)
        if element is None:
            continue
        value: Optional[str] = element.text.strip() if element.text else None
        unit: Optional[str] = element.get("unitCode")
        return value, unit.strip() if unit else None
    return None, None
