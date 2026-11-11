# AGENTS.md — the CRAFT framework repository

**You are in the framework's own repository, not a project using it.**
The `.craft-framework-repo` file at the root is what marks it. Run
`python3 framework/craft.py context` if you are unsure.

## The ownership rule is reversed here

In a project, `framework/` is read-only. **Here it is the work.** Everything
under `framework/` is what you edit; `docs/` holds this repository's own
capabilities, changes and decisions, exactly as a project's would.

`python3 framework/craft.py manifest`, `gates`, `release` and `init` only run
here, and refuse to run in a project.

## Before changing anything

Read **[`MAINTAINING.md`](MAINTAINING.md)** — the release procedure, what is
generated from what, and the rules that keep a change from breaking every
downstream project.

Then read **[`framework/agent-rules.md`](framework/agent-rules.md)** for the
process and the rules for agents. Everything in it applies here *except* the
ownership section, which this file overrides.

## What breaks downstream if you get it wrong

| Mistake | Consequence |
|---|---|
| Editing a generated block by hand | Overwritten at the next `release`, and the source of truth silently disagrees |
| Forgetting `craft.py manifest` before committing | Every project that upgrades sees a false "modified locally" warning |
| Changing a path under `framework/` | Projects' `AGENTS.md` and skills may point at a file that no longer exists |
| Putting project-shaped content in `framework/` | It reaches every client project on upgrade |
| Changing `scripts/verify.sh`'s interface | Breaks CI, git hooks and every document that names the command |

## Generated from something else — never edit directly

| File | Generated from | By |
|---|---|---|
| Gate summaries in `working-guide.md`, `user-guide.md`, `workflows.md` | `framework/definition-of-done.md` | `craft.py gates` |
| `docs/*/README.md` index tables | frontmatter in those folders | `craft.py index` |
| `.claude/skills/`, `.cursor/rules/`, `.github/pull_request_template.md`, `.github/workflows/verify.yml` | `framework/skills/`, `framework/templates/` | `craft.py sync` |
| `framework/MANIFEST.sha256` | every framework file | `craft.py manifest` |

## Cutting a release

```bash
python3 framework/craft.py release
```

It runs everything in the right order and refuses if `framework/VERSION` has
no matching `framework/CHANGELOG.md` entry. `MAINTAINING.md` has the detail.

## Testing a change end to end

A framework change is not proven until a project has survived it:

```bash
python3 framework/craft.py release
cd /tmp && git clone /path/to/this/repo trial && cd trial
python3 framework/craft.py init
bash scripts/verify.sh
```

For a change to the upgrade path, also upgrade an existing project from the
previous version and confirm `git status` shows only framework files.
