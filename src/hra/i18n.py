from __future__ import annotations

LANGUAGE_OPTIONS = {"English": "en", "Norsk": "no"}

TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        "summary_style": "Summary style",
        "summary_mode_plain": "Plain language",
        "summary_mode_research": "Research detail",
        "search_tab": "Search",
        "clinical_tab": "Trial tracker",
        "recent_tab": "Recent publications",
        "research_topic": "Research topic",
        "research_topic_placeholder": "gene silencing, biomarkers, clinical trials...",
        "research_topic_help": "Enter a research topic, not personal health information.",
        "category_filters": "Category filters",
        "publication_year": "Publication year",
        "open_access_only": "Open access only",
        "results_to_show": "Articles per page",
        "search_europe_pmc": "Search Europe PMC",
        "search_trials": "Search clinical trial literature",
        "search_recent": "Search recent publications",
        "expanded_query": "Expanded query",
        "searching": "Searching Europe PMC...",
        "loading_dashboard": "Calculating publication trend...",
        "start_search": "Enter a topic and search Europe PMC to begin.",
        "timeline": "Timeline",
        "publication_dashboard": "Publication dashboard",
        "this_year": "Published this year (to date)",
        "period_total": "Published in selected period",
        "peak_year": "Peak publication year",
        "yearly_trend": "Publications per year",
        "dashboard_note": (
            "Dashboard counts use all matching Europe PMC records for the selected "
            "years and API-compatible filters, not only the paper cards below."
        ),
        "dashboard_unavailable": "Publication dashboard is unavailable: {error}",
        "paper_batch_count": (
            "Showing {shown} paper cards after local filters. "
            "The dashboard above is calculated separately from all matching records."
        ),
        "page_status": "Page {page} of {total_pages}",
        "pagination_help": "Showing {shown} articles on this page. Use the controls to browse all {total:,} matches.",
        "previous_page": "Previous page",
        "next_page": "Next page",
        "download_csv": "Download this page as CSV",
        "download_bibtex": "Download this page as BibTeX",
        "current_page_export_note": "Exports include the papers shown on this page and their source links.",
        "papers": "Papers",
        "no_papers": "No papers found. Try a broader topic or fewer keywords.",
        "no_timeline": "No publication years available for a timeline.",
        "result_count": (
            "Europe PMC matched approximately {total:,} records. "
            "Showing {shown} papers on this page."
        ),
        "source_record": "Open Europe PMC source record",
        "open_access_pdf": "Open full-text PDF",
        "download_paper_details": "Download details and abstract",
        "abstract": "Abstract",
        "no_abstract": "No abstract available.",
        "summarize": "Summarize abstract",
        "summarizing": "Summarizing locally with {model}...",
        "summary_failed": "Summary failed: {error}",
        "plain_summary": "Plain-language summary",
        "research_summary": "Research-detail summary",
        "norwegian_summary_later": (
            "Norwegian translation of abstracts and summaries is coming in a later update."
        ),
        "citations": "Citations",
        "open_access": "Open access",
        "publication_types": "Publication type",
        "retracted_warning": "Europe PMC marks this publication as retracted. Do not rely on it as current evidence.",
        "correction_notice": "Europe PMC reports a correction or related notice for this publication.",
        "related_notices": "Corrections and related notices",
        "yes": "yes",
        "no": "no",
        "recent_searches": "Recent searches",
        "clinical_tracker_title": "Huntington's disease clinical trial tracker",
        "clinical_intro": (
            "This tracker displays registered study information from ClinicalTrials.gov. "
            "Registry status can change and does not indicate that a study is suitable, safe, or effective."
        ),
        "trial_keywords": "Optional study keywords",
        "trial_keywords_placeholder": "gene therapy, exercise, biomarker...",
        "trial_keywords_help": "Filter registered studies by research terms. Do not enter personal health information.",
        "trial_statuses": "Registry status",
        "fetch_trials": "Search ClinicalTrials.gov",
        "fetching_trials": "Retrieving registered studies...",
        "trial_source_note": (
            "Statuses and study details come directly from ClinicalTrials.gov. "
            "Always open the registry record to verify the latest information."
        ),
        "registered_studies": "Registered studies",
        "recruiting_studies": "Recruiting",
        "active_studies": "Active, not recruiting",
        "completed_studies": "Completed",
        "terminated_studies": "Terminated",
        "trial_phase": "Phase",
        "trial_country": "Country",
        "trials_to_show": "Studies to show",
        "no_trials": "No registered studies match these filters.",
        "trial_status": "Status",
        "trial_sponsor": "Sponsor",
        "trial_enrollment": "Enrollment",
        "trial_dates": "Study dates",
        "trial_interventions": "Interventions",
        "trial_locations": "Countries",
        "trial_last_update": "Registry last updated",
        "open_trial_record": "Open ClinicalTrials.gov record",
        "download_trials_csv": "Download visible studies as CSV",
        "trial_registry_unavailable": "The clinical trial tracker is unavailable: {error}",
        "more_trials_available": "The registry returned more studies than this view loaded. Refine the filters to narrow the result.",
        "recent_intro": (
            "Recent publications are retrieved from Europe PMC and filtered by year. "
            "They are not curated breakthroughs or medical recommendations."
        ),
    },
    "no": {
        "summary_style": "Oppsummeringsstil",
        "summary_mode_plain": "Klarspråk",
        "summary_mode_research": "Forskningsdetaljer",
        "search_tab": "Søk",
        "clinical_tab": "Studieregister",
        "recent_tab": "Nylige publikasjoner",
        "research_topic": "Forskningstema",
        "research_topic_placeholder": "gendemping, biomarkører, kliniske studier...",
        "research_topic_help": "Skriv inn et forskningstema, ikke personlige helseopplysninger.",
        "category_filters": "Kategorifiltre",
        "publication_year": "Publikasjonsår",
        "open_access_only": "Kun åpen tilgang",
        "results_to_show": "Artikler per side",
        "search_europe_pmc": "Søk i Europe PMC",
        "search_trials": "Søk etter litteratur om kliniske studier",
        "search_recent": "Søk etter nylige publikasjoner",
        "expanded_query": "Utvidet søk",
        "searching": "Søker i Europe PMC...",
        "loading_dashboard": "Beregner publikasjonstrend...",
        "start_search": "Skriv inn et tema og søk i Europe PMC for å begynne.",
        "timeline": "Tidslinje",
        "publication_dashboard": "Publikasjonsoversikt",
        "this_year": "Publisert i år (hittil)",
        "period_total": "Publisert i valgt periode",
        "peak_year": "År med flest publikasjoner",
        "yearly_trend": "Publikasjoner per år",
        "dashboard_note": (
            "Oversikten teller alle samsvarende poster i Europe PMC for de valgte "
            "årene og API-kompatible filtrene, ikke bare publikasjonene nedenfor."
        ),
        "dashboard_unavailable": "Publikasjonsoversikten er utilgjengelig: {error}",
        "paper_batch_count": (
            "Viser {shown} publikasjoner etter lokale filtre. "
            "Oversikten ovenfor beregnes separat fra alle samsvarende poster."
        ),
        "page_status": "Side {page} av {total_pages}",
        "pagination_help": "Viser {shown} artikler på denne siden. Bruk kontrollene for å bla i alle {total:,} treff.",
        "previous_page": "Forrige side",
        "next_page": "Neste side",
        "download_csv": "Last ned denne siden som CSV",
        "download_bibtex": "Last ned denne siden som BibTeX",
        "current_page_export_note": "Eksporten inneholder publikasjonene på denne siden og lenker til kildene.",
        "papers": "Publikasjoner",
        "no_papers": "Ingen publikasjoner funnet. Prøv et bredere tema eller færre søkeord.",
        "no_timeline": "Ingen publikasjonsår er tilgjengelige for tidslinjen.",
        "result_count": (
            "Europe PMC fant omtrent {total:,} treff. "
            "Viser {shown} publikasjoner på denne siden."
        ),
        "source_record": "Åpne kildepost i Europe PMC",
        "open_access_pdf": "Åpne fulltekst som PDF",
        "download_paper_details": "Last ned detaljer og sammendrag",
        "abstract": "Sammendrag",
        "no_abstract": "Sammendrag er ikke tilgjengelig.",
        "summarize": "Oppsummer sammendraget",
        "summarizing": "Oppsummerer lokalt med {model}...",
        "summary_failed": "Oppsummeringen feilet: {error}",
        "plain_summary": "Oppsummering i klarspråk",
        "research_summary": "Oppsummering med forskningsdetaljer",
        "norwegian_summary_later": (
            "Norsk oversettelse av abstrakt og oppsummering kommer i en senere oppdatering."
        ),
        "citations": "Siteringer",
        "open_access": "Åpen tilgang",
        "publication_types": "Publikasjonstype",
        "retracted_warning": "Europe PMC markerer denne publikasjonen som trukket tilbake. Den bør ikke brukes som gjeldende kunnskapsgrunnlag.",
        "correction_notice": "Europe PMC oppgir at publikasjonen har en rettelse eller relatert merknad.",
        "related_notices": "Rettelser og relaterte merknader",
        "yes": "ja",
        "no": "nei",
        "recent_searches": "Nylige søk",
        "clinical_tracker_title": "Register over kliniske studier på Huntingtons sykdom",
        "clinical_intro": (
            "Denne oversikten viser registrerte studieopplysninger fra ClinicalTrials.gov. "
            "Registerstatus kan endres og betyr ikke at en studie er egnet, trygg eller effektiv."
        ),
        "trial_keywords": "Valgfrie søkeord for studier",
        "trial_keywords_placeholder": "genterapi, trening, biomarkør...",
        "trial_keywords_help": "Filtrer registrerte studier etter forskningstema. Ikke skriv inn personlige helseopplysninger.",
        "trial_statuses": "Registerstatus",
        "fetch_trials": "Søk i ClinicalTrials.gov",
        "fetching_trials": "Henter registrerte studier...",
        "trial_source_note": (
            "Status og studiedetaljer kommer direkte fra ClinicalTrials.gov. "
            "Åpne alltid registerposten for å kontrollere den nyeste informasjonen."
        ),
        "registered_studies": "Registrerte studier",
        "recruiting_studies": "Rekrutterer",
        "active_studies": "Aktiv, rekrutterer ikke",
        "completed_studies": "Fullført",
        "terminated_studies": "Avsluttet før planlagt",
        "trial_phase": "Fase",
        "trial_country": "Land",
        "trials_to_show": "Antall studier som vises",
        "no_trials": "Ingen registrerte studier samsvarer med filtrene.",
        "trial_status": "Status",
        "trial_sponsor": "Sponsor",
        "trial_enrollment": "Planlagt/faktisk antall deltakere",
        "trial_dates": "Studiedatoer",
        "trial_interventions": "Intervensjoner",
        "trial_locations": "Land",
        "trial_last_update": "Sist oppdatert i registeret",
        "open_trial_record": "Åpne registerpost i ClinicalTrials.gov",
        "download_trials_csv": "Last ned viste studier som CSV",
        "trial_registry_unavailable": "Studieregisteret er utilgjengelig: {error}",
        "more_trials_available": "Registeret fant flere studier enn visningen lastet inn. Bruk filtrene for å avgrense resultatet.",
        "recent_intro": (
            "Nylige publikasjoner hentes fra Europe PMC og filtreres etter år. "
            "De er ikke kuraterte gjennombrudd eller medisinske anbefalinger."
        ),
    },
}


def translate(language: str, key: str, **values: object) -> str:
    selected = TRANSLATIONS.get(language, TRANSLATIONS["en"])
    template = selected.get(key, TRANSLATIONS["en"].get(key, key))
    return template.format(**values)
