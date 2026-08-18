from typing import List

from app.core.config import settings
from app.schemas.product import CapabilitiesResponse, SupportedFormat
from app.services.validation_profile import load_scenarios_meta


def build_capabilities() -> CapabilitiesResponse:
    """Return guest Empfang limits and supported formats from live settings."""
    meta: dict[str, object] = load_scenarios_meta()
    standard: str = _meta_str(meta, "standard", "EN 16931:2017")
    xrechnung: str = _meta_str(meta, "xrechnung_version", "3.0.2")
    return CapabilitiesResponse(
        max_upload_size_mb=settings.max_upload_size_mb,
        allowed_extensions=list(settings.allowed_extensions),
        max_files_per_request=1,
        rate_limit_per_minute=settings.rate_limit_per_minute,
        stores_invoice_files=False,
        requires_account=False,
        processing_model="guest",
        standard_version=standard,
        xrechnung_version=xrechnung,
        formats=_supported_formats(),
        profiles=[
            standard,
            f"XRechnung {xrechnung}",
            "ZUGFeRD / Factur-X EN 16931",
        ],
        limitations=_limitations(settings.max_upload_size_mb),
    )


def _supported_formats() -> List[SupportedFormat]:
    return [
        SupportedFormat(
            id="ubl_invoice",
            label="XRechnung UBL Invoice",
            extensions=[".xml"],
            notes="EN 16931 UBL Invoice.",
        ),
        SupportedFormat(
            id="ubl_credit_note",
            label="XRechnung UBL CreditNote",
            extensions=[".xml"],
            notes="EN 16931 UBL CreditNote.",
        ),
        SupportedFormat(
            id="cii",
            label="UN/CEFACT CII",
            extensions=[".xml"],
            notes="Cross Industry Invoice XML.",
        ),
        SupportedFormat(
            id="zugferd_pdf",
            label="ZUGFeRD / Factur-X",
            extensions=[".pdf"],
            notes="PDF with embedded invoice XML.",
        ),
    ]


def _limitations(max_upload_size_mb: int) -> List[str]:
    return [
        f"Eine Datei pro Anfrage, maximal {max_upload_size_mb} MB.",
        "Gastmodus: die Datei wird nur während der Anfrage verarbeitet und danach gelöscht.",
        "Normale PDFs ohne eingebettetes XML, Scans, openTRANS und andere XML-Formate werden abgelehnt.",
        "Der DATEV-Export ist eine Buchungsstapel-CSV und kein DATEVconnect.",
        "Keine Vorsteuer- oder Rechtsgarantie.",
    ]


def _meta_str(meta: dict[str, object], key: str, fallback: str) -> str:
    value: object = meta.get(key)
    if isinstance(value, str) and value.strip():
        return value.strip()
    return fallback
