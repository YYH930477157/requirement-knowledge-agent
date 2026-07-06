from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from openpyxl import load_workbook

from .io import read_json
from .io import write_json
from .validation import KnowledgeValidationError, validate_default_solution
from .validation import validate_standard_clause


LIST_FIELDS = {
    "trigger_terms",
    "boundary_conditions",
    "acceptance_criteria",
    "confirmation_questions",
    "related_standard_clause_ids",
}
REQUIRED_SOLUTION_COLUMNS = (
    "solution_id",
    "module",
    "submodule",
    "scenario",
    "trigger_terms",
    "default_behavior",
)
STANDARD_LIST_FIELDS = {"keywords", "applies_to"}


def ingest_solutions_excel(input_path: Path, out_path: Path) -> list[dict[str, Any]]:
    workbook = load_workbook(input_path, data_only=True)
    sheet = workbook.active
    headers = _read_headers(sheet)
    payload: list[dict[str, Any]] = []
    issues: list[str] = []
    for row_number, values in _iter_data_rows(sheet, headers):
        try:
            raw = _solution_from_row(headers, values)
        except KnowledgeValidationError as exc:
            issues.extend(f"row {row_number}: {issue}" for issue in exc.issues)
            continue
        validation_issues = validate_default_solution(raw)
        issues.extend(f"row {row_number}: {issue}" for issue in validation_issues)
        payload.append(raw)
    if issues:
        raise KnowledgeValidationError(issues)
    write_json(out_path, payload)
    return payload


def ingest_standards(input_path: Path, out_path: Path) -> list[dict[str, Any]]:
    payload: list[dict[str, Any]] = []
    issues: list[str] = []
    for path in _standard_input_files(input_path):
        try:
            raw_items = _read_standard_items(path)
        except KnowledgeValidationError as exc:
            issues.extend(f"{path.name}: {issue}" for issue in exc.issues)
            continue
        for raw in raw_items:
            validation_issues = validate_standard_clause(raw)
            issues.extend(f"{path.name}: {issue}" for issue in validation_issues)
            payload.append(raw)
    if issues:
        raise KnowledgeValidationError(issues)
    write_json(out_path, payload)
    return payload


def _standard_input_files(input_path: Path) -> list[Path]:
    if input_path.is_dir():
        return sorted(
            path
            for path in input_path.iterdir()
            if path.is_file() and path.suffix.lower() in {".md", ".json"}
        )
    return [input_path]


def _read_standard_items(path: Path) -> list[dict[str, Any]]:
    if path.suffix.lower() == ".json":
        payload = read_json(path)
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict) and isinstance(payload.get("items"), list):
            return payload["items"]
        raise KnowledgeValidationError(["JSON must be a list or an object with an items list"])
    if path.suffix.lower() == ".md":
        return [_standard_from_markdown(path)]
    raise KnowledgeValidationError(["input must be a .md file, .json file, or directory"])


def _standard_from_markdown(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8-sig")
    metadata, body = _split_frontmatter(text)
    raw: dict[str, Any] = {}
    for key, value in metadata.items():
        if key in STANDARD_LIST_FIELDS:
            raw[key] = _parse_list(value)
        else:
            raw[key] = value
    raw.setdefault("source_file", path.name)
    raw.setdefault("constraint_level", "reference")
    raw["text"] = body.strip()
    if raw.get("source_section") and not raw.get("citation"):
        raw["citation"] = f"{raw['source_file']} section {raw['source_section']}"
    return raw


def _split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        raise KnowledgeValidationError(["markdown frontmatter is required"])
    lines = text.splitlines()
    end_index = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_index = index
            break
    if end_index is None:
        raise KnowledgeValidationError(["markdown frontmatter closing marker is required"])
    metadata: dict[str, str] = {}
    for line in lines[1:end_index]:
        if not line.strip():
            continue
        if ":" not in line:
            raise KnowledgeValidationError([f"invalid frontmatter line: {line}"])
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip()
    return metadata, "\n".join(lines[end_index + 1 :])


def _read_headers(sheet) -> list[str]:
    first_row = next(sheet.iter_rows(min_row=1, max_row=1, values_only=True), None)
    if not first_row:
        raise KnowledgeValidationError(["row 1: header row is required"])
    headers = [_normalize_header(value) for value in first_row]
    missing = [field for field in REQUIRED_SOLUTION_COLUMNS if field not in headers]
    if missing:
        raise KnowledgeValidationError([f"missing required column: {field}" for field in missing])
    return headers


def _iter_data_rows(sheet, headers: list[str]):
    for row_number, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
        values = list(row[: len(headers)])
        if any(_cell_text(value) for value in values):
            yield row_number, values


def _solution_from_row(headers: list[str], values: list[Any]) -> dict[str, Any]:
    raw: dict[str, Any] = {}
    for header, value in zip(headers, values):
        if not header:
            continue
        if header in LIST_FIELDS:
            raw[header] = _parse_list(value)
        elif header == "config_items":
            raw[header] = _parse_config_items(value)
        elif header == "requires_confirmation":
            raw[header] = _parse_bool(value)
        else:
            raw[header] = _cell_text(value)
    for field in LIST_FIELDS:
        raw.setdefault(field, [])
    raw.setdefault("config_items", [])
    raw.setdefault("requires_confirmation", False)
    return raw


def _normalize_header(value: Any) -> str:
    return _cell_text(value).strip().lower()


def _cell_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _parse_list(value: Any) -> list[str]:
    text = _cell_text(value)
    if not text:
        return []
    return [item.strip() for item in re.split("[;\\n\\uFF1B]+", text) if item.strip()]


def _parse_config_items(value: Any) -> list[dict[str, Any]]:
    text = _cell_text(value)
    if not text:
        return []
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise KnowledgeValidationError(["config_items must be valid JSON"]) from exc
    if isinstance(payload, dict):
        return [payload]
    if isinstance(payload, list) and all(isinstance(item, dict) for item in payload):
        return payload
    raise KnowledgeValidationError(["config_items must be a JSON object or array of objects"])


def _parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    text = _cell_text(value).lower()
    return text in {"1", "true", "yes", "y", "\u662f", "\u9700\u8981", "\u9700\u786e\u8ba4"}
