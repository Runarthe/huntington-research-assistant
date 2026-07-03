import tomllib
from pathlib import Path

import hra


def test_package_version_matches_project_metadata() -> None:
    pyproject = Path(__file__).parents[1] / "pyproject.toml"
    metadata = tomllib.loads(pyproject.read_text(encoding="utf-8"))

    assert hra.__version__ == metadata["project"]["version"]
