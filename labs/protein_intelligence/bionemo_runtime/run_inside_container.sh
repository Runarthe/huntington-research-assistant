#!/usr/bin/env bash
set -euo pipefail

python prepare_checkpoint.py
CHECKPOINT_PATH="$(cat checkpoint_path.txt)"
PRECISION="$(python -c 'import json; print(json.load(open("execution.json"))["settings"]["precision"])')"

mkdir -p results
if find results -mindepth 1 -maxdepth 1 -print -quit | grep -q .; then
  echo "results/ is not empty. Preserve or move the previous run before continuing." >&2
  exit 3
fi

infer_esm2 \
  --checkpoint-path "${CHECKPOINT_PATH}" \
  --data-path input.csv \
  --results-path results \
  --micro-batch-size 1 \
  --num-gpus 1 \
  --num-nodes 1 \
  --precision "${PRECISION}" \
  --include-hiddens \
  --include-embeddings \
  --include-input-ids

python export_hra_result.py
