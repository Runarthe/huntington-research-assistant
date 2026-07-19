"""Reproducible, fixture-only BioNeMo Recipes execution handoff."""

from __future__ import annotations

import hashlib
import io
import json
import re
import zipfile
from dataclasses import replace
from datetime import date, datetime
from importlib.resources import files
from typing import Literal

from pydantic import BaseModel, ConfigDict

from labs.protein_intelligence.bionemo_code_review import (
    BIONEMO_MODEL_CODE_GIT_BLOB,
    BIONEMO_MODEL_CODE_SHA256,
    reviewed_bionemo_model_code,
)
from labs.protein_intelligence.bionemo_recipes_review import (
    BIONEMO_RECIPES_COMMIT,
    BIONEMO_RECIPES_MODEL_ID,
    BIONEMO_RECIPES_MODEL_REVISION,
    BIONEMO_RECIPES_WEIGHTS_SHA256,
    planned_bionemo_recipes_esm2_manifest,
)
from labs.protein_intelligence.local_esm2 import LocalESM2Config, select_sequence_window
from labs.protein_intelligence.manifests import validate_manifest
from labs.protein_intelligence.sequences import ProteinSequenceRecord


BIONEMO_RECIPES_BUNDLE_VERSION = "hra-bionemo-recipes-bundle.v1"
BIONEMO_RECIPES_RESULT_VERSION = "hra-bionemo-result.v1"
BIONEMO_RECIPES_RUNTIME_REVIEW_VERSION = "hra-bionemo-recipes-runtime-review.v1"
BIONEMO_RECIPES_BASE_REPOSITORY = "nvcr.io/nvidia/pytorch"
BIONEMO_RECIPES_BASE_TAG = "26.04-py3"
BIONEMO_RECIPES_BASE_INDEX_DIGEST = (
    "sha256:192d749b4d773610ec9e01c0443a9df545d196c412b7b8fd33bfa3da362a49e7"
)
BIONEMO_RECIPES_BASE_AMD64_DIGEST = (
    "sha256:be06a21bd95a46bce1a5cfc0576051a40209f328440edaa2ba5cd35abf85ca1a"
)
BIONEMO_RECIPES_BASE_REFERENCE = (
    f"{BIONEMO_RECIPES_BASE_REPOSITORY}@{BIONEMO_RECIPES_BASE_AMD64_DIGEST}"
)
BIONEMO_RECIPES_BASE_CATALOG_URL = (
    "https://catalog.ngc.nvidia.com/orgs/nvidia/-/containers/pytorch/-/tags"
)
BIONEMO_RECIPES_BASE_LICENSE_URL = (
    "https://www.nvidia.com/en-us/agreements/enterprise-software/"
    "product-specific-terms-for-ai-products/"
)
BIONEMO_RECIPES_DERIVED_TAG = "hra-bionemo-recipes-esm2:0.12-fixture"
BIONEMO_RECIPES_MAX_FIXTURE_RESIDUES = 64


