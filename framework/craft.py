#!/usr/bin/env python3
"""craft — the framework's command line.

FRAMEWORK-OWNED — do not edit. Replaced wholesale on upgrade.
Project-specific commands belong in scripts/project/verify-impl.sh.

    python3 framework/craft.py <command>

Commands
    verify      [--fast]        the gate: lint, tests, evals, indexes, drift, integrity
    preflight                   check that the tools this framework needs are present
    context                     am I in the framework repo or a project?
    feedback    [note] [--kind] record a finding about the framework itself
    drift       [--warn-only]   structural checks of docs against work
    index       [--check]       rebuild the capability / change / ADR index tables
    sync        [--check]       write the per-tool agent adapters and CI files
    upgrade <path> [--dry-run]  replace framework/ from another checkout

Maintainer commands — only in the framework repo; they refuse to run in a
project, because each would do damage there
    init        [--dry-run]     turn a clone of the framework into a project
    release                     regenerate everything in order, then verify
    gates       [--check]       regenerate gate summaries from definition-of-done.md
    manifest                    regenerate framework/MANIFEST.sha256

Everyone runs `bash scripts/verify.sh`, which is a shim onto `verify` here.
Standard library only, so there is nothing to install beyond Python itself.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

MIN_PYTHON = (3, 8)

REPO = Path(__file__).resolve().parent.parent
FRAMEWORK = REPO / "framework"
DOCS = REPO / "docs"

# The framework's own repository is marked by a root file. It sits outside
# framework/ deliberately: `upgrade` copies only framework/, so the marker can
# never be carried into a project.
MARKER = REPO / ".craft-framework-repo"
IS_FRAMEWORK_REPO = MARKER.exists()

# ---------------------------------------------------------------------------
# output
# ---------------------------------------------------------------------------

# Output uses ✓/✗ and similar. On Windows a piped stdout (CI, git hooks)
# defaults to the ANSI code page, which cannot encode them and raises
# UnicodeEncodeError. Force UTF-8 here, and pass it to child Python processes.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

_COLOR = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _COLOR else text


class Report:
    """Collects pass/fail across a run so verify can summarise honestly."""

    def __init__(self) -> None:
        self.failed = False
        self.warnings: list[str] = []

    def say(self, text: str) -> None:
        print("\n" + _c("1", f"==> {text}"))

    def ok(self, text: str) -> None:
        print(f"    {_c('32', '✓')} {text}")

    def bad(self, text: str) -> None:
        print(f"    {_c('31', '✗')} {text}")
        self.failed = True

    def warn(self, text: str) -> None:
        print(f"    {_c('33', '!')} {text}")
        self.warnings.append(text)

    def skip(self, text: str) -> None:
        print(f"    {_c('33', '–')} {text} (skipped)")

    def note(self, text: str) -> None:
        print(f"    {_c('2', text)}")


# ---------------------------------------------------------------------------
# shared helpers
# ---------------------------------------------------------------------------

def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def frontmatter(text: str) -> dict:
    """Parse a flat YAML frontmatter block. Deliberately minimal — no deps."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    out = {}
    for line in text[3:end].splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, _, value = line.partition(":")
        value = value.strip()
        # As in YAML, " #" starts a comment in an unquoted value. The templates
        # rely on this: `status: draft   # draft | approved | ...`.
        if value[:1] not in {'"', "'"} and " #" in value:
            value = value.split(" #", 1)[0].rstrip()
        out[key.strip()] = value.strip('"').strip("'")
    return out


def parse_list(value: str) -> list:
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        value = value[1:-1]
    return [v.strip().strip('"').strip("'") for v in value.split(",") if v.strip()]


def parse_date(value: str):
    try:
        return dt.date.fromisoformat(value.strip())
    except (ValueError, AttributeError):
        return None


def esc(value: str) -> str:
    """Keep a value from breaking a markdown table."""
    return (value or "").replace("|", "\\|").strip() or "—"


