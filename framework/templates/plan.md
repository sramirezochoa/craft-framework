# Plan — Change NNN

> **The HOW.** Written after `change.md` is approved, never before.

## Approach

The chosen technical approach in a few sentences. If alternatives were
seriously considered, name them and why they lost — and if the decision is
hard to reverse, write an ADR instead of burying it here.

## Components touched

| Component | Change | Notes |
|---|---|---|
| `<module / service / file>` | new / modified / deleted | |

## Structural impact

Does this change what `docs/architecture.md` describes? Tick everything that
applies — each tick becomes a task and a gate-6 item.

- [ ] A component is added, removed or given a different responsibility
- [ ] An integration point changes, including its failure behaviour
- [ ] A cross-cutting approach changes (auth, config, logging, retries, …)
- [ ] A data store is added, removed or repurposed
- [ ] The model, prompt or tool architecture changes
- [ ] Deployment topology or environments change
- [ ] **None of the above — architecture.md is unaffected**

If anything above is ticked, add a task to update `docs/architecture.md` and
list it under gate 6. Structure only; behaviour belongs in the capability doc.

## Contracts

Interface changes, and whether they are breaking.

| Contract | Change | Breaking? | Versioning approach |
|---|---|---|---|
| `POST /orders/{id}/cancel` | new field `reason` | no | additive |

## Data

Schema changes, migrations, backfills. Backward compatibility and sequencing.

## Prompts and model behaviour

*(LLM-based features only — delete otherwise)*

| Prompt / tool | Change | Eval impact |
|---|---|---|
| | | |

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| | | |

## New dependencies

| Dependency | Version | Why | Alternatives considered |
|---|---|---|---|

*(or "none")*

## Observability

How you will know this works in production: logs, metrics, traces, alerts.

## Rollout and rollback

- Feature flag? Phased? All at once?
- How to roll back, and what becomes irreversible once deployed

## Test strategy

| AC | Test type | Where |
|---|---|---|
| AC-1 | integration | `test/...` |
| AC-2 | unit | `test/...` |
| AC-3 | eval | `evals/<capability>/AC-3-....yaml` |

Also note any existing tests that must keep passing and are worth watching.
