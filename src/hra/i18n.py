from __future__ import annotations

LANGUAGE_OPTIONS = {"English": "en", "Norsk": "no"}

TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        "summary_style": "Summary style",
        "summary_mode_plain": "Plain language",
        "summary_mode_research": "Research detail",
        "search_tab": "Search",
        "clinical_tab": "Clinical trials",
        "recent_tab": "Recent publications",
        "research_topic": "Research topic",
        "research_topic_placeholder": "gene silencing, biomarkers, clinical trials...",
        "research_topic_help": "Enter a research topic, not personal health information.",
        "category_filters": "Category filters",
        "publication_year": "Publication year",
        "open_access_only": "Open access only",
        "results_to_show": "Results to show",
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
        "papers": "Papers",
        "no_papers": "No papers found. Try a broader topic or fewer keywords.",
        "no_timeline": "No publication years available for a timeline.",
        "result_count": (
            "Europe PMC matched approximately {total:,} records. "
            "Showing {shown} filtered papers from the fetched batch."
        ),
        "source_record": "Open Europe PMC source record",
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
        "yes": "yes",
        "no": "no",
        "recent_searches": "Recent searches",
        "clinical_intro": (
            "This view searches for publications that mention clinical trials, "
            "randomization, placebo, or trial phases. It is not a treatment guide."
        ),
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
        "clinical_tab": "Kliniske studier",
        "recent_tab": "Nylige publikasjoner",
        "research_topic": "Forskningstema",
        "research_topic_placeholder": "gendemping, biomarkører, kliniske studier...",
        "research_topic_help": "Skriv inn et forskningstema, ikke personlige helseopplysninger.",
        "category_filters": "Kategorifiltre",
        "publication_year": "Publikasjonsår",
        "open_access_only": "Kun åpen tilgang",
        "results_to_show": "Antall resultater",
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
        "papers": "Publikasjoner",
        "no_papers": "Ingen publikasjoner funnet. Prøv et bredere tema eller færre søkeord.",
        "no_timeline": "Ingen publikasjonsår er tilgjengelige for tidslinjen.",
        "result_count": (
            "Europe PMC fant omtrent {total:,} treff. "
            "Viser {shown} filtrerte publikasjoner fra den hentede delen."
        ),
        "source_record": "Åpne kildepost i Europe PMC",
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
        "yes": "ja",
        "no": "nei",
        "recent_searches": "Nylige søk",
        "clinical_intro": (
            "Denne visningen søker etter publikasjoner som omtaler kliniske studier, "
            "randomisering, placebo eller studiefaser. Den er ikke en behandlingsveileder."
        ),
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
