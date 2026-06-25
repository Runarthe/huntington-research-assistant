from __future__ import annotations

LANGUAGE_OPTIONS = {"English": "en", "Norsk": "no"}

TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        "summary_style": "Summary style",
        "summary_mode_plain": "Plain language",
        "summary_mode_research": "Research detail",
        "search_tab": "Search",
        "reading_list_tab": "Reading list",
        "clinical_tab": "Trial tracker",
        "recent_tab": "Recent publications",
        "knowledge_tab": "Research map (experimental)",
        "research_topic": "Research topic",
        "research_topic_placeholder": "gene silencing, biomarkers, clinical trials...",
        "research_topic_help": "Enter a research topic, not personal health information.",
        "literature_sources": "Literature sources",
        "source_provider": "Source",
        "pubmed_query": "PubMed query",
        "combined_source_note": (
            "Results from multiple sources are deduplicated by PMID, DOI, and title/year. "
            "Total counts are approximate across providers."
        ),
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
        "accessible_trend_table": "View publication counts as a table",
        "year": "Year",
        "publication_count": "Publications",
        "dashboard_note": (
            "Dashboard counts use all matching Europe PMC records for the selected "
            "years and API-compatible filters, not only the paper cards below."
        ),
        "dashboard_europe_only": "Publication dashboard is currently available for Europe PMC searches.",
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
        "add_to_reading_list": "Add to reading list",
        "remove_from_reading_list": "Remove from reading list",
        "reading_list_title": "Saved reading list",
        "reading_list_intro": (
            "Save papers locally for later reading. The list is stored only in your local "
            "cache and should not contain personal health information."
        ),
        "reading_list_unavailable": "Local reading-list storage is unavailable.",
        "reading_list_empty": "No saved papers yet. Add papers from search results to build a reading list.",
        "reading_list_count": "Saved papers",
        "abstract": "Abstract",
        "no_abstract": "No abstract available.",
        "summarize": "Summarize abstract",
        "summarizing": "Summarizing locally with {model}...",
        "summary_failed": "Summary failed: {error}",
        "summary_integrity_failed": (
            "The generated text was withheld because it did not pass the factual integrity checks: {reason}"
        ),
        "plain_summary": "Plain-language summary",
        "research_summary": "Research-detail summary",
        "norwegian_summary_experimental": (
            "Norwegian plain-language explanations are machine-generated and experimental. "
            "The original English abstract remains the authoritative source."
        ),
        "norwegian_summary_later": (
            "Norwegian translation of abstracts and summaries will be added in a later update."
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
        "knowledge_title": "Source-linked research map",
        "knowledge_intro": (
            "A knowledge graph is a map of things and their connections. This preview "
            "links catalogued genes, proteins, pathways, and compounds to papers that mention them."
        ),
        "knowledge_scope": (
            "Connections mean 'mentioned in' only. They do not establish causation, treatment "
            "effect, clinical relevance, or evidence quality. Open the source paper to verify context."
        ),
        "knowledge_search_section": "Find source papers",
        "knowledge_query": "Research-map topic",
        "knowledge_paper_limit": "Papers to inspect",
        "knowledge_search": "Build map from Europe PMC",
        "knowledge_start": "Search to build a small research map from the retrieved paper batch.",
        "knowledge_loading": "Retrieving papers and matching controlled terms...",
        "knowledge_no_entities": "No catalogued entities were found in this paper batch.",
        "knowledge_entity_types": "Entity types",
        "knowledge_entities": "Entities",
        "knowledge_source_papers": "Source papers",
        "knowledge_mentions": "Source-linked mentions",
        "knowledge_no_filter_results": "No mentions match the selected entity types.",
        "knowledge_choose_entity": "Choose one entity",
        "knowledge_map": "Mention map",
        "knowledge_map_help": (
            "Each line means only that the selected term appears in the paper's title or abstract."
        ),
        "knowledge_relationship": "mentioned in",
        "knowledge_inspect_entity": "Entity",
        "knowledge_papers_mentioning": "Papers mentioning {entity}",
        "knowledge_graph_limit": "Showing {shown} of {total} papers in the diagram. All source evidence is listed below.",
        "knowledge_evidence_title": "Why are these papers connected?",
        "knowledge_evidence_help": (
            "These are exact title or abstract sentences containing the matched term."
        ),
        "knowledge_matched_term": "Matched term",
        "knowledge_evidence_location": "Found in",
        "knowledge_location_title": "title",
        "knowledge_location_abstract": "abstract",
        "entity_gene": "Gene",
        "entity_protein": "Protein",
        "entity_pathway": "Pathway or biological process",
        "entity_compound": "Compound",
    },
    "no": {
        "summary_style": "Oppsummeringsstil",
        "summary_mode_plain": "Kort klarspråk",
        "summary_mode_research": "Detaljert forskningsforklaring",
        "search_tab": "Søk",
        "reading_list_tab": "Leseliste",
        "clinical_tab": "Studieregister",
        "recent_tab": "Nylige publikasjoner",
        "knowledge_tab": "Forskningskart (eksperimentelt)",
        "research_topic": "Forskningstema",
        "research_topic_placeholder": "gendemping, biomarkører, kliniske studier...",
        "research_topic_help": "Skriv inn et forskningstema, ikke personlige helseopplysninger.",
        "literature_sources": "Litteraturkilder",
        "source_provider": "Kilde",
        "pubmed_query": "PubMed-søk",
        "combined_source_note": (
            "Resultater fra flere kilder dedupliseres etter PMID, DOI og tittel/år. "
            "Totalt antall treff er omtrentlig på tvers av kilder."
        ),
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
        "accessible_trend_table": "Vis publikasjonsantall som tabell",
        "year": "År",
        "publication_count": "Publikasjoner",
        "dashboard_note": (
            "Oversikten teller alle samsvarende poster i Europe PMC for de valgte "
            "årene og API-kompatible filtrene, ikke bare publikasjonene nedenfor."
        ),
        "dashboard_europe_only": "Publikasjonsoversikten er foreløpig tilgjengelig for Europe PMC-søk.",
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
        "add_to_reading_list": "Legg til i leseliste",
        "remove_from_reading_list": "Fjern fra leseliste",
        "reading_list_title": "Lagret leseliste",
        "reading_list_intro": (
            "Lagre publikasjoner lokalt for senere lesing. Listen lagres bare i lokal cache "
            "og skal ikke inneholde personlige helseopplysninger."
        ),
        "reading_list_unavailable": "Lokal lagring av leseliste er utilgjengelig.",
        "reading_list_empty": "Ingen lagrede publikasjoner ennå. Legg til publikasjoner fra søkeresultatene for å bygge en leseliste.",
        "reading_list_count": "Lagrede publikasjoner",
        "abstract": "Originalt abstrakt (engelsk)",
        "no_abstract": "Originalt engelsk abstrakt er ikke tilgjengelig.",
        "summarize": "Lag norsk forklaring",
        "summarizing": "Lager kontrollert norsk forklaring lokalt med {model}...",
        "summary_failed": "Oppsummeringen feilet: {error}",
        "summary_integrity_failed": (
            "Teksten ble holdt tilbake fordi den ikke besto de automatiske faktakontrollene: {reason}"
        ),
        "plain_summary": "Norsk klarspråkforklaring (eksperimentell)",
        "research_summary": "Norsk forskningsforklaring (eksperimentell)",
        "norwegian_summary_experimental": (
            "Norske klarspråkforklaringer er maskingenererte og eksperimentelle. "
            "Det originale engelske abstraktet er den autoritative kilden."
        ),
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
        "knowledge_title": "Kildekoblet forskningskart",
        "knowledge_intro": (
            "En knowledge graph, eller kunnskapsgraf, er et kart over ting og forbindelsene "
            "mellom dem. Denne prøveversjonen kobler registrerte gener, proteiner, biologiske "
            "prosesser og forbindelser til artikler som nevner dem."
        ),
        "knowledge_scope": (
            "Koblingene betyr bare 'nevnt i'. De viser ikke årsak, behandlingseffekt, klinisk "
            "betydning eller evidenskvalitet. Åpne kildeartikkelen for å kontrollere sammenhengen."
        ),
        "knowledge_search_section": "Finn kildeartikler",
        "knowledge_query": "Tema for forskningskartet",
        "knowledge_paper_limit": "Artikler som undersøkes",
        "knowledge_search": "Bygg kart fra Europe PMC",
        "knowledge_start": "Søk for å bygge et lite forskningskart fra de hentede artiklene.",
        "knowledge_loading": "Henter artikler og finner kontrollerte begreper...",
        "knowledge_no_entities": "Ingen registrerte begreper ble funnet i disse artiklene.",
        "knowledge_entity_types": "Begrepstyper",
        "knowledge_entities": "Begreper",
        "knowledge_source_papers": "Kildeartikler",
        "knowledge_mentions": "Kildekoblede treff",
        "knowledge_no_filter_results": "Ingen treff samsvarer med de valgte begrepstypene.",
        "knowledge_choose_entity": "Velg ett begrep",
        "knowledge_map": "Kart over omtaler",
        "knowledge_map_help": (
            "Hver linje betyr bare at det valgte begrepet finnes i artikkelens tittel eller abstrakt."
        ),
        "knowledge_relationship": "nevnt i",
        "knowledge_inspect_entity": "Begrep",
        "knowledge_papers_mentioning": "Artikler som nevner {entity}",
        "knowledge_graph_limit": "Viser {shown} av {total} artikler i diagrammet. Alle kildeutdrag vises nedenfor.",
        "knowledge_evidence_title": "Hvorfor er disse artiklene koblet til begrepet?",
        "knowledge_evidence_help": (
            "Dette er eksakte setninger fra tittelen eller abstraktet som inneholder begrepet."
        ),
        "knowledge_matched_term": "Begrep som ga treff",
        "knowledge_evidence_location": "Funnet i",
        "knowledge_location_title": "tittel",
        "knowledge_location_abstract": "abstrakt",
        "entity_gene": "Gen",
        "entity_protein": "Protein",
        "entity_pathway": "Biologisk prosess eller signalvei",
        "entity_compound": "Forbindelse",
    },
}


def translate(language: str, key: str, **values: object) -> str:
    selected = TRANSLATIONS.get(language, TRANSLATIONS["en"])
    template = selected.get(key, TRANSLATIONS["en"].get(key, key))
    return template.format(**values)