def have(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def find_bash() -> str | None:
    """A bash that can run our scripts, or None.

    On Windows a bare "bash" resolves to C:\\Windows\\System32\\bash.exe, the WSL
    launcher, which fails when no Linux distribution is installed (as on
    GitHub's Windows runners). Skip it and use Git Bash instead.
    """
    if os.name != "nt":
        return shutil.which("bash")
    sysroot = os.path.normcase(os.environ.get("SystemRoot", r"C:\Windows"))

    def usable(path: str) -> bool:
        p = os.path.normcase(os.path.abspath(path))
        return (os.path.isfile(p) and not p.startswith(sysroot)
                and "windowsapps" not in p)

    for d in os.environ.get("PATH", "").split(os.pathsep):
        candidate = os.path.join(d.strip('"'), "bash.exe")
        if d and usable(candidate):
            return candidate
    git = shutil.which("git")
    if git:
        # Git for Windows: <root>\cmd\git.exe or <root>\mingw64\bin\git.exe
        for root in list(Path(git).resolve().parents)[1:3]:
            for rel in ("bin/bash.exe", "usr/bin/bash.exe"):
                if usable(str(root / rel)):
                    return str(root / rel)
    return None


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def version() -> str:
    return read(FRAMEWORK / "VERSION").strip() or "?"


BEGIN = "<!-- BEGIN GENERATED: {} -->"
END = "<!-- END GENERATED -->"


def splice(path: Path, begin: str, block: str, required: bool):
    """Replace the marked region of a file. Returns (changed, new_text)."""
    text = read(path)
    pattern = re.compile(re.escape(begin) + r".*?" + re.escape(END), re.S)
    if pattern.search(text):
        new = pattern.sub(lambda _: block, text)
    elif required:
        raise SystemExit(f"{path.relative_to(REPO)}: missing marker\n  {begin}\n  {END}")
    else:
        sep = "" if text.endswith("\n\n") or not text else "\n"
        new = f"{text}{sep}\n{block}\n"
    return new != text, new


# ---------------------------------------------------------------------------
# which repository is this?
# ---------------------------------------------------------------------------

def require_framework_repo(command: str) -> None:
    """Maintainer commands do real damage in a project. Refuse politely."""
    if IS_FRAMEWORK_REPO:
        return
    harm = {
        "manifest": ("Running it here would record your local edits to framework/ as\n"
                     "  official, permanently disabling the integrity check."),
        "gates": ("It rewrites framework-owned documents, which an upgrade would\n"
                  "  then discard."),
        "release": "Releases are cut in the framework repository.",
        "init": ("This repository is already a project — there is no\n"
                 "  .craft-framework-repo marker to remove."),
    }.get(command, "It only applies to the framework's own repository.")

    print(_c("31", f"✗ `{command}` is a framework-maintainer command and this is a project."))
    print(f"  {harm}\n")
    print("  Project content belongs in:")
    print("    constitution rules ....... docs/amendments.md")
    print("    agent instructions ....... AGENTS.md")
    print("    build/test commands ...... scripts/project/verify-impl.sh")
    print("    CI toolchain ............. .github/actions/setup/action.yml\n")
    print("  To change the framework itself, do it in the framework repository")
    print("  and release a new version, then: craft.py upgrade <path>")
    raise SystemExit(1)


def cmd_context(args, rep: Report) -> int:
    if IS_FRAMEWORK_REPO:
        print("framework repository")
        print(f"  marker:   {MARKER.relative_to(REPO)}")
        print(f"  version:  {version()}")
        print("  framework/ is THE WORK here — edit it freely.")
        print("  Available: init, gates, manifest, release")
        print("  Read MAINTAINING.md before changing anything.")
    else:
        print("project using the framework")
        print(f"  framework version: {version()}")
        print("  framework/ is READ-ONLY — your edits are lost on upgrade.")
        print("  Not available: init, gates, manifest, release")
        print("  Read framework/agent-rules.md before starting a task.")
    return 0


# ---------------------------------------------------------------------------
# preflight
# ---------------------------------------------------------------------------

def cmd_preflight(args, rep: Report) -> int:
    rep.say("Preflight")

    # Python is self-evidently present — we are running. Check the version.
    v = sys.version_info
    if (v.major, v.minor) < MIN_PYTHON:
        rep.bad(f"python {v.major}.{v.minor} — this framework needs "
                f"{MIN_PYTHON[0]}.{MIN_PYTHON[1]} or newer")
    else:
        rep.ok(f"python {v.major}.{v.minor}.{v.micro}")

    # git: used for branching conventions and by upgrade. Not needed to verify.
    if have("git"):
        rep.ok("git")
    else:
        rep.warn("git not found — branch and upgrade workflows unavailable")

    # shellcheck: keeps the two remaining shell files portable.
    if have("shellcheck"):
        rep.ok("shellcheck")
    else:
        rep.warn("shellcheck not found — shell portability is unchecked here; "
                 "CI still checks it")

    # The project must wire its own build commands or verify proves nothing.
    impl = REPO / "scripts" / "project" / "verify-impl.sh"
    if not impl.is_file():
        rep.bad(f"missing {impl.relative_to(REPO)} — verify has no tests to run")
    else:
        body = read(impl)
        for fn in ("project_lint", "project_test", "project_evals"):
            if f"{fn}()" not in body:
                rep.warn(f"{fn} not defined in scripts/project/verify-impl.sh")
        # In the framework repo the placeholder wiring is correct — there is no
        # project to build. In a project it means verify proves nothing.
        if "no test command configured" in body and not IS_FRAMEWORK_REPO:
            rep.warn("verify-impl.sh still has its placeholder test wiring — "
                     "verify cannot prove anything until you edit it")

    if IS_FRAMEWORK_REPO:
        rep.note("framework repository — framework/ is editable here")

    return 1 if rep.failed else 0


# ---------------------------------------------------------------------------
# drift
# ---------------------------------------------------------------------------

CHANGES = DOCS / "changes"
CAPABILITIES = DOCS / "capabilities"
TEST_DIRS = ["src", "test", "tests", "evals", "app", "lib"]
TEST_SUFFIXES = {".java", ".kt", ".py", ".js", ".ts", ".tsx", ".go", ".rb",
                 ".cs", ".rs", ".yaml", ".yml", ".feature"}
AC_RE = re.compile(r"\bAC-\d+\b")
CAPABILITY_STATUSES = ("planned", "active", "deprecated", "superseded-by: <name>")
OPEN_Q_RE = re.compile(r"OPEN QUESTION:", re.IGNORECASE)


def _test_references() -> set:
    """Every AC id mentioned anywhere in test or eval source."""
    refs = set()
    folders = TEST_DIRS + (["framework/tests"] if IS_FRAMEWORK_REPO else [])
    for folder in folders:
        root = REPO / folder
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix in TEST_SUFFIXES:
                refs.update(AC_RE.findall(read(path)))
    return refs


def _check_change(folder: Path, test_refs: set, errors: list, warns: list) -> None:
    change_md = folder / "change.md"
    if not change_md.is_file():
        warns.append(f"{folder.name}: no change.md")
        return

    text = read(change_md)
    meta = frontmatter(text)
    status = meta.get("status", "draft")
    track = meta.get("track", "full")
    if status in {"draft", "abandoned"}:
        return

    if OPEN_Q_RE.search(text):
        errors.append(f"{folder.name}: status '{status}' but unresolved OPEN QUESTION remains")

    body = text.split("\n---", 1)[-1] if text.startswith("---") else text
    acs = sorted(set(AC_RE.findall(body)), key=lambda s: int(s.split("-")[1]))
    if not acs and track == "full":
        warns.append(f"{folder.name}: no acceptance criteria found")

    tasks_md = folder / "tasks.md"
    if tasks_md.is_file():
        task_refs = set(AC_RE.findall(read(tasks_md)))
        for ac in acs:
            if ac not in task_refs:
                errors.append(f"{folder.name}: {ac} is not covered by any task")
    elif status in {"in-progress", "merged"}:
        errors.append(f"{folder.name}: status '{status}' but no tasks.md")

    for ac in acs:
        if ac not in test_refs:
            (errors if status == "merged" else warns).append(
                f"{folder.name}: {ac} is not referenced by any test or eval")

    caps = parse_list(meta.get("capabilities", ""))
    if status == "merged" and not caps:
        warns.append(f"{folder.name}: merged with no capabilities listed")
    merged_on = parse_date(meta.get("merged", ""))

    for cap in caps:
        cap_file = CAPABILITIES / f"{cap}.md"
        if not cap_file.is_file():
            errors.append(f"{folder.name}: capability '{cap}' has no document "
                          f"at docs/capabilities/{cap}.md")
            continue
        if status != "merged":
            continue

        cap_text = read(cap_file)
        if frontmatter(cap_text).get("status") == "planned":
            errors.append(f"capability '{cap}': still 'planned' after merged change "
                          f"{folder.name} — gate 6 sets it to 'active' and writes "
                          f"its current behaviour")
        change_id = meta.get("change", folder.name.split("-")[0])
        # Only the Change log counts: "Planned changes" names the same folder
        # before the work is done.
        log = cap_text.split("## Change log", 1)[-1]
        if (folder.name not in log and f"| {change_id} " not in log
                and f"[{change_id}]" not in log):
            errors.append(f"capability '{cap}': no change-log entry for merged "
                          f"change {folder.name} (gate 6 skipped?)")

        verified = parse_date(frontmatter(cap_text).get("last-verified", ""))
        if merged_on and verified and verified < merged_on:
            errors.append(f"capability '{cap}': last-verified {verified} predates "
                          f"merged change {folder.name} ({merged_on})")


def _valid_capability_status(status: str) -> bool:
    if status.startswith("superseded-by:"):
        return bool(status.partition(":")[2].strip())
    return status in CAPABILITY_STATUSES


def _check_capability_statuses(warns: list) -> None:
    for path in sorted(CAPABILITIES.glob("*.md")) if CAPABILITIES.is_dir() else []:
        if path.name == "README.md":
            continue
        status = frontmatter(read(path)).get("status", "")
        if not _valid_capability_status(status):
            warns.append(f"capability '{path.stem}': unknown status '{status}' — "
                         f"use one of: {', '.join(CAPABILITY_STATUSES)}")


def cmd_drift(args, rep: Report) -> int:
    if not CHANGES.is_dir():
        print("  drift: docs/changes/ not found — nothing to check")
        return 0

    errors: list = []
    warns: list = []
    test_refs = _test_references()
    folders = sorted(p for p in CHANGES.iterdir() if p.is_dir())
    for folder in folders:
        _check_change(folder, test_refs, errors, warns)
    _check_capability_statuses(warns)

    for msg in warns:
        print(f"  warn:  {msg}")
    for msg in errors:
        print(f"  ERROR: {msg}")

    if not errors and not warns:
        print(f"  drift: clean ({len(folders)} change(s) checked)")
        return 0

    print(f"\n  drift: {len(errors)} error(s), {len(warns)} warning(s)")
    if errors and not getattr(args, "warn_only", False):
        print("  Fix these, or explain in review why each is acceptable.")
        return 1
    return 0


# ---------------------------------------------------------------------------
# index
# ---------------------------------------------------------------------------

INDEX_NOTE = ("*Generated by `python3 framework/craft.py index`. "
              "Run it, or `bash scripts/verify.sh`, after adding files.*")


def _build_capabilities() -> str:
    rows = []
    for path in sorted(CAPABILITIES.glob("*.md")):
        if path.name == "README.md":
            continue
        meta = frontmatter(read(path))
        rows.append(f"| [{esc(meta.get('capability', path.stem))}]({path.name}) "
                    f"| {esc(meta.get('status', '?'))} "
                    f"| {esc(meta.get('owner', ''))} "
                    f"| {esc(meta.get('last-verified', ''))} |")
    if not rows:
        return ("*No capability documents yet. The first change that touches an "
                "area creates one.*")
    return "\n".join(["| Capability | Status | Owner | Last verified |",
                      "|---|---|---|---|", *rows])


def _build_changes() -> str:
    rows = []
    for sub in sorted(CHANGES.iterdir(), reverse=True) if CHANGES.is_dir() else []:
        if not sub.is_dir() or not (sub / "change.md").is_file():
            continue
        meta = frontmatter(read(sub / "change.md"))
        caps = ", ".join(f"`{c}`" for c in parse_list(meta.get("capabilities", ""))) or "—"
        rows.append(f"| [{esc(meta.get('change', sub.name.split('-')[0]))}]({sub.name}/change.md) "
                    f"| {esc(meta.get('title', sub.name))} "
                    f"| {esc(meta.get('status', '?'))} "
                    f"| {esc(meta.get('track', ''))} "
                    f"| {caps} "
                    f"| {esc(meta.get('merged', ''))} |")
    if not rows:
        return "*No changes yet.*"
    return "\n".join(["| # | Title | Status | Track | Capabilities | Merged |",
                      "|---|---|---|---|---|---|", *rows])


def _build_adrs() -> str:
    rows = []
    for path in sorted((DOCS / "adr").glob("*.md")) if (DOCS / "adr").is_dir() else []:
        if path.name == "README.md":
            continue
        meta = frontmatter(read(path))
        rows.append(f"| [{esc(meta.get('adr', path.stem.split('-')[0]))}]({path.name}) "
                    f"| {esc(meta.get('title', path.stem))} "
                    f"| {esc(meta.get('status', '?'))} "
                    f"| {esc(meta.get('date', ''))} |")
    if not rows:
        return "*No decisions recorded yet.*"
    return "\n".join(["| # | Decision | Status | Date |", "|---|---|---|---|", *rows])


INDEX_TARGETS = [
    (CAPABILITIES / "README.md", "capabilities", _build_capabilities),
    (CHANGES / "README.md", "changes", _build_changes),
    (DOCS / "adr" / "README.md", "adr", _build_adrs),
]


def cmd_index(args, rep: Report) -> int:
    stale = []
    for path, key, build in INDEX_TARGETS:
        if not path.parent.is_dir():
            continue
        if not path.exists() and not args.check:
            path.write_text(f"# {path.parent.name.title()}\n\n", encoding="utf-8")

        begin = BEGIN.format(key + " — do not edit by hand")
        block = f"{begin}\n\n{build()}\n\n{INDEX_NOTE}\n\n{END}"
        changed, new = splice(path, begin, block, required=False)
        if not changed:
            continue
        if args.check:
            stale.append(path.relative_to(REPO))
        else:
            path.write_text(new, encoding="utf-8")
            print(f"  updated {path.relative_to(REPO)}")

    if args.check and stale:
        for p in stale:
            print(f"  stale: {p}")
        print("  run: python3 framework/craft.py index")
        return 1
    if not args.check and not stale:
        print("  indexes up to date")
    return 0


# ---------------------------------------------------------------------------
# gates  (maintainer)
# ---------------------------------------------------------------------------

DOD = FRAMEWORK / "definition-of-done.md"
GATE_HEADING = re.compile(r"^## Gate (\d+) — (.+?)\s*$", re.M)
GATE_META = re.compile(r'<!--\s*gate\s+passes="([^"]*)"\s+by="([^"]*)"\s+step="([^"]*)"\s*-->')
GATE_NOTE = ("*Generated from [definition-of-done.md](definition-of-done.md), "
             "the single source of truth for the gate model.*")


class Gate:
    def __init__(self, num, title, passes, by, step):
        self.num, self.title = int(num), title
        self.passes, self.by, self.step = passes, by, step


def _parse_gates() -> list:
    text = read(DOD)
    matches = list(GATE_HEADING.finditer(text))
    gates = []
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        meta = GATE_META.search(text[m.end():end])
        if not meta:
            raise SystemExit(f"definition-of-done.md: Gate {m.group(1)} has no "
                             f"'<!-- gate passes=... by=... step=... -->' line")
        gates.append(Gate(m.group(1), m.group(2), *meta.groups()))

    if not gates:
        raise SystemExit("definition-of-done.md: no '## Gate N — Title' headings found")
    expected = list(range(len(gates)))
    if [g.num for g in gates] != expected:
        raise SystemExit(f"definition-of-done.md: gates are {[g.num for g in gates]}, "
                         f"expected {expected} — numbering must be contiguous from 0")
    return gates


def _gates_full(gates) -> str:
    rows = [f"| **{g.num}** {g.step} | {g.title} | {g.passes} | {g.by} |" for g in gates]
    return "\n".join(["| Gate | Means | Passes when | Passed by |",
                      "|---|---|---|---|", *rows])


def _gates_steps(gates) -> str:
    arrow = " → ".join(g.step.lower() for g in gates)
    rows = [f"| {g.step} | Gate {g.num} — {g.title} | {g.by} |" for g in gates]
    return "\n".join(["```", f" {arrow}", "```", "",
                      "| Step | Ends at | Passed by |", "|---|---|---|", *rows])


def _gates_names(gates) -> str:
    return "\n".join(f"- **Gate {g.num}** — {g.title}" for g in gates)


GATE_TARGETS = [
    (FRAMEWORK / "working-guide.md", "gates-steps", _gates_steps),
    (FRAMEWORK / "user-guide.md", "gates-full", _gates_full),
    (FRAMEWORK / "workflows.md", "gates-names", _gates_names),
]


def cmd_gates(args, rep: Report) -> int:
    if not args.check:
        require_framework_repo("gates")
    gates = _parse_gates()
    stale = []
    for path, key, render in GATE_TARGETS:
        begin = BEGIN.format(key + " — from definition-of-done.md, do not edit by hand")
        block = f"{begin}\n\n{render(gates)}\n\n{GATE_NOTE}\n\n{END}"
        changed, new = splice(path, begin, block, required=True)
        if not changed:
            continue
        if args.check:
            stale.append(path.relative_to(REPO))
        else:
            path.write_text(new, encoding="utf-8")
            print(f"  updated {path.relative_to(REPO)}")

    if args.check and stale:
        for p in stale:
            print(f"  stale: {p}")
        print("  run: python3 framework/craft.py gates")
        return 1
    print(f"  {len(gates)} gates, {len(GATE_TARGETS)} documents in sync")
    return 0


# ---------------------------------------------------------------------------
# sync  (agent adapters)
# ---------------------------------------------------------------------------

CURSOR_RULE = """---
description: Project working framework
alwaysApply: true
---

Follow the instructions in AGENTS.md at the repository root, and the process in
framework/working-guide.md. Do not duplicate rules here — AGENTS.md is
canonical.
"""

# Files are COPIED, never symlinked: symlinks need Developer Mode on Windows
# and break silently without it.
SYNC_TREES = [("framework/skills", ".claude/skills")]
SYNC_FILES = [
    ("framework/templates/pull-request.md", ".github/pull_request_template.md"),
    ("framework/templates/ci-verify.yml", ".github/workflows/verify.yml"),
]
SYNC_WRITES = [(".cursor/rules/framework.mdc", CURSOR_RULE)]


def _same_tree(a: Path, b: Path) -> bool:
    if not b.is_dir():
        return False
    ours = {p.relative_to(a): sha256(p) for p in a.rglob("*") if p.is_file()}
    theirs = {p.relative_to(b): sha256(p) for p in b.rglob("*") if p.is_file()}
    return ours == theirs


def cmd_sync(args, rep: Report) -> int:
    stale = []

    for src_s, dst_s in SYNC_TREES:
        src, dst = REPO / src_s, REPO / dst_s
        if not src.is_dir():
            continue
        if args.check:
            if not _same_tree(src, dst):
                stale.append(dst_s)
        else:
            if dst.exists():
                shutil.rmtree(dst)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(src, dst)
            print(f"  synced {dst_s}")

    for src_s, dst_s in SYNC_FILES:
        src, dst = REPO / src_s, REPO / dst_s
        if not src.is_file():
            continue
        if args.check:
            if not dst.is_file() or sha256(src) != sha256(dst):
                stale.append(dst_s)
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
            print(f"  synced {dst_s}")

    for dst_s, content in SYNC_WRITES:
        dst = REPO / dst_s
        if args.check:
            if not dst.is_file() or read(dst) != content:
                stale.append(dst_s)
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(content, encoding="utf-8")
            print(f"  wrote  {dst_s}")

    if (REPO / "mcp" / "servers.yaml").is_file() and not args.check:
        print("  note: mcp/servers.yaml present — generation not implemented yet")

    if args.check and stale:
        for s in stale:
            print(f"  stale: {s}")
        print("  run: python3 framework/craft.py sync")
        return 1
    if not args.check:
        print("  adapters written")
    return 0


# ---------------------------------------------------------------------------
# manifest / integrity
# ---------------------------------------------------------------------------

MANIFEST = FRAMEWORK / "MANIFEST.sha256"


# Never part of the framework, even when git cannot tell us so.
JUNK_NAMES = {".DS_Store", "Thumbs.db", "desktop.ini"}


def _ignored_files() -> set:
    """Files under framework/ that git ignores. A clone never has them, so
    listing them in the manifest makes every new project fail integrity."""
    r = subprocess.run(["git", "ls-files", "--others", "--ignored",
                        "--exclude-standard", "-z", "framework"],
                       cwd=REPO, capture_output=True, text=True) if have("git") else None
    if r is None or r.returncode != 0:
        return set()
    return {(REPO / rel).resolve() for rel in r.stdout.split("\0") if rel}


def _manifest_files() -> list:
    ignored = _ignored_files()
    files = [p for p in FRAMEWORK.rglob("*")
             if p.is_file()
             and p.name != "MANIFEST.sha256"
             and p.name not in JUNK_NAMES
             and "__pycache__" not in p.parts
             and p.resolve() not in ignored
             and "example" not in p.relative_to(FRAMEWORK).parts]
    shim = REPO / "scripts" / "verify.sh"
    if shim.is_file():
        files.append(shim)
    return sorted(files)


def _manifest_pairs():
    """(expected_hash, path) for every line in the manifest."""
    for line in read(MANIFEST).splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        expected, _, rel = line.partition("  ")
        yield expected, REPO / rel


def cmd_manifest(args, rep: Report) -> int:
    require_framework_repo("manifest")
    lines = ["# Framework-owned files and their checksums.",
             "# Generated by `python3 framework/craft.py manifest` at release time.",
             f"# framework/VERSION: {version()}"]
    files = _manifest_files()
    for p in files:
        lines.append(f"{sha256(p)}  {p.relative_to(REPO).as_posix()}")
    MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  wrote {MANIFEST.relative_to(REPO)} ({len(files)} files)")
    return 0


def cmd_integrity(args, rep: Report) -> int:
    if IS_FRAMEWORK_REPO:
        # Here the framework IS the work, so "modified" is the normal state.
        # What matters instead is that the manifest was regenerated before
        # committing — `release` does that, and this reminds you if it drifted.
        stale = any(p.is_file() and sha256(p) != h
                    for h, p in _manifest_pairs())
        if stale:
            rep.warn("manifest is out of date — run `craft.py release` "
                     "before committing, or downstream upgrades warn falsely")
        else:
            rep.ok("manifest matches (framework repo)")
        return 0

    if not MANIFEST.is_file():
        rep.skip(f"no manifest at {MANIFEST.relative_to(REPO)}")
        return 0

    modified, missing = [], []
    for line in read(MANIFEST).splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        expected, _, rel = line.partition("  ")
        path = REPO / rel
        if not path.is_file():
            missing.append(rel)
        elif sha256(path) != expected:
            modified.append(rel)

    if not modified and not missing:
        rep.ok("framework files unmodified")
        return 0

    for rel in missing:
        rep.bad(f"missing: {rel}")
    for rel in modified:
        rep.warn(f"modified locally: {rel}")

    print()
    print(_c("1", "    Framework-owned files have been changed."))
    print("    These edits will be LOST at the next framework upgrade.\n")
    print("    Project content belongs in:")
    print("      constitution rules ....... docs/amendments.md")
    print("      build/test commands ...... scripts/project/verify-impl.sh")
    print("      CI toolchain ............. .github/actions/setup/action.yml")
    print("      project context .......... docs/overview.md\n")
    print("    If the framework itself is wrong, change it in the framework repo")
    print("    and release a new version — that is how it improves.")
    return 0  # warns, never fails the build


# ---------------------------------------------------------------------------
# feedback
# ---------------------------------------------------------------------------

FEEDBACK = DOCS / "framework-feedback.md"


def cmd_feedback(args, rep: Report) -> int:
    """Record a finding about the framework, with zero friction.

    Capture now, triage at the retro, raise upstream what is general. Stopping
    mid-task to open an issue is why feedback never gets written down.
    """
    if not args.note:
        if not FEEDBACK.is_file():
            print(f"no {FEEDBACK.relative_to(REPO)} yet — it is created on first use")
            return 0
        text = read(FEEDBACK)
        entries = re.findall(r"^### .*$", text, re.M)
        print(f"{len(entries)} entry(ies) in {FEEDBACK.relative_to(REPO)}")
        for e in entries[:10]:
            print(f"  {e[4:]}")
        if entries:
            print("\nReview these at the retro. See the file for how to triage.")
        return 0

    if not FEEDBACK.is_file():
        template = FRAMEWORK / "templates" / "project" / "framework-feedback.md"
        FEEDBACK.parent.mkdir(parents=True, exist_ok=True)
        FEEDBACK.write_text(read(template) if template.is_file()
                            else "# Framework feedback\n\n## Log\n", encoding="utf-8")
        print(f"  created {FEEDBACK.relative_to(REPO)}")

    stamp = dt.date.today().isoformat()
    kind = f" · {args.kind}" if args.kind else ""
    entry = (f"### {stamp} · framework {version()}{kind}\n\n"
             f"{args.note.strip()}\n\n"
             f"*Triage: unreviewed*\n")

    text = read(FEEDBACK)
    marker = "## Log"
    if marker in text:
        head, _, tail = text.partition(marker)
        # Newest first, directly under the heading and its comment line.
        lines = tail.split("\n")
        insert_at = 1
        while insert_at < len(lines) and (not lines[insert_at].strip()
                                          or lines[insert_at].lstrip().startswith("<!--")):
            insert_at += 1
        tail = "\n".join(lines[:insert_at] + ["", entry] + lines[insert_at:])
        text = head + marker + tail
    else:
        text = text.rstrip() + f"\n\n## Log\n\n{entry}"

    FEEDBACK.write_text(text, encoding="utf-8")
    print(f"  recorded in {FEEDBACK.relative_to(REPO)}")
    print("  Review it at the retro; raise upstream whatever is true for every project.")
    return 0


# ---------------------------------------------------------------------------
# init  —  turn a clone of the framework into a project
# ---------------------------------------------------------------------------

PROJECT_TEMPLATE = FRAMEWORK / "templates" / "project"

# Removed because they belong to the framework, not to your project.
INIT_REMOVE = [".craft-framework-repo", "MAINTAINING.md",
                ".github/ISSUE_TEMPLATE/framework-finding.md"]

# Wiped and recreated from framework/templates/project/. These hold the
# framework's own capabilities, changes and decisions in the framework repo.
INIT_RESET_DIRS = ["docs/capabilities", "docs/changes", "docs/adr"]


ROOT_LEVEL_TEMPLATES = {"AGENTS.md"}
TOP_LEVEL_TEMPLATE_DIRS = {"evals"}


def _init_destination(rel: Path) -> Path:
    """Where a project-template file lands. Most go under docs/; AGENTS.md is
    root-level and evals/ keeps its own top-level folder."""
    if rel.as_posix() in ROOT_LEVEL_TEMPLATES:
        return REPO / rel.name
    if rel.parts[0] in TOP_LEVEL_TEMPLATE_DIRS:
        return REPO / rel
    return DOCS / rel


def _git(*argv: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *argv], cwd=REPO, capture_output=True, text=True)


