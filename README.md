
<p align="center">
  <img src="src/extension/icons/icon128.svg" width="96" height="96" alt="SMDA Logo" />
</p>

<h1 align="center">Social Manipulation Detector Agent</h1>

<p align="center">
  <strong>AI-powered psychological manipulation & disinformation shield for social platforms</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.11+-blue.svg" alt="Python 3.11+" />
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License: MIT" />
  <img src="https://img.shields.io/badge/status-production%20ready-brightgreen.svg" alt="Status: Production Ready" />
  <img src="https://img.shields.io/badge/platforms-Twitter%20%7C%20Reddit%20%7C%20YouTube%20%7C%20Facebook%20%7C%20Telegram%20%7C%20Discord%20%7C%20TikTok-blueviolet.svg" alt="Platforms" />
  <img src="https://img.shields.io/badge/languages-8-orange.svg" alt="Languages" />
</p>

<p align="center">
  <em>Neutralize AI bot networks that manipulate public opinion, inflate market sentiment,<br/>and spread coordinated disinformation — in real-time, at scale.</em>
</p>

---

## What This Is

Social media is flooded with AI-generated manipulation. Bots impersonate humans. Coordinated campaigns create fake consensus. FOMO/FUD pump-and-dump schemes exploit retail investors. Traditional keyword filters are trivially bypassed by modern LLMs.

**SMDA solves this with a hybrid approach**: LLM-based semantic reasoning (few-shot Chain-of-Thought) combined with behavioral signals, network graph analysis, and a self-updating pattern library — producing an explainable **Manipulation Index** (0.0–1.0) for every comment.

Every verdict includes a full evidence trail: which manipulation tactics were detected, the exact text spans that triggered them, and why.

---

## How It Works

```
Social Platform → API Gateway (FastAPI) → Task Queue (Celery + Redis)
                                              │
         ┌────────────────────────────────────┘
         ▼
  6-Stage Analysis Pipeline ──────────────────────────────────────┐
  ├─ Stage 1: Text Pre-processing + Language Detection            │
  ├─ Stage 2: AI-Generated Text Detection (HuggingFace × 2)      │
  ├─ Stage 3: Manipulation Tactic Scoring (LLM Few-shot CoT)     │
  ├─ Stage 4: Behavioral + Temporal Coordination Signals         │
  ├─ Stage 5: Bot Network Graph Analysis (Neo4j)                  │
  └─ Stage 6: Manipulation Index Weighted Aggregation            │
         │                                                        │
         ▼                                                        │
  Verdict Store (PostgreSQL) → Browser Extension (Visual Overlay) │
         │                                                        │
         ▼                                                        │
  SECOND-KNOWLEDGE-BRAIN ← Self-updating via weekly arXiv crawl   │
  ────────────────────────────────────────────────────────────────┘
```

### Stage by Stage

**Stage 1 — Preprocessing (~10ms)**  
Language detection (langdetect), emoji normalization (🚀🚀🚀 → `[HYPE_EMOJI_CLUSTER]`), URL extraction and replacement, hashtag inventory, token counting. Routes to language-appropriate analysis path.

**Stage 2 — AI-Generated Text Detection (~50ms)**  
Two HuggingFace models in parallel: `roberta-base-openai-detector` (generalized GPT-2 detector, weight 0.6) and `Hello-SimpleAI/chatgpt-detector-roberta` (ChatGPT-specific, weight 0.4). Augmented with 6 heuristic signals: hedging language, hollow affirmations, template structure, uniform sentence length, over-hedging, and balanced-fakeout patterns.

**Stage 3 — Manipulation Tactic Scoring (~800ms)**  
The core intelligence layer. Few-shot Chain-of-Thought prompt with curated manipulation pattern library covering 25 tactics across 5 categories. Two-tier LLM routing: GPT-4o-mini for bulk scoring ($0.00015/comment), Claude 3.5 Sonnet for high-suspicion re-analysis (>0.65 score). All calls at `temperature=0` for reproducibility. Batch processing: up to 20 comments per LLM call.

