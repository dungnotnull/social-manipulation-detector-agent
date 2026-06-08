from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class FinBERTResult:
    fomo_score: float = 0.0
    fud_score: float = 0.0
    is_fomo: bool = False
    is_fud: bool = False
    is_shill: bool = False
    financial_manipulation_score: float = 0.0
    signals: list[str] = field(default_factory=list)


class FinBERTSubsystem:
    def __init__(self):
        self._finbert_pipeline = None
        self._finbert_tone_pipeline = None
        self._loaded = False

    def load(self) -> None:
        if self._loaded:
            return
        try:
            from transformers import pipeline
            self._finbert_pipeline = pipeline(
                "text-classification",
                model="ProsusAI/finbert",
            )
            self._finbert_tone_pipeline = pipeline(
                "text-classification",
                model="yiyanghkust/finbert-tone",
            )
            self._loaded = True
        except Exception as e:
            raise RuntimeError(f"Failed to load FinBERT models: {e}") from e

    def analyze(self, text: str) -> FinBERTResult:
        if not self._loaded:
            return FinBERTResult()

        fin_sentiment = self._run_finbert(text)
        fin_tone = self._run_finbert_tone(text)

        text_lower = text.lower()

        fomo_signals: list[str] = []
        fud_signals: list[str] = []
        shill_signals: list[str] = []

        fomo_keywords = [
            "don't miss", "last chance", "act now", "before it's too late",
            "only today", "limited time", "about to explode", "to the moon",
            "100x", "10x", "next bitcoin", "lambo soon", "whales are",
        ]
        for kw in fomo_keywords:
            if kw in text_lower:
                fomo_signals.append(f"keyword_{kw}")

        fud_keywords = [
            "sell now", "protect your capital", "get out", "crash",
            "exit scam", "rug pull", "insider selling", "scam alert",
        ]
        for kw in fud_keywords:
            if kw in text_lower:
                fud_signals.append(f"keyword_{kw}")

        shill_keywords = ["dm me", "join my group", "use my code", "referral", "sign up with my"]
        for kw in shill_keywords:
            if kw in text_lower:
                shill_signals.append(f"keyword_{kw}")

        has_price_target = any(c.isdigit() for c in text) and any(
            kw in text_lower for kw in ["$", "usd", "x", "target", "price"]
        )
        has_timeframe = any(
            kw in text_lower for kw in ["tomorrow", "next week", "today", "this month", "eoy", "soon"]
        )

        fomo_score = 0.0
        if fin_sentiment == "positive":
            fomo_score = 0.5
            if fomo_signals:
                fomo_score += 0.15 * len(fomo_signals)
            if has_price_target and has_timeframe:
                fomo_score += 0.2

        fud_score = 0.0
        if fin_sentiment == "negative":
            fud_score = 0.5
            if fud_signals:
                fud_score += 0.15 * len(fud_signals)

        shill_score = 0.0
        if shill_signals:
            shill_score = 0.4 + 0.15 * len(shill_signals)

        is_fomo = fomo_score > 0.7
        is_fud = fud_score > 0.7
        is_shill = shill_score > 0.7

        financial_score = max(fomo_score, fud_score, shill_score)
        all_signals = fomo_signals + fud_signals + shill_signals

        return FinBERTResult(
            fomo_score=round(min(1.0, fomo_score), 4),
            fud_score=round(min(1.0, fud_score), 4),
            is_fomo=is_fomo,
            is_fud=is_fud,
            is_shill=is_shill,
            financial_manipulation_score=round(min(1.0, financial_score), 4),
            signals=all_signals,
        )

    def _run_finbert(self, text: str) -> str:
        if not self._finbert_pipeline:
            return "neutral"
        try:
            result = self._finbert_pipeline(text, truncation=True, max_length=512)
            if result and isinstance(result, list):
                return result[0].get("label", "neutral").lower()
        except Exception:
            pass
        return "neutral"

    def _run_finbert_tone(self, text: str) -> str:
        if not self._finbert_tone_pipeline:
            return "Neutral"
        try:
            result = self._finbert_tone_pipeline(text, truncation=True, max_length=512)
            if result and isinstance(result, list):
                return result[0].get("label", "Neutral")
        except Exception:
            pass
        return "Neutral"
