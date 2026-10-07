import sys, os, unittest
from decimal import Decimal
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import fixture as fx


class SmallFixture(unittest.TestCase):
    def setUp(self):
        self.f = fx.small_fixture()

    def test_row_counts(self):
        self.assertEqual(len(self.f.employees), 8)
        self.assertEqual(len(self.f.bom), 6)
        self.assertEqual(len(self.f.transfers), 6)
        self.assertEqual(len(self.f.permissions), 3)
        self.assertEqual(len(self.f.customer_links), 5)
        self.assertEqual(len(self.f.roads), 6)
        self.assertEqual(len(self.f.depends_on), 7)

    def test_links_and_roads_stored_one_direction(self):
        for a, b, _ in self.f.customer_links:
            self.assertNotIn((b, a), [(x, y) for x, y, _ in self.f.customer_links])
        for s, d, _ in self.f.roads:
            self.assertNotIn((d, s), [(x, y) for x, y, _ in self.f.roads])

    def test_to_sql_has_every_table_and_no_schema_when_none(self):
        sql = fx.to_sql(self.f, None)
        for t in fx.TABLES:
            self.assertIn(f"CREATE TABLE {t} (", sql)
        self.assertNotIn("CREATE SCHEMA", sql)
        self.assertIn("INSERT INTO employees", sql)
        self.assertIn("(1, NULL, 'Ada', 300)", sql)

    def test_to_sql_with_schema_qualifies(self):
        sql = fx.to_sql(self.f, "demo")
        self.assertIn("CREATE SCHEMA demo;", sql)
        self.assertIn("CREATE TABLE demo.employees (", sql)
        self.assertIn("INSERT INTO demo.roads", sql)

    def test_sql_literal(self):
        self.assertEqual(fx.sql_literal(None), "NULL")
        self.assertEqual(fx.sql_literal(3), "3")
        self.assertEqual(fx.sql_literal(Decimal("0.50")), "0.50")
        self.assertEqual(fx.sql_literal("O'Neil"), "'O''Neil'")


class EvalFixture(unittest.TestCase):
    def test_deterministic(self):
        a, b = fx.eval_fixture(7, 20), fx.eval_fixture(7, 20)
        self.assertEqual(a, b)
        self.assertNotEqual(a, fx.eval_fixture(8, 20))

    def test_scale_and_traps(self):
        f = fx.eval_fixture(1, 20, traps=True)
        n = f.params["n_employees"]
        self.assertEqual(len(f.employees), n + 4)          # tree plus 3-loop plus dangling reportee
        lm = f.params["loop_manager"]
        mgr = {e[0]: e[1] for e in f.employees}
        self.assertEqual(mgr[lm], lm + 2)
        self.assertEqual(mgr[lm + 1], lm)
        self.assertEqual(mgr[lm + 2], lm + 1)
        self.assertEqual(mgr[lm + 3], lm)
        # bolt is a shared component: at least two parents
        bolt = f.params["shared_part"]
        self.assertGreaterEqual(sum(1 for p, c, _ in f.bom if c == bolt), 2)
        # kit part has children
        self.assertTrue(any(p == f.params["kit_part"] for p, _, _ in f.bom))
        # planted ring is a cycle of 4 distinct accounts
        ring = f.params["ring"]
        self.assertEqual(len(set(ring)), 4)
        edges = {(s, d) for s, d, _, _ in f.transfers}
        for i in range(4):
            self.assertIn((ring[i], ring[(i + 1) % 4]), edges)
        # override: a group with an explicit permission on a doc an ancestor also grants
        g, doc = f.params["override_group"], f.params["override_doc"]
        self.assertTrue(any(gg == g and dd == doc for gg, dd, _ in f.permissions))
        # links and roads one direction only
        links = {(a, b) for a, b, _ in f.customer_links}
        self.assertFalse(any((b, a) in links for a, b in links))
        roads = {(a, b) for a, b, _ in f.roads}
        self.assertFalse(any((b, a) in roads for a, b in roads))

    def test_no_traps(self):
        f = fx.eval_fixture(1, 20, traps=False)
        self.assertEqual(len(f.employees), f.params["n_employees"])
        self.assertNotIn("loop_manager", f.params)

    def test_bom_is_acyclic(self):
        f = fx.eval_fixture(3, 30)
        for p, c, _ in f.bom:
            self.assertLess(p, c)


class Mutations(unittest.TestCase):
    def test_apply_and_sql(self):
        f = fx.small_fixture()
        m = fx.Mutation(inserts={"employees": [(9, 7, "Ivy", 70)]},
                        deletes={"roads": [("A", "C", 10)]})
        g = fx.apply_mutation(f, m)
        self.assertEqual(len(g.employees), 9)
        self.assertEqual(len(g.roads), 5)
        self.assertEqual(len(f.roads), 6)  # original untouched
        sql = fx.mutation_sql(m, None)
        self.assertIn("INSERT INTO employees (id, manager_id, name, salary) VALUES (9, 7, 'Ivy', 70);", sql)
        self.assertIn("DELETE FROM roads WHERE src = 'A' AND dst = 'C' AND km = 10;", sql)

    def test_delete_with_null(self):
        m = fx.Mutation(deletes={"employees": [(1, None, "Ada", 300)]})
        self.assertIn("manager_id IS NULL", fx.mutation_sql(m, "s"))
        self.assertIn("DELETE FROM s.employees", fx.mutation_sql(m, "s"))


if __name__ == "__main__":
    unittest.main()
