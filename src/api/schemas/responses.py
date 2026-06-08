from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field


class EvidenceItem(BaseModel):
    tactic: str
    span: str
    explanation: str


class ManipulationVerdict(BaseModel):
    verdict_id: UUID | None = None
    comment_hash: str = ""
    manipulation_index: Annotated[float, Field(ge=0.0, le=1.0)]
    confidence: str = "LOW"
    level: str = "CLEAN"
    tactics_detected: list[str] = Field(default_factory=list)
    evidence: list[EvidenceItem] = Field(default_factory=list)
    is_likely_ai_generated: bool = False
    is_likely_coordinated: bool = False
    summary: str = ""


class ThreadVerdict(BaseModel):
    thread_id: str = ""
    platform: str = "unknown"
    verdicts: list[ManipulationVerdict] = Field(default_factory=list)
    aggregate_score: Annotated[float, Field(ge=0.0, le=1.0)] = 0.0
    processed_at: datetime | None = None


class CampaignInfo(BaseModel):
    id: UUID | None = None
    name: str
    description: str = ""
    platform: str
    tactic_category: str = ""
    target_topic: str = ""
    account_count: int = 0
    comment_count: int = 0
    first_seen_at: datetime | None = None
    last_seen_at: datetime | None = None
    is_active: bool = True


class PlatformStats(BaseModel):
    platform: str
    total_scanned: int = 0
    manipulation_rate: float = 0.0
    active_campaigns: int = 0
    by_level: dict[str, int] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    error: str
    detail: str = ""
