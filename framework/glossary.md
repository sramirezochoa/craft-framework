# Glossary

| Term | Meaning here |
|---|---|
| **Capability** | A living document describing what the system does *today* in one area of behaviour. Amended at the end of every change that touches it. |
| **Change** | One unit of work: a delta against one or more capabilities. Lives in `docs/changes/NNN-slug/`. |
| **Change spec** (`change.md`) | States current behaviour, desired behaviour, what stays the same, and the acceptance criteria. The *what*, never the *how*. |
| **Plan** (`plan.md`) | The technical approach for one change. The *how*. |
| **Tasks** (`tasks.md`) | Ordered, small work items, each traceable to an acceptance criterion. |
| **Acceptance criterion** (`AC-n`) | A single testable statement of required behaviour, with a stable ID. |
| **ADR** | Architecture Decision Record. Why one approach was chosen over the alternatives. Written for hard-to-reverse decisions. |
| **Gate** | A checkpoint a human passes before the next step starts. Defined in `definition-of-done.md`. |
| **Light track** | Reduced flow for behaviour-preserving work: test + fix + verify. |
| **Full track** | The complete flow, for new or altered behaviour. |
| **Eval case** | A scripted test for non-deterministic (LLM-driven) behaviour, asserting properties rather than exact output. |
| **Drift** | Documentation that no longer matches the code. The failure mode this framework exists to prevent. |
| **Fold back** | Updating the capability doc at the end of a change so it describes the new reality. Gate 6. |
| **Adoption** | Introducing this framework to a codebase that predates it, lazily, one capability at a time. |
| **Skill** | A reusable procedure in `framework/skills/<name>/SKILL.md`, readable by agents and humans. |
| **Adapter** | A generated, tool-specific copy of a canonical file. Never edited by hand. |
| **Verify** | `scripts/verify.sh` — the executable definition of "passing". |
| **EARS** | Easy Approach to Requirements Syntax: the When/While/If/Where/shall patterns used for acceptance criteria. |
