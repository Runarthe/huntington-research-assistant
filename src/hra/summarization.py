from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Any

import httpx
from pydantic import BaseModel, Field, ValidationError

from hra.models import Paper
from hra.norwegian_language import (
    NOT_STATED,
    SummaryIntegrityError,
    glossary_for_text,
    glossary_prompt,
    protect_identifiers_for_translation,
    restore_identifier_placeholders,
    validate_facts_against_source,
    validate_norwegian_summary,
)
from hra.safety import summary_disclaimer


SUMMARY_PIPELINE_VERSION = "structured-no-v2"
DEFAULT_NORWEGIAN_MODEL = (
    "hf.co/norallm/normistral-7b-warm-instruct:Q4_K_M"
)


@dataclass(frozen=True)
class SummarizationConfig:
    host: str = "http://localhost:11434"
    model: str = "qwen2.5:1.5b"
    norwegian_model: str = DEFAULT_NORWEGIAN_MODEL

    @classmethod
    def from_env(cls) -> "SummarizationConfig":
        return cls(
            host=os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/"),
            model=os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b"),
            norwegian_model=os.getenv(
                "OLLAMA_NORWEGIAN_MODEL",
                DEFAULT_NORWEGIAN_MODEL,
            ),
        )

    @property
    def chat_url(self) -> str:
        return f"{self.host}/api/chat"

    @property
    def tags_url(self) -> str:
        return f"{self.host}/api/tags"


@dataclass(frozen=True)
class LocalLLMStatus:
    available: bool
    message: str


class SummaryFacts(BaseModel):
    """Source-bound facts selected before Norwegian language generation."""

    studied: str = Field(min_length=1)
    found: str = Field(min_length=1)
    importance: str = Field(min_length=1)
    limitations: str = Field(min_length=1)


class NorwegianSummarySections(BaseModel):
    """Structured Norwegian text rendered deterministically by the app."""

    studied: str = Field(min_length=1)
    found: str = Field(min_length=1)
    importance: str = Field(min_length=1)
    limitations: str = Field(min_length=1)


class SummarizationDisabled(RuntimeError):
    """Raised when local summarization is unavailable."""


def experimental_norwegian_summaries_enabled() -> bool:
    """Return whether the unreviewed Norwegian generation path is opted in."""

    return os.getenv(
        "HRA_ENABLE_EXPERIMENTAL_NORWEGIAN_SUMMARIES",
        "false",
    ).strip().casefold() in {"1", "true", "yes", "on"}


def disabled_message(
    config: SummarizationConfig | None = None,
    language: str = "en",
) -> str:
    config = config or SummarizationConfig.from_env()
    if language == "no":
        return (
            "Lokal oppsummering er deaktivert. Installer Ollama og kjør "
            f"`ollama pull {config.norwegian_model}` for å aktivere den lokale "
            "norske pipelinen. "
            "Søk fungerer fortsatt uten en språkmodell."
        )
    return (
        "Local summarization is disabled. To enable free local summaries, install "
        f"Ollama, then run `ollama pull {config.model}` and start Ollama locally. "
        "Search still works without any LLM."
    )


def local_llm_status(
    config: SummarizationConfig | None = None,
    timeout: float = 2.0,
    language: str = "en",
) -> LocalLLMStatus:
    """Check whether the configured local Ollama model is available."""

    config = config or SummarizationConfig.from_env()
    try:
        with httpx.Client(timeout=timeout, trust_env=False) as client:
            response = client.get(config.tags_url)
            response.raise_for_status()
            data = response.json()
    except (httpx.HTTPError, ValueError):
        return LocalLLMStatus(False, disabled_message(config, language))

    models = {
        str(model.get("name")).casefold()
        for model in data.get("models", [])
        if isinstance(model, dict) and model.get("name")
    }
    required_models = (
        [config.norwegian_model]
        if language == "no"
        else [config.model]
    )
    missing_models = [
        model for model in required_models if model.casefold() not in models
    ]
    if missing_models:
        commands = " og ".join(f"`ollama pull {model}`" for model in missing_models)
        if language == "no":
            return LocalLLMStatus(
                False,
                (
                    "Ollama kjører, men den norske pipelinen mangler modell. "
                    f"Kjør {commands}."
                ),
            )
        return LocalLLMStatus(
            False,
            (
                f"Ollama is running, but `{missing_models[0]}` is not installed. "
                f"Run `ollama pull {missing_models[0]}` to enable local summaries."
            ),
        )

    message = (
        "Den lokale norske pipelinen er tilgjengelig med "
        f"`{config.norwegian_model}`. Ingen API-nøkler brukes."
        if language == "no"
        else f"Local summarization is available with Ollama model `{config.model}`. No API keys are used."
    )
    return LocalLLMStatus(True, message)