class BioNeMoRuntimeArtifact(BaseModel):
    """One exact model or Python wheel artifact fetched before an offline build."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    filename: str
    size_bytes: int | None = None
    sha256: str
    package: str | None = None
    version: str | None = None
    git_blob_id: str | None = None


MODEL_ARTIFACTS: tuple[BioNeMoRuntimeArtifact, ...] = (
    BioNeMoRuntimeArtifact(
        filename="LICENSE",
        size_bytes=11_446,
        sha256="dc32b0a75f340f3c328158fa07e619fb1bdff2cf59f95466a0504f67ae4a1376",
        git_blob_id="535c39f4801acc063dccaf85ee1c48594dca076c",
    ),
    BioNeMoRuntimeArtifact(
        filename="config.json",
        size_bytes=1_360,
        sha256="ec32297c44fdaaabd294f830673a2926b03dad0b685ddb73a1960c4639cc0827",
        git_blob_id="c6595500ba1a74526a63f8ff2e351c66552446b7",
    ),
    BioNeMoRuntimeArtifact(
        filename="esm_nv.py",
        size_bytes=38_557,
        sha256=BIONEMO_MODEL_CODE_SHA256,
        git_blob_id=BIONEMO_MODEL_CODE_GIT_BLOB,
    ),
    BioNeMoRuntimeArtifact(
        filename="model.safetensors",
        size_bytes=30_058_964,
        sha256=BIONEMO_RECIPES_WEIGHTS_SHA256,
        git_blob_id="c24778848ab73ea08c6ca44574b005dd33ae6014",
    ),
    BioNeMoRuntimeArtifact(
        filename="special_tokens_map.json",
        size_bytes=833,
        sha256="88e84bf25f7be378da4ae5a9dbcc012c1a22995e6ed4b3d336eb143cdb72f027",
        git_blob_id="0d2693ecef3eaa18adaaf4bd35b5631f5d50c1ad",
    ),
    BioNeMoRuntimeArtifact(
        filename="tokenizer.json",
        size_bytes=2_945,
        sha256="72be6f7868700459e7df960a28fa0514a0954436d41e47119191865d39d534fb",
        git_blob_id="569acab82c605915d1c0ff15dd547bd0d605ddb0",
    ),
    BioNeMoRuntimeArtifact(
        filename="tokenizer_config.json",
        size_bytes=402,
        sha256="dd33983666fc8690fb707505eb449a3c1d4454ad1c33581cb5225d821682c208",
        git_blob_id="746a7248353ed0d3d2a51658f43630f361f308a9",
    ),
    BioNeMoRuntimeArtifact(
        filename="vocab.txt",
        size_bytes=93,
        sha256="0b82cc0a7c7cf9e567b1e5892d793285b9fbae822c964ca48696f7db44598e03",
        git_blob_id="6b946952cc35537226f07fd70957ee2f848880d2",
    ),
)


def _wheel(
    package: str,
    version: str,
    filename: str,
    sha256: str,
) -> BioNeMoRuntimeArtifact:
    return BioNeMoRuntimeArtifact(
        filename=filename,
        sha256=sha256,
        package=package,
        version=version,
    )


RUNTIME_WHEELS: tuple[BioNeMoRuntimeArtifact, ...] = (
    _wheel(
        "annotated-doc",
        "0.0.4",
        "annotated_doc-0.0.4-py3-none-any.whl",
        "571ac1dc6991c450b25a9c2d84a3705e2ae7a53467b5d111c24fa8baabbed320",
    ),
    _wheel(
        "anyio",
        "4.14.2",
        "anyio-4.14.2-py3-none-any.whl",
        "9f505dda5ac9f0c8309b5e8bd445a8c2bf7246f3ce950121e45ea15bc41d1494",
    ),
    _wheel(
        "certifi",
        "2026.6.17",
        "certifi-2026.6.17-py3-none-any.whl",
        "2227dcbaafe0d2f59279d1762ddddc37783ed4354594f194ffc31d20f41fc3db",
    ),
    _wheel(
        "click",
        "8.4.2",
        "click-8.4.2-py3-none-any.whl",
        "e6f9f66136c816745b9d65817da91d61d957fb16e02e4dcd0552553c5a197b76",
    ),
    _wheel(
        "colorama",
        "0.4.6",
        "colorama-0.4.6-py2.py3-none-any.whl",
        "4f1d9991f5acc0ca119f9d443620b77f9d6b33703e51011c16baf57afb285fc6",
    ),
    _wheel(
        "filelock",
        "3.31.0",
        "filelock-3.31.0-py3-none-any.whl",
        "739b73e580fe88bb78d830aeddbc492519ece3d97ac8368de13a2032c61010c1",
    ),
    _wheel(
        "fsspec",
        "2026.6.0",
        "fsspec-2026.6.0-py3-none-any.whl",
        "02e0b71817df9b2169dc30a16832045764def1191b43dcff5bb85bdee212d2a1",
    ),
    _wheel(
        "h11",
        "0.16.0",
        "h11-0.16.0-py3-none-any.whl",
        "63cf8bbe7522de3bf65932fda1d9c2772064ffb3dae62d55932da54b31cb6c86",
    ),
    _wheel(
        "hf-xet",
        "1.5.2",
        "hf_xet-1.5.2-cp38-abi3-manylinux2014_x86_64.manylinux_2_17_x86_64.whl",
        "db78c39c83d6279daddc98e2238f373ab8980685556d42472b4ec51abcf03e8c",
    ),
    _wheel(
        "httpcore",
        "1.0.9",
        "httpcore-1.0.9-py3-none-any.whl",
        "2d400746a40668fc9dec9810239072b40b4484b640a8c38fd654a024c7a1bf55",
    ),
    _wheel(
        "httpx",
        "0.28.1",
        "httpx-0.28.1-py3-none-any.whl",
        "d909fcccc110f8c7faf814ca82a9a4d816bc5a6dbfea25d6591d6985b8ba59ad",
    ),
    _wheel(
        "huggingface-hub",
        "1.24.0",
        "huggingface_hub-1.24.0-py3-none-any.whl",
        "6ed4120a84a6beec900640aa7e346bd766a6b7341e41526fef5dc8bd81fb7d59",
    ),
    _wheel(
        "idna",
        "3.18",
        "idna-3.18-py3-none-any.whl",
        "7f952cbe720b688055e3f87de14f5c3e5fdaa8bc3928985c4077ca689de849a2",
    ),
    _wheel(
        "markdown-it-py",
        "4.2.0",
        "markdown_it_py-4.2.0-py3-none-any.whl",
        "9f7ebbcd14fe59494226453aed97c1070d83f8d24b6fc3a3bcf9a38092641c4a",
    ),
    _wheel(
        "mdurl",
        "0.1.2",
        "mdurl-0.1.2-py3-none-any.whl",
        "84008a41e51615a49fc9966191ff91509e3c40b939176e643fd50a5c2196b8f8",
    ),
    _wheel(
        "numpy",
        "2.2.6",
        "numpy-2.2.6-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl",
        "fd83c01228a688733f1ded5201c678f0c53ecc1006ffbc404db9f7a899ac6249",
    ),
    _wheel(
        "packaging",
        "26.2",
        "packaging-26.2-py3-none-any.whl",
        "5fc45236b9446107ff2415ce77c807cee2862cb6fac22b8a73826d0693b0980e",
    ),
    _wheel(
        "pygments",
        "2.20.0",
        "pygments-2.20.0-py3-none-any.whl",
        "81a9e26dd42fd28a23a2d169d86d7ac03b46e2f8b59ed4698fb4785f946d0176",
    ),
    _wheel(
        "pyyaml",
        "6.0.3",
        "pyyaml-6.0.3-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl",
        "ba1cc08a7ccde2d2ec775841541641e4548226580ab850948cbfda66a1befcdc",
    ),
    _wheel(
        "regex",
        "2026.7.19",
        "regex-2026.7.19-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl",
        "9dce8ec9695f531a1b8a6f314fd4b393adcccf2ea861db480cdf97a301d01a68",
    ),
    _wheel(
        "rich",
        "15.0.0",
        "rich-15.0.0-py3-none-any.whl",
        "33bd4ef74232fb73fe9279a257718407f169c09b78a87ad3d296f548e27de0bb",
    ),
    _wheel(
        "safetensors",
        "0.8.0",
        "safetensors-0.8.0-cp310-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.whl",
        "fd6f3f93c9a0a7cc2788ee63fb763353d4bd2e89b0751bc78fcf7dda00bea774",
    ),
    _wheel(
        "shellingham",
        "1.5.4",
        "shellingham-1.5.4-py2.py3-none-any.whl",
        "7ecfff8f2fd72616f7481040475a65b2bf8af90a56c89140852d1120324e8686",
    ),
    _wheel(
        "tokenizers",
        "0.22.2",
        "tokenizers-0.22.2-cp39-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.whl",
        "369cc9fc8cc10cb24143873a0d95438bb8ee257bb80c71989e3ee290e8d72c67",
    ),
    _wheel(
        "tqdm",
        "4.69.0",
        "tqdm-4.69.0-py3-none-any.whl",
        "9979978912be667a6ef21fd5d8abf54e324e63d82f7f43c360792ebc2bc4e622",
    ),
    _wheel(
        "transformers",
        "5.5.0",
        "transformers-5.5.0-py3-none-any.whl",
        "821a9ff0961abbb29eb1eb686d78df1c85929fdf213a3fe49dc6bd94f9efa944",
    ),
    _wheel(
        "typer",
        "0.27.0",
        "typer-0.27.0-py3-none-any.whl",
        "6f4b27631e47f077871b7dc30e933ec0131c1390fbe0e387ea5574b5bac9ccf1",
    ),
    _wheel(
        "typing-extensions",
        "4.16.0",
        "typing_extensions-4.16.0-py3-none-any.whl",
        "481caa481374e813c1b176ada14e97f1f67a4539ce9cfeb3f350d78d6370c2e8",
    ),
)


class BioNeMoRecipesRuntimeReview(BaseModel):
    """Immutable runtime selection; it is not proof that the image is safe or runs."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: str = BIONEMO_RECIPES_RUNTIME_REVIEW_VERSION
    status: Literal["reviewed-not-executed"] = "reviewed-not-executed"
    reviewed_on: date = date(2026, 7, 19)
    recipes_commit: str = BIONEMO_RECIPES_COMMIT
    recipes_dockerfile_base_tag: str = BIONEMO_RECIPES_BASE_TAG
    repository: str = BIONEMO_RECIPES_BASE_REPOSITORY
    manifest_list_digest: str = BIONEMO_RECIPES_BASE_INDEX_DIGEST
    amd64_digest: str = BIONEMO_RECIPES_BASE_AMD64_DIGEST
    immutable_reference: str = BIONEMO_RECIPES_BASE_REFERENCE
    platform: Literal["linux/amd64"] = "linux/amd64"
    compressed_size_gb: float = 9.67
    image_created_at: datetime = datetime.fromisoformat(
        "2026-04-14T00:29:38.694409+00:00"
    )
    python_version: Literal["3.12"] = "3.12"
    cuda_version: Literal["13.2.1.009"] = "13.2.1.009"
    pytorch_version: Literal["2.12.0a0+0291f96"] = "2.12.0a0+0291f96"
    transformer_engine_version: Literal["2.14"] = "2.14"
    cudnn_version: Literal["9.21.0.82"] = "9.21.0.82"
    cuda_architectures: tuple[str, ...] = (
        "7.5",
        "8.0",
        "8.6",
        "9.0",
        "10.0",
        "12.0+PTX",
    )
    image_resolved_anonymously: bool = True
    image_pulled_during_review: bool = False
    derived_image_built: bool = False
    fixture_inference_executed: bool = False
    catalog_signature_reported: bool = True
    signature_verified_locally: bool = False
    catalog_scan_result: Literal["no-malware-reported"] = "no-malware-reported"
    locally_scanned: bool = False
    model_artifacts_redistributed_by_hra: bool = False
    wheel_count: int = len(RUNTIME_WHEELS)
    model_file_count: int = len(MODEL_ARTIFACTS)
    model_card_license: Literal["MIT"] = "MIT"
    repository_license_file: Literal["Apache-2.0"] = "Apache-2.0"
    license_consistency: Literal["review-required"] = "review-required"
    nvidia_terms_review_required: bool = True
    network_policy_during_inference: Literal["none"] = "none"
    max_fixture_residues: int = BIONEMO_RECIPES_MAX_FIXTURE_RESIDUES
    sources: dict[str, str] = {
        "ngc_catalog": BIONEMO_RECIPES_BASE_CATALOG_URL,
        "nvidia_terms": BIONEMO_RECIPES_BASE_LICENSE_URL,
        "recipes_dockerfile": (
            "https://github.com/NVIDIA-BioNeMo/bionemo-recipes/blob/"
            f"{BIONEMO_RECIPES_COMMIT}/models/esm2/Dockerfile"
        ),
        "model_revision": (
            "https://huggingface.co/"
            f"{BIONEMO_RECIPES_MODEL_ID}/tree/{BIONEMO_RECIPES_MODEL_REVISION}"
        ),
    }
    limitations: tuple[str, ...] = (
        "The NGC catalog reports signing and scanning; HRA did not verify the signature or independently scan the image.",
        "The immutable base contains a large native dependency tree that HRA did not source-audit.",
        "The derived image, GPU compatibility, and model output have not been executed or verified on this machine.",
        "Publisher licence signals for the model repository are inconsistent and require human review.",
        "One embedding checksum is a computational artifact, not biological or clinical evidence.",
    )


