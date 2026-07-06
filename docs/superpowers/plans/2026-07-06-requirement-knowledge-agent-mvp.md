# Requirement Knowledge Agent MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a first usable CLI-driven MVP that validates two-layer knowledge files, analyzes requirement JSONL against standard clauses and default solutions, makes semi-constrained decisions, and exports a review package.

**Architecture:** Implement a small Python package under `src/requirement_knowledge_agent/` with focused modules for models, validation, matching, decisions, analysis, exporters, and CLI. The MVP is deterministic-first; LLM generation is represented by grounded deterministic text so the review package is useful without external services.

**Tech Stack:** Python 3.11+, stdlib dataclasses/json/argparse/pathlib, pytest for tests, openpyxl for Excel export.

---

## File Structure

- `pyproject.toml`: package metadata, console script, pytest config, dependencies.
- `src/requirement_knowledge_agent/__init__.py`: package version.
- `src/requirement_knowledge_agent/models.py`: dataclasses and constants for clauses, solutions, requirements, matches, decisions, and review items.
- `src/requirement_knowledge_agent/validation.py`: schema-style validation for standards and default solutions.
- `src/requirement_knowledge_agent/io.py`: JSON/JSONL read-write helpers and fixture-friendly load functions.
- `src/requirement_knowledge_agent/matching.py`: normalized keyword matching for standards and default solutions.
- `src/requirement_knowledge_agent/decision.py`: semi-constrained decision rules.
- `src/requirement_knowledge_agent/analyzer.py`: end-to-end requirement analysis orchestration.
- `src/requirement_knowledge_agent/exporters.py`: JSON, Markdown, and Excel review package exports.
- `src/requirement_knowledge_agent/cli.py`: `rka` command implementation.
- `tests/`: pytest coverage for each component and CLI smoke behavior.

## Task 1: Package Scaffold

**Files:**
- Create: `pyproject.toml`
- Create: `src/requirement_knowledge_agent/__init__.py`
- Create: `tests/test_package.py`

- [ ] **Step 1: Add package metadata and dependencies**

Create `pyproject.toml` with a `rka` console script, pytest path setup, and `openpyxl` dependency.

- [ ] **Step 2: Add package version**

Create `src/requirement_knowledge_agent/__init__.py` with `__version__ = "0.1.0"`.

- [ ] **Step 3: Add smoke test**

Create `tests/test_package.py` asserting the package imports and exposes version `0.1.0`.

- [ ] **Step 4: Run package smoke test**

Run: `python -m pytest tests/test_package.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

Commit message: `chore: scaffold python package`

## Task 2: Models and Validation

**Files:**
- Create: `src/requirement_knowledge_agent/models.py`
- Create: `src/requirement_knowledge_agent/validation.py`
- Create: `tests/test_validation.py`

- [ ] **Step 1: Write validation tests**

Tests should cover:
- a valid standard clause passes.
- a standard clause missing `clause_id` fails.
- a valid default solution passes.
- a default solution missing `solution_id` fails.
- an invalid `constraint_level` fails.

- [ ] **Step 2: Implement dataclasses**

Add dataclasses for `StandardClause`, `DefaultSolution`, `RequirementInput`, `StandardMatch`, `SolutionMatch`, `DecisionResult`, and `ReviewItem`.

- [ ] **Step 3: Implement validators**

Implement `validate_standard_clause(raw)`, `validate_default_solution(raw)`, `load_standard_clause(raw)`, and `load_default_solution(raw)`.

- [ ] **Step 4: Run validation tests**

Run: `python -m pytest tests/test_validation.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

Commit message: `feat: validate knowledge models`

## Task 3: IO Helpers

**Files:**
- Create: `src/requirement_knowledge_agent/io.py`
- Create: `tests/test_io.py`

- [ ] **Step 1: Write IO tests**

Tests should cover reading JSON arrays, reading JSON objects with an `items` list, reading JSONL, writing JSON with UTF-8 content, and creating parent directories.

- [ ] **Step 2: Implement IO helpers**

Add `read_json`, `write_json`, `read_jsonl`, `write_text`, `load_requirements`, `load_standards`, and `load_solutions`.

- [ ] **Step 3: Run IO tests**

Run: `python -m pytest tests/test_io.py -q`
Expected: PASS.

- [ ] **Step 4: Commit**

Commit message: `feat: add knowledge IO helpers`

## Task 4: Deterministic Matchers

**Files:**
- Create: `src/requirement_knowledge_agent/matching.py`
- Create: `tests/test_matching.py`

