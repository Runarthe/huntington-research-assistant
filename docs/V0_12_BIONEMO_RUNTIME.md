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

Use `--strict` when automation should return a nonzero status until every requirement is complete. The passive preflight remains `review-required` until the separate GPU-container probe and remaining support questions are resolved.

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

## Second Increment: Explicit GPU-Container Probe

The advanced probe checks whether Docker can expose the GPU inside one reviewed image that is already stored locally. A complete immutable image digest is required. Without the confirmation flag, the command prints a `not-run` report and starts nothing:

```powershell
python -m labs.protein_intelligence bionemo-gpu-probe `
  --image "nvcr.io/example/bionemo@sha256:REVIEWED_64_CHARACTER_DIGEST"
```

After separately verifying that exact local image, opt in to the bounded diagnostic:

```powershell
python -m labs.protein_intelligence bionemo-gpu-probe `
  --image "nvcr.io/example/bionemo@sha256:REVIEWED_64_CHARACTER_DIGEST" `
  --confirm-local-container
```

The implementation first requires Docker to use a local Unix socket or Windows named pipe, then uses `docker image inspect` to require the exact digest locally. Remote Docker endpoints are blocked before image inspection or execution, and Docker endpoint environment overrides are removed from the probe subprocess. Only then can it run a fixed `docker run` command with:

- `--pull never`;
- `--network none`;
- a read-only filesystem and no host mounts;
- dropped Linux capabilities and `no-new-privileges`;
- `nvidia-smi` as the overridden entrypoint;
- no BioNeMo command, checkpoint, embedding, credential, or user-controlled container command.

A passing report establishes only local GPU visibility through that image. It is not proof that BioNeMo supports the GPU or that ESM-2 inference can complete.

## Current Machine Observation

The initial Windows development-host review detected:

- NVIDIA GeForce RTX 5070 Ti;
- 16 GB VRAM;
- driver 591.86;
- compute capability 12.0;
- Docker client and Linux engine 29.1.3 with the NVIDIA runtime declared;
- WSL 2 installed through Docker Desktop.

The GPU and driver clear the documented numeric thresholds, but the RTX 5070 Ti is not named in the reviewed BioNeMo support matrix. This is recorded as `warning`, not silently upgraded to supported. No reviewed BioNeMo image is currently stored locally, so the explicit GPU-container probe remains unexecuted.

## Official Runtime Contract

The reviewed NVIDIA prerequisites specify x86 Linux, an NVIDIA GPU, driver 560 or newer, Docker Engine 19.03 or newer with GPU support, and NVIDIA Container Toolkit. The configured bfloat16 workflow requires compute capability 8.0 or newer.

- [BioNeMo hardware and software prerequisites](https://docs.nvidia.com/bionemo-framework/latest/main/getting-started/pre-reqs/index.html)
- [BioNeMo access and container startup](https://docs.nvidia.com/bionemo-framework/latest/main/getting-started/access-startup/)
- [BioNeMo Framework 2.7 ESM-2 inference](https://docs.nvidia.com/bionemo-framework/2.7/main/examples/bionemo-esm2/inference/index.html)

The NVIDIA startup documentation demonstrates a moving `nightly` container tag. HRA does not use a moving tag for a provenance experiment. An operator must resolve and review an immutable image digest separately before execution.

## Next Verification Step

The next v0.12 increment should:

1. Select and review a compatible BioNeMo container release and its licence outside HRA.
2. Resolve that image to an immutable repository digest and make it available locally without storing registry credentials in this repository.
3. Run the explicit GPU-container probe and retain its JSON provenance report.
4. Review the RTX 5070 Ti compatibility warning rather than treating numeric capability as vendor support.
5. Run the v0.11 execution bundle only after the probe passes and the exact image/runtime contract is approved.
6. Import the bounded `hra-bionemo-result.json` and review runtime provenance before comparing provider output fields.

No biological interpretation, model ranking, treatment relevance, efficacy, safety, or clinical claim is part of this experiment.