BIONEMO_RECIPES_RUNTIME_FILES = (
    "Dockerfile",
    "README.md",
    "build_image.sh",
    "fetch_assets.py",
    "run_fixture.py",
    "run_fixture.sh",
    "verify_assets.py",
)


class BioNeMoRecipesExecutionError(ValueError):
    """Raised when a Recipes bundle violates the reviewed fixture contract."""


def reviewed_bionemo_recipes_runtime() -> BioNeMoRecipesRuntimeReview:
    """Return the reviewed, not-yet-executed runtime selection."""

    return BioNeMoRecipesRuntimeReview()


def _sha256(data: bytes) -> str:
    return f"sha256:{hashlib.sha256(data).hexdigest()}"


def _runtime_template(name: str) -> bytes:
    resource = files("labs.protein_intelligence").joinpath(
        "bionemo_recipes_runtime", name
    )
    return resource.read_bytes()


def _requirements_lock() -> bytes:
    lines = [
        "# Generated for CPython 3.12 on linux/amd64; install from the verified wheelhouse only.",
        "# Base-provided torch and TransformerEngine are pinned by the immutable NGC image digest.",
    ]
    for artifact in sorted(RUNTIME_WHEELS, key=lambda item: item.package or ""):
        lines.append(
            f"{artifact.package}=={artifact.version} "
            f"--hash=sha256:{artifact.sha256}  # {artifact.filename}"
        )
    return ("\n".join(lines) + "\n").encode("utf-8")


