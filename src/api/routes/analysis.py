from __future__ import annotations

import hashlib
import json

from fastapi import APIRouter, Depends, HTTPException

from src.api.dependencies import get_db, get_redis
from src.api.models import Verdict
from src.api.schemas.requests import AnalyzeAccountRequest, AnalyzeTextRequest, AnalyzeThreadRequest
from src.api.schemas.responses import ManipulationVerdict, ThreadVerdict
from src.api.tasks import run_pipeline_sync, run_thread_pipeline_sync
from src.analyzer.account_features import AccountFeatureExtractor
from src.analyzer.behavior_analyzer import BehaviorAnalyzer, BehaviorScore
from src.config import settings
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/analyze", tags=["analysis"])

_account_extractor = AccountFeatureExtractor()
_behavior = BehaviorAnalyzer()


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


@router.post("/text", response_model=ManipulationVerdict)
async def analyze_text(
    request: AnalyzeTextRequest,
    session: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
) -> ManipulationVerdict:
    comment_hash = _hash_text(request.text)

    cached = await redis.get(f"verdict:{comment_hash}")
    if cached:
        return ManipulationVerdict(**json.loads(cached))

    result = run_pipeline_sync(
        text=request.text,
        platform=request.platform,
    )

    verdict_data = {
        "comment_hash": comment_hash,
        "comment_text": request.text,
        "platform": request.platform,
        "thread_id": request.thread_id,
        "author_id": request.author_id,
        "manipulation_index": result.get("manipulation_index", 0),
        "confidence": result.get("confidence", "LOW"),
        "level": result.get("level", "CLEAN"),
        "tactics_detected": result.get("tactics_detected", []),
        "evidence": result.get("evidence", []),
        "is_likely_ai_generated": result.get("is_likely_ai_generated", False),
        "is_likely_coordinated": result.get("is_likely_coordinated", False),
        "summary": result.get("summary", ""),
        "signals_raw": result,
    }

    await redis.setex(
        f"verdict:{comment_hash}",
        settings.verdict_cache_ttl_hours * 3600,
        json.dumps(verdict_data, default=str),
    )

    db_verdict = Verdict(**verdict_data)
    session.add(db_verdict)
    await session.commit()

    return ManipulationVerdict(**verdict_data)


@router.post("/thread", response_model=ThreadVerdict)
async def analyze_thread(
    request: AnalyzeThreadRequest,
    session: AsyncSession = Depends(get_db),
) -> ThreadVerdict:
    if len(request.comments) > 200:
        raise HTTPException(status_code=422, detail="Maximum 200 comments per thread")

    comments_payload = [
        {
            "id": c.id,
            "text": c.text,
            "author_id": c.author_id,
            "timestamp": c.timestamp,
            "thread_id": request.thread_id,
        }
        for c in request.comments
    ]

    result = run_thread_pipeline_sync(comments=comments_payload, platform=request.platform)

    verdicts = []
    for v in result.get("verdicts", []):
        verdicts.append(ManipulationVerdict(
            comment_hash=v.get("comment_hash", ""),
            manipulation_index=v.get("manipulation_index", 0),
            confidence=v.get("confidence", "LOW"),
            level=v.get("level", "CLEAN"),
            tactics_detected=v.get("tactics_detected", []),
            evidence=v.get("evidence", []),
            is_likely_ai_generated=v.get("is_likely_ai_generated", False),
            is_likely_coordinated=v.get("is_likely_coordinated", False),
            summary=v.get("summary", ""),
        ))

    return ThreadVerdict(
        thread_id=request.thread_id,
        platform=request.platform,
        verdicts=verdicts,
        aggregate_score=result.get("aggregate_score", 0),
    )


@router.post("/account", response_model=dict)
async def analyze_account(
    request: AnalyzeAccountRequest,
) -> dict:
    result: dict = {
        "account_id": request.account_id,
        "platform": request.platform,
        "risk_signals": [],
        "bot_score": 0.0,
        "details": {},
    }

    if request.platform == "twitter":
        from src.api.platforms.twitter import TwitterClient
        client = TwitterClient()
        try:
            account = await client.get_account(request.account_id)
            if account:
                features = _account_extractor.extract_from_twitter_account(account)
                behavior = _behavior.analyze_account_features(features)
                result["risk_signals"] = features.risk_signals
                result["bot_score"] = features.bot_score
                result["details"] = behavior.account_features_detail
        finally:
            await client.close()
    elif request.platform == "reddit":
        from src.api.platforms.reddit import RedditClient
        client = RedditClient()
        try:
            account = await client.get_user(request.account_id)
            if account:
                features = _account_extractor.extract_from_reddit_account(account)
                behavior = _behavior.analyze_account_features(features)
                result["risk_signals"] = features.risk_signals
                result["bot_score"] = features.bot_score
                result["details"] = behavior.account_features_detail
        finally:
            await client.close()

    return result


@router.get("/verdict/{verdict_id}", response_model=ManipulationVerdict)
async def get_verdict(
    verdict_id: str,
    session: AsyncSession = Depends(get_db),
) -> ManipulationVerdict:
    stmt = select(Verdict).where(Verdict.id == verdict_id)
    result = await session.execute(stmt)
    verdict = result.scalar_one_or_none()

    if not verdict:
        raise HTTPException(status_code=404, detail="Verdict not found")

    return ManipulationVerdict(
        verdict_id=verdict.id,
        comment_hash=verdict.comment_hash,
        manipulation_index=verdict.manipulation_index,
        confidence=verdict.confidence,
        level=verdict.level,
        tactics_detected=verdict.tactics_detected,
        evidence=verdict.evidence,
        is_likely_ai_generated=verdict.is_likely_ai_generated,
        is_likely_coordinated=verdict.is_likely_coordinated,
        summary=verdict.summary or "",
    )
