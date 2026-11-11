# Working guide

**The reference.** How the process works and why, organised by concept.

For step-by-step instructions organised by situation — starting a project,
building a feature, fixing a bug, reviewing a change — read
[user-guide.md](user-guide.md) instead. It is shorter and tells you what to do.
Come here when you need the reasoning, or when the user guide's steps are not
enough.

Written for humans and agents alike — if a person can follow it, an agent can.

---

## 1. Why three layers

Each layer prevents a failure the others cannot.

| Layer | Failure it prevents | Mechanism |
|---|---|---|
| **SDD** (spec-driven) | Building the thing wrong — the agent or developer guesses at intent | Written, reviewed intent before code |
| **TDD / evals** | Behaviour regressions — it worked, now it doesn't | Executable acceptance criteria |
| **Agile** | Building the wrong thing — correct implementation of a bad requirement | Small slices, frequent feedback, retros |

Drop SDD and agents drift. Drop TDD and nothing protects what already works.
Drop Agile and you build the wrong thing very precisely.

**What Agile means here** is deliberately thin: vertical slices, a feedback
cadence, a definition of ready and done, and a retro. Not story points, not
standups-for-one, not user stories as a separate artifact — the change spec
*is* the story.

---

## 2. The two nouns

### Capability — what the system does today

A living document, one per meaningful area of behaviour. Always current.
Amended at the end of every change that touches it.

`docs/capabilities/<name>.md`

Granularity rule of thumb: a capability is something you could demo on its own
and a stakeholder would recognise by name. Examples by project type:

| Project type | Capability examples |
|---|---|
| API / service | `order-cancellation`, `auth-and-sessions`, `webhook-delivery` |
| UI | `checkout-flow`, `search-and-filters`, `account-settings` |
| Bot / agent | `booking-intent`, `escalation-to-human`, `whatsapp-channel` |
| CLI / library | `config-resolution`, `plugin-loading` |

Too fine and you drown in documents. Too coarse and each becomes a dumping
ground nobody reviews. If a capability doc exceeds roughly two pages, it is
probably two capabilities.

### Change — one unit of work

A delta against one or more capabilities. Numbered, time-ordered, archived
after merge.

`docs/changes/NNN-slug/{change.md, plan.md, tasks.md}`

Greenfield is simply a change whose delta is "this capability does not exist
yet".

**Why both?** Changes alone give perfect history but make current behaviour
something you reconstruct by replaying five documents. Capabilities alone give
current truth but lose the reasoning. Together: capabilities answer *what*,
changes answer *what changed and why*, ADRs answer *why this approach*.

---

## 3. The lifecycle

Every step ends at a gate. **The exit criteria for each gate live in
[definition-of-done.md](definition-of-done.md) and nowhere else** — this
section is generated from it.

<!-- BEGIN GENERATED: gates-steps — from definition-of-done.md, do not edit by hand -->

```
 understand → change spec → plan → tests → implement → review → fold back
```

| Step | Ends at | Passed by |
|---|---|---|
| Understand | Gate 0 — Understanding confirmed | Owner |
| Change spec | Gate 1 — Change spec approved | Reviewer |
| Plan | Gate 2 — Plan approved | Reviewer |
| Tests | Gate 3 — Tests red for the right reason | Author |
| Implement | Gate 4 — Implementation complete | Author |
| Review | Gate 5 — Review passed | Reviewer |
| Fold back | Gate 6 — Change folded back (Definition of Done) | Owner |

*Generated from [definition-of-done.md](definition-of-done.md), the single source of truth for the gate model.*

<!-- END GENERATED -->

What each step produces:

| Step | Produces |
|---|---|
| **Understand** | A restatement of current behaviour, from the capability doc *and* the code |
| **Change spec** | `change.md` — current → desired, acceptance criteria, scope |
| **Plan** | `plan.md` + `tasks.md` — approach, contracts, risks, structural impact |
| **Tests** | Failing tests and eval cases, one per `AC-n` |
| **Implement** | Code, one task at a time |
| **Review** | — |
| **Fold back** | Updated capability and architecture docs, accepted ADRs, rebuilt indexes |

`scripts/verify.sh` is not a step — it runs continuously inside implementation,
on every task, and again at the last three gates.

**Gate 0 matters more than it looks.** The commonest brownfield failure is an
agent confidently changing code it never read. Making it restate current
behaviour first surfaces misunderstandings before a line is written.

**Gate 6 is the one that gets skipped**, because skipping it has no immediate
cost. Months later the capability documents describe a system that no longer
exists.

**Never skip ahead of a gate.** If you are an agent, stop and hand back.

---

## 4. Choosing a track

| | Light track | Full track |
|---|---|---|
| **Use for** | Bug fixes, refactors, dependency bumps, copy changes, anything behaviour-preserving | New behaviour, altered behaviour, new integrations, anything a user would notice |
| **Artifacts** | A test + the fix | change spec, plan, tasks, tests |
| **Capability doc** | Update only if it was wrong | Always updated |
| **ADR** | Only if a real decision was made | Same |
| **Verify** | Required | Required |

A bug fix that reveals the capability doc was *wrong* about current behaviour
still updates the doc — that is a correction, not a change.

**Choosing the track is a human decision.** When unsure, ask. The cost of the
full track on a small change is an hour; the cost of the light track on a real
behaviour change is an undocumented system.

---

## 5. Tests and evals

Two kinds of verification, because two kinds of behaviour.