**Stage 4 — Behavioral & Temporal Signals (~20ms)**  
Botometer-style account features (age, post frequency, follower ratio, profile completeness). Temporal coordination detection: 3+ accounts posting similar content within 60s window. Cross-thread repetition via Jaccard similarity. Burst detection with configurable time windows.

**Stage 5 — Bot Network Graph (~100ms)**  
Neo4j graph with Louvain community detection. Accounts linked via POSTED, FOLLOWS, and MEMBER_OF relationships. Bot clusters identified when ≥5 accounts share ≥3 narrative posts with <5min temporal variance. Cross-platform same-content tracking.

**Stage 6 — Aggregation (~5ms)**  
Weighted ensemble: LLM tactic score (0.40) + AI-generated probability (0.20) + behavioral score (0.20) + temporal coordination (0.10) + graph cluster score (0.10). Confidence adjusted by text length. Five-level classification.

---

## Manipulation Tactic Taxonomy

SMDA detects 25 manipulation tactics organized into 5 categories:

| Category | Tactics |
|---|---|
| **A — Psychological Influence** (Cialdini-derived) | Social Proof, Urgency/Scarcity, Authority Fabrication, Reciprocity Trap, Liking/Flattery, Commitment Escalation, Emotional Hijacking, False Dilemma, Firehose Falsehood, Context Removal |
| **B — Coordinated Inauthentic Behavior** | Narrative Flooding, Bandwagon Manufacturing, Astroturfing, Hashtag Bombing, Reply Brigading, Cross-Platform Sync, Creation Burst, Engagement Pod, Sleeper Account, Quote-Tweet Amplification |
| **C — Financial Manipulation** | FOMO Pump, FUD Dump, Shill Pattern, Whale Narrative, Pre-Listing Hype, Ponzi Framing |
| **D — Disinformation** | Emotional Hijacking, False Dilemma, Firehose Falsehood, Context Removal, Fake Equivalence, Whataboutism, Cherry Picking, Gish Gallop, Sowing Discord |
| **E — LLM-Characteristic Patterns** | Hollow Affirmation, Over-Hedging, Template Structure, Balanced Fakeout, Conclusion Recap, Persona Mimicry, Haunted Knowledge, Statistical Smoothness |

---

## Manipulation Index Thresholds

| Score | Level | Action |
|---|---|---|
| 0.85–1.00 | 🔴 **HIGH** — Likely coordinated/synthetic | Red warning banner; collapse thread |
| 0.65–0.84 | 🟠 **ELEVATED** — Suspicious patterns detected | Orange badge; expand explanation |
| 0.40–0.64 | 🟡 **MODERATE** — Some manipulation signals | Yellow subtle indicator |
| 0.20–0.39 | 🔵 **LOW** — Minor signals, likely authentic | Log only |
| 0.00–0.19 | ✅ **CLEAN** — No manipulation signals | No UI action |

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Runtime** | Python 3.11+ |
| **API** | FastAPI (async), Pydantic v2 |
| **Task Queue** | Celery + Redis |
| **Databases** | PostgreSQL (verdicts), Neo4j (bot graph), Redis (cache) |
| **LLM Scoring** | Claude 3.5 Sonnet + GPT-4o-mini (two-tier routing) |
| **NLP Models** | 7 HuggingFace pipelines — AI text detection, sentiment, FinBERT, toxicity, zero-shot classification, mDeBERTa |
| **Browser Extension** | Manifest V3 (Chrome + Firefox) |
| **Monitoring** | Prometheus + Grafana, k6 load testing |
| **Migrations** | Alembic (async PostgreSQL) |
| **Containerization** | Docker Compose (7 services) |

### HuggingFace Models

| Model | Purpose |
|---|---|
| `roberta-base-openai-detector` | AI-generated text detection (primary) |
| `Hello-SimpleAI/chatgpt-detector-roberta` | ChatGPT-specific text detection (secondary) |
| `cardiffnlp/twitter-roberta-base-sentiment-latest` | General sentiment analysis |
| `ProsusAI/finbert` | Financial sentiment — FOMO/FUD detection |
| `yiyanghkust/finbert-tone` | Financial tone classification |
| `martin-ha/toxic-comment-model` | Toxicity and hostility scoring |
| `facebook/bart-large-mnli` | Zero-shot manipulation tactic classification |
| `microsoft/mdeberta-v3-base` | Multilingual classification (8 languages) |

