from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from src.config import settings


@dataclass
class BotCluster:
    cluster_id: str
    account_ids: list[str] = field(default_factory=list)
    size: int = 0
    density: float = 0.0
    first_seen: str = ""
    last_seen: str = ""


class Neo4jClient:
    def __init__(self):
        self._driver = None

    async def connect(self) -> None:
        try:
            from neo4j import AsyncGraphDatabase
            self._driver = AsyncGraphDatabase.driver(
                settings.neo4j_url,
                auth=(settings.neo4j_user, settings.neo4j_password),
            )
            await self._driver.verify_connectivity()
        except Exception as e:
            raise RuntimeError(f"Failed to connect to Neo4j: {e}") from e

    async def close(self) -> None:
        if self._driver:
            await self._driver.close()
            self._driver = None

    async def create_or_update_account(
        self, account_id: str, platform: str, metadata: dict | None = None
    ) -> None:
        if not self._driver:
            return
        async with self._driver.session() as session:
            await session.run(
                """
                MERGE (a:Account {id: $account_id, platform: $platform})
                SET a += $metadata, a.updated_at = datetime()
                """,
                account_id=account_id,
                platform=platform,
                metadata=metadata or {},
            )

    async def link_comment_to_account(self, comment_id: str, account_id: str, text_hash: str) -> None:
        if not self._driver:
            return
        async with self._driver.session() as session:
            await session.run(
                """
                MATCH (a:Account {id: $account_id})
                MERGE (c:Comment {id: $comment_id})
                SET c.text_hash = $text_hash, c.created_at = COALESCE(c.created_at, datetime())
                MERGE (a)-[:POSTED]->(c)
                """,
                comment_id=comment_id,
                account_id=account_id,
                text_hash=text_hash,
            )

    async def find_bot_clusters(self, min_size: int = 5) -> list[BotCluster]:
        if not self._driver:
            return []
        async with self._driver.session() as session:
            result = await session.run(
                """
                MATCH (a:Account)-[r:FOLLOWS]-(b:Account)
                WITH a, collect(b) AS neighbors, count(b) AS degree
                WHERE degree >= $min_size - 1
                RETURN collect(DISTINCT a.id) AS account_ids, count(DISTINCT a) AS size
                LIMIT 10
                """,
                min_size=min_size,
            )
            clusters = []
            async for record in result:
                account_ids = record.get("account_ids", [])
                size = record.get("size", 0)
                if size >= min_size:
                    clusters.append(BotCluster(
                        cluster_id=f"cluster_{len(clusters)}",
                        account_ids=account_ids,
                        size=size,
                    ))
            return clusters

    async def add_to_campaign(self, comment_id: str, campaign_id: str) -> None:
        if not self._driver:
            return
        async with self._driver.session() as session:
            await session.run(
                """
                MATCH (c:Comment {id: $comment_id})
                MERGE (camp:Campaign {id: $campaign_id})
                MERGE (c)-[:PART_OF]->(camp)
                """,
                comment_id=comment_id,
                campaign_id=campaign_id,
            )

    async def get_account_graph_neighbors(self, account_id: str, depth: int = 2) -> list[str]:
        if not self._driver:
            return []
        async with self._driver.session() as session:
            result = await session.run(
                """
                MATCH (a:Account {id: $account_id})-[*1..$depth]-(neighbor:Account)
                RETURN DISTINCT neighbor.id AS neighbor_id
                """,
                account_id=account_id,
                depth=depth,
            )
            return [record["neighbor_id"] async for record in result]
