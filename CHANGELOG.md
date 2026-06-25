# Changelog

All notable project changes are documented here. The project follows semantic versioning where practical.

## [Unreleased]

### Added

- Local saved reading list for papers, including add/remove controls, source-preserving exports, and cache tests.

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
