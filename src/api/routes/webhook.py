from __future__ import annotations

from fastapi import APIRouter

from src.api.schemas.requests import WebhookStreamRequest
from src.api.schemas.responses import ManipulationVerdict
from src.api.tasks import run_pipeline_sync

router = APIRouter(prefix="/webhook", tags=["webhook"])


@router.post("/stream", response_model=ManipulationVerdict)
async def stream_comment(
    request: WebhookStreamRequest,
) -> ManipulationVerdict:
    result = run_pipeline_sync(
        text=request.text,
        platform=request.platform,
    )

    return ManipulationVerdict(
        comment_hash=result.get("comment_hash", ""),
        manipulation_index=result.get("manipulation_index", 0),
        confidence=result.get("confidence", "LOW"),
        level=result.get("level", "CLEAN"),
        tactics_detected=result.get("tactics_detected", []),
        evidence=result.get("evidence", []),
        is_likely_ai_generated=result.get("is_likely_ai_generated", False),
        is_likely_coordinated=result.get("is_likely_coordinated", False),
        summary=result.get("summary", ""),
    )
