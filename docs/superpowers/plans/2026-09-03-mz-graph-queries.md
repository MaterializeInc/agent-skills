# mz-graph-queries Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the `mz-graph-queries` skill (a decision procedure plus nine verified reference files for writing graph and hierarchy queries with `WITH MUTUALLY RECURSIVE`) and its eval harness (fixture generator, independent answer keys, automatic grader, clean-room runner).

**Architecture:** One Python fixture generator is the single source of truth for both the small hand-written fixture the skill's examples run against and the seeded eval fixture. A pure-Python reference implementation computes answer keys from the same in-memory fixture. A verifier extracts every fenced SQL block from the skill's reference files and runs it against the small fixture on a local Materialize, comparing with recorded expected output. The grader diffs an agent's views against the keys before and after mutations.

**Tech Stack:** Python 3.13 standard library only (no psycopg; database access goes through the `psql` binary via `subprocess`), bash, Materialize emulator in Docker (`materialize/materialized:latest`, v26.38.1 verified), Claude Code CLI 2.1.x for the clean-room runner.

**Spec:** `docs/superpowers/specs/2026-09-03-mz-graph-queries-design.md`

## Global Constraints

- Commit each task's work on the local branch `mz-graph-queries`. Never push, never touch `main`. The user approved local commits on this branch only.
- Skill name is exactly `mz-graph-queries`; the directory, `SKILL.md` frontmatter `name`, and every table row must match.
- `SKILL.md` body stays under 250 lines. Reference files hold the detail.
- Every fenced ```sql block in `skills/mz-graph-queries/references/*.md` must pass `evals/mz-graph-queries/verify_skill_sql.py`. Blocks that must not run are fenced as ```postgresql (other dialects) or preceded by `<!-- verify: skip -->`; blocks that must error are preceded by `<!-- verify: error -->`.
- Reference SQL references fixture tables unqualified (no schema prefix) so it runs in whatever schema is current.
- Local Materialize for all verification: `docker run -d --name mz-graph-queries -p 127.0.0.1:6877:6875 -p 127.0.0.1:6878:6876 materialize/materialized:latest`. Connection: `psql -h localhost -p 6877 -U materialize -d materialize`. Port 6875 on this machine is an unrelated ssh tunnel; never use it.
- Python scripts run with `python3` from `evals/mz-graph-queries/`; tests run with `python3 -m unittest discover -s evals/mz-graph-queries/tests -v` from the repo root.
- Prose style for skill files follows the repo's existing skills: short declarative sentences, no em-dashes, tables for mappings, `dot` digraphs only where a decision flow needs one.
- Every claim about Materialize behavior in the skill comes from `docs/superpowers/specs/2026-09-03-mz-graph-queries-design.md` section "Semantics the skill must teach" or is verified against the local Materialize before it stays in.

## File structure

```
skills/mz-graph-queries/
  SKILL.md                      decision procedure (Task 13)
  README.md                     user-facing overview (Task 13)
  DEVELOPMENT.md                method and how to test changes (Task 13)
  references/
    fixture.sql                 generated small fixture, kept in sync by the verifier (Task 1)
    semantics.md                (Task 4)
    hierarchies.md              (Task 5)
    rollups.md                  (Task 6)
    reachability.md             (Task 7)
    shortest-paths.md           (Task 8)
    components.md               (Task 9)
    permissions.md              (Task 10)
    migrating.md                (Task 11)
    context-graphs.md           (Task 12)
evals/mz-graph-queries/
  fixture.py                    Fixture dataclass, small_fixture, eval_fixture, to_sql, Mutation (Task 1)
  build_fixture.py              CLI over fixture.py (Task 1)
  reference.py                  pure-Python answer keys (Task 2)
  mzclient.py                   psql subprocess helper (Task 3)
  verify_skill_sql.py           runs skill SQL blocks against the small fixture (Task 3)
  expected/<ref>/<NN>.txt       recorded outputs of skill SQL blocks (Tasks 4-12)
  tasks.py                      eval task registry (Task 14)
  tasks/tNN-*.md                task prompt bodies (Task 14)
  grade.py                      automatic grader (Task 14)
  bench-psql.template           pinned psql wrapper (Task 15)
  prompt.txt.in                 round prompt template (Task 15)
  run_cleanroom.sh              one-round clean-room runner (Task 15)
  preflight.sh                  permission matrix check (Task 15)
  rubric.md, GRADING-TEMPLATE.md, README.md   (Task 15)
  tests/test_fixture.py, test_reference.py, test_verify.py, test_grade.py
```

---

### Task 1: Fixture module and generator CLI

**Files:**
- Create: `evals/mz-graph-queries/fixture.py`
- Create: `evals/mz-graph-queries/build_fixture.py`
- Create: `evals/mz-graph-queries/tests/__init__.py` (empty)
- Create: `evals/mz-graph-queries/tests/test_fixture.py`
- Create: `skills/mz-graph-queries/references/fixture.sql` (generated)

**Interfaces:**
- Produces: `Fixture` dataclass with list fields `employees, parts, bom, accounts, transfers, groups, memberships, permissions, customers, customer_links, cities, roads, pipelines, depends_on` and a `params: dict[str, object]` field; `TABLES: dict[str, list[str]]` (table name to column names, in Fixture field order); `small_fixture() -> Fixture`; `eval_fixture(seed: int, scale: int, traps: bool = True) -> Fixture`; `to_sql(f: Fixture, schema: str | None) -> str`; `Mutation(inserts: dict[str, list[tuple]], deletes: dict[str, list[tuple]])`; `apply_mutation(f: Fixture, m: Mutation) -> Fixture`; `mutation_sql(m: Mutation, schema: str | None) -> str`; `sql_literal(v) -> str`.

The small fixture is the world every reference file's examples describe. Its rows and the facts derived from them:

- `employees(id, manager_id, name, salary)`: (1, NULL, Ada, 300), (2, 1, Bob, 200), (3, 1, Cy, 190), (4, 2, Dee, 120), (5, 2, Eli, 110), (6, 3, Fay, 100), (7, 4, Gus, 90), (8, 4, Hal, 85). Depths: Ada 0; Bob, Cy 1; Dee, Eli, Fay 2; Gus, Hal 3. Team salaries: Dee 295, Bob 605, Cy 290, Ada 1195.
- `parts(id, name, unit_cost)`: (1, bike, NULL), (2, wheel, NULL), (3, frame, NULL), (4, spoke, 0.50), (5, bolt, 0.10), (6, tire, 20.00). `bom(parent_id, child_id, qty)`: (1,2,2), (1,3,1), (2,4,32), (2,6,1), (2,5,4), (3,5,6). One bike needs wheel 2, frame 1, spoke 64, tire 2, bolt 14 (8 via wheels plus 6 via frame). Kit cost 73.40.
- `accounts(id)`: a1..a7. `transfers(src, dst, amount, ts)`: (a1,a2,100,'2026-01-01 00:01:00'), (a2,a3,50,'... 00:02:00'), (a3,a1,25,'... 00:03:00'), (a3,a4,10,'... 00:04:00'), (a4,a5,5,'... 00:05:00'), (a6,a7,7,'... 00:06:00'). Ring {a1,a2,a3}; reachable from a1: a1,a2,a3,a4,a5; within 2 hops of a1 (excluding a1): a2, a3.
- `groups(id, parent_id)`: (g1,NULL), (g2,g1), (g3,g2), (g4,g1). `permissions(group_id, doc_id, level)`: (g1,doc1,read), (g2,doc2,edit), (g3,doc1,edit). `memberships(user_id, group_id)`: (u1,g3), (u2,g4), (u3,g2). Effective by group: g1 {doc1 read}; g2 {doc1 read, doc2 edit}; g3 {doc1 edit, doc2 edit}; g4 {doc1 read}. By user: u1 {doc1 edit, doc2 edit}; u2 {doc1 read}; u3 {doc1 read, doc2 edit}.
- `customers(id)`: c1..c7. `customer_links(a, b, score)` stored one direction: (c1,c2,0.9), (c2,c3,0.8), (c1,c3,0.95), (c4,c5,0.7), (c5,c6,0.4). Clusters at threshold 0.5: {c1,c2,c3}, {c4,c5}, {c6}, {c7}; at 0.3: {c4,c5,c6} merges.
- `cities(id)`: A..E. `roads(src, dst, km)` stored one direction: (A,B,4), (B,C,3), (A,C,10), (C,D,2), (B,D,8), (D,E,5). From A: km B 4, C 7, D 9, E 14; hops B 1, C 1, D 2, E 3.
- `pipelines(id)`: raw_orders, raw_customers, stg_orders, stg_customers, fct_sales, rpt_daily, rpt_churn. `depends_on(task, prereq)`: (stg_orders, raw_orders), (stg_customers, raw_customers), (fct_sales, stg_orders), (fct_sales, stg_customers), (rpt_daily, fct_sales), (rpt_churn, stg_customers), (rpt_churn, fct_sales). Levels: raw_* 0, stg_* 1, fct_sales 2, rpt_daily 3, rpt_churn 3. Downstream of raw_customers: stg_customers, fct_sales, rpt_daily, rpt_churn.
- `params`: `{"ceo_id": 1, "subtree_root": 2, "kit_part": 1, "flagged_account": "a1", "sample_user": "u1", "origin_city": "A", "impact_task": "raw_customers", "threshold": Decimal("0.5"), "hops": 2}`.

- [ ] **Step 1: Write the failing tests**

```python
# evals/mz-graph-queries/tests/test_fixture.py
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest discover -s evals/mz-graph-queries/tests -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'fixture'`

- [ ] **Step 3: Write fixture.py**

```python
# evals/mz-graph-queries/fixture.py
"""Fixture data for the mz-graph-queries skill and its eval.

One fictional company with seven table groups. `small_fixture()` is the
hand-written world every skill example runs against; `eval_fixture()` is a
seeded, scaled variant with planted traps. `to_sql()` serializes either.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field, fields
from decimal import Decimal

# table name -> column names; order matches the Fixture field order
TABLES: dict[str, list[str]] = {
    "employees": ["id", "manager_id", "name", "salary"],
    "parts": ["id", "name", "unit_cost"],
    "bom": ["parent_id", "child_id", "qty"],
    "accounts": ["id"],
    "transfers": ["src", "dst", "amount", "ts"],
    "groups": ["id", "parent_id"],
    "memberships": ["user_id", "group_id"],
    "permissions": ["group_id", "doc_id", "level"],
    "customers": ["id"],
    "customer_links": ["a", "b", "score"],
    "cities": ["id"],
    "roads": ["src", "dst", "km"],
    "pipelines": ["id"],
    "depends_on": ["task", "prereq"],
}

DDL: dict[str, str] = {
    "employees": "id int NOT NULL, manager_id int, name text NOT NULL, salary int NOT NULL",
    "parts": "id int NOT NULL, name text NOT NULL, unit_cost numeric",
    "bom": "parent_id int NOT NULL, child_id int NOT NULL, qty int NOT NULL",
    "accounts": "id text NOT NULL",
    "transfers": "src text NOT NULL, dst text NOT NULL, amount numeric NOT NULL, ts timestamp NOT NULL",
    "groups": "id text NOT NULL, parent_id text",
    "memberships": "user_id text NOT NULL, group_id text NOT NULL",
    "permissions": "group_id text NOT NULL, doc_id text NOT NULL, level text NOT NULL",
    "customers": "id text NOT NULL",
    "customer_links": "a text NOT NULL, b text NOT NULL, score numeric NOT NULL",
    "cities": "id text NOT NULL",
    "roads": "src text NOT NULL, dst text NOT NULL, km int NOT NULL",
    "pipelines": "id text NOT NULL",
    "depends_on": "task text NOT NULL, prereq text NOT NULL",
}


@dataclass
class Fixture:
    employees: list[tuple] = field(default_factory=list)
    parts: list[tuple] = field(default_factory=list)
    bom: list[tuple] = field(default_factory=list)
    accounts: list[tuple] = field(default_factory=list)
    transfers: list[tuple] = field(default_factory=list)
    groups: list[tuple] = field(default_factory=list)
    memberships: list[tuple] = field(default_factory=list)
    permissions: list[tuple] = field(default_factory=list)
    customers: list[tuple] = field(default_factory=list)
    customer_links: list[tuple] = field(default_factory=list)
    cities: list[tuple] = field(default_factory=list)
    roads: list[tuple] = field(default_factory=list)
    pipelines: list[tuple] = field(default_factory=list)
    depends_on: list[tuple] = field(default_factory=list)
    params: dict = field(default_factory=dict)

    def rows(self, table: str) -> list[tuple]:
        return getattr(self, table)


def sql_literal(v) -> str:
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, Decimal)):
        return str(v)
    if isinstance(v, float):
        return repr(v)
    return "'" + str(v).replace("'", "''") + "'"


def _q(schema: str | None, table: str) -> str:
    return f"{schema}.{table}" if schema else table


def to_sql(f: Fixture, schema: str | None, batch: int = 500) -> str:
    out: list[str] = []
    if schema:
        out.append(f"CREATE SCHEMA {schema};")
    for t, cols in TABLES.items():
        out.append(f"CREATE TABLE {_q(schema, t)} ({DDL[t]});")
    for t, cols in TABLES.items():
        rows = f.rows(t)
        for i in range(0, len(rows), batch):
            vals = ",\n  ".join("(" + ", ".join(sql_literal(v) for v in r) + ")" for r in rows[i:i + batch])
            out.append(f"INSERT INTO {_q(schema, t)} ({', '.join(cols)}) VALUES\n  {vals};")
    return "\n".join(out) + "\n"


@dataclass
class Mutation:
    inserts: dict[str, list[tuple]] = field(default_factory=dict)
    deletes: dict[str, list[tuple]] = field(default_factory=dict)


def apply_mutation(f: Fixture, m: Mutation) -> Fixture:
    g = Fixture(**{fl.name: (list(getattr(f, fl.name)) if fl.name != "params" else dict(f.params)) for fl in fields(f)})
    for t, rows in m.deletes.items():
        for r in rows:
            getattr(g, t).remove(r)
    for t, rows in m.inserts.items():
        getattr(g, t).extend(rows)
    return g


def mutation_sql(m: Mutation, schema: str | None) -> str:
    out: list[str] = []
    for t, rows in m.deletes.items():
        cols = TABLES[t]
        for r in rows:
            conds = [f"{c} IS NULL" if v is None else f"{c} = {sql_literal(v)}" for c, v in zip(cols, r)]
            out.append(f"DELETE FROM {_q(schema, t)} WHERE {' AND '.join(conds)};")
    for t, rows in m.inserts.items():
        cols = TABLES[t]
        for r in rows:
            out.append(f"INSERT INTO {_q(schema, t)} ({', '.join(cols)}) VALUES ({', '.join(sql_literal(v) for v in r)});")
    return "\n".join(out) + "\n"


def small_fixture() -> Fixture:
    D = Decimal
    ts = lambda m: f"2026-01-01 00:0{m}:00"
    return Fixture(
        employees=[(1, None, "Ada", 300), (2, 1, "Bob", 200), (3, 1, "Cy", 190), (4, 2, "Dee", 120),
                   (5, 2, "Eli", 110), (6, 3, "Fay", 100), (7, 4, "Gus", 90), (8, 4, "Hal", 85)],
        parts=[(1, "bike", None), (2, "wheel", None), (3, "frame", None),
               (4, "spoke", D("0.50")), (5, "bolt", D("0.10")), (6, "tire", D("20.00"))],
        bom=[(1, 2, 2), (1, 3, 1), (2, 4, 32), (2, 6, 1), (2, 5, 4), (3, 5, 6)],
        accounts=[(f"a{i}",) for i in range(1, 8)],
        transfers=[("a1", "a2", D("100"), ts(1)), ("a2", "a3", D("50"), ts(2)), ("a3", "a1", D("25"), ts(3)),
                   ("a3", "a4", D("10"), ts(4)), ("a4", "a5", D("5"), ts(5)), ("a6", "a7", D("7"), ts(6))],
        groups=[("g1", None), ("g2", "g1"), ("g3", "g2"), ("g4", "g1")],
        memberships=[("u1", "g3"), ("u2", "g4"), ("u3", "g2")],
        permissions=[("g1", "doc1", "read"), ("g2", "doc2", "edit"), ("g3", "doc1", "edit")],
        customers=[(f"c{i}",) for i in range(1, 8)],
        customer_links=[("c1", "c2", D("0.9")), ("c2", "c3", D("0.8")), ("c1", "c3", D("0.95")),
                        ("c4", "c5", D("0.7")), ("c5", "c6", D("0.4"))],
        cities=[(c,) for c in "ABCDE"],
        roads=[("A", "B", 4), ("B", "C", 3), ("A", "C", 10), ("C", "D", 2), ("B", "D", 8), ("D", "E", 5)],
        pipelines=[(p,) for p in ["raw_orders", "raw_customers", "stg_orders", "stg_customers",
                                  "fct_sales", "rpt_daily", "rpt_churn"]],
        depends_on=[("stg_orders", "raw_orders"), ("stg_customers", "raw_customers"), ("fct_sales", "stg_orders"),
                    ("fct_sales", "stg_customers"), ("rpt_daily", "fct_sales"), ("rpt_churn", "stg_customers"),
                    ("rpt_churn", "fct_sales")],
        params={"ceo_id": 1, "subtree_root": 2, "kit_part": 1, "flagged_account": "a1", "sample_user": "u1",
                "origin_city": "A", "impact_task": "raw_customers", "threshold": D("0.5"), "hops": 2},
    )


def eval_fixture(seed: int, scale: int, traps: bool = True) -> Fixture:
    """Seeded fixture. scale=20 is a smoke size; scale=100 is the graded size."""
    rng = random.Random(seed)
    D = Decimal
    f = Fixture()
    p = f.params
    # --- employees: a single tree with deep chains, ids 1..n ---
    n = scale * 5
    p["n_employees"], p["ceo_id"] = n, 1
    f.employees.append((1, None, "emp_1", rng.randint(50, 300)))
    for i in range(2, n + 1):
        mgr = rng.randint(max(1, i - 20), i - 1) if rng.random() < 0.6 else rng.randint(1, i - 1)
        f.employees.append((i, mgr, f"emp_{i}", rng.randint(50, 300)))
    p["subtree_root"] = rng.randint(2, min(n, 10))
    if traps:
        lm = n + 1  # a 3-cycle of managers plus one dangling reportee, detached from the tree
        f.employees += [(lm, lm + 2, f"emp_{lm}", 100), (lm + 1, lm, f"emp_{lm + 1}", 100),
                        (lm + 2, lm + 1, f"emp_{lm + 2}", 100), (lm + 3, lm, f"emp_{lm + 3}", 100)]
        p["loop_manager"] = lm
    # --- parts / bom: DAG, parents have smaller ids than children ---
    m = scale * 2
    leaves = set(range(m // 2 + 1, m + 1))
    for i in range(1, m + 1):
        cost = D(rng.randint(1, 500)) / 100 if i in leaves else None
        f.parts.append((i, f"part_{i}", cost))
    for i in range(1, m // 2 + 1):
        kids = rng.sample(range(i + 1, m + 1), k=min(rng.randint(2, 4), m - i))
        for k in kids:
            f.bom.append((i, k, rng.randint(1, 5)))
    p["kit_part"] = 1
    shared = m  # a leaf used under two distinct assemblies
    parents = rng.sample(range(1, m // 2 + 1), 2)
    for par in parents:
        if not any(pp == par and cc == shared for pp, cc, _ in f.bom):
            f.bom.append((par, shared, rng.randint(1, 3)))
    p["shared_part"] = shared
    # --- accounts / transfers: random digraph with a planted 4-ring ---
    k = scale * 10
    f.accounts = [(f"a{i}",) for i in range(1, k + 1)]
    base = "2026-01-01 00:00:00"
    minute = 0
    def add_transfer(s, d):
        nonlocal minute
        minute += 1
        f.transfers.append((s, d, D(rng.randint(1, 1000)), f"2026-01-01 {minute // 3600:02d}:{(minute // 60) % 60:02d}:{minute % 60:02d}"))
    for _ in range(k * 3):
        s, d = rng.sample(range(1, k + 1), 2)
        add_transfer(f"a{s}", f"a{d}")
    ring = [f"a{i}" for i in rng.sample(range(1, k + 1), 4)]
    for i in range(4):
        add_transfer(ring[i], ring[(i + 1) % 4])
    p["ring"], p["flagged_account"], p["hops"] = ring, ring[0], 3
    # --- groups / memberships / permissions: a tree of 30 groups, 10 docs ---
    ng = 30
    f.groups.append(("g1", None))
    for i in range(2, ng + 1):
        f.groups.append((f"g{i}", f"g{rng.randint(1, i - 1)}"))
    docs = [f"doc{i}" for i in range(1, 11)]
    seen = set()
    for _ in range(25):
        g, d = f"g{rng.randint(1, ng)}", rng.choice(docs)
        if (g, d) not in seen:
            seen.add((g, d))
            f.permissions.append((g, d, rng.choice(["read", "edit"])))
    parent = {g: pg for g, pg in f.groups}
    # planted override: pick an explicit permission, descend to a child, grant the other level
    children = {}
    for g, pg in f.groups:
        children.setdefault(pg, []).append(g)
    for g, d, lvl in list(f.permissions):
        if children.get(g):
            child = children[g][0]
            if (child, d) not in seen:
                seen.add((child, d))
                f.permissions.append((child, d, "edit" if lvl == "read" else "read"))
                p["override_group"], p["override_doc"] = child, d
                break
    for u in range(1, 101):
        for g in rng.sample(range(1, ng + 1), rng.randint(1, 2)):
            f.memberships.append((f"u{u}", f"g{g}"))
    p["sample_user"] = "u1"
    # --- customers / links: one direction only ---
    nc = scale * 3
    f.customers = [(f"c{i}",) for i in range(1, nc + 1)]
    links = set()
    for _ in range(nc):
        a, b = sorted(rng.sample(range(1, nc + 1), 2))
        if (a, b) not in links:
            links.add((a, b))
            f.customer_links.append((f"c{a}", f"c{b}", D(rng.randint(0, 100)) / 100))
    p["threshold"] = D("0.5")
    # --- cities / roads: connected undirected graph stored one direction ---
    ncity = 30
    f.cities = [(f"city{i}",) for i in range(1, ncity + 1)]
    roads = set()
    for i in range(2, ncity + 1):          # spanning tree first, so everything is reachable
        j = rng.randint(1, i - 1)
        roads.add((j, i))
    while len(roads) < ncity * 2:
        a, b = sorted(rng.sample(range(1, ncity + 1), 2))
        roads.add((a, b))
    for a, b in sorted(roads):
        f.roads.append((f"city{a}", f"city{b}", rng.randint(1, 20)))
    p["origin_city"] = "city1"
    # --- pipelines / depends_on: DAG, prereqs have smaller index ---
    nt = 40
    f.pipelines = [(f"task{i}",) for i in range(1, nt + 1)]
    for i in range(4, nt + 1):
        for j in rng.sample(range(1, i), rng.randint(1, 2)):
            f.depends_on.append((f"task{i}", f"task{j}"))
    p["impact_task"] = "task2"
    return f
```

- [ ] **Step 4: Write build_fixture.py**

```python
#!/usr/bin/env python3
# evals/mz-graph-queries/build_fixture.py
"""Emit fixture SQL on stdout.

  build_fixture.py --small [--schema S]                 the skill's example world
  build_fixture.py --eval --seed N --scale N [--no-traps] --schema S
  build_fixture.py --eval ... --manifest                 print params as JSON instead of SQL
"""
import argparse, json, sys
from decimal import Decimal
import fixture as fx


def main() -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--small", action="store_true")
    g.add_argument("--eval", action="store_true")
    ap.add_argument("--schema", default=None, help="omit to emit unqualified names for the current schema")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--scale", type=int, default=100)
    ap.add_argument("--no-traps", action="store_true")
    ap.add_argument("--manifest", action="store_true")
    a = ap.parse_args()
    f = fx.small_fixture() if a.small else fx.eval_fixture(a.seed, a.scale, traps=not a.no_traps)
    if a.manifest:
        json.dump(f.params, sys.stdout, indent=2, default=lambda v: str(v) if isinstance(v, Decimal) else v)
        print()
    else:
        sys.stdout.write(fx.to_sql(f, a.schema))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python3 -m unittest discover -s evals/mz-graph-queries/tests -v`
Expected: all tests PASS. If `test_scale_and_traps` fails on `shared_part` parents, the two sampled parents already had the bolt; the guard `if not any(...)` keeps the count at two or more because a sampled parent is either given the edge or already has it.

- [ ] **Step 6: Load both fixtures into the local Materialize**

Run:
```bash
cd evals/mz-graph-queries
python3 build_fixture.py --small --schema fx_small | psql -X -q -v ON_ERROR_STOP=1 -h localhost -p 6877 -U materialize -d materialize -f -
python3 build_fixture.py --eval --seed 1 --scale 20 --schema fx_eval20 | psql -X -q -v ON_ERROR_STOP=1 -h localhost -p 6877 -U materialize -d materialize -f -
psql -X -At -h localhost -p 6877 -U materialize -d materialize -c "SELECT count(*) FROM fx_small.employees" -c "SELECT count(*) FROM fx_eval20.employees"
```
Expected: `8` and `104`, no errors. Then drop both: `psql ... -c "DROP SCHEMA fx_small CASCADE" -c "DROP SCHEMA fx_eval20 CASCADE"`.

- [ ] **Step 7: Generate the skill's copy of the small fixture**

Run: `mkdir -p skills/mz-graph-queries/references && python3 evals/mz-graph-queries/build_fixture.py --small > skills/mz-graph-queries/references/fixture.sql`

Prepend this header to the file (a `sed -i '1i ...'` or editor insert):

```sql
-- Small fixture for the mz-graph-queries skill. Generated by
-- evals/mz-graph-queries/build_fixture.py --small; do not edit by hand.
-- Load into any schema: psql ... -f fixture.sql
```

The verifier in Task 3 regenerates and compares this file, so the header lines must be exactly these three comment lines followed by the generator output.

---

### Task 2: Reference implementation of answer keys

**Files:**
- Create: `evals/mz-graph-queries/reference.py`
- Create: `evals/mz-graph-queries/tests/test_reference.py`

**Interfaces:**
- Consumes: `fixture.Fixture`, `fixture.small_fixture`, `fixture.eval_fixture`.
- Produces (every function takes a `Fixture` first and returns `set[tuple]` whose tuple order matches the eval view's declared columns): `descendants(f, root) -> {(id,)}` excluding root; `depth(f, root) -> {(id, depth)}` root at 0; `team_salary(f, root) -> {(id, total)}` own plus all descendants, tree part reachable from root; `bom_quantities(f, kit) -> {(part_id, qty)}` summed over paths, excluding kit; `kit_cost(f, kit) -> {(cost,)}` Decimal sum of leaf qty times unit_cost; `within_hops(f, src, k) -> {(id,)}` accounts other than src reachable in 1..k transfers; `ring_accounts(f) -> {(id,)}` accounts on any directed cycle; `scc(f) -> {(id, component)}` component = lexicographically smallest id in the SCC, all accounts; `closure(f) -> {(src, dst)}` transitive closure of transfers; `effective_permissions(f) -> {(user, doc, level)}`; `customer_clusters(f, threshold) -> {(id, cluster)}` cluster = smallest id, edges with score >= threshold, all customers; `shortest_km(f, origin) -> {(city, km)}` reachable cities excluding origin, roads undirected; `shortest_hops(f, origin) -> {(city, hops)}`; `downstream(f, task) -> {(id,)}` tasks depending transitively on task, excluding it; `topo_level(f) -> {(id, level)}` longest path from any source, sources 0.

Override rule for `effective_permissions`: a group's effective set is its explicit permissions plus, for every doc it has no explicit row for, its parent's effective permissions on that doc. A user's set is the union over their groups.

- [ ] **Step 1: Write the failing tests**

```python
# evals/mz-graph-queries/tests/test_reference.py
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest evals.mz-graph-queries.tests.test_reference 2>&1 | tail -3` (or the discover command). Expected: FAIL with `No module named 'reference'`.

- [ ] **Step 3: Write reference.py**

```python
# evals/mz-graph-queries/reference.py
"""Independent answer keys. Plain Python, no SQL, so a wrong pattern in the
skill cannot leak into the key. Every function returns a set of tuples in
the column order of the corresponding eval view."""
from __future__ import annotations

import heapq
from collections import defaultdict, deque
from decimal import Decimal
from fixture import Fixture


def _children(f: Fixture) -> dict[int, list[int]]:
    ch: dict[int, list[int]] = defaultdict(list)
    for i, mgr, _, _ in f.employees:
        if mgr is not None:
            ch[mgr].append(i)
    return ch


def _reach(adj: dict, start) -> set:
    seen, todo = set(), deque([start])
    while todo:
        x = todo.popleft()
        for y in adj.get(x, ()):
            if y not in seen:
                seen.add(y)
                todo.append(y)
    return seen


def descendants(f: Fixture, root: int) -> set[tuple]:
    return {(i,) for i in _reach(_children(f), root) if i != root}


def depth(f: Fixture, root: int) -> set[tuple]:
    ch = _children(f)
    out, seen, todo = set(), {root}, deque([(root, 0)])
    while todo:
        x, d = todo.popleft()
        out.add((x, d))
        for y in ch.get(x, ()):
            if y not in seen:
                seen.add(y)
                todo.append((y, d + 1))
    return out


def team_salary(f: Fixture, root: int) -> set[tuple]:
    ch, sal = _children(f), {i: s for i, _, _, s in f.employees}
    nodes = _reach(ch, root) | {root}
    out = set()
    for x in nodes:
        out.add((x, sal[x] + sum(sal[y] for y in _reach(ch, x) if y != x)))
    return out


def bom_quantities(f: Fixture, kit: int) -> set[tuple]:
    kids: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for p, c, n in f.bom:
        kids[p].append((c, n))
    tot: dict[int, int] = defaultdict(int)

    def walk(part: int, mult: int) -> None:
        for c, n in kids.get(part, ()):
            tot[c] += mult * n
            walk(c, mult * n)
    walk(kit, 1)
    return {(p, q) for p, q in tot.items()}


def kit_cost(f: Fixture, kit: int) -> set[tuple]:
    cost = {i: c for i, _, c in f.parts if c is not None}
    total = sum((Decimal(q) * cost[p] for p, q in bom_quantities(f, kit) if p in cost), Decimal(0))
    return {(total,)}


def _transfer_adj(f: Fixture) -> dict[str, set[str]]:
    adj: dict[str, set[str]] = defaultdict(set)
    for s, d, _, _ in f.transfers:
        adj[s].add(d)
    return adj


def within_hops(f: Fixture, src: str, k: int) -> set[tuple]:
    adj, dist = _transfer_adj(f), {src: 0}
    todo = deque([src])
    while todo:
        x = todo.popleft()
        if dist[x] == k:
            continue
        for y in adj.get(x, ()):
            if y not in dist:
                dist[y] = dist[x] + 1
                todo.append(y)
    return {(y,) for y, d in dist.items() if y != src}


def closure(f: Fixture) -> set[tuple]:
    adj = _transfer_adj(f)
    return {(s, d) for s in {x for x, in f.accounts} for d in _reach(adj, s)}


def scc(f: Fixture) -> set[tuple]:
    adj = _transfer_adj(f)
    nodes = [x for x, in f.accounts]
    reach = {x: _reach(adj, x) for x in nodes}
    out = set()
    for x in nodes:
        members = {y for y in reach[x] if x in reach[y]} | {x}
        out.add((x, min(members)))
    return out


def ring_accounts(f: Fixture) -> set[tuple]:
    adj = _transfer_adj(f)
    return {(x,) for x, in f.accounts if x in _reach(adj, x)}


def effective_permissions(f: Fixture) -> set[tuple]:
    parent = {g: pg for g, pg in f.groups}
    explicit: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    for g, d, lvl in f.permissions:
        explicit[g][d].add(lvl)
    memo: dict[str, dict[str, set[str]]] = {}

    def eff(g: str) -> dict[str, set[str]]:
        if g in memo:
            return memo[g]
        res = {d: set(l) for d, l in explicit[g].items()}
        if parent.get(g) is not None:
            for d, l in eff(parent[g]).items():
                if d not in res:
                    res[d] = set(l)
        memo[g] = res
        return res
    out = set()
    for u, g in f.memberships:
        for d, levels in eff(g).items():
            for lvl in levels:
                out.add((u, d, lvl))
    return out


def customer_clusters(f: Fixture, threshold: Decimal) -> set[tuple]:
    adj: dict[str, set[str]] = defaultdict(set)
    for a, b, s in f.customer_links:
        if s >= threshold:
            adj[a].add(b)
            adj[b].add(a)
    return {(c, min(_reach(adj, c) | {c})) for c, in f.customers}


def _road_adj(f: Fixture) -> dict[str, list[tuple[str, int]]]:
    adj: dict[str, list[tuple[str, int]]] = defaultdict(list)
    for s, d, km in f.roads:
        adj[s].append((d, km))
        adj[d].append((s, km))
    return adj


def shortest_km(f: Fixture, origin: str) -> set[tuple]:
    adj, dist, pq = _road_adj(f), {origin: 0}, [(0, origin)]
    while pq:
        d, x = heapq.heappop(pq)
        if d > dist[x]:
            continue
        for y, w in adj.get(x, ()):
            if d + w < dist.get(y, float("inf")):
                dist[y] = d + w
                heapq.heappush(pq, (d + w, y))
    return {(c, d) for c, d in dist.items() if c != origin}


def shortest_hops(f: Fixture, origin: str) -> set[tuple]:
    adj = {x: [y for y, _ in ys] for x, ys in _road_adj(f).items()}
    dist, todo = {origin: 0}, deque([origin])
    while todo:
        x = todo.popleft()
        for y in adj.get(x, ()):
            if y not in dist:
                dist[y] = dist[x] + 1
                todo.append(y)
    return {(c, d) for c, d in dist.items() if c != origin}


def downstream(f: Fixture, task: str) -> set[tuple]:
    dep: dict[str, set[str]] = defaultdict(set)  # prereq -> tasks that need it
    for t, pre in f.depends_on:
        dep[pre].add(t)
    return {(t,) for t in _reach(dep, task) if t != task}


def topo_level(f: Fixture) -> set[tuple]:
    pre: dict[str, set[str]] = defaultdict(set)
    for t, p in f.depends_on:
        pre[t].add(p)
    memo: dict[str, int] = {}

    def level(t: str) -> int:
        if t not in memo:
            memo[t] = 0 if not pre[t] else 1 + max(level(p) for p in pre[t])
        return memo[t]
    return {(t, level(t)) for t, in f.pipelines}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest discover -s evals/mz-graph-queries/tests -v`
Expected: all PASS. `test_transfers` asserts `len(c) == 17`: a1, a2, a3 each reach {a1,a2,a3,a4,a5} (15 pairs), plus (a4,a5) and (a6,a7).

---

### Task 3: psql client and skill SQL verifier

**Files:**
- Create: `evals/mz-graph-queries/mzclient.py`
- Create: `evals/mz-graph-queries/verify_skill_sql.py`
- Create: `evals/mz-graph-queries/tests/test_verify.py`

**Interfaces:**
- Produces: `mzclient.PSQL_ARGS` (default `["-h", "localhost", "-p", "6877", "-U", "materialize", "-d", "materialize"]`, overridable by env `EVAL_PSQL_ARGS` as a whitespace-split string); `mzclient.run(sql: str, *, schema: str | None = None, cluster: str | None = None, timeout_s: int = 120, on_error_stop: bool = True) -> Result` where `Result` has `rc: int`, `rows: list[list[str]]` (tab-split, `\N` for NULL), `stderr: str`, `timed_out: bool`; `mzclient.run_file(path, **kw) -> Result`.
- Produces: `verify_skill_sql.extract_blocks(md_text: str) -> list[Block]` where `Block(index: int, sql: str, mode: str)` and `mode in {"run", "error", "skip"}`; blocks are only ```sql fences; a line `<!-- verify: error -->` or `<!-- verify: skip -->` immediately above the fence (blank lines allowed between) sets the mode; `index` counts only non-skip blocks starting at 1. CLI: `verify_skill_sql.py [--record] [--only NAME] [--keep]`.

Verifier behaviour: for each `skills/mz-graph-queries/references/*.md` except `fixture.sql`, create schema `verify_<name>` (dropping any existing one), load the small fixture into it with `build_fixture.py --small --schema verify_<name>`, then run the file's blocks in order in that schema (each block is one `psql -f` invocation with `SET schema` and `SET cluster = quickstart`, `statement_timeout = '60s'`). A `run` block must succeed; its rows are sorted lexicographically and joined with `\t` and `\n`, and compared byte-for-byte with `expected/<name>/<NN>.txt` (`NN` zero-padded to two digits). An `error` block must fail; the first line of stderr matching `ERROR:` is compared with the expected file. With `--record`, expected files are written instead of compared and the diff is printed for review. The verifier also regenerates `skills/mz-graph-queries/references/fixture.sql` in memory (header plus generator output) and fails if the checked-in file differs. Schemas are dropped at the end unless `--keep`. Exit code is the number of failures.

- [ ] **Step 1: Write the failing tests**

```python
# evals/mz-graph-queries/tests/test_verify.py
import sys, os, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import verify_skill_sql as v

MD = """# Title

```sql
SELECT 1;
```

Some prose.

<!-- verify: error -->

```sql
SELECT 1/0;
```

```postgresql
WITH RECURSIVE t AS (SELECT 1) SELECT * FROM t;
```

<!-- verify: skip -->
```sql
SELECT 'never runs';
```

```sql
SELECT 2;
```
"""


class Extract(unittest.TestCase):
    def test_blocks_and_modes(self):
        b = v.extract_blocks(MD)
        self.assertEqual([(x.index, x.mode, x.sql.strip()) for x in b], [
            (1, "run", "SELECT 1;"),
            (2, "error", "SELECT 1/0;"),
            (0, "skip", "SELECT 'never runs';"),
            (3, "run", "SELECT 2;"),
        ])

    def test_expected_name(self):
        self.assertEqual(v.expected_path("hierarchies", 3).name, "03.txt")
        self.assertEqual(v.expected_path("hierarchies", 3).parent.name, "hierarchies")


class Normalize(unittest.TestCase):
    def test_sorted_rows(self):
        self.assertEqual(v.normalize([["b", "2"], ["a", "1"]]), "a\t1\nb\t2\n")
        self.assertEqual(v.normalize([]), "")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest discover -s evals/mz-graph-queries/tests -v 2>&1 | tail -3`
Expected: FAIL with `No module named 'verify_skill_sql'`.

- [ ] **Step 3: Write mzclient.py**

```python
# evals/mz-graph-queries/mzclient.py
"""Talk to Materialize through the psql binary. Standard library only."""
from __future__ import annotations

import os
import subprocess
import tempfile
from dataclasses import dataclass, field

PSQL_ARGS: list[str] = os.environ.get(
    "EVAL_PSQL_ARGS", "-h localhost -p 6877 -U materialize -d materialize").split()


@dataclass
class Result:
    rc: int
    rows: list[list[str]] = field(default_factory=list)
    stderr: str = ""
    timed_out: bool = False

    @property
    def ok(self) -> bool:
        return self.rc == 0 and not self.timed_out

    @property
    def error_line(self) -> str:
        for line in self.stderr.splitlines():
            if "ERROR:" in line:
                return line[line.index("ERROR:"):].strip()
        return self.stderr.strip().splitlines()[-1] if self.stderr.strip() else ""


def run(sql: str, *, schema: str | None = None, cluster: str | None = None,
        timeout_s: int = 120, on_error_stop: bool = True) -> Result:
    with tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False) as fh:
        fh.write(sql)
        path = fh.name
    try:
        return run_file(path, schema=schema, cluster=cluster, timeout_s=timeout_s, on_error_stop=on_error_stop)
    finally:
        os.unlink(path)


def run_file(path: str, *, schema: str | None = None, cluster: str | None = None,
             timeout_s: int = 120, on_error_stop: bool = True) -> Result:
    cmd = ["psql", "-X", "-q", "-At", "-F", "\t", "-P", "null=\\N",
           "-v", f"ON_ERROR_STOP={'1' if on_error_stop else '0'}", *PSQL_ARGS,
           "-c", f"SET statement_timeout = '{timeout_s}s'"]
    if cluster:
        cmd += ["-c", f"SET cluster = {cluster}"]
    if schema:
        cmd += ["-c", f"SET schema = {schema}"]
    cmd += ["-f", path]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s + 30)
    except subprocess.TimeoutExpired as e:
        return Result(rc=124, stderr=(e.stderr or "") if isinstance(e.stderr, str) else "", timed_out=True)
    rows = [line.split("\t") for line in p.stdout.splitlines() if line != ""]
    timed_out = "canceling statement due to statement timeout" in p.stderr
    return Result(rc=p.returncode, rows=rows, stderr=p.stderr, timed_out=timed_out)
```

Note: `SET cluster` before `SET schema` and before `-f` so every statement in the file runs on the requested cluster. `-P null=\N` makes NULL visible and distinct from the empty string.

- [ ] **Step 4: Write verify_skill_sql.py**

```python
#!/usr/bin/env python3
# evals/mz-graph-queries/verify_skill_sql.py
"""Run every fenced ```sql block in the skill's reference files against the
small fixture and compare with recorded expected output.

  verify_skill_sql.py [--record] [--only NAME] [--keep]

Conventions in the markdown: only ```sql fences run (other dialects use
```postgresql etc.). An HTML comment line <!-- verify: error --> above a fence
means the block must fail and its ERROR line is compared; <!-- verify: skip -->
means the block is not run. Expected files: expected/<name>/<NN>.txt.
"""
from __future__ import annotations

import argparse
import difflib
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import mzclient

HERE = Path(__file__).resolve().parent
REFS = HERE.parent.parent / "skills" / "mz-graph-queries" / "references"
EXPECTED = HERE / "expected"
FIXTURE_HEADER = (
    "-- Small fixture for the mz-graph-queries skill. Generated by\n"
    "-- evals/mz-graph-queries/build_fixture.py --small; do not edit by hand.\n"
    "-- Load into any schema: psql ... -f fixture.sql\n")

FENCE = re.compile(r"^```(\w*)[^\n]*\n(.*?)^```\s*$", re.M | re.S)
MARK = re.compile(r"<!--\s*verify:\s*(error|skip)\s*-->")


@dataclass
class Block:
    index: int
    sql: str
    mode: str


def extract_blocks(md: str) -> list[Block]:
    out, n = [], 0
    for m in FENCE.finditer(md):
        if m.group(1).lower() != "sql":
            continue
        before = md[:m.start()].rstrip()
        # the marker must be the last non-blank thing before the fence
        tail = before.splitlines()[-1] if before.splitlines() else ""
        mk = MARK.search(tail)
        mode = mk.group(1) if mk else "run"
        if mode == "skip":
            out.append(Block(0, m.group(2), "skip"))
            continue
        n += 1
        out.append(Block(n, m.group(2), mode))
    return out


def expected_path(name: str, index: int) -> Path:
    return EXPECTED / name / f"{index:02d}.txt"


def normalize(rows: list[list[str]]) -> str:
    return "".join("\t".join(r) + "\n" for r in sorted(rows))


def generated_fixture_sql() -> str:
    out = subprocess.run([sys.executable, str(HERE / "build_fixture.py"), "--small"],
                         capture_output=True, text=True, check=True).stdout
    return FIXTURE_HEADER + out


def load_fixture(schema: str) -> None:
    sql = subprocess.run([sys.executable, str(HERE / "build_fixture.py"), "--small", "--schema", schema],
                         capture_output=True, text=True, check=True).stdout
    mzclient.run(f"DROP SCHEMA IF EXISTS {schema} CASCADE;")
    r = mzclient.run(sql)
    if not r.ok:
        raise SystemExit(f"fixture load failed for {schema}: {r.stderr}")


def verify_file(path: Path, record: bool, keep: bool) -> int:
    name = path.stem
    schema = f"verify_{name.replace('-', '_')}"
    load_fixture(schema)
    fails = 0
    for b in extract_blocks(path.read_text()):
        if b.mode == "skip":
            continue
        r = mzclient.run(b.sql, schema=schema, cluster="quickstart", timeout_s=60)
        if b.mode == "error":
            actual = r.error_line + "\n"
            if r.ok:
                print(f"FAIL  {name} #{b.index}: expected an error, block succeeded")
                fails += 1
                continue
        else:
            if not r.ok:
                print(f"FAIL  {name} #{b.index}: {r.error_line or 'timed out'}")
                fails += 1
                continue
            actual = normalize(r.rows)
        exp = expected_path(name, b.index)
        if record:
            exp.parent.mkdir(parents=True, exist_ok=True)
            old = exp.read_text() if exp.exists() else None
            exp.write_text(actual)
            if old is not None and old != actual:
                print(f"CHANGED {name} #{b.index}")
                sys.stdout.writelines(difflib.unified_diff(old.splitlines(True), actual.splitlines(True)))
            else:
                print(f"RECORDED {name} #{b.index} ({len(actual.splitlines())} rows)")
            continue
        if not exp.exists():
            print(f"FAIL  {name} #{b.index}: no expected file {exp.relative_to(HERE)} (run with --record)")
            fails += 1
        elif exp.read_text() != actual:
            print(f"FAIL  {name} #{b.index}: output differs from {exp.relative_to(HERE)}")
            sys.stdout.writelines(difflib.unified_diff(exp.read_text().splitlines(True), actual.splitlines(True),
                                                       "expected", "actual"))
            fails += 1
        else:
            print(f"PASS  {name} #{b.index}")
    if not keep:
        mzclient.run(f"DROP SCHEMA IF EXISTS {schema} CASCADE;")
    return fails


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--record", action="store_true")
    ap.add_argument("--only", default=None)
    ap.add_argument("--keep", action="store_true")
    a = ap.parse_args()
    fails = 0
    fx_path = REFS / "fixture.sql"
    if not fx_path.exists() or fx_path.read_text() != generated_fixture_sql():
        if a.record:
            fx_path.write_text(generated_fixture_sql())
            print("RECORDED references/fixture.sql")
        else:
            print("FAIL  references/fixture.sql is out of date (run with --record)")
            fails += 1
    for path in sorted(REFS.glob("*.md")):
        if a.only and path.stem != a.only:
            continue
        fails += verify_file(path, a.record, a.keep)
    print(f"{'OK' if fails == 0 else 'FAILURES: ' + str(fails)}")
    return fails


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5: Run unit tests**

Run: `python3 -m unittest discover -s evals/mz-graph-queries/tests -v`
Expected: all PASS.

- [ ] **Step 6: End-to-end check with a throwaway reference file**

Create `skills/mz-graph-queries/references/zz-probe.md` containing:

````markdown
# probe

```sql
SELECT id, name FROM employees WHERE manager_id IS NULL;
```

<!-- verify: error -->
```sql
WITH MUTUALLY RECURSIVE bar(x int8) AS (SELECT '1') SELECT * FROM bar;
```
````

Run: `cd evals/mz-graph-queries && python3 verify_skill_sql.py --only zz-probe --record && python3 verify_skill_sql.py --only zz-probe`
Expected: first command prints `RECORDED zz-probe #1 (1 rows)`, `RECORDED zz-probe #2 (1 rows)`; `expected/zz-probe/01.txt` contains `1\tAda`; `expected/zz-probe/02.txt` starts with `ERROR:  WITH MUTUALLY RECURSIVE query "bar" declared types (bigint), but query returns types (text)`. Second command prints two `PASS` lines and `OK`. If the fixture check fails first, run `python3 verify_skill_sql.py --record` once (Task 1 step 7 wrote the file; the header must match exactly).

Then delete the probe: `rm skills/mz-graph-queries/references/zz-probe.md && rm -r evals/mz-graph-queries/expected/zz-probe`.

---

## Reference file tasks (4 to 12): shared procedure

Every reference file task follows the same steps; they are written out once here and each task lists only its content.

1. Write the file at `skills/mz-graph-queries/references/<name>.md` with the layout: a one-paragraph statement of what questions the file answers; a "Fixture tables" line naming the tables used (all files may assume `references/fixture.sql` is loaded); one `##` section per problem containing the pattern as a ```sql block, a sentence on the expected result on the fixture, the convergence argument in one or two sentences, and a "Standard SQL brings" paragraph naming the shape a Postgres or SQL Server user would write and what changes; a final `## Pitfalls` list.
2. Run `cd evals/mz-graph-queries && python3 verify_skill_sql.py --only <name> --record`. Every block must run (or error where marked). Fix SQL until the run is clean.
3. Open each `expected/<name>/NN.txt` and check it against the facts listed in the task. A mismatch means the SQL is wrong, not the fixture; fix the SQL and re-record.
4. Run `python3 verify_skill_sql.py --only <name>` and confirm every line is `PASS` and the last line `OK`.
5. Read the prose once for the Global Constraints style rules. Every claim about Materialize behavior must trace to the spec's semantics list or to a block verified in step 4.

SQL in the tasks below was drafted from verified test-suite and documentation patterns but has not been executed on the fixture; step 2 is where it gets proven. When a block needs a fix, keep the pattern and change the detail.

---

### Task 4: semantics.md

**Files:**
- Create: `skills/mz-graph-queries/references/semantics.md`
- Create: `evals/mz-graph-queries/expected/semantics/*.txt` (recorded)

**Interfaces:**
- Consumes: verifier from Task 3, small fixture.
- Produces: the section anchors the other files and `SKILL.md` link to: `#evaluation-model`, `#multisets-and-convergence`, `#binding-order-and-the-delay-idiom`, `#column-types`, `#recursion-limits`, `#what-the-optimizer-will-not-do`, `#reading-explain`, `#update-locality`, `#what-standard-sql-forbids-that-wmr-allows`.

Sections and blocks:

**Evaluation model.** State the three steps from the spec (bind empty, update each binding in order using current values, stop when nothing changes, evaluate the body). Block 1:

```sql
WITH MUTUALLY RECURSIVE
    counter(n int) AS (
        SELECT 1
        UNION
        SELECT n + 1 FROM counter WHERE n < 5
    )
SELECT n FROM counter ORDER BY n;
```
Expected rows 1 through 5.

**Multisets and convergence.** Bindings are multisets; the back edge consolidates but never deduplicates. Block 2, marked `<!-- verify: error -->`, is the docs' diverging shape on the fixture:

```sql
WITH MUTUALLY RECURSIVE (ERROR AT RECURSION LIMIT 20)
    reach(src text, dst text) AS (
        SELECT DISTINCT src, dst FROM transfers
        UNION ALL
        SELECT src, dst FROM reach
        UNION ALL
        SELECT r.src, t.dst FROM reach r JOIN transfers t ON r.dst = t.src
    )
SELECT src, dst FROM reach;
```
Expected error line begins `ERROR:  Evaluation error: Recursive query exceeded the recursion limit 20.` Block 3 shows how to look inside with `RETURN AT RECURSION LIMIT 2` and `SELECT src, dst, count(*) AS copies FROM reach GROUP BY src, dst ORDER BY src, dst` on the same binding; the recorded output shows every base pair with more than one copy, which is the growth that never stops. Block 4 is the fix: the same recursion with `UNION` in place of both `UNION ALL` and without the `SELECT src, dst FROM reach` branch, selecting `count(*)` from `reach`; expected `17` (the transitive closure of the fixture's transfers). State the rule: `UNION ALL` is correct only when every row derives once (trees, bounded counters) or feeds an aggregate that collapses each group.

**Binding order and the delay idiom.** A `Get` of a binding that appears at or before its own definition in the list reads the previous iteration's value, empty in round one. Block 5:

```sql
WITH MUTUALLY RECURSIVE
    start(pos int) AS (SELECT 0),
    head(pos int) AS (
        SELECT pos FROM start
        EXCEPT ALL
        SELECT pos FROM start_delayed
        UNION ALL
        SELECT CASE WHEN pos < 3 THEN pos + 1 ELSE pos END FROM head
    ),
    start_delayed(pos int) AS (SELECT pos FROM start)
SELECT pos FROM head;
```
Expected `3`. Walk the iterations in prose: round one `start_delayed` is empty so `head` is seeded with 0; from round two the seed cancels and the state advances; it stops moving at 3. Note that the optimizer never inlines across this edge, so the idiom is stable.

**Column types.** Declared types are mandatory, nullable, and applied as assignment casts. Block 6 (`verify: error`): `WITH MUTUALLY RECURSIVE bar(x int8) AS (SELECT '1') SELECT x FROM bar;` expected `ERROR:  WITH MUTUALLY RECURSIVE query "bar" declared types (bigint), but query returns types (text)`. Block 7: `WITH MUTUALLY RECURSIVE t(x numeric(38,2)) AS (SELECT 1.23456) SELECT x FROM t;` expected `1.23`. Block 8 (`verify: error`): a binding declared `(x int)` whose two `UNION` branches produce `int` and `text` (`SELECT 1 UNION SELECT 'a'`), to show the error surfaces before the recursion runs; record whatever error Materialize reports. State the fixes: typed literals (`'1'::int8`, `NULL::text`), and `::` casts on every branch of a `UNION`.

**Recursion limits.** No default. `ERROR AT RECURSION LIMIT n` fails the statement when iteration n still has changes; `RETURN AT RECURSION LIMIT n` returns the state after n iterations. Block 9: the counter from block 1 with `(RETURN AT RECURSION LIMIT 3)` and `WHERE n < 100`; expected 1, 2, 3. Say that limits are per block, survive view inlining, and that a divergent view installs successfully, never hydrates, and holds a hydration slot until dropped. Recommend `ERROR AT` on every maintained view with a limit well above the expected diameter, and `RETURN AT` for debugging and for fixed-iteration numeric methods.

**What the optimizer will not do.** A table: predicate pushdown into a recursive binding (never; write the filter inside the binding), projection pushdown (all declared columns are kept; carry narrow keys), cardinality estimates (unknown), constant folding across bindings (no), arrangements across the back edge (no; every join against the binding re-arranges it each iteration), imported indexes on base tables inside the loop (yes; the main lever), non-recursive prefix bindings (hoisted out of the loop).

**Reading EXPLAIN.** Block 10:

```sql
EXPLAIN WITH MUTUALLY RECURSIVE (ERROR AT RECURSION LIMIT 100)
    reach(src text, dst text) AS (
        SELECT src, dst FROM transfers
        UNION
        SELECT r.src, t.dst FROM reach r JOIN transfers t ON r.dst = t.src
    )
SELECT src, dst FROM reach;
```
Explain the shape in prose: the `With Mutually Recursive [recursion_limit=100]` header, one `cte lN =` block per recursive binding, a `Get lN` inside its own `cte` being the back edge, `Distinct` where `UNION` planned deduplication, `ArrangeBy` on the binding under the join, and `Return`. Note that `EXPLAIN WITH (linear chains)` is rejected for recursive plans.

**Update locality.** The docs' criterion in one paragraph: a maintained recursive view is cheap when one input change touches a bounded number of rows per iteration (reachability with redundant paths, a tree rollup of height h touches at most 2h rows). Name the patterns that violate it (naive PageRank, k-means, any all-pairs score) and say to compute those one-shot with `RETURN AT RECURSION LIMIT` or outside the database. No SQL.

**What standard SQL forbids that WMR allows.** A table with rows: aggregate in the recursive term, `DISTINCT`, `LEFT JOIN` with the binding on the outer side, referencing the binding more than once (non-linear recursion), subquery or `NOT EXISTS` over the binding, `ORDER BY ... LIMIT` and `DISTINCT ON` inside, more than one recursive relation (mutual recursion), nested recursive blocks, no base case required. Each row says what it unlocks (min per key, one witness path, overrides, halving iterations).

Facts to check in recorded outputs: block 1 five rows; block 3 every row has `copies` greater than 1 for base pairs; block 4 is `17`; block 5 is `3`; block 7 is `1.23`; block 9 is 1, 2, 3.

---

### Task 5: hierarchies.md

**Files:**
- Create: `skills/mz-graph-queries/references/hierarchies.md`
- Create: `evals/mz-graph-queries/expected/hierarchies/*.txt`

**Interfaces:**
- Consumes: fixture table `employees(id, manager_id, name, salary)`.
- Produces: patterns named `subtree`, `chain`, `levels`, `rooted`, `closure`, `paths` that `rollups.md`, `SKILL.md`, and the eval prompts refer to by these names.

Sections and blocks:

**Descendants of one node.** Block 1:

```sql
WITH MUTUALLY RECURSIVE
    subtree(id int) AS (
        SELECT id FROM employees WHERE manager_id = 2
        UNION
        SELECT e.id FROM employees e JOIN subtree s ON e.manager_id = s.id
    )
SELECT id FROM subtree ORDER BY id;
```
Expected 4, 5, 7, 8. Convergence: monotone set, one new level per iteration, iterations equal subtree height. Standard SQL brings the same shape with an anchor and `UNION ALL`; here `UNION` is what keeps a cyclic manager chain from looping.

**Ancestors of one node.** Block 2:

```sql
WITH MUTUALLY RECURSIVE
    chain(id int, distance int) AS (
        SELECT manager_id, 1 FROM employees WHERE id = 7 AND manager_id IS NOT NULL
        UNION
        SELECT e.manager_id, c.distance + 1
        FROM chain c JOIN employees e ON e.id = c.id
        WHERE e.manager_id IS NOT NULL
    )
SELECT id, distance FROM chain ORDER BY distance;
```
Expected (4,1), (2,2), (1,3).

**Depth and root for every node.** Block 3 seeds from every root and carries both depth and root:

```sql
WITH MUTUALLY RECURSIVE
    levels(id int, depth int, root_id int) AS (
        SELECT id, 0, id FROM employees WHERE manager_id IS NULL
        UNION
        SELECT e.id, l.depth + 1, l.root_id
        FROM employees e JOIN levels l ON e.manager_id = l.id
    )
SELECT id, depth, root_id FROM levels ORDER BY depth, id;
```
Expected depths as in Task 1 (Ada 0 through Gus and Hal 3), all `root_id` 1. Say that "level" means depth from the root here; height above the leaves is a different recursion (in `rollups.md` as `max` over children).

**A maintained closure table.** Block 4 creates a view and index; block 5 reads it:

```sql
CREATE VIEW employee_closure AS
WITH MUTUALLY RECURSIVE (ERROR AT RECURSION LIMIT 1000)
    closure(ancestor int, descendant int, distance int) AS (
        SELECT id, id, 0 FROM employees
        UNION
        SELECT c.ancestor, e.id, c.distance + 1
        FROM closure c JOIN employees e ON e.manager_id = c.descendant
    )
SELECT ancestor, descendant, distance FROM closure;

CREATE INDEX employee_closure_by_ancestor ON employee_closure (ancestor);
```

```sql
SELECT descendant, distance FROM employee_closure WHERE ancestor = 2 ORDER BY distance, descendant;
```
Expected (2,0), (4,1), (5,1), (7,2), (8,2). Explain that this is Karwin's closure table maintained for free, that the index makes subtree lookups point reads, and that the `ERROR AT` limit is the guardrail against a corrupt manager chain.

**Ordered display with a path.** Block 6:

```sql
WITH MUTUALLY RECURSIVE
    paths(id int, path text list) AS (
        SELECT id, LIST[name] FROM employees WHERE manager_id IS NULL
        UNION
        SELECT e.id, p.path || e.name
        FROM employees e JOIN paths p ON e.manager_id = p.id
    )
SELECT repeat('  ', list_length(path) - 1) || e.name AS tree, path
FROM paths p JOIN employees e USING (id)
ORDER BY path;
```
Expected first row `Ada`, then `  Bob`, `    Dee`, `      Gus`, `      Hal`, `    Eli`, `  Cy`, `    Fay`. If `ORDER BY` on a list is rejected, check the list functions available on the emulator (`SELECT name FROM mz_catalog.mz_functions WHERE name LIKE 'list%'`), order by a text rendering of the path instead, and record what works. Siblings sort by name because the path is names; sort by a `(sort_key, name)` list when a different sibling order is wanted.

**Cycles in a "tree".** Block 7 uses inline data so the fixture stays a tree:

```sql
WITH MUTUALLY RECURSIVE
    looped(id int, manager_id int) AS (
        SELECT id, manager_id FROM (VALUES (10, 12), (11, 10), (12, 11), (13, 10)) AS v(id, manager_id)
    ),
    subtree(id int) AS (
        SELECT id FROM looped WHERE manager_id = 10
        UNION
        SELECT l.id FROM looped l JOIN subtree s ON l.manager_id = s.id
    )
SELECT id FROM subtree WHERE id <> 10 ORDER BY id;
```
Expected 11, 12, 13. Say that the same query with `UNION ALL` never returns, and that the body's `WHERE id <> 10` is needed because the cycle makes the root its own descendant. Block 8 audits the data: nodes that are their own ancestor, using the closure pattern over `looped` and `WHERE ancestor = descendant AND distance > 0`; expected 10, 11, 12.

**Pitfalls.** Depth column breaks `UNION` deduplication on DAGs (each path is a new row); orphans (manager_id pointing at a missing row) never appear under any root; carrying `name` or other payload through the loop keeps every column live in the arrangement, so join it back in the body as the display block does.

---

### Task 6: rollups.md

**Files:**
- Create: `skills/mz-graph-queries/references/rollups.md`
- Create: `evals/mz-graph-queries/expected/rollups/*.txt`

**Interfaces:**
- Consumes: `employees`, `parts`, `bom`; the `subtree` pattern name from Task 5.
- Produces: patterns `team` (bottom-up sum with `LEFT JOIN` on the binding), `totals` (folder-totals form), `height`, `needed` (BOM explosion), `needed_agg` (BOM with the aggregate inside).

Sections and blocks:

**Sum along a tree, aggregate inside the binding.** Block 1, the docs' hierarchy pattern:

```sql
WITH MUTUALLY RECURSIVE
    team(id int, manager_id int, total int) AS (
        SELECT e.id, e.manager_id, e.salary + coalesce(sum(t.total), 0)::int
        FROM employees e LEFT JOIN team t ON t.manager_id = e.id
        GROUP BY e.id, e.manager_id, e.salary
    )
SELECT id, total FROM team ORDER BY id;
```
Expected totals: 1 → 1195, 2 → 605, 3 → 290, 4 → 295, 5 → 110, 6 → 100, 7 → 90, 8 → 85. Convergence: each node's total changes at most once per level below it, so the loop runs height plus one iterations and every iteration touches only the nodes whose children changed. No `UNION` anywhere: the binding is a plain query over itself. Standard SQL brings "build the closure, join facts on the descendant, `GROUP BY` ancestor", which is quadratic in subtree size and cannot be maintained without recomputation.

**Folder-totals form.** Block 2, the same answer with `UNION ALL` feeding a collapsing `sum`:

```sql
WITH MUTUALLY RECURSIVE
    totals(id int, total int) AS (
        SELECT id, sum(amount)::int
        FROM (
            SELECT id, salary AS amount FROM employees
            UNION ALL
            SELECT e.manager_id, t.total
            FROM totals t JOIN employees e ON e.id = t.id
            WHERE e.manager_id IS NOT NULL
        ) AS x(id, amount)
        GROUP BY id
    )
SELECT id, total FROM totals ORDER BY id;
```
Expected identical to block 1. Say when to prefer which: block 1 when the parent pointer lives on the node, block 2 when contributions come from a separate table (files in folders).

**Height above the leaves.** Block 3:

```sql
WITH MUTUALLY RECURSIVE
    height(id int, manager_id int, h int) AS (
        SELECT e.id, e.manager_id, coalesce(max(c.h) + 1, 0)
        FROM employees e LEFT JOIN height c ON c.manager_id = e.id
        GROUP BY e.id, e.manager_id
    )
SELECT id, h FROM height ORDER BY h DESC, id;
```
Expected Ada 3, Bob 2, Dee 1, Cy 1, leaves 0. Pair it with `levels` in `hierarchies.md` to settle the "level" ambiguity.

**Bill of materials, quantities multiply along each path.** Block 4:

```sql
WITH MUTUALLY RECURSIVE
    needed(part_id int, qty int) AS (
        SELECT child_id, qty FROM bom WHERE parent_id = 1
        UNION ALL
        SELECT b.child_id, n.qty * b.qty
        FROM needed n JOIN bom b ON b.parent_id = n.part_id
    )
SELECT part_id, sum(qty) AS qty FROM needed GROUP BY part_id ORDER BY part_id;
```
Expected (2,2), (3,1), (4,64), (5,14), (6,2). `UNION ALL` is correct here because a BOM is a DAG: every path derives exactly once, and the bolt's two paths (8 via wheels, 6 via the frame) must both count. Convergence: finite paths. Guardrail: a cycle in the BOM (a part containing itself) makes this diverge, so a maintained version carries `ERROR AT RECURSION LIMIT`.

**The same with the aggregate inside.** Block 5:

```sql
WITH MUTUALLY RECURSIVE
    needed_agg(part_id int, qty int) AS (
        SELECT child_id, sum(q)::int
        FROM (
            SELECT child_id, qty AS q FROM bom WHERE parent_id = 1
            UNION ALL
            SELECT b.child_id, n.qty * b.qty
            FROM needed_agg n JOIN bom b ON b.parent_id = n.part_id
        ) AS x(child_id, q)
        GROUP BY child_id
    )
SELECT part_id, qty FROM needed_agg ORDER BY part_id;
```
Expected identical to block 4. Explain why it is equivalent (the total for a part is the sum over its parents of the parent's total times the edge quantity) and why it is the better maintained form: one row per part in the loop instead of one per path.

**Kit cost.** Block 6 joins block 5's result to `parts` and sums `qty * unit_cost` where `unit_cost IS NOT NULL`. Expected `73.40` (record the exact numeric formatting Materialize prints).

**Shared components: once or per path.** Block 7 counts distinct parts under the kit with `UNION` (expected 5 rows, bolt once) and per-path rows with `UNION ALL` (expected 6 rows, bolt twice), side by side as two statements in one block that each return `count(*)`; explain that org charts and chart-of-accounts want "once", bills of materials want "per path", and the query must say which.

**Pitfalls.** Own value in or out of the total (block 1 includes it; subtract `salary` in the body to exclude); DAG double counting when a tree pattern is applied to multi-parent data (block 1's shape on a DAG counts a shared child once per parent path, which is wrong for headcount and right for quantities); signed or custom rollups (chart of accounts with contra accounts) need a sign column multiplied in, not a plain sum; a cycle in the data diverges under `UNION ALL`.

---

### Task 7: reachability.md

**Files:**
- Create: `skills/mz-graph-queries/references/reachability.md`
- Create: `evals/mz-graph-queries/expected/reachability/*.txt`

**Interfaces:**
- Consumes: `accounts`, `transfers`, `pipelines`, `depends_on`.
- Produces: patterns `reach` (linear, seeded), `closure` (whole graph), `hops` (k-hop with min), `on_cycle`, `level` (topological), `downstream`, `upstream`.

Sections and blocks:

**Everything reachable from a seed.** Block 1:

```sql
WITH MUTUALLY RECURSIVE
    reach(dst text) AS (
        SELECT dst FROM transfers WHERE src = 'a1'
        UNION
        SELECT t.dst FROM reach r JOIN transfers t ON t.src = r.dst
    )
SELECT dst FROM reach ORDER BY dst;
```
Expected a1, a2, a3, a4, a5 (a1 reaches itself around the ring). Convergence: monotone set. Iterations equal the longest shortest path from the seed.

**Whole-graph closure.** Block 2, linear form over all sources, returning `count(*)` (expected 17). Block 3, the non-linear form `SELECT c1.src, c2.dst FROM closure c1 JOIN closure c2 ON c1.dst = c2.src`, same count; explain that it halves the iteration count and squares the intermediate size, so it suits small dense graphs and one-shot queries more than maintained views.

**Within k hops.** Block 4:

```sql
WITH MUTUALLY RECURSIVE
    hops(dst text, hops int) AS (
        SELECT dst, min(hops)
        FROM (
            SELECT dst, 1 FROM transfers WHERE src = 'a1'
            UNION ALL
            SELECT t.dst, h.hops + 1
            FROM hops h JOIN transfers t ON t.src = h.dst
            WHERE h.hops < 3
        ) AS x(dst, hops)
        GROUP BY dst
    )
SELECT dst, hops FROM hops WHERE dst <> 'a1' ORDER BY hops, dst;
```
Expected (a2,1), (a3,2), (a4,3). Say why the bound is inside the binding (the optimizer does not push predicates into recursive bindings) and why `min` is inside (a node reached two ways stays one row). Name the mis-specification: "all the paths within three hops" almost always means this set; enumerating paths is exponential and rarely wanted.

**Edges that expire.** Block 5 is block 1 with `WHERE src = 'a1' AND mz_now() <= ts + interval '10 years'` in the base case and `AND mz_now() <= t.ts + interval '10 years'` on the join; same expected rows. Say that a temporal filter inside the binding makes the closure shrink as edges age out, and that the result is maintained, not recomputed.

**Cycle membership.** Block 6 selects `src` from the whole-graph closure where `src = dst`; expected a1, a2, a3. Say that set semantics make cycles harmless for termination and that this query is the cheap "is anything circular" audit; the structure of the cycles is the SCC problem in `components.md`.

**Topological level on a DAG.** Block 7:

```sql
WITH MUTUALLY RECURSIVE
    level(task text, level int) AS (
        SELECT task, max(level)
        FROM (
            SELECT p.id, 0
            FROM pipelines p
            WHERE NOT EXISTS (SELECT 1 FROM depends_on d WHERE d.task = p.id)
            UNION ALL
            SELECT d.task, l.level + 1
            FROM level l JOIN depends_on d ON d.prereq = l.task
        ) AS x(task, level)
        GROUP BY task
    )
SELECT task, level FROM level ORDER BY level, task;
```
Expected raw_orders 0, raw_customers 0, stg_orders 1, stg_customers 1, fct_sales 2, rpt_daily 3, rpt_churn 3. Convergence: on a DAG each task's `max` rises at most as many times as it has ancestors levels; on a cyclic graph it never converges, so a maintained version carries `ERROR AT RECURSION LIMIT` and the cycle audit above runs first. Standard SQL brings "traverse every path, `GROUP BY` with `MAX(depth)` outside", which is exponential in path count.

**Impact analysis.** Block 8, downstream of `raw_customers` (expected stg_customers, fct_sales, rpt_daily, rpt_churn); block 9, upstream of `rpt_churn` (expected raw_orders, raw_customers, stg_orders, stg_customers, fct_sales). Both are block 1 with the edge direction chosen. Say which direction answers "what breaks if I change this" and which answers "why is this wrong".

**Pitfalls.** `UNION ALL` on a graph with a cycle never terminates; a path or depth column defeats `UNION` deduplication (use `min` as in block 4); direction is often unstated; whole-graph closure on a dense graph approaches `n^2` rows.

---

### Task 8: shortest-paths.md

**Files:**
- Create: `skills/mz-graph-queries/references/shortest-paths.md`
- Create: `evals/mz-graph-queries/expected/shortest-paths/*.txt`

**Interfaces:**
- Consumes: `cities`, `roads`.
- Produces: patterns `sym` (symmetrized edges), `hops`, `dist`, `best` (argmin with breadcrumb), `route` (path reconstruction).

Sections and blocks:

**Symmetrize once.** Every block starts with a non-recursive binding that the optimizer hoists out of the loop:

```sql
    sym(src text, dst text, km int) AS (
        SELECT src, dst, km FROM roads
        UNION ALL
        SELECT dst, src, km FROM roads
    ),
```

**Fewest hops.** Block 1:

```sql
WITH MUTUALLY RECURSIVE
    sym(src text, dst text, km int) AS (
        SELECT src, dst, km FROM roads
        UNION ALL
        SELECT dst, src, km FROM roads
    ),
    hops(city text, hops int) AS (
        SELECT city, min(hops)
        FROM (
            SELECT 'A', 0
            UNION ALL
            SELECT s.dst, h.hops + 1
            FROM hops h JOIN sym s ON s.src = h.city
        ) AS x(city, hops)
        GROUP BY city
    )
SELECT city, hops FROM hops WHERE city <> 'A' ORDER BY hops, city;
```
Expected (B,1), (C,1), (D,2), (E,3). Convergence: every city's minimum can only fall, and it is bounded below by zero. Note that the recursion reads `hops`, the reduced relation, so only current minima are extended.

**Cheapest route.** Block 2 is block 1 with `km` summed and `min(km)`; expected (B,4), (C,7), (D,9), (E,14). Point out that D is two hops away but nine kilometres, three hops, by the cheaper route; hop count and weight are different questions. Convergence needs positive weights: a negative cycle makes the minimum fall forever. Standard SQL brings Dijkstra in a procedure or an enumerate-all-paths CTE with `MIN` outside and a visited-string cycle check; both disappear here.

**One witness path.** Block 3 keeps a breadcrumb and reconstructs one route in the same block:

```sql
WITH MUTUALLY RECURSIVE
    sym(src text, dst text, km int) AS (
        SELECT src, dst, km FROM roads
        UNION ALL
        SELECT dst, src, km FROM roads
    ),
    best(city text, km int, prev text) AS (
        SELECT DISTINCT ON (city) city, km, prev
        FROM (
            SELECT 'A', 0, NULL::text
            UNION ALL
            SELECT s.dst, b.km + s.km, b.city
            FROM best b JOIN sym s ON s.src = b.city
        ) AS x(city, km, prev)
        ORDER BY city, km, prev
    ),
    route(city text, step int) AS (
        SELECT 'E', 0
        UNION
        SELECT b.prev, r.step + 1
        FROM route r JOIN best b ON b.city = r.city
        WHERE b.prev IS NOT NULL
    )
SELECT city, step FROM route ORDER BY step DESC;
```
Expected A, B, C, D, E in that order (steps 4 down to 0). Explain `DISTINCT ON` as argmin with a deterministic tiebreak on `prev`, why one witness is usually what "the shortest path" means, and that all shortest paths is a different and larger answer.

**One target.** Block 4 filters block 2 in the body with `WHERE city = 'E'` (expected (E,14)) and explains that the filter stays in the body: the loop still explores everything because predicates are not pushed into recursive bindings, and pruning must be written inside the binding when it matters.

**Pitfalls.** Roads stored one way and not symmetrized (results become one-directional); negative weights; asking for path length when reachability was meant; `UNION` without the `min` (each new `km` is a new row, so the loop enumerates walks around cycles forever).

---

### Task 9: components.md

**Files:**
- Create: `skills/mz-graph-queries/references/components.md`
- Create: `evals/mz-graph-queries/expected/components/*.txt`

**Interfaces:**
- Consumes: `customers`, `customer_links`, `accounts`, `transfers`.
- Produces: patterns `links` (thresholded, symmetrized), `label` (min-label propagation), `scc_closure`, `scc_trim` (nested forward and backward propagation).

Sections and blocks:

**Connected components by min-label propagation.** Block 1:

```sql
WITH MUTUALLY RECURSIVE
    links(a text, b text) AS (
        SELECT a, b FROM customer_links WHERE score >= 0.5
        UNION
        SELECT b, a FROM customer_links WHERE score >= 0.5
    ),
    label(id text, comp text) AS (
        SELECT id, min(comp)
        FROM (
            SELECT id, id FROM customers
            UNION ALL
            SELECT l.b, lb.comp
            FROM links l JOIN label lb ON lb.id = l.a
        ) AS x(id, comp)
        GROUP BY id
    )
SELECT id, comp FROM label ORDER BY id;
```
Expected c1, c2, c3 → c1; c4, c5 → c4; c6 → c6; c7 → c7. Convergence: labels only decrease and are bounded by the smallest id; iterations track the component diameter. Memory stays one row per node, which is the point of putting `min` inside; the standard-SQL shape (reach sets then `MIN` outside) is quadratic in component size.

**Threshold changes the answer.** Block 2 is block 1 at `score >= 0.3`, selecting only `id IN ('c4', 'c5', 'c6')`; expected all three → c4.

**Entity resolution.** Prose: the same query where `customer_links` holds pairwise match scores is the clustering step of entity resolution; the threshold is the match cutoff; the label is the golden-record id. Pitfalls specific to it: chains (A~B~C~Z clusters A with Z), unstable ids when a smaller id joins later (pick the oldest id or a stable surrogate as the label instead of the minimum), and users who expect cliques.

**Strongly connected components from the closure.** Block 3:

```sql
WITH MUTUALLY RECURSIVE
    reach(src text, dst text) AS (
        SELECT src, dst FROM transfers
        UNION
        SELECT r.src, t.dst FROM reach r JOIN transfers t ON t.src = r.dst
    )
SELECT a.id, coalesce(least(a.id, min(m.dst)), a.id) AS component
FROM accounts a
LEFT JOIN (
    SELECT r1.src, r1.dst
    FROM reach r1 JOIN reach r2 ON r1.src = r2.dst AND r1.dst = r2.src
) m ON m.src = a.id
GROUP BY a.id
ORDER BY a.id;
```
Expected a1, a2, a3 → a1; a4 through a7 → themselves. Say when this is the right form: the closure is wanted anyway, or the graph is small.

**Strongly connected components without the closure.** Block 4 adapts the test-suite pattern (forward and backward label propagation over edges trimmed to those whose endpoints share both labels, seeded once with the delay idiom):

```sql
WITH MUTUALLY RECURSIVE
    intra(src text, dst text) AS (
        SELECT src, dst FROM transfers
        EXCEPT ALL
        SELECT src, dst FROM transfers_delayed
        UNION ALL
        SELECT t.src, t.dst
        FROM transfers t
        JOIN fwd f_src ON f_src.node = t.src
        JOIN fwd f_dst ON f_dst.node = t.dst
        JOIN bwd b_src ON b_src.node = t.src
        JOIN bwd b_dst ON b_dst.node = t.dst
        WHERE f_src.label = f_dst.label AND b_src.label = b_dst.label
    ),
    fwd(node text, label text) AS (
        WITH MUTUALLY RECURSIVE
            l(node text, comp text) AS (
                SELECT node, min(comp)
                FROM (
                    SELECT id, id FROM accounts
                    UNION ALL
                    SELECT i.dst, l.comp FROM intra i JOIN l ON l.node = i.src
                ) AS x(node, comp)
                GROUP BY node
            )
        SELECT node, comp FROM l
    ),
    bwd(node text, label text) AS (
        WITH MUTUALLY RECURSIVE
            l(node text, comp text) AS (
                SELECT node, min(comp)
                FROM (
                    SELECT id, id FROM accounts
                    UNION ALL
                    SELECT i.src, l.comp FROM intra i JOIN l ON l.node = i.dst
                ) AS x(node, comp)
                GROUP BY node
            )
        SELECT node, comp FROM l
    ),
    transfers_delayed(src text, dst text) AS (SELECT src, dst FROM transfers)
SELECT node, label AS component FROM fwd ORDER BY node;
```
Expected identical to block 3. Explain the mechanism: round one keeps every edge; each later round keeps only edges whose endpoints agree on both a forward and a backward label, which is exactly membership in one SCC; the nested blocks recompute labels over the trimmed edges until nothing changes. This is the form the docs point to for SCC without a closure table. If Materialize rejects the duplicate binding name `l` across the two nested blocks, rename them `lf` and `lb`.

**Pitfalls.** Forgetting to symmetrize turns components into forward reachability sets; a directed relation ("paid", "reports to") treated as undirected; `min(id)` labels shift when data arrives; "connected" on a directed graph without saying weak or strong; asking for cycles when the need is SCCs (there can be exponentially many simple cycles per SCC).

---

### Task 10: permissions.md

**Files:**
- Create: `skills/mz-graph-queries/references/permissions.md`
- Create: `evals/mz-graph-queries/expected/permissions/*.txt`

**Interfaces:**
- Consumes: `groups`, `memberships`, `permissions`.
- Produces: patterns `effective` (group inheritance with override), `user_access` (maintained view for point checks), `holds` (ReBAC relation-tuple reachability).

Sections and blocks:

**Inheritance down a group tree with overrides.** Block 1:

```sql
WITH MUTUALLY RECURSIVE
    effective(group_id text, doc_id text, level text) AS (
        SELECT group_id, doc_id, level FROM permissions
        UNION
        SELECT g.id, e.doc_id, e.level
        FROM groups g JOIN effective e ON e.group_id = g.parent_id
        WHERE NOT EXISTS (
            SELECT 1 FROM permissions p
            WHERE p.group_id = g.id AND p.doc_id = e.doc_id
        )
    )
SELECT group_id, doc_id, level FROM effective ORDER BY group_id, doc_id;
```
Expected g1 doc1 read; g2 doc1 read; g2 doc2 edit; g3 doc1 edit; g3 doc2 edit; g4 doc1 read. The `NOT EXISTS` is over the base table, not the binding, so the recursion stays monotone and converges on any group graph, cycles included. Standard SQL forbids the subquery in the recursive member and forces "compute all inherited rows, then remove overridden ones outside", which cannot express "an override stops inheritance for everything below it".

**Per user, and a point check.** Block 2 creates the maintained view and index:

```sql
CREATE VIEW user_access AS
WITH MUTUALLY RECURSIVE (ERROR AT RECURSION LIMIT 100)
    effective(group_id text, doc_id text, level text) AS (
        SELECT group_id, doc_id, level FROM permissions
        UNION
        SELECT g.id, e.doc_id, e.level
        FROM groups g JOIN effective e ON e.group_id = g.parent_id
        WHERE NOT EXISTS (
            SELECT 1 FROM permissions p
            WHERE p.group_id = g.id AND p.doc_id = e.doc_id
        )
    )
SELECT DISTINCT m.user_id, e.doc_id, e.level
FROM memberships m JOIN effective e ON e.group_id = m.group_id;

CREATE INDEX user_access_by_user_doc ON user_access (user_id, doc_id);
```
Block 3 lists everything (`SELECT user_id, doc_id, level FROM user_access ORDER BY 1, 2, 3`; expected u1 doc1 edit, u1 doc2 edit, u2 doc1 read, u3 doc1 read, u3 doc2 edit). Block 4 is the point check `SELECT level FROM user_access WHERE user_id = 'u1' AND doc_id = 'doc1'` (expected `edit`), and the prose says this is an index lookup that stays current as groups and permissions change, which is the shape an authorization service wants.

**Denies.** Prose plus block 5: model a deny as an explicit row with `level = 'none'`; block 1's override rule already stops inheritance below it, and the body filters `WHERE level <> 'none'`. Demonstrate with inline `VALUES` data rather than changing the fixture: a three-group chain where the middle group has `('none')` on a doc the root grants; expected the leaf has no row for that doc.

**Relationship-based access (Zanzibar shape).** Block 6 on inline tuples:

```sql
WITH MUTUALLY RECURSIVE
    tuples(object text, relation text, subject text) AS (
        SELECT object, relation, subject FROM (VALUES
            ('folder:f1', 'viewer', 'user:ann'),
            ('doc:d1', 'parent', 'folder:f1'),
            ('doc:d1', 'editor', 'user:bob')) AS v(object, relation, subject)
    ),
    holds(object text, relation text, user_id text) AS (
        SELECT object, relation, subject FROM tuples WHERE subject LIKE 'user:%'
        UNION
        SELECT object, 'viewer', user_id FROM holds WHERE relation = 'editor'
        UNION
        SELECT t.object, 'viewer', h.user_id
        FROM tuples t JOIN holds h ON h.object = t.subject AND h.relation = 'viewer'
        WHERE t.relation = 'parent'
    )
SELECT object, relation, user_id FROM holds ORDER BY object, relation, user_id;
```
Expected doc:d1 editor user:bob; doc:d1 viewer user:ann; doc:d1 viewer user:bob; folder:f1 viewer user:ann. Map the three branches to Zanzibar's `this`, `computed_userset`, and `tuple_to_userset`; a check is `EXISTS` over `holds`; nested groups are one more branch that follows `member` tuples. Note that intersection and exclusion rules are non-monotone and belong in the body or in a `NOT EXISTS` over base tuples, as in block 1.

**Pitfalls.** Multiple inheritance paths produce duplicate rows (`UNION` handles it); a cyclic group graph is harmless for block 1 but a `UNION ALL` version never returns; "can this user see X" needs a point check, "list everything the user can see" is the full expansion and can be large; the override rule must be stated by the user, since "nearest explicit wins" and "most permissive wins" are both common.

---

### Task 11: migrating.md

**Files:**
- Create: `skills/mz-graph-queries/references/migrating.md`
- Create: `evals/mz-graph-queries/expected/migrating/*.txt`

**Interfaces:**
- Consumes: patterns from Tasks 5 to 9 by name.
- Produces: a translation table other files link to as `migrating.md#translation-table`.

Foreign-dialect examples use ```postgresql fences (never run); each Materialize translation is a ```sql block (verified).

Sections:

**Translation table.** Rows: `WITH RECURSIVE name AS (anchor UNION ALL recursive)` → `WITH MUTUALLY RECURSIVE name(cols types) AS (anchor UNION recursive)`; `UNION ALL` → `UNION` unless every row derives once; `OPTION (MAXRECURSION n)`, `cte_max_recursion_depth`, BigQuery's fixed limit → `ERROR AT RECURSION LIMIT n`; `CYCLE col SET ... USING path`, `ARRAY[id]` and `id = ANY(path)` guards, `NOCYCLE` → nothing (set semantics) or `min(depth)` when depth is wanted; `WHERE depth < k` as a cycle guard → drop; as a hop bound → keep inside the binding; `LEVEL` → depth column; `CONNECT_BY_ROOT` → root column carried from the seed; `SYS_CONNECT_BY_PATH` → `text list` path; `ORDER SIBLINGS BY` → `ORDER BY path`; `START WITH ... CONNECT BY PRIOR` → seed and join; `ORDER BY` inside the recursive term (SQLite BFS or DFS) → has no evaluation-order meaning here, order the body; DuckDB `USING KEY` with `recurring.` → aggregate inside the binding; window function per level → aggregate inside the binding; "enumerate paths then `MIN` outside" → `min` inside.

**Anchor and recursive member.** Postgres descendants in a ```postgresql block, then the WMR version (block 1, the `subtree` query from `hierarchies.md` verbatim, expected 4, 5, 7, 8). Call out the three edits: column types, `UNION`, and no restriction on where the binding is referenced.

**Depth guards.** Postgres cycle-safe traversal with `path` array and `is_cycle` in ```postgresql, then block 2: `hops` from `reachability.md` verbatim (expected (a2,1), (a3,2), (a4,3)); explain which guard survives (the hop bound, moved inside) and which dies (the cycle check).

**Oracle CONNECT BY.** An Oracle hierarchy with `LEVEL`, `CONNECT_BY_ROOT`, `SYS_CONNECT_BY_PATH`, `ORDER SIBLINGS BY` in ```postgresql, then block 3 combining `levels` (depth and root) with the path list from `hierarchies.md`:

```sql
WITH MUTUALLY RECURSIVE
    tree(id int, depth int, root_id int, path text list) AS (
        SELECT id, 1, id, LIST[name] FROM employees WHERE manager_id IS NULL
        UNION
        SELECT e.id, t.depth + 1, t.root_id, t.path || e.name
        FROM employees e JOIN tree t ON e.manager_id = t.id
    )
SELECT id, depth AS level, root_id, path FROM tree ORDER BY path;
```
Expected eight rows, Ada first with level 1 (Oracle's `LEVEL` starts at 1, so this block does too).

**DuckDB USING KEY and the enumerate-then-aggregate habit.** The DuckDB distance-vector routing query in ```postgresql, then block 4: `dist` from `shortest-paths.md` verbatim (expected (B,4), (C,7), (D,9), (E,14)). Then Halford's `walks` then `MIN` components in ```postgresql and block 5: `label` from `components.md` verbatim (expected the seven labels). State the general rule: whatever the outer aggregate was, move it inside the binding and recurse from the reduced relation.

**Semantics that differ silently.** Bullet list: multiset bindings (a `UNION ALL` that was harmless under Postgres's working-table semantics diverges here); the recursive term sees the whole current binding, not last iteration's new rows; window functions and aggregates apply to the whole binding, not "the current level"; no linear-recursion rule; Feldera-style implicit `DISTINCT` does not exist here.

---

### Task 12: context-graphs.md

**Files:**
- Create: `skills/mz-graph-queries/references/context-graphs.md`
- Create: `evals/mz-graph-queries/expected/context-graphs/*.txt`

**Interfaces:**
- Consumes: pattern names from Tasks 5 to 10; `skills/mz-ontology-design/references/relationships.sql` (read it for the registry's column names before writing the registry section).

Sections:

**What people mean.** Two sentences: the term covers decision-trace graphs (Foundation Capital), metadata and lineage graphs (catalog vendors), agent-memory graphs, and Materialize's sense: a set of live, governed data products with maintained relationships between them. Every sense needs the same traversals, and those are the patterns in this skill.

**Agent questions to patterns.** A table: "what is related to X within n hops" → `hops` in `reachability.md`; "what breaks if X changes" → `downstream`; "why is X wrong, what fed it" → `upstream`; "which precedent or decision chain led here" → `chain` in `hierarchies.md` over a `caused_by` edge, carrying depth; "is this the same customer as that one" → `label` in `components.md` over match edges; "can this agent see this record" → `user_access` in `permissions.md`; "what did the relationship graph look like when the decision was made" → the as-of filter below; "who is in the same ring" → `scc_trim` in `components.md`.

**Edges from the relationship registry.** Read `skills/mz-ontology-design/references/relationships.sql`, then describe in prose and one `<!-- verify: skip -->` ```sql sketch how to build a typed edge relation from registered reference edges: one `SELECT` per registered relationship producing `(src_object, src_id, dst_object, dst_id, relationship)`, unioned into an `edges` view, which every pattern in this skill then walks with the object type carried as part of the key. Say that identity resolution belongs in `core.internal` per the ontology skill and this skill only walks the edges it publishes.

**As-of traversal on effective-dated edges.** Block 1 on the fixture:

```sql
WITH MUTUALLY RECURSIVE
    reach(dst text) AS (
        SELECT dst FROM transfers
        WHERE src = 'a1' AND ts <= TIMESTAMP '2026-01-01 00:03:30'
        UNION
        SELECT t.dst
        FROM reach r JOIN transfers t ON t.src = r.dst
        WHERE t.ts <= TIMESTAMP '2026-01-01 00:03:30'
    )
SELECT dst FROM reach ORDER BY dst;
```
Expected a1, a2, a3 (the a3 → a4 transfer at 00:04 is after the cutoff). Explain that a valid-from and valid-to pair on an edge table is filtered the same way inside the binding, that the filter must be inside because predicates are not pushed into recursive bindings, and that a maintained "current" graph uses `mz_now()` in place of the constant.

**Keep the loop narrow.** Prose: carry ids and the columns the recursion needs, join descriptive payload back in the body; index the edge relation on the join key; add `ERROR AT RECURSION LIMIT`; check update locality before making a traversal a maintained view that agents read constantly.

---

### Task 13: SKILL.md, README.md, DEVELOPMENT.md, and repo tables

**Files:**
- Create: `skills/mz-graph-queries/SKILL.md`
- Create: `skills/mz-graph-queries/README.md`
- Create: `skills/mz-graph-queries/DEVELOPMENT.md`
- Modify: `README.md` (root; the "Available Skills" section and the dated changelog list near the end)
- Modify: `CLAUDE.md` (the "Current Skills" table)
- Modify: `skills/materialize-debug-freshness/references/attribution.md` (the paragraph beginning "Walk the local chain in one query")

**Interfaces:**
- Consumes: all nine reference files and their section anchors.
- Produces: the skill manifest the eval runner mounts (`SKILL.md` plus `references/`).

- [ ] **Step 1: Write SKILL.md**

Frontmatter, exactly:

```yaml
---
name: mz-graph-queries
description: >
  Write correct, convergent, maintainable graph and hierarchy queries in
  Materialize with WITH MUTUALLY RECURSIVE. Use when a user asks for a
  recursive CTE or WITH RECURSIVE in Materialize, or for anything over a tree,
  hierarchy, or graph: org charts, bill of materials, category trees,
  descendants or ancestors, depth or level, rollups along a hierarchy,
  reachability or transitive closure, k-hop neighbours, shortest or cheapest
  path, connected components, entity resolution clusters, strongly connected
  components, cycle detection, topological order, lineage or dependency impact
  analysis, permission or role inheritance, or multi-hop traversal of a context
  graph. Also use when translating WITH RECURSIVE, CONNECT BY, or DuckDB USING
  KEY queries to Materialize, or when a recursive view never returns or never
  hydrates.
---
```

Body outline (target 180 to 240 lines), in this order:

1. Title `# Graph and hierarchy queries with WITH MUTUALLY RECURSIVE` and a three-sentence framing: bindings start empty, are updated in order until nothing changes, and the body runs on the fixpoint; any SQL is allowed inside a binding; the skill's job is to pick the pattern, make it converge, and keep it maintainable. Link `references/semantics.md#evaluation-model`.
2. `## Hand-offs`: freshness or lag of an existing recursive view → `materialize-debug-freshness`; memory or cost → `mz-optimize-memory`; how to model entities and relationships → `mz-ontology-design`. One line each.
3. `## Step 1: Classify the ask` with the four questions (structure, direction, output, lifetime) and a phrasing table. Rows (phrase → family → file): "everyone under", "reports to", "subtree" → descendants → `hierarchies.md`; "path to the top", "which division", "breadcrumb" → ancestors and root → `hierarchies.md`; "level", "depth", "how deep" → depth (say height is different) → `hierarchies.md`, `rollups.md`; "total under each", "roll up", "headcount", "how many of each part" → rollups → `rollups.md`; "connected to", "reachable", "downstream", "upstream", "impact", "lineage" → reachability → `reachability.md`; "within n hops", "all paths within" → k-hop with min → `reachability.md`; "shortest", "cheapest", "fewest hops", "route" → shortest paths → `shortest-paths.md`; "clusters", "groups of linked", "same customer", "duplicates", "rings" → components or SCC → `components.md`; "loop", "circular", "is this a tree" → cycle audit → `reachability.md`; "build order", "which first" → topological level → `reachability.md`; "effective permissions", "inherits access", "can user see" → permissions → `permissions.md`; "convert this WITH RECURSIVE / CONNECT BY" → `migrating.md`; "agent", "context graph", "knowledge graph traversal" → `context-graphs.md`. Then a short list of mis-specifications to resolve before writing: "all paths" usually means reachability; "connected" on a directed relation needs weak or strong; "total under" needs own-value and shared-child decisions; undirected data is often stored one way; "the shortest path" with ties means one witness unless stated.
4. `## Step 2: Write the recursion` with the five rules from the spec, each one sentence plus a link to the section that argues it, and one canonical skeleton block:

```sql
WITH MUTUALLY RECURSIVE (ERROR AT RECURSION LIMIT 1000)
    -- non-recursive prep (symmetrize, filter, type) is hoisted out of the loop
    edges(src text, dst text) AS (
        SELECT src, dst FROM base_edges
        UNION
        SELECT dst, src FROM base_edges
    ),
    -- the recursive binding: aggregate inside, recurse from the reduced relation
    result(node text, value int) AS (
        SELECT node, min(value)
        FROM (
            SELECT seed_node, 0 FROM seeds
            UNION ALL
            SELECT e.dst, r.value + 1
            FROM result r JOIN edges e ON e.src = r.node
        ) AS x(node, value)
        GROUP BY node
    )
-- payload joins and display filters live in the body
SELECT r.node, r.value, n.name
FROM result r JOIN nodes n ON n.id = r.node;
```
Mark this block `<!-- verify: skip -->` in SKILL.md (it names tables that are not in the fixture); the verifier only reads `references/`, so the marker is documentation of intent.
5. `## Step 3: Prove termination`: the checklist (monotone set with `UNION`; or an aggregate that bounds how often each row's value changes; cycles handled by set semantics or by the aggregate; for `EXCEPT ALL` and state-machine bindings, state the progress measure). Link `semantics.md#multisets-and-convergence`.
6. `## Step 4: Guard and verify`: `ERROR AT RECURSION LIMIT` above the expected diameter on every maintained view; step `RETURN AT RECURSION LIMIT 1, 2, 3` to watch a binding grow; mutation check (insert an edge, delete it, confirm the answer moves both ways); the three typing errors and their fixes in a small table. Link `semantics.md#recursion-limits` and `#column-types`.
7. `## Step 5: Make it maintainable`: index loop-invariant inputs on the join key; carry narrow keys; update-locality check with the two named violators; when to compute one-shot instead. Link `semantics.md#update-locality` and `#what-the-optimizer-will-not-do`.
8. `## Reading the plan`: six lines on the `EXPLAIN` shape. Link `semantics.md#reading-explain`.
9. `## What is allowed inside a binding`: the table from `semantics.md#what-standard-sql-forbids-that-wmr-allows`, one line per row.
10. `## Reference map`: one line per reference file, plus `references/fixture.sql` as the runnable example world.

- [ ] **Step 2: Write README.md**

Sections: what the skill does (two sentences), install (`npx skills add MaterializeInc/agent-skills@mz-graph-queries`), what it covers (the nine files as a bullet list), try it (load `references/fixture.sql` into a Materialize schema and run any block), how it was built (one sentence pointing to `DEVELOPMENT.md` and `evals/mz-graph-queries/`).

- [ ] **Step 3: Write DEVELOPMENT.md**

Sections mirroring `skills/mz-optimize-memory/DEVELOPMENT.md`: Provenance (the two research reports, the Materialize source paths and published posts listed in the spec, and the rule that every behavioural claim traces to source or to a verified block); The fixture (one world, generated, with the traps listed); Verification (`verify_skill_sql.py`, the `verify:` markers, when to `--record`); The evaluation (task set, automatic grading, manual axes, clean-room rules, how to run a cell, how to read results); Testing a change to the skill (edit, run the verifier, run one skill cell and one bare cell, compare with the README table, usability pass, re-verify claims).

- [ ] **Step 4: Repo tables and pointer**

In `CLAUDE.md`, add to the "Current Skills" table after the `mz-deploy` row:

```
| `mz-graph-queries` | Writing graph and hierarchy queries in Materialize with WITH MUTUALLY RECURSIVE: pattern selection, convergence, recursion limits, maintainability |
```

In the root `README.md`, read the existing per-skill entries under "Available Skills" and add one in the same format (heading, one-paragraph description, a `**Covers:**` line listing: problem classification, the nine reference files by topic, verified examples on a bundled fixture, translation from other dialects). Add a line to the dated list near the end: `- 2026-09-03: Add mz-graph-queries skill and its eval harness`.

In `skills/materialize-debug-freshness/references/attribution.md`, after the sentence "Materialize spells recursion `with mutually recursive`:" add: "(the `mz-graph-queries` skill covers writing such queries in general)".

- [ ] **Step 5: Validate**

Run:
```bash
wc -l skills/mz-graph-queries/SKILL.md            # under 250
python3 - <<'EOF'
import re, pathlib
t = pathlib.Path("skills/mz-graph-queries/SKILL.md").read_text()
m = re.match(r"---\n(.*?)\n---\n", t, re.S); fm = m.group(1)
assert "name: mz-graph-queries" in fm
desc = re.search(r"description: >\n((?:  .*\n)+)", fm).group(1)
assert 1 <= len(" ".join(l.strip() for l in desc.splitlines())) <= 1024, len(desc)
print("frontmatter ok")
EOF
grep -c "references/" skills/mz-graph-queries/SKILL.md   # every reference file linked at least once
claude plugin validate . --strict
cd evals/mz-graph-queries && python3 verify_skill_sql.py
```
Expected: line count under 250, `frontmatter ok`, at least 9 reference links, plugin validation passes, verifier prints `OK`.

---

### Task 14: Eval task registry, prompts, and grader

**Files:**
- Create: `evals/mz-graph-queries/tasks.py`
- Create: `evals/mz-graph-queries/tasks/t01.md` through `t14.md`
- Create: `evals/mz-graph-queries/grade.py`
- Create: `evals/mz-graph-queries/tests/test_grade.py`

**Interfaces:**
- Consumes: `fixture`, `reference`, `mzclient`.
- Produces: `tasks.Task(id, family, view, columns: list[tuple[str, str]], mode: "set" | "multiset", reference: Callable[[Fixture], set[tuple]], mutation: Mutation | None, prompt: str)`; `tasks.TASKS: list[Task]`; `tasks.render_prompt(task, f: Fixture, schema: str) -> str` (fills `{schema}` and any `{param}` from `f.params`); `tasks.mutation_for(task, f) -> Mutation | None` (mutations reference fixture params, so they are built per fixture); `grade.grade(schema: str, f: Fixture, cluster: str, out_dir: Path) -> dict`; CLI `grade.py --schema S --seed N --scale N [--no-traps] --out DIR`.

Task list (id, family, view name and columns, reference, mutation):

| id | family | view(columns) | reference | mutation |
|---|---|---|---|---|
| t01 | hierarchies | `t01_descendants(employee_id int)` | `descendants(f, loop_manager)` | insert employee `(loop_manager+4, loop_manager+3, 'emp_new', 100)` |
| t02 | hierarchies | `t02_depth(employee_id int, depth int)` | `depth(f, ceo_id)` | none |
| t03 | rollups | `t03_team_salary(employee_id int, total int)` | `team_salary(f, ceo_id)` | delete and re-insert `subtree_root`'s row with salary + 1000 |
| t04 | rollups | `t04_kit_quantity(part_id int, qty int)` | `bom_quantities(f, kit_part)` | none |
| t05 | rollups | `t05_kit_cost(cost numeric)` | `kit_cost(f, kit_part)` | none |
| t06 | reachability | `t06_within_hops(account_id text)` | `within_hops(f, flagged_account, hops)` | none |
| t07 | reachability | `t07_ring_accounts(account_id text)` | `ring_accounts(f)` | none |
| t08 | components | `t08_scc(account_id text, component text)` | `scc(f)` | none |
| t09 | permissions | `t09_effective_access(user_id text, doc_id text, level text)` | `effective_permissions(f)` | insert permission `(override_group's parent, a new doc 'doc99', 'read')` and membership `(sample_user, override_group)` |
| t10 | components | `t10_customer_clusters(customer_id text, cluster_id text)` | `customer_clusters(f, threshold)` | insert link `(c1, c<last>, 0.99)` merging two clusters |
| t11 | shortest-paths | `t11_route_km(city text, km int)` | `shortest_km(f, origin_city)` | insert road `(origin_city, city30, 1)` |
| t12 | shortest-paths | `t12_route_hops(city text, hops int)` | `shortest_hops(f, origin_city)` | none |
| t13 | reachability | `t13_downstream(task_id text)` | `downstream(f, impact_task)` | insert depends_on `(task40, task2)` if absent |
| t14 | reachability | `t14_reachable(src text, dst text)` | `closure(f)` | none |

All modes are `set`. Prompts are written so each view's columns and types are fixed by the prompt. Prompt bodies (each file is the body only; the runner adds the safety header and the wrapper instructions):

- t01: "Create a view `{schema}.t01_descendants(employee_id int)` listing every employee who reports, directly or through any chain of managers, to employee {loop_manager}. Do not include employee {loop_manager}. The `employees` table has `id, manager_id, name, salary`. Some of the manager data is known to be dirty."
- t02: "Create a view `{schema}.t02_depth(employee_id int, depth int)` giving the depth of every employee under the CEO (employee {ceo_id}), with the CEO at depth 0. Only include employees reachable from the CEO."
- t03: "Create a view `{schema}.t03_team_salary(employee_id int, total int)` where total is the employee's own salary plus the salaries of everyone under them at any depth. Cover every employee reachable from the CEO (employee {ceo_id}). This view will be queried continuously as salaries change, so it should be a maintained view rather than a one-off query."
- t04: "Create a view `{schema}.t04_kit_quantity(part_id int, qty int)`: for one unit of part {kit_part}, how many of each other part are needed in total. `bom(parent_id, child_id, qty)` says a parent needs qty of child. Some components are used under more than one assembly."
- t05: "Create a view `{schema}.t05_kit_cost(cost numeric)` with one row: the total cost of the leaf components needed for one unit of part {kit_part}, using `parts.unit_cost` (NULL for assembled parts)."
- t06: "The flagged account is {flagged_account}. I want all the paths money can take from it in up to {hops} transfers. Create a view `{schema}.t06_within_hops(account_id text)` listing every other account that money from the flagged account can reach within {hops} transfers along `transfers(src, dst, amount, ts)`."
- t07: "Create a view `{schema}.t07_ring_accounts(account_id text)` listing every account that is part of a circular chain of transfers (money that can return to the account it left)."
- t08: "Create a view `{schema}.t08_scc(account_id text, component text)` assigning every account to its strongly connected component in the transfers graph, labelled by the smallest account id in the component. Every account gets a row."
- t09: "Create a view `{schema}.t09_effective_access(user_id text, doc_id text, level text)`. Groups form a hierarchy (`groups(id, parent_id)`); `permissions(group_id, doc_id, level)` grants a level on a document to a group; permissions flow from a group to all groups under it unless a group has its own explicit row for that document, which replaces the inherited one for that group and everything below it. Users belong to groups via `memberships(user_id, group_id)`. One row per (user, doc, level) the user effectively holds. This view backs an authorization check, so it must be a maintained view."
- t10: "Create a view `{schema}.t10_customer_clusters(customer_id text, cluster_id text)`: customers linked by a `customer_links(a, b, score)` row with score at least {threshold} are the same person, and being the same person is transitive. Label each cluster with its smallest customer id. Every customer gets a row, including ones with no links. Links are stored once per pair."
- t11: "Create a view `{schema}.t11_route_km(city text, km int)`: the shortest driving distance from {origin_city} to every other reachable city. `roads(src, dst, km)` are two-way but each road is stored once. New roads open regularly, so this should be a maintained view."
- t12: "Create a view `{schema}.t12_route_hops(city text, hops int)`: the fewest roads you must take from {origin_city} to reach each other city."
- t13: "Create a view `{schema}.t13_downstream(task_id text)`: every pipeline task that would be affected, directly or indirectly, if {impact_task} produced bad data. `depends_on(task, prereq)` says task needs prereq. Exclude {impact_task} itself."
- t14: "A colleague wrote this view and it never returns a result. Fix it and create it as `{schema}.t14_reachable(src text, dst text)`, the set of (src, dst) account pairs where money can flow from src to dst through one or more transfers:

```
CREATE VIEW t14_reachable AS
WITH MUTUALLY RECURSIVE
    reach(src text, dst text) AS (
        SELECT src, dst FROM transfers
        UNION ALL
        SELECT src, dst FROM reach
        UNION ALL
        SELECT r.src, t.dst FROM reach r JOIN transfers t ON t.src = r.dst
    )
SELECT src, dst FROM reach;
```
Explain in one paragraph why it never returned."

Prompt files use Python `str.format` placeholders, so literal braces in SQL are not an issue (there are none); the t14 code block is plain text.

Grader behaviour: for each task, `SELECT <columns> FROM <schema>.<view>` on cluster `<schema>` with `statement_timeout = '60s'`; if the view does not exist record `missing`; if it times out record `timed_out`; otherwise parse rows and compare with the reference after normalization (`normalize_cell`: try `Decimal`, else the string; `\N` becomes `None`), reporting `missing_rows` and `extra_rows` (first 20 each). Then, in task order, for each task with a mutation: apply `mutation_sql` to the database and `apply_mutation` to the in-memory fixture, re-query that task only, and compare against the reference on the mutated fixture; record `post_mutation_ok`. Guardrail: `SELECT definition FROM mz_catalog.mz_views WHERE name = '<view>'` joined to `mz_schemas` on the run schema; `guardrail = 'RECURSION LIMIT' in definition.upper()`. Write `results.json` (per task dict plus `summary` with counts of `initial_ok`, `post_mutation_ok`, `timed_out`, `missing`, `guardrail`) and `worksheet.md` listing every task with its automatic outcome and two blank manual rows (maintainability, explanation).

- [ ] **Step 1: Write the failing tests**

```python
# evals/mz-graph-queries/tests/test_grade.py
import sys, os, unittest
from decimal import Decimal
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import fixture as fx
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


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest discover -s evals/mz-graph-queries/tests -v 2>&1 | tail -3`
Expected: FAIL with `No module named 'tasks'`.

- [ ] **Step 3: Write tasks.py**

```python
# evals/mz-graph-queries/tasks.py
"""The eval task registry: one Task per prompt, with its answer key and mutation."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Callable

import reference as ref
from fixture import Fixture, Mutation

HERE = Path(__file__).resolve().parent


@dataclass
class Task:
    id: str
    family: str
    view: str
    columns: list[tuple[str, str]]
    mode: str
    reference: Callable[[Fixture], set[tuple]]
    mutation: Callable[[Fixture], Mutation | None]
    prompt: str  # file name under tasks/


def _no_mutation(f: Fixture) -> Mutation | None:
    return None


def _m_t01(f: Fixture) -> Mutation | None:
    lm = f.params.get("loop_manager")
    if lm is None:
        return None
    return Mutation(inserts={"employees": [(lm + 4, lm + 3, "emp_new", 100)]})


def _m_t03(f: Fixture) -> Mutation:
    root = f.params["subtree_root"]
    row = next(e for e in f.employees if e[0] == root)
    return Mutation(deletes={"employees": [row]}, inserts={"employees": [(row[0], row[1], row[2], row[3] + 1000)]})


def _m_t09(f: Fixture) -> Mutation:
    g = f.params["override_group"]
    parent = next(pg for gid, pg in f.groups if gid == g)
    return Mutation(inserts={"permissions": [(parent, "doc99", "read")],
                             "memberships": [(f.params["sample_user"], g)]})


def _m_t10(f: Fixture) -> Mutation:
    last = f.customers[-1][0]
    return Mutation(inserts={"customer_links": [("c1", last, Decimal("0.99"))]})


def _m_t11(f: Fixture) -> Mutation:
    far = f.cities[-1][0]
    return Mutation(inserts={"roads": [(f.params["origin_city"], far, 1)]})


def _m_t13(f: Fixture) -> Mutation:
    last = f.pipelines[-1][0]
    edge = (last, f.params["impact_task"])
    if edge in f.depends_on:
        edge = (last, f.pipelines[0][0])
    return Mutation(inserts={"depends_on": [edge]})


P = lambda k: (lambda f: f.params[k])

TASKS: list[Task] = [
    Task("t01", "hierarchies", "t01_descendants", [("employee_id", "int")], "set",
         lambda f: ref.descendants(f, f.params.get("loop_manager", f.params["subtree_root"])), _m_t01, "t01.md"),
    Task("t02", "hierarchies", "t02_depth", [("employee_id", "int"), ("depth", "int")], "set",
         lambda f: ref.depth(f, f.params["ceo_id"]), _no_mutation, "t02.md"),
    Task("t03", "rollups", "t03_team_salary", [("employee_id", "int"), ("total", "int")], "set",
         lambda f: ref.team_salary(f, f.params["ceo_id"]), _m_t03, "t03.md"),
    Task("t04", "rollups", "t04_kit_quantity", [("part_id", "int"), ("qty", "int")], "set",
         lambda f: ref.bom_quantities(f, f.params["kit_part"]), _no_mutation, "t04.md"),
    Task("t05", "rollups", "t05_kit_cost", [("cost", "numeric")], "set",
         lambda f: ref.kit_cost(f, f.params["kit_part"]), _no_mutation, "t05.md"),
    Task("t06", "reachability", "t06_within_hops", [("account_id", "text")], "set",
         lambda f: ref.within_hops(f, f.params["flagged_account"], f.params["hops"]), _no_mutation, "t06.md"),
    Task("t07", "reachability", "t07_ring_accounts", [("account_id", "text")], "set",
         ref.ring_accounts, _no_mutation, "t07.md"),
    Task("t08", "components", "t08_scc", [("account_id", "text"), ("component", "text")], "set",
         ref.scc, _no_mutation, "t08.md"),
    Task("t09", "permissions", "t09_effective_access", [("user_id", "text"), ("doc_id", "text"), ("level", "text")], "set",
         ref.effective_permissions, _m_t09, "t09.md"),
    Task("t10", "components", "t10_customer_clusters", [("customer_id", "text"), ("cluster_id", "text")], "set",
         lambda f: ref.customer_clusters(f, f.params["threshold"]), _m_t10, "t10.md"),
    Task("t11", "shortest-paths", "t11_route_km", [("city", "text"), ("km", "int")], "set",
         lambda f: ref.shortest_km(f, f.params["origin_city"]), _m_t11, "t11.md"),
    Task("t12", "shortest-paths", "t12_route_hops", [("city", "text"), ("hops", "int")], "set",
         lambda f: ref.shortest_hops(f, f.params["origin_city"]), _no_mutation, "t12.md"),
    Task("t13", "reachability", "t13_downstream", [("task_id", "text")], "set",
         lambda f: ref.downstream(f, f.params["impact_task"]), _m_t13, "t13.md"),
    Task("t14", "reachability", "t14_reachable", [("src", "text"), ("dst", "text")], "set",
         ref.closure, _no_mutation, "t14.md"),
]


def render_prompt(task: Task, f: Fixture, schema: str) -> str:
    body = (HERE / "tasks" / task.prompt).read_text()
    params = {k: (str(v) if isinstance(v, Decimal) else v) for k, v in f.params.items()}
    return body.format(schema=schema, **params)


def mutation_for(task: Task, f: Fixture) -> Mutation | None:
    return task.mutation(f)
```

Note for the small fixture (no `loop_manager`): t01 falls back to `subtree_root`; the eval always runs with traps, so the prompt's `{loop_manager}` is present there. For `test_mutations_apply`, `_m_t13`'s edge from the last task to `task2` changes `downstream(task2)` only if task40 was not already downstream; if the assertion fails for seed 1, change the mutation to insert `(f.pipelines[-1][0], impact_task)` and delete every existing `depends_on` row of that last task first (put the deletes in the same `Mutation`), which makes the last task's only prerequisite the impact task.

- [ ] **Step 4: Write the fourteen prompt files** with the bodies listed above, one per file under `evals/mz-graph-queries/tasks/`.

- [ ] **Step 5: Write grade.py**

```python
#!/usr/bin/env python3
# evals/mz-graph-queries/grade.py
"""Grade one run schema against the answer keys.

  grade.py --schema RUN --seed N --scale N [--no-traps] [--cluster C] --out DIR
"""
from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path

import fixture as fx
import mzclient
import tasks as T


def normalize_cell(s: str):
    if s == "\\N":
        return None
    try:
        return Decimal(s)
    except InvalidOperation:
        return s


def diff(expected: set[tuple], got_rows: list[list[str]]):
    def norm(t):
        return tuple(Decimal(v) if isinstance(v, (int, Decimal)) else v for v in t)
    exp = {norm(t) for t in expected}
    got = {tuple(normalize_cell(c) for c in r) for r in got_rows}
    return sorted(exp - got, key=repr), sorted(got - exp, key=repr)


def view_definition(schema: str, view: str) -> str | None:
    r = mzclient.run(
        f"SELECT v.definition FROM mz_catalog.mz_views v JOIN mz_catalog.mz_schemas s ON s.id = v.schema_id "
        f"WHERE s.name = '{schema}' AND v.name = '{view}'")
    return r.rows[0][0] if r.ok and r.rows else None


def query_task(schema: str, cluster: str, t: T.Task) -> dict:
    cols = ", ".join(c for c, _ in t.columns)
    r = mzclient.run(f"SELECT {cols} FROM {schema}.{t.view};", cluster=cluster, timeout_s=60)
    out = {"exists": True, "timed_out": r.timed_out, "error": None, "rows": r.rows}
    if not r.ok:
        out["error"] = r.error_line
        if "unknown catalog item" in r.error_line or "does not exist" in r.error_line:
            out["exists"] = False
    return out


def grade(schema: str, f: fx.Fixture, cluster: str, out_dir: Path) -> dict:
    results: dict[str, dict] = {}
    for t in T.TASKS:
        q = query_task(schema, cluster, t)
        rec = {"task": t.id, "family": t.family, "view": t.view, "exists": q["exists"], "timed_out": q["timed_out"],
               "error": q["error"], "initial_ok": False, "missing_rows": [], "extra_rows": [],
               "post_mutation_ok": None, "guardrail": None}
        if q["exists"] and not q["timed_out"] and q["error"] is None:
            missing, extra = diff(t.reference(f), q["rows"])
            rec["initial_ok"] = not missing and not extra
            rec["missing_rows"], rec["extra_rows"] = [repr(x) for x in missing[:20]], [repr(x) for x in extra[:20]]
        d = view_definition(schema, t.view)
        rec["guardrail"] = None if d is None else ("RECURSION LIMIT" in d.upper())
        results[t.id] = rec
    cur = f
    for t in T.TASKS:
        m = T.mutation_for(t, cur)
        if m is None:
            continue
        r = mzclient.run(fx.mutation_sql(m, schema))
        if not r.ok:
            results[t.id]["post_mutation_ok"] = f"mutation failed: {r.error_line}"
            continue
        cur = fx.apply_mutation(cur, m)
        rec = results[t.id]
        if rec["exists"] and not rec["timed_out"]:
            q = query_task(schema, cluster, t)
            if q["timed_out"] or q["error"]:
                rec["post_mutation_ok"] = False
            else:
                missing, extra = diff(t.reference(cur), q["rows"])
                rec["post_mutation_ok"] = not missing and not extra
    summary = {
        "tasks": len(T.TASKS),
        "exists": sum(r["exists"] for r in results.values()),
        "initial_ok": sum(r["initial_ok"] for r in results.values()),
        "post_mutation_ok": sum(r["post_mutation_ok"] is True for r in results.values()),
        "mutations": sum(r["post_mutation_ok"] is not None for r in results.values()),
        "timed_out": sum(r["timed_out"] for r in results.values()),
        "guardrail": sum(r["guardrail"] is True for r in results.values()),
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "results.json").write_text(json.dumps({"summary": summary, "tasks": results}, indent=2))
    lines = ["# Grading worksheet", "", f"schema `{schema}`", "",
             "| task | exists | initial | after mutation | timed out | guardrail | maintainability (manual) | explanation (manual) |",
             "|---|---|---|---|---|---|---|---|"]
    for r in results.values():
        lines.append(f"| {r['task']} | {r['exists']} | {r['initial_ok']} | {r['post_mutation_ok']} | {r['timed_out']} | {r['guardrail']} |  |  |")
    lines += ["", f"summary: {json.dumps(summary)}"]
    (out_dir / "worksheet.md").write_text("\n".join(lines) + "\n")
    return {"summary": summary, "tasks": results}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--schema", required=True)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--scale", type=int, default=100)
    ap.add_argument("--no-traps", action="store_true")
    ap.add_argument("--cluster", default=None, help="defaults to the schema name")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    f = fx.eval_fixture(a.seed, a.scale, traps=not a.no_traps)
    res = grade(a.schema, f, a.cluster or a.schema, Path(a.out))
    print(json.dumps(res["summary"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 6: Run unit tests**

Run: `python3 -m unittest discover -s evals/mz-graph-queries/tests -v`
Expected: all PASS.

- [ ] **Step 7: Grader self-test with reference views**

Build an eval fixture, create the fourteen views yourself using the skill's patterns (this is the "perfect agent" and also a second verification of the skill), then grade. Use schema `selftest` on cluster `quickstart`:

```bash
cd evals/mz-graph-queries
P="psql -X -q -v ON_ERROR_STOP=1 -h localhost -p 6877 -U materialize -d materialize"
$P -c "DROP SCHEMA IF EXISTS selftest CASCADE"
python3 build_fixture.py --eval --seed 1 --scale 20 --schema selftest | $P -f -
python3 build_fixture.py --eval --seed 1 --scale 20 --manifest      # read the params you need
# write $SCRATCH/selftest_views.sql: fourteen CREATE VIEW statements in schema selftest
# built from the reference-file patterns with the manifest's ids substituted; then:
$P -f "$SCRATCH/selftest_views.sql"   # SCRATCH: your session scratchpad directory
python3 grade.py --schema selftest --seed 1 --scale 20 --cluster quickstart --out /tmp/selftest-grade
cat /tmp/selftest-grade/worksheet.md
```
Expected summary: `exists 14, initial_ok 14, post_mutation_ok 6, mutations 6, timed_out 0`. Any task that fails here has either a wrong reference implementation or a wrong skill pattern; resolve by hand-checking the disputed rows on the small fixture before changing either. Keep `selftest_views.sql` out of the repo (it would be an answer key), except that its per-view SQL should already exist in the reference files. Drop the schema afterwards.

---

### Task 15: Clean-room runner, wrapper, preflight, rubric, README

**Files:**
- Create: `evals/mz-graph-queries/bench-psql.template`
- Create: `evals/mz-graph-queries/prompt.txt.in`
- Create: `evals/mz-graph-queries/run_cleanroom.sh`
- Create: `evals/mz-graph-queries/preflight.sh`
- Create: `evals/mz-graph-queries/rubric.md`
- Create: `evals/mz-graph-queries/GRADING-TEMPLATE.md`
- Create: `evals/mz-graph-queries/README.md`

**Interfaces:**
- Consumes: `build_fixture.py`, `tasks.py` (via a small `render_prompts` entry point added here: `python3 -c 'import tasks, fixture as fx, sys; f = fx.eval_fixture(int(sys.argv[1]), int(sys.argv[2])); print("\n\n".join(f"## Task {t.id}\n\n" + tasks.render_prompt(t, f, sys.argv[3]) for t in tasks.TASKS))' SEED SCALE SCHEMA`), `grade.py`.
- Produces: run directories under `$EVAL_BENCH_ROOT/<run>` and private results under `$EVAL_BENCH_ROOT/<run>.private/` containing `prompt.txt`, `transcript.txt`, `results.json`, `worksheet.md`.

- [ ] **Step 1: bench-psql.template**

Copy `evals/mz-optimize-memory/bench-psql.template` and make two edits: delete the whole `if [ "$MODE" = ro ]; then ... fi` block (this eval has one read-write round), and delete the `MODE=__MODE__` line. Keep the flag, meta-command, and backslash checks, the 180 s timeout, and the `SET schema` / `SET cluster` presets.

- [ ] **Step 2: prompt.txt.in**

```text
STRICT SAFETY RULES, read these first: they override everything else.
- This is a LOCAL test bench on a developer laptop. Your ONLY permitted command is ./bench-psql (in your working directory); everything else is deny-listed by the harness.
- NEVER connect to any other host, service, cloud environment, or remote system. No network access beyond localhost psql. Never use web search or web fetch.
- File access: you may read and write your private ./scratch directory. Nothing else on disk, and no other shell commands; the harness denies them.
- Touch ONLY schema __RUN__ and cluster __RUN__. Never modify, drop, or write to anything in any other schema or cluster. Never run ALTER SYSTEM.

You are working on a local Materialize test bench. Your ONLY way to interact
with it is the wrapper script in your working directory: run
./bench-psql 'SQL...' (or pipe SQL via heredoc: ./bench-psql <<'SQLEOF' ... SQLEOF).
It connects to the local Materialize, presets your schema and cluster, and
executes the statements. Plain SQL only (no psql meta-commands except \d, \l,
\x). Each invocation is a fresh session, so put statements that must share a
session into one invocation. Statements time out after 180 seconds.

Schema __RUN__ holds these tables: employees(id int, manager_id int, name text,
salary int); parts(id int, name text, unit_cost numeric); bom(parent_id int,
child_id int, qty int); accounts(id text); transfers(src text, dst text, amount
numeric, ts timestamp); groups(id text, parent_id text); memberships(user_id
text, group_id text); permissions(group_id text, doc_id text, level text);
customers(id text); customer_links(a text, b text, score numeric); cities(id
text); roads(src text, dst text, km int); pipelines(id text); depends_on(task
text, prereq text).

Below are fourteen requests from colleagues. For each one, create the view
exactly as named, with exactly the columns and types given, in schema __RUN__.
Verify each view returns sensible results before moving on. Some requests
contain data quality surprises or are phrased loosely; deliver what the
colleague needs, and when you interpret a request, say how. Where a request
says the view will be maintained or queried continuously, treat it as a
production view. When you finish, write a short report to ./scratch/report.md:
one paragraph per task with the SQL you created, why it terminates, and any
assumptions.

__TASKS__
```

- [ ] **Step 3: run_cleanroom.sh**

```bash
#!/usr/bin/env bash
# One clean-room eval run of the mz-graph-queries skill:
#   run_cleanroom.sh <cond> [seed]
#   cond: sb|ss|ob|os|hb|hs  (sonnet-5 | opus-5 | haiku-4-5  x  bare | skill)
# One read-write authoring round, then automatic grading.
set -euo pipefail
cond=$1; seed=${2:-1}
run="gq_${cond}_s${seed}"
case "$cond" in
  s*) model=claude-sonnet-5;;
  o*) model=claude-opus-5;;
  h*) model=claude-haiku-4-5-20251001;;
  *) echo "unknown cond $cond"; exit 1;;
esac
here="$(cd "$(dirname "$0")" && pwd)"
: "${EVAL_BENCH_ROOT:=$HOME/eval-bench}"
: "${EVAL_PSQL_ARGS:=-h localhost -p 6877 -U materialize -d materialize}"
: "${EVAL_CLUSTER_SIZE:=25cc}"
: "${EVAL_SCALE:=100}"
: "${EVAL_TIMEOUT:=7200}"
: "${SKILL_DIR:=$here/../../skills/mz-graph-queries}"
case "$EVAL_BENCH_ROOT" in /*) ;; *) echo "EVAL_BENCH_ROOT must be absolute" >&2; exit 1;; esac
case "$cond" in *s) [ -f "$SKILL_DIR/SKILL.md" ] || { echo "no SKILL.md at $SKILL_DIR"; exit 1; };; esac
export EVAL_PSQL_ARGS
bench="$EVAL_BENCH_ROOT/$run"; pdir="$EVAL_BENCH_ROOT/$run.private"
d="$bench"; while [ "$d" != "/" ]; do
  [ -e "$d/CLAUDE.md" ] && { echo "refusing: CLAUDE.md at $d would load into the agent session" >&2; exit 1; }
  d=$(dirname "$d")
done
PSQL="psql -X -q -v ON_ERROR_STOP=1 $EVAL_PSQL_ARGS"
mkdir -p "$bench/scratch" "$pdir"

# ---- 1. build --------------------------------------------------------------
$PSQL -c "DROP SCHEMA IF EXISTS $run CASCADE" -c "DROP CLUSTER IF EXISTS $run CASCADE"
$PSQL -c "CREATE CLUSTER $run (SIZE = '$EVAL_CLUSTER_SIZE')"
(cd "$here" && python3 build_fixture.py --eval --seed "$seed" --scale "$EVAL_SCALE" --schema "$run") | $PSQL -f -
n=$(psql -X -At $EVAL_PSQL_ARGS -c "SELECT count(*) FROM $run.employees")
echo "$run built (employees=$n)"

# ---- 2. prompt + skill -----------------------------------------------------
tasks_text=$(cd "$here" && python3 -c '
import sys, tasks, fixture as fx
f = fx.eval_fixture(int(sys.argv[1]), int(sys.argv[2]))
print("\n\n".join(f"## Task {t.id}\n\n" + tasks.render_prompt(t, f, sys.argv[3]) for t in tasks.TASKS))
' "$seed" "$EVAL_SCALE" "$run")
python3 - "$here/prompt.txt.in" "$run" "$pdir/prompt.txt" <<'EOF' "$tasks_text"
import sys
tpl, run, out, tasks_text = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
open(out, "w").write(open(tpl).read().replace("__RUN__", run).replace("__TASKS__", tasks_text))
EOF
case "$cond" in
  *s)
    rm -rf "$bench/skill"; mkdir -p "$bench/skill"
    cp "$SKILL_DIR/SKILL.md" "$bench/skill/"
    cp -r "$SKILL_DIR/references" "$bench/skill/"
    { echo; echo "Internal guidance that may help with this class of task is available under ./skill/;"
      echo "read ./skill/SKILL.md first. It links further files under ./skill/references/."; } >> "$pdir/prompt.txt"
    ;;
esac
rm -f "$bench/bench-psql"
sed -e "s/__RUN__/$run/" -e "s|__PSQL_ARGS__|$EVAL_PSQL_ARGS|" "$here/bench-psql.template" > "$bench/bench-psql"
chmod 555 "$bench/bench-psql"

# ---- 3. the round ----------------------------------------------------------
allowed=( "Bash(./bench-psql:*)" "Bash($bench/bench-psql:*)" "Bash(sleep :*)" "Bash(sleep:*)"
          "Read(//$bench/scratch/**)" "Edit(//$bench/scratch/**)" "Write(//$bench/scratch/**)" "Read(//$bench/skill/**)" )
(cd "$bench" && CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 timeout "$EVAL_TIMEOUT" \
  claude -p --model "$model" --setting-sources project \
  --allowedTools "${allowed[@]}" --disallowedTools "Skill" "WebSearch" "WebFetch" \
  < "$pdir/prompt.txt" | tee "$pdir/transcript.txt") || echo "agent exited $?"
cp "$bench/scratch/report.md" "$pdir/report.md" 2>/dev/null || echo "no report.md written"

# ---- 4. grade --------------------------------------------------------------
(cd "$here" && python3 grade.py --schema "$run" --seed "$seed" --scale "$EVAL_SCALE" --out "$pdir")
echo "RUN $run DONE: results in $pdir"
```

Note the heredoc trick in step 2 passes `$tasks_text` as an argument after the heredoc terminator; if the shell rejects that form, write `$tasks_text` to `$pdir/tasks.txt` first and read it in the Python snippet instead.

- [ ] **Step 4: preflight.sh**

Copy `evals/mz-optimize-memory/v6_preflight.sh`, then: rename `run=v6_preflight` to `run=gq_preflight`; default `EVAL_PSQL_ARGS` port to 6877 and `EVAL_CLUSTER_SIZE` to 25cc; change `write_wrapper` to the single-mode `sed` from the runner (no `__MODE__`); delete every check that asserts a read-only rejection (the "ro rejects CREATE" family) and keep: flags rejected, meta-commands rejected except `\d \l \x`, plain SQL works, heredoc works, DDL works in the run schema; in the agent part keep the allowed and denied matrix but change the source-tree read check to a `./skill/` read check (allowed under the skill condition) and drop `MZ_SRC`. Run `./preflight.sh --wrapper-only` and expect zero failures.

- [ ] **Step 5: rubric.md**

Five axes summing to 5.0:

- Axis 1, initial correctness (1.5): `initial_ok / 14 * 1.5` from `results.json`.
- Axis 2, correctness after mutation (1.0): `post_mutation_ok / mutations * 1.0`; a view that was already wrong scores 0 here.
- Axis 3, convergence and guardrails (0.75): 0.5 if no task timed out; 0.25 scaled by the fraction of views created with a recursion limit (from `guardrail`).
- Axis 4, maintainability (0.75, manual): from `report.md` and the view definitions: aggregate inside the binding where a min, max, or sum is needed (t03, t04, t05, t08, t10, t11, t12); narrow columns in the loop; indexes on join keys for the views the prompt marked as maintained (t03, t09, t11); no `UNION ALL` re-reading the binding.
- Axis 5, explanation (0.5, manual): termination argument stated per task; the t14 diagnosis names multiset growth (`UNION ALL` re-adding the binding and the base case) rather than "cycles"; interpretations of loose requests (t06 "all paths", t01 dirty data, t10 one-direction links) stated.

Say that automatic axes are read from `results.json`, manual axes from `report.md` and `transcript.txt`, and that a grader re-checks any automatic failure by running the view by hand before deducting (a fixture or reference bug is possible and must be fixed in the harness, not scored).

- [ ] **Step 6: GRADING-TEMPLATE.md**

A per-run worksheet: run id, condition, seed, scale, model; the `summary` line pasted; one table row per task (task, initial, after mutation, timed out, guardrail, maintainability note, explanation note); axis scores; total; three free-text lines (what the skill helped with, what it did not, skill text to change).

- [ ] **Step 7: README.md**

Sections: what the environment is (the seven table groups, the six traps, scale and seed); files table (every file in the directory with one line each); how to run (start the emulator command from Global Constraints, `./preflight.sh --wrapper-only`, `./run_cleanroom.sh hs` as a smoke test, `./run_cleanroom.sh ss` and `sb` for graded cells, `grade.py` re-run by hand); how grading works (automatic axes, manual axes, the re-check rule); isolation (the same list as the memory eval's README, minus the source tree); recorded results (an empty table with columns run, condition, seed, initial_ok, post_mutation_ok, timed_out, guardrail, axis total, filled in by Task 16).

- [ ] **Step 8: Check**

Run: `bash -n evals/mz-graph-queries/run_cleanroom.sh evals/mz-graph-queries/preflight.sh && cd evals/mz-graph-queries && ./preflight.sh --wrapper-only`
Expected: no syntax errors; preflight prints only `PASS` lines and exits 0.

---

### Task 16: Smoke run, calibration cells, usability pass, recorded results

**Files:**
- Modify: `evals/mz-graph-queries/README.md` (recorded results table)
- Modify: `skills/mz-graph-queries/*` as the usability pass and graded runs demand

- [ ] **Step 1: Smoke run**

Run: `EVAL_SCALE=20 EVAL_TIMEOUT=1800 evals/mz-graph-queries/run_cleanroom.sh hs`
Expected: the run builds, the agent session ends, `results.json` and `worksheet.md` appear under `~/eval-bench/gq_hs_s1.private/`. The purpose is the harness, not the score; fix runner or grader problems and re-run until the pipeline completes end to end. Then drop the schema and cluster: `psql ... -c "DROP SCHEMA gq_hs_s1 CASCADE" -c "DROP CLUSTER gq_hs_s1 CASCADE"`.

- [ ] **Step 2: Usability pass**

Start a fresh Claude Code session in an empty directory outside this repo with `--add-dir skills/mz-graph-queries`, load the small fixture into schema `usability` on the emulator, and ask the agent to answer three questions using the skill (a rollup, a shortest path with one witness, a permission check with an override) and to report any skill text it found ambiguous, incorrect, or misleading. Verify each reported problem against the emulator before editing the skill. Re-run `verify_skill_sql.py` after edits.

- [ ] **Step 3: Calibration cells**

Run one at a time, each takes roughly one to two hours: `evals/mz-graph-queries/run_cleanroom.sh sb` then `evals/mz-graph-queries/run_cleanroom.sh ss`. For each, fill in a `GRADING-TEMPLATE.md` copy under the private directory, then add a row to the README's recorded results table. Re-check every automatic failure by hand before recording it; a harness bug found here is fixed in the harness and the cell is re-run.

- [ ] **Step 4: Fold findings back**

Where the skill cell failed a task the bare cell also failed, the skill text has a gap; where the skill cell failed and the bare cell passed, the skill text misled. Edit the responsible reference file or `SKILL.md` section, re-verify SQL, and note the change in `DEVELOPMENT.md` under a "Changes from graded runs" heading. Opus cells are not part of this plan; note in the README that they are pending.

- [ ] **Step 5: Final verification**

Run:
```bash
python3 -m unittest discover -s evals/mz-graph-queries/tests -v
(cd evals/mz-graph-queries && python3 verify_skill_sql.py)
claude plugin validate . --strict
wc -l skills/mz-graph-queries/SKILL.md
git status --short
```
Expected: tests pass, verifier `OK`, validation passes, `SKILL.md` under 250 lines, and `git status` shows only the new skill directory, the new eval directory, the spec and plan under `docs/`, and the three modified files (`README.md`, `CLAUDE.md`, the freshness attribution reference), all committed on branch `mz-graph-queries` and nothing pushed.