def _framework_origin() -> str | None:
    """The URL of `origin` if it is a framework repository, else None.

    A fresh clone of the framework still pushes to it, so a project's first
    `git push` would land on the framework. A remote counts as the framework
    when one of its branches carries the framework-repo marker; a project's
    own remote (framework copied into an existing repository) never does.
    """
    if not have("git") or _git("rev-parse", "--git-dir").returncode != 0:
        return None
    url = _git("remote", "get-url", "origin")
    if url.returncode != 0:
        return None
    refs = _git("for-each-ref", "--format=%(refname)", "refs/remotes/origin")
    for ref in refs.stdout.split():
        if _git("cat-file", "-e", f"{ref}:{MARKER.name}").returncode == 0:
            return url.stdout.strip()
    return None


def cmd_init(args, rep: Report) -> int:
    require_framework_repo("init")
    if not PROJECT_TEMPLATE.is_dir():
        raise SystemExit(f"missing {PROJECT_TEMPLATE.relative_to(REPO)}")

    plan: list = []
    for rel in INIT_REMOVE:
        if (REPO / rel).exists():
            plan.append(("remove", rel))
    for rel in INIT_RESET_DIRS:
        d = REPO / rel
        if d.is_dir():
            kept = [p for p in d.rglob("*") if p.is_file()]
            if kept:
                plan.append(("reset", f"{rel}/  ({len(kept)} file(s) replaced "
                                      f"with the empty template)"))
    for src in sorted(PROJECT_TEMPLATE.rglob("*")):
        if src.is_file():
            rel = src.relative_to(PROJECT_TEMPLATE)
            plan.append(("install", _init_destination(rel).relative_to(REPO).as_posix()))

    origin = _framework_origin()
    if origin:
        plan.append(("unlink", f"git remote origin ({origin}) — it is the framework"))

    if args.dry_run:
        print("init would:")
        for action, what in plan:
            print(f"  {action:8} {what}")
        return 0

    for rel in INIT_REMOVE:
        p = REPO / rel
        if p.exists():
            p.unlink()
            print(f"  removed   {rel}")

    for rel in INIT_RESET_DIRS:
        d = REPO / rel
        if d.is_dir():
            shutil.rmtree(d)
        d.mkdir(parents=True, exist_ok=True)
    print(f"  cleared   {', '.join(INIT_RESET_DIRS)}  (those were the framework's own)")

    for src in sorted(PROJECT_TEMPLATE.rglob("*")):
        if not src.is_file():
            continue
        rel = src.relative_to(PROJECT_TEMPLATE)
        dst = _init_destination(rel)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        print(f"  installed {dst.relative_to(REPO)}")

    if origin:
        if _git("remote", "remove", "origin").returncode == 0:
            print(f"  unlinked  git remote origin ({origin})")
            print("            so a push cannot land on the framework repository")
            print(f"            (if that was your project's own repository: "
                  f"git remote add origin {origin})")
        else:
            print(_c("31", f"  ! could not remove git remote origin ({origin}) — "
                           "run: git remote remove origin"))

    cmd_index(argparse.Namespace(check=False), rep)
    cmd_sync(argparse.Namespace(check=False), rep)

    print(f"\n{_c('32', 'This is now a project')} using framework {version()}.\n")
    print("Next, ask your coding agent to run the setup skill:")
    print("  new project, no code yet ........ project-start  (an interview; give it")
    print("                                    a brief or pasted notes if you have them)")
    print("  existing codebase ............... project-adopt\n")
    print("Or edit the four files that are yours by hand:")
    print("  AGENTS.md                         two lines of project description")
    print("  docs/overview.md                  stack, how to run it, conventions")
    print("  scripts/project/verify-impl.sh    your lint and test commands")
    print("  .github/actions/setup/action.yml  your CI toolchain\n")
    print("Then:")
    print("  bash scripts/verify.sh")
    print("  git add -A && git commit -m 'initial'")
    if origin:
        print("  git remote add origin <your-project-repo-url>")
        print("  git push -u origin main")
    print()
    print("Humans: framework/user-guide.md.  Agents: framework/agent-rules.md.")
    return 0


