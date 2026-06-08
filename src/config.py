from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM APIs
    anthropic_api_key: str = ""
    openai_api_key: str = ""

    # Social Platform APIs
    twitter_bearer_token: str = ""
    twitter_api_key: str = ""
    twitter_api_secret: str = ""
    twitter_access_token: str = ""
    twitter_access_secret: str = ""
    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    reddit_user_agent: str = "SMDA/0.1.0"
    youtube_api_key: str = ""
    telegram_api_id: str = ""
    telegram_api_hash: str = ""
    discord_bot_token: str = ""
    tiktok_access_token: str = ""

    # Infrastructure
    redis_url: str = "redis://localhost:6379/0"
    postgres_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/smda"
    neo4j_url: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"

    # Celery
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # Research Crawler
    semantic_scholar_api_key: str = ""
    arxiv_search_enabled: bool = True

    # App Settings
    app_env: str = "development"
    log_level: str = "INFO"
    api_rate_limit_per_min: int = 100
    verdict_cache_ttl_hours: int = 24
    llm_batch_size: int = 20
    llm_default_temperature: float = 0.0
    llm_max_context_size: int = 128000
    llm_max_output_tokens: int = 4096
    llm_cost_budget_monthly_usd: float = 500.0
    feedback_rate_limit_per_hour: int = 20

    # Manipulation Index thresholds
    threshold_high: float = 0.85
    threshold_elevated: float = 0.65
    threshold_moderate: float = 0.40
    threshold_low: float = 0.20

    # LLM two-tier routing
    llm_escalation_threshold: float = 0.65
    llm_skip_threshold: float = 0.20

    # Temporal coordination
    coordination_time_variance_seconds: int = 60
    coordination_min_accounts: int = 3
    cross_thread_similarity_threshold: float = 0.85
    cross_thread_max_unrelated: int = 5

    # AI text detection
    ai_min_text_length: int = 80
    ai_flag_threshold: float = 0.75

    # Bot detection
    account_age_days_suspicious: int = 30
    posts_per_day_suspicious: int = 100
    follower_following_ratio_suspicious_low: float = 0.01
    follower_following_ratio_suspicious_high: float = 200.0

    # Monitoring
    prometheus_port: int = 9090
    grafana_port: int = 3000

    # Multilingual
    supported_languages: list[str] = ["en", "vi", "id", "th", "fil", "zh"]

    # Calibration
    calibration_window_days: int = 30
    calibration_min_samples: int = 100
    recalibration_threshold: float = 0.05


settings = Settings()
