# v0.10 Release Checklist

## Automated

```powershell
python -m pytest -q
python -m build
python -m pip check
git diff --check
```

The default CI suite must pass without installing the `scientific-ai` extra and without downloading model files.

## Optional Real-Model Smoke Test

1. Install `.[scientific-ai]` in a local development environment.
2. Open the Protein Lab and select a bundled BDNF or HTT fixture fragment.
3. Run the pinned ESM-2 checkpoint on CPU.
4. Confirm the artifact records 320 embedding dimensions, tensor shape, dependency versions, hardware, sequence checksum, model revision, and pooling method.
5. Run the identical input again and confirm the repeat status is `matched`.
6. Enable cached-model-only mode and confirm the already-downloaded checkpoint still runs without model-network access.

Do not make the real-model smoke test part of default public CI.

## Sequence Boundary

- Explicitly retrieve one UniProt sequence and confirm it is cached outside the repository.
- Confirm a cache checksum mismatch is rejected.
- Select HTT's authoritative sequence and confirm the UI explains the 1,022-residue limit.
- Confirm the selected one-based window is present in the planned and generated manifests.
- Confirm oversize input fails instead of being silently truncated.

## UI and Safety

- Confirm the experiment does not run until the user checks the execution acknowledgement.
- Confirm missing model dependencies do not break any other app tab.
- Confirm English and Norwegian labels render without raw translation keys.
- Confirm the generated artifact is labelled experimental and contains no function, treatment, causal, or clinical interpretation.
- Confirm both planned and generated JSON downloads work in a standard browser.

## Documentation

- Review `README.md`, `CHANGELOG.md`, `docs/PROJECT_STATE.md`, and `docs/LOCAL_ESM2_EXPERIMENT.md`.
- Record the final release date and change roadmap status from In Progress to Released.
- Add a screenshot only if it improves onboarding and does not expose local paths or personal data.
