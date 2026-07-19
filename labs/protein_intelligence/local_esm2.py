"""Optional local ESM-2 inference with explicit provenance and claim boundaries."""

from __future__ import annotations

import hashlib
import importlib.util
import platform
import struct
from dataclasses import dataclass
from datetime import date
from importlib.metadata import PackageNotFoundError, version
from typing import Protocol

from labs.protein_intelligence.sequences import ProteinSequenceRecord


DEFAULT_ESM2_MODEL = "facebook/esm2_t6_8M_UR50D"
DEFAULT_ESM2_REVISION = "c731040fcd8d73dceaa04b0a8e6329b345b0f5df"
DEFAULT_MAX_RESIDUES = 1022
MODEL_URL = f"https://huggingface.co/{DEFAULT_ESM2_MODEL}"


class LocalESM2Error(RuntimeError):
    """Base error for bounded local ESM-2 execution."""


class LocalESM2DependencyError(LocalESM2Error):
    """Raised when optional model dependencies are unavailable."""


class SequenceWindowError(LocalESM2Error):
    """Raised when sequence input would require implicit truncation."""


@dataclass(frozen=True)
class LocalESM2Status:
    available: bool
    missing_packages: tuple[str, ...]
    installed_versions: dict[str, str]
    model_id: str = DEFAULT_ESM2_MODEL
    model_revision: str = DEFAULT_ESM2_REVISION


@dataclass(frozen=True)
class LocalESM2Config:
    model_id: str = DEFAULT_ESM2_MODEL
    model_revision: str = DEFAULT_ESM2_REVISION
    max_residues: int = DEFAULT_MAX_RESIDUES
    window_start: int = 1
    window_length: int | None = None
    pooling_method: str = "mean_residue_tokens"
    device: str = "auto"
    local_files_only: bool = False

    def __post_init__(self) -> None:
        if self.max_residues <= 0:
            raise ValueError("max_residues must be positive.")
        if self.window_start <= 0:
            raise ValueError("window_start uses one-based coordinates and must be positive.")
        if self.window_length is not None and self.window_length <= 0:
            raise ValueError("window_length must be positive when provided.")
        if self.pooling_method != "mean_residue_tokens":
            raise ValueError("Only mean_residue_tokens pooling is supported in v0.10.")
        if self.device not in {"auto", "cpu", "cuda"}:
            raise ValueError("device must be one of: auto, cpu, cuda.")


@dataclass(frozen=True)
class RuntimeEmbeddingResult:
    vector: tuple[float, ...]
    token_embeddings_shape: tuple[int, ...]
    residue_token_count: int
    device: str
    hardware: str
    torch_version: str
    transformers_version: str


class ESM2Runtime(Protocol):
    def embed(self, sequence: str, config: LocalESM2Config) -> RuntimeEmbeddingResult:
        """Return a pooled representation without attaching biological meaning."""


@dataclass(frozen=True)
class LocalESM2EmbeddingArtifact:
    sequence_record: ProteinSequenceRecord
    config: LocalESM2Config
    selected_sequence: str
    window_start: int
    window_end: int
    runtime: RuntimeEmbeddingResult
    generated_at: date

    @property
    def vector_checksum(self) -> str:
        packed = struct.pack(f"<{len(self.runtime.vector)}f", *self.runtime.vector)
        return f"sha256:{hashlib.sha256(packed).hexdigest()}"


def local_esm2_status() -> LocalESM2Status:
    required = ("torch", "transformers", "safetensors")
    missing = tuple(name for name in required if importlib.util.find_spec(name) is None)
    installed: dict[str, str] = {}
    for package in required:
        if package in missing:
            continue
        try:
            installed[package] = version(package)
        except PackageNotFoundError:
            missing += (package,)
    return LocalESM2Status(
        available=not missing,
        missing_packages=tuple(sorted(set(missing))),
        installed_versions=installed,
    )


def select_sequence_window(
    sequence: str,
    *,
    start: int,
    length: int | None,
    max_residues: int = DEFAULT_MAX_RESIDUES,
) -> tuple[str, int, int]:
    """Select a one-based window and reject any implicit truncation."""

    if start <= 0:
        raise SequenceWindowError("Sequence window start must be one or greater.")
    start_index = start - 1
    if start_index >= len(sequence):
        raise SequenceWindowError("Sequence window starts after the end of the sequence.")
    selected_length = len(sequence) - start_index if length is None else length
    if selected_length <= 0:
        raise SequenceWindowError("Sequence window length must be positive.")
    end_index = start_index + selected_length
    if end_index > len(sequence):
        raise SequenceWindowError("Sequence window extends past the end of the sequence.")
    if selected_length > max_residues:
        raise SequenceWindowError(
            f"Selected sequence has {selected_length} residues; the configured limit is "
            f"{max_residues}. Choose an explicit window instead of truncating silently."
        )
    return sequence[start_index:end_index], start, end_index


