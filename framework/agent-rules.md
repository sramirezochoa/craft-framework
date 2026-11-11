# Agent rules

**FRAMEWORK-OWNED — do not edit.** Project-specific instructions belong in
`AGENTS.md` at the repository root, which points here.

This file holds the rules and the process. It lives in `framework/` so that
upgrading the framework updates it — a rule added in a later version reaches
every project that upgrades, instead of being stranded in an `AGENTS.md`
someone wrote once and never revisited.

---

## Before you start any task

1. Read `framework/constitution.md` **and** `docs/amendments.md` — together
   they are the rules that never bend.
2. Read `framework/working-guide.md` — the process and which track to use.
3. Read the relevant file in `docs/capabilities/` — what the system does **today**.
4. Read `docs/overview.md` and `docs/architecture.md` — project context and
   structure.

The gate criteria live in `framework/definition-of-done.md` and nowhere else.
Any summary of them elsewhere is generated from that file — never edit a
generated block, and never trust a summary over the source.

## Ownership — never edit `framework/`

```
framework/      framework-owned. Replaced wholesale on upgrade. Do not edit.
everything else this project's. Yours to change.
```

If a framework rule or script needs project-specific content, it belongs in a
project-owned file, not in the framework file:

| Instead of editing | Put it in |
|---|---|
| `framework/constitution.md` | `docs/amendments.md` |
| `framework/agent-rules.md` | `AGENTS.md` at the root |
| the verify stages | `scripts/project/verify-impl.sh` |
| the generated CI workflow | `.github/actions/setup/action.yml` |

`bash scripts/verify.sh` warns when a framework-owned file has been modified
locally. If the framework itself is genuinely wrong, say so and stop — do not
patch it here.

> This rule is **reversed** in the framework's own repository, which is marked
> by a `.craft-framework-repo` file at the root. There, `framework/` is the
> work. `python3 framework/craft.py context` says which repository you are in.

## How work flows

Every change follows: **understand → change spec → plan → tests → implement →
review → fold back into the capability doc.**

Each step ends at a gate requiring human review. Do not jump ahead of a gate.
Full detail in `framework/working-guide.md`.

Two tracks:
- **Light** — bug fixes, tweaks, refactors. Test + code + verify. No change spec.
- **Full** — new or altered behaviour. The whole flow above.

Choosing the track is a human decision. If unsure, ask.

## Rules for agents

- **Never invent requirements.** If something is unspecified, ask or mark it
  `OPEN QUESTION` in the change spec. Do not guess and proceed.
- **Read before you write.** Never modify code or behaviour you have not read.
- **One slice at a time.** Finish and verify a task before starting the next.
- **Tests before implementation**, and confirm a new test fails for the right
  reason before making it pass.
- **Never weaken an existing test or eval** to accommodate a change. If existing
  behaviour must change, say so explicitly and get it approved.
- **Keep the capability doc true.** A change is not done until the capability
  doc reflects the new reality.
- **Stop at gates.** Hand back for review rather than continuing on assumption.
- **Secrets never go in files.** Not in specs, not in tests, not in fixtures.

## Where things live

| What | Where |
|---|---|
| What the system does today | `docs/capabilities/<name>.md` |
| How the system is built | `docs/architecture.md` |
| A unit of work in progress | `docs/changes/NNN-slug/` |
| Why we chose an approach | `docs/adr/NNNN-title.md` |
| Process, rules, templates | `framework/` |
| Behavioural test cases | `evals/` |
| Reusable procedures (skills) | `framework/skills/` |

## Skills

Load the one matching the task:

| Skill | Use when |
|---|---|
| `write-change` | Defining a new or altered behaviour |
| `plan-change` | Turning an approved change spec into a technical plan + tasks |
| `tdd-slice` | Implementing one task, tests first |
| `write-eval-cases` | Specifying behaviour of an LLM-based feature |
| `update-capability` | Folding a merged change into the capability doc |
| `drift-check` | Checking docs against code |
| `new-adr` | Recording an architectural decision |
| `project-adopt` | Introducing this framework to an existing codebase |

If your tool does not support skills, read the `SKILL.md` file directly and
follow it. They are plain markdown.

## Files you should not read

These are written for people, not for you. They contain no rule or procedure
that is not already in the files above, and reading them costs context without
adding information:

| File | Why it exists |
|---|---|
| `framework/user-guide.md` | Step-by-step instructions for humans |
| `framework/workflows.md` | The same process as diagrams — ordered steps serve you better |
| `framework/design.md` | Why the framework is shaped this way |
| `framework/CHANGELOG.md` | Framework release history |
| `framework/example/` | A worked example for people; use `framework/templates/` instead |
| `README.md` | Repository front door |

If a human asks how to get started, tell them to open
`framework/user-guide.md` — do not open it yourself and summarise it.

Read one only if the human explicitly asks you to.
