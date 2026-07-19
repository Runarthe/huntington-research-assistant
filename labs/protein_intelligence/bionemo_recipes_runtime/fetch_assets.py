#!/usr/bin/env python3
"""Explicitly fetch exact model files and wheels without executing them."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import urllib.parse
import urllib.request
from pathlib import Path


USER_AGENT = "huntington-research-assistant-bionemo-fetch/1"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_file(path: Path, expected_sha256: str, expected_size: int | None) -> None:
    if not path.is_file():
        raise RuntimeError(f"Missing artifact: {path}")
    if expected_size is not None and path.stat().st_size != expected_size:
        raise RuntimeError(f"Artifact size mismatch: {path.name}")
    if sha256_file(path) != expected_sha256:
        raise RuntimeError(f"Artifact checksum mismatch: {path.name}")


def download(url: str, destination: Path, sha256: str, size: int | None) -> str:
    if destination.exists():
        verify_file(destination, sha256, size)
        return "verified-existing"
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".part")
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    digest = hashlib.sha256()
    byte_count = 0
    try:
        with (
            urllib.request.urlopen(request, timeout=60) as response,
            temporary.open("wb") as output,
        ):
            for block in iter(lambda: response.read(1024 * 1024), b""):
                output.write(block)
                digest.update(block)
                byte_count += len(block)
        if size is not None and byte_count != size:
            raise RuntimeError(f"Downloaded size mismatch: {destination.name}")
        if digest.hexdigest() != sha256:
            raise RuntimeError(f"Downloaded checksum mismatch: {destination.name}")
        os.replace(temporary, destination)
    finally:
        if temporary.exists():
            temporary.unlink()
    return "downloaded"


def pypi_wheel_url(package: str, version: str, filename: str) -> str:
    metadata_url = (
        "https://pypi.org/pypi/"
        f"{urllib.parse.quote(package, safe='')}/"
        f"{urllib.parse.quote(version, safe='')}/json"
    )
    request = urllib.request.Request(metadata_url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        metadata = json.load(response)
    matches = [
        item["url"]
        for item in metadata.get("urls", [])
        if item.get("filename") == filename
    ]
    if len(matches) != 1:
        raise RuntimeError(f"PyPI did not return exactly one locked wheel: {filename}")
    return str(matches[0])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    root = args.root.resolve()
    lock = json.loads(
        (Path(__file__).resolve().parent / "artifact-lock.json").read_text(
            encoding="utf-8"
        )
    )

    repository = lock["model"]["repository"]
    revision = lock["model"]["revision"]
    report: dict[str, str] = {}
    for item in lock["model"]["files"]:
        filename = item["filename"]
        url = (
            "https://huggingface.co/"
            f"{repository}/resolve/{revision}/"
            f"{urllib.parse.quote(filename, safe='')}?download=true"
        )
        report[f"model/{filename}"] = download(
            url,
            root / "model" / filename,
            item["sha256"],
            item["size_bytes"],
        )

    for item in lock["python_wheels"]["files"]:
        filename = item["filename"]
        url = pypi_wheel_url(item["package"], item["version"], filename)
        report[f"wheelhouse/{filename}"] = download(
            url,
            root / "wheelhouse" / filename,
            item["sha256"],
            item["size_bytes"],
        )

    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
