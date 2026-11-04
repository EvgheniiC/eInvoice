"""Read supplier files embedded in a UBL or CII invoice."""

from __future__ import annotations

import base64
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Optional
from xml.etree.ElementTree import Element, tostring

import xmltodict

from ..helper_functions import get_xml_tree

# The live parse response carries these bytes. Cap count and size so one
# invoice cannot turn the JSON response into an unbounded download.
MAX_EMBEDDED_DOCUMENTS: int = 10
MAX_EMBEDDED_DOCUMENT_BYTES: int = 20 * 1024 * 1024

_MEDIA_TYPE_RE: re.Pattern[str] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9!#$&^_.+-]{0,127}/[A-Za-z0-9][A-Za-z0-9!#$&^_.+-]{0,127}$"
)
_FILENAME_FORBIDDEN: re.Pattern[str] = re.compile(r"[\x00-\x1f<>:\"/\\|?*]")
# Active content must not be offered for inline display.
_BLOCKED_MEDIA_TYPES: frozenset[str] = frozenset(
    {"text/html", "image/svg+xml", "application/xhtml+xml"}
)
_EXTENSION_MEDIA: dict[str, str] = {
    "pdf": "application/pdf",
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "gif": "image/gif",
    "webp": "image/webp",
    "csv": "text/csv",
    "txt": "text/plain",
    "xml": "application/xml",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "ods": "application/vnd.oasis.opendocument.spreadsheet",
}
_MEDIA_EXTENSION: dict[str, str] = {
    "application/pdf": ".pdf",
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/gif": ".gif",
    "image/webp": ".webp",
    "text/csv": ".csv",
    "text/plain": ".txt",
    "application/xml": ".xml",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
    "application/vnd.oasis.opendocument.spreadsheet": ".ods",
}


@dataclass(frozen=True)
class ExtractedEmbeddedFile:
    """One binary object from AdditionalDocumentReference or AdditionalReferencedDocument."""

    filename: str
    media_type: str
    size_bytes: int
    content_base64: Optional[str]


def extract_embedded_files(xml_text: str) -> list[ExtractedEmbeddedFile]:
    """Return supplier attachments from UBL Invoice/CreditNote or CII XML."""
    try:
        data_dict: dict[str, Any] = _parsed_xml_dict(xml_text)
    except Exception:
        return []

    found: list[ExtractedEmbeddedFile] = []
    for root_name in ("Invoice", "CreditNote"):
        root: Any = data_dict.get(root_name)
        if isinstance(root, dict):
            found.extend(_ubl_files(root))
    cii_root: Any = data_dict.get("CrossIndustryInvoice")
    if isinstance(cii_root, dict):
        found.extend(_cii_files(cii_root))
    return found[:MAX_EMBEDDED_DOCUMENTS]


def get_pdf_file(invoice_id: str, xml_text: str) -> Optional[list]:
    """Legacy attachment dicts. Prefer extract_embedded_files for new callers."""
    files: list[ExtractedEmbeddedFile] = extract_embedded_files(xml_text)
    attachments: list[dict[str, Any]] = []
    for item in files:
        if not item.content_base64:
            continue
        suffix: str = Path(item.filename).suffix.lower().lstrip(".")
        attachments.append(
            {
                "invoice_id": invoice_id,
                "attachment": item.content_base64,
                "file_name": item.filename,
                "file_type": suffix or "pdf",
            }
        )
    return attachments or None


def _parsed_xml_dict(xml_text: str) -> dict[str, Any]:
    xml_tree: Element = get_xml_tree(xml_text)
    xml_str: str = tostring(xml_tree).decode()
    # disable_entities is True by default; keep explicit for XXE safety
    xml_dict: dict[str, Any] = xmltodict.parse(xml_str, disable_entities=True)
    loaded: Any = json.loads(json.dumps(xml_dict))
    if isinstance(loaded, dict):
        return loaded
    return {}


def _ubl_files(invoice_data: dict[str, Any]) -> list[ExtractedEmbeddedFile]:
    documents: list[ExtractedEmbeddedFile] = []
    for doc in _as_dict_list(invoice_data.get("AdditionalDocumentReference")):
        fallback_name: Optional[str] = _first_text(doc, ("DocumentDescription", "ID"))
        for attachment in _as_dict_list(doc.get("Attachment")):
            for embedded in _binary_nodes(attachment.get("EmbeddedDocumentBinaryObject")):
                entry: Optional[ExtractedEmbeddedFile] = _file_from_binary(
                    embedded, fallback_name, len(documents) + 1
                )
                if entry is not None:
                    documents.append(entry)
    return documents


