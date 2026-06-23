from hra.models import ClinicalTrial, TrialLocation
from hra.trial_filters import filter_trials, trial_filter_options


def make_trial(nct_id: str, phase: str, country: str) -> ClinicalTrial:
    return ClinicalTrial(
        nct_id=nct_id,
        brief_title="Study",
        overall_status="RECRUITING",
        phases=[phase],
        locations=[TrialLocation(country=country)],
        source_url=f"https://clinicaltrials.gov/study/{nct_id}",
    )


def test_trial_filters_and_options() -> None:
    trials = [
        make_trial("NCT00000001", "PHASE1", "Norway"),
        make_trial("NCT00000002", "PHASE2", "United States"),
    ]

    assert [trial.nct_id for trial in filter_trials(trials, phases=["PHASE2"])] == [
        "NCT00000002"
    ]
    assert trial_filter_options(trials) == (
        ["PHASE1", "PHASE2"],
        ["Norway", "United States"],
    )
