## Change

<!-- Link the change folder, e.g. docs/changes/012-allow-cancel-after-ship/ -->

Change: `docs/changes/NNN-slug/`
Track: full / light

## What this does

One or two sentences. The detail is in the change spec.

---

## Definition of Done

See `framework/definition-of-done.md`.

### Gate 4 — implementation

- [ ] All tasks in `tasks.md` are complete
- [ ] `bash scripts/verify.sh` passes locally
- [ ] No check was disabled, skipped or weakened
- [ ] No secrets, credentials or PII in any file
- [ ] New dependencies match what the plan declared
- [ ] The diff contains nothing the change spec did not ask for

### Gate 5 — review

- [ ] Every acceptance criterion is implemented and traced to a test or eval
- [ ] No existing test or eval was weakened without explicit approval in the spec
- [ ] `framework/review-checklist.md` applied
- [ ] CI green on Ubuntu, macOS and Windows

### Gate 6 — folded back  ⚠️ the one that gets skipped

- [ ] Capability doc(s) updated to describe the new reality
- [ ] Capability change-log row added, `last-verified` updated
- [ ] `docs/architecture.md` updated, if the plan ticked any structural impact
- [ ] Generated indexes rebuilt (`python3 framework/craft.py index`)
- [ ] ADRs written and set to `accepted`
- [ ] Contract artefacts (OpenAPI / AsyncAPI / schemas) updated
- [ ] `change.md` set to `status: merged` with the date
- [ ] `docs/changes/README.md` index updated
- [ ] Regression cases added for anything that broke along the way

---

## Notes for the reviewer

Anything worth flagging: divergence from the plan, discoveries, follow-up work.
