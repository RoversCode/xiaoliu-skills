# 小刘的常用 Skills

这个仓库收录我常用的 Agent Skills：有些组合成完整工作流，有些适合单独使用。工作流说明如何协作与交接；每个 skill 的实际指令只保留在自己的 `SKILL.md` 中。

## 工作流

| 工作流 | 用途 |
|---|---|
| [软件开发工作流](workflows/software-development/README.md) | 从项目文档初始化、功能设计和领域建模，到单次功能开发与知识收尾。 |

进入工作流页面可查看它包含的 skill、使用顺序、交接产物和适用边界。

## 独立 Skills

| Skill | 用途 |
|---|---|
| [explain-clearly](skills/explain-clearly/SKILL.md) | 用中文讲清复杂概念和运作机制，补足必要背景、连起因果，并保留事实边界。 |

工作流里的 skill 也可以单独调用；它们的介绍放在相应工作流页面，避免根目录清单越来越难读。

## 仓库结构

```text
README.md                         仓库介绍与目录
workflows/<workflow>/README.md    一条工作流的组成、顺序与交接约定
skills/<skill-name>/SKILL.md      可独立安装和调用的 Agent Skill
```

一个 skill 只在 `skills/` 中维护一份。工作流通过链接引用它，因此同一个 skill 将来也能参与多条工作流，无需复制文件。新增工作流时，在 `workflows/` 中写说明并把它加入上面的清单；新增独立 skill 时，把它加入“独立 Skills”清单。

## 命令安装

先安装 [Node.js](https://nodejs.org/)（当前 Skills CLI 要求 22.20.0 或以上，包含 npm / npx）和 [Git](https://git-scm.com/)。使用 [Skills CLI](https://github.com/vercel-labs/skills) 直接从本仓库安装；首次运行时，npx 可能询问是否下载该工具。

交互选择要安装的 skill 和目标 Agent，安装到用户目录、供各项目使用：

```sh
npx skills add RoversCode/xiaoliu-skills -g
```

安装单个 skill，例如为 Codex 安装 `neat-freak`：

```sh
npx skills add RoversCode/xiaoliu-skills --skill neat-freak --agent codex -g -y
```

安装仓库中的全部 skill：

```sh
npx skills add RoversCode/xiaoliu-skills --skill '*' --agent codex -g -y
```

`--skill` 选择名称，`--agent` 选择目标 Agent（例如 `codex`、`claude-code`、`cursor`），`-g` 安装到用户目录，`-y` 跳过安装确认。省略 `-g` 则安装到运行命令的当前项目。Windows PowerShell、macOS 和 Linux 均可使用这些命令。

安装整套开发工作流的命令见 [软件开发工作流](workflows/software-development/README.md#安装)。它按名称选择所需的五个 skill，因此后续新增其他 skill 时仍只安装这套工作流。

查看本仓库可安装的 skill：

```sh
npx skills add RoversCode/xiaoliu-skills --list
```

安装后可在 Agent 中调用对应 skill；Codex 中例如输入 `$neat-freak`。如果新 skill 没有出现，重新打开 Agent。模板、脚本和参考文件随 skill 目录一起安装。
