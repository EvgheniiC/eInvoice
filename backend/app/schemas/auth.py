from datetime import datetime
from typing import List, Literal, Optional
from uuid import UUID

from pydantic import EmailStr, Field

from app.schemas.invoice import ApiModel

MembershipRole = Literal["inhaber", "buero", "export_only"]
PlanCode = Literal["free", "plus", "team"]
EmailTokenPurpose = Literal["verify_email", "magic_link"]


class RegisterRequest(ApiModel):
    email: EmailStr
    password: str = Field(min_length=10, max_length=72)
    organization_name: Optional[str] = Field(default=None, max_length=120)


class RegisterResponse(ApiModel):
    accepted: bool
    message: str
    verification_token: Optional[str] = None


class LoginRequest(ApiModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)


class MagicLinkRequest(ApiModel):
    email: EmailStr


class TokenRequest(ApiModel):
    token: str = Field(min_length=8, max_length=128)


class MessageResponse(ApiModel):
    accepted: bool
    message: str
    token: Optional[str] = None


class ChangePasswordRequest(ApiModel):
    current_password: str = Field(min_length=1, max_length=72)
    new_password: str = Field(min_length=10, max_length=72)


class PlanInfo(ApiModel):
    code: str
    name: str
    parse_per_day: int
    export_per_day: int
    max_upload_size_mb: int
    max_parallel: int = 1
    allows_batch: bool
    allows_history: bool
    max_batch_files: int = 0
    quotas_enforced: bool = True
    parse_used_today: int = 0
    export_used_today: int = 0


class MembershipInfo(ApiModel):
    organization_id: UUID
    organization_name: str
    role: str


class MeResponse(ApiModel):
    user_id: UUID
    email: str
    email_verified: bool
    organization_id: UUID
    organization_name: str
    role: str
    plan: PlanInfo
    memberships: List[MembershipInfo]


class OrgUpdateRequest(ApiModel):
    name: str = Field(min_length=2, max_length=120)


class OrgResponse(ApiModel):
    organization_id: UUID
    name: str
    role: str
    plan: PlanInfo
    created_at: datetime


class SetPlanRequest(ApiModel):
    plan_code: PlanCode


class SetPlanByEmailRequest(ApiModel):
    email: EmailStr
    plan_code: PlanCode
