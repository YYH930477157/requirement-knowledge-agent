# Default Solutions Template

This template describes the fields used by `default_solutions.xlsx` and the generated runtime file `default_solutions.json`.

Use one worksheet. The first row must contain the field names below. Each following row is one reusable default solution.

## Fields

| Field | Required | Used for matching | Exported to review package | Description |
| --- | --- | --- | --- | --- |
| `solution_id` | Yes | No | Yes | Stable unique ID, for example `SOL-DISPLAY-0001`. |
| `module` | Yes | No | Yes | Business or software module name. |
| `submodule` | Yes | No | Yes | Smaller feature area inside the module. |
| `scenario` | Yes | No | Yes | Human-readable scenario where this solution applies. |
| `trigger_terms` | Yes | Yes | No | Terms that trigger this solution. Separate values with semicolons or new lines. |
| `default_behavior` | Yes | No | Yes | Grounded default implementation behavior. This is used to draft the landing requirement. |
| `config_items` | No | No | Yes | JSON object or JSON array of objects. Each item should include `name`, `default_value`, and optional `requires_confirmation`. |
| `boundary_conditions` | No | No | Yes | Boundary rules. Separate values with semicolons or new lines. |
| `acceptance_criteria` | No | No | Yes | Acceptance checks. Separate values with semicolons or new lines. |
| `confirmation_questions` | No | Decision guard | Yes | Questions reviewers must answer before accepting this solution. Separate values with semicolons or new lines. |
| `related_standard_clause_ids` | No | Decision guard | Yes | Standard clause IDs that support this solution. Separate values with semicolons or new lines. |
| `requires_confirmation` | No | Decision guard | Yes | Use `yes`, `true`, `1`, or `是` when the solution still needs human confirmation. |

## Example Row

| solution_id | module | submodule | scenario | trigger_terms | default_behavior | config_items | boundary_conditions | acceptance_criteria | confirmation_questions | related_standard_clause_ids | requires_confirmation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `SOL-DISPLAY-0001` | `Display` | `Cycle` | `Display values in automatic cycle` | `display; cycle; LCD` | `Software cycles through configured display entries in order.` | `[{"name":"cycle_interval_seconds","default_value":"5","requires_confirmation":true}]` | `Empty display list disables cycling.` | `Configured entries are shown in order.` | `Confirm the cycle interval.` | `STD-DISPLAY-0001` | `yes` |

## Ingestion Command

```powershell
rka ingest-solutions --input .\default_solutions.xlsx --out .\kb\default_solutions.json
```

For the meter standardized requirement workbook, use the specialized importer:

```powershell
rka ingest-meter-template-solutions --input "C:\Users\YYHwudi\Desktop\Canna-29\电表软件标准化需求列表-V2.3.12 - 2026-4-14..xlsx" --out .\kb\default_solutions.json
```

The meter importer treats each supported requirement sheet row as one default solution:

| Meter workbook column | Runtime field |
| --- | --- |
| Sheet name | `module` |
| `子模块` | `submodule` |
| `描述` | `scenario` |
| `需求`, then `需求模版`, then `说明、示例、注意事项` | `default_behavior` |
| Sheet name, sheet topic, `子模块`, cleaned `描述` | `trigger_terms` |
| `说明、示例、注意事项` | `boundary_conditions` |
| Confirmation-like notes such as `确认`, `需说明`, `如可配置`, `根据客户需求` | `confirmation_questions` and `requires_confirmation` |

The generated JSON can be checked with:

```powershell
rka validate --kb .\kb
```
