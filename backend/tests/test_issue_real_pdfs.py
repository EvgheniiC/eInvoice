"""Regression checks for real workshop PDFs in tests/issue_pdfs."""

from __future__ import annotations

import unittest
from decimal import Decimal
from pathlib import Path

from app.schemas.issue import IssueDraftResponse
from app.services.issue_draft import extract_draft_from_pdf

_PDF_DIR: Path = Path(__file__).parent / "issue_pdfs"


def _draft(filename: str) -> IssueDraftResponse:
    content: bytes = (_PDF_DIR / filename).read_bytes()
    return extract_draft_from_pdf(content, filename)


def _net_sum(result: IssueDraftResponse) -> Decimal:
    total: Decimal = Decimal("0.00")
    for line in result.draft.lines:
        total += (line.quantity * line.unit_price).quantize(Decimal("0.01"))
    return total


class RealInvoicePdfTests(unittest.TestCase):
    def test_sixt_parts_invoice_reads_number_date_and_both_lines(self) -> None:
        result: IssueDraftResponse = _draft("0426478731-207600RECHNUNG1.pdf")
        self.assertEqual(result.draft.invoice_number, "0426478731")
        self.assertEqual(result.draft.issue_date, "2026-10-09")
        self.assertEqual(
            [line.description for line in result.draft.lines],
            ["LAGERUNG", "RADSKASTEN"],
        )
        self.assertEqual(_net_sum(result), Decimal("149.25"))

    def test_autohaus_reads_seller_buyer_and_the_full_net(self) -> None:
        result: IssueDraftResponse = _draft("2026-10-09_410023574.pdf")
        self.assertEqual(result.draft.invoice_number, "410023574")
        self.assertEqual(result.draft.issue_date, "2026-10-09")
        self.assertEqual(result.draft.seller.address.city, "Dormagen")
        self.assertEqual(result.draft.seller.address.postcode, "41542")
        self.assertEqual(result.draft.buyer.address.postcode, "18049")
        self.assertIn("Trelleborger", result.draft.buyer.address.line or "")
        self.assertEqual(_net_sum(result), Decimal("378.82"))
        self.assertTrue(all(line.tax_rate == Decimal("19.00") for line in result.draft.lines))

    def test_gotta_reads_seller_city_and_service_lines(self) -> None:
        result: IssueDraftResponse = _draft("20261009_Rechnung_413079_K30100_FGWAUZZZF10VD001406.pdf")
        self.assertEqual(result.draft.invoice_number, "413079")
        self.assertEqual(result.draft.issue_date, "2026-10-09")
        self.assertIn("Mörfelden", result.draft.seller.address.city or "")
        self.assertEqual(_net_sum(result), Decimal("89.99"))

    def test_mex_reads_both_cities_and_the_labor_net(self) -> None:
        result: IssueDraftResponse = _draft(
            "260373_RECHNUNG_Sixt_GmbH___Co__Autovermietung_KG_Repair_Center_Berlin.PDF"
        )
        self.assertEqual(result.draft.invoice_number, "260373")
        self.assertEqual(result.draft.issue_date, "2026-10-09")
        self.assertEqual(result.draft.seller.address.city, "Berlin")
        self.assertEqual(result.draft.buyer.address.postcode, "12529")
        self.assertEqual(_net_sum(result), Decimal("1300.00"))

    def test_jelitto_reads_due_date_and_transport_net(self) -> None:
        result: IssueDraftResponse = _draft("ARg261626.PDF")
        self.assertEqual(result.draft.invoice_number, "261626")
        self.assertEqual(result.draft.issue_date, "2026-10-09")
        self.assertEqual(result.draft.due_date, "2026-10-19")
        self.assertEqual(result.draft.seller.address.postcode, "15517")
        self.assertEqual(result.draft.buyer.address.postcode, "12529")
        self.assertEqual(_net_sum(result), Decimal("664.90"))

    def test_zwetko_reads_seller_buyer_and_wrapped_lines(self) -> None:
        result: IssueDraftResponse = _draft("Ausgangsrechnung_261313964.pdf")
        self.assertEqual(result.draft.invoice_number, "261313964")
        self.assertEqual(result.draft.issue_date, "2026-10-08")
        self.assertEqual(result.draft.seller.address.city, "Olching")
        self.assertEqual(result.draft.buyer.address.postcode, "82049")
        self.assertIn("Sixt", result.draft.buyer.name or "")
        self.assertEqual(_net_sum(result), Decimal("54.28"))

    def test_hetzner_reads_seller_buyer_city_and_net(self) -> None:
        result: IssueDraftResponse = _draft("Hetzner_2026-06-01_083000909711.pdf")
        self.assertEqual(result.draft.invoice_number, "083000909711")
        self.assertEqual(result.draft.issue_date, "2026-06-01")
        self.assertEqual(result.draft.due_date, "2026-06-05")
        self.assertEqual(result.draft.seller.address.city, "Gunzenhausen")
        self.assertEqual(result.draft.buyer.address.postcode, "27755")
        self.assertEqual(result.draft.buyer.address.city, "Delmenhorst")
        self.assertEqual(_net_sum(result), Decimal("13.39"))

    def test_products_reads_seller_and_buyer_head_office(self) -> None:
        result: IssueDraftResponse = _draft("R-RE544720-Kdnr-Sixt42303.pdf")
        self.assertEqual(result.draft.invoice_number, "RE544720")
        self.assertEqual(result.draft.issue_date, "2026-10-09")
        self.assertEqual(result.draft.due_date, "2026-12-08")
        self.assertEqual(result.draft.seller.address.city, "Geretsried")
        self.assertEqual(result.draft.buyer.address.postcode, "82049")
        self.assertEqual(_net_sum(result), Decimal("43.00"))

    def test_sonax_reads_number_and_all_three_products(self) -> None:
        result: IssueDraftResponse = _draft("RA8-26428862.pdf")
        self.assertEqual(result.draft.invoice_number, "RA8-26428862")
        self.assertEqual(result.draft.issue_date, "2026-10-08")
        self.assertIn("Neuburg", result.draft.seller.address.city or "")
        self.assertEqual(result.draft.buyer.address.postcode, "82049")
        self.assertEqual(
            [line.description for line in result.draft.lines],
            ["SONAX CleanStar Ecodetergent", "SONAX TrockenWäsche", "SONAX WinterTrockenWäsche"],
        )
        self.assertEqual(_net_sum(result), Decimal("528.00"))

    def test_heinrich_short_invoice_reads_seller_and_three_charges(self) -> None:
        result: IssueDraftResponse = _draft("RE2026307806.pdf")
        self.assertEqual(result.draft.invoice_number, "2026307806")
        self.assertEqual(result.draft.issue_date, "2026-10-09")
        self.assertEqual(result.draft.seller.address.postcode, "50354")
        self.assertIn("Hürth", result.draft.seller.address.city or "")
        self.assertFalse(result.draft.buyer.address.line)
        self.assertEqual(_net_sum(result), Decimal("265.00"))

    def test_tire_invoice_reads_number_and_line_net(self) -> None:
        result: IssueDraftResponse = _draft("RE2603834.PDF")
        self.assertEqual(result.draft.invoice_number, "2603834")
        self.assertEqual(result.draft.issue_date, "2026-10-09")
        self.assertEqual(_net_sum(result), Decimal("382.00"))

    def test_heinrich_tow_invoice_reads_seller_and_full_net(self) -> None:
        result: IssueDraftResponse = _draft("Rechnung 2026307803 zuSIXT Auftrag 9601209008.pdf")
        self.assertEqual(result.draft.invoice_number, "2026307803")
        self.assertEqual(result.draft.issue_date, "2026-10-09")
        self.assertEqual(result.draft.seller.address.postcode, "50354")
        self.assertFalse(result.draft.buyer.address.line)
        self.assertEqual(_net_sum(result), Decimal("455.00"))

    def test_berner_reads_seller_postcode_buyer_and_tax(self) -> None:
        result: IssueDraftResponse = _draft("Rechnung_1096449708.pdf")
        self.assertEqual(result.draft.invoice_number, "1096449708")
        self.assertEqual(result.draft.issue_date, "2026-10-08")
        self.assertEqual(result.draft.seller.address.postcode, "74653")
        self.assertEqual(result.draft.buyer.address.postcode, "82049")
        self.assertEqual(result.draft.buyer_reference, "SIXT-000000384865")
        self.assertEqual(result.draft.lines[0].tax_rate, Decimal("19.00"))
        self.assertEqual(_net_sum(result), Decimal("162.90"))


