import json

from requirement_knowledge_agent.io import (
    load_requirements,
    load_solutions,
    load_standards,
    read_json,
    read_jsonl,
    write_json,
    write_text,
)


def test_read_json_array(tmp_path):
    path = tmp_path / "items.json"
    path.write_text('[{"id": "a"}]', encoding="utf-8")
    assert read_json(path) == [{"id": "a"}]


def test_read_json_accepts_utf8_bom(tmp_path):
    path = tmp_path / "items.json"
    path.write_text('\ufeff[{"id": "a"}]', encoding="utf-8")
    assert read_json(path) == [{"id": "a"}]


def test_read_jsonl_accepts_utf8_bom(tmp_path):
    path = tmp_path / "items.jsonl"
    path.write_text('\ufeff{"id": "a"}\n', encoding="utf-8")
    assert read_jsonl(path) == [{"id": "a"}]


def test_load_requirements_accepts_items_object(tmp_path):
    path = tmp_path / "requirements.json"
    write_json(path, {"items": [{"requirement_id": "REQ-1", "source_text": "显示轮显"}]})
    requirements = load_requirements(path)
    assert requirements[0].requirement_id == "REQ-1"
    assert requirements[0].source_text == "显示轮显"


def test_load_requirements_accepts_atomizer_atomic_jsonl(tmp_path):
    path = tmp_path / "atomic_requirements.jsonl"
    path.write_text(
        (
            '{"stable_req_id":"SREQ-0123456789ABCDEF",'
            '"req_id":"AREQ-000001",'
            '"requirement":"Need display cycle support.",'
            '"source_refs":["DOC-1#p3"],'
            '"domain":"display"}\n'
        ),
        encoding="utf-8",
    )

    requirements = load_requirements(path)

    assert requirements[0].requirement_id == "SREQ-0123456789ABCDEF"
    assert requirements[0].source_text == "Need display cycle support."
    assert requirements[0].metadata["req_id"] == "AREQ-000001"
    assert requirements[0].metadata["source_refs"] == ["DOC-1#p3"]


def test_read_jsonl(tmp_path):
    path = tmp_path / "items.jsonl"
    path.write_text('{"id": "a"}\n\n{"id": "b"}\n', encoding="utf-8")
    assert read_jsonl(path) == [{"id": "a"}, {"id": "b"}]


def test_write_json_creates_parent_and_preserves_unicode(tmp_path):
    path = tmp_path / "nested" / "out.json"
    write_json(path, {"text": "显示"})
    assert json.loads(path.read_text(encoding="utf-8"))["text"] == "显示"


def test_write_text_creates_parent(tmp_path):
    path = tmp_path / "nested" / "out.md"
    write_text(path, "# 标题\n")
    assert path.read_text(encoding="utf-8") == "# 标题\n"


def test_load_standards_and_solutions(tmp_path):
    standards = tmp_path / "standards.json"
    solutions = tmp_path / "solutions.json"
    write_json(
        standards,
        [
            {
                "clause_id": "STD-1",
                "source_file": "s.md",
                "source_section": "1",
                "title": "Display",
                "text": "The display shall cycle.",
                "keywords": ["display"],
                "applies_to": ["display"],
                "constraint_level": "must",
                "citation": "s.md 1",
            }
        ],
    )
    write_json(
        solutions,
        {
            "items": [
                {
                    "solution_id": "SOL-1",
                    "module": "Display",
                    "submodule": "Cycle",
                    "scenario": "Cycle",
                    "trigger_terms": ["display"],
                    "default_behavior": "Cycle values.",
                }
            ]
        },
    )
    assert load_standards(standards)[0].clause_id == "STD-1"
    assert load_solutions(solutions)[0].solution_id == "SOL-1"
