from io import BytesIO
from typing import Final, Optional

import PyPDF2

MAX_EMBEDDED_XML_BYTES: Final[int] = 10 * 1024 * 1024


def extract_embedded_xml_from_pdf(content: bytes) -> Optional[str]:
    """
    Extract the first embedded XML attachment from a ZUGFeRD / Factur-X PDF.

    Returns None if no XML attachment is found.
    """
    reader: PyPDF2.PdfReader = PyPDF2.PdfReader(BytesIO(content))

    attachments = getattr(reader, "attachments", None)
    if attachments:
        xml_text: Optional[str] = _xml_from_attachments(attachments)
        if xml_text is not None:
            return xml_text

    return _xml_from_name_tree(reader)


def _xml_from_attachments(attachments: dict[object, object]) -> Optional[str]:
    """Try PyPDF2/pypdf attachments mapping (name -> bytes or list of bytes)."""
    preferred: Optional[str] = None
    fallback: Optional[str] = None

    for name, payload in attachments.items():
        raw: Optional[bytes] = _normalize_attachment_payload(payload)
        if raw is None:
            continue
        decoded: Optional[str] = _decode_xml_bytes(raw)
        if decoded is None:
            continue
        name_lower: str = str(name).lower()
        if name_lower.endswith(".xml") or "zugferd" in name_lower or "factur" in name_lower:
            preferred = decoded
            break
        if fallback is None and decoded.lstrip().startswith("<"):
            fallback = decoded

    return preferred if preferred is not None else fallback


def _resolve(obj: object) -> object:
    """Resolve PDF IndirectObject references to concrete objects."""
    if hasattr(obj, "get_object"):
        try:
            return obj.get_object()
        except Exception:
            return obj
    return obj


def _xml_from_name_tree(reader: PyPDF2.PdfReader) -> Optional[str]:
    """Fallback: walk /Names /EmbeddedFiles name tree for XML streams."""
    try:
        root = _resolve(reader.trailer["/Root"])
        names = _resolve(root.get("/Names")) if hasattr(root, "get") else None
        if names is None:
            return None
        embedded = _resolve(names.get("/EmbeddedFiles")) if hasattr(names, "get") else None
        if embedded is None:
            return None
        name_list = embedded.get("/Names") if hasattr(embedded, "get") else None
        if not name_list:
            return None

        # Name tree pairs: [filename, filespec, filename, filespec, ...]
        for index in range(0, len(name_list), 2):
            if index + 1 >= len(name_list):
                break
            filespec = _resolve(name_list[index + 1])
            if filespec is None or not hasattr(filespec, "get"):
                continue
            ef_raw = filespec.get("/EF")
            ef = _resolve(ef_raw) if ef_raw is not None else None
            if ef is None or not hasattr(ef, "get"):
                continue
            stream = _resolve(ef.get("/F") or ef.get("/UF"))
            if stream is None or not hasattr(stream, "get_data"):
                continue
            data: bytes = stream.get_data()
            decoded: Optional[str] = _decode_xml_bytes(data)
            if decoded is not None:
                return decoded
    except Exception:
        return None
    return None


def _normalize_attachment_payload(payload: object) -> Optional[bytes]:
    if isinstance(payload, bytes):
        return payload if len(payload) <= MAX_EMBEDDED_XML_BYTES else None
    if isinstance(payload, list) and payload:
        first: object = payload[0]
        if isinstance(first, bytes):
            return first if len(first) <= MAX_EMBEDDED_XML_BYTES else None
    return None


def _decode_xml_bytes(raw: bytes) -> Optional[str]:
    if len(raw) > MAX_EMBEDDED_XML_BYTES:
        return None
    for encoding in ("utf-8", "utf-16", "latin-1"):
        try:
            text: str = raw.decode(encoding)
        except UnicodeDecodeError:
            continue
        stripped: str = text.lstrip("\ufeff").lstrip()
        if stripped.startswith("<"):
            return text
    return None