**Deterministic behaviour** — the usual pyramid. Unit tests for logic,
integration tests for wiring, contract tests for interfaces. Every acceptance
criterion traces to at least one.

**Non-deterministic behaviour** (anything where an LLM decides) — eval cases
in `evals/`. This is a property of a *feature*, not of a project: a Spring
service may need ordinary tests for validation and persistence and evals for
its single classification endpoint. Scripted inputs, expected behaviours, guardrail assertions.
Assert on properties, not exact strings: which tool was called, whether the
required field was captured, whether a refusal happened, whether the output
validates against the schema.

Rules that apply to both:

- A new acceptance criterion gets a new test/eval before implementation.
- **Every production bug becomes a regression case.** No exceptions.
- Existing cases stay green. Changing one is a behaviour change requiring
  explicit approval.
- Prompt and model changes trigger an eval run — they are code.

---

## 6. The Agile layer

**Slicing.** A change should be completable and reviewable in a day or two.
If it isn't, split it into several changes, each independently shippable.
Slice vertically — through the stack — not by layer.

**Cadence.** Pick one and write it in `docs/overview.md`: a demo every
Friday, a demo at the end of each change, whatever fits the client. The point
is that someone outside the work sees it regularly and can redirect cheaply.

**Backlog.** Holds change IDs and candidate capabilities, not separate user
stories. Wherever you track it (issue tracker, a markdown file), link both ways.

**Retro.** After each slice or at the cadence boundary, ask two questions:

1. What slowed the work down or went wrong?
2. **Did the framework steer correctly?** Was the constitution right, did the
   skills produce good output, did the capability doc tell the truth?

The second question is how the framework improves instead of rotting — but
only if the answers were written down when they happened. Capture findings in
the moment:

```bash
python3 framework/craft.py feedback "gate 0 is slow on one-line copy changes" --kind ceremony
```

Then at the retro, work through `docs/framework-feedback.md` and mark each
entry:

| Verdict | Action |
|---|---|
| Project-specific | Fix it here — `docs/amendments.md` or `AGENTS.md`. Mark `local` |
| True for every project | Raise it on the framework repository. Record the link |
| Not actually a problem | Say why, mark `wontfix`, so nobody re-litigates it |

**Deviations are the most valuable entries.** Every place you quietly worked
around the process is a place the process is wrong, too slow, or unclear.
Record them without judgement.

**What the agent changes about Agile.** The bottleneck moves from writing code
to reviewing it. Tune the cadence to review capacity. Slice smaller than feels
necessary — agents produce large diffs fast, and small slices are what keep
review honest.

---

## 7. Roles

Scales from solo to a small team. With one person, you wear all three hats —
but switch deliberately; reviewing your own spec as the reviewer catches more
than reviewing it as the author.

| Role | Owns | Passes which gates |
|---|---|---|
| **Author** | The change spec, plan, implementation | — |
| **Reviewer** | Correctness against spec and constitution | 1, 2, 5 |
| **Owner** | Priority, scope, client contact | 0, 1, 6 |

Agents are always **authors**, never reviewers of their own work. A separate
agent session with fresh context makes a reasonable second reviewer — it has
not talked itself into the approach — but never the final one.

---

## 8. Collaboration

- **Branch per change**: `change/NNN-slug`. See [conventions.md](conventions.md).
- **PR per change**, linking the change folder. The PR template carries the
  definition of done.
- **Handing a change to someone else** (or to a different agent, or to a future
  session): the change folder *is* the handoff. If it is not enough to pick up
  the work cold, it is not finished.
- **Tool-neutral by rule.** Nothing in `framework/` or `framework/skills/`
  may depend on a specific agent or IDE. Tool-specific detail goes in
  [tooling.md](tooling.md) and nowhere else.

---

## 9. Adoption — existing codebase, framework not yet applied

Do **not** back-write documentation for the whole system. That is weeks of work
producing documents nobody reads, drifting from day one.

Adopt lazily:

1. Write `docs/overview.md` — stack, services, main flows, where things
   live. One page. Enough to orient a newcomer or an agent.
2. Create `docs/capabilities/README.md` listing capability *names* only, with
   no content. The inventory, not the documentation.
3. Make `scripts/verify.sh` run whatever tests exist today, even if coverage is
   poor. A weak gate that runs beats a strong one that doesn't.
4. **The first time you touch an area, write its capability doc as part of that
   change** — describing current behaviour as you discover it — then apply the
   delta.
5. Capture existing behaviour as tests or evals wherever cheap. Executable
   descriptions don't drift.

After a few months the areas you actually work on are documented, and the
dormant ones cost you nothing.

The `project-adopt` skill walks through this.

---

## 10. Anti-patterns

| Smell | What it means | Fix |
|---|---|---|
| Capability docs nobody reads | Too long, or not consulted at gate 0 | Split them; enforce gate 0 |
| Change specs approved in seconds | Rubber-stamping | Smaller slices |
| `verify` routinely skipped | The gate is too slow or too flaky | Fix the gate, don't bypass it |
| Capability docs lagging the code | Gate 6 is being skipped | It is a PR checklist item — enforce it |
| Full track on everything | Ceremony for its own sake | Use the light track |
| Light track on everything | The framework is theatre | Owner decides the track |
| Specs full of implementation detail | Spec and plan have merged | Spec is *what*, plan is *how* |
| ADRs for everything | Decision inflation | Only hard-to-reverse choices |
