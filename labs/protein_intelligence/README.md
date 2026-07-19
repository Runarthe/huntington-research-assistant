# Protein Intelligence Lab

This lab area contains the foundation for bounded protein-sequence and model-output experiments. Heavy model dependencies remain optional and are loaded only during an explicit run.

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

## v0.10 Local ESM-2 Slice

The first real model adapter uses the pinned `facebook/esm2_t6_8M_UR50D` checkpoint. It supports explicit sequence windows, local CPU or CUDA execution, strict no-truncation handling, provenance-rich embedding manifests, and repeat-run checksum comparison.

The Streamlit Protein Lab exposes this workflow without making PyTorch or Transformers core dependencies. See [`docs/LOCAL_ESM2_EXPERIMENT.md`](../../docs/LOCAL_ESM2_EXPERIMENT.md).

## v0.11 Provider-Parity Slice

`provider_parity.py` normalizes embedding provenance into `protein-embedding-artifact.v1`, builds a plan-only BioNeMo ESM-2 manifest from the same selected sequence, and reports each comparable or unresolved field. `bionemo_execution.py` creates a credential-free external execution bundle and validates bounded result JSON against the exact plan. Streamlit never calls BioNeMo or NVIDIA NIM and does not interpret embedding values. See [`docs/V0_11_PROVIDER_PARITY.md`](../../docs/V0_11_PROVIDER_PARITY.md).

## v0.12 Runtime-Readiness Slice

`bionemo_preflight.py` records passive host prerequisites without starting a container. `bionemo_image_review.py` pins the archived BioNeMo Framework 2.7.1 image only as a reproducibility candidate for the existing ESM-2 contract and records its lifecycle, licence, catalogue, and verification boundaries. `bionemo_gpu_probe.py` adds a separate opt-in GPU visibility check for that immutable image when it is already stored locally through a local Docker socket or named pipe. The probe cannot pull, use container networking, mount host paths, inspect credentials, execute BioNeMo, or load a model. See [`docs/V0_12_BIONEMO_RUNTIME.md`](../../docs/V0_12_BIONEMO_RUNTIME.md).

`bionemo_recipes_review.py` keeps the preferred maintained path separate from the archived container. It pins BioNeMo Recipes `v3.0.0`, a public 8M NVIDIA ESM-2 model revision, the executable custom-code blob, and the safetensors digest. It can create a sequence-specific plan, but cannot download weights, enable remote code, import TransformerEngine, or execute inference.

## Not Included Yet

- AlphaFold or NIM calls;
- BioNeMo model execution;
- generated biological hypotheses;

Those belong behind explicit adapters, fixtures, and provenance checks.

## Prototype Flow

```text
ProteinTarget
  -> UniProt FASTA retrieval
  -> ProteinSequenceRecord with checksum
  -> sequence retrieval manifest
  -> mock or optional local ESM-2 provider
  -> embedding manifest with input provenance
```

The mock embedding vector is a deterministic test fixture. It has no biological meaning.

## CLI

The lab helper emits JSON manifests and is offline-safe by default:

```bash
python -m labs.protein_intelligence list-targets
python -m labs.protein_intelligence plan HTT --date 2026-07-03
python -m labs.protein_intelligence retrieve HTT --date 2026-07-03
python -m labs.protein_intelligence mock-embed BDNF --sequence ACDEFG --dimensions 8
python -m labs.protein_intelligence mock-embed HTT --fasta-file labs/protein_intelligence/fixtures/htt.fragment.fasta
python -m labs.protein_intelligence validate-manifest outputs/example-manifest.json
python -m labs.protein_intelligence bionemo-image-review
python -m labs.protein_intelligence bionemo-recipes-review
```

`mock-embed` uses a deterministic fixture vector. It does not call ESM-2, BioNeMo, NIM, AlphaFold, or any external service.
`retrieve` is also offline-safe by default: without `--live`, it emits a failed manifest explaining that live UniProt retrieval was disabled.

The FASTA files in [`fixtures/`](fixtures/) are short offline fragments for tooling tests. They are not complete reference sequences and must not be used for biological interpretation.

To perform a real UniProt retrieval in a manual lab run, pass `--live`:

```bash
python -m labs.protein_intelligence retrieve BDNF --live
```

Do not use live retrieval in default CI tests.

`validate-manifest` performs structural checks only. It confirms that required manifest fields are present, status is known, inputs exist, and limitations are recorded. It does not validate biological claims.
