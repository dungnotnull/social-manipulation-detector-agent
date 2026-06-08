from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from src.config import settings


@dataclass
class LLMScoreResult:
    manipulation_index: float = 0.0
    confidence: str = "LOW"
    tactics_detected: list[str] = field(default_factory=list)
    evidence: list[dict[str, str]] = field(default_factory=list)
    is_likely_ai_generated: bool = False
    is_likely_coordinated: bool = False
    summary: str = ""
    model_used: str = "none"
    tokens_used: int = 0
    cost_estimate: float = 0.0


class LLMScorer:
    _PROMPT_CACHE: dict[str, str] = {}

    def __init__(self):
        self._anthropic_client = None
        self._openai_client = None
        self._prompt_template = None

    @staticmethod
    def _make_default_result() -> LLMScoreResult:
        return LLMScoreResult(
            manipulation_index=0.0,
            confidence="LOW",
            tactics_detected=[],
            evidence=[],
            summary="LLM scoring skipped — text below AI detection threshold",
            model_used="skipped",
            tokens_used=0,
            cost_estimate=0.0,
        )

    def _get_prompt(self) -> str:
        if self._prompt_template is not None:
            return self._prompt_template

        prompt_path = Path(__file__).parent.parent.parent / "prompts" / "manipulation_scoring.md"
        if prompt_path.exists():
            self._prompt_template = prompt_path.read_text(encoding="utf-8")
        else:
            self._prompt_template = self._fallback_prompt()
        return self._prompt_template

    def _ensure_clients(self) -> None:
        if settings.anthropic_api_key and not self._anthropic_client:
            try:
                from anthropic import Anthropic
                self._anthropic_client = Anthropic(api_key=settings.anthropic_api_key)
            except Exception:
                pass

        if settings.openai_api_key and not self._openai_client:
            try:
                from openai import OpenAI
                self._openai_client = OpenAI(api_key=settings.openai_api_key)
            except Exception:
                pass

    def score(
        self,
        text: str,
        thread_context: list[str] | None = None,
    ) -> LLMScoreResult:
        self._ensure_clients()

        if not self._openai_client and not self._anthropic_client:
            return LLMScoreResult(
                summary="No LLM API keys configured. Set ANTHROPIC_API_KEY or OPENAI_API_KEY.",
                model_used="none",
            )

        prompt = self._get_prompt().replace("{input_text}", text)
        ctx = "\n".join(thread_context) if thread_context else "No thread context available."
        prompt = prompt.replace("{thread_context}", ctx)

        result = self._call_mini(prompt)

        if result.manipulation_index > settings.llm_escalation_threshold:
            sonnet_result = self._call_sonnet(prompt)
            if sonnet_result.manipulation_index > 0:
                return sonnet_result

        return result

    def _call_mini(self, prompt: str) -> LLMScoreResult:
        if not self._openai_client:
            return LLMScoreResult(model_used="none")
        try:
            import tiktoken
            enc = tiktoken.get_encoding("cl100k_base")
            token_count = len(enc.encode(prompt))
        except Exception:
            token_count = len(prompt.split()) * 2

        try:
            response = self._openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a computational social science expert. Respond only with valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=settings.llm_default_temperature,
                max_tokens=1024,
            )
            content = response.choices[0].message.content or ""
            return self._parse_response(content, "gpt-4o-mini", token_count)
        except Exception:
            return LLMScoreResult(model_used="gpt-4o-mini", tokens_used=token_count)

    def _call_sonnet(self, prompt: str) -> LLMScoreResult:
        if not self._anthropic_client:
            return LLMScoreResult(model_used="none")
        try:
            import tiktoken
            enc = tiktoken.get_encoding("cl100k_base")
            token_count = len(enc.encode(prompt))
        except Exception:
            token_count = len(prompt.split()) * 2

        try:
            response = self._anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                temperature=settings.llm_default_temperature,
                system="You are a computational social science expert. Respond only with valid JSON.",
                messages=[{"role": "user", "content": prompt}],
            )
            content = response.content[0].text if response.content else ""
            return self._parse_response(content, "claude-3.5-sonnet", token_count)
        except Exception:
            return LLMScoreResult(model_used="claude-3.5-sonnet", tokens_used=token_count)

    def _parse_response(self, content: str, model: str, tokens: int) -> LLMScoreResult:
        import json
        try:
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            data = json.loads(content.strip())
        except (json.JSONDecodeError, IndexError):
            return LLMScoreResult(model_used=model, tokens_used=tokens)

        cost_per_1k = 0.00015 if "mini" in model else 0.003
        cost = (tokens / 1000) * cost_per_1k

        return LLMScoreResult(
            manipulation_index=data.get("manipulation_index", 0.0),
            confidence=data.get("confidence", "LOW"),
            tactics_detected=data.get("tactics_detected", []),
            evidence=data.get("evidence", []),
            is_likely_ai_generated=data.get("is_likely_ai_generated", False),
            is_likely_coordinated=data.get("is_likely_coordinated", False),
            summary=data.get("summary", ""),
            model_used=model,
            tokens_used=tokens,
            cost_estimate=round(cost, 6),
        )

    @staticmethod
    def _fallback_prompt() -> str:
        return """[SYSTEM]
You are a computational social science expert. Analyze the text for manipulation tactics.

Rules:
- Score TACTICS only, never political positions
- Most human comments score < 0.3
- Cite specific text spans as evidence

Output JSON:
{
  "manipulation_index": float (0.0-1.0),
  "confidence": "HIGH|MEDIUM|LOW",
  "tactics_detected": ["TACTIC", ...],
  "evidence": [{"tactic": "...", "span": "...", "explanation": "..."}],
  "is_likely_ai_generated": bool,
  "is_likely_coordinated": bool,
  "summary": "1-2 sentence verdict"
}

Text: {input_text}
Thread context: {thread_context}
"""
