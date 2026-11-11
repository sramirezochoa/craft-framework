# Evals

Behavioural test cases for anything a language model decides — what it says,
which tool it calls, what it refuses, what it extracts, how it classifies.

**Not only chatbots.** A classification endpoint, a document extractor, a RAG
answer and a tool-calling agent all belong here. The dividing line is per
*feature*, not per project: in one service, request validation and
persistence get ordinary tests while the one LLM-backed endpoint gets evals.
If the same input always produces the same output, write a test instead.

Evals are the TDD layer for non-deterministic behaviour: written before
implementation, kept green, never weakened to pass.

## Layout

```
evals/
├── defaults.yaml              guardrails applied to every case
├── run.py                     the runner (PROJECT: implement)
└── <capability>/
    ├── AC-1-happy-path.yaml
    ├── AC-2-missing-info.yaml
    └── regression-1842.yaml
```

## Two case shapes

| Shape | Use for | Key |
|---|---|---|
| Conversation | dialogue, multi-turn flows | `turns: [{user: "..."}]` |
| Single shot | classification, extraction, summarisation, one-call endpoints | `input: <string or object>` |

A case uses one or the other. The runner passes whichever it finds straight
through to `call_system`, so a classifier never has to pretend to be a chat.

## Writing cases

Use `framework/templates/eval-case.yaml` and the `write-eval-cases` skill.

The one rule that matters: **assert properties, not exact strings.** Which tool
was called, whether a field was captured, whether the output validates, whether
a refusal happened — not the precise wording. Exact-match assertions on model
output are brittle, and the next person deletes them.

## Coverage

Each capability wants all three:

| Tag | Covers |
|---|---|
| `happy-path` | The behaviour the criterion describes |
| `edge-case` | Ambiguous input, missing information, multi-intent, out of scope |
| `guardrail` | What must never happen |

Every production bug becomes a `regression` case. No exceptions.

## The runner

`scripts/verify.sh` calls `python3 -I evals/run.py`.

`run.py` ships as a working skeleton with two functions marked TODO:

- **`call_system(request, setup)`** — required. Runs one case against your
  system and returns `{text, tool_calls, turns}`. `request` is either
  `{"turns": [...]}` for a conversation or `{"input": ...}` for a single
  shot. Until you implement it, every case
  fails loudly rather than passing silently.
- **`judge(claim, text)`** — only if you use `contains_information` or prose
  `must_not`. Those are semantic and need a model to decide. Left
  unimplemented, they are reported as UNJUDGED — counted and printed, never
  quietly passed.

Mechanical assertions work out of the box: `tool_calls`, `output_schema`
(with `jsonschema` installed), `max_turns`, `max_tool_calls`, and regex-style
`must_not`.

YAML cases need `pip install pyyaml`; `.json` cases need nothing.

Eval runs cost money and time. `bash scripts/verify.sh --fast` skips them for
quick local loops; CI always runs them.
