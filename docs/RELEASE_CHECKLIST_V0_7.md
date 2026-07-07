# v0.7 Release Checklist

Use this checklist after v0.6 is merged and before tagging v0.7.

## Patch Application

- Apply the v0.6 patch series.
- Run the v0.6 test suite.
- Apply the v0.7 patch series in order.
- Confirm no unrelated files are modified.

## Tests

Run the full suite:

```bash
pytest
```

Run the lab-focused tests:

```bash
pytest tests/test_protein_intelligence_lab.py tests/test_protein_intelligence_v07.py tests/test_protein_report_cli.py
```

## CLI Smoke Checks

Map fixture entities:

```bash
python -m labs.protein_intelligence.report_cli map-entities labs/protein_intelligence/examples/entities.json
```

Index local manifests:

```bash
python -m labs.protein_intelligence.report_cli index-manifests labs/protein_intelligence/manifests/
```

Build reports for the initial targets:

```bash
python -m labs.protein_intelligence.report_cli target-report HTT --entities labs/protein_intelligence/examples/entities.json --sources labs/protein_intelligence/examples/sources.json --manifest-path labs/protein_intelligence/manifests/
python -m labs.protein_intelligence.report_cli target-report BDNF --entities labs/protein_intelligence/examples/entities.json --sources labs/protein_intelligence/examples/sources.json --manifest-path labs/protein_intelligence/manifests/
python -m labs.protein_intelligence.report_cli target-report NEFL --entities labs/protein_intelligence/examples/entities.json --sources labs/protein_intelligence/examples/sources.json --manifest-path labs/protein_intelligence/manifests/
```

Build a compact summary for release review:

```bash
python -m labs.protein_intelligence.report_cli target-report HTT --entities labs/protein_intelligence/examples/entities.json --manifest-path labs/protein_intelligence/manifests/ --summary
```

## Review

- Confirm report outputs contain no generated biological hypotheses.
- Confirm target reports include claim-boundary text.
- Confirm invalid manifests are indexed as invalid rather than crashing the registry.
- Confirm missing manifests produce `literature-provenance-only` or `no-local-provenance` statuses as appropriate.
- Confirm public app imports do not depend on `labs.protein_intelligence`.

## Release Decision

v0.7 is ready when deterministic reports are useful enough to inspect manually and all lab paths remain offline-safe by default.
