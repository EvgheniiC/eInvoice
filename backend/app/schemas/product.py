from typing import List, Literal, Optional

from app.schemas.invoice import ApiModel

FunnelStep = Literal["landing", "upload", "parse_success", "export"]
ClientFunnelStep = Literal["landing", "upload"]


class SupportedFormat(ApiModel):
    """One accepted invoice format shown on the landing and upload pages."""

    id: str
    label: str
    extensions: List[str]
    notes: str


class CapabilitiesResponse(ApiModel):
    """Public product limits, formats, and guest processing model."""

    max_upload_size_mb: int
    allowed_extensions: List[str]
    max_files_per_request: int
    rate_limit_per_minute: int
    stores_invoice_files: bool
    requires_account: bool
    processing_model: str
    standard_version: str
    xrechnung_version: str
    formats: List[SupportedFormat]
    profiles: List[str]
    limitations: List[str]


class FunnelEventRequest(ApiModel):
    """Privacy-safe funnel ping: step name only, no invoice payload."""

    step: ClientFunnelStep


class FunnelEventResponse(ApiModel):
    """Acknowledgement for a funnel ping."""

    accepted: bool


class FeedbackRequest(ApiModel):
    """Text-only feedback. Files and invoice payloads are rejected."""

    message: str
    contact_email: Optional[str] = None


class FeedbackResponse(ApiModel):
    """Acknowledgement for submitted feedback."""

    accepted: bool
    message: str
