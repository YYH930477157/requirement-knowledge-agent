from __future__ import annotations

from typing import Any

from .models import ConfigItem, DefaultSolution, StandardClause


CONSTRAINT_LEVELS = ("must", "should", "reference")


class KnowledgeValidationError(ValueError):
    def __init__(self, issues: list[str]):
        self.issues = issues
        super().__init__("; ".join(issues))


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _string_tuple(value: Any) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    return tuple(str(item).strip() for item in value if str(item).strip())


def validate_standard_clause(raw: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    required = (
        "clause_id",
        "source_file",
        "source_section",
        "title",
        "text",
        "citation",
    )
    for field in required:
        if not _is_non_empty_string(raw.get(field)):
            issues.append(f"{field} is required")
    if raw.get("constraint_level") not in CONSTRAINT_LEVELS:
        issues.append("constraint_level must be one of: must, should, reference")
    if not isinstance(raw.get("keywords"), list) or not _string_tuple(raw.get("keywords")):
        issues.append("keywords must be a non-empty list")
    if not isinstance(raw.get("applies_to"), list):
        issues.append("applies_to must be a list")
    return issues


def load_standard_clause(raw: dict[str, Any]) -> StandardClause:
    issues = validate_standard_clause(raw)
    if issues:
        raise KnowledgeValidationError(issues)
    return StandardClause(
        clause_id=str(raw["clause_id"]).strip(),
        source_file=str(raw["source_file"]).strip(),
        source_section=str(raw["source_section"]).strip(),
        title=str(raw["title"]).strip(),
        text=str(raw["text"]).strip(),
        keywords=_string_tuple(raw.get("keywords")),
        applies_to=_string_tuple(raw.get("applies_to")),
        constraint_level=raw["constraint_level"],
        citation=str(raw["citation"]).strip(),
    )


def validate_default_solution(raw: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    required = (
        "solution_id",
        "module",
        "submodule",
        "scenario",
        "default_behavior",
    )
    for field in required:
        if not _is_non_empty_string(raw.get(field)):
            issues.append(f"{field} is required")
    if not isinstance(raw.get("trigger_terms"), list) or not _string_tuple(raw.get("trigger_terms")):
        issues.append("trigger_terms must be a non-empty list")
    for field in ("config_items", "boundary_conditions", "acceptance_criteria", "related_standard_clause_ids"):
        if field in raw and not isinstance(raw.get(field), list):
            issues.append(f"{field} must be a list")
    return issues


def load_default_solution(raw: dict[str, Any]) -> DefaultSolution:
    issues = validate_default_solution(raw)
    if issues:
        raise KnowledgeValidationError(issues)
    config_items = []
    for item in raw.get("config_items", []):
        if isinstance(item, dict):
            config_items.append(
                ConfigItem(
                    name=str(item.get("name", "")).strip(),
                    default_value=str(item.get("default_value", "")).strip(),
                    requires_confirmation=bool(item.get("requires_confirmation", False)),
                )
            )
    return DefaultSolution(
        solution_id=str(raw["solution_id"]).strip(),
        module=str(raw["module"]).strip(),
        submodule=str(raw["submodule"]).strip(),
        scenario=str(raw["scenario"]).strip(),
        trigger_terms=_string_tuple(raw.get("trigger_terms")),
        default_behavior=str(raw["default_behavior"]).strip(),
        config_items=tuple(config_items),
        boundary_conditions=_string_tuple(raw.get("boundary_conditions", [])),
        acceptance_criteria=_string_tuple(raw.get("acceptance_criteria", [])),
        related_standard_clause_ids=_string_tuple(raw.get("related_standard_clause_ids", [])),
        requires_confirmation=bool(raw.get("requires_confirmation", False)),
    )
