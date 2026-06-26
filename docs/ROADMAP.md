# Roadmap

This roadmap is directional, not a promise of clinical functionality.

Reading lists planned for v0.3.

## v0.1: Public MVP

- Europe PMC search with Huntington-focused query expansion.
- Source-linked paper display, filters, categories, and timeline.
- Clinical-trial and recent-publication views.
- English/Norwegian UI basics.
- Optional local Ollama summaries with plain-language mode.
- Safety documentation, tests, and public contribution guidance.

## v0.2: Research Navigation and Trial Tracking (Current)

- Provider-backed Europe PMC pagination and date/open-access filters.
- CSV and BibTeX publication export.
- ClinicalTrials.gov tracker with status, phase, and country filters plus intervention and sponsor details.
- CSV export for visible registered studies.
- Publication types and prominent correction/retraction notices from Europe PMC.
- Stronger source grounding and deterministic disclaimers for local summaries.
- Norwegian UI with generated Norwegian explanations disabled by default pending professional review.
- A tabular alternative for the publication trend chart.
- An experimental source-linked research map using deterministic "mentioned in" relationships.

## v0.3: Evidence Quality and Reading Workflow

- Saved reading lists without sensitive user profiles.
- Improved category vocabulary and tagging tests.
- Complete manual accessibility and mobile-layout review.
- Expand and professionally review the Norwegian evaluation set.
- Add PubMed/NCBI E-utilities as a second provider.
- Deduplicate records across providers.
- Add stronger summary evaluation and citation-preservation tests.
- Evaluate the experimental source-linked research map against a manually reviewed abstract set.

## Later: Structured Research Map (Experimental)

- Expand the initial deterministic genes, proteins, pathways, and compounds research-map preview.
- Keep every entity and relationship linked to the paper passage that supports it.
- Show extraction confidence and make uncertain relationships explicit.
- Start with deterministic biomedical vocabularies and manual evaluation before adding LLM extraction.
- Present the graph as research navigation, never as treatment guidance or clinical evidence ranking.

## Explicitly Out of Scope for Now

- Diagnosis or treatment recommendations.
- Personalized health or genetic-risk interpretation.
- AlphaFold integration.
- NVIDIA BioNeMo integration.
- Autonomous or agentic AI workflows.
- Clinical decision support.
- Study matching, eligibility interpretation, or ranking studies for an individual.
- Automatic claims that a publication is a breakthrough.
