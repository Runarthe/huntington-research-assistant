from __future__ import annotations

import csv
import io
import re

from pydantic import BaseModel, Field

from hra.models import Paper


class EvidenceProfile(BaseModel):
    """Conservative metadata and exact abstract passages for comparison."""

    paper_id: str
    title: str
    year: int | None = None
    source_provider: str
    source_url: str | None = None
    study_design: str
    research_contexts: list[str] = Field(default_factory=list)
    outcome_passages: list[str] = Field(default_factory=list)
    limitation_passages: list[str] = Field(default_factory=list)
    has_abstract: bool
    is_retracted: bool
    has_correction: bool


_SENTENCE_PATTERN = re.compile(r"(?<=[.!?])\s+")
_OUTCOME_PATTERNS = (
    re.compile(r"^(?:results?|findings?)\s*:", re.IGNORECASE),
    re.compile(
        r"\bwe (?:found|observed|showed|demonstrated|identified|report)\b",
        re.IGNORECASE,
    ),
    re.compile(r"\b(?:was|were) associated with\b", re.IGNORECASE),
)
_LIMITATION_PATTERNS = (
    re.compile(r"\blimitations?\b", re.IGNORECASE),
    re.compile(r"\blimited by\b", re.IGNORECASE),
    re.compile(r"\buncertain(?:ty|ties)?\b", re.IGNORECASE),
    re.compile(r"\bremains? (?:unclear|unknown)\b", re.IGNORECASE),
    re.compile(r"\bsmall sample\b", re.IGNORECASE),
    re.compile(r"\bfurther (?:research|studies|work)\b", re.IGNORECASE),
    re.compile(r"\binterpreted with caution\b", re.IGNORECASE),
)
_CONTEXT_PATTERNS: dict[str, tuple[re.Pattern[str], ...]] = {
    "human_participants": (
        re.compile(r"\bpatient-derived\b", re.IGNORECASE),
        re.compile(r"\bwe (?:enrolled|recruited|included|studied|assessed)\b[^.]*\b(?:patients?|participants?)\b", re.IGNORECASE),
        re.compile(
            r"\b\d+(?:\s+\w+){0,3}\s+(?:patients?|participants?|donors?)\b",
            re.IGNORECASE,
        ),
        re.compile(r"\bhuman\b[^.]{0,60}\b(?:participants?|subjects?|patients?|samples?|tissues?|cells?|donors?)\b", re.IGNORECASE),
        re.compile(r"\bpostmortem\b", re.IGNORECASE),
    ),
    "animal_model": (
        re.compile(r"\banimal models?\b", re.IGNORECASE),
        re.compile(r"\b(?:mouse|mice|murine|rats?|rodents?)\b", re.IGNORECASE),
        re.compile(r"\b(?:minipigs?|zebrafish|drosophila|non-human primates?)\b", re.IGNORECASE),
    ),
    "cell_or_tissue_model": (
        re.compile(r"\bcell(?:ular|s| lines?)?\b", re.IGNORECASE),
        re.compile(r"\b(?:iPSC|induced pluripotent stem cells?|organoids?)\b", re.IGNORECASE),
        re.compile(r"\b(?:in vitro|ex vivo|tissue samples?)\b", re.IGNORECASE),
    ),
    "computational_model": (
        re.compile(r"\b(?:in silico|computational|bioinformatic(?:s| analyses?)?)\b", re.IGNORECASE),
        re.compile(r"\bmolecular dynamics\b", re.IGNORECASE),
    ),
}
_MOLECULAR_EXPERIMENT_PATTERNS = (
    re.compile(r"\b(?:CRISPR|dCas9|gene editing|epigenetic editing)\b", re.IGNORECASE),
    re.compile(r"\b(?:DNA methylation|RNA interference|microRNA|miRNA)\b", re.IGNORECASE),
    re.compile(r"\b(?:gene silencing|knockdown|knockout)\b", re.IGNORECASE),
    re.compile(r"\b(?:PCR|transcriptomic|proteomic)\b", re.IGNORECASE),
)


