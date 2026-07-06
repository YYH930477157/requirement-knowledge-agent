import json

from requirement_knowledge_agent.cli import main


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
