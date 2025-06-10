import re
from ..data_class import XmlInvoiceHeader
from ..data_class import XmlInvoicePosition
from ..helper_functions import get_xml_tree, find_data_within_element
from xml.etree.ElementTree import Element
from ..helper_functions.einvoice_helper import string_to_float


# from logger.einvoice_logging import EinvoiceLoger


# TODO check with another kreditor (without IBAN)
# extract xml data from pdf file
def get_xml_positions(m_cn_id: str, xml_text: str, xml_invoice_data: XmlInvoiceHeader, logger) -> XmlInvoiceHeader:
    print("##### START get_zugpferd_positions")
    logger.info_log(f"START get_xml_header with m_cn_id = {m_cn_id}")

    xml_tree: Element = get_xml_tree(xml_text)
    xml_positions_data: Element = xml_tree.find("./SupplyChainTradeTransaction")
    tags_to_search_description: list = ['SpecifiedTradeProduct/Description', 'SpecifiedTradeProduct/Name']
    tags_to_search_tax_rate: list = ['SpecifiedLineTradeSettlement/ApplicableTradeTax/RateApplicablePercent']
    tags_to_search_quantity: list = ['SpecifiedLineTradeDelivery/BilledQuantity']
    tags_to_search_single_net_price: list = ['SpecifiedLineTradeAgreement/NetPriceProductTradePrice/ChargeAmount']
    tags_to_search_total_net_price: list = [
        'SpecifiedLineTradeSettlement/SpecifiedTradeSettlementLineMonetarySummation/LineTotalAmount']

    # positions
    item_position: int = 1
    for position in xml_positions_data.iter("IncludedSupplyChainTradeLineItem"):
        # print("######### position", position)
        description_text: str = find_data_within_element(position, tags_to_search_description)[
                                0:499] if find_data_within_element(position,
                                                                   tags_to_search_description) else "Default text"
        tax_rate: float = string_to_float(find_data_within_element(position, tags_to_search_tax_rate))
        quantity: float = string_to_float(find_data_within_element(position, tags_to_search_quantity)) if find_data_within_element(
            position,
            tags_to_search_quantity) else 1
        single_net_price: float = string_to_float(find_data_within_element(position, tags_to_search_single_net_price))
        total_net_price: float = string_to_float(find_data_within_element(position, tags_to_search_total_net_price))

        article_number: str = ""
        try:
            if re.findall("OE\s*\w{9,}", description_text):
                article_number: str = re.findall("OE\s*\w{9,}", description_text)[0].replace("OE", "").replace(" ", "")
        except Exception as e:
            print(f"Mistake with article number {e}")
            logger.error_log(f"Mistake with article number {e}")

        xml_invoice_data.add_position(
            XmlInvoicePosition(item_pos=item_position, position_text=description_text, quantity=quantity,
                               single_net_price=single_net_price, tax_rate=tax_rate,
                               total_net_price=total_net_price, invoice_id=xml_invoice_data.m_cn_id,
                               article_number=article_number))
        item_position += 1

    logger.info_log(f"Finish get_xml_header with m_cn_id = {m_cn_id}")

    return xml_invoice_data
