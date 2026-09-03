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
    def test_count_only_when_the_full_read_times_out(self):
        """A result set too large to ship in the timeout is graded on its size."""
        t = next(x for x in tasks.TASKS if x.id == "t14")
        f = fx.eval_fixture(1, 20)
        n = len(t.reference(f))

        def fake_run(sql, **kw):
            if "count(*)" in sql:
                return mzclient.Result(rc=0, rows=[[str(n)]])
            if sql.startswith("SELECT src, dst FROM"):
                return mzclient.Result(rc=124, timed_out=True)
            return mzclient.Result(rc=0, rows=[])

        with mock.patch.object(grade.mzclient, "run", fake_run), \
                mock.patch.object(grade.T, "TASKS", [t]), \
                tempfile.TemporaryDirectory() as d:
            rec = grade.grade("s", f, "c", Path(d))["tasks"]["t14"]
        self.assertTrue(rec["timed_out"])
        self.assertTrue(rec["initial_ok"])
        self.assertEqual(rec["partial"], "count-only")


if __name__ == "__main__":
    unittest.main()
