# Framework changelog

All notable changes to the framework itself. Projects pin a version in
`framework/VERSION`.

## [0.13.0] — capability lifecycle and guided new-project setup

New projects had nothing to write: a capability describes what the system does
*today*, and on day one it does nothing. The framework served existing
codebases and told new ones to skip capabilities and architecture.

### Added
- **Capability lifecycle.** `planned` joins `active`, `deprecated` and
  `superseded-by: <name>`, and all four are now defined — each describes what
  is true today. A `planned` capability holds purpose, scope, expected
  interfaces and planned changes, **never behaviour**: intended behaviour lives
  in change specs (ADR 0003). The capability template gains **Planned changes**
  and **Deprecation** sections.
- **`project-start` skill.** An interview — fed by a brief, PRD or pasted notes
  if the developer has them — that drafts `AGENTS.md`, `docs/overview.md`,
  `docs/architecture.md`, `docs/amendments.md`, `planned` capability documents,
  `scripts/project/verify-impl.sh` and `.github/actions/setup/action.yml` from
  the stack and tools chosen, ADR 0001 and a draft change 001 for the project
  skeleton. `skills/project-start/stacks.md` maps stacks to lint, test and CI
  setup commands. Until the skeleton exists, verify reports *not scaffolded
  yet* instead of failing.
- **Drift enforces the lifecycle:** error when a merged change leaves its
  capability `planned` (gate 6 skipped); warning on an unknown status.
- `craft.py init` ends by pointing at `project-start` / `project-adopt`.
- The framework repository runs its own tests (`framework/tests/`) in verify.

### Fixed
- Frontmatter values kept trailing YAML comments, so a change created from the
  template had `status: draft   # draft | approved | …` and drift treated it as
  something other than a draft. ` #` now starts a comment, as in YAML; quoted
  values are untouched.
- `project-adopt` pointed amendments at `framework/constitution.md` and verify
  wiring at `scripts/verify.sh`; now `docs/amendments.md` and
  `scripts/project/verify-impl.sh`.

### Migration
- None required. Existing `active`, `deprecated` and `superseded-by` documents
  are unchanged. Run `bash scripts/verify.sh` after upgrading: a capability
  with a status outside the four is now reported.

## [0.12.0] — init unlinks the framework remote

A project started with `git clone <framework> my-project` kept `origin`
pointing at the framework repository, so its first `git push` — by anyone with
write access to the framework — landed there.

### Changed
- **`craft.py init` removes `origin` when it is a framework repository** (one
  of its branches carries `.craft-framework-repo`). A project's own remote —
  the framework copied into an existing repository — is left alone. The step
  appears in `init --dry-run`, and `init` prints the commands to connect the
  project's own repository.
- `README.md` and `user-guide.md` §1 describe the step, how to start with a
  clean history, and that upgrades need no git link to the framework.

### Fixed
- **Every new project failed `verify` right after `init`.** `craft.py manifest`
  listed files git ignores — a maintainer's `.DS_Store` — so a fresh clone
  reported them missing. The manifest now skips git-ignored files and OS junk
  (`.DS_Store`, `Thumbs.db`, `desktop.ini`, `__pycache__`).

### Migration
- None for existing projects: `init` runs once, at project creation. A project
  created earlier should check `git remote -v` and repoint `origin` if it
  still names the framework.

## [0.11.3] — verify finds Git Bash on Windows

### Fixed
- On Windows, `craft.py` launched project hooks (lint, tests) and `release`'s
  verify run with a bare `bash`, which resolves to `System32\bash.exe` — the
  WSL launcher. With no Linux distribution installed (GitHub's Windows
  runners, most developer machines) every hook failed with "Windows Subsystem
  for Linux has no installed distributions". `craft.py` now skips the WSL
  launcher and uses Git Bash, from `PATH` or next to `git`, and reports
  clearly when no usable bash exists. No project action needed.

