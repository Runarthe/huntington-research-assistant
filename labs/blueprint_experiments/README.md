# Blueprint Experiments Lab

This folder is the v0.8 scaffold for bounded Digital Biology and NVIDIA Blueprint-style learning experiments.

It is deliberately separate from the Streamlit application. The core Huntington Research Assistant must keep working without Docker, GPU access, NVIDIA credentials, BioNeMo, NIM services, AlphaFold, or paid APIs.

## What This Adds

- A manifest contract for planned or generated lab artifacts.
- Provider-type placeholders for `mock`, `nvidia_nim`, `bionemo`, `alphafold`, `nvidia_blueprint`, and `other`.
- A deterministic offline mock run using curated protein targets from `labs.protein_intelligence`.
- CLI helpers for planning, mock execution, and manifest validation.
- Tests that exercise the scaffold without live provider calls.

## What This Does Not Add

- No live NVIDIA API calls.
- No BioNeMo execution.
- No NIM deployment.
- No AlphaFold or structure prediction.
- No generated molecules, treatment ranking, trial matching, or medical guidance.
- No claims that mock values are biologically meaningful.

## CLI

List provider types:

```bash
python -m labs.blueprint_experiments list-providers
```

Plan a gated future NIM-style run:

```bash
python -m labs.blueprint_experiments plan HTT --provider-type nvidia_nim
```

Run the offline mock path:

```bash
python -m labs.blueprint_experiments run-mock HTT --points 8
```

Validate a manifest:

```bash
python -m labs.blueprint_experiments validate-manifest labs/blueprint_experiments/examples/mock-htt-manifest.json
```

## Safety Boundary

Every artifact produced here is for scientific-AI engineering practice and provenance navigation only. A manifest can show that a target, provider, parameter set, and output file were connected. It cannot show that a protein, compound, pathway, or intervention is safe, effective, causal, clinically relevant, or suitable for any person.

Outputs from this lab should remain experimental until they have clear provenance, review, evaluation, and a demonstrated user need.
