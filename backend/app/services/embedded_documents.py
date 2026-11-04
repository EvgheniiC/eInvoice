"""Map XML attachments onto the public invoice DTO and drop bytes before storage."""

from __future__ import annotations

import logging
from typing import Optional

from app.core.error_events import log_event
from app.invoice_handler.xml_pdf_extraction import ExtractedEmbeddedFile, extract_embedded_files
from app.schemas.invoice import EmbeddedDocument, InvoiceParseResponse
from app.services.pdf_xml_extractor import extract_embedded_xml_from_pdf


def embedded_documents_from_xml(xml_text: str) -> list[EmbeddedDocument]:
    """Read supplier attachments. A broken attachment node does not fail the invoice."""
    try:
        extracted: list[ExtractedEmbeddedFile] = extract_embedded_files(xml_text)
    except Exception as exc:
        log_event(
            logging.WARNING,
            "embedded_documents_failed",
            fields={"exc_type": type(exc).__name__},
        )
        return []
    return [_to_document(item) for item in extracted]


def embedded_documents_from_upload(filename: str, content: bytes) -> list[EmbeddedDocument]:
    """Read attachments from an uploaded XRechnung XML or ZUGFeRD PDF."""
    xml_text: Optional[str] = _invoice_xml(filename, content)
    if xml_text is None:
        return []
    return embedded_documents_from_xml(xml_text)


def without_embedded_content(invoice: InvoiceParseResponse) -> InvoiceParseResponse:
    """Copy the invoice with attachment bytes removed. The original object stays intact."""
    if not any(document.content_base64 for document in invoice.embedded_documents):
        return invoice
    return invoice.model_copy(
        update={
            "embedded_documents": [
                document.model_copy(update={"content_base64": None})
                for document in invoice.embedded_documents
            ]
        }
    )


def _to_document(item: ExtractedEmbeddedFile) -> EmbeddedDocument:
    return EmbeddedDocument(
        filename=item.filename,
        media_type=item.media_type,
        size_bytes=item.size_bytes,
        content_base64=item.content_base64,
    )


def _invoice_xml(filename: str, content: bytes) -> Optional[str]:
    suffix: str = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if suffix == "pdf":
        return extract_embedded_xml_from_pdf(content)
    return _decode_xml(content)


def _decode_xml(content: bytes) -> Optional[str]:
    for encoding in ("utf-8-sig", "utf-8", "utf-16", "latin-1"):
        try:
            text: str = content.decode(encoding)
        except UnicodeDecodeError:
            continue
        if text.lstrip().startswith("<"):
            return text
    return None
