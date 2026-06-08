# PROJECT-detail.md — Social Manipulation Detector Agent: Full Technical Specification

## 1. Problem Statement

Social media platforms host millions of comments daily. A growing fraction are:
- **AI bot-generated:** Synthetic accounts using LLMs to produce persuasive, human-looking content at scale
- **Coordinated campaigns:** Networks of accounts (bot farms, click farms, state-sponsored IRA-style ops) posting synchronized narratives
- **Financial manipulation:** FOMO (Fear Of Missing Out) and FUD (Fear, Uncertainty, Doubt) pump/dump campaigns targeting crypto and retail stock communities
- **Psychological manipulation:** Applying Cialdini-style influence tactics (social proof, urgency, authority, scarcity) via text to shift opinion

**Why static filters fail:** Keywords and regex are trivially bypassed. LLM-generated text has no consistent "fingerprint." Coordinated campaigns continuously adapt their language.

**Our solution:** Combine LLM-based semantic reasoning (few-shot Chain-of-Thought) with behavioral signals, network graph analysis, and a growing pattern library that self-updates from research — producing an explainable "Manipulation Index" per comment and per thread.

---

## 2. System Architecture

```
Social Platform Feed (comment stream)
           │
           ▼
  [API Gateway — FastAPI]
           │  POST /analyze/thread  or  POST /analyze/text
   ┌───────┴────────┐
   │  Task Queue    │ ← Redis + Celery (batch async)
   └───────┬────────┘
           │
   ┌───────▼──────────────────────────────────────────────────┐
   │                  ANALYSIS PIPELINE                       │
   │                                                          │
   │  Stage 1: Text Pre-processing + Language Detection       │
   │  Stage 2: AI-Generated Text Detection (HuggingFace)      │
   │  Stage 3: Manipulation Tactic Scoring (LLM Few-shot CoT) │
   │  Stage 4: Behavioral + Temporal Signals                  │
   │  Stage 5: Network Graph Analysis (Bot Cluster Detection) │
   │  Stage 6: Manipulation Index Aggregation                 │
   └───────┬──────────────────────────────────────────────────┘
           │
   ┌───────▼──────────┐   ┌────────────────────────────────┐
   │  Verdict Store   │   │  Browser Extension             │
   │  (PostgreSQL)    │   │  Visual warning overlay        │
   └──────────────────┘   └────────────────────────────────┘
           │
   ┌───────▼────────────────────┐
   │  SECOND-KNOWLEDGE-BRAIN    │ ← Self-updating via weekly crawler
   └────────────────────────────┘
```

---

## 3. Analysis Pipeline — Detailed

### Stage 1: Text Pre-processing (~10ms)

- Language detection: `langdetect` library — route to language-appropriate few-shot examples
- Tokenization + sentence segmentation
- Emoji normalization: map emoji clusters to semantic tokens (🚀🚀🚀 → `[HYPE_EMOJI_CLUSTER]`)
- URL extraction + replacement with `[URL]` token
- Hashtag analysis: extract and cross-reference against trending manipulation campaign tags
- Input validation: min 10 chars, max 2,000 chars per comment

---

### Stage 2: AI-Generated Text Detection (~50ms, parallel)

**Models (all from HuggingFace, no training required):**

```python
# Primary: OpenAI GPT-2 Output Detector (generalizes to many LLMs)
from transformers import pipeline
ai_detector = pipeline("text-classification", model="roberta-base-openai-detector")

# Secondary: ChatGPT-specific detector
chatgpt_detector = pipeline("text-classification", model="Hello-SimpleAI/chatgpt-detector-roberta")

# Score: average of both, weighted 0.6 / 0.4
```

**Limitations (important — in SECOND-KNOWLEDGE-BRAIN.md):**
- AI text detectors have high false positive rates on short texts (< 50 tokens)
- They degrade against GPT-4+ and Claude outputs vs. GPT-2 era
- Use as a *signal*, never as a standalone verdict
- Threshold for flagging: AI-generated probability > 0.75 AND text length > 80 chars

**Heuristic AI Text Signals (rule-based, fast):**
- Unusually balanced sentence structure (consistent paragraph length)
- Absence of typos, colloquialisms, or regional slang in a native-language context
- Hedging language patterns typical of RLHF-trained models ("It's important to note that...", "Certainly!", "I'd be happy to...")
- Suspiciously high vocabulary diversity score (TTR — Type-Token Ratio) for a "casual" comment

