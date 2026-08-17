from __future__ import annotations

from decimal import Decimal
from typing import FrozenSet, List, Optional, Tuple
from xml.etree.ElementTree import Element

from .amounts import parse_decimal
from .xml_query import _xml_root_local_name, find_data_within_element

_UBL_ITEM_NAME_PLACEHOLDERS: FrozenSet[str] = frozenset({"-", ".", "/", "—", "–"})


def _ubl_item_name_is_placeholder(name: str) -> bool:
    """True if supplier used a sentinel instead of a real article name."""
    trimmed: str = name.strip()
    if not trimmed:
        return True
    return trimmed in _UBL_ITEM_NAME_PLACEHOLDERS


def is_ubl_placeholder_text(value: Optional[str]) -> bool:
    """True if text is empty or an Item/line placeholder (-, ., /)."""
    if value is None:
        return True
    return _ubl_item_name_is_placeholder(value)


def build_description_from_item(position: Optional[Element]) -> Optional[str]:
    """
    Build position description from Item (UBL) or SpecifiedTradeProduct (ZUGFeRD).
    """
    if position is None:
        return None
    parts: List[str] = []

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
            if (
                prop_name_el is not None
                and prop_name_el.text
                and prop_value_el is not None
                and prop_value_el.text
            ):
                parts.append(prop_name_el.text.strip())
                parts.append(prop_value_el.text.strip())
        if parts:
            return " ".join(parts)

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


def _is_gu_document(xml_tree: Element, kind_of_invoice: Optional[str] = None) -> bool:
    """
    Whether the document is GU (credit note): negative amounts should map to positive display.
    """
    if kind_of_invoice in ("GU", "RE"):
        return kind_of_invoice == "GU"

    kind_code: Optional[str] = find_data_within_element(
        xml_tree,
        [
            "./CreditNoteTypeCode",
            "./Invoice/CreditNoteTypeCode",
            "./InvoiceTypeCode",
            "./Invoice/InvoiceTypeCode",
        ],
    )
    if kind_code:
        return kind_code == "381"

    return _xml_root_local_name(xml_tree) == "CreditNote"


def document_charge_description(xml_tree: Element) -> str:
    """Build position text from invoice-level AllowanceCharge with ChargeIndicator true."""
    reasons: List[str] = []
    for path in ("./AllowanceCharge", "./Invoice/AllowanceCharge"):
        for ac in xml_tree.findall(path):
            indicator: Optional[Element] = ac.find("ChargeIndicator")
            if indicator is None or not indicator.text or indicator.text.strip().lower() != "true":
                continue
            amount_el: Optional[Element] = ac.find("Amount")
            if amount_el is None or not amount_el.text:
                continue
            amount: Optional[Decimal] = parse_decimal(amount_el.text)
            if amount is None or amount <= 0:
                continue
            reason_el: Optional[Element] = ac.find("AllowanceChargeReason")
            if reason_el is not None and reason_el.text:
                reasons.append(reason_el.text.strip())
    return "\n".join(reasons) if reasons else "Document charge"


def get_header_trade_allowance_discount(
    xml_tree: Element,
) -> Optional[Tuple[Decimal, str, Optional[Decimal]]]:
    """
    ZUGFeRD / Factur-X: sum document-level allowances (ChargeIndicator false).
    Returns (net amount, combined reason text, VAT percent) or None.
    """
    settlement: Optional[Element] = xml_tree.find(
        "./SupplyChainTradeTransaction/ApplicableHeaderTradeSettlement"
    )
    if settlement is None:
        return None
    total_amount: Decimal = Decimal("0")
    reasons: List[str] = []
    tax_rate: Optional[Decimal] = None
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
        amt: Decimal = parse_decimal(amt_el.text.strip()) or Decimal("0")
        if amt <= 0:
            continue
        total_amount += amt
        reason_el: Optional[Element] = ac.find("Reason")
        if reason_el is not None and reason_el.text:
            reasons.append(reason_el.text.strip())
        rt_el: Optional[Element] = ac.find("CategoryTradeTax/RateApplicablePercent")
        if rt_el is not None and rt_el.text:
            tax_rate = parse_decimal(rt_el.text.strip()) or Decimal("0")
    if total_amount <= 0:
        return None
    description: str = " / ".join(reasons) if reasons else "Discount"
    return (total_amount, description, tax_rate)
