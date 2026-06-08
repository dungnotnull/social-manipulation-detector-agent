CREATE TABLE IF NOT EXISTS verdicts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    comment_hash    VARCHAR(64) NOT NULL UNIQUE,
    comment_text    TEXT NOT NULL,
    platform        VARCHAR(32),
    thread_id       VARCHAR(256),
    author_id       VARCHAR(256),
    manipulation_index  REAL NOT NULL DEFAULT 0.0,
    confidence      VARCHAR(16) NOT NULL DEFAULT 'LOW',
    level           VARCHAR(16) NOT NULL DEFAULT 'CLEAN',
    tactics_detected    JSONB DEFAULT '[]',
    evidence            JSONB DEFAULT '[]',
    is_likely_ai_generated  BOOLEAN DEFAULT FALSE,
    is_likely_coordinated   BOOLEAN DEFAULT FALSE,
    summary         TEXT,
    signals_raw     JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS campaigns (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(256) NOT NULL,
    description     TEXT,
    platform        VARCHAR(32) NOT NULL,
    tactic_category VARCHAR(64),
    target_topic    VARCHAR(256),
    account_count   INTEGER DEFAULT 0,
    comment_count   INTEGER DEFAULT 0,
    first_seen_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_seen_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_active       BOOLEAN DEFAULT TRUE,
    cluster_data    JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS feedback (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    verdict_id      UUID REFERENCES verdicts(id) ON DELETE SET NULL,
    report_type     VARCHAR(32) NOT NULL,
    reporter_notes  TEXT,
    resolved        BOOLEAN DEFAULT FALSE,
    resolution      TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_verdicts_hash ON verdicts(comment_hash);
CREATE INDEX IF NOT EXISTS idx_verdicts_platform ON verdicts(platform);
CREATE INDEX IF NOT EXISTS idx_verdicts_level ON verdicts(level);
CREATE INDEX IF NOT EXISTS idx_verdicts_created ON verdicts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_campaigns_active ON campaigns(is_active, platform);
CREATE INDEX IF NOT EXISTS idx_feedback_verdict ON feedback(verdict_id);
