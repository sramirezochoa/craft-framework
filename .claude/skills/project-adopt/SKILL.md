---
name: project-adopt
description: Introduce this framework to an existing codebase that predates it. Use when setting up the framework on a project that already has code, or when writing the first capability document for an undocumented area.
---

# Adopt the framework into an existing codebase

**Do not back-write documentation for the whole system.** That is weeks of work
producing documents nobody reads, drifting from the day they are written.

Adopt lazily: document each area the first time you touch it.

## Phase 1 — Orientation (once, about an hour)

### 1. Write the project overview and architecture

Explore the repository, then fill in:

- `docs/overview.md` — stack, services, how to run it, how to test it,
  environments, domain terms, and the things a newcomer gets wrong. One page.
- `docs/architecture.md` — structure only: components, internal boundaries,
  integration points and their failure behaviour, cross-cutting concerns. Two
  pages at most.

Do **not** describe behaviour in the architecture document. That is what
capability documents are for, and duplicating it guarantees drift.

Mark anything you could not determine rather than guessing, and have the owner
confirm both before moving on.

### 2. Build the capability inventory

Identify the system's capabilities — areas of behaviour a stakeholder would
recognise by name, not implementation modules. Look at entry points: routes,
event handlers, commands, conversation intents, screens.

Add them to the table in `docs/capabilities/README.md` with
`Documented? = no`. **Names only. Do not write the documents yet.**

Granularity guidance is in the working guide §2. Propose the list to the user
and adjust — getting granularity right matters more than the names.

### 3. Make verify run

Point `scripts/verify.sh` at whatever tests and lint exist today, even if
coverage is poor. A weak gate that runs beats a strong one that does not.

Note gaps in `docs/overview.md` rather than fixing them now.

### 4. Record the starting point

Write an ADR recording the decision to adopt the framework, and the current
state of testing. Useful context later.

## Phase 2 — Lazy documentation (ongoing)

**The first time a change touches an undocumented capability**, writing its
document is part of that change — before the delta is applied.

1. Read the code for that capability thoroughly.
2. Create the document from `framework/templates/capability.md`,
   describing **behaviour as it is today**, including the parts you consider
   wrong. This is a description, not an endorsement.
3. Mark anything you could not determine as `OPEN QUESTION`, and ask.
4. Have the user confirm it is accurate. **You will get things wrong — the
   confirmation is the point.**
5. Update `docs/capabilities/README.md` to `Documented? = yes`.
6. Now proceed with `write-change` for the actual change.

Where cheap, capture current behaviour as tests or eval cases at the same time.
Executable descriptions do not drift.

## Phase 3 — Tightening (as it earns its place)

Once a few capabilities are documented:

- Add project amendments to `framework/constitution.md` for rules this
  codebase actually needs
- Strengthen `verify.sh` — add lint, coverage thresholds, the drift check
- Add regression cases for the bugs that keep recurring
- Run `drift-check` on documented capabilities periodically

## What not to do

| Don't | Why |
|---|---|
| Generate capability docs for everything at once | They will be wrong, and nobody will read them to find out |
| Have an agent write capability docs unreviewed | Confident prose describing behaviour that does not exist is worse than silence |
| Rewrite code to fit the framework | Adoption is documentation, not refactoring |
| Block all work until adoption is complete | It is never complete — that is by design |

## Done when (phase 1)

- `docs/overview.md` and `docs/architecture.md` are filled in and the user
  confirms them
- The capability inventory exists and the user agrees with the granularity
- `bash scripts/verify.sh` runs and passes
- An ADR records the adoption and the starting state
