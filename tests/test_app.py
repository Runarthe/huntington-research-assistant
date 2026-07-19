from pathlib import Path
from unittest.mock import patch

import streamlit as st
from streamlit.testing.v1 import AppTest

from hra.clients.europe_pmc import EuropePMCClient
from hra.models import Paper, SearchResponse
from app.streamlit_app import (
    _blueprint_available_execution_modes,
    _blueprint_cli_commands,
    _blueprint_provider_status_key,
)


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
    assert "Blueprint Lab preview" in {subheader.value for subheader in app.subheader}
    assert any("No model runs automatically" in info.value for info in app.caption)
    assert any(
        "deterministic local fixture data" in info.value
        for info in app.info
    )
    assert "Step 1: Select a curated target" in {
        caption.value for caption in app.caption
    }
    assert "Download planned manifest JSON" in {
        button.label for button in app.get("download_button")
    }
    assert "Download mock manifest JSON" in {
        button.label for button in app.get("download_button")
    }
    assert "Report source" in {radio.label for radio in app.radio}
    assert "Explanations" in {radio.label for radio in app.radio}
    assert "Local ESM-2 experiment" in {subheader.value for subheader in app.subheader}
    assert "Download ESM-2 plan JSON" in {
        button.label for button in app.get("download_button")
    }
    assert "Run local ESM-2" in {button.label for button in app.button}
    assert "Provider parity review" in {
        subheader.value for subheader in app.subheader
    }
    assert "Download BioNeMo plan JSON" in {
        button.label for button in app.get("download_button")
    }
    assert "Download parity report JSON" in {
        button.label for button in app.get("download_button")
    }


def test_blueprint_provider_status_keys_distinguish_provider_boundaries() -> None:
    assert (
        _blueprint_provider_status_key(
            {"provider_type": "mock", "live_enabled": False}
        )
        == "blueprint_lab_provider_mock_fixture"
    )
    assert (
        _blueprint_provider_status_key(
            {"provider_type": "uniprot", "live_enabled": False}
        )
        == "blueprint_lab_provider_public_data_gated"
    )
    assert (
        _blueprint_provider_status_key(
            {"provider_type": "bionemo", "live_enabled": False}
        )
        == "blueprint_lab_provider_planned_only"
    )
    assert (
        _blueprint_provider_status_key(
            {"provider_type": "bionemo", "live_enabled": True}
        )
        == "blueprint_lab_provider_live_ready"
    )


def test_blueprint_preview_exposes_only_safe_execution_modes() -> None:
    assert _blueprint_available_execution_modes("mock") == ("offline",)
    assert _blueprint_available_execution_modes("uniprot") == ("planned",)
    assert _blueprint_available_execution_modes("bionemo") == ("planned",)


def test_blueprint_cli_commands_only_offer_mock_run_for_mock_provider() -> None:
    mock_commands = _blueprint_cli_commands("mock", "offline", "HTT")
    bionemo_commands = _blueprint_cli_commands("bionemo", "planned", "HTT")

    assert any("run-mock" in command for command in mock_commands)
    assert all("run-mock" not in command for command in bionemo_commands)
    assert any("--provider-type bionemo" in command for command in bionemo_commands)


def test_blueprint_preview_hides_mock_artifacts_for_planned_provider() -> None:
    st.cache_data.clear()
    app = AppTest.from_file(str(APP_PATH), default_timeout=30).run()
    provider_select = next(
        selectbox
        for selectbox in app.selectbox
        if selectbox.label == "Provider family"
    )

    provider_select.select("bionemo").run()

    assert not app.exception
    assert any("planning target only" in info.value for info in app.info)
    assert "Download planned manifest JSON" in {
        button.label for button in app.get("download_button")
    }
    assert "Download mock manifest JSON" not in {
        button.label for button in app.get("download_button")
    }
