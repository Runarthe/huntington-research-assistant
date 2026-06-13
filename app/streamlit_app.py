from __future__ import annotations

import sqlite3
import sys
from datetime import date
from pathlib import Path

import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

loaded_hra = sys.modules.get("hra")
if loaded_hra is not None:
    loaded_path = Path(getattr(loaded_hra, "__file__", "")).resolve()
    if SRC_DIR.resolve() not in loaded_path.parents:
        for module_name in list(sys.modules):
            if module_name == "hra" or module_name.startswith("hra."):
                del sys.modules[module_name]

from hra.cache import SearchCache
from hra.clients.europe_pmc import EuropePMCClient, EuropePMCError
from hra.filters import filter_papers, sort_papers_by_year
from hra.i18n import LANGUAGE_OPTIONS, translate
from hra.models import Paper, SearchResponse
from hra.query import (
    DEFAULT_QUERY,
    build_dashboard_query,
    expand_huntington_query,
    normalize_user_query,
)
from hra.safety import medical_disclaimer, prohibited_guidance
from hra.summarization import (
    SummarizationConfig,
    SummarizationDisabled,
    disabled_message,
    local_llm_status,
    summarize_paper,
)
from hra.summary_store import get_summary_store
from hra.tagging import TAG_KEYWORDS
from hra.ui_keys import summarize_button_key


st.set_page_config(
    page_title="Huntington Research Assistant",
    page_icon="HRA",
    layout="wide",
)

CURRENT_YEAR = date.today().year
MIN_YEAR = 1990
ALL_TAGS = list(TAG_KEYWORDS)
CLINICAL_TRIAL_QUERY = "clinical trial OR randomized OR placebo OR phase 1 OR phase 2 OR phase 3"
RECENT_PROGRESS_QUERY = (
    "biomarker OR neurofilament OR gene silencing OR huntingtin lowering "
    "OR clinical trial OR therapy development OR disease progression"
)


@st.cache_data(show_spinner=False, ttl=900)
def search_europe_pmc(expanded_query: str, page: int, page_size: int) -> SearchResponse:
    client = EuropePMCClient()
    return client.search(expanded_query, page=page, page_size=page_size)


@st.cache_data(show_spinner=False, ttl=3600)
def publication_counts_by_year(
    dashboard_query: str,
    start_year: int,
    end_year: int,
) -> list[dict[str, int]]:
    client = EuropePMCClient()
    return client.count_by_year(dashboard_query, start_year, end_year)


def get_cache() -> SearchCache | None:
    try:
        return SearchCache()
    except (OSError, sqlite3.Error) as exc:
        st.warning(f"Local cache is unavailable. Search will still work. Details: {exc}")
        return None


def safe_cache_write(cache: SearchCache | None, action: str, *args: object) -> bool:
    if cache is None:
        return False

    try:
        getattr(cache, action)(*args)
    except (OSError, sqlite3.Error) as exc:
        st.warning(f"Local cache write failed. Search will still work. Details: {exc}")
        return False
    return True


def safe_recent_searches(cache: SearchCache | None, limit: int = 5) -> list[dict[str, object]]:
    if cache is None:
        return []

    try:
        return cache.recent_searches(limit=limit)
    except (OSError, sqlite3.Error) as exc:
        st.warning(f"Recent searches are unavailable. Details: {exc}")
        return []


def render_paper(
    paper: Paper,
    index: int,
    panel_key: str,
    summary_config: SummarizationConfig,
    summary_available: bool,
    language: str,
    summary_mode: str,
) -> None:
    summaries = get_summary_store(st.session_state)
    summary_key = f"{paper.id}:{language}:{summary_mode}"

    st.subheader(paper.title)

    meta_parts = [
        str(part)
        for part in (
            paper.year,
            paper.journal,
            paper.author_display,
        )
        if part
    ]
    st.caption(" | ".join(meta_parts))

    if paper.tags:
        st.write(" ".join(f"`{tag}`" for tag in paper.tags))

    st.write(paper.abstract_snippet)

    link_parts = []
    if paper.doi:
        link_parts.append(f"DOI: `{paper.doi}`")
    if paper.pmid:
        link_parts.append(f"PMID: `{paper.pmid}`")
    if paper.citation_count is not None:
        link_parts.append(
            f"{translate(language, 'citations')}: `{paper.citation_count}`"
        )
    if paper.is_open_access is not None:
        access_value = translate(language, "yes" if paper.is_open_access else "no")
        link_parts.append(
            f"{translate(language, 'open_access')}: `{access_value}`"
        )
    if link_parts:
        st.caption(" | ".join(link_parts))

    if paper.source_url:
        st.link_button(translate(language, "source_record"), str(paper.source_url))

    with st.expander(translate(language, "abstract")):
        st.write(paper.abstract or translate(language, "no_abstract"))

    if language == "no":
        return

    button_key = summarize_button_key(panel_key, paper.id, index)
    if st.button(translate(language, "summarize"), key=button_key):
        if not summary_available:
            st.info(disabled_message(summary_config, language))
        elif not paper.abstract:
            st.warning(translate(language, "no_abstract"))
        else:
            with st.spinner(
                translate(language, "summarizing", model=summary_config.model)
            ):
                try:
                    summary = summarize_paper(
                        paper,
                        config=summary_config,
                        mode=summary_mode,
                        language=language,
                    )
                except SummarizationDisabled as exc:
                    st.info(str(exc))
                except Exception as exc:  # Streamlit should show friendly API failures.
                    st.error(translate(language, "summary_failed", error=exc))
                else:
                    summaries[summary_key] = summary

    if summary_key in summaries:
        summary_label = translate(
            language,
            "plain_summary" if summary_mode == "plain" else "research_summary",
        )
        with st.expander(summary_label, expanded=True):
            st.markdown(summaries[summary_key])
            if paper.source_url:
                st.caption(f"Source / Kilde: {paper.source_url}")


