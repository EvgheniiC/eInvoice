from __future__ import annotations

from decimal import Decimal
from typing import FrozenSet, List, NamedTuple, Optional, Tuple
from xml.etree.ElementTree import Element

from .amounts import parse_decimal
from .xml_query import _xml_root_local_name, find_data_within_element

_UBL_ITEM_NAME_PLACEHOLDERS: FrozenSet[str] = frozenset({"-", ".", "/", "—", "–"})
_ZERO_RATED_VAT_CATEGORIES: FrozenSet[str] = frozenset({"Z", "E", "AE", "G", "K", "O"})


class HeaderTradeAdjustment(NamedTuple):
    """Document-level allowance or charge (EN 16931 BG-20 / BG-21)."""

    amount: Decimal
    description: str
    tax_rate: Optional[Decimal]
    tax_category: Optional[str]


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


def _header_trade_settlement(xml_tree: Element) -> Optional[Element]:
    return xml_tree.find("./SupplyChainTradeTransaction/ApplicableHeaderTradeSettlement")


def _charge_indicator_text(ac: Element) -> str:
    charge_ind: Optional[Element] = ac.find("ChargeIndicator")
    if charge_ind is None:
        return ""
    indicator_el: Optional[Element] = charge_ind.find("Indicator")
    if indicator_el is not None and indicator_el.text:
        return indicator_el.text.strip().lower()
    if charge_ind.text:
        return charge_ind.text.strip().lower()
    return ""


def _charge_indicator_is_charge(ac: Element) -> Optional[bool]:
    ind_text: str = _charge_indicator_text(ac)
    if ind_text in ("true", "1"):
        return True
    if ind_text in ("false", "0"):
        return False
    return None


def _adjustment_reason(ac: Element, *, default_description: str) -> str:
    reason_el: Optional[Element] = ac.find("Reason")
    if reason_el is None:
        reason_el = ac.find("AllowanceChargeReason")
    if reason_el is not None and reason_el.text and reason_el.text.strip():
        return reason_el.text.strip()
    reason_code_el: Optional[Element] = ac.find("ReasonCode")
    if reason_code_el is None:
        reason_code_el = ac.find("AllowanceChargeReasonCode")
    if reason_code_el is not None and reason_code_el.text and reason_code_el.text.strip():
        return reason_code_el.text.strip()
    return default_description


def _category_trade_tax(ac: Element) -> Tuple[Optional[Decimal], Optional[str]]:
    tax_el: Optional[Element] = ac.find("CategoryTradeTax")
    if tax_el is None:
        tax_el = ac.find("TaxCategory")
    if tax_el is None:
        return None, None
    category_el: Optional[Element] = tax_el.find("CategoryCode")
    if category_el is None:
        category_el = tax_el.find("ID")
    tax_category: Optional[str] = (
        category_el.text.strip() if category_el is not None and category_el.text else None
    )
    rate_el: Optional[Element] = tax_el.find("RateApplicablePercent")
    if rate_el is None:
        rate_el = tax_el.find("Percent")
    tax_rate: Optional[Decimal] = None
    if rate_el is not None and rate_el.text:
        tax_rate = parse_decimal(rate_el.text.strip())
    if tax_rate is None and tax_category in _ZERO_RATED_VAT_CATEGORIES:
        tax_rate = Decimal("0")
    return tax_rate, tax_category


def _adjustment_from_cii_element(ac: Element, *, is_charge: bool) -> Optional[HeaderTradeAdjustment]:
    indicator: Optional[bool] = _charge_indicator_is_charge(ac)
    if indicator is None or indicator != is_charge:
        return None
    amt_el: Optional[Element] = ac.find("ActualAmount")
    if amt_el is None or not amt_el.text:
        return None
    amount: Optional[Decimal] = parse_decimal(amt_el.text.strip())
    if amount is None or amount <= 0:
        return None
    default_description: str = "Document charge" if is_charge else "Discount"
    tax_rate: Optional[Decimal]
    tax_category: Optional[str]
    tax_rate, tax_category = _category_trade_tax(ac)
    return HeaderTradeAdjustment(
        amount=amount,
        description=_adjustment_reason(ac, default_description=default_description),
        tax_rate=tax_rate,
        tax_category=tax_category,
    )


