---
adr: 0003
title: Planned capabilities record scope, never behaviour
status: accepted
date: 2026-11-13
deciders: [framework]
related-change: "001"
---

# 0003 — Planned capabilities record scope, never behaviour

## Context

A capability document describes what the system does *today*. That rule is what
lets a human or an agent trust it. It also left new projects with nothing to
write: on day one the system does nothing, so the user guide told new projects
to skip capabilities entirely, and the framework had no first-class way to say
"this is what we are going to build".

`deprecated` and `superseded-by` were already allowed status values with no
defined meaning.

## Options considered

### Option A — `planned` documents that also describe intended behaviour

- **Pros:** One place to read what a capability will do.
- **Cons:** A reader cannot tell built behaviour from intended behaviour
  without checking the status, and agents will not check. Intended behaviour
  duplicates the change spec and drifts from it.

### Option B — `planned` documents that hold purpose and scope only

- **Pros:** Every capability document stays true today. Intended behaviour has
  one home — the change spec — which already exists for it.
- **Cons:** Readers wanting the intended behaviour follow a link to the change.

### Option C — Keep new projects out of capabilities until code exists

- **Pros:** No change.
- **Cons:** The status quo the user found inconsistent: the framework serves
  existing codebases and offers new ones nothing.

## Decision

We will add `planned` to the capability lifecycle, define every status in terms
of what is true today, and keep behaviour out of `planned` documents.

Because the "today" rule is the framework's main defence against documentation
rot, and the change spec already holds intended behaviour.

## Consequences

### Easier

- A new project has real capability documents from day one, written by
  `project-start`.
- Drift can enforce gate 6 for new capabilities: a merged change cannot leave
  one `planned`.

### Harder

- Gate 6 for a planned capability means writing its behaviour for the first
  time, not amending it.

### Committed to

- Four statuses: `planned`, `active`, `deprecated`, `superseded-by: <name>`.
  Adding one is a framework release.

## Revisit if

- Teams routinely keep behaviour notes in `planned` documents anyway — the
  separation is not holding.
- A capability commonly stays `planned` across many merged changes, which
  would mean the error at gate 6 is firing on legitimate work.