def _artifact_lock() -> dict[str, object]:
    return {
        "schema_version": BIONEMO_RECIPES_BUNDLE_VERSION,
        "base_image": reviewed_bionemo_recipes_runtime().model_dump(mode="json"),
        "model": {
            "repository": BIONEMO_RECIPES_MODEL_ID,
            "revision": BIONEMO_RECIPES_MODEL_REVISION,
            "files": [item.model_dump(mode="json") for item in MODEL_ARTIFACTS],
        },
        "python_wheels": {
            "python": "cp312",
            "platform": "manylinux2014_x86_64",
            "files": [item.model_dump(mode="json") for item in RUNTIME_WHEELS],
        },
    }


def _fixture_payload(
    record: ProteinSequenceRecord,
    config: LocalESM2Config,
    plan: dict[str, object],
) -> dict[str, object]:
    selected, start, end = select_sequence_window(
        record.sequence,
        start=config.window_start,
        length=config.window_length,
        max_residues=min(config.max_residues, BIONEMO_RECIPES_MAX_FIXTURE_RESIDUES),
    )
    if len(selected) > BIONEMO_RECIPES_MAX_FIXTURE_RESIDUES:
        raise BioNeMoRecipesExecutionError("Fixture input exceeds the reviewed limit.")
    expected = plan["inputs"][0]
    if hashlib.sha256(selected.encode("ascii")).hexdigest() != str(
        expected["selected_sequence_checksum"]
    ).removeprefix("sha256:"):
        raise BioNeMoRecipesExecutionError("Fixture sequence does not match its plan.")
    return {
        "schema_version": "hra-bionemo-recipes-fixture.v1",
        "experiment_id": plan["experiment_id"],
        "target": record.target.symbol,
        "accession": record.accession,
        "sequence": selected,
        "sequence_sha256": hashlib.sha256(selected.encode("ascii")).hexdigest(),
        "residue_count": len(selected),
        "window_start": start,
        "window_end": end,
        "max_residues": BIONEMO_RECIPES_MAX_FIXTURE_RESIDUES,
        "batch_size": 1,
    }


