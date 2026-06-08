from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class ProcessedText:
    original_text: str
    normalized_text: str
    language: str
    emoji_clusters: list[str] = field(default_factory=list)
    urls: list[str] = field(default_factory=list)
    hashtags: list[str] = field(default_factory=list)
    token_count: int = 0
    char_count: int = 0


class TextPreprocessor:
    _EMOJI_PATTERN = re.compile(
        "[\U0001F300-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF"
        "\U00002702-\U000027B0\U000024C2-\U0001F251"
        "\U0001F600-\U0001F64F\U0001F680-\U0001F6FF"
        "\U00002600-\U000026FF\u2600-\u26FF\u2700-\u27BF]+"
    )
    _URL_PATTERN = re.compile(r"https?://\S+")
    _HASHTAG_PATTERN = re.compile(r"#\w+")

    def __init__(self):
        try:
            from langdetect import DetectorFactory
            DetectorFactory.seed = 0
            self._lang_detect_available = True
        except Exception:
            self._lang_detect_available = False

    def preprocess(self, text: str) -> ProcessedText:
        emoji_clusters = self._extract_emoji_clusters(text)
        urls = self._extract_urls(text)
        hashtags = self._extract_hashtags(text)

        normalized = text
        for cluster in emoji_clusters:
            normalized = normalized.replace(cluster, "[HYPE_EMOJI_CLUSTER]" if len(cluster) >= 3 else "[EMOJI]")
        for url in urls:
            normalized = normalized.replace(url, "[URL]")

        language = self._detect_language(normalized)

        tokens = normalized.split()
        token_count = len(tokens)

        return ProcessedText(
            original_text=text,
            normalized_text=normalized,
            language=language,
            emoji_clusters=emoji_clusters,
            urls=urls,
            hashtags=hashtags,
            token_count=token_count,
            char_count=len(text),
        )

    def _extract_emoji_clusters(self, text: str) -> list[str]:
        return self._EMOJI_PATTERN.findall(text)

    def _extract_urls(self, text: str) -> list[str]:
        return self._URL_PATTERN.findall(text)

    def _extract_hashtags(self, text: str) -> list[str]:
        return self._HASHTAG_PATTERN.findall(text)

    def _detect_language(self, text: str) -> str:
        if not self._lang_detect_available:
            return "en"
        try:
            from langdetect import detect
            return detect(text)
        except Exception:
            return "en"