def render_results(
    papers: list[Paper],
    panel_key: str,
    summary_config: SummarizationConfig,
    summary_available: bool,
    language: str,
    summary_mode: str,
) -> None:
    if not papers:
        st.info(translate(language, "no_papers"))
        return

    for index, paper in enumerate(papers, start=1):
        with st.container(border=True):
            render_paper(
                paper,
                index,
                panel_key,
                summary_config,
                summary_available,
                language,
                summary_mode,
            )


def render_publication_dashboard(
    yearly_counts: list[dict[str, int]],
    language: str,
) -> None:
    if not yearly_counts:
        st.caption(translate(language, "no_timeline"))
        return

    period_total = sum(item["papers"] for item in yearly_counts)
    current_count = next(
        (item["papers"] for item in yearly_counts if item["year"] == CURRENT_YEAR),
        None,
    )
    peak = max(yearly_counts, key=lambda item: item["papers"])

    current_col, total_col, peak_col = st.columns(3)
    current_col.metric(
        translate(language, "this_year"),
        f"{current_count:,}" if current_count is not None else "—",
    )
    total_col.metric(translate(language, "period_total"), f"{period_total:,}")
    peak_col.metric(
        translate(language, "peak_year"),
        f"{peak['year']} ({peak['papers']:,})",
    )

    st.caption(translate(language, "dashboard_note"))
    st.subheader(translate(language, "yearly_trend"))
    st.line_chart(yearly_counts, x="year", y="papers", width="stretch")


