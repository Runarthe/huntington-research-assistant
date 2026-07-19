from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Callable
from urllib.error import URLError
from urllib.request import urlopen

from labs.protein_intelligence.targets import (
    ProteinTarget,
    fasta_sha256,
    parse_fasta_sequence,
)


class SequenceRetrievalError(RuntimeError):
    """Raised when a protein sequence cannot be retrieved or parsed."""


class SequenceCacheError(RuntimeError):
    """Raised when a cached sequence record is missing or invalid."""


@dataclass(frozen=True)
class ProteinSequenceRecord:
    target: ProteinTarget
    accession: str
    sequence: str
    checksum: str
    source_url: str
    retrieved_at: date

    @property
    def sequence_length(self) -> int:
        return len(self.sequence)


Fetcher = Callable[[str], str]


def default_sequence_cache_dir() -> Path:
    """Return a user-local cache path outside the project checkout."""

    override = os.getenv("HRA_PROTEIN_CACHE_DIR")
    if override:
        return Path(override).expanduser()
    if os.name == "nt" and os.getenv("LOCALAPPDATA"):
        return Path(os.environ["LOCALAPPDATA"]) / "huntington-research-assistant" / "protein-sequences"
    cache_root = Path(os.getenv("XDG_CACHE_HOME", Path.home() / ".cache"))
    return cache_root / "huntington-research-assistant" / "protein-sequences"


def sequence_cache_path(
    target: ProteinTarget,
    *,
    cache_dir: str | Path | None = None,
) -> Path:
    root = Path(cache_dir) if cache_dir is not None else default_sequence_cache_dir()
    return root / f"{target.identifiers['uniprot'].lower()}.json"


def write_cached_sequence(
    record: ProteinSequenceRecord,
    *,
    cache_dir: str | Path | None = None,
) -> Path:
    """Persist an authoritative sequence record with checksum provenance."""

    destination = sequence_cache_path(record.target, cache_dir=cache_dir)
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "protein-sequence-cache.v1",
        "target_symbol": record.target.symbol,
        "accession": record.accession,
        "sequence": record.sequence,
        "checksum": record.checksum,
        "source_url": record.source_url,
        "retrieved_at": record.retrieved_at.isoformat(),
    }
    temporary = destination.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(destination)
    return destination


def read_cached_sequence(
    target: ProteinTarget,
    *,
    cache_dir: str | Path | None = None,
) -> ProteinSequenceRecord | None:
    """Load and verify a cached sequence without making a network call."""

    path = sequence_cache_path(target, cache_dir=cache_dir)
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        sequence = parse_fasta_sequence(str(payload["sequence"]))
        checksum = fasta_sha256(sequence)
        if payload.get("schema_version") != "protein-sequence-cache.v1":
            raise SequenceCacheError(f"Unsupported sequence cache schema in {path}.")
        if payload.get("target_symbol") != target.symbol:
            raise SequenceCacheError(f"Cached sequence target does not match {target.symbol}.")
        if payload.get("accession") != target.identifiers["uniprot"]:
            raise SequenceCacheError(f"Cached UniProt accession does not match {target.symbol}.")
        if payload.get("checksum") != checksum:
            raise SequenceCacheError(f"Cached sequence checksum validation failed for {target.symbol}.")
        return ProteinSequenceRecord(
            target=target,
            accession=str(payload["accession"]),
            sequence=sequence,
            checksum=checksum,
            source_url=str(payload["source_url"]),
            retrieved_at=date.fromisoformat(str(payload["retrieved_at"])),
        )
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise SequenceCacheError(f"Could not read cached sequence from {path}.") from exc


def fixture_sequence_record(
    target: ProteinTarget,
    *,
    fixture_dir: str | Path | None = None,
    retrieved_at: date | None = None,
) -> ProteinSequenceRecord:
    """Load a short bundled fixture fragment for offline interface testing."""

    root = Path(fixture_dir) if fixture_dir is not None else Path(__file__).parent / "fixtures"
    path = root / f"{target.symbol.lower()}.fragment.fasta"
    try:
        fasta_text = path.read_text(encoding="utf-8")
        sequence = parse_fasta_sequence(fasta_text)
    except (OSError, ValueError) as exc:
        raise SequenceCacheError(f"No valid fixture fragment is available for {target.symbol}.") from exc
    return ProteinSequenceRecord(
        target=target,
        accession=f"{target.identifiers['uniprot']}:fixture-fragment",
        sequence=sequence,
        checksum=fasta_sha256(fasta_text),
        source_url=f"bundled-fixture:{path.name}",
        retrieved_at=retrieved_at or date.today(),
    )