## [0.11.2] — tooling.md matches the tooling

### Fixed
- `framework/tooling.md` named `sync-adapters.sh`, which was folded into
  `craft.py sync` long ago. It now names the real command, says generated
  adapters are committed and checked by verify, and stops claiming that MCP
  and Codex configs are generated — they are not yet.
- §3 pointed at a `run_tests` function in `verify.sh`; project commands go in
  `project_lint` / `project_test` in `scripts/project/verify-impl.sh`.
- No project action needed.

## [0.11.1] — verify runs on Windows

### Fixed
- `craft.py` crashed with `UnicodeEncodeError: 'charmap' codec can't encode
  character '\u2713'` on Windows whenever its output was piped (CI, git
  hooks), because Python fell back to the ANSI code page. stdout and stderr
  are now forced to UTF-8, and `PYTHONIOENCODING=utf-8` is passed to child
  Python processes. No project action needed.

## [0.11.0] — evals are not bot-specific

The eval layer was described correctly in most places but shipped with a
chat-shaped runner, so a classifier or extraction endpoint had to pretend to
be a conversation.

### Added
- **Single-shot eval cases.** A case now uses either `turns:` for a dialogue
  or `input:` for one payload in, one response out — a string or a structured
  object. The runner passes whichever it finds straight through, so a
  classifier never has to be wrapped in a fake conversation. A case with
  neither is reported as malformed rather than silently running empty.

### Changed
- `call_system(turns, setup)` is now `call_system(request, setup)`, where
  `request` is `{"turns": [...]}` or `{"input": ...}`. This affects new
  projects only: `evals/run.py` is project-owned, so an upgrade never
  overwrites an implementation you have already written.
- Wording corrected where the docs implied evals were for chatbots. They
  cover anything a model decides — classification, extraction, RAG answers,
  routing, tool calls — and the choice is per *feature*, not per project. One
  service commonly needs ordinary tests for its plumbing and evals for its
  single LLM-backed endpoint.
- `framework/templates/eval-case.yaml` documents both shapes and says which
  assertions are mechanical and which need the `judge()` hook.
- `write-eval-cases` skill, `working-guide.md` §5 and `user-guide.md` §7 all
  state the per-feature rule explicitly.

## [0.10.0] — evals that actually run, and a feedback loop

### Added
- **`evals/run.py`** (project-owned, shipped as a template). Previously
  `verify-impl.sh` pointed at a file that did not exist, so the eval stage
  skipped silently — the exact failure the preflight was built to stop.
  It implements the mechanical assertions (`tool_calls`, `output_schema`,
  `max_turns`, `max_tool_calls`, regex `must_not`) and leaves two functions
  marked TODO: `call_system`, which is required and fails loudly until
  written, and `judge`, without which semantic assertions are reported as
  UNJUDGED rather than quietly passing.
- **`craft.py feedback "..." [--kind]`** — records a dated, version-stamped
  finding in `docs/framework-feedback.md`. Capture in the moment; stopping to
  open an issue is why feedback never gets written down. With no argument it
  lists what you have collected.
- **`docs/framework-feedback.md`** (project template) — what is worth
  recording, and how to triage it at the retro into project-specific,
  upstream, or wontfix. Deviations — the times you worked around the process —
  are called out as the most valuable entries.
- **`.github/ISSUE_TEMPLATE/framework-finding.md`** in the framework repo,
  which asks the three questions from `MAINTAINING.md`: is it true for every
  project, could it be executable instead, does a fix duplicate something.
  `init` removes it from projects.
- A **triage section in `MAINTAINING.md`** with the five outcomes a finding
  can have — including "add to known weaknesses", so a closed finding leaves
  a trace rather than returning from the next project.
- **Section 14 of the user guide** and a retro step in the working guide.

### Changed
- `craft.py init` installs `evals/` at the top level rather than under
  `docs/`, via an explicit destination map.

