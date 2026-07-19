import json

from labs.protein_intelligence import (
    BIONEMO_CONTAINER_DIGEST,
    BIONEMO_CONTAINER_REFERENCE,
    BIONEMO_CONTAINER_REVIEW_VERSION,
    is_immutable_image_reference,
    reviewed_bionemo_container,
)
from labs.protein_intelligence import __main__ as protein_cli


def test_review_pins_the_exact_legacy_container_contract() -> None:
    review = reviewed_bionemo_container()

    assert review.schema_version == BIONEMO_CONTAINER_REVIEW_VERSION
    assert review.status == "reviewed-legacy-candidate"
    assert review.tag == "2.7.1"
    assert review.digest == BIONEMO_CONTAINER_DIGEST
    assert review.immutable_reference == BIONEMO_CONTAINER_REFERENCE
    assert review.platform == "linux/amd64"
    assert review.framework_contract == "2.7"
    assert review.inference_command == "infer_esm2"
    assert review.checkpoint_tag == "esm2/650m:2.0"
    assert is_immutable_image_reference(review.immutable_reference)


def test_review_preserves_lifecycle_security_and_licence_boundaries() -> None:
    review = reviewed_bionemo_container()

    assert review.archived is True
    assert review.maintained is False
    assert review.catalog_signature_reported is True
    assert review.signature_verified_locally is False
    assert review.catalog_scan_result == "no-malware-reported"
    assert review.locally_scanned is False
    assert review.registry_manifest_resolved_anonymously is True
    assert review.registry_resolution_tool == "docker buildx imagetools inspect"
    assert review.review_network_calls_made is True
    assert review.registry_credentials_used is False
    assert review.image_pulled_during_review is False
    assert review.user_license_review_required is True
    assert all(url.startswith("https://") for url in review.sources.values())


def test_image_review_cli_is_offline_json(capsys) -> None:
    assert protein_cli.main(["bionemo-image-review"]) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["immutable_reference"] == BIONEMO_CONTAINER_REFERENCE
    assert payload["image_pulled_during_review"] is False
    assert payload["review_network_calls_made"] is True
    assert payload["registry_credentials_used"] is False
