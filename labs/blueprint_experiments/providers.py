from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Protocol

from .manifests import (
    ProviderType,
    VALID_PROVIDER_TYPES,
    mock_blueprint_manifest,
    planned_blueprint_manifest,
)


class LiveProviderDisabledError(RuntimeError):
    """Raised when a live provider is requested without an explicit adapter."""


@dataclass(frozen=True)
class BlueprintRunRequest:
    """A provider-neutral request for a bounded Blueprint-style lab run."""

    target: str
    provider_type: ProviderType = "mock"
    run_date: date | None = None
    points: int = 8
    allow_live: bool = False


class BlueprintExperimentProvider(Protocol):
    """Minimal contract future providers must implement."""

    provider_type: ProviderType
    provider_name: str

    def plan(self, request: BlueprintRunRequest) -> dict[str, object]:
        """Return a manifest describing what would be run."""

    def run(self, request: BlueprintRunRequest) -> dict[str, object]:
        """Return a generated manifest after executing or simulating a run."""


class MockBlueprintProvider:
    """Offline provider used for tests and fixture generation."""

    provider_type: ProviderType = "mock"
    provider_name = "deterministic-blueprint-fixture"

    def plan(self, request: BlueprintRunRequest) -> dict[str, object]:
        return planned_blueprint_manifest(
            request.target,
            provider_type="mock",
            planned_at=request.run_date,
        )

    def run(self, request: BlueprintRunRequest) -> dict[str, object]:
        return mock_blueprint_manifest(
            request.target,
            generated_at=request.run_date,
            points=request.points,
        )


class GatedLiveProvider:
    """Placeholder for future live providers that are not implemented yet."""

    def __init__(self, provider_type: ProviderType) -> None:
        if provider_type == "mock":
            raise ValueError("Use MockBlueprintProvider for mock runs.")
        if provider_type not in VALID_PROVIDER_TYPES:
            raise ValueError(f"Unknown provider type: {provider_type}")
        self.provider_type = provider_type
        self.provider_name = f"{provider_type}-adapter-not-implemented"

    def plan(self, request: BlueprintRunRequest) -> dict[str, object]:
        return planned_blueprint_manifest(
            request.target,
            provider_type=self.provider_type,
            planned_at=request.run_date,
        )

    def run(self, request: BlueprintRunRequest) -> dict[str, object]:
        if not request.allow_live:
            raise LiveProviderDisabledError(
                f"Live provider '{self.provider_type}' is gated. Use planning mode "
                "or add an explicit reviewed adapter before enabling live execution."
            )
        raise LiveProviderDisabledError(
            f"Live provider '{self.provider_type}' has no implemented adapter yet."
        )


def provider_for_type(provider_type: ProviderType) -> BlueprintExperimentProvider:
    """Return the configured provider object without performing live work."""

    if provider_type == "mock":
        return MockBlueprintProvider()
    return GatedLiveProvider(provider_type)