## [0.9.0] — framework repo vs project, and a real way to start

Until now the framework repository and a project using it were
indistinguishable, so `AGENTS.md` told an agent working on the framework not
to edit `framework/` — the only thing it would edit. And "copy this repo's
contents" left you to work out which files were the framework's own.

### Added
- **`.craft-framework-repo`** — a root marker. It sits outside `framework/`
  deliberately: `upgrade` copies only `framework/`, so it can never be carried
  into a project.
- **`craft.py init`** — turns a clone of the framework into a project. Removes
  the marker and `MAINTAINING.md`, clears the framework's own ADRs and
  changes, installs the project templates, writes the adapters, and prints
  the four files you edit. `--dry-run` lists everything first.
- **`craft.py release`** — runs `gates` → `index` → `sync` → `manifest` →
  `verify` in that order, and refuses if `VERSION` has no matching changelog
  entry at the top. Order matters: `manifest` checksums the others' output,
  and forgetting it gives every downstream project a false integrity warning.
- **`craft.py context`** — says which repository you are in and what follows
  from that.
- **Maintainer commands now refuse to run in a project.** `init`, `gates`,
  `manifest` and `release` each explain what damage they would do and where
  the content belongs instead. `manifest` in a project would have recorded
  local edits as official and disabled the integrity check permanently.
- **`MAINTAINING.md`** — the release procedure, what is generated from what,
  three levels of testing a framework change, versioning rules, and the three
  questions to ask before adding anything.
- **`framework/templates/project/`** — the project skeleton, so the framework
  repo's own `docs/` no longer doubles as the template.

### Changed
- **`AGENTS.md` is split.** `framework/agent-rules.md` (framework-owned)
  carries the process, the rules, where things live and the skills table;
  `AGENTS.md` keeps the project description and points at it. Previously
  `AGENTS.md` was never touched by an upgrade, so **every rule added since
  v0.1.0 would never have reached an existing project.** Now they do.
- The root `AGENTS.md` in this repository is the maintainer's version and
  states that the ownership rule is reversed here.
- `verify` adapts: in the framework repo it checks the gate summaries are in
  sync, skips the placeholder-wiring warning, and reports a stale manifest
  instead of warning that every file has been modified.
- Getting started is now `git clone` → `craft.py init` → edit four files,
  instead of "copy the contents and work out what to delete".

### Migration from 0.8.0
Projects: after upgrading, replace your `AGENTS.md` with
`framework/templates/project/AGENTS.md`, move your project description into
it, and keep any project-specific instructions in the section at the bottom.
The rules it used to contain now live in `framework/agent-rules.md` and will
upgrade on their own from here.

## [0.8.0] — one CLI, and a preflight that fails loudly

Nine scripts in two languages became one Python CLI plus a bash shim. The
split was principled — bash for launching processes, Python for parsing — but
nine files was more surface than the work justified, with the frontmatter
parser duplicated three times.

### Added
- `framework/craft.py` — the whole toolchain, standard library only:
  `verify`, `preflight`, `drift`, `index`, `sync`, `gates`, `manifest`,
  `integrity`, `upgrade`. Run it with no arguments for the list.
- **A preflight stage, run first by `verify`.** Previously a machine without
  Python passed verify green while silently skipping four of six stages — a
  gate that passes without running is worse than one that fails. Preflight
  hard-fails on a missing Python or `verify-impl.sh`, and warns about absent
  Git, absent shellcheck, and placeholder test wiring.
- The final line now reports warnings: `✓ verify passed (1 warning(s))`.
- A **Requirements** block in `README.md`, which had none.

### Changed
- `scripts/verify.sh` is now a real shim with one job beyond delegation: it
  detects a missing Python and says so. A Python script cannot report its own
  absence.
- The project's bash hooks still run as bash — `craft.py` provides the
  documented `run`/`ok`/`bad`/`skip`/`have`/`$PY` API and dispatches one
  function — so `verify-impl.sh` stays the natural shell file it should be.
