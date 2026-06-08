from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class MultilingualResult:
    language: str
    confidence: float
    suggested_prompt_variant: str
    should_use_mdeberta: bool = False


class MultilingualHandler:
    LANG_CONFIG = {
        "en": {"prompt_variant": "master_v1", "use_mdeberta": False, "native_name": "English"},
        "vi": {"prompt_variant": "multilingual_v1", "use_mdeberta": True, "native_name": "Tiếng Việt"},
        "id": {"prompt_variant": "multilingual_v1", "use_mdeberta": True, "native_name": "Bahasa Indonesia"},
        "th": {"prompt_variant": "multilingual_v1", "use_mdeberta": True, "native_name": "ภาษาไทย"},
        "fil": {"prompt_variant": "multilingual_v1", "use_mdeberta": True, "native_name": "Filipino"},
        "zh": {"prompt_variant": "multilingual_v1", "use_mdeberta": True, "native_name": "中文"},
        "ja": {"prompt_variant": "multilingual_v1", "use_mdeberta": True, "native_name": "日本語"},
        "ko": {"prompt_variant": "multilingual_v1", "use_mdeberta": True, "native_name": "한국어"},
    }

    def __init__(self):
        self._classifier = None
        self._loaded = False

    def load(self) -> None:
        if self._loaded:
            return
        try:
            from transformers import pipeline
            self._classifier = pipeline(
                "text-classification",
                model="microsoft/mdeberta-v3-base",
            )
            self._loaded = True
        except Exception:
            pass

    def classify_language(self, text: str, detected_lang: str) -> MultilingualResult:
        config = self.LANG_CONFIG.get(detected_lang, self.LANG_CONFIG["en"])
        return MultilingualResult(
            language=detected_lang,
            confidence=0.9,
            suggested_prompt_variant=config["prompt_variant"],
            should_use_mdeberta=config["use_mdeberta"],
        )

    def detect_and_classify(self, text: str) -> MultilingualResult:
        try:
            from langdetect import detect
            lang = detect(text)
        except Exception:
            lang = "en"
        return self.classify_language(text, lang)

    @staticmethod
    def get_native_name(lang_code: str) -> str:
        return MultilingualHandler.LANG_CONFIG.get(lang_code, {}).get("native_name", lang_code)

    @staticmethod
    def get_supported_languages() -> list[str]:
        return list(MultilingualHandler.LANG_CONFIG.keys())
