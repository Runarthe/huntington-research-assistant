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

## Reviewed Container Candidate

For the existing BioNeMo Framework 2.7 ESM-2 command contract, HRA records this exact reproduction candidate:

```text
nvcr.io/nvidia/clara/bionemo-framework@sha256:7d15abfbd648915c367ec14a1eef93d4aa40f3e346bacfe63c05f9269dabd678
```

- NGC tag: `2.7.1`;
- platform: `linux/amd64`;
- compressed size reported by NGC: 16.33 GB;
- checkpoint contract: `esm2/650m:2.0` through `infer_esm2`;
- lifecycle: archived and no longer maintained.

The NGC catalogue reports the artifact as signed and scanned with no malware found. HRA independently resolved the platform manifest to the same digest without registry credentials. HRA did not pull or execute the image, independently verify its signature, or scan it locally. Those distinctions are retained in the downloadable review JSON.

The image is selected only to reproduce the already-reviewed 2.7 command contract. New development should evaluate [BioNeMo Recipes](https://github.com/NVIDIA-BioNeMo/bionemo-recipes), which NVIDIA identifies as the maintained successor. Before acquiring the legacy image, the user must independently review the [NVIDIA AI Product Agreement](https://www.nvidia.com/en-us/agreements/enterprise-software/product-specific-terms-for-ai-products/) and NGC access terms.

Print the same offline review record from the CLI:

```powershell
python -m labs.protein_intelligence bionemo-image-review
```

## Maintained BioNeMo Recipes Path

The container review showed that the 2.7.1 image is useful only as a frozen reproduction path. The preferred development path is therefore tracked separately against the maintained [BioNeMo Recipes v3.0.0 release](https://github.com/NVIDIA-BioNeMo/bionemo-recipes/releases/tag/v3.0.0):

- Recipes release: `v3.0.0`;
- Recipes commit: `66c150f2920d6155697d4edfc87289f239b65022`;
- public model: `nvidia/esm2_t6_8M_UR50D`;
- model revision: `3674a6acb6c217bbeff709d182a11b196125dfc3`;
- model parameters: 7,512,353;
- model licence: MIT;
- weights file: 30,058,964-byte safetensors artifact;
- weights SHA-256: `89dfb9aa2b595936aaccdc50b6b50f3c353c520f0e7bdd54487f5fa00f05a0ed`.

NVIDIA's model card describes this checkpoint as a TransformerEngine-optimized conversion of the original ESM-2 weights. HRA records that as a publisher statement, not as independently reproduced weight or output equivalence.

The model repository includes executable custom code in `esm_nv.py` and requires TransformerEngine. HRA reviewed the repository metadata, configuration, imports, and immutable file identities, but did not conduct a complete security audit, download the weights, enable `trust_remote_code`, import the code, or run inference. The Streamlit panel and CLI export these boundaries alongside a sequence-specific plan:

```powershell
python -m labs.protein_intelligence bionemo-recipes-review
```

See the [official ESM-2 model documentation](https://docs.nvidia.com/bionemo-recipes/latest/main/models/ESM-2/) and [Recipes inference example](https://docs.nvidia.com/bionemo-recipes/latest/main/recipes/recipes/esm2_native_te/) for the upstream contract.

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

The GPU and driver clear the documented numeric thresholds, but the RTX 5070 Ti is not named in the reviewed BioNeMo support matrix. This is recorded as `warning`, not silently upgraded to supported. The reviewed image is not currently stored locally, so the explicit GPU-container probe remains unexecuted.

## Official Runtime Contract

The reviewed NVIDIA prerequisites specify x86 Linux, an NVIDIA GPU, driver 560 or newer, Docker Engine 19.03 or newer with GPU support, and NVIDIA Container Toolkit. The configured bfloat16 workflow requires compute capability 8.0 or newer.

- [BioNeMo hardware and software prerequisites](https://docs.nvidia.com/bionemo-framework/latest/main/getting-started/pre-reqs/index.html)
- [BioNeMo access and container startup](https://docs.nvidia.com/bionemo-framework/latest/main/getting-started/access-startup/)
- [BioNeMo Framework 2.7 ESM-2 inference](https://docs.nvidia.com/bionemo-framework/2.7/main/examples/bionemo-esm2/inference/index.html)

HRA never uses a moving tag for this provenance experiment. The execution bundle embeds the selected digest, rejects any different `BIONEMO_IMAGE`, and uses `docker run --pull never`. Image acquisition and registry authentication must happen explicitly outside HRA.

## Next Verification Step

The next v0.12 increment should:

1. Review the selected image, NVIDIA licence, archived lifecycle, and NGC access terms outside HRA.
2. If accepted, authenticate and pull the exact immutable reference outside HRA without storing registry credentials in this repository.
3. Run the explicit GPU-container probe and retain its JSON provenance report.
4. Review the RTX 5070 Ti compatibility warning rather than treating numeric capability as vendor support.
5. Resolve checkpoint access and run the v0.11 execution bundle only after the probe passes and the exact image/runtime contract is approved.
6. Import the bounded `hra-bionemo-result.json` and review runtime provenance before comparing provider output fields.

For the preferred maintained path, the next increment should complete a security review of the pinned custom model code, define a reproducible Linux/CUDA/TransformerEngine environment, and run only the bundled fixture sequence before considering broader inputs.

No biological interpretation, model ranking, treatment relevance, efficacy, safety, or clinical claim is part of this experiment.
