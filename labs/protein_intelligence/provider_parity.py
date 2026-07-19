"""Provider-neutral protein embedding provenance and parity reports."""

from __future__ import annotations

from copy import deepcopy
from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict

from labs.protein_intelligence.local_esm2 import (
    LocalESM2Config,
    planned_local_esm2_manifest,
)
from labs.protein_intelligence.sequences import ProteinSequenceRecord


ARTIFACT_CONTRACT_VERSION = "protein-embedding-artifact.v1"
PARITY_REPORT_VERSION = "protein-embedding-provider-parity.v1"
BIONEMO_MODEL_NAME = "ESM-2 8M candidate checkpoint"
BIONEMO_MODEL_VERSION = "esm2/8m:2.0"
BIONEMO_MODEL_URL = (
    "https://docs.nvidia.com/bionemo-recipes/latest/models/ESM-2/pre-training/"
)
BIONEMO_INFERENCE_URL = (
    "https://docs.nvidia.com/bionemo-framework/latest/main/examples/"
    "bionemo-esm2/inference/index.html"
)

ParityStatus = Literal["matched", "different", "not-available", "not-comparable"]


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class EmbeddingInputDescriptor(_StrictModel):
    identifier: str | None
    selected_sequence_checksum: str | None
    selected_sequence_length: int | None
    window_start: int | None
    window_end: int | None


class EmbeddingModelDescriptor(_StrictModel):
    provider: str | None
    name: str | None
    version: str | None


class EmbeddingPreprocessingDescriptor(_StrictModel):
    input_handling: str | None
    max_residues: int | None
    silent_truncation: bool | None
    pooling_method: str | None


class EmbeddingOutputDescriptor(_StrictModel):
    dimensions: int | None
    token_embeddings_shape: tuple[int, ...] | None
    vector_checksum: str | None


class EmbeddingRuntimeDescriptor(_StrictModel):
    interface: str | None
    hardware: str | None
    precision: str | None


class EmbeddingArtifactDescriptor(_StrictModel):
    schema_version: str = ARTIFACT_CONTRACT_VERSION
    source_experiment_id: str
    execution_status: str
    model: EmbeddingModelDescriptor
    input: EmbeddingInputDescriptor
    preprocessing: EmbeddingPreprocessingDescriptor
    output: EmbeddingOutputDescriptor
    runtime: EmbeddingRuntimeDescriptor


class ProviderParityCheck(_StrictModel):
    field: str
    status: ParityStatus
    reference: object | None
    candidate: object | None
    explanation: str


class ProviderParityReport(_StrictModel):
    schema_version: str = PARITY_REPORT_VERSION
    report_id: str
    generated_at: date
    overall_status: str
    reference: EmbeddingArtifactDescriptor
    candidate: EmbeddingArtifactDescriptor
    checks: tuple[ProviderParityCheck, ...]
    summary: dict[str, int]
    readiness: dict[str, bool]
    source_documents: tuple[str, ...]
    limitations: tuple[str, ...]


def _mapping(value: object) -> dict[str, object]:
    return value if isinstance(value, dict) else {}


def _optional_int(value: object) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _optional_bool(value: object) -> bool | None:
    return value if isinstance(value, bool) else None


def _optional_str(value: object) -> str | None:
    return value if isinstance(value, str) else None


