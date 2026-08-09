from __future__ import annotations

import re
from datetime import datetime
from typing import List, Optional, Tuple
from xml.etree.ElementTree import Element

from .safe_xml import parse_xml
from .tags_config import load_mappings


def find_data_within_element(
    element: Optional[Element], tags: List[str], default: Optional[str] = None
) -> Optional[str]:
    """Return text of the first matching tag under element, or default."""
    if element is None:
        return default

    for tag in tags:
        data: Optional[Element] = element.find(tag)
        if data is not None and data.text:
            return data.text.strip()
    return default


def find_attribute_within_element(
    element: Optional[Element],
    tags: List[str],
    attribute_name: str,
    default: Optional[str] = None,
) -> Optional[str]:
    """
    Find and map an attribute value within an XML element.

    Returns the mapped value only if it exists in mapping_client.json.
    """
    if element is None:
        return default

    mappings: dict[str, str] = load_mappings()
    for tag in tags:
        data: Optional[Element] = element.find(tag)
        if data is not None:
            value: Optional[str] = data.get(attribute_name)
            if value:
                value = value.strip()
                if value in mappings:
                    return mappings[value]
    return default


def find_data_within_element_with_len(
    element: Optional[Element], tags: List[str], length: int
) -> Optional[str]:
    """Return text of the first tag whose stripped value has the given length."""
    if element is None:
        return None

    for tag in tags:
        data: Optional[Element] = element.find(tag)
        if data is not None and data.text:
            stripped: str = data.text.strip()
            if len(stripped.replace(" ", "")) == length:
                return stripped
    return None


def join_all_texts_for_tags(
    element: Optional[Element], tags: List[str], separator: str = "."
) -> Optional[str]:
    """
    Collect non-empty text from every element matching each XPath in tags,
    then join with separator.
    """
    if element is None:
        return None
    parts: List[str] = []
    for tag in tags:
        for node in element.findall(tag):
            if node.text:
                chunk: str = node.text.strip()
                if chunk:
                    parts.append(chunk)
    return separator.join(parts) if parts else None


def delete_all_prefills(xml_tree: Element) -> Element:
    """Remove namespace URI prefixes from all element tags in the tree."""
    for elem in xml_tree.iter():
        tag: str = elem.tag.split("}")[1] if "}" in elem.tag else elem.tag
        elem.tag = tag
    return xml_tree


def find_data_with_regex(element: Optional[Element], regex_pattern: str) -> Optional[str]:
    """Search concatenated element text with a regex; return first match."""
    if element is None:
        return None
    all_tags_data: str = " ".join(element.itertext())
    match: Optional[re.Match[str]] = re.search(regex_pattern, all_tags_data)
    if match:
        return match.group(0).strip().rstrip()
    return None


def get_xml_tree(xml_text: str) -> Element:
    """Parse XML text safely (no XXE/DTD) and strip namespace prefixes."""
    xml_tree: Element = parse_xml(xml_text)
    return delete_all_prefills(xml_tree)


def parse_xml_date(
    raw: Optional[str],
    formats: Tuple[str, ...] = ("%Y%m%d", "%Y-%m-%d"),
) -> Optional[datetime]:
    """Parse a date string trying formats in order; return None if all fail."""
    if not raw:
        return None
    for fmt in formats:
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    return None


def _xml_root_local_name(element: Element) -> str:
    """Return local name of an XML element tag, stripping namespace URI if present."""
    tag: str = element.tag
    if tag.startswith("{") and "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def _text_or_none(elem: Optional[Element]) -> Optional[str]:
    """Return stripped text of element or None if missing/empty."""
    if elem is not None and elem.text:
        return elem.text.strip()
    return None
