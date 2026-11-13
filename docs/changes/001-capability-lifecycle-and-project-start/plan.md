# Plan — Change 001

## Approach

Extend the capability status set rather than add a second document type, so
the index, drift and skills keep a single shape. Put the interview in a skill —
it runs in whichever agent the developer uses and can read files and pasted
text — with a stack reference beside it for deriving commands. Enforce the
lifecycle in `craft.py drift`, and fix frontmatter comment parsing that the new
check depends on.

## Components touched

| Component | Change | Notes |
|---|---|---|
| `framework/craft.py` | modified | drift lifecycle checks, frontmatter comments, framework tests stage, init message |
| `framework/skills/project-start/` | new | `SKILL.md`, `stacks.md` |
| `framework/tests/` | new | stdlib tests for the drift rules |
| `framework/templates/capability.md` | modified | statuses, Planned changes, Deprecation |
| `framework/skills/update-capability`, `write-change`, `project-adopt` | modified | lifecycle cases; stale paths |
| `framework/working-guide.md`, `user-guide.md`, `conventions.md`, `agent-rules.md`, `definition-of-done.md` | modified | lifecycle and setup |
| `framework/templates/pull-request.md`, `templates/project/capabilities/README.md`, `README.md` | modified | |

## Structural impact

- [ ] A component is added, removed or given a different responsibility
- [ ] An integration point changes, including its failure behaviour
- [ ] A cross-cutting approach changes (auth, config, logging, retries, …)
- [ ] A data store is added, removed or repurposed
- [ ] The model, prompt or tool architecture changes
- [ ] Deployment topology or environments change
- [x] **None of the above — architecture.md is unaffected**

## Contracts

| Contract | Change | Breaking? | Versioning approach |
|---|---|---|---|
| Capability `status` values | adds `planned`; defines the rest | no | additive, minor release |

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Comment stripping truncates an unquoted value containing ` #` | low | Matches YAML; quoted values are kept (AC-4) |
| Framework tests' AC ids satisfy a project's ACs | — | `framework/tests` is scanned only in the framework repo |

## New dependencies

None.

## Test strategy

| AC | Test type | Where |
|---|---|---|
| AC-1 | integration | `framework/tests/test_capability_lifecycle.py` |
| AC-2 | integration | same |
| AC-3 | integration | same |
| AC-4 | integration | same |
| AC-5 | unit | same |

End to end: fresh clone → `init` → `project-start` with a sample brief →
`verify` passes with *not scaffolded yet*.
