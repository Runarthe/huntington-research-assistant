# Changelog

All notable project changes are documented here. The project follows semantic versioning where practical.

## [0.12.0] - Unreleased

### Added

- Added a non-networking BioNeMo environment preflight for the CLI and Protein Lab.
- Added typed checks for host OS, CPU architecture, NVIDIA GPU and driver, bfloat16 compute capability, Docker Linux engine, declared NVIDIA runtime, and immutable image provenance.
- Added a downloadable preflight report that explicitly records that no credential was inspected, no network call was made, and no container was started.

### Safety

- The preflight uses only fixed diagnostic commands and never runs `docker login`, `docker pull`, or `docker run`.
- A detected GPU or Docker installation is not reported as proof that BioNeMo can execute.
- GPUs absent from the reviewed NVIDIA support matrix remain flagged for review even when they meet the documented compute-capability threshold.

## [0.11.0] - 2026-07-19

### Added

- Added a versioned, provider-neutral protein embedding descriptor for comparing provenance without interpreting vectors.
- Added a planned BioNeMo Framework ESM-2 manifest that reuses the exact local sequence checksum, one-based window, and no-silent-truncation policy.
- Added a deterministic provider-parity report covering input handling, model identity, checkpoint identity, pooling, execution status, tensor metadata, checksums, hardware, and numerical precision.
- Added a bilingual Provider Parity review in Protein Lab with readable status labels, official BioNeMo source links, and downloadable plan/report JSON.
- Added a credential-free BioNeMo execution bundle containing the exact selected input CSV, reviewed settings, immutable-container guard, `infer_esm2` command, and result exporter for an external Linux/GPU environment.
- Added bounded import validation for generated BioNeMo result JSON, including exact plan/input matching, tensor shape, runtime metadata, and checksums without accepting full vector payloads.
- Added a deterministic offline result fixture that exercises the import and comparison path without claiming a BioNeMo, container, or GPU run.

### Safety

- BioNeMo and NVIDIA NIM remain plan-only; v0.11 performs no NVIDIA, remote, credentialed, or GPU provider call.
- External execution requires an explicit user-run bundle in a separately reviewed environment; the Streamlit app never invokes Docker or forwards an NGC credential.
- Unknown or unexecuted fields are labelled `not-available` or `not-comparable`, never inferred as matches.
- The report explicitly excludes biological similarity, protein function, structure, causality, treatment relevance, efficacy, safety, and clinical interpretation.

## [0.10.0] - 2026-07-19

### Added

- Added an optional local ESM-2 adapter pinned to `facebook/esm2_t6_8M_UR50D` revision `c731040`.
- Added explicit local or cached UniProt sequence inputs, sequence checksums, one-based input windows, and strict rejection of silent truncation.
- Added downloadable planned and generated embedding manifests with model, runtime, hardware, tensor-shape, pooling, vector, and checksum provenance.
- Added repeat-run checksum comparison for the same model and sequence window.
- Added a user-local authoritative sequence cache and offline fixture fragments for HTT, BDNF, and NEFL.
- Added a `scientific-ai` optional dependency group; core application installs do not include PyTorch or Transformers.

### Safety

- ESM-2 runs only after an explicit user action and confirmation.
- Embeddings remain experimental computational artifacts and are not interpreted as protein function, biological similarity, disease causality, treatment relevance, or clinical meaning.
- Full HTT and other long sequences require an explicit bounded window rather than hidden truncation.

## [0.9.1] - 2026-07-19

### Changed

- Clarified Blueprint Lab provider status labels so mock fixtures, public-data providers, planned-only adapters, and live-reviewed adapters are visually distinct.
- Added a concise four-step Blueprint workflow and an adapter-availability signal.
- Limited the preview to execution modes it can currently perform: offline for mock fixtures and plan-only for other providers.
- Hid mock artifacts and `run-mock` commands when a non-mock provider is selected.

### Added

- Added provider-specific planned-manifest downloads.
- Added `docs/PROJECT_STATE.md` as a maintained overview of stable, experimental, planned, and unavailable functionality.

### Safety

- The Blueprint Lab preview now states when a provider is fixture-only or public-data gated, reducing the chance that users mistake provenance planning for live model execution.
- Non-mock provider selections no longer present deterministic mock output beside their planned artifacts.

## [0.9.0] - 2026-07-16

### Added

- Added a provider-adapter configuration model for Blueprint experiments.
- Added explicit `offline`, `planned`, and `live` execution modes for future scientific-AI providers.
- Added provider metadata for UI and CLI inspection without calling live services.
- Added `describe-provider` and `provider-config` CLI commands.
- Added Blueprint Lab UI status fields for provider readiness, live execution, and credential requirements.
- Added a public UniProt provider family for planned sequence-provenance workflows.

