from hra.knowledge_graph import build_research_map, extract_mentions, graphviz_dot
from hra.models import Paper


def test_extracts_conservative_entities_with_source_evidence() -> None:
    paper = Paper(
        id="paper-1",
        title="A study of the HTT gene",
        abstract=(
            "Mutant huntingtin was measured in a cell model. "
            "The study also examined autophagy and tominersen."
        ),
        source_url="https://europepmc.org/article/MED/1",
    )

    mentions = extract_mentions(paper)
    by_name = {mention.entity_name: mention for mention in mentions}

    assert set(by_name) == {"HTT", "huntingtin protein", "autophagy", "tominersen"}
    assert by_name["HTT"].evidence_location == "title"
    assert by_name["autophagy"].evidence == (
        "The study also examined autophagy and tominersen."
    )
    assert by_name["tominersen"].source_url == "https://europepmc.org/article/MED/1"


def test_short_aliases_do_not_match_inside_other_words() -> None:
    paper = Paper(
        id="paper-2",
        title="Inflammatory patterns",
        abstract="The workflow uses fan1like as an internal label.",
    )

    assert extract_mentions(paper) == []


def test_research_map_counts_only_papers_with_mentions() -> None:
    papers = [
        Paper(id="p1", title="Autophagy in Huntington disease"),
        Paper(id="p2", title="A paper without catalogued entities"),
    ]

    research_map = build_research_map(papers)

    assert research_map.paper_count == 1
    assert [entity.name for entity in research_map.entities] == ["autophagy"]


def test_graphviz_output_uses_mention_relationship_only() -> None:
    paper = Paper(id="p1", title='Autophagy in "HD" research')
    mentions = extract_mentions(paper)

    dot = graphviz_dot(mentions)

    assert "mentioned in" in dot
    assert "treats" not in dot
    assert '\\"HD\\"' in dot


def test_graphviz_output_can_hide_repeated_edge_labels_and_limit_papers() -> None:
    papers = [
        Paper(id=f"p{index}", title=f"Autophagy paper {index}")
        for index in range(10)
    ]
    mentions = [mention for paper in papers for mention in extract_mentions(paper)]

    dot = graphviz_dot(mentions, max_papers=3, show_relationship_labels=False)

    assert "Autophagy paper 0" in dot
    assert "Autophagy paper 2" in dot
    assert "Autophagy paper 3" not in dot
    assert 'label=" mentioned in "' not in dot
