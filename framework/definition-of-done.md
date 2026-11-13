# Definition of ready / done

The gates, stated precisely. Each is a checklist someone signs off. An agent
stops here and hands back; it does not pass its own gates.

---

## Gate 0 — Understanding confirmed

<!-- gate passes="The owner agrees the restatement of current behaviour is correct" by="Owner" step="Understand" -->

**Ready to start when:**

- [ ] The affected capability is identified (or "new capability" stated)
- [ ] The capability doc has been read, or does not exist yet and will be created
- [ ] The relevant code has been read
- [ ] Current behaviour has been restated in the author's own words
- [ ] The owner agrees that restatement is correct

> Skipping this is the single commonest cause of a wrong change.

---

## Gate 1 — Change spec approved

<!-- gate passes="Criteria are testable, scope is clear, no OPEN QUESTION remains" by="Reviewer" step="Change spec" -->

**Ready for planning when:**

- [ ] `change.md` exists and follows the template
- [ ] Current behaviour and desired behaviour are both stated
- [ ] What explicitly does **not** change is stated
- [ ] Every acceptance criterion is testable and has an ID (`AC-1`, …)
- [ ] Out-of-scope items are listed
- [ ] No `OPEN QUESTION` markers remain
- [ ] Capabilities touched are listed (all of them)
- [ ] Any behaviour change to existing tests/evals is called out explicitly
- [ ] The track (light/full) is recorded
- [ ] Reviewer has approved

---

## Gate 2 — Plan approved

<!-- gate passes="The approach is sound, structural impact is decided, every AC-n is traceable to a task" by="Reviewer" step="Plan" -->

**Ready for implementation when:**

- [ ] `plan.md` exists: approach, components touched, contracts, data changes
- [ ] The **structural impact** section is filled in — every line ticked or
      "none of the above" chosen deliberately, not left blank
- [ ] Risks and their mitigations are listed
- [ ] New dependencies are called out
- [ ] Decisions needing an ADR are identified, and the ADRs are drafted
- [ ] `tasks.md` exists, ordered, each task traceable to one or more `AC-n`
- [ ] Each task is small enough to implement and verify independently
- [ ] Reviewer has approved the approach

---

## Gate 3 — Tests red for the right reason

<!-- gate passes="Tests fail because the behaviour is missing, not from a typo or compile error" by="Author" step="Tests" -->

**Ready to implement when:**

- [ ] Every `AC-n` has at least one test or eval case
- [ ] Those tests exist and **fail**
- [ ] The failure message describes the missing behaviour, not a typo, missing
      import or compilation error
- [ ] Existing tests and evals still pass unchanged

---

## Gate 4 — Implementation complete

<!-- gate passes="All tasks done, verify green, nothing in the diff the spec did not ask for" by="Author" step="Implement" -->

**Ready for review when:**

- [ ] All tasks in `tasks.md` are done
- [ ] `bash scripts/verify.sh` passes locally
- [ ] No check was disabled, skipped or weakened
- [ ] No secrets, credentials or PII added to any file
- [ ] New dependencies match what the plan declared
- [ ] The diff contains nothing the change spec did not ask for

---

## Gate 5 — Review passed

<!-- gate passes="Review checklist applied, CI green on all three operating systems" by="Reviewer" step="Review" -->

**Ready to merge when:**

- [ ] [review-checklist.md](review-checklist.md) has been applied by a human
- [ ] CI is green on all supported platforms
- [ ] Constitution compliance confirmed
- [ ] Reviewer approves

---

## Gate 6 — Change folded back (Definition of Done)

<!-- gate passes="Capability and architecture docs describe reality again, ADRs accepted, indexes rebuilt" by="Owner" step="Fold back" -->

**The change is DONE when:**

- [ ] Every affected capability doc reflects the new reality
- [ ] A capability this change built is no longer `planned` — it is `active`,
      with its current behaviour written
- [ ] The capability doc's change log references this change ID
- [ ] `docs/architecture.md` updated, if the plan's structural impact section
      had anything ticked — and `last-verified` moved on
- [ ] Generated indexes rebuilt
      (`python3 framework/craft.py index`)
- [ ] ADRs are written and marked `accepted`
- [ ] Contract artefacts (OpenAPI, AsyncAPI, schemas) are updated and published
- [ ] `change.md` status is `merged`, with the merge date
- [ ] Any `OPEN QUESTION` discovered during implementation is resolved or
      carried into a new change
- [ ] Regression cases added for anything that broke along the way
- [ ] `bash scripts/verify.sh` passes on the main branch

> **Gate 6 is the one that gets skipped.** It is on the PR template for a
> reason. A change that reaches production without it has silently converted
> the capability docs into fiction.
