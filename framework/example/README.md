# Worked example

A filled-in change spec and the capability document it folds back into, so you
can see the intended level of detail rather than inferring it from blank
templates.

| File | Shows |
|---|---|
| [`012-allow-cancel-after-ship/change.md`](012-allow-cancel-after-ship/change.md) | A full-track change spec: current vs desired behaviour, EARS acceptance criteria, an explicit "what does not change", and a declared change to an existing test |
| [`order-cancellation.md`](order-cancellation.md) | The capability doc after gate 6 — present tense, history confined to the change log |

Two things worth noticing:

1. **The change spec contains no implementation.** No class names, no
   algorithms. Those belong in `plan.md`. When spec and plan merge, specs stop
   being reviewable.
2. **The capability doc has no narrative of how it got this way.** It describes
   the system as it is. The change log table carries the history, one line per
   change. Documents written as histories become unreadable after a year.

This folder lives under `framework/` deliberately, so the examples do not
appear in a real project's change history and the drift check ignores them.
Delete it once you have changes of your own.
