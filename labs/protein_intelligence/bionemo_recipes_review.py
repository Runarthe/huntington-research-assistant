"""Pinned review of the maintained BioNeMo Recipes ESM-2 path."""

from __future__ import annotations

import hashlib
from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict

from labs.protein_intelligence.local_esm2 import (
    DEFAULT_MAX_RESIDUES,
    LocalESM2Config,
    select_sequence_window,
)
from labs.protein_intelligence.sequences import ProteinSequenceRecord


BIONEMO_RECIPES_REVIEW_VERSION = "hra-bionemo-recipes-review.v2"
BIONEMO_RECIPES_VERSION = "v3.0.0"
BIONEMO_RECIPES_COMMIT = "66c150f2920d6155697d4edfc87289f239b65022"
BIONEMO_RECIPES_RELEASE_URL = (
    "https://github.com/NVIDIA-BioNeMo/bionemo-recipes/releases/tag/v3.0.0"
)
BIONEMO_RECIPES_ESM2_DOCS_URL = (
    "https://docs.nvidia.com/bionemo-recipes/latest/main/models/ESM-2/"
)
BIONEMO_RECIPES_INFERENCE_URL = (
    "https://docs.nvidia.com/bionemo-recipes/latest/main/recipes/recipes/"
    "esm2_native_te/"
)
BIONEMO_RECIPES_MODEL_ID = "nvidia/esm2_t6_8M_UR50D"
BIONEMO_RECIPES_MODEL_REVISION = "3674a6acb6c217bbeff709d182a11b196125dfc3"
BIONEMO_RECIPES_MODEL_URL = f"https://huggingface.co/{BIONEMO_RECIPES_MODEL_ID}"
BIONEMO_RECIPES_REMOTE_CODE_BLOB = "bbef1bf7708711a0dd9b855f68d094de88024f53"
BIONEMO_RECIPES_CONFIG_BLOB = "c6595500ba1a74526a63f8ff2e351c66552446b7"
BIONEMO_RECIPES_WEIGHTS_SHA256 = (
    "89dfb9aa2b595936aaccdc50b6b50f3c353c520f0e7bdd54487f5fa00f05a0ed"
)


class BioNeMoRecipesFileReview(BaseModel):
    """One relevant immutable file identity from the public model repository."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    path: str
    size_bytes: int
    git_blob_id: str
    lfs_sha256: str | None = None
    contains_executable_model_code: bool = False


class BioNeMoRecipesReview(BaseModel):
    """Review boundary for a maintained path that HRA has not executed."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: str = BIONEMO_RECIPES_REVIEW_VERSION
    status: Literal["reviewed-runtime-prepared"] = "reviewed-runtime-prepared"
    reviewed_on: date = date(2026, 7, 19)
    recipes_version: str = BIONEMO_RECIPES_VERSION
    recipes_commit: str = BIONEMO_RECIPES_COMMIT
    recipes_license: Literal["Apache-2.0"] = "Apache-2.0"
    model_id: str = BIONEMO_RECIPES_MODEL_ID
    model_revision: str = BIONEMO_RECIPES_MODEL_REVISION
    model_card_license: Literal["MIT"] = "MIT"
    repository_license_file: Literal["Apache-2.0"] = "Apache-2.0"
    license_consistency: Literal["review-required"] = "review-required"
    model_public: bool = True
    model_gated: bool = False
    model_parameters: int = 7_512_353
    model_layers: int = 6
    model_hidden_size: int = 320
    model_max_residues: int = DEFAULT_MAX_RESIDUES
    runtime_interface: Literal["Hugging Face Transformers"] = (
        "Hugging Face Transformers"
    )
    transformer_engine_required: bool = True
    remote_code_required: bool = True
    remote_code_reviewed_in_full: bool = False
    remote_code_executed: bool = False
    model_weights_downloaded_during_review: bool = True
    model_weights_retained_by_repository: bool = False
    model_weights_loaded: bool = False
    inference_executed: bool = False
    network_calls_made_during_review: bool = True
    credentials_used_during_review: bool = False
    files: tuple[BioNeMoRecipesFileReview, ...] = (
        BioNeMoRecipesFileReview(
            path="config.json",
            size_bytes=1_360,
            git_blob_id=BIONEMO_RECIPES_CONFIG_BLOB,
        ),
        BioNeMoRecipesFileReview(
            path="esm_nv.py",
            size_bytes=38_557,
            git_blob_id=BIONEMO_RECIPES_REMOTE_CODE_BLOB,
            contains_executable_model_code=True,
        ),
        BioNeMoRecipesFileReview(
            path="model.safetensors",
            size_bytes=30_058_964,
            git_blob_id="c24778848ab73ea08c6ca44574b005dd33ae6014",
            lfs_sha256=BIONEMO_RECIPES_WEIGHTS_SHA256,
        ),
    )
    publisher_weight_statement: str = (
        "NVIDIA reports that the converted checkpoint uses the original ESM-2 "
        "weights with outputs identical within numerical precision."
    )
    weight_identity_verified_by_hra: bool = False
    sources: dict[str, str] = {
        "recipes_release": BIONEMO_RECIPES_RELEASE_URL,
        "recipes_esm2_docs": BIONEMO_RECIPES_ESM2_DOCS_URL,
        "recipes_inference_docs": BIONEMO_RECIPES_INFERENCE_URL,
        "model_card": BIONEMO_RECIPES_MODEL_URL,
        "pinned_model_tree": (
            f"{BIONEMO_RECIPES_MODEL_URL}/tree/{BIONEMO_RECIPES_MODEL_REVISION}"
        ),
    }
    limitations: tuple[str, ...] = (
        "The model-card metadata says MIT, while the repository LICENSE and source header identify Apache 2.0; HRA does not resolve this licence discrepancy.",
        "HRA has not pulled the reviewed base image, built the derived image, or run inference.",
        "Publisher-reported checkpoint equivalence has not been independently reproduced by HRA.",
        "A model embedding does not establish protein function, disease causality, treatment relevance, or clinical meaning.",
    )
    required_next_actions: tuple[str, ...] = (
        "Complete human licence review before downloading or executing model artifacts.",
        "Review the native PyTorch and TransformerEngine dependency boundary before expanding beyond the fixture runtime.",
        "Download only the pinned model revision and verify the safetensors SHA-256 digest.",
        "Run one fixture sequence and import only bounded provenance metadata for comparison.",
    )


