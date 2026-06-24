# Experimental Research Map

A knowledge graph represents named things as nodes and relationships as edges. In this project, a paper and a catalogued biomedical term are nodes. An edge currently means only that the term was **mentioned in** the paper's title or abstract.

For example:

```text
autophagy -> mentioned in -> Paper A
HTT gene  -> mentioned in -> Paper A
tominersen -> mentioned in -> Paper B
```

This can help readers find papers connected by recurring terminology. It does not show that one entity causes, treats, improves, or is clinically relevant to another.

## Current Implementation

- The research map has its own Streamlit tab and Europe PMC search state.
- Entity extraction is deterministic and uses a small reviewed-in-code vocabulary.
- Initial entity types are genes, proteins, pathways or biological processes, and compounds.
- Every mention keeps the exact title or abstract sentence, matched alias, paper title, and Europe PMC source URL.
- The graph is bounded for readability and has a source-evidence view beneath it.
- No LLM is used for entity extraction or relationship generation.

The controlled vocabulary is defined in `src/hra/knowledge_graph.py`. New aliases should be specific enough to avoid substring matches and ambiguous biomedical meanings.

## Important Limitations

- A mention is not evidence of a biological relationship.
- The vocabulary is intentionally small, so many valid entities will be missed.
- Alias matching cannot resolve every gene/protein ambiguity.
- The tool does not rank evidence quality or identify scientific consensus.
- Only metadata and abstracts returned by Europe PMC are inspected.
- Users must open the linked source paper to interpret context.

## Next Validation Steps

1. Build a manually reviewed set of representative Huntington research abstracts.
2. Measure false positives and missed entities separately for each entity type.
3. Link entities to stable identifiers such as HGNC, UniProt, ChEBI, and Reactome only after identifier mappings are manually checked.
4. Add new relationship types only when each relationship can be tied to an exact supporting passage and independently evaluated.
5. Keep an accessible tabular evidence view even if the visual graph becomes more capable.