class HuggingFaceESM2Runtime:
    """Lazy PyTorch/Transformers runtime loaded only during an explicit run."""

    def embed(self, sequence: str, config: LocalESM2Config) -> RuntimeEmbeddingResult:
        status = local_esm2_status()
        if not status.available:
            missing = ", ".join(status.missing_packages)
            raise LocalESM2DependencyError(
                f"Optional local ESM-2 dependencies are missing: {missing}."
            )

        import torch
        import transformers
        from transformers import AutoModelForMaskedLM, AutoTokenizer

        if config.device == "cuda" and not torch.cuda.is_available():
            raise LocalESM2Error("CUDA was requested, but PyTorch cannot access a CUDA device.")
        device = (
            "cuda"
            if config.device == "auto" and torch.cuda.is_available()
            else config.device
        )
        if device == "auto":
            device = "cpu"

        tokenizer = AutoTokenizer.from_pretrained(
            config.model_id,
            revision=config.model_revision,
            local_files_only=config.local_files_only,
        )
        model = AutoModelForMaskedLM.from_pretrained(
            config.model_id,
            revision=config.model_revision,
            local_files_only=config.local_files_only,
        )
        model.eval()
        model.to(device)
        encoded = tokenizer(sequence, return_tensors="pt", truncation=False)
        encoded = {name: tensor.to(device) for name, tensor in encoded.items()}

        with torch.inference_mode():
            hidden = model.base_model(**encoded).last_hidden_state

        token_ids = encoded["input_ids"][0].detach().cpu().tolist()
        special_mask = tokenizer.get_special_tokens_mask(
            token_ids,
            already_has_special_tokens=True,
        )
        residue_mask = torch.tensor(
            [not is_special for is_special in special_mask],
            dtype=torch.bool,
            device=device,
        )
        attention_mask = encoded.get("attention_mask")
        if attention_mask is not None:
            residue_mask &= attention_mask[0].bool()
        residue_embeddings = hidden[0][residue_mask]
        if residue_embeddings.shape[0] != len(sequence):
            raise LocalESM2Error(
                "Tokenizer residue count did not match the selected sequence length."
            )
        pooled = residue_embeddings.mean(dim=0).detach().float().cpu()
        hardware = (
            torch.cuda.get_device_name(torch.cuda.current_device())
            if device == "cuda"
            else platform.processor() or platform.machine() or "CPU"
        )
        return RuntimeEmbeddingResult(
            vector=tuple(float(value) for value in pooled.tolist()),
            token_embeddings_shape=tuple(int(value) for value in hidden.shape),
            residue_token_count=int(residue_embeddings.shape[0]),
            device=device,
            hardware=hardware,
            torch_version=str(torch.__version__),
            transformers_version=str(transformers.__version__),
        )


class LocalESM2Provider:
    provider = "huggingface-local"

    def __init__(
        self,
        config: LocalESM2Config | None = None,
        *,
        runtime: ESM2Runtime | None = None,
        generated_at: date | None = None,
    ) -> None:
        self.config = config or LocalESM2Config()
        self.runtime = runtime or HuggingFaceESM2Runtime()
        self.generated_at = generated_at or date.today()

    def embed(self, record: ProteinSequenceRecord) -> LocalESM2EmbeddingArtifact:
        selected, start, end = select_sequence_window(
            record.sequence,
            start=self.config.window_start,
            length=self.config.window_length,
            max_residues=self.config.max_residues,
        )
        runtime_result = self.runtime.embed(selected, self.config)
        return LocalESM2EmbeddingArtifact(
            sequence_record=record,
            config=self.config,
            selected_sequence=selected,
            window_start=start,
            window_end=end,
            runtime=runtime_result,
            generated_at=self.generated_at,
        )


