"""Pinned container provenance for the bounded BioNeMo 2.7 experiment."""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict

from labs.protein_intelligence.provider_parity import BIONEMO_MODEL_VERSION


BIONEMO_CONTAINER_REVIEW_VERSION = "hra-bionemo-container-review.v1"
BIONEMO_FRAMEWORK_CONTRACT = "2.7"
BIONEMO_CONTAINER_REPOSITORY = "nvcr.io/nvidia/clara/bionemo-framework"
BIONEMO_CONTAINER_TAG = "2.7.1"
BIONEMO_CONTAINER_DIGEST = (
    "sha256:7d15abfbd648915c367ec14a1eef93d4aa40f3e346bacfe63c05f9269dabd678"
)
BIONEMO_CONTAINER_REFERENCE = (
    f"{BIONEMO_CONTAINER_REPOSITORY}@{BIONEMO_CONTAINER_DIGEST}"
)
BIONEMO_CONTAINER_CATALOG_URL = (
    "https://catalog.ngc.nvidia.com/orgs/nvidia/clara/containers/"
    "bionemo-framework/2.7.1/tags"
)
BIONEMO_RECIPES_URL = "https://github.com/NVIDIA-BioNeMo/bionemo-recipes"
BIONEMO_LICENSE_URL = (
    "https://www.nvidia.com/en-us/agreements/enterprise-software/"
    "product-specific-terms-for-ai-products/"
)


class BioNeMoContainerReview(BaseModel):
    """Immutable review record; it is not proof of local runtime compatibility."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: str = BIONEMO_CONTAINER_REVIEW_VERSION
    status: Literal["reviewed-legacy-candidate"] = "reviewed-legacy-candidate"
    repository: str = BIONEMO_CONTAINER_REPOSITORY
    tag: str = BIONEMO_CONTAINER_TAG
    digest: str = BIONEMO_CONTAINER_DIGEST
    immutable_reference: str = BIONEMO_CONTAINER_REFERENCE
    platform: Literal["linux/amd64"] = "linux/amd64"
    compressed_size_gb: float = 16.33
    catalog_updated_on: date = date(2025, 10, 30)
    reviewed_on: date = date(2026, 7, 19)
    framework_contract: str = BIONEMO_FRAMEWORK_CONTRACT
    inference_command: Literal["infer_esm2"] = "infer_esm2"
    checkpoint_tag: str = BIONEMO_MODEL_VERSION
    selection_scope: str = (
        "Reproduction candidate for HRA's bounded BioNeMo Framework 2.7 ESM-2 "
        "execution contract only."
    )
    archived: bool = True
    maintained: bool = False
    catalog_signature_reported: bool = True
    signature_verified_locally: bool = False
    catalog_scan_result: Literal["no-malware-reported"] = "no-malware-reported"
    locally_scanned: bool = False
    registry_manifest_resolved_anonymously: bool = True
    registry_resolution_tool: str = "docker buildx imagetools inspect"
    registry_manifest_media_type: str = (
        "application/vnd.docker.distribution.manifest.v2+json"
    )
    review_network_calls_made: bool = True
    registry_credentials_used: bool = False
    image_pulled_during_review: bool = False
    license_name: str = "NVIDIA AI Product Agreement"
    license_url: str = BIONEMO_LICENSE_URL
    user_license_review_required: bool = True
    sources: dict[str, str] = {
        "ngc_catalog": BIONEMO_CONTAINER_CATALOG_URL,
        "ngc_overview": (
            "https://catalog.ngc.nvidia.com/orgs/nvidia/clara/containers/"
            "bionemo-framework"
        ),
        "framework_access": (
            "https://docs.nvidia.com/bionemo-framework/2.7/main/getting-started/"
            "access-startup/index.html"
        ),
        "esm2_inference": (
            "https://docs.nvidia.com/bionemo-framework/latest/main/examples/"
            "bionemo-esm2/inference/index.html"
        ),
        "license": BIONEMO_LICENSE_URL,
        "maintained_successor": BIONEMO_RECIPES_URL,
    }
    limitations: tuple[str, ...] = (
        "The prebuilt BioNeMo Framework container is archived and no longer maintained.",
        "The catalog reports signing and scanning; HRA has not independently verified the signature or scanned the image locally.",
        "The image was not pulled or executed during review, and the exact local GPU remains outside the documented support matrix.",
        "Selecting an image does not establish model correctness, biological validity, or clinical meaning.",
    )
    required_user_actions: tuple[str, ...] = (
        "Review the NVIDIA licence and NGC access terms outside HRA.",
        "Authenticate and pull the exact immutable image outside HRA if those terms are accepted.",
        "Run the bounded local GPU probe before any model command.",
        "Evaluate maintained BioNeMo Recipes for future development rather than extending this archived container contract.",
    )


def reviewed_bionemo_container() -> BioNeMoContainerReview:
    """Return the deterministic image review selected for the v0.12 experiment."""

    return BioNeMoContainerReview()
