import sys, os, tempfile, unittest
from decimal import Decimal
from pathlib import Path
from unittest import mock
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import fixture as fx
import mzclient
import tasks
import grade


class Registry(unittest.TestCase):
    def test_fourteen_tasks_with_prompts(self):
        self.assertEqual(len(tasks.TASKS), 14)
        f = fx.eval_fixture(1, 20)
        for t in tasks.TASKS:
            p = tasks.render_prompt(t, f, "run_x")
            self.assertIn(f"run_x.{t.view}", p)
            self.assertNotIn("{", p)
            rows = t.reference(f)
            self.assertTrue(all(len(r) == len(t.columns) for r in rows))

    def test_mutations_apply(self):
        f = fx.eval_fixture(1, 20)
        n = 0
        for t in tasks.TASKS:
            m = tasks.mutation_for(t, f)
            if m:
                n += 1
                g = fx.apply_mutation(f, m)
                self.assertNotEqual(t.reference(f), t.reference(g), t.id)
        self.assertEqual(n, 6)


class Compare(unittest.TestCase):
    def test_normalize_and_diff(self):
        exp = {("a", Decimal("1.5")), ("b", Decimal("2"))}
        got = [["a", "1.50"], ["b", "2"], ["c", "3"]]
        missing, extra = grade.diff(exp, got)
        self.assertEqual(missing, [])
        self.assertEqual(extra, [("c", Decimal("3"))])

    def test_null_cell(self):
        self.assertIsNone(grade.normalize_cell("\\N"))
        self.assertEqual(grade.normalize_cell("x"), "x")
        self.assertEqual(grade.normalize_cell("7"), Decimal("7"))


class TimeoutFallback(unittest.TestCase):
    """Grade one task against a stub whose full read always times out."""

    def grade_one(self, task, count):
        f = fx.eval_fixture(1, 20)

        def fake_run(sql, **kw):
            if "count(*)" in sql:
                return mzclient.Result(rc=0, rows=[[str(count)]])
            if f" FROM s.{task.view}" in sql:
                return mzclient.Result(rc=124, timed_out=True)
            return mzclient.Result(rc=0, rows=[])

        with mock.patch.object(grade.mzclient, "run", fake_run), \
                mock.patch.object(grade.T, "TASKS", [task]), \
                tempfile.TemporaryDirectory() as d:
            out = grade.grade("s", f, "c", Path(d))
            return out, (Path(d) / "worksheet.md").read_text()

    def test_count_only_when_the_full_read_times_out(self):
        """A result set too large to ship in the timeout is graded on its size."""
        t = next(x for x in tasks.TASKS if x.id == "t14")
        out, sheet = self.grade_one(t, len(t.reference(fx.eval_fixture(1, 20))))
        rec = out["tasks"]["t14"]
        self.assertTrue(rec["timed_out"])
        self.assertTrue(rec["initial_ok"])
        self.assertEqual(rec["partial"], "count-only")
        self.assertIn("| True (count-only) |", sheet)

    def test_skipped_mutation_is_recorded_and_counted(self):
        t = next(x for x in tasks.TASKS if x.id == "t13")
        out, sheet = self.grade_one(t, 0)
        self.assertEqual(out["tasks"]["t13"]["post_mutation_ok"], "skipped: initial read timed out")
        self.assertEqual(out["summary"]["mutations"], 1)
        self.assertIn("skipped: initial read timed out", sheet)


class ExistsFromCatalog(unittest.TestCase):
    """A view that is in the catalog but answers the wrong column list is a
    wrong answer, not a missing view. The grader used to read "column ... does
    not exist" as "view missing", which undercounts `exists`, the denominator
    of the guardrail component in Axis 3."""

    def grade_one(self, task, error_line, definition):
        f = fx.eval_fixture(1, 20)

        def fake_run(sql, **kw):
            if "mz_catalog.mz_views" in sql:
                return mzclient.Result(rc=0, rows=[[definition]] if definition else [])
            if f" FROM s.{task.view}" in sql:
                return mzclient.Result(rc=1, rows=[], stderr=error_line)
            return mzclient.Result(rc=0, rows=[])

        with mock.patch.object(grade.mzclient, "run", fake_run), \
                mock.patch.object(grade.T, "TASKS", [task]), \
                tempfile.TemporaryDirectory() as d:
            return grade.grade("s", f, "c", Path(d))["tasks"][task.id]

    def test_wrong_column_name_is_not_a_missing_view(self):
        t = next(x for x in tasks.TASKS if x.id == "t08")
        rec = self.grade_one(t, 'ERROR:  column "account_id" does not exist',
                             "CREATE VIEW t08_scc AS WITH MUTUALLY RECURSIVE "
                             "(ERROR AT RECURSION LIMIT 50) r(a text) AS (SELECT id FROM accounts) SELECT a FROM r")
        self.assertTrue(rec["exists"])
        self.assertFalse(rec["initial_ok"])
        self.assertTrue(rec["guardrail"])

    def test_view_absent_from_the_catalog_is_missing(self):
        t = next(x for x in tasks.TASKS if x.id == "t08")
        rec = self.grade_one(t, "ERROR:  unknown catalog item 's.t08_scc'", None)
        self.assertFalse(rec["exists"])
        self.assertIsNone(rec["guardrail"])
        self.assertIsNone(rec["recursive"])


class RecursiveDenominator(unittest.TestCase):
    """Axis 3 divides the guardrail count by `recursive`, not by `exists`: an
    answer written without WITH MUTUALLY RECURSIVE has no recursion to limit
    and must not drag the component down. t06 and t05 were answered
    non-recursively by a real bare cell."""

    def grade_one(self, task, definition):
        f = fx.eval_fixture(1, 20)

        def fake_run(sql, **kw):
            if "mz_catalog.mz_views" in sql:
                return mzclient.Result(rc=0, rows=[[definition]])
            return mzclient.Result(rc=0, rows=[])

        with mock.patch.object(grade.mzclient, "run", fake_run), \
                mock.patch.object(grade.T, "TASKS", [task]), \
                tempfile.TemporaryDirectory() as d:
            out = grade.grade("s", f, "c", Path(d))
            return out, (Path(d) / "worksheet.md").read_text()

    def test_non_recursive_answer_is_outside_the_denominator(self):
        t = next(x for x in tasks.TASKS if x.id == "t06")
        out, sheet = self.grade_one(
            t, "CREATE VIEW t06_hops AS SELECT a.id FROM e a JOIN e b ON b.src = a.dst")
        self.assertFalse(out["tasks"]["t06"]["recursive"])
        self.assertFalse(out["tasks"]["t06"]["guardrail"])
        self.assertEqual(out["summary"]["recursive"], 0)
        self.assertEqual(out["summary"]["exists"], 1)
        self.assertIn("| recursive | guardrail |", sheet)

    def test_recursive_and_limited_answer_counts_in_both(self):
        t = next(x for x in tasks.TASKS if x.id == "t06")
        out, _ = self.grade_one(
            t, "CREATE VIEW t06_hops AS with mutually recursive "
               "(return at recursion limit 50) r(a text) AS (SELECT id FROM e) SELECT a FROM r")
        self.assertTrue(out["tasks"]["t06"]["recursive"])
        self.assertTrue(out["tasks"]["t06"]["guardrail"])
        self.assertEqual(out["summary"]["recursive"], 1)
        self.assertEqual(out["summary"]["guardrail"], 1)


if __name__ == "__main__":
    unittest.main()
