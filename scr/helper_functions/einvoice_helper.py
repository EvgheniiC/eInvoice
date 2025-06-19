import sys
import re
from xml.etree.ElementTree import Element
import xml.etree.ElementTree as ET
from typing import Union
import os
import json
import PyPDF2


sys.path.append("../")
to_replace = ["\[", "\]", " ", "\.\.\."]


def find_data_within_element(element: Element, tags: list, default: str = None) -> Union[str, None]:
    """
    Searches for data within XML elements based on provided tags.

    Args:
    - element: The XML element in which to search for data.
    - tags: A list of tags to search for within the element.
    - default: The default value to return if none of the tags are found.

    Returns:
    - The text content of the first tag found within the element. Returns default if none of the tags are found.
    """
    if element is None:
        return default

    for tag in tags:
        data = element.find(tag)
        if data is not None:
            if data.text:
                return data.text.strip()
    return default


def find_data_within_element_with_len(element: Element, tags: list, length: int) -> Union[str, None]:
    """
    Searches for data within XML elements based on provided tags and length.
    For exam search IBAN with length 22
    Args:
    - element: The XML element in which to search for data.
    - tags: A list of tags to search for within the element.
    - len: length of an element

    Returns:
    - The text content of the first tag found within the element. Returns None if none of the tags are found.
    """
    if element is None:
        return None

    for tag in tags:
        data = element.find(tag)
        if data is not None:
            if data.text:
                if len(data.text.strip()) == length:
                    return data.text.strip()
    return None


# delete all prefixes from xml
def delete_all_prefills(xml_tree: ET) -> ET:
    """
    This function removes namespace prefixes from XML elements in the given XML tree.

    Parameters:
    xml_tree (elementtree.ElementTree): The input ElementTree object representing the XML structure.

    Returns:
    elementtree.ElementTree: The modified ElementTree object with namespace prefixes removed.

    Example:
    <{urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100}CrossIndustryInvoice>
    will be transformed to
    <CrossIndustryInvoice>
    """
    # Remove namespace prefixes
    for elem in xml_tree.iter():
        # Get the tag name without the prefix
        tag = elem.tag.split("}")[1] if "}" in elem.tag else elem.tag
        # Replace the element tag with the tag name without prefix
        elem.tag = tag

    return xml_tree


def find_data_with_regex(element: Element, regex_pattern: str) -> Union[str, None]:
    """
    Finds data within all tags of an XML element using a regular expression pattern.
    For exam, we can find order number 930…

    Args:
    - element: The XML element to search for data.
    - regex_pattern: The regular expression pattern to search for within the element tags.

    Returns:
    - The matched data found within the tags based on the regex pattern. Returns None if no match is found.
    """
    if element:
        all_tags_data = ' '.join(element.itertext())  # Get all text content within the element and tags
        match = re.search(regex_pattern, all_tags_data)

        if match:
            return match.group(0).strip().rstrip()
        else:
            return None
    return None


def get_xml_tree(xml_text: str) -> Element:
    xml_tree: Element = ET.fromstring(xml_text)
    xml_tree = delete_all_prefills(xml_tree)
    return xml_tree


def string_to_float(value, de_format=False) -> Union[float, int, None, str]:
    """
    Formats a none null value into a float value with this format: d{1,}.d{2}

    :param value: The string value to convert
    :type value: str
    :param de_format: If de --> , instead of .
    :type de_format: bool
    :return: 0 if not an number, None if value == None, else the formatted float value
    :rtype: float
    """
    if value is None:
        return None
    if not str(value).replace(",", "").replace(".", "").replace("-", "").strip().isdigit():
        return 0
    return value if isinstance(value, float) or isinstance(value, int) else float(
        create_viable_float_or_int_string(value, de_format))


def create_viable_float_or_int_string(value: str, de_format) -> Union[float, int, None, str]:
    """
    Creates a float / int string, by replacing every , / . except the last one and check

    :param value: string value (i.e. "234.12")
    :type value: str
    :param de_format: deFormat true --> 234.12, False 1,234.23
    :type de_format: bool
    :return: the formatted string
    :rtype: str
    """
    if de_format:
        value = value.replace(".", "")
        return float(value.replace(",", "."))

    value = value.replace(",", ".")
    if value.count(".") == 1:
        return value

    splitValue = value.split(".")
    if len(splitValue) > 0:
        if len(splitValue[-1]) < 3:
            return value.replace(",", ".").replace(".", "", value.replace(",", ".").count(".") - 1)
        else:
            return value.replace(",", ".").replace(".", "")
    return None


# Function to read XML file to string with fixed directory path
def read_xml_file_to_str(file_name):
    """
    Reads the contents of an XML file located in the fixed directory path 'com.sixt.lib.python.eInvoice/tests/xml_files'
    and returns it as a string.

    Args:
        file_name (str): Name of the XML file to read.

    Returns:
        str: The contents of the XML file as a string, or None if the file is not found.
    """
    # Fixed directory path for the XML file
    directory_path = os.path.join(os.getcwd(), '')

    # Construct the full path to the XML file
    xml_file_path = os.path.join(directory_path, file_name)

    try:
        # Attempt to open and read the XML file
        with open(xml_file_path, 'r') as file:
            xml_content = file.read()
        return xml_content
    except FileNotFoundError:
        print(f"Error: File not found at path '{xml_file_path}'")
        return None


def get_tags_from_json(tag: str) -> list:
    """
    Get a list of tags from a JSON file based on the given tag name.

    Parameters:
    tag (str): The tag to retrieve from the JSON file.

    Returns:
    list: A list of tags or an empty list if the tag is not found.
    """

    # Desired directory path where tags.json is located
    desired_directory_path = os.path.dirname(os.path.abspath(__file__)) + "/config/"

    # Construct the full path to the JSON file with tags
    json_file_with_tags = os.path.join(desired_directory_path, 'tags.json')

    # Read tags from the JSON file based on the provided tag
    if os.path.exists(json_file_with_tags):  # Check if the file exists
        with open(json_file_with_tags) as file:
            json_data = json.load(file)
            tags = json_data.get(tag, [])
    else:
        print(f"File {json_file_with_tags} not found.")
        tags = []

    # Return the list of tags
    return tags


def is_zugpferd_pdf(file_path: str):
    """
    checks the PDF file to make sure it is in the zugpferd format
    """
    pdf_file = open(file_path, "rb")
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    file_names = ""
    catalog = ""
    try:
        catalog = pdf_reader.trailer["/Root"]
    except (Exception,):
        print("Not found in Kids")

    if catalog:
        try:
            file_names = catalog['/Names']['/EmbeddedFiles']['/Names']
        except (Exception,):
            print("Not found in Names")

        if not file_names:
            try:
                file_names = catalog['/Names']['/EmbeddedFiles']['/Kids']
            except (Exception,):
                print("Not found in Kids")

    return True if file_names else False