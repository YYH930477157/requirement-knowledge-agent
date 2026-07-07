from __future__ import annotations

from collections import Counter
from dataclasses import asdict
from typing import Any

from .decision import decide_requirement
from .matching import match_solutions, match_standards
from .models import DefaultSolution, RequirementInput, StandardClause


def analyze_requirements(
    requirements: list[RequirementInput],
    standards: list[StandardClause],
    solutions: list[DefaultSolution],
) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    input_errors: list[dict[str, str]] = []
    all_clause_ids = {clause.clause_id for clause in standards}

    for requirement in requirements:
        if not requirement.source_text.strip():
            input_errors.append(
                {
                    "requirement_id": requirement.requirement_id,
                    "error": "source_text is required",
                }
            )
            continue

        standard_matches = match_standards(requirement.source_text, standards)
        solution_matches = match_solutions(requirement.source_text, solutions)
        decision = decide_requirement(requirement, standard_matches, solution_matches, all_clause_ids)
        best_solution = solution_matches[0].solution if solution_matches else None

        item = {
            "requirement_id": requirement.requirement_id,
            "source_text": requirement.source_text,
            "module": best_solution.module if best_solution else "",
            "submodule": best_solution.submodule if best_solution else "",
            "decision": decision.status,
            "confidence": decision.confidence,
            "landing_requirement": _landing_requirement(decision.status, requirement, best_solution),
            "developer_guidance": _developer_guidance(best_solution),
            "acceptance_criteria": list(best_solution.acceptance_criteria) if best_solution else [],
            "applied_solution_ids": [best_solution.solution_id] if best_solution and decision.status in {"applied", "suggested"} else [],
            "candidate_solution_ids": [match.solution.solution_id for match in solution_matches],
            "standard_citations": [_citation(match) for match in standard_matches],
            "open_questions": _open_questions(decision.open_questions, best_solution),
            "reasoning_summary": decision.reason,
            "matches": {
                "standards": [_match_summary(match) for match in standard_matches],
                "solutions": [_solution_match_summary(match) for match in solution_matches],
            },
        }
        if best_solution and _solution_requires_confirmation(best_solution) and decision.status == "applied":
            item["decision"] = "suggested"
            item["open_questions"].append("默认方案标记为需要确认，请评审后再作为确定方案。")
        items.append(item)

    counts = Counter(item["decision"] for item in items)
    return {
        "summary": {
            "total_requirements": len(requirements),
            "analyzed": len(items),
            "input_errors": len(input_errors),
            "decisions": dict(counts),
        },
        "items": items,
        "input_errors": input_errors,
    }


def _landing_requirement(status: str, requirement: RequirementInput, solution: DefaultSolution | None) -> str:
    if status == "blocked":
        return ""
    if solution is None:
        return ""
    prefix = "软件应" if status == "applied" else "建议软件"
    return f"{prefix}{solution.default_behavior}"


def _developer_guidance(solution: DefaultSolution | None) -> list[str]:
    if solution is None:
        return []
    guidance = [solution.default_behavior]
    guidance.extend(solution.boundary_conditions)
    for item in solution.config_items:
        suffix = "，需确认" if item.requires_confirmation else ""
        guidance.append(f"配置项 {item.name} 默认值为 {item.default_value}{suffix}。")
    return guidance


def _solution_requires_confirmation(solution: DefaultSolution) -> bool:
    return solution.requires_confirmation or any(item.requires_confirmation for item in solution.config_items)


def _open_questions(decision_questions: tuple[str, ...], solution: DefaultSolution | None) -> list[str]:
    questions = list(decision_questions)
    if solution is not None:
        questions.extend(question for question in solution.confirmation_questions if question not in questions)
    return questions


def _citation(match) -> dict[str, str]:
    return {
        "clause_id": match.clause.clause_id,
        "citation": match.clause.citation,
        "constraint_level": match.clause.constraint_level,
    }


def _match_summary(match) -> dict[str, Any]:
    return {
        "clause_id": match.clause.clause_id,
        "matched_terms": list(match.matched_terms),
        "score": match.score,
        "strength": match.strength,
        "match_reasons": list(match.match_reasons),
        "match_reason": _format_match_reason(match.match_reasons),
    }


def _solution_match_summary(match) -> dict[str, Any]:
    payload = asdict(match)
    payload["solution"] = {"solution_id": match.solution.solution_id, "module": match.solution.module, "submodule": match.solution.submodule}
    payload["matched_terms"] = list(match.matched_terms)
    payload["match_reasons"] = list(match.match_reasons)
    payload["match_reason"] = _format_match_reason(match.match_reasons)
    return payload


def _format_match_reason(reasons: tuple[dict[str, object], ...]) -> str:
    if not reasons:
        return ""
    return "; ".join(f"{reason['source']} matched {reason['term']} (+{reason['weight']})" for reason in reasons)
