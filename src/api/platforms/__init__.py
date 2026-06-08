from __future__ import annotations

from src.api.platforms.twitter import TwitterClient
from src.api.platforms.reddit import RedditClient
from src.api.platforms.youtube import YoutubeClient
from src.api.platforms.telegram import TelegramClient
from src.api.platforms.discord import DiscordClient
from src.api.platforms.tiktok import TikTokClient

__all__ = [
    "TwitterClient",
    "RedditClient",
    "YoutubeClient",
    "TelegramClient",
    "DiscordClient",
    "TikTokClient",
]