---

### Stage 3: Manipulation Tactic Scoring — LLM Few-shot CoT (Core)

This is the system's primary intelligence layer.

#### 3.1 Tactic Taxonomy (Cialdini + IRA Playbook + FOMO/FUD)

**Category A: Psychological Influence Tactics (Cialdini-derived)**
- `SOCIAL_PROOF` — "Everyone is doing this", "100k people already joined"
- `URGENCY_SCARCITY` — "Only 2 hours left", "Last chance", "Don't miss out"
- `AUTHORITY_FABRICATION` — Fake expert citations, manufactured credentials
- `RECIPROCITY_TRAP` — "I shared this secret with you, now you must..."
- `LIKING_FLATTERY` — Excessive agreement + flattery before persuasion attempt
- `COMMITMENT_ESCALATION` — Small ask → bigger ask pattern across comment chain

**Category B: Coordinated Inauthentic Behavior**
- `NARRATIVE_FLOODING` — Repeating same talking points with slight variations
- `BANDWAGON_MANUFACTURING` — Creating illusion of consensus
- `ASTROTURFING` — Fake grassroots support
- `HASHTAG_BOMBING` — Off-topic hashtag injection for trend manipulation

**Category C: Financial Manipulation (FOMO/FUD)**
- `FOMO_PUMP` — Price prediction + urgency + social proof combo
- `FUD_DUMP` — Fear amplification to trigger selling (coordinated FUD)
- `SHILL_PATTERN` — Unprompted promotion, referral links, fake testimonials
- `WHALE_NARRATIVE` — "Whales are accumulating", "Institutional money incoming"

**Category D: Disinformation Tactics**
- `EMOTIONAL_HIJACKING` — Extreme emotional language to bypass critical thinking
- `FALSE_DILEMMA` — "Either you X or you're a [enemy]"
- `FIREHOSE_FALSEHOOD` — Multiple false claims at once (too many to fact-check)
- `CONTEXT_REMOVAL` — Real quote/statistic stripped of context to mislead

**Category E: LLM-Characteristic Patterns**
- `LLM_HOLLOW_AFFIRMATION` — "Absolutely!", "Great point!", "You're so right!"
- `LLM_OVER_HEDGING` — Excessive qualifications in informal contexts
- `LLM_TEMPLATE_STRUCTURE` — Numbered lists + bullet points in casual conversation
- `LLM_BALANCED_FAKEOUT` — Fake "both sides" intro before pushing one agenda

#### 3.2 Master Few-Shot CoT Prompt

