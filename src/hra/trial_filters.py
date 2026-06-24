from __future__ import annotations

from collections.abc import Iterable

from hra.models import ClinicalTrial


def filter_trials(
    trials: Iterable[ClinicalTrial],
    phases: list[str] | None = None,
    countries: list[str] | None = None,
) -> list[ClinicalTrial]:
    selected_phases = set(phases or [])
    selected_countries = set(countries or [])
    filtered: list[ClinicalTrial] = []
    for trial in trials:
        if selected_phases and not selected_phases.intersection(trial.phases):
            continue
        if selected_countries and not selected_countries.intersection(trial.countries):
            continue
        filtered.append(trial)
    return filtered


def trial_filter_options(trials: Iterable[ClinicalTrial]) -> tuple[list[str], list[str]]:
    trial_list = list(trials)
    phases = sorted({phase for trial in trial_list for phase in trial.phases})
    countries = sorted({country for trial in trial_list for country in trial.countries})
    return phases, countries
