"""Unit tests for EN 16931 business rules, profile detection, and KoSIT gating."""

from __future__ import annotations

import unittest
from decimal import Decimal
from unittest.mock import patch

from app.schemas.invoice import (
    InvoiceParseResponse,
    InvoiceTotals,
    LineItem,
    PartyInfo,
    ParseStatus,
    ValidationIssue,
    ValidationStatus,
)
from app.services.en16931_validator import ValidationResult, validate_invoice
from app.services.validation_profile import InvoiceProfile, extract_invoice_profile


def _parsed_ok() -> InvoiceParseResponse:
    return InvoiceParseResponse(
        status=ParseStatus.SUCCESS,
        message="ok",
        filename="x.xml",
        file_type="xrechnung_xml",
        invoice_number="INV-1",
        issue_date="2026-08-17",
        seller=PartyInfo(name="Seller GmbH", vat_id="DE123", iban="DE89370400440532013000"),
        buyer=PartyInfo(name="Buyer AG"),
        totals=InvoiceTotals(
            net=Decimal("100.00"),
            tax=Decimal("19.00"),
            gross=Decimal("119.00"),
            currency="EUR",
        ),
        line_items=[
            LineItem(
                position=1,
                description="Service",
                quantity=Decimal("1"),
                net_amount=Decimal("100.00"),
                tax_rate=Decimal("19"),
            )
        ],
    )


_XR_XML: str = (
    '<?xml version="1.0"?><Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"'
    ' xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">'
    "<cbc:CustomizationID>urn:cen.eu:en16931:2017#compliant#urn:xeinkauf.de:kosit:xrechnung_3.0"
    "</cbc:CustomizationID></Invoice>"
)


class TestEn16931Validator(unittest.TestCase):
    def test_profile_from_customization_id(self) -> None:
        profile: InvoiceProfile = extract_invoice_profile(_XR_XML)
        self.assertEqual(profile.profile_id, (
            "urn:cen.eu:en16931:2017#compliant#urn:xeinkauf.de:kosit:xrechnung_3.0"
        ))
        self.assertEqual(profile.profile, "XRechnung 3.0")
        self.assertEqual(profile.standard_version, "EN 16931:2017")

    def test_profile_from_cii_guideline(self) -> None:
        cii_xml: str = (
            '<?xml version="1.0"?>'
            '<rsm:CrossIndustryInvoice '
            'xmlns:rsm="urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100" '
            'xmlns:ram="urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100">'
            "<rsm:ExchangedDocumentContext>"
            "<ram:GuidelineSpecifiedDocumentContextParameter>"
            "<ram:ID>urn:cen.eu:en16931:2017#compliant#urn:factur-x.eu:1p0:en16931</ram:ID>"
            "</ram:GuidelineSpecifiedDocumentContextParameter>"
            "</rsm:ExchangedDocumentContext>"
            "</rsm:CrossIndustryInvoice>"
        )
        profile: InvoiceProfile = extract_invoice_profile(cii_xml)
        self.assertEqual(profile.profile, "Factur-X EN 16931")
        self.assertEqual(profile.standard_version, "EN 16931:2017")

    def test_without_kosit_status_is_not_checked_not_valid(self) -> None:
        result: ValidationResult = validate_invoice(xml_text=_XR_XML, parsed=_parsed_ok())
        self.assertEqual(result.status, ValidationStatus.NOT_CHECKED)
        self.assertFalse(result.full_check_completed)
        self.assertEqual(result.engine, "business_rules")
        self.assertEqual(result.profile, "XRechnung 3.0")
        self.assertTrue(any(issue.code == "KOSIT_NOT_CONFIGURED" for issue in result.issues))

    def test_missing_invoice_number_is_invalid_with_bt_code(self) -> None:
        parsed: InvoiceParseResponse = _parsed_ok()
        parsed.invoice_number = None
        result: ValidationResult = validate_invoice(xml_text=_XR_XML, parsed=parsed)
        self.assertEqual(result.status, ValidationStatus.INVALID)
        issue: ValidationIssue = next(item for item in result.issues if item.code == "BT-1_MISSING")
        self.assertEqual(issue.level, "error")
        self.assertEqual(issue.category, "business")
        self.assertEqual(issue.bt_code, "BT-1")
        self.assertEqual(issue.field, "invoice_number")
        self.assertTrue(issue.explanation)

    def test_inconsistent_totals_are_business_errors(self) -> None:
        parsed: InvoiceParseResponse = _parsed_ok()
        self.assertIsNotNone(parsed.totals)
        if parsed.totals is not None:
            parsed.totals.gross = Decimal("1.00")
        result: ValidationResult = validate_invoice(xml_text=_XR_XML, parsed=parsed)
        self.assertEqual(result.status, ValidationStatus.INVALID)
        issue: ValidationIssue = next(
            item for item in result.issues if item.code == "AMOUNT_INCONSISTENT"
        )
        self.assertEqual(issue.level, "error")
        self.assertEqual(issue.bt_code, "BT-112")

    def test_production_requires_kosit_and_does_not_mark_valid(self) -> None:
        with patch("app.services.en16931_validator.settings") as mock_settings:
            mock_settings.kosit_validator_jar = None
            mock_settings.kosit_scenarios_xml = None
            mock_settings.kosit_java_bin = "java"
            mock_settings.kosit_timeout_seconds = 60
            mock_settings.require_kosit = True
            result: ValidationResult = validate_invoice(xml_text=_XR_XML, parsed=_parsed_ok())

        self.assertEqual(result.status, ValidationStatus.NOT_CHECKED)
        self.assertFalse(result.full_check_completed)
        self.assertTrue(
            any(issue.code == "KOSIT_REQUIRED_UNAVAILABLE" for issue in result.issues)
        )


if __name__ == "__main__":
    unittest.main()