### Safety

- Live provider execution remains disabled by default.
- Unreviewed live provider configs are rejected.
- Provider catalogue entries describe integration boundaries only, not biomedical capability claims.
- UniProt adapter output is public source provenance only, not model output or biological interpretation.

## [0.8.3] - 2026-07-16

### Added

- Added a Blueprint Lab preview inside the experimental Protein Lab tab.
- Added UI controls for Blueprint provider family, target selection, planned manifests, mock manifests, registry inspection, and JSON downloads.
- Added a Blueprint manifest registry for indexing local lab manifests without executing providers.
- Added an `index-manifests` CLI command for Blueprint experiment artifacts.
- Added registry tests for valid manifests, invalid manifests, target filtering, and stable checksums.

### Safety

- The Blueprint Lab preview remains mock/registry-only and does not execute live NVIDIA NIM, BioNeMo, AlphaFold, Blueprint, GPU, or provider calls.
- Registry records describe provenance only. They are not biomedical findings, provider capability claims, clinical evidence, or treatment guidance.

## [0.8.1] - 2026-07-15

### Added

- Added a Blueprint provider contract for future live adapters.
- Added a mock provider implementation and gated live-provider placeholder.

### Safety

- Live provider families can be planned but still cannot execute without a future explicit adapter.

## [0.8.0] - 2026-07-15

### Added

- Added an isolated Blueprint Experiments Lab scaffold under `labs/blueprint_experiments`.
- Added a Blueprint-style manifest contract for planned and generated lab artifacts.
- Added offline CLI helpers for listing provider families, planning gated experiments, running deterministic mock output, and validating manifests.
- Added a deterministic HTT mock manifest fixture with explicit safety boundaries and no live provider calls.

### Safety

- The v0.8 scaffold does not run NVIDIA NIM, BioNeMo, AlphaFold, Blueprint workflows, GPU inference, or any live provider by default.
- Mock outputs are fixture values for engineering tests only and are not structural predictions, biomedical findings, or clinical evidence.

## [0.7.1] - 2026-07-15

### Changed

- Marked the v0.7 documentation as released rather than in-progress.
- Added clearer v0.8 planning notes for a bounded Digital Biology Blueprint experiment.
- Added Streamlit troubleshooting notes for stale local servers and confusing localhost ports.
- Clarified README release wording and near-term roadmap links.

## [0.7.0] - 2026-07-14

### Added

- Protein Lab reports can now use saved reading-list papers as their source context.
- Reading-list papers are converted into controlled entity mentions before being mapped to curated protein targets.
- Target reports now preserve source record URLs and exact evidence passages from matched paper titles or abstracts.
- A sidebar toggle switches UI explanations between simple and detailed help text.
- OpenClaw patch artifacts are ignored locally so they do not accidentally enter release commits.

### Safety

- Reading-list powered target reports remain provenance/navigation artifacts only. A source-paper connection means a controlled term was mentioned, not that a paper supports causality, efficacy, clinical relevance, or treatment suitability.

### Known Limitations

- The reading-list workflow depends on the small deterministic entity catalogue and will miss many valid papers or concepts.
- Source links are only as complete as the locally saved paper metadata.
- No live model calls, protein embeddings, AlphaFold/NIM execution, or BioNeMo workflows are added in this release.

## [0.6.0] - 2026-07-14

### Added

- An experimental Protein Lab tab that makes the optional protein-target infrastructure visible in the Streamlit app.
- Curated HTT, BDNF, and NEFL target cards with UniProt, HGNC, and NCBI Gene identifiers.
- Read-only target reports, planned sequence manifests, report summaries, JSON downloads, and matching CLI commands.

### Safety

- The Protein Lab remains offline and provenance-only in the app. It does not run live model calls, rank targets, generate hypotheses, or provide medical guidance.

### Known Limitations

- Protein Lab reports are navigation/provenance artifacts only and are not biomedical conclusions.
- Live UniProt retrieval, real protein embeddings, AlphaFold/NIM workflows, and BioNeMo integrations remain gated future work.

## [0.5.0] - 2026-07-03

### Added

- A structured entity-explorer foundation with versioned canonical entities, aliases, extraction method, and mention-confidence labels.
- Biomarkers as a distinct catalogued entity type, beginning with neurofilament light.
- Source-paper co-occurrence tables that help users find related terms without asserting biological relationships.
- An eight-case maintainer-reviewed synthetic entity-extraction fixture with positive and negative alias examples.

### Safety

- Entity co-occurrence is labelled only as appearing in the same source papers and never as evidence of causation, efficacy, or clinical relevance.

### Known Limitations

