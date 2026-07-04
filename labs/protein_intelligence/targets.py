from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import date
from typing import Literal


DatabaseName = Literal["uniprot", "hgnc", "ncbi_gene"]


@dataclass(frozen=True)
class ProteinTarget:
    """A bounded protein target with stable source identifiers."""

    entity_id: str
    symbol: str
    name: str
    organism: str
    identifiers: dict[DatabaseName, str]
    notes: str

    @property
    def uniprot_url(self) -> str:
        return f"https://www.uniprot.org/uniprotkb/{self.identifiers['uniprot']}/entry"

    @property
    def uniprot_fasta_url(self) -> str:
        return f"https://rest.uniprot.org/uniprotkb/{self.identifiers['uniprot']}.fasta"


PROTEIN_TARGETS: tuple[ProteinTarget, ...] = (
    ProteinTarget(
        entity_id="protein-huntingtin",
        symbol="HTT",
        name="huntingtin",
        organism="Homo sapiens",
        identifiers={
            "uniprot": "P42858",
            "hgnc": "HGNC:4851",
            "ncbi_gene": "3064",
        },
        notes="Primary Huntington disease protein target for bounded sequence workflows.",
    ),
    ProteinTarget(
        entity_id="protein-bdnf",
        symbol="BDNF",
        name="brain-derived neurotrophic factor",
        organism="Homo sapiens",
        identifiers={
            "uniprot": "P23560",
            "hgnc": "HGNC:1033",
            "ncbi_gene": "627",
        },
        notes="Catalogued v0.5 protein entity; useful as a smaller fixture than HTT.",
    ),
    ProteinTarget(
        entity_id="biomarker-nfl",
        symbol="NEFL",
        name="neurofilament light polypeptide",
        organism="Homo sapiens",
        identifiers={
            "uniprot": "P07196",
            "hgnc": "HGNC:7739",
            "ncbi_gene": "4747",
        },
        notes="Protein source for the neurofilament-light biomarker entity.",
    ),
)


def get_protein_target(value: str) -> ProteinTarget:
    """Find a target by entity ID, symbol, or stable source identifier."""

    normalized = value.casefold()
    for target in PROTEIN_TARGETS:
        if normalized in {
            target.entity_id.casefold(),
            target.symbol.casefold(),
            *(identifier.casefold() for identifier in target.identifiers.values()),
        }:
            return target
    known = ", ".join(target.symbol for target in PROTEIN_TARGETS)
    raise KeyError(f"Unknown protein target '{value}'. Known targets: {known}.")


def parse_fasta_sequence(fasta_text: str) -> str:
    """Return a normalized amino-acid sequence from a FASTA record."""

    sequence = "".join(
        line.strip()
        for line in fasta_text.splitlines()
        if line.strip() and not line.startswith(">")
    )
    if not sequence:
        raise ValueError("FASTA record does not contain a sequence.")
    if not sequence.isalpha():
        raise ValueError("FASTA sequence contains non-letter characters.")
    return sequence.upper()


def fasta_sha256(fasta_text: str) -> str:
    sequence = parse_fasta_sequence(fasta_text)
    digest = hashlib.sha256(sequence.encode("ascii")).hexdigest()
    return f"sha256:{digest}"


def planned_sequence_manifest(
    target: ProteinTarget,
    *,
    retrieved_at: date | None = None,
) -> dict[str, object]:
    """Create a planned experiment manifest for sequence retrieval.

    The manifest records authoritative IDs and intended retrieval location, but
    does not claim that the sequence has been downloaded or evaluated.
    """

    retrieval_date = retrieved_at or date.today()
    return {
        "schema_version": "0.1",
        "experiment_id": f"sequence-retrieval-{target.symbol.lower()}",
        "status": "planned",
        "purpose": (
            "Retrieve an authoritative protein sequence as input provenance "
            "for later embedding or structure experiments."
        ),
        "component_type": "sequence_retrieval",
        "model": {
            "provider": "none",
            "name": "authoritative-database-record",
            "version": "not-applicable",
            "licence": "record source database terms before use",
        },
        "inputs": [
            {
                "identifier": target.identifiers["uniprot"],
                "entity_id": target.entity_id,
                "symbol": target.symbol,
                "organism": target.organism,
                "source_url": target.uniprot_url,
                "fasta_url": target.uniprot_fasta_url,
                "retrieved_at": retrieval_date.isoformat(),
                "checksum": "sha256:record-after-download",
            }
        ],
        "runtime": {
            "interface": "http-download",
            "container": "not-applicable",
            "hardware": "cpu",
            "parameters": {},
        },
        "outputs": {
            "path": f"outputs/sequence-retrieval/{target.symbol.lower()}/",
            "confidence_measures": [],
            "generated_at": retrieval_date.isoformat(),
        },
        "evaluation": {
            "method": "manual identifier and checksum review before model use",
            "limitations": [
                "Sequence retrieval is provenance setup only.",
                "No embedding, structure, function, or clinical claim is produced.",
            ],
        },
    }
