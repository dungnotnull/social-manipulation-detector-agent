from __future__ import annotations

from dataclasses import dataclass, field

import httpx

from src.config import settings


@dataclass
class RedditComment:
    id: str
    text: str
    author_id: str
    author_name: str = ""
    subreddit: str = ""
    created_utc: float = 0.0
    score: int = 0
    permalink: str = ""


@dataclass
class RedditAccount:
    id: str
    name: str
    created_utc: float = 0.0
    link_karma: int = 0
    comment_karma: int = 0
    is_gold: bool = False
    is_mod: bool = False
    has_verified_email: bool = False


class RedditClient:
    BASE_URL = "https://oauth.reddit.com"
    AUTH_URL = "https://www.reddit.com/api/v1/access_token"

    def __init__(self):
        self._available = bool(settings.reddit_client_id and settings.reddit_client_secret)
        self._access_token: str | None = None
        self._client = httpx.AsyncClient(
            headers={"User-Agent": settings.reddit_user_agent},
            timeout=15.0,
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def _authenticate(self) -> None:
        if not self._available or self._access_token:
            return
        try:
            auth = httpx.BasicAuth(settings.reddit_client_id, settings.reddit_client_secret)
            response = await httpx.AsyncClient().post(
                self.AUTH_URL,
                data={"grant_type": "client_credentials"},
                auth=auth,
                headers={"User-Agent": settings.reddit_user_agent},
                timeout=10.0,
            )
            if response.status_code == 200:
                self._access_token = response.json()["access_token"]
                self._client.headers["Authorization"] = f"bearer {self._access_token}"
        except Exception:
            pass

    async def get_thread_comments(
        self,
        subreddit: str,
        post_id: str,
        limit: int = 50,
    ) -> list[RedditComment]:
        await self._authenticate()
        if not self._access_token:
            return []

        try:
            response = await self._client.get(
                f"{self.BASE_URL}/r/{subreddit}/comments/{post_id}",
                params={"limit": min(limit, 100), "depth": 10, "sort": "top"},
            )
            if response.status_code != 200:
                return []

            data = response.json()
            comments: list[RedditComment] = []

            def _extract(listing):
                for item in listing:
                    if item["kind"] == "t1":
                        cdata = item["data"]
                        comments.append(RedditComment(
                            id=cdata["id"],
                            text=cdata.get("body", ""),
                            author_id=f"t2_{cdata.get('author', '')}",
                            author_name=cdata.get("author", "[deleted]"),
                            subreddit=cdata.get("subreddit", subreddit),
                            created_utc=cdata.get("created_utc", 0),
                            score=cdata.get("score", 0),
                            permalink=cdata.get("permalink", ""),
                        ))
                        if "replies" in cdata and isinstance(cdata["replies"], dict):
                            _extract(cdata["replies"]["data"]["children"])

            for listing in data:
                if listing["kind"] == "Listing":
                    _extract(listing["data"]["children"])

            return comments
        except Exception:
            return []

    async def get_user(self, username: str) -> RedditAccount | None:
        await self._authenticate()
        if not self._access_token:
            return None
        try:
            response = await self._client.get(
                f"{self.BASE_URL}/user/{username}/about",
            )
            if response.status_code != 200:
                return None
            data = response.json().get("data", {})
            return RedditAccount(
                id=data.get("id", ""),
                name=data.get("name", username),
                created_utc=data.get("created_utc", 0),
                link_karma=data.get("link_karma", 0),
                comment_karma=data.get("comment_karma", 0),
                is_gold=data.get("is_gold", False),
                is_mod=data.get("is_mod", False),
                has_verified_email=data.get("has_verified_email", False),
            )
        except Exception:
            return None
