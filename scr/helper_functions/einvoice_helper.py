import sys
import re
from xml.etree.ElementTree import Element
import xml.etree.ElementTree as ET
from typing import Union, Dict, List, Optional, Tuple, FrozenSet
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
        data = element.find(tag)
        if data is not None:
            value = data.get(attribute_name)
            if value:
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


def join_all_texts_for_tags(element: Optional[Element], tags: List[str], separator: str = ".") -> Optional[str]:
    """
    Collect non-empty text from every element matching each XPath in tags (document order),
    then join with separator. Used for all IncludedNote/Content values in one field.
    """
    if element is None:
        return None
    parts: List[str] = []
    for tag in tags:
        for node in element.findall(tag):
            if node.text:
                chunk: str = node.text.strip()
                if chunk:
                    parts.append(chunk)
    return separator.join(parts) if parts else None


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


# UBL Item/cbc:Name values treated as placeholders; use cbc:Description when present instead.
_UBL_ITEM_NAME_PLACEHOLDERS: FrozenSet[str] = frozenset({"-", ".", "/", "—", "–"})


def _ubl_item_name_is_placeholder(name: str) -> bool:
    """True if supplier used a sentinel instead of a real article name (HW-6052-style)."""
    trimmed: str = name.strip()
    if not trimmed:
        return True
    return trimmed in _UBL_ITEM_NAME_PLACEHOLDERS


def is_ubl_placeholder_text(value: Optional[str]) -> bool:
    """True if text is empty or an Item/line placeholder (-, ., /); skip when merging extra fields."""
    if value is None:
        return True
    return _ubl_item_name_is_placeholder(value)


def build_description_from_item(position: Element) -> Optional[str]:
    """
    Build position description from Item (UBL) or SpecifiedTradeProduct (ZUGPFERD):
    main Name plus all Name/Value or Description/Value pairs, space-separated.

    UBL: Item with cbc:Name and cac:AdditionalItemProperty (Name, Value).
    If Name is a placeholder (-, ., /) but cbc:Description is present, Description is used as primary text.
    ZUGPFERD: SpecifiedTradeProduct with Name and ApplicableProductCharacteristic (Description, Value).
    """
    if position is None:
        return None
    parts: List[str] = []

    # UBL: Item with Name and AdditionalItemProperty (Name, Value)
    item_elem: Optional[Element] = position.find("Item")
    if item_elem is not None:
        name_el: Optional[Element] = item_elem.find("Name")
        desc_el_item: Optional[Element] = item_elem.find("Description")
        name_raw: str = name_el.text.strip() if name_el is not None and name_el.text else ""
        desc_raw: str = (
            desc_el_item.text.strip() if desc_el_item is not None and desc_el_item.text else ""
        )
        if name_raw and not _ubl_item_name_is_placeholder(name_raw):
            parts.append(name_raw)
        elif desc_raw:
            parts.append(desc_raw)
        elif name_raw:
            parts.append(name_raw)
        for prop in item_elem.findall("AdditionalItemProperty"):
            prop_name_el: Optional[Element] = prop.find("Name")
            prop_value_el: Optional[Element] = prop.find("Value")
            if prop_name_el is not None and prop_name_el.text and prop_value_el is not None and prop_value_el.text:
                parts.append(prop_name_el.text.strip())
                parts.append(prop_value_el.text.strip())
        if parts:
            return " ".join(parts)

    # ZUGPFERD: SpecifiedTradeProduct with Name and ApplicableProductCharacteristic (Description, Value)
    prod_elem: Optional[Element] = position.find("SpecifiedTradeProduct")
    if prod_elem is not None:
        name_el = prod_elem.find("Name")
        if name_el is not None and name_el.text:
            parts.append(name_el.text.strip())
        for prop in prod_elem.findall("ApplicableProductCharacteristic"):
            desc_el: Optional[Element] = prop.find("Description")
            value_el: Optional[Element] = prop.find("Value")
            if desc_el is not None and desc_el.text and value_el is not None and value_el.text:
                parts.append(desc_el.text.strip())
                parts.append(value_el.text.strip())
        if parts:
            return " ".join(parts)

    return None


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


def make_amount_non_negative(value: Optional[str]) -> Optional[float]:
    """
    Parse a monetary string and return its absolute value as a non-negative float.

    Returns None if value is None or blank.
    """
    if value is None:
        return None
    stripped: str = str(value).strip()
    if not stripped:
        return None
    parsed: Union[float, int, None, str] = string_to_float(stripped)
    if parsed is None:
        return None
    if isinstance(parsed, str):
        try:
            normalized: float = float(parsed.replace(",", ".").replace(" ", ""))
        except ValueError:
            return None
        return abs(normalized)
    return abs(float(parsed))