def build_summary_prompt(
    paper: Paper,
    mode: str = "plain",
    language: str = "en",
) -> str:
    abstract = paper.abstract or "No abstract available."
    if language == "no":
        headings = (
            "Bruk nøyaktig disse overskriftene:\n"
            "Hva undersøkte de?\n"
            "Hva fant de?\n"
            "Hvorfor er det viktig?\n"
            "Begrensninger / usikkerhet"
        )
        language_instruction = "Svar på norsk."
    else:
        headings = (
            "Use exactly these headings:\n"
            "What did they study?\n"
            "What did they find?\n"
            "Why does it matter?\n"
            "Limitations / uncertainty"
        )
        language_instruction = "Respond in English."

    if language == "no":
        style_instruction = (
            "Skriv for en allmenn leser. Bruk korte setninger og forklar nødvendige faguttrykk."
            if mode == "plain"
            else "Skriv for en forskningsinteressert leser og behold viktige detaljer om studiedesign og metode."
        )
    else:
        style_instruction = (
            "Write for a general reader. Use short sentences and explain unavoidable technical terms."
            if mode == "plain"
            else "Write for a research-oriented reader and preserve important study-design and method details."
        )
    return (
        "Summarize this Huntington's disease research abstract for education and "
        "research navigation. Do not provide medical advice, diagnosis, treatment "
        "recommendations, or personalized health guidance.\n\n"
        f"{language_instruction} {style_instruction}\n\n"
        f"Title: {paper.title}\n"
        f"Journal: {paper.journal or 'Unknown'}\n"
        f"Year: {paper.year or 'Unknown'}\n"
        f"Source record: {paper.source_url or 'Not available'}\n"
        f"Abstract: {abstract}\n\n"
        f"{headings}\n\n"
        "Use only information explicitly present in the abstract. If a requested "
        "detail is absent, say that it is not stated in the abstract. Do not invent "
        "citations, URLs, participant outcomes, effectiveness claims, or clinical implications. "
        f"The application will display this disclaimer separately: {summary_disclaimer(language)}"
    )


_STRUCTURED_SECTION_PATTERN = re.compile(
    r"\b(Background|Objective|Methods|Results|Conclusions|Limitations):\s*",
    re.IGNORECASE,
)
_SENTENCE_SPLIT_PATTERN = re.compile(r"(?<=[.!?])\s+(?=[A-Z])")


def _sentences(text: str) -> list[str]:
    return [
        sentence.strip()
        for sentence in _SENTENCE_SPLIT_PATTERN.split(text)
        if sentence.strip()
    ]


def _limited_sentences(text: str, limit: int) -> str:
    return " ".join(_sentences(text)[:limit]) or NOT_STATED


def _structured_sections(abstract: str) -> dict[str, str]:
    matches = list(_STRUCTURED_SECTION_PATTERN.finditer(abstract))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(abstract)
        sections[match.group(1).casefold()] = abstract[start:end].strip()
    return sections


