from datetime import datetime
from typing import List, Literal, Optional
from uuid import UUID

from app.schemas.invoice import ApiModel

HistorySource = Literal["parse", "batch"]
HistoryItemStatus = Literal["gueltig", "pruefen", "ablehnen"]


class HistoryItemResponse(ApiModel):
    id: UUID
    processed_at: datetime
    filename: str
    file_hash: str
    seller_name: Optional[str] = None
    invoice_number: Optional[str] = None
    issue_date: Optional[str] = None
    gross_amount: Optional[str] = None
    currency: Optional[str] = None
    status: HistoryItemStatus
    source: HistorySource
    original_available: bool
    original_expires_at: Optional[datetime] = None


class HistoryListResponse(ApiModel):
    items: List[HistoryItemResponse]
    total: int
    history_enabled: bool
    store_originals_enabled: bool
    original_retention_days: int
