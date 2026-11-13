# Conventions

Mechanical details. When in doubt, follow what already exists in the repo.

---

## Capability files

```
docs/capabilities/<kebab-case-name>.md
```

- Named after the behaviour, not the implementation: `order-cancellation`,
  not `OrderServiceImpl`.
- No numbering — capabilities are not ordered, they are a set.
- Listed in `docs/capabilities/README.md`.
- Status in frontmatter, one of:

  | Status | Meaning |
  |---|---|
  | `planned` | Decided, not built. Purpose and scope only — no behaviour |
  | `active` | Built. Current behaviour describes it |
  | `deprecated` | Still runs as described; being phased out, nothing new depends on it |
  | `superseded-by: <name>` | Replaced by another capability |

  A capability removed with no replacement has its document deleted by the
  removal change. `craft.py drift` warns on any other value.

## Change folders

```
docs/changes/NNN-kebab-slug/
```

- `NNN` is a zero-padded sequence number, three digits, never reused.
- **Allocating the number**: take the highest existing number plus one, at the
  moment the folder is created. If two branches collide, the later-merged one
  renumbers — it is a folder rename plus a branch rename, nothing more.
- If you use an issue tracker, prefer the ticket ID instead and say so in
  `docs/overview.md`: `docs/changes/PROJ-142-cancel-after-ship/`.
  Pick one scheme per project and stick to it.
- Archived changes stay where they are. History is not deleted.

## ADRs

```
docs/adr/NNNN-kebab-title.md
```

- Four digits, starting at `0001`.
- Title states the decision, not the topic: `0007-use-outbox-for-event-publishing`,
  not `0007-event-publishing`.
- Never edited after acceptance except to change `status`. A reversal is a new
  ADR that supersedes the old one.

## Branches

```
change/NNN-slug          a full-track change
fix/short-description    a light-track fix
chore/short-description  tooling, deps, no behaviour change
```

## Commits

Conventional Commits, with the change ID in the footer:

```
feat(orders): allow cancellation after shipment

Refs: change 012
```

Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `perf`, `build`.

## Pull requests

- One PR per change. Title: `NNN — short description`.
- Body uses `.github/pull_request_template.md`.
- A PR that touches behaviour and does not touch a capability doc should be
  questioned in review.

## Acceptance criteria

Write them so a test can be derived mechanically. The EARS-style patterns
(borrowed from Kiro) work well and are tool-independent:

| Pattern | Shape |
|---|---|
| Event-driven | **When** `<trigger>`, the system **shall** `<response>` |
| State-driven | **While** `<state>`, the system **shall** `<response>` |
| Conditional | **If** `<condition>`, **then** the system **shall** `<response>` |
| Optional | **Where** `<feature is present>`, the system **shall** `<response>` |
| Ubiquitous | The system **shall** `<response>` |

```
✅ When an order with status SHIPPED is cancelled, the system shall reject the
   request with HTTP 409 and leave the order unchanged.
✅ While a booking conversation is active, the bot shall not disclose prices
   from a different region.
❌ Cancellation should work properly.
❌ The bot should be helpful and accurate.
```

Each criterion gets a stable ID — `AC-1`, `AC-2` — referenced from tests,
tasks and eval cases. That ID is what makes traceability checkable.

## Test and eval naming

- Tests reference the criterion: `cancelAfterShipment_returns409` with a
  `// AC-3` comment, or the equivalent in your language.
- Eval case files: `evals/<capability>/<AC-id>-<slug>.yaml`.
- Regression cases from production bugs: `evals/<capability>/regression-<issue>.yaml`.

## Open questions

Anywhere in any artifact:

```
OPEN QUESTION: does the client want a refund triggered automatically on
cancellation, or is that a separate manual step?
```

A change spec with unresolved `OPEN QUESTION` markers cannot pass gate 1.

## File and path hygiene

Windows collaborators exist. Therefore:

- Relative paths only, never absolute.
- No spaces in file or folder names.
- Keep nesting shallow — Windows path length limits are real.
- Scripts are invoked as `bash scripts/x.sh`, never `./scripts/x.sh`, because
  Windows does not track the executable bit reliably.
- `.gitattributes` forces LF on scripts. Do not override it.
