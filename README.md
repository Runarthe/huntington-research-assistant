# Huntington Research Assistant

Huntington Research Assistant is a small open-source app for searching, summarizing, and navigating Huntington's disease research papers and registered clinical studies.

The app uses [Europe PMC](https://europepmc.org/RestfulWebService) for publications and the [ClinicalTrials.gov API](https://clinicaltrials.gov/data-api/api) for registered study information. It is intended as an educational public-good project and as a foundation that can later add PubMed/NCBI E-utilities as a second literature provider.

> [!IMPORTANT]
> This tool is for educational and research navigation purposes only. It is not medical advice. Always consult qualified healthcare professionals for diagnosis, treatment, or genetic counselling.

## Medical Disclaimer

This tool is for educational and research navigation purposes only. It is not medical advice. Always consult qualified healthcare professionals for diagnosis, treatment, or genetic counselling.

The app does not provide diagnosis, treatment recommendations, personalized health guidance, or interpretation of personal medical situations. Do not enter personal health data.

This project is not affiliated with any medical association, including the Norwegian Huntington's disease association, at this stage.

## Features

- Search Europe PMC for Huntington-related research papers.
- Expand simple user queries into a Huntington's disease literature context.
- Display titles, authors, year, journal, DOI, PMID, abstract snippets, source links, citation counts, and open-access flags where available.
- Display publication types and prominent Europe PMC retraction/correction notices.
- Add simple rule-based topic tags.
- Filter Europe PMC results by topic category, publication year, and open-access status.
- Browse provider-backed result pages instead of only filtering a small local batch.
- Download each paper's metadata and abstract, with direct open-access PDF links where Europe PMC provides them.
- Export the visible publication page as CSV or BibTeX with source links.
- Show a publication dashboard with yearly Europe PMC result counts, the selected-period total, and the current-year count.
- Track registered Huntington's disease studies by status, phase, country, intervention, sponsor, and registry update date.
- Export visible registered studies as CSV.
- Include a dedicated view for recent publications from the last couple of years.
- Offer English and Norwegian UI labels and safety disclaimers.
- Offer English plain-language and research-detail summary modes.
- Optionally summarize abstracts with a local Ollama model such as Qwen.
- Keep a small local SQLite cache/history.
- Continue to work without any LLM by showing retrieved papers only.

Norwegian translation of abstracts and generated summaries is planned for a later update. Norwegian UI labels and safety information are already available.

## Screenshots

### Search and filters

![Disclaimer and search filters](docs/screenshots/Disclaimer_and_searchfilters_options.png)

### Publication dashboard

![Publication dashboard](docs/screenshots/Publication_dashboard.png)

### Search results

![Search results](docs/screenshots/Two_results_for_search_gene_splicing.png)

### Clinical-trial literature from the v0.1 interface

![Clinical trials search and trends](docs/screenshots/Clinical_trials_search_tab_and_some_publishing_trends.png)

The v0.2 development version replaces this publication search with a separate ClinicalTrials.gov tracker. An updated screenshot will be added after release verification.

### Recent publications

![Recent publications](docs/screenshots/Recent_publication_tab.png)

### Optional local plain-language summary

![Example English plain-language summary](<docs/screenshots/Example_paper_summarized_in_simpler_english_language(plain_Language).png>)

## Setup

Requirements:

- Python 3.11+

Create a virtual environment and install locally:

```bash
python -m venv .venv
pip install -e .
```

For development and tests:

```bash
pip install -e ".[dev]"
pytest
```

## Automated Tests

GitHub Actions runs the test suite automatically on Python 3.11 and 3.12 whenever code is pushed or a pull request is opened. The workflow does not require Ollama, an API key, or access to personal data.

The workflow is defined in [`.github/workflows/tests.yml`](.github/workflows/tests.yml). A green check means the automated tests passed; it does not certify medical or scientific accuracy.

## Run

```bash
streamlit run app/streamlit_app.py
```

## Optional Local Summaries

Summaries are optional and run locally through [Ollama](https://ollama.com/). No cloud LLM API key is used or needed.

One small default option is Qwen 2.5 1.5B:

```bash
ollama pull qwen2.5:1.5b
ollama serve
```

Then run the Streamlit app normally. If Ollama is not installed, not running, or the model is not pulled, the app shows retrieved papers only. Larger models such as `qwen2.5:3b` may produce better summaries but require more disk and memory.

## Environment Variables

Copy `.env.example` if you want local defaults:

```bash
cp .env.example .env
```

Supported variables:

- `OLLAMA_HOST`: local Ollama server URL. Defaults to `http://localhost:11434`.
- `OLLAMA_MODEL`: local model name. Defaults to `qwen2.5:1.5b`.
- `HRA_CACHE_PATH`: optional SQLite cache path override. By default the app stores cache in the OS local app data/cache directory, outside the repo. If that location is unavailable, it falls back to the system temp directory. This avoids SQLite I/O problems in synced folders such as OneDrive.
- `HRA_EUROPE_PMC_EMAIL`: optional contact email sent in the Europe PMC user agent.
- `HRA_TRUST_ENV`: set to `true` only if Europe PMC and ClinicalTrials.gov requests should use system proxy environment variables. Defaults to `false` to avoid broken local proxy settings.

No API keys are required or hardcoded. If local summarization is unavailable, the app still searches Europe PMC.

## Data and Privacy

- Search queries are sent to Europe PMC.
- Clinical-trial filter queries are sent to ClinicalTrials.gov when the tracker is used.
- Ollama summaries remain local unless `OLLAMA_HOST` is deliberately pointed elsewhere.
- Search history is stored in a local SQLite database.
- Do not enter personal health or identifying information.
- Generated summaries may be incomplete or inaccurate; always inspect the linked source paper.

## Roadmap

Near-term priorities include saved reading lists, Norwegian refinement, accessibility testing, and a second PubMed/NCBI provider. AlphaFold, BioNeMo, autonomous agents, personalized medical features, and automated claims about study suitability remain out of scope.

See [docs/ROADMAP.md](docs/ROADMAP.md).

## Contributing

Contributions are welcome. Please keep the project focused on education and research navigation, avoid collecting sensitive user data, and do not add features that provide medical advice or personalized health guidance.

Read [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) and [docs/SAFETY.md](docs/SAFETY.md) before opening a pull request.

Good first issues:

- Add more tagging keywords.
- Improve README examples.
- Add tests for Europe PMC response parsing.
- Improve Streamlit result layout.

## License

This project is released under the MIT License. See `LICENSE`.
