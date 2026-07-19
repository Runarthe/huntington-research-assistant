#!/usr/bin/env bash
set -euo pipefail

EXPECTED_BASE="nvcr.io/nvidia/pytorch@sha256:be06a21bd95a46bce1a5cfc0576051a40209f328440edaa2ba5cd35abf85ca1a"
IMAGE_TAG="hra-bionemo-recipes-esm2:0.12-fixture"

if [[ "${HRA_NVIDIA_TERMS_REVIEWED:-}" != "yes" ]]; then
  echo "Set HRA_NVIDIA_TERMS_REVIEWED=yes only after reviewing the applicable NVIDIA terms." >&2
  exit 2
fi
if [[ -n "${DOCKER_HOST:-}" && "${DOCKER_HOST}" != unix://* ]]; then
  echo "A remote Docker endpoint is not allowed for this fixture build." >&2
  exit 3
fi
if ! docker image inspect "${EXPECTED_BASE}" >/dev/null 2>&1; then
  echo "The exact reviewed base image is not local. This script will not pull it." >&2
  exit 4
fi

python verify_assets.py --root .
DOCKER_BUILDKIT=1 docker build \
  --pull=false \
  --network=none \
  --no-cache \
  --tag "${IMAGE_TAG}" \
  .

IMAGE_ID="$(docker image inspect "${IMAGE_TAG}" --format '{{.Id}}')"
if [[ ! "${IMAGE_ID}" =~ ^sha256:[0-9a-f]{64}$ ]]; then
  echo "Docker did not return an immutable local image ID." >&2
  exit 5
fi
printf '%s\n' "${IMAGE_ID}" > built-image-id.txt
echo "Built ${IMAGE_TAG} as ${IMAGE_ID}"
