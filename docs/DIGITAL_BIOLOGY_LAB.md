# Digital Biology Lab

## Purpose

The Digital Biology Lab is the project's optional learning track for scientific foundation models and NVIDIA's digital-biology stack. It is deliberately separated from the public Streamlit application so the research-navigation tool remains lightweight, free to run, and useful without specialist hardware or service credentials.

## Technology Layers

### BioNeMo Framework

BioNeMo Framework provides models and tools for developing and adapting biological foundation-model workflows. Candidate learning areas include protein representation models such as ESM-2, genomic models such as Evo 2, and single-cell representation models such as Geneformer.

The v0.10 development milestone implements the first local ESM-2 representation workflow with pinned model provenance, explicit sequence windows, tensor metadata, and repeat-run checks. It is a local Transformers/PyTorch reference implementation, not yet a BioNeMo or NIM integration. See [LOCAL_ESM2_EXPERIMENT.md](LOCAL_ESM2_EXPERIMENT.md).

Official documentation: <https://docs.nvidia.com/bionemo-framework/latest/>

### NVIDIA NIM

NIM packages model inference behind versioned container and API contracts. Biological NIMs include services for protein structure prediction, sequence models, protein design, and molecular workflows. A NIM integration belongs in the lab until its access requirements, licence, cost, hardware support, failure modes, and reproducibility are understood.

Official documentation: <https://docs.nvidia.com/nim/>

### NVIDIA AI Blueprints

Blueprints combine multiple services into reference workflows. They are useful for learning orchestration, deployment, observability, and provenance, but a Blueprint should not be copied into the main application without a demonstrated user need and a safety review.

Official catalogue: <https://build.nvidia.com/blueprints>

### Huntington Research Assistant

The application layer links papers, registry records, and carefully labelled model outputs. It must keep three kinds of information visually and structurally distinct:

1. publication or registry metadata;
2. curated database annotations;
3. experimental model predictions.

## First Learning Workflow

The first complete experiment should stay intentionally small:

```text
source-linked paper
  -> catalogued biomedical entity
  -> authoritative protein or gene identifier
  -> versioned sequence record
  -> model or NIM inference
  -> confidence and runtime metadata
  -> provenance-linked experimental view
```

This workflow teaches entity resolution, data provenance, model interfaces, GPU-aware deployment, output evaluation, and safe presentation without claiming drug discovery.

## Engineering Rules

- Pin model, container, dataset, and API versions.
- Store no API keys or service credentials in the repository.
- Keep large weights, datasets, caches, and generated outputs outside Git.
- Record authoritative input identifiers and retrieval dates.
- Retain model-native confidence measures rather than replacing them with vague labels.
- Add fixture-based tests for every external service adapter.
- Make timeouts, unavailable services, and unsupported hardware visible.
- Never silently mix model predictions into publication metadata.

## Evaluation Questions

Each experiment should answer:

- What exact task does the model perform?
- What input representation and preprocessing does it require?
- What does the output mean, and what does it not mean?
- Which confidence or uncertainty measures are available?
- How reproducible is the result across versions and hardware?
- What is the latency, memory requirement, and operational cost?
- Which claims can be checked against an authoritative source or benchmark?
- Could the presentation be mistaken for medical guidance or validated evidence?

## Safety

Protein embeddings, predicted structures, generated sequences, and proposed compounds are experimental computational outputs. They are not diagnoses, treatments, evidence of clinical effectiveness, or substitutes for laboratory and clinical validation.
