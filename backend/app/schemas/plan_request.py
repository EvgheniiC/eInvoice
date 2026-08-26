"""API schemas for manual subscription upgrade requests."""

from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import Field, field_validator

from app.schemas.invoice import ApiModel

RequestedPlan = Literal["plus", "team"]
PlanRequestStatus = Literal["pending", "approved", "rejected"]
AdminPlanRequestStatus = Literal["approved", "rejected"]
PlanRequestListFilter = Literal["pending", "all"]


class PlanRequestCreate(ApiModel):
    requested_plan: RequestedPlan
    message: Optional[str] = Field(default=None, max_length=1000)

    @field_validator("message", mode="before")
    @classmethod
    def normalize_message(cls, value: object) -> object:
        if value is None or not isinstance(value, str):
            return value
        normalized: str = value.strip()
        return normalized or None


class PlanRequestStatusUpdate(ApiModel):
    status: AdminPlanRequestStatus


class PlanRequestResponse(ApiModel):
    id: UUID
    organization_id: UUID
    requested_by_user_id: UUID
    requested_plan: RequestedPlan
    status: PlanRequestStatus
    message: Optional[str]
    created_at: datetime
    updated_at: datetime
