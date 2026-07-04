import json
from datetime import date
from pathlib import Path

import pytest

from labs.protein_intelligence import (
    ManifestValidationError,
    MockEmbeddingProvider,
    PROTEIN_TARGETS,
    SequenceRetrievalError,
    DisabledEmbeddingProvider,
    EmbeddingProviderConfig,
    EmbeddingProviderUnavailable,
    embedding_manifest,
    fasta_sha256,
    failed_embedding_manifest,
    failed_sequence_manifest,
    get_protein_target,
    identifier_resolution_manifest,
    manifest_summary,
    parse_fasta_sequence,
    planned_sequence_manifest,
    resolve_protein_identifier,
    retrieve_uniprot_sequence,
    sequence_manifest,
    validate_manifest,
)
from labs.protein_intelligence.__main__ import (
    _sequence_from_args,
    build_identifier_resolution_manifest,
    build_retrieval_manifest,
    build_mock_embedding_manifest,
    list_targets,
    validate_manifest_file,
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
    assert get_protein_target("HGNC:4851").symbol == "HTT"
    assert get_protein_target("627").symbol == "BDNF"


def test_resolve_protein_identifier_records_matched_field() -> None:
    hgnc = resolve_protein_identifier(" hgnc:4851 ")
    ncbi = resolve_protein_identifier("4747")

    assert hgnc.status == "resolved"
    assert hgnc.matched_field == "hgnc"
    assert hgnc.target is not None
    assert hgnc.target.symbol == "HTT"
    assert ncbi.matched_field == "ncbi_gene"
    assert ncbi.target is not None
    assert ncbi.target.symbol == "NEFL"


def test_resolve_protein_identifier_returns_unresolved_result() -> None:
    result = resolve_protein_identifier("not-a-known-target")

    assert result.status == "unresolved"
    assert result.matched_field is None
    assert result.target is None


def test_identifier_resolution_manifest_is_valid_and_bounded() -> None:
    manifest = identifier_resolution_manifest("P23560", resolved_at=date(2026, 7, 5))

    validate_manifest(manifest)
    assert manifest["status"] == "retrieved"
    assert manifest["component_type"] == "identifier_resolution"
    assert manifest["inputs"][0]["normalized_query"] == "p23560"
    assert manifest["outputs"]["resolution"]["matched_field"] == "uniprot"
    assert manifest["outputs"]["resolution"]["target"]["symbol"] == "BDNF"
    assert "No fuzzy matching" in manifest["evaluation"]["limitations"][1]


def test_identifier_resolution_manifest_records_failed_resolution() -> None:
    manifest = identifier_resolution_manifest("unknown", resolved_at=date(2026, 7, 5))

    validate_manifest(manifest)
    assert manifest["status"] == "failed"
    assert manifest["outputs"]["resolution"]["resolved"] is False
    assert manifest["outputs"]["resolution"]["target"] is None


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
    validate_manifest(manifest)


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


def test_embedding_provider_config_is_disabled_by_default() -> None:
    config = EmbeddingProviderConfig(
        provider="example",
        model_name="example-model",
        model_version="blocked",
        interface="http-api",
        licence="manual-review-required",
    )

    assert config.enabled is False
    with pytest.raises(EmbeddingProviderUnavailable):
        config.require_enabled()


def test_disabled_embedding_provider_records_failure_manifest() -> None:
    record = retrieve_uniprot_sequence(
        PROTEIN_TARGETS[0],
        fetcher=lambda _url: ">HTT\nACDEFG\n",
        retrieved_at=date(2026, 7, 5),
    )
    provider = DisabledEmbeddingProvider(
        EmbeddingProviderConfig(
            provider="bionemo",
            model_name="example-embedding-model",
            model_version="manual-lab-only",
            interface="http-api",
            licence="record-before-use",
            container="nvcr.io/example@sha256:fixture",
            hardware="gpu-record-required",
            parameters={"timeout_seconds": 30},
        )
    )

    manifest = provider.failed_manifest(record, attempted_at=date(2026, 7, 5))

    validate_manifest(manifest)
    assert manifest["status"] == "failed"
    assert manifest["model"]["provider"] == "bionemo"
    assert manifest["runtime"]["interface"] == "http-api"
    assert manifest["runtime"]["container"] == "nvcr.io/example@sha256:fixture"
    assert manifest["runtime"]["parameters"]["timeout_seconds"] == 30
    assert "disabled by configuration" in manifest["evaluation"]["limitations"][0]


def test_disabled_embedding_provider_never_calls_model() -> None:
    record = retrieve_uniprot_sequence(
        PROTEIN_TARGETS[1],
        fetcher=lambda _url: ">BDNF\nACDEFG\n",
        retrieved_at=date(2026, 7, 5),
    )
    provider = DisabledEmbeddingProvider(
        EmbeddingProviderConfig(
            provider="esm",
            model_name="esm-fixture",
            model_version="manual-lab-only",
            interface="local-python",
            licence="record-before-use",
        )
    )

    with pytest.raises(EmbeddingProviderUnavailable):
        provider.embed(record)


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
    assert manifest_summary(manifest)["input_count"] == 1


def test_cli_builds_identifier_resolution_manifest() -> None:
    manifest = build_identifier_resolution_manifest(
        "HGNC:1033",
        resolved_at=date(2026, 7, 5),
    )

    assert manifest["status"] == "retrieved"
    assert manifest["outputs"]["resolution"]["target"]["symbol"] == "BDNF"


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


def test_manifest_validation_rejects_missing_required_fields() -> None:
    with pytest.raises(ManifestValidationError):
        validate_manifest({"status": "planned"})


def test_manifest_validation_rejects_unknown_status() -> None:
    manifest = planned_sequence_manifest(PROTEIN_TARGETS[0])
    manifest["status"] = "maybe"

    with pytest.raises(ManifestValidationError):
        validate_manifest(manifest)


def test_validate_manifest_file_returns_summary(tmp_path: Path) -> None:
    manifest = planned_sequence_manifest(PROTEIN_TARGETS[0], retrieved_at=date(2026, 7, 3))
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")

    assert validate_manifest_file(str(path)) == {
        "experiment_id": "sequence-retrieval-htt",
        "status": "planned",
        "component_type": "sequence_retrieval",
        "input_count": 1,
    }
