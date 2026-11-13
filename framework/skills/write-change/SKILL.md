---
name: write-change
description: Define a new or altered behaviour before implementing it. Use when the user wants to add a feature, change how something works, or start a new piece of work. Produces a change spec for human review.
---

# Write a change spec

Produces `docs/changes/NNN-slug/change.md`. This is the *what*, never the *how*.

Read `framework/working-guide.md` §3 and `framework/definition-of-done.md`
gates 0–1 before starting.

## Steps

### 1. Decide the track

Ask the user if it is not obvious:

- **Light** — bug fix, refactor, dependency bump, anything behaviour-preserving.
  No change spec needed. Stop here and use `tdd-slice` instead.
- **Full** — new or altered behaviour. Continue.

### 2. Identify the capabilities affected

Check `docs/capabilities/README.md`.

- Existing capability → read its document fully.
- `planned` capability → read its purpose, scope and open questions. This
  change spec is where its intended behaviour gets written; the capability
  document stays free of behaviour until gate 6. Add this change to its
  **Planned changes** list if it is not there.
- `deprecated` capability → building on it is a smell. Say so and confirm with
  the user before continuing.
- No document yet, but the area exists → say so. Writing that capability doc is
  part of this change (see `project-adopt`).
- Genuinely new, not even planned → this change will create one.

List every capability touched. A change that spans several must say so.

### 3. Understand current behaviour (gate 0)

**Read the actual code, not just the capability doc.** Then state current
behaviour in your own words, concretely: entry points, rules, edge cases,
failure modes.

If the capability doc and the code disagree, say so explicitly — correcting it
is part of this change.

For a `planned` capability, current behaviour is "not built" — but check the
code anyway and say so if any part of it already exists.

**Stop and confirm this understanding with the user before continuing.**
This gate catches more wrong changes than any other.

### 4. Ask before drafting

Ask up to five clarifying questions covering only what you cannot determine
from the code or the user's request. Prioritise:

- Scope boundaries — what is deliberately excluded
- Edge cases and failure behaviour
- Who or what consumes this, and whether they break
- Non-functional constraints (latency, volume, compliance)

**Never invent an answer.** Anything unresolved becomes `OPEN QUESTION:` in the
document.

### 5. Draft the spec

Copy `framework/templates/change.md` to `docs/changes/NNN-slug/change.md`.

- `NNN` = highest existing number + 1, zero-padded to three digits. If the
  project uses ticket IDs instead (see `docs/overview.md`), use those.
- Fill every section. Do not delete sections — write "none" where empty.
- **Acceptance criteria** use EARS phrasing (`framework/conventions.md`),
  each with a stable ID `AC-1`, `AC-2`, …
- Each criterion must be mechanically testable. If you cannot imagine the test,
  rewrite the criterion.
- Fill **"What does NOT change"** carefully. The reviewer checks the diff
  against it.
- If the change invalidates an existing test or eval, list it in the
  **"Behaviour changes to existing tests or evals"** table. Never plan to
  quietly modify one.

### 6. Check the size

If the change has more than roughly six acceptance criteria, or cannot be
implemented and reviewed in a day or two, **propose splitting it** into
separate changes, each independently shippable. Slice vertically.

### 7. Stop

Run `python3 framework/craft.py index` so the change appears in the
index — the table is generated from your frontmatter, so do not edit it by
hand. Then hand back for review.

Do not write a plan, tests or code. Gate 1 is a human decision.

## Done when

- Every section is filled
- No `OPEN QUESTION` markers remain unresolved
- Every acceptance criterion is testable and has an ID
- Current behaviour was verified against the code, not assumed
- The user has been asked to review
