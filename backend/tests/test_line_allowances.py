"""Line-level allowances (EN 16931 BG-27) on UBL and CII positions."""

from __future__ import annotations

import unittest
from decimal import Decimal
from typing import List, Optional
from unittest.mock import Mock

from app.data_class.XmlInvoiceHeader import XmlInvoiceHeader
from app.invoice_handler.xml_parser_header import get_xml_header
from app.invoice_handler.xml_parser_positions import get_xml_positions

CII_NS: str = """xmlns:rsm="urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100"
 xmlns:ram="urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100"
 xmlns:udt="urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100" """

UBL_NS: str = """xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
 xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
 xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2" """


def _parse(xml_text: str) -> XmlInvoiceHeader:
    header: XmlInvoiceHeader = XmlInvoiceHeader(invoice_id="line-discount-1")
    header = get_xml_header(xml_text=xml_text, xml_invoice_data=header, logger=Mock())
    return get_xml_positions(xml_text=xml_text, xml_invoice_data=header, logger=Mock())


def _ubl_allowance_xml(
    *,
    amount: str,
    percent: Optional[str] = None,
    charge: bool = False,
) -> str:
    percent_xml: str = (
        f"<cbc:MultiplierFactorNumeric>{percent}</cbc:MultiplierFactorNumeric>"
        if percent is not None
        else ""
    )
    indicator: str = "true" if charge else "false"
    return f"""
  <cac:AllowanceCharge>
    <cbc:ChargeIndicator>{indicator}</cbc:ChargeIndicator>
    {percent_xml}
    <cbc:Amount currencyID="EUR">{amount}</cbc:Amount>
  </cac:AllowanceCharge>"""


def _ubl_line_xml(
    *,
    line_id: str,
    name: str,
    quantity: str,
    unit_price: str,
    line_net: str,
    allowances_xml: str = "",
) -> str:
    return f"""
  <cac:InvoiceLine>
    <cbc:ID>{line_id}</cbc:ID>
    <cbc:InvoicedQuantity unitCode="H87">{quantity}</cbc:InvoicedQuantity>
    <cbc:LineExtensionAmount currencyID="EUR">{line_net}</cbc:LineExtensionAmount>
    {allowances_xml}
    <cac:Item>
      <cbc:Name>{name}</cbc:Name>
      <cac:ClassifiedTaxCategory>
        <cbc:ID>S</cbc:ID>
        <cbc:Percent>19.00</cbc:Percent>
      </cac:ClassifiedTaxCategory>
    </cac:Item>
    <cac:Price>
      <cbc:PriceAmount currencyID="EUR">{unit_price}</cbc:PriceAmount>
    </cac:Price>
  </cac:InvoiceLine>"""


def _ubl_invoice_xml(
    lines_xml: str,
    *,
    header_allowance_xml: str = "",
    allowance_total: str = "0.00",
) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Invoice {UBL_NS}>
  <cbc:ID>44184348</cbc:ID>
  <cbc:IssueDate>2026-08-27</cbc:IssueDate>
  <cbc:InvoiceTypeCode>380</cbc:InvoiceTypeCode>
  <cbc:DocumentCurrencyCode>EUR</cbc:DocumentCurrencyCode>
  {header_allowance_xml}
  <cac:LegalMonetaryTotal>
    <cbc:LineExtensionAmount currencyID="EUR">690.63</cbc:LineExtensionAmount>
    <cbc:TaxExclusiveAmount currencyID="EUR">690.63</cbc:TaxExclusiveAmount>
    <cbc:TaxInclusiveAmount currencyID="EUR">821.85</cbc:TaxInclusiveAmount>
    <cbc:AllowanceTotalAmount currencyID="EUR">{allowance_total}</cbc:AllowanceTotalAmount>
    <cbc:PayableAmount currencyID="EUR">821.85</cbc:PayableAmount>
  </cac:LegalMonetaryTotal>
  {lines_xml}
