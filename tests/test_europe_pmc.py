from hra.clients.europe_pmc import EuropePMCClient


def test_europe_pmc_does_not_trust_proxy_env_by_default(monkeypatch) -> None:
    monkeypatch.setenv("HTTP_PROXY", "http://127.0.0.1:9")
    monkeypatch.setenv("HTTPS_PROXY", "http://127.0.0.1:9")
    monkeypatch.delenv("HRA_TRUST_ENV", raising=False)

    client = EuropePMCClient()

    assert client.trust_env is False


def test_europe_pmc_can_opt_into_proxy_env(monkeypatch) -> None:
    monkeypatch.setenv("HRA_TRUST_ENV", "true")

    client = EuropePMCClient()

    assert client.trust_env is True


def test_search_uses_cursor_mark_for_real_pagination(monkeypatch) -> None:
    seen_params: dict[str, object] = {}

    class FakeResponse:
        status_code = 200

        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, object]:
            return {
                "hitCount": 20,
                "nextCursorMark": "next-cursor",
                "resultList": {"result": [{"id": "123", "title": "Paper"}]},
            }

    class FakeClient:
        def __init__(self, **kwargs: object) -> None:
            pass

        def __enter__(self) -> "FakeClient":
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def get(self, url: str, params: dict[str, object]) -> FakeResponse:
            seen_params.update(params)
            return FakeResponse()

    monkeypatch.setattr("hra.clients.europe_pmc.httpx.Client", FakeClient)

    response = EuropePMCClient().search(
        "huntingtin",
        page=2,
        page_size=10,
        cursor_mark="current-cursor",
    )

    assert seen_params["cursorMark"] == "current-cursor"
    assert "page" not in seen_params
    assert response.next_cursor_mark == "next-cursor"


def test_count_by_year_queries_every_year(monkeypatch) -> None:
    seen_queries: list[str] = []

    class FakeResponse:
        def __init__(self, count: int) -> None:
            self.count = count

        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, str]:
            return {"hitCount": str(self.count)}

    class FakeClient:
        def __init__(self, **kwargs: object) -> None:
            pass

        def __enter__(self) -> "FakeClient":
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def get(self, url: str, params: dict[str, object]) -> FakeResponse:
            query = str(params["query"])
            seen_queries.append(query)
            year = int(query.rsplit("PUB_YEAR:", 1)[1])
            return FakeResponse(year - 2020)

    monkeypatch.setattr("hra.clients.europe_pmc.httpx.Client", FakeClient)

    counts = EuropePMCClient().count_by_year("huntingtin", 2024, 2026)

    assert counts == [
        {"year": 2024, "papers": 4},
        {"year": 2025, "papers": 5},
        {"year": 2026, "papers": 6},
    ]
    assert seen_queries == [
        "(huntingtin) AND PUB_YEAR:2024",
        "(huntingtin) AND PUB_YEAR:2025",
        "(huntingtin) AND PUB_YEAR:2026",
    ]


def test_parse_paper_includes_publication_and_correction_metadata() -> None:
    paper = EuropePMCClient()._parse_paper(
        {
            "id": "123",
            "title": "RETRACTED: <i>Example</i>",
            "pubTypeList": {"pubType": ["Retracted Publication", "Journal Article"]},
            "commentCorrectionList": {
                "commentCorrection": {
                    "id": "456",
                    "source": "MED",
                    "type": "Retraction in",
                    "reference": "Retraction notice",
                }
            },
        }
    )

    assert paper.publication_types == ["Retracted Publication", "Journal Article"]
    assert paper.title == "RETRACTED: Example"
    assert paper.is_retracted is True
    assert paper.correction_notices[0].notice_type == "Retraction in"


def test_parse_paper_includes_only_open_access_full_text_urls() -> None:
    paper = EuropePMCClient()._parse_paper(
        {
            "id": "123",
            "title": "Open paper",
            "fullTextUrlList": {
                "fullTextUrl": [
                    {
                        "availabilityCode": "S",
                        "documentStyle": "pdf",
                        "url": "https://example.org/subscription.pdf",
                    },
                    {
                        "availabilityCode": "OA",
                        "documentStyle": "html",
                        "url": "https://europepmc.org/articles/PMC123",
                    },
                    {
                        "availabilityCode": "OA",
                        "documentStyle": "pdf",
                        "url": "https://europepmc.org/articles/PMC123?pdf=render",
                    },
                ]
            },
        }
    )

    assert str(paper.open_access_full_text_url).endswith("/articles/PMC123")
    assert str(paper.open_access_pdf_url).endswith("PMC123?pdf=render")


def test_parse_paper_cleans_structured_abstract_markup() -> None:
    paper = EuropePMCClient()._parse_paper(
        {
            "id": "123",
            "title": "Study",
            "abstractText": (
                "<h4>Objective</h4><p>To study <i>HTT</i>.</p>"
                "<h4>Methods</h4><p>We tested <i>HTT</i>-expressing cells.</p>"
            ),
        }
    )

    assert paper.abstract == (
        "Objective: To study HTT. Methods: We tested HTT-expressing cells."
    )
