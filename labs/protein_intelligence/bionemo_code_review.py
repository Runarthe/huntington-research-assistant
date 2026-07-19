"""Static review record for the pinned BioNeMo Recipes ESM-2 model code."""

from __future__ import annotations

import ast
import hashlib
from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict

from labs.protein_intelligence.bionemo_recipes_review import (
    BIONEMO_RECIPES_COMMIT,
    BIONEMO_RECIPES_MODEL_REVISION,
    BIONEMO_RECIPES_MODEL_URL,
)


BIONEMO_CODE_REVIEW_VERSION = "hra-bionemo-code-review.v1"
BIONEMO_MODEL_CODE_PATH = "esm_nv.py"
BIONEMO_MODEL_CODE_RECIPES_PATH = "models/esm2/modeling_esm_te.py"
BIONEMO_MODEL_CODE_GIT_BLOB = "bbef1bf7708711a0dd9b855f68d094de88024f53"
BIONEMO_MODEL_CODE_SHA256 = (
    "b4dc5bf54c9e6c0b99123e8ef9755773d950d69769a50136cde6a002f00ceaa0"
)
BIONEMO_MODEL_CODE_SIZE = 38_557
BIONEMO_MODEL_CODE_LINES = 847

_ALLOWED_IMPORTS = (
    "contextlib",
    "torch",
    "torch.nn",
    "transformer_engine.common.recipe",
    "transformer_engine.pytorch",
    "transformer_engine.pytorch.attention.rope",
    "transformers.modeling_outputs",
    "transformers.models.esm.configuration_esm",
    "transformers.models.esm.modeling_esm",
    "transformers.utils",
    "transformers.utils.generic",
    "typing",
    "warnings",
)

_FORBIDDEN_CALL_PREFIXES = (
    "__import__",
    "compile",
    "eval",
    "exec",
    "importlib",
    "open",
    "os.popen",
    "os.system",
    "pathlib.Path.open",
    "pathlib.Path.read",
    "pathlib.Path.write",
    "pickle",
    "requests",
    "socket",
    "subprocess",
    "torch.load",
    "torch.save",
    "urllib",
)


class BioNeMoCodeFinding(BaseModel):
    """One static review observation and its bounded mitigation."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    finding_id: str
    severity: Literal["informational", "low", "medium", "high"]
    summary: str
    evidence: str
    mitigation: str


class BioNeMoRecipesCodeReview(BaseModel):
    """Auditable result of reviewing code without importing or executing it."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: str = BIONEMO_CODE_REVIEW_VERSION
    status: Literal["conditionally-approved-bounded-fixture"] = (
        "conditionally-approved-bounded-fixture"
    )
    reviewed_on: date = date(2026, 7, 19)
    recipes_commit: str = BIONEMO_RECIPES_COMMIT
    model_revision: str = BIONEMO_RECIPES_MODEL_REVISION
    huggingface_path: str = BIONEMO_MODEL_CODE_PATH
    recipes_path: str = BIONEMO_MODEL_CODE_RECIPES_PATH
    git_blob_id: str = BIONEMO_MODEL_CODE_GIT_BLOB
    sha256: str = BIONEMO_MODEL_CODE_SHA256
    size_bytes: int = BIONEMO_MODEL_CODE_SIZE
    line_count: int = BIONEMO_MODEL_CODE_LINES
    source_identity_matches_recipes: bool = True
    ast_parsed: bool = True
    class_count: int = 8
    function_count: int = 24
    allowed_imports: tuple[str, ...] = _ALLOWED_IMPORTS
    forbidden_calls_found: tuple[str, ...] = ()
    top_level_call: Literal["logging.get_logger"] = "logging.get_logger"
    bandit_version: str = "1.8.6"
    bandit_high_findings: int = 0
    bandit_medium_findings: int = 0
    bandit_low_findings: int = 1
    source_imported_during_review: bool = False
    source_executed_during_review: bool = False
    dependency_source_audit_complete: bool = False
    licence_review_required: bool = True
    findings: tuple[BioNeMoCodeFinding, ...] = (
        BioNeMoCodeFinding(
            finding_id="B101-config-assert",
            severity="low",
            summary="Configuration validation uses one Python assert.",
            evidence=(
                "Bandit B101 at source line 135; the check can be removed by "
                "running Python with optimization enabled."
            ),
            mitigation=(
                "The fixture runtime rejects optimized Python and validates the "
                "pinned configuration independently before importing model code."
            ),
        ),
        BioNeMoCodeFinding(
            finding_id="native-dependencies",
            severity="medium",
            summary="Imports load PyTorch and TransformerEngine native extensions.",
            evidence=(
                "The source imports torch and transformer_engine at module load; "
                "their dependency trees were not source-audited by HRA."
            ),
            mitigation=(
                "Run only inside the reviewed immutable NVIDIA base image, with a "
                "hash-locked Python layer, no network, a read-only root filesystem, "
                "dropped capabilities, and one bundled fixture."
            ),
        ),
        BioNeMoCodeFinding(
            finding_id="cuda-allocation",
            severity="informational",
            summary="Model construction allocates TransformerEngine layers on CUDA.",
            evidence=(
                "The pinned constructors select the CUDA device unless initialized "
                "through the meta-device loading path."
            ),
            mitigation=(
                "The runtime requires one NVIDIA GPU, caps the input length, uses "
                "batch size one, and aborts instead of falling back to CPU."
            ),
        ),
        BioNeMoCodeFinding(
            finding_id="licence-metadata-mismatch",
            severity="medium",
            summary="Publisher licence signals are inconsistent.",
            evidence=(
                "The model card metadata declares MIT, while the repository LICENSE "
                "file contains Apache 2.0 and the Python source carries an Apache-2.0 "
                "identifier."
            ),
            mitigation=(
                "HRA records both statements, does not redistribute the artifacts, "
                "and requires human licence review before downloading or running."
            ),
        ),
    )
    decision_scope: str = (
        "Technical approval for one exact, local, network-disabled fixture inference. "
        "This is not a full dependency security audit, licence determination, or "
        "approval for arbitrary models, sequences, training, or production use."
    )
    sources: dict[str, str] = {
        "huggingface_source": (
            f"{BIONEMO_RECIPES_MODEL_URL}/blob/"
            f"{BIONEMO_RECIPES_MODEL_REVISION}/{BIONEMO_MODEL_CODE_PATH}"
        ),
        "recipes_source": (
            "https://github.com/NVIDIA-BioNeMo/bionemo-recipes/blob/"
            f"{BIONEMO_RECIPES_COMMIT}/{BIONEMO_MODEL_CODE_RECIPES_PATH}"
        ),
        "bandit": "https://bandit.readthedocs.io/en/1.8.6/",
    }


