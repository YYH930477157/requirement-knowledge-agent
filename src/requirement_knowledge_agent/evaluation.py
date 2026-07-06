from __future__ import annotations

from typing import Any


def evaluate_package(package: dict[str, Any], expected_items: list[dict[str, Any]]) -> dict[str, Any]:
    actual_by_id = {item.get("requirement_id", ""): item for item in package.get("items", [])}
    failures: list[dict[str, Any]] = []
    evaluated = 0
    standard_hits = 0
    solution_hits = 0
    decision_matches = 0

    for expected in expected_items:
        requirement_id = str(expected.get("requirement_id", ""))
        actual = actual_by_id.get(requirement_id)
        expected_standard_ids = _string_list(expected.get("expected_standard_clause_ids", []))
        expected_solution_ids = _string_list(expected.get("expected_solution_ids", []))
        expected_decision = str(expected.get("expected_decision", ""))

        if actual is None:
            failure = _failure(
                requirement_id=requirement_id,
                expected_standard_ids=expected_standard_ids,
                actual_standard_ids=[],
                expected_solution_ids=expected_solution_ids,
                actual_solution_ids=[],
                expected_decision=expected_decision,
                actual_decision="",
            )
            failures.append(failure)
            continue

        evaluated += 1
        actual_standard_ids = _actual_standard_ids(actual)
        actual_solution_ids = _actual_solution_ids(actual)
        actual_decision = str(actual.get("decision", ""))
        standard_hit = _contains_all(actual_standard_ids, expected_standard_ids)
        solution_hit = _contains_all(actual_solution_ids, expected_solution_ids)
        decision_correct = actual_decision == expected_decision
        standard_hits += int(standard_hit)
        solution_hits += int(solution_hit)
        decision_matches += int(decision_correct)
        if not (standard_hit and solution_hit and decision_correct):
            failures.append(
                _failure(
                    requirement_id=requirement_id,
                    expected_standard_ids=expected_standard_ids,
                    actual_standard_ids=actual_standard_ids,
                    expected_solution_ids=expected_solution_ids,
                    actual_solution_ids=actual_solution_ids,
                    expected_decision=expected_decision,
                    actual_decision=actual_decision,
                )
            )

    total = len(expected_items)
    return {
        "summary": {
            "total_expected": total,
            "evaluated": evaluated,
            "standard_hit_rate": _rate(standard_hits, total),
            "solution_hit_rate": _rate(solution_hits, total),
            "decision_accuracy": _rate(decision_matches, total),
        },
        "failures": failures,
    }


def _actual_standard_ids(item: dict[str, Any]) -> list[str]:
    matches = item.get("matches", {}).get("standards", [])
    return _unique_strings(match.get("clause_id", "") for match in matches if isinstance(match, dict))


def _actual_solution_ids(item: dict[str, Any]) -> list[str]:
    ids = list(item.get("applied_solution_ids", []))
    for match in item.get("matches", {}).get("solutions", []):
        if isinstance(match, dict):
            solution = match.get("solution", {})
            if isinstance(solution, dict):
                ids.append(solution.get("solution_id", ""))
    return _unique_strings(ids)


def _failure(
    *,
    requirement_id: str,
    expected_standard_ids: list[str],
    actual_standard_ids: list[str],
    expected_solution_ids: list[str],
    actual_solution_ids: list[str],
    expected_decision: str,
    actual_decision: str,
) -> dict[str, Any]:
    return {
        "requirement_id": requirement_id,
        "standard_hit": _contains_all(actual_standard_ids, expected_standard_ids),
        "solution_hit": _contains_all(actual_solution_ids, expected_solution_ids),
        "decision_correct": actual_decision == expected_decision,
        "expected_standard_clause_ids": expected_standard_ids,
        "actual_standard_clause_ids": actual_standard_ids,
        "expected_solution_ids": expected_solution_ids,
        "actual_solution_ids": actual_solution_ids,
        "expected_decision": expected_decision,
        "actual_decision": actual_decision,
    }


def _contains_all(actual: list[str], expected: list[str]) -> bool:
    return all(item in actual for item in expected)


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return _unique_strings(value)


def _unique_strings(values) -> list[str]:
    seen = []
    for value in values:
        text = str(value).strip()
        if text and text not in seen:
            seen.append(text)
    return seen


def _rate(count: int, total: int) -> float:
    if total == 0:
        return 0.0
    return round(count / total, 4)
