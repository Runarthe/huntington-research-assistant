"""Portable, gated BioNeMo execution bundles and result validation."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import struct
import zipfile
from copy import deepcopy
from datetime import date
from importlib.resources import files

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from labs.protein_intelligence.local_esm2 import LocalESM2Config, select_sequence_window
from labs.protein_intelligence.manifests import validate_manifest
from labs.protein_intelligence.bionemo_image_review import (
    BIONEMO_FRAMEWORK_CONTRACT,
    BioNeMoContainerReview,
    reviewed_bionemo_container,
)
from labs.protein_intelligence.provider_parity import (
    BIONEMO_INFERENCE_URL,
    BIONEMO_MODEL_VERSION,
    planned_bionemo_esm2_manifest,
)
from labs.protein_intelligence.sequences import ProteinSequenceRecord


BIONEMO_BUNDLE_VERSION = "hra-bionemo-execution-bundle.v1"
BIONEMO_RESULT_VERSION = "hra-bionemo-result.v1"
BIONEMO_PREREQUISITES_URL = (
    "https://docs.nvidia.com/bionemo-framework/latest/main/getting-started/"
    "pre-reqs/index.html"
)
BIONEMO_RUNTIME_FILES = (
    "README.md",
    "export_hra_result.py",
    "prepare_checkpoint.py",
    "run_container.sh",
    "run_inside_container.sh",
)


class BioNeMoExecutionError(ValueError):
    """Raised when a bundle or imported BioNeMo result violates the contract."""


class BioNeMoExecutionConfig(BaseModel):
    """Non-secret, reviewable settings for one external BioNeMo run."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    framework_contract: str = BIONEMO_FRAMEWORK_CONTRACT
    checkpoint_tag: str = BIONEMO_MODEL_VERSION
    precision: str = "bf16-mixed"
    micro_batch_size: int = Field(default=1, ge=1)
    num_gpus: int = Field(default=1, ge=1)
    num_nodes: int = Field(default=1, ge=1)
    include_hiddens: bool = True
    include_embeddings: bool = True
    include_input_ids: bool = True
    include_logits: bool = False


def _sha256(data: bytes) -> str:
    return f"sha256:{hashlib.sha256(data).hexdigest()}"


def _is_sha256(value: object, *, image_reference: bool = False) -> bool:
    if not isinstance(value, str):
        return False
    pattern = r".+@sha256:[0-9a-fA-F]{64}" if image_reference else r"sha256:[0-9a-fA-F]{64}"
    return re.fullmatch(pattern, value) is not None


def _selected_sequence(
    record: ProteinSequenceRecord,
    config: LocalESM2Config,
) -> str:
    selected, _, _ = select_sequence_window(
        record.sequence,
        start=config.window_start,
        length=config.window_length,
        max_residues=config.max_residues,
    )
    return selected


def _input_csv(sequence: str) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(["sequences"])
    writer.writerow([sequence])
    return stream.getvalue().encode("ascii")


def _runtime_template(name: str) -> bytes:
    resource = files("labs.protein_intelligence").joinpath("bionemo_runtime", name)
    return resource.read_bytes()


def _zip_files(bundle_files: dict[str, bytes]) -> bytes:
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, mode="w", compression=zipfile.ZIP_DEFLATED) as output:
        for name in sorted(bundle_files):
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (
                0o100755 << 16 if name.endswith(".sh") else 0o100644 << 16
            )
            output.writestr(info, bundle_files[name])
    return archive.getvalue()


def build_bionemo_execution_bundle(
    record: ProteinSequenceRecord,
    local_config: LocalESM2Config,
    execution_config: BioNeMoExecutionConfig | None = None,
    *,
    planned_at: date | None = None,
) -> bytes:
    """Build a deterministic bundle for explicit execution on a reviewed GPU host."""

    execution = execution_config or BioNeMoExecutionConfig()
    if execution.checkpoint_tag != BIONEMO_MODEL_VERSION:
        raise BioNeMoExecutionError(
            "The v0.11 bundle supports only its reviewed BioNeMo checkpoint tag."
        )
    selected = _selected_sequence(record, local_config)
    plan = planned_bionemo_esm2_manifest(record, local_config, planned_at=planned_at)
    expected_checksum = plan["inputs"][0]["selected_sequence_checksum"]
    if _sha256(selected.encode("ascii")) != expected_checksum:
        raise BioNeMoExecutionError("Selected sequence does not match the plan checksum.")

    execution_payload = {
        "schema_version": BIONEMO_BUNDLE_VERSION,
        "framework_contract": execution.framework_contract,
        "official_inference_documentation": BIONEMO_INFERENCE_URL,
        "official_prerequisites": BIONEMO_PREREQUISITES_URL,
        "settings": execution.model_dump(mode="json"),
        "container_review": reviewed_bionemo_container().model_dump(mode="json"),
        "security": {
            "contains_credentials": False,
            "container_image_must_match_review": True,
            "image_pull_policy": "never",
            "registry_authentication_managed_by_hra": False,
        },
    }
    bundle_files: dict[str, bytes] = {
        "input.csv": _input_csv(selected),
        "plan.json": json.dumps(plan, indent=2, sort_keys=True).encode("utf-8"),
        "execution.json": json.dumps(
            execution_payload,
            indent=2,
            sort_keys=True,
        ).encode("utf-8"),
    }
    for name in BIONEMO_RUNTIME_FILES:
        bundle_files[name] = _runtime_template(name)

    manifest = {
        "schema_version": BIONEMO_BUNDLE_VERSION,
        "experiment_id": plan["experiment_id"],
        "created_at": (planned_at or date.today()).isoformat(),
        "files": {
            name: _sha256(content) for name, content in sorted(bundle_files.items())
        },
        "limitations": [
            "The bundle has not executed BioNeMo or pulled the reviewed container image.",
            "Execution requires a separately reviewed Linux, Docker, and NVIDIA GPU environment.",
            "The pinned prebuilt container is archived and is retained only for this bounded legacy contract.",
            "Generated artifacts are computational provenance, not biomedical evidence.",
        ],
    }
    bundle_files["bundle-manifest.json"] = json.dumps(
        manifest,
        indent=2,
        sort_keys=True,
    ).encode("utf-8")
    return _zip_files(bundle_files)


