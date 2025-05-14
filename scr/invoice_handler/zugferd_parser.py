from datetime import datetime
import re
import xml.etree.ElementTree as ET

from xml.etree.ElementTree import Element
from ..data_class import XmlInvoiceHeader
from ..data_class import XmlInvoicePosition
from ..helper_functions import find_data_within_element


# from logger.einvoice_logging import EinvoiceLoger

# from invoice_extraction.helperFunctions.logging import get_next_seq_val
# from invoice_extraction.helperFunctions.dbHelper import config

# inv_path = config('inv_path')
# inv_target_path = config('inv_target_path')
# mail_body_path = config('mail_body_path')


# delete all prefixes from xml
def delete_all_prefills(xml_tree: ET):
    """
    {urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100}CrossIndustryInvoice' -> CrossIndustryInvoice
    """
    # Remove namespace prefixes
    for elem in xml_tree.iter():
        # Get the tag name without the prefix
        tag = elem.tag.split("}")[1] if "}" in elem.tag else elem.tag
        # Replace the element tag with the tag name without prefix
        elem.tag = tag
    return xml_tree


def find_data_with_regex(element: Element, regex_pattern: str) -> str | None:
    """
    Finds data within all tags of an XML element using a regular expression pattern.
    For exam, we can find order number 930…

    Args:
    - element: The XML element to search for data.
    - regex_pattern: The regular expression pattern to search for within the element tags.

    Returns:
    - The matched data found within the tags based on the regex pattern. Returns None if no match is found.
    """
    all_tags_data = ' '.join(element.itertext())  # Get all text content within the element and tags
    match = re.search(regex_pattern, all_tags_data)

    if match:
        return match.group(0)
    else:
        return None


