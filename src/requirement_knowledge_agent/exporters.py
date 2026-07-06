from __future__ import annotations

from pathlib import Path
from typing import Any

from openpyxl import Workbook

from .io import write_json, write_text


EXCEL_HEADERS = [
    "需求编号",
    "原始需求",
    "模块",
    "子模块",
    "裁决状态",
    "置信度",
    "落地需求",
    "开发建议",
    "验收标准",
    "默认方案",
    "标准引用",
    "待确认问题",
    "推导说明",
]


def export_review_package(package: dict[str, Any], out_dir: Path) -> dict[str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "review_package.json"
    markdown_path = out_dir / "review_package.md"
    excel_path = out_dir / "software_requirements.xlsx"
    write_json(json_path, package)
    write_text(markdown_path, render_markdown(package))
    write_excel(package, excel_path)
    return {
        "json": str(json_path),
        "markdown": str(markdown_path),
        "excel": str(excel_path),
    }


def render_markdown(package: dict[str, Any]) -> str:
    lines = ["# 需求评审辅助包", ""]
    summary = package.get("summary", {})
    lines += [
        "## 汇总",
        "",
        f"- 总需求数：{summary.get('total_requirements', 0)}",
        f"- 已分析：{summary.get('analyzed', 0)}",
        f"- 输入错误：{summary.get('input_errors', 0)}",
        "",
    ]
    items = package.get("items", [])
    for decision in ("blocked", "needs_review", "suggested", "applied"):
        group = [item for item in items if item.get("decision") == decision]
        if not group:
            continue
        lines += [f"## {decision}", ""]
        for item in group:
            lines += [
                f"### {item.get('requirement_id', '')}",
                "",
                f"- 模块：{item.get('module', '')} / {item.get('submodule', '')}",
                f"- 置信度：{item.get('confidence', '')}",
                f"- 原始需求：{item.get('source_text', '')}",
                f"- 落地需求：{item.get('landing_requirement', '')}",
                f"- 推导说明：{item.get('reasoning_summary', '')}",
                f"- 默认方案：{', '.join(item.get('applied_solution_ids', []))}",
                f"- 标准引用：{_format_citations(item.get('standard_citations', []))}",
                f"- 待确认：{'; '.join(item.get('open_questions', []))}",
                "",
            ]
    if package.get("input_errors"):
        lines += ["## input_errors", ""]
        for error in package["input_errors"]:
            lines.append(f"- {error.get('requirement_id', '')}: {error.get('error', '')}")
        lines.append("")
    return "\n".join(lines)


def write_excel(package: dict[str, Any], path: Path) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "software_requirements"
    ws.append(EXCEL_HEADERS)
    for item in package.get("items", []):
        ws.append(
            [
                item.get("requirement_id", ""),
                item.get("source_text", ""),
                item.get("module", ""),
                item.get("submodule", ""),
                item.get("decision", ""),
                item.get("confidence", ""),
                item.get("landing_requirement", ""),
                "\n".join(item.get("developer_guidance", [])),
                "\n".join(item.get("acceptance_criteria", [])),
                ", ".join(item.get("applied_solution_ids", [])),
                _format_citations(item.get("standard_citations", [])),
                "\n".join(item.get("open_questions", [])),
                item.get("reasoning_summary", ""),
            ]
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)


def _format_citations(citations: list[dict[str, Any]]) -> str:
    return "; ".join(
        f"{item.get('clause_id', '')}({item.get('constraint_level', '')}): {item.get('citation', '')}"
        for item in citations
    )