def validate_bionemo_execution_bundle(archive: bytes) -> dict[str, object]:
    """Validate bundle membership and checksums without executing any file."""

    try:
        with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
            names = set(bundle.namelist())
            required = {
                "bundle-manifest.json",
                "execution.json",
                "input.csv",
                "plan.json",
                *BIONEMO_RUNTIME_FILES,
            }
            if names != required:
                raise BioNeMoExecutionError("Bundle file set does not match the contract.")
            manifest = json.loads(bundle.read("bundle-manifest.json"))
            if manifest.get("schema_version") != BIONEMO_BUNDLE_VERSION:
                raise BioNeMoExecutionError("Unknown BioNeMo bundle version.")
            recorded = manifest.get("files")
            if not isinstance(recorded, dict):
                raise BioNeMoExecutionError("Bundle checksum index is missing.")
            for name in sorted(required - {"bundle-manifest.json"}):
                if recorded.get(name) != _sha256(bundle.read(name)):
                    raise BioNeMoExecutionError(f"Bundle checksum mismatch: {name}")
            for name in BIONEMO_RUNTIME_FILES:
                if bundle.read(name) != _runtime_template(name):
                    raise BioNeMoExecutionError(
                        f"Bundle runtime template does not match this HRA version: {name}"
                    )

            plan = json.loads(bundle.read("plan.json"))
            validate_manifest(plan)
            if plan.get("model", {}).get("version") != BIONEMO_MODEL_VERSION:
                raise BioNeMoExecutionError("Bundle checkpoint does not match the contract.")
            execution = json.loads(bundle.read("execution.json"))
            if execution.get("schema_version") != BIONEMO_BUNDLE_VERSION:
                raise BioNeMoExecutionError("Execution settings version is invalid.")
            if execution.get("framework_contract") != BIONEMO_FRAMEWORK_CONTRACT:
                raise BioNeMoExecutionError("BioNeMo framework contract is invalid.")
            settings = execution.get("settings")
            if not isinstance(settings, dict):
                raise BioNeMoExecutionError("Execution settings are missing.")
            BioNeMoExecutionConfig.model_validate(settings)
            review_payload = execution.get("container_review")
            if not isinstance(review_payload, dict):
                raise BioNeMoExecutionError("Container review provenance is missing.")
            reviewed = BioNeMoContainerReview.model_validate(review_payload)
            if reviewed != reviewed_bionemo_container():
                raise BioNeMoExecutionError(
                    "Container review does not match this HRA version."
                )
            security = execution.get("security")
            expected_security = {
                "contains_credentials": False,
                "container_image_must_match_review": True,
                "image_pull_policy": "never",
                "registry_authentication_managed_by_hra": False,
            }
            if security != expected_security:
                raise BioNeMoExecutionError("Bundle security policy is invalid.")

            input_rows = list(
                csv.DictReader(
                    io.StringIO(bundle.read("input.csv").decode("ascii"))
                )
            )
            if len(input_rows) != 1 or set(input_rows[0]) != {"sequences"}:
                raise BioNeMoExecutionError("Bundle input CSV contract is invalid.")
            selected = input_rows[0]["sequences"]
            plan_inputs = plan.get("inputs")
            plan_input = plan_inputs[0] if isinstance(plan_inputs, list) else {}
            if (
                _sha256(selected.encode("ascii"))
                != plan_input.get("selected_sequence_checksum")
                or len(selected) != plan_input.get("selected_sequence_length")
            ):
                raise BioNeMoExecutionError("Bundle input does not match its plan.")
            return manifest
    except (
        OSError,
        UnicodeDecodeError,
        zipfile.BadZipFile,
        json.JSONDecodeError,
        ValidationError,
    ) as exc:
        raise BioNeMoExecutionError("BioNeMo bundle is not a valid archive.") from exc