---

## Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- An OpenAI API key or Anthropic API key (for LLM scoring)

### 5-Minute Setup

```bash
# 1. Clone
git clone https://github.com/dungnotnull/social-manipulation-detector-agent.git
cd social-manipulation-detector-agent

# 2. Configure
cp .env.example .env
# Edit .env — add your ANTHROPIC_API_KEY and/or OPENAI_API_KEY

# 3. Start the stack
docker-compose up -d

# 4. Verify health
curl http://localhost:8000/health

# 5. Analyze a comment
python -m src.api.client analyze-text \
  --text "🚀🚀 This token will 100x by Friday! Don't miss out!!" \
  --platform twitter

# 6. Analyze a thread from a JSON file
python -m src.api.client analyze-thread \
  --input thread.json \
  --platform twitter
```

### Without Docker (Development)

```bash
pip install -e ".[dev]"
cp .env.example .env

# Start Redis + PostgreSQL + Neo4j separately, then:
python -m src.api.main          # API server on :8000
celery -A src.worker worker      # Worker (optional, for async processing)
```

---

## API Reference

Full interactive docs available at `http://localhost:8000/docs` (Swagger) and `http://localhost:8000/redoc` (ReDoc).

### Core Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/analyze/text` | Analyze a single comment |
| `POST` | `/analyze/thread` | Analyze a thread (up to 200 comments) |
| `POST` | `/analyze/account` | Analyze account behavior (bot probability) |
| `GET` | `/verdict/{id}` | Retrieve a stored verdict by ID |

### Platform Streams

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/stream/twitter/search` | Search Twitter/X for matching comments |
| `POST` | `/stream/twitter/search-and-analyze` | Search + analyze in one call |
| `GET` | `/stream/reddit/thread` | Fetch Reddit thread comments |
| `GET` | `/stream/youtube/video` | Fetch YouTube video comments |

### Campaigns & Stats

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/campaigns/active` | Currently active manipulation campaigns |
| `GET` | `/stats/platform/{name}` | Platform-level manipulation statistics |

### Feedback & Webhooks

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/feedback/false-positive` | Report a false positive for calibration |
| `POST` | `/webhook/stream` | Platform partner webhook integration |

### Operations

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check + model readiness report |
| `GET` | `/metrics` | Prometheus metrics endpoint |

### Example Response

```json
{
  "manipulation_index": 0.93,
  "confidence": "HIGH",
  "level": "HIGH",
  "tactics_detected": [
    "FOMO_PUMP",
    "SOCIAL_PROOF",
    "URGENCY_SCARCITY",
    "SHILL_PATTERN"
  ],
  "evidence": [
    {
      "tactic": "FOMO_PUMP",
      "span": "will 100x by Friday",
      "explanation": "Price prediction + urgency combo"
    },
    {
      "tactic": "URGENCY_SCARCITY",
      "span": "Don't miss out",
      "explanation": "Explicit FOMO trigger"
    }
  ],
  "is_likely_ai_generated": false,
  "is_likely_coordinated": false,
  "summary": "Multiple high-confidence financial manipulation tactics detected.",
  "comment_hash": "sha256...",
  "model_used": "gpt-4o-mini",
  "processing_time_ms": 847.32
}
```

---

## Browser Extension

The browser extension provides real-time visual warnings as you browse social platforms.

### Supported Platforms
- **Twitter/X** — Hook: `<article>` elements, badge after username
- **Reddit** — Hook: `.Comment` elements, flair-style badge
- **YouTube** — Hook: `ytd-comment-renderer`, timestamp badge
- **Facebook** — Hook: comment containers, indicator before text
- **Telegram Web** — Hook: `.Message` elements
- **Discord Web** — Hook: message elements

### Features
- Color-coded warning badges (🔴🟠🟡🔵)
- Click-to-expand evidence panel with detected tactics and text spans
- Batch API calls (up to 20 comments per 2s interval)
- 24-hour local cache (chrome.storage.local)
- False-positive reporting directly from the badge
- Configurable sensitivity threshold
- Per-platform enable/disable toggles

### Installation

```bash
# Build both Chrome and Firefox packages
python scripts/build_extension.py

