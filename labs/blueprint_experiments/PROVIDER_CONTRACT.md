# Blueprint Provider Contract

This contract describes how future live Blueprint, NIM, BioNeMo, AlphaFold, or other scientific-AI providers should be added to the lab.

The current implementation only executes the `mock` provider. All live provider families are gated placeholders.

## Provider Responsibilities

Every provider must:

- accept a `BlueprintRunRequest`;
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
- `GatedLiveProvider` can plan future provider families but raises `LiveProviderDisabledError` for execution.

This gives the project a safe extension point without implying that any provider output is validated biomedical evidence.
