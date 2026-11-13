"""Capability lifecycle checks in `craft.py drift` (change 001 in the framework repo).

Each test builds a throwaway project — craft.py plus a docs/ tree — and runs
drift against it. Standard library only; run by `craft.py verify` in the
framework repository:

    python3 -m unittest discover -s framework/tests
"""

import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

CRAFT = Path(__file__).resolve().parents[1] / "craft.py"


def capability(status: str) -> str:
    return textwrap.dedent(f"""\
        ---
        capability: orders
        status: {status}
        owner: team
        last-verified: 2026-11-13
        ---

        # Capability: Orders

        ## Change log

        | [001](../changes/001-build-orders/change.md) | 2026-11-13 | Built |
        """)


def change(status: str) -> str:
    return textwrap.dedent(f"""\
        ---
        change: 001
        title: Build orders
        status: {status}
        track: full
        capabilities: [orders]
        created: 2026-11-12
        merged: 2026-11-12
        ---

        # Change 001

        | ID | Criterion |
        |---|---|
        | AC-1 | When an order is placed, the system shall store it. |
        """)


class DriftProject:
    """A minimal project in a temporary directory."""

    def __init__(self):
        self.root = Path(tempfile.mkdtemp())
        (self.root / "framework").mkdir()
        shutil.copy(CRAFT, self.root / "framework" / "craft.py")
        (self.root / "docs" / "capabilities").mkdir(parents=True)
        self.change_dir = self.root / "docs" / "changes" / "001-build-orders"
        self.change_dir.mkdir(parents=True)
        (self.change_dir / "tasks.md").write_text("- [x] T1 · AC-1\n", encoding="utf-8")
        (self.root / "tests").mkdir()
        (self.root / "tests" / "test_orders.py").write_text("# AC-1\n", encoding="utf-8")

    def write(self, rel: str, text: str) -> None:
        (self.root / rel).write_text(text, encoding="utf-8")

    def drift(self) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "-I", str(self.root / "framework" / "craft.py"), "drift"],
            cwd=self.root, capture_output=True, text=True, encoding="utf-8")

    def close(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)


class CapabilityLifecycleTest(unittest.TestCase):

    def setUp(self):
        self.project = DriftProject()
        self.addCleanup(self.project.close)

    def run_drift(self, cap_status: str, change_status: str = "merged"):
        self.project.write("docs/capabilities/orders.md", capability(cap_status))
        self.project.write("docs/changes/001-build-orders/change.md", change(change_status))
        return self.project.drift()

    def test_merged_change_leaves_capability_planned(self):
        """AC-1: a merged change whose capability is still planned fails drift."""
        r = self.run_drift("planned")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("still 'planned'", r.stdout)

    def test_planned_capability_before_merge_is_fine(self):
        """AC-1: while the change is not merged, planned is the expected state."""
        r = self.run_drift("planned", change_status="approved")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertNotIn("still 'planned'", r.stdout)

    def test_planned_folded_to_active_is_clean(self):
        """AC-2: once gate 6 sets the capability active, drift is clean."""
        r = self.run_drift("active")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("drift: clean", r.stdout)

    def test_planned_changes_list_is_not_a_change_log_entry(self):
        """AC-2: naming the change under Planned changes does not satisfy gate 6."""
        doc = capability("active").replace(
            "## Change log\n\n| [001](../changes/001-build-orders/change.md) | 2026-11-13 | Built |\n",
            "## Planned changes\n\n1. `001-build-orders`\n\n## Change log\n\n")
        self.project.write("docs/capabilities/orders.md", doc)
        self.project.write("docs/changes/001-build-orders/change.md", change("merged"))
        r = self.project.drift()
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("no change-log entry", r.stdout)

    def test_every_lifecycle_status_is_accepted(self):
        """AC-3: planned, active, deprecated and superseded-by are all valid."""
        for status in ("planned", "active", "deprecated", "superseded-by: billing"):
            with self.subTest(status=status):
                self.project.write("docs/capabilities/orders.md", capability(status))
                self.project.write("docs/changes/001-build-orders/change.md", change("draft"))
                r = self.project.drift()
                self.assertNotIn("unknown status", r.stdout)

    def test_unknown_status_warns(self):
        """AC-3: any other status value is reported."""
        for status in ("banana", "superseded-by:"):
            with self.subTest(status=status):
                self.project.write("docs/capabilities/orders.md", capability(status))
                self.project.write("docs/changes/001-build-orders/change.md", change("draft"))
                r = self.project.drift()
                self.assertIn("unknown status", r.stdout)

    def test_template_comments_are_not_part_of_the_value(self):
        """AC-4: `status: merged   # draft | ...` from a template reads as merged."""
        r = self.run_drift("planned   # planned | active | deprecated",
                           change_status="merged   # draft | approved | merged")
        self.assertIn("still 'planned'", r.stdout)
        self.assertNotIn("unknown status", r.stdout)

    def test_quoted_values_keep_their_hash(self):
        """AC-4: a quoted value is not truncated at '#'."""
        self.project.write("docs/capabilities/orders.md", capability("active"))
        self.project.write("docs/changes/001-build-orders/change.md",
                           change("merged").replace("title: Build orders",
                                                    'title: "Fix #12 in orders"'))
        r = subprocess.run(
            [sys.executable, "-I", str(self.project.root / "framework" / "craft.py"),
             "index"], cwd=self.project.root, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        index = (self.project.root / "docs" / "changes" / "README.md").read_text(encoding="utf-8")
        self.assertIn("Fix #12 in orders", index)


class ProjectStartSkillTest(unittest.TestCase):

    def test_skill_ships_with_its_stack_reference(self):
        """AC-5: project-start exists, is named correctly and links stacks.md."""
        skill = CRAFT.parent / "skills" / "project-start"
        text = (skill / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\nname: project-start\n"))
        self.assertIn("(stacks.md)", text)
        self.assertTrue((skill / "stacks.md").is_file())


if __name__ == "__main__":
    unittest.main()
