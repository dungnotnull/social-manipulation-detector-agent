from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.api.db import Base


class Verdict(Base):
    __tablename__ = "verdicts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    comment_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    comment_text: Mapped[str] = mapped_column(Text, nullable=False)
    platform: Mapped[str | None] = mapped_column(String(32))
    thread_id: Mapped[str | None] = mapped_column(String(256))
    author_id: Mapped[str | None] = mapped_column(String(256))
    manipulation_index: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    confidence: Mapped[str] = mapped_column(String(16), default="LOW", nullable=False)
    level: Mapped[str] = mapped_column(String(16), default="CLEAN", nullable=False)
    tactics_detected: Mapped[dict] = mapped_column(JSONB, default=list)
    evidence: Mapped[dict] = mapped_column(JSONB, default=list)
    is_likely_ai_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    is_likely_coordinated: Mapped[bool] = mapped_column(Boolean, default=False)
    summary: Mapped[str | None] = mapped_column(Text)
    signals_raw: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    platform: Mapped[str] = mapped_column(String(32), nullable=False)
    tactic_category: Mapped[str | None] = mapped_column(String(64))
    target_topic: Mapped[str | None] = mapped_column(String(256))
    account_count: Mapped[int] = mapped_column(Integer, default=0)
    comment_count: Mapped[int] = mapped_column(Integer, default=0)
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    cluster_data: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    verdict_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("verdicts.id", ondelete="SET NULL"), nullable=True
    )
    report_type: Mapped[str] = mapped_column(String(32), nullable=False)
    reporter_notes: Mapped[str | None] = mapped_column(Text)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    resolution: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    verdict: Mapped[Verdict | None] = relationship("Verdict")
