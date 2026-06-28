# Digital Biology Lab

This directory is reserved for optional, reproducible scientific-AI experiments. Nothing under `labs/` is required to install or run the Huntington Research Assistant Streamlit application.

## Boundary

The public application navigates literature and registered-study metadata. Lab experiments may explore biological foundation models, embeddings, structure prediction, NVIDIA BioNeMo, NIM microservices, and AI Blueprints, but their outputs are model predictions rather than established biomedical evidence.

Lab experiments must not:

- provide diagnosis, treatment recommendations, or personalized guidance;
- describe generated molecules or structures as validated Huntington therapies;
- send personal or sensitive health information to a model service;
- place credentials, downloaded model weights, caches, or generated outputs in Git;
- become a required dependency of the core application.

## Experiment Contract

Every experiment should include a manifest based on [`experiment-manifest.example.json`](experiment-manifest.example.json) and record:

- purpose and bounded research question;
- model provider, model name, version, and governing licence;
- authoritative identifiers and provenance for every input;
- runtime, container, hardware, and important parameters;
- output location and confidence measures;
- evaluation method and known limitations;
- an explicit statement that the output is not clinically validated.

Experiments should support a mock or fixture-driven path where practical so their integration code can be tested without a GPU, paid service, or NVIDIA account.

## Planned Sequence

1. Resolve selected literature entities to authoritative database identifiers.
2. Run a bounded protein-embedding example and document the vector output.
3. Evaluate an AlphaFold or compatible NIM structure workflow on an educational example.
4. Connect model outputs back to their inputs, versions, confidence metrics, and source records.
5. Reproduce a small Blueprint workflow only after the individual components are understood.

See [`docs/DIGITAL_BIOLOGY_LAB.md`](../docs/DIGITAL_BIOLOGY_LAB.md) for the architecture and learning goals.
