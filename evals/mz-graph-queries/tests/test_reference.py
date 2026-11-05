import sys, os, unittest
from decimal import Decimal
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import fixture as fx
import reference as ref


class SmallWorld(unittest.TestCase):
    def setUp(self):
        self.f = fx.small_fixture()

    def test_descendants(self):
        self.assertEqual(ref.descendants(self.f, 2), {(4,), (5,), (7,), (8,)})
        self.assertEqual(ref.descendants(self.f, 8), set())

    def test_depth(self):
        self.assertEqual(ref.depth(self.f, 1), {(1, 0), (2, 1), (3, 1), (4, 2), (5, 2), (6, 2), (7, 3), (8, 3)})

    def test_team_salary(self):
        got = dict(ref.team_salary(self.f, 1))
        self.assertEqual(got[4], 295)
        self.assertEqual(got[2], 605)
        self.assertEqual(got[3], 290)
        self.assertEqual(got[1], 1195)
        self.assertEqual(got[8], 85)

    def test_bom(self):
        self.assertEqual(ref.bom_quantities(self.f, 1), {(2, 2), (3, 1), (4, 64), (6, 2), (5, 14)})
        self.assertEqual(ref.kit_cost(self.f, 1), {(Decimal("73.40"),)})

    def test_transfers(self):
        self.assertEqual(ref.within_hops(self.f, "a1", 2), {("a2",), ("a3",)})
        self.assertEqual(ref.within_hops(self.f, "a1", 3), {("a2",), ("a3",), ("a4",)})
        self.assertEqual(ref.ring_accounts(self.f), {("a1",), ("a2",), ("a3",)})
        self.assertEqual(ref.scc(self.f), {("a1", "a1"), ("a2", "a1"), ("a3", "a1"), ("a4", "a4"),
                                           ("a5", "a5"), ("a6", "a6"), ("a7", "a7")})
        c = ref.closure(self.f)
        self.assertIn(("a1", "a1"), c)
        self.assertIn(("a1", "a5"), c)
        self.assertNotIn(("a4", "a1"), c)
        self.assertEqual(len(c), 3 * 5 + 1 + 1)  # ring members reach 5 each; a4->a5; a6->a7

    def test_permissions(self):
        self.assertEqual(ref.effective_permissions(self.f), {
            ("u1", "doc1", "edit"), ("u1", "doc2", "edit"),
            ("u2", "doc1", "read"),
            ("u3", "doc1", "read"), ("u3", "doc2", "edit")})

    def test_clusters(self):
        self.assertEqual(ref.customer_clusters(self.f, Decimal("0.5")),
                         {("c1", "c1"), ("c2", "c1"), ("c3", "c1"), ("c4", "c4"), ("c5", "c4"), ("c6", "c6"), ("c7", "c7")})
        self.assertEqual(dict(ref.customer_clusters(self.f, Decimal("0.3")))["c6"], "c4")

    def test_roads(self):
        self.assertEqual(ref.shortest_km(self.f, "A"), {("B", 4), ("C", 7), ("D", 9), ("E", 14)})
        self.assertEqual(ref.shortest_hops(self.f, "A"), {("B", 1), ("C", 1), ("D", 2), ("E", 3)})

    def test_pipelines(self):
        self.assertEqual(ref.downstream(self.f, "raw_customers"),
                         {("stg_customers",), ("fct_sales",), ("rpt_daily",), ("rpt_churn",)})
        self.assertEqual(ref.topo_level(self.f), {("raw_orders", 0), ("raw_customers", 0), ("stg_orders", 1),
                                                  ("stg_customers", 1), ("fct_sales", 2), ("rpt_daily", 3), ("rpt_churn", 3)})


class EvalWorld(unittest.TestCase):
    def test_loop_terminates_and_excludes_self(self):
        f = fx.eval_fixture(1, 20)
        lm = f.params["loop_manager"]
        self.assertEqual(ref.descendants(f, lm), {(lm + 1,), (lm + 2,), (lm + 3,)})

    def test_ring_detected(self):
        f = fx.eval_fixture(1, 20)
        rings = {r[0] for r in ref.ring_accounts(f)}
        self.assertTrue(set(f.params["ring"]) <= rings)

    def test_every_customer_and_account_labelled(self):
        f = fx.eval_fixture(2, 20)
        self.assertEqual(len(ref.customer_clusters(f, f.params["threshold"])), len(f.customers))
        self.assertEqual(len(ref.scc(f)), len(f.accounts))

    def test_shared_part_counted_per_path(self):
        f = fx.eval_fixture(1, 20)
        q = dict(ref.bom_quantities(f, 1))
        # brute force: sum of products over all paths from the kit
        kids = {}
        for p, c, n in f.bom:
            kids.setdefault(p, []).append((c, n))
        tot = {}
        def walk(part, mult):
            for c, n in kids.get(part, []):
                tot[c] = tot.get(c, 0) + mult * n
                walk(c, mult * n)
        walk(1, 1)
        self.assertEqual(q, tot)


if __name__ == "__main__":
    unittest.main()