def _cii_files(data: dict[str, Any]) -> list[ExtractedEmbeddedFile]:
    documents: list[ExtractedEmbeddedFile] = []
    for doc in _collect_nodes_by_key(data, "AdditionalReferencedDocument"):
        fallback_name: Optional[str] = _first_text(doc, ("Name", "IssuerAssignedID"))
        for embedded in _binary_nodes(doc.get("AttachmentBinaryObject")):
            entry: Optional[ExtractedEmbeddedFile] = _file_from_binary(
                embedded, fallback_name, len(documents) + 1
            )
            if entry is not None:
                documents.append(entry)
    return documents


def _file_from_binary(
    embedded: Any,
    fallback_name: Optional[str],
    index: int,
) -> Optional[ExtractedEmbeddedFile]:
    payload: Optional[str] = None
    attr_name: Optional[str] = None
    mime_code: Optional[str] = None

    if isinstance(embedded, str):
        payload = embedded.strip() or None
    elif isinstance(embedded, dict):
        payload = _text_value(embedded.get("#text"))
        attr_name = _text_value(embedded.get("@filename"))
        mime_code = _text_value(embedded.get("@mimeCode"))

    if not payload:
        return None

    decoded: Optional[bytes] = _decode_base64(payload)
    if decoded is None or len(decoded) == 0:
        return None

    media_type: str = _media_type(mime_code, attr_name or fallback_name)
    filename: str = _display_filename(attr_name or fallback_name, index, media_type)
    content_base64: Optional[str] = _compact_base64(payload)
    if len(decoded) > MAX_EMBEDDED_DOCUMENT_BYTES:
        content_base64 = None
    return ExtractedEmbeddedFile(
        filename=filename,
        media_type=media_type,
        size_bytes=len(decoded),
        content_base64=content_base64,
    )


def _as_dict_list(value: Any) -> List[dict[str, Any]]:
    """Normalize xmltodict single-or-list nodes into a list of dicts."""
    if value is None:
        return []
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if isinstance(value, dict):
        return [value]
    return []


def _binary_nodes(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _collect_nodes_by_key(data: Any, key: str) -> List[dict[str, Any]]:
    """Find all dict nodes named `key` anywhere in a parsed XML tree."""
    found: List[dict[str, Any]] = []
    if isinstance(data, dict):
        if key in data:
            found.extend(_as_dict_list(data[key]))
        for child in data.values():
            found.extend(_collect_nodes_by_key(child, key))
    elif isinstance(data, list):
        for item in data:
            found.extend(_collect_nodes_by_key(item, key))
    return found


def _first_text(node: dict[str, Any], keys: tuple[str, ...]) -> Optional[str]:
    for key in keys:
        text: Optional[str] = _text_value(node.get(key))
        if text:
            return text
    return None


def _text_value(value: Any) -> Optional[str]:
    if isinstance(value, str):
        stripped: str = value.strip()
        return stripped or None
    if isinstance(value, dict):
        return _text_value(value.get("#text"))
    return None


def _decode_base64(payload: str) -> Optional[bytes]:
    compact: str = "".join(payload.split())
    if not compact:
        return None
    padding: int = (-len(compact)) % 4
    if padding:
        compact = compact + ("=" * padding)
    try:
        return base64.b64decode(compact, validate=True)
    except Exception:
        return None


def _compact_base64(payload: str) -> str:
    compact: str = "".join(payload.split())
    padding: int = (-len(compact)) % 4
    if padding:
        return compact + ("=" * padding)
    return compact


def _media_type(mime_code: Optional[str], filename: Optional[str]) -> str:
    if mime_code:
        candidate: str = mime_code.split(";", 1)[0].strip().lower()
        if candidate in _BLOCKED_MEDIA_TYPES:
            return "application/octet-stream"
        if _MEDIA_TYPE_RE.fullmatch(candidate):
            return candidate
    extension: str = Path(filename or "").suffix.lower().lstrip(".")
    return _EXTENSION_MEDIA.get(extension, "application/octet-stream")


def _display_filename(raw_name: Optional[str], index: int, media_type: str) -> str:
    name: str = Path(raw_name or "").name
    name = _FILENAME_FORBIDDEN.sub("_", name).strip(" .")
    if not name or name in {".", ".."}:
        return f"anhang-{index}{_MEDIA_EXTENSION.get(media_type, '')}"
    if len(name) > 180:
        suffix: str = Path(name).suffix[:20]
        stem: str = Path(name).stem[: 180 - len(suffix)]
        name = f"{stem}{suffix}"
    return name
