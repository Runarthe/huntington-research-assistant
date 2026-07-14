from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, Field

from hra.models import Paper


EntityType = Literal["gene", "protein", "biomarker", "pathway", "compound"]
MentionConfidence = Literal["high", "medium"]
ExtractionMethod = Literal["controlled_vocabulary_alias"]

ENTITY_CATALOG_VERSION = "0.5"


@dataclass(frozen=True)
class ControlledEntity:
    id: str
    name: str
    entity_type: EntityType
    aliases: tuple[str, ...]
    case_sensitive_aliases: tuple[str, ...] = ()
    medium_confidence_aliases: tuple[str, ...] = ()


class KnowledgeEntity(BaseModel):
    id: str
    name: str
    entity_type: EntityType
    aliases: list[str] = Field(default_factory=list)


class EntityMention(BaseModel):
    entity_id: str
    entity_name: str
    entity_type: EntityType
    paper_id: str
    paper_title: str
    source_url: str | None = None
    matched_alias: str
    evidence: str
    evidence_location: Literal["title", "abstract"]
    extraction_method: ExtractionMethod = "controlled_vocabulary_alias"
    mention_confidence: MentionConfidence = "high"


class EntityConnection(BaseModel):
    """A paper-level co-occurrence, not an asserted biological relationship."""

    entity_id: str
    entity_name: str
    entity_type: EntityType
    shared_paper_count: int
    paper_ids: list[str] = Field(default_factory=list)


class ResearchMap(BaseModel):
    entities: list[KnowledgeEntity] = Field(default_factory=list)
    mentions: list[EntityMention] = Field(default_factory=list)
    paper_count: int = 0
    catalog_version: str = ENTITY_CATALOG_VERSION


ENTITY_CATALOG: tuple[ControlledEntity, ...] = (
    ControlledEntity("gene-htt", "HTT", "gene", ("HTT gene", "huntingtin gene")),
    ControlledEntity(
        "gene-msh3", "MSH3", "gene", ("MSH3",), case_sensitive_aliases=("MSH3",)
    ),
    ControlledEntity(
        "gene-fan1", "FAN1", "gene", ("FAN1",), case_sensitive_aliases=("FAN1",)
    ),
    ControlledEntity(
        "protein-huntingtin",
        "huntingtin protein",
        "protein",
        ("huntingtin protein", "mutant huntingtin", "mHTT"),
    ),
    ControlledEntity(
        "biomarker-nfl",
        "neurofilament light",
        "biomarker",
        (
            "neurofilament light",
            "neurofilament light chain",
            "plasma neurofilament light",
            "CSF neurofilament light",
            "NfL",
        ),
        case_sensitive_aliases=("NfL",),
        medium_confidence_aliases=("NfL",),
    ),
    ControlledEntity(
        "protein-bdnf", "BDNF", "protein", ("BDNF",), case_sensitive_aliases=("BDNF",)
    ),
    ControlledEntity("pathway-autophagy", "autophagy", "pathway", ("autophagy",)),
    ControlledEntity(
        "pathway-dna-repair",
        "DNA repair",
        "pathway",
        ("DNA repair", "mismatch repair"),
    ),
    ControlledEntity(
        "pathway-somatic-expansion",
        "somatic CAG expansion",
        "pathway",
        ("somatic CAG expansion", "somatic expansion"),
    ),
    ControlledEntity(
        "pathway-ubiquitin-proteasome",
        "ubiquitin-proteasome system",
        "pathway",
        ("ubiquitin-proteasome system", "proteasome pathway"),
    ),
    ControlledEntity(
        "pathway-mitochondrial",
        "mitochondrial function",
        "pathway",
        ("mitochondrial function", "mitochondrial dysfunction"),
    ),
    ControlledEntity(
        "pathway-neuroinflammation",
        "neuroinflammation",
        "pathway",
        ("neuroinflammation", "neuroinflammatory"),
    ),
    ControlledEntity("compound-tominersen", "tominersen", "compound", ("tominersen",)),
    ControlledEntity("compound-branaplam", "branaplam", "compound", ("branaplam",)),
    ControlledEntity("compound-pridopidine", "pridopidine", "compound", ("pridopidine",)),
    ControlledEntity(
        "compound-deutetrabenazine",
        "deutetrabenazine",
        "compound",
        ("deutetrabenazine",),
    ),
    ControlledEntity("compound-valbenazine", "valbenazine", "compound", ("valbenazine",)),
)


_SENTENCE_PATTERN = re.compile(r"(?<=[.!?])\s+")


def _alias_pattern(alias: str, *, case_sensitive: bool = False) -> re.Pattern[str]:
    return re.compile(
        rf"(?<![A-Za-z0-9]){re.escape(alias)}(?![A-Za-z0-9])",
        0 if case_sensitive else re.IGNORECASE,
    )


def _matching_evidence(
    text: str,
    alias: str,
    *,
    case_sensitive: bool = False,
) -> str | None:
    pattern = _alias_pattern(alias, case_sensitive=case_sensitive)
    for sentence in _SENTENCE_PATTERN.split(" ".join(text.split())):
        if pattern.search(sentence):
            return sentence.strip()
    return None