</Invoice>
"""


def _babelsberg_ubl_xml() -> str:
    parts: List[str] = []
    rows: List[tuple[str, str, str, str, str, str, str]] = [
        ("1", "TUER", "1.0000", "706.27", "575.61", "130.66", "18.50"),
        ("2", "DICHTUNG", "1.0000", "15.06", "13.18", "1.88", "12.50"),
        ("3", "DICHTUNG", "1.0000", "101.16", "88.52", "12.64", "12.50"),
        ("4", "DAEMPFUNG", "1.0000", "23.58", "13.32", "10.26", "43.50"),
    ]
    for line_id, name, qty, unit_price, line_net, amount, percent in rows:
        parts.append(
            _ubl_line_xml(
                line_id=line_id,
                name=name,
                quantity=qty,
                unit_price=unit_price,
                line_net=line_net,
                allowances_xml=_ubl_allowance_xml(amount=amount, percent=percent),
            )
        )
    return _ubl_invoice_xml("".join(parts))


def _cii_allowance_xml(
    *,
    amount: str,
    percent: Optional[str] = None,
    charge: bool = False,
    tag: str = "SpecifiedTradeAllowanceCharge",
) -> str:
    percent_xml: str = (
        f"<ram:CalculationPercent>{percent}</ram:CalculationPercent>"
        if percent is not None
        else ""
    )
    indicator: str = "true" if charge else "false"
    return f"""
        <ram:{tag}>
          <ram:ChargeIndicator>
            <udt:Indicator>{indicator}</udt:Indicator>
          </ram:ChargeIndicator>
          {percent_xml}
          <ram:ActualAmount>{amount}</ram:ActualAmount>
        </ram:{tag}>"""


def _cii_line_xml(
    *,
    name: str,
    quantity: str,
    unit_price: str,
    line_net: str,
    settlement_xml: str = "",
    price_level_xml: str = "",
    gross_price: Optional[str] = None,
) -> str:
    gross_amount: str = gross_price if gross_price is not None else unit_price
    price_block: str = f"""
      <ram:SpecifiedLineTradeAgreement>
        <ram:GrossPriceProductTradePrice>
          <ram:ChargeAmount>{gross_amount}</ram:ChargeAmount>
          {price_level_xml}
        </ram:GrossPriceProductTradePrice>
        <ram:NetPriceProductTradePrice>
          <ram:ChargeAmount>{unit_price}</ram:ChargeAmount>
        </ram:NetPriceProductTradePrice>
      </ram:SpecifiedLineTradeAgreement>"""
    return f"""
    <ram:IncludedSupplyChainTradeLineItem>
      <ram:SpecifiedTradeProduct>
        <ram:Name>{name}</ram:Name>
      </ram:SpecifiedTradeProduct>
      {price_block}
      <ram:SpecifiedLineTradeDelivery>
        <ram:BilledQuantity unitCode="H87">{quantity}</ram:BilledQuantity>
      </ram:SpecifiedLineTradeDelivery>
      <ram:SpecifiedLineTradeSettlement>
        <ram:ApplicableTradeTax>
          <ram:RateApplicablePercent>19.00</ram:RateApplicablePercent>
        </ram:ApplicableTradeTax>
        {settlement_xml}
        <ram:SpecifiedTradeSettlementLineMonetarySummation>
          <ram:LineTotalAmount>{line_net}</ram:LineTotalAmount>
        </ram:SpecifiedTradeSettlementLineMonetarySummation>
      </ram:SpecifiedLineTradeSettlement>
    </ram:IncludedSupplyChainTradeLineItem>"""


def _cii_invoice_xml(
    lines_xml: str,
    *,
    header_allowance_xml: str = "",
    allowance_total: str = "0.00",
) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rsm:CrossIndustryInvoice {CII_NS}>
  <rsm:ExchangedDocument>
    <ram:ID>44184348</ram:ID>
    <ram:TypeCode>380</ram:TypeCode>
    <ram:IssueDateTime>
      <udt:DateTimeString format="102">20260827</udt:DateTimeString>
    </ram:IssueDateTime>
  </rsm:ExchangedDocument>
  <rsm:SupplyChainTradeTransaction>
    {lines_xml}
    <ram:ApplicableHeaderTradeSettlement>
      <ram:InvoiceCurrencyCode>EUR</ram:InvoiceCurrencyCode>
      {header_allowance_xml}
      <ram:SpecifiedTradeSettlementHeaderMonetarySummation>
        <ram:LineTotalAmount>690.63</ram:LineTotalAmount>
        <ram:AllowanceTotalAmount>{allowance_total}</ram:AllowanceTotalAmount>
        <ram:TaxBasisTotalAmount>690.63</ram:TaxBasisTotalAmount>
        <ram:GrandTotalAmount>821.85</ram:GrandTotalAmount>
      </ram:SpecifiedTradeSettlementHeaderMonetarySummation>
    </ram:ApplicableHeaderTradeSettlement>
  </rsm:SupplyChainTradeTransaction>
</rsm:CrossIndustryInvoice>
"""