def format_header_amount_string(value: Optional[float]) -> Optional[str]:
    """
    Format a float for XmlInvoice header attributes (stored as strings).
    Whole numbers are serialized without a fractional part (e.g. 1225 -> "1225").
    """
    if value is None:
        return None
    rounded: float = round(value, 2)
    if rounded == int(rounded):
        return str(int(rounded))
    return format(rounded, ".2f")


def _xml_root_local_name(element: Element) -> str:
    """
    Return local name of root (or any) XML element tag, stripping namespace URI if present.
    """
    tag: str = element.tag
    if tag.startswith("{") and "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def document_charge_description(xml_tree: Element) -> str:
    """
    Build position text from invoice-level AllowanceCharge elements with ChargeIndicator true.
    """
    reasons: List[str] = []
    for path in ("./AllowanceCharge", "./Invoice/AllowanceCharge"):
        for ac in xml_tree.findall(path):
            indicator = ac.find("ChargeIndicator")
            if indicator is None or not indicator.text or indicator.text.strip().lower() != "true":
                continue
            amount_el = ac.find("Amount")
            if amount_el is None or not amount_el.text:
                continue
            if string_to_float(amount_el.text) <= 0:
                continue
            reason_el = ac.find("AllowanceChargeReason")
            if reason_el is not None and reason_el.text:
                reasons.append(reason_el.text.strip())
    return "\n".join(reasons) if reasons else "Document charge"

# HW-6192
def get_header_trade_allowance_discount(
    xml_tree: Element,
) -> Optional[Tuple[float, str, Optional[float]]]:
    """
    ZUGFeRD / Factur-X: sum document-level allowances from ApplicableHeaderTradeSettlement
    SpecifiedTradeAllowanceCharge where ChargeIndicator is false (discount).
    Returns (net amount, combined reason text, VAT percent from CategoryTradeTax) or None.
    """
    settlement: Optional[Element] = xml_tree.find(
        "./SupplyChainTradeTransaction/ApplicableHeaderTradeSettlement"
    )
    if settlement is None:
        return None
    total_amount: float = 0.0
    reasons: List[str] = []
    tax_rate: Optional[float] = None
    for ac in settlement.findall("SpecifiedTradeAllowanceCharge"):
        charge_ind: Optional[Element] = ac.find("ChargeIndicator")
        if charge_ind is None:
            continue
        indicator_el: Optional[Element] = charge_ind.find("Indicator")
        ind_text: str = ""
        if indicator_el is not None and indicator_el.text:
            ind_text = indicator_el.text.strip().lower()
        elif charge_ind.text:
            ind_text = charge_ind.text.strip().lower()
        if ind_text not in ("false", "0"):
            continue
        amt_el: Optional[Element] = ac.find("ActualAmount")
        if amt_el is None or not amt_el.text:
            continue
        amt: float = string_to_float(amt_el.text.strip())
        if amt <= 0:
            continue
        total_amount += amt
        reason_el: Optional[Element] = ac.find("Reason")
        if reason_el is not None and reason_el.text:
            reasons.append(reason_el.text.strip())
        rt_el: Optional[Element] = ac.find("CategoryTradeTax/RateApplicablePercent")
        if rt_el is not None and rt_el.text:
            tax_rate = string_to_float(rt_el.text.strip())
    if total_amount <= 0:
        return None
    description: str = " / ".join(reasons) if reasons else "Discount"
    return (total_amount, description, tax_rate)


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


def _text_or_none(elem: Optional[Element]) -> Optional[str]:
    """Return stripped text of element or None if missing/empty."""
    if elem is not None and elem.text:
        return elem.text.strip()
    return None


def _tax_scheme_from_id_elem(id_elem: Optional[Element]) -> str:
    if id_elem is None:
        return ""
    scheme: Optional[str] = id_elem.get("schemeID")
    if scheme:
        return scheme.strip().upper()
    return ""


def extract_specified_tax_registration_vat_id(
        party: Optional[Element],
        prefer_schemes: Tuple[str, ...] = ("VA", "VAT")
) -> Optional[str]:
    """
    Read SpecifiedTaxRegistration/ID from a RAM trade party (e.g. Seller, Invoicee).
    Prefer EU VAT scheme (VA/VAT); otherwise first non-empty registration ID.
    """
    if party is None:
        return None
    pairs: List[Tuple[str, str]] = []
    for reg in party.findall("SpecifiedTaxRegistration"):
        id_elem: Optional[Element] = reg.find("ID")
        if id_elem is None or not id_elem.text:
            continue
        pairs.append((_tax_scheme_from_id_elem(id_elem), id_elem.text.strip()))
    if not pairs:
        return None
    for pref in prefer_schemes:
        up: str = pref.strip().upper()
        for scheme, text in pairs:
            if scheme == up:
                return text
    return pairs[0][1]