def extract_mentions(paper: Paper) -> list[EntityMention]:
    """Extract conservative vocabulary mentions with exact source evidence."""

    mentions: list[EntityMention] = []
    sources = (("title", paper.title), ("abstract", paper.abstract or ""))
    for entity in ENTITY_CATALOG:
        match: tuple[str, str, str] | None = None
        for location, text in sources:
            for alias in sorted(entity.aliases, key=len, reverse=True):
                evidence = _matching_evidence(
                    text,
                    alias,
                    case_sensitive=alias in entity.case_sensitive_aliases,
                )
                if evidence:
                    match = (location, alias, evidence)
                    break
            if match:
                break
        if not match:
            continue

        location, alias, evidence = match
        mentions.append(
            EntityMention(
                entity_id=entity.id,
                entity_name=entity.name,
                entity_type=entity.entity_type,
                paper_id=paper.id,
                paper_title=paper.title,
                source_url=str(paper.source_url) if paper.source_url else None,
                matched_alias=alias,
                evidence=evidence,
                evidence_location=location,
                mention_confidence=(
                    "medium"
                    if alias in entity.medium_confidence_aliases
                    else "high"
                ),
            )
        )
    return mentions


def build_research_map(papers: list[Paper]) -> ResearchMap:
    mentions = [mention for paper in papers for mention in extract_mentions(paper)]
    entity_ids = {mention.entity_id for mention in mentions}
    entities = [
        KnowledgeEntity(
            id=entity.id,
            name=entity.name,
            entity_type=entity.entity_type,
            aliases=list(entity.aliases),
        )
        for entity in ENTITY_CATALOG
        if entity.id in entity_ids
    ]
    return ResearchMap(
        entities=entities,
        mentions=mentions,
        paper_count=len({mention.paper_id for mention in mentions}),
    )


def build_entity_connections(
    research_map: ResearchMap,
    selected_entity_id: str,
) -> list[EntityConnection]:
    """Find entities catalogued in the same papers as the selected entity."""

    selected_papers = {
        mention.paper_id
        for mention in research_map.mentions
        if mention.entity_id == selected_entity_id
    }
    papers_by_entity: dict[str, set[str]] = {}
    for mention in research_map.mentions:
        if mention.entity_id == selected_entity_id or mention.paper_id not in selected_papers:
            continue
        papers_by_entity.setdefault(mention.entity_id, set()).add(mention.paper_id)

    entities = {entity.id: entity for entity in research_map.entities}
    connections = [
        EntityConnection(
            entity_id=entity_id,
            entity_name=entities[entity_id].name,
            entity_type=entities[entity_id].entity_type,
            shared_paper_count=len(paper_ids),
            paper_ids=sorted(paper_ids),
        )
        for entity_id, paper_ids in papers_by_entity.items()
        if entity_id in entities
    ]
    return sorted(
        connections,
        key=lambda connection: (
            -connection.shared_paper_count,
            connection.entity_name.casefold(),
        ),
    )


def graphviz_dot(
    mentions: list[EntityMention],
    max_entities: int = 12,
    max_papers: int = 8,
    relationship_label: str = "mentioned in",
    show_relationship_labels: bool = True,
) -> str:
    """Build a bounded entity-to-paper mention graph for Streamlit."""

    selected_entity_ids: list[str] = []
    for mention in mentions:
        if mention.entity_id not in selected_entity_ids:
            selected_entity_ids.append(mention.entity_id)
        if len(selected_entity_ids) >= max_entities:
            break

    entity_mentions = [
        mention for mention in mentions if mention.entity_id in selected_entity_ids
    ]
    selected_paper_ids: list[str] = []
    for mention in entity_mentions:
        if mention.paper_id not in selected_paper_ids:
            selected_paper_ids.append(mention.paper_id)
        if len(selected_paper_ids) >= max_papers:
            break
    visible_mentions = [
        mention for mention in entity_mentions if mention.paper_id in selected_paper_ids
    ]
    entity_nodes = {
        mention.entity_id: (mention.entity_name, mention.entity_type)
        for mention in visible_mentions
    }
    paper_nodes = {
        mention.paper_id: mention.paper_title for mention in visible_mentions
    }
    colors = {
        "gene": "#3b82f6",
        "protein": "#22c55e",
        "biomarker": "#06b6d4",
        "pathway": "#f59e0b",
        "compound": "#ef4444",
    }

    def escaped(value: str, limit: int = 58) -> str:
        shortened = value if len(value) <= limit else f"{value[: limit - 3]}..."
        return shortened.replace("\\", "\\\\").replace('"', '\\"')

    lines = [
        "digraph research_map {",
        'rankdir="LR";',
        'graph [bgcolor="transparent", pad="0.2", nodesep="0.35", ranksep="0.8"];',
        'node [fontname="Arial", fontsize="10", fontcolor="white"];',
        'edge [color="#64748b", arrowsize="0.65"];',
    ]
    for index, (entity_id, (name, entity_type)) in enumerate(entity_nodes.items()):
        lines.append(
            f'e{index} [label="{escaped(name)}", shape="box", style="filled", '
            f'fillcolor="{colors[entity_type]}", tooltip="{escaped(entity_type)}"];'
        )
    for index, (paper_id, title) in enumerate(paper_nodes.items()):
        lines.append(
            f'p{index} [label="{escaped(title)}", shape="ellipse", style="filled", '
            'fillcolor="#374151"];'
        )

    entity_indexes = {entity_id: index for index, entity_id in enumerate(entity_nodes)}
    paper_indexes = {paper_id: index for index, paper_id in enumerate(paper_nodes)}
    for mention in visible_mentions:
        edge_label = (
            f'label=" {escaped(relationship_label)} ", fontsize="8", '
            'fontcolor="#94a3b8"'
            if show_relationship_labels
            else 'tooltip="mentioned in"'
        )
        lines.append(
            f'e{entity_indexes[mention.entity_id]} -> p{paper_indexes[mention.paper_id]} '
            f'[{edge_label}];'
        )
    lines.append("}")
    return "\n".join(lines)
