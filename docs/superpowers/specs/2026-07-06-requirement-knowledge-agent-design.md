# Requirement Knowledge Agent Design

Date: 2026-07-06
Status: Pending user review

## Background

The existing `requirement-atomizer-vue3` project already extracts atomic requirements from technical documents and produces software-oriented analysis. The next step is to create an independent repository that turns internal standards and default solution patterns into a reusable knowledge system for requirement analysis.

This project is not a general chat RAG system. It is a requirement-analysis support system where knowledge must be traceable, default solutions must not be silently over-applied, and generated implementation requirements must be reviewable.

## Goals

- Create an independent repository named `requirement-knowledge-agent`.
- Maintain a two-layer knowledge base:
  - standard evidence layer for standards, clauses, definitions, constraints, and citations.
  - default solution layer for internal solution patterns, default behaviors, configuration items, boundary conditions, and acceptance criteria.
- Analyze incoming requirements against both layers.
- Apply a semi-constrained decision model:
  - matched standards and matched default solutions constrain output.
  - unmatched cases may receive LLM suggestions, but must be marked as suggestions or review items.
- Generate a review assistance package that includes landing requirements, citations, applied/default solution records, confidence, and open questions.
- Keep the project independently usable through CLI and file-based input/output first.
- Leave room for later integration with `requirement-atomizer-vue3`.

## Non-Goals

- Do not replace `requirement-atomizer-vue3`.
- Do not build a full Agentic RAG planner in the first version.
- Do not require a vector database in the first version.
- Do not let the LLM invent standard references, default values, numbers, protocol codes, or source citations.
- Do not treat all knowledge as free-form text. Structured standards and default solutions must remain first-class data.

## Repository Boundary

`requirement-atomizer-vue3` remains responsible for:

- document parsing.
- atomic requirement extraction.
- existing deterministic and LLM-assisted analysis flows.
- desktop UI and current review workflows.

`requirement-knowledge-agent` is responsible for:

- ingesting standards and default solution files.
- compiling knowledge into validated runtime artifacts.
- matching requirements against standards and default solutions.
- deciding whether a default solution can be applied, suggested, reviewed, or blocked.
- generating review assistance outputs.

The first integration contract is file-based:

```text
Input:
- raw requirement text
- atomic requirement JSON or JSONL
- standard source files
- default solution tables

Output:
- review_package.json
- review_package.md
- software_requirements.xlsx
```

An HTTP API can be added later without changing the core decision model.

## Knowledge Model

### Standard Evidence Layer

The standard layer stores authoritative or semi-authoritative requirements from standards and internal documents.

Required fields:

```json
{
  "clause_id": "STD-CLAUSE-0001",
  "source_file": "standard.docx",
  "source_section": "4.2.1",
  "title": "Display behavior",
  "text": "The device shall ...",
  "keywords": ["display", "scroll", "obis"],
  "applies_to": ["display", "metering"],
  "constraint_level": "must",
  "citation": "standard.docx section 4.2.1"
}
```

`constraint_level` values:

- `must`: binding requirement. Conflicts block direct generation.
- `should`: preferred requirement. Conflicts require review.
- `reference`: contextual evidence. It can guide output but cannot force a decision by itself.

### Default Solution Layer

The default solution layer stores internal implementation patterns and reusable requirement templates.

Required fields:

```json
{
  "solution_id": "SOL-DISPLAY-0001",
  "module": "Display",
  "submodule": "Auto scroll",
  "scenario": "Display cyclic measurement values",
  "trigger_terms": ["display cycle", "auto scroll", "LCD"],
  "default_behavior": "The software cycles configured display items in order.",
  "config_items": [
    {
      "name": "cycle_interval_seconds",
      "default_value": "5",
      "requires_confirmation": true
    }
  ],
  "boundary_conditions": [
    "Empty display list shall not start cyclic display."
  ],
  "acceptance_criteria": [
    "Given a configured display list, the UI cycles through entries in order."
  ],
  "related_standard_clause_ids": ["STD-CLAUSE-0001"],
  "requires_confirmation": true
}
```

Default solutions can be used directly only when the requirement evidence is strong enough and no binding standard conflicts exist.

## Semi-Constrained Decision Model

Each requirement receives one decision status:

- `applied`: a default solution is strongly matched and compatible with matched `must` clauses.
- `suggested`: evidence is plausible, but the solution is not strong enough for automatic application.
- `needs_review`: required evidence is missing, conflicting, or incomplete.
- `blocked`: the requirement or selected solution conflicts with a `must` standard clause.

