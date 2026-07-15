from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Protocol

from pydantic import BaseModel, Field, model_validator

from .manifests import (
    ProviderType,
    VALID_PROVIDER_TYPES,
    mock_blueprint_manifest,
    planned_blueprint_manifest,
)

ExecutionMode = str
VALID_EXECUTION_MODES = {"offline", "planned", "live"}


class LiveProviderDisabledError(RuntimeError):
    """Raised when a live provider is requested without an explicit adapter."""


class BlueprintProviderConfig(BaseModel):
    """Provider configuration that is safe to serialize and commit.

    The model intentionally stores only non-secret configuration. Credentials
    should be referenced by environment variable name and never by value.
    """

    provider_type: ProviderType = "mock"
    execution_mode: ExecutionMode = "planned"
    provider_name: str | None = None
    model_name: str | None = None
    model_version: str | None = None
    endpoint_url: str | None = None
    credentials_env_var: str | None = None
    live_reviewed: bool = False
    notes: tuple[str, ...] = Field(default_factory=tuple)

    @model_validator(mode="after")
    def _validate_config(self) -> "BlueprintProviderConfig":
        if self.provider_type not in VALID_PROVIDER_TYPES:
            raise ValueError(f"Unknown provider type: {self.provider_type}")
        if self.execution_mode not in VALID_EXECUTION_MODES:
            raise ValueError(f"Unknown execution mode: {self.execution_mode}")
        if self.provider_type == "mock" and self.execution_mode == "live":
            raise ValueError("Mock provider cannot be configured for live execution.")
        if self.execution_mode == "live" and not self.live_reviewed:
            raise ValueError("Live provider execution requires an explicit reviewed config.")
        return self


@dataclass(frozen=True)
class BlueprintRunRequest:
    """A provider-neutral request for a bounded Blueprint-style lab run."""

    target: str
    provider_type: ProviderType = "mock"
    execution_mode: ExecutionMode = "planned"
    run_date: date | None = None
    points: int = 8
    allow_live: bool = False


@dataclass(frozen=True)
class BlueprintProviderMetadata:
    """Adapter metadata for UI display, CLI inspection, and provenance."""

    provider_type: ProviderType
    provider_name: str
    execution_mode: ExecutionMode
    implemented: bool
    live_enabled: bool
    requires_credentials: bool
    claim_boundary: str
    notes: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, object]:
        return {
            "provider_type": self.provider_type,
            "provider_name": self.provider_name,
            "execution_mode": self.execution_mode,
            "implemented": self.implemented,
            "live_enabled": self.live_enabled,
            "requires_credentials": self.requires_credentials,
            "claim_boundary": self.claim_boundary,
            "notes": list(self.notes),
        }


class BlueprintExperimentProvider(Protocol):
    """Minimal contract future providers must implement."""

    provider_type: ProviderType
    provider_name: str

    def describe(self) -> BlueprintProviderMetadata:
        """Return adapter metadata without calling any live provider."""

    def plan(self, request: BlueprintRunRequest) -> dict[str, object]:
        """Return a manifest describing what would be run."""

    def run(self, request: BlueprintRunRequest) -> dict[str, object]:
        """Return a generated manifest after executing or simulating a run."""


class MockBlueprintProvider:
    """Offline provider used for tests and fixture generation."""

    provider_type: ProviderType = "mock"
    provider_name = "deterministic-blueprint-fixture"

    def describe(self) -> BlueprintProviderMetadata:
        return BlueprintProviderMetadata(
            provider_type=self.provider_type,
            provider_name=self.provider_name,
            execution_mode="offline",
            implemented=True,
            live_enabled=False,
            requires_credentials=False,
            claim_boundary=(
                "Mock provider output is deterministic fixture data for engineering "
                "tests only, not biomedical evidence or model output."
            ),
            notes=("Runs locally without network, credentials, GPU, or external services.",),
        )

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

    def __init__(self, config: BlueprintProviderConfig | ProviderType) -> None:
        if isinstance(config, str):
            config = BlueprintProviderConfig(provider_type=config)
        if config.provider_type == "mock":
            raise ValueError("Use MockBlueprintProvider for mock runs.")
        self.config = config
        self.provider_type = config.provider_type
        self.provider_name = (
            config.provider_name or f"{config.provider_type}-adapter-not-implemented"
        )

    def describe(self) -> BlueprintProviderMetadata:
        return BlueprintProviderMetadata(
            provider_type=self.provider_type,
            provider_name=self.provider_name,
            execution_mode=self.config.execution_mode,
            implemented=False,
            live_enabled=False,
            requires_credentials=self.config.credentials_env_var is not None,
            claim_boundary=(
                "This provider family is a planned adapter boundary only. It has "
                "not executed a live provider and does not produce biomedical claims."
            ),
            notes=(
                self.config.notes
                or (
                    "Planning mode is available for provenance design.",
                    "Live execution remains disabled until a reviewed adapter is added.",
                )
            ),
        )

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


def default_provider_config(provider_type: ProviderType) -> BlueprintProviderConfig:
    """Return a conservative default config for a provider family."""

    if provider_type == "mock":
        return BlueprintProviderConfig(
            provider_type="mock",
            execution_mode="offline",
            provider_name="deterministic-blueprint-fixture",
            model_name="planned-offline-fixture",
            model_version="0.1",
            notes=("Default local fixture provider.",),
        )
    return BlueprintProviderConfig(
        provider_type=provider_type,
        execution_mode="planned",
        provider_name=f"{provider_type}-adapter-not-implemented",
        model_name="select-before-live-run",
        model_version="record-before-live-run",
        notes=(
            "No live adapter is implemented.",
            "Use this config to plan provenance and safety checks before integration.",
        ),
    )


def provider_for_config(config: BlueprintProviderConfig) -> BlueprintExperimentProvider:
    """Return the provider object for a validated config without live execution."""

    if config.provider_type == "mock":
        return MockBlueprintProvider()
    return GatedLiveProvider(config)


def provider_for_type(provider_type: ProviderType) -> BlueprintExperimentProvider:
    """Return the configured provider object without performing live work."""

    return provider_for_config(default_provider_config(provider_type))


def provider_metadata(provider_type: ProviderType) -> dict[str, object]:
    """Return serializable metadata for a provider family."""

    provider = provider_for_type(provider_type)
    return provider.describe().as_dict()


def provider_catalogue() -> dict[str, object]:
    """Return all provider metadata for CLI and UI inspection."""

    return {
        "schema_version": "blueprint-provider-catalogue.v2",
        "default": "mock",
        "execution_modes": sorted(VALID_EXECUTION_MODES),
        "providers": [
            provider_metadata(provider_type)
            for provider_type in sorted(VALID_PROVIDER_TYPES)
        ],
        "safety": {
            "claim_boundary": (
                "Provider catalogue entries describe integration boundaries, "
                "not validated biomedical capabilities or clinical evidence."
            ),
        },
    }
