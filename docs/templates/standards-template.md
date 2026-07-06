# Standards Template

This template describes the fields used by Markdown standard sources and the generated runtime file `standards.json`.

Each item is one traceable clause, definition, rule, or reference from a standard or internal specification.

## Fields

| Field | Required | Used for matching | Exported to review package | Description |
| --- | --- | --- | --- | --- |
| `clause_id` | Yes | Decision guard | Yes | Stable unique ID, for example `STD-DISPLAY-0001`. |
| `source_file` | Yes | No | Yes | Source document or file name. |
| `source_section` | Yes | No | Yes | Section, chapter, heading, or paragraph marker in the source. |
| `title` | Yes | No | Yes | Short clause title. |
| `text` | Yes | No | Yes | Clause text or summarized rule. Keep it grounded in the source. |
| `keywords` | Yes | Yes | No | Terms used to match requirements. Store as a JSON array. |
| `applies_to` | Yes | Future matching | No | Module or domain tags. Store as a JSON array. |
| `constraint_level` | Yes | Decision guard | Yes | One of `must`, `should`, or `reference`. |
| `citation` | Yes | No | Yes | Human-readable citation shown in review output. |

## Constraint Levels

| Value | Meaning |
| --- | --- |
| `must` | Hard constraint. Conflicts block direct application of a default solution. |
| `should` | Recommended constraint. Conflicts or weak evidence should go to review. |
| `reference` | Supporting context. It cannot justify an `applied` decision by itself. |

## Example JSON

```json
[
  {
    "clause_id": "STD-DISPLAY-0001",
    "source_file": "display-standard.md",
    "source_section": "4.2.1",
    "title": "Display cycle behavior",
    "text": "The device shall support configured display cycling.",
    "keywords": ["display", "cycle", "LCD"],
    "applies_to": ["display"],
    "constraint_level": "must",
    "citation": "display-standard.md section 4.2.1"
  }
]
```

Validate the file with:

```powershell
rka validate --kb .\kb
```

## Markdown Source Format

Create one `.md` file per clause. Put metadata in simple frontmatter, then put the clause text below it.

```markdown
---
clause_id: STD-DISPLAY-0001
source_section: 4.2.1
title: Display cycle behavior
keywords: display; cycle; LCD
applies_to: display
constraint_level: must
---
The device shall support configured display cycling.
```

When `source_file` is omitted, the Markdown file name is used. When `citation` is omitted, it is generated as `<source_file> section <source_section>`.

Ingest a directory with:

```powershell
rka ingest-standards --input .\standards --out .\kb\standards.json
```
