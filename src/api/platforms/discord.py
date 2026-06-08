from __future__ import annotations

from dataclasses import dataclass, field

import httpx

from src.config import settings


@dataclass
class DiscordMessage:
    id: str
    text: str
    author_id: str
    author_name: str = ""
    channel_id: str = ""
    channel_name: str = ""
    guild_id: str = ""
    guild_name: str = ""
    timestamp: str = ""


@dataclass
class DiscordGuild:
    id: str
    name: str
    member_count: int = 0
    description: str = ""


class DiscordClient:
    BASE_URL = "https://discord.com/api/v10"

    def __init__(self):
        self._available = bool(settings.discord_bot_token)
        self._client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={"Authorization": f"Bot {settings.discord_bot_token}"},
            timeout=15.0,
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def get_channel_messages(
        self,
        channel_id: str,
        limit: int = 50,
    ) -> list[DiscordMessage]:
        if not self._available:
            return []
        try:
            response = await self._client.get(
                f"/channels/{channel_id}/messages",
                params={"limit": min(limit, 100)},
            )
            if response.status_code != 200:
                return []

            messages: list[DiscordMessage] = []
            for msg in response.json():
                author = msg.get("author", {})
                messages.append(DiscordMessage(
                    id=msg["id"],
                    text=msg.get("content", ""),
                    author_id=author.get("id", ""),
                    author_name=author.get("username", ""),
                    channel_id=msg.get("channel_id", ""),
                    timestamp=msg.get("timestamp", ""),
                ))
            return messages
        except Exception:
            return []

    async def search_guild_channels(
        self,
        guild_id: str,
        keyword: str = "",
    ) -> list[DiscordMessage]:
        if not self._available:
            return []
        try:
            response = await self._client.get(f"/guilds/{guild_id}/channels")
            if response.status_code != 200:
                return []

            channels = response.json()
            text_channels = [
                c for c in channels
                if c.get("type") == 0 and (not keyword or keyword.lower() in c.get("name", "").lower())
            ]

            all_messages: list[DiscordMessage] = []
            for channel in text_channels[:5]:
                msgs = await self.get_channel_messages(channel["id"], limit=20)
                for m in msgs:
                    m.channel_name = channel.get("name", "")
                    m.guild_id = guild_id
                all_messages.extend(msgs)

            return all_messages
        except Exception:
            return []

    async def get_guild(self, guild_id: str) -> DiscordGuild | None:
        if not self._available:
            return None
        try:
            response = await self._client.get(f"/guilds/{guild_id}")
            if response.status_code != 200:
                return None
            guild = response.json()
            return DiscordGuild(
                id=guild["id"],
                name=guild.get("name", ""),
                description=guild.get("description", ""),
            )
        except Exception:
            return None
