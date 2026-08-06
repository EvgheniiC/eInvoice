from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional


@dataclass
class XmlInvoicePosition:
    """Neutral invoice line-item DTO for XRechnung / ZUGFeRD parsing."""

    item_pos: int = 1
    position_text: Optional[str] = None
    quantity: float = 1.0
    single_net_price: Optional[float] = None
    tax_rate: Optional[float] = None
    total_net_price: Optional[float] = None
    invoice_id: Optional[str] = None
    article_number: Optional[str] = None
    quantity_unit: Optional[float] = None
    discount_percent: Optional[float] = None
    inventory_account: Optional[float] = None
    tax_code: Optional[str] = None
    discount_amount: Optional[float] = None
    order_pos_id: Optional[str] = None
    e_class: Optional[str] = None

    def __post_init__(self) -> None:
        self.order_pos_id = self.order_pos_id or ""
        self.e_class = self.e_class or ""

    def to_dict(self) -> Dict[str, Any]:
        """Serialize line-item fields with neutral keys."""
        return asdict(self)
