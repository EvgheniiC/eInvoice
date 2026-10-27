"""Create an e-invoice from a plain PDF. The file is not stored."""

from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_admin_user
from app.db.models import Organization
from app.helper_functions.pdf_security import UnsafePdfError, assert_pdf_safe
from app.schemas.issue import IssueBuildRequest, IssueBuildResponse, IssueDraftResponse
from app.services.auth_service import OrgContext
from app.services.export_service import decode_pdf_base64
from app.services.issue_draft import SellerSeed
from app.services.issue_service import build_issue, draft_from_pdf
from app.services.quota_service import limits_for_context

router: APIRouter = APIRouter()


@router.post("/draft", response_model=IssueDraftResponse)
async def create_issue_draft(
    file: UploadFile = File(...),
    org_context: OrgContext = Depends(require_admin_user),
    db: Session = Depends(get_db),
) -> IssueDraftResponse:
    """Read a plain PDF into an editable draft. Only an administrator may call this."""
    content: bytes = await _read_pdf(file, org_context)
    return draft_from_pdf(content, file.filename or "rechnung.pdf", seller=_seller_seed(db, org_context))


@router.post("/build", response_model=IssueBuildResponse)
def create_issue_files(
    body: IssueBuildRequest,
    org_context: OrgContext = Depends(require_admin_user),
) -> IssueBuildResponse:
    """Build XRechnung and ZUGFeRD from a confirmed draft. Download stays closed until KoSIT is valid."""
    pdf_bytes: Optional[bytes] = _optional_pdf(body.pdf_base64, org_context)
    return build_issue(body, pdf_bytes)


def _seller_seed(db: Session, org_context: OrgContext) -> Optional[SellerSeed]:
    organization: Organization | None = db.get(Organization, org_context.organization_id)
    if organization is None:
        return None
    return SellerSeed(
        name=organization.name,
        vat_id=organization.vat_id,
        iban=organization.iban,
    )


async def _read_pdf(file: UploadFile, org_context: OrgContext) -> bytes:
    filename: str = file.filename or ""
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bitte eine PDF-Datei hochladen.",
        )
    max_bytes: int = limits_for_context(org_context).max_upload_size_mb * 1024 * 1024
    content: bytes = await _read_limited(file, max_bytes)
    if len(content) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Datei ist leer.")
    try:
        assert_pdf_safe(content)
    except UnsafePdfError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return content


def _optional_pdf(pdf_base64: Optional[str], org_context: OrgContext) -> Optional[bytes]:
    if not pdf_base64:
        return None
    try:
        pdf_bytes: bytes = decode_pdf_base64(pdf_base64)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    max_bytes: int = limits_for_context(org_context).max_upload_size_mb * 1024 * 1024
    if len(pdf_bytes) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Datei ist zu groß. Maximum: {max_bytes // (1024 * 1024)} MB.",
        )
    try:
        assert_pdf_safe(pdf_bytes)
    except UnsafePdfError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return pdf_bytes


async def _read_limited(file: UploadFile, max_bytes: int) -> bytes:
    chunks: list[bytes] = []
    total_bytes: int = 0
    chunk_size: int = 64 * 1024
    while chunk := await file.read(chunk_size):
        total_bytes += len(chunk)
        if total_bytes > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Datei ist zu groß. Maximum: {max_bytes // (1024 * 1024)} MB.",
            )
        chunks.append(chunk)
    return b"".join(chunks)
