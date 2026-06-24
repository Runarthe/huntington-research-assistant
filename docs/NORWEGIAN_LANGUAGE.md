# Norwegian Language Quality

Norwegian UI labels and safety information are available. Automated Norwegian translation and summarization are disabled by default because the current local-model output is not reliable enough for a public medical-research navigation tool. The original English abstract remains visible and is the authoritative source.

## Generation Pipeline

1. Deterministic code selects exact English source excerpts for four fields: what was studied, what was found, why it matters, and limitations.
2. The app rejects extracted facts that introduce numbers or protected biomedical identifiers not present in the source.
3. A second local-model call renders the accepted facts in Norwegian using a curated terminology list.
4. The app rejects the Norwegian text if it changes selected numbers, identifier spelling, required headings, or introduces common personalized-advice phrases.
5. The UI always displays the original abstract, source link, experimental label, and educational disclaimer.

These deterministic checks reduce common errors but cannot establish scientific or linguistic correctness.

## Terminology

The initial glossary is in `src/hra/norwegian_language.py`. Terms should be checked against [MeSH på norsk](https://mesh.uia.no/) where a suitable term exists. Specialized terms may retain the English form in parentheses on first use.

Protected identifiers such as `HTT`, `mHTT`, `CAG`, `NfL`, `CRISPR`, and `Cas9` must retain their scientific spelling.

## Model

The experimental pipeline uses `hf.co/norallm/normistral-7b-warm-instruct:Q4_K_M` to render source excerpts in Norwegian Bokmål. Source selection itself is deterministic and does not require Qwen 3.

NorMistral is an Apache 2.0-licensed Norwegian instruction model from the NORA.LLM collaboration. Its own model card describes the instruction tuning as work in progress. Local evaluation found mixed Scandinavian forms, unreliable biomedical terminology, unwanted simplification, and occasional meaning changes. Automated integrity checks catch some failures, but cannot establish linguistic or scientific correctness.

Developers can explicitly enable the preview after pulling the model:

```bash
ollama pull hf.co/norallm/normistral-7b-warm-instruct:Q4_K_M
$env:HRA_ENABLE_EXPERIMENTAL_NORWEGIAN_SUMMARIES="true"
streamlit run app/streamlit_app.py
```

This opt-in is for evaluation, not public deployment. The app remains fully usable for search, source navigation, and optional English summaries without the Norwegian model.

No model is treated as medically validated. Changing the model requires rerunning the evaluation set.

## Evaluation

`tests/fixtures/norwegian_summary_cases.json` is a small, synthetic regression set covering laboratory research, clinical trials, biomarkers, genetics, animal models, and exercise research. Automated tests verify formatting and preservation rules.

Before describing Norwegian output as reviewed or high quality, the project needs:

- At least 20 representative real abstracts with rights-compatible test excerpts.
- Independent review by a fluent Norwegian biomedical professional.
- Recorded checks for factual fidelity, uncertainty, terminology, readability, and absence of medical advice.
- Regression testing after every prompt, glossary, or model change.

Machine-generated summaries must remain labelled experimental until that review exists.
