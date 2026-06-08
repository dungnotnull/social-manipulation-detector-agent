from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone

from src.config import settings


@dataclass
class AccountFeatures:
    account_id: str
    platform: str
    account_age_days: int = 0
    followers_count: int = 0
    following_count: int = 0
    posts_count: int = 0
    posts_per_day_avg: float = 0.0
    follower_following_ratio: float = 0.0
    profile_completeness: float = 0.0
    verified_status: bool = False
    has_bio: bool = False
    has_profile_image: bool = False
    retweet_ratio: float = 0.0
    content_diversity_ratio: float = 0.0
    bot_score: float = 0.0
    risk_signals: list[str] = field(default_factory=list)


class AccountFeatureExtractor:
    def extract_from_twitter_account(self, account) -> AccountFeatures:
        age_days = 365
        if account.created_at:
            try:
                created = datetime.fromisoformat(account.created_at.replace("Z", "+00:00"))
                age_days = max(1, (datetime.now(timezone.utc) - created).days)
            except (ValueError, TypeError):
                pass

        features = AccountFeatures(
            account_id=account.id,
            platform="twitter",
            account_age_days=age_days,
            followers_count=account.followers_count,
            following_count=account.following_count,
            posts_count=account.tweet_count,
            verified_status=account.verified,
            has_bio=bool(account.description),
            has_profile_image=bool(account.profile_image_url),
        )

        features.posts_per_day_avg = (
            features.posts_count / age_days if age_days > 0 else features.posts_count
        )
        features.follower_following_ratio = (
            features.followers_count / features.following_count
            if features.following_count > 0
            else float("inf")
        )
        features.profile_completeness = (
            (1.0 if features.has_bio else 0.0)
            + (1.0 if features.has_profile_image else 0.0)
        ) / 2.0

        features.bot_score = self._compute_bot_score(features)
        features.risk_signals = self._compute_risk_signals(features)
        return features

    def extract_from_reddit_account(self, account) -> AccountFeatures:
        age_days = 365
        if account.created_utc:
            created = datetime.fromtimestamp(account.created_utc, tz=timezone.utc)
            age_days = max(1, (datetime.now(timezone.utc) - created).days)

        features = AccountFeatures(
            account_id=account.id,
            platform="reddit",
            account_age_days=age_days,
            followers_count=account.link_karma,
            following_count=0,
            posts_count=account.link_karma + account.comment_karma,
            has_profile_image=account.has_verified_email,
            verified_status=account.has_verified_email,
        )
        features.posts_per_day_avg = features.posts_count / age_days if age_days > 0 else 0
        features.bot_score = self._compute_bot_score(features)
        features.risk_signals = self._compute_risk_signals(features)
        return features

    def extract_from_youtube_channel(self, channel, account_id: str = "") -> AccountFeatures:
        age_days = 365
        if channel.created_at:
            try:
                created = datetime.fromisoformat(channel.created_at.replace("Z", "+00:00"))
                age_days = max(1, (datetime.now(timezone.utc) - created).days)
            except (ValueError, TypeError):
                pass

        features = AccountFeatures(
            account_id=account_id or channel.id,
            platform="youtube",
            account_age_days=age_days,
            followers_count=channel.subscriber_count,
            posts_count=channel.video_count,
        )
        features.posts_per_day_avg = features.posts_count / age_days if age_days > 0 else 0
        features.follower_following_ratio = features.followers_count
        features.bot_score = self._compute_bot_score(features)
        features.risk_signals = self._compute_risk_signals(features)
        return features

    def _compute_bot_score(self, f: AccountFeatures) -> float:
        score = 0.0
        weights = 0.0

        if f.account_age_days > 0:
            weights += 0.21
            if f.account_age_days < settings.account_age_days_suspicious:
                score += 1.0 * 0.21
            elif f.account_age_days < 180:
                score += 0.5 * 0.21

        if not math.isinf(f.follower_following_ratio):
            weights += 0.18
            if f.follower_following_ratio < settings.follower_following_ratio_suspicious_low:
                score += 1.0 * 0.18
            elif f.follower_following_ratio > settings.follower_following_ratio_suspicious_high:
                score += 0.8 * 0.18

        if f.posts_per_day_avg > 0:
            weights += 0.16
            if f.posts_per_day_avg > settings.posts_per_day_suspicious:
                score += 1.0 * 0.16
            elif f.posts_per_day_avg > 50:
                score += 0.6 * 0.16

        weights += 0.14
        score += (1.0 - f.profile_completeness) * 0.14

        return round(score / weights, 4) if weights > 0 else 0.0

    def _compute_risk_signals(self, f: AccountFeatures) -> list[str]:
        signals: list[str] = []
        if f.account_age_days < settings.account_age_days_suspicious:
            signals.append(f"NEW_ACCOUNT_{f.account_age_days}d")
        if f.posts_per_day_avg > settings.posts_per_day_suspicious:
            signals.append(f"HIGH_POSTING_RATE_{f.posts_per_day_avg:.0f}/day")
        if not math.isinf(f.follower_following_ratio):
            if f.follower_following_ratio < settings.follower_following_ratio_suspicious_low:
                signals.append("LOW_FOLLOWER_RATIO")
            elif f.follower_following_ratio > settings.follower_following_ratio_suspicious_high:
                signals.append("HIGH_FOLLOWER_RATIO")
        if f.profile_completeness < 0.5:
            signals.append("LOW_PROFILE_COMPLETENESS")
        if f.retweet_ratio > 0.8:
            signals.append("HIGH_RETWEET_RATIO")
        if f.content_diversity_ratio < 0.1:
            signals.append("LOW_CONTENT_DIVERSITY")
        return signals
