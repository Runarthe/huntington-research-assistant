from __future__ import annotations

import os
from typing import Any

import httpx

from hra.models import Author, Paper, SearchResponse
from hra.tagging import tag_papers


class EuropePMCError(RuntimeError):
    """Raised when Europe PMC cannot return a usable response."""


class EuropePMCClient:
    """Client for the official Europe PMC RESTful Web Service."""

    BASE_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest"

    def __init__(
        self,
        base_url: str = BASE_URL,
        timeout: float = 20.0,
        email: str | None = None,
        trust_env: bool | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.email = email or os.getenv("HRA_EUROPE_PMC_EMAIL")
        self.trust_env = trust_env if trust_env is not None else _env_flag("HRA_TRUST_ENV")

    def search(
        self,
        query: str,
        page: int = 1,
        page_size: int = 10,
    ) -> SearchResponse:
        params = {
            "query": query,
            "format": "json",
            "page": page,
            "pageSize": page_size,
            "resultType": "core",
        }
        headers = {"User-Agent": self._user_agent()}

        try:
            with httpx.Client(
                timeout=self.timeout,
                headers=headers,
                trust_env=self.trust_env,
            ) as client:
                response = client.get(f"{self.base_url}/search", params=params)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as exc:
            raise EuropePMCError(f"Europe PMC request failed: {exc}") from exc
        except ValueError as exc:
            raise EuropePMCError("Europe PMC returned invalid JSON.") from exc

        result_list = data.get("resultList", {}).get("result", [])
        papers = tag_papers([self._parse_paper(item) for item in result_list])
        return SearchResponse(
            query=query,
            page=page,
            page_size=page_size,
            total_results=self._safe_int(data.get("hitCount")),
            papers=papers,
        )

    def count_by_year(
        self,
        query: str,
        start_year: int,
        end_year: int,
    ) -> list[dict[str, int]]:
        """Return exact Europe PMC hit counts for each publication year."""

        headers = {"User-Agent": self._user_agent()}
        counts: list[dict[str, int]] = []
        try:
            with httpx.Client(
                timeout=self.timeout,
                headers=headers,
                trust_env=self.trust_env,
            ) as client:
                for year in range(start_year, end_year + 1):
                    params = {
                        "query": f"({query}) AND PUB_YEAR:{year}",
                        "format": "json",
                        "pageSize": 1,
                        "resultType": "lite",
                    }
                    response = client.get(f"{self.base_url}/search", params=params)
                    response.raise_for_status()
                    data = response.json()
                    counts.append(
                        {
                            "year": year,
                            "papers": self._safe_int(data.get("hitCount")) or 0,
                        }
                    )
        except httpx.HTTPError as exc:
            raise EuropePMCError(f"Europe PMC analytics request failed: {exc}") from exc
        except ValueError as exc:
            raise EuropePMCError("Europe PMC returned invalid analytics JSON.") from exc
        return counts

    def _user_agent(self) -> str:
        contact = f" ({self.email})" if self.email else ""
        return f"huntington-research-assistant/0.1{contact}"

    def _parse_paper(self, item: dict[str, Any]) -> Paper:
        paper_id = (
            item.get("id")
            or item.get("pmid")
            or item.get("doi")
            or item.get("title")
            or "unknown"
        )
        source_url = self._source_url(item)
        return Paper(
            id=str(paper_id),
            title=item.get("title") or "Untitled",
            authors=self._parse_authors(item),
            year=item.get("pubYear") or item.get("firstPublicationDate"),
            journal=item.get("journalTitle"),
            doi=item.get("doi"),
            pmid=item.get("pmid"),
            abstract=item.get("abstractText"),
            source_url=source_url,
            citation_count=item.get("citedByCount"),
            is_open_access=item.get("isOpenAccess"),
        )

    def _parse_authors(self, item: dict[str, Any]) -> list[Author]:
        author_string = item.get("authorString")
        if author_string:
            names = [
                name.strip().rstrip(".")
                for name in author_string.split(",")
                if name.strip()
            ]
            return [Author(full_name=name) for name in names]

        authors = item.get("authorList", {}).get("author", [])
        parsed: list[Author] = []
        for author in authors:
            name = author.get("fullName") or author.get("lastName")
            if name:
                parsed.append(Author(full_name=name))
        return parsed

    def _source_url(self, item: dict[str, Any]) -> str:
        if item.get("pmid"):
            return f"https://europepmc.org/article/MED/{item['pmid']}"
        source = item.get("source")
        item_id = item.get("id")
        if source and item_id:
            return f"https://europepmc.org/article/{source}/{item_id}"
        if item.get("doi"):
            return f"https://doi.org/{item['doi']}"
        return "https://europepmc.org/"

    def _safe_int(self, value: Any) -> int | None:
        if value in (None, ""):
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None


def _env_flag(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}
