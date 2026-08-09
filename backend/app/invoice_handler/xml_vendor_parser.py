from typing import Any, Dict, Optional, Tuple
from xml.etree.ElementTree import Element

from ..helper_functions import (
    find_data_within_element,
    find_data_within_element_with_len,
    join_all_texts_for_tags,
    get_tags_from_json,
    get_xml_tree,
    extract_payment_means_list,
    extract_seller_vat_id_zugferd,
    extract_invoicee_or_buyer_vat_id,
)
from ..services.logger_adapter import InvoiceLogger


def get_einvoice_vendor_data(
    invoice_id: str, xml_text: str, logger: InvoiceLogger
) -> Tuple[Dict[str, Any], Optional[str]]:
    """Extract seller / buyer party data with neutral DTO keys."""
    logger.info_log(f"START get_einvoice_vendor_data invoice_id={invoice_id}")

    xml_tree: Element = get_xml_tree(xml_text)
    xml_vendor_data: Element = xml_tree.find("./SupplyChainTradeTransaction")
    if xml_vendor_data is None:
        xml_vendor_data = xml_tree

    # AccountingCustomerParty / BuyerTradeParty → buyer (billing);
    # Delivery / ShipToTradeParty → delivery address (*_delivery).
    tags_to_search_tax_id: list = get_tags_from_json("tags_to_search_tax_id")
    tags_to_search_tax_id_billing: list = get_tags_from_json("tags_to_search_tax_id_billing")
    tags_to_search_client_name: list = get_tags_from_json("tags_to_search_client_name")
    tags_to_search_client_name_delivery: list = get_tags_from_json("tags_to_search_client_name_delivery")
    tags_to_search_vendor_name: list = get_tags_from_json("tags_to_search_vendor_name")
    tags_to_search_address: list = get_tags_from_json("tags_to_search_address")
    tags_to_search_address_delivery: list = get_tags_from_json("tags_to_search_address_delivery")
    tags_to_search_postcode: list = get_tags_from_json("tags_to_search_postcode")
    tags_to_search_postcode_delivery: list = get_tags_from_json("tags_to_search_postcode_delivery")
    tags_to_search_city_name: list = get_tags_from_json("tags_to_search_city_name")
    tags_to_search_city_name_delivery: list = get_tags_from_json("tags_to_search_city_name_delivery")
    tags_to_search_country: list = get_tags_from_json("tags_to_search_country")
    tags_to_search_country_delivery: list = get_tags_from_json("tags_to_search_country_delivery")
    tags_to_search_iban: list = get_tags_from_json("tags_to_search_iban")
    tags_to_search_supplier: list = get_tags_from_json("tags_to_search_supplier")
    tags_to_search_buyer_reference: list = get_tags_from_json("tags_to_search_buyer_reference")
    tags_to_search_contact: list = get_tags_from_json("tags_to_search_contact")
    tags_to_search_client_name_billing: list = get_tags_from_json("tags_to_search_client_name_billing")
    tags_to_search_street_billing: list = get_tags_from_json("tags_to_search_street_billing")
    tags_to_search_postcode_billing: list = get_tags_from_json("tags_to_search_postcode_billing")
    tags_to_search_city_name_billing: list = get_tags_from_json("tags_to_search_city_name_billing")
    tags_to_search_country_billing: list = get_tags_from_json("tags_to_search_country_billing")
    tags_to_search_peppol_id: list = get_tags_from_json("tags_to_search_peppol_id")
    tags_to_search_client_number: list = get_tags_from_json("tags_to_search_client_number")

    iban_22: Optional[str] = find_data_within_element_with_len(xml_vendor_data, tags_to_search_iban, 22)
    seller_iban: Optional[str] = iban_22.replace(" ", "") if iban_22 else None

    vendor_data: Dict[str, Any] = {
        "invoice_id": invoice_id,
        "seller_name": find_data_within_element(xml_vendor_data, tags_to_search_vendor_name),
        "seller_street": find_data_within_element(xml_vendor_data, tags_to_search_address),
        "seller_city": find_data_within_element(xml_vendor_data, tags_to_search_city_name),
        "seller_postcode": find_data_within_element(xml_vendor_data, tags_to_search_postcode),
        "seller_country": find_data_within_element(xml_vendor_data, tags_to_search_country),
        "seller_vat_id": extract_seller_vat_id_zugferd(xml_vendor_data)
        or find_data_within_element(xml_vendor_data, tags_to_search_tax_id),
        "seller_iban": seller_iban,
        "seller_contact": find_data_within_element(xml_vendor_data, tags_to_search_contact),
        "seller_peppol_id": find_data_within_element(xml_vendor_data, tags_to_search_peppol_id),
        "buyer_name": find_data_within_element(xml_vendor_data, tags_to_search_client_name),
        "buyer_name_billing": find_data_within_element(xml_vendor_data, tags_to_search_client_name_billing),
        "buyer_name_delivery": find_data_within_element(xml_vendor_data, tags_to_search_client_name_delivery),
        "buyer_street_billing": find_data_within_element(xml_vendor_data, tags_to_search_street_billing),
        "buyer_postcode_billing": find_data_within_element(xml_vendor_data, tags_to_search_postcode_billing),
        "buyer_city_billing": find_data_within_element(xml_vendor_data, tags_to_search_city_name_billing),
        "buyer_country_billing": find_data_within_element(xml_vendor_data, tags_to_search_country_billing),
        "buyer_street_delivery": find_data_within_element(xml_vendor_data, tags_to_search_address_delivery),
        "buyer_postcode_delivery": find_data_within_element(xml_vendor_data, tags_to_search_postcode_delivery),
        "buyer_city_delivery": find_data_within_element(xml_vendor_data, tags_to_search_city_name_delivery),
        "buyer_country_delivery": find_data_within_element(xml_vendor_data, tags_to_search_country_delivery),
        "buyer_vat_id": extract_invoicee_or_buyer_vat_id(xml_vendor_data)
        or find_data_within_element(xml_vendor_data, tags_to_search_tax_id_billing),
        "buyer_reference": find_data_within_element(xml_vendor_data, tags_to_search_buyer_reference),
        "buyer_notes": join_all_texts_for_tags(xml_tree, tags_to_search_client_number),
        "payment_means": extract_payment_means_list(xml_vendor_data),
    }

    vendor: Optional[str] = find_data_within_element(xml_vendor_data, tags_to_search_supplier)

    if not vendor_data["seller_iban"]:
        iban_16: Optional[str] = find_data_within_element_with_len(xml_vendor_data, tags_to_search_iban, 16)
        vendor_data["seller_iban"] = iban_16.replace(" ", "") if iban_16 else None

    if vendor and len(vendor) != 8:
        vendor = ""

    logger.info_log(f"Finish get_einvoice_vendor_data invoice_id={invoice_id}, supplier={vendor}")
    return vendor_data, vendor
