# Requirement Knowledge Agent

面向需求分析的独立知识库 Agent。

本仓库用于把“标准文件”和“内部默认方案”整理成可追溯、可约束、可评审的知识层，辅助生成可落地的软件需求。

当前状态：设计阶段。

主要设计文档：

- `docs/superpowers/specs/2026-07-06-requirement-knowledge-agent-design.md`

第一版规划采用双层知识库：

- 标准依据层：条款、约束、定义、引用来源。
- 默认方案层：可复用方案、默认行为、配置项、边界条件、验收标准。

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

准备需求 JSONL：

```jsonl
{"requirement_id":"REQ-1","source_text":"电表需要支持显示轮显"}
```

运行分析：

```powershell
rka analyze --requirements .\requirements.jsonl --kb .\kb --out .\out\review
```

输出文件：

- `review_package.json`：完整机器可读结果。
- `review_package.md`：按裁决状态分组的评审报告。
- `software_requirements.xlsx`：软件侧需求工作簿。
