# 需求知识库 Agent 设计

日期：2026-07-06
状态：待用户评审

## 背景

现有 `requirement-atomizer-vue3` 项目已经可以从技术文档中抽取原子需求，并输出面向软件侧的需求分析结果。下一步需要把“标准文件”和“内部默认方案”组织成一个独立知识系统，让需求分析不只是依赖模型生成，而是能够结合标准依据、默认做法和评审规则，生成可落地、可追溯、可复核的软件需求。

本项目不是普通聊天式 RAG。它的核心目标是：在需求分析过程中让知识库参与约束、裁决和生成，避免模型把默认方案、标准条款、数值、编号或引用来源自由发挥成“看起来合理但无法追溯”的内容。

## 目标

- 新建独立仓库 `requirement-knowledge-agent`。
- 建立双层知识库：
  - 标准依据层：管理标准条款、定义、约束等级、适用范围和来源引用。
  - 默认方案层：管理内部默认方案、默认行为、配置项、边界条件、验收标准和适配建议。
- 对输入需求同时匹配标准依据和默认方案。
- 建立半约束裁决机制：
  - 命中标准和默认方案时，输出必须受知识库约束。
  - 未充分命中时，允许模型给建议，但必须标记为建议或待确认，不能伪装成已确定方案。
- 生成评审辅助包，包含落地需求、标准引用、默认方案套用记录、裁决状态、置信度和待确认问题。
- 第一版优先支持 CLI 和文件式输入输出，便于独立验证。
- 后续可再接入 `requirement-atomizer-vue3` 的分析流程或桌面端。

## 非目标

- 不替换 `requirement-atomizer-vue3`。
- 第一版不做完整 Agentic RAG 多轮规划器。
- 第一版不强依赖向量数据库。
- 不允许 LLM 编造标准引用、默认值、数字、协议编号、OBIS、来源章节或其他结构化事实。
- 不把所有知识都当作自由文本处理。标准依据和默认方案必须是结构化的一等数据。

## 仓库边界

`requirement-atomizer-vue3` 继续负责：

- 文档解析。
- 原子需求抽取。
- 现有确定性和 LLM 辅助分析流程。
- 桌面端 UI 和当前评审流程。

`requirement-knowledge-agent` 负责：

- 摄入标准文件和默认方案文件。
- 编译并校验运行时知识库。
- 将需求匹配到标准依据和默认方案。
- 判断默认方案是否可以套用、仅建议、需要评审或被标准阻断。
- 生成评审辅助输出。

第一阶段采用文件式集成：

```text
输入：
- 原始需求文本
- 原子需求 JSON 或 JSONL
- 标准文件
- 默认方案表格

输出：
- review_package.json
- review_package.md
- software_requirements.xlsx
```

后续可以在不改变核心裁决模型的前提下增加本地 HTTP API。

## 知识模型

### 标准依据层

标准依据层保存来自标准文件或内部规范的权威/半权威约束。

建议字段：

```json
{
  "clause_id": "STD-CLAUSE-0001",
  "source_file": "standard.docx",
  "source_section": "4.2.1",
  "title": "显示行为",
  "text": "设备应当...",
  "keywords": ["显示", "轮显", "OBIS"],
  "applies_to": ["display", "metering"],
  "constraint_level": "must",
  "citation": "standard.docx section 4.2.1"
}
```

`constraint_level` 取值：

- `must`：强制约束。若需求或默认方案与其冲突，应阻断直接生成。
- `should`：推荐约束。若存在冲突，应进入评审确认。
- `reference`：参考依据。可用于补充上下文，但不能单独决定方案。

### 默认方案层

默认方案层保存公司内部可复用的实现模式和需求模板。

建议字段：

```json
{
  "solution_id": "SOL-DISPLAY-0001",
  "module": "显示",
  "submodule": "自动轮显",
  "scenario": "显示测量值循环展示",
  "trigger_terms": ["轮显", "自动显示", "LCD"],
  "default_behavior": "软件按配置顺序循环显示条目。",
  "config_items": [
    {
      "name": "cycle_interval_seconds",
      "default_value": "5",
      "requires_confirmation": true
    }
  ],
  "boundary_conditions": [
    "显示列表为空时不应启动轮显。"
  ],
  "acceptance_criteria": [
    "给定已配置的显示列表时，界面按顺序循环展示各条目。"
  ],
  "related_standard_clause_ids": ["STD-CLAUSE-0001"],
  "requires_confirmation": true
}
```

默认方案只有在需求证据足够强、且不违反强制标准条款时，才能作为确定方案套用。

## 半约束裁决模型

每条需求最终得到一个裁决状态：

