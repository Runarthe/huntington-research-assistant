#!/usr/bin/env bash
set -euo pipefail

: "${BIONEMO_IMAGE:?Set BIONEMO_IMAGE to a reviewed immutable container reference.}"

EXPECTED_BIONEMO_IMAGE="$(python - <<'PY'
import json

with open("execution.json", encoding="utf-8") as handle:
    print(json.load(handle)["container_review"]["immutable_reference"])
PY
)"

if [[ "${BIONEMO_IMAGE}" != "${EXPECTED_BIONEMO_IMAGE}" ]]; then
  echo "BIONEMO_IMAGE must exactly match the immutable reference in execution.json." >&2
  exit 2
fi

mkdir -p .bionemo-cache results

docker run --rm --pull never --gpus all --shm-size=4g \
  -e HRA_BIONEMO_IMAGE="${BIONEMO_IMAGE}" \
  -v "${PWD}:/workspace/hra" \
  -v "${PWD}/.bionemo-cache:/root/.cache/bionemo" \
  -w /workspace/hra \
  "${BIONEMO_IMAGE}" \
  bash ./run_inside_container.sh
