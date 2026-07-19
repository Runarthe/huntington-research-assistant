from __future__ import annotations

import hashlib
import io
import json
import zipfile
from dataclasses import replace
from datetime import date

import pytest

from labs.protein_intelligence import (
    BIONEMO_RECIPES_BASE_AMD64_DIGEST,
    BIONEMO_RECIPES_BUNDLE_VERSION,
    BIONEMO_RECIPES_MAX_FIXTURE_RESIDUES,
    BioNeMoRecipesExecutionError,
    LocalESM2Config,
    build_bionemo_recipes_execution_bundle,
    fixture_sequence_record,
    get_protein_target,
    reviewed_bionemo_recipes_runtime,
    validate_bionemo_recipes_execution_bundle,
)


def _bundle() -> bytes:
    record = fixture_sequence_record(
        get_protein_target("HTT"),
        retrieved_at=date(2026, 7, 19),
    )
    return build_bionemo_recipes_execution_bundle(
        record,
        LocalESM2Config(max_residues=BIONEMO_RECIPES_MAX_FIXTURE_RESIDUES),
        planned_at=date(2026, 7, 19),
    )


def test_runtime_review_pins_unexecuted_linux_cuda_stack() -> None:
    review = reviewed_bionemo_recipes_runtime()

    assert review.status == "reviewed-not-executed"
    assert review.amd64_digest == BIONEMO_RECIPES_BASE_AMD64_DIGEST
    assert review.platform == "linux/amd64"
    assert review.cuda_version == "13.2.1.009"
    assert review.pytorch_version == "2.12.0a0+0291f96"
    assert review.transformer_engine_version == "2.14"
    assert review.image_pulled_during_review is False
    assert review.derived_image_built is False
    assert review.fixture_inference_executed is False
    assert review.license_consistency == "review-required"


def test_recipes_bundle_is_deterministic_bounded_and_self_validating() -> None:
    first = _bundle()
    second = _bundle()
    manifest = validate_bionemo_recipes_execution_bundle(first)

    assert first == second
    assert manifest["schema_version"] == BIONEMO_RECIPES_BUNDLE_VERSION
    assert manifest["contains_model_weights"] is False
    assert manifest["contains_python_wheels"] is False
    assert manifest["contains_credentials"] is False
    with zipfile.ZipFile(io.BytesIO(first)) as archive:
        fixture = json.loads(archive.read("fixture.json"))
        assert fixture["batch_size"] == 1
        assert fixture["residue_count"] <= BIONEMO_RECIPES_MAX_FIXTURE_RESIDUES
        assert "model.safetensors" not in archive.namelist()
        assert not any(name.endswith(".whl") for name in archive.namelist())
        build_script = archive.read("build_image.sh")
        run_script = archive.read("run_fixture.sh")
        assert b"HRA_NVIDIA_TERMS_REVIEWED" in build_script
        assert b"--pull=false" in build_script
        assert b"--network=none" in build_script
        assert b"HRA_RUN_BOUNDED_FIXTURE" in run_script
        assert b"--pull never" in run_script
        assert b"--network none" in run_script
        assert b"--read-only" in run_script
        assert b"--cap-drop ALL" in run_script


def test_recipes_bundle_rejects_rechecksummed_fixture_tampering() -> None:
    original = _bundle()
    with zipfile.ZipFile(io.BytesIO(original)) as source:
        contents = {name: source.read(name) for name in source.namelist()}
    fixture = json.loads(contents["fixture.json"])
    fixture["sequence"] = "A" * fixture["residue_count"]
    fixture["sequence_sha256"] = hashlib.sha256(
        fixture["sequence"].encode("ascii")
    ).hexdigest()
    contents["fixture.json"] = json.dumps(fixture, indent=2, sort_keys=True).encode(
        "utf-8"
    )
    bundle_manifest = json.loads(contents["bundle-manifest.json"])
    bundle_manifest["files"]["fixture.json"] = (
        "sha256:" + hashlib.sha256(contents["fixture.json"]).hexdigest()
    )
    contents["bundle-manifest.json"] = json.dumps(
        bundle_manifest, indent=2, sort_keys=True
    ).encode("utf-8")
    rewritten = io.BytesIO()
    with zipfile.ZipFile(rewritten, "w") as output:
        for name, content in contents.items():
            output.writestr(name, content)

    with pytest.raises(BioNeMoRecipesExecutionError, match="Fixture checksum"):
        validate_bionemo_recipes_execution_bundle(rewritten.getvalue())


def test_recipes_bundle_rejects_unbounded_implicit_sequence() -> None:
    record = fixture_sequence_record(get_protein_target("HTT"))
    record = replace(record, sequence=record.sequence * 3)

    with pytest.raises(RuntimeError, match="explicit window"):
        build_bionemo_recipes_execution_bundle(
            record,
            LocalESM2Config(max_residues=1_022),
        )
