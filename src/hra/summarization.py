from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import httpx

from hra.models import Paper
from hra.safety import summary_disclaimer


@dataclass(frozen=True)
class SummarizationConfig:
    host: str = "http://localhost:11434"
    model: str = "qwen2.5:1.5b"

    @classmethod
    def from_env(cls) -> "SummarizationConfig":
        return cls(
            host=os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/"),
            model=os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b"),
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


class SummarizationDisabled(RuntimeError):
    """Raised when local summarization is unavailable."""


def disabled_message(
    config: SummarizationConfig | None = None,
    language: str = "en",
) -> str:
    config = config or SummarizationConfig.from_env()
    if language == "no":
        return (
            "Lokal oppsummering er deaktivert. Installer Ollama og kjør "
            f"`ollama pull {config.model}` for å aktivere gratis lokale oppsummeringer. "
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
        model.get("name")
        for model in data.get("models", [])
        if isinstance(model, dict) and model.get("name")
    }
    if config.model not in models:
        if language == "no":
            return LocalLLMStatus(
                False,
                (
                    f"Ollama kjører, men `{config.model}` er ikke installert. "
                    f"Kjør `ollama pull {config.model}` for å aktivere lokale oppsummeringer."
                ),
            )
        return LocalLLMStatus(
            False,
            (
                f"Ollama is running, but `{config.model}` is not installed. "
                f"Run `ollama pull {config.model}` to enable local summaries."
            ),
        )

    message = (
        f"Lokal oppsummering er tilgjengelig med Ollama-modellen `{config.model}`. "
        "Ingen API-nøkler brukes."
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
            "Begrensninger / usikkerhet\n"
            "Ansvarsfraskrivelse"
        )
        language_instruction = "Svar på norsk."
    else:
        headings = (
            "Use exactly these headings:\n"
            "What did they study?\n"
            "What did they find?\n"
            "Why does it matter?\n"
            "Limitations / uncertainty\n"
            "Disclaimer"
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
        f"Abstract: {abstract}\n\n"
        f"{headings}\n\n"
        "For the final disclaimer heading, include this exact idea: "
        f"{summary_disclaimer(language)}"
    )


def summarize_paper(
    paper: Paper,
    config: SummarizationConfig | None = None,
    timeout: float = 30.0,
    mode: str = "plain",
    language: str = "en",
) -> str:
    """Summarize a paper abstract with a local Ollama chat model."""

    config = config or SummarizationConfig.from_env()
    payload: dict[str, Any] = {
        "model": config.model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You help users understand biomedical literature accurately. "
                    "You never provide medical advice, diagnosis, treatment recommendations, "
                    "or personalized health guidance."
                ),
            },
            {
                "role": "user",
                "content": build_summary_prompt(paper, mode=mode, language=language),
            },
        ],
        "stream": False,
        "options": {"temperature": 0.2},
    }

    try:
        with httpx.Client(timeout=timeout, trust_env=False) as client:
            response = client.post(config.chat_url, json=payload)
            response.raise_for_status()
            data = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise SummarizationDisabled(disabled_message(config, language)) from exc

    content = data.get("message", {}).get("content")
    if not content:
        message = (
            "Den lokale modellen returnerte en tom oppsummering."
            if language == "no"
            else "Local model returned an empty summary."
        )
        raise SummarizationDisabled(message)
    return str(content).strip()
