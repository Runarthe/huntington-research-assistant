# Roadmap

This roadmap is directional, not a promise of clinical functionality.

## Vision

Huntington Research Assistant has two complementary goals:

1. Build a useful, transparent public-good tool for navigating Huntington's disease research.
2. Provide an open learning environment for scientific AI, digital biology, and evidence-grounded software engineering.

The stable application must remain useful without an LLM, GPU, NVIDIA account, or paid API. Experimental scientific-AI work must be optional, clearly labelled, and kept separate from verified literature metadata.

## Product Tracks

### Public-Good Application

The main Streamlit application focuses on literature search, registered clinical studies, reading workflows, accessible presentation, source-linked summaries, and evidence navigation. It must not provide diagnosis, treatment recommendations, study matching, or personalized medical guidance.

### Digital Biology Lab

An optional experimental area will support learning about:

- biological and scientific foundation models;
- NVIDIA BioNeMo Framework;
- NVIDIA NIM microservices;
- NVIDIA AI Blueprints;
- protein language models and embeddings;
- protein structure prediction and confidence measures;
- reproducible GPU inference and evaluation.

Lab work should live under an isolated `labs/` area or optional package. It must never be required to install or run the main application. Model predictions must be presented as experimental outputs, not medical findings or established evidence.

## v0.1: Public MVP

- Europe PMC search with Huntington-focused query expansion.
- Source-linked paper display, filters, categories, and timeline.
- Clinical-trial and recent-publication views.
- English/Norwegian UI basics.
- Optional local Ollama summaries with plain-language mode.
- Safety documentation, tests, and public contribution guidance.

## v0.2: Research Navigation and Trial Tracking (Released)

- Provider-backed Europe PMC pagination and date/open-access filters.
- CSV and BibTeX publication export.
- ClinicalTrials.gov tracker with status, phase, and country filters plus intervention and sponsor details.
- CSV export for visible registered studies.
- Publication types and prominent correction/retraction notices from Europe PMC.
- Stronger source grounding and deterministic disclaimers for local summaries.
- Norwegian UI with generated Norwegian explanations disabled by default pending professional review.
- A tabular alternative for the publication trend chart.
- An experimental source-linked research map using deterministic "mentioned in" relationships.

## v0.3: Stable Research Library (Released)

- Saved reading lists without sensitive user profiles.
- PubMed through official NCBI E-utilities.
- Deduplication across Europe PMC and PubMed.
- Provider-neutral labels, downloads, and fallback detail views.
- Validate Europe PMC, PubMed, ClinicalTrials.gov, combined search, pagination, and exports.
- Improve provider-comparison UX, pagination semantics, category vocabulary, and tagging tests.
- Complete mobile-layout and accessibility review.
- Expand and professionally review the Norwegian evaluation set.
- Improve error handling, loading feedback, and provider status reporting.
- Add stronger summary evaluation and citation-preservation tests.
- Update release documentation, changelog, screenshots, and package metadata.

## v0.4: Evidence Explorer and Lab Foundation (Released)

### Public-Good Application

- Compare a small set of papers side by side.
- Structure study type, population or model, outcomes, and stated limitations.
- Improve filtering for reviews, clinical studies, animal models, and preclinical research.
- Expand the controlled entity and topic vocabulary.
- Keep corrections, retractions, and source provenance visible during comparison and export.

### Digital Biology Lab

- Add an isolated `labs/` structure with optional dependencies.
- Document the roles of BioNeMo Framework, NIM inference services, and AI Blueprints.
- Introduce provider interfaces and mock responses so examples remain testable without GPU services.
- Resolve selected literature entities to stable external identifiers before running model inference.
- Record model version, parameters, input, output, licence, runtime, and provenance for every experiment.

## v0.5: Structured Entity Explorer (Released)

### Public-Good Application

- Normalize an initial catalogue of genes, proteins, biomarkers, compounds, and pathways found in publication titles and abstracts.
- Keep every entity mention linked to the exact source passage that supports it.
- Begin with conservative relationships such as "mentioned in" and paper-level co-occurrence.
- Show extraction method and confidence without implying scientific consensus.
- Add deterministic regression coverage for positive and negative alias examples.

## v0.6: Protein Intelligence Lab Prototype (Released)

- Make selected protein targets visible in the app with stable identifiers, planned manifests, and read-only provenance reports.
- Keep live retrieval, embeddings, AlphaFold/NIM workflows, and model inference gated outside the core app.
- Clearly separate literature evidence, database annotations, planned manifests, and future model predictions.

## v0.7: Evidence-Grounded Scientific Workflow (Released)

- Build one end-to-end, reproducible workflow before introducing multiple agents.
- Connect locally saved publications, controlled biomedical entities, curated protein targets, and provenance reports.
- Preserve exact source-paper passages before introducing model inference, confidence, or generated synthesis.
- Keep generated synthesis, live inference, and multi-agent workflows out of the release until source coverage and factual-consistency checks are stronger.

Example experimental flow:

```text
Paper
  -> biomedical entity
  -> authoritative sequence or database record
  -> BioNeMo or NIM inference
  -> model output and confidence
  -> provenance-linked exploration
```

## v0.8: Blueprint Experiment (Released)

- Study and reproduce a bounded NVIDIA digital-biology or virtual-screening Blueprint tutorial.
- Document container deployment, API contracts, GPU requirements, observability, evaluation, and licensing.
- Keep generated proteins or compounds in the experimental lab.
- Do not claim that a generated molecule, protein, or model output is safe, effective, or a treatment for Huntington's disease.
- Only promote lab components into the main application when they solve a demonstrated user need.
- Start with an offline scaffold that records planned provider families, mock output, provenance, and safety boundaries before any live provider is connected.

See [V0_8_BLUEPRINT_PLAN.md](V0_8_BLUEPRINT_PLAN.md) for the initial experiment plan.

## v0.9: Provider Adapter Foundations (Released)

- Add a non-secret provider configuration model for Blueprint-style lab providers.
- Make execution mode explicit: offline fixtures, planned manifests, or future reviewed live adapters.
- Expose provider readiness, credential requirements, and claim boundaries in both CLI and UI.
- Keep NVIDIA NIM, BioNeMo, AlphaFold, and Blueprint providers gated until an explicit adapter, provenance checks, licensing notes, and tests exist.
- Start with a safe public UniProt adapter for sequence-provenance metadata before introducing credentialed or GPU-backed workflows.

See [V0_9_PROVIDER_ADAPTERS.md](V0_9_PROVIDER_ADAPTERS.md) for the adapter boundary.

## Toward v1.0

A mature release should combine reliable multi-provider research navigation, clinical-trial discovery, evidence comparison, reading workflows, transparent summaries, and a carefully evaluated structured research map. Optional scientific-AI modules should demonstrate reproducible engineering without weakening the safety, accessibility, or maintainability of the public application.

## Explicitly Out of Scope

- Diagnosis or treatment recommendations.
- Personalized health or genetic-risk interpretation.
- Clinical decision support.
- Study matching, eligibility interpretation, or ranking studies for an individual.
- Automatic claims that a publication is a breakthrough.
- Presenting model-generated structures, molecules, relationships, or hypotheses as validated scientific findings.
- Requiring proprietary services, paid APIs, or specialist GPU hardware to use the core application.
