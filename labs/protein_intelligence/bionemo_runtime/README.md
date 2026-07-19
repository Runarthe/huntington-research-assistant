# HRA BioNeMo Execution Bundle

This bundle is a reviewed handoff from Huntington Research Assistant to an external BioNeMo Framework environment. It contains one explicitly selected protein-sequence window and no credentials.

## Requirements

- x86 Linux;
- a supported NVIDIA GPU;
- compatible NVIDIA drivers;
- Docker with GPU support;
- NVIDIA Container Toolkit;
- the exact reviewed image already stored locally: `nvcr.io/nvidia/clara/bionemo-framework@sha256:7d15abfbd648915c367ec14a1eef93d4aa40f3e346bacfe63c05f9269dabd678`.

Review NVIDIA's current prerequisites, licence, and container documentation before running. This archived BioNeMo Framework 2.7.1 image is pinned only to reproduce HRA's bounded 2.7 ESM-2 contract. It is not recommended as the foundation for new production development; evaluate the maintained BioNeMo Recipes project for that work.

## Run

1. Inspect `plan.json`, `execution.json`, `input.csv`, and every script.
2. Outside HRA, review NVIDIA's NGC access and licence terms. If accepted, authenticate and pull the exact immutable image recorded in `execution.json`.
3. From this extracted directory, set only the non-secret image reference:

   ```bash
   export BIONEMO_IMAGE='nvcr.io/nvidia/clara/bionemo-framework@sha256:7d15abfbd648915c367ec14a1eef93d4aa40f3e346bacfe63c05f9269dabd678'
   ./run_container.sh
   ```

4. The container downloads the checkpoint declared in `execution.json`, runs `infer_esm2`, and creates `hra-bionemo-result.json`.
5. Copy only `hra-bionemo-result.json` back to HRA's Provider parity review. The raw PyTorch prediction remains in `results/` for local audit.

The runner rejects any other image and uses `docker run --pull never`; it cannot fetch a missing image. Do not put an NGC key, password, token, or other credential in this bundle. Authenticate Docker/NGC separately according to NVIDIA's documentation. Checkpoint access may also require separately configured NGC access and remains an unresolved manual runtime step.

## Claim Boundary

The result is a computational provenance artifact. It is not evidence about protein function, biological similarity, structure, disease causality, treatment relevance, efficacy, safety, or clinical meaning.
