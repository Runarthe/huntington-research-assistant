# HRA BioNeMo Execution Bundle

This bundle is a reviewed handoff from Huntington Research Assistant to an external BioNeMo Framework environment. It contains one explicitly selected protein-sequence window and no credentials.

## Requirements

- x86 Linux;
- a supported NVIDIA GPU;
- compatible NVIDIA drivers;
- Docker with GPU support;
- NVIDIA Container Toolkit;
- an immutable BioNeMo container reference containing `@sha256:`.

Review NVIDIA's current prerequisites and container documentation before running. The command contract in this bundle targets the BioNeMo Framework 2.7 ESM-2 tutorial and may require revision for another release.

## Run

1. Inspect `plan.json`, `execution.json`, `input.csv`, and every script.
2. Pull a reviewed BioNeMo image and obtain its immutable repository digest.
3. From this extracted directory, set only the non-secret image reference:

   ```bash
   export BIONEMO_IMAGE='nvcr.io/.../bionemo-framework@sha256:REVIEWED_DIGEST'
   ./run_container.sh
   ```

4. The container downloads the checkpoint declared in `execution.json`, runs `infer_esm2`, and creates `hra-bionemo-result.json`.
5. Copy only `hra-bionemo-result.json` back to HRA's Provider parity review. The raw PyTorch prediction remains in `results/` for local audit.

Do not put an NGC key, password, token, or other credential in this bundle. Authenticate Docker/NGC separately according to NVIDIA's documentation.

## Claim Boundary

The result is a computational provenance artifact. It is not evidence about protein function, biological similarity, structure, disease causality, treatment relevance, efficacy, safety, or clinical meaning.
