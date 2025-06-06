from ..helper_functions import get_xml_tree
from xml.etree.ElementTree import Element
import xmltodict
import json
from xml.etree.ElementTree import tostring
from typing import Optional


# many XML files have emdbebebe PDF File, most of all attachments is in teg AdditionalDocumentReference ->Attachment-> EmbeddedDocumentBinaryObject
# there may be many PDF files
def extract_pdf_attachments(m_cn_id: str, data: dict, key: str) -> {}:
    """
    This function extracts the values of "#text" and "@filename" from all elements under the specified key in the data dictionary.

    Args:
        m_cn_id (str): main id.
        data (dict): The dictionary containing the data.
        key (str): The key under which to extract the values.
    """

    # Get the list of elements under the specified key
    additional_documents = data.get(key, [])
    attachments = []

    for document in additional_documents:
        file = {"M_CN_ID": m_cn_id, "ATTACHMENT": None, "FILE_NAME": None, "FILE_TYPE": "pdf"}

        for sub_key, value in document.get("Attachment", {}).get("EmbeddedDocumentBinaryObject", {}).items():
            if sub_key == "#text":
                file["ATTACHMENT"] = value
            if sub_key == "@filename":
                file["FILE_NAME"] = value

        attachments.append(file)

    return attachments


# sometimes we have a PDF file embedded in an XML file
def get_pdf_file(m_cn_id: str, xml_text: str) -> Optional[dict]:
    xml_tree: Element = get_xml_tree(xml_text)
    xml_str: str = tostring(xml_tree).decode()
    xml_dict: dict = xmltodict.parse(xml_str)
    json_data = json.dumps(xml_dict, indent=4)
    data_dict: dict = json.loads(json_data)

    # at the moment XML have embedded PDF only if we have the tag Invoice
    if 'Invoice' in data_dict:
        invoice_data = data_dict['Invoice']
        return extract_pdf_attachments(m_cn_id, invoice_data, "AdditionalDocumentReference")

    return None