from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from src.config import settings


class FewShotRefresher:
    def __init__(self):
        self._examples_dir = Path(__file__).parent.parent / "data" / "few_shot_examples"

    def add_example(
        self,
        language: str,
        text: str,
        category: str | None,
        tactic: str | None,
        manipulation_index: float,
        confidence: str,
        evidence_spans: list[dict],
        is_ai_generated: bool = False,
        is_coordinated: bool = False,
    ) -> bool:
        file_path = self._examples_dir / f"{language}_examples.json"
        if not file_path.exists():
            file_path = self._examples_dir / "en_examples.json"

        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, FileNotFoundError):
            return False

        examples = data if isinstance(data, list) else data.get("examples", [])

        text_hash = hashlib.sha256(text.encode()).hexdigest()
        for ex in examples:
            if hashlib.sha256(ex.get("text", "").encode()).hexdigest() == text_hash:
                ex["manipulation_index"] = manipulation_index
                ex["confidence"] = confidence
                ex["evidence_spans"] = evidence_spans
                ex["is_ai_generated"] = is_ai_generated
                ex["is_coordinated"] = is_coordinated
                ex["confirmed_at"] = datetime.now(timezone.utc).isoformat()
                self._write_examples(file_path, data, examples)
                return True

        new_example = {
            "language": language,
            "category": category,
            "tactic": tactic,
            "text": text,
            "manipulation_index": manipulation_index,
            "confidence": confidence,
            "evidence_spans": evidence_spans,
            "is_ai_generated": is_ai_generated,
            "is_coordinated": is_coordinated,
            "added_at": datetime.now(timezone.utc).isoformat(),
        }
        examples.append(new_example)
        self._write_examples(file_path, data, examples)
        return True

    def _write_examples(self, file_path: Path, original_data: dict | list, examples: list) -> None:
        if isinstance(original_data, list):
            output = examples
        else:
            output = {**original_data, "examples": examples}
        file_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")

    def get_example_count(self, language: str = "en") -> int:
        file_path = self._examples_dir / f"{language}_examples.json"
        if not file_path.exists():
            return 0
        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
            examples = data if isinstance(data, list) else data.get("examples", [])
            return len(examples)
        except (json.JSONDecodeError, FileNotFoundError):
            return 0

    def get_all_language_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for f in self._examples_dir.glob("*_examples.json"):
            lang = f.stem.replace("_examples", "")
            counts[lang] = self.get_example_count(lang)
        return counts

    def remove_stale_examples(self, before_date: str) -> int:
        removed = 0
        for f in self._examples_dir.glob("*_examples.json"):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                examples = data if isinstance(data, list) else data.get("examples", [])
                kept = [e for e in examples if e.get("added_at", "") >= before_date]
                removed += len(examples) - len(kept)
                if isinstance(data, list):
                    f.write_text(json.dumps(kept, indent=2, ensure_ascii=False), encoding="utf-8")
                else:
                    f.write_text(json.dumps({**data, "examples": kept}, indent=2, ensure_ascii=False), encoding="utf-8")
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        return removed


few_shot_refresher = FewShotRefresher()
