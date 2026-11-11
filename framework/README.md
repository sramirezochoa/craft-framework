# The framework — start here

**Everything in this directory is framework-owned.** Do not edit it: the whole
tree is replaced on upgrade, and local edits disappear. Project-specific
content goes in the files listed under "Where your things go" below.

**New here? Read [user-guide.md](user-guide.md).** It is short, organised by
situation, and tells you what to do. Everything below is reference.

| File | Read when | Changes |
|---|---|---|
| [user-guide.md](user-guide.md) | First. Find your situation, follow the steps | Occasionally |
| [constitution.md](constitution.md) | Once, then refer back | Rarely |
| [working-guide.md](working-guide.md) | When the process needs explaining | Occasionally |
| [workflows.md](workflows.md) | To see the process drawn | With the guide |
| [conventions.md](conventions.md) | When naming or filing something | Occasionally |
| [definition-of-done.md](definition-of-done.md) | At every gate | Occasionally |
| [review-checklist.md](review-checklist.md) | When reviewing a change | Occasionally |
| [tooling.md](tooling.md) | During setup, or when tools change | Often |
| [glossary.md](glossary.md) | When a term is unclear | Rarely |
| [design.md](design.md) | When you want the rationale, or are tempted to change the framework | Rarely |
| [templates/](templates/) | When creating an artifact | Rarely |
| [example/](example/) | To see a filled-in change spec and capability doc | Delete once you have your own |

## The thirty-second version

- A **capability** describes what the system does *today*. It is living.
- A **change** is one unit of work: a delta against one or more capabilities.
- Work flows: understand → change spec → plan → tests → implement → verify →
  fold back into the capability.
- Each arrow is a **gate** a human passes.
- **Light track** skips the spec for small, behaviour-preserving work.
- `bash scripts/verify.sh` is the executable definition of "passing".

## Where your things go

| You want to | Edit |
|---|---|
| Add a rule for this project | `docs/amendments.md` |
| Wire up lint / test / eval commands | `scripts/project/verify-impl.sh` |
| Set up the CI toolchain | `.github/actions/setup/action.yml` |
| Record stack, conventions, domain terms | `docs/overview.md` |
| Describe how the system is built | `docs/architecture.md` |
| Describe what the system does | `docs/capabilities/<name>.md` |
| Start a piece of work | `docs/changes/NNN-slug/` |
| Record a decision | `docs/adr/NNNN-title.md` |

## When the framework itself is wrong

Within a development cycle, this directory is static — that is the point of it
being the reference everyone reads against.

Between cycles it changes through the retro's second question: *did the
framework steer correctly?* If a rule or a skill is wrong for every project,
change it in the framework repository, add a `CHANGELOG.md` entry, bump
`VERSION`, and let projects upgrade when they choose. If it is wrong for only
this project, that is an amendment, and it needs an ADR.
