---
name: plan-change
description: Turn an approved change spec into a technical plan and an ordered task list. Use after a change spec has been approved and before any code is written.
---

# Plan a change

Produces `plan.md` and `tasks.md` in the change folder. This is the *how*.

Prerequisite: `change.md` has `status: approved`. If it does not, stop and say so.

## Steps

### 1. Read

- The change spec in full
- `framework/constitution.md`
- The capability doc(s) listed in the spec
- The code the change will touch
- Any ADR that constrains this area

### 2. Design the approach

Choose the approach that fits existing patterns in the codebase unless there is
a reason not to — and if there is, that reason is probably an ADR.

Check against the constitution as you go, particularly:

- Contracts explicit and versioned (rule 15)
- Breaking contract changes need an ADR (rule 15)
- New dependencies called out (rule 14)
- Input validation and error handling (rules 11–12)
- Prompts are code; model changes need evals (rules 18–19)

### 3. Write the plan

Copy `framework/templates/plan.md` into the change folder and fill it in.

Be concrete: name files, modules and interfaces. A plan that could describe any
change is not a plan.

**Fill in the structural impact section deliberately.** Read
`docs/architecture.md` and decide, line by line, whether this change alters
what it describes. Never leave it blank, and do not tick "none of the above"
without having checked. Every tick becomes a task and a gate-6 item, which is
what keeps the architecture document from going stale.

For the **test strategy** table, map every `AC-n` to a test type and location.
Use eval cases for anything an LLM decides, ordinary tests for everything else.

### 4. Identify decisions needing an ADR

A decision needs one if it is hard to reverse, affects multiple capabilities, or
has real alternatives someone could question later.

Draft those ADRs now, with `status: proposed`, using the `new-adr` skill. They
are accepted at gate 6.

### 5. Break into tasks

Copy `framework/templates/tasks.md` into the change folder.

- Order them. Dependencies first.
- Each task small enough to implement and verify independently.
- Each traceable to one or more `AC-n`.
- **Test tasks come before their implementation tasks.**
- Include the gate-6 tasks: update capability doc, accept ADRs, update
  contracts, and — if the structural impact section has any tick — update
  `docs/architecture.md`.
- Fill in the traceability table. Every `AC-n` must appear.

### 6. Stop

Hand back for review. Gate 2 is a human decision.

Do not start implementing.

## Done when

- `plan.md` and `tasks.md` exist and are filled in
- Every `AC-n` appears in the test strategy and in the traceability table
- Risks, new dependencies and rollback are addressed
- ADRs are drafted for decisions that need them
- The user has been asked to review
