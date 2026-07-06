from requirement_knowledge_agent.matching import find_terms, match_solutions, match_standards, normalize_text
from requirement_knowledge_agent.models import DefaultSolution, StandardClause


def clause():
    return StandardClause(
        clause_id="STD-1",
        source_file="s.md",
        source_section="1",
        title="Display cycle",
        text="The display shall cycle configured values.",
        keywords=("display", "cycle"),
        applies_to=("display",),
        constraint_level="must",
        citation="s.md 1",
    )


def solution():
    return DefaultSolution(
        solution_id="SOL-1",
        module="显示",
        submodule="轮显",
        scenario="轮显",
        trigger_terms=("轮显", "LCD", "display"),
        default_behavior="按配置轮显。",
    )


def test_normalize_text_is_case_insensitive_for_english():
    assert normalize_text(" Display  CYCLE ") == "display cycle"


def test_find_terms_matches_chinese_and_english():
    assert find_terms("LCD 需要支持轮显", ("轮显", "lcd")) == ("轮显", "lcd")


def test_match_standards_by_keyword():
    matches = match_standards("The DISPLAY should cycle values", [clause()])
    assert matches[0].clause.clause_id == "STD-1"
    assert matches[0].strength == "strong"


def test_standard_match_reports_weighted_reasons_by_source():
    matches = match_standards("The Display cycle behavior applies to display screens", [clause()])

    assert matches[0].score > 0
    assert matches[0].match_reasons == (
        {"source": "title", "term": "display cycle", "weight": 5},
        {"source": "keyword", "term": "display", "weight": 3},
        {"source": "keyword", "term": "cycle", "weight": 3},
        {"source": "applies_to", "term": "display", "weight": 1},
    )


def test_match_solution_strong_when_two_trigger_terms_match():
    matches = match_solutions("LCD 需要支持轮显", [solution()])
    assert matches[0].solution.solution_id == "SOL-1"
    assert matches[0].strength == "strong"


def test_solution_match_reports_weighted_reasons_and_ranks_candidates():
    better = DefaultSolution(
        solution_id="SOL-2",
        module="Display",
        submodule="Cycle",
        scenario="Display cycle",
        trigger_terms=("display", "cycle"),
        default_behavior="Cycle display values.",
    )
    weaker = DefaultSolution(
        solution_id="SOL-3",
        module="Display",
        submodule="Status",
        scenario="Display status",
        trigger_terms=("display",),
        default_behavior="Show status.",
    )

    matches = match_solutions("Need display cycle support", [weaker, better])

    assert [match.solution.solution_id for match in matches] == ["SOL-2", "SOL-3"]
    assert matches[0].match_reasons == (
        {"source": "trigger", "term": "display", "weight": 4},
        {"source": "trigger", "term": "cycle", "weight": 4},
        {"source": "module", "term": "display", "weight": 2},
        {"source": "submodule", "term": "cycle", "weight": 2},
        {"source": "scenario", "term": "display cycle", "weight": 1},
    )


def test_match_solution_weak_when_one_trigger_term_matches():
    matches = match_solutions("需要 LCD 显示", [solution()])
    assert matches[0].strength == "weak"


def test_no_match_when_terms_absent():
    assert match_standards("billing tariff", [clause()]) == []
    assert match_solutions("billing tariff", [solution()]) == []
