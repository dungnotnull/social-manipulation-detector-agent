from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from src.analyzer.account_features import AccountFeatureExtractor
from src.analyzer.aggregator import AggregationInput, ManipulationAggregator
from src.analyzer.ai_text_detector import AITextDetector
from src.analyzer.behavior_analyzer import BehaviorAnalyzer, BehaviorScore, CommentMeta
from src.analyzer.cost_auditor import cost_auditor
from src.analyzer.cross_platform import CrossPlatformLinker
from src.analyzer.llm_scorer import LLMScorer
from src.analyzer.multilingual import MultilingualHandler
from src.analyzer.preprocessor import TextPreprocessor, ProcessedText
from src.analyzer.prompt_engineer import prompt_engineer
from src.analyzer.sentiment_analyzer import SentimentAnalyzer
from src.analyzer.token_counter import token_counter
from src.analyzer.toxicity_detector import ToxicityDetector
from src.analyzer.zero_shot_classifier import ZeroShotClassifier
from src.config import settings


@dataclass
class PipelineResult:
    manipulation_index: float
    confidence: str
    level: str
    tactics_detected: list[str]
    evidence: list[dict[str, str]]
    is_likely_ai_generated: bool
    is_likely_coordinated: bool
    summary: str
    comment_hash: str
    model_used: str
    tokens_used: int
    cost_estimate: float
    language: str
    ai_probability: float
    fomo_score: float
    fud_score: float
    toxicity_score: float
    account_risk: float
    processing_time_ms: float
    stages_completed: list[str] = field(default_factory=list)


class PipelineOrchestrator:
    def __init__(self):
        self._preprocessor = TextPreprocessor()
        self._ai_detector = AITextDetector()
        self._sentiment = SentimentAnalyzer()
        self._toxicity = ToxicityDetector()
        self._llm_scorer = LLMScorer()
        self._zero_shot = ZeroShotClassifier()
        self._behavior = BehaviorAnalyzer()
        self._aggregator = ManipulationAggregator()
        self._multilingual = MultilingualHandler()
        self._account_extractor = AccountFeatureExtractor()
        self._cross_platform = CrossPlatformLinker()

    def analyze_single(
        self,
        text: str,
        platform: str = "unknown",
        thread_context: list[str] | None = None,
        skip_llm: bool = False,
    ) -> PipelineResult:
        t_start = datetime.now(timezone.utc)
        stages: list[str] = []

        processed = self._preprocessor.preprocess(text)
        stages.append("stage1_preprocess")

        ml_result = self._multilingual.detect_and_classify(processed.normalized_text)
        stages.append("lang_detect")

        ai_result = self._ai_detector.detect(processed.normalized_text)
        stages.append("stage2_ai_detect")

        sentiment_result = self._sentiment.analyze(processed.normalized_text)
        stages.append("sentiment")

        tox_result = self._toxicity.detect(processed.normalized_text)
        stages.append("toxicity")

        tokens = token_counter.count(processed.normalized_text)

        should_skip = ai_result.should_skip_llm or skip_llm
        if should_skip:
            llm_result = LLMScorer._make_default_result()
            stages.append("stage3_llm_skipped")
        else:
            llm_result = self._llm_scorer.score(
                processed.normalized_text, thread_context
            )
            stages.append("stage3_llm_score")

        model_used = llm_result.model_used
        model_tokens = llm_result.tokens_used
        cost = llm_result.cost_estimate

        if model_used != "skipped":
            cost_auditor.record_call(model_used, model_tokens, cost)

        signals = AggregationInput(
            llm_tactic_score=llm_result.manipulation_index,
            ai_generated_probability=ai_result.ai_probability,
            behavioral_score=0.0,
            temporal_coordination=0.0,
            graph_cluster_score=0.0,
            token_count=processed.token_count,
            llm_evidence=llm_result.evidence,
            llm_summary=llm_result.summary,
        )
        stages.append("stage6_aggregate")

        verdict = self._aggregator.compute(signals)

        t_end = datetime.now(timezone.utc)
        elapsed_ms = (t_end - t_start).total_seconds() * 1000

        return PipelineResult(
            manipulation_index=verdict.manipulation_index,
            confidence=verdict.confidence,
            level=verdict.level,
            tactics_detected=llm_result.tactics_detected,
            evidence=llm_result.evidence,
            is_likely_ai_generated=llm_result.is_likely_ai_generated,
            is_likely_coordinated=llm_result.is_likely_coordinated,
            summary=verdict.summary,
            comment_hash=hashlib.sha256(text.encode()).hexdigest(),
            model_used=model_used,
            tokens_used=model_tokens,
            cost_estimate=cost,
            language=processed.language,
            ai_probability=ai_result.ai_probability,
            fomo_score=sentiment_result.fomo_score,
            fud_score=sentiment_result.fud_score,
            toxicity_score=tox_result.toxicity_score,
            account_risk=0.0,
            processing_time_ms=round(elapsed_ms, 2),
            stages_completed=stages,
        )

    def analyze_thread(
        self,
        texts: list[str],
        platform: str = "unknown",
    ) -> list[PipelineResult]:
        results: list[PipelineResult] = []
        for i, text in enumerate(texts):
            context = [t for j, t in enumerate(texts) if j != i]
            result = self.analyze_single(text, platform=platform, thread_context=context)
            results.append(result)

        metas = [
            CommentMeta(text=t, author_id="", platform=platform)
            for t in texts
        ]
        coordination = self._behavior.detect_temporal_coordination(metas)
        repetition = self._behavior.detect_cross_thread_repetition(texts)

        if coordination.is_coordinated:
            results = [
                PipelineResult(
                    manipulation_index=r.manipulation_index,
                    confidence=r.confidence,
                    level=r.level,
                    tactics_detected=r.tactics_detected,
                    evidence=r.evidence,
                    is_likely_ai_generated=r.is_likely_ai_generated,
                    is_likely_coordinated=True,
                    summary=r.summary,
                    comment_hash=r.comment_hash,
                    model_used=r.model_used,
                    tokens_used=r.tokens_used,
                    cost_estimate=r.cost_estimate,
                    language=r.language,
                    ai_probability=r.ai_probability,
                    fomo_score=r.fomo_score,
                    fud_score=r.fud_score,
                    toxicity_score=r.toxicity_score,
                    account_risk=r.account_risk,
                    processing_time_ms=r.processing_time_ms,
                    stages_completed=r.stages_completed + ["coordination_flagged"],
                )
                for r in results
            ]

        if repetition > 0.5:
            for r in results:
                r.stages_completed.append("cross_thread_repetition")

        return results

    def get_cost_audit(self):
        return cost_auditor.audit()

    def get_cache_stats(self):
        return {
            "hit_rate": cost_auditor.get_cache_hit_rate(),
            "within_budget": cost_auditor.is_within_budget(),
        }
