from __future__ import annotations

from hra.tagging import TAG_KEYWORDS

DEFAULT_QUERY = "gene silencing"

HUNTINGTON_TERMS = (
    '"Huntington disease"',
    '"Huntington\'s disease"',
    "huntingtin",
    "HTT",
)


def normalize_user_query(user_query: str | None) -> str:
    """Return a compact query string with a useful default."""

    query = " ".join((user_query or "").split())
    return query or DEFAULT_QUERY


def expand_huntington_query(user_query: str | None) -> str:
    """Expand a user query into a Huntington-focused Europe PMC query."""

    normalized = normalize_user_query(user_query)
    huntington_clause = " OR ".join(HUNTINGTON_TERMS)
    return f"({huntington_clause}) AND ({normalized})"


def build_dashboard_query(
    expanded_query: str,
    selected_tags: list[str] | None = None,
    open_access_only: bool = False,
) -> str:
    """Add API-representable filters for publication-count analytics."""

    clauses = [f"({expanded_query})"]
    keywords = {
        keyword
        for tag in selected_tags or []
        for keyword in TAG_KEYWORDS.get(tag, ())
    }
    if keywords:
        keyword_query = " OR ".join(_quote_term(keyword) for keyword in sorted(keywords))
        clauses.append(f"({keyword_query})")
    if open_access_only:
        clauses.append("OPEN_ACCESS:Y")
    return " AND ".join(clauses)


def _quote_term(term: str) -> str:
    return f'"{term}"' if " " in term else term
