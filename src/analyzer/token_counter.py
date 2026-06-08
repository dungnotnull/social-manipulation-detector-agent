from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class TokenCount:
    tokens: int
    model: str
    truncation_needed: bool = False


class TokenCounter:
    _ENCODINGS: dict[str, Any] = {}

    def count(self, text: str, model: str = "gpt-4o-mini") -> TokenCount:
        encoding = self._get_encoding(model)
        if encoding is None:
            token_count = len(text.split()) * 2
            return TokenCount(tokens=token_count, model=model)

        tokens = len(encoding.encode(text))
        from src.config import settings
        truncation_needed = tokens > settings.llm_max_context_size
        return TokenCount(tokens=tokens, model=model, truncation_needed=truncation_needed)

    def count_batch(self, texts: list[str], model: str = "gpt-4o-mini") -> list[TokenCount]:
        return [self.count(t, model) for t in texts]

    def truncate(self, text: str, max_tokens: int, model: str = "gpt-4o-mini") -> str:
        encoding = self._get_encoding(model)
        if encoding is None:
            words = text.split()
            approximate = max_tokens // 2
            return " ".join(words[:approximate]) if len(words) > approximate else text

        tokens = encoding.encode(text)
        if len(tokens) <= max_tokens:
            return text
        return encoding.decode(tokens[:max_tokens])

    def _get_encoding(self, model: str) -> Any:
        if model in self._ENCODINGS:
            return self._ENCODINGS[model]
        try:
            import tiktoken
            if "claude" in model.lower():
                enc = tiktoken.get_encoding("cl100k_base")
            elif "gpt-4" in model.lower() or "gpt-3.5" in model.lower():
                enc = tiktoken.get_encoding("cl100k_base")
            else:
                enc = tiktoken.get_encoding("cl100k_base")
            self._ENCODINGS[model] = enc
            return enc
        except Exception:
            self._ENCODINGS[model] = None
            return None


token_counter = TokenCounter()
