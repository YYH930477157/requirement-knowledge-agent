from __future__ import annotations

import re

from .models import DefaultSolution, SolutionMatch, StandardClause, StandardMatch


def normalize_text(value: object | None) -> str:
    text = "" if value is None else str(value)
    text = text.replace("\u3000", " ").replace("\u00a0", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def find_terms(text: str, terms: tuple[str, ...]) -> tuple[str, ...]:
    normalized = normalize_text(text)
    matches = []
    for term in terms:
        normalized_term = normalize_text(term)
        if normalized_term and normalized_term in normalized and normalized_term not in matches:
            matches.append(normalized_term)
    return tuple(matches)


def match_standards(text: str, clauses: list[StandardClause], *, limit: int = 10) -> list[StandardMatch]:
    matches: list[StandardMatch] = []
    for clause in clauses:
        terms = tuple(dict.fromkeys((*clause.keywords, clause.title, *clause.applies_to)))
        matched_terms = find_terms(text, terms)
        if not matched_terms:
            continue
        score = sum(len(term) for term in matched_terms)
        strength = "strong" if len(matched_terms) >= 2 or clause.constraint_level == "must" else "weak"
        matches.append(StandardMatch(clause=clause, matched_terms=matched_terms, score=score, strength=strength))
    matches.sort(key=lambda item: (-item.score, item.clause.clause_id))
    return matches[:limit]


def match_solutions(text: str, solutions: list[DefaultSolution], *, limit: int = 10) -> list[SolutionMatch]:
    matches: list[SolutionMatch] = []
    for solution in solutions:
        terms = tuple(dict.fromkeys((*solution.trigger_terms, solution.module, solution.submodule, solution.scenario)))
        matched_terms = find_terms(text, terms)
        if not matched_terms:
            continue
        score = sum(len(term) for term in matched_terms)
        trigger_matches = find_terms(text, solution.trigger_terms)
        strength = "strong" if len(trigger_matches) >= 2 else "weak"
        matches.append(SolutionMatch(solution=solution, matched_terms=matched_terms, score=score, strength=strength))
    matches.sort(key=lambda item: (-item.score, item.solution.solution_id))
    return matches[:limit]
