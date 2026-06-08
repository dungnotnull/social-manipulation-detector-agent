from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db
from src.api.models import Campaign, Verdict
from src.api.schemas.responses import CampaignInfo, PlatformStats

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.get("/active", response_model=list[CampaignInfo])
async def get_active_campaigns(
    session: AsyncSession = Depends(get_db),
) -> list[CampaignInfo]:
    stmt = select(Campaign).where(Campaign.is_active == True).order_by(Campaign.last_seen_at.desc())
    result = await session.execute(stmt)
    campaigns = result.scalars().all()

    return [
        CampaignInfo(
            id=c.id,
            name=c.name,
            description=c.description or "",
            platform=c.platform,
            tactic_category=c.tactic_category or "",
            target_topic=c.target_topic or "",
            account_count=c.account_count,
            comment_count=c.comment_count,
            first_seen_at=c.first_seen_at,
            last_seen_at=c.last_seen_at,
            is_active=c.is_active,
        )
        for c in campaigns
    ]


@router.get("/stats/platform/{platform_name}", response_model=PlatformStats)
async def get_platform_stats(
    platform_name: str,
    session: AsyncSession = Depends(get_db),
) -> PlatformStats:
    count_stmt = (
        select(func.count(Verdict.id))
        .where(Verdict.platform == platform_name)
    )
    total = await session.scalar(count_stmt) or 0

    campaign_stmt = (
        select(func.count(Campaign.id))
        .where(Campaign.platform == platform_name, Campaign.is_active == True)
    )
    active_campaigns = await session.scalar(campaign_stmt) or 0

    manipulation_count = await session.scalar(
        select(func.count(Verdict.id)).where(
            Verdict.platform == platform_name,
            Verdict.manipulation_index >= 0.65,
        )
    ) or 0

    rate = round(manipulation_count / total, 4) if total > 0 else 0.0

    levels = {}
    for level in ["HIGH", "ELEVATED", "MODERATE", "LOW", "CLEAN"]:
        lc = await session.scalar(
            select(func.count(Verdict.id)).where(
                Verdict.platform == platform_name,
                Verdict.level == level,
            )
        ) or 0
        levels[level] = lc

    return PlatformStats(
        platform=platform_name,
        total_scanned=total,
        manipulation_rate=rate,
        active_campaigns=active_campaigns,
        by_level=levels,
    )
