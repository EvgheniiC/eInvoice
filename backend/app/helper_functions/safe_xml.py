"""Safe XML parsing helpers (XXE / DTD / entity expansion / complexity)."""

from __future__ import annotations

import re
from typing import Final, List, Tuple
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import ParseError as EtParseError

from defusedxml import ElementTree as DefusedET
from defusedxml.common import DefusedXmlException

# Invoice XML must not carry DTD / entity declarations.
_FORBIDDEN_MARKUP_RE: Final[re.Pattern[str]] = re.compile(
    r"<!DOCTYPE|<!ENTITY",
    re.IGNORECASE,
)

MAX_XML_DEPTH: Final[int] = 80
MAX_XML_ELEMENTS: Final[int] = 100_000


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


def assert_xml_complexity(root: Element) -> None:
    """Reject XML trees that are too deep or too large for invoice processing."""
    count: int = 0
    stack: List[Tuple[Element, int]] = [(root, 1)]
    while stack:
        node, depth = stack.pop()
        count += 1
        if depth > MAX_XML_DEPTH:
            raise UnsafeXmlError(
                "XML ist zu tief verschachtelt und wurde aus Sicherheitsgründen abgelehnt."
            )
        if count > MAX_XML_ELEMENTS:
            raise UnsafeXmlError(
                "XML enthält zu viele Elemente und wurde aus Sicherheitsgründen abgelehnt."
            )
        for child in list(node):
            stack.append((child, depth + 1))


def parse_xml(xml_text: str) -> Element:
    """
    Parse XML with defusedxml (no external entities, no DTD, limited entities).

    Raises:
        UnsafeXmlError: forbidden constructs or excessive complexity
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
    assert_xml_complexity(root)
    return root
