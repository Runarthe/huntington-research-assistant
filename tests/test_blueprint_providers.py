from __future__ import annotations

from datetime import date

import pytest

from labs.blueprint_experiments.providers import (
    BlueprintProviderConfig,
    BlueprintRunRequest,
    GatedLiveProvider,
    LiveProviderDisabledError,
    MockBlueprintProvider,
    PublicUniProtProvider,
    provider_catalogue,
    provider_for_type,
    provider_metadata,
)
from labs.blueprint_experiments.manifests import validate_blueprint_manifest


def test_mock_provider_plans_and_runs_offline() -> None:
    provider = MockBlueprintProvider()
    request = BlueprintRunRequest(target="HTT", run_date=date(2026, 7, 15), points=3)

    metadata = provider.describe()
    plan = provider.plan(request)
    run = provider.run(request)

    assert metadata.implemented is True
    assert metadata.execution_mode == "offline"
    assert plan["status"] == "planned"
    assert plan["provider_type"] == "mock"
    assert run["status"] == "generated"
    assert run["provider_type"] == "mock"
    assert run["runtime"]["requires_live_provider"] is False


def test_gated_live_provider_can_plan_but_not_run() -> None:
    provider = GatedLiveProvider("nvidia_nim")
    request = BlueprintRunRequest(target="HTT", run_date=date(2026, 7, 15))

    metadata = provider.describe()
    plan = provider.plan(request)

    assert metadata.implemented is False
    assert metadata.live_enabled is False
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
    assert isinstance(provider_for_type("uniprot"), PublicUniProtProvider)
    assert isinstance(provider_for_type("alphafold"), GatedLiveProvider)


def test_provider_config_rejects_unreviewed_live_mode() -> None:
    with pytest.raises(ValueError, match="requires an explicit reviewed config"):
        BlueprintProviderConfig(provider_type="bionemo", execution_mode="live")


def test_provider_metadata_is_serializable_and_claim_bounded() -> None:
    metadata = provider_metadata("bionemo")

    assert metadata["provider_type"] == "bionemo"
    assert metadata["implemented"] is False
    assert "does not produce biomedical claims" in metadata["claim_boundary"]


def test_provider_catalogue_lists_modes_and_providers() -> None:
    catalogue = provider_catalogue()

    assert catalogue["schema_version"] == "blueprint-provider-catalogue.v2"
    assert "planned" in catalogue["execution_modes"]
    assert {provider["provider_type"] for provider in catalogue["providers"]} >= {
        "mock",
        "bionemo",
        "nvidia_nim",
        "uniprot",
    }


def test_public_uniprot_provider_plans_without_live_retrieval() -> None:
    provider = PublicUniProtProvider()
    request = BlueprintRunRequest(target="HTT", run_date=date(2026, 7, 16))

    metadata = provider.describe()
    plan = provider.plan(request)

    assert metadata.implemented is True
    assert metadata.live_enabled is False
    assert metadata.requires_credentials is False
    assert plan["provider_type"] == "uniprot"
    assert plan["status"] == "planned"
    assert plan["runtime"]["requires_live_provider"] is True


def test_public_uniprot_provider_requires_reviewed_live_config() -> None:
    provider = PublicUniProtProvider()

    with pytest.raises(LiveProviderDisabledError, match="reviewed live config"):
        provider.run(BlueprintRunRequest(target="HTT", allow_live=True))


def test_public_uniprot_provider_can_generate_metadata_with_injected_fetcher() -> None:
    config = BlueprintProviderConfig(
        provider_type="uniprot",
        execution_mode="live",
        live_reviewed=True,
    )
    provider = PublicUniProtProvider(
        config,
        fetcher=lambda _url: ">sp|P23560|BDNF_HUMAN Brain-derived neurotrophic factor\nMSKGQR\n",
    )

    manifest = provider.run(
        BlueprintRunRequest(
            target="BDNF",
            run_date=date(2026, 7, 16),
            allow_live=True,
        )
    )

    validate_blueprint_manifest(manifest)
    assert manifest["provider_type"] == "uniprot"
    assert manifest["status"] == "generated"
    assert manifest["outputs"]["artifact_type"] == "public_sequence_metadata"
    assert manifest["runtime"]["parameters"]["sequence_length"] == 6
    assert manifest["runtime"]["parameters"]["checksum"].startswith("sha256:")
