from requirement_knowledge_agent.analyzer import analyze_requirements
from requirement_knowledge_agent.models import DefaultSolution, RequirementInput, StandardClause


def clause():
    return StandardClause(
        clause_id="STD-1",
        source_file="s.md",
        source_section="1",
        title="显示轮显",
        text="设备应支持显示轮显。",
        keywords=("显示", "轮显"),
        applies_to=("显示",),
        constraint_level="must",
        citation="s.md section 1",
    )


def solution(requires_confirmation=False):
    return DefaultSolution(
        solution_id="SOL-1",
        module="显示",
        submodule="轮显",
        scenario="显示轮显",
        trigger_terms=("显示", "轮显"),
        default_behavior="软件按配置顺序轮显条目。",
        boundary_conditions=("显示列表为空时不启动轮显。",),
        acceptance_criteria=("配置显示列表后，软件按顺序显示条目。",),
        related_standard_clause_ids=("STD-1",),
        requires_confirmation=requires_confirmation,
    )


def test_analyze_matching_requirement_produces_review_item():
    package = analyze_requirements([RequirementInput("REQ-1", "电表需要支持显示轮显")], [clause()], [solution()])
    item = package["items"][0]
    assert item["requirement_id"] == "REQ-1"
    assert item["decision"] == "applied"
    assert item["applied_solution_ids"] == ["SOL-1"]
    assert item["standard_citations"][0]["clause_id"] == "STD-1"


def test_applied_item_includes_landing_requirement_and_citations():
    package = analyze_requirements([RequirementInput("REQ-1", "电表需要支持显示轮显")], [clause()], [solution()])
    item = package["items"][0]
    assert "软件按配置顺序轮显条目" in item["landing_requirement"]
    assert item["standard_citations"][0]["citation"] == "s.md section 1"


def test_suggested_item_includes_open_questions():
    weak_solution = DefaultSolution(
        solution_id="SOL-2",
        module="显示",
        submodule="LCD",
        scenario="LCD",
        trigger_terms=("LCD",),
        default_behavior="显示信息。",
    )
    package = analyze_requirements([RequirementInput("REQ-1", "设备需要 LCD")], [clause()], [weak_solution])
    assert package["items"][0]["decision"] in {"suggested", "needs_review"}
    assert package["items"][0]["open_questions"]


def test_malformed_requirement_is_reported_as_input_error():
    package = analyze_requirements([RequirementInput("REQ-1", "")], [clause()], [solution()])
    assert package["items"] == []
    assert package["input_errors"][0]["requirement_id"] == "REQ-1"
