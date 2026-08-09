"""
Generate local edge-case fixtures from existing samples.

Outputs (gitignored):
  backend/tests/xml_files/Invalid_XR_*.xml
  backend/tests/pdf_files/Mismatch_*.pdf
  backend/tests/pdf_files/Broken_embedded_xml_*.pdf

Run from repo:
  python backend/scripts/generate_edge_case_fixtures.py
"""

from __future__ import annotations

import re
from io import BytesIO
from pathlib import Path

from PyPDF2 import PdfReader, PdfWriter

from app.services.pdf_xml_extractor import extract_embedded_xml_from_pdf

ROOT: Path = Path(__file__).resolve().parents[1]
XML_DIR: Path = ROOT / "tests" / "xml_files"
PDF_DIR: Path = ROOT / "tests" / "pdf_files"

BASE_XML: Path = XML_DIR / "xml_text_from_zugpferd.xml"
BASE_PDF: Path = PDF_DIR / "Rechnung_1096393995.pdf"


def _write_xml(name: str, content: str) -> Path:
    path: Path = XML_DIR / name
    path.write_text(content, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)} ({len(content)} chars)")
    return path


def _clone_pdf_with_attachment(src_pdf: bytes, attachment_name: str, xml_bytes: bytes) -> bytes:
    reader: PdfReader = PdfReader(BytesIO(src_pdf))
    writer: PdfWriter = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.add_attachment(attachment_name, xml_bytes)
    out: BytesIO = BytesIO()
    writer.write(out)
    return out.getvalue()


def _write_pdf(name: str, content: bytes) -> Path:
    path: Path = PDF_DIR / name
    path.write_bytes(content)
    print(f"wrote {path.relative_to(ROOT)} ({len(content)} bytes)")
    return path


def generate_invalid_xml() -> None:
    base: str = BASE_XML.read_text(encoding="utf-8")

    missing_id: str = re.sub(
        r"<rsm:ExchangedDocument>\s*<ram:ID>2025/10294</ram:ID>",
        "<rsm:ExchangedDocument>\n      <!-- invoice id removed for Invalid_XR_missing_invoice_id -->",
        base,
        count=1,
    )
    _write_xml("Invalid_XR_missing_invoice_id.xml", missing_id)

    missing_date: str = re.sub(
        r"<ram:IssueDateTime>\s*<udt:DateTimeString format=\"102\">20250131</udt:DateTimeString>\s*</ram:IssueDateTime>",
        "<!-- issue date removed for Invalid_XR_missing_issue_date -->",
        base,
        count=1,
    )
    _write_xml("Invalid_XR_missing_issue_date.xml", missing_date)

    inconsistent: str = base.replace(
        "<ram:GrandTotalAmount>270.73</ram:GrandTotalAmount>",
        "<ram:GrandTotalAmount>1.00</ram:GrandTotalAmount>",
    ).replace(
        "<ram:DuePayableAmount>270.73</ram:DuePayableAmount>",
        "<ram:DuePayableAmount>1.00</ram:DuePayableAmount>",
    )
    _write_xml("Invalid_XR_inconsistent_totals.xml", inconsistent)

    cut_at: int = max(200, len(base) // 2)
    broken: str = base[:cut_at] + "\n<!-- truncated for Invalid_XR_not_well_formed -->\n"
    _write_xml("Invalid_XR_not_well_formed.xml", broken)


def generate_zugferd_edge_cases() -> None:
    src_pdf: bytes = BASE_PDF.read_bytes()
    xml_text: str | None = extract_embedded_xml_from_pdf(src_pdf)
    if xml_text is None:
        raise RuntimeError(f"Could not extract XML from {BASE_PDF}")

    mismatch_no_amount: str = (
        xml_text.replace("1096393995", "MISMATCH-99999")
        .replace(">52.96<", ">9999.99<")
        .replace(">8.46<", ">1595.79<")
        .replace(">44.50<", ">8404.20<")
    )
    _write_pdf(
        "Mismatch_invoice_no_amount_1096393995.pdf",
        _clone_pdf_with_attachment(src_pdf, "xrechnung.xml", mismatch_no_amount.encode("utf-8")),
    )

    mismatch_iban: str = xml_text.replace(
        "DE93622515500005005505",
        "DE00111111111111111111",
    )
    _write_pdf(
        "Mismatch_iban_1096393995.pdf",
        _clone_pdf_with_attachment(src_pdf, "xrechnung.xml", mismatch_iban.encode("utf-8")),
    )

    broken_xml: str = xml_text[:400] + "\n<!-- truncated embedded XML -->\n"
    _write_pdf(
        "Broken_embedded_xml_1096393995.pdf",
        _clone_pdf_with_attachment(src_pdf, "xrechnung.xml", broken_xml.encode("utf-8")),
    )


def main() -> None:
    if not BASE_XML.exists():
        raise SystemExit(f"Missing base XML: {BASE_XML}")
    if not BASE_PDF.exists():
        raise SystemExit(f"Missing base PDF: {BASE_PDF}")
    generate_invalid_xml()
    generate_zugferd_edge_cases()
    print("done")


if __name__ == "__main__":
    main()
