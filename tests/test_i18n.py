from hra.i18n import TRANSLATIONS, translate
from hra.safety import medical_disclaimer, prohibited_guidance, summary_disclaimer


def test_translate_returns_norwegian_ui_label() -> None:
    assert translate("no", "search_tab") == "Søk"
    assert translate("no", "summary_mode_plain") == "Kort klarspråk"
    assert "eksperimentelle" in translate(
        "no", "norwegian_summary_experimental"
    )
    assert "senere oppdatering" in translate(
        "no", "norwegian_summary_later"
    )
    assert translate("en", "evidence_source_record") == "Source record"
    assert translate("en", "evidence_open_source") == "Open source"


def test_unknown_language_falls_back_to_english() -> None:
    assert translate("unknown", "search_tab") == "Search"


def test_translation_catalogs_have_matching_keys() -> None:
    assert set(TRANSLATIONS["no"]) == set(TRANSLATIONS["en"])


def test_safety_copy_is_available_in_both_languages() -> None:
    assert "not medical advice" in medical_disclaimer("en")
    assert "ikke medisinsk rådgivning" in medical_disclaimer("no")
    assert "personalized" in prohibited_guidance("en")
    assert "personlig" in prohibited_guidance("no")
    assert "medisinske beslutninger" in summary_disclaimer("no")