def select_summary_facts(paper: Paper, mode: str = "plain") -> SummaryFacts:
    """Select exact source excerpts without asking an LLM to rewrite evidence."""

    abstract = paper.abstract or ""
    sections = _structured_sections(abstract)
    sentence_limit = 1 if mode == "plain" else 3
    if sections:
        studied_parts = [
            _limited_sentences(sections[name], sentence_limit)
            for name in ("objective", "methods")
            if sections.get(name)
        ]
        studied = " ".join(part for part in studied_parts if part != NOT_STATED)
        if not studied:
            studied = _limited_sentences(
                sections.get("background", abstract),
                sentence_limit,
            )
        return SummaryFacts(
            studied=studied,
            found=_limited_sentences(
                sections.get("results", ""),
                sentence_limit,
            ),
            importance=_limited_sentences(
                sections.get("conclusions", ""),
                sentence_limit,
            ),
            limitations=_limited_sentences(
                sections.get("limitations", ""),
                sentence_limit,
            ),
        )

    abstract_sentences = _sentences(abstract)
    if paper.is_review:
        found_limit = 2 if mode == "plain" else 4
        importance_limit = 1 if mode == "plain" else 3
        return SummaryFacts(
            studied=paper.title,
            found=" ".join(abstract_sentences[:found_limit]) or NOT_STATED,
            importance=(
                " ".join(abstract_sentences[-importance_limit:])
                if abstract_sentences
                else NOT_STATED
            ),
            limitations=NOT_STATED,
        )

    studied_limit = 1 if mode == "plain" else 2
    found_limit = 1 if mode == "plain" else 3
    return SummaryFacts(
        studied=" ".join(abstract_sentences[:studied_limit]) or paper.title,
        found=(
            " ".join(abstract_sentences[studied_limit : studied_limit + found_limit])
            or NOT_STATED
        ),
        importance=(abstract_sentences[-1] if abstract_sentences else NOT_STATED),
        limitations=NOT_STATED,
    )
def build_norwegian_field_prompt(
    paper: Paper,
    field_name: str,
    source_excerpt: str,
    mode: str = "plain",
) -> str:
    terminology = glossary_prompt(glossary_for_text(source_excerpt))
    publication_context = (
        "Dette er en oversiktsartikkel. Ikke presenter omtalt forskning som nye funn "
        "gjort av forfatterne."
        if paper.is_review
        else "Behold studietypen, modellen eller populasjonen som står i utdraget."
    )
    style = (
        "Bruk korte, naturlige setninger uten å utelate innhold."
        if mode == "plain"
        else "Bruk presist norsk fagspråk og behold alle metode- og resultatdetaljer."
    )
    field_instruction = {
        "studied": (
            "Gjør eventuelle mål- eller metodefragmenter til fullstendige setninger. "
            "Ikke omtale HTT som selve årsaken til sykdommen."
        ),
        "found": "Bruk fortid for observerte resultater og behold all usikkerhet.",
        "importance": (
            "Når utdraget omtaler en mulig terapeutisk tilnærming, start med "
            "'Forfatterne mener at' og bevar ord som kan, mulig og potensial."
        ),
        "limitations": "Ikke legg til begrensninger som ikke står i utdraget.",
    }[field_name]
    return (
        "Oversett ett utdrag fra et medisinsk forskningsabstrakt til naturlig norsk "
        "bokmål. Svar bare med oversettelsen, uten overskrift, JSON eller forklaring. "
        "Ikke forkort teksten og ikke legg til nye opplysninger. Behold alle tall, "
        "enheter, sammenligninger, negasjoner og usikkerhetsord. Tekst som ser ut som "
        "__HRA_TERM_0__ er en beskyttet fagidentifikator og må kopieres helt uendret. "
        "Bruk de oppgitte norske fagtermene og bøy dem grammatisk i setningen; ikke la "
        "de engelske termene stå igjen. Ikke gi medisinske råd. "
        f"{style} {publication_context} {field_instruction}\n\n"
        f"Terminologi:\n{terminology}\n\n"
        f"Engelsk utdrag:\n{source_excerpt}"
    )


def paper_source_text(paper: Paper) -> str:
    publication_types = ", ".join(paper.publication_types) or "Not stated"
    return (
        f"Title: {paper.title}\n"
        f"Publication type: {publication_types}\n"
        f"Abstract: {paper.abstract or 'No abstract available.'}"
    )


