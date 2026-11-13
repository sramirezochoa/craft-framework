---
capability: <kebab-case-name>
status: active            # planned | active | deprecated | superseded-by: <name>
owner: <team or person>
last-verified: YYYY-MM-DD
---

# Capability: <Human readable name>

> **This document describes what the system does TODAY.**
> It is not a history and not a plan. Write it in the present tense.
> Amend it at the end of every change that touches this capability (gate 6).

<!-- STATUS — what is true today depends on it:
     planned     Decided, not built. Purpose, scope, interfaces, open questions
                 and "Planned changes" only. "Current behaviour" says "Not built
                 yet." Intended behaviour goes in change specs, never here.
     active      Built. "Current behaviour" describes it.
     deprecated  Still runs exactly as described, and is being phased out:
                 fill in "Deprecation". Nothing new may depend on it.
     superseded-by: <name>
                 Replaced. Keep Purpose and a pointer to the replacement; the
                 change that removes the code deletes or trims the rest.
     A capability removed with no replacement: its removal change deletes this
     file. The history lives in that change and in git. -->

## Purpose

One or two sentences. What this capability is for, and who it serves.

## Current behaviour

*While `planned`: write "Not built yet." and nothing else.*

What the system actually does now. Enough that a new collaborator — or an agent
about to modify it — understands the behaviour without reading the code first.

Use the EARS patterns where behaviour is precise:

- When `<trigger>`, the system shall `<response>`.
- While `<state>`, the system shall `<response>`.
- If `<condition>`, then the system shall `<response>`.

### Rules and constraints

- Business rules that govern this capability
- Limits, quotas, timeouts
- Anything a change here must not break

### Failure behaviour

What happens when things go wrong — invalid input, downstream failure, timeout.

## Interfaces

| Kind | Identifier | Notes |
|---|---|---|
| HTTP | `POST /orders/{id}/cancel` | Contract in `<path>` |
| Event | `order.cancelled.v1` | Schema in `<path>` |
| Tool / function | `cancel_order` | For agent-driven features |
| UI | `<route or screen>` | |

## Where it lives

| Concern | Location |
|---|---|
| Entry point | `src/...` |
| Core logic | `src/...` |
| Persistence | `src/...` |
| Prompts (if any) | `prompts/...` |
| Tests | `test/...` |
| Evals | `evals/<capability>/` |

## Dependencies

- Other capabilities this one relies on
- External systems and what happens when they are unavailable

## Planned changes

*Only while `planned` — delete the section once the capability is `active`.*
The changes expected to build it, in order. Names, not specs: each becomes a
change spec through `write-change`, where its intended behaviour is written.

1. `<change slug>` — one line on what it delivers

## Deprecation

*Only while `deprecated` — delete otherwise.*

| | |
|---|---|
| Why | |
| Replaced by | `<capability>` or "nothing" |
| Removed by | change `NNN` (planned or in progress) |
| Decided | YYYY-MM-DD, ADR `NNNN` if one was needed |

## Not in scope

Behaviour people reasonably assume is here but isn't, and where it actually
lives. This section prevents a lot of wrong changes.

## Open questions

- `OPEN QUESTION:` anything genuinely undecided about current behaviour

## Change log

Newest first. One line per change, pointing at the folder — the detail lives
there, not here.

| Change | Date | Summary |
|---|---|---|
| `012` → `../changes/012-allow-cancel-after-ship/` | YYYY-MM-DD | Allowed cancellation up to 24h after shipment |

<!-- Link the folder once it exists:
     | [012](../changes/012-allow-cancel-after-ship/change.md) | ... | ... | -->

