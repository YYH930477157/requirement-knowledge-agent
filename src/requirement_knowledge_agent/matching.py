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
        if normalized_term and _term_in_text(normalized_term, normalized) and normalized_term not in matches:
            matches.append(normalized_term)
    return tuple(matches)


def match_standards(text: str, clauses: list[StandardClause], *, limit: int = 10) -> list[StandardMatch]:
    matches: list[StandardMatch] = []
    for clause in clauses:
        match_reasons = _weighted_reasons(
            text,
            (
                ("title", (clause.title,), 5),
                ("keyword", clause.keywords, 3),
                ("applies_to", clause.applies_to, 1),
                ("text", (clause.text,), 1),
            ),
        )
        matched_terms = _terms_from_reasons(match_reasons)
        if not matched_terms:
            continue
        score = sum(int(reason["weight"]) for reason in match_reasons)
        has_substantive_match = any(reason["source"] in {"title", "keyword"} for reason in match_reasons)
        strength = "strong" if len(matched_terms) >= 2 and has_substantive_match else "weak"
        matches.append(
            StandardMatch(
                clause=clause,
                matched_terms=matched_terms,
                score=score,
                strength=strength,
                match_reasons=match_reasons,
            )
        )
    matches.sort(key=lambda item: (-item.score, item.clause.clause_id))
    return matches[:limit]


def match_solutions(text: str, solutions: list[DefaultSolution], *, limit: int = 10) -> list[SolutionMatch]:
    matches: list[SolutionMatch] = []
    for solution in solutions:
        match_reasons = _weighted_reasons(
            text,
            (
                ("trigger", solution.trigger_terms, 4),
                ("module", (solution.module,), 2),
                ("submodule", (solution.submodule,), 2),
                ("scenario", (solution.scenario,), 1),
                ("default_behavior", (solution.default_behavior,), 1),
            ),
        )
        matched_terms = _terms_from_reasons(match_reasons)
        if not matched_terms:
            continue
        trigger_matches = find_terms(text, solution.trigger_terms)
        score = sum(int(reason["weight"]) for reason in match_reasons)
        strength = "strong" if len(trigger_matches) >= 2 else "weak"
        matches.append(
            SolutionMatch(
                solution=solution,
                matched_terms=matched_terms,
                score=score,
                strength=strength,
                match_reasons=match_reasons,
            )
        )
    matches.sort(key=lambda item: (-item.score, item.solution.solution_id))
    return matches[:limit]


def _weighted_reasons(
    text: str,
    groups: tuple[tuple[str, tuple[str, ...], int], ...],
) -> tuple[dict[str, object], ...]:
    reasons: list[dict[str, object]] = []
    seen: set[tuple[str, str]] = set()
    for source, terms, weight in groups:
        for term in find_terms(text, terms):
            key = (source, term)
            if key in seen:
                continue
            seen.add(key)
            reasons.append({"source": source, "term": term, "weight": weight})
    return tuple(reasons)


def _terms_from_reasons(reasons: tuple[dict[str, object], ...]) -> tuple[str, ...]:
    terms = []
    for reason in reasons:
        term = str(reason["term"])
        if term not in terms:
            terms.append(term)
    return tuple(terms)


def _term_in_text(term: str, text: str) -> bool:
    if term.isascii() and any(char.isalnum() for char in term):
        pattern = rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])"
        return re.search(pattern, text) is not None
    return term in text
