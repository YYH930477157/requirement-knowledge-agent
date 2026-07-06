import pytest

from requirement_knowledge_agent.models import DefaultSolution, StandardClause
from requirement_knowledge_agent.validation import (
    KnowledgeValidationError,
    load_default_solution,
    load_standard_clause,
    validate_default_solution,
    validate_standard_clause,
)


def valid_clause():
    return {
        "clause_id": "STD-1",
        "source_file": "standard.md",
        "source_section": "1.1",
        "title": "Display",
        "text": "The display shall cycle values.",
        "keywords": ["display", "cycle"],
        "applies_to": ["display"],
        "constraint_level": "must",
        "citation": "standard.md section 1.1",
    }


def valid_solution():
    return {
        "solution_id": "SOL-1",
        "module": "Display",
        "submodule": "Cycle",
        "scenario": "Display cycle",
        "trigger_terms": ["display", "cycle"],
        "default_behavior": "Cycle configured display entries.",
        "config_items": [{"name": "interval", "default_value": "5", "requires_confirmation": True}],
        "boundary_conditions": ["No entries means no cycle."],
        "acceptance_criteria": ["Entries are shown in order."],
        "confirmation_questions": ["Confirm cycle interval."],
        "related_standard_clause_ids": ["STD-1"],
        "requires_confirmation": True,
    }


def test_valid_standard_clause_passes():
    assert validate_standard_clause(valid_clause()) == []
    clause = load_standard_clause(valid_clause())
    assert isinstance(clause, StandardClause)
    assert clause.clause_id == "STD-1"


def test_standard_clause_missing_id_fails():
    raw = valid_clause()
    del raw["clause_id"]
    issues = validate_standard_clause(raw)
    assert "clause_id is required" in issues
    with pytest.raises(KnowledgeValidationError):
        load_standard_clause(raw)


def test_invalid_constraint_level_fails():
    raw = valid_clause()
    raw["constraint_level"] = "maybe"
    assert "constraint_level must be one of: must, should, reference" in validate_standard_clause(raw)


def test_valid_default_solution_passes():
    assert validate_default_solution(valid_solution()) == []
    solution = load_default_solution(valid_solution())
    assert isinstance(solution, DefaultSolution)
    assert solution.solution_id == "SOL-1"
    assert solution.confirmation_questions == ("Confirm cycle interval.",)


def test_default_solution_missing_id_fails():
    raw = valid_solution()
    del raw["solution_id"]
    issues = validate_default_solution(raw)
    assert "solution_id is required" in issues
    with pytest.raises(KnowledgeValidationError):
        load_default_solution(raw)
