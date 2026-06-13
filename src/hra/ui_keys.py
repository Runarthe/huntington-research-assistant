from __future__ import annotations


def summarize_button_key(panel_key: str, paper_id: str, index: int) -> str:
    return f"summarize-{panel_key}-{paper_id}-{index}"
