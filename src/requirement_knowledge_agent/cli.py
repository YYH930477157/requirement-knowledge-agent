from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .analyzer import analyze_requirements
from .evaluation import evaluate_package
from .exporters import export_review_package
from .ingestion import ingest_meter_template_solutions, ingest_solutions_excel, ingest_standards
from .io import load_requirements, load_solutions, load_standards, read_json, write_json
from .validation import KnowledgeValidationError


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "init-kb":
            return command_init_kb(args)
        if args.command == "validate":
            return command_validate(args)
        if args.command == "ingest-solutions":
            return command_ingest_solutions(args)
        if args.command == "ingest-meter-template-solutions":
            return command_ingest_meter_template_solutions(args)
        if args.command == "ingest-standards":
            return command_ingest_standards(args)
        if args.command == "analyze":
            return command_analyze(args)
        if args.command == "evaluate":
            return command_evaluate(args)
    except (FileNotFoundError, KnowledgeValidationError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    parser.print_help()
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rka", description="Requirement Knowledge Agent CLI")
    subparsers = parser.add_subparsers(dest="command")

    init = subparsers.add_parser("init-kb", help="Create empty knowledge base files.")
    init.add_argument("--out", type=Path, required=True)

    validate = subparsers.add_parser("validate", help="Validate knowledge base files.")
    validate.add_argument("--kb", type=Path, required=True)

    ingest_solutions = subparsers.add_parser(
        "ingest-solutions",
        help="Convert a default solutions Excel workbook to runtime JSON.",
    )
    ingest_solutions.add_argument("--input", type=Path, required=True)
    ingest_solutions.add_argument("--out", type=Path, required=True)

    ingest_meter_template = subparsers.add_parser(
        "ingest-meter-template-solutions",
        help="Convert a meter standardized requirement workbook to default solutions JSON.",
    )
    ingest_meter_template.add_argument("--input", type=Path, required=True)
    ingest_meter_template.add_argument("--out", type=Path, required=True)

    ingest_standards_parser = subparsers.add_parser(
        "ingest-standards",
        help="Convert Markdown or JSON standard sources to runtime JSON.",
    )
    ingest_standards_parser.add_argument("--input", type=Path, required=True)
    ingest_standards_parser.add_argument("--out", type=Path, required=True)

    analyze = subparsers.add_parser("analyze", help="Analyze requirements against a knowledge base.")
    analyze.add_argument("--requirements", type=Path, required=True)
    analyze.add_argument("--kb", type=Path, required=True)
    analyze.add_argument("--out", type=Path, required=True)

    evaluate = subparsers.add_parser("evaluate", help="Evaluate analysis output against expected decisions.")
    evaluate.add_argument("--requirements", type=Path, required=True)
    evaluate.add_argument("--kb", type=Path, required=True)
    evaluate.add_argument("--expected", type=Path, required=True)
    evaluate.add_argument("--out", type=Path, required=True)
    return parser


def command_init_kb(args: argparse.Namespace) -> int:
    args.out.mkdir(parents=True, exist_ok=True)
    write_json(args.out / "standards.json", [])
    write_json(args.out / "default_solutions.json", [])
    print(json.dumps({"ok": True, "kb": str(args.out)}, ensure_ascii=False))
    return 0


def command_validate(args: argparse.Namespace) -> int:
    standards_path, solutions_path = _kb_paths(args.kb)
    standards = load_standards(standards_path)
    solutions = load_solutions(solutions_path)
    print(
        json.dumps(
            {"ok": True, "standards": len(standards), "default_solutions": len(solutions)},
            ensure_ascii=False,
        )
    )
    return 0


def command_ingest_solutions(args: argparse.Namespace) -> int:
    payload = ingest_solutions_excel(args.input, args.out)
    print(json.dumps({"ok": True, "out": str(args.out), "default_solutions": len(payload)}, ensure_ascii=False))
    return 0


def command_ingest_meter_template_solutions(args: argparse.Namespace) -> int:
    payload = ingest_meter_template_solutions(args.input, args.out)
    print(json.dumps({"ok": True, "out": str(args.out), "default_solutions": len(payload)}, ensure_ascii=False))
    return 0


def command_ingest_standards(args: argparse.Namespace) -> int:
    payload = ingest_standards(args.input, args.out)
    print(json.dumps({"ok": True, "out": str(args.out), "standards": len(payload)}, ensure_ascii=False))
    return 0


def command_analyze(args: argparse.Namespace) -> int:
    standards_path, solutions_path = _kb_paths(args.kb)
    requirements = load_requirements(args.requirements)
    standards = load_standards(standards_path)
    solutions = load_solutions(solutions_path)
    package = analyze_requirements(requirements, standards, solutions)
    outputs = export_review_package(package, args.out)
    print(json.dumps({"ok": True, "outputs": outputs, "summary": package["summary"]}, ensure_ascii=False))
    return 0


def command_evaluate(args: argparse.Namespace) -> int:
    standards_path, solutions_path = _kb_paths(args.kb)
    requirements = load_requirements(args.requirements)
    standards = load_standards(standards_path)
    solutions = load_solutions(solutions_path)
    package = analyze_requirements(requirements, standards, solutions)
    expected = _expected_items(args.expected)
    report = evaluate_package(package, expected)
    write_json(args.out, report)
    print(json.dumps({"ok": True, "out": str(args.out), "summary": report["summary"]}, ensure_ascii=False))
    return 0


def _kb_paths(kb_dir: Path) -> tuple[Path, Path]:
    standards_path = kb_dir / "standards.json"
    solutions_path = kb_dir / "default_solutions.json"
    if not standards_path.exists():
        raise FileNotFoundError(f"missing standards file: {standards_path}")
    if not solutions_path.exists():
        raise FileNotFoundError(f"missing default solutions file: {solutions_path}")
    return standards_path, solutions_path


def _expected_items(path: Path) -> list[dict]:
    payload = read_json(path)
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("items"), list):
        return payload["items"]
    raise ValueError("expected decisions must be a list or an object with an items list")


if __name__ == "__main__":
    raise SystemExit(main())
