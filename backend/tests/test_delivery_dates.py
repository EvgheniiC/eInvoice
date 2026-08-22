"""BT-72 / BT-73 / BT-74 extraction for UBL (XRechnung) and CII (ZUGFeRD)."""

from __future__ import annotations

import unittest
from datetime import datetime
from typing import Optional
from unittest.mock import Mock

from app.data_class.XmlInvoiceHeader import XmlInvoiceHeader
from app.invoice_handler.xml_parser_header import get_xml_header, resolve_delivery_dates

ISSUE: datetime = datetime(2025, 1, 31)
DELIVERY: datetime = datetime(2025, 1, 7)
PERIOD_START: datetime = datetime(2025, 1, 1)
PERIOD_END: datetime = datetime(2025, 1, 31)

CII_NS: str = """xmlns:rsm="urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100"
 xmlns:ram="urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100"
 xmlns:udt="urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100" """

UBL_NS: str = """xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
 xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
 xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2" """


def _cii_date(value: str) -> str:
    return f'<udt:DateTimeString format="102">{value}</udt:DateTimeString>'


def _cii_invoice(
    *,
    period_start: Optional[str] = None,
    period_end: Optional[str] = None,
    actual_delivery: Optional[str] = None,
    issue_date: str = "20250131",
) -> str:
    period_xml: str = ""
    if period_start or period_end:
        start_xml: str = (
            f"<ram:StartDateTime>{_cii_date(period_start)}</ram:StartDateTime>"
            if period_start
            else ""
        )
        end_xml: str = (
            f"<ram:EndDateTime>{_cii_date(period_end)}</ram:EndDateTime>"
            if period_end
            else ""
        )
        period_xml = (
            f"<ram:BillingSpecifiedPeriod>{start_xml}{end_xml}</ram:BillingSpecifiedPeriod>"
        )

    delivery_xml: str = ""
    if actual_delivery:
        delivery_xml = (
            "<ram:ApplicableHeaderTradeDelivery>"
            "<ram:ActualDeliverySupplyChainEvent>"
            f"<ram:OccurrenceDateTime>{_cii_date(actual_delivery)}</ram:OccurrenceDateTime>"
            "</ram:ActualDeliverySupplyChainEvent>"
            "</ram:ApplicableHeaderTradeDelivery>"
        )

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rsm:CrossIndustryInvoice {CII_NS}>
  <rsm:ExchangedDocument>
    <ram:ID>CII-DATES-1</ram:ID>
    <ram:TypeCode>380</ram:TypeCode>
    <ram:IssueDateTime>{_cii_date(issue_date)}</ram:IssueDateTime>
  </rsm:ExchangedDocument>
  <rsm:SupplyChainTradeTransaction>
    {delivery_xml}
    <ram:ApplicableHeaderTradeSettlement>
      <ram:InvoiceCurrencyCode>EUR</ram:InvoiceCurrencyCode>
      {period_xml}
    </ram:ApplicableHeaderTradeSettlement>
  </rsm:SupplyChainTradeTransaction>
</rsm:CrossIndustryInvoice>
"""


def _ubl_invoice(
    *,
    period_start: Optional[str] = None,
    period_end: Optional[str] = None,
    actual_delivery: Optional[str] = None,
    issue_date: str = "2025-01-31",
) -> str:
    period_xml: str = ""
    if period_start or period_end:
        start_xml: str = f"<cbc:StartDate>{period_start}</cbc:StartDate>" if period_start else ""
        end_xml: str = f"<cbc:EndDate>{period_end}</cbc:EndDate>" if period_end else ""
        period_xml = f"<cac:InvoicePeriod>{start_xml}{end_xml}</cac:InvoicePeriod>"

    delivery_xml: str = ""
    if actual_delivery:
        delivery_xml = (
            "<cac:Delivery>"
            f"<cbc:ActualDeliveryDate>{actual_delivery}</cbc:ActualDeliveryDate>"
            "</cac:Delivery>"
        )

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Invoice {UBL_NS}>
  <cbc:ID>UBL-DATES-1</cbc:ID>
  <cbc:IssueDate>{issue_date}</cbc:IssueDate>
  <cbc:InvoiceTypeCode>380</cbc:InvoiceTypeCode>
  <cbc:DocumentCurrencyCode>EUR</cbc:DocumentCurrencyCode>
  {period_xml}
  <cac:AccountingSupplierParty><cac:Party><cac:PartyLegalEntity>
    <cbc:RegistrationName>Demo Supplier GmbH</cbc:RegistrationName>
  </cac:PartyLegalEntity></cac:Party></cac:AccountingSupplierParty>
  {delivery_xml}
</Invoice>
"""


def _parse(xml_text: str) -> XmlInvoiceHeader:
    header: XmlInvoiceHeader = XmlInvoiceHeader(invoice_id="dates-1")
    return get_xml_header(xml_text=xml_text, xml_invoice_data=header, logger=Mock())


