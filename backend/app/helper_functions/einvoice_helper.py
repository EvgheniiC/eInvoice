"""
Compatibility facade for helper functions.

Prefer importing from app.helper_functions or the focused modules
(amounts, xml_query, tags_config, ...). This module re-exports the public API
so existing `from app.helper_functions.einvoice_helper import ...` keeps working.
"""

from .amounts import (
    create_viable_float_or_int_string,
    decimal_non_negative,
    format_header_amount_string,
    make_amount_non_negative,
    normalize_header_amount,
    optional_string_to_decimal,
    optional_string_to_float,
    parse_decimal,
    quantize_money,
    string_to_float,
    string_to_float_negative,
)
from .description import (
    HeaderTradeAdjustment,
    LineAllowanceDiscount,
    _is_gu_document,
    build_description_from_item,
    document_charge_description,
    get_document_level_charges,
    get_header_trade_allowance_discount,
    get_header_trade_charges,
    get_line_allowance_discount,
    is_ubl_placeholder_text,
)
from .field_extract import extract_value, find_value_by_keywords, get_field_value
from .fixture_io import read_xml_file_to_str
from .party_extract import (
    extract_invoicee_or_buyer_vat_id,
    extract_payment_means_list,
    extract_seller_vat_id_zugferd,
    extract_specified_tax_registration_vat_id,
)
from .pdf_utils import is_zugpferd_pdf
from .tags_config import get_tags_from_json, load_config, load_mappings
from .tax import find_tax_data
from .xml_query import (
    _text_or_none,
    _xml_root_local_name,
    delete_all_prefills,
    find_attribute_within_element,
    find_data_with_regex,
    find_data_within_element,
    find_data_within_element_with_len,
    get_xml_tree,
    join_all_texts_for_tags,
    parse_xml_date,
)

__all__ = [
    "create_viable_float_or_int_string",
    "decimal_non_negative",
    "format_header_amount_string",
    "make_amount_non_negative",
    "normalize_header_amount",
    "optional_string_to_decimal",
    "optional_string_to_float",
    "parse_decimal",
    "quantize_money",
    "string_to_float",
    "string_to_float_negative",
    "_is_gu_document",
    "build_description_from_item",
    "HeaderTradeAdjustment",
    "LineAllowanceDiscount",
    "document_charge_description",
    "get_document_level_charges",
    "get_header_trade_allowance_discount",
    "get_header_trade_charges",
    "get_line_allowance_discount",
    "is_ubl_placeholder_text",
    "extract_value",
    "find_value_by_keywords",
    "get_field_value",
    "read_xml_file_to_str",
    "extract_invoicee_or_buyer_vat_id",
    "extract_payment_means_list",
    "extract_seller_vat_id_zugferd",
    "extract_specified_tax_registration_vat_id",
    "is_zugpferd_pdf",
    "get_tags_from_json",
    "load_config",
    "load_mappings",
    "find_tax_data",
    "_text_or_none",
    "_xml_root_local_name",
    "delete_all_prefills",
    "find_attribute_within_element",
    "find_data_with_regex",
    "find_data_within_element",
    "find_data_within_element_with_len",
    "get_xml_tree",
    "join_all_texts_for_tags",
    "parse_xml_date",
]
