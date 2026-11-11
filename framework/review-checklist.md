# Review checklist

Used by a human reviewer, and by a reviewer agent running in a **fresh session**
(one that did not write the code). Work top to bottom; the order is deliberate.

---

## 1. Intent — does it do the right thing?

- [ ] Every acceptance criterion in `change.md` is actually implemented
- [ ] Nothing is implemented that the change spec did not ask for
- [ ] The "what does not change" section is actually true of the diff
- [ ] Scope has not crept beyond the listed capabilities

> Review the spec against the diff, not the diff on its own. A beautiful
> implementation of the wrong thing is the failure mode this catches.

## 2. Tests — is it actually verified?

- [ ] Each `AC-n` traces to at least one test or eval case
- [ ] Tests assert behaviour, not implementation detail
- [ ] Failure cases, edge cases and error paths are covered, not just the happy path
- [ ] No existing test or eval was weakened, deleted or `@Disabled` without
      explicit approval in the change spec
- [ ] For LLM features: evals assert properties (tool called, field captured,
      schema valid, refusal happened), not exact output strings
- [ ] Regression cases exist for any bug found during the work

## 3. Constitution

- [ ] No secrets in any file, including tests and fixtures
- [ ] External input is validated before reaching business logic
- [ ] Errors are handled explicitly — nothing silently swallowed
- [ ] Logs carry correlation IDs, no PII or credentials
- [ ] New dependencies were declared in the plan and are justified
- [ ] Contract changes are versioned; breaking ones have an ADR
- [ ] Project amendments in `constitution.md` are respected

## 4. Code

- [ ] The change is understandable without the author explaining it
- [ ] It follows existing patterns in the codebase, or deviates deliberately
      and says why
- [ ] No dead code, commented-out blocks, stray debug output or TODOs without
      an owner
- [ ] Naming matches the domain language used in the capability doc
- [ ] Concurrency, retries and timeouts are considered where relevant
- [ ] Failure modes degrade safely

## 5. Documentation

- [ ] Capability doc updated to reflect new reality (gate 6)
- [ ] The capability doc reads as *current state*, not as a history of changes
- [ ] ADRs written for hard-to-reverse decisions
- [ ] `change.md` status updated
- [ ] Contract artefacts regenerated and committed

## 6. Operability

- [ ] The change is observable — can you tell from logs/metrics that it works?
- [ ] Rollback is possible, and the plan says how
- [ ] Migrations are backward compatible, or a sequencing plan exists
- [ ] Configuration comes from the environment, with sane defaults

---

## Reviewing agent-written changes specifically

Extra scrutiny on the things agents get wrong:

- [ ] **Invented requirements** — behaviour in the diff that no criterion asked for
- [ ] **Unread code** — did the author actually read what it changed, or pattern-match?
- [ ] **Plausible-but-wrong API usage** — library calls that look right but aren't
- [ ] **Tests written to pass** rather than to verify — assertions that would
      pass against a broken implementation
- [ ] **Over-broad changes** — a two-line fix delivered as a refactor
- [ ] **Confident prose in docs** describing behaviour that does not exist

---

## Reviewer's note

If you cannot review it properly in one sitting, it is too big. Say so and ask
for it to be split. Approving something you did not understand is worse than
blocking it.
