from typing import Any, Dict, List, Optional
from xml.etree.ElementTree import Element, tostring
import json

import xmltodict

from ..helper_functions import get_xml_tree


def _as_dict_list(value: Any) -> List[dict]:
    """Normalize xmltodict single-or-list nodes into a list of dicts."""
    if value is None:
        return []
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if isinstance(value, dict):
        return [value]
    return []


def _collect_nodes_by_key(data: Any, key: str) -> List[dict]:
    """Find all dict nodes named `key` anywhere in a parsed XML tree."""
    found: List[dict] = []
    if isinstance(data, dict):
        if key in data:
            found.extend(_as_dict_list(data[key]))
        for child in data.values():
            found.extend(_collect_nodes_by_key(child, key))
    elif isinstance(data, list):
        for item in data:
            found.extend(_collect_nodes_by_key(item, key))
    return found


def _file_entry_from_binary(
    invoice_id: str,
    embedded: Any,
    fallback_name: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Build an attachment dict from a UBL or CII binary object node."""
    file_name: Optional[str] = fallback_name
    payload: Optional[str] = None

    if isinstance(embedded, str):
        payload = embedded.strip() or None
    elif isinstance(embedded, dict):
        raw_text: Any = embedded.get("#text")
        if isinstance(raw_text, str):
            payload = raw_text.strip() or None
        attr_name: Any = embedded.get("@filename")
        if isinstance(attr_name, str) and attr_name.strip():
            file_name = attr_name.strip()

    if not payload:
        return None

    return {
        "invoice_id": invoice_id,
        "attachment": payload,
        "file_name": file_name,
        "file_type": file_name.split(".")[-1] if file_name else "pdf",
    }


def extract_pdf_attachments(invoice_id: str, data: dict, key: str) -> list:
    """
    Extracts all PDF attachments from the specified key in the data dictionary.

    Args:
        invoice_id: Neutral invoice identifier.
        data: The dictionary containing the data.
        key: The key under which to extract the values.

    Returns:
        List of dictionaries containing attachment information.
    """
    additional_documents: Any = data.get(key, [])

    if not isinstance(additional_documents, list):
        additional_documents = [additional_documents]

    attachments: List[Dict[str, Any]] = []

    for doc in additional_documents:
        if not isinstance(doc, dict) or "Attachment" not in doc:
            continue

        try:
            attachment: Any = doc["Attachment"]
            if "EmbeddedDocumentBinaryObject" not in attachment:
                continue

            file_entry: Optional[Dict[str, Any]] = _file_entry_from_binary(
                invoice_id, attachment["EmbeddedDocumentBinaryObject"]
            )
            if file_entry:
                attachments.append(file_entry)

        except Exception:
            continue

    return attachments


def extract_cii_pdf_attachments(invoice_id: str, data: dict) -> list:
    """
    Extract PDF attachments from CII / XRechnung (CrossIndustryInvoice).

    CII stores supporting documents as AdditionalReferencedDocument with
    AttachmentBinaryObject, nested under the trade transaction — not as
    UBL AdditionalDocumentReference / EmbeddedDocumentBinaryObject.
    """
    attachments: List[Dict[str, Any]] = []

    for doc in _collect_nodes_by_key(data, "AdditionalReferencedDocument"):
        if "AttachmentBinaryObject" not in doc:
            continue

        fallback_name: Optional[str] = None
        for name_key in ("Name", "IssuerAssignedID"):
            raw_name: Any = doc.get(name_key)
            if isinstance(raw_name, str) and raw_name.strip():
                fallback_name = raw_name.strip()
                break

        try:
            file_entry: Optional[Dict[str, Any]] = _file_entry_from_binary(
                invoice_id, doc["AttachmentBinaryObject"], fallback_name
            )
            if file_entry:
                attachments.append(file_entry)
        except Exception:
            continue

    return attachments


def get_pdf_file(invoice_id: str, xml_text: str) -> Optional[list]:
    """Extract embedded PDF attachments from a UBL Invoice or CII XML document."""
    xml_tree: Element = get_xml_tree(xml_text)
    xml_str: str = tostring(xml_tree).decode()
    # disable_entities is True by default; keep explicit for XXE safety
    xml_dict: dict = xmltodict.parse(xml_str, disable_entities=True)
    data_dict: dict = json.loads(json.dumps(xml_dict, indent=4))

    try:
        if "Invoice" in data_dict:
            invoice_data: dict = data_dict["Invoice"]
            return extract_pdf_attachments(invoice_id, invoice_data, "AdditionalDocumentReference")
        if "CrossIndustryInvoice" in data_dict:
            cii_data: dict = data_dict["CrossIndustryInvoice"]
            return extract_cii_pdf_attachments(invoice_id, cii_data)
    except Exception:
        return None

    return None
