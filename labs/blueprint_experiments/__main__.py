from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from pydantic import ValidationError

from .manifests import (
    BlueprintManifestValidationError,
    VALID_PROVIDER_TYPES,
    manifest_summary,
    mock_blueprint_manifest,
    planned_blueprint_manifest,
)
from .providers import (
    VALID_EXECUTION_MODES,
    BlueprintProviderConfig,
    provider_catalogue,
    provider_metadata,
)
from .registry import build_blueprint_registry, registry_payload


def _date_arg(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None


def _write_json(payload: object) -> None:
    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")


def validate_manifest_file(path: str) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise BlueprintManifestValidationError("Manifest JSON must be an object.")
    return manifest_summary(payload)


def provider_payload() -> dict[str, object]:
    return provider_catalogue()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m labs.blueprint_experiments",
        description="Offline-safe v0.8 Blueprint Experiment scaffold.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser(
        "list-providers",
        help="List provider types supported by the manifest contract.",
    )

    describe_parser = subparsers.add_parser(
        "describe-provider",
        help="Print safe adapter metadata for one provider family.",
    )
    describe_parser.add_argument(
        "provider_type",
        choices=sorted(VALID_PROVIDER_TYPES),
        help="Provider family to inspect.",
    )

    config_parser = subparsers.add_parser(
        "provider-config",
        help="Print a non-secret provider config skeleton.",
    )
    config_parser.add_argument(
        "provider_type",
        choices=sorted(VALID_PROVIDER_TYPES),
        help="Provider family to configure.",
    )
    config_parser.add_argument(
        "--execution-mode",
        choices=sorted(VALID_EXECUTION_MODES),
        default=None,
        help="Execution mode to record in the config skeleton.",
    )
    config_parser.add_argument(
        "--credentials-env-var",
        help="Name of an environment variable that would hold credentials. Do not pass secret values.",
    )

    plan_parser = subparsers.add_parser(
        "plan",
        help="Print a planned Blueprint-style experiment manifest.",
    )
    plan_parser.add_argument("target", help="Target symbol, entity ID, or UniProt ID.")
    plan_parser.add_argument(
        "--provider-type",
        choices=sorted(VALID_PROVIDER_TYPES),
        default="mock",
        help="Provider family to plan for. Default: mock.",
    )
    plan_parser.add_argument("--date", help="ISO date to record in the manifest.")

    mock_parser = subparsers.add_parser(
        "run-mock",
        help="Print a deterministic mock output manifest. No provider is called.",
    )
    mock_parser.add_argument("target", help="Target symbol, entity ID, or UniProt ID.")
    mock_parser.add_argument("--date", help="ISO date to record in the manifest.")
    mock_parser.add_argument(
        "--points",
        type=int,
        default=8,
        help="Number of mock confidence points to generate.",
    )

    validate_parser = subparsers.add_parser(
        "validate-manifest",
        help="Validate a Blueprint experiment manifest and print a compact summary.",
    )
    validate_parser.add_argument("path", help="Path to manifest JSON.")

    registry_parser = subparsers.add_parser(
        "index-manifests",
        help="Index Blueprint manifest JSON files or directories.",
    )
    registry_parser.add_argument("paths", nargs="+", help="Manifest JSON file or directory paths.")

    args = parser.parse_args(argv)

    try:
        if args.command == "list-providers":
            _write_json(provider_payload())
            return 0
        if args.command == "describe-provider":
            _write_json(provider_metadata(args.provider_type))
            return 0
        if args.command == "provider-config":
            payload = {
                "provider_type": args.provider_type,
                "execution_mode": (
                    args.execution_mode
                    or ("offline" if args.provider_type == "mock" else "planned")
                ),
                "credentials_env_var": args.credentials_env_var,
                "notes": [
                    "This config skeleton is safe to commit only if it contains no secret values.",
                    "Live execution remains disabled until a reviewed adapter exists.",
                ],
            }
            _write_json(BlueprintProviderConfig(**payload).model_dump(mode="json"))
            return 0
        if args.command == "plan":
            _write_json(
                planned_blueprint_manifest(
                    args.target,
                    provider_type=args.provider_type,
                    planned_at=_date_arg(args.date),
                )
            )
            return 0
        if args.command == "run-mock":
            _write_json(
                mock_blueprint_manifest(
                    args.target,
                    generated_at=_date_arg(args.date),
                    points=args.points,
                )
            )
            return 0
        if args.command == "validate-manifest":
            _write_json(validate_manifest_file(args.path))
            return 0
        if args.command == "index-manifests":
            _write_json(registry_payload(build_blueprint_registry(args.paths)))
            return 0
    except (KeyError, ValueError, ValidationError, OSError, json.JSONDecodeError) as exc:
        parser.exit(2, f"{exc}\n")

    parser.exit(2, "Unknown command.\n")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
