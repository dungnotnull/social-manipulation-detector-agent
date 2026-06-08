from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class IntegrityCheck:
    table: str
    total_rows: int
    orphaned_rows: int = 0
    null_required_fields: list[str] = field(default_factory=list)
    duplicate_hashes: int = 0
    invalid_scores: int = 0
    passed: bool = True


@dataclass
class IntegrityReport:
    checks: list[IntegrityCheck] = field(default_factory=list)
    overall_passed: bool = True
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class DBIntegrityChecker:
    @staticmethod
    async def check_verdicts(session) -> IntegrityCheck:
        from sqlalchemy import select, func, text
        from src.api.models import Verdict

        result = await session.execute(select(func.count(Verdict.id)))
        total = result.scalar() or 0

        null_required = []
        required_fields = {
            "comment_hash": Verdict.comment_hash,
            "comment_text": Verdict.comment_text,
            "manipulation_index": Verdict.manipulation_index,
        }
        for name, col in required_fields.items():
            null_count = await session.scalar(
                select(func.count(Verdict.id)).where(col.is_(None))
            )
            if null_count and null_count > 0:
                null_required.append(name)

        dup_count = 0
        dup_result = await session.execute(
            select(Verdict.comment_hash, func.count(Verdict.id).label("cnt"))
            .group_by(Verdict.comment_hash)
            .having(func.count(Verdict.id) > 1)
        )
        duplicates = dup_result.all()
        if duplicates:
            dup_count = sum(r.cnt - 1 for r in duplicates)

        invalid_scores = 0
        invalid_result = await session.scalar(
            select(func.count(Verdict.id)).where(
                (Verdict.manipulation_index < 0) | (Verdict.manipulation_index > 1)
            )
        )
        if invalid_result:
            invalid_scores = invalid_result

        passed = not null_required and dup_count == 0 and invalid_scores == 0
        return IntegrityCheck(
            table="verdicts",
            total_rows=total,
            null_required_fields=null_required,
            duplicate_hashes=dup_count,
            invalid_scores=invalid_scores,
            passed=passed,
        )

    @staticmethod
    async def check_campaigns(session) -> IntegrityCheck:
        from sqlalchemy import select, func
        from src.api.models import Campaign

        result = await session.execute(select(func.count(Campaign.id)))
        total = result.scalar() or 0

        null_required = []
        for name, col in [("name", Campaign.name), ("platform", Campaign.platform)]:
            cnt = await session.scalar(
                select(func.count(Campaign.id)).where(col.is_(None))
            )
            if cnt and cnt > 0:
                null_required.append(name)

        passed = not null_required
        return IntegrityCheck(
            table="campaigns",
            total_rows=total,
            null_required_fields=null_required,
            passed=passed,
        )

    @staticmethod
    async def run_full_check(session) -> IntegrityReport:
        checks = [
            await DBIntegrityChecker.check_verdicts(session),
            await DBIntegrityChecker.check_campaigns(session),
        ]
        return IntegrityReport(
            checks=checks,
            overall_passed=all(c.passed for c in checks),
        )
