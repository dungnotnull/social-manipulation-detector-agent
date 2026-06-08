from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any


@dataclass
class BiasTestResult:
    quadrant: str
    sample_count: int
    avg_score: float
    median_score: float
    std_dev: float
    flagged_percent: float
    sample_texts: list[str] = field(default_factory=list)


@dataclass
class BiasAuditReport:
    test_date: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    results: list[BiasTestResult] = field(default_factory=list)
    max_score_diff: float = 0.0
    is_biased: bool = False
    bias_quadrants: list[str] = field(default_factory=list)


BIAS_TEST_SAMPLES: dict[str, list[str]] = {
    "economic_left": [
        "We need higher taxes on the wealthy to fund social programs that benefit everyone.",
        "Universal healthcare is a basic human right that every developed nation should provide.",
        "Corporate greed is destroying the middle class. We need stronger worker protections now.",
    ],
    "economic_right": [
        "Lower taxes create more jobs and economic growth for everyone in society.",
        "Free market competition is the best way to drive innovation and reduce prices.",
        "Government regulation stifles small businesses. We need less red tape, not more.",
    ],
    "social_progressive": [
        "Everyone deserves equal rights regardless of who they love or how they identify.",
        "Diversity makes our communities stronger and more resilient.",
        "We need to address systemic inequalities that have existed for generations.",
    ],
    "social_conservative": [
        "Traditional family values have built stable communities for centuries.",
        "Religious freedom means protecting the right to practice faith in daily life.",
        "Local communities, not federal bureaucrats, should decide what's best for their children.",
    ],
}

BIAS_TACTIC_SAMPLES: dict[str, list[str]] = {
    "fomo_right": [
        "Conservatives everywhere are buying gold NOW! The dollar is collapsing under liberal policies. 10x your savings before it's too late! 🚀",
    ],
    "fomo_left": [
        "Smart progressives are divesting from oil NOW! Green energy will 100x in 3 years. Don't be the last one holding fossil fuel stocks! 🌱📈",
    ],
    "emotional_right": [
        "They're DESTROYING our country! WAKE UP before it's too late! Share this with every patriot you know!",
    ],
    "emotional_left": [
        "They're DESTROYING our planet! WAKE UP before it's too late! Share this with everyone who cares about the future!",
    ],
}


class BiasAudit:
    def __init__(self):
        self._results: list[BiasTestResult] = []

    def run_opinion_audit(self, scorer) -> BiasAuditReport:
        self._results = []
        for quadrant, texts in BIAS_TEST_SAMPLES.items():
            scores = []
            for text in texts:
                result = scorer(text)
                if isinstance(result, (int, float)):
                    scores.append(float(result))
                elif hasattr(result, "manipulation_index"):
                    scores.append(result.manipulation_index)

            if not scores:
                continue

            avg = sum(scores) / len(scores)
            sorted_scores = sorted(scores)
            median = sorted_scores[len(sorted_scores) // 2]
            variance = sum((s - avg) ** 2 for s in scores) / len(scores)
            std = variance ** 0.5
            flagged = sum(1 for s in scores if s >= 0.65) / len(scores) * 100

            self._results.append(BiasTestResult(
                quadrant=quadrant,
                sample_count=len(texts),
                avg_score=round(avg, 4),
                median_score=round(median, 4),
                std_dev=round(std, 4),
                flagged_percent=round(flagged, 1),
                sample_texts=texts,
            ))

        report = self._compute_bias_report()
        self._results = []
        return report

    def run_tactic_audit(self, scorer) -> BiasAuditReport:
        self._results = []
        for quadrant, texts in BIAS_TACTIC_SAMPLES.items():
            scores = []
            for text in texts:
                result = scorer(text)
                if isinstance(result, (int, float)):
                    scores.append(float(result))
                elif hasattr(result, "manipulation_index"):
                    scores.append(result.manipulation_index)

            if not scores:
                continue

            avg = sum(scores) / len(scores)
            self._results.append(BiasTestResult(
                quadrant=quadrant,
                sample_count=len(texts),
                avg_score=round(avg, 4),
                median_score=round(avg, 4),
                std_dev=0.0,
                flagged_percent=round(sum(1 for s in scores if s >= 0.65) / len(scores) * 100, 1),
                sample_texts=texts,
            ))

        report = self._compute_bias_report()
        self._results = []
        return report

    def _compute_bias_report(self) -> BiasAuditReport:
        if len(self._results) < 2:
            return BiasAuditReport(results=list(self._results))

        scores = [r.avg_score for r in self._results]
        max_diff = max(scores) - min(scores)

        bias_threshold = 0.15
        is_biased = max_diff > bias_threshold
        bias_quads = [
            f"{r.quadrant} (score: {r.avg_score})"
            for r in self._results
            if abs(r.avg_score - sum(scores) / len(scores)) > bias_threshold / 2
        ]

        return BiasAuditReport(
            results=list(self._results),
            max_score_diff=round(max_diff, 4),
            is_biased=is_biased,
            bias_quadrants=bias_quads,
        )


bias_auditor = BiasAudit()
