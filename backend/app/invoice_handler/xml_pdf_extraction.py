from typing import Any, Dict, List, Optional
from xml.etree.ElementTree import Element, tostring
import json

import xmltodict

from ..helper_functions import get_xml_tree


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
    additional_documents = data.get(key, [])

    if not isinstance(additional_documents, list):
        additional_documents = [additional_documents]

    attachments: List[Dict[str, Any]] = []

    for doc in additional_documents:
        if "Attachment" not in doc:
            continue

        try:
            attachment = doc["Attachment"]
            if "EmbeddedDocumentBinaryObject" not in attachment:
                continue

            embedded = attachment["EmbeddedDocumentBinaryObject"]
            file_name: Optional[str] = embedded.get("@filename")
            file_entry: Dict[str, Any] = {
                "invoice_id": invoice_id,
                "attachment": embedded.get("#text"),
                "file_name": file_name,
                "file_type": file_name.split(".")[-1] if file_name else "pdf",
            }

            if file_entry["attachment"]:
                attachments.append(file_entry)

        except Exception:
            continue

    return attachments


def get_pdf_file(invoice_id: str, xml_text: str) -> Optional[list]:
    """Extract embedded PDF attachments from an Invoice XML document."""
    xml_tree: Element = get_xml_tree(xml_text)
    xml_str: str = tostring(xml_tree).decode()
    # disable_entities is True by default; keep explicit for XXE safety
    xml_dict: dict = xmltodict.parse(xml_str, disable_entities=True)
    data_dict: dict = json.loads(json.dumps(xml_dict, indent=4))

    try:
        if "Invoice" in data_dict:
            invoice_data: dict = data_dict["Invoice"]
            return extract_pdf_attachments(invoice_id, invoice_data, "AdditionalDocumentReference")
    except Exception:
        return None

    return None
