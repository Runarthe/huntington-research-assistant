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

## v0.5: Structured Research Map and Protein Intelligence Prototype

### Research Map

- Normalize genes, proteins, biomarkers, compounds, pathways, publications, and registered studies.
- Keep every entity and relationship linked to the passage or registry field that supports it.
- Begin with conservative relationships such as "mentioned in", "described in", and "registered intervention".
- Show extraction method and confidence without implying scientific consensus.
- Evaluate extraction against a manually reviewed Huntington abstract set.

### Protein Intelligence Lab

- Retrieve selected protein sequences from authoritative databases with stable identifiers.
- Generate protein embeddings with a documented protein language model such as ESM-2.
- Explore similarity as a model output, not as proof of shared biological function.
- Evaluate an AlphaFold or compatible NIM workflow on a bounded educational example.
- Visualize structure confidence, including pLDDT or PAE where available.
- Clearly separate literature evidence, database annotations, and model predictions.

## v0.6: Evidence-Grounded Scientific Workflow

- Build one end-to-end, reproducible workflow before introducing multiple agents.
- Connect publication, biomedical entity, authoritative sequence, model inference, confidence, and provenance.
- Add a cited research-comparison workflow that cannot silently discard contradictory sources.
- Label generated synthesis and keep sentence-level links to supporting evidence where possible.
- Evaluate factual consistency, source coverage, uncertainty, latency, and cost.

Example experimental flow:

```text
Paper
  -> biomedical entity
  -> authoritative sequence or database record
  -> BioNeMo or NIM inference
  -> model output and confidence
  -> provenance-linked exploration
```

## v0.7: Blueprint Experiment

- Study and reproduce a bounded NVIDIA digital-biology or virtual-screening Blueprint tutorial.
- Document container deployment, API contracts, GPU requirements, observability, evaluation, and licensing.
- Keep generated proteins or compounds in the experimental lab.
- Do not claim that a generated molecule, protein, or model output is safe, effective, or a treatment for Huntington's disease.
- Only promote lab components into the main application when they solve a demonstrated user need.

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
