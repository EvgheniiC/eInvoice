import re
from datetime import datetime
from typing import List, Literal, Optional
from uuid import UUID

from pydantic import EmailStr, Field, TypeAdapter, field_validator

from app.schemas.invoice import ApiModel

_EMAIL_ADAPTER: TypeAdapter[EmailStr] = TypeAdapter(EmailStr)
_VAT_ID_RE: re.Pattern[str] = re.compile(r"[A-Z]{2}[A-Z0-9]{2,14}")


def _compact_alnum(value: object) -> Optional[str]:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("Ungültiger Wert.")
    cleaned: str = re.sub(r"[\s-]+", "", value).upper()
    if cleaned == "":
        return None
    return cleaned


def iban_checksum_ok(iban: str) -> bool:
    """ISO 13616: length, charset, and MOD-97 checksum."""
    if len(iban) < 15 or len(iban) > 34:
        return False
    if not iban[:2].isalpha() or not iban[2:4].isdigit() or not iban.isalnum():
        return False
    rearranged: str = iban[4:] + iban[:4]
    numeric: str = "".join(str(ord(char) - 55) if char.isalpha() else char for char in rearranged)
    return int(numeric) % 97 == 1


def validated_vat_id(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    if not _VAT_ID_RE.fullmatch(value):
        raise ValueError("USt-IdNr. ist ungültig.")
    return value


def validated_iban(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    if not iban_checksum_ok(value):
        raise ValueError("IBAN ist ungültig.")
    return value


def validated_accountant_email(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    try:
        return str(_EMAIL_ADAPTER.validate_python(value))
    except Exception as exc:
        raise ValueError("E-Mail des Steuerberaters ist ungültig.") from exc


MembershipRole = Literal["inhaber", "buero", "export_only"]
PlanCode = Literal["free", "plus", "team"]
EmailTokenPurpose = Literal["verify_email", "magic_link", "reset_password"]


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


class ResetPasswordRequest(ApiModel):
    token: str = Field(min_length=8, max_length=128)
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
    history_enabled: bool = False
    store_originals_enabled: bool = False


class OrgUpdateRequest(ApiModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    history_enabled: Optional[bool] = None
    store_originals_enabled: Optional[bool] = None
    tax_number: Optional[str] = Field(default=None, max_length=32)
    vat_id: Optional[str] = Field(default=None, max_length=16)
    iban: Optional[str] = Field(default=None, max_length=42)
    accountant_email: Optional[str] = Field(default=None, max_length=254)

    @field_validator("tax_number", mode="before")
    @classmethod
    def normalize_tax_number(cls, value: object) -> object:
        if value is None:
            return None
        if not isinstance(value, str):
            return value
        stripped: str = " ".join(value.split())
        return stripped or None

    @field_validator("vat_id", mode="before")
    @classmethod
    def normalize_vat_id(cls, value: object) -> object:
        return _compact_alnum(value)

    @field_validator("iban", mode="before")
    @classmethod
    def normalize_iban(cls, value: object) -> object:
        return _compact_alnum(value)

    @field_validator("accountant_email", mode="before")
    @classmethod
    def normalize_accountant_email(cls, value: object) -> object:
        if value is None:
            return None
        if not isinstance(value, str):
            return value
        stripped: str = value.strip()
        return stripped or None


class OrgResponse(ApiModel):
    organization_id: UUID
    name: str
    role: str
    plan: PlanInfo
    created_at: datetime
    history_enabled: bool = False
    store_originals_enabled: bool = False
    tax_number: Optional[str] = None
    vat_id: Optional[str] = None
    iban: Optional[str] = None
    accountant_email: Optional[str] = None


class SetPlanRequest(ApiModel):
    plan_code: PlanCode


class SetPlanByEmailRequest(ApiModel):
    email: EmailStr
    plan_code: PlanCode
