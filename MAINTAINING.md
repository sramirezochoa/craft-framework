# Maintaining the framework

For people working on CRAFT itself. If you are using the framework on a
project, you want [`framework/user-guide.md`](framework/user-guide.md)
instead.

This file exists only in the framework repository. `craft.py init` removes it.

---

## Am I in the right repository?

```bash
python3 framework/craft.py context
```

The framework repository has a `.craft-framework-repo` file at the root. A
project does not. Four commands — `init`, `gates`, `manifest`, `release` —
refuse to run without it, because each would do damage in a project.

---

## The rule that matters

**Everything you change here reaches every client project on the next
upgrade.** That cuts both ways: a fix propagates, and so does a mistake.
Before changing anything under `framework/`, ask whether it is true for
*every* project, or only for the one that prompted it. If the latter, it
belongs in that project's `docs/amendments.md`.

---

## What is generated, and from what

Never edit a generated block by hand — `release` overwrites it, and the real
source then silently disagrees.

| Output | Source | Command |
|---|---|---|
| Gate summaries in `working-guide.md`, `user-guide.md`, `workflows.md` | `framework/definition-of-done.md` | `craft.py gates` |
| `docs/*/README.md` index tables | frontmatter in those folders | `craft.py index` |
| `.claude/skills/`, `.cursor/rules/` | `framework/skills/` | `craft.py sync` |
| `.github/pull_request_template.md`, `.github/workflows/verify.yml` | `framework/templates/` | `craft.py sync` |
| `framework/MANIFEST.sha256` | every framework file | `craft.py manifest` |

Order matters: `manifest` must run **last**, because it checksums the output
of the others.

---

## Cutting a release

1. Make the change under `framework/`.
2. Add a `framework/CHANGELOG.md` entry with the new version at the top,
   including migration notes if a path moved or a file was removed.
3. Bump `framework/VERSION`.
4. Run it:

   ```bash
   python3 framework/craft.py release
   ```

   This runs `gates` → `index` → `sync` → `manifest` → `verify` in order, and
   refuses if `VERSION` has no matching changelog entry.

5. Commit and tag:

   ```bash
   git commit -am "framework vX.Y.Z: <summary>"
   git tag vX.Y.Z && git push --tags
   ```

### Versioning

| Bump | When |
|---|---|
| **Patch** | Wording, a fixed typo, a clarified rule. No project action needed |
| **Minor** | A new skill, script, template or check. Projects upgrade and carry on |
| **Major** | A moved path, a removed file, a changed command. **Requires migration notes** |

Anything that moves or removes a path is at least a documented migration, even
if the version number is small. A project maintainer reading only the
changelog must be able to follow it.

---

## Testing a change

Three levels, in increasing order of confidence.

**1. The gate**

```bash
bash scripts/verify.sh
```

**2. A fresh project survives it**

```bash
python3 framework/craft.py release
cd /tmp && rm -rf trial && git clone /path/to/craft-framework trial && cd trial
python3 framework/craft.py init
bash scripts/verify.sh
```

**3. An existing project upgrades cleanly** — required for any change to a
path, the upgrade command, or the manifest:

```bash
cd /path/to/some-project
python3 framework/craft.py upgrade /path/to/craft-framework
git status --porcelain      # ONLY framework/ and generated files may appear
bash scripts/verify.sh
```

If anything project-owned shows up in that `git status`, the change has a bug.
That is the single most valuable test in this list.

---

## Conformance across agents

The portability claim is only true if it is tested. Periodically:

1. Take a small reference change.
2. Run the full lifecycle with Claude Code, then with Codex, from clean.
3. Both should produce a change spec, a plan, failing tests, a passing
   `verify`, and an updated capability doc.

Where the two diverge, the instructions were too vague or too tool-specific.
Fix the instructions, not the tool.

---

## Does the framework use itself?

Yes, and it should — it is the best source of bugs. ADR 0002 came out of
exactly that. `docs/` here holds this repository's own changes and decisions.

Use the full track for anything structural, the light track for wording and
fixes. Do not force capability documents onto a repo this small; the ceremony
would outweigh the value.

---

## Receiving findings from projects

Projects collect findings in their own `docs/framework-feedback.md` as they
work, and raise the general ones here as issues using the **Framework
finding** template.

Triage each against the three questions below. Most findings should end in
one of:

| Outcome | When |
|---|---|
| **Fix in the framework** | True for every project. Patch, minor or major per the versioning rules |
| **Make it executable** | The finding describes something a check could have caught. Prefer this over a documentation fix |
| **Clarify the docs** | The rule was right but unfindable or ambiguous |
| **Close as project-specific** | Belongs in that project's `docs/amendments.md`. Say so plainly, and point at the file |
| **Add to known weaknesses** | Real, but not worth fixing yet. Record it in `framework/design.md` rather than letting it be rediscovered |

That last row matters. A finding closed with no trace will come back from the
next project.

**Watch for repeats.** The same finding from two different projects is strong
evidence it is general — that is the signal the per-project logs exist to
produce.

## Before you add anything

The framework's own worst failure mode is bloat. Three questions:

1. **Is it true for every project**, or only the one that prompted it?
2. **Can it be executable** rather than written down? A check that runs beats
   a rule that is read.
3. **Does it duplicate something?** Two statements of one fact will drift —
   that is how the gate numbering broke in 0.6.1. Generate it, or link to it.

`framework/design.md` has the known weaknesses and the open questions. Add to
that list honestly rather than quietly working around a gap.
