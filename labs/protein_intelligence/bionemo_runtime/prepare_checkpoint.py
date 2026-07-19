import json
from pathlib import Path

from bionemo.core.data.load import load


execution = json.loads(Path("execution.json").read_text(encoding="utf-8"))
checkpoint_tag = execution["settings"]["checkpoint_tag"]
checkpoint_path = load(checkpoint_tag)
Path("checkpoint_path.txt").write_text(str(checkpoint_path), encoding="utf-8")
print(f"Prepared checkpoint declared in execution.json: {checkpoint_tag}")
