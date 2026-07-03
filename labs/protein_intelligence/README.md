# Protein Intelligence Lab

This lab area contains the v0.6 foundation for bounded protein-sequence and model-output experiments. It is optional and is not imported by the core Streamlit application.

## v0.6 Starting Scope

The first slice is deliberately small:

- define a few Huntington-relevant protein targets with stable identifiers;
- generate planned sequence-retrieval manifests before any model work;
- parse FASTA records and compute sequence checksums for provenance;
- retrieve UniProt FASTA records through an injectable adapter that can be mocked in tests;
- convert retrieved sequences into completed provenance manifests;
- provide a deterministic mock embedding provider for interface and manifest testing;
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
  -> UniProt FASTA retrieval
  -> ProteinSequenceRecord with checksum
  -> sequence retrieval manifest
  -> mock embedding provider
  -> embedding manifest with input provenance
```

The mock embedding vector is a deterministic test fixture. It has no biological meaning.
