from __future__ import annotations

import os
from typing import Any

import requests

from hra.models import ClinicalTrial, ClinicalTrialResponse, TrialLocation

TRIAL_STATUS_OPTIONS = (
    "RECRUITING",
    "NOT_YET_RECRUITING",
    "ACTIVE_NOT_RECRUITING",
    "ENROLLING_BY_INVITATION",
    "COMPLETED",
    "SUSPENDED",
    "TERMINATED",
    "WITHDRAWN",
    "UNKNOWN",
)


class ClinicalTrialsError(RuntimeError):
    """Raised when ClinicalTrials.gov cannot return a usable response."""


class ClinicalTrialsClient:
    """Client for the official ClinicalTrials.gov API v2."""

    BASE_URL = "https://clinicaltrials.gov/api/v2"

    def __init__(
        self,
        base_url: str = BASE_URL,
        timeout: float = 30.0,
        trust_env: bool | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.trust_env = trust_env if trust_env is not None else _env_flag("HRA_TRUST_ENV")

    def search(
        self,
        condition: str = "Huntington Disease",
        other_terms: str | None = None,
        statuses: list[str] | None = None,
        page_size: int = 100,
        page_token: str | None = None,
    ) -> ClinicalTrialResponse:
        params: dict[str, str | int | bool] = {
            "query.cond": condition,
            "format": "json",
            "pageSize": min(max(page_size, 1), 1000),
            "countTotal": "true",
        }
        if other_terms:
            params["query.term"] = other_terms
        if statuses:
            params["filter.overallStatus"] = "|".join(statuses)
        if page_token:
            params["pageToken"] = page_token

        try:
            with requests.Session() as session:
                session.trust_env = self.trust_env
                session.headers.update(
                    {"User-Agent": self._user_agent(), "Accept": "application/json"}
                )
                response = session.get(
                    f"{self.base_url}/studies",
                    params=params,
                    timeout=self.timeout,
                )
                response.raise_for_status()
                data = response.json()
        except requests.HTTPError as exc:
            status = exc.response.status_code
            raise ClinicalTrialsError(
                f"ClinicalTrials.gov request failed with HTTP {status}. "
                "The official service may be temporarily unavailable or blocking this connection."
            ) from exc
        except requests.RequestException as exc:
            raise ClinicalTrialsError(f"ClinicalTrials.gov request failed: {exc}") from exc
        except ValueError as exc:
            raise ClinicalTrialsError("ClinicalTrials.gov returned invalid JSON.") from exc

        studies = [self._parse_study(item) for item in data.get("studies", [])]
        return ClinicalTrialResponse(
            total_results=_safe_int(data.get("totalCount")),
            studies=studies,
            next_page_token=data.get("nextPageToken"),
        )

    def _parse_study(self, item: dict[str, Any]) -> ClinicalTrial:
        protocol = item.get("protocolSection", {})
        identification = protocol.get("identificationModule", {})
        status = protocol.get("statusModule", {})
        description = protocol.get("descriptionModule", {})
        design = protocol.get("designModule", {})
        sponsors = protocol.get("sponsorCollaboratorsModule", {})
        arms = protocol.get("armsInterventionsModule", {})
        contacts = protocol.get("contactsLocationsModule", {})

        nct_id = str(identification.get("nctId") or item.get("nctId") or "").strip()
        if not nct_id:
            raise ClinicalTrialsError("ClinicalTrials.gov returned a study without an NCT ID.")

        interventions = []
        for intervention in arms.get("interventions", []):
            name = str(intervention.get("name") or "").strip()
            if not name:
                continue
            intervention_type = str(intervention.get("type") or "").replace("_", " ").title()
            interventions.append(f"{intervention_type}: {name}" if intervention_type else name)

        locations = [
            TrialLocation(
                facility=location.get("facility"),
                status=location.get("status"),
                city=location.get("city"),
                state=location.get("state"),
                country=location.get("country"),
            )
            for location in contacts.get("locations", [])
            if isinstance(location, dict)
        ]

        return ClinicalTrial(
            nct_id=nct_id,
            brief_title=identification.get("briefTitle") or "Untitled study",
            official_title=identification.get("officialTitle"),
            overall_status=status.get("overallStatus") or "UNKNOWN",
            phases=design.get("phases", []),
            study_type=design.get("studyType"),
            brief_summary=description.get("briefSummary"),
            interventions=interventions,
            sponsor=sponsors.get("leadSponsor", {}).get("name"),
            enrollment=_safe_int(design.get("enrollmentInfo", {}).get("count")),
            start_date=status.get("startDateStruct", {}).get("date"),
            completion_date=status.get("completionDateStruct", {}).get("date"),
            last_update=(
                status.get("lastUpdatePostDateStruct", {}).get("date")
                or status.get("studyFirstPostDateStruct", {}).get("date")
            ),
            locations=locations,
            source_url=f"https://clinicaltrials.gov/study/{nct_id}",
        )

    def _user_agent(self) -> str:
        return (
            "huntington-research-assistant/0.2 "
            "(https://github.com/Runarthe/huntington-research-assistant)"
        )


def _safe_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _env_flag(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}