- `applied`：默认方案强命中，且与命中的 `must` 标准兼容，可以套用。
- `suggested`：证据合理，但不足以自动套用，只能作为建议。
- `needs_review`：缺少必要依据、匹配不完整、模块不明确或存在歧义，需要人工确认。
- `blocked`：需求或默认方案与 `must` 标准冲突，不能直接生成落地方案。

第一版裁决规则：

```text
强标准命中 + 强默认方案命中 + 无 must 冲突
-> applied

should/reference 标准命中 + 弱默认方案命中
-> suggested

无标准依据、默认方案缺关键字段、模块匹配歧义
-> needs_review

与 must 标准条款冲突
-> blocked
```

LLM 生成必须服从裁决状态：

- `applied`：可以基于命中的标准和默认方案生成落地需求。
- `suggested`：可以生成建议方案，但输出必须明确标注为“建议”。
- `needs_review`：可以总结缺口和提出澄清问题，但不能把方案写成已确定需求。
- `blocked`：不能生成落地方案，只能解释冲突原因和引用依据。

## 数据流

```text
标准文件和默认方案文件
-> 摄入
-> 生成并校验知识库产物
-> 输入需求
-> 标准依据匹配
-> 默认方案匹配
-> 半约束裁决
-> 受控生成
-> 评审辅助包导出
```

第一版优先使用确定性结构化匹配，再进入 LLM 生成：

- 精确 ID 和来源引用匹配。
- 规范化关键词匹配。
- 模块/子模块词表匹配。
- 默认方案与标准条款关系校验。

向量检索、hybrid search 和 reranker 后续可以隐藏在 matcher 接口之后增加。

## 评审辅助包输出

每条需求输出结构示例：

```json
{
  "requirement_id": "REQ-0001",
  "source_text": "原始需求文本",
  "module": "显示",
  "submodule": "自动轮显",
  "decision": "suggested",
  "confidence": 0.72,
  "landing_requirement": "软件应当...",
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
    "请确认实际轮显周期。"
  ],
  "reasoning_summary": "命中了轮显相关关键词和一个标准条款，但默认周期仍需确认。"
}
```

包级输出：

- `review_package.json`：机器可读完整结果。
- `review_package.md`：按裁决状态分组的人类评审报告。
- `software_requirements.xlsx`：供软件侧继续评审和交付的需求工作簿。

## 初始 CLI 形态

第一版 CLI 建议支持：

```powershell
rka init-kb --out .\kb
rka ingest-standards --input .\standards --out .\kb\standards.json
rka ingest-solutions --input .\solutions.xlsx --out .\kb\default_solutions.json
rka analyze --requirements .\requirements.jsonl --kb .\kb --out .\out\review
```

`rka` 是暂定命令名，实施前可再改为 `req-kb` 或完整名称。

## 错误处理

- 知识库文件字段非法时，输出可操作的字段级错误。
- 默认方案声明关联标准但找不到标准条款时，不能进入 `applied`。
- 输入需求格式错误时，写入 `input_errors`，不阻断整个批次。
- LLM 调用失败时，降级为确定性输出，并记录问题说明。
- 生成内容中的数值、编号、默认值或引用来源如果无法追溯到输入需求、标准条款或默认方案字段，必须拒绝或降级为建议。

## 测试策略

测试使用小型人工 fixture，不依赖真实私有标准文件。

必须覆盖：

- 标准条款 schema 校验。
- 默认方案 schema 校验。
- 标准 matcher 能返回引用和约束等级。
- 默认方案 matcher 能区分强命中和弱命中。
- 裁决引擎能输出 `applied`、`suggested`、`needs_review`、`blocked`。
- 生成护栏能拒绝编造引用和无依据默认值。
- 导出器能写出 JSON、Markdown 和 Excel 的关键字段。
- CLI 命令返回稳定的机器可读 envelope。

## 与 Requirement Atomizer 的集成计划

第一阶段采用文件式集成：

```text
requirement-atomizer-vue3
-> 导出原子需求 JSONL
-> requirement-knowledge-agent analyze
-> 生成评审辅助包
-> requirement-atomizer-vue3 可选择导入评审结果
```

后续可扩展：

- 本地 HTTP 服务。
- 桌面端调用入口。
- 共享评审状态。
- 直接接入 `ratomizer analyze`。

## 待决策事项

- 最终 CLI 命令名使用 `rka`、`req-kb` 还是 `requirement-knowledge-agent`。
- 第一版标准摄入是否直接支持 `.docx`，还是先要求转换为 Markdown/JSON/Excel。
- `software_requirements.xlsx` 是否严格沿用现有内部模板，还是先使用中立版工作簿。
- 默认方案编辑源以 Excel 为主、Markdown 为主，还是两者都支持。
