from __future__ import annotations

import sqlite3
import sys
from datetime import date
from math import ceil
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
from hra.clients.clinical_trials import (
    TRIAL_STATUS_OPTIONS,
    ClinicalTrialsClient,
    ClinicalTrialsError,
)
from hra.clients.europe_pmc import EuropePMCClient, EuropePMCError
from hra.export import (
    paper_text_filename,
    paper_to_text,
    papers_to_bibtex,
    papers_to_csv,
    trials_to_csv,
)
from hra.i18n import LANGUAGE_OPTIONS, translate
from hra.knowledge_graph import build_research_map, graphviz_dot
from hra.models import ClinicalTrial, ClinicalTrialResponse, Paper, SearchResponse
from hra.norwegian_language import SummaryIntegrityError
from hra.query import (
    DEFAULT_QUERY,
    build_dashboard_query,
    build_literature_query,
    expand_huntington_query,
    normalize_user_query,
)
from hra.safety import medical_disclaimer, prohibited_guidance, summary_disclaimer
from hra.summarization import (
    SUMMARY_PIPELINE_VERSION,
    SummarizationConfig,
    SummarizationDisabled,
    disabled_message,
    experimental_norwegian_summaries_enabled,
    local_llm_status,
    summarize_paper,
)
from hra.summary_store import get_summary_store
from hra.tagging import TAG_KEYWORDS
from hra.trial_filters import filter_trials, trial_filter_options
from hra.ui_keys import summarize_button_key


st.set_page_config(
    page_title="Huntington Research Assistant",
    page_icon="HRA",
    layout="wide",
)

CURRENT_YEAR = date.today().year
MIN_YEAR = 1990
ALL_TAGS = list(TAG_KEYWORDS)
RECENT_PROGRESS_QUERY = (
    "biomarker OR neurofilament OR gene silencing OR huntingtin lowering "
    "OR clinical trial OR therapy development OR disease progression"
)
DEFAULT_TRIAL_STATUSES = [
    "RECRUITING",
    "NOT_YET_RECRUITING",
    "ACTIVE_NOT_RECRUITING",
    "ENROLLING_BY_INVITATION",
    "COMPLETED",
    "TERMINATED",
]


@st.cache_data(show_spinner=False, ttl=900)
def search_europe_pmc(
    expanded_query: str,
    cursor_mark: str,
    page: int,
    page_size: int,
) -> SearchResponse:
    client = EuropePMCClient()
    return client.search(
        expanded_query,
        page=page,
        page_size=page_size,
        cursor_mark=cursor_mark,
    )


@st.cache_data(show_spinner=False, ttl=3600)
def publication_counts_by_year(
    dashboard_query: str,
    start_year: int,
    end_year: int,
) -> list[dict[str, int]]:
    client = EuropePMCClient()
    return client.count_by_year(dashboard_query, start_year, end_year)


