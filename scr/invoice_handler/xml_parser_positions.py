import re
from typing import Optional, Tuple

from ..data_class import XmlInvoiceHeader, XmlInvoicePosition
from ..helper_functions import get_xml_tree, find_data_within_element, get_tags_from_json, check_cost_center, \
    get_field_value, string_to_float_negative, string_to_float, build_description_from_item, \
    is_ubl_placeholder_text, document_charge_description, \
    get_header_trade_allowance_discount, make_amount_non_negative, _xml_root_local_name
from xml.etree.ElementTree import Element


# extract positions data from XML
def get_xml_positions(xml_text: str, xml_invoice_data: XmlInvoiceHeader, logger) -> XmlInvoiceHeader:
    print("##### START get_zugpferd_positions")
    logger.info_log(f"START get_xml_header with m_cn_id = {xml_invoice_data.m_cn_id}")

    xml_tree: Element = get_xml_tree(xml_text)
    is_credit_note_ubl: bool = _xml_root_local_name(xml_tree) == "CreditNote"
    xml_positions_data_zugpferd: Element = xml_tree.find("./SupplyChainTradeTransaction")
    # some XML invoices have a tag InvoiceLine for positions
    xml_positions_data: list = xml_tree.findall("./InvoiceLine")
    item_position: int = 1
    tags_to_search_additional_description_name: list = get_tags_from_json('tags_to_search_additional_description_name')
    tags_to_search_additional_description_sellers_item_identification: list = get_tags_from_json(
        'tags_to_search_additional_description_sellers_item_identification')
    tags_to_search_tax_rate: list = get_tags_from_json('tags_to_search_tax_rate')
    tags_to_search_quantity: list = get_tags_from_json('tags_to_search_quantity')
    tags_to_search_single_net_price: list = get_tags_from_json('tags_to_search_single_net_price')
    tags_to_search_total_net_price: list = get_tags_from_json('tags_to_search_total_net_price')
    tags_to_search_order_line_reference: list = get_tags_from_json('tags_to_search_order_line_reference')
    tags_to_search_discount: list = get_tags_from_json('tags_to_search_discount')
    tags_to_search_charge_total_amount: list = get_tags_from_json('tags_to_search_charge_total_amount')
    tags_to_search_line_extension_amount: list = get_tags_from_json('tags_to_search_line_extension_amount')
    tags_to_search_tax_exclusive_amount: list = get_tags_from_json('tags_to_search_tax_exclusive_amount')

    xml_invoice_head_money: Element = xml_tree

    if not xml_positions_data_zugpferd and not xml_positions_data:
        xml_positions_data: list = xml_tree.findall("./CreditNoteLine")

    # for BE
    if not xml_positions_data:
        xml_positions_data: list = xml_tree.findall("./Invoice/InvoiceLine")

    # cost_center = xml_invoice_data.cost_center if xml_invoice_data.cost_center else None
    cost_center = check_cost_center(get_field_value(xml_tree, 'cost_center'))
    reference_tax_rate: Optional[float] = None
    last_line_tax_rate: Optional[float] = None

    # positions IncludedSupplyChainTradeLineItem for ZUGPFERD, InvoiceLine for xml
    for position in xml_positions_data_zugpferd.iter(
            "IncludedSupplyChainTradeLineItem") if xml_positions_data_zugpferd else xml_positions_data:
        description_raw: str = build_description_from_item(position) or ""
        description_text: str = (description_raw.strip()[:1000] if description_raw.strip() else "Default text")

        # HW-5851
        additional_description_name: str = find_data_within_element(position,
                                                                    tags_to_search_additional_description_name)[
            0:1000] if find_data_within_element(position,
                                               tags_to_search_additional_description_name) else ""
        additional_description_sellers_item_identification: str = find_data_within_element(position,
                                                                                           tags_to_search_additional_description_sellers_item_identification)[
            0:1000] if find_data_within_element(position,
                                               tags_to_search_additional_description_sellers_item_identification) else ""
        # some clients write the same info in description_text and in additional_description_name -> description_text != additional_description_name
        if (additional_description_name and not is_ubl_placeholder_text(additional_description_name)
                and description_text != additional_description_name):
            description_text = description_text + "\n" + additional_description_name

        # some clients write the same info in description_text and in additional_description_sellers_item_identification -> description_text != additional_description_sellers_item_identification
        if (additional_description_sellers_item_identification
                and not is_ubl_placeholder_text(additional_description_sellers_item_identification)
                and description_text != additional_description_sellers_item_identification):
            description_text = description_text + "\n" + additional_description_sellers_item_identification

        tax_rate: float = string_to_float(find_data_within_element(position, tags_to_search_tax_rate))
        last_line_tax_rate = tax_rate
        if reference_tax_rate is None:
            reference_tax_rate = tax_rate
        quantity: float = string_to_float(
            find_data_within_element(position, tags_to_search_quantity)) if find_data_within_element(
            position,
            tags_to_search_quantity) else 1
        single_raw: Optional[str] = find_data_within_element(position, tags_to_search_single_net_price)
        total_raw: Optional[str] = find_data_within_element(position, tags_to_search_total_net_price)
        if is_credit_note_ubl:
            single_net_price = make_amount_non_negative(single_raw)
            total_net_price = make_amount_non_negative(total_raw)
        else:
            single_net_price = string_to_float_negative(single_raw)
            total_net_price = string_to_float_negative(total_raw)
        order_pos_id = find_data_within_element(position, tags_to_search_order_line_reference)

        article_number: str = ""
        try:
            if re.findall("OE\s*\w{9,}", description_text):
                article_number: str = re.findall("OE\s*\w{9,}", description_text)[0].replace("OE", "").replace(" ", "")
        except Exception as e:
            print(f"Mistake with article number {e}")
            logger.error_log(f"Mistake with article number {e}")

        xml_invoice_data.add_position(
            XmlInvoicePosition(item_pos=item_position, position_text=description_text, quantity=quantity,
                               single_net_price=single_net_price, tax_rate=tax_rate, cost_center=cost_center,
                               total_net_price=total_net_price, invoice_id=xml_invoice_data.m_cn_id,
                               article_number=article_number,order_pos_id=order_pos_id))
        item_position += 1

    # HW-6170
    charge_total_str: Optional[str] = find_data_within_element(xml_invoice_head_money,
                                                                 tags_to_search_charge_total_amount)
    charge_total_value: Optional[float] = string_to_float(charge_total_str) if charge_total_str else None
    if charge_total_value is not None and charge_total_value <= 0:
        charge_total_value = None

    line_ext_str: Optional[str] = find_data_within_element(xml_invoice_head_money,
                                                           tags_to_search_line_extension_amount)
    tax_exc_str: Optional[str] = find_data_within_element(xml_invoice_head_money,
                                                          tags_to_search_tax_exclusive_amount)
    line_ext_val: Optional[float] = string_to_float(line_ext_str) if line_ext_str else None
    tax_exc_val: Optional[float] = string_to_float(tax_exc_str) if tax_exc_str else None
    # Net document charge increases tax base vs sum of lines (not netted by header allowances)
    add_document_charge_line: bool = bool(
        charge_total_value
        and line_ext_val is not None
        and tax_exc_val is not None
        and tax_exc_val > line_ext_val
    )

    if add_document_charge_line:
        charge_position_text: str = document_charge_description(xml_tree)
        charge_tax_rate: float = reference_tax_rate if reference_tax_rate is not None else 0.0
        xml_invoice_data.add_position(
            XmlInvoicePosition(item_pos=item_position, position_text=charge_position_text, quantity=1.0,
                               single_net_price=charge_total_value, tax_rate=charge_tax_rate, cost_center=cost_center,
                               total_net_price=charge_total_value, invoice_id=xml_invoice_data.m_cn_id,
                               article_number="", order_pos_id=""))
        item_position += 1

    header_allowance: Optional[Tuple[float, str, Optional[float]]] = get_header_trade_allowance_discount(xml_tree)
    discount_amount_str: Optional[str] = find_data_within_element(
        xml_invoice_head_money, tags_to_search_discount
    )
    discount_amount: Optional[float] = None
    discount_position_text: str = "description_text"
    discount_tax_rate: float = 0.0

    if header_allowance is not None:
        discount_amount = header_allowance[0]
        discount_position_text = header_allowance[1][:1000]
        header_vat: Optional[float] = header_allowance[2]
        if header_vat is not None:
            discount_tax_rate = header_vat
        elif reference_tax_rate is not None:
            discount_tax_rate = reference_tax_rate
        elif last_line_tax_rate is not None:
            discount_tax_rate = last_line_tax_rate
    elif discount_amount_str:
        parsed_from_tags: float = string_to_float(discount_amount_str)
        if parsed_from_tags > 0:
            discount_amount = parsed_from_tags
            if reference_tax_rate is not None:
                discount_tax_rate = reference_tax_rate
            elif last_line_tax_rate is not None:
                discount_tax_rate = last_line_tax_rate

    if discount_amount is not None and discount_amount > 0:
        net_discount: float = -discount_amount
        net_price_val = string_to_float_negative(str(net_discount))
        xml_invoice_data.add_position(
            XmlInvoicePosition(item_pos=item_position, position_text=discount_position_text, quantity=1,
                               single_net_price=net_price_val, tax_rate=discount_tax_rate, cost_center=cost_center,
                               total_net_price=net_price_val, invoice_id=xml_invoice_data.m_cn_id))

    # if not positions
    if not xml_positions_data_zugpferd and not xml_positions_data:
        xml_invoice_data.add_position(
            XmlInvoicePosition(item_pos=item_position, position_text=discount_position_text, quantity=1,
                               single_net_price=0, tax_rate=0,
                               total_net_price=0, invoice_id=xml_invoice_data.m_cn_id,
                               article_number=None))

        logger.info_log(f"Finish get_xml_header with m_cn_id = {xml_invoice_data.m_cn_id}")

    return xml_invoice_data
