from ..helper_functions import get_xml_three, extract_pdf_attachments
from xml.etree.ElementTree import Element
import xmltodict
import json
from xml.etree.ElementTree import tostring
from typing import Union


# sometimes we have a PDF file embedded in an XML file
def get_pdf_file(m_cn_id: str, xml_text: str) -> Union[str, None]:
    xml_tree: Element = get_xml_three(xml_text)
    # Assuming xml_tree is an Element object obtained from your XML data
    xml_str = tostring(xml_tree).decode()

    # Convert XML string to OrderedDict
    xml_dict = xmltodict.parse(xml_str)

    # Convert OrderedDict to JSON
    json_data = json.dumps(xml_dict, indent=4)

    # Load JSON data into a Python dictionary
    data_dict = json.loads(json_data)
    invoice_data = data_dict['Invoice']

    return extract_pdf_attachments(m_cn_id, invoice_data, "AdditionalDocumentReference")
