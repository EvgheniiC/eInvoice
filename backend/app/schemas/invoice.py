from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class ParseStatus(str, Enum):
    """High-level parse outcome for the uploaded invoice."""

    SUCCESS = "success"
    PARTIAL = "partial"
    ERROR = "error"
    NOT_IMPLEMENTED = "not_implemented"


class ValidationStatus(str, Enum):
    """EN 16931 / business validation outcome shown in the UI."""

    VALID = "valid"
    INVALID = "invalid"
    WARNING = "warning"
    NOT_CHECKED = "not_checked"


class PartyInfo(BaseModel):
    """Seller or buyer party information."""

    name: Optional[str] = None
    address: Optional[str] = None
    vat_id: Optional[str] = None
    iban: Optional[str] = None


class LineItem(BaseModel):
    """Single invoice line item for UI/export."""

    position: Optional[int] = None
    description: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    unit_price: Optional[float] = None
    tax_rate: Optional[float] = None
    net_amount: Optional[float] = None
    gross_amount: Optional[float] = None


class InvoiceTotals(BaseModel):
    """Invoice monetary totals."""

    net: Optional[float] = None
    tax: Optional[float] = None
    gross: Optional[float] = None
    currency: Optional[str] = None


class ValidationIssue(BaseModel):
    """Single validation warning or error for the user."""

    level: str = Field(description="error | warning | info")
    category: str = Field(
        default="business",
        description="schema | business | mismatch | info",
    )
    code: Optional[str] = None
    message: str


class MismatchField(BaseModel):
    """PDF vs XML field comparison result for ZUGFeRD."""

    field: str
    label: str
    xml_value: Optional[str] = None
    pdf_value: Optional[str] = None
    matched: bool


class InvoiceParseResponse(BaseModel):
    """Normalized invoice DTO returned to the frontend."""

    status: ParseStatus
    message: str
    filename: str
    file_type: Optional[str] = None
    invoice_number: Optional[str] = None
    issue_date: Optional[str] = None
    due_date: Optional[str] = None
    seller: Optional[PartyInfo] = None
    buyer: Optional[PartyInfo] = None
    totals: Optional[InvoiceTotals] = None
    line_items: List[LineItem] = Field(default_factory=list)
    payment_reference: Optional[str] = None
    validation_status: ValidationStatus = ValidationStatus.NOT_CHECKED
    validation_issues: List[ValidationIssue] = Field(default_factory=list)
    mismatch_warnings: List[str] = Field(default_factory=list)
    mismatch_fields: List[MismatchField] = Field(default_factory=list)
    next_steps: List[str] = Field(default_factory=list)
