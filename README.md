# CRAFT — Capability-based, Review-gated, Agent-Friendly Technique

A tool-neutral delivery framework for building software with AI coding agents.

Works for **APIs, UIs, bots, agents, services, CLIs** — greenfield and brownfield.
Works with **Claude Code, Codex, Cursor, or no agent at all**.
Works on **Windows, macOS and Linux**.

> Rename it to whatever you like. The name only appears in this file and `AGENTS.md`.

---

## The idea in one paragraph

Three layers, each covering a failure mode the others don't:

| Layer | Prevents | Mechanism |
|---|---|---|
| **SDD** — spec-driven | Building the thing wrong | Written intent, reviewed before code |
| **TDD / evals** | Behaviour regressions | Executable acceptance criteria |
| **Agile** | Building the wrong thing | Small slices, frequent feedback, retros |

The unit of documentation is a **capability** (a living description of what the
system does today), and the unit of work is a **change** (a delta against one or
more capabilities). Greenfield just means the change creates a new capability.

---

## One rule about ownership

```
framework/      ← framework-owned. Never edit. Replaced wholesale on upgrade.
everything else ← yours. Never overwritten.
```

That's the whole rule. `framework/` holds the process, the rules, the
templates, the skills and the scripts. Your project — its capabilities, its
changes, its decisions, its build wiring — lives outside it.

Where the framework needs something project-specific, it reads a file you own:

| Framework file | Reads your | 
|---|---|
| `framework/constitution.md` | `docs/amendments.md` |
| `framework/craft.py` | `scripts/project/verify-impl.sh` |
| generated CI workflow | `.github/actions/setup/action.yml` |
| `framework/agent-rules.md` | `AGENTS.md`, then `docs/overview.md` |

`bash scripts/verify.sh` warns if a framework-owned file has been edited
locally, because such edits disappear at the next upgrade.

---

## Requirements

| | |
|---|---|
| **Python ≥ 3.8** | Standard library only — nothing to install. It runs `framework/craft.py`, the entire toolchain |
| **bash** | Ships with Git on Windows; already present on macOS and Linux |
| **Your language toolchain** | Whatever builds and tests your project |
| *Optional* | Git ≥ 2.30, shellcheck |

No Node, no Make, no Docker, no framework package to install. On Windows, use
WSL2 or Git Bash. `bash scripts/verify.sh` checks all of this first and tells
you what is missing — details in [framework/tooling.md](framework/tooling.md).

## Quick start

> **Using this day to day?** Read
> **[framework/user-guide.md](framework/user-guide.md)** — short instructions
> organised by situation: starting a project, adopting it into an existing
> codebase, building a feature, fixing a bug, reviewing a change, plus
> troubleshooting. The rest of this README is orientation.

### New project

```bash
git clone <this-repo-url> my-project
cd my-project
python3 framework/craft.py init     # turns the clone into a project
```

`init` strips the framework's own files and installs the project skeleton.
It also removes the `origin` remote, which still points at the framework
repository — otherwise your first `git push` would land there. Point it at
your project's own repository instead:

```bash
git remote add origin <your-project-repo-url>
```

Then edit the four files that are yours — `init` prints the list — and run:

```bash
bash scripts/verify.sh
```

The clone keeps the framework's commit history. For a project that starts
clean, clone with `--depth 1`, then `rm -rf .git && git init -b main` before
running `init`.

Add `--dry-run` to `init` to see exactly what it changes first.

### Existing project

See **Adoption** in [framework/working-guide.md](framework/working-guide.md).
Short version: write `docs/overview.md`, stub the capability list, and write
each capability doc lazily the first time you touch that area. Do not
back-write the whole system.

### Starting a change

Ask your agent: *"start a change to allow cancelling an order after shipping"*.
It should pick up the `write-change` skill, read the relevant capability doc,
and draft `docs/changes/NNN-slug/change.md` for your review.

Without an agent, copy `framework/templates/change.md` by hand. The framework
is just files; the skills are a convenience layer.

---

## Layout

```
framework/                 FRAMEWORK-OWNED — replaced on upgrade
├── VERSION
├── CHANGELOG.md
├── user-guide.md          START HERE — what to do, by situation
├── agent-rules.md         the process and rules, read by agents
├── constitution.md        the rules that never bend
├── working-guide.md       the reference: lifecycle, tracks, roles, adoption
├── workflows.md           every workflow as a Mermaid diagram
├── design.md              why the framework is shaped this way
├── conventions.md         naming, numbering, EARS criteria
├── definition-of-done.md  gates 0–6 as checklists
├── review-checklist.md
├── tooling.md             the only file that names specific tools
├── glossary.md
├── templates/             artifact templates + the project skeleton
├── skills/                canonical skills, synced into tool-specific folders
├── craft.py               the whole toolchain: verify, drift, index, sync, upgrade
├── example/               a worked change spec + capability doc
└── MANIFEST.sha256        checksums, so local edits are detectable

docs/                      YOURS
├── overview.md            project context, stack, conventions chosen
├── architecture.md        how the system is built — structure, not behaviour
├── amendments.md          project-specific constitution rules
├── capabilities/          what the system does today
├── changes/               NNN-slug/ — the units of work
└── adr/                   why we chose what we chose

scripts/
├── verify.sh              stable entry point (thin shim into framework/)
└── project/verify-impl.sh YOURS — your build commands

evals/                     YOURS — behavioural cases for LLM features
mcp/servers.yaml           YOURS — connector list
.github/actions/setup/     YOURS — CI toolchain
AGENTS.md                  YOURS — project description, points at agent-rules
CLAUDE.md                  adapter → @AGENTS.md
MAINTAINING.md             framework repo only; `init` removes it
```

Start with **[framework/README.md](framework/README.md)**.

---

## Upgrading

```bash
python3 framework/craft.py upgrade ~/src/craft-framework --dry-run
python3 framework/craft.py upgrade ~/src/craft-framework
bash scripts/verify.sh
```

`python3 framework/craft.py` with no arguments lists every command.

It replaces `framework/` and the `scripts/verify.sh` shim, regenerates the
adapters, and touches nothing else. `git diff` afterwards should show only
framework files — if it shows anything of yours, that is a bug in the
framework, not in your project.

Projects pin a version in `framework/VERSION` and upgrade when they choose. A
client project can sit on `0.1.0` while you work on `0.3.0`.

---

## Lineage

Borrowed deliberately:

- **GitHub Spec Kit** — constitution + numbered change folders + spec/plan/tasks split
- **OpenSpec** — the brownfield delta model, which this generalises into capabilities
- **Kiro / EARS** — structured, testable phrasing for acceptance criteria
- **Michael Nygard** — architecture decision records
- **XP / Agile** — vertical slices, small batches, retros

Deliberately skipped: multi-agent role-play, spec-as-source code generation, and
anything that only works inside one IDE.

What this adds on top: **capabilities as the living source of truth**,
**executable gates** instead of conventions, **evals as a first-class test
type** for non-deterministic features, and **structural ownership** so the
framework can be upgraded without merge archaeology.