- `framework/tooling.md` prerequisites rewritten: required vs optional, what
  needs each, and the explicit "no Node, no Make, no Docker, nothing to pip
  install".

### Fixed
- The documented Python floor was **3.9**; the scripts compile against 3.8,
  since every annotation sits under `from __future__ import annotations`. A
  number asserted without checking. Corrected everywhere.
- The CI workflow shellchecked `framework/scripts/*.sh`, which no longer
  exists and would have failed the job.

### Removed
- `framework/scripts/` — `verify.sh`, `drift_check.py`, `update_indexes.py`,
  `gen_gate_summary.py`, `sync-adapters.sh`, `check-integrity.sh`,
  `update-manifest.sh`, `upgrade.sh`.

### Migration from 0.7.0
Replace `framework/` and `scripts/verify.sh` as usual. Any local command that
called a script by path becomes a subcommand:
`python3 framework/craft.py drift|index|sync|gates|manifest|upgrade`.
Your `scripts/project/verify-impl.sh` is unchanged.

## [0.7.0] — one source for the gate model

The 0.6.1 bug was possible because four documents each stated the gate model.
Fixing the wording did not remove the cause. This does.

### Added
- `framework/gen_gate_summary.py` — generates the gate summaries in
  `working-guide.md`, `user-guide.md` and `workflows.md` from
  `definition-of-done.md`, which is now the only place the gate model exists.
  A maintainer tool, run at framework release; projects never run it, because
  the files it writes are checksummed and a hand-edit surfaces as an integrity
  warning instead of drifting.
- Each gate in `definition-of-done.md` carries a machine-readable metadata
  line: `<!-- gate passes="..." by="..." step="..." -->`.
- The generator **refuses to emit** on non-contiguous gate numbering or a
  missing metadata line — so the 0.6.1 defect cannot recur.

### Changed
- `working-guide.md` §3 keeps only what it alone knows: what each step
  produces. The step/gate/owner table is generated.
- `user-guide.md` gates-at-a-glance is generated.
- `workflows.md` states gate **names** only, generated, and no exit criteria.
- `AGENTS.md` gained a **"Files you should not read"** table covering the
  human-facing documents, and says the gate criteria live in one file.
- `user-guide.md`, `workflows.md` and `design.md` carry a HUMAN-FACING header.

### Why the diagrams stay
Diagrams and ordered steps are not duplication for one audience — they are two
forms for two audiences. A flowchart's meaning sits in an edge list a model
must traverse; ordered steps and tables are more direct for an agent, and a
picture is more direct for a person. The fix was to stop both forms carrying
the same *facts*, not to delete one.

## [0.6.1] — gate numbering corrected

### Fixed
- The lifecycle diagram in `framework/working-guide.md` §3 was off by one from
  gate 4 onward. It showed implementation as having no gate, labelled review
  as gate 4, and fold-back as gate 5 — while `definition-of-done.md`,
  `workflows.md`, the PR template and the user guide all use gate 4 =
  implementation complete, 5 = review passed, 6 = folded back. The guide
  predated the seven-gate model and was never revisited.
- The summary table's Gate column held exit criteria rather than gate numbers,
  and merged two distinct gates into one "verify" step. It now has separate
  Gate, "passes when" and "passed by" columns, matching the user guide's
  gates-at-a-glance table.
- Clarified that `verify` is not a lifecycle step: it runs continuously inside
  step 4 and again at gates 4, 5 and 6.

### Audited
Every gate reference in the repository — 70+ across documents, templates,
skills and scripts. The working-guide diagram was the only incorrect one.

No mechanical check covers prose-to-prose consistency, so this class of defect
is found by reading. It is listed in `design.md` under known weaknesses.

## [0.6.0] — user guide completed

