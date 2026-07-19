# HRA BioNeMo Recipes Fixture Runtime

This bundle performs one bounded ESM-2 inference for the exact fixture in `fixture.json`. It does not accept arbitrary model IDs, checkpoints, URLs, or sequences.

## Boundaries

- Model: `nvidia/esm2_t6_8M_UR50D` at the revision in `artifact-lock.json`.
- BioNeMo Recipes: the exact commit recorded in `runtime-review.json`.
- Base image: the Linux/AMD64 digest recorded in `runtime-review.json`.
- Input: one bundled sequence window, at most 64 residues, batch size one.
- Output: tensor shapes and SHA-256 checksums only. No embedding vector is exported.
- Inference: no network, read-only root filesystem, dropped Linux capabilities, no new privileges, one visible GPU.

This produces a computational provenance artifact. It does not establish protein function, similarity, structure, disease causality, treatment relevance, efficacy, safety, or clinical meaning.

## Before Running

Read `code-review.json`, `runtime-review.json`, `artifact-lock.json`, every script, and the current NVIDIA and model terms. Publisher licence signals are inconsistent: the model-card metadata declares MIT, while the repository `LICENSE` and Python source identify Apache 2.0. HRA does not resolve that legal question for you.

The base image is about 9.67 GB compressed. HRA does not pull it or accept NVIDIA terms on your behalf.

## Prepare Exact Artifacts

This explicit command makes HTTPS requests to Hugging Face and PyPI, downloads about 70 MB, and verifies every file before keeping it:

```bash
python fetch_assets.py --root .
python verify_assets.py --root .
```

The fetched model and wheel files are not part of the HRA repository or ZIP bundle.

From the HRA repository, the extracted directory can be checked without network or container execution:

```bash
python -m labs.protein_intelligence bionemo-recipes-readiness \
  --bundle hra-bionemo-recipes-htt.zip \
  --artifact-root EXTRACTED_RUNTIME_DIRECTORY \
  --terms-reviewed \
  --strict
```

`--terms-reviewed` records only the user's declaration and does not accept any term on the user's behalf. The readiness status means only that required local inputs are present for a build.

## Prepare the Base Image

After reviewing and accepting the applicable NVIDIA terms yourself, pull the exact digest shown in `runtime-review.json`. Do not replace it with a tag.

```bash
docker pull nvcr.io/nvidia/pytorch@sha256:be06a21bd95a46bce1a5cfc0576051a40209f328440edaa2ba5cd35abf85ca1a
```

## Build Offline

The build refuses to pull a base image and installs only the verified local wheels with `--require-hashes`:

```bash
export HRA_NVIDIA_TERMS_REVIEWED=yes
./build_image.sh
```

## Run the Fixture

The run is separately gated and writes one JSON result to `output/`:

```bash
export HRA_RUN_BOUNDED_FIXTURE=yes
./run_fixture.sh
```

Import `output/hra-bionemo-recipes-result.json` into Protein Lab for provider-parity review. Preserve the extracted bundle and `built-image-id.txt` with the result if you need an audit trail.