def _qualified_name(node: ast.expr) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _qualified_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    if isinstance(node, ast.Call):
        return _qualified_name(node.func)
    return ""


def scan_python_source(source: bytes) -> dict[str, object]:
    """Parse Python as data and report imports and sensitive calls."""

    text = source.decode("utf-8")
    tree = ast.parse(text)
    imports: set[str] = set()
    forbidden_calls: set[str] = set()
    top_level_calls: list[str] = []

    for node in tree.body:
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.add(node.module or "")
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            value = node.value
            if isinstance(value, ast.Call):
                top_level_calls.append(_qualified_name(value.func))

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = _qualified_name(node.func)
        if any(
            name == prefix or name.startswith(f"{prefix}.")
            for prefix in _FORBIDDEN_CALL_PREFIXES
        ):
            forbidden_calls.add(name)

    return {
        "imports": sorted(imports),
        "forbidden_calls": sorted(forbidden_calls),
        "top_level_calls": top_level_calls,
        "assert_lines": [
            node.lineno for node in ast.walk(tree) if isinstance(node, ast.Assert)
        ],
        "class_count": sum(isinstance(node, ast.ClassDef) for node in ast.walk(tree)),
        "function_count": sum(
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            for node in ast.walk(tree)
        ),
    }


def verify_pinned_bionemo_source(source: bytes) -> dict[str, object]:
    """Verify exact source identity and the reviewed static structure."""

    digest = hashlib.sha256(source).hexdigest()
    git_blob = hashlib.sha1(
        f"blob {len(source)}\0".encode("ascii") + source,
        usedforsecurity=False,
    ).hexdigest()
    if len(source) != BIONEMO_MODEL_CODE_SIZE:
        raise ValueError("Pinned BioNeMo source size does not match the review.")
    if digest != BIONEMO_MODEL_CODE_SHA256:
        raise ValueError("Pinned BioNeMo source SHA-256 does not match the review.")
    if git_blob != BIONEMO_MODEL_CODE_GIT_BLOB:
        raise ValueError("Pinned BioNeMo Git blob does not match the review.")

    scan = scan_python_source(source)
    if tuple(scan["imports"]) != _ALLOWED_IMPORTS:
        raise ValueError("Pinned BioNeMo import boundary has changed.")
    if scan["forbidden_calls"]:
        raise ValueError("Pinned BioNeMo source contains a forbidden call.")
    if scan["top_level_calls"] != ["logging.get_logger"]:
        raise ValueError("Pinned BioNeMo top-level execution boundary has changed.")
    if scan["assert_lines"] != [135]:
        raise ValueError("Pinned BioNeMo assert review has changed.")
    if scan["class_count"] != 8 or scan["function_count"] != 24:
        raise ValueError("Pinned BioNeMo source structure has changed.")
    if len(source.decode("utf-8").splitlines()) != BIONEMO_MODEL_CODE_LINES:
        raise ValueError("Pinned BioNeMo source line count has changed.")
    return scan


def reviewed_bionemo_model_code() -> BioNeMoRecipesCodeReview:
    """Return the deterministic bounded static review record."""

    return BioNeMoRecipesCodeReview()