def normalize_embedding_manifest(
    manifest: dict[str, object],
) -> EmbeddingArtifactDescriptor:
    """Normalize an HRA embedding manifest without interpreting its vector."""

    model = _mapping(manifest.get("model"))
    runtime = _mapping(manifest.get("runtime"))
    parameters = _mapping(runtime.get("parameters"))
    outputs = _mapping(manifest.get("outputs"))
    embedding = _mapping(outputs.get("embedding"))
    inputs = manifest.get("inputs")
    first_input = (
        _mapping(inputs[0])
        if isinstance(inputs, list) and inputs
        else {}
    )
    shape = embedding.get("token_embeddings_shape")
    normalized_shape = (
        tuple(value for value in shape if isinstance(value, int))
        if isinstance(shape, list)
        else None
    )

    return EmbeddingArtifactDescriptor(
        source_experiment_id=str(manifest.get("experiment_id", "unknown")),
        execution_status=str(manifest.get("status", "unknown")),
        model=EmbeddingModelDescriptor(
            provider=_optional_str(model.get("provider")),
            name=_optional_str(model.get("name")),
            version=_optional_str(model.get("version")),
        ),
        input=EmbeddingInputDescriptor(
            identifier=_optional_str(first_input.get("identifier")),
            selected_sequence_checksum=_optional_str(
                first_input.get("selected_sequence_checksum")
            ),
            selected_sequence_length=_optional_int(
                first_input.get("selected_sequence_length")
            ),
            window_start=_optional_int(first_input.get("window_start")),
            window_end=_optional_int(first_input.get("window_end")),
        ),
        preprocessing=EmbeddingPreprocessingDescriptor(
            input_handling=_optional_str(first_input.get("input_handling")),
            max_residues=_optional_int(parameters.get("max_residues")),
            silent_truncation=_optional_bool(parameters.get("silent_truncation")),
            pooling_method=_optional_str(parameters.get("pooling_method")),
        ),
        output=EmbeddingOutputDescriptor(
            dimensions=_optional_int(embedding.get("dimensions")),
            token_embeddings_shape=normalized_shape,
            vector_checksum=_optional_str(embedding.get("checksum")),
        ),
        runtime=EmbeddingRuntimeDescriptor(
            interface=_optional_str(runtime.get("interface")),
            hardware=_optional_str(runtime.get("hardware")),
            precision=_optional_str(parameters.get("precision")),
        ),
    )


def planned_bionemo_esm2_manifest(
    record: ProteinSequenceRecord,
    config: LocalESM2Config,
    *,
    planned_at: date | None = None,
) -> dict[str, object]:
    """Plan BioNeMo ESM-2 parity using the exact local sequence selection."""

    local_plan = planned_local_esm2_manifest(record, config, planned_at=planned_at)
    input_record = deepcopy(local_plan["inputs"][0])
    fingerprint = str(input_record["selected_sequence_checksum"]).split(":", 1)[1][
        :12
    ]
    start = input_record["window_start"]
    end = input_record["window_end"]
    return {
        "schema_version": "0.3",
        "experiment_id": (
            f"bionemo-esm2-{record.target.symbol.lower()}-{start}-{end}-{fingerprint}"
        ),
        "status": "planned",
        "purpose": (
            "Plan a provider-parity ESM-2 embedding run with the same explicit "
            "sequence input used by the local reference provider."
        ),
        "component_type": "foundation_model",
        "model": {
            "provider": "NVIDIA BioNeMo Framework",
            "name": BIONEMO_MODEL_NAME,
            "version": BIONEMO_MODEL_VERSION,
            "licence": "Review BioNeMo and checkpoint licences before execution",
            "source_url": BIONEMO_MODEL_URL,
        },
        "inputs": [input_record],
        "runtime": {
            "interface": "BioNeMo Framework CLI/API - not run",
            "container": "not-selected",
            "hardware": "GPU runtime not selected",
            "provider": "bionemo-framework",
            "parameters": {
                "artifact_contract": ARTIFACT_CONTRACT_VERSION,
                "include_hiddens": True,
                "include_embeddings": True,
                "pooling_method": "mean_non_padding_hidden_states",
                "max_residues": config.max_residues,
                "precision": "record-at-runtime",
                "silent_truncation": False,
                "hra_input_handling": "explicit-window-before-provider",
                "upstream_long_sequence_handling": (
                    "may automatically truncate; HRA must supply the reviewed window"
                ),
            },
        },
        "outputs": {
            "path": None,
            "confidence_measures": [],
            "generated_at": None,
            "embedding": None,
        },
        "evaluation": {
            "method": "provider contract and input-parity review before execution",
            "limitations": [
                "This is a plan only; BioNeMo has not run and no NVIDIA output exists.",
                "The candidate checkpoint is not asserted to contain the same weights as the local Meta ESM-2 checkpoint.",
                "Provider parity is an engineering comparison, not evidence of protein function, similarity, or clinical meaning.",
            ],
        },
    }


def _check(
    field: str,
    reference: object | None,
    candidate: object | None,
    *,
    unavailable_if_missing: bool = True,
    comparable: bool = True,
    explanation: str,
) -> ProviderParityCheck:
    if unavailable_if_missing and (reference is None or candidate is None):
        status: ParityStatus = "not-available"
    elif not comparable:
        status = "not-comparable"
    else:
        status = "matched" if reference == candidate else "different"
    return ProviderParityCheck(
        field=field,
        status=status,
        reference=reference,
        candidate=candidate,
        explanation=explanation,
    )


