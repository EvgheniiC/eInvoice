"""Embed Factur-X XML into the issuer PDF as PDF/A-3."""

from __future__ import annotations


class IssueEmbedError(Exception):
    """The ZUGFeRD container could not be built."""


def embed_facturx(pdf_bytes: bytes, xml_bytes: bytes) -> bytes:
    """Return a Factur-X PDF. Raises IssueEmbedError when embedding fails."""
    try:
        from facturx import generate_from_binary
    except ImportError as exc:
        raise IssueEmbedError(
            "ZUGFeRD-Einbettung ist in dieser Installation nicht verfügbar."
        ) from exc

    try:
        embedded: object = generate_from_binary(
            pdf_bytes,
            xml_bytes,
            flavor="factur-x",
            level="en16931",
            check_xsd=False,
            check_schematron=False,
        )
    except Exception as exc:
        raise IssueEmbedError("Das PDF konnte nicht als ZUGFeRD eingebettet werden.") from exc

    if not isinstance(embedded, (bytes, bytearray)) or not bytes(embedded).startswith(b"%PDF-"):
        raise IssueEmbedError("Die Einbettung lieferte kein PDF.")
    return bytes(embedded)
