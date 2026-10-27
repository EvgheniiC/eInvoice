"""Draft extraction, arithmetic, and the KoSIT download gate for outgoing invoices."""

from __future__ import annotations

import base64
import unittest
from decimal import Decimal
from io import BytesIO
from typing import List
from unittest.mock import patch
from xml.etree import ElementTree as ET

from fastapi.testclient import TestClient
from reportlab.pdfgen import canvas

from app.core.config import settings
from app.db.bootstrap import init_account_store
from app.db.session import dispose_engine
from app.main import create_app
from app.schemas.invoice import ValidationStatus
from app.schemas.issue import (
    IssueAddress,
    IssueBuildRequest,
    IssueBuildResponse,
    IssueDraft,
    IssueDraftResponse,
    IssueLineInput,
    IssueParty,
)
from app.services.en16931_validator import ValidationResult
from app.services.issue_draft import SellerSeed, extract_draft_from_pdf, prepare_invoice
from app.services.issue_pdf import embed_facturx
from app.services.issue_service import build_issue
from app.services.issue_xml import XRECHNUNG_GUIDELINE, render_cii

_NS: dict[str, str] = {
    "ram": "urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100",
    "rsm": "urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100",
}


def _party(**kwargs: str) -> IssueParty:
    address: IssueAddress = IssueAddress(
        line=kwargs.get("line"),
        postcode=kwargs.get("postcode"),
        city=kwargs.get("city"),
        country=kwargs.get("country", "DE"),
    )
    return IssueParty(
        name=kwargs.get("name"),
        address=address,
        vat_id=kwargs.get("vat_id"),
        email=kwargs.get("email"),
        contact_name=kwargs.get("contact_name"),
        phone=kwargs.get("phone"),
        iban=kwargs.get("iban"),
    )


def _complete_draft() -> IssueDraft:
    return IssueDraft(
        invoice_number="RE-1",
        issue_date="2026-10-26",
        currency="EUR",
        buyer_reference="LEITWEG-1",
        seller=_party(
            name="Muster GmbH",
            line="Hauptstr. 1",
            postcode="10115",
            city="Berlin",
            vat_id="DE123456789",
            email="billing@muster.example",
            contact_name="Ada Meister",
            phone="+4930123456",
            iban="DE89370400440532013000",
        ),
        buyer=_party(
            name="Beispiel AG",
            line="Markt 2",
            postcode="80331",
            city="München",
        ),
        lines=[
            IssueLineInput(
                description="Beratung",
                quantity=Decimal("2"),
                unit_code="HUR",
                unit_price=Decimal("10.00"),
                tax_rate=Decimal("19"),
            )
        ],
    )


def _text_pdf(lines: List[str]) -> bytes:
    buffer: BytesIO = BytesIO()
    pdf: canvas.Canvas = canvas.Canvas(buffer)
    cursor: int = 800
    for line in lines:
        pdf.drawString(50, cursor, line)
        cursor -= 18
    pdf.save()
    return buffer.getvalue()


