from ..helper_functions import get_xml_tree
from xml.etree.ElementTree import Element
import xmltodict
import json
from xml.etree.ElementTree import tostring
from typing import Optional


# old
# def extract_pdf_attachments(m_cn_id: str, data: dict, key: str) -> {}:
#     """
#     This function extracts the values of "#text" and "@filename" from all elements under the specified key in the data dictionary.
#
#     Args:
#         m_cn_id (str): main id.
#         data (dict): The dictionary containing the data.
#         key (str): The key under which to extract the values.
#     """
#
#     # Get the list of elements under the specified key
#     additional_documents = data.get(key, [])
#     attachments = []
#
#     if 'Attachment' in additional_documents:
#         invoice_data: dict = additional_documents['Attachment']
#         file = {"M_CN_ID": m_cn_id, "ATTACHMENT": None, "FILE_NAME": None, "FILE_TYPE": "pdf"}
#
#         for sub_key, value in invoice_data['EmbeddedDocumentBinaryObject'].items():
#             if sub_key == "#text":
#                 file["ATTACHMENT"] = value
#             if sub_key == "@filename":
#                 file["FILE_NAME"] = value
#
#         attachments.append(file)
#
#     return attachments

# many XML files have emdbebebe PDF File, most of all attachments is in teg AdditionalDocumentReference ->Attachment-> EmbeddedDocumentBinaryObject
# there may be many PDF files
def extract_pdf_attachments(m_cn_id: str, data: dict, key: str) -> list:
    """
    Extracts all PDF attachments from the specified key in the data dictionary.

    Args:
        m_cn_id (str): Main ID.
        data (dict): The dictionary containing the data.
        key (str): The key under which to extract the values.

    Returns:
        list: List of dictionaries containing attachment information.
    """
    # Get the list of elements under the specified key
    additional_documents = data.get(key, [])

    # Ensure it's a list
    if not isinstance(additional_documents, list):
        additional_documents = [additional_documents]

    attachments = []

    # Iterate through all documents
    for doc in additional_documents:
        # Check if this document has an Attachment
        if 'Attachment' not in doc:
            continue

        try:
            attachment = doc['Attachment']

            # Check if EmbeddedDocumentBinaryObject exists
            if 'EmbeddedDocumentBinaryObject' not in attachment:
                continue

            embedded = attachment['EmbeddedDocumentBinaryObject']

            # Extract data
            file = {
                "M_CN_ID": m_cn_id,
                "ATTACHMENT": embedded.get('#text'),
                "FILE_NAME": embedded.get('@filename'),
                "FILE_TYPE": "pdf"
            }

            # Only add if we have at least the attachment content
            if file["ATTACHMENT"]:
                attachments.append(file)

        except Exception as e:
            print(f"Error processing attachment in document {doc.get('ID', 'unknown')}: {e}")
            continue

    return attachments


# sometimes we have a PDF file embedded in an XML file
def get_pdf_file(m_cn_id: str, xml_text: str) -> Optional[list]:
    xml_tree: Element = get_xml_tree(xml_text)
    xml_str: str = tostring(xml_tree).decode()
    xml_dict: dict = xmltodict.parse(xml_str)
    json_data = json.dumps(xml_dict, indent=4)
    data_dict: dict = json.loads(json_data)

    # at the moment XML have embedded PDF only if we have the tag Invoice
    try:
        if 'Invoice' in data_dict:
            invoice_data: dict = data_dict['Invoice']
            return extract_pdf_attachments(m_cn_id, invoice_data, "AdditionalDocumentReference")
    except Exception as e:
        print(f"Error in get_pdf_file {e}")
        return None

    return None
