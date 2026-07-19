import json
from datetime import date

from labs.protein_intelligence import (
    BIONEMO_RECIPES_COMMIT,
    BIONEMO_RECIPES_MODEL_REVISION,
    BIONEMO_RECIPES_REVIEW_VERSION,
    BIONEMO_RECIPES_WEIGHTS_SHA256,
    LocalESM2Config,
    PROTEIN_TARGETS,
    fixture_sequence_record,
    planned_bionemo_recipes_esm2_manifest,
    reviewed_bionemo_recipes_path,
    validate_manifest,
)
from labs.protein_intelligence import __main__ as protein_cli


def test_review_pins_the_maintained_recipes_and_model_revisions() -> None:
    review = reviewed_bionemo_recipes_path()

    assert review.schema_version == BIONEMO_RECIPES_REVIEW_VERSION
    assert review.status == "reviewed-plan-only"
    assert review.recipes_version == "v3.0.0"
    assert review.recipes_commit == BIONEMO_RECIPES_COMMIT
    assert len(review.recipes_commit) == 40
    assert review.model_id == "nvidia/esm2_t6_8M_UR50D"
    assert review.model_revision == BIONEMO_RECIPES_MODEL_REVISION
    assert len(review.model_revision) == 40
    assert review.recipes_license == "Apache-2.0"
    assert review.model_license == "MIT"
    assert review.model_public is True
    assert review.model_gated is False


def test_review_keeps_remote_code_and_execution_boundaries_explicit() -> None:
    review = reviewed_bionemo_recipes_path()
    files = {item.path: item for item in review.files}

    assert review.transformer_engine_required is True
    assert review.remote_code_required is True
    assert review.remote_code_reviewed_in_full is False
    assert review.remote_code_executed is False
    assert review.model_weights_downloaded is False
    assert review.inference_executed is False
    assert review.credentials_used_during_review is False
    assert files["esm_nv.py"].contains_executable_model_code is True
    assert files["model.safetensors"].lfs_sha256 == BIONEMO_RECIPES_WEIGHTS_SHA256
    assert files["model.safetensors"].size_bytes == 30_058_964
    assert review.weight_identity_verified_by_hra is False
    assert all(url.startswith("https://") for url in review.sources.values())


def test_recipes_plan_reuses_the_exact_selected_sequence_without_execution() -> None:
    record = fixture_sequence_record(PROTEIN_TARGETS[0], retrieved_at=date(2026, 7, 19))
    config = LocalESM2Config(window_start=2, window_length=8, device="cpu")

    plan = planned_bionemo_recipes_esm2_manifest(
        record,
        config,
        planned_at=date(2026, 7, 19),
    )

    validate_manifest(plan)
    assert plan["status"] == "planned"
    assert plan["model"]["version"] == BIONEMO_RECIPES_MODEL_REVISION
    assert plan["model"]["weights_sha256"] == BIONEMO_RECIPES_WEIGHTS_SHA256
    assert plan["inputs"][0]["selected_sequence_length"] == 8
    assert plan["inputs"][0]["window_start"] == 2
    assert plan["inputs"][0]["window_end"] == 9
    assert plan["runtime"]["parameters"]["remote_code_executed"] is False
    assert plan["runtime"]["parameters"]["silent_truncation"] is False
    assert plan["outputs"]["embedding"] is None


def test_recipes_review_cli_outputs_offline_json(capsys) -> None:
    assert protein_cli.main(["bionemo-recipes-review"]) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["recipes_commit"] == BIONEMO_RECIPES_COMMIT
    assert payload["remote_code_executed"] is False
    assert payload["model_weights_downloaded"] is False