# ---------------------------------------------------------------------------
# release  (maintainer)
# ---------------------------------------------------------------------------

def cmd_release(args, rep: Report) -> int:
    require_framework_repo("release")

    v = version()
    changelog = read(FRAMEWORK / "CHANGELOG.md")
    if f"## [{v}]" not in changelog:
        print(_c("31", f"✗ framework/VERSION is {v} but CHANGELOG.md has no "
                       f"'## [{v}]' entry."))
        print("  Add the entry, including migration notes if a path moved or a")
        print("  file was removed, then run this again.")
        return 1

    first = re.search(r"^## \[([^\]]+)\]", changelog, re.M)
    if first and first.group(1) != v:
        print(_c("31", f"✗ the newest CHANGELOG entry is [{first.group(1)}] but "
                       f"VERSION is {v}."))
        print("  The new version's entry must be at the top.")
        return 1

    print(f"releasing framework {v}\n")
    # Order matters: manifest checksums the output of everything before it.
    for label, fn, ns in [
        ("gates", cmd_gates, argparse.Namespace(check=False)),
        ("index", cmd_index, argparse.Namespace(check=False)),
        ("sync", cmd_sync, argparse.Namespace(check=False)),
        ("manifest", cmd_manifest, argparse.Namespace()),
    ]:
        print(_c("1", f"==> {label}"))
        if fn(ns, rep) != 0:
            print(_c("31", f"✗ {label} failed"))
            return 1

    print(_c("1", "\n==> verify"))
    sys.stdout.flush()
    bash = find_bash()
    if bash is None:
        print(_c("31", "\n✗ release blocked: bash not found (on Windows, install Git for Windows)"))
        return 1
    code = subprocess.run([bash, "scripts/verify.sh"], cwd=REPO).returncode
    if code != 0:
        print(_c("31", "\n✗ release blocked: verify failed"))
        return 1

    print(_c("32", f"\n✓ framework {v} is ready to commit"))
    print(f"  git commit -am 'framework v{v}: <summary>'")
    print(f"  git tag v{v} && git push --tags")
    print("\n  Before pushing a path change, test an upgrade into a real")
    print("  project — see MAINTAINING.md.")
    return 0


