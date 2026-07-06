# Requirement Knowledge Agent 后续待办

更新时间：2026-07-06

## 当前状态

MVP 已完成并推送到 GitHub：

- Python 包骨架。
- 标准依据层和默认方案层数据模型。
- JSON/JSONL 读取。
- 确定性 matcher。
- 半约束裁决：`applied`、`suggested`、`needs_review`、`blocked`。
- 评审辅助包导出：JSON、Markdown、Excel。
- CLI：`rka init-kb`、`rka validate`、`rka analyze`、`rka ingest-solutions`、`rka ingest-standards`、`rka evaluate`。
- 测试基线：53 个测试通过。

下一阶段重点不是继续加复杂 Agent，而是让真实标准文件、默认方案和真实需求样本跑通闭环。

## M1：真实知识库闭环

目标：让系统可以接收真实标准依据和默认方案，输出可评审的需求辅助包。

### M1.1 定义真实知识库模板

- [x] 设计标准依据层运行时字段模板。
- [x] 设计 `default_solutions.xlsx` 模板。
- [x] 在 `docs/templates/` 下保存模板字段说明。
- [x] 给每个字段标注是否必填、是否参与匹配、是否进入生成输出。

建议标准依据层字段：

| 字段 | 说明 |
| --- | --- |
| `clause_id` | 标准条款唯一 ID |
| `source_file` | 来源文件 |
| `source_section` | 来源章节 |
| `title` | 条款标题 |
| `text` | 条款正文 |
| `keywords` | 匹配关键词 |
| `applies_to` | 适用模块/领域 |
| `constraint_level` | `must` / `should` / `reference` |
| `citation` | 可展示引用 |

建议默认方案层字段：

| 字段 | 说明 |
| --- | --- |
| `solution_id` | 默认方案唯一 ID |
| `module` | 模块 |
| `submodule` | 子模块 |
| `scenario` | 适用场景 |
| `trigger_terms` | 触发词 |
| `default_behavior` | 默认行为 |
| `config_items` | 配置项和默认值 |
| `boundary_conditions` | 边界条件 |
| `acceptance_criteria` | 验收标准 |
| `confirmation_questions` | 人工确认问题 |
| `related_standard_clause_ids` | 关联标准条款 |
| `requires_confirmation` | 是否需要人工确认 |

验收标准：

- [x] 模板字段能完整映射到当前 JSON schema。
- [x] 默认方案示例模板能被摄入命令转换为运行时 JSON。
- [x] 字段说明能让非开发人员维护知识库。

### M1.2 实现默认方案 Excel 摄入

目标命令：

```powershell
rka ingest-solutions --input .\default_solutions.xlsx --out .\kb\default_solutions.json
```

待办：

- [x] 增加 Excel 读取依赖使用方式说明。
- [x] 实现 `ingest-solutions` CLI 子命令。
- [x] 支持单 sheet 默认方案表。
- [x] 支持用分号或换行解析 `trigger_terms`、`boundary_conditions`、`acceptance_criteria`。
- [x] 支持 `config_items` 的基础 JSON 字符串格式。
- [x] 对必填字段缺失输出字段级错误。
- [x] 增加测试 fixture，不使用真实私有文件。

验收标准：

- [x] 输入一个小型 Excel，可生成 `default_solutions.json`。
- [x] 生成的 JSON 可通过 `rka validate --kb .\kb`。
- [x] 摄入结果可被 `rka analyze` 使用。

### M1.3 实现标准依据摄入

目标命令：

```powershell
rka ingest-standards --input .\standards --out .\kb\standards.json
```

第一版建议先支持 Markdown 和 JSON，不急于直接解析复杂 PDF。

待办：

- [x] 设计 Markdown frontmatter 或简化格式。
- [x] 支持从目录读取多个 `.md` 文件。
- [x] 每个条款保留 `source_file`、`source_section`、`citation`。
- [x] 支持 `constraint_level` 默认值和合法性校验。
- [x] 支持关键词字段解析。
- [x] 增加人工 fixture 测试。

验收标准：

- [x] 输入一个标准目录，可生成 `standards.json`。
- [x] 每条标准依据都有可追溯引用。
- [x] 生成结果可参与 `rka analyze`。