```
[SYSTEM]
You are a computational social science expert specializing in detecting psychological manipulation, coordinated inauthentic behavior, and AI-generated synthetic content in social media.

Your task: Analyze the provided social media comment(s) and produce a structured Manipulation Index score.

RULES:
- Score TACTICS and METHODS, never political positions or opinions themselves
- Be calibrated: most comments from real humans are score < 0.3
- Short ambiguous comments default to LOW confidence
- Always cite specific text spans as evidence

MANIPULATION TACTIC TAXONOMY:
[SOCIAL_PROOF] "Everyone knows...", "100k people already...", manufactured consensus
[URGENCY_SCARCITY] "Only today", "Don't miss out", artificial time pressure  
[FOMO_PUMP] Price prediction + urgency + social proof in financial context
[FUD_DUMP] Fear amplification to trigger panic selling
[LLM_HOLLOW_AFFIRMATION] "Absolutely!", "Great question!", "Certainly!"
[LLM_TEMPLATE_STRUCTURE] Bullet points/numbered lists in casual social context
[NARRATIVE_FLOODING] Same message with slight variation (compare with thread context)
[EMOTIONAL_HIJACKING] Extreme emotion to bypass critical thinking
[AUTHORITY_FABRICATION] Invented expert credentials or statistics
[SHILL_PATTERN] Unprompted product/asset promotion, referral links

FEW-SHOT EXAMPLES:
---
Comment: "🚀🚀 This token is about to EXPLODE! Whales are accumulating RIGHT NOW! Don't be the last one holding fiat when this 10x's by Friday! I turned $500 into $47,000 last month with this exact strategy! DM me for my private group! 🔥🔥"
Analysis:
- [FOMO_PUMP]: "about to EXPLODE", "10x's by Friday" — price prediction + urgency
- [SOCIAL_PROOF]: "Whales are accumulating" — manufactured authority/consensus  
- [URGENCY_SCARCITY]: "Don't be the last one" — explicit FOMO trigger
- [SHILL_PATTERN]: "DM me for my private group" — referral/commercial intent
- [AUTHORITY_FABRICATION]: "$500 into $47,000" unverified personal testimonial
Tactics detected: 5 | Manipulation Index: 0.93 | Confidence: HIGH
---
Comment: "I disagree with this policy because it historically hasn't worked in similar contexts."
Analysis:
- No manipulation tactics detected
- Direct opinion with reasoning
Tactics detected: 0 | Manipulation Index: 0.04 | Confidence: HIGH
---
Comment: "Absolutely! You've raised such an important point. It's crucial that we consider all perspectives here. There are several key factors to consider: 1) The economic implications, 2) The social impact, 3) The long-term sustainability."
Analysis:
- [LLM_HOLLOW_AFFIRMATION]: "Absolutely!", "such an important point"
- [LLM_TEMPLATE_STRUCTURE]: Numbered list in casual social context
- [LLM_OVER_HEDGING]: "consider all perspectives", "several key factors"
Tactics detected: 3 | Manipulation Index: 0.71 | Confidence: MEDIUM (short text)
---

Now analyze the following:
[COMMENT_OR_THREAD]
{input_text}
[THREAD_CONTEXT — for NARRATIVE_FLOODING detection]
{thread_context}

Respond as JSON:
{
  "manipulation_index": float (0.0-1.0),
  "confidence": "HIGH|MEDIUM|LOW",
  "tactics_detected": ["TACTIC_NAME", ...],
  "evidence": [{"tactic": "...", "span": "exact quote from text", "explanation": "..."}],
  "is_likely_ai_generated": bool,
  "is_likely_coordinated": bool,
  "summary": "1-2 sentence human-readable verdict"
}
```

#### 3.3 Cost Optimization Strategy

- **Batch processing:** Group up to 20 comments per LLM call (thread context included)
- **Two-tier routing:**
  - GPT-4o-mini for bulk scoring (< 0.65 score → log and move on, cost ~$0.00015/comment)
  - Claude 3.5 Sonnet only for HIGH suspicion re-analysis (> 0.65 from mini) or explicit user request
- **Cache:** Identical or near-identical texts (cosine sim > 0.95) reuse cached verdict (Redis, 24h TTL)
- **Skip LLM:** If AI text detector score < 0.20 AND no FOMO/FUD keywords → rule-based LOW verdict

---

### Stage 4: Behavioral & Temporal Signals (~20ms, from platform API)

**Account-Level Features (when platform API available):**
- `account_age_days` — < 30 days: elevated risk
- `follower_following_ratio` — ratio > 100 or < 0.01: bot signal
- `posts_per_day_avg` — > 50 posts/day: automation signal
- `profile_completeness` — no bio, default avatar, no profile photo
- `verified_status` — verified accounts get score reduction
- `historical_coordination_score` — from Neo4j graph (past coordinated behavior)

**Temporal Signals (thread-level):**
- `posting_burst_detection` — 3+ accounts posting same narrative within 60s window
- `cross_thread_repetition` — same text appearing in > 5 unrelated threads simultaneously
- `coordinated_engagement` — like/retweet clusters from bot accounts within seconds

```python
def temporal_coordination_score(comment_timestamps: list[datetime], 
                                  account_ids: list[str]) -> float:
    """
    Detect if multiple accounts posted similar content in suspiciously tight time windows.
    Returns 0.0–1.0 coordination probability.
    """
    # Variance < 60s across 3+ accounts with similar content = high coordination
    variance = compute_temporal_variance(comment_timestamps)
    if variance < 60 and len(account_ids) >= 3:
        return min(1.0, (60 - variance) / 60 * 1.2)
    return 0.0
```

---

### Stage 5: Bot Network Graph Analysis (Neo4j)

