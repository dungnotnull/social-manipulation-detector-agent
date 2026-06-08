from __future__ import annotations

from dataclasses import dataclass, field

import httpx

from src.config import settings


@dataclass
class TelegramMessage:
    id: int
    text: str
    author_id: str = ""
    author_username: str = ""
    chat_id: int = 0
    chat_title: str = ""
    date: str = ""
    views: int = 0
    forwards: int = 0


@dataclass
class TelegramChat:
    id: int
    title: str = ""
    username: str = ""
    member_count: int = 0
    description: str = ""


class TelegramClient:
    BASE_URL = "https://api.telegram.org"

    def __init__(self):
        self._token = settings.telegram_api_id or ""
        self._available = bool(self._token and settings.telegram_api_hash)
        self._client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            timeout=15.0,
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def get_chat_messages(
        self,
        channel_username: str,
        limit: int = 50,
    ) -> list[TelegramMessage]:
        if not self._available:
            return []
        try:
            response = await self._client.post(
                f"/bot{self._token}/getUpdates",
                json={"limit": min(limit, 100)},
            )
            if response.status_code != 200:
                return []
            updates = response.json().get("result", [])
            messages: list[TelegramMessage] = []
            for update in updates:
                msg = update.get("message", update.get("channel_post", {}))
                if not msg:
                    continue
                chat = msg.get("chat", {})
                author = msg.get("from", {})
                messages.append(TelegramMessage(
                    id=msg.get("message_id", 0),
                    text=msg.get("text", msg.get("caption", "")),
                    author_id=str(author.get("id", "")),
                    author_username=author.get("username", ""),
                    chat_id=chat.get("id", 0),
                    chat_title=chat.get("title", ""),
                    date=str(msg.get("date", "")),
                    views=msg.get("views", 0),
                    forwards=msg.get("forward_count", 0),
                ))
            return messages
        except Exception:
            return []

    async def get_chat_info(self, channel_username: str) -> TelegramChat | None:
        if not self._available:
            return None
        try:
            response = await self._client.post(
                f"/bot{self._token}/getChat",
                json={"chat_id": f"@{channel_username}"},
            )
            if response.status_code != 200:
                return None
            chat = response.json().get("result", {})
            return TelegramChat(
                id=chat.get("id", 0),
                title=chat.get("title", ""),
                username=chat.get("username", ""),
                member_count=chat.get("members_count", 0),
                description=chat.get("description", ""),
            )
        except Exception:
            return None
