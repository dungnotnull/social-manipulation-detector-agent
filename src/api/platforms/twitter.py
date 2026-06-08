from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

import httpx

from src.config import settings


@dataclass
class TwitterComment:
    id: str
    text: str
    author_id: str
    author_username: str = ""
    created_at: str = ""
    like_count: int = 0
    retweet_count: int = 0
    reply_count: int = 0


@dataclass
class TwitterAccount:
    id: str
    username: str
    name: str = ""
    created_at: str = ""
    followers_count: int = 0
    following_count: int = 0
    tweet_count: int = 0
    verified: bool = False
    profile_image_url: str = ""
    description: str = ""


class TwitterClient:
    BASE_URL = "https://api.twitter.com/2"

    def __init__(self):
        self._client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={"Authorization": f"Bearer {settings.twitter_bearer_token}"},
            timeout=15.0,
        )
        self._available = bool(settings.twitter_bearer_token)

    async def close(self) -> None:
        await self._client.aclose()

    async def search_comments(
        self,
        query: str,
        max_results: int = 20,
    ) -> list[TwitterComment]:
        if not self._available:
            return []

        try:
            response = await self._client.get(
                "/tweets/search/recent",
                params={
                    "query": query,
                    "max_results": min(max_results, 100),
                    "tweet.fields": "author_id,created_at,public_metrics",
                    "expansions": "author_id",
                    "user.fields": "username",
                },
            )
            if response.status_code != 200:
                return []

            data = response.json()
            users = {
                u["id"]: u.get("username", "")
                for u in data.get("includes", {}).get("users", [])
            }

            comments: list[TwitterComment] = []
            for tweet in data.get("data", []):
                metrics = tweet.get("public_metrics", {})
                comments.append(TwitterComment(
                    id=tweet["id"],
                    text=tweet["text"],
                    author_id=tweet.get("author_id", ""),
                    author_username=users.get(tweet.get("author_id", ""), ""),
                    created_at=tweet.get("created_at", ""),
                    like_count=metrics.get("like_count", 0),
                    retweet_count=metrics.get("retweet_count", 0),
                    reply_count=metrics.get("reply_count", 0),
                ))

            return comments
        except Exception:
            return []

    async def get_thread(self, conversation_id: str, max_results: int = 50) -> list[TwitterComment]:
        if not self._available:
            return []
        try:
            response = await self._client.get(
                "/tweets/search/recent",
                params={
                    "query": f"conversation_id:{conversation_id}",
                    "max_results": min(max_results, 100),
                    "tweet.fields": "author_id,created_at,public_metrics",
                },
            )
            if response.status_code != 200:
                return []

            data = response.json()
            return [
                TwitterComment(
                    id=t["id"],
                    text=t["text"],
                    author_id=t.get("author_id", ""),
                    created_at=t.get("created_at", ""),
                    like_count=t.get("public_metrics", {}).get("like_count", 0),
                )
                for t in data.get("data", [])
            ]
        except Exception:
            return []

    async def get_account(self, user_id: str) -> TwitterAccount | None:
        if not self._available:
            return None
        try:
            response = await self._client.get(
                f"/users/{user_id}",
                params={
                    "user.fields": "created_at,public_metrics,verified,profile_image_url,description",
                },
            )
            if response.status_code != 200:
                return None
            user = response.json().get("data", {})
            metrics = user.get("public_metrics", {})
            return TwitterAccount(
                id=user["id"],
                username=user.get("username", ""),
                name=user.get("name", ""),
                created_at=user.get("created_at", ""),
                followers_count=metrics.get("followers_count", 0),
                following_count=metrics.get("following_count", 0),
                tweet_count=metrics.get("tweet_count", 0),
                verified=user.get("verified", False),
                profile_image_url=user.get("profile_image_url", ""),
                description=user.get("description", ""),
            )
        except Exception:
            return None

    async def get_account_by_username(self, username: str) -> TwitterAccount | None:
        if not self._available:
            return None
        try:
            response = await self._client.get(
                f"/users/by/username/{username.lstrip('@')}",
                params={
                    "user.fields": "created_at,public_metrics,verified,profile_image_url,description",
                },
            )
            if response.status_code != 200:
                return None
            user = response.json().get("data", {})
            metrics = user.get("public_metrics", {})
            return TwitterAccount(
                id=user["id"],
                username=user.get("username", ""),
                name=user.get("name", ""),
                created_at=user.get("created_at", ""),
                followers_count=metrics.get("followers_count", 0),
                following_count=metrics.get("following_count", 0),
                tweet_count=metrics.get("tweet_count", 0),
                verified=user.get("verified", False),
                profile_image_url=user.get("profile_image_url", ""),
                description=user.get("description", ""),
            )
        except Exception:
            return None
