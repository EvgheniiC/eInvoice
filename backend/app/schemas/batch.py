from enum import Enum
from typing import List, Optional
from uuid import UUID

from app.schemas.invoice import ApiModel, InvoiceParseResponse


class BatchJobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"


class BatchItemStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    GUELTIG = "gueltig"
    PRUEFEN = "pruefen"
    ABLEHNEN = "ablehnen"


class BatchItemResponse(ApiModel):
    id: UUID
    filename: str
    status: BatchItemStatus
    invoice_number: Optional[str] = None
    seller_name: Optional[str] = None
    gross_amount: Optional[str] = None
    currency: Optional[str] = None
    message: Optional[str] = None
    invoice: Optional[InvoiceParseResponse] = None


class BatchJobResponse(ApiModel):
    id: UUID
    status: BatchJobStatus
    item_count: int
    done_count: int
    items: List[BatchItemResponse]
    export_package_available: bool = False
    view_pdf_package_available: bool = False
