---
change: 001
title: Capability lifecycle and guided new-project setup
status: merged
track: full
capabilities: []
author: Saul Ramirez Ochoa
reviewer: Saul Ramirez Ochoa
created: 2026-11-13
merged: 2026-11-13
---

# Change 001 — Capability lifecycle and guided new-project setup

## Why

The framework serves existing codebases (`project-adopt`) but leaves a new
project with nothing. A capability is defined only as what the system does
*today*, so on day one there is nothing to write, and the user guide tells new
projects to skip capabilities and architecture altogether. Developers starting
a project want help producing its overview, rules, capabilities and
architecture.

## Current behaviour

- Capability statuses `active`, `deprecated` and `superseded-by` are listed in
  the template and `conventions.md`, with no meaning defined for any of them.
- The only home for an unbuilt capability is the "Not yet documented" list,
  worded for adoption.
- `user-guide.md` §1 says to edit four files by hand and let capabilities and
  architecture "accrete".
- `craft.py` frontmatter parsing keeps trailing `# comments`, so a document
  created from a template carries `status: draft   # draft | approved | …` as
  its status — the drift check then treats a draft change as active.

## Desired behaviour

- Capabilities have a lifecycle — `planned`, `active`, `deprecated`,
  `superseded-by: <name>` — each describing what is true today. A `planned`
  capability holds purpose and scope, never behaviour; intended behaviour lives
  in change specs.
- A `project-start` skill interviews the developer, optionally from a brief or
  pasted text, and drafts the overview, architecture, planned capabilities,
  amendments, verify wiring, CI toolchain and ADR 0001.
- Drift enforces the lifecycle.

## What does NOT change

- Existing `active` capabilities and every existing check behave as before.
- `project-adopt` stays the path for existing codebases.
- No file paths move; projects upgrade without migration.

## Acceptance criteria

| ID | Criterion |
|---|---|
| AC-1 | When a merged change lists a capability whose status is `planned`, drift shall report an error; before the change is merged it shall not. |
| AC-2 | When the capability is `active` after a merged change, drift shall pass. |
| AC-3 | When a capability's status is not `planned`, `active`, `deprecated` or `superseded-by: <name>`, drift shall warn. |
| AC-4 | When a frontmatter value carries a trailing ` # comment`, the comment shall not be part of the value, unless the value is quoted. |
| AC-5 | The framework shall ship a `project-start` skill with its stack reference, synced to the agent adapters. |

## Behaviour changes to existing tests or evals

| Test / eval | Current assertion | New assertion | Why |
|---|---|---|---|
| | | | |

## Out of scope

- Scaffolding the project's build files — change 001 of each project does it.
- Generating MCP or Codex configuration.

## Impact

| Area | Impact |
|---|---|
| Capabilities touched | none in this repository |
| Contracts | new capability statuses; `craft.py init` message |
| Data / migrations | none |
| Configuration | none |
| Clients or consumers affected | every project, on upgrade — additive |
| Rollout considerations | release 0.13.0 |

## Open questions

None.

## Decisions needing an ADR

- `planned` capabilities hold no behaviour — ADR 0003.
