from hra.models import Paper
from hra.summarization import (
    SummarizationConfig,
    NorwegianSummarySections,
    build_norwegian_field_prompt,
    build_summary_prompt,
    disabled_message,
    experimental_norwegian_summaries_enabled,
    format_norwegian_summary,
    select_summary_facts,
)


def test_experimental_norwegian_summaries_are_disabled_by_default(monkeypatch) -> None:
    monkeypatch.delenv(
        "HRA_ENABLE_EXPERIMENTAL_NORWEGIAN_SUMMARIES",
        raising=False,
    )

    assert experimental_norwegian_summaries_enabled() is False


def test_experimental_norwegian_summaries_can_be_opted_in(monkeypatch) -> None:
    monkeypatch.setenv("HRA_ENABLE_EXPERIMENTAL_NORWEGIAN_SUMMARIES", "true")

    assert experimental_norwegian_summaries_enabled() is True


def test_summarization_config_uses_local_ollama_defaults(monkeypatch) -> None:
    monkeypatch.delenv("OLLAMA_HOST", raising=False)
    monkeypatch.delenv("OLLAMA_MODEL", raising=False)

    config = SummarizationConfig.from_env()

    assert config.host == "http://localhost:11434"
    assert config.model == "qwen2.5:1.5b"
    assert config.norwegian_model == (
        "hf.co/norallm/normistral-7b-warm-instruct:Q4_K_M"
    )
    assert config.chat_url == "http://localhost:11434/api/chat"


def test_disabled_message_never_mentions_api_keys() -> None:
    message = disabled_message(SummarizationConfig())

    assert "Ollama" in message
    assert "API key" not in message
    assert "Search still works" in message


def test_plain_language_prompt_requests_simple_explanations() -> None:
    paper = Paper(
        id="p1",
        title="Study",
        abstract="Technical abstract",
        source_url="https://europepmc.org/article/MED/1",
    )

    prompt = build_summary_prompt(paper, mode="plain", language="en")

    assert "general reader" in prompt
    assert "explain unavoidable technical terms" in prompt
    assert "https://europepmc.org/article/MED/1" in prompt
    assert "Use only information explicitly present in the abstract" in prompt
    assert "Do not invent citations" in prompt


def test_norwegian_research_prompt_uses_norwegian_headings() -> None:
    paper = Paper(id="p1", title="Studie", abstract="Teknisk sammendrag")

    prompt = build_summary_prompt(paper, mode="research", language="no")

    assert "Svar på norsk" in prompt
    assert "Hva undersøkte de?" in prompt
    assert "forsknings" in prompt.lower()


def test_structured_abstract_facts_are_selected_deterministically() -> None:
    paper = Paper(
        id="p1",
        title="HTT study",
        abstract=(
            "Objective: To study HTT. Methods: We tested a cell model. "
            "Results: mHTT was reduced by 25%. Conclusions: The approach may help research."
        ),
    )

    facts = select_summary_facts(paper, mode="research")

    assert facts.studied == "To study HTT. We tested a cell model."
    assert facts.found == "mHTT was reduced by 25%."
    assert facts.importance == "The approach may help research."
    assert facts.limitations == "Not stated in the abstract."


def test_review_facts_use_title_and_source_sentences() -> None:
    paper = Paper(
        id="p1",
        title="Review of Huntington research.",
        abstract="First source sentence. Second source sentence. Final implication.",
        publication_types=["Review"],
    )

    facts = select_summary_facts(paper, mode="plain")

    assert facts.studied == paper.title
    assert facts.found == "First source sentence. Second source sentence."
    assert facts.importance == "Final implication."


def test_norwegian_field_prompt_uses_glossary_and_locked_facts() -> None:
    paper = Paper(
        id="p1",
        title="Gene silencing study",
        abstract="Gene silencing reduced mHTT by 25%.",
    )
    prompt = build_norwegian_field_prompt(
        paper,
        "found",
        "Gene silencing reduced mHTT by 25%.",
    )

    assert "gendemping" in prompt
    assert "mHTT" in prompt
    assert "25%" in prompt
    assert "Behold alle tall" in prompt


def test_norwegian_summary_format_is_compact_and_deterministic() -> None:
    sections = NorwegianSummarySections(
        studied="Studien undersøkte HTT.",
        found="HTT ble redusert.",
        importance="Ikke oppgitt i abstraktet.",
        limitations="Ikke oppgitt i abstraktet.",
    )

    result = format_norwegian_summary(sections)

    assert result.startswith("**Hva undersøkte de?**")
    assert "##" not in result
    assert "**Begrensninger og usikkerhet**" in result


def test_review_summary_uses_review_specific_labels() -> None:
    sections = NorwegianSummarySections(
        studied="Artikkelen gjennomgår forskningen.",
        found="Den beskriver flere mekanismer.",
        importance="Temaet er relevant for videre forskning.",
        limitations="Ikke oppgitt i abstraktet.",
    )

    result = format_norwegian_summary(sections, is_review=True)

    assert "**Hva handler oversiktsartikkelen om?**" in result
    assert "**Hva beskriver den?**" in result
