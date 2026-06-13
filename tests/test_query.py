from hra.query import (
    DEFAULT_QUERY,
    build_dashboard_query,
    expand_huntington_query,
    normalize_user_query,
)


def test_normalize_user_query_uses_default_for_blank_input() -> None:
    assert normalize_user_query("   ") == DEFAULT_QUERY
    assert normalize_user_query(None) == DEFAULT_QUERY


def test_expand_huntington_query_wraps_user_topic() -> None:
    expanded = expand_huntington_query("gene silencing")

    assert '"Huntington disease"' in expanded
    assert '"Huntington\'s disease"' in expanded
    assert "huntingtin" in expanded
    assert "HTT" in expanded
    assert expanded.endswith("AND (gene silencing)")


def test_build_dashboard_query_adds_category_and_open_access_filters() -> None:
    query = build_dashboard_query(
        "(huntingtin) AND (therapy)",
        selected_tags=["biomarkers"],
        open_access_only=True,
    )

    assert '"imaging marker"' in query
    assert "biomarker" in query
    assert "OPEN_ACCESS:Y" in query
