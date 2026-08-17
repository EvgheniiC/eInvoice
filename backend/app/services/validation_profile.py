"""Extract EN 16931 / XRechnung / Factur-X profile identifiers from invoice XML."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import ParseError as EtParseError

from app.helper_functions.safe_xml import UnsafeXmlError, parse_xml

_META_PATH: Path = Path(__file__).parent / "validation_scenarios_meta.json"
_BT_RE: re.Pattern[str] = re.compile(r"\b(B[TG]-\d+[a-zA-Z]?)\b", re.IGNORECASE)
_XRECHNUNG_RE: re.Pattern[str] = re.compile(
    r"xrechnung(?:-extended)?[_:]?(\d+(?:\.\d+)*)",
    re.IGNORECASE,
)
_FACTURX_RE: re.Pattern[str] = re.compile(
    r"factur-x\.eu:([^:<\s]+):([^:<\s]+)",
    re.IGNORECASE,
)
_ZUGFERD_RE: re.Pattern[str] = re.compile(
    r"zugferd(?:\.de)?:([^:<\s]+):([^:<\s]+)",
    re.IGNORECASE,
)
_EN16931_RE: re.Pattern[str] = re.compile(
    r"en16931:(\d{4})",
    re.IGNORECASE,
)


@dataclass
class InvoiceProfile:
    """Detected invoice standard and CIUS/profile identifiers."""

    profile_id: Optional[str] = None
    profile: Optional[str] = None
    standard_version: Optional[str] = None


def load_scenarios_meta() -> Dict[str, Any]:
    """Load the pinned KoSIT / XRechnung scenario metadata file."""
    try:
        raw: Any = json.loads(_META_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(raw, dict):
        return {}
    return raw


def pinned_standard_version() -> str:
    meta: Dict[str, Any] = load_scenarios_meta()
    value: object = meta.get("standard")
    if isinstance(value, str) and value.strip():
        return value.strip()
    return "EN 16931:2017"


def extract_invoice_profile(xml_text: str) -> InvoiceProfile:
    """Read CustomizationID / guideline ID and map it to a readable profile."""
    profile_id: Optional[str] = _read_profile_id(xml_text)
    if not profile_id:
        return InvoiceProfile()
    return InvoiceProfile(
        profile_id=profile_id,
        profile=_human_profile_name(profile_id),
        standard_version=_standard_from_profile_id(profile_id),
    )


def extract_bt_code(*texts: Optional[str]) -> Optional[str]:
    """Return the first BT/BG identifier found in the given strings."""
    for text in texts:
        if not text:
            continue
        match: Optional[re.Match[str]] = _BT_RE.search(text)
        if match:
            return match.group(1).upper()
    return None


def _read_profile_id(xml_text: str) -> Optional[str]:
    try:
        root: Element = parse_xml(xml_text)
    except (UnsafeXmlError, EtParseError, ValueError):
        return None

    for element in root.iter():
        if _local_name(element.tag) == "CustomizationID" and element.text:
            value: str = element.text.strip()
            if value:
                return value

    for element in root.iter():
        if _local_name(element.tag) != "GuidelineSpecifiedDocumentContextParameter":
            continue
        for child in element.iter():
            if _local_name(child.tag) == "ID" and child.text:
                value = child.text.strip()
                if value:
                    return value
    return None


def _human_profile_name(profile_id: str) -> str:
    lowered: str = profile_id.lower()
    xr_match: Optional[re.Match[str]] = _XRECHNUNG_RE.search(profile_id)
    if xr_match:
        version: str = xr_match.group(1)
        if "extended" in lowered:
            return f"XRechnung {version} Extended"
        return f"XRechnung {version}"

    fx_match: Optional[re.Match[str]] = _FACTURX_RE.search(profile_id)
    if fx_match:
        fx_profile: str = fx_match.group(2)
        if fx_profile.lower() == "en16931":
            return "Factur-X EN 16931"
        return f"Factur-X {fx_profile}"

    zf_match: Optional[re.Match[str]] = _ZUGFERD_RE.search(profile_id)
    if zf_match:
        return f"ZUGFeRD {zf_match.group(1)} {zf_match.group(2)}"

    if "en16931" in lowered:
        return "EN 16931"
    return profile_id


def _standard_from_profile_id(profile_id: str) -> str:
    match: Optional[re.Match[str]] = _EN16931_RE.search(profile_id)
    if match:
        return f"EN 16931:{match.group(1)}"
    return pinned_standard_version()


def _local_name(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[-1]
    return tag.split(":")[-1]
