from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .analyzer import analyze_requirements
from .exporters import export_review_package
from .io import load_requirements, load_solutions, load_standards, write_json
from .validation import KnowledgeValidationError


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "init-kb":
            return command_init_kb(args)
        if args.command == "validate":
            return command_validate(args)
        if args.command == "analyze":
            return command_analyze(args)
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

    analyze = subparsers.add_parser("analyze", help="Analyze requirements against a knowledge base.")
    analyze.add_argument("--requirements", type=Path, required=True)
    analyze.add_argument("--kb", type=Path, required=True)
    analyze.add_argument("--out", type=Path, required=True)
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


def command_analyze(args: argparse.Namespace) -> int:
    standards_path, solutions_path = _kb_paths(args.kb)
    requirements = load_requirements(args.requirements)
    standards = load_standards(standards_path)
    solutions = load_solutions(solutions_path)
    package = analyze_requirements(requirements, standards, solutions)
    outputs = export_review_package(package, args.out)
    print(json.dumps({"ok": True, "outputs": outputs, "summary": package["summary"]}, ensure_ascii=False))
    return 0


def _kb_paths(kb_dir: Path) -> tuple[Path, Path]:
    standards_path = kb_dir / "standards.json"
    solutions_path = kb_dir / "default_solutions.json"
    if not standards_path.exists():
        raise FileNotFoundError(f"missing standards file: {standards_path}")
    if not solutions_path.exists():
        raise FileNotFoundError(f"missing default solutions file: {solutions_path}")
    return standards_path, solutions_path


if __name__ == "__main__":
    raise SystemExit(main())