# ---------------------------------------------------------------------------
# upgrade
# ---------------------------------------------------------------------------

def cmd_upgrade(args, rep: Report) -> int:
    src = Path(args.source).expanduser().resolve()
    if not (src / "framework").is_dir():
        raise SystemExit(f"{src} does not contain a framework/ directory")

    to = read(src / "framework" / "VERSION").strip() or "?"
    print(f"framework {version()} -> {to}")

    if (REPO / ".git").exists() and have("git"):
        dirty = subprocess.run(["git", "status", "--porcelain"], cwd=REPO,
                               capture_output=True, text=True).stdout.strip()
        if dirty:
            print("warning: working tree is dirty — commit first so the upgrade "
                  "is reviewable")

    if args.dry_run:
        print("would replace: framework/ and scripts/verify.sh")
        return 0

    shutil.rmtree(FRAMEWORK)
    shutil.copytree(src / "framework", FRAMEWORK)
    shutil.copyfile(src / "scripts" / "verify.sh", REPO / "scripts" / "verify.sh")

    subprocess.run([sys.executable, "-I", str(FRAMEWORK / "craft.py"), "sync"],
                   cwd=REPO, check=False)

    print(f"\nupgraded to {to}. Next:")
    print("  1. read framework/CHANGELOG.md for migration notes")
    print("  2. bash scripts/verify.sh")
    print("  3. git diff — only framework/ and generated adapters should appear")
    return 0


