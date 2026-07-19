import json
from dataclasses import replace
from datetime import date

import pytest

from labs.protein_intelligence import (
    LocalESM2Config,
    LocalESM2Provider,
    PROTEIN_TARGETS,
    SequenceCacheError,
    SequenceWindowError,
    compare_embedding_manifests,
    fixture_sequence_record,
    local_esm2_manifest,
    local_esm2_status,
    planned_local_esm2_manifest,
    read_cached_sequence,
    retrieve_and_cache_uniprot_sequence,
    select_sequence_window,
    validate_manifest,
    write_cached_sequence,
)
from labs.protein_intelligence.local_esm2 import RuntimeEmbeddingResult


class FixtureRuntime:
    def embed(self, sequence: str, config: LocalESM2Config) -> RuntimeEmbeddingResult:
        return RuntimeEmbeddingResult(
            vector=(0.125, 0.25, 0.5),
            token_embeddings_shape=(1, len(sequence) + 2, 3),
            residue_token_count=len(sequence),
            device="cpu",
            hardware="fixture-cpu",
            torch_version="fixture",
            transformers_version="fixture",
        )


def test_sequence_window_is_explicit_and_never_silently_truncated() -> None:
    selected, start, end = select_sequence_window(
        "ACDEFGHIKL",
        start=3,
        length=4,
        max_residues=8,
    )

    assert selected == "DEFG"
    assert (start, end) == (3, 6)
    with pytest.raises(SequenceWindowError, match="explicit window"):
        select_sequence_window("A" * 10, start=1, length=None, max_residues=8)
    with pytest.raises(SequenceWindowError, match="past the end"):
        select_sequence_window("ACDE", start=3, length=3, max_residues=8)


def test_planned_manifest_records_sequence_window_and_model_revision() -> None:
    record = fixture_sequence_record(PROTEIN_TARGETS[0], retrieved_at=date(2026, 7, 19))
    config = LocalESM2Config(window_start=2, window_length=5, device="cpu")

    manifest = planned_local_esm2_manifest(record, config, planned_at=date(2026, 7, 19))

    validate_manifest(manifest)
    assert manifest["status"] == "planned"
    assert manifest["inputs"][0]["input_handling"] == "explicit-window"
    assert manifest["inputs"][0]["window_start"] == 2
    assert manifest["inputs"][0]["window_end"] == 6
    assert manifest["runtime"]["parameters"]["silent_truncation"] is False
    assert len(manifest["model"]["version"]) == 40


def test_experiment_id_distinguishes_different_sequence_inputs() -> None:
    record = fixture_sequence_record(PROTEIN_TARGETS[0], retrieved_at=date(2026, 7, 19))
    altered = replace(record, sequence="A" * record.sequence_length, checksum="sha256:altered")
    config = LocalESM2Config(window_length=record.sequence_length)

    first = planned_local_esm2_manifest(record, config)
    second = planned_local_esm2_manifest(altered, config)

    assert first["experiment_id"] != second["experiment_id"]


def test_local_provider_generates_provenance_artifact_with_injected_runtime() -> None:
    record = fixture_sequence_record(PROTEIN_TARGETS[1], retrieved_at=date(2026, 7, 19))
    provider = LocalESM2Provider(
        LocalESM2Config(window_start=1, window_length=8, device="cpu"),
        runtime=FixtureRuntime(),
        generated_at=date(2026, 7, 19),
    )

    manifest = local_esm2_manifest(provider.embed(record))

    validate_manifest(manifest)
    assert manifest["status"] == "generated"
    assert manifest["outputs"]["embedding"]["dimensions"] == 3
    assert manifest["outputs"]["embedding"]["token_embeddings_shape"] == [1, 10, 3]
    assert manifest["outputs"]["embedding"]["residue_token_count"] == 8
    assert manifest["outputs"]["embedding"]["checksum"].startswith("sha256:")
    assert manifest["runtime"]["hardware"] == "fixture-cpu"
    assert manifest["runtime"]["parameters"]["local_files_only"] is False
    assert "No function" in manifest["evaluation"]["limitations"][1]


def test_repeat_check_compares_only_matching_experiments() -> None:
    record = fixture_sequence_record(PROTEIN_TARGETS[1], retrieved_at=date(2026, 7, 19))
    provider = LocalESM2Provider(
        LocalESM2Config(window_length=8),
        runtime=FixtureRuntime(),
        generated_at=date(2026, 7, 19),
    )
    first = local_esm2_manifest(provider.embed(record))
    second = local_esm2_manifest(provider.embed(record))

    assert compare_embedding_manifests(first, second) == "matched"
    second["outputs"]["embedding"]["vector"] = [1.0]
    assert compare_embedding_manifests(first, second) == "matched"
    second["outputs"]["embedding"]["checksum"] = "sha256:different"
    assert compare_embedding_manifests(first, second) == "different"
    second["experiment_id"] = "another-experiment"
    assert compare_embedding_manifests(first, second) == "not-comparable"


def test_sequence_cache_round_trip_and_checksum_validation(tmp_path) -> None:
    record = fixture_sequence_record(PROTEIN_TARGETS[0], retrieved_at=date(2026, 7, 19))
    authoritative_record = replace(
        record,
        accession=record.target.identifiers["uniprot"],
        source_url=record.target.uniprot_url,
    )
    path = write_cached_sequence(authoritative_record, cache_dir=tmp_path)

    loaded = read_cached_sequence(record.target, cache_dir=tmp_path)

    assert loaded == authoritative_record
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["sequence"] = "AAAAAAAA"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(SequenceCacheError, match="checksum"):
        read_cached_sequence(record.target, cache_dir=tmp_path)


def test_explicit_uniprot_retrieval_writes_verified_cache(tmp_path) -> None:
    target = PROTEIN_TARGETS[2]
    fasta = ">sp|P07196|NFL_HUMAN\nMSSFSYEPYYST\n"

    record = retrieve_and_cache_uniprot_sequence(
        target,
        fetcher=lambda _: fasta,
        retrieved_at=date(2026, 7, 19),
        cache_dir=tmp_path,
    )

    assert record.sequence == "MSSFSYEPYYST"
    assert read_cached_sequence(target, cache_dir=tmp_path) == record


def test_every_curated_target_has_an_offline_fragment() -> None:
    records = [fixture_sequence_record(target) for target in PROTEIN_TARGETS]

    assert {record.target.symbol for record in records} == {"HTT", "BDNF", "NEFL"}
    assert all(record.source_url.startswith("bundled-fixture:") for record in records)


def test_runtime_status_is_safe_without_importing_optional_models() -> None:
    status = local_esm2_status()

    assert status.model_id == "facebook/esm2_t6_8M_UR50D"
    assert len(status.model_revision) == 40
    assert status.available is (not status.missing_packages)
