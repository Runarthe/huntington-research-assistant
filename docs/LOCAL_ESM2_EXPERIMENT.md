# Local ESM-2 Experiment

The v0.10 Protein Lab adds the project's first real protein foundation-model execution. It is optional, local, deliberately small, and separate from the literature-navigation features.

## What It Does

The experiment converts an explicit amino-acid sequence window into a 320-dimensional numerical vector using Meta's `facebook/esm2_t6_8M_UR50D` checkpoint. The model revision is pinned to `c731040fcd8d73dceaa04b0a8e6329b345b0f5df`.

The artifact records:

- target and UniProt identifiers;
- source and selected-sequence checksums;
- one-based input-window coordinates;
- model ID, revision, and licence;
- PyTorch and Transformers versions;
- compute device and hardware;
- token tensor shape and mean-pooling method;
- vector dimensions and checksum;
- whether a repeated run produced the same checksum.

It does not assign biological meaning to the vector.

## Install

The core application does not install PyTorch or Transformers. Install the optional packages only when you want to run this lab:

```powershell
python -m pip install -e ".[scientific-ai]"
```

PyTorch is substantially larger than the approximately 31 MB checkpoint. CPU execution is enough for the short bundled fragments. For NVIDIA GPU support, select the appropriate command for the machine at the [official PyTorch installation page](https://pytorch.org/get-started/locally/).

## Use the UI

1. Start the app with `streamlit run app/streamlit_app.py`.
2. Open **Protein Lab (experimental)**.
3. Choose HTT, BDNF, or NEFL.
4. Scroll to **Local ESM-2 experiment**.
5. Start with **Bundled fixture fragment** for the quickest offline check.
6. Review the planned manifest and selected sequence window.
7. Select CPU, CUDA, or Auto.
8. Confirm the execution boundary and click **Run local ESM-2**.
9. Inspect or download the generated artifact.
10. Run the same input again to compare embedding checksums.

No model or sequence download happens merely by opening the tab.

## Authoritative Sequence Cache

Select **Cached UniProt sequence** and click **Retrieve or refresh from UniProt** to make an explicit public-data request. The response is normalized, checksummed, and saved outside the repository in an OS-local user cache.

Set `HRA_PROTEIN_CACHE_DIR` to override the cache location.

HTT is longer than the experiment's 1,022-residue input limit. The UI therefore requires a visible, one-based sequence window. The adapter rejects oversize input rather than silently truncating it.

## Model Download and Offline Runs

On the first run, Transformers may download the pinned checkpoint from Hugging Face. Enable **Use already-downloaded model files only** to prohibit model-network access. That mode fails clearly if the pinned files are absent.

The model is loaded lazily only after the run button is pressed. Missing optional dependencies do not prevent literature search, clinical-trial tracking, reading lists, or Ollama summaries from working.

## Interpretation Boundary

An ESM-2 embedding is a learned numerical representation. In this project it is an engineering and provenance artifact only.

Do not use the vector or its checksum to claim:

- protein function or structure;
- biological similarity or interaction;
- pathogenicity or disease causality;
- target quality or treatment relevance;
- clinical effectiveness, safety, or suitability;
- anything about an individual's health.

Any downstream scientific use needs a separately designed task, labelled evaluation data, metrics, uncertainty analysis, and domain review.

## Why This Matters for the Learning Track

This workflow exercises the parts that mock manifests cannot:

```text
authoritative or fixture sequence
  -> deterministic preprocessing boundary
  -> local foundation-model tensors
  -> pooled embedding
  -> versioned provenance artifact
  -> repeat-run check
```

The same artifact contract can later be compared with an NVIDIA BioNeMo or NIM execution without changing what the output is allowed to claim.
