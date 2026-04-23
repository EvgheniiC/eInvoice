from ..helper_functions import find_data_within_element, delete_all_prefills, find_data_within_element_with_len, \
    join_all_texts_for_tags, get_tags_from_json, get_field_value, get_vehicle_value, extract_payment_means_list, \
    extract_seller_vat_id_zugferd, extract_invoicee_or_buyer_vat_id
from xml.etree.ElementTree import Element
import xml.etree.ElementTree as ET


def get_einvoice_vendor_data(m_cn_id: str, xml_text: str, logger) -> (dict, str):
    logger.info_log(f"START get_einvoice_client_data with m_cn_id = {m_cn_id}")

    xml_tree: Element = ET.fromstring(xml_text)
    xml_tree = delete_all_prefills(xml_tree)
    xml_vendor_data: Element = xml_tree.find("./SupplyChainTradeTransaction")
    # for not zugpferd format, only xml
    if not xml_vendor_data:
        xml_vendor_data: Element = xml_tree

    # SWFM-5490 AccountingCustomerParty -> for Address of the Sixt company, Delivery -> for Lieferanschrift (xxx_delivery)
    tags_to_search_tax_id: list = get_tags_from_json('tags_to_search_tax_id')
    tags_to_search_tax_id_billing: list = get_tags_from_json('tags_to_search_tax_id_billing')
    tags_to_search_client_name: list = get_tags_from_json('tags_to_search_client_name')
    tags_to_search_client_name_delivery: list = get_tags_from_json('tags_to_search_client_name_delivery')
    tags_to_search_vendor_name: list = get_tags_from_json('tags_to_search_vendor_name')
    tags_to_search_address: list = get_tags_from_json('tags_to_search_address')
    tags_to_search_address_delivery: list = get_tags_from_json('tags_to_search_address_delivery')
    tags_to_search_postcode: list = get_tags_from_json('tags_to_search_postcode')
    tags_to_search_postcode_delivery: list = get_tags_from_json('tags_to_search_postcode_delivery')
    tags_to_search_city_name: list = get_tags_from_json('tags_to_search_city_name')
    tags_to_search_city_name_delivery: list = get_tags_from_json('tags_to_search_city_name_delivery')
    tags_to_search_country: list = get_tags_from_json('tags_to_search_country')
    tags_to_search_country_delivery: list = get_tags_from_json('tags_to_search_country_delivery')
    tags_to_search_iban: list = get_tags_from_json('tags_to_search_iban')
    tags_to_search_supplier: list = get_tags_from_json('tags_to_search_supplier')
    tags_to_search_buyer_reference: list = get_tags_from_json('tags_to_search_buyer_reference')
    tags_to_search_contact: list = get_tags_from_json('tags_to_search_contact')
    tags_to_search_client_name_billing: list = get_tags_from_json('tags_to_search_client_name_billing')
    tags_to_search_street_billing: list = get_tags_from_json('tags_to_search_street_billing')
    tags_to_search_postcode_billing: list = get_tags_from_json('tags_to_search_postcode_billing')
    tags_to_search_city_name_billing: list = get_tags_from_json('tags_to_search_city_name_billing')
    tags_to_search_country_billing: list = get_tags_from_json('tags_to_search_country_billing')
    tags_to_search_peppol_id: list = get_tags_from_json('tags_to_search_peppol_id')
    tags_to_search_client_number: list = get_tags_from_json('tags_to_search_client_number')

    clients_data: dict = {
        "M_CN_ID": m_cn_id,
        "S_KR_NAME1": find_data_within_element(xml_vendor_data, tags_to_search_vendor_name),
        "S_KR_STRASSE": find_data_within_element(xml_vendor_data, tags_to_search_address),
        "S_KR_STRASSE_DELIVERY": find_data_within_element(xml_vendor_data, tags_to_search_address_delivery),
        "S_KR_ORT": find_data_within_element(xml_vendor_data, tags_to_search_city_name),
        "S_KR_ORT_DELIVERY": find_data_within_element(xml_vendor_data, tags_to_search_city_name_delivery),
        "S_KR_POSTLEITZAHL": find_data_within_element(xml_vendor_data, tags_to_search_postcode),
        "S_KR_POSTLEITZAHL_DELIVERY": find_data_within_element(xml_vendor_data, tags_to_search_postcode_delivery),
        "S_KR_LAND": find_data_within_element(xml_vendor_data, tags_to_search_country),
        "S_KR_LAND_DELIVERY": find_data_within_element(xml_vendor_data, tags_to_search_country_delivery),
        "S_KR_USTID": extract_seller_vat_id_zugferd(xml_vendor_data) or find_data_within_element(
            xml_vendor_data, tags_to_search_tax_id),
        "S_KR_USTID_BILLING": extract_invoicee_or_buyer_vat_id(xml_vendor_data) or find_data_within_element(
            xml_vendor_data, tags_to_search_tax_id_billing),
        "S_KR_CLIENT_NAME": find_data_within_element(xml_vendor_data, tags_to_search_client_name),
        "S_KR_CLIENT_NAME_DELIVERY": find_data_within_element(xml_vendor_data, tags_to_search_client_name_delivery),
        "S_KR_IBAN": find_data_within_element_with_len(xml_vendor_data, tags_to_search_iban, 22).replace(" ",
                                                                                                         "") if find_data_within_element_with_len(
            xml_vendor_data, tags_to_search_iban, 22) else None,
        "S_KR_EMPLOYEE_ID": get_field_value(xml_tree, 'employee_id'),
        "S_KR_BUDGET": get_field_value(xml_tree, 'cc_budget'),
        "S_KR_TRIP_INFO": get_field_value(xml_tree, 'trip_purpose'),
        "S_KR_APPROVAL": get_field_value(xml_tree, 'pa_report_id'),
        "S_KR_TRIP_PURPOSE": get_field_value(xml_tree, 'private_extension'),
        "S_KR_BUYERREFERENCE": find_data_within_element(xml_vendor_data, tags_to_search_buyer_reference),
        "S_KR_CONTACT": find_data_within_element(xml_vendor_data, tags_to_search_contact),
        "S_KR_CLIENT_NAME_BILLING": find_data_within_element(xml_vendor_data, tags_to_search_client_name_billing),
        "S_KR_STRASSE_BILLING": find_data_within_element(xml_vendor_data, tags_to_search_street_billing),
        "S_KR_POSTLEITZAHL_BILLING": find_data_within_element(xml_vendor_data, tags_to_search_postcode_billing),
        "S_KR_ORT_BILLING": find_data_within_element(xml_vendor_data, tags_to_search_city_name_billing),
        "S_KR_LAND_BILLING": find_data_within_element(xml_vendor_data, tags_to_search_country_billing),
        "S_KR_VEHICLE_REGISTRATION": get_vehicle_value(xml_text, "registration"),
        "S_KR_VEHICLE_ODOMETER_READING": get_vehicle_value(xml_text, "odometer"),
        "S_KR_VEHICLE_ID": get_vehicle_value(xml_text, "Identification"),
        "S_KR_PAYMENT_MEANS": extract_payment_means_list(xml_vendor_data),
        "S_KR_PEPPOL_ID": find_data_within_element(xml_vendor_data, tags_to_search_peppol_id),
        "S_KR_CLIENT_NUMBER": join_all_texts_for_tags(xml_tree, tags_to_search_client_number)
    }

    # HW-5851 new field(S_KR_EMPLOYEE_ID,S_KR_BUDGET,S_KR_TRIP_INFO,S_KR_APPROVAL,S_KR_TRIP_PURPOSE)
    vendor: str = find_data_within_element(xml_vendor_data, tags_to_search_supplier)

    # sometimes len(IBAN) = 16(for client 35)
    if not clients_data["S_KR_IBAN"]:
        clients_data["S_KR_IBAN"] = find_data_within_element_with_len(xml_vendor_data, tags_to_search_iban, 16).replace(
            " ",
            "") if find_data_within_element_with_len(
            xml_vendor_data, tags_to_search_iban, 16) else None

    if vendor:
        # sometimes write client supplier number not correctly
        if len(vendor) != 8 and vendor.startswith(r"8|9\d{7}") != 'False':
            vendor = ""

    logger.info_log(f"Finish get_einvoice_client_data with m_cn_id = {m_cn_id} , supplier = {vendor}")

    return clients_data, vendor