def validate_bionemo_result_manifest(
    result: dict[str, object],
    expected_plan: dict[str, object],
) -> dict[str, object]:
    """Validate imported provenance without loading a model or raw tensor file."""

    validate_manifest(result)
    if result.get("schema_version") != BIONEMO_RESULT_VERSION:
        raise BioNeMoExecutionError("Unknown BioNeMo result version.")
    if result.get("status") != "generated":
        raise BioNeMoExecutionError("Imported BioNeMo result must be generated.")
    if result.get("experiment_id") != expected_plan.get("experiment_id"):
        raise BioNeMoExecutionError("Result experiment ID does not match the plan.")
    if result.get("model") != expected_plan.get("model"):
        raise BioNeMoExecutionError("Result model identity does not match the plan.")
    if result.get("inputs") != expected_plan.get("inputs"):
        raise BioNeMoExecutionError("Result sequence provenance does not match the plan.")

    runtime = result.get("runtime")
    if not isinstance(runtime, dict):
        raise BioNeMoExecutionError("Result runtime metadata is missing.")
    interface = runtime.get("interface")
    if interface not in {"bionemo-framework-container", "fixture-validation"}:
        raise BioNeMoExecutionError("Result runtime interface is not accepted.")
    if interface == "bionemo-framework-container":
        container = runtime.get("container")
        if not _is_sha256(container, image_reference=True):
            raise BioNeMoExecutionError(
                "Generated BioNeMo result must record its immutable container digest."
            )

    outputs = result.get("outputs")
    embedding = outputs.get("embedding") if isinstance(outputs, dict) else None
    if not isinstance(embedding, dict):
        raise BioNeMoExecutionError("Result embedding metadata is missing.")
    if "vector" in embedding:
        raise BioNeMoExecutionError("Import checksum metadata, not the full embedding vector.")
    dimensions = embedding.get("dimensions")
    if not isinstance(dimensions, int) or dimensions <= 0:
        raise BioNeMoExecutionError("Embedding dimensions must be positive.")
    shape = embedding.get("token_embeddings_shape")
    if (
        not isinstance(shape, list)
        or not shape
        or any(not isinstance(value, int) or value <= 0 for value in shape)
    ):
        raise BioNeMoExecutionError("Token embedding shape is invalid.")
    checksum = embedding.get("checksum")
    if not _is_sha256(checksum):
        raise BioNeMoExecutionError("Embedding checksum is missing or invalid.")
    raw_checksum = outputs.get("raw_output_checksum")
    if not _is_sha256(raw_checksum):
        raise BioNeMoExecutionError("Raw output checksum is missing or invalid.")
    return deepcopy(result)


def load_bionemo_result_manifest(
    payload: bytes,
    expected_plan: dict[str, object],
) -> dict[str, object]:
    """Parse a bounded JSON result and validate it against its exact plan."""

    if len(payload) > 1_000_000:
        raise BioNeMoExecutionError("BioNeMo result JSON exceeds the 1 MB limit.")
    try:
        parsed = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BioNeMoExecutionError("BioNeMo result is not valid UTF-8 JSON.") from exc
    if not isinstance(parsed, dict):
        raise BioNeMoExecutionError("BioNeMo result JSON must contain an object.")
    return validate_bionemo_result_manifest(parsed, expected_plan)


def fixture_bionemo_result_manifest(
    expected_plan: dict[str, object],
    *,
    generated_at: date | None = None,
) -> dict[str, object]:
    """Create deterministic non-model output for importer and parity tests."""

    candidate = deepcopy(expected_plan)
    input_record = candidate["inputs"][0]
    length = int(input_record["selected_sequence_length"])
    fixture_vector = (0.125, 0.25, 0.5, 1.0)
    vector_bytes = struct.pack(f"<{len(fixture_vector)}f", *fixture_vector)
    candidate["schema_version"] = BIONEMO_RESULT_VERSION
    candidate["status"] = "generated"
    candidate["runtime"] = {
        "interface": "fixture-validation",
        "container": "not-applicable",
        "hardware": "deterministic fixture",
        "provider": "fixture-bionemo-contract",
        "dependencies": {"bionemo-framework": "not-run"},
        "parameters": {
            "precision": "fixture-fp32",
            "pooling_method": "mean_non_padding_hidden_states",
            "max_residues": 1022,
            "silent_truncation": False,
        },
    }
    candidate["outputs"] = {
        "path": "fixture://predictions__rank_0__dp_rank_0.pt",
        "raw_output_checksum": _sha256(b"fixture-bionemo-output"),
        "confidence_measures": [],
        "generated_at": (generated_at or date.today()).isoformat(),
        "embedding": {
            "dimensions": len(fixture_vector),
            "checksum": _sha256(vector_bytes),
            "token_embeddings_shape": [1, length + 2, len(fixture_vector)],
            "residue_token_count": length,
        },
    }
    candidate["evaluation"] = {
        "method": "deterministic result-import and parity plumbing fixture",
        "limitations": [
            "No BioNeMo model, container, NVIDIA GPU, or provider executed.",
            "Fixture tensor metadata and checksums are not scientific model output.",
            "No biological, treatment, safety, efficacy, or clinical claim is produced.",
        ],
    }
    return validate_bionemo_result_manifest(candidate, expected_plan)
