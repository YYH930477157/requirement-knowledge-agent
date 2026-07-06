from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


ConstraintLevel = Literal["must", "should", "reference"]
DecisionStatus = Literal["applied", "suggested", "needs_review", "blocked"]
MatchStrength = Literal["strong", "weak"]


@dataclass(frozen=True)
class StandardClause:
    clause_id: str
    source_file: str
    source_section: str
    title: str
    text: str
    keywords: tuple[str, ...]
    applies_to: tuple[str, ...]
    constraint_level: ConstraintLevel
    citation: str


@dataclass(frozen=True)
class ConfigItem:
    name: str
    default_value: str
    requires_confirmation: bool = False


@dataclass(frozen=True)
class DefaultSolution:
    solution_id: str
    module: str
    submodule: str
    scenario: str
    trigger_terms: tuple[str, ...]
    default_behavior: str
    config_items: tuple[ConfigItem, ...] = ()
    boundary_conditions: tuple[str, ...] = ()
    acceptance_criteria: tuple[str, ...] = ()
    related_standard_clause_ids: tuple[str, ...] = ()
    requires_confirmation: bool = False


@dataclass(frozen=True)
class RequirementInput:
    requirement_id: str
    source_text: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class StandardMatch:
    clause: StandardClause
    matched_terms: tuple[str, ...]
    score: int
    strength: MatchStrength


@dataclass(frozen=True)
class SolutionMatch:
    solution: DefaultSolution
    matched_terms: tuple[str, ...]
    score: int
    strength: MatchStrength


@dataclass(frozen=True)
class DecisionResult:
    status: DecisionStatus
    confidence: float
    reason: str
    open_questions: tuple[str, ...] = ()


@dataclass(frozen=True)
class ReviewItem:
    requirement_id: str
    source_text: str
    module: str
    submodule: str
    decision: DecisionStatus
    confidence: float
    landing_requirement: str
    developer_guidance: tuple[str, ...]
    acceptance_criteria: tuple[str, ...]
    applied_solution_ids: tuple[str, ...]
    standard_citations: tuple[dict[str, str], ...]
    open_questions: tuple[str, ...]
    reasoning_summary: str
