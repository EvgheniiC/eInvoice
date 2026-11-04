"""EN 16931 BG-21 document-level charges (CII SpecifiedTradeAllowanceCharge)."""

from __future__ import annotations

import unittest
from decimal import Decimal
from typing import List, NamedTuple, Optional, Tuple
from unittest.mock import Mock
from xml.etree.ElementTree import Element

from app.data_class.XmlInvoiceHeader import XmlInvoiceHeader
from app.helper_functions.description import (
    HeaderTradeAdjustment,
    get_document_level_charges,
    get_header_trade_allowance_discount,
    get_header_trade_charges,
)
from app.helper_functions.einvoice_helper import get_xml_tree, read_xml_file_to_str
from app.invoice_handler.xml_parser_header import get_xml_header
from app.invoice_handler.xml_parser_positions import get_xml_positions

CII_NS: str = """xmlns:rsm="urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100"
 xmlns:ram="urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100"
 xmlns:udt="urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100" """

SHIPPING_REASON: str = (
    "Sixt international: DHL 0-10 kg (Belgien, Niederlande, Luxemburg)"
)


def _cii_charge_xml(
    *,
    charge_indicator: str = "true",
    actual_amount: str = "14.89",
    reason: str = SHIPPING_REASON,
    category_code: str = "Z",
    tax_percent: str = "0.00",
    include_charge_total: bool = True,
) -> str:
    charge_total_xml: str = (
        f"<ram:ChargeTotalAmount>{actual_amount}</ram:ChargeTotalAmount>"
        if include_charge_total
        else ""
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rsm:CrossIndustryInvoice {CII_NS}>
  <rsm:ExchangedDocument>
    <ram:ID>44172613</ram:ID>
    <ram:TypeCode>380</ram:TypeCode>
    <ram:IssueDateTime>
      <udt:DateTimeString format="102">20250822</udt:DateTimeString>
    </ram:IssueDateTime>
  </rsm:ExchangedDocument>
  <rsm:SupplyChainTradeTransaction>
    <ram:IncludedSupplyChainTradeLineItem>
      <ram:SpecifiedTradeProduct>
        <ram:Name>Demo article</ram:Name>
      </ram:SpecifiedTradeProduct>
      <ram:SpecifiedLineTradeAgreement>
        <ram:NetPriceProductTradePrice>
          <ram:ChargeAmount>100.00</ram:ChargeAmount>
        </ram:NetPriceProductTradePrice>
      </ram:SpecifiedLineTradeAgreement>
      <ram:SpecifiedLineTradeDelivery>
        <ram:BilledQuantity unitCode="C62">1</ram:BilledQuantity>
      </ram:SpecifiedLineTradeDelivery>
      <ram:SpecifiedLineTradeSettlement>
        <ram:ApplicableTradeTax>
          <ram:RateApplicablePercent>19.00</ram:RateApplicablePercent>
        </ram:ApplicableTradeTax>
        <ram:SpecifiedTradeSettlementLineMonetarySummation>
          <ram:LineTotalAmount>100.00</ram:LineTotalAmount>
        </ram:SpecifiedTradeSettlementLineMonetarySummation>
      </ram:SpecifiedLineTradeSettlement>
    </ram:IncludedSupplyChainTradeLineItem>
    <ram:ApplicableHeaderTradeSettlement>
      <ram:InvoiceCurrencyCode>EUR</ram:InvoiceCurrencyCode>
      <ram:SpecifiedTradeAllowanceCharge>
        <ram:ChargeIndicator>
          <udt:Indicator>{charge_indicator}</udt:Indicator>
        </ram:ChargeIndicator>
        <ram:ActualAmount>{actual_amount}</ram:ActualAmount>
        <ram:Reason>{reason}</ram:Reason>
        <ram:CategoryTradeTax>
          <ram:TypeCode>VAT</ram:TypeCode>
          <ram:CategoryCode>{category_code}</ram:CategoryCode>
          <ram:RateApplicablePercent>{tax_percent}</ram:RateApplicablePercent>
        </ram:CategoryTradeTax>
      </ram:SpecifiedTradeAllowanceCharge>
      <ram:SpecifiedTradeSettlementHeaderMonetarySummation>
        <ram:LineTotalAmount>100.00</ram:LineTotalAmount>
        {charge_total_xml}
        <ram:TaxBasisTotalAmount>114.89</ram:TaxBasisTotalAmount>
        <ram:GrandTotalAmount>133.89</ram:GrandTotalAmount>
      </ram:SpecifiedTradeSettlementHeaderMonetarySummation>
    </ram:ApplicableHeaderTradeSettlement>
  </rsm:SupplyChainTradeTransaction>
</rsm:CrossIndustryInvoice>
"""


def _ubl_charge_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
 xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
 xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2">
  <cbc:ID>UBL-CHARGE-1</cbc:ID>
  <cbc:IssueDate>2025-08-22</cbc:IssueDate>
  <cbc:InvoiceTypeCode>380</cbc:InvoiceTypeCode>
  <cbc:DocumentCurrencyCode>EUR</cbc:DocumentCurrencyCode>
  <cac:AllowanceCharge>
    <cbc:ChargeIndicator>true</cbc:ChargeIndicator>
    <cbc:AllowanceChargeReason>Freight</cbc:AllowanceChargeReason>
    <cbc:Amount>12.50</cbc:Amount>
    <cac:TaxCategory>
      <cbc:ID>S</cbc:ID>
      <cbc:Percent>19.00</cbc:Percent>
    </cac:TaxCategory>
  </cac:AllowanceCharge>
  <cac:LegalMonetaryTotal>
    <cbc:LineExtensionAmount>100.00</cbc:LineExtensionAmount>
    <cbc:ChargeTotalAmount>12.50</cbc:ChargeTotalAmount>
    <cbc:TaxExclusiveAmount>112.50</cbc:TaxExclusiveAmount>
    <cbc:TaxInclusiveAmount>133.88</cbc:TaxInclusiveAmount>
  </cac:LegalMonetaryTotal>
</Invoice>
"""


def _parse(xml_text: str) -> XmlInvoiceHeader:
    header: XmlInvoiceHeader = XmlInvoiceHeader(invoice_id="charge-1")
    header = get_xml_header(xml_text=xml_text, xml_invoice_data=header, logger=Mock())
    return get_xml_positions(xml_text=xml_text, xml_invoice_data=header, logger=Mock())


class TestHeaderTradeCharges(unittest.TestCase):
    def test_cii_charge_extracts_amount_reason_and_tax(self) -> None:
        xml_tree: Element = get_xml_tree(_cii_charge_xml())
        charges: List[HeaderTradeAdjustment] = get_header_trade_charges(xml_tree)
        self.assertEqual(len(charges), 1)
        charge: HeaderTradeAdjustment = charges[0]
        self.assertEqual(charge.amount, Decimal("14.89"))
        self.assertEqual(charge.description, SHIPPING_REASON)
        self.assertEqual(charge.tax_rate, Decimal("0.00"))
        self.assertEqual(charge.tax_category, "Z")

    def test_cii_allowance_is_not_a_charge(self) -> None:
        xml_tree: Element = get_xml_tree(_cii_charge_xml(charge_indicator="false"))
        charges: List[HeaderTradeAdjustment] = get_header_trade_charges(xml_tree)
        self.assertEqual(charges, [])
        allowance: Optional[HeaderTradeAdjustment] = get_header_trade_allowance_discount(
            xml_tree
        )
        self.assertIsNotNone(allowance)
        assert allowance is not None
        self.assertEqual(allowance.amount, Decimal("14.89"))
        self.assertEqual(allowance.description, SHIPPING_REASON)

    def test_ubl_document_charge(self) -> None:
        xml_tree: Element = get_xml_tree(_ubl_charge_xml())
        charges: List[HeaderTradeAdjustment] = get_document_level_charges(xml_tree)
        self.assertEqual(len(charges), 1)
        self.assertEqual(charges[0].amount, Decimal("12.50"))
        self.assertEqual(charges[0].description, "Freight")
        self.assertEqual(charges[0].tax_rate, Decimal("19.00"))
        self.assertEqual(charges[0].tax_category, "S")

    def test_ubl_header_charge_needs_only_free_text_reason(self) -> None:
        xml_tree: Element = get_xml_tree(
            """<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
 xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
 xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2">
  <cbc:ID>1001113267</cbc:ID>
  <cbc:InvoiceTypeCode>380</cbc:InvoiceTypeCode>
  <cac:AllowanceCharge>
    <cbc:ChargeIndicator>false</cbc:ChargeIndicator>
    <cbc:AllowanceChargeReason>PC RT Remise Base</cbc:AllowanceChargeReason>
    <cbc:MultiplierFactorNumeric>19.00</cbc:MultiplierFactorNumeric>
    <cbc:Amount currencyID="EUR">28506.52</cbc:Amount>
    <cbc:BaseAmount currencyID="EUR">150034.33</cbc:BaseAmount>
    <cac:TaxCategory>
      <cbc:ID>S</cbc:ID>
      <cbc:Percent>20.00</cbc:Percent>
    </cac:TaxCategory>
  </cac:AllowanceCharge>
  <cac:AllowanceCharge>
    <cbc:ChargeIndicator>true</cbc:ChargeIndicator>
    <cbc:AllowanceChargeReason>Coût de Transport</cbc:AllowanceChargeReason>
    <cbc:Amount currencyID="EUR">125.00</cbc:Amount>
    <cac:TaxCategory>
      <cbc:ID>S</cbc:ID>
      <cbc:Percent>20.00</cbc:Percent>
    </cac:TaxCategory>
  </cac:AllowanceCharge>
</Invoice>
"""
        )
        charges: List[HeaderTradeAdjustment] = get_document_level_charges(xml_tree)
        self.assertEqual(len(charges), 1)
        self.assertEqual(charges[0].amount, Decimal("125.00"))
        self.assertEqual(charges[0].description, "Coût de Transport")
        self.assertEqual(charges[0].tax_rate, Decimal("20.00"))
        self.assertEqual(charges[0].tax_category, "S")
        allowance: Optional[HeaderTradeAdjustment] = get_header_trade_allowance_discount(
            xml_tree
        )
        self.assertIsNotNone(allowance)
        assert allowance is not None
        self.assertEqual(allowance.amount, Decimal("28506.52"))
        self.assertEqual(allowance.description, "PC RT Remise Base")
        self.assertEqual(allowance.tax_rate, Decimal("20.00"))
        self.assertEqual(allowance.tax_category, "S")


class TestDocumentChargePositions(unittest.TestCase):
    def test_cii_shipping_becomes_line_with_zero_vat(self) -> None:
        data: XmlInvoiceHeader = _parse(_cii_charge_xml())
        positions: List[dict] = data.get_positions_map()
        self.assertEqual(len(positions), 2)
        charge_line: dict = positions[1]
        self.assertEqual(charge_line["position_text"], SHIPPING_REASON)
        self.assertEqual(charge_line["total_net_price"], Decimal("14.89"))
        self.assertEqual(charge_line["tax_rate"], Decimal("0.00"))
        self.assertEqual(charge_line["tax_code"], "Z")
        self.assertEqual(data.charge_total, Decimal("14.89"))

    def test_charge_total_falls_back_to_actual_amount(self) -> None:
        data: XmlInvoiceHeader = _parse(_cii_charge_xml(include_charge_total=False))
        self.assertEqual(data.charge_total, Decimal("14.89"))
        charge_line: dict = data.get_positions_map()[1]
        self.assertEqual(charge_line["total_net_price"], Decimal("14.89"))
        self.assertEqual(charge_line["position_text"], SHIPPING_REASON)


class _HeaderChargeFixture(NamedTuple):
    relative_path: str
    invoice_number: str
    line_net: Decimal
    charge_amount: Decimal
    charge_reason: str
    invoice_total: Decimal


_BRAND: str = "S" + "ixt"
_ITALY_SHIPPING_REASON: str = (
    f"{_BRAND} international: DHL 0-10 kg (Osterreich, Frankreich, Monaco, Italien)"
)
_HEADER_CHARGE_FIXTURES: Tuple[_HeaderChargeFixture, ...] = (
    _HeaderChargeFixture(
        relative_path="xml_files/8765788_factur-x.xml",
        invoice_number="RE534870",
        line_net=Decimal("172.00"),
        charge_amount=Decimal("14.89"),
        charge_reason=SHIPPING_REASON,
        invoice_total=Decimal("186.89"),
    ),
    _HeaderChargeFixture(
        relative_path="xml_files/8765795_sap.xml",
        invoice_number="RE534872",
        line_net=Decimal("129.00"),
        charge_amount=Decimal("15.89"),
        charge_reason=_ITALY_SHIPPING_REASON,
        invoice_total=Decimal("144.89"),
    ),
)


class TestHeaderChargeFixtures(unittest.TestCase):
    def test_real_invoices_keep_header_shipping_charge(self) -> None:
        for fixture in _HEADER_CHARGE_FIXTURES:
            with self.subTest(fixture=fixture.relative_path):
                xml_text: Optional[str] = read_xml_file_to_str(fixture.relative_path)
                self.assertIsNotNone(xml_text)
                assert xml_text is not None
                data: XmlInvoiceHeader = _parse(xml_text)
                self.assertEqual(data.invoice_number, fixture.invoice_number)
                self.assertEqual(data.charge_total, fixture.charge_amount)
                self.assertEqual(data.invoice_amount, fixture.invoice_total)
                self.assertEqual(data.total_amount, fixture.invoice_total)
                positions: List[dict] = data.get_positions_map()
                self.assertEqual(len(positions), 2)
                self.assertEqual(positions[0]["total_net_price"], fixture.line_net)
                charge_line: dict = positions[1]
                self.assertEqual(charge_line["position_text"], fixture.charge_reason)
                self.assertEqual(charge_line["single_net_price"], fixture.charge_amount)
                self.assertEqual(charge_line["total_net_price"], fixture.charge_amount)
                self.assertEqual(charge_line["tax_rate"], Decimal("0.00"))
                self.assertEqual(charge_line["tax_code"], "Z")


class TestMercedesHeaderAdjustments(unittest.TestCase):
    def test_transport_charge_without_multiplier_is_a_position(self) -> None:
        fixture: str = "xml_files/9041269_sap.xml"
        xml_text: Optional[str] = read_xml_file_to_str(fixture)
        self.assertIsNotNone(xml_text)
        assert xml_text is not None
        data: XmlInvoiceHeader = _parse(xml_text)
        self.assertEqual(data.invoice_number, "1001113267")
        self.assertEqual(data.charge_total, Decimal("125.00"))
        self.assertEqual(data.discount, Decimal("28506.52"))
        self.assertEqual(data.invoice_amount, Decimal("121652.81"))
        self.assertEqual(data.total_amount, Decimal("145983.37"))

        positions: List[dict] = data.get_positions_map()
        charge_lines: List[dict] = [
            position
            for position in positions
            if position["position_text"] == "Coût de Transport"
        ]
        self.assertEqual(len(charge_lines), 1)
        charge_line: dict = charge_lines[0]
        self.assertEqual(charge_line["single_net_price"], Decimal("125.00"))
        self.assertEqual(charge_line["total_net_price"], Decimal("125.00"))
        self.assertEqual(charge_line["tax_rate"], Decimal("20.00"))
        self.assertEqual(charge_line["tax_code"], "S")

        allowance_lines: List[dict] = [
            position
            for position in positions
            if position["position_text"] == "PC RT Remise Base"
        ]
        self.assertEqual(len(allowance_lines), 1)
        allowance_line: dict = allowance_lines[0]
        self.assertEqual(allowance_line["total_net_price"], Decimal("-28506.52"))
        self.assertEqual(allowance_line["tax_rate"], Decimal("20.00"))


if __name__ == "__main__":
    unittest.main()
