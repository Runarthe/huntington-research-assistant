#!/usr/bin/env python3
"""Run one exact local fixture and export bounded provenance metadata."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import platform
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path("/opt/hra")
MODEL_DIR = ROOT / "model"
OUTPUT_PATH = Path("/output/hra-bionemo-recipes-result.json")
EXPECTED_BASE = (
    "sha256:be06a21bd95a46bce1a5cfc0576051a40209f328440edaa2ba5cd35abf85ca1a"
)
EXPECTED_REVISION = "3674a6acb6c217bbeff709d182a11b196125dfc3"
MAX_RESIDUES = 64


def sha256(data: bytes) -> str:
    return f"sha256:{hashlib.sha256(data).hexdigest()}"


def distribution_version(*names: str) -> str:
    for name in names:
        try:
            return importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            continue
    return "not-recorded"


def require_runtime_boundary() -> None:
    if sys.flags.optimize != 0 or os.environ.get("PYTHONOPTIMIZE") not in {
        None,
        "",
        "0",
    }:
        raise RuntimeError(
            "Optimized Python is forbidden because reviewed asserts must remain active."
        )
    for name in ("HF_HUB_OFFLINE", "TRANSFORMERS_OFFLINE", "HF_DATASETS_OFFLINE"):
        if os.environ.get(name) != "1":
            raise RuntimeError(f"Offline runtime flag is missing: {name}")
    image_reference = os.environ.get("HRA_RUNTIME_IMAGE_REFERENCE", "")
    if not re.fullmatch(
        r"local/hra-bionemo-recipes@sha256:[0-9a-f]{64}", image_reference
    ):
        raise RuntimeError("Immutable derived image identity is missing.")
    if platform.system() != "Linux" or platform.machine() not in {"x86_64", "AMD64"}:
        raise RuntimeError("The reviewed fixture requires Linux/AMD64.")


def main() -> int:
    require_runtime_boundary()
    plan = json.loads((ROOT / "plan.json").read_text(encoding="utf-8"))
    fixture = json.loads((ROOT / "fixture.json").read_text(encoding="utf-8"))
    lock = json.loads((ROOT / "artifact-lock.json").read_text(encoding="utf-8"))
    sequence = fixture.get("sequence")
    if not isinstance(sequence, str) or not re.fullmatch(
        r"[ACDEFGHIKLMNPQRSTVWYBXZJUO]+", sequence
    ):
        raise RuntimeError("Fixture sequence contains unsupported symbols.")
    if not 1 <= len(sequence) <= MAX_RESIDUES or fixture.get("batch_size") != 1:
        raise RuntimeError(
            "Fixture length or batch size exceeds the reviewed boundary."
        )
    if sha256(sequence.encode("ascii")) != f"sha256:{fixture.get('sequence_sha256')}":
        raise RuntimeError("Fixture checksum changed.")
    if plan.get("experiment_id") != fixture.get("experiment_id"):
        raise RuntimeError("Fixture and plan identifiers differ.")
    if plan.get("model", {}).get("version") != EXPECTED_REVISION:
        raise RuntimeError("Plan model revision changed.")
    if lock.get("base_image", {}).get("amd64_digest") != EXPECTED_BASE:
        raise RuntimeError("Base image digest changed.")

    config = json.loads((MODEL_DIR / "config.json").read_text(encoding="utf-8"))
    if config.get("layer_precision") is not None or config.get("dtype") != "float32":
        raise RuntimeError(
            "Quantized or non-FP32 execution is outside this fixture review."
        )
    if config.get("num_hidden_layers") != 6 or config.get("hidden_size") != 320:
        raise RuntimeError("Model architecture changed.")

    import numpy as np
    import torch
    from transformers import AutoModel, AutoTokenizer

    if str(torch.__version__) != "2.12.0a0+0291f96":
        raise RuntimeError("Base-image PyTorch version changed.")
    if not torch.cuda.is_available() or torch.cuda.device_count() < 1:
        raise RuntimeError("One CUDA GPU is required; CPU fallback is forbidden.")

    torch.manual_seed(0)
    torch.cuda.manual_seed_all(0)
    torch.use_deterministic_algorithms(True)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR, local_files_only=True)
    encoded = tokenizer(sequence, return_tensors="pt", add_special_tokens=True)

    previous_device = torch.get_default_device()
    torch.set_default_device("cuda")
    try:
        model = AutoModel.from_pretrained(
            MODEL_DIR,
            local_files_only=True,
            trust_remote_code=True,
            dtype=torch.float32,
        )
    finally:
        torch.set_default_device(previous_device)
    model.eval()
    encoded = {name: value.to("cuda") for name, value in encoded.items()}
    with torch.inference_mode():
        hidden = model(**encoded).last_hidden_state
    torch.cuda.synchronize()

    input_ids = encoded["input_ids"][0]
    attention = encoded["attention_mask"][0].bool()
    special = torch.zeros_like(attention)
    for token_id in tokenizer.all_special_ids:
        special |= input_ids.eq(token_id)
    residue_hidden = hidden[0][attention & ~special].detach().float().cpu().contiguous()
    if residue_hidden.shape != (len(sequence), 320):
        raise RuntimeError("Unexpected residue embedding shape.")
    pooled = residue_hidden.mean(dim=0).contiguous()
    residue_bytes = np.asarray(residue_hidden.numpy(), dtype="<f4").tobytes()
    pooled_bytes = np.asarray(pooled.numpy(), dtype="<f4").tobytes()

    result = dict(plan)
    result["schema_version"] = "hra-bionemo-result.v1"
    result["status"] = "generated"
    result["runtime"] = {
        "interface": "bionemo-recipes-container",
        "container": os.environ["HRA_RUNTIME_IMAGE_REFERENCE"],
        "hardware": torch.cuda.get_device_name(0),
        "provider": "nvidia-bionemo-recipes-esm2",
        "dependencies": {
            "base_image": EXPECTED_BASE,
            "cuda": str(torch.version.cuda),
            "torch": str(torch.__version__),
            "transformer-engine": distribution_version(
                "transformer-engine", "transformer_engine"
            ),
            "transformers": distribution_version("transformers"),
        },
        "parameters": {
            "recipes_commit": lock["base_image"]["recipes_commit"],
            "model_revision": EXPECTED_REVISION,
            "precision": "fp32",
            "pooling_method": "mean_residue_tokens",
            "max_residues": MAX_RESIDUES,
            "silent_truncation": False,
            "batch_size": 1,
            "network": "none",
        },
    }
    result["outputs"] = {
        "path": str(OUTPUT_PATH),
        "raw_output_checksum": sha256(residue_bytes),
        "confidence_measures": [],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "embedding": {
            "dimensions": int(pooled.shape[0]),
            "checksum": sha256(pooled_bytes),
            "token_embeddings_shape": list(residue_hidden.shape),
            "residue_token_count": len(sequence),
        },
    }
    result["evaluation"] = {
        "method": "exact-input, offline-runtime, tensor-shape, and checksum validation",
        "limitations": [
            "The JSON omits all embedding values and retains only shapes and checksums.",
            "The output has not been validated on a downstream scientific task.",
            "No protein-function, similarity, structure, disease, treatment, safety, efficacy, or clinical claim is produced.",
        ],
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("x", encoding="utf-8") as output:
        json.dump(result, output, indent=2, sort_keys=True)
        output.write("\n")
    print(f"Created {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
