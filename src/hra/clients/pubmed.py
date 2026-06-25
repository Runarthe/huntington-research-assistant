from __future__ import annotations

import os
import time
import xml.etree.ElementTree as ET
from typing import Any

import httpx

from hra.clients.europe_pmc import _plain_text
from hra.models import Author, Paper, SearchResponse
from hra.tagging import tag_papers


class PubMedError(RuntimeError):
    """Raised when NCBI E-utilities cannot return a usable PubMed response."""


class PubMedClient:
    """Client for the official NCBI E-utilities PubMed API."""

    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    def __init__(
        self,
        base_url: str = BASE_URL,
        timeout: float = 20.0,
        email: str | None = None,
        api_key: str | None = None,
        trust_env: bool | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.email = email or os.getenv("HRA_NCBI_EMAIL")
        self.api_key = api_key or os.getenv("HRA_NCBI_API_KEY")
        self.trust_env = trust_env if trust_env is not None else _env_flag("HRA_TRUST_ENV")

    def search(self, query: str, page: int = 1, page_size: int = 10) -> SearchResponse:
        start = max(0, (page - 1) * page_size)
        headers = {"User-Agent": self._user_agent()}
        try:
            with httpx.Client(
                timeout=self.timeout,
                headers=headers,
                trust_env=self.trust_env,
            ) as client:
                search_data = self._get_json(
                    client,
                    f"{self.base_url}/esearch.fcgi",
                    {
                        **self._base_params(),
                        "db": "pubmed",
                        "term": query,
                        "retmode": "json",
                        "retstart": start,
                        "retmax": page_size,
                        "sort": "pub date",
                    },
                )
                id_list = search_data.get("esearchresult", {}).get("idlist", [])
                papers = self._fetch_papers(client, id_list) if id_list else []
        except httpx.HTTPError as exc:
            raise PubMedError(f"PubMed request failed: {exc}") from exc
        except (ET.ParseError, ValueError) as exc:
            raise PubMedError("PubMed returned an invalid response.") from exc

        count = search_data.get("esearchresult", {}).get("count")
        return SearchResponse(
            query=query,
            page=page,
            page_size=page_size,
            total_results=_safe_int(count),
            papers=tag_papers(papers),
        )

    def _fetch_papers(self, client: httpx.Client, pmids: list[str]) -> list[Paper]:
        xml_text = self._get_text(
            client,
            f"{self.base_url}/efetch.fcgi",
            {
                **self._base_params(),
                "db": "pubmed",
                "id": ",".join(pmids),
                "retmode": "xml",
            },
        )
        root = ET.fromstring(xml_text)
        return [
            self._parse_article(article)
            for article in root.findall(".//PubmedArticle")
        ]

    def _get_json(
        self,
        client: httpx.Client,
        url: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        response = self._get_response(client, url, params)
        return response.json()

    def _get_text(
        self,
        client: httpx.Client,
        url: str,
        params: dict[str, Any],
    ) -> str:
        return self._get_response(client, url, params).text

    def _get_response(
        self,
        client: httpx.Client,
        url: str,
        params: dict[str, Any],
    ) -> httpx.Response:
        for attempt in range(3):
            response = client.get(url, params=params)
            status_code = getattr(response, "status_code", 200)
            if status_code not in {429, 500, 502, 503, 504} or attempt == 2:
                response.raise_for_status()
                return response
            time.sleep(0.5 * (attempt + 1))
        raise PubMedError("PubMed retry loop ended unexpectedly.")

    def _base_params(self) -> dict[str, str]:
        params = {"tool": "huntington-research-assistant"}
        if self.email:
            params["email"] = self.email
        if self.api_key:
            params["api_key"] = self.api_key
        return params

    def _user_agent(self) -> str:
        contact = f" ({self.email})" if self.email else ""
        return f"huntington-research-assistant/0.3{contact}"

    def _parse_article(self, article: ET.Element) -> Paper:
        medline = article.find("MedlineCitation")
        pubmed_data = article.find("PubmedData")
        pmid = _text(medline, "PMID") if medline is not None else None
        article_node = medline.find("Article") if medline is not None else None

        return Paper(
            id=f"pubmed:{pmid}" if pmid else "pubmed:unknown",
            source_provider="PubMed",
            title=_plain_text(_text(article_node, "ArticleTitle") or "Untitled"),
            authors=_authors(article_node),
            year=_publication_year(article_node),
            journal=_text(article_node, "Journal/Title"),
            doi=_article_id(pubmed_data, "doi"),
            pmid=pmid,
            abstract=_abstract(article_node),
            source_url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else None,
            publication_types=_publication_types(article_node),
        )


def _authors(article: ET.Element | None) -> list[Author]:
    if article is None:
        return []
    authors: list[Author] = []
    for author in article.findall("AuthorList/Author"):
        collective = _text(author, "CollectiveName")
        if collective:
            authors.append(Author(full_name=collective))
            continue
        last_name = _text(author, "LastName")
        fore_name = _text(author, "ForeName") or _text(author, "Initials")
        name = " ".join(part for part in (fore_name, last_name) if part)
        if name:
            authors.append(Author(full_name=name))
    return authors


def _publication_year(article: ET.Element | None) -> int | None:
    if article is None:
        return None
    candidates = [
        _text(article, "ArticleDate/Year"),
        _text(article, "Journal/JournalIssue/PubDate/Year"),
        _text(article, "Journal/JournalIssue/PubDate/MedlineDate"),
    ]
    for candidate in candidates:
        year = _safe_int(str(candidate)[:4]) if candidate else None
        if year:
            return year
    return None


def _abstract(article: ET.Element | None) -> str | None:
    if article is None:
        return None
    parts: list[str] = []
    for abstract_text in article.findall("Abstract/AbstractText"):
        text = _element_text(abstract_text)
        if not text:
            continue
        label = abstract_text.attrib.get("Label")
        parts.append(f"{label}: {text}" if label else text)
    abstract = " ".join(parts).strip()
    return _plain_text(abstract) if abstract else None


def _publication_types(article: ET.Element | None) -> list[str]:
    if article is None:
        return []
    return [
        value
        for item in article.findall("PublicationTypeList/PublicationType")
        if (value := _element_text(item))
    ]


def _article_id(pubmed_data: ET.Element | None, id_type: str) -> str | None:
    if pubmed_data is None:
        return None
    for article_id in pubmed_data.findall("ArticleIdList/ArticleId"):
        if article_id.attrib.get("IdType") == id_type:
            return _element_text(article_id)
    return None


def _text(parent: ET.Element | None, path: str) -> str | None:
    if parent is None:
        return None
    child = parent.find(path)
    return _element_text(child)


def _element_text(element: ET.Element | None) -> str | None:
    if element is None:
        return None
    text = " ".join("".join(element.itertext()).split())
    return text or None


def _safe_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _env_flag(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}