def format_norwegian_summary(
    sections: NorwegianSummarySections,
    *,
    is_review: bool = False,
) -> str:
    studied_label = (
        "Hva handler oversiktsartikkelen om?" if is_review else "Hva undersøkte de?"
    )
    found_label = "Hva beskriver den?" if is_review else "Hva fant de?"
    importance_label = (
        "Hvorfor er temaet relevant for forskning?"
        if is_review
        else "Hvorfor er det viktig?"
    )
    labels = (
        (studied_label, sections.studied),
        (found_label, sections.found),
        (importance_label, sections.importance),
        ("Begrensninger og usikkerhet", sections.limitations),
    )
    return "\n\n".join(f"**{label}**\n\n{text}" for label, text in labels)


def _chat_content(
    client: httpx.Client,
    config: SummarizationConfig,
    messages: list[dict[str, str]],
    *,
    json_output: bool = False,
    model: str | None = None,
    options: dict[str, Any] | None = None,
) -> str:
    payload: dict[str, Any] = {
        "model": model or config.model,
        "messages": messages,
        "stream": False,
        "options": options or {"temperature": 0.1},
    }
    if json_output:
        payload["format"] = "json"

    response = client.post(config.chat_url, json=payload)
    response.raise_for_status()
    data = response.json()
    content = data.get("message", {}).get("content")
    if not content:
        raise SummarizationDisabled("Den lokale modellen returnerte et tomt svar.")
    return str(content).strip()


def _summarize_paper_in_norwegian(
    client: httpx.Client,
    paper: Paper,
    config: SummarizationConfig,
    mode: str,
) -> str:
    facts = select_summary_facts(paper, mode=mode)
    source_text = paper_source_text(paper)
    fact_values = facts.model_dump()
    validate_facts_against_source(fact_values, source_text)
    protected_values, identifier_replacements = protect_identifiers_for_translation(
        fact_values
    )
    generated_values: dict[str, str] = {}
    for field_name, source_excerpt in protected_values.items():
        if source_excerpt == NOT_STATED:
            generated_values[field_name] = "Ikke oppgitt i abstraktet."
            continue
        generated_values[field_name] = _chat_content(
            client,
            config,
            [
                {
                    "role": "system",
                    "content": (
                        "Du oversetter medisinsk forskningstekst til nøkternt, "
                        "idiomatisk norsk bokmål uten å endre innholdet."
                    ),
                },
                {
                    "role": "user",
                    "content": build_norwegian_field_prompt(
                        paper,
                        field_name,
                        source_excerpt,
                        mode=mode,
                    ),
                },
            ],
            model=config.norwegian_model,
            options={
                "temperature": 0.1,
                "num_predict": 512 if mode == "research" else 256,
                "repeat_penalty": 1.0,
                "top_k": 64,
                "top_p": 0.9,
            },
        )
    restored_values = restore_identifier_placeholders(
        generated_values,
        identifier_replacements,
    )
    sections = NorwegianSummarySections.model_validate(restored_values)
    summary = format_norwegian_summary(sections, is_review=paper.is_review)
    validate_norwegian_summary(fact_values, summary, source_text)
    return summary


def summarize_paper(
    paper: Paper,
    config: SummarizationConfig | None = None,
    timeout: float = 90.0,
    mode: str = "plain",
    language: str = "en",
) -> str:
    """Summarize a paper abstract with a local Ollama chat model."""

    config = config or SummarizationConfig.from_env()
    try:
        with httpx.Client(timeout=timeout, trust_env=False) as client:
            if language == "no":
                return _summarize_paper_in_norwegian(
                    client,
                    paper,
                    config,
                    mode,
                )
            content = _chat_content(
                client,
                config,
                [
                    {
                        "role": "system",
                        "content": (
                            "You help users understand biomedical literature accurately. "
                            "You never provide medical advice, diagnosis, treatment "
                            "recommendations, or personalized health guidance."
                        ),
                    },
                    {
                        "role": "user",
                        "content": build_summary_prompt(
                            paper,
                            mode=mode,
                            language=language,
                        ),
                    },
                ],
            )
    except (httpx.HTTPError, ValueError) as exc:
        raise SummarizationDisabled(disabled_message(config, language)) from exc
    return str(content).strip()
