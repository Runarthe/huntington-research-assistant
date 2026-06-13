from hra.ui_keys import summarize_button_key


def test_summarize_button_key_includes_panel_key() -> None:
    assert summarize_button_key("general", "41757336", 3) != summarize_button_key(
        "recent",
        "41757336",
        3,
    )