class TestUblLineAllowances(unittest.TestCase):
    def test_four_positions_keep_prices_and_store_discount(self) -> None:
        data: XmlInvoiceHeader = _parse(_babelsberg_ubl_xml())
        positions: List[dict] = data.get_positions_map()
        self.assertEqual(len(positions), 4)
        expected: List[tuple[str, Decimal, Decimal, Decimal, Decimal]] = [
            ("TUER", Decimal("706.27"), Decimal("575.61"), Decimal("130.66"), Decimal("18.50")),
            ("DICHTUNG", Decimal("15.06"), Decimal("13.18"), Decimal("1.88"), Decimal("12.50")),
            ("DICHTUNG", Decimal("101.16"), Decimal("88.52"), Decimal("12.64"), Decimal("12.50")),
            ("DAEMPFUNG", Decimal("23.58"), Decimal("13.32"), Decimal("10.26"), Decimal("43.50")),
        ]
        for position, (name, unit, line_net, amount, percent) in zip(positions, expected):
            self.assertIn(name, position["position_text"])
            self.assertEqual(position["quantity"], Decimal("1.0000"))
            self.assertEqual(position["single_net_price"], unit)
            self.assertEqual(position["total_net_price"], line_net)
            self.assertEqual(position["discount_amount"], amount)
            self.assertEqual(position["discount_percent"], percent)

    def test_no_allowance_leaves_discount_empty(self) -> None:
        xml_text: str = _ubl_invoice_xml(
            _ubl_line_xml(
                line_id="1",
                name="PART",
                quantity="2",
                unit_price="50.00",
                line_net="80.00",
            )
        )
        position: dict = _parse(xml_text).get_positions_map()[0]
        self.assertEqual(position["single_net_price"], Decimal("50.00"))
        self.assertEqual(position["total_net_price"], Decimal("80.00"))
        self.assertIsNone(position["discount_amount"])
        self.assertIsNone(position["discount_percent"])

    def test_charge_is_not_a_discount(self) -> None:
        xml_text: str = _ubl_invoice_xml(
            _ubl_line_xml(
                line_id="1",
                name="PART",
                quantity="1",
                unit_price="100.00",
                line_net="110.00",
                allowances_xml=_ubl_allowance_xml(amount="10.00", percent="10.00", charge=True),
            )
        )
        position: dict = _parse(xml_text).get_positions_map()[0]
        self.assertIsNone(position["discount_amount"])
        self.assertIsNone(position["discount_percent"])

    def test_several_allowances_sum_amount_and_drop_percent(self) -> None:
        xml_text: str = _ubl_invoice_xml(
            _ubl_line_xml(
                line_id="1",
                name="PART",
                quantity="1",
                unit_price="100.00",
                line_net="85.00",
                allowances_xml=(
                    _ubl_allowance_xml(amount="10.00", percent="10.00")
                    + _ubl_allowance_xml(amount="5.00", percent="5.00")
                ),
            )
        )
        position: dict = _parse(xml_text).get_positions_map()[0]
        self.assertEqual(position["discount_amount"], Decimal("15.00"))
        self.assertIsNone(position["discount_percent"])
        self.assertEqual(position["single_net_price"], Decimal("100.00"))
        self.assertEqual(position["total_net_price"], Decimal("85.00"))

    def test_header_allowance_is_not_copied_onto_the_line(self) -> None:
        xml_text: str = _ubl_invoice_xml(
            _ubl_line_xml(
                line_id="1",
                name="PART",
                quantity="1",
                unit_price="100.00",
                line_net="100.00",
            ),
            header_allowance_xml=_ubl_allowance_xml(amount="20.00", percent="20.00"),
            allowance_total="20.00",
        )
        positions: List[dict] = _parse(xml_text).get_positions_map()
        line: dict = positions[0]
        self.assertIn("PART", line["position_text"])
        self.assertIsNone(line["discount_amount"])
        self.assertIsNone(line["discount_percent"])

    def test_item_price_allowance_is_not_a_line_discount(self) -> None:
        line_xml: str = """
  <cac:InvoiceLine>
    <cbc:ID>1</cbc:ID>
    <cbc:InvoicedQuantity unitCode="H87">1</cbc:InvoicedQuantity>
    <cbc:LineExtensionAmount currencyID="EUR">90.00</cbc:LineExtensionAmount>
    <cac:Item>
      <cbc:Name>PART</cbc:Name>
      <cac:ClassifiedTaxCategory>
        <cbc:ID>S</cbc:ID>
        <cbc:Percent>19.00</cbc:Percent>
      </cac:ClassifiedTaxCategory>
    </cac:Item>
    <cac:Price>
      <cbc:PriceAmount currencyID="EUR">90.00</cbc:PriceAmount>
      <cac:AllowanceCharge>
        <cbc:ChargeIndicator>false</cbc:ChargeIndicator>
        <cbc:Amount currencyID="EUR">10.00</cbc:Amount>
      </cac:AllowanceCharge>
    </cac:Price>
  </cac:InvoiceLine>"""
        position: dict = _parse(_ubl_invoice_xml(line_xml)).get_positions_map()[0]
        self.assertEqual(position["single_net_price"], Decimal("90.00"))
        self.assertEqual(position["total_net_price"], Decimal("90.00"))
        self.assertIsNone(position["discount_amount"])
        self.assertIsNone(position["discount_percent"])


