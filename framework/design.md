# Design

**FRAMEWORK-OWNED — do not edit.**
**HUMAN-FACING — agents should not read this file.** It is rationale, not
procedure. Nothing here changes what an agent should do.


Why this framework is shaped the way it is. [working-guide.md](working-guide.md)
says *how to work*; this says *why the machinery exists*, what was rejected, and
where it is weak. Read it once, or when you are tempted to change something
here.

For your project's own architecture, see `docs/architecture.md` — a different
document with a different audience.

---

## 1. The problem

AI coding agents shifted where software goes wrong.

Writing code stopped being the bottleneck. Three failure modes took its place:

| Failure | What it looks like |
|---|---|
| **Drift of intent** | The agent builds something plausible that is not what was wanted. Requirements lived in a chat window and evaporated with the context. |
| **Silent regression** | A change works, and quietly breaks something nobody tested. With LLM features, a prompt tweak for one case degrades three others. |
| **Documentation as fiction** | Docs describe a system that stopped existing months ago. Worse than none, because people and agents trust them. |

A fourth is specific to agents: **they start cold every session**. Everything a
returning human would remember — why this approach, what was already rejected,
what the code actually does — has to be written down or it does not exist.

## 2. Goals

1. **Intent survives the session.** Written, reviewed, in the repository.
2. **Current behaviour is always knowable** without reading the whole codebase.
3. **Verification is executable**, not aspirational.
4. **Humans decide; agents propose.** Judgement stays with people at defined points.
5. **Portable across tools.** No lock-in to one agent or IDE.
6. **Cheap on small work.** Ceremony proportional to risk.
7. **Upgradable.** The framework improves without breaking live client projects.

### Non-goals

- **Specs that generate code.** Attractive, not reliable. Specs steer; tests verify.
- **Replacing human review.** Every gate ends with a person.
- **Covering everything.** Deliberately silent on team structure, estimation, contracts, pricing.
- **One-size granularity.** An API, a UI and a bot differ; the framework names the shape and lets the project choose the size.

## 3. Three layers

Each prevents a failure the others cannot.

```
SDD      ──  intent      ──  prevents building the thing wrong
TDD/eval ──  behaviour   ──  prevents regressions
Agile    ──  direction   ──  prevents building the wrong thing
```

The combination matters more than any part. SDD alone drifts toward waterfall:
a big approved spec, built correctly, wrong by the time it ships. TDD alone
verifies behaviour nobody agreed to. Agile alone gives feedback with nothing
durable to feed back into.

**Agile is deliberately thin here** — vertical slices, a feedback cadence,
definitions of ready and done, a retro. Story points, standups and user stories
as a separate artifact are omitted: the change spec *is* the story, and
estimation behaves oddly when implementation is fast and review is the
bottleneck.

## 4. Four nouns

The core modelling decision. Most SDD frameworks have one artifact — the spec —
and run into trouble because a spec answers only one question well.

| Artifact | Question | Lifecycle | Why separate |
|---|---|---|---|
| **Capability** | What does it do **now**? | Living | Must be readable without replaying history |
| **Change** | What changed, and why? | Archived | Must be reviewable as a unit, before the work |
| **ADR** | Why this approach? | Append-only | Outlives the feature; constrains future work |
| **Test / eval** | Does it actually? | Runs continuously | The only artifact that cannot lie |

### Why capability *and* change

Append-only specs give perfect history and no answer to "what does this do
today" — you reconstruct it by replaying five documents in order. Living specs
give current truth and lose the reasoning.

Holding both costs one step: **gate 6**, folding the change into the capability
at merge. That step is the whole design. Everything else is support for making
sure it happens.

This generalises OpenSpec's delta model. Their insight — brownfield needs
deltas against existing behaviour, not greenfield specs — is right, and
capabilities make the thing the delta applies *to* explicit. Greenfield then
becomes the special case where the delta creates the capability.

### Why "capability" and not "feature" or "module"

A capability is behaviour a stakeholder recognises by name. "Feature" implies
something newly added; much of what a system does was never a feature. "Module"
is implementation, and implementation gets refactored while behaviour persists.
Capabilities survive restructuring, which is what a living document must do.

## 5. Gates

Review points with explicit exit criteria, each ending with a human.

Three reasons:

1. **Cost of correction rises steeply.** A wrong assumption costs minutes in a
   spec, hours in a plan, days in code.
2. **Agents do not know when they are wrong.** Confident, fluent, incorrect
   output is the characteristic failure. A gate is where that gets caught.
