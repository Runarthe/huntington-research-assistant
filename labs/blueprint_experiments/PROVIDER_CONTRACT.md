# Blueprint Provider Contract

This contract describes how future live Blueprint, NIM, BioNeMo, AlphaFold, or other scientific-AI providers should be added to the lab.

The current implementation only executes the `mock` provider. All live provider families are gated placeholders.

The `uniprot` provider family is a public-data provenance adapter. It can be planned without network calls. Retrieval metadata must remain explicitly reviewed and requested, and it still cannot produce biological or clinical interpretation.

## Provider Responsibilities

Every provider must:

- accept a `BlueprintRunRequest`;
- expose non-secret `BlueprintProviderConfig` metadata;
- declare whether it is `offline`, `planned`, or future `live`;
- return a manifest matching `blueprint-experiment-manifest.v1`;
- preserve target identifiers and source URLs;
- record provider name, model or service version, parameters, runtime, output path, and limitations;
- clearly identify whether the output came from a mock fixture or live provider;
- avoid personal health data;
- avoid treatment, diagnosis, trial matching, safety, efficacy, causality, or clinical-suitability claims.

## Planning Before Execution

Providers should support a `plan` path before live execution. Planning records what would be run without calling a provider.

Live `run` methods must remain unavailable until:

- the adapter is implemented explicitly;
- credentials are documented outside Git;
- runtime and licensing requirements are documented;
- output manifests include confidence and limitation fields;
- tests cover disabled-by-default behavior;
- safety wording has been reviewed.

## Current State

- `MockBlueprintProvider` can plan and run deterministic offline fixtures.
- `PublicUniProtProvider` can plan public sequence-provenance workflows and can generate checksum metadata when a reviewed live config and explicit run request are supplied.
- `GatedLiveProvider` can plan future provider families but raises `LiveProviderDisabledError` for execution.
- `BlueprintProviderConfig` records safe adapter configuration without storing secret values.
- Unreviewed live configs are rejected before a provider object is used.

This gives the project a safe extension point without implying that any provider output is validated biomedical evidence.