# Chrome: Load unpacked from src/extension/
# Firefox: Load temporary add-on from src/extension/manifest.json
```

---

## Self-Improvement Loop

SMDA's detection capabilities continuously improve without retraining:

```
Every 7 days:

  1. scripts/crawl_research.py
     Sources: arXiv, Semantic Scholar
     Topics: disinformation, bot detection, LLM text detection,
             coordinated inauthentic behavior, FOMO manipulation

  2. Claude API summarizes papers → extracts new tactics + patterns

  3. scripts/update_patterns.py
     Appends new tactics to data/manipulation_patterns/ (versioned YAML)

  4. scripts/update_knowledge_brain.py
     Appends structured research findings to SECOND-KNOWLEDGE-BRAIN.md

  5. Few-shot examples refreshed with newly confirmed real-world cases

  6. Calibration loop adjusts thresholds based on false-positive reports
```

### Automation Scripts

```bash
# Crawl research papers
python scripts/crawl_research.py \
  --topics "disinformation,bot detection,LLM text detection,FOMO manipulation" \
  --output-dir data/research_cache/

# Update pattern YAML files from research
python scripts/update_patterns.py \
  --source data/research_cache/ \
  --output data/manipulation_patterns/

# Update knowledge brain
python scripts/update_knowledge_brain.py \
  --input data/research_cache/ \
  --output SECOND-KNOWLEDGE-BRAIN.md

# Generate weekly performance report
python scripts/weekly_report.py --output-dir reports/

# Export anonymized dataset for academic research
python scripts/academic_export.py --output-dir exports/