def extract_seller_vat_id_zugferd(transaction_root: Optional[Element]) -> Optional[str]:
    """Seller USt-ID from ApplicableHeaderTradeAgreement/SellerTradeParty (VA preferred)."""
    if transaction_root is None:
        return None
    agr: Optional[Element] = transaction_root.find("./ApplicableHeaderTradeAgreement")
    if agr is None:
        return None
    seller: Optional[Element] = agr.find("SellerTradeParty")
    return extract_specified_tax_registration_vat_id(seller)


def extract_invoicee_or_buyer_vat_id(transaction_root: Optional[Element]) -> Optional[str]:
    """
    Recipient VAT: ApplicableHeaderTradeSettlement/InvoiceeTradeParty if present,
    else ApplicableHeaderTradeAgreement/BuyerTradeParty (VA preferred).
    """
    if transaction_root is None:
        return None
    settlement: Optional[Element] = transaction_root.find("./ApplicableHeaderTradeSettlement")
    if settlement is not None:
        invoicee: Optional[Element] = settlement.find("InvoiceeTradeParty")
        vid: Optional[str] = extract_specified_tax_registration_vat_id(invoicee)
        if vid:
            return vid
    agr: Optional[Element] = transaction_root.find("./ApplicableHeaderTradeAgreement")
    if agr is None:
        return None
    buyer: Optional[Element] = agr.find("BuyerTradeParty")
    return extract_specified_tax_registration_vat_id(buyer)


def extract_payment_means_list(element: Optional[Element]) -> List[Dict[str, Optional[str]]]:
    """
    Extract all PaymentMeans blocks from XML element as a list of dicts (table-friendly for PDF).
    UBL: PaymentMeans with PayeeFinancialAccount.
    ZUGFeRD RAM: SpecifiedTradeSettlementPaymentMeans under ApplicableHeaderTradeSettlement.
    Each dict has: PaymentMeansCode, PaymentID, AccountID (IBAN / account id), BranchID (BIC).
    """
    if element is None:
        return []
    result: List[Dict[str, Optional[str]]] = []
    for pm in element.findall(".//PaymentMeans"):
        code_elem = pm.find("PaymentMeansCode")
        pid_elem = pm.find("PaymentID")
        payee = pm.find("PayeeFinancialAccount")
        account_id: Optional[str] = None
        branch_id: Optional[str] = None
        if payee is not None:
            id_elem = payee.find("ID")
            account_id = _text_or_none(id_elem)
            branch = payee.find("FinancialInstitutionBranch")
            if branch is not None:
                branch_id_elem = branch.find("ID")
                if branch_id_elem is None:
                    fin_inst = branch.find("FinancialInstitution")
                    if fin_inst is not None:
                        branch_id_elem = fin_inst.find("ID")
                branch_id = _text_or_none(branch_id_elem)
        result.append({
            "PaymentMeansCode": _text_or_none(code_elem),
            "PaymentID": _text_or_none(pid_elem),
            "AccountID": account_id,
            "BranchID": branch_id,
        })

    settlement_payment_ref: Optional[str] = None
    settlement: Optional[Element] = element.find("./ApplicableHeaderTradeSettlement")
    if settlement is None:
        settlement = element.find(".//ApplicableHeaderTradeSettlement")
    if settlement is not None:
        settlement_payment_ref = _text_or_none(settlement.find("PaymentReference"))

    for pm in element.findall(".//SpecifiedTradeSettlementPaymentMeans"):
        type_code: Optional[str] = _text_or_none(pm.find("TypeCode"))
        info: Optional[str] = _text_or_none(pm.find("Information"))
        payment_ref_local: Optional[str] = _text_or_none(pm.find("PaymentReference"))
        payment_id_val: Optional[str] = payment_ref_local or settlement_payment_ref or info
        account_id: Optional[str] = None
        branch_id: Optional[str] = None
        payee_fin: Optional[Element] = pm.find("PayeePartyCreditorFinancialAccount")
        if payee_fin is not None:
            iban_el: Optional[Element] = payee_fin.find("IBANID")
            account_id = _text_or_none(iban_el)
            if account_id is None:
                account_id = _text_or_none(payee_fin.find("ProprietaryID"))
            if account_id:
                account_id = account_id.replace(" ", "")
        cred_fin: Optional[Element] = pm.find("PayeeSpecifiedCreditorFinancialInstitution")
        if cred_fin is not None:
            bic_el: Optional[Element] = cred_fin.find("BICID")
            branch_id = _text_or_none(bic_el)
        if branch_id is None and payee_fin is not None:
            pi_el: Optional[Element] = payee_fin.find("PaymentServiceProviderID")
            branch_id = _text_or_none(pi_el)
        result.append({
            "PaymentMeansCode": type_code,
            "PaymentID": payment_id_val,
            "AccountID": account_id,
            "BranchID": branch_id,
        })
    return result
