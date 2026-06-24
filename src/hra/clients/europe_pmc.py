from __future__ import annotations

import os
import re
import time
from html import unescape
from html.parser import HTMLParser
from typing import Any

import httpx

from hra.models import Author, CorrectionNotice, Paper, SearchResponse
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
        cursor_mark: str = "*",
    ) -> SearchResponse:
        params = {
            "query": query,
            "format": "json",
            "pageSize": page_size,
            "resultType": "core",
            "cursorMark": cursor_mark,
        }
        headers = {"User-Agent": self._user_agent()}

        try:
            with httpx.Client(
                timeout=self.timeout,
                headers=headers,
                trust_env=self.trust_env,
            ) as client:
                data = self._get_json(client, f"{self.base_url}/search", params)
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
            next_cursor_mark=data.get("nextCursorMark"),
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
                    data = self._get_json(client, f"{self.base_url}/search", params)
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

    def _get_json(
        self,
        client: httpx.Client,
        url: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        for attempt in range(3):
            response = client.get(url, params=params)
            status_code = getattr(response, "status_code", 200)
            if status_code not in {429, 500, 502, 503, 504} or attempt == 2:
                response.raise_for_status()
                return response.json()
            time.sleep(0.5 * (attempt + 1))
        raise EuropePMCError("Europe PMC retry loop ended unexpectedly.")

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
        full_text_url, pdf_url = self._open_access_urls(item)
        return Paper(
            id=str(paper_id),
            title=_plain_text(item.get("title") or "Untitled"),
            authors=self._parse_authors(item),
            year=item.get("pubYear") or item.get("firstPublicationDate"),
            journal=item.get("journalTitle"),
            doi=item.get("doi"),
            pmid=item.get("pmid"),
            abstract=(
                _plain_text(item["abstractText"])
                if item.get("abstractText")
                else None
            ),
            source_url=source_url,
            open_access_full_text_url=full_text_url,
            open_access_pdf_url=pdf_url,
            citation_count=item.get("citedByCount"),
            is_open_access=item.get("isOpenAccess"),
            publication_types=self._parse_publication_types(item),
            correction_notices=self._parse_correction_notices(item),
        )

    def _open_access_urls(self, item: dict[str, Any]) -> tuple[str | None, str | None]:
        entries = item.get("fullTextUrlList", {}).get("fullTextUrl", [])
        if isinstance(entries, dict):
            entries = [entries]

        html_url: str | None = None
        pdf_url: str | None = None
        for entry in entries:
            if not isinstance(entry, dict) or entry.get("availabilityCode") != "OA":
                continue
            url = entry.get("url")
            if not url:
                continue
            style = str(entry.get("documentStyle", "")).lower()
            if style == "pdf" and pdf_url is None:
                pdf_url = str(url)
            elif style == "html" and html_url is None:
                html_url = str(url)
        return html_url, pdf_url

    def _parse_publication_types(self, item: dict[str, Any]) -> list[str]:
        values = item.get("pubTypeList", {}).get("pubType", [])
        if isinstance(values, str):
            values = [values]
        return [str(value).strip() for value in values if str(value).strip()]

    def _parse_correction_notices(
        self,
        item: dict[str, Any],
    ) -> list[CorrectionNotice]:
        values = item.get("commentCorrectionList", {}).get("commentCorrection", [])
        if isinstance(values, dict):
            values = [values]
        notices: list[CorrectionNotice] = []
        for value in values:
            if not isinstance(value, dict) or not value.get("type"):
                continue
            notices.append(
                CorrectionNotice(
                    id=str(value["id"]) if value.get("id") else None,
                    source=value.get("source"),
                    reference=value.get("reference"),
                    notice_type=str(value["type"]),
                )
            )
        return notices

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


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def _plain_text(value: str) -> str:
    parser = _TextExtractor()
    parser.feed(unescape(value))
    text = " ".join(" ".join(parser.parts).split()).strip()
    text = re.sub(r"\s+([,.;:!?)-])", r"\1", text)
    text = re.sub(r"([(])\s+", r"\1", text)
    for heading in ("Background", "Objective", "Methods", "Results", "Conclusions"):
        text = re.sub(
            rf"\b{heading}\s*(?=[A-Z])",
            f" {heading}: ",
            text,
        )
    return " ".join(text.split()).strip()