# ---------------------------------------------------------------------------
# verify
# ---------------------------------------------------------------------------

# The project's build commands live in bash, because that is the natural
# language for shelling out to Maven, Gradle or npm. This preamble gives that
# file the helper API its header documents, then dispatches one function.
HOOK_HARNESS = r"""
set -uo pipefail
FAILED=0
ok()   { printf '    \033[32m✓\033[0m %s\n' "$1"; }
bad()  { printf '    \033[31m✗\033[0m %s\n' "$1"; FAILED=1; }
skip() { printf '    \033[33m–\033[0m %s (skipped)\n' "$1"; }
have() { command -v "$1" >/dev/null 2>&1; }
run()  { local label="$1"; shift; if "$@"; then ok "$label"; else bad "$label"; fi; }
. scripts/project/verify-impl.sh
if declare -F "$1" >/dev/null 2>&1; then "$1"; else exit 97; fi
exit $FAILED
"""


def _run_hook(name: str, rep: Report) -> None:
    impl = REPO / "scripts" / "project" / "verify-impl.sh"
    if not impl.is_file():
        rep.bad(f"missing {impl.relative_to(REPO)}")
        return
    bash = find_bash()
    if bash is None:
        rep.bad("bash not found — on Windows, install Git for Windows")
        return
    env = dict(os.environ, PY=sys.executable)
    # Our stdout is buffered; the subprocess writes straight to the terminal.
    # Without this flush its output lands above our own headings.
    sys.stdout.flush()
    result = subprocess.run([bash, "-c", HOOK_HARNESS, "harness", name],
                            cwd=REPO, env=env)
    if result.returncode == 97:
        rep.skip(f"{name} not defined in scripts/project/verify-impl.sh")
    elif result.returncode != 0:
        rep.failed = True


