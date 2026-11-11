---
name: update-capability
description: Fold a completed change into the capability documents so they describe current reality. Use at the end of a change, before it is considered done. This is gate 6 and it is the step that keeps documentation from rotting.
---

# Fold a change into the capability docs

**This is the step that gets skipped, and skipping it turns every capability
document into fiction.** It is gate 6 in `framework/definition-of-done.md`.

Run it when implementation is complete and verify is green, before the change
is marked done.

## Steps

### 1. Collect what actually happened

Read the change spec, the plan, and **the actual diff**. Implementation often
diverges from the plan — the capability doc must describe what was built, not
what was planned.

Note any divergence. If it is significant, it belongs in the change spec too.

### 2. For each capability listed in the change spec

**Existing capability** — open its document and amend it in place:

- Rewrite the affected parts of **Current behaviour** so the document reads as
  a description of the system *today*, in the present tense
- Update **Rules and constraints** and **Failure behaviour**
- Update **Interfaces** if contracts changed
- Update **Where it lives** if files moved or were added
- Update **Dependencies** if new ones appeared
- Revise **Not in scope** if the boundary moved
- Resolve or carry forward any `OPEN QUESTION`
- Add one row to the **Change log** table pointing at the change folder
- Set `last-verified` to today

**New capability** — create it from `framework/templates/capability.md`
and add it to `docs/capabilities/README.md`.

### 3. Do not turn the document into a history

The change log table holds the history, one line per change. The body describes
only current state.

Wrong: *"Originally cancellation was blocked after shipping, but change 012
allowed it within 24 hours."*

Right: *"When an order has shipped, cancellation is accepted within 24 hours of
the shipment timestamp and rejected after that with HTTP 409."*

### 3b. Update the architecture document, if the plan said so

Open `plan.md` and read the **structural impact** section.

If nothing is ticked, skip this step. If anything is ticked, open
`docs/architecture.md` and update only what that tick refers to:

| Ticked | Update |
|---|---|
| Component added / removed / repurposed | Components table, internal structure diagram |
| Integration point changed | Integration points table, including failure behaviour |
| Cross-cutting approach changed | Cross-cutting concerns table |
| Data store changed | Data table |
| Model / prompt / tool architecture changed | That section |
| Deployment or environments changed | Environments table |

Then set `last-verified` to today.

**Structure only.** If you find yourself writing about what the system *does*,
that belongs in the capability doc — you are duplicating, and the two copies
will diverge.

### 4. Finish the rest of gate 6

- Accept the ADRs drafted at gate 2 — set `status: accepted`
- Rebuild the generated indexes:
  `python3 framework/craft.py index`
- Update and publish contract artefacts (OpenAPI, AsyncAPI, schemas)
- Set `change.md` to `status: merged` with the merge date — the index in
  `docs/changes/README.md` is generated from that frontmatter, so do not edit
  the table by hand
- Add regression cases for anything that broke during the work
- Carry unresolved questions into a new change rather than leaving them floating

### 5. Verify

```bash
bash scripts/verify.sh
```

The drift check will flag capabilities whose `last-verified` date predates a
change that touched them.

## Done when

- Every affected capability doc describes the system as it is now
- Each has a change-log row for this change and a current `last-verified` date
- `docs/architecture.md` matches, if the plan ticked any structural impact
- Generated indexes are rebuilt
- ADRs are accepted, contracts published, `change.md` marked merged
- Verify is green
