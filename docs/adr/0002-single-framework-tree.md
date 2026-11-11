---
adr: 0002
title: Keep framework-owned files in a single top-level tree
status: accepted
date: 2026-11-11
deciders: [framework]
related-change: ""
---

# 0002 — Keep framework-owned files in a single top-level tree

## Context

The framework is reused across client projects and upgraded independently of
them. That only works if it is unambiguous which files belong to the framework
and which belong to the project.

In version 0.1.0 framework-owned files were scattered across five locations
(`docs/framework/`, `.agents/skills/`, three files in `scripts/`, two in
`.github/`, and two at the root), and three of them contained project content:
the constitution held project amendments, `verify.sh` held the project's build
commands, and the CI workflow held its toolchain. An upgrade was therefore a
three-way merge, and after a few months nobody would remember which lines were
local.

## Options considered

### Option A — Move `capabilities/`, `changes/` and `adr/` under `docs/project/`

- **Pros:** Makes the `docs/` tree unambiguous. Small diff.
- **Cons:** Leaves `.agents/` and `scripts/` just as unclear, so ownership is
  still only partly structural. Deepens the three most-navigated directories
  in the repository, against the shallow-nesting rule that exists for Windows
  path limits. Files work product under "project context", which are different
  kinds of thing.

### Option B — Keep the layout, add a manifest of framework-owned paths

- **Pros:** Smallest diff. Ownership becomes checkable rather than merely
  conventional, and checksums catch a framework file edited in good faith.
- **Cons:** Ownership remains invisible in the tree, so a newcomer must consult
  the manifest to know what is safe to edit. Upgrade stays a multi-path
  operation.

### Option C — One top-level `framework/` tree; everything else project-owned

- **Pros:** One rule with no exceptions. Upgrade is a directory replacement.
  Daily paths get shallower, not deeper. Fixes the `.agents/` and `scripts/`
  ambiguity as well. The manifest from option B becomes near-trivial.
- **Cons:** Largest one-time diff. Process documentation leaves `docs/`, which
  is mildly unintuitive for humans looking for it.

## Decision

We will adopt **option C**: all framework-owned files live under `framework/`,
and everything outside it is project-owned.

Because ownership expressed in the tree needs no documentation to be understood,
and because upgrades become a replacement instead of a merge — which was the
actual problem.

Where the framework needs project-specific input it reads a project-owned file
rather than containing the content: `docs/amendments.md`,
`scripts/project/verify-impl.sh`, `.github/actions/setup/action.yml`.

The manifest and checksum check from option B are adopted as well, because
structure prevents accidents but does not detect them. `verify` warns when a
framework-owned file has been modified locally and names the project-owned file
the content belonged in.

`scripts/verify.sh` stays as a thin shim so that the command in `AGENTS.md`,
CI, the skills and any git hook never has to change.

The directory is `framework/` rather than `.craft/`: dot-prefixing matches the
convention for tooling directories, but the working guide is read by people, and
hiding it from `ls` is the wrong trade.

## Consequences

### Easier

- Upgrading: replace one directory, and `git diff` shows only framework files
- Explaining ownership to a collaborator: one sentence
- Reviewing an upgrade: nothing of the project's appears in the diff
- Navigating the directories used daily, which are now one level shallower

### Harder

- A one-time migration for any project already on 0.1.0
- Process documentation is no longer under `docs/`, so `AGENTS.md` and the
  root README must point at it clearly

### Committed to

- `framework/` as the only framework-owned path
- Every framework need for project input being expressed as a reference to a
  project-owned file, never as content inside a framework file
- Generating the PR template and CI workflow, since they carry framework
  content but must live at fixed paths outside `framework/`

## Revisit if

- A project needs to fork a framework file permanently, which would suggest the
  framework is missing an extension point
- The number of generated adapter files grows enough that `sync-adapters.sh`
  becomes the thing people fight with
- Tooling appears that makes a dependency-style framework distribution
  (installed as a package rather than copied into the repo) practical
