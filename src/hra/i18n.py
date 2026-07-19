from __future__ import annotations

LANGUAGE_OPTIONS = {"English": "en", "Norsk": "no"}

TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        "summary_style": "Summary style",
        "summary_mode_plain": "Plain language",
        "summary_mode_research": "Research detail",
        "explanation_style": "Explanations",
        "explanation_mode_simple": "Simple",
        "explanation_mode_detailed": "Detailed",
        "search_tab": "Search",
        "reading_list_tab": "Reading list",
        "evidence_tab": "Evidence explorer",
        "protein_lab_tab": "Protein Lab (experimental)",
        "clinical_tab": "Trial tracker",
        "recent_tab": "Recent publications",
        "knowledge_tab": "Entity explorer (experimental)",
        "search_tab_intro": (
            "Search official literature sources. The app expands your topic with Huntington-related terms."
        ),
        "search_tab_intro_simple": "Search official literature sources for Huntington-related research.",
        "research_topic": "Research topic",
        "research_topic_placeholder": "gene silencing, biomarkers, clinical trials...",
        "research_topic_help": "Enter a research topic, not personal health information.",
        "research_topic_help_simple": "Enter a research topic, not personal health information.",
        "literature_sources": "Literature sources",
        "literature_sources_help": (
            "Choose where to search. Europe PMC is best for metadata and open-access links; PubMed is the official NCBI literature index."
        ),
        "literature_sources_help_simple": "Choose which literature databases to search.",
        "source_provider": "Source",
        "pubmed_query": "PubMed query",
        "combined_source_note": (
            "Results from multiple sources are deduplicated by PMID, DOI, and title/year. "
            "Total counts are approximate across providers."
        ),
        "category_filters": "Category filters",
        "category_filters_help": (
            "Optional topic filters based on simple keywords in the title and abstract."
        ),
        "category_filters_help_simple": "Optional keyword-based topic filters.",
        "publication_year": "Publication year",
        "publication_year_help": "Limit results to papers published within this year range.",
        "publication_year_help_simple": "Limit results by publication year.",
        "open_access_only": "Open access only",
        "open_access_only_help": (
            "Show only records marked as open access by the source provider when that metadata is available."
        ),
        "open_access_only_help_simple": "Show only records marked as open access.",
        "hide_saved_papers": "Hide papers already in reading list",
        "hide_saved_papers_help": "Use this to discover papers you have not saved locally yet.",
        "hide_saved_papers_help_simple": "Hide papers you already saved.",
        "hide_seen_papers": "Hide papers marked as seen",
        "hide_seen_papers_help": "Use this to skip papers you have already reviewed in this browser.",
        "hide_seen_papers_help_simple": "Hide papers you marked as seen.",
        "local_hidden_papers": "Hidden by local reading filters on this page: {count}",
        "results_to_show": "Articles per page",
        "results_to_show_help": "Choose how many paper cards to load for each result page.",
        "results_to_show_help_simple": "Choose how many papers to show per page.",
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
        "trial_keywords_help_simple": "Optional research keywords. Do not enter personal health information.",
        "trial_statuses": "Registry status",
        "trial_statuses_help": (
            "Filter studies by their current ClinicalTrials.gov registry status. Status does not mean a study is suitable, safe, or effective."
        ),
        "trial_statuses_help_simple": "Filter studies by registry status.",
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
            "Recent publications use the same literature search workflow, but start with the last couple of years selected. "
            "They are not curated breakthroughs, clinical guidance, or medical recommendations."
        ),
        "recent_intro_simple": "Search newer Huntington-related papers from the last couple of years.",
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
        "knowledge_entity_types_help": (
            "Choose which controlled entity categories to show. These are exact term matches, not AI-discovered relationships."
        ),
        "knowledge_entity_types_help_simple": "Choose which entity categories to show.",
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
            "No model runs automatically. Reports and embeddings are provenance artifacts, "
            "not biological hypotheses, treatment rankings, or medical advice."
        ),
        "protein_lab_symbol": "Symbol",
        "protein_lab_name": "Protein name",
        "protein_lab_entity_id": "Entity ID",
        "protein_lab_source": "Source record",
        "protein_lab_choose_target": "Protein target",
        "protein_lab_choose_target_help": "Choose one curated target to inspect. The list is intentionally small for review.",
        "protein_lab_choose_target_help_simple": "Choose one curated protein target.",
        "protein_lab_open_uniprot": "Open UniProt record",
        "protein_lab_mapped_entities": "Mapped entities",
        "protein_lab_manifests": "Local manifests",
        "protein_lab_report_status": "Report status",
        "protein_lab_report_source": "Report source",
        "protein_lab_report_source_help": (
            "Use the catalogue for a stable target report, or the reading list to link saved source papers by controlled mentions."
        ),
        "protein_lab_report_source_help_simple": "Choose catalogue data or saved reading-list papers.",
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
        "esm2_lab_title": "Local ESM-2 experiment",
        "esm2_lab_intro": (
            "Generate a numerical protein-sequence representation with a small, local ESM-2 checkpoint. "
            "The model runs only after you explicitly start it."
        ),
        "esm2_lab_scope": (
            "This experiment records model and sequence provenance. It does not predict protein function, "
            "disease relevance, treatment value, or clinical meaning."
        ),
        "esm2_input_source": "Sequence input",
        "esm2_input_source_help": (
            "Use the bundled short fragment for an offline interface check, or explicitly retrieve and cache "
            "the current authoritative UniProt sequence."
        ),
        "esm2_input_source_help_simple": "Choose a test fragment or a cached UniProt sequence.",
        "esm2_input_fixture": "Bundled fixture fragment",
        "esm2_input_uniprot_cache": "Cached UniProt sequence",
        "esm2_retrieve_uniprot": "Retrieve or refresh from UniProt",
        "esm2_retrieving": "Retrieving and validating the UniProt sequence...",
        "esm2_retrieved": "The UniProt sequence was validated and saved in the local user cache.",
        "esm2_retrieval_failed": "UniProt retrieval failed: {error}",
        "esm2_no_cached_sequence": "No cached UniProt sequence is available for this target yet.",
        "esm2_sequence_length": "Sequence residues",
        "esm2_sequence_checksum": "Sequence checksum",
        "esm2_sequence_source": "Input source",
        "esm2_sequence_details": "Accession: {accession} | Retrieved/recorded: {date}",
        "esm2_window_required": (
            "This sequence has {length} residues and exceeds the {limit}-residue experiment limit. "
            "Choose an explicit window; the app will never truncate silently."
        ),
        "esm2_window_start": "Window start (one-based)",
        "esm2_window_start_help": "First residue included in the model input, using one-based sequence coordinates.",
        "esm2_window_start_help_simple": "Choose the first residue to include.",
        "esm2_window_length": "Window length",
        "esm2_window_length_help": "Number of residues included. v0.10 allows at most 1,022 residues.",
        "esm2_window_length_help_simple": "Choose how many residues to include.",
        "esm2_device": "Compute device",
        "esm2_device_help": "Auto uses CUDA when PyTorch can access it; CPU is the portable fallback.",
        "esm2_device_help_simple": "Choose automatic, CPU, or NVIDIA CUDA execution.",
        "esm2_device_auto": "Auto",
        "esm2_device_cpu": "CPU",
        "esm2_device_cuda": "NVIDIA CUDA",
        "esm2_cached_model_only": "Use already-downloaded model files only",
        "esm2_cached_model_only_help": (
            "Prevent network access during model loading. This run fails if the pinned checkpoint is not already cached."
        ),
        "esm2_cached_model_only_help_simple": "Do not download model files during this run.",
        "esm2_plan_title": "Planned ESM-2 manifest",
        "esm2_download_plan": "Download ESM-2 plan JSON",
        "esm2_runtime_ready": "Local ESM-2 dependencies are available.",
        "esm2_runtime_missing": "Local ESM-2 is optional. Missing packages: {packages}",
        "esm2_run_confirmation": (
            "I understand that the first run may download model files and that the output has no clinical meaning."
        ),
        "esm2_run": "Run local ESM-2",
        "esm2_running": "Loading the pinned checkpoint and generating the embedding...",
        "esm2_run_complete": "Embedding artifact generated. Run the same input again to compare checksums.",
        "esm2_run_failed": "Local ESM-2 run failed: {error}",
        "esm2_dimensions": "Embedding dimensions",
        "esm2_tensor_shape": "Token tensor shape",
        "esm2_repeat_status": "Repeat check",
        "esm2_repeat_baseline_recorded": "Baseline recorded",
        "esm2_repeat_matched": "Checksum matched",
        "esm2_repeat_different": "Checksum differed",
        "esm2_repeat_not_comparable": "Not comparable",
        "esm2_artifact_warning": (
            "Experimental computational artifact only. The vector has not been evaluated for a scientific downstream task."
        ),
        "esm2_artifact_title": "Embedding artifact and provenance",
        "esm2_download_artifact": "Download embedding artifact JSON",
        "parity_lab_title": "Provider parity review",
        "parity_lab_intro": (
            "Compare the local ESM-2 provenance contract with a planned BioNeMo Framework run using the exact same sequence window."
        ),
        "parity_lab_scope": (
            "BioNeMo is not executed here. Matching fields show engineering input compatibility only, not equivalent model weights, vectors, or biological meaning."
        ),
        "parity_handoff_title": "External BioNeMo handoff",
        "parity_handoff_help": (
            "Download a credential-free bundle for a separately reviewed x86 Linux, Docker, and NVIDIA GPU environment. Inspect every included file before running it."
        ),
        "parity_prerequisites_docs": "Official BioNeMo hardware and software prerequisites",
        "parity_download_execution_bundle": "Download Linux/GPU execution bundle",
        "parity_use_fixture": "Use offline result fixture",
        "parity_use_fixture_help": (
            "Exercise result validation and UI plumbing with deterministic metadata. No model, container, or GPU runs."
        ),
        "parity_import_result": "Import BioNeMo result JSON",
        "parity_import_result_help": (
            "Import the small hra-bionemo-result.json created by the execution bundle. Full vectors and files over 1 MB are rejected."
        ),
        "parity_import_success": "The BioNeMo result matches this exact plan and passed structural validation.",
        "parity_import_failed": "The BioNeMo result was rejected: {error}",
        "parity_fixture_warning": (
            "Fixture validation is active. These tensor values and checksums are test data, not BioNeMo model output."
        ),
        "parity_input_contract": "Input contract ready",
        "parity_bionemo_execution": "BioNeMo execution",
        "parity_planned_only": "Planned only",
        "parity_imported_result": "Imported result",
        "parity_fixture_validated": "Fixture validated",
        "parity_unresolved_checks": "Unresolved checks",
        "parity_check": "Check",
        "parity_result": "Result",
        "parity_local_reference": "Local reference",
        "parity_bionemo_candidate": "BioNeMo candidate",
        "parity_meaning": "What this checks",
        "parity_not_recorded": "Not recorded",
        "parity_status_matched": "Matched",
        "parity_status_different": "Different",
        "parity_status_not_available": "Not available",
        "parity_status_not_comparable": "Not comparable",
        "parity_field_selected_sequence_checksum": "Selected sequence checksum",
        "parity_field_sequence_window": "Sequence window",
        "parity_field_selected_sequence_length": "Selected sequence length",
        "parity_field_silent_truncation": "Silent truncation policy",
        "parity_field_model_identity": "Model identity",
        "parity_field_checkpoint_weight_identity": "Checkpoint weight identity",
        "parity_field_pooling_method": "Pooling method",
        "parity_field_execution_status": "Execution status",
        "parity_field_embedding_dimensions": "Embedding dimensions",
        "parity_field_token_embeddings_shape": "Token tensor shape",
        "parity_field_vector_checksum": "Vector checksum",
        "parity_field_runtime_hardware": "Runtime hardware",
        "parity_field_runtime_precision": "Runtime precision",
        "parity_meaning_selected_sequence_checksum": "Checks whether both providers receive the same selected residues.",
        "parity_meaning_sequence_window": "Compares the explicit one-based sequence coordinates.",
        "parity_meaning_selected_sequence_length": "Compares how many residues are submitted.",
        "parity_meaning_silent_truncation": "Requires HRA to reject unrecorded provider-side truncation.",
        "parity_meaning_model_identity": "Compares provider, checkpoint name, and revision literally.",
        "parity_meaning_checkpoint_weight_identity": "A shared architecture does not prove that checkpoint weights are identical.",
        "parity_meaning_pooling_method": "Similar averaging labels still need implementation-level validation.",
        "parity_meaning_execution_status": "A planned provider has no runtime output to compare.",
        "parity_meaning_embedding_dimensions": "Dimensions become comparable only after both providers run.",
        "parity_meaning_token_embeddings_shape": "Tensor shapes become comparable only after both providers run.",
        "parity_meaning_vector_checksum": "Checksums support reproducibility; they do not measure biological similarity.",
        "parity_meaning_runtime_hardware": "Hardware is recorded as provenance and need not match.",
        "parity_meaning_runtime_precision": "Numerical precision must be recorded before output comparison.",
        "parity_sources": "Official BioNeMo documentation used to define this plan:",
        "parity_bionemo_model_docs": "ESM-2 model and checkpoint documentation",
        "parity_bionemo_inference_docs": "ESM-2 inference documentation",
        "parity_bionemo_plan_title": "Planned BioNeMo ESM-2 manifest",
        "parity_report_title": "Provider parity report",
        "parity_download_bionemo_plan": "Download BioNeMo plan JSON",
        "parity_download_report": "Download parity report JSON",
        "blueprint_lab_title": "Blueprint Lab preview",
        "blueprint_lab_intro": (
            "This preview shows how a curated target, provider boundary, experiment manifest, "
            "and provenance record fit together before live scientific-AI execution is enabled."
        ),
        "blueprint_lab_scope": (
            "Blueprint artifacts are engineering provenance records only. They are not model-validated findings, "
            "clinical evidence, treatment guidance, or medical advice."
        ),
        "blueprint_lab_workflow_title": "Workflow",
        "blueprint_lab_workflow_target": "Step 1: Select a curated target",
        "blueprint_lab_workflow_provider": "Step 2: Inspect a provider boundary",
        "blueprint_lab_workflow_manifest": "Step 3: Review the planned artifact",
        "blueprint_lab_workflow_provenance": "Step 4: Check recorded provenance",
        "blueprint_lab_provider": "Provider family",
        "blueprint_lab_provider_help": (
            "Choose a provider family to plan for. Only the mock provider can generate an offline fixture today."
        ),
        "blueprint_lab_provider_help_simple": "Choose a provider family. Only mock runs execute offline.",
        "blueprint_lab_execution_mode": "Execution mode",
        "blueprint_lab_execution_mode_help": (
            "The preview exposes only modes it can safely perform: offline fixture generation for mock data, "
            "or plan-only manifests for providers without an enabled live adapter."
        ),
        "blueprint_lab_execution_mode_help_simple": "Mock uses offline test data; other providers remain plan-only.",
        "blueprint_mode_offline": "Offline fixture",
        "blueprint_mode_planned": "Planned only",
        "blueprint_mode_live": "Live provider",
        "blueprint_lab_provider_status": "Provider status",
        "blueprint_lab_provider_mock_fixture": "Mock fixture",
        "blueprint_lab_provider_mock_fixture_detail": (
            "This provider uses deterministic local fixture data only. It does not call a model, API, GPU, or external service."
        ),
        "blueprint_lab_provider_public_data_gated": "Public data / gated",
        "blueprint_lab_provider_public_data_gated_detail": (
            "This provider describes public source provenance. Live retrieval is still explicit and gated, and no interpretation is produced."
        ),
        "blueprint_lab_provider_planned_only": "Planned only",
        "blueprint_lab_provider_planned_only_detail": (
            "This provider family is a planning target only. It records what would be run, without executing a live provider."
        ),
        "blueprint_lab_provider_live_ready": "Live reviewed",
        "blueprint_lab_provider_live_ready_detail": (
            "This provider has an explicit reviewed live configuration. Use only for bounded lab runs with recorded provenance."
        ),
        "blueprint_lab_live_enabled": "Live enabled",
        "blueprint_lab_implemented": "Adapter available",
        "blueprint_lab_credentials": "Needs credentials",
        "blueprint_lab_target": "Blueprint target",
        "blueprint_lab_target_help": "Choose one curated protein target for the planned or mock artifact.",
        "blueprint_lab_target_help_simple": "Choose one curated protein target.",
        "blueprint_lab_registry_records": "Registry records",
        "blueprint_lab_registry_valid": "Valid",
        "blueprint_lab_registry_invalid": "Invalid",
        "blueprint_lab_experiment_id": "Experiment ID",
        "blueprint_lab_status": "Status",
        "blueprint_lab_targets": "Targets",
        "blueprint_lab_artifact_type": "Artifact type",
        "blueprint_lab_valid": "Valid",
        "blueprint_lab_checksum": "Checksum",
        "blueprint_lab_no_registry_records": "No local Blueprint manifests were found.",
        "blueprint_lab_registry_title": "Local artifact registry",
        "blueprint_lab_registry_help": (
            "The registry indexes saved manifest files and their checksums. It does not execute providers or interpret results."
        ),
        "blueprint_lab_planned_manifest": "Planned Blueprint manifest",
        "blueprint_lab_planned_manifest_help": (
            "This records the selected target and provider boundary without calling that provider."
        ),
        "blueprint_lab_mock_manifest": "Mock Blueprint manifest",
        "blueprint_lab_mock_manifest_help": (
            "This deterministic fixture is available only for the mock provider and is not model output."
        ),
        "blueprint_lab_download_plan": "Download planned manifest JSON",
        "blueprint_lab_download_mock": "Download mock manifest JSON",
        "blueprint_lab_download_registry": "Download registry JSON",
        "blueprint_lab_cli_title": "Blueprint CLI checks",
        "blueprint_lab_cli_help": "Equivalent offline commands for reviewing Blueprint manifests outside the app.",
        "blueprint_provider_alphafold": "AlphaFold / structure workflow",
        "blueprint_provider_bionemo": "BioNeMo",
        "blueprint_provider_mock": "Mock fixture",
        "blueprint_provider_nvidia_blueprint": "NVIDIA Blueprint",
        "blueprint_provider_nvidia_nim": "NVIDIA NIM",
        "blueprint_provider_other": "Other provider",
        "blueprint_provider_uniprot": "UniProt public data",
    },
    "no": {
        "summary_style": "Oppsummeringsstil",
        "summary_mode_plain": "Kort klarspråk",
        "summary_mode_research": "Detaljert forskningsforklaring",
        "explanation_style": "Forklaringer",
        "explanation_mode_simple": "Enkle",
        "explanation_mode_detailed": "Detaljerte",
        "search_tab": "Søk",
        "reading_list_tab": "Leseliste",
        "evidence_tab": "Evidensutforsker",
        "protein_lab_tab": "Proteinlab (eksperimentell)",
        "clinical_tab": "Studieregister",
        "recent_tab": "Nylige publikasjoner",
        "knowledge_tab": "Begrepsutforsker (eksperimentell)",
        "search_tab_intro": (
            "Søk i offisielle litteraturkilder. Appen utvider temaet med Huntington-relaterte begreper."
        ),
        "search_tab_intro_simple": "Søk i offisielle litteraturkilder om Huntington-relatert forskning.",
        "research_topic": "Forskningstema",
        "research_topic_placeholder": "gendemping, biomarkører, kliniske studier...",
        "research_topic_help": "Skriv inn et forskningstema, ikke personlige helseopplysninger.",
        "research_topic_help_simple": "Skriv inn et forskningstema, ikke personlige helseopplysninger.",
        "literature_sources": "Litteraturkilder",
        "literature_sources_help": (
            "Velg hvor det skal søkes. Europe PMC er nyttig for metadata og åpen tilgang; PubMed er NCBIs offisielle litteraturindeks."
        ),
        "literature_sources_help_simple": "Velg hvilke litteraturdatabaser som skal brukes.",
        "source_provider": "Kilde",
        "pubmed_query": "PubMed-søk",
        "combined_source_note": (
            "Resultater fra flere kilder dedupliseres etter PMID, DOI og tittel/år. "
            "Totalt antall treff er omtrentlig på tvers av kilder."
        ),
        "category_filters": "Kategorifiltre",
        "category_filters_help": (
            "Valgfrie temafiltre basert på enkle nøkkelord i tittel og abstrakt."
        ),
        "category_filters_help_simple": "Valgfrie temafiltre basert på nøkkelord.",
        "publication_year": "Publikasjonsår",
        "publication_year_help": "Avgrens resultatene til publikasjoner fra denne årsperioden.",
        "publication_year_help_simple": "Avgrens etter publikasjonsår.",
        "open_access_only": "Kun åpen tilgang",
        "open_access_only_help": (
            "Vis bare poster som kilden markerer som åpen tilgang når slik metadata finnes."
        ),
        "open_access_only_help_simple": "Vis bare poster merket som apen tilgang.",
        "hide_saved_papers": "Skjul publikasjoner som allerede er i leselisten",
        "hide_saved_papers_help": "Bruk dette for a finne artikler du ikke allerede har lagret lokalt.",
        "hide_saved_papers_help_simple": "Skjul artikler du allerede har lagret.",
        "hide_seen_papers": "Skjul publikasjoner som er merket som sett",
        "hide_seen_papers_help": "Bruk dette for a hoppe over artikler du allerede har sett i denne nettleseren.",
        "hide_seen_papers_help_simple": "Skjul artikler du har merket som sett.",
        "local_hidden_papers": "Skjult av lokale lesefiltre på denne siden: {count}",
        "results_to_show": "Artikler per side",
        "results_to_show_help": "Velg hvor mange artikkelkort som lastes for hver resultatside.",
        "results_to_show_help_simple": "Velg hvor mange artikler som vises per side.",
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
        "trial_keywords_help_simple": "Valgfrie forskningsord. Ikke skriv personlige helseopplysninger.",
        "trial_statuses": "Registerstatus",
        "trial_statuses_help": (
            "Filtrer studier etter gjeldende status i ClinicalTrials.gov. Status betyr ikke at en studie er egnet, trygg eller effektiv."
        ),
        "trial_statuses_help_simple": "Filtrer studier etter registerstatus.",
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
            "Nylige publikasjoner bruker samme litteratursøk, men starter med de siste par årene valgt. "
            "De er ikke kuraterte gjennombrudd, klinisk veiledning eller medisinske anbefalinger."
        ),
        "recent_intro_simple": "Søk etter nyere Huntington-relaterte artikler fra de siste par årene.",
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
        "knowledge_entity_types_help": (
            "Velg hvilke kontrollerte begrepskategorier som vises. Dette er eksakte begrepstreff, ikke AI-oppdagede relasjoner."
        ),
        "knowledge_entity_types_help_simple": "Velg hvilke begrepstyper som vises.",
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
            "Ingen modell kjores automatisk. Rapporter og embeddings er proveniensartefakter, "
            "ikke biologiske hypoteser, behandlingsrangeringer eller medisinske rad."
        ),
        "protein_lab_symbol": "Symbol",
        "protein_lab_name": "Proteinnavn",
        "protein_lab_entity_id": "Begreps-ID",
        "protein_lab_source": "Kildepost",
        "protein_lab_choose_target": "Proteinmal",
        "protein_lab_choose_target_help": "Velg ett kuratert mal for gjennomgang. Listen er med vilje liten.",
        "protein_lab_choose_target_help_simple": "Velg ett kuratert proteinmal.",
        "protein_lab_open_uniprot": "Apne UniProt-post",
        "protein_lab_mapped_entities": "Koblede begreper",
        "protein_lab_manifests": "Lokale manifester",
        "protein_lab_report_status": "Rapportstatus",
        "protein_lab_report_source": "Rapportkilde",
        "protein_lab_report_source_help": (
            "Bruk katalogen for en stabil malrapport, eller leselisten for a koble lagrede kildeartikler via kontrollerte begrepstreff."
        ),
        "protein_lab_report_source_help_simple": "Velg katalogdata eller lagrede artikler fra leselisten.",
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
        "esm2_lab_title": "Lokalt ESM-2-eksperiment",
        "esm2_lab_intro": (
            "Lag en numerisk representasjon av en proteinsekvens med et lite, lokalt ESM-2-kontrollpunkt. "
            "Modellen kjores bare nar du starter den uttrykkelig."
        ),
        "esm2_lab_scope": (
            "Eksperimentet registrerer proveniens for modell og sekvens. Det predikerer ikke proteinfunksjon, "
            "sykdomsrelevans, behandlingsverdi eller klinisk betydning."
        ),
        "esm2_input_source": "Sekvensgrunnlag",
        "esm2_input_source_help": (
            "Bruk det korte medfolgende fragmentet for en offline grensesnittsjekk, eller hent og mellomlagre "
            "den gjeldende autoritative UniProt-sekvensen uttrykkelig."
        ),
        "esm2_input_source_help_simple": "Velg et testfragment eller en mellomlagret UniProt-sekvens.",
        "esm2_input_fixture": "Medfolgende testfragment",
        "esm2_input_uniprot_cache": "Mellomlagret UniProt-sekvens",
        "esm2_retrieve_uniprot": "Hent eller oppdater fra UniProt",
        "esm2_retrieving": "Henter og validerer UniProt-sekvensen...",
        "esm2_retrieved": "UniProt-sekvensen ble validert og lagret i den lokale brukerbufferen.",
        "esm2_retrieval_failed": "Henting fra UniProt mislyktes: {error}",
        "esm2_no_cached_sequence": "Ingen mellomlagret UniProt-sekvens er tilgjengelig for dette malet enna.",
        "esm2_sequence_length": "Sekvensrester",
        "esm2_sequence_checksum": "Sekvenssjekksum",
        "esm2_sequence_source": "Datakilde",
        "esm2_sequence_details": "Aksessjonsnummer: {accession} | Hentet/registrert: {date}",
        "esm2_window_required": (
            "Sekvensen har {length} rester og overstiger eksperimentgrensen pa {limit}. "
            "Velg et eksplisitt vindu; appen trunkerer aldri i det skjulte."
        ),
        "esm2_window_start": "Start pa vindu (en-basert)",
        "esm2_window_start_help": "Forste rest som tas med i modellgrunnlaget, med en-baserte sekvenskoordinater.",
        "esm2_window_start_help_simple": "Velg den forste resten som skal tas med.",
        "esm2_window_length": "Vinduslengde",
        "esm2_window_length_help": "Antall rester som tas med. v0.10 tillater maksimalt 1 022 rester.",
        "esm2_window_length_help_simple": "Velg hvor mange rester som skal tas med.",
        "esm2_device": "Beregningsenhet",
        "esm2_device_help": "Auto bruker CUDA nar PyTorch har tilgang; CPU er den portable reservelosningen.",
        "esm2_device_help_simple": "Velg automatisk, CPU eller NVIDIA CUDA.",
        "esm2_device_auto": "Auto",
        "esm2_device_cpu": "CPU",
        "esm2_device_cuda": "NVIDIA CUDA",
        "esm2_cached_model_only": "Bruk bare allerede nedlastede modellfiler",
        "esm2_cached_model_only_help": (
            "Hindre nettverkstilgang ved modellasting. Kjoringen mislykkes hvis det pinnede kontrollpunktet ikke er mellomlagret."
        ),
        "esm2_cached_model_only_help_simple": "Ikke last ned modellfiler under denne kjoringen.",
        "esm2_plan_title": "Planlagt ESM-2-manifest",
        "esm2_download_plan": "Last ned ESM-2-plan som JSON",
        "esm2_runtime_ready": "Lokale ESM-2-avhengigheter er tilgjengelige.",
        "esm2_runtime_missing": "Lokal ESM-2 er valgfritt. Manglende pakker: {packages}",
        "esm2_run_confirmation": (
            "Jeg forstar at forste kjoring kan laste ned modellfiler, og at resultatet ikke har klinisk betydning."
        ),
        "esm2_run": "Kjor lokal ESM-2",
        "esm2_running": "Laster det pinnede kontrollpunktet og lager embedding...",
        "esm2_run_complete": "Embedding-artefakten er laget. Kjor samme grunnlag igjen for a sammenligne sjekksummer.",
        "esm2_run_failed": "Lokal ESM-2-kjoring mislyktes: {error}",
        "esm2_dimensions": "Embedding-dimensjoner",
        "esm2_tensor_shape": "Form pa token-tensor",
        "esm2_repeat_status": "Gjentakelsessjekk",
        "esm2_repeat_baseline_recorded": "Referanse registrert",
        "esm2_repeat_matched": "Sjekksum samsvarte",
        "esm2_repeat_different": "Sjekksum var ulik",
        "esm2_repeat_not_comparable": "Kan ikke sammenlignes",
        "esm2_artifact_warning": (
            "Kun en eksperimentell beregningsartefakt. Vektoren er ikke evaluert for en vitenskapelig nedstromsoppgave."
        ),
        "esm2_artifact_title": "Embedding-artefakt og proveniens",
        "esm2_download_artifact": "Last ned embedding-artefakt som JSON",
        "parity_lab_title": "Gjennomgang av leverandørsamsvar",
        "parity_lab_intro": (
            "Sammenlign provenienskontrakten for lokal ESM-2 med en planlagt kjøring i BioNeMo Framework på nøyaktig samme sekvensvindu."
        ),
        "parity_lab_scope": (
            "BioNeMo kjøres ikke her. Samsvar viser bare teknisk kompatibilitet for inndata, ikke like modellvekter, vektorer eller biologisk betydning."
        ),
        "parity_handoff_title": "Ekstern BioNeMo-overføring",
        "parity_handoff_help": (
            "Last ned en pakke uten påloggingsopplysninger for et separat gjennomgått miljø med x86 Linux, Docker og NVIDIA GPU. Kontroller alle filene før kjøring."
        ),
        "parity_prerequisites_docs": "Offisielle maskin- og programvarekrav for BioNeMo",
        "parity_download_execution_bundle": "Last ned kjøringspakke for Linux/GPU",
        "parity_use_fixture": "Bruk offline testresultat",
        "parity_use_fixture_help": (
            "Test resultatvalidering og brukergrensesnitt med deterministiske metadata. Ingen modell, container eller GPU kjøres."
        ),
        "parity_import_result": "Importer BioNeMo-resultat som JSON",
        "parity_import_result_help": (
            "Importer den lille hra-bionemo-result.json som lages av kjøringspakken. Hele vektorer og filer over 1 MB avvises."
        ),
        "parity_import_success": "BioNeMo-resultatet samsvarer med denne nøyaktige planen og bestod strukturvalideringen.",
        "parity_import_failed": "BioNeMo-resultatet ble avvist: {error}",
        "parity_fixture_warning": (
            "Validering med testdata er aktiv. Disse tensorverdiene og sjekksummene er ikke resultat fra BioNeMo-modellen."
        ),
        "parity_input_contract": "Inndatakontrakt klar",
        "parity_bionemo_execution": "BioNeMo-kjøring",
        "parity_planned_only": "Bare planlagt",
        "parity_imported_result": "Importert resultat",
        "parity_fixture_validated": "Testdata validert",
        "parity_unresolved_checks": "Uavklarte kontroller",
        "parity_check": "Kontroll",
        "parity_result": "Resultat",
        "parity_local_reference": "Lokal referanse",
        "parity_bionemo_candidate": "BioNeMo-kandidat",
        "parity_meaning": "Hva dette kontrollerer",
        "parity_not_recorded": "Ikke registrert",
        "parity_status_matched": "Samsvarer",
        "parity_status_different": "Forskjellig",
        "parity_status_not_available": "Ikke tilgjengelig",
        "parity_status_not_comparable": "Kan ikke sammenlignes",
        "parity_field_selected_sequence_checksum": "Sjekksum for valgt sekvens",
        "parity_field_sequence_window": "Sekvensvindu",
        "parity_field_selected_sequence_length": "Lengde på valgt sekvens",
        "parity_field_silent_truncation": "Regel for skjult trunkering",
        "parity_field_model_identity": "Modellidentitet",
        "parity_field_checkpoint_weight_identity": "Identitet for kontrollpunktvekter",
        "parity_field_pooling_method": "Sammenstillingsmetode",
        "parity_field_execution_status": "Kjørestatus",
        "parity_field_embedding_dimensions": "Embedding-dimensjoner",
        "parity_field_token_embeddings_shape": "Form på token-tensor",
        "parity_field_vector_checksum": "Vektorsjekksum",
        "parity_field_runtime_hardware": "Kjøremaskinvare",
        "parity_field_runtime_precision": "Numerisk presisjon",
        "parity_meaning_selected_sequence_checksum": "Kontrollerer om begge leverandører mottar de samme valgte restene.",
        "parity_meaning_sequence_window": "Sammenligner eksplisitte, en-baserte sekvenskoordinater.",
        "parity_meaning_selected_sequence_length": "Sammenligner hvor mange rester som sendes inn.",
        "parity_meaning_silent_truncation": "Krever at HRA avviser trunkering som ikke registreres.",
        "parity_meaning_model_identity": "Sammenligner leverandør, navn på kontrollpunkt og revisjon ordrett.",
        "parity_meaning_checkpoint_weight_identity": "Felles arkitektur beviser ikke at modellvektene er identiske.",
        "parity_meaning_pooling_method": "Lignende navn på gjennomsnittsberegning krever fortsatt validering av implementasjonen.",
        "parity_meaning_execution_status": "En planlagt leverandør har ingen kjøreresultater å sammenligne.",
        "parity_meaning_embedding_dimensions": "Dimensjoner kan først sammenlignes etter at begge leverandører er kjørt.",
        "parity_meaning_token_embeddings_shape": "Tensorformer kan først sammenlignes etter at begge leverandører er kjørt.",
        "parity_meaning_vector_checksum": "Sjekksummer støtter reproduserbarhet; de måler ikke biologisk likhet.",
        "parity_meaning_runtime_hardware": "Maskinvare registreres som proveniens og trenger ikke være lik.",
        "parity_meaning_runtime_precision": "Numerisk presisjon må registreres før resultatene sammenlignes.",
        "parity_sources": "Offisiell BioNeMo-dokumentasjon brukt til å definere planen:",
        "parity_bionemo_model_docs": "Dokumentasjon for ESM-2-modell og kontrollpunkt",
        "parity_bionemo_inference_docs": "Dokumentasjon for ESM-2-inferens",
        "parity_bionemo_plan_title": "Planlagt BioNeMo ESM-2-manifest",
        "parity_report_title": "Rapport for leverandørsamsvar",
        "parity_download_bionemo_plan": "Last ned BioNeMo-plan som JSON",
        "parity_download_report": "Last ned samsvarsrapport som JSON",
        "blueprint_lab_title": "Blueprint-labforhåndsvisning",
        "blueprint_lab_intro": (
            "Denne visningen viser hvordan et kuratert mål, en leverandørgrense, et eksperimentmanifest "
            "og en provenienspost henger sammen før live-kjøring av vitenskapelig KI aktiveres."
        ),
        "blueprint_lab_scope": (
            "Blueprint-artefakter er bare tekniske proveniensposter. De er ikke modellvaliderte funn, "
            "klinisk evidens, behandlingsveiledning eller medisinske råd."
        ),
        "blueprint_lab_workflow_title": "Arbeidsflyt",
        "blueprint_lab_workflow_target": "Trinn 1: Velg et kuratert mål",
        "blueprint_lab_workflow_provider": "Trinn 2: Se leverandørgrensen",
        "blueprint_lab_workflow_manifest": "Trinn 3: Gå gjennom planlagt artefakt",
        "blueprint_lab_workflow_provenance": "Trinn 4: Kontroller registrert proveniens",
        "blueprint_lab_provider": "Leverandørfamilie",
        "blueprint_lab_provider_help": (
            "Velg en leverandørfamilie å planlegge for. Bare mock-leverandøren kan lage en offline testpost nå."
        ),
        "blueprint_lab_provider_help_simple": "Velg leverandørfamilie. Bare mock-kjøringer utføres offline.",
        "blueprint_lab_execution_mode": "Kjøremodus",
        "blueprint_lab_execution_mode_help": (
            "Forhåndsvisningen viser bare moduser den trygt kan utføre: offline testdata for mock, "
            "eller planlagte manifester for leverandører uten en aktivert live-adapter."
        ),
        "blueprint_lab_execution_mode_help_simple": "Mock bruker offline testdata; andre leverandører er bare planlagt.",
        "blueprint_mode_offline": "Offline testdata",
        "blueprint_mode_planned": "Bare planlagt",
        "blueprint_mode_live": "Live-leverandør",
        "blueprint_lab_provider_status": "Leverandørstatus",
        "blueprint_lab_provider_mock_fixture": "Mock-testdata",
        "blueprint_lab_provider_mock_fixture_detail": (
            "Denne leverandøren bruker bare deterministiske lokale testdata. Den kaller ikke modell, API, GPU eller ekstern tjeneste."
        ),
        "blueprint_lab_provider_public_data_gated": "Offentlige data / sperret",
        "blueprint_lab_provider_public_data_gated_detail": (
            "Denne leverandøren beskriver offentlig kildeproveniens. Live-henting er fortsatt eksplisitt og sperret, og ingen tolkning produseres."
        ),
        "blueprint_lab_provider_planned_only": "Bare planlagt",
        "blueprint_lab_provider_planned_only_detail": (
            "Denne leverandørfamilien er bare et planleggingsmål. Den registrerer hva som ville blitt kjørt, uten å kjøre en live-leverandør."
        ),
        "blueprint_lab_provider_live_ready": "Live gjennomgått",
        "blueprint_lab_provider_live_ready_detail": (
            "Denne leverandøren har en eksplisitt gjennomgått live-konfigurasjon. Brukes bare til avgrensede labkjøringer med registrert proveniens."
        ),
        "blueprint_lab_live_enabled": "Live aktivert",
        "blueprint_lab_implemented": "Adapter tilgjengelig",
        "blueprint_lab_credentials": "Trenger credentials",
        "blueprint_lab_target": "Blueprint-mål",
        "blueprint_lab_target_help": "Velg ett kuratert proteinmål for planlagt eller mock-basert artefakt.",
        "blueprint_lab_target_help_simple": "Velg ett kuratert proteinmål.",
        "blueprint_lab_registry_records": "Registerposter",
        "blueprint_lab_registry_valid": "Gyldige",
        "blueprint_lab_registry_invalid": "Ugyldige",
        "blueprint_lab_experiment_id": "Eksperiment-ID",
        "blueprint_lab_status": "Status",
        "blueprint_lab_targets": "Mål",
        "blueprint_lab_artifact_type": "Artefakttype",
        "blueprint_lab_valid": "Gyldig",
        "blueprint_lab_checksum": "Sjekksum",
        "blueprint_lab_no_registry_records": "Ingen lokale Blueprint-manifester ble funnet.",
        "blueprint_lab_registry_title": "Lokalt artefaktregister",
        "blueprint_lab_registry_help": (
            "Registeret indekserer lagrede manifestfiler og sjekksummene deres. Det kjører ikke leverandører eller tolker resultater."
        ),
        "blueprint_lab_planned_manifest": "Planlagt Blueprint-manifest",
        "blueprint_lab_planned_manifest_help": (
            "Dette registrerer valgt mål og leverandørgrense uten å kalle leverandøren."
        ),
        "blueprint_lab_mock_manifest": "Mock-basert Blueprint-manifest",
        "blueprint_lab_mock_manifest_help": (
            "Disse deterministiske testdataene er bare tilgjengelige for mock-leverandøren og er ikke modellresultater."
        ),
        "blueprint_lab_download_plan": "Last ned planlagt manifest som JSON",
        "blueprint_lab_download_mock": "Last ned mock-manifest som JSON",
        "blueprint_lab_download_registry": "Last ned register som JSON",
        "blueprint_lab_cli_title": "Blueprint CLI-sjekker",
        "blueprint_lab_cli_help": "Tilsvarende offline-kommandoer for gjennomgang av Blueprint-manifester utenfor appen.",
        "blueprint_provider_alphafold": "AlphaFold / strukturarbeidsflyt",
        "blueprint_provider_bionemo": "BioNeMo",
        "blueprint_provider_mock": "Mock-testdata",
        "blueprint_provider_nvidia_blueprint": "NVIDIA Blueprint",
        "blueprint_provider_nvidia_nim": "NVIDIA NIM",
        "blueprint_provider_other": "Annen leverandør",
        "blueprint_provider_uniprot": "UniProt offentlige data",
    },
}


def translate(language: str, key: str, **values: object) -> str:
    selected = TRANSLATIONS.get(language, TRANSLATIONS["en"])
    template = selected.get(key, TRANSLATIONS["en"].get(key, key))
    return template.format(**values)
