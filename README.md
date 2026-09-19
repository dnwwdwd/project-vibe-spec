# Project Vibe Spec

用于 Vibe Coding 项目的协作与交付治理：把用户确认、项目事实、设计决策、实现、验证和进度维持在同一条可追溯链路上，同时避免把所有上下文塞进一个巨大的 `AGENTS.md`。

这套 Skill 默认沿用仓库已有规则和目录。根 `AGENTS.md` 只承担工作入口与任务路由，`DOCUMENT_MAP.md` 负责定位现行事实来源，REQ/DEC/PRD/PDD/Progress 分别保存需求、决策、项目事实和交付状态。

## 包含内容

- `SKILL.md`：日常任务的需求确认、决策关卡、实现、验证和交付规则。
- `references/init-workflow.md`：可重复执行的 `init` 审计流程。
- `references/document-maintenance.md`：文档职责、状态、更新矩阵和记录关系。
- `references/decision-gates.md`：需求、数据模型和高风险变更的确认清单。
- `assets/governance-starter/`：在仓库确实缺少某项职责时才使用的起步模板。

## 安装

```bash
git clone https://github.com/dnwwdwd/project-vibe-spec.git \
  ~/.codex/skills/project-vibe-spec
```

重启或重新扫描 Codex 后，可在项目中调用 `$project-vibe-spec`。

## 初始化

```text
使用 $project-vibe-spec init 初始化这个仓库。
```

`init` 会先审计现有规则、文档、代码、测试和构建入口，再建立或刷新：

- 根 `AGENTS.md` 的轻量任务路由；
- `DOCUMENT_MAP.md` 的职责、状态与真实路径；
- 当前项目确实需要的需求、决策或进度台账；
- 有证据的交付基线。

它不会为了凑齐模板自动生成空 PRD/PDD，也不会根据代码猜测产品原始需求。已有功能可以直接作为“当前实现事实”进入基线；从初始化之后新增或继续推进的工作再用 REQ/DEC/Progress 追踪。

再次运行 `init` 时，应刷新已有映射和路由，不重复创建目录或覆盖仓库自己的规则。

## 日常使用

```text
使用 $project-vibe-spec 完成这个需求，并同步相关事实文档和验证记录。
```

Agent 先从当前目录适用的 `AGENTS.md` 判断本次需要读取哪些资料，再进入实现。长期稳定的产品、工程和设计规则留在各自正本文档里；能自动化保证的要求优先落到 lint、测试、类型检查或脚本。

## 边界

模板只是缺失职责的默认结构。已有项目如果使用 `specs/`、`architecture/`、GitHub Issues、ADR 或其他组织方式，优先沿用，并在 `DOCUMENT_MAP.md` 中记录真实位置。

`init` 是本 Skill 的子命令约定，不替代宿主工具自己的全局命令。
