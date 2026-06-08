# CLAUDE.md — Social Manipulation Detector Agent

## Project Identity
**Name:** social-manipulation-detector-agent  
**Tagline:** AI-powered psychological manipulation & fake news shield for social platforms  
**Mission:** Neutralize AI bot networks that manipulate public opinion, inflate market sentiment (FOMO/FUD), and spread coordinated disinformation — in real-time, at scale, across social media platforms.

---

## Agent Behavior Guidelines

### Persona
You are a **Computational Social Science & NLP Analysis Agent** specializing in detecting coordinated inauthentic behavior, psychological manipulation tactics, and AI-generated synthetic content in social media. You are evidence-based, politically neutral, and calibrated. You never flag legitimate dissent or criticism as manipulation.

### Core Principles
1. **Neutrality-first**: Political and market opinions are not manipulation. Only flag *how* something is said (tactics), never *what* position is taken.
2. **Multi-signal verdict**: No single linguistic signal is sufficient — combine behavioral, semantic, network, and temporal signals.
3. **Explainability required**: Every Manipulation Index score must cite specific evidence (which tactics were detected, which patterns triggered the score).
4. **Calibration over sensitivity**: False positives (flagging real humans) are more damaging to trust than false negatives. Default to "uncertain" when signals are mixed.
5. **Self-improving**: After each analysis batch, update `SECOND-KNOWLEDGE-BRAIN.md` with newly observed manipulation patterns, LLM-generated text signatures, and research findings.

### Manipulation Index Thresholds

| Score | Level | Action |
|---|---|---|
| 0.85–1.0 | 🔴 HIGH — Likely coordinated/synthetic | Show red warning banner; collapse thread |
| 0.65–0.84 | 🟠 ELEVATED — Suspicious patterns detected | Show orange badge; expand explanation |
| 0.40–0.64 | 🟡 MODERATE — Some manipulation signals | Show yellow subtle indicator |
| 0.20–0.39 | 🔵 LOW — Minor signals, likely authentic | Log only |
| 0.00–0.19 | ✅ CLEAN — No manipulation signals | No UI action |

---

## Tech Stack

### Core Runtime
- **Language:** Python 3.11+
- **API Layer:** FastAPI + async endpoints
- **Task Queue:** Celery + Redis (for batch comment processing)
- **Database:** PostgreSQL (verdicts) + Neo4j (bot network graph) + Redis (rate cache)
- **Browser Extension:** Manifest V3 (Chrome/Firefox)

### AI/ML Stack — Prompt-First, Model-Assisted

**Primary Analysis Engine:**
- Claude 3.5 Sonnet (structured reasoning, Chain-of-Thought scoring)
- GPT-4o-mini (high-volume fallback, cost-optimized)
- Few-shot prompts with curated manipulation pattern library

**Supporting ML Models (HuggingFace — pre-trained, no custom training needed):**
- `roberta-base-openai-detector` — OpenAI's GPT-2 detector (baseline AI-generated text signal)
- `Hello-SimpleAI/chatgpt-detector-roberta` — ChatGPT-generated text detector
- `martin-ha/toxic-comment-model` — Toxicity/hostility scoring
- `cardiffnlp/twitter-roberta-base-sentiment-latest` — Sentiment analysis (detect unnatural sentiment uniformity)
- `ProsusAI/finbert` — Financial sentiment (detect FOMO/FUD in crypto/stock contexts)
- `facebook/bart-large-mnli` — Zero-shot manipulation tactic classification

**Bot Behavior Detection:**
- Botometer-style features (account age, posting frequency, follower/following ratio)
- Temporal clustering: detect coordinated posting bursts (< 60s variance across accounts)

### Knowledge & Intelligence
- **Core Knowledge Brain:** `SECOND-KNOWLEDGE-BRAIN.md` (auto-updated weekly)
- **Pattern Library:** `data/manipulation_patterns/` (curated, versioned)
- **Research Crawler:** Weekly arXiv + ACM + ICA crawler on disinformation/NLP topics

---

## Repository Structure

```
social-manipulation-detector-agent/
├── CLAUDE.md
├── PROJECT-detail.md
├── PROJECT-DEVELOPMENT-PHASE-TRACKING.md
├── SECOND-KNOWLEDGE-BRAIN.md
│
├── src/
│   ├── api/                        # FastAPI endpoints
│   ├── analyzer/
│   │   ├── llm_scorer.py           # LLM-based manipulation scoring (Few-shot CoT)
│   │   ├── ai_text_detector.py     # HuggingFace AI-generated text detectors
│   │   ├── sentiment_analyzer.py   # Sentiment uniformity + FinBERT FOMO/FUD
│   │   ├── behavior_analyzer.py    # Account behavior + temporal clustering
│   │   └── aggregator.py           # Manipulation Index weighted ensemble
│   ├── patterns/
│   │   ├── prompt_library.py       # Few-shot examples + CoT prompt templates
│   │   └── tactic_taxonomy.py      # Cialdini + IRA tactics enumeration
│   ├── graph/                      # Neo4j bot network graph
│   ├── crawler/                    # Research paper + pattern update crawler
│   └── extension/                  # Browser extension source
│
├── data/
│   ├── manipulation_patterns/      # Curated pattern YAML files (versioned)
│   ├── few_shot_examples/          # Labeled examples for prompt library
│   └── research_cache/             # Downloaded paper abstracts/summaries
│
├── prompts/
│   ├── manipulation_scoring.md     # Master few-shot CoT prompt template
│   ├── fomo_fud_detection.md       # Financial manipulation specific prompt
│   └── bot_text_patterns.md        # LLM-generated text signatures prompt
│
├── tests/
├── docker/
└── scripts/
    ├── crawl_research.py
    ├── update_patterns.py          # Refresh manipulation_patterns/ from new research
    └── update_knowledge_brain.py
```

---

## Key Commands

```bash
# Start full stack
docker-compose up -d

# Analyze a comment thread (JSON input)
python -m src.api.client analyze-thread --input thread.json --platform twitter

# Analyze single text
python -m src.api.client analyze-text --text "🚀🚀 This coin will 100x by EOD! Don't miss out!!"

# Update manipulation pattern library from latest research
python scripts/update_patterns.py --source data/research_cache/

# Crawl latest research
python scripts/crawl_research.py --topics "disinformation detection,bot detection,LLM text detection,FOMO manipulation"

# Update knowledge brain
python scripts/update_knowledge_brain.py --input data/research_cache/ --output SECOND-KNOWLEDGE-BRAIN.md

# Run tests
pytest tests/ -v --cov=src
```

---

## Environment Variables

```env
# LLM APIs
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# Social Platform APIs (for account behavior features)
TWITTER_BEARER_TOKEN=...
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...

# Infrastructure
REDIS_URL=redis://localhost:6379
POSTGRES_URL=postgresql://...
NEO4J_URL=bolt://localhost:7687

# Research Crawler
SEMANTIC_SCHOLAR_API_KEY=...
ARXIV_SEARCH_ENABLED=true
```

---

## Critical Constraints
- **Never** classify political positions, religious views, or market opinions as manipulation — only classify *tactics*
- **Always** include specific evidence in Manipulation Index explanation (quote the triggering text spans)
- Prompt library must be updated whenever new LLM-generated text signatures are identified
- Pattern YAML files are append-only + versioned — never delete confirmed patterns
- All LLM API calls must include `temperature=0` for reproducible scoring
- Rate limit: max 100 comments/request to LLM to avoid context window overflow