class TestIssueDraft(unittest.TestCase):
    def test_reads_labeled_fields_and_keeps_header_amounts_out_of_lines(self) -> None:
        pdf: bytes = _text_pdf(
            [
                "Rechnungsnummer: RE-2026-42",
                "Rechnungsdatum: 26.10.2026",
                "USt-IdNr.: DE123456789",
                "IBAN: DE89 3704 0044 0532 0130 00",
                "Leitweg-ID: 04011000-1234512345-06",
                "Nettobetrag: 100,00",
                "MwSt 19 %: 19,00",
                "Gesamtbetrag: 119,00",
                "billing@muster.example",
            ]
        )
        result: IssueDraftResponse = extract_draft_from_pdf(pdf, "rechnung.pdf")
        self.assertTrue(result.text_found)
        self.assertEqual(result.draft.invoice_number, "RE-2026-42")
        self.assertEqual(result.draft.issue_date, "2026-10-26")
        self.assertEqual(result.draft.seller.vat_id, "DE123456789")
        self.assertEqual(result.draft.seller.iban, "DE89370400440532013000")
        self.assertEqual(result.draft.buyer_reference, "04011000-1234512345-06")
        self.assertEqual(result.draft.seller.email, "billing@muster.example")
        self.assertIsNone(result.draft.lines[0].description)
        self.assertTrue(any("100,00" in warning for warning in result.warnings))

    def test_organization_seller_wins_over_a_different_pdf_iban(self) -> None:
        pdf: bytes = _text_pdf(
            [
                "Rechnungsnummer: RE-1",
                "IBAN: DE89 3704 0044 0532 0130 00",
            ]
        )
        result: IssueDraftResponse = extract_draft_from_pdf(
            pdf,
            "rechnung.pdf",
            seller=SellerSeed(name="Werkstatt GmbH", vat_id="DE111111111", iban="DE44500105175407324931"),
        )
        self.assertEqual(result.draft.seller.name, "Werkstatt GmbH")
        self.assertEqual(result.draft.seller.iban, "DE44500105175407324931")
        self.assertTrue(any("IBAN" in warning for warning in result.warnings))

    def test_confirmation_and_zero_tax_block_generation(self) -> None:
        draft: IssueDraft = _complete_draft()
        unconfirmed = prepare_invoice(draft, confirmed=False)
        self.assertIsNone(unconfirmed.invoice)
        self.assertTrue(any(issue.code == "CONFIRMED_REQUIRED" for issue in unconfirmed.blocking))

        draft.lines[0].tax_rate = Decimal("0")
        zero_tax = prepare_invoice(draft, confirmed=True)
        self.assertIsNone(zero_tax.invoice)
        self.assertTrue(any(issue.code == "BT-152_UNSUPPORTED" for issue in zero_tax.blocking))

    def test_xml_totals_come_from_lines(self) -> None:
        prepared = prepare_invoice(_complete_draft(), confirmed=True)
        self.assertIsNotNone(prepared.invoice)
        assert prepared.invoice is not None
        self.assertEqual(prepared.invoice.line_total, Decimal("20.00"))
        self.assertEqual(prepared.invoice.tax_total, Decimal("3.80"))
        self.assertEqual(prepared.invoice.grand_total, Decimal("23.80"))
        self.assertEqual(prepared.xrechnung_gaps, [])

        xml_text: str = render_cii(prepared.invoice, "xrechnung")
        root: ET.Element = ET.fromstring(xml_text)
        guideline: str = root.findtext(".//ram:GuidelineSpecifiedDocumentContextParameter/ram:ID", namespaces=_NS) or ""
        self.assertEqual(guideline, XRECHNUNG_GUIDELINE)
        self.assertEqual(root.findtext(".//ram:GrandTotalAmount", namespaces=_NS), "23.80")
        self.assertEqual(root.findtext(".//ram:DuePayableAmount", namespaces=_NS), "23.80")
        self.assertEqual(root.findtext(".//ram:IBANID", namespaces=_NS), "DE89370400440532013000")

    def test_missing_buyer_reference_blocks_only_xrechnung(self) -> None:
        draft: IssueDraft = _complete_draft()
        draft.buyer_reference = None
        prepared = prepare_invoice(draft, confirmed=True)
        self.assertIsNotNone(prepared.invoice)
        self.assertTrue(any(issue.code == "BT-10_MISSING" for issue in prepared.xrechnung_gaps))


class TestIssueBuildGate(unittest.TestCase):
    def test_without_kosit_nothing_is_downloadable(self) -> None:
        response: IssueBuildResponse = build_issue(
            IssueBuildRequest(draft=_complete_draft(), confirmed=True),
            pdf_bytes=b"%PDF-1.7",
        )
        self.assertFalse(response.ready)
        for artifact in response.artifacts:
            self.assertFalse(artifact.download_allowed)
            self.assertIsNone(artifact.content_base64)

    def test_valid_kosit_returns_xml_and_embedded_pdf(self) -> None:
        valid: ValidationResult = ValidationResult(
            status=ValidationStatus.VALID,
            full_check_completed=True,
            engine="kosit",
        )
        with (
            patch("app.services.issue_service.validate_invoice", return_value=valid),
            patch("app.services.issue_service.embed_facturx", return_value=b"%PDF-1.7 embedded"),
        ):
            response: IssueBuildResponse = build_issue(
                IssueBuildRequest(draft=_complete_draft(), confirmed=True, pdf_base64="ignored-by-service"),
                pdf_bytes=b"%PDF-1.7",
            )
        self.assertTrue(response.ready)
        by_format: dict[str, str] = {}
        for artifact in response.artifacts:
            self.assertTrue(artifact.download_allowed)
            self.assertIsNotNone(artifact.content_base64)
            assert artifact.content_base64 is not None
            by_format[artifact.format] = base64.b64decode(artifact.content_base64).decode("utf-8", errors="ignore")
        self.assertIn("23.80", by_format["xrechnung"])
        self.assertIn("urn:factur-x.eu:1p0:en16931", by_format["zugferd_xml"])
        self.assertTrue(by_format["zugferd_pdf"].startswith("%PDF-"))

    def test_facturx_library_embeds_xml_into_the_pdf(self) -> None:
        prepared = prepare_invoice(_complete_draft(), confirmed=True)
        self.assertIsNotNone(prepared.invoice)
        assert prepared.invoice is not None
        xml_bytes: bytes = render_cii(prepared.invoice, "facturx").encode("utf-8")
        embedded: bytes = embed_facturx(_text_pdf(["Rechnung RE-1"]), xml_bytes)
        self.assertTrue(embedded.startswith(b"%PDF-"))
        self.assertGreater(len(embedded), 1000)


