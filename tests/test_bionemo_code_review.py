from __future__ import annotations

import pytest

from labs.protein_intelligence import (
    BIONEMO_MODEL_CODE_GIT_BLOB,
    BIONEMO_MODEL_CODE_SHA256,
    reviewed_bionemo_model_code,
    scan_python_source,
    verify_pinned_bionemo_source,
)


def test_code_review_records_exact_identity_and_bounded_decision() -> None:
    review = reviewed_bionemo_model_code()

    assert review.status == "conditionally-approved-bounded-fixture"
    assert review.git_blob_id == BIONEMO_MODEL_CODE_GIT_BLOB
    assert review.sha256 == BIONEMO_MODEL_CODE_SHA256
    assert review.forbidden_calls_found == ()
    assert review.bandit_high_findings == 0
    assert review.bandit_medium_findings == 0
    assert review.bandit_low_findings == 1
    assert review.source_imported_during_review is False
    assert review.source_executed_during_review is False
    assert review.dependency_source_audit_complete is False
    assert review.licence_review_required is True


def test_source_scan_treats_python_as_data() -> None:
    safe = scan_python_source(b"import torch\nLOGGER = logging.get_logger(__name__)\n")
    unsafe = scan_python_source(
        b"import subprocess\nsubprocess.run(['x'])\nopen('artifact')\n"
    )

    assert safe["imports"] == ["torch"]
    assert safe["top_level_calls"] == ["logging.get_logger"]
    assert safe["forbidden_calls"] == []
    assert unsafe["forbidden_calls"] == ["open", "subprocess.run"]


def test_exact_source_verifier_rejects_unreviewed_bytes() -> None:
    with pytest.raises(ValueError, match="size"):
        verify_pinned_bionemo_source(b"print('not reviewed')\n")
