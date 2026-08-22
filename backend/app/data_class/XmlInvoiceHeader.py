from __future__ import annotations

from dataclasses import dataclass, field, fields
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from .XmlInvoicePosition import XmlInvoicePosition


@dataclass
class XmlInvoiceHeader:
    """Neutral invoice header DTO for XRechnung / ZUGFeRD parsing."""

    invoice_id: Optional[str] = None
    receipt_date: Optional[datetime] = None
    supplier: Optional[str] = None
    client: Optional[str] = None
    contract_id: Optional[str] = None
    order_id: Optional[str] = None
    iban: Optional[str] = None
    kind_of_invoice: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    delivery_date: Optional[datetime] = None
    cost_center: Optional[str] = None
    delivery_date_till: Optional[datetime] = None
    invoice_amount: Optional[Decimal] = None
    total_amount: Optional[Decimal] = None
    total_tax_amount: Optional[Decimal] = None
    tax_rate1: Optional[Decimal] = None
    tax_amount1: Optional[Decimal] = None
    tax_rate2: Optional[Decimal] = None
    tax_amount2: Optional[Decimal] = None
    tax_rate3: Optional[Decimal] = None
    tax_amount3: Optional[Decimal] = None
    tax_rate4: Optional[Decimal] = None
    tax_amount4: Optional[Decimal] = None
    tax_rate5: Optional[Decimal] = None
    tax_amount5: Optional[Decimal] = None
    currency: Optional[str] = None
    receiver: Optional[str] = None
    contract_start: Optional[datetime] = None
    contract_end: Optional[datetime] = None
    buyer_vat_id: Optional[str] = None
    discount: Optional[Decimal] = None
    charge_total: Optional[Decimal] = None
    _positions: List[XmlInvoicePosition] = field(
        default_factory=list, init=False, repr=False, compare=False
    )

    def __post_init__(self) -> None:
        self.iban = self._normalize_iban(self.iban)

    def __setattr__(self, name: str, value: object) -> None:
        if name == "iban":
            iban_value: Optional[str]
            if value is None or isinstance(value, str):
                iban_value = value
            else:
                iban_value = str(value)
            value = self._normalize_iban(iban_value)
        super().__setattr__(name, value)

    @staticmethod
    def _normalize_iban(value: Optional[str]) -> Optional[str]:
        return value.replace(" ", "") if value else None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize header fields with neutral keys for API / tests."""
        result: Dict[str, Any] = {}
        for item in fields(self):
            if item.name.startswith("_"):
                continue
            result[item.name] = getattr(self, item.name)
        return result

    def set_dates(self) -> None:
        """Apply BT-2 fallback when neither BT-73/74 nor BT-72 was resolved."""
        if self.delivery_date is None and self.delivery_date_till is None:
            self.delivery_date = self.invoice_date
            self.delivery_date_till = self.invoice_date

    def correct_data(self) -> None:
        """Apply standard post-parse normalization used by all parsers."""
        self.set_dates()

    def add_position(self, position: XmlInvoicePosition) -> None:
        """Append a line item and link it to this invoice id."""
        position.invoice_id = self.invoice_id
        self._positions.append(position)

    def get_positions(self) -> List[XmlInvoicePosition]:
        return list(self._positions)

    def get_positions_map(self) -> List[Dict[str, Any]]:
        return [position.to_dict() for position in self._positions]
