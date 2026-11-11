---
adr: 0001
title: Record architecture decisions
status: accepted
date: 2026-11-10
deciders: [framework]
related-change: ""
---

# 0001 — Record architecture decisions

## Context

Code and capability documents describe *what* the system does. Neither records
*why* one approach was chosen over the alternatives. Without that record,
people — and agents, which have no memory across sessions — either reverse a
decision without knowing its reasons, or follow it long after the reasons have
expired.

This matters more with AI agents in the loop: an agent that can read past
decisions will not re-propose the approach that was already rejected for good
cause.

## Options considered

### Option A — Architecture Decision Records in the repository

- **Pros:** Versioned with the code, reviewed in the same PR, readable by
  agents and humans, an established convention with existing tooling.
- **Cons:** Requires discipline; risks decision inflation if applied too widely.

### Option B — A wiki or external document store

- **Pros:** Easier for non-developers to edit.
- **Cons:** Drifts from the code, is not reviewed with changes, and agents
  working in the repository cannot see it.

## Decision

We will record architecture decisions as ADRs in `docs/adr/`, following the
convention described by Michael Nygard, using the template in
`framework/templates/adr.md`.

An ADR is required when a decision is **hard to reverse, affects multiple
capabilities, or has real alternatives someone could reasonably question
later**. Routine choices do not get one.

## Consequences

### Easier

- Future contributors and agents can see why the system is shaped as it is
- Decision review happens in the normal PR flow
- Reversals are explicit, via a superseding ADR

### Harder

- One more artefact to write at gate 2
- Requires judgement about what crosses the bar

### Committed to

- `docs/adr/` as the home for decisions, with append-only history

## Revisit if

- ADRs stop being read, which would suggest the bar is set too low
- A documentation system appears that keeps decisions this close to the code
  while being more accessible to non-developers