def build_provider_parity_report(
    reference_manifest: dict[str, object],
    candidate_manifest: dict[str, object],
    *,
    generated_at: date | None = None,
) -> ProviderParityReport:
    """Compare provenance fields without treating vectors as scientific evidence."""

    reference = normalize_embedding_manifest(reference_manifest)
    candidate = normalize_embedding_manifest(candidate_manifest)
    same_checkpoint = (
        reference.model.provider == candidate.model.provider
        and reference.model.name == candidate.model.name
        and reference.model.version == candidate.model.version
    )
    candidate_generated = candidate.execution_status == "generated"
    checks = (
        _check(
            "selected_sequence_checksum",
            reference.input.selected_sequence_checksum,
            candidate.input.selected_sequence_checksum,
            explanation="Confirms whether both providers receive the same selected residues.",
        ),
        _check(
            "sequence_window",
            (reference.input.window_start, reference.input.window_end),
            (candidate.input.window_start, candidate.input.window_end),
            explanation="Compares the explicit one-based sequence coordinates.",
        ),
        _check(
            "selected_sequence_length",
            reference.input.selected_sequence_length,
            candidate.input.selected_sequence_length,
            explanation="Compares the number of residues submitted to each provider.",
        ),
        _check(
            "silent_truncation",
            reference.preprocessing.silent_truncation,
            candidate.preprocessing.silent_truncation,
            explanation="Both HRA plans must reject unrecorded provider-side truncation.",
        ),
        _check(
            "model_identity",
            reference.model.model_dump(mode="json"),
            candidate.model.model_dump(mode="json"),
            explanation="Provider, checkpoint name, and recorded revision are compared literally.",
        ),
        _check(
            "checkpoint_weight_identity",
            reference.model.version,
            candidate.model.version,
            comparable=same_checkpoint,
            explanation="Weight equality is not assumed from a shared ESM-2 architecture or parameter count.",
        ),
        _check(
            "pooling_method",
            reference.preprocessing.pooling_method,
            candidate.preprocessing.pooling_method,
            comparable=(
                reference.preprocessing.pooling_method
                == candidate.preprocessing.pooling_method
            ),
            explanation="Similar averaging labels still require implementation-level validation.",
        ),
        _check(
            "execution_status",
            reference.execution_status,
            candidate.execution_status,
            comparable=candidate_generated,
            explanation="A planned provider cannot be compared with generated runtime output.",
        ),
        _check(
            "embedding_dimensions",
            reference.output.dimensions,
            candidate.output.dimensions,
            explanation="Output dimensions can be compared only after both providers run.",
        ),
        _check(
            "token_embeddings_shape",
            reference.output.token_embeddings_shape,
            candidate.output.token_embeddings_shape,
            explanation="Tensor shapes can be compared only after both providers run.",
        ),
        _check(
            "vector_checksum",
            reference.output.vector_checksum,
            candidate.output.vector_checksum,
            explanation="Checksums are reproducibility metadata, not a scientific similarity measure.",
        ),
        _check(
            "runtime_hardware",
            reference.runtime.hardware,
            candidate.runtime.hardware,
            comparable=candidate_generated,
            explanation="Runtime hardware is descriptive provenance and need not be identical.",
        ),
        _check(
            "runtime_precision",
            reference.runtime.precision,
            candidate.runtime.precision,
            explanation="Numerical precision must be recorded before output comparison.",
        ),
    )
    summary = {
        status: sum(check.status == status for check in checks)
        for status in ("matched", "different", "not-available", "not-comparable")
    }
    input_contract_ready = all(check.status == "matched" for check in checks[:4])
    overall_status = (
        "input-compatible-plan-only"
        if input_contract_ready and not candidate_generated
        else "review-required"
    )
    return ProviderParityReport(
        report_id=(
            f"parity-{reference.source_experiment_id}--{candidate.source_experiment_id}"
        ),
        generated_at=generated_at or date.today(),
        overall_status=overall_status,
        reference=reference,
        candidate=candidate,
        checks=checks,
        summary=summary,
        readiness={
            "input_contract_ready": input_contract_ready,
            "candidate_provider_executed": candidate_generated,
            "output_comparison_available": all(
                check.status in {"matched", "different"}
                for check in checks[8:11]
            ),
        },
        source_documents=(BIONEMO_MODEL_URL, BIONEMO_INFERENCE_URL),
        limitations=(
            "The report compares engineering provenance fields, not biological meaning.",
            "A matching input contract does not establish matching checkpoints, vectors, or downstream performance.",
            "No function, structure, causality, treatment, safety, efficacy, or clinical conclusion is produced.",
        ),
    )