# TODO check with another kreditor (without IBAN)
# extract xml data from pdf file
def zugpferd_extraction(m_cn_id: str, xml_text: str, db_helper, barcode: str):
    print("##### START zugpferd_extraction")
    # logger = EinvoiceLoger("zugpferd_extraction", m_cn_id)
    # logger.info_log(f"start zugpferd_extraction with m_cn_id = {m_cn_id}")
    xml_tree: Element = ET.fromstring(xml_text)
    xml_tree = delete_all_prefills(xml_tree)

    xml_exchanged_document = xml_tree.find("./ExchangedDocument")
    xml_invoice_head = xml_tree.find("./SupplyChainTradeTransaction/ApplicableHeaderTradeSettlement")
    xml_invoice_head_money = xml_tree.find(
        "./SupplyChainTradeTransaction/ApplicableHeaderTradeSettlement/SpecifiedTradeSettlementHeaderMonetarySummation")
    # xml_invoice_head_tax = xml_tree.find(
    #     "./SupplyChainTradeTransaction/ApplicableHeaderTradeSettlement/ApplicableTradeTax")
    xml_supplier_data = xml_tree.find("./SupplyChainTradeTransaction")
    xml_positions_data = xml_tree.find("./SupplyChainTradeTransaction")

    # header data
    xml_invoice_data = XmlInvoiceHeader(m_cn_id=m_cn_id)
    # xml_invoice_data.invoice_number = xml_exchanged_document.find("./ID").text
    tags_to_search_invoice_number = ['./ID']
    tags_to_search_order_id = ['./ApplicableHeaderTradeAgreement/BuyerOrderReferencedDocument/IssuerAssignedID',
                               './IncludedNote/Content']
    tags_to_search_invoice_date = ['./IssueDateTime/DateTimeString']
    tags_to_search_delivery_date = ['./BillingSpecifiedPeriod/StartDateTime/DateTimeString']
    tags_to_search_delivery_date_till = ['./BillingSpecifiedPeriod/EndDateTime/DateTimeString']
    tags_to_search_currency = ['./InvoiceCurrencyCode']
    tags_to_search_invoice_amount = ['./TaxBasisTotalAmount']
    tags_to_search_total_amount = ['./GrandTotalAmount']
    tags_to_search_total_tax_amount = ['./TaxTotalAmount']
    tags_to_search_supplier = ['./ApplicableHeaderTradeAgreement/SellerTradeParty/ID']
    tags_to_search_iban = ['./ApplicableHeaderTradeAgreement/BuyerTradeParty/ID',
                           './ApplicableHeaderTradeSettlement/SpecifiedTradeSettlementPaymentMeans/PayeePartyCreditorFinancialAccount/IBANID']
    tags_to_search_s_kr_ustd = ['./ApplicableHeaderTradeAgreement/SellerTradeParty/SpecifiedTaxRegistration/ID']
    tags_to_search_s_kr_name1 = ['./ApplicableHeaderTradeAgreement/SellerTradeParty/Name']
    tags_to_search_s_kr_strasse = ['./ApplicableHeaderTradeAgreement/SellerTradeParty/PostalTradeAddress/LineOne']
    tags_to_search_s_kr_postleitzahl = [
        './ApplicableHeaderTradeAgreement/SellerTradeParty/PostalTradeAddress/PostcodeCode']
    tags_to_search_s_kr_ort = ['./ApplicableHeaderTradeAgreement/SellerTradeParty/PostalTradeAddress/CityName']
    tags_to_search_s_kr_country = ['./ApplicableHeaderTradeAgreement/SellerTradeParty/PostalTradeAddress/CountryID']
    tags_to_search_tax_amount1 = [
        './SupplyChainTradeTransaction/ApplicableHeaderTradeSettlement/ApplicableTradeTax/CalculatedAmount']
    tags_to_search_tax_rate1 = [
        './SupplyChainTradeTransaction/ApplicableHeaderTradeSettlement/ApplicableTradeTax/RateApplicablePercent']
    tags_to_search_kind_of_invoice = ['./TypeCode']
    xml_invoice_data.invoice_number = find_data_within_element(xml_exchanged_document, tags_to_search_invoice_number)

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
        # xml_invoice_data.order_id = get_ordernummer_from_positions(xml_positions_data)
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

    # xml_invoice_data.invoice_amount = xml_invoice_head_money.find(
    #     "./TaxBasisTotalAmount").text if xml_invoice_head_money.find("./TaxBasisTotalAmount") is not None else None

    # xml_invoice_data.total_amount = xml_invoice_head_money.find(
    #     "./GrandTotalAmount").text if xml_invoice_head_money.find("./GrandTotalAmount") is not None else None

    # xml_invoice_data.total_tax_amount = xml_invoice_head_money.find(
    #     "./TaxTotalAmount").text if xml_invoice_head_money.find("./TaxTotalAmount") is not None else None

    # xml_invoice_data.supplier = xml_supplier_data.find(
    #     "./ApplicableHeaderTradeAgreement/SellerTradeParty/ID").text if xml_supplier_data.find(
    #     "./ApplicableHeaderTradeAgreement/SellerTradeParty/ID") is not None else None

    # xml_invoice_data.iban = xml_supplier_data.find(
    #     "./ApplicableHeaderTradeAgreement/BuyerTradeParty/ID").text if xml_supplier_data.find(
    #     "./ApplicableHeaderTradeAgreement/BuyerTradeParty/ID") is not None else None

    # if xml_invoice_data.iban:
    # if len(xml_invoice_data.iban) < 22:
    #         xml_invoice_data.iban = xml_supplier_data.find(
    #             "./ApplicableHeaderTradeSettlement/SpecifiedTradeSettlementPaymentMeans/PayeePartyCreditorFinancialAccount/IBANID").text if xml_supplier_data.find(
    #             "./ApplicableHeaderTradeSettlement/SpecifiedTradeSettlementPaymentMeans/PayeePartyCreditorFinancialAccount/IBANID") is not None else None

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

    # s_kr_ustd = find_data_within_element(xml_supplier_data, tags_to_search_s_kr_ustd)
    # s_kr_name1 = find_data_within_element(xml_supplier_data, tags_to_search_s_kr_name1)
    # s_kr_strasse = find_data_within_element(xml_supplier_data, tags_to_search_s_kr_strasse)
    # s_kr_postleitzahl = find_data_within_element(xml_supplier_data, tags_to_search_s_kr_postleitzahl)
    # s_kr_s_kr_ort = find_data_within_element(xml_supplier_data, tags_to_search_s_kr_ort)
    # s_kr_s_kr_country = find_data_within_element(xml_supplier_data, tags_to_search_s_kr_country)

    # s_kr_ustd = xml_supplier_data.find(
    #     "./ApplicableHeaderTradeAgreement/SellerTradeParty/SpecifiedTaxRegistration/ID").text if xml_supplier_data.find(
    #     "./ApplicableHeaderTradeAgreement/SellerTradeParty/SpecifiedTaxRegistration/ID") is not None else None
    # s_kr_name1 = xml_supplier_data.find(
    #     "./ApplicableHeaderTradeAgreement/SellerTradeParty/Name").text if xml_supplier_data.find(
    #     "./ApplicableHeaderTradeAgreement/SellerTradeParty/Name") is not None else None
    # s_kr_strasse = xml_supplier_data.find(
    #     "./ApplicableHeaderTradeAgreement/SellerTradeParty/PostalTradeAddress/LineOne").text if xml_supplier_data.find(
    #     "./ApplicableHeaderTradeAgreement/SellerTradeParty/PostalTradeAddress/LineOne") is not None else None
    # s_kr_postleitzahl = xml_supplier_data.find(
    #     "./ApplicableHeaderTradeAgreement/SellerTradeParty/PostalTradeAddress/PostcodeCode").text if xml_supplier_data.find(
    #     "./ApplicableHeaderTradeAgreement/SellerTradeParty/PostalTradeAddress/PostcodeCode") is not None else None
    # s_kr_ort = xml_supplier_data.find(
    #     "./ApplicableHeaderTradeAgreement/SellerTradeParty/PostalTradeAddress/CityName").text if xml_supplier_data.find(
    #     "./ApplicableHeaderTradeAgreement/SellerTradeParty/PostalTradeAddress/CityName") is not None else None

    clients_data = {
        "M_CN_ID": m_cn_id,
        "S_KR_NAME1": find_data_within_element(xml_supplier_data, tags_to_search_s_kr_name1),
        "S_KR_STRASSE": find_data_within_element(xml_supplier_data, tags_to_search_s_kr_strasse),
        "S_KR_ORT": find_data_within_element(xml_supplier_data, tags_to_search_s_kr_ort),
        "S_KR_POSTLEITZAHL": find_data_within_element(xml_supplier_data, tags_to_search_s_kr_postleitzahl),
        "S_KR_LAND": find_data_within_element(xml_supplier_data, tags_to_search_s_kr_country),
        "S_KR_USTID": find_data_within_element(xml_supplier_data, tags_to_search_s_kr_ustd),
        "S_KR_IBAN": xml_invoice_data.iban
    }
    print("clients_data = ", clients_data)
    # sometimes write client supplier number not correctly
    # if not xml_invoice_data.supplier or len(xml_invoice_data.supplier) > 8:
    #     xml_invoice_data.supplier = get_kreditor_cronox(clients_data)

    # xml_invoice_data.tax_amount1 = xml_tree.find(
    #     "./SupplyChainTradeTransaction/ApplicableHeaderTradeSettlement/ApplicableTradeTax/CalculatedAmount").text if xml_tree.find(
    #     "./SupplyChainTradeTransaction/ApplicableHeaderTradeSettlement/ApplicableTradeTax/CalculatedAmount") is not None else None
    # xml_invoice_data.tax_rate1 = xml_tree.find(
    #     "./SupplyChainTradeTransaction/ApplicableHeaderTradeSettlement/ApplicableTradeTax/RateApplicablePercent").text if xml_tree.find(
    #     "./SupplyChainTradeTransaction/ApplicableHeaderTradeSettlement/ApplicableTradeTax/RateApplicablePercent") is not None else None

    # TODO need? another function
    # try:
    #     print("LEN ", len(xml_invoice_head_tax))
    #     # if we have many tax_rate,and tax_amount
    #     if len(xml_invoice_head_tax) > 1:
    #         count = 1
    #         for line in xml_invoice_head_tax:
    #             print("count am anfang", count)
    #             print("line", line)
    #             if count == 1:
    #                 xml_invoice_data.tax_amount1 = line.find("./CalculatedAmount").text if line.find("./CalculatedAmount") is not None else None
    #                 xml_invoice_data.tax_rate1 = line.find("./RateApplicablePercent").text if line.find("./RateApplicablePercent") is not None else None
    #                 print("xml_invoice_data.tax_amount1 ", line.find("./CalculatedAmount"))
    #                 print("xml_invoice_data.tax_rate1 ", line.find("./RateApplicablePercent"))
    #                 count += 1
    #                 continue
    #             if count == 2:
    #                 xml_invoice_data.tax_amount2 = line.find("./CalculatedAmount").text if line.find("./CalculatedAmount") is not None else None
    #                 xml_invoice_data.tax_rate2 = line.find("./RateApplicablePercent").text if line.find("./RateApplicablePercent") is not None else None
    #                 count += 1
    #                 continue
    #     # if only 1 taxrate
    #     else:
    #         print("DA??")
    #         xml_invoice_data.tax_rate1 = xml_invoice_head_tax.find("./CalculatedAmount").text if xml_invoice_head_tax.find("./CalculatedAmount") is not None else None
    #         xml_invoice_data.tax_amount1 = xml_invoice_head_tax.find("./RateApplicablePercent").text if xml_invoice_head_tax.find("./RateApplicablePercent") is not None else None
    # except Exception as e:
    #     print(f"Can not find tax_rate1 and tax_amount1 {e}")
    #     logger.error_log(f"Can not find tax_rate1 and tax_amount1 {e}")
    #     # xml_invoice_data.tax_rate1 = 19

    # positions
    item_position = 1
    for position in xml_positions_data.iter("IncludedSupplyChainTradeLineItem"):
        # print("######### position", position)
        try:
            description_text = re.sub(r'[\t\n]', ' ', position.find("SpecifiedTradeProduct/Description").text.strip())[
                               0:499]
            # print("description_text", description_text)
        except Exception as e:
            # logger.error_log(f"Mistake with description_text {e}")
            description_text = "Default text"

        tax_rate = position.find(
            "SpecifiedLineTradeSettlement/ApplicableTradeTax/RateApplicablePercent").text.strip()
        # print("tax_rate ", tax_rate)
        if position.find("SpecifiedLineTradeDelivery/BilledQuantity") is None:
            quantity = 1
        else:
            quantity = position.find("SpecifiedLineTradeDelivery/BilledQuantity").text.strip()
        # print("quantity ", quantity)
        single_net_price = position.find(
            "SpecifiedLineTradeAgreement/NetPriceProductTradePrice/ChargeAmount").text.strip()
        # print("single_net_price ", single_net_price)
        total_net_price = position.find(
            "SpecifiedLineTradeSettlement/SpecifiedTradeSettlementLineMonetarySummation/LineTotalAmount").text.strip()
        # print("total_net_price ", total_net_price)
        article_number = ""
        try:
            if re.findall("OE\s*\w{9,}", description_text):
                article_number = re.findall("OE\s*\w{9,}", description_text)[0].replace("OE", "").replace(" ", "")
        except Exception as e:
            print(f"Mistake with article number {e}")
            # logger.error_log(f"Mistake with positions {e}")

        m_cn_position_id = get_next_seq_val("M_IP_INVOICE_POS_SEQ")
        xml_invoice_data.add_position(
            XmlInvoicePosition(item_pos=item_position, position_text=description_text, quantity=quantity,
                               single_net_price=single_net_price, tax_rate=tax_rate,
                               total_net_price=total_net_price, invoice_id=xml_invoice_data.m_cn_id,
                               m_cn_id=m_cn_position_id, article_number=article_number))
        item_position += 1

    xml_invoice_data.correct_data()
    # logger.info_log(f"end script zugpferd_extraction")

    return xml_invoice_data, clients_data
