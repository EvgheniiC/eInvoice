from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional
from xml.etree.ElementTree import Element

logger: logging.Logger = logging.getLogger(__name__)

# EN 16931 categories that are 0% when BT-119 (Percent) is omitted.
# Category O must not carry a rate at all; buyers still expect that bucket as 0%.
_ZERO_RATE_CATEGORIES: frozenset[str] = frozenset({"Z", "E", "AE", "K", "G", "O"})
_UBL_TAX_SUBTOTAL_PATHS: tuple[str, ...] = (
    "./TaxTotal/TaxSubtotal",
    "./Invoice/TaxTotal/TaxSubtotal",
)
_CII_TAX_SUBTOTAL_PATHS: tuple[str, ...] = (
    "./SupplyChainTradeTransaction/ApplicableHeaderTradeSettlement/ApplicableTradeTax",
)
MAX_HEADER_TAX_RATES: int = 5


@dataclass(frozen=True)
class HeaderTaxSubtotal:
    """One VAT breakdown row: rate, VAT amount, and taxable net, kept together."""

    rate: Optional[str]
    tax_amount: Optional[str]
    taxable_amount: Optional[str]


def find_tax_data(
    root: Element,
    json_config_paths: List[str],
    tax_name: str,
    max_rates: int = 5,
) -> Dict[str, Optional[str]]:
    """
    Find unique tax values for the given XPath list.

    Always returns exactly max_rates entries (missing ones are None).
    """
    percent_values: List[str] = []
    seen_values: set[str] = set()

    for path in json_config_paths:
        try:
            elements: List[Element] = root.findall(path)
            for elem in elements:
                if elem.text:
                    value: str = str(elem.text.strip())
                    if value not in seen_values:
                        percent_values.append(value)
                        seen_values.add(value)
                        if len(percent_values) >= max_rates:
                            break
            if len(percent_values) >= max_rates:
                break
        except Exception as exc:
            logger.warning("Could not process path %s: %s", path, exc)
            continue

    tax_rates: Dict[str, Optional[str]] = {}
    for index in range(1, max_rates + 1):
        if index <= len(percent_values):
            tax_rates[f"{tax_name}{index}"] = percent_values[index - 1]
        else:
            tax_rates[f"{tax_name}{index}"] = None
    return tax_rates


def find_header_tax_subtotals(
    root: Element,
    max_rates: int = MAX_HEADER_TAX_RATES,
) -> List[HeaderTaxSubtotal]:
    """Read header VAT rows so each rate stays paired with its net and VAT.

    Rates and amounts must not be collected separately: a category without
    Percent (UBL "O") would otherwise shift the following rates onto the wrong amounts.
    """
    nodes: List[Element] = _first_tax_nodes(root, _UBL_TAX_SUBTOTAL_PATHS)
    if not nodes:
        nodes = _first_tax_nodes(root, _CII_TAX_SUBTOTAL_PATHS)

    subtotals: List[HeaderTaxSubtotal] = []
    for node in nodes:
        if len(subtotals) >= max_rates:
            break
        subtotals.append(_read_header_tax_subtotal(node))
    return subtotals


def _first_tax_nodes(root: Element, paths: tuple[str, ...]) -> List[Element]:
    for path in paths:
        found: List[Element] = list(root.findall(path))
        if found:
            return found
    return []


def _read_header_tax_subtotal(node: Element) -> HeaderTaxSubtotal:
    category_node: Optional[Element] = node.find("TaxCategory")
    if category_node is not None:
        rate: Optional[str] = _element_text(category_node, "Percent")
        category: Optional[str] = _element_text(category_node, "ID")
        return HeaderTaxSubtotal(
            rate=_rate_or_zero(rate, category),
            tax_amount=_element_text(node, "TaxAmount"),
            taxable_amount=_element_text(node, "TaxableAmount"),
        )
    rate = _element_text(node, "RateApplicablePercent")
    category = _element_text(node, "CategoryCode")
    return HeaderTaxSubtotal(
        rate=_rate_or_zero(rate, category),
        tax_amount=_element_text(node, "CalculatedAmount"),
        taxable_amount=_element_text(node, "BasisAmount"),
    )


def _rate_or_zero(rate: Optional[str], category: Optional[str]) -> Optional[str]:
    if rate is not None:
        return rate
    if category is not None and category.strip().upper() in _ZERO_RATE_CATEGORIES:
        return "0"
    return None


def _element_text(element: Element, tag: str) -> Optional[str]:
    child: Optional[Element] = element.find(tag)
    if child is None or child.text is None:
        return None
    value: str = child.text.strip()
    if value == "":
        return None
    return value
