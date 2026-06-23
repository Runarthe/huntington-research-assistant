from hra.models import Paper
from hra.summarization import SummarizationConfig, build_summary_prompt, disabled_message


def test_summarization_config_uses_local_ollama_defaults(monkeypatch) -> None:
    monkeypatch.delenv("OLLAMA_HOST", raising=False)
    monkeypatch.delenv("OLLAMA_MODEL", raising=False)

    config = SummarizationConfig.from_env()

    assert config.host == "http://localhost:11434"
    assert config.model == "qwen2.5:1.5b"
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
