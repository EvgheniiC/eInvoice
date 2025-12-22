from ..data_class import XmlInvoiceHeader, XmlInvoiceEquipment
from ..helper_functions import get_xml_tree, find_data_within_element, get_tags_from_json
from xml.etree.ElementTree import Element
from ..helper_functions.einvoice_helper import string_to_float


# extract equipment data from XML
def get_xml_equipment(xml_text: str, xml_invoice_data: XmlInvoiceHeader, logger) -> XmlInvoiceHeader:
    print("##### START get_xml_equipment")
    logger.info_log(f"START get_xml_header with m_cn_id = {xml_invoice_data.m_cn_id}")

    xml_tree: Element = get_xml_tree(xml_text)
    # some XML invoices have a tag InvoiceLine for equipment
    xml_equipment_data: list = xml_tree.findall("./InvoiceLine")
    pos_nummer: int = 1
    tags_to_search_description: list = get_tags_from_json('tags_to_search_description')
    tags_to_search_pos_code: list = get_tags_from_json('tags_to_search_pos_code')
    tags_to_search_pos_price: list = get_tags_from_json('tags_to_search_pos_price')
    tags_to_search_pos_msrp_price: list = get_tags_from_json('tags_to_search_pos_msrp_price')

    # for BE
    if not xml_equipment_data:
        xml_equipment_data: list = xml_tree.findall("./Invoice/InvoiceLine")

    for equipment in xml_equipment_data:
        pos_description: str = find_data_within_element(equipment, tags_to_search_description)[0:499]
        pos_code: str = find_data_within_element(equipment, tags_to_search_pos_code)
        pos_price: float = string_to_float(
            find_data_within_element(equipment, tags_to_search_pos_price))
        pos_msrp_price: float = string_to_float(
            find_data_within_element(equipment, tags_to_search_pos_msrp_price))

        xml_invoice_data.add_position_equipment(
            XmlInvoiceEquipment(m_cn_header_id=xml_invoice_data.m_cn_id, pos_nummer=pos_nummer, pos_code=pos_code,
                                pos_description=pos_description, pos_price=pos_price, pos_msrp_price=pos_msrp_price))
        pos_nummer += 1

    logger.info_log(f"Finish get_xml_header with m_cn_id = {xml_invoice_data.m_cn_id}")

    return xml_invoice_data
