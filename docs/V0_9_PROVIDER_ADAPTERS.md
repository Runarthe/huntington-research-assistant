# v0.9 Provider Adapter Foundations

v0.9 introduces a safer boundary for future scientific-AI providers in the Digital Biology Lab.

The goal is not to run BioNeMo, NIM, AlphaFold, or NVIDIA Blueprint workflows yet. The goal is to make the integration shape explicit before any live service, GPU workflow, credential, or model output is connected.

## Core Idea

A provider adapter is a small boundary object that says:

- what provider family it represents;
- whether it is offline, planned only, or live;
- whether it is implemented;
- whether credentials would be required;
- what claim boundary applies to its outputs;
- what provenance must be recorded before output is trusted even as an experimental artifact.

This keeps the app honest. A provider can be visible as a learning target without implying that it has produced validated biomedical findings.

## Execution Modes

`offline`

Runs only local deterministic fixtures. This is the only mode that can generate output today.

`planned`

Creates manifests that describe what would be run. No provider, model, endpoint, GPU, or network call is used.

`live`

Reserved for future reviewed adapters. Unreviewed live provider configs are rejected.

## CLI Checks

List provider families:

```bash
python -m labs.blueprint_experiments list-providers
```

Inspect one provider family:

```bash
python -m labs.blueprint_experiments describe-provider bionemo
```

Generate a non-secret config skeleton:

```bash
python -m labs.blueprint_experiments provider-config bionemo --execution-mode planned --credentials-env-var BIONEMO_API_KEY
```

The command records the environment variable name only. Do not put secret values in config files, manifests, commits, screenshots, or issues.

## Safety Boundary

Provider configs and metadata are engineering records. They are not evidence that a model, provider, compound, pathway, or protein relationship is clinically meaningful.

The lab must not produce diagnosis, treatment recommendations, trial matching, personal health guidance, or claims about safety, efficacy, causality, or clinical suitability.

## Next Good Step

The next low-risk adapter should use public, deterministic metadata first, such as UniProt or AlphaFold Database metadata. Credentialed NVIDIA or BioNeMo workflows should stay gated until their inputs, outputs, licensing, runtime, and provenance contract are well understood.

## First Public-Data Adapter

The first public-data provider family is `uniprot`.

It is intentionally modest:

- planning mode records that UniProt sequence provenance would be used;
- generated output records sequence length and checksum metadata;
- no sequence interpretation is produced;
- no embedding, structure prediction, function prediction, treatment ranking, or clinical claim is produced;
- live retrieval still requires an explicit reviewed live config and an explicit run request.

This makes it useful for learning adapter design while preserving the public-good app boundary.
