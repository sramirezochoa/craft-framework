# Tasks — Change 001

## Tasks

- [x] **T1** — Write failing drift tests for the lifecycle · *AC-1, AC-2, AC-3, AC-4*
- [x] **T2** — Strip YAML comments in `frontmatter()` · *AC-4*
- [x] **T3** — Drift: error on `planned` after a merged change; warn on unknown status · *AC-1, AC-2, AC-3*
- [x] **T4** — Run `framework/tests` in verify, framework repo only · *AC-1, AC-2, AC-3, AC-4, AC-5*
- [x] **T5** — Write `project-start` skill and `stacks.md` · *AC-5*
- [x] **T6** — Lifecycle in capability template, conventions, working guide, skills, gate 6, PR template · *—*
- [x] **T7** — User guide, README, agent rules, `init` message · *—*
- [x] **T8** — ADR 0003 · *gate 6*

## Traceability

| AC | Tasks |
|---|---|
| AC-1 | T1, T3, T4 |
| AC-2 | T1, T3, T4 |
| AC-3 | T1, T3, T4 |
| AC-4 | T1, T2, T4 |
| AC-5 | T4, T5 |

## Notes

- Found while exploring: `project-adopt` pointed amendments at
  `framework/constitution.md` and verify wiring at `scripts/verify.sh`. Fixed
  here.
