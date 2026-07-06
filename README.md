# Requirement Knowledge Agent

面向需求分析的独立知识库 Agent。

本仓库用于把“标准文件”和“内部默认方案”整理成可追溯、可约束、可评审的知识层，辅助生成可落地的软件需求。

当前核心思路是双层知识库：

- 标准依据层：条款、约束、定义、引用来源。
- 默认方案层：可复用方案、默认行为、配置项、边界条件、验收标准、确认问题。

目标输出是“评审辅助包”，包含落地需求、引用依据、套用或建议的默认方案、裁决状态、置信度和待确认问题。

## 快速开始

安装依赖并运行测试：

```powershell
python -m pip install -e .
python -m pytest -q
```

初始化空知识库：

```powershell
rka init-kb --out .\kb
```

从标准化默认方案 Excel 生成运行时知识库 JSON：

```powershell
rka ingest-solutions --input .\default_solutions.xlsx --out .\kb\default_solutions.json
```

从电表标准化需求模板生成默认方案知识库 JSON：

```powershell
rka ingest-meter-template-solutions --input "C:\Users\YYHwudi\Desktop\Canna-29\电表软件标准化需求列表-V2.3.12 - 2026-4-14..xlsx" --out .\kb\default_solutions.json
```

从标准 Markdown/JSON 生成运行时知识库 JSON：

```powershell
rka ingest-standards --input .\standards --out .\kb\standards.json
```

校验知识库：

```powershell
rka validate --kb .\kb
```

模板字段说明：

- `docs/templates/default-solutions-template.md`
- `docs/templates/standards-template.md`

准备需求 JSONL：

```jsonl
{"requirement_id":"REQ-1","source_text":"电表需要支持显示轮显"}
```

运行分析：

```powershell
rka analyze --requirements .\requirements.jsonl --kb .\kb --out .\out\review
```

也可以直接分析 `requirement-atomizer-vue3` 导出的原子需求 JSONL：

```powershell
rka analyze --requirements .\samples\from_atomizer.jsonl --kb .\samples\kb --out .\out\from_atomizer_review
```

运行样本评估：

```powershell
rka evaluate --requirements .\samples\requirements.jsonl --kb .\samples\kb --expected .\samples\expected_decisions.json --out .\out\evaluation_report.json
```

## 输出文件

- `review_package.json`：完整机器可读结果。
- `review_package.md`：按裁决状态分组的评审报告。
- `software_requirements.xlsx`：软件侧需求工作簿。
