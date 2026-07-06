from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import RequirementInput
from .validation import load_default_solution, load_standard_clause


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _items_from_payload(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("items"), list):
        return payload["items"]
    raise ValueError("payload must be a list or an object with an items list")


def _read_items(path: Path) -> list[dict[str, Any]]:
    if path.suffix.lower() == ".jsonl":
        return read_jsonl(path)
    return _items_from_payload(read_json(path))


def load_requirements(path: Path) -> list[RequirementInput]:
    requirements = []
    for index, raw in enumerate(_read_items(path), start=1):
        requirement_id = str(raw.get("requirement_id") or raw.get("id") or f"REQ-{index:04d}").strip()
        source_text = str(raw.get("source_text") or raw.get("text") or raw.get("requirement") or "").strip()
        requirements.append(
            RequirementInput(
                requirement_id=requirement_id,
                source_text=source_text,
                metadata={key: value for key, value in raw.items() if key not in {"requirement_id", "id", "source_text", "text", "requirement"}},
            )
        )
    return requirements


def load_standards(path: Path):
    return [load_standard_clause(raw) for raw in _read_items(path)]


def load_solutions(path: Path):
    return [load_default_solution(raw) for raw in _read_items(path)]
