from datetime import date
from pathlib import Path

import pytest

from labs.protein_intelligence import (
    MockEmbeddingProvider,
    PROTEIN_TARGETS,
    SequenceRetrievalError,
    embedding_manifest,
    fasta_sha256,
    failed_embedding_manifest,
    failed_sequence_manifest,
    get_protein_target,
    parse_fasta_sequence,
    planned_sequence_manifest,
    retrieve_uniprot_sequence,
    sequence_manifest,
)
from labs.protein_intelligence.__main__ import (
    _sequence_from_args,
    build_retrieval_manifest,
    build_mock_embedding_manifest,
    list_targets,
)


FIXTURE_DIR = Path(__file__).parents[1] / "labs" / "protein_intelligence" / "fixtures"


def test_protein_targets_have_stable_identifiers() -> None:
    by_entity = {target.entity_id: target for target in PROTEIN_TARGETS}

    assert by_entity["protein-huntingtin"].identifiers["uniprot"] == "P42858"
    assert by_entity["protein-bdnf"].identifiers["hgnc"] == "HGNC:1033"
    assert by_entity["biomarker-nfl"].symbol == "NEFL"
    assert all(target.organism == "Homo sapiens" for target in PROTEIN_TARGETS)


def test_get_protein_target_accepts_symbol_entity_or_accession() -> None:
    assert get_protein_target("HTT").entity_id == "protein-huntingtin"
    assert get_protein_target("protein-bdnf").symbol == "BDNF"
    assert get_protein_target("P07196").symbol == "NEFL"


def test_parse_fasta_sequence_normalizes_sequence() -> None:
    fasta = ">sp|P23560|BDNF_HUMAN Brain-derived neurotrophic factor\nmskG\nqR\n"

    assert parse_fasta_sequence(fasta) == "MSKGQR"


def test_parse_fasta_sequence_rejects_empty_or_invalid_records() -> None:
    with pytest.raises(ValueError):
        parse_fasta_sequence(">empty")

    with pytest.raises(ValueError):
        parse_fasta_sequence(">bad\nACD-*")


def test_fasta_checksum_uses_normalized_sequence() -> None:
    assert fasta_sha256(">example\nACD\n") == fasta_sha256(">example\nacd")


def test_planned_sequence_manifest_keeps_model_claims_out() -> None:
    target = PROTEIN_TARGETS[0]
    manifest = planned_sequence_manifest(target, retrieved_at=date(2026, 7, 3))

    assert manifest["status"] == "planned"
    assert manifest["component_type"] == "sequence_retrieval"
    assert manifest["model"]["provider"] == "none"
    assert manifest["inputs"][0]["identifier"] == "P42858"
    assert manifest["inputs"][0]["retrieved_at"] == "2026-07-03"
    assert "No embedding" in manifest["evaluation"]["limitations"][1]


def test_retrieve_uniprot_sequence_uses_injected_fetcher() -> None:
    target = PROTEIN_TARGETS[1]

    def fetcher(url: str) -> str:
        assert url == target.uniprot_fasta_url
        return ">sp|P23560|BDNF_HUMAN Brain-derived neurotrophic factor\nMSKGQR\n"

    record = retrieve_uniprot_sequence(
        target,
        fetcher=fetcher,
        retrieved_at=date(2026, 7, 3),
    )

    assert record.accession == "P23560"
    assert record.sequence == "MSKGQR"
    assert record.sequence_length == 6
    assert record.checksum.startswith("sha256:")
    assert record.retrieved_at.isoformat() == "2026-07-03"


def test_retrieve_uniprot_sequence_rejects_invalid_fasta() -> None:
    with pytest.raises(SequenceRetrievalError):
        retrieve_uniprot_sequence(PROTEIN_TARGETS[0], fetcher=lambda _url: ">bad\n")


def test_sequence_manifest_marks_retrieval_complete() -> None:
    record = retrieve_uniprot_sequence(
        PROTEIN_TARGETS[2],
        fetcher=lambda _url: ">NEFL\nACDE\n",
        retrieved_at=date(2026, 7, 3),
    )

    manifest = sequence_manifest(record)

    assert manifest["status"] == "retrieved"
    assert manifest["inputs"][0]["identifier"] == "P07196"
    assert manifest["inputs"][0]["sequence_length"] == 4
    assert manifest["inputs"][0]["checksum"] == record.checksum


