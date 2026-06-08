from __future__ import annotations

from dataclasses import dataclass, field

from src.patterns.tactic_taxonomy import TacticCategory, TACTICS


@dataclass
class ZeroShotResult:
    labels: dict[str, float] = field(default_factory=dict)
    top_label: str = ""
    top_score: float = 0.0


class ZeroShotClassifier:
    def __init__(self):
        self._pipeline = None
        self._loaded = False
        self._candidate_labels = [t.name for t in TACTICS.values()]

    def load(self) -> None:
        if self._loaded:
            return
        try:
            from transformers import pipeline
            self._pipeline = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
            )
            self._loaded = True
        except Exception as e:
            raise RuntimeError(f"Failed to load zero-shot model: {e}") from e

    def classify(self, text: str, labels: list[str] | None = None) -> ZeroShotResult:
        if not self._loaded:
            return ZeroShotResult()

        candidate_labels = labels or self._candidate_labels
        try:
            result = self._pipeline(
                text,
                candidate_labels,
                truncation=True,
                max_length=512,
                multi_label=True,
            )
            labels_dict = dict(zip(result["labels"], result["scores"]))
            return ZeroShotResult(
                labels={k: round(v, 4) for k, v in labels_dict.items()},
                top_label=result["labels"][0],
                top_score=round(result["scores"][0], 4),
            )
        except Exception:
            return ZeroShotResult()

    def classify_by_category(self, text: str) -> dict[TacticCategory, float]:
        result: dict[TacticCategory, float] = {}
        for cat in TacticCategory:
            cat_tactics = [t.name for t in TACTICS.values() if t.category == cat]
            if not cat_tactics:
                continue
            zs_result = self.classify(text, cat_tactics)
            result[cat] = max(zs_result.labels.values()) if zs_result.labels else 0.0
        return result
