---
name: domain-modeling
description: 在设计或开发中澄清项目特有的领域词汇、上下文边界和重要架构决策，并维护 CONTEXT.md 与必要的 ADR；仅阅读现有术语时不触发。
---

# 领域建模

这是贯穿设计、实施和收尾的按需活动，不是必须等 `brainstorming` 结束才开始的独立关卡。先读相关代码、现有 `CONTEXT.md` / `CONTEXT-MAP.md` 和 ADR，再改变模型。

## 澄清与记录

- 术语含糊或一词多义时，用具体业务场景区分概念；与现有术语冲突时指出冲突并解决后再改文档。
- 检查用户描述与代码、数据和真实行为是否一致。不能确定的事实留待验证，不把猜测写成定义。
- 词义一旦确定，立即更新对应 `CONTEXT.md`，使用 [CONTEXT 格式](references/context-format.md)。它只承载项目特有词汇与边界，不放实现步骤、功能验收或架构流水账。已有布局优先；无布局时单上下文项目用根目录 `CONTEXT.md`，确有多个相对独立领域上下文时用根目录 `CONTEXT-MAP.md` 指向各自的 `CONTEXT.md`。按需创建。
- 只有决策难逆转、若不解释会令人意外、且确实比较过不同取舍时，才写 ADR。沿用项目 ADR 位置；没有约定时用 `docs/adr/`，格式见 [ADR 格式](references/adr-format.md)。更改既有决策时标清取代关系。

## 交接

在 `brainstorming` 的设计稿里给出相关术语和 ADR 的链接，不复制长篇定义。`planning-with-files-zh` 从这些权威文件读取约束；`neat-freak` 在实现后核对它们是否仍准确。若本次没有新术语或符合条件的决策，不制造文档。