def _collect_header_trade_adjustments(
    xml_tree: Element, *, is_charge: bool
) -> List[HeaderTradeAdjustment]:
    settlement: Optional[Element] = _header_trade_settlement(xml_tree)
    if settlement is None:
        return []
    items: List[HeaderTradeAdjustment] = []
    for ac in settlement.findall("SpecifiedTradeAllowanceCharge"):
        parsed: Optional[HeaderTradeAdjustment] = _adjustment_from_cii_element(
            ac, is_charge=is_charge
        )
        if parsed is not None:
            items.append(parsed)
    return items


def _collect_ubl_document_charges(xml_tree: Element) -> List[HeaderTradeAdjustment]:
    items: List[HeaderTradeAdjustment] = []
    for path in ("./AllowanceCharge", "./Invoice/AllowanceCharge"):
        for ac in xml_tree.findall(path):
            if _charge_indicator_is_charge(ac) is not True:
                continue
            amount_el: Optional[Element] = ac.find("Amount")
            if amount_el is None or not amount_el.text:
                continue
            amount: Optional[Decimal] = parse_decimal(amount_el.text)
            if amount is None or amount <= 0:
                continue
            tax_rate: Optional[Decimal]
            tax_category: Optional[str]
            tax_rate, tax_category = _category_trade_tax(ac)
            items.append(
                HeaderTradeAdjustment(
                    amount=amount,
                    description=_adjustment_reason(ac, default_description="Document charge"),
                    tax_rate=tax_rate,
                    tax_category=tax_category,
                )
            )
    return items


def document_charge_description(xml_tree: Element) -> str:
    """Build position text from invoice-level charges (UBL or CII)."""
    charges: List[HeaderTradeAdjustment] = get_document_level_charges(xml_tree)
    reasons: List[str] = [
        item.description for item in charges if item.description != "Document charge"
    ]
    return "\n".join(reasons) if reasons else "Document charge"


def get_header_trade_charges(xml_tree: Element) -> List[HeaderTradeAdjustment]:
    """ZUGFeRD / Factur-X: document-level charges (ChargeIndicator true, BG-21)."""
    return _collect_header_trade_adjustments(xml_tree, is_charge=True)


def get_document_level_charges(xml_tree: Element) -> List[HeaderTradeAdjustment]:
    """
    EN 16931 BG-21 charges: CII SpecifiedTradeAllowanceCharge first, then UBL AllowanceCharge.
    """
    cii_charges: List[HeaderTradeAdjustment] = get_header_trade_charges(xml_tree)
    if cii_charges:
        return cii_charges
    return _collect_ubl_document_charges(xml_tree)


def get_header_trade_allowance_discount(
    xml_tree: Element,
) -> Optional[HeaderTradeAdjustment]:
    """
    ZUGFeRD / Factur-X: sum document-level allowances (ChargeIndicator false).
    Returns the combined adjustment or None.
    """
    items: List[HeaderTradeAdjustment] = _collect_header_trade_adjustments(
        xml_tree, is_charge=False
    )
    if not items:
        return None
    total_amount: Decimal = sum((item.amount for item in items), Decimal("0"))
    if total_amount <= 0:
        return None
    reasons: List[str] = [item.description for item in items if item.description != "Discount"]
    description: str = " / ".join(reasons) if reasons else "Discount"
    tax_rate: Optional[Decimal] = None
    tax_category: Optional[str] = None
    for item in items:
        if item.tax_rate is not None:
            tax_rate = item.tax_rate
        if item.tax_category:
            tax_category = item.tax_category
    return HeaderTradeAdjustment(
        amount=total_amount,
        description=description,
        tax_rate=tax_rate,
        tax_category=tax_category,
    )