def test_failed_sequence_manifest_records_reason_without_outputs() -> None:
    manifest = failed_sequence_manifest(
        PROTEIN_TARGETS[0],
        reason="UniProt unavailable in test.",
        attempted_at=date(2026, 7, 3),
    )

    assert manifest["status"] == "failed"
    assert manifest["outputs"]["path"] is None
    assert manifest["inputs"][0]["checksum"] is None
    assert manifest["evaluation"]["limitations"][0] == "UniProt unavailable in test."


def test_mock_embedding_provider_is_deterministic() -> None:
    record = retrieve_uniprot_sequence(
        PROTEIN_TARGETS[1],
        fetcher=lambda _url: ">BDNF\nACDEFG\n",
        retrieved_at=date(2026, 7, 3),
    )
    provider = MockEmbeddingProvider(dimensions=6, generated_at=date(2026, 7, 4))

    first = provider.embed(record)
    second = provider.embed(record)

    assert first.vector == second.vector
    assert first.dimensions == 6
    assert first.provider == "mock"
    assert first.generated_at.isoformat() == "2026-07-04"


def test_embedding_manifest_preserves_provenance_without_claims() -> None:
    record = retrieve_uniprot_sequence(
        PROTEIN_TARGETS[0],
        fetcher=lambda _url: ">HTT\nACDEFGHIK\n",
        retrieved_at=date(2026, 7, 3),
    )
    embedding = MockEmbeddingProvider(dimensions=3).embed(record)

    manifest = embedding_manifest(embedding)

    assert manifest["status"] == "generated"
    assert manifest["model"]["provider"] == "mock"
    assert manifest["runtime"]["parameters"]["dimensions"] == 3
    assert manifest["inputs"][0]["checksum"] == record.checksum
    assert "No biological similarity" in manifest["evaluation"]["limitations"][1]


def test_failed_embedding_manifest_records_provider_and_reason() -> None:
    record = retrieve_uniprot_sequence(
        PROTEIN_TARGETS[1],
        fetcher=lambda _url: ">BDNF\nACDEFG\n",
        retrieved_at=date(2026, 7, 3),
    )

    manifest = failed_embedding_manifest(
        record,
        provider="example",
        model_name="example-model",
        model_version="blocked",
        reason="Model service unavailable.",
        attempted_at=date(2026, 7, 4),
    )

    assert manifest["status"] == "failed"
    assert manifest["model"]["provider"] == "example"
    assert manifest["outputs"]["path"] is None
    assert manifest["outputs"]["generated_at"] == "2026-07-04"
    assert manifest["evaluation"]["limitations"][0] == "Model service unavailable."


def test_cli_helpers_list_targets_and_build_mock_manifest() -> None:
    targets = list_targets()
    manifest = build_mock_embedding_manifest(
        "BDNF",
        sequence="ACDE",
        generated_at=date(2026, 7, 4),
        dimensions=5,
    )

    assert {target["symbol"] for target in targets} == {"HTT", "BDNF", "NEFL"}
    assert manifest["status"] == "generated"
    assert manifest["runtime"]["parameters"]["dimensions"] == 5
    assert manifest["inputs"][0]["symbol"] == "BDNF"


def test_cli_retrieve_is_offline_safe_by_default() -> None:
    manifest = build_retrieval_manifest(
        "HTT",
        live=False,
        attempted_at=date(2026, 7, 3),
    )

    assert manifest["status"] == "failed"
    assert manifest["inputs"][0]["identifier"] == "P42858"
    assert "Live retrieval disabled" in manifest["evaluation"]["limitations"][0]


def test_cli_sequence_helper_reads_fixture_fasta() -> None:
    sequence = _sequence_from_args(
        "IGNORED",
        str(FIXTURE_DIR / "bdnf.fragment.fasta"),
    )

    assert sequence == "MSKGPVRR"