- [ ] **Step 1: Write matcher tests**

Tests should cover:
- standard clause match by keyword.
- default solution strong match when two trigger terms match.
- default solution weak match when one trigger term matches.
- no match when terms are absent.
- Chinese and English terms are matched case-insensitively where applicable.

- [ ] **Step 2: Implement normalization and scoring**

Implement `normalize_text`, `find_terms`, `match_standards`, and `match_solutions`.

- [ ] **Step 3: Run matcher tests**

Run: `python -m pytest tests/test_matching.py -q`
Expected: PASS.

- [ ] **Step 4: Commit**

Commit message: `feat: match requirements to knowledge`

## Task 5: Semi-Constrained Decision Engine

**Files:**
- Create: `src/requirement_knowledge_agent/decision.py`
- Create: `tests/test_decision.py`

- [ ] **Step 1: Write decision tests**

Tests should cover:
- strong standard + strong solution + no conflict -> `applied`.
- weak/reference evidence -> `suggested`.
- no standard or ambiguous solution -> `needs_review`.
- explicit conflict with `must` clause -> `blocked`.
- missing related standard clause prevents `applied`.

- [ ] **Step 2: Implement decision rules**

Implement `decide_requirement(requirement, standard_matches, solution_matches, all_clause_ids)` returning `DecisionResult`.

- [ ] **Step 3: Run decision tests**

Run: `python -m pytest tests/test_decision.py -q`
Expected: PASS.

- [ ] **Step 4: Commit**

Commit message: `feat: add semi-constrained decisions`

## Task 6: Analyzer Orchestration

**Files:**
- Create: `src/requirement_knowledge_agent/analyzer.py`
- Create: `tests/test_analyzer.py`

- [ ] **Step 1: Write analyzer tests**

Tests should cover:
- a requirement with matching standard and solution produces a review item.
- `applied` items include landing requirement text and citations.
- `suggested` items include open questions.
- malformed input requirement is reported as an input error.

- [ ] **Step 2: Implement analyzer**

Implement `analyze_requirements(requirements, standards, solutions)` returning a package dict with `items`, `input_errors`, and summary counts.

- [ ] **Step 3: Run analyzer tests**

Run: `python -m pytest tests/test_analyzer.py -q`
Expected: PASS.

- [ ] **Step 4: Commit**

Commit message: `feat: analyze requirements against knowledge`

## Task 7: Exporters

**Files:**
- Create: `src/requirement_knowledge_agent/exporters.py`
- Create: `tests/test_exporters.py`

- [ ] **Step 1: Write exporter tests**

Tests should cover:
- JSON export writes `review_package.json`.
- Markdown export groups items by decision.
- Excel export writes headers and at least one row.

- [ ] **Step 2: Implement exporters**

Implement `export_review_package(package, out_dir)` plus helpers for JSON, Markdown, and Excel.

- [ ] **Step 3: Run exporter tests**

Run: `python -m pytest tests/test_exporters.py -q`
Expected: PASS.

- [ ] **Step 4: Commit**

Commit message: `feat: export review packages`

## Task 8: CLI

**Files:**
- Create: `src/requirement_knowledge_agent/cli.py`
- Create: `tests/test_cli.py`
- Modify: `README.md`

- [ ] **Step 1: Write CLI tests**

Tests should cover:
- `rka init-kb --out <dir>` creates `standards.json` and `default_solutions.json`.
- `rka analyze --requirements <file> --kb <dir> --out <dir>` writes all review package outputs.
- CLI returns non-zero for missing files.

- [ ] **Step 2: Implement CLI**

Implement `main(argv=None)` with `init-kb`, `validate`, and `analyze` subcommands.

- [ ] **Step 3: Update README usage**

Document install and example CLI commands in Chinese.

- [ ] **Step 4: Run CLI tests**

Run: `python -m pytest tests/test_cli.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

Commit message: `feat: add rka cli`

## Task 9: Full Verification

**Files:**
- Modify: `README.md` if final command examples need correction.

- [ ] **Step 1: Run all tests**

Run: `python -m pytest -q`
Expected: PASS.

- [ ] **Step 2: Run CLI smoke manually**

Run a small temp sample through `rka init-kb` and `rka analyze`.
Expected: `review_package.json`, `review_package.md`, and `software_requirements.xlsx` exist.

- [ ] **Step 3: Check git status**

Run: `git status --short`
Expected: no uncommitted files except intentional docs changes.

- [ ] **Step 4: Commit final docs if needed**

Commit message: `docs: document mvp usage`
