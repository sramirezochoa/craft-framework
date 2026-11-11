---
change: NNN
title: <short imperative description>
status: draft           # draft | approved | in-progress | merged | abandoned
track: full             # full | light
capabilities: [<capability-name>, ...]
author: <name>
reviewer: <name>
created: YYYY-MM-DD
merged: ""
---

# Change NNN — <title>

> **This document states WHAT changes and WHY. Not how.**
> The *how* belongs in `plan.md`. Keep them separate — when they merge, specs
> become unreviewable.

## Why

The problem, request or opportunity. Who asked, and what outcome they want.
Two or three sentences.

## Current behaviour

What the system does today, in the area this change touches.

> **Fill this in by reading the capability doc AND the code. Do not assume.**
> This is gate 0. If the capability doc turns out to be wrong, correcting it is
> part of this change.

- …

## Desired behaviour

What it should do instead. Still *what*, not *how*.

- …

## What does NOT change

Explicit list. Behaviour that must be preserved, interfaces that stay stable,
assumptions that still hold. The reviewer checks the diff against this.

- …

## Acceptance criteria

Each one testable, each with a stable ID. Use EARS phrasing.

| ID | Criterion |
|---|---|
| AC-1 | When an order with status SHIPPED is cancelled within 24h of shipment, the system shall accept the request and set status to CANCELLATION_REQUESTED. |
| AC-2 | When an order with status SHIPPED is cancelled more than 24h after shipment, the system shall reject the request with HTTP 409 and leave the order unchanged. |
| AC-3 | … |

## Behaviour changes to existing tests or evals

Any existing assertion this change invalidates. **Leave empty if none — do not
delete the section.** Changing an existing test without listing it here
violates the constitution.

| Test / eval | Current assertion | New assertion | Why |
|---|---|---|---|
| | | | |

## Out of scope

What a reader might reasonably expect to be included, and is deliberately not.
Say where it will be handled, if anywhere.

- …

## Impact

| Area | Impact |
|---|---|
| Capabilities touched | |
| Contracts (HTTP, events, schemas) | |
| Data / migrations | |
| Configuration | |
| Clients or consumers affected | |
| Rollout considerations | |

## Open questions

Must be empty before this spec passes gate 1.

- `OPEN QUESTION:` …

## Decisions needing an ADR

- …  *(or "none")*
