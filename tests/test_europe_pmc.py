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
