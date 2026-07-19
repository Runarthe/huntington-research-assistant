import csv
import hashlib
import importlib.metadata
import json
import os
import struct
from datetime import datetime, timezone
from pathlib import Path

import torch


def sha256(data: bytes) -> str:
    return f"sha256:{hashlib.sha256(data).hexdigest()}"


def package_version(*names: str) -> str:
    for name in names:
        try:
            return importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            continue
    return "not-recorded"


plan = json.loads(Path("plan.json").read_text(encoding="utf-8"))
execution = json.loads(Path("execution.json").read_text(encoding="utf-8"))
with Path("input.csv").open(newline="", encoding="ascii") as input_file:
    rows = list(csv.DictReader(input_file))
if len(rows) != 1 or set(rows[0]) != {"sequences"}:
    raise RuntimeError("input.csv must contain exactly one sequences row")
sequence = rows[0]["sequences"]
expected_checksum = plan["inputs"][0]["selected_sequence_checksum"]
if sha256(sequence.encode("ascii")) != expected_checksum:
    raise RuntimeError("input.csv no longer matches plan.json")

prediction_paths = sorted(Path("results").glob("predictions__rank_*.pt"))
if len(prediction_paths) != 1:
    raise RuntimeError("Expected one single-GPU BioNeMo prediction artifact")
prediction_path = prediction_paths[0]
results = torch.load(prediction_path, map_location="cpu", weights_only=True)
embeddings = results.get("embeddings")
hidden_states = results.get("hidden_states")
input_ids = results.get("input_ids")
if embeddings is None or hidden_states is None or input_ids is None:
    raise RuntimeError("BioNeMo output omitted a requested provenance tensor")
if embeddings.ndim != 2 or embeddings.shape[0] != 1:
    raise RuntimeError("Expected one sequence-level embedding")

vector = embeddings[0].detach().float().cpu().tolist()
vector_bytes = struct.pack(f"<{len(vector)}f", *vector)
settings = execution["settings"]
result = {
    **plan,
    "schema_version": "hra-bionemo-result.v1",
    "status": "generated",
    "runtime": {
        "interface": "bionemo-framework-container",
        "container": os.environ["HRA_BIONEMO_IMAGE"],
        "hardware": (
            torch.cuda.get_device_name(0) if torch.cuda.is_available() else "GPU not reported"
        ),
        "provider": "bionemo-framework",
        "dependencies": {
            "torch": str(torch.__version__),
            "bionemo-esm2": package_version("bionemo-esm2", "bionemo-framework"),
        },
        "parameters": {
            "framework_contract": execution["framework_contract"],
            "precision": settings["precision"],
            "pooling_method": "mean_non_padding_hidden_states",
            "max_residues": plan["runtime"]["parameters"]["max_residues"],
            "silent_truncation": False,
            "micro_batch_size": settings["micro_batch_size"],
            "num_gpus": settings["num_gpus"],
            "num_nodes": settings["num_nodes"],
        },
    },
    "outputs": {
        "path": str(prediction_path),
        "raw_output_checksum": sha256(prediction_path.read_bytes()),
        "confidence_measures": [],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "embedding": {
            "dimensions": len(vector),
            "checksum": sha256(vector_bytes),
            "token_embeddings_shape": list(hidden_states.shape),
            "input_ids_shape": list(input_ids.shape),
            "residue_token_count": len(sequence),
        },
    },
    "evaluation": {
        "method": "input, tensor-shape, runtime, artifact-checksum, and provenance validation",
        "limitations": [
            "The exported JSON omits the full embedding vector and retains only shape and checksum metadata.",
            "The run has not been evaluated on a downstream scientific task.",
            "No function, similarity, structure, treatment, safety, efficacy, or clinical claim is produced.",
        ],
    },
}
Path("hra-bionemo-result.json").write_text(
    json.dumps(result, indent=2, sort_keys=True),
    encoding="utf-8",
)
print("Created hra-bionemo-result.json")
