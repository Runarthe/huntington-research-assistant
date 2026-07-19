#!/usr/bin/env bash
set -euo pipefail

EXPECTED_BASE_DIGEST="sha256:be06a21bd95a46bce1a5cfc0576051a40209f328440edaa2ba5cd35abf85ca1a"
EXPECTED_MODEL_REVISION="3674a6acb6c217bbeff709d182a11b196125dfc3"

if [[ "${HRA_RUN_BOUNDED_FIXTURE:-}" != "yes" ]]; then
  echo "Set HRA_RUN_BOUNDED_FIXTURE=yes to allow this one reviewed fixture run." >&2
  exit 2
fi
if [[ -n "${DOCKER_HOST:-}" && "${DOCKER_HOST}" != unix://* ]]; then
  echo "A remote Docker endpoint is not allowed for this fixture run." >&2
  exit 3
fi
if [[ ! -f built-image-id.txt ]]; then
  echo "Run build_image.sh first." >&2
  exit 4
fi
IMAGE_ID="$(cat built-image-id.txt)"
if [[ ! "${IMAGE_ID}" =~ ^sha256:[0-9a-f]{64}$ ]]; then
  echo "built-image-id.txt is invalid." >&2
  exit 5
fi
if ! docker image inspect "${IMAGE_ID}" >/dev/null 2>&1; then
  echo "The recorded derived image is not local." >&2
  exit 6
fi
BASE_LABEL="$(docker image inspect "${IMAGE_ID}" --format '{{ index .Config.Labels "io.hra.base.digest" }}')"
MODEL_LABEL="$(docker image inspect "${IMAGE_ID}" --format '{{ index .Config.Labels "io.hra.model.revision" }}')"
if [[ "${BASE_LABEL}" != "${EXPECTED_BASE_DIGEST}" || "${MODEL_LABEL}" != "${EXPECTED_MODEL_REVISION}" ]]; then
  echo "The derived image labels do not match the reviewed contract." >&2
  exit 7
fi

mkdir -p output
if [[ -e output/hra-bionemo-recipes-result.json ]]; then
  echo "Move or preserve the previous result before running again." >&2
  exit 8
fi

docker run --rm --pull never \
  --gpus all \
  --network none \
  --read-only \
  --cap-drop ALL \
  --security-opt no-new-privileges \
  --pids-limit 256 \
  --memory 8g \
  --cpus 4 \
  --shm-size 512m \
  --ulimit core=0 \
  --user "$(id -u):$(id -g)" \
  --env HOME=/tmp \
  --env CUDA_VISIBLE_DEVICES=0 \
  --env HRA_RUNTIME_IMAGE_REFERENCE="local/hra-bionemo-recipes@${IMAGE_ID}" \
  --tmpfs /tmp:rw,noexec,nosuid,nodev,size=256m \
  --mount "type=bind,src=${PWD}/output,dst=/output" \
  "${IMAGE_ID}"
