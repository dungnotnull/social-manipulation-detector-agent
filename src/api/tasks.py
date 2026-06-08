from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from celery import shared_task

from src.analyzer.pipeline_orchestrator import PipelineOrchestrator


_orchestrator = PipelineOrchestrator()


def _hash_text(text: str) -> str:
    import hashlib
    return hashlib.sha256(text.encode()).hexdigest()


def run_pipeline_sync(
    text: str,
    platform: str = "unknown",
    thread_context: list[str] | None = None,
) -> dict[str, Any]:
    """Run the full analysis pipeline synchronously. Safe to call from routes or Celery."""
    result = _orchestrator.analyze_single(
        text,
        platform=platform,
        thread_context=thread_context,
    )
    output = _pipeline_result_to_dict(result)
    output["comment_hash"] = _hash_text(text)
    return output


def run_thread_pipeline_sync(
    comments: list[dict[str, Any]],
    platform: str = "unknown",
) -> dict[str, Any]:
    """Run batch analysis synchronously on a thread of comments."""
    texts = [c["text"] for c in comments]
    verdicts: list[dict[str, Any]] = []
    for comment in comments:
        thread_context = [t for t in texts if t != comment["text"]]
        result = _orchestrator.analyze_single(
            comment["text"],
            platform=platform,
            thread_context=thread_context,
        )
        output = _pipeline_result_to_dict(result)
        output["comment_hash"] = _hash_text(comment["text"])
        verdicts.append(output)

    aggregate = 0.0
    if verdicts:
        aggregate = sum(v.get("manipulation_index", 0) for v in verdicts) / len(verdicts)

    return {
        "thread_id": comments[0].get("thread_id", ""),
        "platform": platform,
        "verdicts": verdicts,
        "aggregate_score": round(aggregate, 4),
    }


def _pipeline_result_to_dict(result) -> dict[str, Any]:
    return {
        "manipulation_index": result.manipulation_index,
        "confidence": result.confidence,
        "level": result.level,
        "tactics_detected": result.tactics_detected,
        "evidence": result.evidence,
        "is_likely_ai_generated": result.is_likely_ai_generated,
        "is_likely_coordinated": result.is_likely_coordinated,
        "summary": result.summary,
        "comment_hash": result.comment_hash,
        "model_used": result.model_used,
        "tokens_used": result.tokens_used,
        "cost_estimate": result.cost_estimate,
        "language": result.language,
        "ai_probability": result.ai_probability,
        "fomo_score": result.fomo_score,
        "fud_score": result.fud_score,
        "toxicity_score": result.toxicity_score,
        "account_risk": result.account_risk,
        "processing_time_ms": result.processing_time_ms,
        "stages_completed": result.stages_completed,
    }


@shared_task(bind=True, max_retries=2)
def analyze_text_task(
    self,
    text: str,
    platform: str = "unknown",
    thread_id: str = "",
    author_id: str = "",
    thread_context: list[str] | None = None,
) -> dict[str, Any]:
    return run_pipeline_sync(text, platform=platform, thread_context=thread_context)


@shared_task(bind=True, max_retries=2)
def analyze_thread_task(
    self,
    comments: list[dict[str, Any]],
    platform: str = "unknown",
) -> dict[str, Any]:
    return run_thread_pipeline_sync(comments, platform=platform)
