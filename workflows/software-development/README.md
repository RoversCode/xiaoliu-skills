# 软件开发工作流

[返回仓库目录](../../README.md)

这条工作流把项目文档初始化、功能设计、领域建模、实施计划和知识收尾连接起来。五个 skill 可以独立调用；只有当前工作需要的阶段才运行。

## 流程

```text
首次接手项目：project-docs-setup ──────────────────────────────┐
新功能：       brainstorming → planning-with-files-zh → 实施与验证 → neat-freak
                    ↕                                           ↕
              domain-modeling（术语或重要决策变化时按需参与）───────┘
```

`project-docs-setup` 通常每个项目运行一次；已有清晰文档结构时可以跳过。新功能如果需求和验收标准已经明确，可以直接进入 `planning-with-files-zh`。小修复、纯机械改动不必强制经历设计讨论或三文件计划。`neat-freak` 在功能完成后核对长期文档；独立的文档同步和交接任务也可直接调用它。

## 包含的 Skills

| Skill | 何时使用 | 主要交付物 |
|---|---|---|
| [project-docs-setup](../../skills/project-docs-setup/SKILL.md) | 首次建立或修复项目文档入口 | 已核实的项目概览、文档导航、适用的 Agent 规则入口 |
| [brainstorming](../../skills/brainstorming/SKILL.md) | 项目功能或系统行为的目标、边界、验收仍有实质歧义 | `docs/specs/` 中的设计稿，或项目既有设计文档 |
| [domain-modeling](../../skills/domain-modeling/SKILL.md) | 领域词汇、边界或重要架构决策需要澄清 | `CONTEXT.md` / `CONTEXT-MAP.md`、必要的 ADR |
| [planning-with-files-zh](../../skills/planning-with-files-zh/SKILL.md) | 开始一项已界定范围的功能开发 | `.planning/<feature>/` 下的计划、发现、进度 |
| [neat-freak](../../skills/neat-freak/SKILL.md) | 实施后更新文档、规则和交接状态 | 与实现一致的长期文档及未闭合事项清单 |

## 文档合同

| 内容 | 权威位置 | 生命周期 |
|---|---|---|
| 项目目的、使用方式和现有能力 | 现有 README / 项目文档 | 持续维护；由 `project-docs-setup` 建入口，`neat-freak` 更新 |
| 功能意图、范围和可观察的验收标准 | `docs/specs/YYYY-MM-DD-<topic>.md`，或项目既有设计文档位置 | 设计与实施的依据；需求已清楚时也可直接写简短设计记录；与最终实现不一致时要明确修订或标注状态 |
| 领域词汇和边界 | `CONTEXT.md`；多上下文项目使用 `CONTEXT-MAP.md` 指向各自的 `CONTEXT.md` | 术语确定时由 `domain-modeling` 更新；只写领域语义 |
| 难逆转且不言自明程度低的决策及理由 | `docs/adr/`，或项目既有 ADR 位置 | 决策确定时写入；后续变更明确废弃或取代关系 |
| 当前功能的步骤、发现、执行记录 | `.planning/<feature>/task_plan.md`、`findings.md`、`progress.md` | 临时工作记忆；不得成为项目事实的唯一权威来源 |
| Agent 必须遵守的项目约束和文档入口 | 当前平台实际加载的 `AGENTS.md`、`CLAUDE.md` 或等价规则文件 | 保持简短；详细机制留在文档中 |

所有路径都是新项目缺少既有约定时的默认值。已有文档布局和项目规则优先；同一事实保留一个权威解释，其余位置给出链接。不要为了凑齐目录而创建空文档。

## 一项功能怎样交接

1. 需求有实质歧义时，`brainstorming` 读项目背景和已有领域文档，形成带验收标准的设计稿；需求已清楚时，实施前直接保存简短设计记录。领域词汇或重要决策发生变化时，同时调用 `domain-modeling`。
2. `planning-with-files-zh` 读取已确定的设计稿、相关 `CONTEXT.md` 和 ADR，建立该功能的计划。三份计划文件只记录怎样实施、发现了什么、做到哪一步，并链接长期文档。
3. 实施和验证完成后，`neat-freak` 对照代码与可用的运行证据，更新 README、架构、使用和规则文档；必要时调用 `domain-modeling` 修订术语或 ADR。计划文件标记完成，临时文件是否清理由项目规则和当前授权决定。

## 迁移说明

`project-docs-setup` 是原 `setup-matt-pocock-skills` 的工作流版本：保留“建立项目文档入口”的职责，移除了本流程未使用的 issue tracker、triage 配置。旧版源目录未被本仓库修改；若已安装旧版，应以新版目录替换，避免同一职责出现两份不同规则。
