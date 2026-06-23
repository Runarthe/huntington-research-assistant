from hra.clients.clinical_trials import ClinicalTrialsClient


def test_clinical_trials_client_parses_official_v2_shape(monkeypatch) -> None:
    payload = {
        "totalCount": 1,
        "nextPageToken": "next-token",
        "studies": [
            {
                "protocolSection": {
                    "identificationModule": {
                        "nctId": "NCT12345678",
                        "briefTitle": "A Huntington study",
                    },
                    "statusModule": {
                        "overallStatus": "RECRUITING",
                        "startDateStruct": {"date": "2025-01"},
                        "lastUpdatePostDateStruct": {"date": "2026-06-01"},
                    },
                    "descriptionModule": {"briefSummary": "Registry summary"},
                    "designModule": {
                        "studyType": "INTERVENTIONAL",
                        "phases": ["PHASE2"],
                        "enrollmentInfo": {"count": 42},
                    },
                    "sponsorCollaboratorsModule": {
                        "leadSponsor": {"name": "Example Sponsor"}
                    },
                    "armsInterventionsModule": {
                        "interventions": [{"type": "DRUG", "name": "Example compound"}]
                    },
                    "contactsLocationsModule": {
                        "locations": [
                            {"facility": "Study Centre", "city": "Oslo", "country": "Norway"}
                        ]
                    },
                }
            }
        ],
    }

    class FakeResponse:
        status_code = 200

        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, object]:
            return payload

    class FakeSession:
        def __init__(self) -> None:
            self.trust_env = True
            self.headers: dict[str, str] = {}

        def __enter__(self) -> "FakeSession":
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def get(
            self,
            url: str,
            params: dict[str, object],
            timeout: float,
        ) -> FakeResponse:
            assert params["query.cond"] == "Huntington Disease"
            assert params["filter.overallStatus"] == "RECRUITING"
            return FakeResponse()

    monkeypatch.setattr("hra.clients.clinical_trials.requests.Session", FakeSession)

    response = ClinicalTrialsClient().search(statuses=["RECRUITING"])
    trial = response.studies[0]

    assert response.total_results == 1
    assert response.next_page_token == "next-token"
    assert trial.nct_id == "NCT12345678"
    assert trial.interventions == ["Drug: Example compound"]
    assert trial.countries == ["Norway"]
    assert str(trial.source_url).endswith("/NCT12345678")
