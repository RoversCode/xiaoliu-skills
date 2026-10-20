# 依据与边界

核对日期：2026-10-20。以下区分官方公开原文、现有 skill 和本技能的中文设计，不将中文适配称为 ASD-STE100 正式符合性检查。

## 一手资料实际读取范围

- [ASD/STEMG 官方 FAQ](https://www.asd-ste100.org/STE_faq.html)：已读取页面正文。公开说明短句、每句一个主题、主动语态、固定词义与术语、必要条件先于结果；也说明描述性文字在执行者未知时可用被动语态。该页强调精确表达复杂系统，不以幼儿化或改变含义为目的。
- [ASD 官方基础说明](https://www.asd-europe.org/standards-specifications/simplified-technical-english/what-are-the-basics-of-simplified-technical-english/)：官方对用词与结构原则的公开说明，可交叉核对术语一致、减少多余同义词和每句一项指令。
- [STEMG 官方 AI 白皮书](https://www.asd-ste100.org/assets/files/WhitePaper-ASD-STE100_and_AI.pdf)：已读取全部三页，署期 2026 年 6 月。用于核对事实准确、来源和人工审阅的边界；这份白皮书不是 Issue 9 标准正文。
- [ASD-STE100 官方获取入口](https://www.asd-ste100.org/STE_downloads.html)：官网说明现行版为 Issue 9（2025 年 1 月）。完整版 PDF 通过申请取得。本次没有提交申请、发送邮件或取得 Issue 9 全文及完整受控词典。

因此，不声称逐条核验了 Issue 9 全部规则，不给未核实的规则号，不附受控词典，不承诺符合性认证。本技能采用的是已核实的公开原则，不是完整标准的中文复刻。

## 借鉴现有 skill 的部分

均读取了实际 SKILL.md，采用的是下述思路，没有复制完整文件：

- [danyuchn/asd-ste100-skill](https://github.com/danyuchn/asd-ste100-skill/blob/master/SKILL.md)：句子与术语纪律，尤其是改写不改变条件、范围和确定程度；不照搬英文词数限制、固定词典或工具消息改写流程。
- [Cloudflare/eli5](https://github.com/cloudflare/cloudflare-docs/blob/production/.agents/skills/eli5/SKILL.md)：发现未声明前提与跳步，按理解层次展开，核实新增机制，说明类比失效处；去掉 Cloudflare 仓库依赖、强制类比、文档确认步骤和长审查模板。
- [neurofoo/feynman](https://github.com/neurofoo/agent-skills/blob/main/feynman/SKILL.md)：内部检查含糊点和术语缺口；不强制十二岁读者、类比、四步学习报告或公开自我审查表。
- [dbs-plain-writing](https://github.com/dontbesilent2025/dbskill/blob/main/skills/dbs-plain-writing/SKILL.md)：中文先定义、具体动作、语义核对；不继承作者个人的去行末句号习惯、产品介绍骨架或跨任务交接流程。

## 本技能补上的要求

“对象定义 → 必要要素 → 相互作用或变化 → 结果”的理解顺序，来自本次用户偏好与测试，不宣称是 ASD 标准原文要求。

默认克制旁支：不先堆历史、分类、古建故事、营销修辞或专家指标。用户明确要求的深度和范围优先，不能因此删掉重要内容。

截图用于辨认表达偏好，不作为木工知识来源。示例保留受力方向、摩擦所需接触压力和防退出条件，不将胀缩、抗震或自行锁定推广到所有榫卯。

## 验证方式

`../evals/` 保存写入技能前的基线、六个行为用例和后续试用记录。基线已观察到额外分类、未解释术语和无关指标的展开；保留基线本来正确清晰的部分，不制造失败。

验证重点是对象、术语、机制、范围和事实是否可理解，不能用字数、短句数、标题数或关键词命中代替理解效果。模型试用与审查只能验证这些可观察行为，不代表已经完成真实读者实验。
