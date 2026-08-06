from __future__ import annotations

import logging
from typing import Any, Optional

import PyPDF2

logger: logging.Logger = logging.getLogger(__name__)


def is_zugpferd_pdf(file_path: str) -> bool:
    """Return True if the PDF has embedded files typical for ZUGFeRD/Factur-X."""
    with open(file_path, "rb") as pdf_file:
        pdf_reader: PyPDF2.PdfReader = PyPDF2.PdfReader(pdf_file)
        file_names: Any = ""
        catalog: Any = None
        try:
            catalog = pdf_reader.trailer["/Root"]
        except Exception:
            logger.debug("PDF catalog /Root not found for %s", file_path)

        if catalog:
            try:
                file_names = catalog["/Names"]["/EmbeddedFiles"]["/Names"]
            except Exception:
                logger.debug("EmbeddedFiles /Names not found for %s", file_path)

            if not file_names:
                try:
                    file_names = catalog["/Names"]["/EmbeddedFiles"]["/Kids"]
                except Exception:
                    logger.debug("EmbeddedFiles /Kids not found for %s", file_path)

        return bool(file_names)
