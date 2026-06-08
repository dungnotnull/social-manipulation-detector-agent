# Changelog

## [1.0.0] - 2026-06-08

### Added
- Complete 6-stage analysis pipeline (preprocessing, AI text detection, sentiment, LLM scoring, behavioral, aggregation)
- Two-tier LLM routing (GPT-4o-mini → Claude 3.5 Sonnet escalation)
- Cost auditor with per-model tracking and monthly budget monitoring
- 6 platform API clients (Twitter/X v2, Reddit OAuth2, YouTube v3, Telegram, Discord, TikTok)
- 8-language multilingual support with mDeBERTa routing
- 43 manipulation tactic patterns across 5 categories (A-E)
- 50 few-shot examples across English, Vietnamese, Indonesian
- 4 language-specific manipulation pattern YAMLs (VI, ID, TH, FIL)
- Browser extension with 6 platform DOM injectors (Chrome + Firefox)
- Prometheus + Grafana monitoring with 8 metric types
- k6 load test script (5-stage ramp to 500 VUs)
- Alembic database migration support
- Political bias audit with 8-quadrant red-team test suite
- Calibration feedback loop with automatic threshold adjustment
- Research paper crawler (arXiv + Semantic Scholar)
- Self-updating knowledge brain and pattern library
- Weekly model performance report automation
- Public campaign monitoring dashboard
- Academic dataset export (anonymized)
- Chrome Web Store and Firefox Add-ons submission prep
- Full Docker Compose stack (API, worker, Redis, PostgreSQL, Neo4j, Prometheus, Grafana)

### Security
- API rate limiting (Redis-backed token bucket)
- Database integrity checks for verdicts and campaigns
- False-positive reporting with calibration feedback
- Conservative manipulation thresholds to minimize false positives

### Documentation
- CLAUDE.md (developer guide)
- PROJECT-detail.md (technical specification)
- SECOND-KNOWLEDGE-BRAIN.md (research encyclopedia)
- PROJECT-DEVELOPMENT-PHASE-TRACKING.md (implementation status)
- README.md (public documentation)
- CONTRIBUTING.md (contribution guide)
- LICENSE (MIT)
