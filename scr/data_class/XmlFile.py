import xml.etree.ElementTree as elementTree
from dataclasses import dataclass, asdict
from io import StringIO
import xml.etree.ElementTree as ET


@dataclass
class XmlFile:
    """
    Represents an XML file and facilitates its manipulation and parsing.

    This class provides functionality for handling XML files, such as resolving
    namespaces, extracting content to a dictionary, and maintaining file-related
    attributes. It can parse XML data and transform it into a structured
    dictionary format for further processing and analysis.

    Attributes:
        xml_file (str): Represents the OS file path where the XML document is located.
        xml_file_data (dict): Stores the structured data parsed from the XML document.
        xml_file_name_spaces (dict): Contains resolved namespace information extracted from
            the XML file.
    """
    def __init__(self, xml_file):
        # Resolved file data
        self.xml_file_data = None
        # OS file path the document is located in
        self.xml_file = xml_file
        # Some XML documents have a specific prefix used inside the document.
        # This prefix could be used to identify the correct layout.
        self.xml_file_name_spaces = self.resolve_name_spaces()
        # logger
        # self.xml_file_info_logger = info_logger
        # self.xml_file_error_logger = error_logger

    @property
    def xml_file(self):
        return self.__xml_file

    @xml_file.setter
    def xml_file(self, value: str):
        self.__xml_file = value

    @property
    def xml_file_data(self):
        return self.__xml_file_data

    @xml_file_data.setter
    def xml_file_data(self, value: dict):
        self.__xml_file_data = value

    def get_attributes(self):
        return asdict(self)

    # def write_info_log(self, info_msg):
    #     if self.xml_file_info_logger is not None:
    #         self.xml_file_info_logger.info(info_msg)
    #
    # def write_error_log(self, error_msg):
    #     if self.xml_file_error_logger is not None:
    #         self.xml_file_error_logger.error(error_msg)

    def resolve_name_spaces(self):
        # f = open(self.__xml_file, "r")
        xml_data = self.__xml_file.read()
        # my_namespaces = dict([node for _, node in elementTree.iterparse(StringIO(self.__xml_file), events=['start-ns'])])
        my_namespaces = dict([node for _, node in elementTree.iterparse(StringIO(xml_data), events=['start-ns'])])
        return my_namespaces

    def resolve_xml_file_content(self):
        # self.write_info_log(f"#### START PROCESSING: {self.__xml_file} ####")

        try:
            if not self.__xml_file:
                # self.write_error_log(f"File size for path: {self.__xml_file} was invalid.")
                self.__xml_file_data = None
            else:

                # extract namespace information from element tags
                def extract_namespace(tag):
                    ns_split = tag.split('}')
                    if len(ns_split) > 1:
                        return {
                            'prefix': ns_split[0][1:],
                            'uri': ns_split[0][:ns_split[0].find('}') + 1],
                            'tag': ns_split[1]
                        }
                    return {'prefix': None, 'uri': None, 'tag': ns_split[0]}

                # recursive function to convert XML to a dictionary
                def xml_to_dict(element):
                    tag_info = extract_namespace(element.tag)
                    child_dict = {'prefix': tag_info.get("prefix"),
                                  'attributes': {},
                                  'children': [],
                                  'text': element.text.strip() if element.text else ''}

                    # add child element's attributes to the dictionary
                    for name, value in element.attrib.items():
                        attr_info = extract_namespace(name)
                        child_dict['attributes'][
                            attr_info['uri'] if attr_info['uri'] else '' + attr_info['tag'] if attr_info[
                                'tag'] else ''] = value

                    # iterate over all child elements
                    for child in element:
                        child_dict['children'].append(xml_to_dict(child))

                    return {
                        tag_info['uri'] if tag_info['uri'] else '' + tag_info['tag']
                        if tag_info['tag'] else '': child_dict}

                # parse given XML file
                xml_data = self.__xml_file.read()

                # parse the XML data into an ElementTree object
                root = ET.fromstring(xml_data)

                # convert the XML to a dictionary
                data = xml_to_dict(root)
                self.__xml_file_data = data

        except Exception as ex:
            self.__xml_file_data = None
            # self.write_error_log(f"Error while processing document occur: {ex}")
