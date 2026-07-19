# Release Checklist

Use this checklist before publishing a tagged release.

## Code and Tests

- [ ] Confirm the version in `pyproject.toml` matches the intended tag.
- [ ] Run `python -m pytest -q`.
- [ ] Run `python -m build`.
- [ ] Install the built wheel in a clean virtual environment and import `hra`.
- [ ] Confirm `git diff --check` reports no whitespace errors.
- [ ] Confirm GitHub Actions passes on all supported Python versions.

## Manual App Checks

- [ ] Search Europe PMC and open a source record.
- [ ] Search PubMed and open a source record.
- [ ] Run a combined-provider search and verify duplicate records are merged.
- [ ] Browse to the next and previous publication page.
- [ ] Verify publication dashboard counts render.
- [ ] Search ClinicalTrials.gov and open a registry record.
- [ ] Export publication CSV/BibTeX and registered-study CSV.
- [ ] Confirm the app still works when Ollama is stopped.
- [ ] Confirm English local summaries work when the configured Ollama model is available.
- [ ] Confirm Norwegian UI states that generated translation and summaries come later.
- [ ] Add, remove, persist, and export papers from the local reading list.
- [ ] Mark a paper as seen and verify the saved/seen search filters.
- [ ] Compare two to five saved papers in Evidence Explorer and verify source-linked passages and CSV export.
- [ ] Build an Entity Explorer map and verify that every visible mention has source evidence.
- [ ] Confirm paper-level co-occurrences are labelled as navigation signals, not biological relationships.
- [ ] Confirm catalogue ID, catalogue version, aliases, extraction method, and mention confidence are visible for inspected entities.
- [ ] Check the main workflows at a narrow mobile viewport without clipped or overlapping controls.
- [ ] Review the local ESM-2 plan with a bundled fixture without running the model.
- [ ] Confirm the Provider parity table marks identical input fields as matched and unexecuted BioNeMo output as unavailable.
- [ ] Download and validate the BioNeMo plan and provider-parity JSON files.
- [ ] Download the BioNeMo execution ZIP, inspect its checksummed file list, and confirm it contains no credential.
- [ ] Enable the offline BioNeMo result fixture and confirm the UI does not label it as provider execution.
- [ ] Confirm a result with a changed experiment, model, sequence checksum, full vector, or oversized JSON payload is rejected.
- [ ] Run the BioNeMo environment preflight and confirm that it makes no network call, inspects no credential, and starts no container.
- [ ] Confirm a stopped Docker engine or unsupported architecture is reported as blocked rather than ready.
- [ ] Confirm an unlisted GPU model is visibly marked for review even when its compute capability passes.
- [ ] Confirm the GPU probe rejects moving image tags and remains disabled until its explicit container confirmation is selected.
- [ ] Confirm a missing immutable image is reported without a registry login or image pull.
- [ ] Confirm a remote Docker endpoint is blocked before image inspection or container execution.
- [ ] If a reviewed local image is available, verify the probe command uses `--pull never`, `--network none`, no host mount, and only the fixed `nvidia-smi` entrypoint.
- [ ] Confirm a passed GPU probe is not labelled as BioNeMo inference or model execution.
- [ ] Export the reviewed container JSON and confirm its tag, full digest, Linux/AMD64 platform, archived lifecycle, catalogue-reported scan/signature, and local-verification limitations are present.
- [ ] Confirm the Protein Lab requires licence review and local-container confirmation before enabling the reviewed-image GPU probe.
- [ ] Confirm the execution bundle rejects a different image reference and its runner includes `--pull never`.

## Safety and Privacy

- [ ] Confirm the medical disclaimer is visible in both languages.
- [ ] Confirm no feature asks for personal health information.
- [ ] Search tracked files for secrets, API keys, local databases, and personal data.
- [ ] Confirm all generated summaries and Entity Explorer evidence retain source links.
- [ ] Confirm Evidence Explorer labels its classifications and passages as navigation aids rather than quality or effectiveness assessments.
- [ ] Confirm Entity Explorer labels mention confidence as alias-match confidence only, not confidence in a scientific claim.
- [ ] Confirm registry status is not described as evidence of safety or effectiveness.

## GitHub Release

- [ ] Update `CHANGELOG.md` and release-facing README text.
- [ ] Commit and push the release branch.
- [ ] Review the complete pull-request diff.
- [ ] Merge only after required checks pass.
- [ ] Tag the merge commit with the version declared in `pyproject.toml`.
- [ ] Create the GitHub release from the changelog entry.