Decision rules for the first version:

```text
Strong standard match + strong default solution match + no must conflict
-> applied

Reference/should standard match + weak default solution match
-> suggested

No standard evidence, missing default fields, or ambiguous module match
-> needs_review

Contradiction with matched must clause
-> blocked
```

LLM generation must respect the decision:

- `applied`: may generate landing requirement text using matched standards and default solution fields.
- `suggested`: may generate a proposal, but the output must label it as a suggestion.
- `needs_review`: may summarize gaps and propose questions, but must not present the solution as accepted.
- `blocked`: must not generate a landing solution except to explain the conflict.

## Data Flow

```text
Source standards and default solution files
-> ingestion
-> validated knowledge artifacts
-> requirement input
-> standard matcher
-> default solution matcher
-> decision engine
-> constrained generator
-> review package exporter
```

The first version uses deterministic structured matching before LLM generation:

- exact IDs and source references.
- normalized keyword matching.
- module and submodule vocabulary matching.
- relation checks between default solutions and standard clauses.

Vector search and reranking can be added later behind the matcher interface.

## Review Package Output

Each analyzed requirement produces:

```json
{
  "requirement_id": "REQ-0001",
  "source_text": "Original requirement text",
  "module": "Display",
  "submodule": "Auto scroll",
  "decision": "suggested",
  "confidence": 0.72,
  "landing_requirement": "Software shall ...",
  "developer_guidance": ["..."],
  "acceptance_criteria": ["..."],
  "applied_solution_ids": ["SOL-DISPLAY-0001"],
  "standard_citations": [
    {
      "clause_id": "STD-CLAUSE-0001",
      "citation": "standard.docx section 4.2.1",
      "constraint_level": "must"
    }
  ],
  "open_questions": [
    "Confirm the actual display cycle interval."
  ],
  "reasoning_summary": "Matched display cycle terms and one related standard clause, but default interval requires confirmation."
}
```

The package-level outputs are:

- `review_package.json`: machine-readable full result.
- `review_package.md`: human review report grouped by decision status.
- `software_requirements.xlsx`: software-facing workbook for downstream review.

## Initial CLI Shape

The initial CLI should support:

```powershell
rka init-kb --out .\kb
rka ingest-standards --input .\standards --out .\kb\standards.json
rka ingest-solutions --input .\solutions.xlsx --out .\kb\default_solutions.json
rka analyze --requirements .\requirements.jsonl --kb .\kb --out .\out\review
```

`rka` is the tentative command name. It can be renamed before implementation if needed.

## Error Handling

- Invalid knowledge files fail validation with actionable field-level messages.
- Missing standard citations prevent `applied` decisions when a solution declares related standards.
- Malformed input requirements are skipped into an `input_errors` section instead of stopping the full run.
- LLM failure degrades to deterministic output with empty generated narrative fields and an issue note.
- Any generated value that cannot be traced to source requirement text, standard clauses, or default solution fields must be rejected or marked as suggestion-only.

## Testing Strategy

Use test fixtures that contain small artificial standards and default solutions. Do not rely on private real documents in tests.

Required test areas:

- schema validation for standard clauses.
- schema validation for default solutions.
- standard matcher returns citations and constraint levels.
- default solution matcher returns strong and weak matches.
- decision engine maps evidence to `applied`, `suggested`, `needs_review`, and `blocked`.
- generator guard rejects invented citations and ungrounded default values.
- exporters write JSON, Markdown, and Excel with expected fields.
- CLI commands return stable machine-readable envelopes.

## Integration Plan With Requirement Atomizer

The first integration should be file-based:

```text
requirement-atomizer-vue3
-> exports atomic requirements JSONL
-> requirement-knowledge-agent analyze
-> outputs review package
-> requirement-atomizer-vue3 optionally imports selected outputs
```

Later integration can add:

- local HTTP service.
- desktop UI callout.
- shared review state.
- direct use inside `ratomizer analyze`.

## Open Decisions

- Final CLI command name: `rka`, `req-kb`, or `requirement-knowledge-agent`.
- Whether the first ingestion version should support `.docx` directly or require Markdown/JSON/Excel conversion first.
- Whether `software_requirements.xlsx` should follow the current internal template exactly or use a neutral first-version workbook.
- Whether default solutions should be edited as Excel first, Markdown first, or both.