def _zip_files(bundle_files: dict[str, bytes]) -> bytes:
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, mode="w", compression=zipfile.ZIP_DEFLATED) as output:
        for name in sorted(bundle_files):
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (
                0o100755 << 16 if name.endswith(".sh") else 0o100644 << 16
            )
            output.writestr(info, bundle_files[name])
    return archive.getvalue()


def build_bionemo_recipes_execution_bundle(
    record: ProteinSequenceRecord,
    config: LocalESM2Config,
    *,
    planned_at: date | None = None,
) -> bytes:
    """Build a deterministic handoff for one exact offline fixture inference."""

    bounded_config = replace(
        config,
        max_residues=min(
            config.max_residues,
            BIONEMO_RECIPES_MAX_FIXTURE_RESIDUES,
        ),
    )
    plan = planned_bionemo_recipes_esm2_manifest(
        record,
        bounded_config,
        planned_at=planned_at,
    )
    fixture = _fixture_payload(record, bounded_config, plan)
    bundle_files: dict[str, bytes] = {
        "artifact-lock.json": json.dumps(
            _artifact_lock(), indent=2, sort_keys=True
        ).encode("utf-8"),
        "code-review.json": json.dumps(
            reviewed_bionemo_model_code().model_dump(mode="json"),
            indent=2,
            sort_keys=True,
        ).encode("utf-8"),
        "fixture.json": json.dumps(fixture, indent=2, sort_keys=True).encode("utf-8"),
        "plan.json": json.dumps(plan, indent=2, sort_keys=True).encode("utf-8"),
        "requirements.lock": _requirements_lock(),
        "runtime-review.json": json.dumps(
            reviewed_bionemo_recipes_runtime().model_dump(mode="json"),
            indent=2,
            sort_keys=True,
        ).encode("utf-8"),
    }
    for name in BIONEMO_RECIPES_RUNTIME_FILES:
        bundle_files[name] = _runtime_template(name)
    manifest = {
        "schema_version": BIONEMO_RECIPES_BUNDLE_VERSION,
        "experiment_id": plan["experiment_id"],
        "created_at": (planned_at or date.today()).isoformat(),
        "contains_model_weights": False,
        "contains_python_wheels": False,
        "contains_credentials": False,
        "files": {
            name: _sha256(content) for name, content in sorted(bundle_files.items())
        },
    }
    bundle_files["bundle-manifest.json"] = json.dumps(
        manifest, indent=2, sort_keys=True
    ).encode("utf-8")
    return _zip_files(bundle_files)