_SCANS: tuple[str, ...] = (
    "15275429_foto.pdf",
    "15278005_photo.pdf",
    "15318416_photo.pdf",
    "15318417_photo.pdf",
    "15345507_photo.pdf",
    "15364169.pdf",
    "15370644_photo.pdf",
    "15370645_photo.pdf",
)


class NewInvoicePdfTests(unittest.TestCase):
    def test_scans_have_no_text_layer(self) -> None:
        for filename in _SCANS:
            result: IssueDraftResponse = _draft(filename)
            self.assertFalse(result.text_found, filename)
            self.assertIsNone(result.draft.invoice_number, filename)
            self.assertIsNone(result.draft.lines[0].description, filename)

    def test_aschenbrenner_reads_both_parties_and_the_date(self) -> None:
        result: IssueDraftResponse = _draft("15342926.pdf")
        self.assertEqual(result.draft.invoice_number, "A2038693")
        self.assertEqual(result.draft.issue_date, "2026-10-13")
        self.assertEqual(result.draft.seller.name, "Aschenbrenner GmbH")
        self.assertEqual(result.draft.seller.address.postcode, "34123")
        self.assertEqual(result.draft.seller.address.city, "Kassel")
        self.assertEqual(result.draft.buyer.address.postcode, "64521")
        self.assertEqual(result.draft.buyer.address.city, "Groß-Gerau")

    def test_magnus_reads_number_and_seller(self) -> None:
        result: IssueDraftResponse = _draft("15355630.pdf")
        self.assertEqual(result.draft.invoice_number, "262173")
        self.assertEqual(result.draft.seller.name, "Günter Magnus GmbH")
        self.assertEqual(result.draft.seller.address.postcode, "26441")
        self.assertEqual(result.draft.seller.address.city, "Jever")

    def test_markwort_reads_number_seller_and_order_reference(self) -> None:
        result: IssueDraftResponse = _draft("15332491.pdf")
        self.assertEqual(result.draft.invoice_number, "0052074855")
        self.assertEqual(result.draft.seller.name, "Markwort KG")
        self.assertEqual(result.draft.seller.address.postcode, "59494")
        self.assertEqual(result.draft.buyer_reference, "55773333002200000011")

    def test_mercedes_leasing_reads_seller_date_and_contract(self) -> None:
        result: IssueDraftResponse = _draft("58815714.pdf")
        self.assertEqual(result.draft.issue_date, "2026-11-02")
        self.assertEqual(result.draft.seller.name, "Mercedes-Benz Leasing GmbH")
        self.assertEqual(result.draft.seller.address.postcode, "10836")
        self.assertEqual(result.draft.seller.address.city, "Berlin")
        self.assertEqual(result.draft.buyer_reference, "5322403342")

    def test_riller_reads_header_and_buyer_window(self) -> None:
        result: IssueDraftResponse = _draft("58856348_photo.pdf")
        self.assertEqual(result.draft.invoice_number, "0117238226")
        self.assertEqual(result.draft.issue_date, "2026-11-16")
        self.assertEqual(result.draft.delivery_date, "2026-11-16")
        self.assertEqual(result.draft.buyer_reference, "9601256470")
        self.assertEqual(result.draft.seller.address.postcode, "12203")
        self.assertEqual(result.draft.seller.address.city, "Berlin")
        self.assertIn("Trelleborger", result.draft.buyer.address.line or "")
        self.assertEqual(result.draft.buyer.address.postcode, "18107")

    def test_bmw_battery_line_net_is_the_discounted_amount(self) -> None:
        result: IssueDraftResponse = _draft("15386302.pdf")
        self.assertEqual(result.draft.invoice_number, "50031423")
        self.assertEqual(result.draft.issue_date, "2026-11-10")
        battery: list[Decimal] = [
            (line.quantity * line.unit_price).quantize(Decimal("0.01"))
            for line in result.draft.lines
            if line.description and "Batterie" in line.description and line.quantity and line.unit_price
        ]
        self.assertEqual(battery, [Decimal("375.37")])

    def test_volkswagen_hamburg_reads_the_invoice_number(self) -> None:
        result: IssueDraftResponse = _draft("58598834.pdf")
        self.assertEqual(result.draft.invoice_number, "10621129077")
        self.assertEqual(result.draft.buyer_reference, "2026030685")

    def test_nuremberg_tow_reads_the_invoice_number(self) -> None:
        result: IssueDraftResponse = _draft("15327729.pdf")
        self.assertEqual(result.draft.invoice_number, "5022299")

    def test_mercedes_credit_reads_number_and_date(self) -> None:
        result: IssueDraftResponse = _draft("58863655.pdf")
        self.assertEqual(result.draft.invoice_number, "100/26/1186942")
        self.assertEqual(result.draft.issue_date, "2026-11-03")
