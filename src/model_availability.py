from __future__ import annotations

import importlib.util
from pathlib import Path


class ModelAvailability:
    _CHECKED: dict[str, bool] = {}

    @classmethod
    def check_transformers(cls) -> bool:
        return importlib.util.find_spec("transformers") is not None

    @classmethod
    def check_anthropic(cls) -> bool:
        return importlib.util.find_spec("anthropic") is not None

    @classmethod
    def check_openai(cls) -> bool:
        return importlib.util.find_spec("openai") is not None

    @classmethod
    def check_neo4j(cls) -> bool:
        return importlib.util.find_spec("neo4j") is not None

    @classmethod
    def check_redis(cls) -> bool:
        return importlib.util.find_spec("redis") is not None

    @classmethod
    def check_all(cls) -> dict[str, bool]:
        return {
            "transformers": cls.check_transformers(),
            "anthropic": cls.check_anthropic(),
            "openai": cls.check_openai(),
            "neo4j": cls.check_neo4j(),
            "redis": cls.check_redis(),
            "tiktoken": importlib.util.find_spec("tiktoken") is not None,
            "langdetect": importlib.util.find_spec("langdetect") is not None,
            "httpx": importlib.util.find_spec("httpx") is not None,
            "celery": importlib.util.find_spec("celery") is not None,
        }

    @classmethod
    def get_available_models(cls) -> list[dict[str, str]]:
        models = []
        hf_available = cls.check_transformers()
        models.append({
            "name": "roberta-base-openai-detector",
            "status": "available" if hf_available else "unavailable",
            "type": "ai_text_detection",
            "requires": "transformers",
        })
        models.append({
            "name": "Hello-SimpleAI/chatgpt-detector-roberta",
            "status": "available" if hf_available else "unavailable",
            "type": "ai_text_detection",
            "requires": "transformers",
        })
        models.append({
            "name": "cardiffnlp/twitter-roberta-base-sentiment-latest",
            "status": "available" if hf_available else "unavailable",
            "type": "sentiment",
            "requires": "transformers",
        })
        models.append({
            "name": "ProsusAI/finbert",
            "status": "available" if hf_available else "unavailable",
            "type": "financial_sentiment",
            "requires": "transformers",
        })
        models.append({
            "name": "martin-ha/toxic-comment-model",
            "status": "available" if hf_available else "unavailable",
            "type": "toxicity",
            "requires": "transformers",
        })
        models.append({
            "name": "facebook/bart-large-mnli",
            "status": "available" if hf_available else "unavailable",
            "type": "zero_shot",
            "requires": "transformers",
        })
        models.append({
            "name": "microsoft/mdeberta-v3-base",
            "status": "available" if hf_available else "unavailable",
            "type": "multilingual",
            "requires": "transformers",
        })
        models.append({
            "name": "claude-3-5-sonnet",
            "status": "available" if cls.check_anthropic() else "unavailable",
            "type": "llm_scoring",
            "requires": "anthropic",
        })
        models.append({
            "name": "gpt-4o-mini",
            "status": "available" if cls.check_openai() else "unavailable",
            "type": "llm_scoring",
            "requires": "openai",
        })

        return models


def get_readiness_report() -> dict:
    deps = ModelAvailability.check_all()
    models = ModelAvailability.get_available_models()
    available_models = [m for m in models if m["status"] == "available"]
    unavailable_models = [m for m in models if m["status"] != "available"]

    return {
        "all_deps_installed": all(deps.values()),
        "dependencies": deps,
        "models_available": len(available_models),
        "models_total": len(models),
        "available_models": available_models,
        "unavailable_models": unavailable_models,
        "can_run_inference": deps.get("transformers", False),
        "can_use_llm": deps.get("openai", False) or deps.get("anthropic", False),
        "can_use_graph": deps.get("neo4j", False),
        "can_use_queue": deps.get("celery", False),
    }