def run_search_panel(
    *,
    panel_key: str,
    default_query: str,
    submit_label: str,
    summary_config: SummarizationConfig,
    summary_available: bool,
    language: str,
    summary_mode: str,
    cache: SearchCache | None,
    default_tags: list[str] | None = None,
    default_year_start: int = 2015,
    help_text: str = "Enter a research topic, not personal health information.",
    intro: str | None = None,
) -> None:
    if intro:
        st.caption(intro)

    with st.form(f"{panel_key}-form"):
        query = st.text_input(
            translate(language, "research_topic"),
            value=default_query,
            placeholder=translate(language, "research_topic_placeholder"),
            help=translate(language, "research_topic_help") if help_text else None,
            key=f"{panel_key}-query",
        )
        selected_tags = st.multiselect(
            translate(language, "category_filters"),
            options=ALL_TAGS,
            default=default_tags or [],
            key=f"{panel_key}-tags",
        )
        year_range = st.slider(
            translate(language, "publication_year"),
            min_value=MIN_YEAR,
            max_value=CURRENT_YEAR,
            value=(max(MIN_YEAR, default_year_start), CURRENT_YEAR),
            key=f"{panel_key}-year-range",
        )
        open_access_only = st.checkbox(
            translate(language, "open_access_only"),
            value=False,
            key=f"{panel_key}-open-access",
        )
        max_results = st.slider(
            translate(language, "results_to_show"),
            min_value=5,
            max_value=50,
            value=10,
            step=5,
            key=f"{panel_key}-max-results",
        )
        submitted = st.form_submit_button(submit_label)

    normalized_query = normalize_user_query(query)
    expanded_query = expand_huntington_query(normalized_query)
    dashboard_query = build_dashboard_query(
        expanded_query,
        selected_tags=selected_tags,
        open_access_only=open_access_only,
    )

    with st.expander(translate(language, "expanded_query")):
        st.code(expanded_query)

    if submitted:
        safe_cache_write(cache, "record_search", normalized_query, expanded_query)

        fetch_size = min(max_results * 3, 100)
        with st.spinner(translate(language, "searching")):
            try:
                response = search_europe_pmc(expanded_query, 1, int(fetch_size))
            except EuropePMCError as exc:
                st.error(str(exc))
                return

        safe_cache_write(cache, "upsert_papers", response.papers)
        st.session_state[f"{panel_key}-response"] = response
        st.session_state[f"{panel_key}-filters"] = {
            "selected_tags": selected_tags,
            "year_range": year_range,
            "open_access_only": open_access_only,
            "max_results": max_results,
        }
        try:
            with st.spinner(translate(language, "loading_dashboard")):
                yearly_counts = publication_counts_by_year(
                    dashboard_query,
                    int(year_range[0]),
                    int(year_range[1]),
                )
        except EuropePMCError as exc:
            st.session_state[f"{panel_key}-dashboard"] = []
            st.session_state[f"{panel_key}-dashboard-error"] = str(exc)
        else:
            st.session_state[f"{panel_key}-dashboard"] = yearly_counts
            st.session_state.pop(f"{panel_key}-dashboard-error", None)

    response = st.session_state.get(f"{panel_key}-response")
    filters = st.session_state.get(f"{panel_key}-filters")
    if not response or not filters:
        st.write(translate(language, "start_search"))
        return

    filtered = filter_papers(
        response.papers,
        selected_tags=filters["selected_tags"],
        year_range=tuple(filters["year_range"]),
        open_access_only=filters["open_access_only"],
    )
    filtered = sort_papers_by_year(filtered)[: filters["max_results"]]

    st.caption(translate(language, "paper_batch_count", shown=len(filtered)))

    st.subheader(translate(language, "publication_dashboard"))
    dashboard_error = st.session_state.get(f"{panel_key}-dashboard-error")
    if dashboard_error:
        st.warning(
            translate(language, "dashboard_unavailable", error=dashboard_error)
        )
    else:
        render_publication_dashboard(
            st.session_state.get(f"{panel_key}-dashboard", []),
            language,
        )

    st.subheader(translate(language, "papers"))
    render_results(
        filtered,
        panel_key,
        summary_config,
        summary_available,
        language,
        summary_mode,
    )


def main() -> None:
    language_name = st.sidebar.selectbox(
        "Language / Språk",
        options=list(LANGUAGE_OPTIONS),
        key="ui-language",
    )
    language = LANGUAGE_OPTIONS[language_name]
    if language == "no":
        summary_mode = "plain"
    else:
        summary_mode = st.sidebar.radio(
            translate(language, "summary_style"),
            options=["plain", "research"],
            format_func=lambda value: translate(language, f"summary_mode_{value}"),
            horizontal=True,
            key="summary-mode",
        )

    st.title("Huntington Research Assistant")
    st.warning(medical_disclaimer(language))
    st.caption(prohibited_guidance(language))

    summary_config = SummarizationConfig.from_env()
    status = local_llm_status(summary_config, language=language)
    if language == "no":
        st.info(translate(language, "norwegian_summary_later"))
    elif status.available:
        st.success(status.message)
    else:
        st.info(status.message)

    cache = get_cache()

    search_tab, clinical_tab, recent_tab = st.tabs(
        [
            translate(language, "search_tab"),
            translate(language, "clinical_tab"),
            translate(language, "recent_tab"),
        ]
    )

    with search_tab:
        run_search_panel(
            panel_key="general",
            default_query=DEFAULT_QUERY,
            submit_label=translate(language, "search_europe_pmc"),
            summary_config=summary_config,
            summary_available=status.available,
            language=language,
            summary_mode=summary_mode,
            cache=cache,
            default_year_start=2015,
        )

    with clinical_tab:
        run_search_panel(
            panel_key="clinical",
            default_query=CLINICAL_TRIAL_QUERY,
            submit_label=translate(language, "search_trials"),
            summary_config=summary_config,
            summary_available=status.available,
            language=language,
            summary_mode=summary_mode,
            cache=cache,
            default_tags=["clinical trials"],
            default_year_start=2010,
            intro=translate(language, "clinical_intro"),
        )

    with recent_tab:
        run_search_panel(
            panel_key="recent",
            default_query=RECENT_PROGRESS_QUERY,
            submit_label=translate(language, "search_recent"),
            summary_config=summary_config,
            summary_available=status.available,
            language=language,
            summary_mode=summary_mode,
            cache=cache,
            default_year_start=CURRENT_YEAR - 2,
            intro=translate(language, "recent_intro"),
        )

    if cache is not None:
        with st.sidebar:
            st.header(translate(language, "recent_searches"))
            for item in safe_recent_searches(cache, limit=5):
                st.caption(item["created_at"])
                st.write(item["query"])


if __name__ == "__main__":
    main()
