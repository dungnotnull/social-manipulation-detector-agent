from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db
from src.api.models import Feedback
from src.api.schemas.requests import FalsePositiveRequest
from src.api.schemas.responses import ErrorResponse

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("/false-positive")
async def report_false_positive(
    request: FalsePositiveRequest,
    session: AsyncSession = Depends(get_db),
) -> dict:
    feedback = Feedback(
        verdict_id=request.verdict_id,
        report_type=request.report_type,
        reporter_notes=request.reporter_notes,
    )
    session.add(feedback)
    await session.commit()

    return {"status": "received", "id": str(feedback.id)}
