from pathlib import Path
from unittest.mock import patch

import streamlit as st
from streamlit.testing.v1 import AppTest

from hra.clients.europe_pmc import EuropePMCClient
from hra.models import Paper, SearchResponse


APP_PATH = Path(__file__).parents[1] / "app" / "streamlit_app.py"


def test_entity_explorer_builds_map_from_provider_response() -> None:
    response = SearchResponse(
        query="fixture",
        page=1,
        page_size=10,
        total_results=1,
        papers=[
            Paper(
                id="fixture-1",
                title="HTT gene and autophagy",
                abstract=(
                    "Mutant huntingtin and NfL were measured. "
                    "Tominersen was discussed."
                ),
                source_url="https://europepmc.org/article/MED/fixture-1",
            )
        ],
    )

    st.cache_data.clear()
    with patch.object(EuropePMCClient, "search", return_value=response):
        app = AppTest.from_file(str(APP_PATH), default_timeout=30).run()
        build_button = next(
            button
            for button in app.button
            if button.label == "Build map from Europe PMC"
        )

        build_button.click().run()

    assert not app.exception
    assert "Also catalogued in the same source papers" in {
        subheader.value for subheader in app.subheader
    }
    assert any(
        subheader.value.startswith("Papers mentioning")
        for subheader in app.subheader
    )


def test_protein_lab_tab_renders_without_live_calls() -> None:
    st.cache_data.clear()
    app = AppTest.from_file(str(APP_PATH), default_timeout=30).run()

    assert not app.exception
    assert "Protein Lab (experimental)" in {subheader.value for subheader in app.subheader}
    assert any("No live model calls" in info.value for info in app.caption)
    assert "Report source" in {radio.label for radio in app.radio}
    assert "Explanations" in {radio.label for radio in app.radio}
