#!/usr/bin/env python3
"""Verify model, wheel, configuration, and runtime identities offline."""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.metadata
import json
import platform
import sys
from pathlib import Path


FORBIDDEN_CALL_PREFIXES = (
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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def qualified_name(node: ast.expr) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = qualified_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    if isinstance(node, ast.Call):
        return qualified_name(node.func)
    return ""


def verify_source(path: Path) -> dict[str, object]:
    source = path.read_bytes()
    tree = ast.parse(source.decode("utf-8"))
    forbidden: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = qualified_name(node.func)
        if any(
            name == prefix or name.startswith(f"{prefix}.")
            for prefix in FORBIDDEN_CALL_PREFIXES
        ):
            forbidden.add(name)
    assert_lines = [
        node.lineno for node in ast.walk(tree) if isinstance(node, ast.Assert)
    ]
    if forbidden:
        raise RuntimeError(f"Forbidden model-code calls found: {sorted(forbidden)}")
    if assert_lines != [135]:
        raise RuntimeError("Reviewed model-code assert boundary changed.")
    return {"forbidden_calls": [], "assert_lines": assert_lines}


def installed_version(*names: str) -> str:
    for name in names:
        try:
            return importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            continue
    raise RuntimeError(f"Required distribution is missing: {names[0]}")


def verify_runtime(lock: dict[str, object]) -> dict[str, object]:
    if sys.version_info[:2] != (3, 12):
        raise RuntimeError("The reviewed runtime requires Python 3.12.")
    if platform.system() != "Linux" or platform.machine() not in {"x86_64", "AMD64"}:
        raise RuntimeError("The reviewed runtime requires Linux/AMD64.")
    installed: dict[str, str] = {}
    for item in lock["python_wheels"]["files"]:
        version = installed_version(item["package"])
        if version != item["version"]:
            raise RuntimeError(f"Installed version mismatch: {item['package']}")
        installed[item["package"]] = version
    torch_version = installed_version("torch")
    te_version = installed_version("transformer-engine", "transformer_engine")
    expected = lock["base_image"]
    if torch_version != expected["pytorch_version"]:
        raise RuntimeError("Base-image PyTorch version changed.")
    if not te_version.startswith(expected["transformer_engine_version"]):
        raise RuntimeError("Base-image TransformerEngine version changed.")
    return {
        "python": platform.python_version(),
        "torch": torch_version,
        "transformer_engine": te_version,
        "locked_wheels": len(installed),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--runtime", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    lock = json.loads((root / "artifact-lock.json").read_text(encoding="utf-8"))

    verified: dict[str, object] = {"model_files": 0, "wheel_files": 0}
    for item in lock["model"]["files"]:
        path = root / "model" / item["filename"]
        if (
            not path.is_file()
            or path.stat().st_size != item["size_bytes"]
            or sha256_file(path) != item["sha256"]
        ):
            raise RuntimeError(f"Model artifact mismatch: {item['filename']}")
        verified["model_files"] += 1
    for item in lock["python_wheels"]["files"]:
        path = root / "wheelhouse" / item["filename"]
        if not path.is_file() or sha256_file(path) != item["sha256"]:
            raise RuntimeError(f"Wheel artifact mismatch: {item['filename']}")
        verified["wheel_files"] += 1

    config = json.loads((root / "model" / "config.json").read_text(encoding="utf-8"))
    expected_config = {
        "model_type": "nv_esm",
        "num_hidden_layers": 6,
        "hidden_size": 320,
        "num_attention_heads": 20,
        "max_position_embeddings": 1026,
        "dtype": "float32",
        "layer_precision": None,
    }
    for key, expected in expected_config.items():
        if config.get(key) != expected:
            raise RuntimeError(f"Pinned model configuration changed: {key}")
    verified["model_source"] = verify_source(root / "model" / "esm_nv.py")
    if args.runtime:
        verified["runtime"] = verify_runtime(lock)
    print(json.dumps(verified, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
