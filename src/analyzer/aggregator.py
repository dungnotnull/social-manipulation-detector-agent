from __future__ import annotations

from dataclasses import dataclass, field

from src.config import settings


@dataclass
class AggregationInput:
    llm_tactic_score: float = 0.0
    ai_generated_probability: float = 0.0
    behavioral_score: float = 0.0
    temporal_coordination: float = 0.0
    graph_cluster_score: float = 0.0
    token_count: int = 0
    llm_evidence: list[dict[str, str]] = field(default_factory=list)
    llm_summary: str = ""


@dataclass
class ManipulationVerdict:
    manipulation_index: float = 0.0
    confidence: str = "LOW"
    level: str = "CLEAN"
    tactics_detected: list[str] = field(default_factory=list)
    evidence: list[dict[str, str]] = field(default_factory=list)
    is_likely_ai_generated: bool = False
    is_likely_coordinated: bool = False
    summary: str = ""


class ManipulationAggregator:
    WEIGHTS = {
        "llm_tactic_score": 0.40,
        "ai_generated_probability": 0.20,
        "behavioral_score": 0.20,
        "temporal_coordination": 0.10,
        "graph_cluster_score": 0.10,
    }

    def compute(self, signals: AggregationInput) -> ManipulationVerdict:
        raw_score = (
            signals.llm_tactic_score * self.WEIGHTS["llm_tactic_score"]
            + signals.ai_generated_probability * self.WEIGHTS["ai_generated_probability"]
            + signals.behavioral_score * self.WEIGHTS["behavioral_score"]
            + signals.temporal_coordination * self.WEIGHTS["temporal_coordination"]
            + signals.graph_cluster_score * self.WEIGHTS["graph_cluster_score"]
        )

        confidence = self._compute_confidence(signals.token_count)
        level = self._classify_level(raw_score)

        return ManipulationVerdict(
            manipulation_index=round(raw_score, 4),
            confidence=confidence,
            level=level,
            evidence=signals.llm_evidence,
            summary=signals.llm_summary,
        )

    @staticmethod
    def _compute_confidence(token_count: int) -> str:
        if token_count > 80:
            return "HIGH"
        if token_count > 30:
            return "MEDIUM"
        return "LOW"

    @staticmethod
    def _classify_level(raw_score: float) -> str:
        if raw_score >= settings.threshold_high:
            return "HIGH"
        if raw_score >= settings.threshold_elevated:
            return "ELEVATED"
        if raw_score >= settings.threshold_moderate:
            return "MODERATE"
        if raw_score >= settings.threshold_low:
            return "LOW"
        return "CLEAN"
