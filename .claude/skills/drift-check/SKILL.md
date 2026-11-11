---
name: drift-check
description: Check whether the documentation still matches the code. Use periodically, before a release, when picking up an unfamiliar area, or when a capability document feels out of date.
---

# Check for drift

Documentation that no longer matches the code is worse than none, because
people and agents trust it. This skill finds the gap.

`framework/craft.py drift` catches structural drift mechanically. This skill
covers what a script cannot judge.

## Steps

### 1. Run the mechanical check

```bash
python3 framework/craft.py drift
```

It reports: acceptance criteria with no matching test or eval, capability docs
with stale `last-verified` dates, merged changes whose capabilities were never
updated, broken cross-references, and unresolved `OPEN QUESTION` markers in
approved documents.

Fix what it finds, or explain why each finding is acceptable.

### 2. Check prose against behaviour

Pick the capabilities to review — all of them before a release, or just the one
you are about to work in.

For each, read the document, then read the code. Look for:

| Drift type | How it shows up |
|---|---|
| **Stale** | The doc describes behaviour that was changed or removed |
| **Missing** | Code does something the doc never mentions |
| **Aspirational** | The doc describes what someone intended, not what exists |
| **Misplaced** | Behaviour documented under the wrong capability |
| **Wrong location** | "Where it lives" points at files that moved |
| **Dead interfaces** | Endpoints, events or tools listed that no longer exist |
| **Undocumented interfaces** | The reverse |

Then check `docs/architecture.md` the same way, but only for *structure*:
components that no longer exist, integration points whose failure behaviour
changed, cross-cutting approaches that were replaced. If it has started
describing behaviour, that content belongs in a capability document — move it
rather than maintaining it twice.

### 3. Check the evals still mean something

For LLM features, confirm eval cases still assert the behaviour the capability
describes, and that assertions have not been loosened over time to keep the
suite green. A suite that passes because its assertions were weakened is worse
than a failing one.

### 4. Report, do not silently rewrite

Produce a list: capability, type of drift, what the doc says, what the code
does, and the suggested correction.

**Where the doc and the code disagree, the human decides which one is wrong.**
Sometimes the code is the bug. Do not assume the code is right and quietly
rewrite the documentation to match it.

### 5. Fix

Once agreed:

- Doc was wrong → correct it, update `last-verified`, note the correction
- Code was wrong → that is a bug. Open a change (light track) with a
  regression test
- Something undocumented and significant → write it up, or open a change

## When to run this

- Before a release
- Before starting work in an area you have not touched recently
- When onboarding someone new
- As a periodic task — monthly is a reasonable default
- Whenever a capability doc surprises you