**Graph Schema:**
```
(Account)-[:POSTED]->(Comment)
(Account)-[:FOLLOWS]->(Account)
(Account)-[:MEMBER_OF]->(BotCluster)
(Comment)-[:PART_OF]->(NarrativeCampaign)
(NarrativeCampaign)-[:TARGETS]->(Topic)
```

**Cluster Detection:**
- Community detection: Louvain algorithm on follower/interaction graph
- Accounts posting identical/near-identical content within 1h window → candidate cluster
- Cluster confirmed when ≥ 5 accounts, ≥ 3 shared narrative posts, temporal variance < 5min

**Signals from Graph:**
- `cluster_membership_score` — is this account in a known bot cluster?
- `narrative_campaign_score` — is this comment part of an active campaign?
- `infrastructure_reuse_score` — shared creation IP, device fingerprint, or registration pattern

---

### Stage 6: Manipulation Index Aggregation

```python
def compute_manipulation_index(signals: dict) -> ManipulationVerdict:
    weights = {
        "llm_tactic_score":         0.40,  # Core semantic analysis
        "ai_generated_probability": 0.20,  # HuggingFace detector
        "behavioral_score":         0.20,  # Account-level behavior
        "temporal_coordination":    0.10,  # Posting timing patterns
        "graph_cluster_score":      0.10,  # Bot network membership
    }
    
    raw_score = sum(signals[k] * weights[k] for k in weights)
    
    # Confidence adjustment: short texts get confidence penalty
    confidence = "HIGH" if token_count > 80 else "MEDIUM" if token_count > 30 else "LOW"
    
    return ManipulationVerdict(
        manipulation_index=raw_score,
        confidence=confidence,
        level=classify_level(raw_score),
        signals=signals,
        evidence=signals["llm_evidence"],
        summary=signals["llm_summary"],
    )
```

---

## 4. Knowledge Self-Improvement Loop

```
Every 7 days:
  1. crawl_research.py
     Sources: arXiv, ACM DL, ICA (Int'l Communication Assoc.), USENIX
     Topics: ["disinformation detection", "bot detection NLP", "LLM text detection",
              "coordinated inauthentic behavior", "FOMO manipulation", "astroturfing"]
  
  2. Summarize papers via Claude API → extract:
     - New manipulation tactics observed in the wild
     - New LLM-generated text fingerprints
     - Model performance benchmarks
     - New labeled datasets
  
  3. update_patterns.py → append new patterns to data/manipulation_patterns/
     (versioned YAML files, never deleted)
  
  4. update_knowledge_brain.py → append structured summaries to SECOND-KNOWLEDGE-BRAIN.md
  
  5. Refresh few-shot examples in prompts/ with newly confirmed real-world cases
  
  6. Optional: if new labeled dataset found → fine-tune FinBERT or toxicity model
```

**Why this matters:** LLM-generated text fingerprints shift with each model version. GPT-4o has different writing patterns than GPT-3.5. The self-updating pattern library keeps the few-shot examples current with what's actually being deployed in the wild.

---

## 5. Platform Integration Architecture

### 5.1 Browser Extension (Primary User Surface)

**Manifest V3 — Chrome/Firefox/Edge**

Injection points per platform:
- **Twitter/X:** Hook `<article>` elements → inject badge after username
- **Facebook:** Hook comment containers → inject indicator before text
- **Reddit:** Hook `.Comment` elements → inject flair-style badge
- **YouTube:** Hook `ytd-comment-renderer` → inject timestamp badge
- **Telegram Web:** Hook `.message` elements

**Visual Warning System:**
```
🔴 [MANIPULATION DETECTED — 3 tactics] [Expand]
🟠 [SUSPICIOUS — AI-generated patterns] [Details]  
🟡 [LOW RISK — 1 minor signal] [Info]
```

**Performance:** Analysis cached by comment hash. Fresh comments batched every 2s and sent to API. Cached verdicts reused for 24h. Extension adds < 80ms overhead on cached results.

### 5.2 API Endpoints

```
POST /analyze/text          — Single text analysis
POST /analyze/thread        — Thread/comment array analysis (up to 200 comments)
POST /analyze/account       — Account behavior analysis (requires platform token)
GET  /verdict/{id}          — Retrieve stored verdict
GET  /campaigns/active      — Currently detected active manipulation campaigns
GET  /stats/platform/{name} — Platform-level manipulation statistics
POST /feedback/false-positive — User report (feeds confidence calibration)
```

