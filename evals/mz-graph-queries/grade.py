#!/usr/bin/env python3
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

TIMEOUT_S = 60


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
    """The submitted SQL, whether the answer is a view or a materialized view."""
    r = mzclient.run(
        "SELECT v.definition FROM ("
        "  SELECT schema_id, name, definition FROM mz_catalog.mz_views"
        "  UNION ALL SELECT schema_id, name, definition FROM mz_catalog.mz_materialized_views"
        ") v JOIN mz_catalog.mz_schemas s ON s.id = v.schema_id "
        f"WHERE s.name = '{schema}' AND v.name = '{view}';")
    return r.rows[0][0] if r.ok and r.rows else None


def query_task(schema: str, cluster: str, t: T.Task) -> dict:
    cols = ", ".join(c for c, _ in t.columns)
    r = mzclient.run(f"SELECT {cols} FROM {schema}.{t.view};", cluster=cluster, timeout_s=TIMEOUT_S)
    out = {"exists": True, "timed_out": r.timed_out, "error": None, "rows": r.rows}
    if not r.ok and not r.timed_out:
        out["error"] = r.error_line
        if "unknown catalog item" in r.error_line or "does not exist" in r.error_line:
            out["exists"] = False
    return out


def count_task(schema: str, cluster: str, t: T.Task) -> int | None:
    """Fallback for a result set too large to ship in the statement timeout."""
    r = mzclient.run(f"SELECT count(*) FROM {schema}.{t.view};", cluster=cluster, timeout_s=TIMEOUT_S)
    if not r.ok or not r.rows:
        return None
    try:
        return int(r.rows[0][0])
    except ValueError:
        return None


def grade(schema: str, f: fx.Fixture, cluster: str, out_dir: Path) -> dict:
    results: dict[str, dict] = {}
    for t in T.TASKS:
        q = query_task(schema, cluster, t)
        rec = {"task": t.id, "family": t.family, "view": t.view, "exists": q["exists"], "timed_out": q["timed_out"],
               "error": q["error"], "initial_ok": False, "missing_rows": [], "extra_rows": [],
               "partial": None, "post_mutation_ok": None, "guardrail": None}
        if q["exists"] and not q["timed_out"] and q["error"] is None:
            missing, extra = diff(t.reference(f), q["rows"])
            rec["initial_ok"] = not missing and not extra
            rec["missing_rows"], rec["extra_rows"] = [repr(x) for x in missing[:20]], [repr(x) for x in extra[:20]]
        elif q["timed_out"]:
            n = count_task(schema, cluster, t)
            if n is not None:
                rec["initial_ok"] = n == len(t.reference(f))
                rec["partial"] = "count-only"
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
        lines.append(f"| {r['task']} | {r['exists']} | {r['initial_ok']} | {r['post_mutation_ok']} | "
                     f"{r['timed_out']} | {r['guardrail']} |  |  |")
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
