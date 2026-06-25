from hra.clients.pubmed import PubMedClient


def test_pubmed_does_not_trust_proxy_env_by_default(monkeypatch) -> None:
    monkeypatch.setenv("HTTP_PROXY", "http://127.0.0.1:9")
    monkeypatch.setenv("HTTPS_PROXY", "http://127.0.0.1:9")
    monkeypatch.delenv("HRA_TRUST_ENV", raising=False)

    client = PubMedClient()

    assert client.trust_env is False


def test_pubmed_search_uses_esearch_and_efetch(monkeypatch) -> None:
    seen_urls: list[str] = []
    seen_params: list[dict[str, object]] = []

    class FakeResponse:
        status_code = 200

        def __init__(self, text: str = "") -> None:
            self.text = text

        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, object]:
            return {"esearchresult": {"count": "1", "idlist": ["123"]}}

    class FakeClient:
        def __init__(self, **kwargs: object) -> None:
            pass

        def __enter__(self) -> "FakeClient":
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def get(self, url: str, params: dict[str, object]) -> FakeResponse:
            seen_urls.append(url)
            seen_params.append(params)
            if url.endswith("efetch.fcgi"):
                return FakeResponse(PUBMED_XML)
            return FakeResponse()

    monkeypatch.setattr("hra.clients.pubmed.httpx.Client", FakeClient)

    response = PubMedClient().search("huntingtin", page=2, page_size=10)

    assert seen_urls[0].endswith("esearch.fcgi")
    assert seen_params[0]["retstart"] == 10
    assert seen_params[0]["retmax"] == 10
    assert seen_urls[1].endswith("efetch.fcgi")
    assert response.total_results == 1
    assert response.papers[0].pmid == "123"
    assert response.papers[0].doi == "10.1000/example"
    assert response.papers[0].source_provider == "PubMed"
    assert response.papers[0].year == 2025
    assert response.papers[0].publication_types == ["Journal Article"]
    assert response.papers[0].abstract == "Objective: Study HTT. Results: HTT changed."


PUBMED_XML = """<?xml version="1.0" encoding="UTF-8"?>
<PubmedArticleSet>
  <PubmedArticle>
    <MedlineCitation>
      <PMID>123</PMID>
      <Article>
        <Journal>
          <JournalIssue>
            <PubDate><Year>2025</Year></PubDate>
          </JournalIssue>
          <Title>Example Journal</Title>
        </Journal>
        <ArticleTitle>Example HTT paper</ArticleTitle>
        <Abstract>
          <AbstractText Label="Objective">Study HTT.</AbstractText>
          <AbstractText Label="Results">HTT changed.</AbstractText>
        </Abstract>
        <AuthorList>
          <Author>
            <LastName>Smith</LastName>
            <ForeName>Alex</ForeName>
          </Author>
        </AuthorList>
        <PublicationTypeList>
          <PublicationType>Journal Article</PublicationType>
        </PublicationTypeList>
      </Article>
    </MedlineCitation>
    <PubmedData>
      <ArticleIdList>
        <ArticleId IdType="doi">10.1000/example</ArticleId>
      </ArticleIdList>
    </PubmedData>
  </PubmedArticle>
</PubmedArticleSet>
"""
