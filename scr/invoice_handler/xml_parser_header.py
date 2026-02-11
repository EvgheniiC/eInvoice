from datetime import datetime
import re
from ..data_class import XmlInvoiceHeader
from ..helper_functions import find_data_within_element, find_data_with_regex, get_xml_tree, \
    find_data_within_element_with_len, get_tags_from_json, check_cost_center, find_tax_data, format_sixt_number, \
    get_field_value, string_to_float
from xml.etree.ElementTree import Element


# extract xml data from pdf file
# def zugpferd_extraction(m_cn_id: str, xml_text: str, db_helper, barcode: str):
def get_xml_header(xml_text: str, xml_invoice_data: XmlInvoiceHeader, logger) -> XmlInvoiceHeader:
    print("##### START get_xml_header")
    logger.info_log(f"START get_xml_header with m_cn_id = {xml_invoice_data.m_cn_id}")

    if not xml_invoice_data.barcode or not xml_invoice_data.m_cn_id or not xml_text:
        return xml_invoice_data

    xml_tree: Element = get_xml_tree(xml_text)

    xml_exchanged_document: Element = xml_tree.find("./ExchangedDocument")
    xml_invoice_head: Element = xml_tree.find("./SupplyChainTradeTransaction/ApplicableHeaderTradeSettlement")
    xml_invoice_head_money: Element = xml_tree.find(
        "./SupplyChainTradeTransaction/ApplicableHeaderTradeSettlement/SpecifiedTradeSettlementHeaderMonetarySummation")
    xml_supplier_data: Element = xml_tree.find("./SupplyChainTradeTransaction")
    xml_positions_data: Element = xml_tree.find("./SupplyChainTradeTransaction")

    # not zugpferd xml use another tags
    if not xml_invoice_head:
        xml_invoice_head: Element = xml_tree
        xml_positions_data: Element = xml_tree
        xml_supplier_data: Element = xml_tree
        xml_invoice_head_money: Element = xml_tree
        xml_exchanged_document: Element = xml_tree

    # header data
    tags_to_search_invoice_number: list = get_tags_from_json('tags_to_search_invoice_number')
    tags_to_search_order_id: list = get_tags_from_json('tags_to_search_order_id')
    tags_to_search_invoice_date: list = get_tags_from_json('tags_to_search_invoice_date')
    tags_to_search_delivery_date: list = get_tags_from_json('tags_to_search_delivery_date')
    tags_to_search_delivery_date_till: list = get_tags_from_json('tags_to_search_delivery_date_till')
    tags_to_search_currency: list = get_tags_from_json('tags_to_search_currency')
    tags_to_search_invoice_amount: list = get_tags_from_json('tags_to_search_invoice_amount')
    tags_to_search_total_amount: list = get_tags_from_json('tags_to_search_total_amount')
    tags_to_search_total_tax_amount: list = get_tags_from_json('tags_to_search_total_tax_amount')
    tags_to_search_supplier: list = get_tags_from_json('tags_to_search_supplier')
    tags_to_search_iban: list = get_tags_from_json('tags_to_search_iban')
    tags_to_search_tax_amount1: list = get_tags_from_json('tags_to_search_tax_amount1')
    tags_to_search_tax_rate1: list = get_tags_from_json('tags_to_search_tax_rate1')
    tags_to_search_kind_of_invoice: list = get_tags_from_json('tags_to_search_kind_of_invoice')
    tags_to_search_vin: list = get_tags_from_json('tags_to_search_vin')
    tags_to_search_cost_center: list = get_tags_from_json('tags_to_search_cost_center')
    tags_to_search_client_vat_id: list = get_tags_from_json('tags_to_search_client_vat_id')
    tags_to_search_discount: list = get_tags_from_json('tags_to_search_discount')

    xml_invoice_data.invoice_number = find_data_within_element(xml_exchanged_document, tags_to_search_invoice_number)

    try:
        xml_invoice_data.invoice_date = datetime.strptime(
            find_data_within_element(xml_exchanged_document, tags_to_search_invoice_date), '%Y%m%d')
    except Exception:
        try:
            xml_invoice_data.invoice_date = datetime.strptime(
                find_data_within_element(xml_exchanged_document, tags_to_search_invoice_date), '%Y-%m-%d')
        except Exception as e:
            print(f"Invoice date Date was not found {e}")
            logger.error_log(f"Invoice date bis was not found {e}")

    try:
        xml_invoice_data.delivery_date = datetime.strptime(
            find_data_within_element(xml_invoice_head, tags_to_search_delivery_date), '%Y%m%d')
    except Exception as e:
        try:
            xml_invoice_data.delivery_date = datetime.strptime(
                find_data_within_element(xml_invoice_head, tags_to_search_delivery_date), '%Y-%m-%d')
        except Exception as e:
            print(f"Delivery date was not found {e}")
            logger.error_log(f"Delivery date was not found {e}")

    try:
        xml_invoice_data.delivery_date_till = datetime.strptime(
            find_data_within_element(xml_invoice_head, tags_to_search_delivery_date_till), '%Y%m%d')
    except Exception:
        try:
            xml_invoice_data.delivery_date_till = datetime.strptime(
                find_data_within_element(xml_invoice_head, tags_to_search_delivery_date_till), '%Y-%m-%d')
        except Exception as e:
            print(f"delivery_date_till bis was not found {e}")
            logger.error_log(f"delivery_date_till bis was not found {e}")

    xml_invoice_data.currency = find_data_within_element(xml_invoice_head,
                                                         tags_to_search_currency) if not find_data_within_element(
        xml_invoice_head, tags_to_search_currency) else "EUR"

    xml_invoice_data.order_id = find_data_with_regex(xml_supplier_data, "930\d{7}|960\d{7}|SIXT-\d{7,}")
    # HW-5852
    if not xml_invoice_data.order_id:
        coupa_number: str = find_data_within_element(xml_tree, tags_to_search_order_id)
        xml_invoice_data.order_id = format_sixt_number(coupa_number)

    xml_invoice_data.contract_id = find_data_with_regex(xml_supplier_data, r"\bSX-\d{5}(?:-\d{3})?\b")

    # SWFM-5293
    if not xml_invoice_data.order_id:
        # sometimes we get order in positions
        logger.info_log(f"Order id was not founded, will find in positions")
        xml_invoice_data.order_id = find_data_with_regex(xml_positions_data, "930\d{7}|960\d{7}|SIXT-\d{7,}")

    if not xml_invoice_data.order_id:
        text_order_id = find_data_within_element(xml_exchanged_document, tags_to_search_order_id)
        if text_order_id:
            try:
                xml_invoice_data.order_id = re.findall("930\d{7}|960\d{7}|SIXT-\d{7,}", text_order_id)[0]
            except Exception as e:
                print(f"Order was not found {e}")
                logger.error_log(f"Order bis was not found {e}")

    xml_invoice_data.invoice_amount = find_data_within_element(xml_invoice_head_money,
                                                               tags_to_search_invoice_amount)

    # HW-5945 xml_invoice_data.invoice_amount = xml_invoice_data.invoice_amount - discount
    discount:float = string_to_float(find_data_within_element(xml_invoice_head_money, tags_to_search_discount))
    if discount:
        xml_invoice_data.invoice_amount = str(round(string_to_float(xml_invoice_data.invoice_amount) - discount, 2))

    xml_invoice_data.total_amount = find_data_within_element(xml_invoice_head_money, tags_to_search_total_amount)
    xml_invoice_data.total_tax_amount = find_data_within_element(xml_invoice_head_money,
                                                                 tags_to_search_total_tax_amount)
    tax_amount: dict = find_tax_data(xml_tree, tags_to_search_tax_amount1, "tax_amount")
    xml_invoice_data.tax_amount1 = tax_amount["tax_amount1"]
    xml_invoice_data.tax_amount2 = tax_amount["tax_amount2"]
    xml_invoice_data.tax_amount3 = tax_amount["tax_amount3"]
    xml_invoice_data.tax_amount4 = tax_amount["tax_amount4"]
    xml_invoice_data.tax_amount5 = tax_amount["tax_amount5"]

    tax_rate: dict = find_tax_data(xml_tree, tags_to_search_tax_rate1, "tax_rate")
    xml_invoice_data.tax_rate1 = tax_rate["tax_rate1"]
    xml_invoice_data.tax_rate2 = tax_rate["tax_rate2"]
    xml_invoice_data.tax_rate3 = tax_rate["tax_rate3"]
    xml_invoice_data.tax_rate4 = tax_rate["tax_rate4"]
    xml_invoice_data.tax_rate5 = tax_rate["tax_rate5"]

    xml_invoice_data.supplier = find_data_within_element(xml_supplier_data, tags_to_search_supplier)
    # for BE
    if not xml_invoice_data.supplier:
        xml_invoice_data.supplier = find_data_within_element(xml_supplier_data, tags_to_search_supplier)

    xml_invoice_data.sixt_vat_id = find_data_within_element(xml_supplier_data, tags_to_search_client_vat_id)
    xml_invoice_data.image_path = xml_invoice_data.barcode + ".pdf"
    xml_invoice_data.vin = find_data_within_element(xml_tree, tags_to_search_vin)
    # Vin number should be = 17
    if xml_invoice_data.vin and len(xml_invoice_data.vin) != 17:
        xml_invoice_data.vin = None
    xml_invoice_data.iban = find_data_within_element_with_len(xml_supplier_data, tags_to_search_iban, 22).replace(
        " ",
        "") if find_data_within_element_with_len(xml_supplier_data, tags_to_search_iban, 22) else None

    if xml_invoice_data.iban:
        logger.info_log(f"IBAN was founded = {xml_invoice_data.iban}")
        if len(xml_invoice_data.iban) < 22:
            xml_invoice_data.iban = find_data_within_element(xml_supplier_data, tags_to_search_iban)

    # sometimes len(IBAN) = 16(for client 35)
    if not xml_invoice_data.iban:
        xml_invoice_data.iban = find_data_within_element_with_len(xml_supplier_data, tags_to_search_iban, 16).replace(
            " ",
            "") if find_data_within_element_with_len(xml_supplier_data, tags_to_search_iban, 16) else None

    # 380 → "RE" (invoice)
    # 381 → "GU" (credit note)
    # 384 → "RE" (corrected invoice, still invoice)
    xml_invoice_data.kind_of_invoice = "RE" if find_data_within_element(xml_exchanged_document,
                                                                        tags_to_search_kind_of_invoice) == '380' else "GU"
    xml_invoice_data.cost_center = check_cost_center(find_data_within_element(xml_exchanged_document,
                                                                              tags_to_search_cost_center))

    # HW-5851
    if not xml_invoice_data.cost_center:
        xml_invoice_data.cost_center = check_cost_center(get_field_value(xml_tree, 'cost_center'))

    xml_invoice_data.client = get_field_value(xml_tree, 'legal_entity')
    # some clients send 035 or 001
    if xml_invoice_data.client:
        xml_invoice_data.client = xml_invoice_data.client.lstrip('0')

    xml_invoice_data.correct_data()

    logger.info_log(f"Finish get_xml_header with m_cn_id = {xml_invoice_data.m_cn_id}")

    return xml_invoice_data
