"""Safe XML parsing helpers (XXE / DTD / entity expansion)."""

from __future__ import annotations

import re
from typing import Final
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import ParseError as EtParseError

from defusedxml import ElementTree as DefusedET
from defusedxml.common import DefusedXmlException

# Invoice XML must not carry DTD / entity declarations.
_FORBIDDEN_MARKUP_RE: Final[re.Pattern[str]] = re.compile(
    r"<!DOCTYPE|<!ENTITY",
    re.IGNORECASE,
)


class UnsafeXmlError(ValueError):
    """Raised when uploaded XML uses forbidden DTD/entity features."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message: str = message


def assert_xml_safe(xml_text: str) -> None:
    """
    Reject XML that declares a DTD or entities (XXE / billion-laughs vectors).

    XRechnung / ZUGFeRD invoices do not need DOCTYPE or ENTITY declarations.
    """
    if _FORBIDDEN_MARKUP_RE.search(xml_text):
        raise UnsafeXmlError(
            "XML enthält DOCTYPE/ENTITY-Deklarationen und wurde aus "
            "Sicherheitsgründen abgelehnt (XXE-/Entity-Schutz)."
        )


def parse_xml(xml_text: str) -> Element:
    """
    Parse XML with defusedxml (no external entities, no DTD, limited entities).

    Raises:
        UnsafeXmlError: forbidden constructs
        EtParseError: not well-formed XML
    """
    assert_xml_safe(xml_text)
    try:
        root: Element = DefusedET.fromstring(xml_text)
    except DefusedXmlException as exc:
        raise UnsafeXmlError(
            "XML enthält unerlaubte Konstrukte (DTD/Entities) und wurde abgelehnt."
        ) from exc
    except EtParseError:
        raise
    return root