3. **Review capacity is now the bottleneck.** Agents produce large diffs fast.
   Gates ration what reaches review and make each unit small enough to review
   honestly.

**Gate 0** — restating current behaviour before proposing a change — is the one
that is easiest to dismiss and catches the most. The characteristic brownfield
failure is an agent confidently changing code it never read.

**Gate 6** is marked as the dangerous one throughout, because skipping it has no
immediate cost and converts the capability docs into fiction over months.

## 6. Enforcement: executable, not conventional

Spec Kit, the closest relative, has no enforcement — it is convention, and its
own benchmark shows measurable drift regardless. Conventions decay under
deadline pressure.

So the gates that can be mechanised are:

| Rule | Enforced by |
|---|---|
| Tests pass, lint clean, evals green | `scripts/verify.sh` |
| Every AC traced to a task and a test | `drift_check.py` |
| Capability updated after a merged change | `drift_check.py` |
| Gate checklists | PR template |
| Portability | CI across three OSes |
| Framework not locally edited | `check-integrity.sh` |

What stays human: whether the spec is *right*, whether the plan is sound,
whether prose matches behaviour. A script can prove traceability; it cannot
judge truth.

**Hooks are deliberately not load-bearing.** A Claude hook that a Codex user
does not have is a guardrail that silently disappears. Anything that matters is
in `verify` and CI, which everyone runs.

## 7. Tool neutrality

`AGENTS.md` is canonical; `CLAUDE.md` is a pointer; tool-specific files are
generated. Skills are plain markdown that a human can follow when no agent
supports them.

The rule that keeps it honest: **nothing outside `framework/tooling.md` may name
a specific tool.** Without that single exception point, tool-specific
assumptions leak everywhere and portability becomes a claim rather than a
property.

Tested by conformance, not asserted: run the same change through two different
agents and compare the artifacts.

## 8. Ownership

`framework/` is framework-owned; everything else is the project's. Where the
framework needs project-specific content it reads a file the project owns.

This exists because v0.1.0 did the opposite and upgrading became a three-way
merge nobody could review. Structure prevents the accident; the checksum
manifest detects it when it happens anyway. Rationale in ADR 0002.

## 9. What was rejected

| Rejected | Why |
|---|---|
| **Multi-agent role-play** (BMAD-style) | Heavy — critics estimate months to master versus days for simpler frameworks, with high token cost. Agent-simulated roles do not substitute for human judgement. |
| **Spec-as-source code generation** (Tessl-style) | Non-deterministic generation from a spec is not reproducible enough to be a source of truth. |
| **IDE-locked tooling** (Kiro-style) | Fails the portability goal outright. |
| **Story points and velocity** | Noisy when implementation is fast and review is the constraint. |
| **User stories alongside specs** | Two descriptions of one thing; they diverge. |
| **Documenting everything up front on adoption** | Weeks of work producing documents nobody reads, drifting immediately. |
| **Mandatory ADRs** | Decision inflation makes ADRs stop being read. |

EARS phrasing is borrowed from Kiro without the IDE; ADRs from Nygard unchanged;
the constitution and the change-folder layout from Spec Kit.

## 10. Known weaknesses

Stated plainly, because a design document that lists no costs is marketing.

1. **Gate 6 depends on discipline.** The drift check catches a missing
   change-log row, not a lazy one-line update that says nothing true.
2. **Drift checking is structural only.** Nothing mechanically verifies that
   prose matches behaviour. The `drift-check` skill makes it a human task.
3. **Capability granularity is judgement.** Too fine and you drown; too coarse
   and documents become dumping grounds. The framework gives heuristics, not
   an answer.
4. **Evals are non-deterministic.** A flickering case erodes trust in the
   suite, and the tempting fix — loosening the assertion — is the wrong one.
5. **Ceremony has a real cost.** Benchmarks on comparable frameworks show
   modest merge-rate gains at meaningfully higher time and token cost. The
   light track exists because of this, and choosing tracks badly wastes the
   benefit.
6. **The framework itself can rot.** Its only correction mechanism is the
   retro's second question. If nobody asks it, this becomes another set of
   documents describing how people wish they worked.
7. **Agent tooling moves faster than this document.** `tooling.md` will be
   wrong before the rest of the framework is.

## 11. Open questions

- Should capability documents carry a confidence or freshness signal beyond
  `last-verified`?
- Can drift between prose and behaviour be partly mechanised — for instance by
  checking that the interfaces a capability lists still exist?
- Is there a reliable way to measure whether the framework is paying for
  itself on a given project?
- Should the framework ship as a dependency rather than copied files, once
  tooling makes that practical?
