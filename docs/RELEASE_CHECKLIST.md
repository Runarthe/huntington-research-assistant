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
- [ ] Build a research map and verify that every visible relationship has source evidence.
- [ ] Check the main workflows at a narrow mobile viewport without clipped or overlapping controls.

## Safety and Privacy

- [ ] Confirm the medical disclaimer is visible in both languages.
- [ ] Confirm no feature asks for personal health information.
- [ ] Search tracked files for secrets, API keys, local databases, and personal data.
- [ ] Confirm all generated summaries and research-map evidence retain source links.
- [ ] Confirm Evidence Explorer labels its classifications and passages as navigation aids rather than quality or effectiveness assessments.
- [ ] Confirm registry status is not described as evidence of safety or effectiveness.

## GitHub Release

- [ ] Update `CHANGELOG.md` and release-facing README text.
- [ ] Commit and push the release branch.
- [ ] Review the complete pull-request diff.
- [ ] Merge only after required checks pass.
- [ ] Tag the merge commit with the version declared in `pyproject.toml`.
- [ ] Create the GitHub release from the changelog entry.
