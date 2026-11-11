#!/usr/bin/env python3
"""Eval runner — PROJECT-OWNED. This file is yours; rewrite it freely.

Shipped as a working skeleton because a generic runner cannot know how to call
your system. Two functions below are marked TODO; until you implement
`call_system`, every case fails loudly rather than passing silently.

    python3 evals/run.py                 # all cases
    python3 evals/run.py --tag guardrail # only cases with that tag
    python3 evals/run.py --case AC-3     # one case by id substring

Called by `scripts/project/verify-impl.sh` → `project_evals`.

Cases are YAML (see framework/templates/eval-case.yaml). YAML needs PyYAML:
    pip install pyyaml
A case may also be written as .json, which needs nothing.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

EVALS = Path(__file__).resolve().parent
ROOT = EVALS.parent


# ===========================================================================
# TODO 1 — call your system. This is the only part that must exist.
# ===========================================================================

def call_system(request: dict, setup: dict) -> dict:
    """Run one eval case against the system under test.

    Evals cover anything a model decides — not only chatbots. A classifier,
    an extraction endpoint, a RAG answer and a tool-calling agent all qualify.
    So a case comes in one of two shapes, and `request` carries whichever the
    case used:

        {"turns":  [{"user": "..."}, ...]}   a conversation, multi-turn
        {"input":  <str or dict>}            a single shot: one payload in,
                                             one response out

    `setup` is the case's `setup` block — fixtures, locale, whatever context
    the run needs.

    Return:
        {
          "text":       "the final response, as a string",
          "tool_calls": [{"name": "cancel_order", "args": {...}}, ...],
          "turns":      <number of assistant turns taken>,   # optional
        }

    For a classifier or extractor, put the structured result in "text" as
    JSON and assert against it with `output_schema`.

    Typical wiring:
      - HTTP:    POST the input (or each turn) to a locally running service
      - in-proc: import the handler and call it directly — fastest, no server
      - CLI:     subprocess your binary with the input on stdin
    """
    raise NotImplementedError(
        "Implement call_system() in evals/run.py so evals can run against "
        "your system. See the docstring above for the expected shapes."
    )


# ===========================================================================
# TODO 2 — semantic assertions, only if you use them.
# ===========================================================================

def judge(claim: str, response_text: str) -> bool:
    """Decide whether a natural-language claim holds for a response.

    Used by `contains_information` and `must_not`, which cannot be checked
    mechanically. Implement with whatever model you already depend on, asking
    for a strict yes/no.

    Leave it unimplemented and those assertions are reported as UNJUDGED —
    counted and printed, never silently passed.
    """
    raise NotImplementedError


# ===========================================================================
# Everything below is generic. Change it if it does not fit.
# ===========================================================================

def load_case(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        return json.loads(text)
    try:
        import yaml  # type: ignore
    except ImportError:
        raise SystemExit(
            f"{path.name} is YAML and PyYAML is not installed.\n"
            "  pip install pyyaml      (or write cases as .json)"
        )
    return yaml.safe_load(text) or {}


def discover(args) -> list:
    cases = []
    for path in sorted(EVALS.rglob("*")):
        if path.suffix not in {".yaml", ".yml", ".json"}:
            continue
        if path.name in {"defaults.yaml", "defaults.yml"}:
            continue
        case = load_case(path)
        case["_path"] = path.relative_to(ROOT).as_posix()
        if args.tag and args.tag not in (case.get("tags") or []):
            continue
        if args.case and args.case not in str(case.get("id", "")):
            continue
        cases.append(case)
    return cases


def load_defaults() -> dict:
    for name in ("defaults.yaml", "defaults.yml"):
        p = EVALS / name
        if p.is_file():
            return load_case(p)
    return {}


class Result:
    def __init__(self, case):
        self.case, self.failures, self.unjudged = case, [], []

    @property
    def passed(self) -> bool:
        return not self.failures


def check_tool_calls(expect: dict, got: dict, res: Result) -> None:
    wanted = expect.get("tool_calls") or []
    actual = got.get("tool_calls") or []
    names = [c.get("name") for c in actual]
    for w in wanted:
        name = w.get("name")
        if name not in names:
            res.failures.append(f"expected tool call `{name}`, got {names or 'none'}")
            continue
        want_args = w.get("with") or {}
        if not want_args:
            continue
        match = next((c for c in actual if c.get("name") == name), {})
        for k, v in want_args.items():
            got_v = (match.get("args") or {}).get(k)
            if str(got_v) != str(v):
                res.failures.append(f"`{name}` arg {k}: expected {v!r}, got {got_v!r}")


def check_schema(expect: dict, got: dict, res: Result) -> None:
    rel = expect.get("output_schema")
    if not rel:
        return
    schema_path = ROOT / rel
    if not schema_path.is_file():
        res.failures.append(f"schema not found: {rel}")
        return
    try:
        import jsonschema  # type: ignore
    except ImportError:
        res.unjudged.append(f"output_schema {rel} (pip install jsonschema)")
        return
    try:
        payload = json.loads(got.get("text") or "")
    except json.JSONDecodeError:
        res.failures.append("output is not valid JSON but a schema was declared")
        return
    try:
        jsonschema.validate(payload, json.loads(schema_path.read_text()))
    except Exception as e:  # noqa: BLE001 - surface whatever the validator says
        res.failures.append(f"schema: {str(e).splitlines()[0]}")


def check_limits(expect: dict, got: dict, res: Result) -> None:
    for key, actual in (("max_turns", got.get("turns")),
                        ("max_tool_calls", len(got.get("tool_calls") or []))):
        limit = expect.get(key)
        if limit is not None and actual is not None and actual > limit:
            res.failures.append(f"{key}: {actual} exceeds {limit}")


def check_semantic(expect: dict, got: dict, res: Result) -> None:
    text = got.get("text") or ""
    for claim in expect.get("contains_information") or []:
        try:
            if not judge(claim, text):
                res.failures.append(f"missing information: {claim}")
        except NotImplementedError:
            res.unjudged.append(f"contains_information: {claim}")
    for claim in expect.get("must_not") or []:
        # A plain string is treated as a regex when it looks like one.
        if any(ch in claim for ch in "\\^$[]()"):
            if re.search(claim, text):
                res.failures.append(f"must_not matched: {claim}")
            continue
        try:
            if judge(claim, text):
                res.failures.append(f"must_not violated: {claim}")
        except NotImplementedError:
            res.unjudged.append(f"must_not: {claim}")


def run_case(case: dict, defaults: dict) -> Result:
    res = Result(case)
    expect = dict(case.get("expect") or {})
    for key in ("must_not", "contains_information"):
        merged = (defaults.get(key) or []) + (expect.get(key) or [])
        if merged:
            expect[key] = merged
    for key, value in (defaults.get("limits") or {}).items():
        expect.setdefault(key, value)

    # A case is either conversational (`turns`) or single-shot (`input`).
    # Pass through whichever it used rather than forcing one into the other.
    if "input" in case:
        request = {"input": case["input"]}
    elif "turns" in case:
        request = {"turns": case["turns"]}
    else:
        res.failures.append("case has neither `turns` nor `input`")
        return res

    try:
        got = call_system(request, case.get("setup") or {})
    except NotImplementedError as e:
        res.failures.append(str(e).splitlines()[0])
        return res
    except Exception as e:  # noqa: BLE001 - a crash is a failed case
        res.failures.append(f"{type(e).__name__}: {e}")
        return res

    check_tool_calls(expect, got, res)
    check_schema(expect, got, res)
    check_limits(expect, got, res)
    check_semantic(expect, got, res)
    return res


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tag", help="only cases carrying this tag")
    ap.add_argument("--case", help="only cases whose id contains this")
    args = ap.parse_args()

    cases = discover(args)
    if not cases:
        print("  no eval cases found")
        return 0

    defaults = load_defaults()
    results = [run_case(c, defaults) for c in cases]

    failed = [r for r in results if not r.passed]
    unjudged = [r for r in results if r.unjudged]

    for r in results:
        cid = r.case.get("id") or r.case["_path"]
        if r.passed and not r.unjudged:
            print(f"    ✓ {cid}")
        elif r.passed:
            print(f"    ? {cid}")
        else:
            print(f"    ✗ {cid}")
        for f in r.failures:
            print(f"        {f}")
        for u in r.unjudged:
            print(f"        unjudged: {u}")

    print(f"\n  {len(results) - len(failed)}/{len(results)} passed", end="")
    if unjudged:
        n = sum(len(r.unjudged) for r in unjudged)
        print(f", {n} assertion(s) unjudged — implement judge() in evals/run.py")
    else:
        print()

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
