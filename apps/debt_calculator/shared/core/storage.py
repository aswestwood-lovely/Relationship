from __future__ import annotations
import json
from pathlib import Path
from typing import Any

def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)

def load_json(path: Path, default: Any) -> Any:
    try:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default

def save_json(path: Path, data: Any) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
