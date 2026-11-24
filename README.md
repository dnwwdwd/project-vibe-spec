# Project Vibe Spec

用于 Vibe Coding 项目的协作与交付治理：把用户确认、项目事实、设计决策、实现、验证和进度维持在同一条可追溯链路上，同时避免把所有上下文塞进一个巨大的 `AGENTS.md`。

这套 Skill 默认沿用仓库已有规则和目录。根 `AGENTS.md` 只承担工作入口与任务路由，`DOCUMENT_MAP.md` 负责定位现行事实来源，REQ / DEC / PRD / PDD / Progress 分别保存需求、决策、项目事实和交付状态，并通过分级流程避免对微改动过度治理。

## 包含内容

- `SKILL.md`：四层治理模型、任务分级（微改动 / 常规任务 / 跨模块高风险）、决策关卡、验证与交付规则。
- `references/init-workflow.md`：可重复执行的 `init` 审计流程（含多指令文件并存策略）。
- `references/document-maintenance.md`：文档职责、统一状态机、更新矩阵、跨模块标准与模板索引。
- `references/decision-gates.md`：需求、数据模型和高风险变更的确认清单。
- `scripts/audit_governance.py`：零依赖只读审计脚本，自动检查指令文件膨胀/并存、路由断链、文档地图冲突、台账孤儿文件和未收口的待方案确认/待实机回归项。
- `assets/governance-starter/`：在仓库确实缺少某项职责时按需选用的起步模板。

## 安装

以 Codex 为例（其他支持 Skill 目录的 Agent 可克隆到对应 skills 目录）：

```bash
git clone https://github.com/dnwwdwd/project-vibe-spec.git \
  ~/.codex/skills/project-vibe-spec
```

重启或重新扫描后，可在项目中调用 `$project-vibe-spec`。

## 初始化与审计

```text
使用 $project-vibe-spec init 初始化这个仓库。
```

`init` 会先执行只读审计并检查现有规则、文档、代码、测试和构建入口，再建立或刷新：

- 根 `AGENTS.md` 尽量指向真实路径的轻量任务路由（兼容 `CLAUDE.md` 等既有指令文件，避免平行正文漂移）；
- `DOCUMENT_MAP.md` 的职责、状态（`现行` / `参考` / `待澄清` / `缺失` / `不适用`）与真实路径；
- 当前项目确实需要的需求、决策或进度台账（支持默认结构或收拢至 `docs/`）；
- 有证据的交付基线。

它不会为了凑齐模板自动生成空 PRD/PDD，也不会根据代码猜测产品原始需求。再次运行 `init` 时，只刷新已有映射与路由块，不重复创建目录或覆盖仓库自己的规则。

也可以随时独立运行只读审计脚本做健康检查：

```bash
python3 scripts/audit_governance.py /path/to/your-repo
# 严格模式（存在结构错误时返回非 0）或输出 JSON：
python3 scripts/audit_governance.py /path/to/your-repo --strict --json
```

## 日常使用

```text
使用 $project-vibe-spec 完成这个需求，并同步相关事实文档和验证记录。
```

Agent 先从当前目录适用的 `AGENTS.md` 路由命中本次所需资料，再按改动影响分级推进：微改动免建台账，常规任务复用现有台账，跨模块或数据/高风险变更走详细 REQ 与方案确认关卡。能自动化保证的约束优先落到 lint、测试、类型检查或脚本。

## 边界

模板只是缺失职责的默认结构。已有项目如果使用 `specs/`、`architecture/`、GitHub Issues、Linear、ADR 或其他组织方式，优先沿用既有目录与编号体系，并在 `DOCUMENT_MAP.md` 中如实映射。

`init` 是本 Skill 的子命令约定，不替代宿主工具自带的全局 `/init` 命令。