def validate_bionemo_recipes_execution_bundle(archive: bytes) -> dict[str, object]:
    """Validate the exact bundle without executing scripts or model code."""

    try:
        with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
            required = {
                "artifact-lock.json",
                "bundle-manifest.json",
                "code-review.json",
                "fixture.json",
                "plan.json",
                "requirements.lock",
                "runtime-review.json",
                *BIONEMO_RECIPES_RUNTIME_FILES,
            }
            if set(bundle.namelist()) != required:
                raise BioNeMoRecipesExecutionError(
                    "Recipes bundle file set does not match the contract."
                )
            manifest = json.loads(bundle.read("bundle-manifest.json"))
            if manifest.get("schema_version") != BIONEMO_RECIPES_BUNDLE_VERSION:
                raise BioNeMoRecipesExecutionError("Unknown Recipes bundle version.")
            if any(
                manifest.get(key) is not False
                for key in (
                    "contains_model_weights",
                    "contains_python_wheels",
                    "contains_credentials",
                )
            ):
                raise BioNeMoRecipesExecutionError(
                    "Recipes bundle boundary is invalid."
                )
            recorded = manifest.get("files")
            if not isinstance(recorded, dict):
                raise BioNeMoRecipesExecutionError(
                    "Recipes bundle checksums are missing."
                )
            for name in sorted(required - {"bundle-manifest.json"}):
                if recorded.get(name) != _sha256(bundle.read(name)):
                    raise BioNeMoRecipesExecutionError(
                        f"Recipes bundle checksum mismatch: {name}"
                    )
            for name in BIONEMO_RECIPES_RUNTIME_FILES:
                if bundle.read(name) != _runtime_template(name):
                    raise BioNeMoRecipesExecutionError(
                        f"Recipes runtime template mismatch: {name}"
                    )

            plan = json.loads(bundle.read("plan.json"))
            validate_manifest(plan)
            if plan.get("model", {}).get("version") != BIONEMO_RECIPES_MODEL_REVISION:
                raise BioNeMoRecipesExecutionError("Recipes model revision changed.")
            fixture = json.loads(bundle.read("fixture.json"))
            if fixture.get("experiment_id") != plan.get("experiment_id"):
                raise BioNeMoRecipesExecutionError("Fixture experiment ID changed.")
            sequence = fixture.get("sequence")
            if not isinstance(sequence, str) or not re.fullmatch(
                r"[ACDEFGHIKLMNPQRSTVWYBXZJUO]+", sequence
            ):
                raise BioNeMoRecipesExecutionError("Fixture sequence is invalid.")
            if len(sequence) > BIONEMO_RECIPES_MAX_FIXTURE_RESIDUES:
                raise BioNeMoRecipesExecutionError("Fixture is too long.")
            if hashlib.sha256(sequence.encode("ascii")).hexdigest() != fixture.get(
                "sequence_sha256"
            ):
                raise BioNeMoRecipesExecutionError("Fixture checksum changed.")
            plan_inputs = plan.get("inputs")
            plan_input = plan_inputs[0] if isinstance(plan_inputs, list) else {}
            if (
                f"sha256:{fixture.get('sequence_sha256')}"
                != plan_input.get("selected_sequence_checksum")
                or fixture.get("residue_count")
                != plan_input.get("selected_sequence_length")
                or fixture.get("window_start") != plan_input.get("window_start")
                or fixture.get("window_end") != plan_input.get("window_end")
            ):
                raise BioNeMoRecipesExecutionError(
                    "Fixture checksum or window does not match its plan."
                )
            if json.loads(
                bundle.read("code-review.json")
            ) != reviewed_bionemo_model_code().model_dump(mode="json"):
                raise BioNeMoRecipesExecutionError("Code review record changed.")
            if json.loads(
                bundle.read("runtime-review.json")
            ) != reviewed_bionemo_recipes_runtime().model_dump(mode="json"):
                raise BioNeMoRecipesExecutionError("Runtime review record changed.")
            if json.loads(bundle.read("artifact-lock.json")) != _artifact_lock():
                raise BioNeMoRecipesExecutionError("Artifact lock changed.")
            if bundle.read("requirements.lock") != _requirements_lock():
                raise BioNeMoRecipesExecutionError("Python dependency lock changed.")
            return manifest
    except (
        OSError,
        UnicodeDecodeError,
        zipfile.BadZipFile,
        json.JSONDecodeError,
    ) as exc:
        raise BioNeMoRecipesExecutionError(
            "Recipes bundle is not a valid archive."
        ) from exc