### Fixed
- The setup table in section 1 said `docs/architecture.md` should be "filled
  in as it takes shape", which predated 0.5.0 and contradicted the
  what-maintains-itself table in the same document. It now says to leave the
  skeleton and let gate 6 fill it, with the opposite advice for adoption,
  where the structure already exists.

### Added
Four sections covering situations the guide had no answer for:
- **Build or change an LLM feature** — evals instead of tests for the model's
  part, assert properties not strings, prompt changes are behaviour changes,
  every production bug becomes a case, what a flickering case means
- **Record a decision** — when an ADR is worth writing, with a worth-it /
  not-worth-it table, and why the bar stays high
- **When the agent goes off the rails** — eight common failures with the
  sentence to say for each, plus how to resume a change in a fresh session
  when context runs out
- **Work with someone on a different agent** — what a Codex collaborator does
  once, the change folder as the handoff, and the two things to agree up front

Also added:
- **Gates at a glance** — all seven gates, what passes each, and who passes it
- Prerequisites and the Windows environment choice in section 1
- A light-vs-full test in section 6, for people unsure which track they are on
- Two more troubleshooting rows, and two more rules in the cheat sheet

## [0.5.0] — generated indexes, architecture in the lifecycle

Closes the gap where `docs/architecture.md` was the only document with no
process behind it, and stops three hand-maintained tables from rotting.

### Added
- `framework/craft.py index` — regenerates the capability, change
  and ADR index tables from frontmatter. Pure derivation, so no review is
  needed. Writes only between `BEGIN/END GENERATED` markers, so hand-written
  prose in those files is untouched, and appends the block if the markers are
  missing rather than failing.
- A **Generated indexes** stage in `verify`: a stale index fails the build,
  the same way stale adapters do.
- `docs/adr/README.md` — an ADR index, which did not exist before.
- A **structural impact** checklist in `framework/templates/plan.md`. Each tick
  becomes a task and a gate-6 item.

### Changed
- `docs/architecture.md` is now maintained by the lifecycle rather than only at
  adoption: planned at gate 2, updated at gate 6, checked by `drift-check`
- `update-capability` skill folds architecture changes and rebuilds indexes
- `plan-change` skill must fill the structural impact section deliberately
- `write-change` skill regenerates the index instead of editing the table
- Gate 2 and gate 6 in `definition-of-done.md`, plus the PR template
- `framework/user-guide.md` opens with a table of what is generated, what is
  agent-drafted and human-approved, and what is purely yours

### Note
The index tables are the only thing that updates without review. Everything
else is prose, and prose that changes unreviewed is how documentation becomes
fiction.

## [0.4.0] — user guide

### Added
- `framework/user-guide.md` — short, task-oriented instructions for people,
  organised by situation rather than by concept: start a new project, adopt an
  existing codebase, join a project, build something new, change existing
  behaviour, fix a bug, review a change, check for drift, upgrade. Plus a
  troubleshooting table and a one-screen cheat sheet.

### Changed
- `framework/working-guide.md` is now explicitly the *reference*, and points at
  the user guide for step-by-step instructions. The two were conflated: the
  working guide is organised by concept, which is wrong for onboarding.
- `framework/README.md` leads with the user guide
- Root `README.md` and `AGENTS.md` point at it

## [0.3.0] — diagrams and rationale

### Added
- `framework/workflows.md` — every workflow as a Mermaid diagram: the full
  track with gates, the track decision tree, how the four artifacts relate,
  who passes which gate, the brownfield fold-back loop, adoption, and the
  ownership/upgrade model. Mermaid because it is plain text, diffable,
  rendered by GitHub, and editable by any agent.
- `framework/design.md` — why the framework is shaped this way: the problem,
  goals and non-goals, why four artifacts rather than one, why gates, why
  enforcement is executable, what was rejected and why, and a plainly stated
  list of known weaknesses and open questions. Rationale, not process — the
  working guide remains the process.
