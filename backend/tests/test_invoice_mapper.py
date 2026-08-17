import unittest

from app.schemas.invoice import (
    InvoiceParseResponse,
    InvoiceTotals,
    MismatchField,
    PartyInfo,
    ParseStatus,
    ValidationIssue,
    ValidationStatus,
)
from app.services.invoice_mapper import build_next_steps, has_blocking_errors, has_pdf_xml_mismatch


def _base_invoice() -> InvoiceParseResponse:
    return InvoiceParseResponse(
        status=ParseStatus.SUCCESS,
        message="ok",
        filename="sample.xml",
        file_type="xrechnung_xml",
        invoice_number="RE-1",
        issue_date="2026-08-01",
        due_date="2026-08-20",
        seller=PartyInfo(name="Seller GmbH", iban="DE00111111111111111111"),
        buyer=PartyInfo(name="Buyer AG"),
        totals=InvoiceTotals(net=100, tax=19, gross=119, currency="EUR"),
        validation_status=ValidationStatus.VALID,
    )


class TestNextSteps(unittest.TestCase):
    def test_mismatch_tells_user_not_to_pay(self) -> None:
        invoice: InvoiceParseResponse = _base_invoice()
        invoice.file_type = "zugferd_pdf"
        invoice.validation_status = ValidationStatus.WARNING
        invoice.mismatch_fields = [
            MismatchField(
                field="iban",
                label="IBAN",
                xml_value="DE00111111111111111111",
                pdf_value="DE00999999999999999999",
                matched=False,
            )
        ]
        steps: list[str] = build_next_steps(invoice)
        self.assertTrue(has_pdf_xml_mismatch(invoice))
        self.assertTrue(has_blocking_errors(invoice))
        self.assertTrue(any("Nicht zahlen" in step for step in steps), msg=steps)
        self.assertTrue(any("Prüfbericht" in step for step in steps), msg=steps)
        self.assertFalse(any("Betrag zahlen" in step for step in steps), msg=steps)

    def test_invalid_invoice_requests_correction_and_report(self) -> None:
        invoice: InvoiceParseResponse = _base_invoice()
        invoice.validation_status = ValidationStatus.INVALID
        invoice.validation_issues = [
            ValidationIssue(
                level="error",
                category="business",
                code="AMOUNT_INCONSISTENT",
                message="Summen stimmen nicht.",
            )
        ]
        steps: list[str] = build_next_steps(invoice)
        self.assertTrue(any("Nicht zahlen" in step for step in steps), msg=steps)
        self.assertTrue(any("Prüfbericht" in step for step in steps), msg=steps)
        self.assertTrue(any("Bestätigung" in step for step in steps), msg=steps)

    def test_valid_invoice_offers_export(self) -> None:
        steps: list[str] = build_next_steps(_base_invoice())
        self.assertTrue(any("Paket für Steuerberater" in step for step in steps), msg=steps)
        self.assertFalse(any("Nicht zahlen" in step for step in steps), msg=steps)


if __name__ == "__main__":
    unittest.main()
