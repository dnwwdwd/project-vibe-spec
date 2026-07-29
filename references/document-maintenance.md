# 文档维护规则

## 先确定实际路径

`DOCUMENT_MAP.md` 是模板职责与项目实际路径之间的唯一索引。项目可以采用 `PDD.md`、`Notus_PDD.md`、`specs/product.md` 或既有目录；实施和交付一律引用映射后的真实路径。

首次接入时优先沿用已有的近似目录。只有缺少该职责时才创建模板目录，不能把同类事实拆到两套台账中。

## 文档职责

| 文档 | 记录内容 | 不记录内容 |
|---|---|---|
| Requirements Ledger | 每个非 Bug 需求的分类、确认状态、进度文档链接、归档与结果 | Bug 细节、逐日进度正文 |
| Requirement Record | 背景、确认范围、方案、验收、依赖、影响与需求级验证 | 与需求无关的全局设计 |
| Decision Record | 数据/架构/API 等重大方案、备选项、理由、用户确认和回滚口径 | 日常实现流水账 |
| Bug Tracker | 现象、影响、根因、修复和验证 | 常规优化 |
| PDD | 产品定位、范围、体验、用户流程和验收 | 低层实现细节 |
| PRD | 技术约束、模块、接口、数据、兼容和验证 | 逐条需求流水账 |
| UI Guide | 视觉、交互、状态、组件和响应式规则 | 业务根因 |
| Project Progress | 项目当前口径、阶段和里程碑 | 每次细节改动 |
| Feature Progress Ledger | 大任务功能进度文档的位置、状态和最近更新时间 | 阶段明细和验证证据 |
| Feature Progress Record | 某个大任务的阶段计划、进度、DoD、证据、阻塞和下一步 | 无关任务的进度 |
| Business Flow | 指定业务域的入口、主链路、状态、异常和边界 | 无关模块说明 |

## 更新矩阵

| 变化 | 必须更新 | 按需更新 |
|---|---|---|
| 新增功能 | Requirements、PDD、PRD | Decision、Flow、UI Guide、Project/Feature Progress |
| 功能或流程优化 | Requirements、PDD、PRD | Decision、Flow、UI Guide、Project/Feature Progress |
| UI 或交互优化 | Requirements、UI Guide | PDD、PRD、Flow、Progress |
| Bug 修复 | Bug Tracker | PDD、PRD、UI Guide、Flow、Progress |
| 架构、数据、检索、Agent 或接口变化 | Requirements、Decision、PDD、PRD、Flow | UI Guide、Progress |
| 仅构建或重新打包 | 无，除非项目另有规定 | 发布说明 |

## 记录之间的链接

- 每个非 Bug 需求在需求台账中有唯一 ID；复杂、长期或跨模块需求必须有详细需求记录。
- 重大决策必须关联 REQ；数据表或 DDL 变更还必须写明用户确认的方案与时间。
- 大任务的需求台账填写功能进度文档链接；功能进度台账填写 REQ 链接。两处共同维护，防止文件变成孤岛。
- Bug 如果由特定需求引入，必须链接该 REQ；功能进度文档若处理 Bug，也链接 Bug ID。
- 完成时，需求记录、决策记录和功能进度文档都写入相同的验证证据或相互链接。