def reviewed_bionemo_recipes_path() -> BioNeMoRecipesReview:
    """Return the deterministic maintained-path review selected for v0.12."""

    return BioNeMoRecipesReview()


def planned_bionemo_recipes_esm2_manifest(
    record: ProteinSequenceRecord,
    config: LocalESM2Config,
    *,
    planned_at: date | None = None,
) -> dict[str, object]:
    """Plan the maintained ESM-2 path without loading code, weights, or a model."""

    selected, start, end = select_sequence_window(
        record.sequence,
        start=config.window_start,
        length=config.window_length,
        max_residues=config.max_residues,
    )
    selected_checksum = hashlib.sha256(selected.encode("ascii")).hexdigest()
    return {
        "schema_version": "0.2",
        "experiment_id": (
            f"bionemo-recipes-esm2-{record.target.symbol.lower()}-{start}-{end}-"
            f"{selected_checksum[:12]}"
        ),
        "status": "planned",
        "purpose": (
            "Evaluate a maintained BioNeMo Recipes ESM-2 inference path with "
            "explicit code, checkpoint, and input provenance."
        ),
        "component_type": "foundation_model",
        "model": {
            "provider": "NVIDIA BioNeMo Recipes / Hugging Face",
            "name": BIONEMO_RECIPES_MODEL_ID,
            "version": BIONEMO_RECIPES_MODEL_REVISION,
            "licence": "review-required (model card MIT; repository Apache-2.0)",
            "source_url": BIONEMO_RECIPES_MODEL_URL,
            "weights_sha256": BIONEMO_RECIPES_WEIGHTS_SHA256,
        },
        "inputs": [
            {
                "identifier": record.accession,
                "entity_id": record.target.entity_id,
                "symbol": record.target.symbol,
                "organism": record.target.organism,
                "source_url": record.source_url,
                "retrieved_at": record.retrieved_at.isoformat(),
                "checksum": record.checksum,
                "sequence_length": record.sequence_length,
                "selected_sequence_checksum": f"sha256:{selected_checksum}",
                "selected_sequence_length": len(selected),
                "window_start": start,
                "window_end": end,
                "input_handling": (
                    "full-sequence"
                    if start == 1 and end == record.sequence_length
                    else "explicit-window"
                ),
            }
        ],
        "runtime": {
            "interface": "external-python-plan",
            "container": "not-selected",
            "hardware": "not-executed",
            "parameters": {
                "recipes_version": BIONEMO_RECIPES_VERSION,
                "recipes_commit": BIONEMO_RECIPES_COMMIT,
                "transformer_engine_required": True,
                "remote_code_required": True,
                "remote_code_executed": False,
                "pooling_method": "not-selected",
                "max_residues": config.max_residues,
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
            "method": "plan-only code, checkpoint, input, and runtime review",
            "limitations": [
                "No BioNeMo Recipes code, checkpoint, TransformerEngine runtime, or model was executed.",
                "Checkpoint equivalence and output parity remain unverified.",
                "No biological or clinical conclusion can be drawn from this plan.",
            ],
        },
    }
