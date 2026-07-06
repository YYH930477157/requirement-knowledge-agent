import json

from openpyxl import Workbook

from requirement_knowledge_agent.cli import main


def write_solution_workbook(path):
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(
        [
            "solution_id",
            "module",
            "submodule",
            "scenario",
            "trigger_terms",
            "default_behavior",
            "related_standard_clause_ids",
        ]
    )
    sheet.append(
        [
            "SOL-1",
            "Display",
            "Cycle",
            "Automatic display cycle",
            "display; cycle",
            "Cycle configured display entries.",
            "STD-1",
        ]
    )
    workbook.save(path)


def write_meter_template_workbook(path):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "显示需求"
    sheet.append(["关闭", "序号", "子模块", "描述", "需求模版", "需求", "说明、示例、注意事项"])
    sheet.append(["", "1", "显示格式", "LCD背光：", "支持", "支持", "确认是否支持背光"])
    workbook.save(path)


def test_init_kb_creates_empty_files(tmp_path):
    out = tmp_path / "kb"
    assert main(["init-kb", "--out", str(out)]) == 0
    assert (out / "standards.json").exists()
    assert (out / "default_solutions.json").exists()


def test_analyze_writes_review_outputs(tmp_path):
    kb = tmp_path / "kb"
    main(["init-kb", "--out", str(kb)])
    (kb / "standards.json").write_text(
        json.dumps(
            [
                {
                    "clause_id": "STD-1",
                    "source_file": "s.md",
                    "source_section": "1",
                    "title": "显示轮显",
                    "text": "设备应支持轮显。",
                    "keywords": ["显示", "轮显"],
                    "applies_to": ["显示"],
                    "constraint_level": "must",
                    "citation": "s.md 1",
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (kb / "default_solutions.json").write_text(
        json.dumps(
            [
                {
                    "solution_id": "SOL-1",
                    "module": "显示",
                    "submodule": "轮显",
                    "scenario": "轮显",
                    "trigger_terms": ["显示", "轮显"],
                    "default_behavior": "按配置顺序轮显条目。",
                    "related_standard_clause_ids": ["STD-1"],
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    requirements = tmp_path / "requirements.jsonl"
    requirements.write_text('{"requirement_id":"REQ-1","source_text":"需要显示轮显"}\n', encoding="utf-8")
    out = tmp_path / "out"
    assert main(["analyze", "--requirements", str(requirements), "--kb", str(kb), "--out", str(out)]) == 0
    assert (out / "review_package.json").exists()
    assert (out / "review_package.md").exists()
    assert (out / "software_requirements.xlsx").exists()


def test_analyze_returns_non_zero_for_missing_files(tmp_path):
    assert main(["analyze", "--requirements", str(tmp_path / "missing.jsonl"), "--kb", str(tmp_path), "--out", str(tmp_path / "out")]) == 2


def test_ingest_solutions_writes_default_solutions_json(tmp_path):
    source = tmp_path / "default_solutions.xlsx"
    out = tmp_path / "kb" / "default_solutions.json"
    write_solution_workbook(source)

    assert main(["ingest-solutions", "--input", str(source), "--out", str(out)]) == 0

    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload[0]["solution_id"] == "SOL-1"
    assert payload[0]["trigger_terms"] == ["display", "cycle"]


def test_ingest_meter_template_solutions_writes_default_solutions_json(tmp_path):
    source = tmp_path / "meter_template.xlsx"
    out = tmp_path / "kb" / "default_solutions.json"
    write_meter_template_workbook(source)

    assert main(["ingest-meter-template-solutions", "--input", str(source), "--out", str(out)]) == 0

    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload[0]["solution_id"] == "SOL-METER-DISPLAY-0002"
    assert payload[0]["default_behavior"] == "支持"
    assert payload[0]["confirmation_questions"] == ["请确认显示格式/LCD背光：确认是否支持背光"]


def test_ingest_standards_writes_standards_json(tmp_path):
    source = tmp_path / "standards"
    source.mkdir()
    (source / "display.md").write_text(
        """---
clause_id: STD-1
source_section: 1
title: Display
keywords: display; cycle
applies_to: display
constraint_level: must
---
The display shall cycle.
""",
        encoding="utf-8",
    )
    out = tmp_path / "kb" / "standards.json"

    assert main(["ingest-standards", "--input", str(source), "--out", str(out)]) == 0

    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload[0]["clause_id"] == "STD-1"
    assert payload[0]["keywords"] == ["display", "cycle"]


def test_evaluate_writes_metrics_json(tmp_path):
    kb = tmp_path / "kb"
    main(["init-kb", "--out", str(kb)])
    (kb / "standards.json").write_text(
        json.dumps(
            [
                {
                    "clause_id": "STD-1",
                    "source_file": "s.md",
                    "source_section": "1",
                    "title": "Display",
                    "text": "The display shall cycle.",
                    "keywords": ["display", "cycle"],
                    "applies_to": ["display"],
                    "constraint_level": "must",
                    "citation": "s.md 1",
                }
            ]
        ),
        encoding="utf-8",
    )
    (kb / "default_solutions.json").write_text(
        json.dumps(
            [
                {
                    "solution_id": "SOL-1",
                    "module": "Display",
                    "submodule": "Cycle",
                    "scenario": "Display cycle",
                    "trigger_terms": ["display", "cycle"],
                    "default_behavior": "Cycle configured display entries.",
                    "related_standard_clause_ids": ["STD-1"],
                }
            ]
        ),
        encoding="utf-8",
    )
    requirements = tmp_path / "requirements.jsonl"
    requirements.write_text('{"requirement_id":"REQ-1","source_text":"Need display cycle support"}\n', encoding="utf-8")
    expected = tmp_path / "expected_decisions.json"
    expected.write_text(
        json.dumps(
            [
                {
                    "requirement_id": "REQ-1",
                    "expected_standard_clause_ids": ["STD-1"],
                    "expected_solution_ids": ["SOL-1"],
                    "expected_decision": "applied",
                }
            ]
        ),
        encoding="utf-8",
    )
    out = tmp_path / "metrics.json"

    assert main(["evaluate", "--requirements", str(requirements), "--kb", str(kb), "--expected", str(expected), "--out", str(out)]) == 0

    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["summary"]["decision_accuracy"] == 1.0
    assert payload["failures"] == []
