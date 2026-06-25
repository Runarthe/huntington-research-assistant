# Safety Policy

## Scope

Huntington Research Assistant helps people find and understand published Huntington's disease research. It is an educational literature-navigation tool, not a clinical system.

## Required Disclaimer

The app must always show a prominent disclaimer explaining that it is not medical advice and that qualified healthcare professionals should be consulted for diagnosis, treatment, and genetic counselling.

## The App Must Not

- Diagnose Huntington's disease or any other condition.
- Recommend, rank, or personalize treatments.
- Interpret symptoms, genetic results, or risk for an individual.
- Replace genetic counselling or clinical care.
- Ask users for personal health data or identifying information.
- Present generated summaries as complete, authoritative, or clinically actionable.
- Hide the source paper or separate a summary from its source context.
- Recommend, rank, or match clinical studies for an individual.
- Interpret registry eligibility criteria for a user's personal circumstances.

## Source and Summary Requirements

- Literature results must link to the Europe PMC or PubMed source record whenever available.
- DOI and PMID should be shown when available.
- Local summaries must include limitations/uncertainty and an educational-use disclaimer.
- Plain-language mode may simplify wording, but must preserve uncertainty.
- Experimental Norwegian explanations must pass deterministic checks for selected numbers and protected biomedical identifiers before display.
- The original abstract must remain accessible next to any generated summary.
- Registered studies must link to their ClinicalTrials.gov record.
- Registry status must be presented as reported metadata, not as evidence that an intervention is safe or effective.
- Users must be reminded that study status and registry details can change.

## Data Handling

- Selected literature providers, such as Europe PMC and PubMed, receive literature search queries.
- ClinicalTrials.gov receives tracker filter queries.
- Local Ollama summaries should remain local by default.
- SQLite history must not be treated as a place for sensitive or medical data.
- New telemetry or analytics must be documented and opt-in before introduction.

## Reporting Safety Issues

Open a GitHub issue describing the unsafe behavior without including personal medical information. Security-sensitive reports should use a private maintainer contact once one is published.
