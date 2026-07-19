# v0.11 Provider-Parity Experiment

v0.11 adds a provider-neutral review step between the local ESM-2 experiment and a future BioNeMo Framework execution. It does not call BioNeMo, NVIDIA NIM, or a remote service.

## Purpose

The same protein-model workflow can behave differently across libraries, checkpoints, containers, hardware, and numerical precision. Before comparing output, HRA now asks a smaller and more useful question:

> Have both providers received the same recorded input, and do we know enough about each run to compare their artifacts honestly?

The comparison covers:

- selected-sequence checksum and one-based window;
- selected-sequence length and truncation policy;
- provider, model, and checkpoint identity;
- pooling method;
- execution status;
- embedding dimensions, token-tensor shape, and vector checksum;
- runtime hardware and numerical precision.

Each field is labelled `matched`, `different`, `not-available`, or `not-comparable`. Unknown values are not treated as matches.

## Current Boundary

The local reference uses the pinned `facebook/esm2_t6_8M_UR50D` checkpoint introduced in v0.10. The executable BioNeMo handoff uses the `esm2/650m:2.0` checkpoint shown in NVIDIA's BioNeMo Framework 2.7 ESM-2 inference tutorial.

These checkpoints have different sizes, training provenance, and identifiers. HRA does not claim that their weights or numerical output should match. The provider-parity report is designed to expose that difference while still verifying the exact input and runtime contract. The BioNeMo side remains `planned` until a reviewed external runtime records real output.

The plan also records that BioNeMo can apply its own long-sequence handling. HRA preserves its stricter rule: select and checksum an explicit window before handing input to either provider. Silent provider-side truncation is not accepted.

## Use in the App

1. Open **Protein Lab (experimental)**.
2. Select a curated target and sequence source.
3. Choose an explicit sequence window.
4. Review or run the local ESM-2 experiment.
5. Scroll to **Provider parity review**.
6. Inspect the readable comparison table.
7. Download the planned BioNeMo manifest and parity report when a machine-readable record is useful.
8. Use **Download Linux/GPU execution bundle** to create a portable handoff for a reviewed BioNeMo host.
9. Enable the offline result fixture to test the importer without running a provider.
10. Import `hra-bionemo-result.json` after a real external run.

The comparison works with a planned local run, but generated dimensions and checksums appear only after local ESM-2 has run. BioNeMo output fields remain unavailable until the external bundle runs and its result passes import validation.

## External Execution Bundle

The ZIP bundle contains:

- `input.csv`, with exactly one `sequences` row containing the selected and checksummed window;
- `plan.json` and non-secret `execution.json`;
- a host-side `run_container.sh` that requires an immutable `@sha256:` container reference;
- a container-side `infer_esm2` command requesting hidden states, pooled embeddings, and input IDs;
- `export_hra_result.py`, which verifies the input and exports the immutable container digest, runtime, tensor-shape, and checksum metadata without the full embedding vector;
- a bundle manifest containing a checksum for every included file.

The current official prerequisites describe BioNeMo Framework support on x86 Linux with NVIDIA GPU access, Docker GPU support, and NVIDIA Container Toolkit. `bfloat16` support requires a compatible Ampere-generation or newer GPU. This Windows development machine does not execute that environment.

After reviewing every file, the operator supplies an immutable image reference and runs:

```bash
export BIONEMO_IMAGE='nvcr.io/.../bionemo-framework@sha256:REVIEWED_DIGEST'
./run_container.sh
```

Authentication to NGC or the container registry happens separately. The bundle contains no key and Streamlit neither launches Docker nor forwards credentials. A successful run produces `hra-bionemo-result.json`, which can be imported into the matching Protein Lab plan. Results for another sequence, window, model, or experiment ID are rejected.

## Official References

- [BioNeMo Framework 2.7 ESM-2 inference](https://docs.nvidia.com/bionemo-framework/2.7/main/examples/bionemo-esm2/inference/index.html)
- [BioNeMo hardware and software prerequisites](https://docs.nvidia.com/bionemo-framework/latest/main/getting-started/pre-reqs/index.html)
- [BioNeMo Framework overview](https://docs.nvidia.com/bionemo-framework/latest/main/about/overview/index.html)

## Safety and Interpretation

This report compares software provenance. It does not evaluate protein function, biological similarity, structure, disease causality, treatment relevance, efficacy, safety, or clinical meaning. Matching metadata cannot turn an embedding into scientific evidence.

No current official protein ESM-2 NIM API was verified for this milestone, so v0.11 does not invent or simulate one. A NIM adapter should be added only against a documented, reviewed endpoint with explicit deployment, licensing, authentication, and failure-path tests.
