# Project State

Last reviewed: 2026-07-19

This page is the quickest way to understand what Huntington Research Assistant can do today, what remains experimental, and what the newest development work is intended to teach.

## Release Status

- Latest public release: `v0.9.1`
- Next planned version: `v0.10.0`
- Next development focus: the first bounded local protein foundation-model experiment
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

This is not a full knowledge graph and is not classic retrieval-augmented generation. The current graph relationships mean only "mentioned in" or "catalogued in the same source paper." The lab artifacts describe engineering provenance rather than biomedical findings.

## What v0.9 and v0.9.1 Add

`v0.9.0` introduced a provider-adapter boundary for `mock`, `uniprot`, `bionemo`, `nvidia_nim`, `alphafold`, `nvidia_blueprint`, and future providers. A provider records whether it is implemented, whether live execution is enabled, and what claim boundary applies.

`v0.9.1` makes that boundary easier to understand in the UI:

- Mock exposes deterministic offline test data.
- UniProt is an implemented public-data boundary, but the UI remains plan-only.
- BioNeMo, NVIDIA NIM, AlphaFold, and NVIDIA Blueprint are plan-only placeholders.
- Non-mock providers no longer display mock artifacts or mock-run commands.
- The UI exposes only execution modes it can currently perform safely.

No live NVIDIA, BioNeMo, NIM, AlphaFold, Blueprint, or GPU inference runs in the application today.

## Using the Newest Addition

1. Run `streamlit run app/streamlit_app.py`.
2. Open **Protein Lab (experimental)**.
3. Scroll to **Blueprint Lab preview**.
4. Select a curated protein target and provider family.
5. Inspect provider status and adapter availability.
6. Expand the planned manifest to see the intended inputs, provider, output type, and safety boundary.
7. With Mock selected, inspect or download the deterministic fixture.
8. Review the local registry to see indexed manifests and checksums.

The CLI commands shown in the app are equivalent developer checks. They are optional for normal UI use.

## Learning Progress

The project has already exercised:

- biomedical API integration and provider error handling;
- typed data models and cross-provider deduplication;
- local LLM integration and safety-aware summarization;
- deterministic biomedical entity extraction;
- evidence-preserving UI and export design;
- identifier resolution and artifact provenance;
- provider interfaces, execution gating, manifests, registries, CI, and releases.

It has not yet exercised real protein-model tensors, GPU inference, NIM deployment, BioNeMo runtime execution, model-output evaluation, or structure-prediction interpretation.

## Recommended Next Milestone

The proposed `v0.10.0` milestone is one bounded, optional foundation-model workflow:

```text
authoritative sequence record
  -> versioned local ESM-2 adapter
  -> embedding artifact
  -> runtime and tensor metadata
  -> reproducibility check
  -> provenance-linked lab view
```

The first implementation should use a small local ESM-2 checkpoint and record sequence checksum, model version, input handling, tensor shape, pooling method, runtime, and hardware. It should not infer treatment relevance, protein function, clinical meaning, or biological causality.

After that contract is evaluated locally, the same provider boundary can be used to study BioNeMo Framework execution and NIM deployment without changing the public research-navigation application.

## Maintainer Checks

Before each release:

```powershell
python -m pytest -q
python -m build
```

Also complete the manual checks in [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md).
