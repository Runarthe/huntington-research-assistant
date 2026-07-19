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

The local reference uses the pinned `facebook/esm2_t6_8M_UR50D` checkpoint introduced in v0.10. The BioNeMo side is a plan for the candidate `esm2/8m:2.0` checkpoint documented by NVIDIA.

HRA does not claim that these checkpoints contain identical weights. A shared ESM-2 architecture or parameter count is not enough to establish numerical parity. The BioNeMo plan therefore remains `planned` until a reviewed runtime adapter records real output.

The plan also records that BioNeMo can apply its own long-sequence handling. HRA preserves its stricter rule: select and checksum an explicit window before handing input to either provider. Silent provider-side truncation is not accepted.

## Use in the App

1. Open **Protein Lab (experimental)**.
2. Select a curated target and sequence source.
3. Choose an explicit sequence window.
4. Review or run the local ESM-2 experiment.
5. Scroll to **Provider parity review**.
6. Inspect the readable comparison table.
7. Download the planned BioNeMo manifest and parity report when a machine-readable record is useful.

The comparison works with a planned local run, but generated dimensions and checksums appear only after local ESM-2 has run. BioNeMo output fields remain unavailable until a future reviewed adapter executes.

## Official References

- [BioNeMo ESM-2 inference](https://docs.nvidia.com/bionemo-framework/latest/main/examples/bionemo-esm2/inference/index.html)
- [BioNeMo Recipes ESM-2 checkpoints](https://docs.nvidia.com/bionemo-recipes/latest/models/ESM-2/pre-training/)
- [BioNeMo Framework overview](https://docs.nvidia.com/bionemo-framework/latest/main/about/overview/index.html)

## Safety and Interpretation

This report compares software provenance. It does not evaluate protein function, biological similarity, structure, disease causality, treatment relevance, efficacy, safety, or clinical meaning. Matching metadata cannot turn an embedding into scientific evidence.

No current official protein ESM-2 NIM API was verified for this milestone, so v0.11 does not invent or simulate one. A NIM adapter should be added only against a documented, reviewed endpoint with explicit deployment, licensing, authentication, and failure-path tests.
