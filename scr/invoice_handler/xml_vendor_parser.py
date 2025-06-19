from ..helper_functions import find_data_within_element, delete_all_prefills, find_data_within_element_with_len, \
    get_tags_from_json
from xml.etree.ElementTree import Element
import xml.etree.ElementTree as ET


def get_einvoice_vendor_data(m_cn_id: str, xml_text: str, logger) -> (dict, str):
    logger.info_log(f"START get_einvoice_client_data with m_cn_id = {m_cn_id}")

    xml_tree: Element = ET.fromstring(xml_text)
    xml_tree = delete_all_prefills(xml_tree)
    xml_vendor_data: Element = xml_tree.find("./SupplyChainTradeTransaction")

    tags_to_search_tax_id: list = get_tags_from_json('tags_to_search_tax_id')
    tags_to_search_vendor_name: list = get_tags_from_json('tags_to_search_vendor_name')
    tags_to_search_address: list = get_tags_from_json('tags_to_search_address')
    tags_to_search_postcode: list = get_tags_from_json('tags_to_search_postcode')
    tags_to_search_city_name: list = get_tags_from_json('tags_to_search_city_name')
    tags_to_search_country: list = get_tags_from_json('tags_to_search_country')
    tags_to_search_iban: list = get_tags_from_json('tags_to_search_iban')
    tags_to_search_vendor: list = get_tags_from_json('tags_to_search_vendor')

    clients_data: dict = {
        "M_CN_ID": m_cn_id,
        "S_KR_NAME1": find_data_within_element(xml_vendor_data, tags_to_search_vendor_name),
        "S_KR_STRASSE": find_data_within_element(xml_vendor_data, tags_to_search_address),
        "S_KR_ORT": find_data_within_element(xml_vendor_data, tags_to_search_city_name),
        "S_KR_POSTLEITZAHL": find_data_within_element(xml_vendor_data, tags_to_search_postcode),
        "S_KR_LAND": find_data_within_element(xml_vendor_data, tags_to_search_country),
        "S_KR_USTID": find_data_within_element(xml_vendor_data, tags_to_search_tax_id),
        "S_KR_IBAN": find_data_within_element_with_len(xml_vendor_data, tags_to_search_iban, 22).replace(" ",
                                                                                                         "") if find_data_within_element_with_len(
            xml_vendor_data, tags_to_search_iban, 22) else None
    }
    vendor: str = find_data_within_element(xml_vendor_data, tags_to_search_vendor)

    if vendor:
        # sometimes write client supplier number not correctly
        if len(vendor) != 8 or not vendor.startswith(r"8|9\d{8}"):
            vendor = ""

    logger.info_log(f"Finish get_einvoice_client_data with m_cn_id = {m_cn_id} , supplier = {vendor}")

    return clients_data, vendor
