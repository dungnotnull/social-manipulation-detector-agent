from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from src.analyzer.llm_scorer import LLMScorer
from src.config import settings


@dataclass
class CostRecord:
    date: str
    model: str
    request_count: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0


@dataclass
class CostAudit:
    records: list[CostRecord] = field(default_factory=list)
    total_cost: float = 0.0
    cost_without_routing: float = 0.0
    savings_percent: float = 0.0
    mini_calls: int = 0
    sonnet_calls: int = 0
    cache_hits: int = 0
    cache_misses: int = 0


class CostAuditor:
    def __init__(self):
        self._records: dict[str, CostRecord] = {}
        self._mini_calls = 0
        self._sonnet_calls = 0
        self._cache_hits = 0
        self._cache_misses = 0

    def record_call(self, model: str, tokens: int, cost: float) -> None:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if today not in self._records:
            self._records[today] = CostRecord(date=today, model=model)
        record = self._records[today]
        record.request_count += 1
        record.total_tokens += tokens
        record.total_cost += cost
        if "mini" in model:
            self._mini_calls += 1
        elif "sonnet" in model or "claude" in model:
            self._sonnet_calls += 1

    def record_cache(self, hit: bool) -> None:
        if hit:
            self._cache_hits += 1
        else:
            self._cache_misses += 1

    def audit(self) -> CostAudit:
        total = sum(r.total_cost for r in self._records.values())
        total_tokens = sum(r.total_tokens for r in self._records.values())
        all_sonnet_cost = total_tokens / 1000 * 0.003
        savings = max(0.0, all_sonnet_cost - total)
        savings_pct = (savings / all_sonnet_cost * 100) if all_sonnet_cost > 0 else 0.0

        return CostAudit(
            records=list(self._records.values()),
            total_cost=round(total, 4),
            cost_without_routing=round(all_sonnet_cost, 4),
            savings_percent=round(savings_pct, 1),
            mini_calls=self._mini_calls,
            sonnet_calls=self._sonnet_calls,
            cache_hits=self._cache_hits,
            cache_misses=self._cache_misses,
        )

    def is_within_budget(self) -> bool:
        audit = self.audit()
        return audit.total_cost <= settings.llm_cost_budget_monthly_usd

    def get_cache_hit_rate(self) -> float:
        total = self._cache_hits + self._cache_misses
        return round(self._cache_hits / total, 4) if total > 0 else 0.0


cost_auditor = CostAuditor()
