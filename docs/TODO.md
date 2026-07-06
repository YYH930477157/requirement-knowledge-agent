# Requirement Knowledge Agent 后续待办

更新时间：2026-07-06

## 当前状态

MVP 已完成并推送到 GitHub，当前分支为 `codex/m1-real-kb-loop`。

已完成能力：

- Python 包骨架。
- 标准依据层和默认方案层数据模型。
- JSON/JSONL 读取。
- 确定性 matcher。
- 半约束裁决：`applied`、`suggested`、`needs_review`、`blocked`。
- 评审辅助包导出：JSON、Markdown、Excel。
- CLI：`rka init-kb`、`rka validate`、`rka analyze`、`rka ingest-solutions`、`rka ingest-meter-template-solutions`、`rka ingest-standards`、`rka evaluate`。
- 测试基线。

下一阶段重点不是直接加复杂 Agent，而是让真实标准文件、默认方案和真实需求样本跑通闭环。

## M1：真实知识库闭环

目标：让系统可以接收真实标准依据和默认方案，输出可评审的需求辅助包。

### M1.1 定义真实知识库模板

- [x] 设计标准依据层运行时字段模板。
- [x] 设计 `default_solutions.xlsx` 模板。
- [x] 在 `docs/templates/` 下保存模板字段说明。
- [x] 给每个字段标注是否必填、是否参与匹配、是否进入生成输出。

### M1.2 实现默认方案 Excel 摄入

- [x] 实现 `rka ingest-solutions`。
- [x] 支持单 sheet 标准默认方案表。
- [x] 支持列表字段和 `config_items` 基础 JSON 字符串。
- [x] 对必填字段缺失输出字段级错误。
- [x] 增加人工 fixture 测试，不依赖真实私有文件。

### M1.3 实现标准依据摄入

- [x] 实现 `rka ingest-standards`。
- [x] 支持 Markdown frontmatter。
- [x] 支持 JSON 或带 `items` 的 JSON。
- [x] 保留 `source_file`、`source_section`、`citation`。
- [x] 支持 `constraint_level` 和关键词字段校验。

### M1.4 建立真实需求样本集

- [x] 准备 10 条人工需求样本。
- [x] 覆盖 `applied`、`suggested`、`needs_review`、`blocked`。
- [x] 增加评估命令。
- [x] 输出命中率、裁决准确率和失败案例。

### M1.5 摄入电表标准化需求模板

- [x] 实现 `rka ingest-meter-template-solutions`。
- [x] 支持从电表模板中跳过 Release notes、列表、容量计算等非需求 sheet。
- [x] 支持 `系统需求`、`计量需求`、`显示需求`、`事件需求` 等需求 sheet。
- [x] 将每行需求模板转换为一条 `DefaultSolution`。
- [x] 将 `说明、示例、注意事项` 作为默认方案知识的一部分。
- [x] 从 `确认`、`需说明`、`如可配置`、`根据客户需求` 等文本生成确认问题。
- [x] 用真实附件烟测：当前可生成 952 条默认方案。

## M2：接入 requirement-atomizer-vue3

目标：让现有需求抽取项目可以把原子需求交给本项目分析。

- [x] 明确 `requirement-atomizer-vue3` 导出的 JSONL 字段。
- [x] 增加兼容输入适配。
- [x] 加入 `samples/from_atomizer.jsonl` 示例。
- [x] 编写文档说明如何从 atomizer 输出运行 `rka analyze`。
- [ ] 评估是否需要把结果导回 atomizer 桌面端。

## M3：增强匹配质量和评审控制

目标：提升真实场景中的命中稳定性，减少误套默认方案。

- [x] 为标准和默认方案匹配增加权重。
- [x] 区分标题命中、关键词命中、正文命中、模块命中。
- [x] 增加 `match_reason` 字段。
- [x] 增加冲突检测规则，例如禁止条件、排除场景、互斥方案。
- [x] 增加人工确认字段，例如 `confirmation_questions`。
- [x] 支持同一需求命中多个候选方案时输出排序和原因。

## M4：真实评估集与调参

目标：用真实模板知识和真实需求样本评估当前结构化 matcher 的效果，再决定是否需要 RAG。

- [ ] 从真实项目需求中挑选 30-50 条样本，脱敏后写入 JSONL。
- [ ] 为样本人工标注期望命中的标准条款、默认方案和裁决状态。
- [ ] 使用电表模板生成的默认方案知识库跑评估。
- [ ] 根据失败案例调整触发词、确认规则和冲突规则。
- [ ] 把高频误判沉淀回知识库或规则，而不是直接交给 LLM 猜。

## M5：再考虑 RAG / Agentic 能力

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

## 推荐下一步

1. 用 `rka ingest-meter-template-solutions` 把真实电表模板生成默认方案 JSON。
2. 从真实项目需求中挑 30-50 条做脱敏评估集。
3. 跑 `rka analyze` 和 `rka evaluate`，先看结构化 matcher 的失败案例。
4. 根据失败案例调整默认方案触发词与确认规则。
5. 评估是否需要引入 BM25/向量检索作为 M5。