def retrieve_and_cache_uniprot_sequence(
    target: ProteinTarget,
    *,
    fetcher: Fetcher | None = None,
    retrieved_at: date | None = None,
    cache_dir: str | Path | None = None,
) -> ProteinSequenceRecord:
    """Explicitly retrieve a UniProt record and persist it to the local cache."""

    record = retrieve_uniprot_sequence(
        target,
        fetcher=fetcher or http_text_fetcher,
        retrieved_at=retrieved_at,
    )
    write_cached_sequence(record, cache_dir=cache_dir)
    return record


def http_text_fetcher(url: str, *, timeout_seconds: float = 20) -> str:
    """Fetch text from a URL using the standard library."""

    try:
        with urlopen(url, timeout=timeout_seconds) as response:  # noqa: S310
            return response.read().decode("utf-8")
    except (OSError, UnicodeDecodeError, URLError) as exc:
        raise SequenceRetrievalError(f"Could not retrieve sequence from {url}") from exc


def retrieve_uniprot_sequence(
    target: ProteinTarget,
    *,
    fetcher: Fetcher = http_text_fetcher,
    retrieved_at: date | None = None,
) -> ProteinSequenceRecord:
    """Retrieve and normalize a UniProt FASTA sequence for a target."""

    try:
        fasta_text = fetcher(target.uniprot_fasta_url)
        sequence = parse_fasta_sequence(fasta_text)
    except ValueError as exc:
        raise SequenceRetrievalError(
            f"Retrieved FASTA for {target.symbol} was invalid."
        ) from exc

    return ProteinSequenceRecord(
        target=target,
        accession=target.identifiers["uniprot"],
        sequence=sequence,
        checksum=fasta_sha256(fasta_text),
        source_url=target.uniprot_url,
        retrieved_at=retrieved_at or date.today(),
    )


def sequence_manifest(record: ProteinSequenceRecord) -> dict[str, object]:
    """Create a completed retrieval manifest from a sequence record."""

    return {
        "schema_version": "0.1",
        "experiment_id": f"sequence-retrieval-{record.target.symbol.lower()}",
        "status": "retrieved",
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
                "identifier": record.accession,
                "entity_id": record.target.entity_id,
                "symbol": record.target.symbol,
                "organism": record.target.organism,
                "source_url": record.source_url,
                "fasta_url": record.target.uniprot_fasta_url,
                "retrieved_at": record.retrieved_at.isoformat(),
                "checksum": record.checksum,
                "sequence_length": record.sequence_length,
            }
        ],
        "runtime": {
            "interface": "http-download",
            "container": "not-applicable",
            "hardware": "cpu",
            "parameters": {},
        },
        "outputs": {
            "path": f"outputs/sequence-retrieval/{record.target.symbol.lower()}/",
            "confidence_measures": [],
            "generated_at": record.retrieved_at.isoformat(),
        },
        "evaluation": {
            "method": "manual identifier and checksum review before model use",
            "limitations": [
                "Sequence retrieval is provenance setup only.",
                "No embedding, structure, function, or clinical claim is produced.",
            ],
        },
    }


def failed_sequence_manifest(
    target: ProteinTarget,
    *,
    reason: str,
    attempted_at: date | None = None,
) -> dict[str, object]:
    """Create a manifest for a failed sequence retrieval attempt."""

    failure_date = attempted_at or date.today()
    return {
        "schema_version": "0.1",
        "experiment_id": f"sequence-retrieval-{target.symbol.lower()}",
        "status": "failed",
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
                "retrieved_at": failure_date.isoformat(),
                "checksum": None,
            }
        ],
        "runtime": {
            "interface": "http-download",
            "container": "not-applicable",
            "hardware": "cpu",
            "parameters": {},
        },
        "outputs": {
            "path": None,
            "confidence_measures": [],
            "generated_at": failure_date.isoformat(),
        },
        "evaluation": {
            "method": "failure captured before model use",
            "limitations": [
                reason,
                "No embedding, structure, function, or clinical claim is produced.",
            ],
        },
    }
