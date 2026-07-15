# v0.8 Blueprint Experiment Plan

v0.8 should be a bounded learning experiment, not a broad product expansion.

The goal is to learn the shape of NVIDIA digital-biology tooling while keeping the public Huntington Research Assistant easy to install, safe, and useful without specialist hardware.

## Candidate Experiment

Start with one small workflow under `labs/`:

1. Select one documented NVIDIA digital-biology Blueprint, BioNeMo example, NIM endpoint, or compatible protein-model tutorial.
2. Reproduce the setup in an isolated lab folder.
3. Record exact inputs, environment, model or service version, parameters, runtime requirements, output files, and known limitations.
4. Add a deterministic mock or fixture path so tests run without GPU access, cloud credentials, or paid APIs.
5. Document what the output can and cannot mean.

## Product Boundary

The main Streamlit app must not require:

- a GPU;
- an NVIDIA account;
- a paid API;
- Docker;
- BioNeMo;
- NIM services;
- AlphaFold or structure-prediction tooling.

Any model output belongs in the experimental lab until it has clear provenance, review, and a demonstrated user need.

## Safety Boundary

Do not present generated structures, embeddings, molecules, similarity scores, or model predictions as validated biomedical findings.

Do not use lab output to rank treatments, recommend therapies, interpret symptoms, match people to trials, or make claims about safety or efficacy.

Every lab artifact should preserve:

- input source;
- model or service name and version;
- parameters;
- runtime environment;
- output path;
- limitations;
- whether the output came from a mock fixture or live provider.

## Suggested First Deliverable

A good v0.8 release can be small:

- one lab folder with a documented experiment skeleton;
- one mock provider or fixture-backed run;
- one manifest schema for lab outputs;
- tests that validate manifest completeness;
- a short report explaining what was learned and what remains gated.

That is enough to move toward scientific foundation models without weakening the core public-good application.

## Scaffold Status

The initial scaffold lives in `labs/blueprint_experiments/`. It supports offline planning and mock manifests first. Live NVIDIA NIM, BioNeMo, AlphaFold, and Blueprint adapters remain future gated work.
