from __future__ import annotations

from dataclasses import dataclass, field

import httpx

from src.config import settings


@dataclass
class TikTokComment:
    id: str
    text: str
    author_id: str
    author_name: str = ""
    create_time: int = 0
    like_count: int = 0
    reply_count: int = 0


class TikTokClient:
    BASE_URL = "https://open.tiktokapis.com/v2"

    def __init__(self):
        self._available = bool(settings.tiktok_access_token)
        self._client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Bearer {settings.tiktok_access_token}",
                "Content-Type": "application/json",
            },
            timeout=15.0,
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def get_video_comments(
        self,
        video_id: str,
        max_results: int = 50,
    ) -> list[TikTokComment]:
        if not self._available:
            return []

        try:
            response = await self._client.post(
                "/research/video/comment/list/",
                json={
                    "video_id": video_id,
                    "max_count": min(max_results, 100),
                },
            )
            if response.status_code != 200:
                return []

            data = response.json()
            comments: list[TikTokComment] = []
            for item in data.get("data", {}).get("comments", []):
                comments.append(TikTokComment(
                    id=item.get("comment_id", ""),
                    text=item.get("text", ""),
                    author_id=item.get("user_id", ""),
                    author_name=item.get("username", ""),
                    create_time=item.get("create_time", 0),
                    like_count=item.get("like_count", 0),
                    reply_count=item.get("reply_count", 0),
                ))
            return comments
        except Exception:
            return []

    async def search_comments(
        self,
        keyword: str,
        max_results: int = 20,
    ) -> list[TikTokComment]:
        if not self._available:
            return []
        try:
            response = await self._client.post(
                "/research/comment/search/",
                json={
                    "keyword": keyword,
                    "max_count": min(max_results, 50),
                },
            )
            if response.status_code != 200:
                return []
            data = response.json()
            comments: list[TikTokComment] = []
            for item in data.get("data", {}).get("comments", []):
                comments.append(TikTokComment(
                    id=item.get("comment_id", ""),
                    text=item.get("text", ""),
                    author_id=item.get("user_id", ""),
                    author_name=item.get("username", ""),
                    create_time=item.get("create_time", 0),
                    like_count=item.get("like_count", 0),
                    reply_count=item.get("reply_count", 0),
                ))
            return comments
        except Exception:
            return []
