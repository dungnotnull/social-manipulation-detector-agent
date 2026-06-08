from __future__ import annotations

from dataclasses import dataclass, field

import httpx

from src.config import settings


@dataclass
class YoutubeComment:
    id: str
    text: str
    author_id: str
    author_name: str = ""
    published_at: str = ""
    like_count: int = 0
    reply_count: int = 0
    is_reply: bool = False


@dataclass
class YoutubeChannel:
    id: str
    title: str
    subscriber_count: int = 0
    video_count: int = 0
    created_at: str = ""


class YoutubeClient:
    BASE_URL = "https://www.googleapis.com/youtube/v3"

    def __init__(self):
        self._available = bool(settings.youtube_api_key)
        self._client = httpx.AsyncClient(timeout=15.0)

    async def close(self) -> None:
        await self._client.aclose()

    async def get_video_comments(
        self,
        video_id: str,
        max_results: int = 50,
    ) -> list[YoutubeComment]:
        if not self._available:
            return []

        try:
            response = await self._client.get(
                f"{self.BASE_URL}/commentThreads",
                params={
                    "part": "snippet,replies",
                    "videoId": video_id,
                    "maxResults": min(max_results, 100),
                    "order": "relevance",
                    "key": settings.youtube_api_key,
                },
            )
            if response.status_code != 200:
                return []

            data = response.json()
            comments: list[YoutubeComment] = []
            for item in data.get("items", []):
                top_comment = item["snippet"]["topLevelComment"]
                snippet = top_comment["snippet"]
                comments.append(YoutubeComment(
                    id=top_comment["id"],
                    text=snippet.get("textDisplay", ""),
                    author_id=snippet.get("authorChannelId", {}).get("value", ""),
                    author_name=snippet.get("authorDisplayName", ""),
                    published_at=snippet.get("publishedAt", ""),
                    like_count=snippet.get("likeCount", 0),
                    reply_count=item["snippet"].get("totalReplyCount", 0),
                ))

                if "replies" in item:
                    for reply in item["replies"].get("comments", []):
                        rs = reply["snippet"]
                        comments.append(YoutubeComment(
                            id=reply["id"],
                            text=rs.get("textDisplay", ""),
                            author_id=rs.get("authorChannelId", {}).get("value", ""),
                            author_name=rs.get("authorDisplayName", ""),
                            published_at=rs.get("publishedAt", ""),
                            like_count=rs.get("likeCount", 0),
                            is_reply=True,
                        ))

            return comments
        except Exception:
            return []

    async def get_channel(self, channel_id: str) -> YoutubeChannel | None:
        if not self._available:
            return None
        try:
            response = await self._client.get(
                f"{self.BASE_URL}/channels",
                params={
                    "part": "snippet,statistics",
                    "id": channel_id,
                    "key": settings.youtube_api_key,
                },
            )
            if response.status_code != 200:
                return None
            items = response.json().get("items", [])
            if not items:
                return None
            item = items[0]
            return YoutubeChannel(
                id=item["id"],
                title=item["snippet"]["title"],
                subscriber_count=int(item["statistics"].get("subscriberCount", 0)),
                video_count=int(item["statistics"].get("videoCount", 0)),
                created_at=item["snippet"].get("publishedAt", ""),
            )
        except Exception:
            return None
