from datetime import datetime
import re
from ..data_class import XmlInvoiceHeader
from ..helper_functions import find_data_within_element, find_data_with_regex, get_xml_tree
from xml.etree.ElementTree import Element


# TODO logger
# extract xml data from pdf file
# def zugpferd_extraction(m_cn_id: str, xml_text: str, db_helper, barcode: str):
def get_xml_header(m_cn_id: str, xml_text: str, barcode: str,
                   xml_invoice_data: XmlInvoiceHeader) -> XmlInvoiceHeader:
    print("##### START zugpferd_extraction")
    # logger = EinvoiceLoger("zugpferd_extraction", m_cn_id)
    # logger.info_log(f"start zugpferd_extraction with m_cn_id = {m_cn_id}")

    xml_tree: Element = get_xml_tree(xml_text)

    xml_exchanged_document: Element = xml_tree.find("./ExchangedDocument")
    xml_invoice_head: Element = xml_tree.find("./SupplyChainTradeTransaction/ApplicableHeaderTradeSettlement")
    xml_invoice_head_money: Element = xml_tree.find(
        "./SupplyChainTradeTransaction/ApplicableHeaderTradeSettlement/SpecifiedTradeSettlementHeaderMonetarySummation")
    xml_supplier_data: Element = xml_tree.find("./SupplyChainTradeTransaction")
    xml_positions_data: Element = xml_tree.find("./SupplyChainTradeTransaction")

    # header data
    tags_to_search_invoice_number: list = ['./ID']
    tags_to_search_order_id: list = ['./ApplicableHeaderTradeAgreement/BuyerOrderReferencedDocument/IssuerAssignedID',
                                     './IncludedNote/Content']
    tags_to_search_invoice_date: list = ['./IssueDateTime/DateTimeString']
    tags_to_search_delivery_date: list = ['./BillingSpecifiedPeriod/StartDateTime/DateTimeString']
    tags_to_search_delivery_date_till: list = ['./BillingSpecifiedPeriod/EndDateTime/DateTimeString']
    tags_to_search_currency: list = ['./InvoiceCurrencyCode']
    tags_to_search_invoice_amount: list = ['./TaxBasisTotalAmount']
    tags_to_search_total_amount: list = ['./GrandTotalAmount']
    tags_to_search_total_tax_amount: list = ['./TaxTotalAmount']
    tags_to_search_supplier: list = ['./ApplicableHeaderTradeAgreement/SellerTradeParty/ID']
    tags_to_search_iban: list = ['./ApplicableHeaderTradeAgreement/BuyerTradeParty/ID',
                                 './ApplicableHeaderTradeSettlement/SpecifiedTradeSettlementPaymentMeans/PayeePartyCreditorFinancialAccount/IBANID']

    tags_to_search_tax_amount1: list = [
        './SupplyChainTradeTransaction/ApplicableHeaderTradeSettlement/ApplicableTradeTax/CalculatedAmount']
    tags_to_search_tax_rate1: list = [
        './SupplyChainTradeTransaction/ApplicableHeaderTradeSettlement/ApplicableTradeTax/RateApplicablePercent']
    tags_to_search_kind_of_invoice: list = ['./TypeCode']
    xml_invoice_data.invoice_number: str = find_data_within_element(xml_exchanged_document, tags_to_search_invoice_number)

    print("####### xml_invoice_data.invoice_number ", xml_invoice_data.invoice_number)

    try:
        xml_invoice_data.invoice_date = datetime.strptime(
            find_data_within_element(xml_exchanged_document, tags_to_search_invoice_date), '%Y%m%d')
    except Exception as e:
        print(f"Invoice date Date was not found {e}")
        # logger.error_log(f"Invoice date Date was not found {e}")
    try:
        xml_invoice_data.delivery_date = datetime.strptime(
            find_data_within_element(xml_invoice_head, tags_to_search_delivery_date), '%Y%m%d')
    except Exception as e:
        print(f"Delivery date was not found {e}")
        # logger.error_log(f"Delivery date was not found {e}")

    try:
        xml_invoice_data.delivery_date_till = datetime.strptime(
            find_data_within_element(xml_invoice_head, tags_to_search_delivery_date_till), '%Y%m%d')
    except Exception as e:
        print(f"Delivery date bis was not found {e}")
        # logger.error_log(f"Delivery date bis was not found {e}")

    xml_invoice_data.currency = find_data_within_element(xml_invoice_head,
                                                         tags_to_search_currency) if not find_data_within_element(
        xml_invoice_head, tags_to_search_currency) else "EUR"

    print("xml_invoice_data.currency ", xml_invoice_data.invoice_date)

    xml_invoice_data.order_id = find_data_within_element(xml_supplier_data, tags_to_search_order_id)

    # TODO test
    # SWFM-5293
    if not xml_invoice_data.order_id:
        # sometimes we get order in positions
        xml_invoice_data.order_id = find_data_with_regex(xml_positions_data, "930\d{7}|960\d{7}")

    if not xml_invoice_data.order_id:
        text_order_id = find_data_within_element(xml_exchanged_document, tags_to_search_order_id)
        if text_order_id:
            try:
                xml_invoice_data.order_id = re.findall("930\d{7}|960\d{7}", text_order_id)[0]
            except Exception as e:
                print(f"Order was not found {e}")
                # logger.error_log(f"Order bis was not found {e}")

    xml_invoice_data.invoice_amount = find_data_within_element(xml_invoice_head_money, tags_to_search_invoice_amount)
    xml_invoice_data.total_amount = find_data_within_element(xml_invoice_head_money, tags_to_search_total_amount)
    xml_invoice_data.total_tax_amount = find_data_within_element(xml_invoice_head_money,
                                                                 tags_to_search_total_tax_amount)
    xml_invoice_data.tax_amount1 = find_data_within_element(xml_tree, tags_to_search_tax_amount1)
    xml_invoice_data.tax_rate1 = find_data_within_element(xml_tree, tags_to_search_tax_rate1)
    xml_invoice_data.supplier = find_data_within_element(xml_supplier_data, tags_to_search_supplier)
    xml_invoice_data.client = "1"
    xml_invoice_data.m_cn_id = m_cn_id
    xml_invoice_data.barcode = barcode
    xml_invoice_data.image_path = barcode + ".pdf"
    xml_invoice_data.iban = find_data_within_element(xml_supplier_data, tags_to_search_iban)
    if xml_invoice_data.iban:
        if len(xml_invoice_data.iban) < 22:
            xml_invoice_data.iban = find_data_within_element(xml_supplier_data, tags_to_search_iban)

    xml_invoice_data.kind_of_invoice = "RE" if find_data_within_element(xml_exchanged_document,
                                                                        tags_to_search_kind_of_invoice) == '380' else "GU"

    xml_invoice_data.correct_data()

    return xml_invoice_data
