from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

import math

from src.analyzer.account_features import AccountFeatures
from src.config import settings


@dataclass
class BehaviorScore:
    account_risk: float = 0.0
    temporal_coordination_score: float = 0.0
    cross_thread_repetition: float = 0.0
    burst_detected: bool = False
    cross_platform_match: bool = False
    account_features_detail: dict = field(default_factory=dict)


@dataclass
class CoordinationResult:
    is_coordinated: bool = False
    coordination_probability: float = 0.0
    cluster_size: int = 0
    time_variance_seconds: float = 0.0
    content_similarity: float = 0.0


@dataclass
class CommentMeta:
    text: str
    author_id: str
    timestamp: str = ""
    platform: str = ""


class BehaviorAnalyzer:
    SAFE_THRESHOLDS = {
        "account_age_days": 180,
        "posts_per_day_max": 20,
        "follower_following_ratio_min": 0.1,
        "follower_following_ratio_max": 10,
        "retweet_ratio_max": 0.5,
        "content_diversity_min": 0.3,
    }

    def analyze_account(self, account_id: str, platform: str) -> BehaviorScore:
        return BehaviorScore()

    def analyze_account_features(self, features: AccountFeatures) -> BehaviorScore:
        score = BehaviorScore(account_risk=features.bot_score)
        if features.risk_signals:
            score.account_risk = min(1.0, score.account_risk + len(features.risk_signals) * 0.05)
        score.account_features_detail = {
            "account_age_days": features.account_age_days,
            "posts_per_day": round(features.posts_per_day_avg, 2),
            "follower_ratio": round(features.follower_following_ratio, 4) if not math.isinf(features.follower_following_ratio) else 999.0,
            "profile_completeness": round(features.profile_completeness, 2),
            "risk_signals": features.risk_signals,
            "platform": features.platform,
        }
        return score

    def detect_temporal_coordination(self, comments: list[CommentMeta]) -> CoordinationResult:
        if len(comments) < settings.coordination_min_accounts:
            return CoordinationResult()

        timestamps: list[datetime] = []
        for c in comments:
            try:
                ts = datetime.fromisoformat(c.timestamp.replace("Z", "+00:00"))
                timestamps.append(ts)
            except (ValueError, AttributeError):
                return CoordinationResult()

        if len(timestamps) < 3:
            return CoordinationResult()

        timestamps.sort()
        variances: list[float] = []
        for i in range(len(timestamps) - 2):
            window = timestamps[i : i + 3]
            span = (window[-1] - window[0]).total_seconds()
            variances.append(span)

        min_variance = min(variances) if variances else float("inf")
        similarity = self._compute_content_similarity(comments)

        if min_variance < settings.coordination_time_variance_seconds:
            prob = min(1.0, (settings.coordination_time_variance_seconds - min_variance) / settings.coordination_time_variance_seconds * 1.2)
            if similarity > 0.7:
                prob = min(1.0, prob * 1.3)
            return CoordinationResult(
                is_coordinated=True,
                coordination_probability=round(prob, 4),
                cluster_size=len(comments),
                time_variance_seconds=round(min_variance, 2),
                content_similarity=round(similarity, 4),
            )

        return CoordinationResult(
            time_variance_seconds=round(min_variance, 2),
            content_similarity=round(similarity, 4),
        )

    def detect_burst(self, comments: list[CommentMeta], window_seconds: int = 60) -> bool:
        if len(comments) < 3:
            return False
        try:
            timestamps = []
            for c in comments:
                ts = datetime.fromisoformat(c.timestamp.replace("Z", "+00:00"))
                timestamps.append(ts.timestamp())
            timestamps.sort()
            for i in range(len(timestamps) - 2):
                if timestamps[i + 2] - timestamps[i] < window_seconds:
                    return True
        except (ValueError, TypeError):
            pass
        return False

    def detect_cross_thread_repetition(
        self,
        texts: list[str],
        threshold: float | None = None,
    ) -> float:
        if threshold is None:
            threshold = settings.cross_thread_similarity_threshold
        if len(texts) < 2:
            return 0.0

        similar_pairs = 0
        total_pairs = 0
        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                total_pairs += 1
                sim = self._text_similarity(texts[i], texts[j])
                if sim > threshold:
                    similar_pairs += 1

        return round(similar_pairs / total_pairs, 4) if total_pairs > 0 else 0.0

    @staticmethod
    def _compute_content_similarity(comments: list[CommentMeta]) -> float:
        if len(comments) < 2:
            return 0.0
        texts = [c.text.lower().strip() for c in comments if c.text]
        if len(texts) < 2:
            return 0.0
        similarities = []
        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                sim = BehaviorAnalyzer._text_similarity(texts[i], texts[j])
                similarities.append(sim)
        return sum(similarities) / len(similarities) if similarities else 0.0

    @staticmethod
    def _text_similarity(a: str, b: str) -> float:
        a_words = set(a.split())
        b_words = set(b.split())
        if not a_words or not b_words:
            return 0.0
        intersection = a_words & b_words
        union = a_words | b_words
        return len(intersection) / len(union)
