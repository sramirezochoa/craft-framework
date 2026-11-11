# User guide

**FRAMEWORK-OWNED — do not edit.**
**HUMAN-FACING — agents should not read this file.** It contains no rule or
procedure that is not already in `AGENTS.md`, `constitution.md`,
`working-guide.md` and the skills. Agents: point the person here, do not read
and summarise it.


Short, practical instructions for people. Find your situation, follow the
steps.

This is the task-oriented guide. [working-guide.md](working-guide.md) is the
reference — read it once the process starts making sense, or when you need the
reasoning. [workflows.md](workflows.md) has the same thing as diagrams.

| Your situation | Jump to |
|---|---|
| Starting a brand new project | [1](#1-start-a-new-project) |
| Adding this to an existing codebase | [2](#2-add-this-to-an-existing-codebase) |
| Joining a project that already uses it | [3](#3-join-a-project-already-using-it) |
| Building something new | [4](#4-build-something-new) |
| Changing how something already works | [5](#5-change-existing-behaviour) |
| Fixing a bug | [6](#6-fix-a-bug) |
| Building or changing an LLM feature | [7](#7-build-or-change-an-llm-feature) |
| Making a significant technical choice | [8](#8-record-a-decision) |
| Reviewing someone's change | [9](#9-review-a-change) |
| The docs feel out of date | [10](#10-the-docs-feel-out-of-date) |
| The agent is going off the rails | [11](#11-when-the-agent-goes-off-the-rails) |
| Collaborating with someone on a different agent | [12](#12-work-with-someone-on-a-different-agent) |
| Upgrading the framework | [13](#13-upgrade-the-framework) |
| The framework itself got in your way | [14](#14-report-a-framework-finding) |
| | [Gates at a glance](#gates-at-a-glance) · [Troubleshooting](#troubleshooting) · [Cheat sheet](#cheat-sheet) |

---

## What maintains itself, and what you maintain

| | Who writes it | When |
|---|---|---|
| `docs/capabilities/README.md` tables | **Generated** | `verify` fails if stale |
| `docs/changes/README.md` | **Generated** | same |
| `docs/adr/README.md` | **Generated** | same |
| `docs/capabilities/*.md` | Agent drafts, **you approve** | Gate 6 of every change |
| `docs/changes/NNN/*` | Agent drafts, **you approve** | Gates 1 and 2 |
| `docs/adr/*.md` | Agent drafts, **you approve** | Gate 2, accepted at gate 6 |
| `docs/architecture.md` | Agent drafts, **you approve** | Gate 6, when the plan ticks structural impact |
| `docs/overview.md` | **You** | Setup, then rarely |
| `docs/amendments.md` | **You** | When a project rule is needed |

Only the index tables update without review. Everything else is prose, and
prose that changes without a human reading it is how documentation becomes
fiction.

---

## 1. Start a new project

**About 20 minutes, once.**

Prerequisites: Python 3.8+, bash, and your language toolchain. On Windows use
WSL2 or Git Bash — pick one, and record it in `docs/overview.md` so
collaborators match.

1. **Get the framework and turn it into your project:**

   ```bash
   git clone <framework-repo-url> my-project
   cd my-project
   python3 framework/craft.py init
   ```

   `init` removes the framework's own files — its ADRs, its maintainer
   guide, the marker that identifies the framework repository — and installs
   the project skeleton. Run it with `--dry-run` first if you want to see
   exactly what it touches.

   *Already have a repository?* Copy the contents in alongside your code,
   then run `init` there.

2. **Edit the four files that are yours.** Nothing here is ever overwritten
   by an upgrade:

   | File | What to put in it |
   |---|---|
   | `AGENTS.md` | Two lines of project description |
   | `docs/overview.md` | Stack, how to run it, conventions you're choosing |
   | `scripts/project/verify-impl.sh` | Your lint and test commands |
   | `.github/actions/setup/action.yml` | Your CI toolchain |

   Two more are yours but can wait: `docs/amendments.md` (project-specific
   rules — fine to leave empty) and `docs/architecture.md` (leave the
   skeleton; it fills in through gate 6 as structure emerges).

   **Only `overview.md` and the verify wiring need real content on day one.**
   Capabilities and architecture accrete as you work — writing them up front
   on a greenfield project is mostly speculation, and the first three changes
   will contradict it.

3. **Confirm the gate works:**

   ```bash
   bash scripts/verify.sh
   ```

   Its preflight stage tells you if anything is missing or unwired.

4. Commit. Then go to [section 4](#4-build-something-new).

> **Not sure which repository you're in?** `python3 framework/craft.py
> context` says so, and what follows from it. If you are maintaining the
> framework itself rather than using it, read `MAINTAINING.md` instead of
> this guide.

---

## 2. Add this to an existing codebase

**About an hour, then nothing.**

**Do not document the whole system.** That is weeks of work producing documents
nobody reads.

1. Do steps 1–4 of [section 1](#1-start-a-new-project), pointing
   `verify-impl.sh` at whatever tests already exist, even if coverage is poor.
2. Ask your agent:

   > Use the project-adopt skill. Explore this repo and draft
   > `docs/overview.md` and `docs/architecture.md`.

   Here the architecture document **is** worth writing now — the structure
   already exists, you just have not written it down.

3. Review both carefully. The agent will get things wrong — that is what your
   review is for.
4. Ask it to list **capability names only** under "Not yet documented" in
   `docs/capabilities/README.md`. No documents yet. Check the list makes sense.
5. Stop. You are done adopting.

From now on, the first time a change touches an undocumented area, writing that
capability document is part of that change. After a few months the areas you
actually work on are documented and the rest costs you nothing.

---

## 3. Join a project already using it

**15 minutes before your first task.**

Read, in order:

1. `docs/overview.md` — what this project is
2. `framework/workflows.md` — the diagrams, to see the shape of the process
3. `docs/architecture.md` — how it is built
4. `framework/agent-rules.md` — the process and the rules for agents
5. `framework/constitution.md` + `docs/amendments.md` — the rules that never bend
5. The capability document for whatever you are about to touch

Then run `bash scripts/verify.sh` to confirm your machine is set up. Check
`docs/overview.md` for which Windows environment the project uses.

---

## 4. Build something new

**The full track.** Each step ends with you reviewing something.

1. **Ask for a change spec:**
   > Use the write-change skill. I want to add <description>.

   The agent reads the relevant code first and asks you questions. Answer them
   — do not let it guess.

2. **Review `docs/changes/NNN-slug/change.md`.** Check:
   - The acceptance criteria are things you could actually test
   - "What does NOT change" is right
   - No `OPEN QUESTION` left unanswered

   More than about six criteria? Ask it to split the change.

3. **Ask for the plan:**
   > The spec is approved. Use the plan-change skill.

   Review the approach, the task list, and the **structural impact** section —
   if it ticked anything there, `docs/architecture.md` gets updated at the end.

4. **Let it build:**
   > The plan is approved. Work through tasks.md with the tdd-slice skill.

   It writes failing tests first, then code, one task at a time.

5. **Review the PR.** The checklist is already in the template. Give
   `framework/review-checklist.md` a pass, particularly the "reviewing
   agent-written changes" section.

6. **Make sure it folds back:**
   > Use the update-capability skill to fold this change back.

   This step keeps the documentation honest. It is the one that gets skipped.

---

## 5. Change existing behaviour

Same as [section 4](#4-build-something-new), with one addition at the start.

Before anything else, make the agent prove it understands what exists:

> Before proposing anything: read the capability document and the code, and
> tell me how this works today.

Check its answer against what you know. **This catches more bad changes than
any other step.** If it is wrong here, everything downstream is wrong.

If the capability document turns out to disagree with the code, say so —
correcting it becomes part of this change.

---

## 6. Fix a bug

**The light track.** No change spec.

> There is a bug: <description>. Use the tdd-slice skill — write a failing
> regression test first.

Then:

1. Check the test actually reproduces the bug before the fix.
2. Review the fix.
3. `bash scripts/verify.sh`
4. If the capability document was *wrong* about how this worked, correct it.
   That is a documentation fix, not a behaviour change.

**Light or full?** If a user would notice the behaviour change, it is full
track. Bug fixes, refactors and dependency bumps are light. When unsure, ask
yourself whether you would want a written spec if someone else had done it.

---

## 7. Build or change an LLM feature

Anything where a model decides — what to say, which tool to call, what to
extract, how to classify, when to refuse. **Not only chatbots:** a single
LLM-backed endpoint inside an otherwise ordinary service counts, and only
that endpoint needs evals.

**The difference: evals replace tests for the model's part.** Deterministic
code around the model call still gets ordinary unit tests.

1. Write the change spec as normal. Acceptance criteria still apply — make
   them about observable properties, not phrasing.
2. Ask for eval cases before implementing:
   > Use the write-eval-cases skill for AC-2 and AC-3.
3. Check the assertions are **properties, not strings**: which tool was called,
   whether a required field was captured, whether output validates, whether a
   refusal happened. An assertion on exact wording will be deleted by the next
   person, which defeats the point.
4. Make sure all three kinds exist for the capability: `happy-path`,
   `edge-case`, `guardrail`.
5. Implement, then run the suite.

Three rules that catch people out:

- **A prompt change is a behaviour change.** It goes through the same flow and
  triggers an eval run. Prompts live in version control and are reviewed.
- **Every production bug becomes an eval case.** No exceptions — that is how
  the suite becomes worth having.
- **A flickering case means the assertion is too specific.** Tighten the
  property. Never loosen it to get green, and never delete it.

`bash scripts/verify.sh --fast` skips evals for a quick local loop. CI always
runs them.

---

## 8. Record a decision

Write an ADR when a choice is **hard to reverse, affects several capabilities,
or has real alternatives someone could question later**.

| Worth an ADR | Not worth one |
|---|---|
| Messaging or persistence technology | Which helper to extract |
| Auth approach | A variable name |
| Which model provider, and whether to abstract it | Temperature for one call |
| How prompts and evals are structured | Wording of one prompt |
| A breaking contract change | An additive field |
| Sync vs async integration | Retry count |

> Use the new-adr skill for <the decision>.

It drafts with `status: proposed` at gate 2; you accept it at gate 6. Accepted
ADRs are never edited — a reversal is a new ADR that supersedes the old one.

Keep the bar high. Decision inflation makes ADRs stop being read, which costs
you more than the missing records.

---

## 9. Review a change

1. Open `framework/review-checklist.md` and work top to bottom. The order is
   deliberate: intent first, then tests, then rules, then code.
2. Read the **change spec against the diff**, not the diff alone. A beautiful
   implementation of the wrong thing is what this catches.
3. Check nothing weakened an existing test or eval without that being declared
   in the spec.
4. Check the capability document was updated — and `architecture.md` too, if
   the plan ticked structural impact.

If you cannot review it properly in one sitting, it is too big. Say so and ask
for a split. Approving something you did not understand is worse than blocking
it.

---

## 10. The docs feel out of date

> Use the drift-check skill.

It runs the mechanical check first, then compares prose against code and gives
you a list.

**Where a document and the code disagree, you decide which is wrong.**
Sometimes the code is the bug. Do not let the agent silently rewrite the
documentation to match whatever the code happens to do.

Worth running before a release, before working in an unfamiliar area, and
roughly monthly.

---

## 11. When the agent goes off the rails

The common failures and what to do. All of these are better caught early than
in review.

| What happened | Say this |
|---|---|
| It skipped straight to code | *Stop. Revert that. We are at gate 1 — use the write-change skill first.* |
| It implemented something nobody asked for | *Which acceptance criterion does this serve? If none, remove it.* |
| The diff is enormous | *This is too big to review. Split the change and do the first slice only.* |
| It changed or disabled an existing test | *Constitution rule 6. Revert that test. If the behaviour genuinely must change, it goes in the spec and gets approved first.* |
| It is confidently wrong about existing code | *Quote me the lines you are relying on.* Then back to gate 0. |
| It is guessing at a requirement | *Do not guess. Mark it OPEN QUESTION and ask me.* |
| It edited something under `framework/` | *That is framework-owned. Project rules go in docs/amendments.md.* |
| `verify` fails and it wants to skip a check | *Never. Fix the cause, or stop and tell me the check is wrong.* |

**If the session runs out of context mid-change**, the change folder is the
handoff. Start a fresh session and say:

> Read AGENTS.md, then `docs/changes/NNN-slug/`. Continue from the first
> unchecked task in tasks.md.

If that is not enough for a cold session to continue, the change folder is
incomplete — which is useful information about the work, not just the session.

---

## 12. Work with someone on a different agent

The framework is tool-neutral on purpose. Claude Code, Codex, Cursor and a
plain text editor all follow the same process.

**What your collaborator does once:**

```bash
git clone <repo> && cd <repo>
python3 framework/craft.py sync
bash scripts/verify.sh
```

`AGENTS.md` is the canonical instruction file and Codex reads it natively.
`CLAUDE.md` is only a pointer at it. Skills are plain markdown — if their tool
does not support skills, they open the `SKILL.md` and follow it.

**Handing over a change in progress:** the change folder is the handoff.
Nothing else needs explaining.

**Two things to agree up front:**

- **Framework version.** Check `framework/VERSION` matches. Different versions
  mean different gates.
- **No tool-specific guardrails.** Hooks, subagents and slash commands are
  conveniences. Anything that actually matters lives in `verify` and CI, which
  everyone runs. If you find yourself relying on a Claude-only hook, move the
  rule into `verify`.

Worth doing occasionally: run the same change through both tools from a clean
start and compare the artifacts. Where they diverge, the instructions were too
vague or too tool-specific.

---

## 13. Upgrade the framework

```bash
python3 framework/craft.py upgrade ~/src/craft-framework --dry-run
python3 framework/craft.py upgrade ~/src/craft-framework
bash scripts/verify.sh
```

Then check `git diff` — only `framework/` and generated files should appear.
Anything of yours in that diff is a bug in the framework, not in your project.

Read `framework/CHANGELOG.md` for migration notes. You upgrade when you choose;
a client project can sit on an old version indefinitely.

---

## 14. Report a framework finding

When the framework is wrong, slow, unclear, or silent on something you do
often — record it **immediately**, while the detail is fresh:

```bash
python3 framework/craft.py feedback "drift warns on every Java test because \
they have no AC-n comment" --kind check
```

It appends a dated, version-stamped entry to `docs/framework-feedback.md`.
Do not stop to open an issue — that friction is exactly why feedback never
gets written down.

`python3 framework/craft.py feedback` with no argument lists what you have
collected.

**At the retro**, work through the log and mark each entry:

| Verdict | Action |
|---|---|
| Specific to this project | Fix it in `docs/amendments.md` or `AGENTS.md` |
| True for every project | Open a finding on the framework repository |
| Not a problem after all | Say why, so nobody re-litigates it |

**Record deviations too** — every time you skipped a step or worked around
the process. Those entries are the most useful and the least likely to be
written down. They are data, not confessions.

---

## Gates at a glance

<!-- BEGIN GENERATED: gates-full — from definition-of-done.md, do not edit by hand -->

| Gate | Means | Passes when | Passed by |
|---|---|---|---|
| **0** Understand | Understanding confirmed | The owner agrees the restatement of current behaviour is correct | Owner |
| **1** Change spec | Change spec approved | Criteria are testable, scope is clear, no OPEN QUESTION remains | Reviewer |
| **2** Plan | Plan approved | The approach is sound, structural impact is decided, every AC-n is traceable to a task | Reviewer |
| **3** Tests | Tests red for the right reason | Tests fail because the behaviour is missing, not from a typo or compile error | Author |
| **4** Implement | Implementation complete | All tasks done, verify green, nothing in the diff the spec did not ask for | Author |
| **5** Review | Review passed | Review checklist applied, CI green on all three operating systems | Reviewer |
| **6** Fold back | Change folded back (Definition of Done) | Capability and architecture docs describe reality again, ADRs accepted, indexes rebuilt | Owner |

*Generated from [definition-of-done.md](definition-of-done.md), the single source of truth for the gate model.*

<!-- END GENERATED -->

Agents are always the **author**, never the reviewer of their own work. Gate 6
is the one that gets skipped; skipping it turns the capability documents into
fiction.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `verify` fails on shellcheck | Portability problem in a script | Fix the script. Do not disable the check |
| `verify` says "no test command configured" | `verify-impl.sh` not wired up | Edit `scripts/project/verify-impl.sh` |
| "modified locally: framework/..." | Project content put in a framework file | Move it: rules → `docs/amendments.md`, build commands → `verify-impl.sh`, CI → `.github/actions/setup/` |
| "AC-n is not covered by any task" | A criterion with no work behind it | Add the task, or remove the criterion |
| "no change-log entry for merged change" | Gate 6 was skipped | Run the `update-capability` skill |
| "stale: docs/changes/README.md" | A file was added or its frontmatter changed | `python3 framework/craft.py index` |
| An index table keeps reverting | You edited inside the generated block | Edit the frontmatter in the source file instead |
| "adapters out of date" | Skills changed, adapters not regenerated | `python3 framework/craft.py sync` |
| Script fails with `\r` errors on Windows | CRLF line endings | Check `.gitattributes` is committed; re-clone |
| Agent ignores the process | It did not read `AGENTS.md` | Point it there explicitly, and name the skill you want |
| Eval case passes sometimes | Assertion is too specific | Assert a property, not an exact string. Do not delete the case |
| Everything feels like too much ceremony | Full track on small work | Use the light track. See [section 6](#6-fix-a-bug) |

---

## Cheat sheet

```bash
bash scripts/verify.sh                       # the gate — must pass
bash scripts/verify.sh --fast                # skip evals for a quick loop
python3 framework/craft.py                   # list every command
python3 framework/craft.py preflight         # are my tools installed?
python3 framework/craft.py context           # framework repo, or a project?
python3 framework/craft.py feedback "..."     # record a framework finding
python3 framework/craft.py index             # rebuild the index tables
python3 framework/craft.py sync              # after changing skills
python3 framework/craft.py drift             # docs vs work, mechanically
python3 framework/craft.py upgrade <path>    # pull a new framework version
```

| I want to | Skill to ask for |
|---|---|
| Define new or changed behaviour | `write-change` |
| Turn an approved spec into a plan | `plan-change` |
| Write the code | `tdd-slice` |
| Test an LLM feature | `write-eval-cases` |
| Fold a finished change back | `update-capability` |
| Check the docs are honest | `drift-check` |
| Record a decision | `new-adr` |
| Set this up on existing code | `project-adopt` |

**Five rules worth remembering:**

1. Never let an agent change code it has not read.
2. Never weaken a test or an eval to make something pass.
3. A change is not done until the capability document is true again.
4. If you cannot review it in one sitting, it is too big.
5. Never edit anything under `framework/` — your edits disappear on upgrade.
