from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path

from src.config import settings


@dataclass
class CalibrationSample:
    comment_text: str
    original_score: float
    ground_truth: float
    confidence: str
    feedback_type: str
    recorded_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class CalibrationResult:
    samples_count: int
    false_positive_rate: float
    false_negative_rate: float
    mean_error: float
    threshold_adjust: float
    recommended_threshold_high: float
    confidence: str


class CalibrationLoop:
    def __init__(self, storage_dir: Path | None = None):
        if storage_dir is None:
            storage_dir = Path(__file__).parent.parent.parent / "data" / "calibration"
        self._storage_dir = storage_dir
        self._storage_dir.mkdir(parents=True, exist_ok=True)
        self._samples: list[CalibrationSample] = []
        self._load_samples()

    def _load_samples(self) -> None:
        sample_file = self._storage_dir / "calibration_samples.json"
        if sample_file.exists():
            try:
                data = json.loads(sample_file.read_text(encoding="utf-8"))
                self._samples = [CalibrationSample(**s) for s in data]
            except (json.JSONDecodeError, TypeError):
                self._samples = []

    def _save_samples(self) -> None:
        sample_file = self._storage_dir / "calibration_samples.json"
        data = [
            {
                "comment_text": s.comment_text,
                "original_score": s.original_score,
                "ground_truth": s.ground_truth,
                "confidence": s.confidence,
                "feedback_type": s.feedback_type,
                "recorded_at": s.recorded_at,
            }
            for s in self._samples
        ]
        sample_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def record_feedback(
        self,
        comment_text: str,
        original_score: float,
        ground_truth: float,
        confidence: str = "MEDIUM",
        feedback_type: str = "user_report",
    ) -> None:
        sample = CalibrationSample(
            comment_text=comment_text,
            original_score=original_score,
            ground_truth=ground_truth,
            confidence=confidence,
            feedback_type=feedback_type,
        )
        self._samples.append(sample)
        if len(self._samples) > 10000:
            self._samples = self._samples[-10000:]
        self._save_samples()

    def compute_calibration(self) -> CalibrationResult:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=settings.calibration_window_days)).isoformat()
        recent = [s for s in self._samples if s.recorded_at >= cutoff]

        if len(recent) < settings.calibration_min_samples:
            return CalibrationResult(
                samples_count=len(recent),
                false_positive_rate=0.0,
                false_negative_rate=0.0,
                mean_error=0.0,
                threshold_adjust=0.0,
                recommended_threshold_high=settings.threshold_high,
                confidence="LOW",
            )

        false_positives = [
            s for s in recent
            if s.original_score >= settings.threshold_high and s.ground_truth < 0.3
        ]
        false_negatives = [
            s for s in recent
            if s.original_score < settings.threshold_moderate and s.ground_truth > 0.7
        ]

        fp_rate = len(false_positives) / len(recent)
        fn_rate = len(false_negatives) / len(recent)

        errors = [abs(s.original_score - s.ground_truth) for s in recent]
        mean_error = sum(errors) / len(errors)

        threshold_adjust = 0.0
        if fp_rate > 0.05:
            threshold_adjust += (fp_rate - 0.05) * 0.1
        if fn_rate > 0.05:
            threshold_adjust -= (fn_rate - 0.05) * 0.1

        recommended = min(0.95, max(0.60, settings.threshold_high + threshold_adjust))

        return CalibrationResult(
            samples_count=len(recent),
            false_positive_rate=round(fp_rate, 4),
            false_negative_rate=round(fn_rate, 4),
            mean_error=round(mean_error, 4),
            threshold_adjust=round(threshold_adjust, 4),
            recommended_threshold_high=round(recommended, 4),
            confidence="HIGH" if len(recent) >= 500 else "MEDIUM",
        )

    def update_thresholds(self) -> bool:
        result = self.compute_calibration()
        if result.confidence == "LOW":
            return False
        if abs(result.threshold_adjust) < settings.recalibration_threshold:
            return False
        settings.threshold_high = result.recommended_threshold_high
        return True

    def get_false_positive_rate(self) -> float:
        result = self.compute_calibration()
        return result.false_positive_rate


calibration_loop = CalibrationLoop()