@st.cache_data(show_spinner=False, ttl=3600)
def search_clinical_trials(
    other_terms: str,
    statuses: tuple[str, ...],
) -> ClinicalTrialResponse:
    client = ClinicalTrialsClient()
    return client.search(
        condition="Huntington Disease",
        other_terms=other_terms or None,
        statuses=list(statuses),
        page_size=1000,
    )


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
    summary_key = (
        f"{paper.id}:{language}:{summary_mode}:{summary_config.model}:"
        f"{summary_config.norwegian_model}:{SUMMARY_PIPELINE_VERSION}"
    )

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

    if paper.publication_types:
        st.caption(
            f"{translate(language, 'publication_types')}: "
            + ", ".join(paper.publication_types)
        )

    if paper.is_retracted:
        st.error(translate(language, "retracted_warning"))
    elif paper.has_correction:
        st.warning(translate(language, "correction_notice"))

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

    action_count = 1 + int(paper.source_url is not None) + int(
        paper.open_access_pdf_url is not None
    )
    action_columns = st.columns(action_count)
    action_index = 0
    if paper.source_url:
        action_columns[action_index].link_button(
            translate(language, "source_record"),
            str(paper.source_url),
            use_container_width=True,
        )
        action_index += 1
    if paper.open_access_pdf_url:
        action_columns[action_index].link_button(
            translate(language, "open_access_pdf"),
            str(paper.open_access_pdf_url),
            use_container_width=True,
        )
        action_index += 1
    action_columns[action_index].download_button(
        translate(language, "download_paper_details"),
        data=paper_to_text(paper).encode("utf-8"),
        file_name=paper_text_filename(paper),
        mime="text/plain",
        key=f"{panel_key}-download-paper-{paper.id}-{index}",
        use_container_width=True,
    )

    with st.expander(translate(language, "abstract")):
        st.write(paper.abstract or translate(language, "no_abstract"))

    if paper.correction_notices:
        with st.expander(translate(language, "related_notices")):
            for notice in paper.correction_notices:
                label = notice.reference or notice.notice_type
                if notice.source_url:
                    st.markdown(f"- [{notice.notice_type}: {label}]({notice.source_url})")
                else:
                    st.write(f"- {notice.notice_type}: {label}")

    if language == "no" and not experimental_norwegian_summaries_enabled():
        st.caption(translate(language, "norwegian_summary_later"))
        return

    if language == "no":
        st.caption(translate(language, "norwegian_summary_experimental"))

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
                except SummaryIntegrityError as exc:
                    st.warning(
                        translate(
                            language,
                            "summary_integrity_failed",
                            reason=exc,
                        )
                    )
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
            st.caption(summary_disclaimer(language))
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


def render_paper_exports(papers: list[Paper], panel_key: str, language: str) -> None:
    if not papers:
        return
    st.caption(translate(language, "current_page_export_note"))
    csv_col, bibtex_col = st.columns(2)
    csv_col.download_button(
        translate(language, "download_csv"),
        data=papers_to_csv(papers).encode("utf-8-sig"),
        file_name=f"hra-{panel_key}-papers.csv",
        mime="text/csv",
        key=f"{panel_key}-download-csv",
        use_container_width=True,
    )
    bibtex_col.download_button(
        translate(language, "download_bibtex"),
        data=papers_to_bibtex(papers),
        file_name=f"hra-{panel_key}-papers.bib",
        mime="application/x-bibtex",
        key=f"{panel_key}-download-bibtex",
        use_container_width=True,
    )


def set_literature_page(panel_key: str, page: int) -> None:
    st.session_state[f"{panel_key}-page"] = page


