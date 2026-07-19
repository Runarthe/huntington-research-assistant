# v0.12 BioNeMo Runtime Experiment

v0.12 is the first attempt to move from a reviewed BioNeMo execution contract toward an actual external runtime. The core Streamlit application remains free, CPU-capable, and independent of NVIDIA software.

## First Increment: Environment Preflight

The first increment adds an explicit local preflight before any container action. Run it from Protein Lab or from the CLI:

```powershell
python -m labs.protein_intelligence bionemo-preflight
```

An immutable image reference can also be checked without contacting its registry:

```powershell
python -m labs.protein_intelligence bionemo-preflight `
  --image "nvcr.io/example/bionemo@sha256:REVIEWED_64_CHARACTER_DIGEST"
```

Use `--strict` when automation should return a nonzero status until every requirement is complete. The current preflight intentionally remains `review-required` until a separate GPU-container probe is implemented.

The report checks:

- x86 architecture and the documented Linux execution boundary;
- NVIDIA GPU discovery through `nvidia-smi`;
- driver major version 560 or newer;
- compute capability 8.0 or newer for the configured bfloat16 precision;
- whether the exact GPU appears in the reviewed support matrix;
- Docker Engine 19.03 or newer with a Linux server;
- whether Docker declares an NVIDIA runtime;
- whether a supplied image reference ends in a complete immutable SHA-256 digest.

The preflight does not:

- inspect environment variables, Docker configuration, NGC credentials, or API keys;
- call a network service or registry;
- pull an image, start a container, reserve a GPU, or execute BioNeMo;
- infer that an unlisted GPU is supported merely because its compute capability is high enough;
- produce a protein embedding or any biomedical claim.

## Current Machine Observation

The initial Windows development-host review detected:

- NVIDIA GeForce RTX 5070 Ti;
- 16 GB VRAM;
- driver 591.86;
- compute capability 12.0;
- Docker client 29.1.3 with the Docker Desktop Linux engine stopped;
- WSL 2 installed through Docker Desktop.

The GPU and driver clear the documented numeric thresholds, but the RTX 5070 Ti is not named in the reviewed BioNeMo support matrix. This is recorded as `warning`, not silently upgraded to supported. The stopped Docker engine is a blocking condition.

## Official Runtime Contract

The reviewed NVIDIA prerequisites specify x86 Linux, an NVIDIA GPU, driver 560 or newer, Docker Engine 19.03 or newer with GPU support, and NVIDIA Container Toolkit. The configured bfloat16 workflow requires compute capability 8.0 or newer.

- [BioNeMo hardware and software prerequisites](https://docs.nvidia.com/bionemo-framework/latest/main/getting-started/pre-reqs/index.html)
- [BioNeMo access and container startup](https://docs.nvidia.com/bionemo-framework/latest/main/getting-started/access-startup/)
- [BioNeMo Framework 2.7 ESM-2 inference](https://docs.nvidia.com/bionemo-framework/2.7/main/examples/bionemo-esm2/inference/index.html)

The NVIDIA startup documentation demonstrates a moving `nightly` container tag. HRA does not use a moving tag for a provenance experiment. An operator must resolve and review an immutable image digest separately before execution.

## Next Verification Step

The next v0.12 increment should:

1. Start and review the Docker Linux engine outside Streamlit.
2. Re-run the non-networking preflight.
3. Add an explicit GPU-container probe against an already available, immutable image.
4. Keep registry authentication outside the app and out of generated artifacts.
5. Run the v0.11 execution bundle only after the probe passes.
6. Import the bounded `hra-bionemo-result.json` and review runtime provenance before comparing provider output fields.

No biological interpretation, model ranking, treatment relevance, efficacy, safety, or clinical claim is part of this experiment.
