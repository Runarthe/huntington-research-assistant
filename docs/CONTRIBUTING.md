# Contributing

Thank you for helping improve Huntington Research Assistant.

## Development Setup

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
python -m pytest
python -m build
streamlit run app/streamlit_app.py
```

## Before Opening a Pull Request

- Keep changes focused and maintainable.
- Add or update tests for behavioral changes.
- Run `python -m pytest`.
- Run `python -m build` when packaging or release metadata changes.
- Confirm the app still works without Ollama.
- Confirm sources remain visible for papers and summaries.
- Confirm registered studies retain their ClinicalTrials.gov source links.
- Review copy for medical-advice or personalized-guidance language.
- Do not commit API keys, personal data, SQLite files, model files, or generated caches.

## Automated Tests on GitHub

The GitHub Actions workflow in `.github/workflows/tests.yml` installs the project and runs `python -m pytest` on Python 3.11 and 3.12. It runs automatically for pushes and pull requests.

Contributors can see the result in the pull request checks. A failing check should be investigated before merging. These checks verify software behavior only; they do not validate medical claims or guarantee that generated summaries are scientifically accurate.

## Safety Guardrails

Pull requests must not add diagnosis, personalized interpretation, treatment recommendations, requests for personal health information, authoritative summary claims, or hidden source attribution.

Clinical-trial contributions must not rank studies, infer eligibility, or describe registry status as evidence of safety or effectiveness.

See [SAFETY.md](SAFETY.md).

## Good First Contributions

- Documentation and Norwegian copy improvements.
- Accessibility fixes.
- Europe PMC parsing fixtures and tests.
- Topic-tag keyword improvements with tests.
- Export formats and reading-list UX.
- Clearer error messages and offline behavior.

## Code Style

- Use Python type hints.
- Keep functions small.
- Prefer existing project patterns over new dependencies.
- Add comments only when they clarify non-obvious behavior.
- Keep UI text in the translation layer where practical.

## Pull Request Notes

Describe what changed, why it is useful, how it was tested, and any safety or privacy implications.
