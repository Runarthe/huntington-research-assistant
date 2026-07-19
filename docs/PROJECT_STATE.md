# Project State

Last reviewed: 2026-07-19

This page is the quickest way to understand what Huntington Research Assistant can do today, what remains experimental, and what the newest development work is intended to teach.

## Release Status

- Latest public release: `v0.11.0`
- Current development version: `v0.12.0`
- Current development focus: one bounded, externally executed BioNeMo Framework experiment with strict runtime provenance
- Core application requirement: Python 3.11 or newer
- Optional local summarization: Ollama with no cloud API key

## Stable Public-Good Application

The main Streamlit application supports:

- Huntington-focused literature search through Europe PMC and PubMed;
- provider-aware deduplication, pagination, filtering, downloads, and exports;
- a local reading list and seen-paper state;
- a source-linked Evidence Explorer for conservative paper comparison;
- a ClinicalTrials.gov tracker for registered-study metadata;
- recent-publication and publication-trend views;
- deterministic entity extraction with exact source passages;
- optional local English summaries through Ollama;
- English and Norwegian interface labels and safety information.

These features are for education and research navigation. They do not provide medical advice, treatment recommendations, diagnosis, trial suitability, or personalized health guidance.

## Experimental Research Layers

The experimental features are deliberately conservative:

1. **Entity Explorer** links catalogued terms to exact paper passages and paper-level co-occurrence. It does not assert causality or scientific consensus.
2. **Protein Lab** maps controlled literature entities to curated HTT, BDNF, and NEFL identifiers and provenance reports.
3. **Blueprint Lab preview** records provider boundaries, planned runs, deterministic mock artifacts, and a local manifest registry.
4. **Provider parity review** checks whether local ESM-2 and a future BioNeMo run share the same recorded input, exports a gated external execution bundle, and validates returned provenance without importing full vectors.

This is not a full knowledge graph and is not classic retrieval-augmented generation. The current graph relationships mean only "mentioned in" or "catalogued in the same source paper." The lab artifacts describe engineering provenance rather than biomedical findings.

## What v0.9 and v0.9.1 Add

`v0.9.0` introduced a provider-adapter boundary for `mock`, `uniprot`, `bionemo`, `nvidia_nim`, `alphafold`, `nvidia_blueprint`, and future providers. A provider records whether it is implemented, whether live execution is enabled, and what claim boundary applies.

`v0.9.1` makes that boundary easier to understand in the UI:

- Mock exposes deterministic offline test data.
- UniProt is an implemented public-data boundary, but the UI remains plan-only.
- BioNeMo, NVIDIA NIM, AlphaFold, and NVIDIA Blueprint are plan-only placeholders.
- Non-mock providers no longer display mock artifacts or mock-run commands.
- The UI exposes only execution modes it can currently perform safely.

No live NVIDIA, BioNeMo, NIM, AlphaFold, or Blueprint provider runs in the application today. v0.10 adds one optional local ESM-2 run with no biological interpretation; v0.11 adds an offline BioNeMo planning and parity layer around that run.

## Using the Newest Addition

1. Run `streamlit run app/streamlit_app.py`.
2. Open **Protein Lab (experimental)**.
3. Scroll to **Local ESM-2 experiment**.
4. Select a bundled fixture fragment or explicitly retrieve and cache a UniProt sequence.
5. Review the sequence checksum, explicit input window, pinned model revision, and planned manifest.
6. Install the optional `scientific-ai` dependencies when real local inference is wanted.
7. Confirm the execution boundary and run the local model.
8. Inspect or download the embedding artifact, then repeat the same run to compare checksums.
9. Review the Provider parity table and download the planned BioNeMo manifest or parity report.

The CLI commands shown in the app are equivalent developer checks. They are optional for normal UI use.

## Learning Progress

The project has already exercised:

- biomedical API integration and provider error handling;
- typed data models and cross-provider deduplication;
- local LLM integration and safety-aware summarization;
- deterministic biomedical entity extraction;
- evidence-preserving UI and export design;
- identifier resolution and artifact provenance;
- provider interfaces, execution gating, manifests, registries, CI, and releases;
- a real local protein-model tensor workflow with explicit preprocessing and reproducibility metadata.

It has not yet exercised GPU inference, NIM deployment, BioNeMo runtime execution, task-specific model-output evaluation, or structure-prediction interpretation.

## Current v0.12 Development

v0.12 begins with a non-networking BioNeMo environment preflight. It records the host OS and architecture, NVIDIA GPU and driver, bfloat16 compute capability, Docker Linux engine, declared NVIDIA runtime, and immutable-image readiness. It does not inspect NGC credentials, pull an image, or start a container.

On the current development machine, the preflight detects an RTX 5070 Ti with 16 GB VRAM, compute capability 12.0, and driver 591.86. Docker Desktop is installed, but its Linux engine was stopped during the initial review. The exact GPU model is also absent from the reviewed NVIDIA support matrix, so compatibility remains unverified even though the documented compute-capability and driver thresholds are met.

See [V0_12_BIONEMO_RUNTIME.md](V0_12_BIONEMO_RUNTIME.md) for the execution boundary and next verification step.

## Released v0.11 Milestone

v0.11 normalizes local and future provider artifacts into a small shared descriptor, then compares each provenance field explicitly. Identical input checksum, window, length, and truncation policy can be verified before a second provider runs. Checkpoint weights, pooling implementation, tensor output, vector checksum, hardware, and precision remain different, unavailable, or not comparable until supporting runtime records exist.

The Streamlit-side BioNeMo artifact is a plan only. It is sourced from official NVIDIA BioNeMo ESM-2 documentation and does not execute a container, GPU, NIM, endpoint, or credentialed service. A credential-free bundle can be downloaded for explicit execution in a separately reviewed x86 Linux/NVIDIA environment, and only its bounded provenance JSON is imported back. See [V0_11_PROVIDER_PARITY.md](V0_11_PROVIDER_PARITY.md).

## Released v0.10 Milestone

The `v0.10.0` release implements one bounded, optional foundation-model workflow:

```text
authoritative sequence record
  -> versioned local ESM-2 adapter
  -> embedding artifact
  -> runtime and tensor metadata
  -> reproducibility check
  -> provenance-linked lab view
```

The first implementation uses a pinned 8M-parameter ESM-2 checkpoint and records sequence checksum, model revision, input handling, tensor shape, pooling method, runtime, hardware, embedding checksum, and repeat-run comparison. Long sequences require an explicit input window. It does not infer treatment relevance, protein function, clinical meaning, or biological causality.

After that contract is evaluated locally, the same provider boundary can be used to study BioNeMo Framework execution and NIM deployment without changing the public research-navigation application.

## Maintainer Checks

Before each release:

```powershell
python -m pytest -q
python -m build
```

Also complete the manual checks in [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md).