def _sentences(text: str | None) -> list[str]:
    if not text:
        return []
    normalized = " ".join(text.split())
    return [sentence.strip() for sentence in _SENTENCE_PATTERN.split(normalized) if sentence.strip()]


def _matching_passages(
    text: str | None,
    patterns: tuple[re.Pattern[str], ...],
    limit: int = 3,
) -> list[str]:
    matches: list[str] = []
    for sentence in _sentences(text):
        if any(pattern.search(sentence) for pattern in patterns):
            matches.append(sentence)
        if len(matches) >= limit:
            break
    return matches


def detect_research_contexts(paper: Paper) -> list[str]:
    text = f"{paper.title} {paper.abstract or ''}"
    contexts = [
        context
        for context, patterns in _CONTEXT_PATTERNS.items()
        if any(pattern.search(text) for pattern in patterns)
    ]
    if not contexts and any(pattern.search(text) for pattern in _MOLECULAR_EXPERIMENT_PATTERNS):
        contexts.append("molecular_experiment")
    return contexts


def classify_study_design(paper: Paper, contexts: list[str] | None = None) -> str:
    publication_text = " ".join(paper.publication_types).lower()
    full_text = f"{paper.title} {paper.abstract or ''}".lower()
    detected_contexts = contexts if contexts is not None else detect_research_contexts(paper)

    if "meta-analysis" in publication_text or "meta-analysis" in full_text:
        return "meta_analysis"
    if "systematic review" in publication_text or "systematic review" in full_text:
        return "systematic_review"
    if "randomized controlled trial" in publication_text:
        return "randomized_controlled_trial"
    if "clinical trial" in publication_text:
        return "clinical_trial"
    if paper.is_review:
        return "review"
    if re.search(r"\brandomi[sz]ed controlled trial\b", full_text):
        return "randomized_controlled_trial"
    if "clinical trial" in full_text:
        return "clinical_trial"
    if "case report" in publication_text:
        return "case_report"
    if any(
        term in full_text
        for term in ("cohort study", "cross-sectional", "case-control", "longitudinal study")
    ):
        return "observational_study"
    if {"animal_model", "cell_or_tissue_model"}.intersection(detected_contexts):
        return "preclinical_study"
    if "human_participants" in detected_contexts:
        return "human_study"
    if "molecular_experiment" in detected_contexts:
        return "laboratory_study"
    if "preprint" in publication_text:
        return "preprint"
    if publication_text:
        return "journal_article"
    return "not_classified"


def extract_evidence_profile(paper: Paper) -> EvidenceProfile:
    """Build a comparison profile without inferring efficacy or evidence quality."""

    contexts = detect_research_contexts(paper)
    return EvidenceProfile(
        paper_id=paper.id,
        title=paper.title,
        year=paper.year,
        source_provider=paper.source_provider,
        source_url=str(paper.source_url) if paper.source_url else None,
        study_design=classify_study_design(paper, contexts),
        research_contexts=contexts,
        outcome_passages=_matching_passages(paper.abstract, _OUTCOME_PATTERNS),
        limitation_passages=_matching_passages(paper.abstract, _LIMITATION_PATTERNS),
        has_abstract=bool(paper.abstract),
        is_retracted=paper.is_retracted,
        has_correction=paper.has_correction,
    )


def build_evidence_profiles(papers: list[Paper]) -> list[EvidenceProfile]:
    return [extract_evidence_profile(paper) for paper in papers]


def evidence_profiles_to_csv(profiles: list[EvidenceProfile]) -> str:
    output = io.StringIO(newline="")
    fieldnames = [
        "paper_id",
        "title",
        "year",
        "source_provider",
        "source_url",
        "study_design",
        "research_contexts",
        "outcome_passages",
        "limitation_passages",
        "has_abstract",
        "is_retracted",
        "has_correction",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for profile in profiles:
        row = profile.model_dump()
        row["research_contexts"] = "; ".join(profile.research_contexts)
        row["outcome_passages"] = "\n".join(profile.outcome_passages)
        row["limitation_passages"] = "\n".join(profile.limitation_passages)
        writer.writerow(row)
    return output.getvalue()
