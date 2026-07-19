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
- [ ] Export the maintained Recipes review and confirm the release commit, model revision, custom-code blob, conflicting licence signals, and safetensors SHA-256 are present.
- [ ] Download the Recipes ESM-2 plan and confirm it records the exact selected sequence window while reporting no model execution or embedding.
- [ ] Download and validate the Recipes runtime ZIP; confirm it contains no weights, wheels, credentials, or embedding values.
- [ ] Confirm the Recipes runtime requires an explicit window of at most 64 residues and does not start Docker from Streamlit.
- [ ] Confirm the code review retains the low assert finding, incomplete native-dependency audit, and licence-review requirement.
- [ ] Confirm the runtime pins the exact Linux/AMD64 base digest and reports the image, derived build, and fixture inference as not executed until manually proven.
- [ ] Run the Recipes readiness check and confirm it does not call a registry, pull an image, start a container, inspect credentials, or import the model.
- [ ] Confirm a remote Docker endpoint, tampered bundle, linked artifact, or checksum mismatch is blocked.
- [ ] Confirm missing terms declaration, exact base image, or artifact directory is reported as review required rather than as a successful build.

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