class TestCiiLineAllowances(unittest.TestCase):
    def test_settlement_and_price_level_are_not_added_twice(self) -> None:
        xml_text: str = _cii_invoice_xml(
            _cii_line_xml(
                name="TUER",
                quantity="1",
                unit_price="706.27",
                line_net="575.61",
                settlement_xml=_cii_allowance_xml(amount="130.66", percent="18.50"),
                price_level_xml=_cii_allowance_xml(
                    amount="130.66",
                    percent="18.50",
                    tag="AppliedTradeAllowanceCharge",
                ),
            )
        )
        position: dict = _parse(xml_text).get_positions_map()[0]
        self.assertEqual(position["single_net_price"], Decimal("706.27"))
        self.assertEqual(position["total_net_price"], Decimal("575.61"))
        self.assertEqual(position["discount_amount"], Decimal("130.66"))
        self.assertEqual(position["discount_percent"], Decimal("18.50"))

    def test_price_level_allowance_used_when_settlement_has_none(self) -> None:
        xml_text: str = _cii_invoice_xml(
            _cii_line_xml(
                name="TUER",
                quantity="1",
                unit_price="706.27",
                line_net="575.61",
                price_level_xml=_cii_allowance_xml(
                    amount="130.66",
                    percent="18.50",
                    tag="AppliedTradeAllowanceCharge",
                ),
            )
        )
        position: dict = _parse(xml_text).get_positions_map()[0]
        self.assertEqual(position["discount_amount"], Decimal("130.66"))
        self.assertEqual(position["discount_percent"], Decimal("18.50"))

    def test_header_allowance_is_not_copied_onto_the_line(self) -> None:
        xml_text: str = _cii_invoice_xml(
            _cii_line_xml(
                name="PART",
                quantity="1",
                unit_price="100.00",
                line_net="100.00",
            ),
            header_allowance_xml=_cii_allowance_xml(amount="20.00", percent="20.00"),
            allowance_total="20.00",
        )
        line: dict = _parse(xml_text).get_positions_map()[0]
        self.assertIn("PART", line["position_text"])
        self.assertIsNone(line["discount_amount"])
        self.assertIsNone(line["discount_percent"])


if __name__ == "__main__":
    unittest.main()