def _sequence_input(
    record: ProteinSequenceRecord,
    selected_sequence: str,
    start: int,
    end: int,
) -> dict[str, object]:
    selected_checksum = hashlib.sha256(selected_sequence.encode("ascii")).hexdigest()
    return {
        "identifier": record.accession,
        "entity_id": record.target.entity_id,
        "symbol": record.target.symbol,
        "organism": record.target.organism,
        "source_url": record.source_url,
        "retrieved_at": record.retrieved_at.isoformat(),
        "checksum": record.checksum,
        "sequence_length": record.sequence_length,
        "selected_sequence_checksum": f"sha256:{selected_checksum}",
        "selected_sequence_length": len(selected_sequence),
        "window_start": start,
        "window_end": end,
        "input_handling": (
            "full-sequence"
            if start == 1 and end == record.sequence_length
            else "explicit-window"
        ),
    }


def planned_local_esm2_manifest(
    record: ProteinSequenceRecord,
    config: LocalESM2Config,
    *,
    planned_at: date | None = None,
) -> dict[str, object]:
    selected, start, end = select_sequence_window(
        record.sequence,
        start=config.window_start,
        length=config.window_length,
        max_residues=config.max_residues,
    )
    input_record = _sequence_input(record, selected, start, end)
    sequence_fingerprint = str(input_record["selected_sequence_checksum"]).split(
        ":",
        1,
    )[1][:12]
    return {
        "schema_version": "0.2",
        "experiment_id": (
            f"local-esm2-{record.target.symbol.lower()}-{start}-{end}-"
            f"{sequence_fingerprint}"
        ),
        "status": "planned",
        "purpose": "Generate a local protein embedding with explicit provenance.",
        "component_type": "foundation_model",
        "model": {
            "provider": "Hugging Face Transformers / local PyTorch",
            "name": config.model_id,
            "version": config.model_revision,
            "licence": "MIT",
            "source_url": MODEL_URL,
        },
        "inputs": [input_record],
        "runtime": {
            "interface": "local-python",
            "container": "not-applicable",
            "hardware": "selected-at-runtime",
            "parameters": {
                "device": config.device,
                "pooling_method": config.pooling_method,
                "max_residues": config.max_residues,
                "local_files_only": config.local_files_only,
                "silent_truncation": False,
            },
        },
        "outputs": {
            "path": None,
            "confidence_measures": [],
            "generated_at": (planned_at or date.today()).isoformat(),
            "embedding": None,
        },
        "evaluation": {
            "method": "planned provenance and input-boundary review",
            "limitations": [
                "This plan does not contain model output.",
                "An embedding is a computational representation, not a biological or clinical conclusion.",
            ],
        },
    }


def local_esm2_manifest(artifact: LocalESM2EmbeddingArtifact) -> dict[str, object]:
    runtime = artifact.runtime
    config = artifact.config
    record = artifact.sequence_record
    manifest = planned_local_esm2_manifest(record, config, planned_at=artifact.generated_at)
    manifest["status"] = "generated"
    manifest["runtime"] = {
        "interface": "local-python",
        "container": "not-applicable",
        "hardware": runtime.hardware,
        "provider": "huggingface-local",
        "dependencies": {
            "torch": runtime.torch_version,
            "transformers": runtime.transformers_version,
        },
        "parameters": {
            "device": runtime.device,
            "pooling_method": config.pooling_method,
            "max_residues": config.max_residues,
            "local_files_only": config.local_files_only,
            "silent_truncation": False,
        },
    }
    manifest["outputs"] = {
        "path": None,
        "confidence_measures": [],
        "generated_at": artifact.generated_at.isoformat(),
        "embedding": {
            "vector": list(runtime.vector),
            "dimensions": len(runtime.vector),
            "checksum": artifact.vector_checksum,
            "token_embeddings_shape": list(runtime.token_embeddings_shape),
            "residue_token_count": runtime.residue_token_count,
        },
    }
    manifest["evaluation"] = {
        "method": "shape, checksum, provenance, and optional repeat-run comparison",
        "reproducibility_check": {
            "status": "baseline-recorded",
            "compared_checksum": None,
        },
        "limitations": [
            "The pooled vector has not been evaluated for a downstream scientific task.",
            "No function, similarity, structure, causality, treatment relevance, or clinical claim is produced.",
        ],
    }
    return manifest


def compare_embedding_manifests(
    previous: dict[str, object],
    current: dict[str, object],
) -> str:
    """Compare two artifact checksums from the same planned experiment."""

    if previous.get("experiment_id") != current.get("experiment_id"):
        return "not-comparable"
    try:
        previous_checksum = previous["outputs"]["embedding"]["checksum"]
        current_checksum = current["outputs"]["embedding"]["checksum"]
    except (KeyError, TypeError):
        return "not-comparable"
    return "matched" if previous_checksum == current_checksum else "different"
