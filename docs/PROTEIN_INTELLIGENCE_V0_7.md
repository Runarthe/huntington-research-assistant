# Protein Intelligence v0.7

v0.7 connects the optional Protein Intelligence Lab back to curated research-assistant provenance. It does not add live provider execution, biological hypothesis generation, target ranking, or medical interpretation.

The release theme is:

> Literature entity provenance -> curated protein target -> lab manifest provenance -> read-only target report.

## What v0.7 Adds

v0.7 adds an offline reporting spine:

- deterministic mapping from literature entities to curated protein targets;
- manifest registry records for planned, completed, failed, and invalid lab artifacts;
- target-level report JSON that combines literature mappings, source records, and lab manifests;
- an offline CLI helper for mapping entities, indexing manifests, and building target reports;
- small fixture JSON files for manual inspection and regression tests.

## What v0.7 Does Not Add

v0.7 intentionally excludes:

- real embedding providers;
- BioNeMo, NIM, AlphaFold, or external model calls;
- live network retrieval by default;
- generated biological hypotheses;
- therapeutic ranking or target scoring;
- claims about efficacy, causality, disease modification, or patient suitability.

## Safety Boundary

Every v0.7 output should preserve this distinction:

- literature evidence: what terms appeared in source records;
- catalogue provenance: how a term maps to a curated protein target;
- lab provenance: what sequence or embedding artifacts exist and how they were produced;
- interpretation boundary: no biological or medical conclusion is asserted by the report itself.

Reports are useful for navigation and auditability. They are not evidence synthesis.

## Example Workflow

After applying the v0.6 patches and the v0.7 patch series:

```bash
python -m labs.protein_intelligence.report_cli map-entities \
  labs/protein_intelligence/examples/entities.json
```

Index local manifests:

```bash
python -m labs.protein_intelligence.report_cli index-manifests \
  labs/protein_intelligence/manifests/
```

Build a target report:

```bash
python -m labs.protein_intelligence.report_cli target-report HTT \
  --entities labs/protein_intelligence/examples/entities.json \
  --sources labs/protein_intelligence/examples/sources.json \
  --manifest-path labs/protein_intelligence/manifests/
```

The command prints JSON. The output is intended to be easy to snapshot-test, inspect in reviews, and later feed into a read-only application panel.

For review checklists or release notes, emit a compact validated summary:

```bash
python -m labs.protein_intelligence.report_cli target-report HTT \
  --entities labs/protein_intelligence/examples/entities.json \
  --manifest-path labs/protein_intelligence/manifests/ \
  --summary
```

Every CLI payload is validated before it is written to stdout. Invalid generated payloads fail fast instead of quietly producing report-shaped nonsense.

## Report Shape

A target report contains:

- `schema_version`: report contract version;
- `target`: curated target metadata and stable identifiers;
- `literature`: mapped entity records and optional source summaries;
- `lab_artifacts`: manifest registry records for the target;
- `interpretation`: a status label and explicit claim boundary.

Expected interpretation statuses:

- `literature-and-lab-provenance`;
- `literature-provenance-only`;
- `lab-provenance-only`;
- `no-local-provenance`.

## Implementation Notes

The v0.7 reporting modules are deliberately separate from the Streamlit app and from the provider contract. This keeps the public application independent from optional lab code and keeps provider integration as a later, gated step.

The CLI helper lives in `labs.protein_intelligence.report_cli` rather than patching the package-level `__main__.py` immediately. That avoids brittle patch conflicts while the v0.6 CLI is still settling. A later cleanup can expose these commands through the main lab CLI.

## Next After v0.7

Reasonable v0.8 candidates:

- read-only UI panel for mapped protein targets;
- stable app-side JSON export of entity/source records;
- reviewed external identifier expansion;
- optional provider adapters behind explicit local configuration;
- richer manifest registry summaries.
