from __future__ import annotations

from dataclasses import dataclass, field

from src.config import settings


@dataclass
class AIDetectionResult:
    ai_probability: float = 0.0
    model_scores: dict[str, float] = field(default_factory=dict)
    heuristic_flags: list[str] = field(default_factory=list)
    should_skip_llm: bool = False


class AITextDetector:
    def __init__(self):
        self._roberta_detector = None
        self._chatgpt_detector = None
        self._loaded = False

    def load(self) -> None:
        if self._loaded:
            return
        try:
            from transformers import pipeline
            self._roberta_detector = pipeline(
                "text-classification",
                model="roberta-base-openai-detector",
            )
            self._chatgpt_detector = pipeline(
                "text-classification",
                model="Hello-SimpleAI/chatgpt-detector-roberta",
            )
            self._loaded = True
        except Exception as e:
            raise RuntimeError(f"Failed to load AI text detection models: {e}") from e

    def detect(self, text: str) -> AIDetectionResult:
        if not self._loaded:
            return AIDetectionResult()

        roberta_score = self._run_model(self._roberta_detector, text)
        chatgpt_score = self._run_model(self._chatgpt_detector, text)

        ai_probability = (roberta_score * 0.6) + (chatgpt_score * 0.4)

        heuristic_flags = self._run_heuristics(text)

        skip_llm = (
            ai_probability < settings.ai_skip_threshold
            and not self._has_fomo_fud_keywords(text)
        )

        return AIDetectionResult(
            ai_probability=round(ai_probability, 4),
            model_scores={
                "roberta_openai_detector": round(roberta_score, 4),
                "chatgpt_detector": round(chatgpt_score, 4),
            },
            heuristic_flags=heuristic_flags,
            should_skip_llm=skip_llm,
        )

    def _run_model(self, pipeline, text: str) -> float:
        try:
            result = pipeline(text, truncation=True, max_length=512)
            if result and isinstance(result, list):
                item = result[0]
                label = item.get("label", "").lower()
                score = item.get("score", 0.0)
                if "fake" in label or "ai" in label or "generated" in label:
                    return score
                return 1.0 - score
        except Exception:
            return 0.0
        return 0.0

    def _run_heuristics(self, text: str) -> list[str]:
        flags: list[str] = []
        text_lower = text.lower()

        hedging_phrases = [
            "it's important to note",
            "it's worth considering",
            "one might argue",
            "certainly",
            "absolutely",
            "i'd be happy to",
        ]
        for phrase in hedging_phrases:
            if phrase in text_lower:
                flags.append("HEDGING_LANGUAGE")
                break

        if "great question" in text_lower or "great point" in text_lower:
            flags.append("HOLLOW_AFFIRMATION")

        numbered_list_pattern = __import__("re").search(r"(?:^|\n)\s*\d+[\.\)]\s", text)
        if numbered_list_pattern:
            flags.append("TEMPLATE_STRUCTURE")

        sentences = [s.strip() for s in text.replace("!", ".").replace("?", ".").split(".") if s.strip()]
        if len(sentences) >= 3:
            lengths = [len(s.split()) for s in sentences]
            if lengths:
                avg = sum(lengths) / len(lengths)
                if avg > 0:
                    variance = sum((l - avg) ** 2 for l in lengths) / len(lengths)
                    if variance < 2.0 and avg > 8:
                        flags.append("UNIFORM_SENTENCE_LENGTH")

        return flags

    def _has_fomo_fud_keywords(self, text: str) -> bool:
        keywords = [
            "moonshot", "100x", "10x", "to the moon", "don't miss",
            "last chance", "whales are", "pump", "dump", "exit scam",
            "rug pull", "insider", "about to explode",
        ]
        text_lower = text.lower()
        return any(kw in text_lower for kw in keywords)
