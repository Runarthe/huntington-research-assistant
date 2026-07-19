from __future__ import annotations

import sqlite3
import sys
import json
from datetime import date
from math import ceil
from pathlib import Path

import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
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
from hra.clients.pubmed import PubMedClient, PubMedError
from hra.deduplication import deduplicate_papers
from hra.evidence import (
    EvidenceProfile,
    build_evidence_profiles,
    evidence_profiles_to_csv,
)
from hra.export import (
    paper_text_filename,
    paper_to_text,
    papers_to_bibtex,
    papers_to_csv,
    trials_to_csv,
)
from hra.filters import filter_local_reading_state
from hra.i18n import LANGUAGE_OPTIONS, translate
from hra.knowledge_graph import (
    EntityMention,
    build_entity_connections,
    build_research_map,
    graphviz_dot,
)
from hra.models import ClinicalTrial, ClinicalTrialResponse, Paper, SearchResponse
from hra.norwegian_language import SummaryIntegrityError
from hra.query import (
    DEFAULT_QUERY,
    build_dashboard_query,
    build_literature_query,
    build_pubmed_query,
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

from labs.protein_intelligence import (
    DEFAULT_MAX_RESIDUES,
    PROTEIN_TARGETS,
    LocalESM2Config,
    LocalESM2Error,
    LocalESM2Provider,
    ProteinSequenceRecord,
    ProteinTarget,
    SequenceCacheError,
    SequenceRetrievalError,
    BIONEMO_INFERENCE_URL,
    BIONEMO_MODEL_URL,
    build_provider_parity_report,
    compare_embedding_manifests,
    fixture_sequence_record,
    local_esm2_manifest,
    local_esm2_status,
    planned_local_esm2_manifest,
    planned_bionemo_esm2_manifest,
    planned_sequence_manifest,
    read_cached_sequence,
    retrieve_and_cache_uniprot_sequence,
)
from labs.protein_intelligence.entity_mapping import LiteratureEntity, map_entities_to_targets
from labs.protein_intelligence.registry import build_manifest_registry
from labs.protein_intelligence.reports import build_target_report
from labs.protein_intelligence.report_validation import report_summary
from labs.blueprint_experiments.manifests import (
    VALID_PROVIDER_TYPES,
    mock_blueprint_manifest,
    planned_blueprint_manifest,
)
from labs.blueprint_experiments.providers import (
    BlueprintProviderConfig,
    provider_for_config,
)
from labs.blueprint_experiments.registry import (
    build_blueprint_registry,
    registry_payload as blueprint_registry_payload,
)


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
SOURCE_EUROPE_PMC = "Europe PMC"
SOURCE_PUBMED = "PubMed"
SOURCE_OPTIONS = [SOURCE_EUROPE_PMC, SOURCE_PUBMED]
PROTEIN_MANIFEST_DIR = ROOT_DIR / "labs" / "protein_intelligence" / "manifests"
BLUEPRINT_EXAMPLES_DIR = ROOT_DIR / "labs" / "blueprint_experiments" / "examples"


def explanation(language: str, key: str, mode: str) -> str:
    if mode == "simple":
        return translate(language, f"{key}_simple")
    return translate(language, key)


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


@st.cache_data(show_spinner=False, ttl=900)
def search_pubmed(
    query: str,
    page: int,
    page_size: int,
) -> SearchResponse:
    client = PubMedClient()
    return client.search(query, page=page, page_size=page_size)


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


def safe_reading_list_ids(cache: SearchCache | None) -> set[str]:
    if cache is None:
        return set()

    try:
        return cache.reading_list_ids()
    except (OSError, sqlite3.Error) as exc:
        st.warning(f"Reading list is unavailable. Details: {exc}")
        return set()


def safe_reading_list_papers(cache: SearchCache | None) -> list[Paper]:
    if cache is None:
        return []

    try:
        return cache.reading_list_papers()
    except (OSError, sqlite3.Error) as exc:
        st.warning(f"Reading list is unavailable. Details: {exc}")
        return []


def safe_seen_paper_ids(cache: SearchCache | None) -> set[str]:
    if cache is None:
        return set()

    try:
        return cache.seen_paper_ids()
    except (OSError, sqlite3.Error) as exc:
        st.warning(f"Seen-paper history is unavailable. Details: {exc}")
        return set()


def render_paper(
    paper: Paper,
    index: int,
    panel_key: str,
    summary_config: SummarizationConfig,
    summary_available: bool,
    language: str,
    summary_mode: str,
    cache: SearchCache | None,
    reading_list_ids: set[str],
    seen_paper_ids: set[str],
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
    if paper.source_provider != "unknown":
        link_parts.append(f"{translate(language, 'source_provider')}: `{paper.source_provider}`")
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

    action_count = 2 + int(paper.source_url is not None) + int(
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
    paper_export_text = paper_to_text(paper)
    action_columns[action_index].download_button(
        translate(language, "download_paper_details"),
        data=paper_export_text.encode("utf-8"),
        file_name=paper_text_filename(paper),
        mime="text/plain",
        key=f"{panel_key}-download-paper-{paper.id}-{index}",
        use_container_width=True,
    )
    action_index += 1
    paper_is_saved = paper.id in reading_list_ids
    if paper_is_saved:
        if action_columns[action_index].button(
            translate(language, "remove_from_reading_list"),
            key=f"{panel_key}-remove-reading-list-{paper.id}-{index}",
            use_container_width=True,
        ):
            safe_cache_write(cache, "remove_from_reading_list", paper.id)
            st.rerun()
    else:
        if action_columns[action_index].button(
            translate(language, "add_to_reading_list"),
            key=f"{panel_key}-add-reading-list-{paper.id}-{index}",
            disabled=cache is None,
            use_container_width=True,
        ):
            safe_cache_write(cache, "add_to_reading_list", paper)
            st.rerun()

    paper_is_seen = paper.id in seen_paper_ids
    if st.button(
        translate(language, "mark_as_unseen" if paper_is_seen else "mark_as_seen"),
        key=f"{panel_key}-seen-state-{paper.id}-{index}",
        disabled=cache is None,
        use_container_width=True,
    ):
        action = "mark_paper_unseen" if paper_is_seen else "mark_paper_seen"
        safe_cache_write(cache, action, paper.id)
        st.rerun()

    with st.expander(translate(language, "show_export_text")):
        st.code(paper_export_text, language="text")

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
    cache: SearchCache | None,
    reading_list_ids: set[str],
    seen_paper_ids: set[str],
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
                cache,
                reading_list_ids,
                seen_paper_ids,
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
    explanation_mode: str,
    cache: SearchCache | None,
    default_tags: list[str] | None = None,
    default_year_start: int = 2015,
    help_text: str = "Enter a research topic, not personal health information.",
    intro: str | None = None,
) -> None:
    if intro:
        st.info(intro)

    with st.form(f"{panel_key}-form"):
        query = st.text_input(
            translate(language, "research_topic"),
            value=default_query,
            placeholder=translate(language, "research_topic_placeholder"),
            help=explanation(language, "research_topic_help", explanation_mode)
            if help_text
            else None,
            key=f"{panel_key}-query",
        )
        selected_sources = st.multiselect(
            translate(language, "literature_sources"),
            options=SOURCE_OPTIONS,
            default=[SOURCE_EUROPE_PMC],
            help=explanation(language, "literature_sources_help", explanation_mode),
            key=f"{panel_key}-sources",
        )
        selected_tags = st.multiselect(
            translate(language, "category_filters"),
            options=ALL_TAGS,
            default=default_tags or [],
            help=explanation(language, "category_filters_help", explanation_mode),
            key=f"{panel_key}-tags",
        )
        year_range = st.slider(
            translate(language, "publication_year"),
            min_value=MIN_YEAR,
            max_value=CURRENT_YEAR,
            value=(max(MIN_YEAR, default_year_start), CURRENT_YEAR),
            help=explanation(language, "publication_year_help", explanation_mode),
            key=f"{panel_key}-year-range",
        )
        open_access_only = st.checkbox(
            translate(language, "open_access_only"),
            value=False,
            help=explanation(language, "open_access_only_help", explanation_mode),
            key=f"{panel_key}-open-access",
        )
        hide_saved_papers = st.checkbox(
            translate(language, "hide_saved_papers"),
            value=False,
            help=explanation(language, "hide_saved_papers_help", explanation_mode),
            key=f"{panel_key}-hide-saved",
        )
        hide_seen_papers = st.checkbox(
            translate(language, "hide_seen_papers"),
            value=False,
            help=explanation(language, "hide_seen_papers_help", explanation_mode),
            key=f"{panel_key}-hide-seen",
        )
        page_size = st.selectbox(
            translate(language, "results_to_show"),
            options=[10, 25, 50],
            index=0,
            help=explanation(language, "results_to_show_help", explanation_mode),
            key=f"{panel_key}-page-size",
        )
        submitted = st.form_submit_button(submit_label)

    normalized_query = normalize_user_query(query)
    expanded_query = expand_huntington_query(normalized_query)
    with st.expander(translate(language, "expanded_query")):
        st.code(expanded_query)

    if submitted:
        if not selected_sources:
            selected_sources = [SOURCE_EUROPE_PMC]
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
        pubmed_query = build_pubmed_query(
            expanded_query,
            selected_tags=selected_tags,
            year_range=(int(year_range[0]), int(year_range[1])),
            open_access_only=open_access_only,
        )
        st.session_state[f"{panel_key}-request"] = {
            "provider_query": provider_query,
            "pubmed_query": pubmed_query,
            "dashboard_query": dashboard_query,
            "year_range": (int(year_range[0]), int(year_range[1])),
            "page_size": int(page_size),
            "sources": list(selected_sources),
            "hide_saved_papers": bool(hide_saved_papers),
            "hide_seen_papers": bool(hide_seen_papers),
        }
        st.session_state[f"{panel_key}-page"] = 1
        st.session_state[f"{panel_key}-cursor-history"] = ["*"]
        st.session_state[f"{panel_key}-dashboard-pending"] = (
            SOURCE_EUROPE_PMC in selected_sources
        )
        if SOURCE_EUROPE_PMC not in selected_sources:
            st.session_state[f"{panel_key}-dashboard"] = []
            st.session_state.pop(f"{panel_key}-dashboard-error", None)

    request = st.session_state.get(f"{panel_key}-request")
    if not request:
        st.write(translate(language, "start_search"))
        return

    page = int(st.session_state.get(f"{panel_key}-page", 1))
    sources = list(request.get("sources", [SOURCE_EUROPE_PMC]))
    cursor_history = list(
        st.session_state.get(f"{panel_key}-cursor-history", ["*"])
    )
    if SOURCE_EUROPE_PMC in sources and page > len(cursor_history):
        page = len(cursor_history)
        st.session_state[f"{panel_key}-page"] = page
    cursor_mark = cursor_history[min(page - 1, len(cursor_history) - 1)]
    if len(sources) > 1:
        st.info(translate(language, "combined_source_note"))
    if SOURCE_PUBMED in sources:
        with st.expander(translate(language, "pubmed_query")):
            st.code(str(request.get("pubmed_query", "")))

    papers: list[Paper] = []
    total_results = 0
    next_cursor_mark: str | None = None
    with st.spinner(translate(language, "searching")):
        if SOURCE_EUROPE_PMC in sources:
            try:
                europe_response = search_europe_pmc(
                    str(request["provider_query"]),
                    cursor_mark,
                    page,
                    int(request["page_size"]),
                )
            except EuropePMCError as exc:
                st.error(str(exc))
                return
            papers.extend(europe_response.papers)
            total_results += europe_response.total_results or len(europe_response.papers)
            next_cursor_mark = europe_response.next_cursor_mark

        if SOURCE_PUBMED in sources:
            try:
                pubmed_response = search_pubmed(
                    str(request["pubmed_query"]),
                    page,
                    int(request["page_size"]),
                )
            except PubMedError as exc:
                st.error(str(exc))
                return
            papers.extend(pubmed_response.papers)
            total_results += pubmed_response.total_results or len(pubmed_response.papers)

    papers = deduplicate_papers(papers)
    safe_cache_write(cache, "upsert_papers", papers)
    reading_list_ids = safe_reading_list_ids(cache)
    seen_paper_ids = safe_seen_paper_ids(cache)
    papers, locally_hidden_count = filter_local_reading_state(
        papers,
        reading_list_ids=reading_list_ids,
        seen_paper_ids=seen_paper_ids,
        hide_saved=bool(request.get("hide_saved_papers", False)),
        hide_seen=bool(request.get("hide_seen_papers", False)),
    )
    papers = papers[: int(request["page_size"])]
    if next_cursor_mark and len(cursor_history) == page:
        cursor_history.append(next_cursor_mark)
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

    total_results = total_results or len(papers)
    total_pages = max(1, ceil(total_results / int(request["page_size"])))
    st.caption(
        translate(
            language,
            "result_count",
            total=total_results,
            shown=len(papers),
        )
    )
    if locally_hidden_count:
        st.caption(
            translate(language, "local_hidden_papers", count=locally_hidden_count)
        )
    st.info(
        translate(
            language,
            "pagination_help",
            shown=len(papers),
            total=total_results,
        )
    )
    render_pagination(panel_key, page, total_pages, language, position="top")

    st.subheader(translate(language, "publication_dashboard"))
    if SOURCE_EUROPE_PMC not in sources:
        st.caption(translate(language, "dashboard_europe_only"))
    else:
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

    render_paper_exports(papers, panel_key, language)
    st.subheader(translate(language, "papers"))
    render_results(
        papers,
        panel_key,
        summary_config,
        summary_available,
        language,
        summary_mode,
        cache,
        reading_list_ids,
        seen_paper_ids,
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


def run_trial_tracker(language: str, explanation_mode: str) -> None:
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
            help=explanation(language, "trial_keywords_help", explanation_mode),
            key="trial-other-terms",
        )
        selected_status_labels = st.multiselect(
            translate(language, "trial_statuses"),
            options=list(status_codes_by_label),
            default=[status_labels[status] for status in DEFAULT_TRIAL_STATUSES],
            help=explanation(language, "trial_statuses_help", explanation_mode),
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


def run_reading_list(
    *,
    cache: SearchCache | None,
    summary_config: SummarizationConfig,
    summary_available: bool,
    language: str,
    summary_mode: str,
) -> None:
    st.subheader(translate(language, "reading_list_title"))
    st.info(translate(language, "reading_list_intro"))
    if cache is None:
        st.warning(translate(language, "reading_list_unavailable"))
        return

    papers = safe_reading_list_papers(cache)
    if not papers:
        st.caption(translate(language, "reading_list_empty"))
        return

    st.metric(translate(language, "reading_list_count"), len(papers))
    render_paper_exports(papers, "reading-list", language)
    render_results(
        papers,
        "reading-list",
        summary_config,
        summary_available,
        language,
        summary_mode,
        cache,
        {paper.id for paper in papers},
        safe_seen_paper_ids(cache),
    )


def run_evidence_explorer(cache: SearchCache | None, language: str) -> None:
    st.subheader(translate(language, "evidence_title"))
    st.info(translate(language, "evidence_intro"))
    st.caption(translate(language, "evidence_scope"))
    if cache is None:
        st.warning(translate(language, "reading_list_unavailable"))
        return

    papers = safe_reading_list_papers(cache)
    if len(papers) < 2:
        st.warning(translate(language, "evidence_need_two"))
        return

    papers_by_id = {paper.id: paper for paper in papers}

    def paper_label(paper_id: str) -> str:
        paper = papers_by_id[paper_id]
        year = f" ({paper.year})" if paper.year else ""
        return f"{paper.title}{year}"

    selected_ids = st.multiselect(
        translate(language, "evidence_choose_papers"),
        options=list(papers_by_id),
        default=list(papers_by_id)[:2],
        format_func=paper_label,
        max_selections=5,
        help=translate(language, "evidence_choose_help"),
        key="evidence-selected-papers",
    )
    if len(selected_ids) < 2:
        st.warning(translate(language, "evidence_select_two"))
        return

    selected_papers = [papers_by_id[paper_id] for paper_id in selected_ids]
    profiles = build_evidence_profiles(selected_papers)

    def study_design_label(study_design: str) -> str:
        return translate(language, f"evidence_design_{study_design}")

    def context_labels(contexts: list[str]) -> str:
        if not contexts:
            return translate(language, "evidence_context_not_identified")
        return ", ".join(
            translate(language, f"evidence_context_{context}") for context in contexts
        )

    def record_status(profile: EvidenceProfile) -> str:
        if profile.is_retracted:
            return translate(language, "evidence_status_retracted")
        if profile.has_correction:
            return translate(language, "evidence_status_corrected")
        return translate(language, "evidence_status_clear")

    st.subheader(translate(language, "evidence_comparison"))
    st.dataframe(
        [
            {
                translate(language, "evidence_paper"): profile.title,
                translate(language, "year"): profile.year or "-",
                translate(language, "evidence_study_design"): study_design_label(
                    profile.study_design
                ),
                translate(language, "evidence_contexts"): context_labels(
                    profile.research_contexts
                ),
                translate(language, "evidence_source"): profile.source_provider,
                translate(language, "evidence_source_record"): profile.source_url,
                translate(language, "evidence_record_status"): record_status(profile),
            }
            for profile in profiles
        ],
        column_config={
            translate(language, "evidence_source_record"): st.column_config.LinkColumn(
                translate(language, "evidence_source_record"),
                display_text=translate(language, "evidence_open_source"),
            )
        },
        hide_index=True,
        use_container_width=True,
    )
    st.download_button(
        translate(language, "evidence_download_csv"),
        data=evidence_profiles_to_csv(profiles).encode("utf-8-sig"),
        file_name="hra-evidence-comparison.csv",
        mime="text/csv",
        key="evidence-comparison-download",
    )

    st.subheader(translate(language, "evidence_passages"))
    st.caption(translate(language, "evidence_passage_note"))
    for profile in profiles:
        with st.expander(profile.title):
            st.markdown(f"**{translate(language, 'evidence_outcome_passages')}**")
            if profile.outcome_passages:
                for passage in profile.outcome_passages:
                    st.write(passage)
            else:
                st.caption(translate(language, "evidence_no_outcome_passages"))

            st.markdown(f"**{translate(language, 'evidence_limitation_passages')}**")
            if profile.limitation_passages:
                for passage in profile.limitation_passages:
                    st.write(passage)
            else:
                st.caption(translate(language, "evidence_no_limitation_passages"))

            if profile.source_url:
                st.link_button(
                    translate(language, "source_record"),
                    profile.source_url,
                )
            else:
                st.warning(translate(language, "evidence_source_unavailable"))


def run_knowledge_graph(language: str, explanation_mode: str) -> None:
    st.subheader(translate(language, "knowledge_title"))
    st.info(translate(language, "knowledge_intro"))
    st.caption(translate(language, "knowledge_scope"))

    st.subheader(translate(language, "knowledge_search_section"))
    with st.form("knowledge-map-form"):
        query = st.text_input(
            translate(language, "knowledge_query"),
            value="HTT OR huntingtin OR autophagy OR biomarker",
            help=explanation(language, "research_topic_help", explanation_mode),
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
        "biomarker": translate(language, "entity_biomarker"),
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
        help=explanation(language, "knowledge_entity_types_help", explanation_mode),
        key=f"knowledge-entity-types-{language}",
    )
    visible_mentions = [
        mention
        for mention in research_map.mentions
        if mention.entity_type in selected_types
    ]
    entity_catalog = {entity.id: entity for entity in research_map.entities}
    visible_entities = {
        mention.entity_id: entity_catalog[mention.entity_id]
        for mention in visible_mentions
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
        key=lambda entity_id: visible_entities[entity_id].name.casefold(),
    )
    selected_entity_id = st.selectbox(
        translate(language, "knowledge_inspect_entity"),
        options=entity_options,
        format_func=lambda entity_id: (
            f"{visible_entities[entity_id].name} "
            f"({type_labels[visible_entities[entity_id].entity_type]})"
        ),
        key=f"knowledge-selected-entity-{language}",
    )
    selected_mentions = [
        mention
        for mention in visible_mentions
        if mention.entity_id == selected_entity_id
    ]

    selected_entity = visible_entities[selected_entity_id]
    selected_entity_name = selected_entity.name
    st.caption(
        f"{translate(language, 'knowledge_catalog_id')}: `{selected_entity.id}` | "
        f"{translate(language, 'knowledge_catalog_version')}: "
        f"`{research_map.catalog_version}`"
    )
    st.caption(
        f"{translate(language, 'knowledge_aliases')}: "
        f"{', '.join(selected_entity.aliases)}"
    )

    st.subheader(translate(language, "knowledge_related_title"))
    st.caption(translate(language, "knowledge_related_help"))
    related_entities = [
        connection
        for connection in build_entity_connections(research_map, selected_entity_id)
        if connection.entity_type in selected_types
    ]
    if related_entities:
        st.dataframe(
            [
                {
                    translate(language, "knowledge_related_entity"): connection.entity_name,
                    translate(language, "knowledge_entity_type"): type_labels[
                        connection.entity_type
                    ],
                    translate(language, "knowledge_shared_papers"): (
                        connection.shared_paper_count
                    ),
                }
                for connection in related_entities
            ],
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.info(translate(language, "knowledge_related_none"))

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
            f"{translate(language, f'knowledge_location_{mention.evidence_location}')} | "
            f"{translate(language, 'knowledge_extraction_method')}: "
            f"{translate(language, f'knowledge_method_{mention.extraction_method}')} | "
            f"{translate(language, 'knowledge_confidence')}: "
            f"{translate(language, f'knowledge_confidence_{mention.mention_confidence}')}"
        )


def _parity_value(value: object, language: str) -> str:
    if value is None:
        return translate(language, "parity_not_recorded")
    if isinstance(value, dict):
        provider = value.get("provider") or translate(language, "parity_not_recorded")
        name = value.get("name") or translate(language, "parity_not_recorded")
        version = value.get("version") or translate(language, "parity_not_recorded")
        return f"{provider} | {name} | {version}"
    if isinstance(value, (list, tuple)):
        return " - ".join(str(item) for item in value)
    if isinstance(value, bool):
        return translate(language, "yes" if value else "no")
    return str(value)


def _render_provider_parity_experiment(
    language: str,
    record: ProteinSequenceRecord,
    config: LocalESM2Config,
    reference_manifest: dict[str, object],
) -> None:
    st.subheader(translate(language, "parity_lab_title"))
    st.info(translate(language, "parity_lab_intro"))
    st.caption(translate(language, "parity_lab_scope"))

    bionemo_plan = planned_bionemo_esm2_manifest(record, config)
    report = build_provider_parity_report(reference_manifest, bionemo_plan)
    report_payload = report.model_dump(mode="json")

    input_col, execution_col, unknown_col = st.columns(3)
    input_col.metric(
        translate(language, "parity_input_contract"),
        translate(
            language,
            "yes" if report.readiness["input_contract_ready"] else "no",
        ),
    )
    execution_col.metric(
        translate(language, "parity_bionemo_execution"),
        translate(language, "parity_planned_only"),
    )
    unknown_col.metric(
        translate(language, "parity_unresolved_checks"),
        report.summary["not-available"] + report.summary["not-comparable"],
    )

    rows = [
        {
            translate(language, "parity_check"): translate(
                language,
                f"parity_field_{check.field}",
            ),
            translate(language, "parity_result"): translate(
                language,
                f"parity_status_{check.status.replace('-', '_')}",
            ),
            translate(language, "parity_local_reference"): _parity_value(
                check.reference,
                language,
            ),
            translate(language, "parity_bionemo_candidate"): _parity_value(
                check.candidate,
                language,
            ),
            translate(language, "parity_meaning"): translate(
                language,
                f"parity_meaning_{check.field}",
            ),
        }
        for check in report.checks
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)
    st.caption(translate(language, "parity_sources"))
    st.markdown(
        f"[{translate(language, 'parity_bionemo_model_docs')}]({BIONEMO_MODEL_URL}) | "
        f"[{translate(language, 'parity_bionemo_inference_docs')}]({BIONEMO_INFERENCE_URL})"
    )

    with st.expander(translate(language, "parity_bionemo_plan_title")):
        st.json(bionemo_plan, expanded=False)
    with st.expander(translate(language, "parity_report_title")):
        st.json(report_payload, expanded=False)
    plan_col, report_col = st.columns(2)
    plan_col.download_button(
        translate(language, "parity_download_bionemo_plan"),
        data=json.dumps(bionemo_plan, indent=2, sort_keys=True).encode("utf-8"),
        file_name=f"hra-bionemo-plan-{record.target.symbol.lower()}.json",
        mime="application/json",
        key=f"parity-plan-download-{bionemo_plan['experiment_id']}",
        use_container_width=True,
    )
    report_col.download_button(
        translate(language, "parity_download_report"),
        data=json.dumps(report_payload, indent=2, sort_keys=True).encode("utf-8"),
        file_name=f"hra-provider-parity-{record.target.symbol.lower()}.json",
        mime="application/json",
        key=f"parity-report-download-{bionemo_plan['experiment_id']}",
        use_container_width=True,
    )


def _render_local_esm2_experiment(
    language: str,
    selected_target: ProteinTarget,
    explanation_mode: str,
) -> None:
    st.subheader(translate(language, "esm2_lab_title"))
    st.info(translate(language, "esm2_lab_intro"))
    st.caption(translate(language, "esm2_lab_scope"))

    input_source = st.radio(
        translate(language, "esm2_input_source"),
        options=["fixture", "uniprot_cache"],
        format_func=lambda value: translate(language, f"esm2_input_{value}"),
        horizontal=True,
        help=explanation(language, "esm2_input_source_help", explanation_mode),
        key=f"esm2-input-source-{language}-{selected_target.symbol}",
    )

    record = None
    if input_source == "fixture":
        try:
            record = fixture_sequence_record(selected_target)
        except SequenceCacheError as exc:
            st.error(str(exc))
    else:
        try:
            record = read_cached_sequence(selected_target)
        except SequenceCacheError as exc:
            st.error(str(exc))
        if st.button(
            translate(language, "esm2_retrieve_uniprot"),
            key=f"esm2-retrieve-{selected_target.symbol}",
        ):
            try:
                with st.spinner(translate(language, "esm2_retrieving")):
                    record = retrieve_and_cache_uniprot_sequence(selected_target)
                st.success(translate(language, "esm2_retrieved"))
            except (SequenceRetrievalError, OSError) as exc:
                st.error(translate(language, "esm2_retrieval_failed", error=str(exc)))
        if record is None:
            st.warning(translate(language, "esm2_no_cached_sequence"))

    if record is None:
        return

    source_label = translate(language, f"esm2_input_{input_source}")
    length_col, checksum_col, source_col = st.columns(3)
    length_col.metric(translate(language, "esm2_sequence_length"), record.sequence_length)
    checksum_col.metric(translate(language, "esm2_sequence_checksum"), record.checksum[7:19])
    source_col.metric(translate(language, "esm2_sequence_source"), source_label)
    st.caption(
        translate(
            language,
            "esm2_sequence_details",
            accession=record.accession,
            date=record.retrieved_at.isoformat(),
        )
    )

    max_length = min(DEFAULT_MAX_RESIDUES, record.sequence_length)
    if record.sequence_length > DEFAULT_MAX_RESIDUES:
        st.warning(
            translate(
                language,
                "esm2_window_required",
                length=record.sequence_length,
                limit=DEFAULT_MAX_RESIDUES,
            )
        )
    window_col, size_col = st.columns(2)
    window_start = int(
        window_col.number_input(
            translate(language, "esm2_window_start"),
            min_value=1,
            max_value=record.sequence_length,
            value=1,
            step=1,
            help=explanation(language, "esm2_window_start_help", explanation_mode),
            key=f"esm2-window-start-{selected_target.symbol}-{input_source}",
        )
    )
    remaining = record.sequence_length - window_start + 1
    window_length = int(
        size_col.number_input(
            translate(language, "esm2_window_length"),
            min_value=1,
            max_value=min(DEFAULT_MAX_RESIDUES, remaining),
            value=min(max_length, remaining),
            step=1,
            help=explanation(language, "esm2_window_length_help", explanation_mode),
            key=f"esm2-window-length-{selected_target.symbol}-{input_source}",
        )
    )
    device = st.segmented_control(
        translate(language, "esm2_device"),
        options=["auto", "cpu", "cuda"],
        default="auto",
        format_func=lambda value: translate(language, f"esm2_device_{value}"),
        help=explanation(language, "esm2_device_help", explanation_mode),
        key=f"esm2-device-{selected_target.symbol}",
    ) or "auto"
    cached_model_only = st.checkbox(
        translate(language, "esm2_cached_model_only"),
        value=False,
        help=explanation(language, "esm2_cached_model_only_help", explanation_mode),
        key=f"esm2-cache-only-{selected_target.symbol}",
    )

    config = LocalESM2Config(
        window_start=window_start,
        window_length=window_length,
        device=device,
        local_files_only=cached_model_only,
    )
    plan = planned_local_esm2_manifest(record, config)
    with st.expander(translate(language, "esm2_plan_title")):
        st.json(plan, expanded=False)
    st.download_button(
        translate(language, "esm2_download_plan"),
        data=json.dumps(plan, indent=2, sort_keys=True).encode("utf-8"),
        file_name=f"hra-esm2-plan-{selected_target.symbol.lower()}.json",
        mime="application/json",
        key=f"esm2-plan-download-{selected_target.symbol}-{input_source}",
    )

    status = local_esm2_status()
    if status.available:
        versions = ", ".join(
            f"{name} {package_version}"
            for name, package_version in status.installed_versions.items()
        )
        st.success(translate(language, "esm2_runtime_ready"))
        st.caption(versions)
    else:
        st.warning(
            translate(
                language,
                "esm2_runtime_missing",
                packages=", ".join(status.missing_packages),
            )
        )
        st.code('python -m pip install -e ".[scientific-ai]"', language="powershell")

    confirmed = st.checkbox(
        translate(language, "esm2_run_confirmation"),
        value=False,
        key=f"esm2-confirm-{selected_target.symbol}",
    )
    experiment_id = str(plan["experiment_id"])
    artifacts = st.session_state.setdefault("local-esm2-artifacts", {})
    if st.button(
        translate(language, "esm2_run"),
        disabled=not status.available or not confirmed,
        key=f"esm2-run-{selected_target.symbol}-{input_source}",
    ):
        try:
            with st.spinner(translate(language, "esm2_running")):
                artifact = LocalESM2Provider(config).embed(record)
                manifest = local_esm2_manifest(artifact)
            previous = artifacts.get(experiment_id)
            comparison = (
                compare_embedding_manifests(previous, manifest)
                if previous is not None
                else "baseline-recorded"
            )
            manifest["evaluation"]["reproducibility_check"] = {
                "status": comparison,
                "compared_checksum": (
                    previous["outputs"]["embedding"]["checksum"]
                    if previous is not None
                    else None
                ),
            }
            artifacts[experiment_id] = manifest
            st.success(translate(language, "esm2_run_complete"))
        except (LocalESM2Error, OSError, ValueError) as exc:
            st.error(translate(language, "esm2_run_failed", error=str(exc)))

    manifest = artifacts.get(experiment_id)
    if manifest is not None:
        embedding = manifest["outputs"]["embedding"]
        reproducibility = manifest["evaluation"]["reproducibility_check"]["status"]
        dimensions_col, tensor_col, repeat_col = st.columns(3)
        dimensions_col.metric(translate(language, "esm2_dimensions"), embedding["dimensions"])
        tensor_col.metric(
            translate(language, "esm2_tensor_shape"),
            " x ".join(str(value) for value in embedding["token_embeddings_shape"]),
        )
        repeat_col.metric(
            translate(language, "esm2_repeat_status"),
            translate(language, f"esm2_repeat_{reproducibility.replace('-', '_')}"),
        )
        st.caption(translate(language, "esm2_artifact_warning"))
        with st.expander(translate(language, "esm2_artifact_title")):
            st.json(manifest, expanded=False)
        st.download_button(
            translate(language, "esm2_download_artifact"),
            data=json.dumps(manifest, indent=2, sort_keys=True).encode("utf-8"),
            file_name=f"hra-esm2-artifact-{selected_target.symbol.lower()}.json",
            mime="application/json",
            key=f"esm2-artifact-download-{experiment_id}",
        )

    _render_provider_parity_experiment(
        language,
        record,
        config,
        manifest or plan,
    )


def run_protein_lab(
    language: str,
    cache: SearchCache | None,
    explanation_mode: str,
) -> None:
    st.subheader(translate(language, "protein_lab_title"))
    st.info(translate(language, "protein_lab_intro"))
    st.caption(translate(language, "protein_lab_scope"))

    target_rows = [
        {
            translate(language, "protein_lab_symbol"): target.symbol,
            translate(language, "protein_lab_name"): target.name,
            translate(language, "protein_lab_entity_id"): target.entity_id,
            "UniProt": target.identifiers["uniprot"],
            "HGNC": target.identifiers["hgnc"],
            "NCBI Gene": target.identifiers["ncbi_gene"],
            translate(language, "protein_lab_source"): target.uniprot_url,
        }
        for target in PROTEIN_TARGETS
    ]
    st.dataframe(
        target_rows,
        column_config={
            translate(language, "protein_lab_source"): st.column_config.LinkColumn(
                translate(language, "protein_lab_source"),
                display_text="UniProt",
            )
        },
        hide_index=True,
        use_container_width=True,
    )

    selected_symbol = st.selectbox(
        translate(language, "protein_lab_choose_target"),
        options=[target.symbol for target in PROTEIN_TARGETS],
        help=explanation(language, "protein_lab_choose_target_help", explanation_mode),
        key=f"protein-lab-target-{language}",
    )
    selected_target = next(
        target for target in PROTEIN_TARGETS if target.symbol == selected_symbol
    )

    id_col, uniprot_col, hgnc_col, ncbi_col = st.columns(4)
    id_col.metric(
        translate(language, "protein_lab_entity_id"),
        selected_target.entity_id,
    )
    uniprot_col.metric("UniProt", selected_target.identifiers["uniprot"])
    hgnc_col.metric("HGNC", selected_target.identifiers["hgnc"])
    ncbi_col.metric("NCBI Gene", selected_target.identifiers["ncbi_gene"])
    st.caption(selected_target.notes)
    st.link_button(
        translate(language, "protein_lab_open_uniprot"),
        selected_target.uniprot_url,
    )

    report_source = st.radio(
        translate(language, "protein_lab_report_source"),
        options=["catalogue", "reading_list"],
        format_func=lambda value: translate(
            language,
            f"protein_lab_report_source_{value}",
        ),
        horizontal=True,
        help=explanation(language, "protein_lab_report_source_help", explanation_mode),
        key=f"protein-lab-report-source-{language}",
    )

    entities, source_records, source_note = _protein_lab_report_inputs(
        report_source,
        selected_target.symbol,
        cache,
        language,
    )
    if source_note:
        st.caption(source_note)

    manifest_records = build_manifest_registry((PROTEIN_MANIFEST_DIR,))
    report = build_target_report(
        selected_target.symbol,
        entities=entities,
        manifest_records=manifest_records,
        source_records=source_records,
    )
    summary = report_summary(report)
    interpretation = report["interpretation"]

    report_col, manifest_col, status_col = st.columns(3)
    report_col.metric(
        translate(language, "protein_lab_mapped_entities"),
        summary["mapped_entity_count"],
    )
    manifest_col.metric(
        translate(language, "protein_lab_manifests"),
        summary["manifest_count"],
    )
    status_col.metric(
        translate(language, "protein_lab_report_status"),
        str(summary["interpretation_status"]),
    )
    st.caption(str(interpretation["claim_boundary"]))

    with st.expander(translate(language, "protein_lab_planned_manifest")):
        st.json(planned_sequence_manifest(selected_target), expanded=False)

    with st.expander(translate(language, "protein_lab_target_report")):
        st.json(report, expanded=False)

    st.download_button(
        translate(language, "protein_lab_download_report"),
        data=json.dumps(report, indent=2, sort_keys=True).encode("utf-8"),
        file_name=f"hra-protein-report-{selected_target.symbol.lower()}.json",
        mime="application/json",
        key=f"protein-lab-report-download-{selected_target.symbol}",
    )

    st.divider()
    _render_local_esm2_experiment(language, selected_target, explanation_mode)

    if source_records:
        st.subheader(translate(language, "protein_lab_source_papers"))
        st.caption(translate(language, "protein_lab_source_papers_help"))
        st.dataframe(
            [
                {
                    translate(language, "evidence_paper"): record["title"],
                    translate(language, "year"): record["year"] or "-",
                    translate(language, "knowledge_matched_term"): ", ".join(
                        record["matched_terms"]
                    ),
                    translate(language, "source_record"): record["source_url"],
                }
                for record in source_records
            ],
            column_config={
                translate(language, "source_record"): st.column_config.LinkColumn(
                    translate(language, "source_record"),
                    display_text=translate(language, "evidence_open_source"),
                )
            },
            hide_index=True,
            use_container_width=True,
        )

    st.subheader(translate(language, "protein_lab_cli_title"))
    st.caption(translate(language, "protein_lab_cli_help"))
    st.code(
        "\n".join(
            [
                "python -m labs.protein_intelligence list-targets",
                f"python -m labs.protein_intelligence plan {selected_target.symbol}",
                (
                    "python -m labs.protein_intelligence.report_cli "
                    f"target-report {selected_target.symbol} "
                    "--entities labs/protein_intelligence/examples/entities.json "
                    "--manifest-path labs/protein_intelligence/manifests "
                    "--summary"
                ),
            ]
        ),
        language="powershell",
    )

    st.divider()
    _render_blueprint_lab_preview(language, explanation_mode)


def _blueprint_provider_status_key(metadata: dict[str, object]) -> str:
    provider_type = metadata["provider_type"]
    if metadata["live_enabled"]:
        return "blueprint_lab_provider_live_ready"
    if provider_type == "mock":
        return "blueprint_lab_provider_mock_fixture"
    if provider_type == "uniprot":
        return "blueprint_lab_provider_public_data_gated"
    return "blueprint_lab_provider_planned_only"


def _blueprint_available_execution_modes(provider_type: str) -> tuple[str, ...]:
    """Return only the execution modes that this UI can safely perform."""

    if provider_type == "mock":
        return ("offline",)
    return ("planned",)


def _blueprint_cli_commands(
    provider_type: str,
    execution_mode: str,
    target_symbol: str,
) -> tuple[str, ...]:
    commands = [
        "python -m labs.blueprint_experiments list-providers",
        (
            "python -m labs.blueprint_experiments "
            f"describe-provider {provider_type}"
        ),
        (
            "python -m labs.blueprint_experiments "
            f"provider-config {provider_type} --execution-mode {execution_mode}"
        ),
        (
            "python -m labs.blueprint_experiments "
            f"plan {target_symbol} --provider-type {provider_type}"
        ),
    ]
    if provider_type == "mock":
        commands.append(
            "python -m labs.blueprint_experiments "
            f"run-mock {target_symbol} --points 8"
        )
    commands.append(
        "python -m labs.blueprint_experiments "
        "index-manifests labs/blueprint_experiments/examples"
    )
    return tuple(commands)


def _render_blueprint_registry(language: str) -> dict[str, object]:
    st.subheader(translate(language, "blueprint_lab_registry_title"))
    st.caption(translate(language, "blueprint_lab_registry_help"))

    registry = blueprint_registry_payload(
        build_blueprint_registry((BLUEPRINT_EXAMPLES_DIR,))
    )
    count_col, valid_col, invalid_col = st.columns(3)
    count_col.metric(
        translate(language, "blueprint_lab_registry_records"),
        registry["record_count"],
    )
    valid_col.metric(
        translate(language, "blueprint_lab_registry_valid"),
        registry["valid_count"],
    )
    invalid_col.metric(
        translate(language, "blueprint_lab_registry_invalid"),
        registry["invalid_count"],
    )
    st.caption(registry["safety"]["claim_boundary"])

    records = registry["records"]
    if records:
        st.dataframe(
            [
                {
                    translate(language, "blueprint_lab_experiment_id"): record[
                        "experiment_id"
                    ],
                    translate(language, "blueprint_lab_provider"): translate(
                        language,
                        f"blueprint_provider_{record['provider_type']}",
                    )
                    if record["provider_type"] in VALID_PROVIDER_TYPES
                    else record["provider_type"],
                    translate(language, "blueprint_lab_status"): record["status"],
                    translate(language, "blueprint_lab_targets"): ", ".join(
                        record["target_symbols"]
                    ),
                    translate(language, "blueprint_lab_artifact_type"): record[
                        "artifact_type"
                    ]
                    or "-",
                    translate(language, "blueprint_lab_valid"): record["valid"],
                    translate(language, "blueprint_lab_checksum"): record["checksum"][
                        :12
                    ],
                }
                for record in records
            ],
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.info(translate(language, "blueprint_lab_no_registry_records"))
    return registry


def _render_blueprint_lab_preview(language: str, explanation_mode: str) -> None:
    st.subheader(translate(language, "blueprint_lab_title"))
    st.info(translate(language, "blueprint_lab_intro"))
    st.caption(translate(language, "blueprint_lab_scope"))

    st.markdown(f"**{translate(language, 'blueprint_lab_workflow_title')}**")
    workflow_columns = st.columns(4)
    for column, key in zip(
        workflow_columns,
        (
            "blueprint_lab_workflow_target",
            "blueprint_lab_workflow_provider",
            "blueprint_lab_workflow_manifest",
            "blueprint_lab_workflow_provenance",
        ),
        strict=True,
    ):
        column.caption(translate(language, key))

    provider_options = sorted(VALID_PROVIDER_TYPES)
    selected_provider = st.selectbox(
        translate(language, "blueprint_lab_provider"),
        options=provider_options,
        index=provider_options.index("mock"),
        format_func=lambda value: translate(language, f"blueprint_provider_{value}"),
        help=explanation(language, "blueprint_lab_provider_help", explanation_mode),
        key=f"blueprint-lab-provider-{language}",
    )
    mode_options = _blueprint_available_execution_modes(selected_provider)
    selected_mode = st.selectbox(
        translate(language, "blueprint_lab_execution_mode"),
        options=mode_options,
        index=0,
        format_func=lambda value: translate(language, f"blueprint_mode_{value}"),
        help=explanation(language, "blueprint_lab_execution_mode_help", explanation_mode),
        key=f"blueprint-lab-mode-{language}-{selected_provider}",
    )
    selected_symbol = st.selectbox(
        translate(language, "blueprint_lab_target"),
        options=[target.symbol for target in PROTEIN_TARGETS],
        help=explanation(language, "blueprint_lab_target_help", explanation_mode),
        key=f"blueprint-lab-target-{language}",
    )

    try:
        selected_config = BlueprintProviderConfig(
            provider_type=selected_provider,
            execution_mode=selected_mode,
        )
        selected_metadata = provider_for_config(selected_config).describe().as_dict()
    except ValueError as exc:
        selected_metadata = None
        st.warning(str(exc))

    if selected_metadata is not None:
        metadata_col, implemented_col, live_col = st.columns(3)
        status_key = _blueprint_provider_status_key(selected_metadata)
        metadata_col.metric(
            translate(language, "blueprint_lab_provider_status"),
            translate(language, status_key),
        )
        implemented_col.metric(
            translate(language, "blueprint_lab_implemented"),
            translate(
                language,
                "yes" if selected_metadata["implemented"] else "no",
            ),
        )
        live_col.metric(
            translate(language, "blueprint_lab_live_enabled"),
            translate(
                language,
                "yes" if selected_metadata["live_enabled"] else "no",
            ),
        )
        st.info(translate(language, f"{status_key}_detail"))
        st.caption(selected_metadata["claim_boundary"])

    planned_manifest = planned_blueprint_manifest(
        selected_symbol,
        provider_type=selected_provider,
    )

    with st.expander(translate(language, "blueprint_lab_planned_manifest")):
        st.caption(translate(language, "blueprint_lab_planned_manifest_help"))
        st.json(planned_manifest, expanded=False)

    artifact_columns = st.columns(2 if selected_provider == "mock" else 1)
    artifact_columns[0].download_button(
        translate(language, "blueprint_lab_download_plan"),
        data=json.dumps(planned_manifest, indent=2, sort_keys=True).encode("utf-8"),
        file_name=(
            f"hra-blueprint-plan-{selected_provider}-{selected_symbol.lower()}.json"
        ),
        mime="application/json",
        key=f"blueprint-lab-plan-download-{selected_provider}-{selected_symbol}",
    )

    if selected_provider == "mock":
        mock_manifest = mock_blueprint_manifest(selected_symbol)
        with st.expander(translate(language, "blueprint_lab_mock_manifest")):
            st.caption(translate(language, "blueprint_lab_mock_manifest_help"))
            st.json(mock_manifest, expanded=False)
        artifact_columns[1].download_button(
            translate(language, "blueprint_lab_download_mock"),
            data=json.dumps(mock_manifest, indent=2, sort_keys=True).encode("utf-8"),
            file_name=f"hra-blueprint-mock-{selected_symbol.lower()}.json",
            mime="application/json",
            key=f"blueprint-lab-mock-download-{selected_symbol}",
        )

    registry = _render_blueprint_registry(language)
    st.download_button(
        translate(language, "blueprint_lab_download_registry"),
        data=json.dumps(registry, indent=2, sort_keys=True).encode("utf-8"),
        file_name="hra-blueprint-registry.json",
        mime="application/json",
        key="blueprint-lab-registry-download",
    )

    st.subheader(translate(language, "blueprint_lab_cli_title"))
    st.caption(translate(language, "blueprint_lab_cli_help"))
    st.code(
        "\n".join(
            _blueprint_cli_commands(
                selected_provider,
                selected_mode,
                selected_symbol,
            )
        ),
        language="powershell",
    )


def _protein_lab_entities() -> tuple[LiteratureEntity, ...]:
    return tuple(
        LiteratureEntity(
            entity_id=target.entity_id,
            label=target.name,
            aliases=(target.symbol,),
            entity_type="protein",
        )
        for target in PROTEIN_TARGETS
    )


def _protein_lab_report_inputs(
    report_source: str,
    selected_symbol: str,
    cache: SearchCache | None,
    language: str,
) -> tuple[tuple[LiteratureEntity, ...], tuple[dict[str, object], ...], str | None]:
    if report_source != "reading_list":
        return _protein_lab_entities(), (), None

    if cache is None:
        return (
            _protein_lab_entities(),
            (),
            translate(language, "protein_lab_reading_list_unavailable"),
        )

    papers = safe_reading_list_papers(cache)
    if not papers:
        return (
            _protein_lab_entities(),
            (),
            translate(language, "protein_lab_no_reading_list_papers"),
        )

    research_map = build_research_map(papers)
    entities = tuple(
        LiteratureEntity(
            entity_id=entity.id,
            label=entity.name,
            aliases=tuple(entity.aliases),
            entity_type=entity.entity_type,
        )
        for entity in research_map.entities
    )
    mappings = map_entities_to_targets(entities)
    mapped_entity_ids = {
        mapping.entity.entity_id
        for mapping in mappings
        if mapping.target.symbol == selected_symbol
    }
    source_records = _protein_lab_source_records(
        research_map.mentions,
        mapped_entity_ids,
        {paper.id: paper.year for paper in papers},
    )
    note = (
        translate(
            language,
            "protein_lab_using_reading_list",
            count=len(source_records),
            symbol=selected_symbol,
        )
    )
    if not source_records:
        note = translate(
            language,
            "protein_lab_no_target_mentions",
        )
    return entities or _protein_lab_entities(), source_records, note


def _protein_lab_source_records(
    mentions: list[EntityMention],
    mapped_entity_ids: set[str],
    years_by_paper_id: dict[str, int | None],
) -> tuple[dict[str, object], ...]:
    records_by_paper: dict[str, dict[str, object]] = {}
    for mention in mentions:
        if mention.entity_id not in mapped_entity_ids:
            continue
        record = records_by_paper.setdefault(
            mention.paper_id,
            {
                "id": mention.paper_id,
                "title": mention.paper_title,
                "year": years_by_paper_id.get(mention.paper_id),
                "source_url": mention.source_url,
                "matched_terms": [],
                "evidence_passages": [],
            },
        )
        if mention.matched_alias not in record["matched_terms"]:
            record["matched_terms"].append(mention.matched_alias)
        if mention.evidence not in record["evidence_passages"]:
            record["evidence_passages"].append(mention.evidence)
    return tuple(records_by_paper.values())


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
    explanation_mode = st.sidebar.radio(
        translate(language, "explanation_style"),
        options=["simple", "detailed"],
        index=0,
        format_func=lambda value: translate(language, f"explanation_mode_{value}"),
        horizontal=True,
        key="explanation-mode",
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

    (
        search_tab,
        reading_list_tab,
        evidence_tab,
        protein_lab_tab,
        clinical_tab,
        recent_tab,
        knowledge_tab,
    ) = st.tabs(
        [
            translate(language, "search_tab"),
            translate(language, "reading_list_tab"),
            translate(language, "evidence_tab"),
            translate(language, "protein_lab_tab"),
            translate(language, "clinical_tab"),
            translate(language, "recent_tab"),
            translate(language, "knowledge_tab"),
        ]
    )

    with search_tab:
        run_search_panel(
            panel_key="general",
            default_query=DEFAULT_QUERY,
            submit_label=translate(language, "search_literature"),
            summary_config=summary_config,
            summary_available=summary_available,
            language=language,
            summary_mode=summary_mode,
            explanation_mode=explanation_mode,
            cache=cache,
            default_year_start=2015,
            intro=explanation(language, "search_tab_intro", explanation_mode),
        )

    with clinical_tab:
        run_trial_tracker(language, explanation_mode)

    with reading_list_tab:
        run_reading_list(
            cache=cache,
            summary_config=summary_config,
            summary_available=summary_available,
            language=language,
            summary_mode=summary_mode,
        )

    with evidence_tab:
        run_evidence_explorer(cache, language)

    with protein_lab_tab:
        run_protein_lab(language, cache, explanation_mode)

    with recent_tab:
        run_search_panel(
            panel_key="recent",
            default_query=RECENT_PROGRESS_QUERY,
            submit_label=translate(language, "search_recent"),
            summary_config=summary_config,
            summary_available=summary_available,
            language=language,
            summary_mode=summary_mode,
            explanation_mode=explanation_mode,
            cache=cache,
            default_year_start=CURRENT_YEAR - 2,
            intro=explanation(language, "recent_intro", explanation_mode),
        )

    with knowledge_tab:
        run_knowledge_graph(language, explanation_mode)

    if cache is not None:
        with st.sidebar:
            st.header(translate(language, "recent_searches"))
            for item in safe_recent_searches(cache, limit=5):
                st.caption(item["created_at"])
                st.write(item["query"])


if __name__ == "__main__":
    main()
