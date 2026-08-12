"""Load and validate CodeGraphCL task/edge/family configs against their JSON schemas.

No task-specific knowledge here (no httpx/ripgrep/r829/start_tls). Everything task-specific
lives in the task's own directory as data.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft7Validator

ROOT = Path(__file__).resolve().parent.parent          # the CodeGraphCL repo root
BENCH = ROOT / "benchmark"
SCHEMAS = BENCH / "schemas"


def _load_yaml(p: Path) -> dict:
    with open(p) as f:
        return yaml.safe_load(f)


def schema_for(kind: str) -> dict:
    p = SCHEMAS / f"{kind}.schema.json"
    if not p.exists():
        raise FileNotFoundError(f"no schema for {kind}: {p}")
    return json.loads(p.read_text())


def load_task(task_dir: Path | str) -> dict:
    """Load a task's task.yaml as a dict. task_dir = benchmark/tasks/<id>."""
    task_dir = Path(task_dir)
    cfg = _load_yaml(task_dir / "task.yaml")
    return cfg


def validate_against_schema(cfg: dict, kind: str) -> list[str]:
    """Return list of schema errors (empty = OK)."""
    errs: list[str] = []
    v = Draft7Validator(schema_for(kind))
    for e in sorted(v.iter_errors(cfg), key=lambda x: list(x.path)):
        loc = ".".join(str(p) for p in e.path) or "(root)"
        errs.append(f"{loc}: {e.message}")
    return errs


# --- file-presence checks ---
def task_files_present(task_dir: Path, cfg: dict) -> list[str]:
    """Return list of missing-file errors."""
    errs: list[str] = []
    for rel in [cfg["instruction"]["path"], cfg["patches"]["gold"]]:
        if not (task_dir / rel).exists():
            errs.append(f"missing file: {rel}")
    # verifier patch (optional if hermetic verifier/test.sh present)
    vpatch = cfg.get("patches", {}).get("verifier")
    if vpatch and not (task_dir / vpatch).exists():
        errs.append(f"missing verifier patch: {vpatch}")
    sep = cfg.get("separability", {})
    for k in ("banned_words", "checklist"):
        rel = sep.get(k)
        if rel and not (task_dir / rel).exists():
            errs.append(f"missing separability {k}: {rel}")
    for nm in cfg.get("verifier", {}).get("near_miss", []):
        if not (task_dir / nm).exists():
            errs.append(f"missing near-miss: {nm}")
    return errs
