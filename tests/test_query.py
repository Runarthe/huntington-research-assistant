from hra.query import (
    DEFAULT_QUERY,
    build_dashboard_query,
    build_literature_query,
    build_pubmed_query,
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


def test_literature_query_adds_provider_side_year_range() -> None:
    query = build_literature_query(
        "(huntingtin) AND (biomarker)",
        year_range=(2020, 2026),
        open_access_only=True,
    )

    assert "PUB_YEAR:[2020 TO 2026]" in query
    assert "OPEN_ACCESS:Y" in query


def test_build_pubmed_query_adds_pubmed_filters() -> None:
    query = build_pubmed_query(
        "(huntingtin) AND (biomarker)",
        selected_tags=["biomarkers"],
        year_range=(2020, 2026),
        open_access_only=True,
    )

    assert '"2020"[Date - Publication] : "2026"[Date - Publication]' in query
    assert "free full text[sb]" in query
    assert "neurofilament" in query