# Load test with k6
k6 run scripts/load_test.js
```

---

## Project Structure

```
social-manipulation-detector-agent/
│
├── src/
│   ├── api/                         # FastAPI application
│   │   ├── routes/                  #   Route handlers (analysis, campaigns, feedback, webhook, stream)
│   │   ├── schemas/                 #   Pydantic request/response models
│   │   ├── platforms/               #   Platform API clients (Twitter, Reddit, YouTube, Telegram, Discord, TikTok)
│   │   ├── models.py                #   SQLAlchemy ORM models
│   │   ├── db.py                    #   Async database engine + session factory
│   │   ├── dependencies.py          #   Shared dependencies (Redis, Neo4j, rate limiter)
│   │   ├── tasks.py                 #   Celery tasks + sync pipeline runner
│   │   ├── metrics.py               #   Prometheus metrics + middleware
│   │   ├── db_integrity.py          #   Database integrity check utilities
│   │   ├── main.py                  #   FastAPI app factory + all router registration
│   │   └── client.py                #   CLI client for API interaction
│   │
│   ├── analyzer/                    # 6-Stage analysis pipeline
│   │   ├── preprocessor.py          #   Stage 1: Text preprocessing, language detection
│   │   ├── ai_text_detector.py      #   Stage 2: AI-generated text detection (HF models + heuristics)
│   │   ├── sentiment_analyzer.py    #   Stage 3b: Sentiment analysis + FinBERT FOMO/FUD
│   │   ├── finbert_subsystem.py     #   Stage 3b: FinBERT-Tone financial manipulation subsystem
│   │   ├── llm_scorer.py            #   Stage 3a: Few-shot CoT LLM scoring (two-tier routing)
│   │   ├── behavior_analyzer.py     #   Stage 4: Behavioral + temporal coordination signals
│   │   ├── aggregator.py            #   Stage 6: Weighted ensemble + confidence + level classification
│   │   ├── pipeline_orchestrator.py #   Full pipeline runner with timing + cost tracking
│   │   ├── token_counter.py         #   Tiktoken-based token counting + truncation
│   │   ├── toxicity_detector.py     #   Toxicity scoring (martin-ha/toxic-comment-model)
│   │   ├── zero_shot_classifier.py  #   Zero-shot tactic classification (bart-large-mnli)
│   │   ├── prompt_engineer.py       #   Prompt variant management + iterative improvement
│   │   ├── multilingual.py          #   Language detection + mDeBERTa routing
│   │   ├── account_features.py      #   Botometer-style account feature extraction
│   │   ├── cross_platform.py        #   Cross-platform content matching
│   │   ├── calibration.py           #   Calibration feedback loop + threshold auto-adjust
│   │   ├── few_shot_refresher.py    #   Auto-refresh few-shot examples from new cases
│   │   ├── cost_auditor.py          #   LLM cost tracking + budget monitoring
│   │   └── bias_audit.py            #   Political bias audit (8-quadrant red-team)
│   │
│   ├── patterns/                    # Tactic taxonomy + prompt library
│   │   ├── tactic_taxonomy.py       #   25 tactics across 5 categories (typed enums + dataclasses)
│   │   └── prompt_library.py        #   LRU-cached prompt loader + few-shot example manager
│   │
│   ├── graph/                       # Neo4j bot network operations
│   │   └── neo4j_client.py          #   Async driver, Louvain community detection, campaign linking
│   │
│   ├── crawler/                     # Research paper crawler
│   │   └── research_crawler.py      #   arXiv + Semantic Scholar + Claude summarization
│   │
│   ├── extension/                   # Chrome/Firefox MV3 browser extension
│   │   ├── manifest.json            #   MV3 manifest with browser_specific_settings for Firefox
│   │   ├── background.js            #   Service worker: batch API calls, cache management
│   │   ├── content.js               #   Cross-platform content script: DOM observation, badge injection
│   │   ├── injectors/               #   Platform-specific DOM injectors
│   │   │   ├── twitter.js           #     Twitter/X: article[data-testid="tweet"]
│   │   │   ├── reddit.js            #     Reddit: shreddit-comment
│   │   │   ├── youtube.js           #     YouTube: ytd-comment-renderer
│   │   │   ├── facebook.js          #     Facebook: [role="article"]
│   │   │   ├── telegram.js          #     Telegram Web: .Message
│   │   │   └── discord.js           #     Discord Web: message-content
│   │   ├── popup/                   #     Extension popup UI
│   │   │   ├── popup.html           #       Campaign stats, sensitivity, platform toggles
│   │   │   ├── popup.js             #       Dynamic stat loading + settings persistence
│   │   │   └── popup.css            #       Minimalist editorial styling
│   │   └── icons/                   #   Extension icons (PNG + SVG source)
│   │
│   ├── config.py                    # Pydantic Settings — all 40+ env vars with defaults
│   ├── worker.py                    # Celery app factory
│   └── model_availability.py        # Runtime model readiness checker
│
├── data/
│   ├── manipulation_patterns/       # 9 YAML files — 43 tactics + 4 language-specific
│   ├── few_shot_examples/           # 50 labeled examples (EN, VI, ID)
│   └── research_cache/              # Downloaded paper abstracts (auto-populated)
│
├── prompts/                         # LLM prompt templates
│   ├── manipulation_scoring.md      #   Master few-shot CoT prompt (7 examples, 5 categories)
│   ├── fomo_fud_detection.md        #   Financial manipulation specialized prompt
│   └── bot_text_patterns.md         #   LLM-generated text signature detection prompt
│
├── scripts/                         # Automation scripts
│   ├── crawl_research.py            #   Weekly arXiv + Semantic Scholar crawler
│   ├── update_patterns.py           #   Auto-append new tactics to YAML pattern files
│   ├── update_knowledge_brain.py    #   Auto-update SECOND-KNOWLEDGE-BRAIN.md
│   ├── weekly_report.py             #   Weekly performance report generator
│   ├── academic_export.py           #   Anonymized dataset export for research
│   ├── build_extension.py           #   Chrome + Firefox extension packaging
│   ├── prepare_submission.py        #   Store submission package preparation
│   └── load_test.js                 #   k6 load test script (5-stage ramp)
│
├── docker/
│   ├── api.Dockerfile               #   Python 3.11-slim, uvicorn on :8000
│   ├── worker.Dockerfile            #   Python 3.11-slim, Celery worker
│   ├── init-db.sql                  #   PostgreSQL schema (verdicts, campaigns, feedback + indexes)
│   ├── prometheus.yml               #   Prometheus scrape config
│   ├── grafana-datasources.yml      #   Grafana Prometheus datasource
│   └── grafana-dashboards.yml       #   Grafana dashboard provisioning
│
├── alembic/                         # Database migrations
│   ├── env.py                       #   Async PostgreSQL migration runner
│   └── versions/                    #   Migration files
│
├── public/
│   └── dashboard.html               #   Public campaign monitoring dashboard
│
├── CLAUDE.md                        # Developer agent guide
├── PROJECT-detail.md                # Full technical specification
├── SECOND-KNOWLEDGE-BRAIN.md        # Self-updating research encyclopedia
├── PROJECT-DEVELOPMENT-PHASE-TRACKING.md  # Development status (all phases complete)
├── README.md                        # This file
├── CONTRIBUTING.md                  # Contribution guidelines
├── CHANGELOG.md                     # Release changelog
├── LICENSE                          # MIT
├── pyproject.toml                   # Build config + dependencies
├── requirements.txt                 # Flat pip dependency list
├── docker-compose.yml               # 7-service stack (API, worker, Redis, PostgreSQL, Neo4j, Prometheus, Grafana)
├── alembic.ini                      # Alembic configuration
└── .env.example                     # Environment variable template
```

---

## Supported Platforms

| Platform | API Integration | Browser Extension | Account Analysis |
|---|---|---|---|
| **Twitter/X** | API v2 (Bearer token) | ✅ article hook | ✅ (age, followers, verified) |
| **Reddit** | OAuth2 (PRAW-style) | ✅ .Comment hook | ✅ (karma, age, verified) |
| **YouTube** | Data API v3 | ✅ ytd-comment hook | ✅ (subscribers, videos) |
| **Facebook** | — (DOM only) | ✅ [role="article"] | — |
| **Telegram** | Bot API | ✅ .Message hook | — (chat info) |
| **Discord** | Bot API (Gateway) | ✅ message-content hook | — (guild info) |
| **TikTok** | Research API v2 | — | — |

---

## Supported Languages

| Language | Code | Few-Shot Examples | Pattern YAML | mDeBERTa |
|---|---|---|---|---|
| English | `en` | 25 | — | — |
| Vietnamese | `vi` | 15 | ✅ | ✅ |
| Indonesian | `id` | 10 | ✅ | ✅ |
| Thai | `th` | — | ✅ | ✅ |
| Filipino | `fil` | — | ✅ | ✅ |
| Chinese | `zh` | — | — | ✅ |
| Japanese | `ja` | — | — | ✅ |
| Korean | `ko` | — | — | ✅ |

---

## Cost Optimization

SMDA's two-tier LLM routing achieves ~80% cost reduction vs. all-Claude-Sonnet:

| Metric | Value |
|---|---|
| GPT-4o-mini cost/comment | ~$0.00015 |
| Claude 3.5 Sonnet cost/comment | ~$0.0015 |
| Escalation rate (mini → Sonnet) | ~10% of comments |
| Redis cache hit rate (typical) | 50-70% |
| Effective cost/comment | ~$0.00005 |
| Monthly budget (default) | $500 |

The `cost_auditor` tracks all LLM spending in real-time and can trigger budget alerts.

---

## Ethical Safeguards

**SMDA scores and labels — it never removes content.** Removal decisions belong to platforms and users.

- **No political targeting**: Tactic classification is content-agnostic. A left-wing FOMO post and a right-wing FOMO post get the same score. Political positions, religious views, and market opinions are never classified as manipulation — only *how* something is said.

- **Transparency by default**: Every verdict includes a full evidence trail. Users can see exactly which text spans triggered which tactics, and why. There is no "black box" score.

- **Calibration-first philosophy**: False positives (flagging real humans) are more damaging to trust than false negatives. Default to "uncertain" when signals are mixed. The system is deliberately conservative — most human comments score <0.3.

- **Quarterly bias audits**: The `bias_audit` module runs 8-quadrant red-team tests (economic left/right × social progressive/conservative) to verify that identical manipulation tactics receive identical scores regardless of political orientation.

- **Opt-in only**: The browser extension requires explicit user installation. No passive surveillance. Comment text is processed ephemerally — only verdicts and anonymized signals are stored.

- **Data minimization**: Comment text is hashed (SHA-256) for cache keys. Anonymized academic exports strip all user-identifying information.

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | For LLM | — | Claude 3.5 Sonnet API key |
| `OPENAI_API_KEY` | For LLM | — | GPT-4o-mini API key |
| `TWITTER_BEARER_TOKEN` | For Twitter | — | Twitter API v2 bearer token |
| `REDDIT_CLIENT_ID` | For Reddit | — | Reddit app client ID |
| `REDDIT_CLIENT_SECRET` | For Reddit | — | Reddit app client secret |
| `YOUTUBE_API_KEY` | For YouTube | — | YouTube Data API v3 key |
| `TELEGRAM_BOT_TOKEN` | For Telegram | — | Telegram bot token |
| `DISCORD_BOT_TOKEN` | For Discord | — | Discord bot token |
| `TIKTOK_ACCESS_TOKEN` | For TikTok | — | TikTok Research API token |
| `REDIS_URL` | Yes | `redis://localhost:6379/0` | Redis connection |
| `POSTGRES_URL` | Yes | `postgresql+asyncpg://...` | PostgreSQL connection |
| `NEO4J_URL` | For graph | `bolt://localhost:7687` | Neo4j connection |
| `SEMANTIC_SCHOLAR_API_KEY` | For crawler | — | Semantic Scholar API key |
| `LLM_COST_BUDGET_MONTHLY_USD` | No | `500.00` | Monthly LLM budget cap |
| `VERDICT_CACHE_TTL_HOURS` | No | `24` | Redis cache TTL |
| `API_RATE_LIMIT_PER_MIN` | No | `100` | Rate limit per IP |

