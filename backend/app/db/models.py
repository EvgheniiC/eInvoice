"""SQLAlchemy ORM models for accounts. Invoice bytes are never stored in these tables."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, JSON, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from app.core.clock import utc_now


class Base(DeclarativeBase):
    """Declarative base for account tables."""


class Plan(Base):
    """Subscription plan with daily parse/export quotas."""

    __tablename__: str = "plans"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(64))
    parse_per_day: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    export_per_day: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    max_upload_size_mb: Mapped[int] = mapped_column(Integer, default=10)
    max_parallel: Mapped[int] = mapped_column(Integer, default=1)
    allows_batch: Mapped[bool] = mapped_column(Boolean, default=False)
    allows_history: Mapped[bool] = mapped_column(Boolean, default=False)

    organizations: Mapped[list["Organization"]] = relationship(back_populates="plan")


class User(Base):
    """Login identity. One user may belong to several organizations."""

    __tablename__: str = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    email_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    password_changed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    memberships: Mapped[list["Membership"]] = relationship(back_populates="user")
    sessions: Mapped[list["AuthSession"]] = relationship(back_populates="user")


class Organization(Base):
    """Firma / Handwerk. Not 1:1 with a user."""

    __tablename__: str = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(120))
    plan_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("plans.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    history_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    store_originals_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    history_enabled_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    tax_number: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    vat_id: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    iban: Mapped[Optional[str]] = mapped_column(String(34), nullable=True)
    accountant_email: Mapped[Optional[str]] = mapped_column(String(254), nullable=True)

    plan: Mapped[Plan] = relationship(back_populates="organizations")
    memberships: Mapped[list["Membership"]] = relationship(back_populates="organization")
    batch_jobs: Mapped[list["BatchJob"]] = relationship(
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    history_records: Mapped[list["InvoiceHistory"]] = relationship(
        back_populates="organization",
        cascade="all, delete-orphan",
    )


class Membership(Base):
    """User ↔ organization with a role (Inhaber / Büro / nur Export)."""

    __tablename__: str = "memberships"
    __table_args__ = (UniqueConstraint("user_id", "organization_id", name="uq_membership_user_org"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    role: Mapped[str] = mapped_column(String(32))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    user: Mapped[User] = relationship(back_populates="memberships")
    organization: Mapped[Organization] = relationship(back_populates="memberships")


class AuthSession(Base):
    """Server-side session. Cookie stores the raw id; DB stores the hash."""

    __tablename__: str = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped[User] = relationship(back_populates="sessions")


class EmailToken(Base):
    """Hashed one-time token for email verify, magic link, or password reset."""

    __tablename__: str = "email_tokens"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    purpose: Mapped[str] = mapped_column(String(32), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    consumed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class UsageCounter(Base):
    """Daily parse/export counts. Guest rows use a hashed IP, never the raw address."""

    __tablename__: str = "usage_counters"
    __table_args__ = (
        UniqueConstraint(
            "subject_type",
            "subject_key",
            "usage_date",
            "action",
            name="uq_usage_counter_day",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    subject_type: Mapped[str] = mapped_column(String(16), index=True)
    subject_key: Mapped[str] = mapped_column(String(64), index=True)
    usage_date: Mapped[date] = mapped_column(Date, index=True)
    action: Mapped[str] = mapped_column(String(16))
    count: Mapped[int] = mapped_column(Integer, default=0)


class BatchJob(Base):
    """Queued Plus/Team upload. Original files live only in short-lived temp paths."""

    __tablename__: str = "batch_jobs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        index=True,
    )
    created_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(16), index=True, default="queued")
    item_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    organization: Mapped["Organization"] = relationship(back_populates="batch_jobs")
    items: Mapped[list["BatchItem"]] = relationship(
        back_populates="job",
        cascade="all, delete-orphan",
        order_by="BatchItem.position",
    )


class BatchItem(Base):
    """One file in a batch. Parse metadata/result in DB; original bytes stay on disk until TTL."""

    __tablename__: str = "batch_items"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("batch_jobs.id", ondelete="CASCADE"),
        index=True,
    )
    position: Mapped[int] = mapped_column(Integer, default=0)
    filename: Mapped[str] = mapped_column(String(255))
    storage_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(String(16), index=True, default="queued")
    invoice_number: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    seller_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    gross_amount: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    currency: Mapped[Optional[str]] = mapped_column(String(8), nullable=True)
    message: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    result_json: Mapped[Optional[dict[str, object]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    claimed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    job: Mapped["BatchJob"] = relationship(back_populates="items")


class InvoiceHistory(Base):
    """Opt-in parse journal. Default is metadata + file hash; original bytes stay on disk."""

    __tablename__: str = "invoice_history"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        index=True,
    )
    created_by_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    processed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)
    filename: Mapped[str] = mapped_column(String(255))
    file_hash: Mapped[str] = mapped_column(String(64), index=True)
    seller_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    invoice_number: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    issue_date: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    gross_amount: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    currency: Mapped[Optional[str]] = mapped_column(String(8), nullable=True)
    status: Mapped[str] = mapped_column(String(16))
    source: Mapped[str] = mapped_column(String(16))
    batch_job_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("batch_jobs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    original_storage_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    original_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    result_json: Mapped[Optional[dict[str, object]]] = mapped_column(JSON, nullable=True)

    organization: Mapped["Organization"] = relationship(back_populates="history_records")
