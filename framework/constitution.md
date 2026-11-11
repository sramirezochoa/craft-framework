# Constitution

**FRAMEWORK-OWNED — do not edit.** Project-specific rules go in
`docs/amendments.md`, which is read alongside this file and carries equal
weight. Edits here are lost at the next framework upgrade.

The rules that do not bend. Short on purpose — if everything is a rule, nothing
is. Process and explanation live in `working-guide.md`; this file is only the
non-negotiables.

Anyone, human or agent, may stop work by pointing at a line in this file or in
`docs/amendments.md`.

---

## Core

1. **Intent is written down before behaviour changes.** No new or altered
   behaviour ships without an approved change spec. (Exception: the light
   track — see the working guide.)
2. **Acceptance criteria are executable.** Every criterion maps to at least one
   test or eval case. A criterion no one can test is not a criterion.
3. **Tests are written before the implementation**, and are confirmed to fail
   for the right reason first.
4. **`scripts/verify.sh` must pass.** Nothing is "done" while it is red.
   Checks are never disabled, skipped or weakened to get it green.
5. **The capability document is true.** A change is not complete until the
   capability doc reflects the system's new reality.
6. **Existing behaviour is not broken silently.** If a change alters behaviour
   an existing test or eval asserts, that change is stated explicitly in the
   change spec and approved before the test is touched.
7. **Nothing is invented.** Unknowns are raised as questions or recorded as
   `OPEN QUESTION`, never resolved by assumption.
8. **Code is read before it is changed.**
9. **Every change is reviewed by a human.** Agent output is a proposal, not a
   decision.

## Quality floor

10. **No secrets in the repository.** Not in code, specs, tests, fixtures or
    eval cases. Configuration comes from the environment.
11. **Input from outside the system is validated** before it reaches business
    logic — HTTP bodies, queue messages, model output, user text.
12. **Errors are handled explicitly.** No silently swallowed exceptions, no
    empty catch blocks, no ignored error returns.
13. **Logs carry correlation, not secrets.** No PII, credentials, tokens or
    full prompts containing user data.
14. **Dependencies are added deliberately**, and a new one in a change spec is
    called out for review.

## Architecture

15. **Contracts are explicit and versioned** — HTTP, events, model/tool
    interfaces. A breaking contract change requires an ADR.
16. **Decisions that are hard to reverse get an ADR** before implementation.
17. **No change spans more than one capability without saying so.** If it does,
    the change spec lists every capability it touches.

## For LLM-based features

18. **Prompts are code.** They live in version control, are reviewed, and
    change only through the normal flow.
19. **Prompt and model changes require an eval run.** A prompt tweak is a
    behaviour change, not a config tweak.
20. **Model output is never trusted blindly.** It is validated, constrained, or
    bounded before it causes a side effect.

---

## Project amendments

Project-specific rules live in **[`docs/amendments.md`](../docs/amendments.md)**,
numbered from 21 onwards. Read both files; they are one constitution.

---

## Changing this file

This file changes only in the framework repository, via a release. If a rule
here is wrong for every project, that is a framework change: raise it at a
retro, change it upstream, bump the version. If it is wrong for *this* project,
that is an amendment, and it needs an ADR explaining why.

Rules are removed when they stop earning their place, not when they become
inconvenient.
