---
name: project-start
description: Set up a new project that has no code yet, through an interview. Use right after `craft.py init` on a greenfield project, or when the user wants to start a new project, describe what they are going to build, or turn a product brief, PRD or pasted notes into the project's documentation. Produces the overview, architecture, planned capabilities, project rules, verify wiring, CI toolchain and a founding ADR — each confirmed by the user.
---

# Start a new project

Turn what the developer knows about the project — in their head, in a brief, or
both — into the project's documentation, one confirmed document at a time.

For a codebase that already has code, use `project-adopt` instead.

## Rules for the whole interview

- **Every answer lands in a document.** Never ask a question whose answer is
  not written down somewhere below.
- **Unknown is an answer.** "Not decided yet" becomes `OPEN QUESTION: …` in the
  document it belongs to. Never fill a gap with a plausible guess — a confident
  wrong document is worse than an honest gap.
- **Confirm before writing.** Show each document's content and get a yes before
  writing the file and moving to the next block.
- **Ask in small batches** — three or four questions at a time, grouped by
  block. Offer a sensible default where one exists; the developer can accept it
  with a word.
- **No behaviour in capability documents.** They are `planned`: purpose and
  scope only. Intended behaviour is written later, in change specs.
- **Write nothing under `framework/`.** It is read-only in a project.

## 0. Gather what already exists

Ask once: *"Do you have anything written about this project — a brief, a PRD,
notes, an email? Give me a path or paste it. Or we can start from scratch."*

If they provide something (any number of files and pasted chunks):

1. Read all of it.
2. Map it onto the five blocks below and show a short table: per block, what
   you **found** and what is **missing**.
3. Point out contradictions between sources, and anything that reads like a
   decision but might be a wish. Ask which is right; do not pick.
4. In the interview that follows, **skip what the input already answers** —
   show it for confirmation instead of asking again.

The input is not copied into the repository; it would go stale beside the real
documents. Note what it was (title, date, author if known) for ADR 0001.

## 1. The product

Ask: what it is, who uses it, what problem it solves, what success looks like,
and the domain terms that mean something specific here.

Write:
- `AGENTS.md` — replace the two placeholder lines under **This project** with a
  one-sentence description and the stack line (fill the stack after block 3).
- `docs/overview.md` — **What this is** (one paragraph) and **Domain glossary**.

## 2. What it must do — planned capabilities

Ask what the system must do, then **propose a capability list** using the
granularity rule in `framework/working-guide.md` §2: something you could demo
on its own and a stakeholder would recognise by name. Named after behaviour,
not modules. Let the developer merge, split and rename before writing
anything — granularity matters more than names.

For each agreed capability, ask: its purpose, what is clearly in and out of
scope, the interfaces it is expected to expose (HTTP, events, UI, tools), what
it depends on, and the order of the changes likely to build it.

Write one `docs/capabilities/<name>.md` per capability from
`framework/templates/capability.md`:

- `status: planned`, `owner`, `last-verified: <today>`
- **Purpose**, **Not in scope**, **Dependencies**, **Open questions**
- **Interfaces** — expected, marked "(planned)"
- **Current behaviour** — exactly "Not built yet."
- **Planned changes** — the ordered list
- Delete **Deprecation**; leave **Where it lives** and **Change log** empty

Then run `python3 framework/craft.py index`.

## 3. Stack and tools

Ask, defaulting where the stack makes one obvious:

| Ask | Example answer |
|---|---|
| Language and version | Java 21 |
| Framework | Spring Boot 3 |
| Build tool / package manager | Maven (wrapper) |
| Test framework | JUnit 5 |
| Linter / formatter | Spotless |
| Persistence | PostgreSQL |
| Messaging | none |
| LLM provider and models | none |
| Deployment target | Kubernetes |
| Windows environment for the team | Git Bash |

From the answers, derive the commands with **[stacks.md](stacks.md)**. If a tool
is missing ("Maven, but no linter decided"), ask — offering the stack's usual
choice from `stacks.md` — rather than choosing silently. Show the derived
commands and confirm them.

Write:
- `docs/overview.md` — **Stack** table; **How to run it locally** with the
  commands that will work once the skeleton exists.
- `scripts/project/verify-impl.sh` — define `project_lint`, `project_test` and
  `project_evals` for this stack, each guarded so verify reports "not
  scaffolded yet" until the build file exists. Use the pattern in `stacks.md`
  exactly; keep the file's header comment.
- `.github/actions/setup/action.yml` — the toolchain setup steps from
  `stacks.md`, with the versions chosen above.

## 4. Structure

Ask: the components or services and what each is responsible for, which
capabilities each serves, the external systems it talks to and **what happens
when each is unavailable**, data stores, and the approach to authentication,
configuration and secrets, logging, error handling.

Write `docs/architecture.md`, keeping its sections:
- **System context** diagram and **Components** table (with the *Capabilities
  it serves* column filled from block 2)
- **Integration points** including failure behaviour, **Data**,
  **Cross-cutting concerns**
- **Model and prompt architecture** only if an LLM is involved; otherwise
  delete the section
- **Scale and limits** — "unmeasured" is the honest answer on day one
- Leave **Known debt** and **Key decisions** for block 6

Structure only — if an answer describes behaviour, it belongs to a capability
or a future change spec.

## 5. Rules and conventions

Ask: rules that must never be broken in this project (money handling, data
retention, what may never be logged, approval steps), then the conventions —
change numbering, issue tracker, feedback cadence, team and their tools,
environments.

Write:
- `docs/amendments.md` — only rules someone could check. Anything that cannot
  be checked is a preference: put it in `docs/overview.md` instead, and say so.
- `docs/overview.md` — **Conventions chosen for this project**, **Collaborators
  and tools**, **Environments**, **Things a newcomer gets wrong** (often empty
  on day one — leave the placeholder).

## 6. Wrap up

1. **ADR 0001** — `docs/adr/0001-<stack-and-structure>.md` from
   `framework/templates/adr.md`, following the `new-adr` skill: the stack and
   initial structure, the alternatives the developer mentioned, and in
   **Context** what the setup was based on (e.g. "client brief, 2026-11-13, plus
   interview"). Add it to **Key decisions** in `docs/architecture.md`.
2. **Change 001** — use `write-change` to draft
   `docs/changes/001-project-skeleton/change.md` with `status: draft`: create
   the build files and an empty, passing test suite so verify runs the real
   commands. It lists no capabilities.
3. Run `python3 framework/craft.py index`, then `bash scripts/verify.sh`. It
   should pass, with lint and tests reported *not scaffolded yet*.
4. Show the developer the list of files written and every `OPEN QUESTION` left,
   grouped by document.

## Done when

- `AGENTS.md`, `docs/overview.md`, `docs/architecture.md` and
  `docs/amendments.md` hold confirmed content, with unknowns as `OPEN QUESTION`
- Every agreed capability has a `planned` document and appears in the index
- `verify-impl.sh` and the CI setup action match the chosen stack
- ADR 0001 exists and change 001 is drafted
- `bash scripts/verify.sh` passes

The next step is `write-change` → approve → `plan-change` for change 001, then
for the first capability.
