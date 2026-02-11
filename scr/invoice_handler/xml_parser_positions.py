import re
from ..data_class import XmlInvoiceHeader, XmlInvoicePosition
from ..helper_functions import get_xml_tree, find_data_within_element, get_tags_from_json, check_cost_center, \
    get_field_value, string_to_float_negative, string_to_float
from xml.etree.ElementTree import Element


# extract positions data from XML
def get_xml_positions(xml_text: str, xml_invoice_data: XmlInvoiceHeader, logger) -> XmlInvoiceHeader:
    print("##### START get_zugpferd_positions")
    logger.info_log(f"START get_xml_header with m_cn_id = {xml_invoice_data.m_cn_id}")

    xml_tree: Element = get_xml_tree(xml_text)
    xml_positions_data_zugpferd: Element = xml_tree.find("./SupplyChainTradeTransaction")
    # some XML invoices have a tag InvoiceLine for positions
    xml_positions_data: list = xml_tree.findall("./InvoiceLine")
    item_position: int = 1
    tags_to_search_description: list = get_tags_from_json('tags_to_search_description')
    tags_to_search_additional_description_name: list = get_tags_from_json('tags_to_search_additional_description_name')
    tags_to_search_additional_description_sellers_item_identification: list = get_tags_from_json(
        'tags_to_search_additional_description_sellers_item_identification')
    tags_to_search_tax_rate: list = get_tags_from_json('tags_to_search_tax_rate')
    tags_to_search_quantity: list = get_tags_from_json('tags_to_search_quantity')
    tags_to_search_single_net_price: list = get_tags_from_json('tags_to_search_single_net_price')
    tags_to_search_total_net_price: list = get_tags_from_json('tags_to_search_total_net_price')
    tags_to_search_order_line_reference: list = get_tags_from_json('tags_to_search_order_line_reference')

    if not xml_positions_data_zugpferd and not xml_positions_data:
        xml_positions_data: list = xml_tree.findall("./CreditNoteLine")

    # for BE
    if not xml_positions_data:
        xml_positions_data: list = xml_tree.findall("./Invoice/InvoiceLine")

    # cost_center = xml_invoice_data.cost_center if xml_invoice_data.cost_center else None
    cost_center = check_cost_center(get_field_value(xml_tree, 'cost_center'))

    # positions IncludedSupplyChainTradeLineItem for ZUGPFERD, InvoiceLine for xml
    for position in xml_positions_data_zugpferd.iter(
            "IncludedSupplyChainTradeLineItem") if xml_positions_data_zugpferd else xml_positions_data:
        description_text: str = find_data_within_element(position, tags_to_search_description)[
            0:499] if find_data_within_element(position,
                                               tags_to_search_description) else "Default text"

        # HW-5851
        additional_description_name: str = find_data_within_element(position,
                                                                    tags_to_search_additional_description_name)[
            0:499] if find_data_within_element(position,
                                               tags_to_search_additional_description_name) else ""
        additional_description_sellers_item_identification: str = find_data_within_element(position,
                                                                                           tags_to_search_additional_description_sellers_item_identification)[
            0:499] if find_data_within_element(position,
                                               tags_to_search_additional_description_sellers_item_identification) else ""
        # some clients write the same info in description_text and in additional_description_name -> description_text != additional_description_name
        if additional_description_name and description_text != additional_description_name:
            description_text = description_text + "\n" + additional_description_name

        # some clients write the same info in description_text and in additional_description_sellers_item_identification -> description_text != additional_description_sellers_item_identification
        if additional_description_sellers_item_identification and description_text != additional_description_sellers_item_identification:
            description_text = description_text + "\n" + additional_description_sellers_item_identification

        tax_rate: float = string_to_float(find_data_within_element(position, tags_to_search_tax_rate))
        quantity: float = string_to_float(
            find_data_within_element(position, tags_to_search_quantity)) if find_data_within_element(
            position,
            tags_to_search_quantity) else 1
        single_net_price: float = string_to_float_negative(
            find_data_within_element(position, tags_to_search_single_net_price))
        total_net_price: float = string_to_float_negative(
            find_data_within_element(position, tags_to_search_total_net_price))
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
                               article_number=article_number, order_pos_id=order_pos_id))
        item_position += 1

    # if not positions
    if not xml_positions_data_zugpferd and not xml_positions_data:
        xml_invoice_data.add_position(
            XmlInvoicePosition(item_pos=item_position, position_text="description_text", quantity=1,
                               single_net_price=0, tax_rate=0,
                               total_net_price=0, invoice_id=xml_invoice_data.m_cn_id,
                               article_number=None))

    logger.info_log(f"Finish get_xml_header with m_cn_id = {xml_invoice_data.m_cn_id}")

    return xml_invoice_data
