import sys
import re
from xml.etree.ElementTree import Element
import xml.etree.ElementTree as ET
from typing import Union, Dict, List, Optional
import os
import json
import PyPDF2
from pathlib import Path

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


def load_mappings() -> dict:
    """
    Load and cache attribute mappings from JSON configuration file.

    Returns:
        Dictionary with attribute mappings or empty dict if file not found.
    """
    try:
        config_path = Path(__file__).parent / "config" / "mapping_client.json"
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f).get("attribute_mappings", {})
    except FileNotFoundError as e:
        print(f"Config file not found: {e}")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return {}


def find_attribute_within_element(
        element: Element, tags: list, attribute_name: str, default: str = None) -> Union[str, None]:
    """
    Find and map attribute value within XML element.

    Searches through provided tags within the XML element and extracts
    the specified attribute value. Returns mapped value only if the
    attribute value exists in the mapping configuration.

    Args:
        element: The XML element to search within.
        tags: List of tag names to search for in the element.
        attribute_name: Name of the attribute to extract from the tag.
        default: Default value to return if attribute is not found or not in mapping.

    Returns:
        Mapped attribute value if found in mapping configuration.
        Returns default if attribute is not found or not in mapping.
    """

    if not element:
        return default

    for tag in tags:
        if (data := element.find(tag)) is not None:
            if (value := data.get(attribute_name)):
                value = value.strip()
                mappings = load_mappings()

                # Return mapped value only if exists in mapping
                if value in mappings:
                    return mappings[value]

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
                if len(data.text.strip().replace(" ", "")) == length:
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
        create_viable_float_or_int_string(value.replace("-", ""), de_format))


