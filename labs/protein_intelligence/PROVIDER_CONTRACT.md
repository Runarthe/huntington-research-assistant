# Protein Embedding Provider Contract

This contract defines what a future real embedding adapter must provide before it can be used in the Digital Biology Lab.

## Required Inputs

- `ProteinSequenceRecord` with:
  - target entity ID;
  - UniProt accession;
  - normalized amino-acid sequence;
  - sequence checksum;
  - source URL;
  - retrieval date.

Adapters must not accept personal health data or raw publication text as embedding input.

## Required Output

Every provider must return a `ProteinEmbeddingRecord` or a failed embedding manifest. A successful record must include:

- provider name;
- model name;
- model version;
- vector values;
- vector dimensions;
- generation date;
- input sequence provenance.

The adapter must not attach biological meaning to the vector. Similarity, function, structure, pathogenicity, treatment relevance, and clinical value require separate evaluated workflows.

## Runtime Metadata

A real adapter manifest must record:

- interface type, such as local Python, container, HTTP API, NIM, or BioNeMo;
- container image and digest when a container is used;
- hardware class, including GPU model when relevant;
- model parameters and preprocessing choices;
- timeout and retry behavior;
- licence and access constraints.

Adapters start disabled by default. Enabling a real provider must be an explicit
manual lab decision and must preserve the same manifest fields as the disabled
adapter path.

## Test Requirements

Every adapter needs:

- fixture-driven tests that run without network access;
- an unavailable-service test path;
- output shape tests;
- provenance preservation tests;
- failure manifest tests.

Real model calls belong in manual lab runs or integration jobs, not the default public test suite.

## Safety Boundary

Embedding output is an experimental model representation. It is not evidence of biological relationship, therapeutic value, clinical effectiveness, diagnosis, or personal medical relevance.
