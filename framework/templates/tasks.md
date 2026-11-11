# Tasks — Change NNN

Ordered. Each task is small enough to implement and verify on its own, and
traces to at least one acceptance criterion.

Mark `[x]` only when the task's tests pass and `bash scripts/verify.sh` is green.

## Tasks

- [ ] **T1** — Write failing tests for AC-1 and AC-2 · *AC-1, AC-2*
- [ ] **T2** — <implementation step> · *AC-1*
- [ ] **T3** — <implementation step> · *AC-2*
- [ ] **T4** — Write eval cases for AC-3 · *AC-3*
- [ ] **T5** — <implementation step> · *AC-3*
- [ ] **T6** — Update contract artefacts and regenerate clients · *—*
- [ ] **T7** — Update capability doc(s) · *gate 6*
- [ ] **T8** — Update `docs/architecture.md` · *gate 6, only if the plan's
      structural impact section has a tick*
- [ ] **T9** — Write/accept ADRs · *gate 6*

## Traceability

Every `AC-n` must appear at least once above. `framework/craft.py drift` checks this.

| AC | Tasks |
|---|---|
| AC-1 | T1, T2 |
| AC-2 | T1, T3 |
| AC-3 | T4, T5 |

## Notes

Anything discovered during implementation worth carrying into the capability
doc, a new change, or a retro.
