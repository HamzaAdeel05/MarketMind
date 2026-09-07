import json
from dataclasses import asdict
from pathlib import Path

def save_json(run_dir: Path, name: str, data):
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / name).write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
