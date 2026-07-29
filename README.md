# Project Vibe Spec

用于软件项目的 Vibe Coding 工作规范：在用户确认的需求与数据决策、代码、文档、测试、进度和 Git 交付之间保持同一份可追溯的事实来源。

它不会替代仓库现有的 `AGENTS.md`。已有项目规则优先；本 Skill 提供一套可复制的起步模板和一条稳定的执行闭环。

## 包含内容

- `SKILL.md`：首次接入、需求确认、数据设计确认、计划、进度、文档联动、验证与交付规则。
- `assets/governance-starter/`：新项目可复制的项目契约、目录索引、需求、决策、Bug、PDD、PRD、UI、项目进度、功能进度和业务流程模板。
- `references/document-maintenance.md`：文档职责、更新矩阵和记录关联规则。
- `references/decision-gates.md`：需求、数据表与 DDL 变更的方案确认清单。

## 安装

```bash
git clone https://github.com/dnwwdwd/project-vibe-spec.git \
  ~/.codex/skills/project-vibe-spec
```

重启或重新扫描 Codex 后，可在项目工作中直接调用 `$project-vibe-spec`。

## 使用示例

```text
使用 $project-vibe-spec，为这个仓库建立项目契约和需求台账。
```

```text
使用 $project-vibe-spec 修复这个问题，并同步相关文档与验证结果。
```

## 边界

首次接入会先审视仓库已有文档；同类目录会被沿用，缺失职责才使用模板补齐。随后将真实位置写入目标仓库根目录的 `DOCUMENT_MAP.md`，并在 `AGENTS.md` 中关联这个索引。

模板提供默认结构。将技术栈、运行命令、远程仓库、部署方式、产品规则和具体业务流程写入目标项目自己的契约文档，不要写死在通用 Skill 中。
