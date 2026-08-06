import tempfile
import uuid
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from app.data_class.XmlInvoiceHeader import XmlInvoiceHeader
from app.helper_functions.einvoice_helper import is_zugpferd_pdf
from app.invoice_handler.xml_parser_header import get_xml_header
from app.invoice_handler.xml_parser_positions import get_xml_positions
from app.invoice_handler.xml_vendor_parser import get_einvoice_vendor_data
from app.schemas.invoice import (
    InvoiceParseResponse,
    ParseStatus,
    ValidationIssue,
    ValidationStatus,
)
from app.services.en16931_validator import ValidationResult, validate_invoice
from app.services.invoice_mapper import build_next_steps, map_to_parse_response
from app.services.logger_adapter import ServiceLogger
from app.services.pdf_xml_extractor import extract_embedded_xml_from_pdf
from app.services.zugferd_consistency import compare_pdf_with_xml


class InvoiceService:
    """Facade over existing XML/PDF parsers for the public upload API."""

    def detect_file_type(self, filename: str, content: bytes) -> str:
        """Detect whether the upload is XML, ZUGFeRD PDF, plain PDF, or unsupported."""
        suffix: str = Path(filename).suffix.lower()
        if suffix == ".xml":
            return "xrechnung_xml"
        if suffix == ".pdf":
            if content[:4] != b"%PDF":
                return "pdf_unknown"
            if self._is_zugferd_content(content):
                return "zugferd_pdf"
            return "pdf_unknown"
        return "unsupported"

    def parse_upload(self, filename: str, content: bytes) -> InvoiceParseResponse:
        """Parse an uploaded invoice file into the public DTO."""
        file_type: str = self.detect_file_type(filename=filename, content=content)

        if file_type == "unsupported":
            return self._error_response(
                filename=filename,
                file_type=file_type,
                message="Nicht unterstützter Dateityp. Erlaubt: .xml / .pdf",
                code="UNSUPPORTED_TYPE",
                detail="Nur XRechnung-XML oder ZUGFeRD-PDF werden unterstützt.",
            )

        if file_type == "pdf_unknown":
            return self._error_response(
                filename=filename,
                file_type=file_type,
                message="PDF ohne eingebettetes ZUGFeRD/Factur-X XML.",
                code="NOT_ZUGFERD",
                detail=(
                    "Die PDF enthält kein erkennbares eingebettetes Rechnungs-XML. "
                    "Bitte XRechnung-XML oder ZUGFeRD-PDF verwenden."
                ),
            )

        xml_text: Optional[str] = None
        if file_type == "xrechnung_xml":
            xml_text = self._decode_xml(content)
            if xml_text is None:
                return self._error_response(
                    filename=filename,
                    file_type=file_type,
                    message="XML-Datei konnte nicht gelesen werden (Encoding).",
                    code="XML_DECODE_ERROR",
                    detail="Die Datei ist kein gültiges UTF-8/UTF-16 XML.",
                )
        elif file_type == "zugferd_pdf":
            xml_text = extract_embedded_xml_from_pdf(content)
            if xml_text is None:
                return self._error_response(
                    filename=filename,
                    file_type=file_type,
                    message="ZUGFeRD erkannt, aber eingebettetes XML konnte nicht extrahiert werden.",
                    code="ZUGFERD_XML_EXTRACT_FAILED",
                    detail="Embedded XML fehlt oder ist beschädigt.",
                )

        assert xml_text is not None
        try:
            header, vendor_data = self._run_parsers(xml_text=xml_text)
        except Exception as exc:
            return self._error_response(
                filename=filename,
                file_type=file_type,
                message="Fehler beim Parsen der Rechnung.",
                code="PARSE_EXCEPTION",
                detail=str(exc),
            )

        response: InvoiceParseResponse = map_to_parse_response(
            filename=filename,
            file_type=file_type,
            header=header,
            vendor_data=vendor_data,
        )

        if response.status == ParseStatus.ERROR:
            response.next_steps = build_next_steps(response)
            return response

        validation: ValidationResult = validate_invoice(xml_text=xml_text, parsed=response)
        response.validation_status = validation.status
        response.validation_issues.extend(validation.issues)

        if file_type == "zugferd_pdf":
            mismatch_fields, mismatch_warnings, mismatch_issues = compare_pdf_with_xml(
                pdf_content=content,
                parsed=response,
            )
            response.mismatch_fields = mismatch_fields
            response.mismatch_warnings = mismatch_warnings
            response.validation_issues.extend(mismatch_issues)
            if any(not item.matched for item in mismatch_fields if item.xml_value):
                if response.validation_status == ValidationStatus.VALID:
                    response.validation_status = ValidationStatus.WARNING

        response = self._refresh_status_message(response)
        response.next_steps = build_next_steps(response)
        return response

    def _refresh_status_message(self, response: InvoiceParseResponse) -> InvoiceParseResponse:
        has_schema_error: bool = any(
            issue.level == "error" and issue.category == "schema"
            for issue in response.validation_issues
        )
        has_business_error: bool = any(
            issue.level == "error" and issue.category == "business"
            for issue in response.validation_issues
        )
        has_mismatch: bool = any(
            not item.matched for item in response.mismatch_fields if item.xml_value
        )

        if has_schema_error or has_business_error:
            response.status = ParseStatus.PARTIAL if response.invoice_number else ParseStatus.ERROR
            response.message = "Rechnung gelesen, aber Validierung meldet Fehler."
        elif has_mismatch:
            response.status = ParseStatus.PARTIAL
            response.message = "Rechnung gelesen — PDF und XML weichen ab."
        elif response.validation_status == ValidationStatus.WARNING:
            response.status = ParseStatus.PARTIAL
            response.message = "Rechnung gelesen — bitte Warnungen prüfen."
        elif response.status != ParseStatus.ERROR:
            response.status = ParseStatus.SUCCESS
            response.message = "Rechnung erfolgreich gelesen und geprüft."
        return response

    def _error_response(
        self,
        *,
        filename: str,
        file_type: str,
        message: str,
        code: str,
        detail: str,
    ) -> InvoiceParseResponse:
        response: InvoiceParseResponse = InvoiceParseResponse(
            status=ParseStatus.ERROR,
            message=message,
            filename=filename,
            file_type=file_type,
            validation_status=ValidationStatus.INVALID,
            validation_issues=[
                ValidationIssue(
                    level="error",
                    category="schema",
                    code=code,
                    message=detail,
                )
            ],
        )
        response.next_steps = build_next_steps(response)
        return response

    def _run_parsers(self, xml_text: str) -> Tuple[XmlInvoiceHeader, Dict[str, Any]]:
        logger: ServiceLogger = ServiceLogger()
        job_id: str = uuid.uuid4().hex[:12]

        header: XmlInvoiceHeader = XmlInvoiceHeader(invoice_id=job_id)
        header = get_xml_header(xml_text=xml_text, xml_invoice_data=header, logger=logger)
        header = get_xml_positions(xml_text=xml_text, xml_invoice_data=header, logger=logger)
        vendor_data, _vendor_code = get_einvoice_vendor_data(
            invoice_id=job_id,
            xml_text=xml_text,
            logger=logger,
        )
        return header, vendor_data

    def _decode_xml(self, content: bytes) -> Optional[str]:
        for encoding in ("utf-8-sig", "utf-8", "utf-16", "latin-1"):
            try:
                text: str = content.decode(encoding)
            except UnicodeDecodeError:
                continue
            if text.lstrip().startswith("<"):
                return text
        return None

    def _is_zugferd_content(self, content: bytes) -> bool:
        tmp_path: Optional[str] = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp.write(content)
                tmp_path = tmp.name
            return bool(is_zugpferd_pdf(tmp_path))
        except Exception:
            return False
        finally:
            if tmp_path is not None:
                Path(tmp_path).unlink(missing_ok=True)
