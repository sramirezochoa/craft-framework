# Framework feedback

**PROJECT-OWNED.** A running log of things the framework got wrong, got in the
way, or failed to cover on *this* project.

Capture findings **the moment you hit them**, while you still remember the
detail. Do not stop to open an issue — that friction is why feedback never
gets recorded. Review this file at the retro, and raise upstream whatever is
true for more than this project.

```bash
python3 framework/craft.py feedback "gate 0 is slow on one-line copy changes"
```

That appends a dated entry with the framework version filled in.

## What is worth recording

| Kind | Example |
|---|---|
| **Rule wrong** | A constitution rule that is too strict, too loose, or does not apply here |
| **Check misfires** | `drift` warns about something correct, or stays quiet about something broken |
| **Skill output poor** | A skill produced a spec or plan you had to largely rewrite |
| **Docs unclear** | You had to guess, or two documents disagreed |
| **Gap** | The framework has no answer for something you do regularly |
| **Not worth it** | Ceremony whose cost exceeded its value |
| **Deviation** | **You did not follow the framework. Why not?** |

That last row is the most valuable and the least likely to be written down.
Every place you quietly worked around the process is a place the process is
wrong, too slow, or unclear. Record it without judgement — it is data.

## Triage at the retro

For each entry, decide one of:

- **Project-specific** → fix it here: `docs/amendments.md`, `AGENTS.md`, or
  your own conventions. Mark the entry `local`.
- **True for every project** → raise it on the framework repository. Mark the
  entry with the issue link.
- **Not actually a problem** → say why, and mark it `wontfix` so the next
  person does not re-litigate it.

The bar for changing the framework is in `MAINTAINING.md`: is it true for
every project, can it be executable rather than written, and does it duplicate
something that already exists?

---

## Log

<!-- Newest first. `craft.py feedback` adds entries here. -->