def cmd_verify(args, rep: Report) -> int:
    print(_c("1", "verify") + f"  framework {version()}  "
          f"({os.uname().sysname if hasattr(os, 'uname') else sys.platform})")

    if cmd_preflight(args, rep) != 0:
        print("\n" + _c("31", "✗ verify failed in preflight"))
        print("  Install what is missing, then run again.")
        return 1

    rep.say("Lint")
    _run_hook("project_lint", rep)
    shell_files = [str(p.relative_to(REPO)) for p in
                   [REPO / "scripts" / "verify.sh",
                    REPO / "scripts" / "project" / "verify-impl.sh"] if p.is_file()]
    if have("shellcheck") and shell_files:
        sys.stdout.flush()
        r = subprocess.run(["shellcheck", *shell_files], cwd=REPO)
        rep.ok("shellcheck") if r.returncode == 0 else rep.bad("shellcheck")

    rep.say("Tests")
    _run_hook("project_test", rep)

    if IS_FRAMEWORK_REPO and (FRAMEWORK / "tests").is_dir():
        rep.say("Framework tests")
        sys.stdout.flush()
        r = subprocess.run([sys.executable, "-I", "-m", "unittest", "discover",
                            "-s", str(FRAMEWORK / "tests"), "-t", str(FRAMEWORK / "tests"),
                            "-q"], cwd=REPO)
        rep.ok("framework tests") if r.returncode == 0 else rep.bad("framework tests")

    rep.say("Evals")
    cases = list((REPO / "evals").rglob("*.yaml")) if (REPO / "evals").is_dir() else []
    cases = [c for c in cases if c.name != "defaults.yaml"]
    if not cases:
        rep.skip("no eval cases")
    elif args.fast:
        rep.skip("--fast")
    else:
        _run_hook("project_evals", rep)

    rep.say("Generated indexes")
    code = cmd_index(argparse.Namespace(check=True), rep)
    rep.ok("indexes up to date") if code == 0 else rep.bad("indexes are stale")

    rep.say("Documentation drift")
    code = cmd_drift(argparse.Namespace(warn_only=False), rep)
    rep.ok("drift check") if code == 0 else rep.bad("drift check")

    if IS_FRAMEWORK_REPO:
        rep.say("Gate summaries")
        code = cmd_gates(argparse.Namespace(check=True), rep)
        rep.ok("gate summaries in sync") if code == 0 else rep.bad("gate summaries are stale")

    rep.say("Framework integrity")
    cmd_integrity(args, rep)

    rep.say("Agent adapters")
    code = cmd_sync(argparse.Namespace(check=True), rep)
    rep.ok("adapters up to date") if code == 0 else rep.bad("adapters out of date")

    print()
    if rep.failed:
        print(_c("31", "✗ verify failed"))
        print("  Do not disable or weaken a check to make this pass.")
        print("  See framework/constitution.md rule 4.")
        return 1

    tail = f" ({len(rep.warnings)} warning(s))" if rep.warnings else ""
    print(_c("32", f"✓ verify passed{tail}"))
    return 0


