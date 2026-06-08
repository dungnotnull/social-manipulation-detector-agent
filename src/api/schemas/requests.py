from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field


class CommentItem(BaseModel):
    id: str
    text: Annotated[str, Field(min_length=10, max_length=2000)]
    author_id: str = ""
    timestamp: str = ""


class AnalyzeTextRequest(BaseModel):
    text: Annotated[str, Field(min_length=10, max_length=2000)]
    platform: str = "unknown"
    thread_id: str = ""
    author_id: str = ""


class AnalyzeThreadRequest(BaseModel):
    comments: Annotated[list[CommentItem], Field(min_length=1, max_length=200)]
    platform: str = "unknown"
    thread_id: str = ""


class AnalyzeAccountRequest(BaseModel):
    account_id: str
    platform: str
    recent_comments: list[str] = Field(default_factory=list)


class FalsePositiveRequest(BaseModel):
    verdict_id: UUID | None = None
    comment_hash: str = ""
    report_type: str = "false_positive"
    reporter_notes: str = ""


class WebhookStreamRequest(BaseModel):
    platform: str
    event: str
    comment_id: str
    text: Annotated[str, Field(min_length=10, max_length=2000)]
    author_id: str = ""
    timestamp: str = ""