def string_to_float_negative(value, de_format=False) -> Union[float, int, None, str]:
    """
    for positions, we need negative value for position
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


def create_viable_float_or_int_string(value: str, de_format=False) -> Union[float, int, None, str]:
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


# cost center can not be more than 4
def check_cost_center(cost_center: Optional[str]) -> Optional[str]:
    """
    Validates a cost center string.

    A valid cost center must:
    - Not be None or empty
    - Have a maximum length of 4 characters

    Args:
        cost_center (Optional[str]): The cost center string to validate.
                                   Can be None, empty string, or any string.

    Returns:
        Optional[str]: The original cost_center if valid, None otherwise.
                      Returns None if cost_center is None, empty, or longer than 4 characters.

    Examples:
        #>>> check_cost_center("1234")
        '1234'
        #>>> check_cost_center("12345")  # Too long
        None
        #>>> check_cost_center("")       # Empty
        None
        #>>> check_cost_center(None)     # None input
        None
    """
    if not cost_center or len(cost_center) > 5:
        return None
    return cost_center


def find_tax_data(root, json_config_paths, tax_name, max_rates=5) -> dict:
    """
    Finds all unique tax values for tax data

    Args:
        root: XML tree root element
        json_config_paths: list of XPath strings from JSON config
        tax_name: name for variable
        max_rates: maximum number of tax rates to extract (default: 5)

    Returns:
        dict: dictionary in format {'tax_rate1': 21.0, 'tax_rate2': 0.0, ...}
              Always returns exactly max_rates entries (missing ones are None)
    """
    percent_values = []
    seen_values = set()  # Track unique values

    for path in json_config_paths:
        try:
            # Find elements
            elements = root.findall(path)

            # Extract values
            for elem in elements:
                if elem.text:
                    value = str(elem.text.strip())
                    # Add only unique values
                    if value not in seen_values:
                        percent_values.append(value)
                        seen_values.add(value)

                        # Stop if max limit reached
                        if len(percent_values) >= max_rates:
                            break

            if len(percent_values) >= max_rates:
                break

        except Exception as e:
            print(f"Warning: could not process path {path}: {e}")
            continue

    # Create dictionary tax_rate1, tax_rate2, etc.
    # Always return exactly max_rates entries
    tax_rates = {}
    for i in range(1, max_rates + 1):
        if i <= len(percent_values):
            tax_rates[f'{tax_name}{i}'] = percent_values[i - 1]
        else:
            tax_rates[f'{tax_name}{i}'] = None

    return tax_rates


# HW-5852
def format_sixt_number(number: str) -> Optional[str]:
    """
    Formats a number with the SIXT- prefix according to specific rules.

    Args:
        number: string representing a number or SIXT code

    Returns:
        Formatted string in SIXT-XXXXXXXXXXXX format or None

    Rules:
    - length 6: pad to 12 digits and add SIXT- prefix
    - length 12: add SIXT- prefix
    - length 18: normalize existing SIXT-/sixt- prefix to uppercase
    - otherwise: return None

    Examples:
        328137 (len=6) → SIXT-000000328137
        000000328429 (len=12) → SIXT-000000328429
        SIXT-000000320584 (len=18) → SIXT-000000320584
        sixt-000000320584 (len=18) → SIXT-000000320584
    """
    if not number or not number.isdigit():
        return None

    number_str = str(number).strip()
    length = len(number_str)

    if length == 6:
        # Pad to 12 digits and add prefix
        return f"SIXT-{number_str.zfill(12)}"

    elif length == 12:
        # Just add prefix
        return f"SIXT-{number_str}"

    elif length == 18:
        # Check if it starts with SIXT- or sixt-
        if number_str.upper().startswith("SIXT-"):
            return number_str.upper()
        else:
            return None

    else:
        return None


def load_config(config_path='config.json'):
    """
    Loads configuration from a JSON file.

    Args:
        config_path (str): Path to the configuration JSON file. Can be relative or absolute.

    Returns:
        dict: Dictionary containing field configurations with keywords to search for.
              Returns empty dict if file not found.

    Example:
         config = load_config('config/fields.json')
         print(config['cost_center'])
         ['Cost Center', 'CC']
    """
    if not Path(config_path).is_absolute():
        script_dir = Path(__file__).parent
        config_path = script_dir / config_path

    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config.get('fields', config)
    else:
        print(f"Mistake: File {config_path} not found!")
        return {}


def get_field_value(xml_text: Element, field_name: str, config_path='config/fields.json'):
    """
    Extracts a specific field value from XML text.

    Args:
        xml_text (str): XML content as a string.
        field_name (str): Name of the field to extract (e.g., 'cost_center', 'legal_entity').
        config_path (str, optional): Path to the configuration JSON file.
                                      Defaults to 'config/fields.json'.

    Returns:
        str or dict or None:
            - str: Simple value if no description found (e.g., '41872')
            - dict: {'value': str, 'description': str} if description exists after dash
            - None: If field not found in XML

    Raises:
        ValueError: If field_name is not found in configuration.

    Example:
        cost_center = get_field_value(xml, 'cost_center')
        '41872'
        cc_budget = get_field_value(xml, 'cc_budget')
        {'value': '41872', 'description': 'TRAVEL TRAINEES'}
        """
    config = load_config(config_path)

    if field_name not in config:
        print(f"Field '{field_name}' not found in fields.json")
        return None

    keywords = config[field_name]

    return find_value_by_keywords(xml_text, keywords)


def find_value_by_keywords(root: Element, keywords: str):
    """
    Searches for a value in XML by matching keywords in AdditionalDocumentReference elements.

    Args:
        root (Element): XML content as a string.
        keywords (str or list): Keyword(s) to search for in ID elements.

    Returns:
        str or dict or None:
            - str: Extracted value after keyword/colon
            - dict: {'value': str, 'description': str} if description exists
            - None: If no matching keyword found

    Note:
        Supports XML with namespaces (cac:, cbc: prefixes).
    """
    if isinstance(keywords, str):
        keywords = [keywords]

    for ref in root.iter('AdditionalDocumentReference'):
        id_elem = ref.find('ID')

        if id_elem is not None and id_elem.text:
            id_text = id_elem.text.strip()

            for keyword in keywords:
                if keyword.lower() in id_text.lower():
                    return extract_value(id_text, keyword)

    return None


def extract_value(text, keyword):
    """
    Extracts value from text after a keyword or colon.

    Supports patterns:
        - "Keyword : Value" → returns "Value"
        - "Keyword Value" → returns "Value"
        - "Keyword : Value - Description" → returns "Value - Description"

    Args:
        text (str): Text to extract value from.
        keyword (str): Keyword that precedes the value.

    Returns:
        str: Extracted value, optionally with description separated by ' - '

    Example:
        extract_value("Cost Center : 41872", "Cost Center")
        '41872'
        extract_value("CC - Budget : 41872 - TRAVEL TRAINEES", "CC - Budget")
        '41872 - TRAVEL TRAINEES'
    """
    # Pattern 1: With colon
    match = re.search(r':\s*(.+?)(?:\s*-\s*(.+))?$', text)
    if match:
        value = match.group(1).strip()
        description = match.group(2).strip() if match.group(2) else None

        if description:
            return f"{value} - {description}"
        return value

    # Pattern 2: Without colon
    pattern = rf'{re.escape(keyword)}\s+(.+?)(?:\s*-\s*(.+))?$'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        value = match.group(1).strip()
        description = match.group(2).strip() if match.group(2) else None

        if description:
            return f"{value} - {description}"
        return value

    return text


def parse_vehicle_info(xml_string: str) -> Dict[str, str]:
    """
    Parses XML and extracts data from AdditionalDocumentReference elements

    Args:
        xml_string: XML as a string

    Returns:
        Dictionary with format {description: id_value}
    """
    try:
        root: ET.Element = ET.fromstring(xml_string)
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return {}

    result: Dict[str, str] = {}

    # Find all elements ending with 'AdditionalDocumentReference'
    for doc_ref in root.iter():
        if doc_ref.tag.endswith('AdditionalDocumentReference'):
            doc_id: Optional[str] = None
            doc_desc: Optional[str] = None

            # Extract ID and Description from child elements
            for child in doc_ref:
                if child.tag.endswith('ID'):
                    doc_id = child.text
                elif child.tag.endswith('DocumentDescription'):
                    doc_desc = child.text

            # Add to result if both values exist
            if doc_id and doc_desc:
                result[doc_desc] = doc_id

    return result


def format_vehicle_info(xml_string: str) -> List[str]:
    """
    Parses XML and returns formatted strings

    Args:
        xml_string: XML as a string

    Returns:
        List of strings in format "Description: Value"
    """
    data: Dict[str, str] = parse_vehicle_info(xml_string)

    formatted: List[str] = []
    for description, value in data.items():
        formatted.append(f"{description}: {value}")

    return formatted


def get_vehicle_value(xml_string: str, description_keyword: str) -> Optional[str]:
    """
    Gets specific value by keyword in description

    Args:
        xml_string: XML data as string
        description_keyword: Part of description to search for (e.g., "registration")

    Returns:
        Found value or None if not found
    """
    data: Dict[str, str] = parse_vehicle_info(xml_string)

    for description, value in data.items():
        if description_keyword.lower() in description.lower():
            return value

    return None
