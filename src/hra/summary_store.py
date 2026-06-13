from __future__ import annotations

from collections.abc import MutableMapping


SUMMARY_STORE_KEY = "paper_summaries"


def get_summary_store(session_state: MutableMapping[str, object]) -> dict[str, str]:
    store = session_state.setdefault(SUMMARY_STORE_KEY, {})
    if not isinstance(store, dict):
        store = {}
        session_state[SUMMARY_STORE_KEY] = store
    return store
