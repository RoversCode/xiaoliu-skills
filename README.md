# 小刘的常用 Skills

这个仓库收录我常用的 Agent Skills：有些组合成完整工作流，有些适合单独使用。工作流说明如何协作与交接；每个 skill 的实际指令只保留在自己的 `SKILL.md` 中。

## 工作流

| 工作流 | 用途 |
|---|---|
| [软件开发工作流](workflows/software-development/README.md) | 从项目文档初始化、功能设计和领域建模，到单次功能开发与知识收尾。 |

进入工作流页面可查看它包含的 skill、使用顺序、交接产物和适用边界。

## 独立 Skills

目前还没有单独归档的 skill。后续不属于某条工作流的 skill 会放在 `skills/<skill-name>/`，并直接列在这里。工作流里的 skill 也可以单独调用；它们的介绍放在相应工作流页面，避免根目录清单越来越难读。

## 仓库结构

```text
README.md                         仓库介绍与目录
workflows/<workflow>/README.md    一条工作流的组成、顺序与交接约定
skills/<skill-name>/SKILL.md      可独立安装和调用的 Agent Skill
```

一个 skill 只在 `skills/` 中维护一份。工作流通过链接引用它，因此同一个 skill 将来也能参与多条工作流，无需复制文件。新增工作流时，在 `workflows/` 中写说明并把它加入上面的清单；新增独立 skill 时，把它加入“独立 Skills”清单。

## 使用

打开工作流页面选择适用的 skill。每个 `skills/<skill-name>/` 都是独立的 Agent Skill，可复制或链接到所用 Agent 的 skill 搜索目录。安装时保留整个 skill 目录，以便其中的模板、脚本和参考文件仍能通过相对路径访问。
