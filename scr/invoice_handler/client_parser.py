from ..helper_functions import find_data_within_element, delete_all_prefills, find_data_within_element_with_len
from xml.etree.ElementTree import Element
import xml.etree.ElementTree as ET


def get_einvoice_client_data(m_cn_id: str, xml_text: str, logger) -> (dict, str):
    logger.info_log(f"START get_einvoice_client_data with m_cn_id = {m_cn_id}")

    xml_tree: Element = ET.fromstring(xml_text)
    xml_tree = delete_all_prefills(xml_tree)
    xml_supplier_data: Element = xml_tree.find("./SupplyChainTradeTransaction")

    tags_to_search_s_kr_ustd: list = ['./ApplicableHeaderTradeAgreement/SellerTradeParty/SpecifiedTaxRegistration/ID']
    tags_to_search_s_kr_name1: list = ['./ApplicableHeaderTradeAgreement/SellerTradeParty/Name']
    tags_to_search_s_kr_strasse: list = ['./ApplicableHeaderTradeAgreement/SellerTradeParty/PostalTradeAddress/LineOne']
    tags_to_search_s_kr_postleitzahl: list = [
        './ApplicableHeaderTradeAgreement/SellerTradeParty/PostalTradeAddress/PostcodeCode']
    tags_to_search_s_kr_ort: list = ['./ApplicableHeaderTradeAgreement/SellerTradeParty/PostalTradeAddress/CityName']
    tags_to_search_s_kr_country: list = [
        './ApplicableHeaderTradeAgreement/SellerTradeParty/PostalTradeAddress/CountryID']
    tags_to_search_iban: list = ['./ApplicableHeaderTradeAgreement/BuyerTradeParty/ID',
                                 './ApplicableHeaderTradeSettlement/SpecifiedTradeSettlementPaymentMeans/PayeePartyCreditorFinancialAccount/IBANID']
    tags_to_search_supplier: list = ['./ApplicableHeaderTradeAgreement/SellerTradeParty/ID']

    clients_data: dict = {
        "M_CN_ID": m_cn_id,
        "S_KR_NAME1": find_data_within_element(xml_supplier_data, tags_to_search_s_kr_name1),
        "S_KR_STRASSE": find_data_within_element(xml_supplier_data, tags_to_search_s_kr_strasse),
        "S_KR_ORT": find_data_within_element(xml_supplier_data, tags_to_search_s_kr_ort),
        "S_KR_POSTLEITZAHL": find_data_within_element(xml_supplier_data, tags_to_search_s_kr_postleitzahl),
        "S_KR_LAND": find_data_within_element(xml_supplier_data, tags_to_search_s_kr_country),
        "S_KR_USTID": find_data_within_element(xml_supplier_data, tags_to_search_s_kr_ustd),
        "S_KR_IBAN": find_data_within_element_with_len(xml_supplier_data, tags_to_search_iban, 22).replace(" ", "") if find_data_within_element_with_len(xml_supplier_data, tags_to_search_iban, 22) else None
    }
    supplier: str = find_data_within_element(xml_supplier_data, tags_to_search_supplier)

    if supplier:
        # sometimes write client supplier number not correctly
        if len(supplier) != 8 or not supplier.startswith(r"8|9\d{8}"):
            supplier = ""

    logger.info_log(f"Finish get_einvoice_client_data with m_cn_id = {m_cn_id} , supplier = {supplier}")

    return clients_data, supplier
