# Protein Intelligence Lab

This lab area contains the v0.6 foundation for bounded protein-sequence and model-output experiments. It is optional and is not imported by the core Streamlit application.

## v0.6 Starting Scope

The first slice is deliberately small:

- define a few Huntington-relevant protein targets with stable identifiers;
- resolve configured symbols, entity IDs, UniProt, HGNC, and NCBI Gene IDs locally;
- generate planned sequence-retrieval manifests before any model work;
- parse FASTA records and compute sequence checksums for provenance;
- retrieve UniProt FASTA records through an injectable adapter that can be mocked in tests;
- convert retrieved sequences into completed provenance manifests;
- provide a deterministic mock embedding provider for interface and manifest testing;
- define disabled-by-default embedding adapter configuration for future real providers;
- keep every output labelled as experimental lab data, not literature evidence or medical guidance.

The initial targets are:

- HTT / huntingtin, UniProt `P42858`;
- BDNF, UniProt `P23560`;
- NEFL / neurofilament light polypeptide, UniProt `P07196`.

## Not Included Yet

- real embedding models;
- AlphaFold or NIM calls;
- BioNeMo integration;
- generated biological hypotheses;
- UI integration with the public app.

Those belong behind explicit adapters, fixtures, and provenance checks.

## Prototype Flow

```text
ProteinTarget
  -> local identifier resolution
  -> UniProt FASTA retrieval
  -> ProteinSequenceRecord with checksum
  -> sequence retrieval manifest
  -> mock embedding provider
  -> embedding manifest with input provenance
```

The mock embedding vector is a deterministic test fixture. It has no biological meaning.

## CLI

The lab helper emits JSON manifests and is offline-safe by default:

```bash
python -m labs.protein_intelligence list-targets
python -m labs.protein_intelligence resolve-identifier HGNC:4851 --date 2026-07-03
python -m labs.protein_intelligence plan HTT --date 2026-07-03
python -m labs.protein_intelligence retrieve HTT --date 2026-07-03
python -m labs.protein_intelligence mock-embed BDNF --sequence ACDEFG --dimensions 8
python -m labs.protein_intelligence mock-embed HTT --fasta-file labs/protein_intelligence/fixtures/htt.fragment.fasta
python -m labs.protein_intelligence validate-manifest outputs/example-manifest.json
```

`mock-embed` uses a deterministic fixture vector. It does not call ESM-2, BioNeMo, NIM, AlphaFold, or any external service.
`retrieve` is also offline-safe by default: without `--live`, it emits a failed manifest explaining that live UniProt retrieval was disabled.
Real embedding providers belong behind disabled-by-default adapter configuration. The default public test suite must keep using fixtures and failure manifests, not live model calls.

The FASTA files in [`fixtures/`](fixtures/) are short offline fragments for tooling tests. They are not complete reference sequences and must not be used for biological interpretation.

`resolve-identifier` only performs exact local catalogue matching. It does not call HGNC, UniProt, NCBI, or any ontology service, and it does not infer synonyms beyond the identifiers already configured in code.

To perform a real UniProt retrieval in a manual lab run, pass `--live`:

```bash
python -m labs.protein_intelligence retrieve BDNF --live
```

Do not use live retrieval in default CI tests.

`validate-manifest` performs structural checks only. It confirms that required manifest fields are present, status is known, inputs exist, and limitations are recorded. It does not validate biological claims.
