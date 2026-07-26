---
name: project-vibe-spec
description: Establish and follow a durable project contract for Vibe Coding. Use when creating, modifying, planning, reviewing, debugging, documenting, testing, packaging, or shipping work in a software repository, especially when the project needs requirements tracking, bug triage, synchronized product and technical documentation, safe Git scope, and verifiable delivery.
---

# Project Vibe Spec

Create a traceable delivery loop without replacing the repository's existing rules. Treat project-specific instructions as authoritative; use the starter templates only when the repository lacks an equivalent document.

## 1. Discover the contract

Before changing code, configuration, documentation, or UI:

1. Read applicable `AGENTS.md` files from the repository root upward.
2. Read the project's document map, requirements ledger, bug tracker, progress report, product/technical/UI documents, and affected business-flow documents.
3. Inspect the relevant implementation, tests, configuration, and build scripts.
4. Resolve conflicts using the project's documented priority order. State the selected rule if the conflict affects the delivery.

If the project has no contract, copy the starter files from [assets/governance-starter](assets/governance-starter) and tailor `AGENTS.md` plus `DOCUMENT_MAP.md` before substantial implementation. Read [references/document-maintenance.md](references/document-maintenance.md) for the update matrix.

## 2. Classify and record the work

Classify each independent request before implementation:

- **Bug**: an existing promise, design, or implementation fails. Record it in the bug tracker.
- **Feature**: adds a capability, page, interface, flow, configuration, or rule. Record it in the requirements ledger.
- **Functional improvement**: strengthens or changes an existing capability, boundary, or process. Record it in the requirements ledger.
- **UX improvement**: improves interaction, visual hierarchy, copy, feedback, defaults, or comprehension. Record it in the requirements ledger.
- **Packaging only**: do not create a product requirement or bug record unless the project explicitly requires it.

Split mixed bug and improvement requests. Create a detailed requirement record for broad, long-running, or cross-module work. Read [references/document-maintenance.md](references/document-maintenance.md) before choosing documents to update.

## 3. Implement within confirmed boundaries

- Confirm product scope, data, permissions, security, compatibility, and runtime constraints before designing the change.
- Make the smallest complete change. Preserve unrelated user changes.
- Reuse the repository's established abstractions, dependencies, and platform boundaries.
- Keep credentials, local data, generated artifacts, dependencies, and logs out of version control unless the project explicitly includes them.
- Identify exact targets before destructive actions. Prefer recoverable actions.

Stop for direction when a missing decision would materially expand the product scope, change external state, or make an unsafe assumption.

## 4. Synchronize the source of truth

Update documentation with implementation rather than after it:

| Change | Update when affected |
|---|---|
| Product behavior, scope, or user flow | PDD and requirement record |
| Architecture, API, data, runtime, or compatibility | PRD and affected flow documents |
| UI, interaction, copy, defaults, or responsive behavior | UI Guide |
| Agent, search, indexing, automation, or data flow | affected business-flow documents |
| Bug investigation or repair | bug tracker |
| Milestone or current project position | progress report |

Use the paths declared in the repository's document map. Do not retain conflicting old and new product statements. State why a relevant document remains unchanged when that would otherwise be ambiguous.

## 5. Validate and deliver

Run the smallest sufficient checks for the risk: focused tests, static checks, build, and an affected user path when practical. Never describe an unrun check as passing.

Before staging or publishing, inspect the worktree, branch, remotes, ignored files, and project-specific public/private submission scope. Stage only intended files. Push, deploy, release, or open a pull request only with user authorization.

In the final handoff, lead with the completed outcome and include:

- behavior changed;
- key files and documents changed;
- requirement or bug record updated;
- commands run and their results;
- remaining verification, risk, or user decision.
