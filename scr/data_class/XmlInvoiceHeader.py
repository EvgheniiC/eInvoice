from dataclasses import dataclass
from datetime import datetime

import sys

sys.path.append('../..')
from scr.data_class.XmlInvoicePosition import XmlInvoicePosition
import re


@dataclass
class XmlInvoiceHeader:
    """
    Represents the header of an XML invoice, encapsulating all relevant metadata and
    attributes necessary for invoice processing.

    This class models the header information of an invoice typically captured
    within an XML structure for digital invoice processing. It provides attributes
    for invoice metadata, supplier and client details, associated financial
    information, dates, and related identifiers. Additionally, it supports
    property-based access control for critical fields to ensure consistent data
    updates.

    Attributes:
        m_cn_id: The unique ID for the invoice header.
        receipt_date: The date when the invoice was received.
        scan_location: The location where the invoice scan is stored. Default is "E-Mail".
        image_path: The file path of the invoice image.
        barcode: A barcode identifier for the invoice.
        mail_subject: The subject line of the email containing the invoice.
        source: The origin system for the invoice data. Default is "eInvoice".
        highway_timestamp: Timestamp for highway-related processing.
        invoice_type: The type of invoice. Default is "EKS".
        supplier: The supplier associated with the invoice.
        client: The client associated with the invoice.
        contract_id: The contract identifier linked to the invoice.
        order_id: The order identifier linked to the invoice.
        iban: The International Bank Account Number related to the invoice.
        kind_of_invoice: The type or category of invoice.
        invoice_number: The unique invoice number.
        invoice_date: The date of the invoice.
        delivery_date: The specified delivery date associated with the invoice.
        cost_center: Cost center information for accounting purposes.
        damage_number: A damage reference number if applicable.
        delivery_date_till: The end date for the delivery period.
        invoice_amount: The total amount of the invoice before taxes.
        total_amount: The final total amount including taxes.
        total_tax_amount: The cumulative tax amount applied to the invoice.
        tax_rate1: The first applicable tax rate.
        tax_amount1: The tax amount for the first tax rate.
        tax_rate2: The second applicable tax rate.
        tax_amount2: The tax amount for the second tax rate.
        tax_rate3: The third applicable tax rate.
        tax_amount3: The tax amount for the third tax rate.
        tax_rate4: The fourth applicable tax rate.
        tax_amount4: The tax amount for the fourth tax rate.
        tax_rate5: The fifth applicable tax rate.
        tax_amount5: The tax amount for the fifth tax rate.
        currency: The currency in which the invoice is issued.
        vin: The Vehicle Identification Number if applicable.
        receiver: The receiver of the invoice.
        contract_start: The start date of the associated contract.
        contract_end: The end date of the associated contract.
        trigger_highway: A flag to indicate highway-related processing triggers. Default is "0".
    """

    def __init__(self,
                 m_cn_id: str = None,
                 receipt_date: datetime = None,
                 scan_location: str = 'E-Mail',
                 image_path: str = None,
                 barcode: str = None,
                 mail_subject: str = None,
                 source: str = 'eInvoice',
                 highway_timestamp: datetime = None,
                 invoice_type: str = "EKS",
                 supplier: str = None,
                 client: str = None,
                 contract_id: str = None,
                 order_id: str = None,
                 iban: str = None,
                 kind_of_invoice: str = None,
                 invoice_number: str = None,
                 invoice_date: datetime = None,
                 delivery_date: datetime = None,
                 cost_center: str = None,
                 damage_number: str = None,
                 delivery_date_till: datetime = None,
                 invoice_amount: float = None,
                 total_amount: float = None,
                 total_tax_amount: float = None,
                 tax_rate1: float = None,
                 tax_amount1: float = None,
                 tax_rate2: float = None,
                 tax_amount2: float = None,
                 tax_rate3: float = None,
                 tax_amount3: float = None,
                 tax_rate4: float = None,
                 tax_amount4: float = None,
                 tax_rate5: float = None,
                 tax_amount5: float = None,
                 currency: str = None,
                 vin: str = None,
                 receiver: str = None,
                 contract_start: datetime = None,
                 contract_end: datetime = None,
                 trigger_highway: str = "0",
                 m_cn_mail_id=None,
                 email_name=None
                 ):

        self.m_cn_id = m_cn_id
        self.receipt_date = receipt_date
        self.scan_location = scan_location
        self.image_path = image_path
        self.barcode = barcode
        self.mail_subject = mail_subject
        self.source = source
        self.highway_timestamp = highway_timestamp
        self.invoice_type = invoice_type
        self.supplier = supplier
        self.client = client
        self.contract_id = contract_id
        self.order_id = order_id
        self.iban = iban
        self.kind_of_invoice = kind_of_invoice
        self.invoice_number = invoice_number
        self.invoice_date = invoice_date
        self.cost_center = cost_center
        self.damage_number = damage_number
        self.delivery_date = delivery_date
        self.delivery_date_till = delivery_date_till
        self.invoice_amount = invoice_amount
        self.total_amount = total_amount
        self.total_tax_amount = total_tax_amount
        self.tax_rate1 = tax_rate1
        self.tax_amount1 = tax_amount1
        self.tax_rate2 = tax_rate2
        self.tax_amount2 = tax_amount2
        self.tax_rate3 = tax_rate3
        self.tax_amount3 = tax_amount3
        self.tax_rate4 = tax_rate4
        self.tax_amount4 = tax_amount4
        self.tax_rate5 = tax_rate5
        self.tax_amount5 = tax_amount5
        self.currency = currency
        self.vin = vin
        self.receiver = receiver
        self.contract_start = contract_start
        self.contract_end = contract_end
        self.trigger_highway = trigger_highway
        self.m_cn_mail_id = m_cn_mail_id
        self.email_name = email_name
        self.__table = "CHRONOS_EINVOICE_HEADER"
        self.__table_pos = "CHRONOS_EINVOICE_POSITOINS"
        self.__positions = []

    def get_xml_header_attributes(self):
        return {"M_CN_ID": self.m_cn_id,
                "M_IV_BARCODE": self.barcode,
                "M_IV_RECEIPTDATE": self.receipt_date,
                "M_IV_SCANLOCATION": self.scan_location,
                "M_IV_IMAGEPATH": self.image_path,
                "M_IV_QUELLSYSTEM": self.source,
                "M_IV_MAIL_SUBJECT": self.mail_subject,
                "HIGHWAY_ZEITSTEMPEL": self.highway_timestamp,
                "M_IV_INVOICETYPE": self.invoice_type,
                "M_IV_KREDITOR": self.supplier,
                "M_IV_MANDANT": self.client,
                "M_IV_CONTRACTID": self.contract_id,
                "M_IV_ORDERID": self.order_id,
                "M_IV_IBAN": self.iban,
                "M_IV_KINDOFINVOICE": self.kind_of_invoice,
                "M_IV_INVOICENUMBER": self.invoice_number,
                "M_IV_COSTCENTER": self.cost_center,
                "M_IV_DAMAGENUMBER": self.damage_number,
                "M_IV_INVOICEDATE": self.invoice_date,
                "M_IV_DELIVERYDATE": self.delivery_date,
                "M_IV_DELIVERYDATE_BIS": self.delivery_date_till,
                "M_IV_INVOICEAMOUNT": self.invoice_amount,
                "M_IV_TOTALAMOUNT": self.total_amount,
                "M_IV_TOTALTAXAMOUNT": self.total_tax_amount,
                "M_IV_TAXRATE1": self.tax_rate1, "M_IV_TAXAMOUNT1": self.tax_amount1,
                "M_IV_TAXRATE2": self.tax_rate2, "M_IV_TAXAMOUNT2": self.tax_amount2,
                "M_IV_TAXRATE3": self.tax_rate3, "M_IV_TAXAMOUNT3": self.tax_amount3,
                "M_IV_TAXRATE4": self.tax_rate4, "M_IV_TAXAMOUNT4": self.tax_amount4,
                "M_IV_TAXRATE5": self.tax_rate5, "M_IV_TAXAMOUNT5": self.tax_amount5,
                "M_IV_CURRENCY": self.currency,
                "M_IV_VIN": self.vin,
                "M_IV_EMPFAENGER": self.receiver,
                "M_IV_CONTRACT_START": self.contract_start,
                "M_IV_CONTRACT_END": self.contract_end,
                "TRIGGER_HIGHWAY": self.trigger_highway,
                "M_CN_MAIL_ID": self.m_cn_mail_id,
                "EMAIL_NAME": self.email_name,
                }


    def get_xml_header_attributes_for_hw(self):
        return {"M_IV_ID": self.m_cn_id,
                "M_IV_BARCODE": self.barcode,
                "M_IV_RECEIPTDATE": self.receipt_date,
                "M_IV_SCANLOCATION": self.scan_location,
                "M_IV_IMAGEPATH": self.image_path,
                "M_IV_QUELLSYSTEM": self.source,
                "M_IV_MAIL_SUBJECT": self.mail_subject,
                "M_IV_INVOICETYPE": self.invoice_type,
                "M_IV_KREDITOR": self.supplier,
                "M_IV_MANDANT": self.client,
                "M_IV_CONTRACTID": self.contract_id,
                "M_IV_ORDERID": self.order_id,
                "M_IV_IBAN": self.iban,
                "M_IV_KINDOFINVOICE": self.kind_of_invoice,
                "M_IV_INVOICENUMBER": self.invoice_number,
                "M_IV_COSTCENTER": self.cost_center,
                "M_IV_DAMAGENUMBER": self.damage_number,
                "M_IV_INVOICEDATE": self.invoice_date,
                "M_IV_DELIVERYDATE": self.delivery_date,
                "M_IV_DELIVERYDATE_BIS": self.delivery_date_till,
                "M_IV_INVOICEAMOUNT": self.invoice_amount,
                "M_IV_TOTALAMOUNT": self.total_amount,
                "M_IV_TOTALTAXAMOUNT": self.total_tax_amount,
                "M_IV_TAXRATE1": self.tax_rate1, "M_IV_TAXAMOUNT1": self.tax_amount1,
                "M_IV_TAXRATE2": self.tax_rate2, "M_IV_TAXAMOUNT2": self.tax_amount2,
                "M_IV_TAXRATE3": self.tax_rate3, "M_IV_TAXAMOUNT3": self.tax_amount3,
                "M_IV_TAXRATE4": self.tax_rate4, "M_IV_TAXAMOUNT4": self.tax_amount4,
                "M_IV_TAXRATE5": self.tax_rate5, "M_IV_TAXAMOUNT5": self.tax_amount5,
                "M_IV_CURRENCY": self.currency,
                "M_IV_VIN": self.vin,
                "M_IV_EMPFAENGER": self.receiver,
                "M_IV_CONTRACT_START": self.contract_start,
                "M_IV_CONTRACT_END": self.contract_end,
                }

    @property
    def m_cn_mail_id(self):
        return self.__m_cn_mail_id

    @m_cn_mail_id.setter
    def m_cn_mail_id(self, value: str):
        self.__m_cn_mail_id = value

    @property
    def email_name(self):
        return self.__email_name

    @email_name.setter
    def email_name(self, value: str):
        self.__email_name = value

    @property
    def invoice_type(self):
        return self.__invoice_type

    @invoice_type.setter
    def invoice_type(self, value: str):
        self.__invoice_type = value

    @property
    def supplier(self):
        return self.__supplier

    @supplier.setter
    def supplier(self, value: str):
        self.__supplier = value

    @property
    def client(self):
        return self.__client

    @client.setter
    def client(self, value: str):
        self.__client = value

    @property
    def contract_id(self):
        return self.__contract_id

    @contract_id.setter
    def contract_id(self, value: str):
        self.__contract_id = value

    @property
    def order_id(self):
        return self.__order_id

    @order_id.setter
    def order_id(self, value: str):
        self.__order_id = value

    @property
    def iban(self):
        return self.__iban

    @iban.setter
    def iban(self, value: str):
        self.__iban = value

    @property
    def kind_of_invoice(self):
        return self.__kind_of_invoice

    @kind_of_invoice.setter
    def kind_of_invoice(self, value: str):
        self.__kind_of_invoice = value

    @property
    def invoice_number(self):
        return self.__invoice_number

    @invoice_number.setter
    def invoice_number(self, value: str):
        self.__invoice_number = value

    @property
    def invoice_date(self):
        return self.__invoice_date

    @invoice_date.setter
    def invoice_date(self, value: str):
        self.__invoice_date = value

    @property
    def cost_center(self):
        return self.__cost_center

    @cost_center.setter
    def cost_center(self, value: str):
        self.__cost_center = value

    @property
    def damage_number(self):
        return self.__damage_number

    @damage_number.setter
    def damage_number(self, value: str):
        self.__damage_number = value

    @property
    def delivery_date_till(self):
        return self.__delivery_date_till

    @delivery_date_till.setter
    def delivery_date_till(self, value: str):
        self.__delivery_date_till = value

    @property
    def invoice_amount(self):
        return self.__invoice_amount

    @invoice_amount.setter
    def invoice_amount(self, value: str):
        self.__invoice_amount = value

    @property
    def total_amount(self):
        return self.__total_amount

    @total_amount.setter
    def total_amount(self, value: str):
        self.__total_amount = value

    @property
    def total_tax_amount(self):
        return self.__total_tax_amount

    @total_tax_amount.setter
    def total_tax_amount(self, value: str):
        self.__total_tax_amount = value

    @property
    def tax_rate1(self):
        return self.__tax_rate1

    @tax_rate1.setter
    def tax_rate1(self, value: str):
        self.__tax_rate1 = value

    @property
    def tax_rate2(self):
        return self.__tax_rate2

    @tax_rate2.setter
    def tax_rate2(self, value: str):
        self.__tax_rate2 = value

    @property
    def tax_rate3(self):
        return self.__tax_rate3

    @tax_rate3.setter
    def tax_rate3(self, value: str):
        self.__tax_rate3 = value

    @property
    def tax_rate4(self):
        return self.__tax_rate4

    @tax_rate4.setter
    def tax_rate4(self, value: str):
        self.__tax_rate4 = value

    @property
    def tax_rate5(self):
        return self.__tax_rate5

    @tax_rate5.setter
    def tax_rate5(self, value: str):
        self.__tax_rate5 = value

    @property
    def tax_amount1(self):
        return self.__tax_amount1

    @tax_amount1.setter
    def tax_amount1(self, value: str):
        self.__tax_amount1 = value

    @property
    def tax_amount2(self):
        return self.__tax_amount2

    @tax_amount2.setter
    def tax_amount2(self, value: str):
        self.__tax_amount2 = value

    @property
    def tax_amount3(self):
        return self.__tax_amount3

    @tax_amount3.setter
    def tax_amount3(self, value: str):
        self.__tax_amount3 = value

    @property
    def tax_amount4(self):
        return self.__tax_amount4

    @tax_amount4.setter
    def tax_amount4(self, value: str):
        self.__tax_amount4 = value

    @property
    def tax_amount5(self):
        return self.__tax_amount5

    @tax_amount5.setter
    def tax_amount5(self, value: str):
        self.__tax_amount5 = value

    @property
    def currency(self):
        return self.__currency

    @currency.setter
    def currency(self, value: str):
        self.__currency = value

    @property
    def vin(self):
        return self.__vin

    @vin.setter
    def vin(self, value: str):
        self.__vin = value

    @property
    def receiver(self):
        return self.__receiver

    @receiver.setter
    def receiver(self, value: str):
        self.__receiver = value

    @property
    def contract_start(self):
        return self.__contract_start

    @contract_start.setter
    def contract_start(self, value: str):
        self.__contract_start = value

    @property
    def contract_end(self):
        return self.__contract_end

    @contract_end.setter
    def contract_end(self, value: str):
        self.__contract_end = value

    @property
    def trigger_highway(self):
        return self.__trigger_highway

    @trigger_highway.setter
    def trigger_highway(self, value: str):
        self.__trigger_highway = value

    @property
    def m_cn_id(self):
        return self.__m_cn_id

    @m_cn_id.setter
    def m_cn_id(self, value: str):
        self.__m_cn_id = value

    @property
    def barcode(self):
        return self.__barcode

    @barcode.setter
    def barcode(self, value: str):
        self.__barcode = value

    @property
    def receipt_date(self):
        return self.__receipt_date

    @receipt_date.setter
    def receipt_date(self, value: str):
        self.__receipt_date = value

    @property
    def scan_location(self):
        return self.__scan_location

    @scan_location.setter
    def scan_location(self, value: str):
        self.__scan_location = value

    @property
    def image_path(self):
        return self.__image_path

    @image_path.setter
    def image_path(self, value: str):
        self.__image_path = value

    @property
    def source(self):
        return self.__source

    @source.setter
    def source(self, value: str):
        self.__source = value

    @property
    def mail_subject(self):
        return self.__mail_subject

    @mail_subject.setter
    def mail_subject(self, value: str):
        self.__mail_subject = value

    @property
    def highway_timestamp(self):
        return self.__highway_timestamp

    @highway_timestamp.setter
    def highway_timestamp(self, value: str):
        self.__highway_timestamp = value

    def set_dates(self):
        """
        If only delivery date / date from found --> set the opposing date
        If no delivery date / date from found --> set it to invoicedate

        """
        if self.delivery_date and not self.delivery_date_till:
            self.delivery_date_till = self.delivery_date

        if self.delivery_date_till and not self.delivery_date:
            self.delivery_date = self.delivery_date_till

        if not self.delivery_date and self.delivery_date_till:
            self.delivery_date = self.invoice_date
            self.delivery_date_till = self.invoice_date

        if not self.delivery_date and not self.delivery_date_till:
            self.delivery_date = self.invoice_date
            self.delivery_date_till = self.invoice_date


    def normalize_invoice_number(self):
        """
        | The invoicenumber needs to be in lower cases and numbers/letters only,
        | so replace every non-Number / Character and remove leading zeros.

        """
        if self.invoice_number:
            # remove all non numerical / letters, remove all leading zeros
            self.invoice_number = re.sub("[^0-9a-z]", "", self.invoice_number.lower()).lstrip("0")

    def correct_data(self):
        """
        Run all the functions every script uses anyway, put together in a function.

        """
        self.set_dates()
        self.normalize_invoice_number()

    def add_position(self, position: XmlInvoicePosition):
        """
        Adds a new position to the position List

        :param position: Position
        :rtype: InvoicePosition
        """
        XmlInvoicePosition.m_cn_id = self.m_cn_id
        self.__positions.append(position)

    def get_xml_postions_map(self):
        """
        Return all positions in a List

        :return: List of positionsDict (i.e. [{M_IP_ID : 1 }, {M_IP_ID : 2}]
        :rtype: [InvoicePosition]
        """
        return [position.get_xml_positions_attributes() for position in self.__positions]

    def get_xml_postions_map_for_hw(self):
        """
        Return all positions in an List

        :return: List of positionsDict (i.e. [{M_IP_ID : 1 }, {M_IP_ID : 2}]
        :rtype: [InvoicePosition]
        """
        return [position.get_xml_positions_attributes_for_hw() for position in self.__positions]
