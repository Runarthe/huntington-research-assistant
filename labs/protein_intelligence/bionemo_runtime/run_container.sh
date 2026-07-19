#!/usr/bin/env bash
set -euo pipefail

: "${BIONEMO_IMAGE:?Set BIONEMO_IMAGE to a reviewed immutable container reference.}"

if [[ ! "${BIONEMO_IMAGE}" =~ @sha256:[[:xdigit:]]{64}$ ]]; then
  echo "BIONEMO_IMAGE must end with a complete immutable @sha256 digest, not a moving tag." >&2
  exit 2
fi

mkdir -p .bionemo-cache results

docker run --rm --gpus all --shm-size=4g \
  -e HRA_BIONEMO_IMAGE="${BIONEMO_IMAGE}" \
  -v "${PWD}:/workspace/hra" \
  -v "${PWD}/.bionemo-cache:/root/.cache/bionemo" \
  -w /workspace/hra \
  "${BIONEMO_IMAGE}" \
  bash ./run_inside_container.sh
