import re
from ..data_class import XmlInvoiceHeader
from ..data_class import XmlInvoicePosition
from ..helper_functions import get_xml_three, find_data_within_element


# from logger.einvoice_logging import EinvoiceLoger


# TODO check with another kreditor (without IBAN)
# extract xml data from pdf file
def get_zugpferd_positions(m_cn_id: str, xml_text: str, xml_invoice_data: XmlInvoiceHeader):
    print("##### START get_zugpferd_positions")
    xml_tree = get_xml_three(xml_text)
    xml_positions_data = xml_tree.find("./SupplyChainTradeTransaction")
    tags_to_search_description: list = ['SpecifiedTradeProduct/Description', 'SpecifiedTradeProduct/Name']
    tags_to_search_tax_rate: list = ['SpecifiedLineTradeSettlement/ApplicableTradeTax/RateApplicablePercent']
    tags_to_search_quantity: list = ['SpecifiedLineTradeDelivery/BilledQuantity']
    tags_to_search_single_net_price: list = ['SpecifiedLineTradeAgreement/NetPriceProductTradePrice/ChargeAmount']
    tags_to_search_total_net_price: list = [
        'SpecifiedLineTradeSettlement/SpecifiedTradeSettlementLineMonetarySummation/LineTotalAmount']

    # positions
    item_position = 1
    for position in xml_positions_data.iter("IncludedSupplyChainTradeLineItem"):
        # print("######### position", position)
        description_text = find_data_within_element(position, tags_to_search_description)[
                           0:499] if find_data_within_element(position, tags_to_search_description) else "Default text"
        tax_rate = find_data_within_element(position, tags_to_search_tax_rate)
        quantity = find_data_within_element(position, tags_to_search_quantity) if find_data_within_element(position,
                                                                                                           tags_to_search_quantity) else 1
        single_net_price = find_data_within_element(position, tags_to_search_single_net_price)
        total_net_price = find_data_within_element(position, tags_to_search_total_net_price)

        article_number = ""
        try:
            if re.findall("OE\s*\w{9,}", description_text):
                article_number = re.findall("OE\s*\w{9,}", description_text)[0].replace("OE", "").replace(" ", "")
        except Exception as e:
            print(f"Mistake with article number {e}")
            # logger.error_log(f"Mistake with positions {e}")

        xml_invoice_data.add_position(
            XmlInvoicePosition(item_pos=item_position, position_text=description_text, quantity=quantity,
                               single_net_price=single_net_price, tax_rate=tax_rate,
                               total_net_price=total_net_price, invoice_id=xml_invoice_data.m_cn_id,
                               article_number=article_number))
        item_position += 1

    # logger.info_log(f"end script zugpferd_extraction")

    return xml_invoice_data
