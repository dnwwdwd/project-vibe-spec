# 文档维护规则

## 文档职责

| 文档 | 记录内容 | 不记录内容 |
|---|---|---|
| Requirements Ledger | 每个非 Bug 需求的分类、状态、归档和结果 | Bug 细节 |
| Bug Tracker | 现象、影响、根因、修复和验证 | 常规优化 |
| PDD | 产品定位、范围、体验、用户流程和验收 | 低层实现细节 |
| PRD | 技术约束、模块、接口、数据、兼容和验证 | 逐条需求流水账 |
| UI Guide | 视觉、交互、状态、组件和响应式规则 | 业务根因 |
| Progress | 当前口径、阶段和里程碑 | 每次细节改动 |
| Business Flow | 指定业务域的入口、主链路、状态、异常和边界 | 无关模块说明 |

## 更新矩阵

| 变化 | 必须更新 | 按需更新 |
|---|---|---|
| 新增功能 | Requirements、PDD、PRD | Flow、UI Guide、Progress |
| 功能或流程优化 | Requirements、PDD、PRD | Flow、UI Guide、Progress |
| UI 或交互优化 | Requirements、UI Guide | PDD、PRD、Flow |
| Bug 修复 | Bug Tracker | PDD、PRD、UI Guide、Flow、Progress |
| 架构、数据、检索、Agent 或接口变化 | Requirements、PDD、PRD、Flow | UI Guide、Progress |
| 仅构建或重新打包 | 无，除非项目另有规定 | 发布说明 |

## 文档映射

`DOCUMENT_MAP.md` 是模板名与项目实际路径之间的唯一映射。项目可采用 `PDD.md`、`Notus_PDD.md` 或任何约定名称；所有实施与交付说明都引用映射后的实际路径。
