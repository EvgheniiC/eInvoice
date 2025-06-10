import sys
import re
from xml.etree.ElementTree import Element
import xml.etree.ElementTree as ET
from typing import Union

sys.path.append("../")
to_replace = ["\[", "\]", " ", "\.\.\."]


def get_xml_object_by_keys(dictionary, search_list):
    """
        Retrieves specific XML object data based on a list of search criteria.

        This function processes a dictionary representation of an XML structure and
        retrieves data for specified keys provided in a search list. The search list
        specifies the query parameters, including which key to search for, optional
        modifications such as taking only the first result, extracting only text, or
        applying a namespace.

        Arguments:
            dictionary (dict): The dictionary representing the XML structure.
            search_list (List[Dict[str, Any]]): A list of dictionaries, where each dictionary
                contains the details for a key to search in the XML object. The supported
                dictionary keys are:
                - 'key' (Optional[str]): Specifies the output key for the result.
                - 'searchKey' (str): The key to search in the XML dictionary.
                - 'take_first' (Optional[bool]): Whether to take only the first result. Defaults
                  to False if not specified.
                - 'take_only_text' (Optional[bool]): Whether to extract only the text content
                  of the search result. Defaults to False if not specified.
                - 'name_space' (Optional[str]): Namespace to apply to the search. Defaults to
                  None if not specified.

        Returns:
            Dict[str, Any]: A dictionary containing the results mapped with specified keys.
            Results are fetched according to the search criteria defined in the input
            search list.
    """
    result_list = {}
    for item in search_list:
        key = item.get("key")
        search_key = item.get("searchKey")
        take_first = item.get("take_first") if item.get("take_first") is not None else False
        take_only_text = item.get("take_only_text") if item.get("take_only_text") is not None else False
        name_space = item.get("name_space") if item.get("name_space") else None

        # print("key", key)
        # print("take_only_text", take_only_text)
        # print("name_space", name_space)

        result = get_xml_object_by_key(dictionary, search_key,
                                       take_first_result=take_first,
                                       take_only_text=take_only_text,
                                       name_space=name_space)

        if type(result) is not str and take_only_text and len(result) == 0:
            result_list.update({search_key if key is None or key == "" else key: ""})
        if type(result) is not str and take_only_text and len(result) == 1:
            result_list.update({search_key if key is None or key == "" else key: result[0]})
        else:
            result_list.update({search_key if key is None or key == "" else key: result})

    return result_list


def get_xml_object_by_key(dictionary, key, deep=10, take_first_result=True, take_only_text=False, name_space=None):
    """
    Retrieve XML objects from a nested dictionary by matching a specific key.

    This function searches for XML-like objects within a nested dictionary structure
    that match a specified key. The search can be adjusted to limit the depth of recursion,
    retrieve only the first matching result, strip unused characters from the resulting
    text, or filter results based on a namespace.

    Arguments:
        dictionary (dict): The root dictionary containing the XML-like data to be searched.
        key (str): The key to search for within the dictionary structure.
        deep (int, optional): The maximum depth to recursively search through children. Default is 10.
        take_first_result (bool, optional): Whether to return only the first matching object. Default is True.
        take_only_text (bool, optional): Whether to return only the text content of the matching object(s). Default is False.
        name_space (str, optional): Namespace prefix to match when searching for objects. Default is None.

    Returns:
        list or dict or str: If take_first_result is True, returns the first matching object or its text if
        take_only_text is True. Otherwise, returns a list of all matching objects or their texts.

    Raises:
        None explicitly raised, but may raise exceptions on invalid input such as a malformed dictionary.

    Notes:
        The function employs recursive parsing to traverse child objects. Performance may degrade with
        very deep or wide dictionary trees. It relies on dictionary keys and structure being XML-like,
        which may not apply in all cases.
    """
    results = []

    # print("dictionary", dictionary)
    def parse_children(d, key1, search_key, c):
        """
        Recursively searches for XML key values within a nested dictionary structure and retrieves matching values. The
        search involves traversing dictionaries and nested "children" elements within the structure up to a specified depth.

        Arguments:
        - d: The dictionary structure representing the XML-like data where the search is performed.
        - key1: The initial key to start searching within the XML-like data.
        - search_key: The target key to search for across the nested structure.
        - c: A counter for the current depth of the search.

        Parameters:
        - deep (int, optional): Specifies the maximum depth to search in the XML-like structure. Default is 10.
        - take_first_result (bool, optional): Whether to retrieve only the first matching result. Default is True.
        - take_only_text (bool, optional): Whether to extract only the plain text content of the matching key. Default is False.
        - name_space (optional): A namespace filter to match key prefixes. Default is None.

        Raises:
        - Exception: If processing a key encounters an error, the function continues the search on other elements.

        Returns:
        - str | list: If take_only_text is True, returns a string containing the text of the first matching key or an empty
          string if none are found. If take_only_text is False, returns a list of matching key objects or an empty list if
          none are found.
        """
        if c <= deep:
            c += 1

            # print("counter", c, key1, search_key)
            for _d in d:
                # Test if element is inside object or error would occur
                try:
                    _d[key1]
                except (Exception,):
                    continue

                # print(key1 == search_key)
                # print('_d[key1].get("prefix")', _d[key1].get("prefix"))
                if key1 == search_key and (name_space is None or name_space == _d[key1].get("prefix")):
                    if _d.get(key1) not in results:
                        if take_only_text:
                            text = _d.get(key1).get("text")
                            # replace all unused characters
                            for replace in to_replace:
                                text = re.sub(replace, '', text)
                            results.append(text)
                        else:
                            results.append(_d.get(key1))

                    if take_first_result:
                        return True

                else:
                    if len(list(_d.get(key1).get("children"))) > 0:
                        my__keys = ','.join(str(list(e.keys())[0]) for e in _d.get(key1).get("children"))

                        # print("my__keys", my__keys)
                        for ch_keys in my__keys.split(","):
                            # print("abc", abc)
                            parse_children(_d.get(key1).get("children"), ch_keys, search_key, c)
                            if take_first_result and len(results) > 0:
                                return True

        else:
            return "" if take_only_text else []

        return "" if take_only_text else []

    for x in dictionary:
        # print("dictionary[x]", dictionary[x])
        # print("dictionary[x].get(key)", dictionary[x].get(key))
        # print('dictionary[x].get("prefix")', dictionary[x].get("prefix"))
        # TODO try catch ??
        if dictionary[x].get(key) and (name_space is None or name_space == dictionary[x].get("prefix")):
            # if dictionary[x].get(key) if type(dictionary[x]) == dict else False and (name_space is None or name_space == dictionary[x].get("prefix") if type(dictionary[x]) ==dict else ""):

            results.append(dictionary[x])

            if take_first_result:
                if take_only_text:
                    # print("#####", results[0])
                    return results[0].get("text")
                else:
                    # print("results found:", len(results))
                    return results

        else:
            # check children
            # print("#1", dictionary[x])
            # print(x)
            try:
                if len(dictionary.get(x).get("children")) > 0:
                    my_keys = ','.join(str(list(e.keys())[0]) for e in dictionary.get(x).get("children"))
                    counter = 0

                    for key2 in my_keys.split(","):
                        if parse_children(dictionary.get(x).get("children"), key2, key, counter):
                            if take_first_result:
                                # print("results found:", len(results))
                                if len(results) > 0:
                                    return results[0]
            except (Exception,):
                if take_only_text:
                    return ""
    # results = list(dict.fromkeys(results))
    # print("results found:", len(results))
    return results if len(results) > 0 else ""


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
        print("tag = ", tag)
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
