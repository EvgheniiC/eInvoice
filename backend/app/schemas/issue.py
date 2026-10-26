"""Outbound draft used to create an e-invoice from a plain PDF."""

from decimal import Decimal
from typing import List, Literal, Optional

from pydantic import Field

from app.schemas.invoice import ApiModel, ValidationIssue, ValidationStatus

IssueArtifactFormat = Literal["xrechnung", "zugferd_xml", "zugferd_pdf"]
FieldSource = Literal["pdf", "organization", "empty"]


class IssueAddress(ApiModel):
    """Postal address entered or read for one party."""

    line: Optional[str] = None
    postcode: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None


class IssueParty(ApiModel):
    """Seller or buyer data for an outgoing invoice."""

    name: Optional[str] = None
    address: IssueAddress = Field(default_factory=IssueAddress)
    vat_id: Optional[str] = None
    email: Optional[str] = None
    contact_name: Optional[str] = None
    phone: Optional[str] = None
    iban: Optional[str] = None


class IssueLineInput(ApiModel):
    """One invoice line before totals are calculated."""

    description: Optional[str] = None
    quantity: Optional[Decimal] = None
    unit_code: Optional[str] = None
    unit_price: Optional[Decimal] = None
    tax_rate: Optional[Decimal] = None


class IssueDraft(ApiModel):
    """Editable invoice the issuer confirms before XML is built."""

    invoice_number: Optional[str] = None
    issue_date: Optional[str] = None
    currency: str = "EUR"
    buyer_reference: Optional[str] = None
    seller: IssueParty = Field(default_factory=IssueParty)
    buyer: IssueParty = Field(default_factory=IssueParty)
    lines: List[IssueLineInput] = Field(default_factory=list)


class FieldHint(ApiModel):
    """Where a draft value came from, so the form can show uncertainty."""

    field: str
    source: FieldSource
    message: str


class IssueDraftResponse(ApiModel):
    """Best-effort draft. Nothing is stored after the response is sent."""

    filename: str
    text_found: bool
    draft: IssueDraft
    hints: List[FieldHint] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class IssueBuildRequest(ApiModel):
    """Confirmed draft plus the original PDF used for a ZUGFeRD container."""

    draft: IssueDraft
    pdf_base64: Optional[str] = None
    confirmed: bool = False


class IssueArtifact(ApiModel):
    """One generated file. Bytes are present only after a completed valid KoSIT run."""

    format: IssueArtifactFormat
    filename: str
    media_type: str
    content_base64: Optional[str] = None
    download_allowed: bool
    validation_status: ValidationStatus
    validation_issues: List[ValidationIssue] = Field(default_factory=list)


class IssueBuildResponse(ApiModel):
    """Build result. Download stays closed until KoSIT reports the file valid."""

    ready: bool
    message: str
    blocking_issues: List[ValidationIssue] = Field(default_factory=list)
    artifacts: List[IssueArtifact] = Field(default_factory=list)
