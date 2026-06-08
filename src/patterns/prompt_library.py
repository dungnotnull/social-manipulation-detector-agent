from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts"
EXAMPLES_DIR = Path(__file__).parent.parent.parent / "data" / "few_shot_examples"


class PromptLibrary:
    @staticmethod
    @lru_cache(maxsize=8)
    def load_prompt(template_name: str) -> str:
        prompt_path = PROMPTS_DIR / f"{template_name}.md"
        if prompt_path.exists():
            return prompt_path.read_text(encoding="utf-8")
        return ""

    @staticmethod
    def build_few_shot_prompt(
        tactic_category: str | None = None,
        language: str = "en",
        num_examples: int = 5,
    ) -> str:
        base_prompt = PromptLibrary.load_prompt("manipulation_scoring")
        if not base_prompt:
            return ""

        examples = PromptLibrary.load_examples(language, tactic_category)
        selected = examples[:num_examples]

        example_text = ""
        for ex in selected:
            example_text += f"---\nComment: \"{ex['text']}\"\n"
            example_text += f"Analysis:\n"
            for evidence in ex.get("evidence_spans", []):
                example_text += f"- [{evidence.get('tactic', '')}]: \"{evidence.get('span', '')}\" — {evidence.get('explanation', '')}\n"
            example_text += f"Tactics detected: {len(ex.get('evidence_spans', []))} | "
            example_text += f"Manipulation Index: {ex.get('manipulation_index', 0.0)} | "
            example_text += f"Confidence: {ex.get('confidence', 'LOW')}\n"

        return base_prompt.replace("{examples}", example_text)

    @staticmethod
    @lru_cache(maxsize=16)
    def load_examples(language: str = "en", tactic: str | None = None) -> list[dict]:
        file_path = EXAMPLES_DIR / f"{language}_examples.json"
        if not file_path.exists():
            return _fallback_examples()

        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
            examples = data if isinstance(data, list) else data.get("examples", [])
        except (json.JSONDecodeError, FileNotFoundError):
            return _fallback_examples()

        if tactic:
            examples = [e for e in examples if e.get("tactic") == tactic or e.get("category") == tactic]

        return examples


@lru_cache(maxsize=1)
def _fallback_examples() -> list[dict]:
    return [
        {
            "language": "en",
            "category": "C",
            "tactic": "FOMO_PUMP",
            "text": "🚀🚀 This token is about to EXPLODE! Whales are accumulating RIGHT NOW! Don't be the last one holding fiat when this 10x's by Friday!",
            "manipulation_index": 0.93,
            "confidence": "HIGH",
            "evidence_spans": [
                {"tactic": "FOMO_PUMP", "span": "about to EXPLODE", "explanation": "Price prediction + urgency"},
                {"tactic": "SOCIAL_PROOF", "span": "Whales are accumulating", "explanation": "Manufactured authority/consensus"},
                {"tactic": "URGENCY_SCARCITY", "span": "Don't be the last one", "explanation": "Explicit FOMO trigger"},
            ],
            "is_ai_generated": False,
            "is_coordinated": False,
        },
        {
            "language": "en",
            "category": "A",
            "tactic": "SOCIAL_PROOF",
            "text": "Everyone is switching to this platform. 100k people joined just this week. You're missing out if you're still using the old one.",
            "manipulation_index": 0.78,
            "confidence": "HIGH",
            "evidence_spans": [
                {"tactic": "SOCIAL_PROOF", "span": "Everyone is switching", "explanation": "Manufactured consensus claim"},
                {"tactic": "SOCIAL_PROOF", "span": "100k people joined", "explanation": "Unverifiable statistic for social proof"},
            ],
            "is_ai_generated": False,
            "is_coordinated": False,
        },
        {
            "language": "en",
            "category": "E",
            "tactic": "LLM_HOLLOW_AFFIRMATION",
            "text": "Absolutely! You've raised such an important point. It's crucial that we consider all perspectives. There are several key factors: 1) The economic implications, 2) The social impact, 3) The long-term sustainability.",
            "manipulation_index": 0.71,
            "confidence": "MEDIUM",
            "evidence_spans": [
                {"tactic": "LLM_HOLLOW_AFFIRMATION", "span": "Absolutely! You've raised such an important point", "explanation": "Excessive agreement without substance"},
                {"tactic": "LLM_TEMPLATE_STRUCTURE", "span": "1) The economic implications, 2)...", "explanation": "Numbered list in casual social context"},
            ],
            "is_ai_generated": True,
            "is_coordinated": False,
        },
        {
            "language": "en",
            "category": "D",
            "tactic": "EMOTIONAL_HIJACKING",
            "text": "This is OUTRAGEOUS! They're literally destroying everything we care about! SHARE THIS before it gets taken down!",
            "manipulation_index": 0.65,
            "confidence": "MEDIUM",
            "evidence_spans": [
                {"tactic": "EMOTIONAL_HIJACKING", "span": "OUTRAGEOUS! They're literally destroying everything", "explanation": "Extreme emotional language to bypass critical thinking"},
                {"tactic": "URGENCY_SCARCITY", "span": "before it gets taken down", "explanation": "Artificial urgency for sharing"},
            ],
            "is_ai_generated": False,
            "is_coordinated": False,
        },
        {
            "language": "en",
            "category": None,
            "tactic": None,
            "text": "I disagree with this policy because it historically hasn't worked in similar contexts.",
            "manipulation_index": 0.04,
            "confidence": "HIGH",
            "evidence_spans": [],
            "is_ai_generated": False,
            "is_coordinated": False,
        },
    ]
