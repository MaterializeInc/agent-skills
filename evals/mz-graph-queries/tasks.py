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
    """A new employee under the loop manager's dangling reportee."""
    lm = f.params.get("loop_manager")
    if lm is None:
        return None
    return Mutation(inserts={"employees": [(lm + 4, lm + 3, "emp_new", 100)]})


def _m_t03(f: Fixture) -> Mutation:
    """Give the subtree root a raise: their total and every ancestor's total moves."""
    root = f.params["subtree_root"]
    row = next(e for e in f.employees if e[0] == root)
    return Mutation(deletes={"employees": [row]}, inserts={"employees": [(row[0], row[1], row[2], row[3] + 1000)]})


def _m_t09(f: Fixture) -> Mutation:
    """A new document granted on the override group's parent, plus a new membership."""
    g = f.params["override_group"]
    parent = next(pg for gid, pg in f.groups if gid == g)
    return Mutation(inserts={"permissions": [(parent, "doc99", "read")],
                             "memberships": [(f.params["sample_user"], g)]})


def _m_t10(f: Fixture) -> Mutation:
    """A brand new customer linked to c1: joins c1's cluster, whose label does not move."""
    return Mutation(inserts={"customers": [("c_new",)],
                             "customer_links": [("c1", "c_new", Decimal("0.99"))]})


def _m_t11(f: Fixture) -> Mutation:
    """A new city one km from the origin."""
    return Mutation(inserts={"cities": [("city_new",)],
                             "roads": [(f.params["origin_city"], "city_new", 1)]})


def _m_t13(f: Fixture) -> Mutation:
    """A new task that depends on the impact task, so it lands downstream of it."""
    return Mutation(inserts={"pipelines": [("task_new",)],
                             "depends_on": [("task_new", f.params["impact_task"])]})


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
    Task("t09", "permissions", "t09_effective_access",
         [("user_id", "text"), ("doc_id", "text"), ("level", "text")], "set",
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
