---
name: tdd-slice
description: Implement one task from an approved plan, tests first. Also used for light-track work like bug fixes and refactors. Use when it is time to actually write code.
---

# Implement one slice, tests first

One task at a time. Never several at once.

## Which track

**Full track** — an approved `plan.md` and `tasks.md` exist. Pick the next
unchecked task.

**Light track** — bug fix, refactor, behaviour-preserving change. No change
spec. Start at step 2 with the bug as the criterion. A bug fix still gets a
regression test (constitution rule 2, and the working guide §5).

## Steps

### 1. Read before writing

Read the code this task touches. All of it, not a keyword search. Read the
capability doc for the behaviour you are about to change.

Never modify code you have not read (constitution rule 8).

### 2. Write the failing test

Write the test or eval case for the acceptance criteria this task covers.

- Reference the criterion in the test name or a comment: `// AC-3`
- Assert **behaviour**, not implementation detail
- Cover the failure and edge cases named in the spec, not only the happy path
- For LLM behaviour, write an eval case asserting properties — tool called,
  field captured, schema valid, refusal happened — never exact output strings
  (`framework/templates/eval-case.yaml`)

### 3. Confirm it fails for the right reason (gate 3)

Run it. Read the failure message.

It must fail because the behaviour is missing — not because of a typo, a
missing import, or a compilation error. If the message does not describe the
missing behaviour, the test is wrong. Fix the test first.

### 4. Implement

Write the smallest change that makes the test pass.

- Follow existing patterns in the codebase
- Validate external input before it reaches business logic
- Handle errors explicitly — nothing silently swallowed
- No secrets in any file
- Add only the dependencies the plan declared

### 5. Refactor

Now that it is green, improve the code without changing behaviour. Tests stay
green throughout.

### 6. Verify

```bash
bash scripts/verify.sh
```

- All existing tests and evals must still pass.
- **Never weaken, disable or delete an existing test to make this pass.** If a
  change to existing behaviour is genuinely required, stop: it must be listed
  in the change spec's "Behaviour changes to existing tests or evals" table and
  approved (constitution rule 6).
- Never disable or skip a check to get verify green (rule 4).

### 7. Mark done and repeat

Tick the task in `tasks.md`. Move to the next one.

**Stop and report** when the task list is complete, or whenever you hit
something the plan did not anticipate. An unanticipated discovery is new
information for the human, not a licence to improvise.

## Done when

- The task's tests pass
- All existing tests and evals still pass, unmodified
- `bash scripts/verify.sh` is green
- The diff contains nothing the spec did not ask for
- `tasks.md` is updated