# ---------------------------------------------------------------------------
# entry point
# ---------------------------------------------------------------------------

def main() -> int:
    if sys.version_info < MIN_PYTHON:
        print(f"craft needs Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]} or newer; "
              f"this is {sys.version.split()[0]}")
        return 1

    parser = argparse.ArgumentParser(
        prog="craft", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("verify", help="the gate — run everything")
    p.add_argument("--fast", action="store_true", help="skip evals")
    p.set_defaults(fn=cmd_verify)

    sub.add_parser("preflight", help="check required tools").set_defaults(fn=cmd_preflight)

    p = sub.add_parser("drift", help="structural checks of docs against work")
    p.add_argument("--warn-only", action="store_true")
    p.set_defaults(fn=cmd_drift)

    p = sub.add_parser("index", help="rebuild the index tables")
    p.add_argument("--check", action="store_true")
    p.set_defaults(fn=cmd_index)

    p = sub.add_parser("sync", help="write the agent adapters and CI files")
    p.add_argument("--check", action="store_true")
    p.set_defaults(fn=cmd_sync)

    p = sub.add_parser("gates", help="[maintainer] regenerate gate summaries")
    p.add_argument("--check", action="store_true")
    p.set_defaults(fn=cmd_gates)

    sub.add_parser("manifest", help="[maintainer] regenerate MANIFEST.sha256") \
        .set_defaults(fn=cmd_manifest)

    sub.add_parser("release", help="[maintainer] regenerate everything and verify") \
        .set_defaults(fn=cmd_release)

    p = sub.add_parser("init", help="[maintainer] turn this clone into a project")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(fn=cmd_init)

    sub.add_parser("context", help="am I in the framework repo or a project?") \
        .set_defaults(fn=cmd_context)

    p = sub.add_parser("feedback", help="record a finding about the framework")
    p.add_argument("note", nargs="?", help="what went wrong; omit to list entries")
    p.add_argument("--kind", choices=["rule", "check", "skill", "docs", "gap",
                                      "ceremony", "deviation"],
                   help="category, to make retro triage quicker")
    p.set_defaults(fn=cmd_feedback)

    sub.add_parser("integrity", help="check framework files are unmodified") \
        .set_defaults(fn=cmd_integrity)

    p = sub.add_parser("upgrade", help="replace framework/ from another checkout")
    p.add_argument("source", help="path to a framework repo checkout")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(fn=cmd_upgrade)

    args = parser.parse_args()
    if not getattr(args, "fn", None):
        parser.print_help()
        return 2

    os.chdir(REPO)
    return args.fn(args, Report())


if __name__ == "__main__":
    sys.exit(main())
