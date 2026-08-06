from __future__ import annotations

import logging
import re
from typing import Any, List, Optional, Union
from xml.etree.ElementTree import Element

from .tags_config import load_config

logger: logging.Logger = logging.getLogger(__name__)


def extract_value(text: str, keyword: str) -> str:
    """
    Extract value from text after a keyword or colon.

    Supports:
    - "Keyword : Value"
    - "Keyword Value"
    - "Keyword : Value - Description"
    """
    match: Optional[re.Match[str]] = re.search(r":\s*(.+?)(?:\s*-\s*(.+))?$", text)
    if match:
        value: str = match.group(1).strip()
        description: Optional[str] = match.group(2).strip() if match.group(2) else None
        if description:
            return f"{value} - {description}"
        return value

    pattern: str = rf"{re.escape(keyword)}\s+(.+?)(?:\s*-\s*(.+))?$"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        value = match.group(1).strip()
        description = match.group(2).strip() if match.group(2) else None
        if description:
            return f"{value} - {description}"
        return value

    return text


def find_value_by_keywords(
    root: Element, keywords: Union[str, List[str]]
) -> Optional[str]:
    """Search AdditionalDocumentReference/ID nodes for keyword matches."""
    keyword_list: List[str] = [keywords] if isinstance(keywords, str) else list(keywords)

    for ref in root.iter("AdditionalDocumentReference"):
        id_elem: Optional[Element] = ref.find("ID")
        if id_elem is not None and id_elem.text:
            id_text: str = id_elem.text.strip()
            for keyword in keyword_list:
                if keyword.lower() in id_text.lower():
                    return extract_value(id_text, keyword)
    return None


def get_field_value(
    xml_text: Element,
    field_name: str,
    config_path: str = "config/fields.json",
) -> Optional[str]:
    """Extract a configured field value (e.g. cost_center, legal_entity) from XML."""
    config: dict[str, Any] = load_config(config_path)

    if field_name not in config:
        logger.warning("Field '%s' not found in fields.json", field_name)
        return None

    keywords: Any = config[field_name]
    if isinstance(keywords, str):
        return find_value_by_keywords(xml_text, keywords)
    if isinstance(keywords, list):
        return find_value_by_keywords(xml_text, [str(item) for item in keywords])
    return None
