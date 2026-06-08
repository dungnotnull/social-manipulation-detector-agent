from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class CrossPlatformMatch:
    text: str
    text_hash: str
    platforms: list[str] = field(default_factory=list)
    account_ids: list[str] = field(default_factory=list)
    first_seen: str = ""
    match_count: int = 0


class CrossPlatformLinker:
    def __init__(self):
        self._seen_texts: dict[str, CrossPlatformMatch] = {}

    def register_comment(
        self,
        text: str,
        platform: str,
        account_id: str,
    ) -> CrossPlatformMatch | None:
        text_hash = hashlib.sha256(text.strip().lower().encode()).hexdigest()

        if text_hash in self._seen_texts:
            match = self._seen_texts[text_hash]
            if platform not in match.platforms:
                match.platforms.append(platform)
            if account_id not in match.account_ids:
                match.account_ids.append(account_id)
            match.match_count += 1
            return match

        match = CrossPlatformMatch(
            text=text,
            text_hash=text_hash,
            platforms=[platform],
            account_ids=[account_id],
            first_seen=datetime.now(timezone.utc).isoformat(),
            match_count=1,
        )
        self._seen_texts[text_hash] = match
        return None

    def find_cross_platform_matches(self) -> list[CrossPlatformMatch]:
        return [
            m for m in self._seen_texts.values()
            if len(m.platforms) > 1
        ]

    def clear_old(self, max_age_hours: int = 72) -> None:
        cutoff = datetime.now(timezone.utc).timestamp() - (max_age_hours * 3600)
        to_remove = []
        for text_hash, match in self._seen_texts.items():
            try:
                seen_time = datetime.fromisoformat(match.first_seen).timestamp()
                if seen_time < cutoff:
                    to_remove.append(text_hash)
            except (ValueError, TypeError):
                to_remove.append(text_hash)
        for h in to_remove:
            del self._seen_texts[h]
