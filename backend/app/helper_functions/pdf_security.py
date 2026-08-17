from __future__ import annotations

import re
from io import BytesIO
from typing import Final, Pattern

import PyPDF2

MAX_PDF_PAGES: Final[int] = 500
_ACTIVE_CONTENT_RE: Final[Pattern[bytes]] = re.compile(
    rb"/(?:JavaScript|JS|Launch|RichMedia|OpenAction|AA)(?=[\s<>\[\]()/%])"
)


class UnsafePdfError(ValueError):
    """Raised when a PDF is malformed or contains unsupported active content."""


def assert_pdf_safe(content: bytes) -> None:
    """Reject malformed, encrypted, oversized-page-count, and active-content PDFs."""
    if not content.startswith(b"%PDF-"):
        raise UnsafePdfError("Die Datei besitzt keine gültige PDF-Signatur.")
    if b"%%EOF" not in content[-4096:]:
        raise UnsafePdfError("Die PDF-Datei ist unvollständig oder beschädigt.")
    if _ACTIVE_CONTENT_RE.search(content):
        raise UnsafePdfError(
            "PDF mit JavaScript, automatischen Aktionen oder aktiven Inhalten "
            "wird aus Sicherheitsgründen nicht verarbeitet."
        )

    try:
        reader: PyPDF2.PdfReader = PyPDF2.PdfReader(BytesIO(content), strict=True)
        if reader.is_encrypted:
            raise UnsafePdfError("Verschlüsselte PDF-Dateien werden nicht unterstützt.")
        page_count: int = len(reader.pages)
    except UnsafePdfError:
        raise
    except Exception as exc:
        raise UnsafePdfError("Die PDF-Datei ist beschädigt oder nicht lesbar.") from exc

    if page_count > MAX_PDF_PAGES:
        raise UnsafePdfError(
            f"PDF mit mehr als {MAX_PDF_PAGES} Seiten wird aus Sicherheitsgründen abgelehnt."
        )
