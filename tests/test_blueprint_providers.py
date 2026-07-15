from __future__ import annotations

from datetime import date

import pytest

from labs.blueprint_experiments.providers import (
    BlueprintRunRequest,
    GatedLiveProvider,
    LiveProviderDisabledError,
    MockBlueprintProvider,
    provider_for_type,
)


def test_mock_provider_plans_and_runs_offline() -> None:
    provider = MockBlueprintProvider()
    request = BlueprintRunRequest(target="HTT", run_date=date(2026, 7, 15), points=3)

    plan = provider.plan(request)
    run = provider.run(request)

    assert plan["status"] == "planned"
    assert plan["provider_type"] == "mock"
    assert run["status"] == "generated"
    assert run["provider_type"] == "mock"
    assert run["runtime"]["requires_live_provider"] is False


def test_gated_live_provider_can_plan_but_not_run() -> None:
    provider = GatedLiveProvider("nvidia_nim")
    request = BlueprintRunRequest(target="HTT", run_date=date(2026, 7, 15))

    plan = provider.plan(request)

    assert plan["status"] == "planned"
    assert plan["provider_type"] == "nvidia_nim"
    assert plan["runtime"]["requires_live_provider"] is True
    with pytest.raises(LiveProviderDisabledError, match="gated"):
        provider.run(request)


def test_gated_live_provider_still_fails_when_live_flag_is_set() -> None:
    provider = GatedLiveProvider("bionemo")
    request = BlueprintRunRequest(
        target="BDNF",
        run_date=date(2026, 7, 15),
        allow_live=True,
    )

    with pytest.raises(LiveProviderDisabledError, match="no implemented adapter"):
        provider.run(request)


def test_provider_factory_returns_mock_or_gated_provider() -> None:
    assert isinstance(provider_for_type("mock"), MockBlueprintProvider)
    assert isinstance(provider_for_type("alphafold"), GatedLiveProvider)
