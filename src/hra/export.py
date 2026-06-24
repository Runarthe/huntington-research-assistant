from __future__ import annotations

import csv
import re
from io import StringIO

from hra.models import ClinicalTrial, Paper


def paper_to_text(paper: Paper) -> str:
    """Serialize one paper as readable UTF-8 text with source attribution."""

    fields = [
        paper.title,
        "",
        f"Authors: {', '.join(author.full_name for author in paper.authors) or 'Not listed'}",
        f"Year: {paper.year or 'Not listed'}",
        f"Journal: {paper.journal or 'Not listed'}",
        f"DOI: {paper.doi or 'Not listed'}",
        f"PMID: {paper.pmid or 'Not listed'}",
        f"Source: {paper.source_url or 'Not available'}",
    ]
    if paper.open_access_full_text_url:
        fields.append(f"Open-access full text: {paper.open_access_full_text_url}")
    if paper.open_access_pdf_url:
        fields.append(f"Open-access PDF: {paper.open_access_pdf_url}")
    fields.extend(["", "Abstract", "--------", paper.abstract or "No abstract available."])
    return "\n".join(str(field) for field in fields) + "\n"


def paper_text_filename(paper: Paper) -> str:
    """Return a filesystem-friendly filename for one paper export."""

    identifier = paper.pmid or paper.doi or paper.id
    safe_identifier = re.sub(r"[^A-Za-z0-9._-]", "-", identifier).strip("-.")
    return f"hra-paper-{safe_identifier or 'details'}.txt"


def papers_to_csv(papers: list[Paper]) -> str:
    """Serialize the visible paper page to a portable CSV file."""

    output = StringIO(newline="")
    fieldnames = [
        "title",
        "authors",
        "year",
        "journal",
        "publication_types",
        "doi",
        "pmid",
        "open_access",
        "citation_count",
        "tags",
        "source_url",
        "open_access_full_text_url",
        "open_access_pdf_url",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for paper in papers:
        writer.writerow(
            {
                "title": paper.title,
                "authors": "; ".join(author.full_name for author in paper.authors),
                "year": paper.year or "",
                "journal": paper.journal or "",
                "publication_types": "; ".join(paper.publication_types),
                "doi": paper.doi or "",
                "pmid": paper.pmid or "",
                "open_access": paper.is_open_access,
                "citation_count": paper.citation_count if paper.citation_count is not None else "",
                "tags": "; ".join(paper.tags),
                "source_url": str(paper.source_url or ""),
                "open_access_full_text_url": str(paper.open_access_full_text_url or ""),
                "open_access_pdf_url": str(paper.open_access_pdf_url or ""),
            }
        )
    return output.getvalue()


def papers_to_bibtex(papers: list[Paper]) -> str:
    """Serialize the visible paper page as basic BibTeX entries."""

    entries: list[str] = []
    used_keys: set[str] = set()
    for index, paper in enumerate(papers, start=1):
        key = _citation_key(paper, index)
        while key in used_keys:
            key = f"{key}_{index}"
        used_keys.add(key)

        fields = {
            "title": paper.title,
            "author": " and ".join(author.full_name for author in paper.authors),
            "journal": paper.journal or "",
            "year": str(paper.year or ""),
            "doi": paper.doi or "",
            "pmid": paper.pmid or "",
            "url": str(paper.source_url or ""),
        }
        lines = [f"@article{{{key},"]
        lines.extend(
            f"  {name} = {{{_bibtex_escape(value)}}},"
            for name, value in fields.items()
            if value
        )
        lines.append("}")
        entries.append("\n".join(lines))
    return "\n\n".join(entries) + ("\n" if entries else "")


def trials_to_csv(trials: list[ClinicalTrial]) -> str:
    """Serialize the visible trial list while preserving source links."""

    output = StringIO(newline="")
    fieldnames = [
        "nct_id",
        "title",
        "status",
        "phases",
        "interventions",
        "sponsor",
        "enrollment",
        "countries",
        "start_date",
        "completion_date",
        "last_update",
        "source_url",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for trial in trials:
        writer.writerow(
            {
                "nct_id": trial.nct_id,
                "title": trial.brief_title,
                "status": trial.overall_status,
                "phases": "; ".join(trial.phases),
                "interventions": "; ".join(trial.interventions),
                "sponsor": trial.sponsor or "",
                "enrollment": trial.enrollment if trial.enrollment is not None else "",
                "countries": "; ".join(trial.countries),
                "start_date": trial.start_date or "",
                "completion_date": trial.completion_date or "",
                "last_update": trial.last_update or "",
                "source_url": str(trial.source_url),
            }
        )
    return output.getvalue()


def _citation_key(paper: Paper, index: int) -> str:
    author = paper.authors[0].full_name.split()[-1] if paper.authors else "paper"
    raw = f"{author}{paper.year or ''}{paper.id or index}"
    return re.sub(r"[^A-Za-z0-9_-]", "", raw) or f"paper{index}"


def _bibtex_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}")