All variables in `.env.example`.

---

## Monitoring

### Prometheus Metrics

| Metric | Type | Description |
|---|---|---|
| `smda_http_requests_total` | Counter | HTTP requests by method, endpoint, status |
| `smda_http_request_duration_seconds` | Histogram | Request latency distribution |
| `smda_verdicts_total` | Counter | Verdicts by level and platform |
| `smda_manipulation_index` | Histogram | Manipulation score distribution |
| `smda_llm_cost_total_usd` | Gauge | Cumulative LLM API cost |
| `smda_llm_calls_total` | Counter | LLM API calls by model |
| `smda_cache_hit_ratio` | Gauge | Redis cache effectiveness |
| `smda_pipeline_duration_seconds` | Histogram | End-to-end pipeline latency |
| `smda_active_campaigns` | Gauge | Currently active manipulation campaigns |

Access Grafana at `http://localhost:3000` (admin/admin) after `docker-compose up -d`.

### Health Endpoint

`GET /health` returns a full readiness report:

```json
{
  "status": "ok",
  "version": "0.1.0",
  "readiness": {
    "dependencies": { "transformers": true, "openai": true, ... },
    "models_available": 7,
    "models_total": 9,
    "can_run_inference": true,
    "can_use_llm": true,
    "can_use_graph": false,
    "can_use_queue": true
  }
}
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for full guidelines.

Quick start:

```bash
git clone https://github.com/dungnotnull/social-manipulation-detector-agent.git
cd social-manipulation-detector-agent
pip install -e ".[dev]"
```

Areas that welcome contributions:
- New platform integrations (platform client + DOM injector)
- New language support (few-shot examples + pattern YAML + LANG_CONFIG entry)
- New manipulation tactics (taxonomy entry + pattern YAML + prompt update + few-shot examples)
- Improved evasion counter-strategies (Section 9 of SECOND-KNOWLEDGE-BRAIN.md)

---

## License

MIT — see [LICENSE](LICENSE) for full text.

---

<p align="center">
  <sub>Built with ❤️ by <a href="https://github.com/dungnotnull">dungnotnull</a> and contributors</sub>
</p>
