from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ToxicityResult:
    toxicity_score: float = 0.0
    severe_toxicity_score: float = 0.0
    identity_attack_score: float = 0.0
    insult_score: float = 0.0
    threat_score: float = 0.0
    is_toxic: bool = False


class ToxicityDetector:
    def __init__(self):
        self._pipeline = None
        self._loaded = False

    def load(self) -> None:
        if self._loaded:
            return
        try:
            from transformers import pipeline
            self._pipeline = pipeline(
                "text-classification",
                model="martin-ha/toxic-comment-model",
            )
            self._loaded = True
        except Exception as e:
            raise RuntimeError(f"Failed to load toxicity model: {e}") from e

    def detect(self, text: str) -> ToxicityResult:
        if not self._loaded:
            return ToxicityResult()

        try:
            result = self._pipeline(text, truncation=True, max_length=512)
            if result and isinstance(result, list):
                item = result[0]
                label = item.get("label", "").lower()
                score = item.get("score", 0.0)
                if "toxic" in label:
                    return ToxicityResult(toxicity_score=round(score, 4), is_toxic=score > 0.5)
        except Exception:
            pass
        return ToxicityResult()
