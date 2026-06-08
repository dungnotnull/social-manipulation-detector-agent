from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.dependencies import get_db
from src.api.platforms.twitter import TwitterClient
from src.api.platforms.reddit import RedditClient
from src.api.platforms.youtube import YoutubeClient
from src.api.schemas.responses import ManipulationVerdict, ThreadVerdict
from src.api.tasks import run_pipeline_sync, run_thread_pipeline_sync
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/stream", tags=["stream"])


@router.get("/twitter/search", response_model=list[dict])
async def stream_twitter_search(
    query: str = Query(..., min_length=2),
    max_results: int = Query(default=20, le=100),
) -> list[dict]:
    client = TwitterClient()
    try:
        comments = await client.search_comments(query, max_results)
        return [
            {
                "id": c.id,
                "text": c.text,
                "author_id": c.author_id,
                "author_username": c.author_username,
                "created_at": c.created_at,
                "metrics": {
                    "likes": c.like_count,
                    "retweets": c.retweet_count,
                    "replies": c.reply_count,
                },
            }
            for c in comments
        ]
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Twitter API error: {e}")
    finally:
        await client.close()


@router.post("/twitter/search-and-analyze", response_model=ThreadVerdict)
async def stream_twitter_analyze(
    query: str = Query(..., min_length=2),
    max_results: int = Query(default=10, le=50),
    session: AsyncSession = Depends(get_db),
) -> ThreadVerdict:
    client = TwitterClient()
    try:
        comments = await client.search_comments(query, max_results)
        if not comments:
            return ThreadVerdict(thread_id=query, platform="twitter", verdicts=[])

        payload = [
            {"id": c.id, "text": c.text, "author_id": c.author_id, "timestamp": c.created_at}
            for c in comments
        ]
        result = run_thread_pipeline_sync(comments=payload, platform="twitter")

        verdicts = [
            ManipulationVerdict(
                comment_hash=v.get("comment_hash", ""),
                manipulation_index=v.get("manipulation_index", 0),
                confidence=v.get("confidence", "LOW"),
                level=v.get("level", "CLEAN"),
                tactics_detected=v.get("tactics_detected", []),
                evidence=v.get("evidence", []),
                is_likely_ai_generated=v.get("is_likely_ai_generated", False),
                is_likely_coordinated=v.get("is_likely_coordinated", False),
                summary=v.get("summary", ""),
            )
            for v in result.get("verdicts", [])
        ]
        return ThreadVerdict(
            thread_id=query,
            platform="twitter",
            verdicts=verdicts,
            aggregate_score=result.get("aggregate_score", 0),
        )
    finally:
        await client.close()


@router.get("/reddit/thread", response_model=list[dict])
async def stream_reddit_thread(
    subreddit: str = Query(...),
    post_id: str = Query(...),
    limit: int = Query(default=50, le=100),
) -> list[dict]:
    client = RedditClient()
    try:
        comments = await client.get_thread_comments(subreddit, post_id, limit)
        return [
            {"id": c.id, "text": c.text, "author_name": c.author_name, "score": c.score}
            for c in comments
        ]
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Reddit API error: {e}")
    finally:
        await client.close()


@router.get("/youtube/video", response_model=list[dict])
async def stream_youtube_comments(
    video_id: str = Query(...),
    max_results: int = Query(default=50, le=100),
) -> list[dict]:
    client = YoutubeClient()
    try:
        comments = await client.get_video_comments(video_id, max_results)
        return [
            {"id": c.id, "text": c.text, "author_name": c.author_name, "likes": c.like_count}
            for c in comments
        ]
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"YouTube API error: {e}")
    finally:
        await client.close()
