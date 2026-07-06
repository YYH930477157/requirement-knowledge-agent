from requirement_knowledge_agent.decision import decide_requirement
from requirement_knowledge_agent.models import (
    DefaultSolution,
    RequirementInput,
    SolutionMatch,
    StandardClause,
    StandardMatch,
)


def req(text="display cycle"):
    return RequirementInput(requirement_id="REQ-1", source_text=text)


def clause(level="must"):
    return StandardClause(
        clause_id="STD-1",
        source_file="s.md",
        source_section="1",
        title="Display",
        text="Display shall cycle.",
        keywords=("display", "cycle"),
        applies_to=("display",),
        constraint_level=level,
        citation="s.md 1",
    )


def solution(related=("STD-1",)):
    return DefaultSolution(
        solution_id="SOL-1",
        module="Display",
        submodule="Cycle",
        scenario="Cycle",
        trigger_terms=("display", "cycle"),
        default_behavior="Cycle configured values.",
        related_standard_clause_ids=related,
    )


def standard_match(level="must", strength="strong"):
    return StandardMatch(clause=clause(level), matched_terms=("display", "cycle"), score=12, strength=strength)


def solution_match(strength="strong", related=("STD-1",)):
    return SolutionMatch(solution=solution(related), matched_terms=("display", "cycle"), score=12, strength=strength)


def test_strong_standard_and_solution_applies():
    decision = decide_requirement(req(), [standard_match()], [solution_match()], {"STD-1"})
    assert decision.status == "applied"
    assert decision.confidence > 0.8


def test_weak_reference_evidence_is_suggested():
    decision = decide_requirement(req(), [standard_match(level="reference", strength="weak")], [solution_match("weak")], {"STD-1"})
    assert decision.status == "suggested"


def test_no_standard_needs_review():
    decision = decide_requirement(req(), [], [solution_match()], {"STD-1"})
    assert decision.status == "needs_review"


def test_explicit_conflict_with_must_clause_blocks():
    decision = decide_requirement(req("display cycle conflict:STD-1"), [standard_match()], [solution_match()], {"STD-1"})
    assert decision.status == "blocked"


def test_missing_related_standard_prevents_applied():
    decision = decide_requirement(req(), [standard_match()], [solution_match(related=("STD-MISSING",))], {"STD-1"})
    assert decision.status == "needs_review"


def test_weak_standard_evidence_prevents_applied_even_with_strong_solution():
    weak_standard = StandardMatch(
        clause=clause("should"),
        matched_terms=("display",),
        score=1,
        strength="weak",
        match_reasons=({"source": "applies_to", "term": "display", "weight": 1},),
    )

    decision = decide_requirement(req(), [weak_standard], [solution_match()], {"STD-1"})

    assert decision.status == "suggested"
    assert decision.open_questions


def test_forbidden_language_with_must_standard_blocks():
    decision = decide_requirement(
        req("Display cycle must be disabled and not allowed for this product."),
        [standard_match()],
        [solution_match()],
        {"STD-1"},
    )

    assert decision.status == "blocked"
    assert "冲突" in decision.reason