- `docs/architecture.md` (project-owned) — a template for the project's own
  structure: context, components, internal boundaries, integration points with
  their failure behaviour, cross-cutting concerns, model/prompt architecture,
  environments, scale limits and known debt.

### Changed
- `project-adopt` phase 1 now produces the architecture document alongside the
  overview, with an explicit warning not to describe behaviour in it
- `drift-check` covers `docs/architecture.md`, structurally only
- `docs/overview.md` opens with a pointer table to the other documents
- Indexes updated: `framework/README.md`, `AGENTS.md`, root `README.md`

### Note
All seven diagrams were rendered during the build to confirm they parse.

## [0.2.0] — structural ownership

The 0.1.0 layout mixed project content into framework-owned files, so an
upgrade was a three-way merge rather than a replacement. This release makes
ownership structural: `framework/` is entirely framework-owned, everything else
is entirely yours.

### Added
- `framework/` as the single framework-owned tree — process docs, templates,
  skills and scripts in one place
- `docs/amendments.md` — project-specific constitution rules (project-owned)
- `scripts/project/verify-impl.sh` — project build/test/eval commands
  (project-owned), sourced by the framework's verify
- `scripts/verify.sh` — thin, stable shim so the command never changes
- `.github/actions/setup/action.yml` — project CI toolchain (project-owned)
- `framework/MANIFEST.sha256` and `framework/craft.py integrity` —
  `verify` now warns when a framework-owned file has been edited locally, and
  says where the content should have gone
- `framework/upgrade.sh` — one-command upgrade, with `--dry-run`
- `framework/update-manifest.sh` — maintainer tool, run at release
- PR template and CI workflow are now generated from `framework/templates/`
  by `sync-adapters.sh`, so an upgrade carries them

### Changed
- `docs/framework/**` → `framework/**`
- `.agents/skills/**` → `framework/skills/**`
- `scripts/{verify,drift_check,sync-adapters}` → `framework/**`
- `FRAMEWORK_VERSION` → `framework/VERSION`
- `CHANGELOG.md` → `framework/CHANGELOG.md`
- `docs/project/overview.md` → `docs/overview.md`
- `docs/capabilities/`, `docs/changes/`, `docs/adr/` keep their paths — they are
  the most-navigated directories and stay shallow
- `verify` gained a framework-integrity stage and reports the framework version

### Migration from 0.1.0

```bash
git mv docs/framework framework
git mv .agents/skills framework/skills && rmdir .agents
mkdir -p framework/scripts scripts/project
git mv scripts/verify.sh scripts/sync-adapters.sh scripts/drift_check.py framework/
git mv FRAMEWORK_VERSION framework/VERSION
git mv CHANGELOG.md framework/CHANGELOG.md
git mv docs/project/overview.md docs/overview.md && rmdir docs/project
```

Then copy `scripts/verify.sh`, `scripts/project/verify-impl.sh`,
`docs/amendments.md` and `.github/actions/setup/action.yml` from this release,
move your constitution amendments into `docs/amendments.md`, move your
`run_lint`/`run_tests` bodies into `verify-impl.sh`, and run
`python3 framework/craft.py sync`.

Rationale is in `docs/adr/0002-single-framework-tree.md`.

## [0.1.0] — initial draft

### Added
- Three-layer model: SDD for intent, TDD/evals for behaviour, Agile for direction
- Capability documents as the living source of truth
- Change folders (`docs/changes/NNN-slug/`) as the unit of work
- Light and full tracks
- Templates: capability, change, plan, tasks, ADR, eval case
- Skills: write-change, plan-change, tdd-slice, write-eval-cases,
  update-capability, drift-check, new-adr, project-adopt
- Cross-OS `verify` entry point and adapter sync script
- CI matrix across Ubuntu, macOS and Windows

### Known gaps
- `drift_check.py` implements traceability checks only; it does not verify that
  prose matches behaviour.
- No automated capability-inventory generation for adoption yet.
