from __future__ import annotations

from .models import DecisionResult, RequirementInput, SolutionMatch, StandardMatch


def decide_requirement(
    requirement: RequirementInput,
    standard_matches: list[StandardMatch],
    solution_matches: list[SolutionMatch],
    all_clause_ids: set[str],
) -> DecisionResult:
    must_matches = [match for match in standard_matches if match.clause.constraint_level == "must"]
    if _has_must_conflict(requirement.source_text, must_matches):
        return DecisionResult(
            status="blocked",
            confidence=0.95,
            reason="需求与命中的 must 标准条款存在显式冲突。",
            open_questions=("请确认需求是否需要调整以满足强制标准。",),
        )

    if not standard_matches:
        return DecisionResult(
            status="needs_review",
            confidence=0.35,
            reason="未命中标准依据，不能自动套用默认方案。",
            open_questions=("请补充或确认适用标准依据。",),
        )

    if not solution_matches:
        return DecisionResult(
            status="needs_review",
            confidence=0.4,
            reason="未命中默认方案。",
            open_questions=("请确认是否需要新增默认方案或人工分析。",),
        )

    best_solution = solution_matches[0]
    missing_related = [clause_id for clause_id in best_solution.solution.related_standard_clause_ids if clause_id not in all_clause_ids]
    if missing_related:
        return DecisionResult(
            status="needs_review",
            confidence=0.45,
            reason=f"默认方案关联的标准条款不存在：{', '.join(missing_related)}。",
            open_questions=("请修正默认方案关联标准，或确认该方案是否仍可使用。",),
        )

    has_strong_standard = any(match.strength == "strong" for match in standard_matches)
    has_strong_solution = best_solution.strength == "strong"
    has_must_or_should = any(match.clause.constraint_level in {"must", "should"} for match in standard_matches)
    if has_strong_standard and has_strong_solution and has_must_or_should:
        return DecisionResult(
            status="applied",
            confidence=0.9,
            reason="强命中标准依据和默认方案，且未发现 must 冲突。",
        )

    return DecisionResult(
        status="suggested",
        confidence=0.7,
        reason="命中证据合理，但不足以自动套用为确定方案。",
        open_questions=("请评审默认方案是否适用于该需求。",),
    )


def _has_must_conflict(source_text: str, must_matches: list[StandardMatch]) -> bool:
    lowered = source_text.lower()
    for match in must_matches:
        if f"conflict:{match.clause.clause_id.lower()}" in lowered:
            return True
    return False