### 5.3 Webhook Integration

For platform partners who want native integration:
```json
POST /webhook/stream
{
  "platform": "twitter",
  "event": "comment_created",
  "comment_id": "...",
  "text": "...",
  "author_id": "...",
  "timestamp": "..."
}
```
Returns verdict within 2s (async with callback URL supported for longer analyses).

---

## 6. Financial Manipulation (FOMO/FUD) Subsystem

This is a specialized track for crypto/stock community platforms (Reddit r/wallstreetbets, Telegram trading groups, Discord servers).

**Additional Models:**
- `ProsusAI/finbert` — financial sentiment (positive/negative/neutral)
- `yiyanghkust/finbert-tone` — financial tone classification

**FOMO Detection Signals:**
- Extreme positive sentiment + urgency keywords + price prediction combo
- Asset-specific pattern: `[ASSET_NAME] + [PRICE_TARGET] + [TIMEFRAME] + [SOCIAL_PROOF]`
- Referral link presence in financial recommendation context
- New account (< 30 days) promoting specific low-cap assets

**FUD Detection Signals:**
- Coordinated negative sentiment spike on specific asset within short window
- Unverified "insider information" claims + fear language
- Reference to regulatory action without source
- Pattern: appears shortly before/after large sell orders (cross-reference with on-chain data if available)

**FinBERT Pipeline:**
```python
fin_sentiment = pipeline("text-classification", model="ProsusAI/finbert")
result = fin_sentiment("This token will 100x by Friday!")
# → {'label': 'positive', 'score': 0.97}
# High positive + urgency keywords → escalate to FOMO_PUMP check
```

---

## 7. Multilingual Support

**Priority languages (SEA + global):**
- English (primary)
- Vietnamese (Tiếng Việt)
- Indonesian (Bahasa Indonesia)  
- Thai (ภาษาไทย)
- Filipino (Tagalog)
- Chinese Simplified (普通话)

**Multilingual Models:**
- `microsoft/mdeberta-v3-base` — cross-lingual semantic classification
- Few-shot examples in prompts must include examples in each target language
- Language-specific manipulation phrase dictionaries in `data/manipulation_patterns/`

**Vietnamese-specific patterns (high priority for SEA market):**
- FOMO phrases: "Đừng để lỡ cơ hội", "Đang tăng mạnh", "Vào ngay hôm nay"
- FUD phrases: "Sắp sập rồi", "Cảnh báo khẩn", "Rút tiền ngay"
- Bot indicators: Excessive use of "bạn ơi", overly formal Kinh Bắc/Southern dialect mixing

---

## 8. Improvements Over Base Concept

Beyond the original prompt-engineering idea, the following were added:

1. **HuggingFace AI text detectors** as Stage 2 pre-filter — catches obvious LLM output before expensive LLM API call
2. **Behavioral + temporal signals** — catches coordinated campaigns that use individually clean text
3. **Neo4j bot network graph** — links accounts across platforms, detects infrastructure reuse
4. **Financial manipulation subsystem** (FinBERT) — specialized for crypto/stock FOMO/FUD
5. **Multilingual support** with language-appropriate few-shot examples
6. **Self-updating pattern library** — YAML-versioned, never stale
7. **Browser extension** with platform-specific DOM injection per site
8. **Two-tier LLM routing** (GPT-4o-mini bulk + Claude 3.5 Sonnet precision) — reduces cost ~80%
9. **False positive feedback loop** — user reports recalibrate thresholds over time
10. **Calibration-first philosophy** — explicit bias toward avoiding false positives on legitimate speech

---

## 9. Ethical Safeguards

- **No content moderation:** The system scores and labels — it never removes content. Removal decisions belong to platforms/users.
- **No political targeting:** Tactic classification is content-agnostic. A left-wing FOMO post and a right-wing FOMO post get the same score.
- **Transparency:** Every verdict includes full evidence trail. Users can see exactly why a comment was flagged.
- **Adversarial testing:** Quarterly red-team exercises to ensure the system doesn't develop political bias.
- **Opt-in only:** Browser extension requires explicit user installation. No passive surveillance.
- **Data minimization:** Comment text processed ephemerally; only verdicts + anonymized signals stored.
