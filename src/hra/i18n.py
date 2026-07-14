from __future__ import annotations

LANGUAGE_OPTIONS = {"English": "en", "Norsk": "no"}

TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        "summary_style": "Summary style",
        "summary_mode_plain": "Plain language",
        "summary_mode_research": "Research detail",
        "search_tab": "Search",
        "reading_list_tab": "Reading list",
        "evidence_tab": "Evidence explorer",
        "protein_lab_tab": "Protein Lab (experimental)",
        "clinical_tab": "Trial tracker",
        "recent_tab": "Recent publications",
        "knowledge_tab": "Entity explorer (experimental)",
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
        "hide_saved_papers": "Hide papers already in reading list",
        "hide_seen_papers": "Hide papers marked as seen",
        "local_hidden_papers": "Hidden by local reading filters on this page: {count}",
        "results_to_show": "Articles per page",
        "search_literature": "Search literature",
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
            "Selected sources matched approximately {total:,} records. "
            "Showing {shown} papers on this page."
        ),
        "source_record": "Open source record",
        "open_access_pdf": "Open full-text PDF",
        "download_paper_details": "Download details and abstract",
        "show_export_text": "View details text",
        "add_to_reading_list": "Add to reading list",
        "remove_from_reading_list": "Remove from reading list",
        "mark_as_seen": "Mark as seen",
        "mark_as_unseen": "Mark as not seen",
        "reading_list_title": "Saved reading list",
        "reading_list_intro": (
            "Save papers locally for later reading. The list is stored only in your local "
            "cache and should not contain personal health information."
        ),
        "reading_list_unavailable": "Local reading-list storage is unavailable.",
        "reading_list_empty": "No saved papers yet. Add papers from search results to build a reading list.",
        "reading_list_count": "Saved papers",
        "evidence_title": "Compare saved papers",
        "evidence_intro": (
            "Select two to five papers from the local reading list for a source-linked, "
            "rule-based comparison."
        ),
        "evidence_scope": (
            "Study design and research-context signals are automatically identified from metadata and abstract text. "
            "Highlighted passages are exact excerpts, not an assessment of evidence strength, study quality, "
            "clinical relevance, or treatment effectiveness."
        ),
        "evidence_need_two": "Save at least two papers in the reading list before comparing them.",
        "evidence_choose_papers": "Papers to compare",
        "evidence_choose_help": "Choose between two and five locally saved papers.",
        "evidence_select_two": "Select at least two papers to build a comparison.",
        "evidence_comparison": "Structured comparison",
        "evidence_paper": "Paper",
        "evidence_study_design": "Study design",
        "evidence_contexts": "Research context signals",
        "evidence_record_status": "Record notices",
        "evidence_source": "Source",
        "evidence_source_record": "Source record",
        "evidence_open_source": "Open source",
        "evidence_passages": "Source passages",
        "evidence_passage_note": (
            "These excerpts are copied from the source abstract by simple rules. Read the full abstract and "
            "source record before drawing conclusions."
        ),
        "evidence_outcome_passages": "Possible result passages",
        "evidence_limitation_passages": "Possible limitation or uncertainty passages",
        "evidence_no_outcome_passages": "No result passage was identified automatically.",
        "evidence_no_limitation_passages": "No limitation passage was identified automatically.",
        "evidence_source_unavailable": "No source record URL is available for this cached paper.",
        "evidence_download_csv": "Download detailed comparison as CSV",
        "evidence_status_retracted": "Retracted",
        "evidence_status_corrected": "Correction or related notice",
        "evidence_status_clear": "No prominent notice reported",
        "evidence_design_meta_analysis": "Meta-analysis",
        "evidence_design_systematic_review": "Systematic review",
        "evidence_design_randomized_controlled_trial": "Randomized controlled trial",
        "evidence_design_clinical_trial": "Clinical trial",
        "evidence_design_review": "Review",
        "evidence_design_case_report": "Case report",
        "evidence_design_observational_study": "Observational study",
        "evidence_design_preprint": "Preprint",
        "evidence_design_preclinical_study": "Preclinical study",
        "evidence_design_human_study": "Human study / not further classified",
        "evidence_design_laboratory_study": "Molecular or laboratory study",
        "evidence_design_journal_article": "Journal article / not further classified",
        "evidence_design_not_classified": "Not classified",
        "evidence_context_human_participants": "Human participants or samples",
        "evidence_context_animal_model": "Animal model",
        "evidence_context_cell_or_tissue_model": "Cell or tissue model",
        "evidence_context_computational_model": "Computational model",
        "evidence_context_molecular_experiment": "Molecular or genetic experiment",
        "evidence_context_not_identified": "Not reported or not identified",
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
        "knowledge_title": "Source-linked entity explorer",
        "knowledge_intro": (
            "A knowledge graph is a map of things and their connections. This preview "
            "links catalogued genes, proteins, biomarkers, pathways, and compounds to papers that mention them."
        ),
        "knowledge_scope": (
            "Connections mean 'mentioned in' only. They do not establish causation, treatment "
            "effect, clinical relevance, or evidence quality. Mention confidence describes only "
            "the alias match. Open the source paper to verify context."
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
        "knowledge_catalog_id": "Catalogue ID",
        "knowledge_catalog_version": "Catalogue version",
        "knowledge_aliases": "Known aliases",
        "knowledge_related_title": "Also catalogued in the same source papers",
        "knowledge_related_help": (
            "Shared papers are a navigation signal only. They do not establish a biological or clinical relationship."
        ),
        "knowledge_related_none": "No other selected entity types were catalogued in the same papers.",
        "knowledge_related_entity": "Entity",
        "knowledge_entity_type": "Entity type",
        "knowledge_shared_papers": "Shared source papers",
        "knowledge_extraction_method": "Extraction method",
        "knowledge_method_controlled_vocabulary_alias": "controlled vocabulary alias",
        "knowledge_confidence": "Mention confidence",
        "knowledge_confidence_high": "high",
        "knowledge_confidence_medium": "medium",
        "entity_gene": "Gene",
        "entity_protein": "Protein",
        "entity_biomarker": "Biomarker",
        "entity_pathway": "Pathway or biological process",
        "entity_compound": "Compound",
        "protein_lab_title": "Protein Lab (experimental)",
        "protein_lab_intro": (
            "This lab makes the protein-target infrastructure visible for review. "
            "It uses curated identifiers and local provenance reports only."
        ),
        "protein_lab_scope": (
            "No live model calls are made here. Reports are navigation/provenance artifacts, "
            "not biological hypotheses, treatment rankings, or medical advice."
        ),
        "protein_lab_symbol": "Symbol",
        "protein_lab_name": "Protein name",
        "protein_lab_entity_id": "Entity ID",
        "protein_lab_source": "Source record",
        "protein_lab_choose_target": "Protein target",
        "protein_lab_open_uniprot": "Open UniProt record",
        "protein_lab_mapped_entities": "Mapped entities",
        "protein_lab_manifests": "Local manifests",
        "protein_lab_report_status": "Report status",
        "protein_lab_report_source": "Report source",
        "protein_lab_report_source_catalogue": "Curated target catalogue",
        "protein_lab_report_source_reading_list": "Saved reading list",
        "protein_lab_planned_manifest": "Planned sequence manifest",
        "protein_lab_target_report": "Read-only target report",
        "protein_lab_download_report": "Download target report JSON",
        "protein_lab_source_papers": "Source papers linked to this target",
        "protein_lab_source_papers_help": (
            "These papers come from the local reading list and are linked by controlled entity mentions only."
        ),
        "protein_lab_reading_list_unavailable": (
            "Local reading-list storage is unavailable. Using catalogue entities."
        ),
        "protein_lab_no_reading_list_papers": (
            "No saved reading-list papers are available. Using catalogue entities."
        ),
        "protein_lab_using_reading_list": (
            "Using {count} saved reading-list source paper(s) with catalogued mentions for {symbol}."
        ),
        "protein_lab_no_target_mentions": (
            "No saved reading-list papers mention this selected protein target through the current controlled entity catalogue."
        ),
        "protein_lab_cli_title": "CLI checks",
        "protein_lab_cli_help": "Equivalent offline commands for reviewing this target outside the app.",
    },
    "no": {
        "summary_style": "Oppsummeringsstil",
        "summary_mode_plain": "Kort klarspråk",
        "summary_mode_research": "Detaljert forskningsforklaring",
        "search_tab": "Søk",
        "reading_list_tab": "Leseliste",
        "evidence_tab": "Evidensutforsker",
        "protein_lab_tab": "Proteinlab (eksperimentell)",
        "clinical_tab": "Studieregister",
        "recent_tab": "Nylige publikasjoner",
        "knowledge_tab": "Begrepsutforsker (eksperimentell)",
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
        "hide_saved_papers": "Skjul publikasjoner som allerede er i leselisten",
        "hide_seen_papers": "Skjul publikasjoner som er merket som sett",
        "local_hidden_papers": "Skjult av lokale lesefiltre på denne siden: {count}",
        "results_to_show": "Artikler per side",
        "search_literature": "Søk i litteraturkilder",
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
            "Valgte kilder fant omtrent {total:,} treff. "
            "Viser {shown} publikasjoner på denne siden."
        ),
        "source_record": "Åpne kildepost",
        "open_access_pdf": "Åpne fulltekst som PDF",
        "download_paper_details": "Last ned detaljer og sammendrag",
        "show_export_text": "Vis detaljtekst",
        "add_to_reading_list": "Legg til i leseliste",
        "remove_from_reading_list": "Fjern fra leseliste",
        "mark_as_seen": "Merk som sett",
        "mark_as_unseen": "Merk som ikke sett",
        "reading_list_title": "Lagret leseliste",
        "reading_list_intro": (
            "Lagre publikasjoner lokalt for senere lesing. Listen lagres bare i lokal cache "
            "og skal ikke inneholde personlige helseopplysninger."
        ),
        "reading_list_unavailable": "Lokal lagring av leseliste er utilgjengelig.",
        "reading_list_empty": "Ingen lagrede publikasjoner ennå. Legg til publikasjoner fra søkeresultatene for å bygge en leseliste.",
        "reading_list_count": "Lagrede publikasjoner",
        "evidence_title": "Sammenlign lagrede publikasjoner",
        "evidence_intro": (
            "Velg to til fem publikasjoner fra den lokale leselisten for en kildekoblet, "
            "regelbasert sammenligning."
        ),
        "evidence_scope": (
            "Studiedesign og signaler om forskningskontekst identifiseres automatisk fra metadata og abstrakttekst. "
            "Markerte passasjer er eksakte utdrag, ikke en vurdering av evidensstyrke, studiekvalitet, "
            "klinisk betydning eller behandlingseffekt."
        ),
        "evidence_need_two": "Lagre minst to publikasjoner i leselisten før du sammenligner dem.",
        "evidence_choose_papers": "Publikasjoner som skal sammenlignes",
        "evidence_choose_help": "Velg mellom to og fem lokalt lagrede publikasjoner.",
        "evidence_select_two": "Velg minst to publikasjoner for å bygge en sammenligning.",
        "evidence_comparison": "Strukturert sammenligning",
        "evidence_paper": "Publikasjon",
        "evidence_study_design": "Studiedesign",
        "evidence_contexts": "Signaler om forskningskontekst",
        "evidence_record_status": "Merknader om kildeposten",
        "evidence_source": "Kilde",
        "evidence_source_record": "Kildepost",
        "evidence_open_source": "Åpne kilde",
        "evidence_passages": "Kildeutdrag",
        "evidence_passage_note": (
            "Disse utdragene er kopiert fra kildeabstraktet med enkle regler. Les hele abstraktet og "
            "kildeposten før du trekker konklusjoner."
        ),
        "evidence_outcome_passages": "Mulige resultatpassasjer",
        "evidence_limitation_passages": "Mulige passasjer om begrensninger eller usikkerhet",
        "evidence_no_outcome_passages": "Ingen resultatpassasje ble identifisert automatisk.",
        "evidence_no_limitation_passages": "Ingen begrensningspassasje ble identifisert automatisk.",
        "evidence_source_unavailable": "Ingen lenke til kildeposten er tilgjengelig for denne lagrede publikasjonen.",
        "evidence_download_csv": "Last ned detaljert sammenligning som CSV",
        "evidence_status_retracted": "Trukket tilbake",
        "evidence_status_corrected": "Rettelse eller relatert merknad",
        "evidence_status_clear": "Ingen fremtredende merknad rapportert",
        "evidence_design_meta_analysis": "Metaanalyse",
        "evidence_design_systematic_review": "Systematisk oversikt",
        "evidence_design_randomized_controlled_trial": "Randomisert kontrollert studie",
        "evidence_design_clinical_trial": "Klinisk studie",
        "evidence_design_review": "Oversiktsartikkel",
        "evidence_design_case_report": "Kasusrapport",
        "evidence_design_observational_study": "Observasjonsstudie",
        "evidence_design_preprint": "Preprint",
        "evidence_design_preclinical_study": "Preklinisk studie",
        "evidence_design_human_study": "Studie med mennesker / ikke nærmere klassifisert",
        "evidence_design_laboratory_study": "Molekylær studie eller laboratoriestudie",
        "evidence_design_journal_article": "Tidsskriftartikkel / ikke nærmere klassifisert",
        "evidence_design_not_classified": "Ikke klassifisert",
        "evidence_context_human_participants": "Menneskelige deltakere eller prøver",
        "evidence_context_animal_model": "Dyremodell",
        "evidence_context_cell_or_tissue_model": "Celle- eller vevsmodell",
        "evidence_context_computational_model": "Datamodell",
        "evidence_context_molecular_experiment": "Molekylært eller genetisk eksperiment",
        "evidence_context_not_identified": "Ikke rapportert eller ikke identifisert",
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
        "knowledge_title": "Kildekoblet begrepsutforsker",
        "knowledge_intro": (
            "En knowledge graph, eller kunnskapsgraf, er et kart over ting og forbindelsene "
            "mellom dem. Denne prøveversjonen kobler registrerte gener, proteiner, "
            "biomarkører, prosesser og forbindelser til artikler som nevner dem."
        ),
        "knowledge_scope": (
            "Koblingene betyr bare 'nevnt i'. De viser ikke årsak, behandlingseffekt, klinisk "
            "betydning eller evidenskvalitet. Treffsikkerheten gjelder bare gjenkjenning av "
            "begrepet. Åpne kildeartikkelen for å kontrollere sammenhengen."
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
        "knowledge_catalog_id": "Katalog-ID",
        "knowledge_catalog_version": "Katalogversjon",
        "knowledge_aliases": "Alternative skrivemåter",
        "knowledge_related_title": "Også registrert i de samme kildeartiklene",
        "knowledge_related_help": (
            "Felles artikler er bare et navigasjonssignal. De viser ikke en biologisk eller klinisk sammenheng."
        ),
        "knowledge_related_none": "Ingen andre valgte begrepstyper ble funnet i de samme artiklene.",
        "knowledge_related_entity": "Begrep",
        "knowledge_entity_type": "Begrepstype",
        "knowledge_shared_papers": "Felles kildeartikler",
        "knowledge_extraction_method": "Uttrekksmetode",
        "knowledge_method_controlled_vocabulary_alias": "kontrollert ordliste",
        "knowledge_confidence": "Treffsikkerhet for omtale",
        "knowledge_confidence_high": "høy",
        "knowledge_confidence_medium": "middels",
        "entity_gene": "Gen",
        "entity_protein": "Protein",
        "entity_biomarker": "Biomarkør",
        "entity_pathway": "Biologisk prosess eller signalvei",
        "entity_compound": "Forbindelse",
        "protein_lab_title": "Proteinlab (eksperimentell)",
        "protein_lab_intro": (
            "Denne labben gjor proteinmal-infrastrukturen synlig for gjennomgang. "
            "Den bruker kuraterte identifikatorer og lokale proveniensrapporter."
        ),
        "protein_lab_scope": (
            "Ingen levende modellkall kjores her. Rapportene er navigasjon og proveniens, "
            "ikke biologiske hypoteser, behandlingsrangeringer eller medisinske rad."
        ),
        "protein_lab_symbol": "Symbol",
        "protein_lab_name": "Proteinnavn",
        "protein_lab_entity_id": "Begreps-ID",
        "protein_lab_source": "Kildepost",
        "protein_lab_choose_target": "Proteinmal",
        "protein_lab_open_uniprot": "Apne UniProt-post",
        "protein_lab_mapped_entities": "Koblede begreper",
        "protein_lab_manifests": "Lokale manifester",
        "protein_lab_report_status": "Rapportstatus",
        "protein_lab_report_source": "Rapportkilde",
        "protein_lab_report_source_catalogue": "Kurert malkatalog",
        "protein_lab_report_source_reading_list": "Lagret leseliste",
        "protein_lab_planned_manifest": "Planlagt sekvensmanifest",
        "protein_lab_target_report": "Skrivebeskyttet malrapport",
        "protein_lab_download_report": "Last ned malrapport som JSON",
        "protein_lab_source_papers": "Kildeartikler koblet til dette malet",
        "protein_lab_source_papers_help": (
            "Disse artiklene kommer fra den lokale leselisten og kobles bare via kontrollerte begrepstreff."
        ),
        "protein_lab_reading_list_unavailable": (
            "Lokal leseliste er utilgjengelig. Bruker kuraterte katalogbegreper."
        ),
        "protein_lab_no_reading_list_papers": (
            "Ingen lagrede leselisteartikler er tilgjengelige. Bruker kuraterte katalogbegreper."
        ),
        "protein_lab_using_reading_list": (
            "Bruker {count} lagrede kildeartikkel/artikler fra leselisten med katalogtreff for {symbol}."
        ),
        "protein_lab_no_target_mentions": (
            "Ingen lagrede leselisteartikler nevner dette proteinmalet gjennom den gjeldende kontrollerte begrepskatalogen."
        ),
        "protein_lab_cli_title": "CLI-sjekker",
        "protein_lab_cli_help": "Tilsvarende offline-kommandoer for gjennomgang utenfor appen.",
    },
}


def translate(language: str, key: str, **values: object) -> str:
    selected = TRANSLATIONS.get(language, TRANSLATIONS["en"])
    template = selected.get(key, TRANSLATIONS["en"].get(key, key))
    return template.format(**values)
