---
name: write-eval-cases
description: Write eval cases for behaviour decided by a language model — chatbots, agents, classification, extraction, generation. Use when acceptance criteria cannot be checked with ordinary assertions because the output is non-deterministic.
---

# Write eval cases

Evals are the TDD layer for non-deterministic behaviour. Same discipline as
tests: written before implementation, kept green, never weakened.

Evals are **not bot-specific**. Anything a model decides qualifies: a
classifier, an extraction endpoint, a RAG answer, a routing decision. The
choice is per feature — one service often needs ordinary tests for its
plumbing and evals for its one LLM-backed endpoint.

## When to use this instead of an ordinary test

| Behaviour | Verify with |
|---|---|
| Deterministic logic, API shape, data transforms | Ordinary tests |
| What the model decides, says, calls or refuses | Eval cases |
| Guardrails — things the model must never do | Eval cases |

Many features need both. The deterministic wrapper around a model call still
gets unit tests.

## Steps

### 1. Start from the acceptance criteria

Each `AC-n` in the change spec that depends on model behaviour gets at least
one eval case.

### 2. Choose what to assert

**Assert properties, not strings.** Exact-match assertions on generated text
are brittle, and the next person deletes them — which defeats the point.

Good assertions:

- Which tool or function was called, and with what arguments
- Whether a required field was captured or extracted
- Whether the output validates against a schema
- Whether a refusal or an escalation happened
- Whether specific information is present — a refund timeline, a disclaimer
- Whether something is absent — an invented figure, a competitor's name, PII

### 3. Write the case

Copy `framework/templates/eval-case.yaml` to
`evals/<capability>/<AC-id>-<slug>.yaml`.

Pick the shape that fits, and use one or the other:

| Shape | Use for | Key |
|---|---|---|
| Conversation | dialogue, multi-turn flows | `turns: [{user: "..."}]` |
| Single shot | classification, extraction, summarisation | `input: <string or object>` |

Do not wrap a single-shot input in a fake conversation — the runner supports
both shapes directly.

Keep setup minimal — only the fixtures the case actually needs.

### 4. Cover the three categories

For each capability, make sure you have:

| Tag | Covers |
|---|---|
| `happy-path` | The behaviour the criterion describes |
| `edge-case` | Ambiguous input, missing information, out-of-scope requests, multi-intent messages |
| `guardrail` | What must never happen — inventing facts, leaking internals, acting outside permission, unsafe content |

Guardrails belong in `evals/defaults.yaml` when they apply to every case, rather
than being copy-pasted.

### 5. Confirm they fail (gate 3)

Run the suite. New cases must fail because the behaviour is missing.

### 6. Regression cases

**Every production bug becomes an eval case.** No exceptions (working guide §5).
Tag it `regression` and name it after the issue.

## Rules

- A prompt change or a model change is a behaviour change: run the suite
  (constitution rules 18–19).
- Never loosen an assertion to make a case pass. If the expected behaviour
  genuinely changed, that goes in the change spec and gets approved first.
- Evals are non-deterministic by nature. If a case flickers between runs, the
  assertion is too specific — tighten the property, do not delete the case.

## Done when

- Every model-dependent `AC-n` has at least one case
- Happy-path, edge-case and guardrail coverage exists for the capability
- New cases fail for the right reason
- Existing cases still pass