def render_pagination(
    panel_key: str,
    page: int,
    total_pages: int,
    language: str,
    position: str,
) -> None:
    previous_col, status_col, next_col = st.columns([1, 2, 1])
    previous_col.button(
        translate(language, "previous_page"),
        disabled=page <= 1,
        key=f"{panel_key}-{position}-previous-page",
        use_container_width=True,
        on_click=set_literature_page,
        args=(panel_key, page - 1),
    )
    status_col.markdown(
        f"**{translate(language, 'page_status', page=page, total_pages=total_pages)}**"
    )
    next_col.button(
        translate(language, "next_page"),
        disabled=page >= total_pages,
        key=f"{panel_key}-{position}-next-page",
        use_container_width=True,
        on_click=set_literature_page,
        args=(panel_key, page + 1),
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
    with st.expander(translate(language, "accessible_trend_table")):
        st.table(
            [
                {
                    translate(language, "year"): item["year"],
                    translate(language, "publication_count"): item["papers"],
                }
                for item in yearly_counts
            ]
        )


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
        page_size = st.selectbox(
            translate(language, "results_to_show"),
            options=[10, 25, 50],
            index=0,
            key=f"{panel_key}-page-size",
        )
        submitted = st.form_submit_button(submit_label)

    normalized_query = normalize_user_query(query)
    expanded_query = expand_huntington_query(normalized_query)
    with st.expander(translate(language, "expanded_query")):
        st.code(expanded_query)

    if submitted:
        safe_cache_write(cache, "record_search", normalized_query, expanded_query)
        dashboard_query = build_dashboard_query(
            expanded_query,
            selected_tags=selected_tags,
            open_access_only=open_access_only,
        )
        provider_query = build_literature_query(
            expanded_query,
            selected_tags=selected_tags,
            year_range=(int(year_range[0]), int(year_range[1])),
            open_access_only=open_access_only,
        )
        st.session_state[f"{panel_key}-request"] = {
            "provider_query": provider_query,
            "dashboard_query": dashboard_query,
            "year_range": (int(year_range[0]), int(year_range[1])),
            "page_size": int(page_size),
        }
        st.session_state[f"{panel_key}-page"] = 1
        st.session_state[f"{panel_key}-cursor-history"] = ["*"]
        st.session_state[f"{panel_key}-dashboard-pending"] = True

    request = st.session_state.get(f"{panel_key}-request")
    if not request:
        st.write(translate(language, "start_search"))
        return

    page = int(st.session_state.get(f"{panel_key}-page", 1))
    cursor_history = list(
        st.session_state.get(f"{panel_key}-cursor-history", ["*"])
    )
    if page > len(cursor_history):
        page = len(cursor_history)
        st.session_state[f"{panel_key}-page"] = page
    cursor_mark = cursor_history[page - 1]
    with st.spinner(translate(language, "searching")):
        try:
            response = search_europe_pmc(
                str(request["provider_query"]),
                cursor_mark,
                page,
                int(request["page_size"]),
            )
        except EuropePMCError as exc:
            st.error(str(exc))
            return

    safe_cache_write(cache, "upsert_papers", response.papers)
    if response.next_cursor_mark and len(cursor_history) == page:
        cursor_history.append(response.next_cursor_mark)
        st.session_state[f"{panel_key}-cursor-history"] = cursor_history
    if st.session_state.pop(f"{panel_key}-dashboard-pending", False):
        try:
            with st.spinner(translate(language, "loading_dashboard")):
                yearly_counts = publication_counts_by_year(
                    str(request["dashboard_query"]),
                    int(request["year_range"][0]),
                    int(request["year_range"][1]),
                )
        except EuropePMCError as exc:
            st.session_state[f"{panel_key}-dashboard"] = []
            st.session_state[f"{panel_key}-dashboard-error"] = str(exc)
        else:
            st.session_state[f"{panel_key}-dashboard"] = yearly_counts
            st.session_state.pop(f"{panel_key}-dashboard-error", None)

    total_results = response.total_results or len(response.papers)
    total_pages = max(1, ceil(total_results / int(request["page_size"])))
    st.caption(
        translate(
            language,
            "result_count",
            total=total_results,
            shown=len(response.papers),
        )
    )
    st.info(
        translate(
            language,
            "pagination_help",
            shown=len(response.papers),
            total=total_results,
        )
    )
    render_pagination(panel_key, page, total_pages, language, position="top")

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

    render_paper_exports(response.papers, panel_key, language)
    st.subheader(translate(language, "papers"))
    render_results(
        response.papers,
        panel_key,
        summary_config,
        summary_available,
        language,
        summary_mode,
    )
    render_pagination(panel_key, page, total_pages, language, position="bottom")


def trial_status_label(status: str, language: str) -> str:
    norwegian = {
        "RECRUITING": "Rekrutterer",
        "NOT_YET_RECRUITING": "Har ikke startet rekruttering",
        "ACTIVE_NOT_RECRUITING": "Aktiv, rekrutterer ikke",
        "ENROLLING_BY_INVITATION": "Deltakelse etter invitasjon",
        "COMPLETED": "Fullført",
        "SUSPENDED": "Midlertidig stanset",
        "TERMINATED": "Avsluttet før planlagt",
        "WITHDRAWN": "Trukket før oppstart",
        "UNKNOWN": "Ukjent",
    }
    if language == "no":
        return norwegian.get(status, status.replace("_", " ").title())
    return status.replace("_", " ").title()


def render_trial(trial: ClinicalTrial, language: str) -> None:
    st.subheader(trial.brief_title)
    phase = ", ".join(item.replace("_", " ").title() for item in trial.phases) or "—"
    st.caption(
        f"{trial.nct_id} | {translate(language, 'trial_status')}: "
        f"{trial_status_label(trial.overall_status, language)} | "
        f"{translate(language, 'trial_phase')}: {phase}"
    )
    if trial.brief_summary:
        st.write(trial.brief_summary)

    details: list[str] = []
    if trial.sponsor:
        details.append(f"**{translate(language, 'trial_sponsor')}:** {trial.sponsor}")
    if trial.enrollment is not None:
        details.append(f"**{translate(language, 'trial_enrollment')}:** {trial.enrollment:,}")
    if trial.interventions:
        details.append(
            f"**{translate(language, 'trial_interventions')}:** "
            + "; ".join(trial.interventions)
        )
    if trial.countries:
        details.append(
            f"**{translate(language, 'trial_locations')}:** " + ", ".join(trial.countries)
        )
    dates = " – ".join(value for value in (trial.start_date, trial.completion_date) if value)
    if dates:
        details.append(f"**{translate(language, 'trial_dates')}:** {dates}")
    if trial.last_update:
        details.append(f"**{translate(language, 'trial_last_update')}:** {trial.last_update}")
    for detail in details:
        st.markdown(detail)

    st.link_button(translate(language, "open_trial_record"), str(trial.source_url))


def run_trial_tracker(language: str) -> None:
    st.subheader(translate(language, "clinical_tracker_title"))
    st.info(translate(language, "clinical_intro"))
    status_labels = {
        status: trial_status_label(status, language) for status in TRIAL_STATUS_OPTIONS
    }
    status_codes_by_label = {label: status for status, label in status_labels.items()}

    with st.form("clinical-trial-tracker-form"):
        other_terms = st.text_input(
            translate(language, "trial_keywords"),
            placeholder=translate(language, "trial_keywords_placeholder"),
            help=translate(language, "trial_keywords_help"),
            key="trial-other-terms",
        )
        selected_status_labels = st.multiselect(
            translate(language, "trial_statuses"),
            options=list(status_codes_by_label),
            default=[status_labels[status] for status in DEFAULT_TRIAL_STATUSES],
            key="trial-statuses",
        )
        submitted = st.form_submit_button(translate(language, "fetch_trials"))

    if submitted:
        st.session_state.pop("clinical-trial-response", None)
        with st.spinner(translate(language, "fetching_trials")):
            try:
                response = search_clinical_trials(
                    " ".join(other_terms.split()),
                    tuple(status_codes_by_label[label] for label in selected_status_labels),
                )
            except ClinicalTrialsError as exc:
                st.session_state["clinical-trial-error"] = str(exc)
            else:
                st.session_state["clinical-trial-response"] = response
                st.session_state.pop("clinical-trial-error", None)

    error = st.session_state.get("clinical-trial-error")
    if error:
        st.error(translate(language, "trial_registry_unavailable", error=error))
        return

    response = st.session_state.get("clinical-trial-response")
    if not response:
        st.caption(translate(language, "trial_source_note"))
        return

    studies = response.studies
    registered_col, recruiting_col, active_col, completed_col, terminated_col = st.columns(5)
    registered_col.metric(
        translate(language, "registered_studies"),
        f"{(response.total_results or len(studies)):,}",
    )
    recruiting_col.metric(
        translate(language, "recruiting_studies"),
        sum(trial.overall_status == "RECRUITING" for trial in studies),
    )
    active_col.metric(
        translate(language, "active_studies"),
        sum(trial.overall_status == "ACTIVE_NOT_RECRUITING" for trial in studies),
    )
    completed_col.metric(
        translate(language, "completed_studies"),
        sum(trial.overall_status == "COMPLETED" for trial in studies),
    )
    terminated_col.metric(
        translate(language, "terminated_studies"),
        sum(trial.overall_status == "TERMINATED" for trial in studies),
    )
    st.caption(translate(language, "trial_source_note"))

    phase_options, country_options = trial_filter_options(studies)
    phase_col, country_col, limit_col = st.columns(3)
    selected_phases = phase_col.multiselect(
        translate(language, "trial_phase"),
        options=phase_options,
        format_func=lambda value: value.replace("_", " ").title(),
        key="trial-phase-filter",
    )
    selected_countries = country_col.multiselect(
        translate(language, "trial_country"),
        options=country_options,
        key="trial-country-filter",
    )
    max_trials = limit_col.selectbox(
        translate(language, "trials_to_show"),
        options=[10, 25, 50, 100],
        index=1,
        key="trial-result-limit",
    )

    visible = filter_trials(
        studies,
        phases=selected_phases,
        countries=selected_countries,
    )[: int(max_trials)]
    if response.next_page_token:
        st.warning(translate(language, "more_trials_available"))
    if not visible:
        st.info(translate(language, "no_trials"))
        return

    st.download_button(
        translate(language, "download_trials_csv"),
        data=trials_to_csv(visible).encode("utf-8-sig"),
        file_name="hra-clinical-trials.csv",
        mime="text/csv",
        key="download-clinical-trials",
    )
    for trial in visible:
        with st.container(border=True):
            render_trial(trial, language)


def run_knowledge_graph(language: str) -> None:
    st.subheader(translate(language, "knowledge_title"))
    st.info(translate(language, "knowledge_intro"))
    st.caption(translate(language, "knowledge_scope"))

    st.subheader(translate(language, "knowledge_search_section"))
    with st.form("knowledge-map-form"):
        query = st.text_input(
            translate(language, "knowledge_query"),
            value="HTT OR huntingtin OR autophagy OR biomarker",
            help=translate(language, "research_topic_help"),
            key="knowledge-query",
        )
        paper_limit = st.selectbox(
            translate(language, "knowledge_paper_limit"),
            options=[10, 25, 50],
            index=1,
            key="knowledge-paper-limit",
        )
        submitted = st.form_submit_button(translate(language, "knowledge_search"))

    if submitted:
        normalized_query = normalize_user_query(query)
        st.session_state["knowledge-request"] = {
            "query": expand_huntington_query(normalized_query),
            "paper_limit": int(paper_limit),
        }

    request = st.session_state.get("knowledge-request")
    if not request:
        st.write(translate(language, "knowledge_start"))
        return

    with st.spinner(translate(language, "knowledge_loading")):
        try:
            response = search_europe_pmc(
                str(request["query"]),
                "*",
                1,
                int(request["paper_limit"]),
            )
        except EuropePMCError as exc:
            st.error(str(exc))
            return

    research_map = build_research_map(response.papers)
    if not research_map.mentions:
        st.info(translate(language, "knowledge_no_entities"))
        return

    type_labels = {
        "gene": translate(language, "entity_gene"),
        "protein": translate(language, "entity_protein"),
        "pathway": translate(language, "entity_pathway"),
        "compound": translate(language, "entity_compound"),
    }
    st.subheader(translate(language, "knowledge_choose_entity"))
    available_types = [
        entity_type
        for entity_type in type_labels
        if any(entity.entity_type == entity_type for entity in research_map.entities)
    ]
    selected_types = st.multiselect(
        translate(language, "knowledge_entity_types"),
        options=available_types,
        default=available_types,
        format_func=lambda value: type_labels[value],
        key=f"knowledge-entity-types-{language}",
    )
    visible_mentions = [
        mention
        for mention in research_map.mentions
        if mention.entity_type in selected_types
    ]
    visible_entities = {
        mention.entity_id: mention for mention in visible_mentions
    }

    entity_col, paper_col, mention_col = st.columns(3)
    entity_col.metric(translate(language, "knowledge_entities"), len(visible_entities))
    paper_col.metric(
        translate(language, "knowledge_source_papers"),
        len({mention.paper_id for mention in visible_mentions}),
    )
    mention_col.metric(
        translate(language, "knowledge_mentions"),
        len(visible_mentions),
    )

    if not visible_mentions:
        st.info(translate(language, "knowledge_no_filter_results"))
        return

    entity_options = sorted(
        visible_entities,
        key=lambda entity_id: visible_entities[entity_id].entity_name.casefold(),
    )
    selected_entity_id = st.selectbox(
        translate(language, "knowledge_inspect_entity"),
        options=entity_options,
        format_func=lambda entity_id: (
            f"{visible_entities[entity_id].entity_name} "
            f"({type_labels[visible_entities[entity_id].entity_type]})"
        ),
        key=f"knowledge-selected-entity-{language}",
    )
    selected_mentions = [
        mention
        for mention in visible_mentions
        if mention.entity_id == selected_entity_id
    ]

    selected_entity_name = visible_entities[selected_entity_id].entity_name
    st.subheader(
        translate(
            language,
            "knowledge_papers_mentioning",
            entity=selected_entity_name,
        )
    )
    st.caption(translate(language, "knowledge_map_help"))
    st.graphviz_chart(
        graphviz_dot(
            selected_mentions,
            relationship_label=translate(language, "knowledge_relationship"),
            show_relationship_labels=False,
        ),
        width="stretch",
    )
    if len(selected_mentions) > 8:
        st.caption(
            translate(
                language,
                "knowledge_graph_limit",
                shown=8,
                total=len(selected_mentions),
            )
        )

    st.subheader(translate(language, "knowledge_evidence_title"))
    st.caption(translate(language, "knowledge_evidence_help"))
    for mention in selected_mentions:
        if mention.source_url:
            st.markdown(f"**[{mention.paper_title}]({mention.source_url})**")
        else:
            st.markdown(f"**{mention.paper_title}**")
        st.write(f'"{mention.evidence}"')
        st.caption(
            f"{translate(language, 'knowledge_matched_term')}: "
            f"`{mention.matched_alias}` | "
            f"{translate(language, 'knowledge_evidence_location')}: "
            f"{translate(language, f'knowledge_location_{mention.evidence_location}')}"
        )


def main() -> None:
    language_name = st.sidebar.selectbox(
        "Language / Språk",
        options=list(LANGUAGE_OPTIONS),
        key="ui-language",
    )
    language = LANGUAGE_OPTIONS[language_name]
    norwegian_generation_enabled = experimental_norwegian_summaries_enabled()
    if language == "no" and not norwegian_generation_enabled:
        summary_mode = "research"
    else:
        summary_mode = st.sidebar.radio(
            translate(language, "summary_style"),
            options=["plain", "research"],
            index=1 if language == "no" else 0,
            format_func=lambda value: translate(language, f"summary_mode_{value}"),
            horizontal=True,
            key="summary-mode",
        )

    st.title("Huntington Research Assistant")
    st.warning(medical_disclaimer(language))
    st.caption(prohibited_guidance(language))

    summary_config = SummarizationConfig.from_env()
    if language == "no" and not norwegian_generation_enabled:
        summary_available = False
        st.info(translate(language, "norwegian_summary_later"))
    else:
        status = local_llm_status(summary_config, language=language)
        summary_available = status.available
        if status.available:
            st.success(status.message)
        else:
            st.info(status.message)

    if language == "no" and norwegian_generation_enabled:
        st.info(translate(language, "norwegian_summary_experimental"))

    cache = get_cache()

    search_tab, clinical_tab, recent_tab, knowledge_tab = st.tabs(
        [
            translate(language, "search_tab"),
            translate(language, "clinical_tab"),
            translate(language, "recent_tab"),
            translate(language, "knowledge_tab"),
        ]
    )

    with search_tab:
        run_search_panel(
            panel_key="general",
            default_query=DEFAULT_QUERY,
            submit_label=translate(language, "search_europe_pmc"),
            summary_config=summary_config,
            summary_available=summary_available,
            language=language,
            summary_mode=summary_mode,
            cache=cache,
            default_year_start=2015,
        )

    with clinical_tab:
        run_trial_tracker(language)

    with recent_tab:
        run_search_panel(
            panel_key="recent",
            default_query=RECENT_PROGRESS_QUERY,
            submit_label=translate(language, "search_recent"),
            summary_config=summary_config,
            summary_available=summary_available,
            language=language,
            summary_mode=summary_mode,
            cache=cache,
            default_year_start=CURRENT_YEAR - 2,
            intro=translate(language, "recent_intro"),
        )

    with knowledge_tab:
        run_knowledge_graph(language)

    if cache is not None:
        with st.sidebar:
            st.header(translate(language, "recent_searches"))
            for item in safe_recent_searches(cache, limit=5):
                st.caption(item["created_at"])
                st.write(item["query"])


if __name__ == "__main__":
    main()