class TestResolveDeliveryDatesPriority(unittest.TestCase):
    def test_period_both_sides_wins_over_actual_delivery(self) -> None:
        start: Optional[datetime]
        end: Optional[datetime]
        start, end = resolve_delivery_dates(
            period_start=PERIOD_START,
            period_end=PERIOD_END,
            actual_delivery=DELIVERY,
            invoice_date=ISSUE,
        )
        self.assertEqual(start, PERIOD_START)
        self.assertEqual(end, PERIOD_END)

    def test_actual_delivery_wins_over_invoice_date(self) -> None:
        start: Optional[datetime]
        end: Optional[datetime]
        start, end = resolve_delivery_dates(
            period_start=None,
            period_end=None,
            actual_delivery=DELIVERY,
            invoice_date=ISSUE,
        )
        self.assertEqual(start, DELIVERY)
        self.assertEqual(end, DELIVERY)

    def test_incomplete_period_falls_through_to_actual_delivery(self) -> None:
        start: Optional[datetime]
        end: Optional[datetime]
        start, end = resolve_delivery_dates(
            period_start=PERIOD_START,
            period_end=None,
            actual_delivery=DELIVERY,
            invoice_date=ISSUE,
        )
        self.assertEqual(start, DELIVERY)
        self.assertEqual(end, DELIVERY)

    def test_fallback_to_invoice_date(self) -> None:
        start: Optional[datetime]
        end: Optional[datetime]
        start, end = resolve_delivery_dates(
            period_start=None,
            period_end=None,
            actual_delivery=None,
            invoice_date=ISSUE,
        )
        self.assertEqual(start, ISSUE)
        self.assertEqual(end, ISSUE)


class TestCiiDeliveryDates(unittest.TestCase):
    def test_bt72_from_datetime_string(self) -> None:
        data: XmlInvoiceHeader = _parse(_cii_invoice(actual_delivery="20250107"))
        self.assertEqual(data.invoice_date, ISSUE)
        self.assertEqual(data.delivery_date, DELIVERY)
        self.assertEqual(data.delivery_date_till, DELIVERY)

    def test_bt73_bt74_from_datetime_string(self) -> None:
        data: XmlInvoiceHeader = _parse(
            _cii_invoice(period_start="20250101", period_end="20250131")
        )
        self.assertEqual(data.delivery_date, PERIOD_START)
        self.assertEqual(data.delivery_date_till, PERIOD_END)

    def test_period_wins_when_bt72_differs(self) -> None:
        data: XmlInvoiceHeader = _parse(
            _cii_invoice(
                period_start="20250101",
                period_end="20250131",
                actual_delivery="20250107",
            )
        )
        self.assertEqual(data.delivery_date, PERIOD_START)
        self.assertEqual(data.delivery_date_till, PERIOD_END)
        self.assertNotEqual(data.delivery_date, DELIVERY)

    def test_fallback_to_bt2_when_neither_period_nor_delivery(self) -> None:
        data: XmlInvoiceHeader = _parse(_cii_invoice())
        self.assertEqual(data.delivery_date, ISSUE)
        self.assertEqual(data.delivery_date_till, ISSUE)

    def test_occurrence_datetime_without_string_is_empty(self) -> None:
        xml_text: str = """<?xml version="1.0" encoding="UTF-8"?>
<rsm:CrossIndustryInvoice xmlns:rsm="urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100"
 xmlns:ram="urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100"
 xmlns:udt="urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100">
  <rsm:ExchangedDocument>
    <ram:ID>CII-EMPTY-DT</ram:ID>
    <ram:IssueDateTime><udt:DateTimeString format="102">20250131</udt:DateTimeString></ram:IssueDateTime>
  </rsm:ExchangedDocument>
  <rsm:SupplyChainTradeTransaction>
    <ram:ApplicableHeaderTradeDelivery>
      <ram:ActualDeliverySupplyChainEvent>
        <ram:OccurrenceDateTime/>
      </ram:ActualDeliverySupplyChainEvent>
    </ram:ApplicableHeaderTradeDelivery>
    <ram:ApplicableHeaderTradeSettlement>
      <ram:InvoiceCurrencyCode>EUR</ram:InvoiceCurrencyCode>
    </ram:ApplicableHeaderTradeSettlement>
  </rsm:SupplyChainTradeTransaction>
</rsm:CrossIndustryInvoice>
"""
        data: XmlInvoiceHeader = _parse(xml_text)
        self.assertEqual(data.delivery_date, ISSUE)
        self.assertEqual(data.delivery_date_till, ISSUE)


class TestUblDeliveryDates(unittest.TestCase):
    def test_bt72_actual_delivery_date(self) -> None:
        data: XmlInvoiceHeader = _parse(_ubl_invoice(actual_delivery="2025-01-07"))
        self.assertEqual(data.invoice_date, ISSUE)
        self.assertEqual(data.delivery_date, DELIVERY)
        self.assertEqual(data.delivery_date_till, DELIVERY)

    def test_bt73_bt74_invoice_period(self) -> None:
        data: XmlInvoiceHeader = _parse(
            _ubl_invoice(period_start="2025-01-01", period_end="2025-01-31")
        )
        self.assertEqual(data.delivery_date, PERIOD_START)
        self.assertEqual(data.delivery_date_till, PERIOD_END)

    def test_period_wins_when_bt72_differs(self) -> None:
        data: XmlInvoiceHeader = _parse(
            _ubl_invoice(
                period_start="2025-01-01",
                period_end="2025-01-31",
                actual_delivery="2025-01-07",
            )
        )
        self.assertEqual(data.delivery_date, PERIOD_START)
        self.assertEqual(data.delivery_date_till, PERIOD_END)
        self.assertNotEqual(data.delivery_date, DELIVERY)

    def test_fallback_to_bt2_when_neither_period_nor_delivery(self) -> None:
        data: XmlInvoiceHeader = _parse(_ubl_invoice())
        self.assertEqual(data.delivery_date, ISSUE)
        self.assertEqual(data.delivery_date_till, ISSUE)

    def test_period_and_delivery_are_siblings_not_nested(self) -> None:
        data: XmlInvoiceHeader = _parse(
            _ubl_invoice(
                period_start="2025-01-01",
                period_end="2025-01-31",
                actual_delivery="2025-01-07",
            )
        )
        self.assertEqual(data.delivery_date, PERIOD_START)
        self.assertEqual(data.delivery_date_till, PERIOD_END)


if __name__ == "__main__":
    unittest.main()
