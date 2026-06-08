from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SentimentResult:
    general_sentiment: str = "neutral"
    general_score: float = 0.0
    financial_sentiment: str = "neutral"
    financial_score: float = 0.0
    fomo_score: float = 0.0
    fud_score: float = 0.0
    is_fomo: bool = False
    is_fud: bool = False
    is_unnatural_uniform: bool = False


class SentimentAnalyzer:
    def __init__(self):
        self._sentiment_pipeline = None
        self._finbert_pipeline = None
        self._loaded = False

    def load(self) -> None:
        if self._loaded:
            return
        try:
            from transformers import pipeline
            self._sentiment_pipeline = pipeline(
                "text-classification",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
            )
            self._finbert_pipeline = pipeline(
                "text-classification",
                model="ProsusAI/finbert",
            )
            self._loaded = True
        except Exception as e:
            raise RuntimeError(f"Failed to load sentiment models: {e}") from e

    def analyze(self, text: str) -> SentimentResult:
        if not self._loaded:
            return SentimentResult()

        general = self._run_sentiment(text)
        fin_data = self._run_finbert(text)

        fomo_score = 0.0
        fud_score = 0.0
        is_fomo = False
        is_fud = False

        text_lower = text.lower()

        urgency_keywords = [
            "don't miss", "last chance", "act now", "before it's too late",
            "only today", "limited time", "about to explode",
        ]
        fomo_urgency = any(kw in text_lower for kw in urgency_keywords)

        fud_keywords = [
            "sell now", "protect your capital", "get out", "crash",
            "exit scam", "rug pull", "insider selling",
        ]
        fud_urgency = any(kw in text_lower for kw in fud_keywords)

        fin_sentiment = fin_data.get("label", "neutral")
        fin_score = fin_data.get("score", 0.0)

        if fin_sentiment == "positive" and fin_score > 0.8:
            fomo_score = fin_score
            if fomo_urgency:
                fomo_score = min(1.0, fomo_score * 1.2)
                is_fomo = True

        if fin_sentiment == "negative" and fin_score > 0.8:
            fud_score = fin_score
            if fud_urgency:
                fud_score = min(1.0, fud_score * 1.2)
                is_fud = True

        return SentimentResult(
            general_sentiment=general.get("label", "neutral"),
            general_score=general.get("score", 0.0),
            financial_sentiment=fin_sentiment,
            financial_score=fin_score,
            fomo_score=round(fomo_score, 4),
            fud_score=round(fud_score, 4),
            is_fomo=is_fomo,
            is_fud=is_fud,
            is_unnatural_uniform=False,
        )

    def _run_sentiment(self, text: str) -> dict[str, str | float]:
        try:
            result = self._sentiment_pipeline(text, truncation=True, max_length=512)
            if result and isinstance(result, list):
                item = result[0]
                return {"label": item.get("label", "neutral"), "score": item.get("score", 0.5)}
        except Exception:
            pass
        return {"label": "neutral", "score": 0.5}

    def _run_finbert(self, text: str) -> dict[str, str | float]:
        try:
            result = self._finbert_pipeline(text, truncation=True, max_length=512)
            if result and isinstance(result, list):
                item = result[0]
                return {
                    "label": item.get("label", "neutral").lower(),
                    "score": item.get("score", 0.5),
                }
        except Exception:
            pass
        return {"label": "neutral", "score": 0.5}