class TestIssueApi(unittest.TestCase):
    def setUp(self) -> None:
        self._patches = [
            patch.object(settings, "database_url", "sqlite://"),
            patch.object(settings, "auth_secret_key", "test-secret-key"),
            patch.object(settings, "environment", "development"),
            patch.object(settings, "admin_emails", "admin@example.com"),
        ]
        for item in self._patches:
            item.start()
        dispose_engine()
        init_account_store()
        self.client: TestClient = TestClient(create_app())

    def tearDown(self) -> None:
        self.client.close()
        dispose_engine()
        for item in reversed(self._patches):
            item.stop()

    def test_guest_cannot_create_a_draft(self) -> None:
        pdf: bytes = _text_pdf(["Rechnungsnummer: RE-9"])
        response = self.client.post(
            "/api/issue/draft",
            files={"file": ("rechnung.pdf", pdf, "application/pdf")},
        )
        self.assertEqual(response.status_code, 401)

    def test_signed_in_user_cannot_create_a_draft(self) -> None:
        self._login("meister@example.com")
        pdf: bytes = _text_pdf(["Rechnungsnummer: RE-9"])
        response = self.client.post(
            "/api/issue/draft",
            files={"file": ("rechnung.pdf", pdf, "application/pdf")},
        )
        self.assertEqual(response.status_code, 403)

    def test_admin_can_read_a_text_pdf(self) -> None:
        self._login("admin@example.com")
        pdf: bytes = _text_pdf(["Rechnungsnummer: RE-9", "Rechnungsdatum: 01.02.2026"])
        response = self.client.post(
            "/api/issue/draft",
            files={"file": ("rechnung.pdf", pdf, "application/pdf")},
        )
        self.assertEqual(response.status_code, 200, response.text)
        body: IssueDraftResponse = IssueDraftResponse.model_validate(response.json())
        self.assertEqual(body.draft.invoice_number, "RE-9")
        self.assertEqual(body.draft.issue_date, "2026-02-01")

    def test_admin_build_keeps_download_closed(self) -> None:
        self._login("admin@example.com")
        response = self.client.post(
            "/api/issue/build",
            json=IssueBuildRequest(draft=_complete_draft(), confirmed=True).model_dump(mode="json"),
        )
        self.assertEqual(response.status_code, 200, response.text)
        body: IssueBuildResponse = IssueBuildResponse.model_validate(response.json())
        self.assertFalse(body.ready)
        self.assertTrue(all(item.download_allowed is False for item in body.artifacts))

    def _login(self, email: str) -> None:
        registered = self.client.post(
            "/api/auth/register",
            json={
                "email": email,
                "password": "sicher-passwort-1",
                "organization_name": "Muster Handwerk",
            },
        )
        self.assertEqual(registered.status_code, 200, registered.text)
        token: str = str(registered.json()["verification_token"])
        verified = self.client.post("/api/auth/verify-email", json={"token": token})
        self.assertEqual(verified.status_code, 200, verified.text)
        logged_in = self.client.post(
            "/api/auth/login",
            json={"email": email, "password": "sicher-passwort-1"},
        )
        self.assertEqual(logged_in.status_code, 200, logged_in.text)
