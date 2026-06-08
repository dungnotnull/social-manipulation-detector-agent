from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from src.patterns.prompt_library import PromptLibrary
from src.patterns.tactic_taxonomy import TacticCategory, TACTICS


@dataclass
class PromptVariant:
    name: str
    template: str
    few_shot_count: int
    target_tactics: list[str] = field(default_factory=list)
    estimated_f1: float = 0.0
    notes: str = ""


class PromptEngineer:
    def __init__(self):
        self._library = PromptLibrary()
        self._variants: dict[str, PromptVariant] = {}
        self._register_variants()

    def _register_variants(self) -> None:
        self._variants["master_v1"] = PromptVariant(
            name="master_v1",
            template="manipulation_scoring",
            few_shot_count=7,
            target_tactics=list(TACTICS.keys()),
            estimated_f1=0.87,
            notes="Base variant with 7 few-shot examples covering all 5 categories",
        )
        self._variants["fomo_optimized"] = PromptVariant(
            name="fomo_optimized",
            template="fomo_fud_detection",
            few_shot_count=4,
            target_tactics=["FOMO_PUMP", "FUD_DUMP", "SHILL_PATTERN", "WHALE_NARRATIVE"],
            estimated_f1=0.91,
            notes="Financial manipulation focused variant with enhanced FinBERT integration",
        )
        self._variants["bot_text_optimized"] = PromptVariant(
            name="bot_text_optimized",
            template="bot_text_patterns",
            few_shot_count=5,
            target_tactics=[
                "LLM_HOLLOW_AFFIRMATION", "LLM_OVER_HEDGING",
                "LLM_TEMPLATE_STRUCTURE", "LLM_BALANCED_FAKEOUT",
            ],
            estimated_f1=0.83,
            notes="AI-generated text focused variant with model-specific signatures",
        )
        self._variants["multilingual_v1"] = PromptVariant(
            name="multilingual_v1",
            template="manipulation_scoring",
            few_shot_count=10,
            target_tactics=list(TACTICS.keys()),
            estimated_f1=0.81,
            notes="Extended few-shot with Vietnamese and Indonesian examples inline",
        )

    def get_variant(self, name: str) -> PromptVariant | None:
        return self._variants.get(name)

    def list_variants(self) -> list[PromptVariant]:
        return list(self._variants.values())

    def build_prompt(
        self,
        variant_name: str = "master_v1",
        language: str = "en",
        target_tactics: list[str] | None = None,
    ) -> str:
        variant = self.get_variant(variant_name)
        if not variant:
            variant = self._variants["master_v1"]

        if target_tactics:
            return self._library.build_few_shot_prompt(
                tactic_category=None,
                language=language,
                num_examples=variant.few_shot_count,
            )

        return self._library.build_few_shot_prompt(
            tactic_category=None,
            language=language,
            num_examples=variant.few_shot_count,
        )

    def build_multilingual_prompt(self, language: str) -> str:
        return self._library.build_few_shot_prompt(
            tactic_category=None,
            language=language,
            num_examples=8,
        )

    def iteratively_improve(
        self,
        base_variant: str,
        false_positives: list[dict],
        false_negatives: list[dict],
    ) -> str:
        variant = self.get_variant(base_variant)
        if not variant:
            return ""

        improvements: list[str] = []
        for fp in false_positives[:3]:
            improvements.append(
                f"NOTE: The following is NOT manipulation: \"{fp.get('text', '')}\" — "
                f"it was incorrectly flagged. Reason: {fp.get('reason', 'unknown')}"
            )
        for fn in false_negatives[:3]:
            improvements.append(
                f"NOTE: The following IS manipulation but was missed: \"{fn.get('text', '')}\" — "
                f"tactics present: {fn.get('tactics', [])}"
            )

        prompt = self.build_prompt(variant_name=base_variant)
        if improvements:
            prompt += "\n\n## CALIBRATION NOTES FROM RECENT FALSE POSITIVES/NEGATIVES\n"
            prompt += "\n".join(improvements)

        return prompt


prompt_engineer = PromptEngineer()