- The v0.5 entity catalogue is intentionally small and deterministic; it will miss many valid entities.
- The current entity-extraction fixture is synthetic regression coverage, not biomedical ground truth.
- Stable external identifiers such as HGNC, UniProt, ChEBI, and Reactome mappings are planned but not included in this release.
- Protein-sequence retrieval, embeddings, structure prediction, and BioNeMo/NIM experiments remain future Digital Biology Lab work and are not part of the core v0.5 application.

## [0.4.0] - 2026-06-29

### Added

- A source-linked Evidence Explorer for comparing two to five papers from the local reading list.
- Conservative, rule-based study-design and research-context classification.
- Exact abstract passages that may describe results, limitations, or uncertainty, with no generated interpretation.
- Detailed Evidence Explorer CSV export with source URLs and extraction output.
- An isolated Digital Biology Lab foundation with learning documentation and an experiment-manifest example.
- Explicit local "seen" state plus search filters for hiding saved or previously seen papers.
- A 12-case maintainer-reviewed classification fixture covering human, animal, cell, molecular, computational, review, and unknown contexts.

### Changed

- Evidence Explorer context detection now avoids treating background patient mentions as study populations and uses a neutral molecular/laboratory fallback when the experimental system is not otherwise reported.
- Search and paper-card controls were verified at a 390 x 844 emulated mobile viewport; physical-device and screen-reader checks remain outstanding.

### Safety

- Evidence Explorer passages are labelled as navigation aids rather than assessments of evidence strength, study quality, clinical relevance, or treatment effectiveness.
- Digital Biology Lab experiments remain optional and separate from the core application.

### Known Limitations

- Evidence classifications are conservative rule-based navigation signals, not assessments of study quality or evidence strength.
- Classification fixtures are maintainer-reviewed synthetic regression cases rather than biomedical ground truth.
- Mobile layout was checked in an emulated viewport; physical-device, keyboard-only, 200% zoom, and screen-reader reviews remain outstanding.

## [0.3.0] - 2026-06-29

### Added

- Local saved reading list for papers, including add/remove controls, source-preserving exports, and cache tests.
- PubMed search through official NCBI E-utilities.
- Combined Europe PMC and PubMed search with deduplication by PMID, DOI, and title/year.
- Provider provenance on merged records, including combined source labels.
- In-app detail fallback when a browser blocks Streamlit downloads.

### Changed

- Search actions and source links now use provider-neutral labels.
- Release documentation now separates the stable public-good application from optional future Digital Biology Lab experiments.

### Safety

- PubMed integration preserves direct source links and does not add generated medical interpretation.
- Reading lists remain local and do not require user profiles or personal health information.

### Known Limitations

- Combined-provider totals and pagination reflect different upstream provider semantics.
- Downloads may be handled differently by embedded browsers; the detail fallback remains available.
- PubMed citation counts and Europe PMC open-access metadata are not always available from both providers.

## [0.2.0] - 2026-06-24

### Added

- Provider-backed Europe PMC pagination, publication-year filters, and open-access filters.
- Publication dashboard with yearly counts, selected-period totals, and current-year counts.
- CSV and BibTeX publication exports plus per-paper metadata and abstract downloads.
- ClinicalTrials.gov tracker with status, phase, country, intervention, sponsor, and update information.
- CSV export for registered-study results.
- Publication-type metadata and visible correction or retraction notices.
- English plain-language and research-detail summary modes using optional local Ollama models.
- Norwegian UI labels and safety information.
- Experimental source-linked research map for deterministic gene, protein, pathway, and compound mentions.
- Accessibility, Norwegian-language, research-map, safety, roadmap, and contribution documentation.

### Changed

- SQLite cache storage defaults to an operating-system local data directory to avoid sync-folder locking problems.
- Europe PMC abstracts are normalized more carefully, including structured section headings.
- Summary storage preserves multiple paper summaries during a Streamlit session.
- Norwegian abstract labels now make clear that the source abstract remains in English.

### Safety

- Norwegian generated explanations are disabled by default after local testing found unreliable biomedical language.
- Research-map edges mean only "mentioned in" and always retain source evidence.
- Registered-study status is presented as registry metadata, not as evidence of safety, effectiveness, or suitability.

### Known Limitations

- The app depends on the availability and access policies of Europe PMC and ClinicalTrials.gov.
- Local summaries may be incomplete or inaccurate and are not medically validated.
- The research map uses a small controlled vocabulary and may miss entities or ambiguous terminology.
- Norwegian translation of abstracts and summaries is planned for a later reviewed release.

## [0.1.0]

- Initial public MVP with Europe PMC search, paper display, topic tagging, local cache, safety copy, and optional local summarization.
