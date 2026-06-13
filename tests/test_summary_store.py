from hra.summary_store import SUMMARY_STORE_KEY, get_summary_store


def test_get_summary_store_reuses_existing_store() -> None:
    state: dict[str, object] = {SUMMARY_STORE_KEY: {"paper-1": "summary"}}

    store = get_summary_store(state)

    assert store == {"paper-1": "summary"}
    assert state[SUMMARY_STORE_KEY] is store


def test_get_summary_store_resets_invalid_store() -> None:
    state: dict[str, object] = {SUMMARY_STORE_KEY: "not a dict"}

    store = get_summary_store(state)

    assert store == {}
    assert state[SUMMARY_STORE_KEY] is store
