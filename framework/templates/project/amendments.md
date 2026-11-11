# Project amendments to the constitution

**PROJECT-OWNED.** The framework never overwrites this file.

Rules specific to this project, in addition to `framework/constitution.md`.
They carry the same weight: anyone, human or agent, may stop work by pointing
at a line here.

Keep them as short and as testable as the framework's. A rule nobody can check
is a preference, and preferences belong in `docs/overview.md`.

---

## Amendments

*None yet.*

<!--
Examples of what belongs here:

21. All money is handled as `BigDecimal` with explicit scale and rounding mode.
    Never `double`, never `float`.
22. Every HTTP endpoint declares an explicit timeout; there is no default.
23. No direct writes to the `legacy_orders` table — go through
    `LegacyOrderGateway`.
24. Customer-facing copy is approved by the client before release.
25. Conversations are never logged in full; only intent, tool calls and
    outcome.
-->

---

## Removing an amendment

Same bar as the framework constitution: it needs an ADR explaining why. Rules
are removed when they stop earning their place, not when they become
inconvenient.