### M1.4 建立真实需求样本集

目标：用真实业务样本校验 matcher 和裁决逻辑。

建议文件：

```text
samples/requirements.jsonl
samples/expected_decisions.json
```

每条样本建议包含：

| 字段 | 说明 |
| --- | --- |
| `requirement_id` | 需求 ID |
| `source_text` | 原始需求 |
| `expected_standard_clause_ids` | 期望命中的标准 |
| `expected_solution_ids` | 期望命中的默认方案 |
| `expected_decision` | 期望裁决 |
| `notes` | 人工说明 |

待办：

- [x] 准备 10 条人工需求样本。
- [x] 覆盖 `applied`、`suggested`、`needs_review`、`blocked`。
- [x] 增加评估命令或测试脚本。
- [x] 输出命中率、裁决准确率和失败案例。

验收标准：

- [x] 10 条样本可一键分析。
- [x] 每条样本都有期望结果。
- [x] 分析结果能定位误匹配和漏匹配。

## M2：接入 requirement-atomizer-vue3

目标：让现有需求抽取项目可以把原子需求交给本项目分析。

待办：

- [x] 明确 `requirement-atomizer-vue3` 导出的 JSONL 字段。
- [x] 增加兼容输入适配器。
- [x] 在本项目中加入 `samples/from_atomizer.jsonl` 示例。
- [x] 编写文档说明如何从 atomizer 输出运行 `rka analyze`。
- [ ] 评估是否需要把结果导回 atomizer 的桌面端。

验收标准：

- [x] atomizer 导出的原子需求 JSONL 可直接或轻量转换后分析。
- [x] 输出评审辅助包可被软件需求评审人员阅读。
- [x] 不破坏现有 atomizer 仓库。

## M3：增强匹配质量和评审控制

目标：提升真实场景中的命中稳定性，减少误套默认方案。

待办：

- [x] 为标准和默认方案匹配增加权重。
- [x] 区分标题命中、关键词命中、正文命中、模块命中。
- [x] 增加 `match_reason` 字段。
- [x] 增加冲突检测规则，例如禁止条件、排除场景、互斥方案。
- [x] 增加人工确认字段，例如 `confirmation_questions`。
- [x] 支持同一需求命中多个候选方案时输出排序和原因。

验收标准：

- [x] 评审包能解释“为什么命中这个方案”。
- [x] 弱证据不会误判为 `applied`。
- [x] 冲突和歧义会进入 `needs_review` 或 `blocked`。

## M4：再考虑 RAG / Agentic 能力

目标：在结构化 KB 稳定后，再引入更强检索和 Agent 能力。

暂不优先做：

- 向量数据库。
- hybrid search。
- reranker。
- 多轮 Agent planner。
- 自动拆解复杂需求。

触发条件：

- [ ] 标准文件数量明显增多，关键词匹配漏召回严重。
- [ ] 默认方案描述复杂，简单触发词不足以定位方案。
- [ ] 真实样本评估显示语义检索能明显提升效果。

候选架构：

```text
结构化 matcher
+ BM25 / sparse search
+ dense vector search
+ reranker
+ 半约束裁决
+ 受控生成
```

验收标准：

- [ ] 引入 RAG 后，评估集指标优于纯结构化 matcher。
- [ ] RAG 结果不能绕过半约束裁决。
- [ ] 所有输出仍保留标准引用和默认方案引用。

## 推荐执行顺序

1. M1.1：真实知识库模板。
2. M1.2：默认方案 Excel 摄入。
3. M1.3：标准依据 Markdown/JSON 摄入。
4. M1.4：10 条真实需求样本集。
5. M2：接入 `requirement-atomizer-vue3`。
6. M3：匹配质量和评审控制增强。
7. M4：根据评估结果决定是否引入 RAG/Agentic 能力。

## 最近下一步

建议优先开一个分支做 M1：

```powershell
git switch -c codex/m1-real-kb-loop
```

第一批任务只做：

- `docs/templates/standards-template.md`
- `docs/templates/default-solutions-template.md`
- `rka ingest-solutions`
- 对应测试

这样能最快把“默认方案表格 -> 知识库 JSON -> 需求分析输出”跑通。
