from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

from src.config import settings


@dataclass
class PaperSummary:
    title: str
    source: str
    url: str
    abstract: str
    authors: list[str] = field(default_factory=list)
    published_date: str = ""
    key_findings: list[str] = field(default_factory=list)
    extracted_tactics: list[dict] = field(default_factory=list)


@dataclass
class ExtractedTactic:
    name: str
    category: str
    description: str
    source_paper: str
    confidence: str = "MEDIUM"


class ResearchCrawler:
    def __init__(self):
        self._anthropic_client = None

    def _ensure_summarizer(self) -> None:
        if settings.anthropic_api_key and not self._anthropic_client:
            try:
                from anthropic import Anthropic
                self._anthropic_client = Anthropic(api_key=settings.anthropic_api_key)
            except Exception:
                pass

    def crawl_arxiv(self, topics: list[str], max_papers: int = 50) -> list[PaperSummary]:
        if not settings.arxiv_search_enabled:
            return []

        papers: list[PaperSummary] = []
        try:
            query = "+OR+".join(t.replace(" ", "+") for t in topics)
            url = (
                f"http://export.arxiv.org/api/query?search_query=all:{query}"
                f"&start=0&max_results={min(max_papers, 50)}&sortBy=relevance"
            )
            import urllib.request
            import xml.etree.ElementTree as ET

            req = urllib.request.Request(url, headers={"User-Agent": "SMDA-Research-Crawler/0.1"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read().decode("utf-8")

            ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
            root = ET.fromstring(data)

            for entry in root.findall("atom:entry", ns):
                title = entry.find("atom:title", ns)
                summary = entry.find("atom:summary", ns)
                link = entry.find("atom:id", ns)
                published = entry.find("atom:published", ns)

                papers.append(PaperSummary(
                    title=title.text.strip() if title is not None and title.text else "Untitled",
                    source="arxiv",
                    url=link.text.strip() if link is not None and link.text else "",
                    abstract=summary.text.strip()[:2000] if summary is not None and summary.text else "",
                    authors=[],
                    published_date=published.text.strip()[:10] if published is not None and published.text else "",
                ))

        except Exception:
            pass

        return papers

    def crawl_semantic_scholar(self, topics: list[str], max_papers: int = 30) -> list[PaperSummary]:
        if not settings.semantic_scholar_api_key:
            return []

        papers: list[PaperSummary] = []
        try:
            import httpx
            for topic in topics[:3]:
                response = httpx.get(
                    "https://api.semanticscholar.org/graph/v1/paper/search",
                    params={
                        "query": topic,
                        "limit": min(max_papers // 3, 10),
                        "fields": "title,abstract,authors,year,url",
                    },
                    headers={"x-api-key": settings.semantic_scholar_api_key},
                    timeout=15,
                )
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get("data", []):
                        authors = [a.get("name", "") for a in item.get("authors", [])]
                        papers.append(PaperSummary(
                            title=item.get("title", "Untitled"),
                            source="semantic_scholar",
                            url=item.get("url", ""),
                            abstract=item.get("abstract", "")[:2000] if item.get("abstract") else "",
                            authors=authors,
                            published_date=str(item.get("year", "")),
                        ))
        except Exception:
            pass

        return papers

    def summarize_paper(self, paper: PaperSummary) -> str:
        self._ensure_summarizer()
        if not self._anthropic_client or not paper.abstract:
            return ""

        try:
            response = self._anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                temperature=0,
                system="Summarize this research paper abstract in 3 bullet points. Focus on: new manipulation tactics, LLM text detection methods, or bot coordination patterns relevant to social media manipulation detection.",
                messages=[{
                    "role": "user",
                    "content": f"Title: {paper.title}\n\nAbstract: {paper.abstract}",
                }],
            )
            return response.content[0].text if response.content else ""
        except Exception:
            return ""

    def extract_tactics(self, summary: str) -> list[ExtractedTactic]:
        if not summary:
            return []
        return []

    def run_weekly_crawl(
        self,
        topics: list[str] | None = None,
        output_dir: Path | None = None,
    ) -> int:
        if topics is None:
            topics = [
                "disinformation detection",
                "bot detection NLP",
                "LLM text detection",
                "coordinated inauthentic behavior",
                "FOMO manipulation crypto",
                "astroturfing social media",
            ]

        if output_dir is None:
            today = date.today().isoformat()
            output_dir = Path(__file__).parent.parent.parent / "data" / "research_cache" / today

        output_dir.mkdir(parents=True, exist_ok=True)

        all_papers: list[PaperSummary] = []
        all_papers.extend(self.crawl_arxiv(topics))
        all_papers.extend(self.crawl_semantic_scholar(topics))

        for i, paper in enumerate(all_papers):
            summary_text = self.summarize_paper(paper)
            paper.key_findings = [line.strip("- ") for line in summary_text.split("\n") if line.strip().startswith("-")]

        output_path = output_dir / "papers.json"
        output_path.write_text(
            json.dumps(
                [
                    {
                        "title": p.title,
                        "source": p.source,
                        "url": p.url,
                        "abstract": p.abstract,
                        "authors": p.authors,
                        "key_findings": p.key_findings,
                        "extracted_tactics": p.extracted_tactics,
                        "published_date": p.published_date,
                    }
                    for p in all_papers
                ],
                indent=2,
                default=str,
            ),
            encoding="utf-8",
        )

        return len(all_papers)
