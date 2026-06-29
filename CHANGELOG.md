# Changelog

All notable project changes are documented here. The project follows semantic versioning where practical.

## [Unreleased]

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
