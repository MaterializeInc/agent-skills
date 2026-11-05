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
    for t in TABLES:
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
    # planted override, seed-independent: g2's parent is g1 by construction, so g2's
    # explicit edit on doc1 overrides the read it would inherit from g1.
    forced = [("g1", "doc1", "read"), ("g2", "doc1", "edit")]
    keys = {(g, d) for g, d, _ in forced}
    f.permissions = [r for r in f.permissions if (r[0], r[1]) not in keys] + forced
    p["override_group"], p["override_doc"] = "g2", "doc1"
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
