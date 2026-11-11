---
name: new-adr
description: Record an architecture decision and the reasoning behind it. Use when choosing between real alternatives on something hard to reverse, or when the user asks why something is built the way it is and the answer is not written down.
---

# Write an ADR

An Architecture Decision Record captures **why** one approach was chosen over
the alternatives. Code says what the system does; the ADR says why it is shaped
that way.

This matters especially with agents, which have no memory across sessions. An
agent that reads `docs/adr/` will not re-propose the approach already rejected
for good reason.

## Does this need an ADR?

Write one when the decision is **hard to reverse**, **affects multiple
capabilities**, or **has real alternatives someone could question later**.

| Needs an ADR | Does not |
|---|---|
| Choice of messaging or persistence technology | Which utility method to extract |
| Authentication and authorisation approach | Variable naming |
| How prompts and evals are structured | Wording of one prompt |
| Which LLM provider, and whether to abstract over it | Temperature for one call |
| A breaking contract change | An additive field |
| Sync versus async integration | Retry count |
| Amending the constitution | — |

When in doubt, ask. Decision inflation makes ADRs stop being read, which is
its own failure.

## Steps

### 1. Confirm it is not already decided

Read `docs/adr/`. If an ADR covers this, either it applies — follow it — or it
is being reversed, in which case the new ADR supersedes it explicitly and the
old one gets `status: superseded-by: NNNN`. Never edit an accepted ADR's
substance.

### 2. Write it

Copy `framework/templates/adr.md` to `docs/adr/NNNN-kebab-title.md`.
Four digits, next in sequence.

Title states the decision, not the topic:
`0007-use-outbox-for-event-publishing`, not `0007-event-publishing`.

### 3. Fill it honestly

- **Context** — the forces and constraints. Write it so someone with no memory
  of today can judge whether the context still holds.
- **Options considered** — at least two, each with real pros and cons. If an
  option has no pros, it was not a real option and should not be listed.
- **Decision** — what, and the one or two reasons that actually decided it.
- **Consequences** — what gets easier, what gets harder, what this locks in.
  Be honest about the costs. An ADR with no downsides is marketing.
- **Revisit if** — the conditions that would make this wrong. The most useful
  section two years from now.

### 4. Status

- `proposed` when drafted at gate 2
- `accepted` at gate 6, once implemented
- Never edited afterwards except to change status

## Done when

- The file exists with the next sequence number
- At least two real options are documented
- Consequences include the costs
- "Revisit if" is filled in
- Status reflects where it is in the lifecycle
- It is linked from the change folder that produced it
