# mz-graph-queries: design

Date: 2026-09-03
Status: approved (brainstorming complete), not yet implemented

## Purpose

A new skill, `mz-graph-queries`, that teaches an agent to write correct,
convergent, maintainable graph and hierarchy queries in Materialize using
`WITH MUTUALLY RECURSIVE` (WMR). Scope is authoring only: given a graph or
hierarchy question, produce the SQL. Live-cluster diagnosis of an existing
recursive view is handed off to `materialize-debug-freshness` and
`mz-optimize-memory`. Relationship modeling is handed off to
`mz-ontology-design`.

The skill is organized by classic problem family. The live context graph
appears as a motivating application and as trigger words, with one reference
file mapping agent questions onto the families.

Verification: every SQL block in the skill is machine-verified against a
local Materialize, and a graded clean-room agent evaluation (skill vs bare)
ships under `evals/mz-graph-queries/`.

## Research basis

Two research reports are the source material (scratchpad copies were made
during brainstorming; the durable citations are the Materialize source tree
and the URLs below):

- Materialize source at `~/materialize` (commit `09a24b3`, 2026-09-01):
  `doc/user/content/sql/select/recursive-ctes.md`, design docs
  `doc/developer/design/20221204_with_mutually_recursive.md`,
  `20230223_stabilize_with_mutually_recursive.md`,
  `20230330_recursion_limit.md`, `20231204_wmr_type_casts.md`; planner
  `src/sql/src/plan/query.rs` (`plan_ctes`), `src/expr/src/relation.rs`
  (`LetRec`, `recursive_ids`), `src/transform/src/normalize_lets.rs`,
  `src/compute/src/render.rs` (iterative scope, `LetRecConsolidation`,
  limit enforcement); tests `test/sqllogictest/with_mutually_recursive.slt`,
  `ldbc_bi.slt`, `test/ldbc-bi/*.sql`, `freshmart.slt`,
  `session-window-wmr.slt`, `github-17808.slt`, `transform/normalize_lets.slt`,
  `test/testdrive/divergent-dataflow-cancellation.td`, `hydration-status.td`.
- Published writing: Materialize docs recursive CTEs page; McSherry,
  "Recursion in Materialize" (2023), "Reasons for Recursion", "Doing business
  with recursive SQL", "Materialize and Advent of Code" and the AoC 2023
  solutions repo, "Exploring Social Trends on Bluesky", "Transaction
  Processing in the Data Plane"; Alexandrov, "Recursive SQL Queries in
  Materialize"; changelog 2024-12-23 (permission inheritance example);
  v25.2 release post (loop-invariant index reads). Problem catalog sources:
  PostgreSQL, SQL Server, MySQL, Oracle, SQLite, DuckDB and Db2 docs; Celko;
  Karwin; Ben-Gan; Kimball; Fusionbox; Halford; Zanzibar (Pang et al.);
  OpenFGA. Context graph sources: Foundation Capital essays; Materialize
  "What Is a Live Context Graph?" and related posts; Atlan, DataHub, Neo4j,
  Zep/Graphiti.

### Semantics the skill must teach (verified in source)

1. Bindings are multisets. The recursive variable is consolidated
   (`LetRecConsolidation`) but never made distinct. `UNION ALL` of a base
   case with a re-read of the binding grows multiplicities every iteration
   and never converges; `UNION`, `DISTINCT`, or an aggregate that collapses
   each group makes the fixpoint exist.
2. Evaluation is sequential within an iteration. A `Get` of a binding that
   appears before that binding's definition (or in its own definition) reads
   the previous iteration's value, empty in round one. This is observable
   (the `X EXCEPT ALL X_delayed` first-round idiom depends on it) and the
   optimizer never inlines across that edge.
3. Almost nothing is restricted inside a binding: aggregates, `LEFT JOIN` on
   the binding, `DISTINCT ON`, `ORDER BY ... LIMIT`, `NOT EXISTS` against a
   binding, correlated subqueries, `mz_now()` temporal filters, nested and
   sequenced WMR blocks, a binding with no base case.
4. Column types are mandatory, declared nullable, and applied as assignment
   casts (typmods imposed, e.g. `numeric(38,2)` rounds). String literals type
   as `text`, so `bar(x int8) AS (SELECT '1')` fails at plan time; out-of-range
   casts fail at runtime. Error text: `WITH MUTUALLY RECURSIVE query "<name>"
   declared types (...), but query returns types (...)`.
5. Recursion limits: no default. `ERROR AT RECURSION LIMIT n` (also bare
   `RECURSION LIMIT n`) errors with SQLSTATE program-limit-exceeded when the
   loop reaches n iterations with non-empty changes; `RETURN AT RECURSION
   LIMIT n` returns the state after exactly n iterations. Limits are per
   block in SQL, per binding internally, and survive view inlining. A
   divergent view installs successfully and never hydrates.
6. Optimizer treatment of recursive bindings: no predicate pushdown into
   them, all columns retained, cardinality unknown, no constant folding
   across bindings, arrangements do not cross the back edge. Imported
   indexes on base tables are usable inside the loop (primary performance
   lever; v25.2 made loop-invariant reads hit indexes). Non-recursive prefix
   and suffix bindings are hoisted out of the loop.
7. Performance model: only deltas circulate. Iterations track graph
   diameter for linear recursion; non-linear closure halves depth at
   quadratic intermediate cost. "Update locality" (docs) separates
   maintainable recursions (reachability, tree rollups touching at most 2h
   rows) from ones that thrash (naive PageRank, k-means).
8. `EXPLAIN` shape: `With Mutually Recursive [recursion_limit=N,
   return_at_limit]` header, `cte lN = ...` blocks, `Return`. A `Get lN`
   inside `cte lN` is the back edge. `EXPLAIN WITH (linear chains)` is
   rejected for WMR.

### The recurring translation

Standard SQL forces "enumerate all paths, aggregate outside". WMR collapses
this into an aggregate inside the binding, recursing from the reduced
relation:

| Problem | Standard SQL shape | Materialize shape |
|---|---|---|
| Shortest path | enumerate paths, `MIN` outside | `MIN(len)` per pair inside the binding |
| Connected components | reach sets, `MIN` outside | min-label propagation with `GROUP BY node` inside |
| Tree rollup | closure join then `SUM` | `SUM` over children per iteration with `LEFT JOIN` on the binding |
| Longest path in a DAG | all paths | `MAX(depth)` per node inside |
| Permission inheritance | reachability, no overrides | reachability with `NOT EXISTS` override inside the binding |

Common mis-specifications the skill must catch: "all paths" when
reachability is meant; "connected" on a directed relation without weak vs
strong; "total under each node" without deciding own-value inclusion and
shared-child counting; undirected data stored one way; asking for one
shortest path and getting ties.

## Skill layout

```
skills/mz-graph-queries/
  SKILL.md            decision procedure, under ~250 lines
  README.md           user-facing overview
  DEVELOPMENT.md      how the skill was built and how to test changes
  references/
    hierarchies.md    trees: descendants, ancestors, depth, root, ordering
    rollups.md        tree sums, BOM explosion, DAG double counting
    reachability.md   closure, k-hop, expiring edges, cycles, topo level, impact
    shortest-paths.md unweighted, weighted, witness path via breadcrumbs
    components.md     connected components, SCC, entity resolution
    permissions.md    inheritance with overrides, ReBAC mapping
    semantics.md      evaluation model, multiset rule, delay idiom, typing,
                      limits, optimizer blind spots, EXPLAIN, update locality,
                      how divergence presents on a cluster
    migrating.md      WITH RECURSIVE, CONNECT BY, USING KEY translations
    context-graphs.md agent questions mapped to families, registry edges,
                      effective-dated edges for as-of queries
```

Name: `mz-graph-queries`. Description trigger words: recursive CTE, WITH
RECURSIVE, WITH MUTUALLY RECURSIVE, hierarchy, tree, graph, org chart, bill
of materials, reachability, shortest path, connected components, permission
inheritance, lineage, impact analysis, context graph traversal, transitive
closure, cycle detection, topological order.

### SKILL.md workflow

1. **Classify the ask.** Structure (tree, DAG, general graph); direction
   (directed, undirected so symmetrize first, mutual); output (membership,
   per-node min/max/sum, witness path); lifetime (one-shot `SELECT` or
   maintained view). A phrasing-to-family table including the
   mis-specifications above.
2. **Write the recursion from the pattern.** Declare column types and cast
   every branch. Put the aggregate inside the binding and recurse from the
   reduced relation. Choose `UNION` vs `UNION ALL` by convergence. Carry
   narrow keys through the loop and join payload back in the body. Bound
   every recursive reference in non-linear recursion.
3. **Prove termination.** Checklist: monotone binding, or aggregate that
   bounds how often each row's value changes; cycles handled by set
   semantics; for non-monotone bindings state the progress measure.
4. **Guard and verify.** `ERROR AT RECURSION LIMIT` on maintained views,
   above the expected diameter. Step `RETURN AT RECURSION LIMIT 1, 2, 3`.
   Mutation check: insert and delete an edge, confirm the new answer.
5. **Make it maintainable.** Index loop-invariant inputs on the join key.
   Check update locality; name violating patterns and when to compute
   one-shot instead.

Also in the body: compact `EXPLAIN` reading, the typing errors and fixes, a
table of things standard SQL forbids that WMR allows, and hand-offs to the
freshness, memory and ontology skills.

### Reference file layout

Every reference file: the problem statements it answers; fixture tables
used; one verified pattern per problem with expected output on the fixture;
convergence argument; the standard-SQL shape and why it changes; pitfalls.
Numeric fixpoints (PageRank) appear only in `semantics.md` as the
update-locality counterexample.

## Shared fixture domain

One fictional company. All reference SQL and all eval tasks run against it.

| Tables | Shape | Families |
|---|---|---|
| `employees(id, manager_id, name, salary)` | tree, one root | descendants, ancestors, depth, root, ordered display, salary rollup |
| `parts(id, name)`, `bom(parent_id, child_id, qty)` | DAG with quantities | BOM explosion, shared-component double counting |
| `accounts(id, ...)`, `transfers(src, dst, amount, ts)` | directed, cyclic, timestamped | reachability, k-hop, cycle detection, SCC, expiring edges |
| `groups(id, parent_id)`, `memberships(user_id, group_id)`, `permissions(group_id, doc_id, level)` | tree with overrides | permission inheritance, NOT EXISTS override, point check |
| `customer_links(a, b, score)` | undirected, weighted | connected components, same-as clustering with threshold |
| `roads(src, dst, km)` | undirected, weighted | BFS hop count, weighted shortest path, one witness path |
| `pipelines(id, ...)`, `depends_on(task, prereq)` | DAG | topological level, downstream impact, upstream blast radius |

Planted traps in the eval-scale fixture: a manager loop in the org tree, a
shared sub-assembly in the BOM, a payment ring, an override in the
permission tree, unsymmetrized customer links, one-way road rows for a
two-way network.

## Eval harness

```
evals/mz-graph-queries/
  README.md              operation, recorded results
  build_fixture.py       fixture generator (seeded, --scale, --traps), emits SQL
  reference.py           independent Python answer keys, initial + post-mutation
  tasks/                 one prompt file per task + metadata (family, output
                         columns, mutation script, grading mode set|multiset)
  grade.py               diff agent views vs keys, apply mutations, re-diff,
                         convergence via hydration status, guardrail via view
                         definition; per-task JSON + manual-axis worksheet
  run_cleanroom.sh       one authoring round; conditions {sonnet,opus} x {bare,skill}
  preflight.sh           permission matrix check (single mode)
  bench-psql.template    pinned psql wrapper
  verify_skill_sql.sh    extract fenced SQL from references/, run on small
                         fixture, compare to expected/
  expected/              expected outputs for skill SQL blocks
  rubric.md              five axes: initial correctness, post-mutation
                         correctness, convergence and guardrails,
                         maintainability, explanation
  GRADING-TEMPLATE.md    per-run worksheet
```

Task set: about fourteen prompts covering every family and every trap.
Examples: descendants of a manager where the data has a loop; total kit
cost where a bolt appears under two assemblies; accounts within three hops
of a flagged account phrased as "all paths"; effective document access with
an override; customer clusters above a score threshold; cheapest route with
one witness path; downstream pipelines affected by a change; a colleague's
`UNION ALL` closure that never returns and must be fixed; a maintained view
that must stay correct after a mutation.

Clean-room rules carried over from `evals/mz-optimize-memory`: agent's only
database route is the generated `psql` wrapper pinned to the run schema
(read-write within it); no network, no skills except the one under test;
answer keys structurally unreachable; ancestor `CLAUDE.md` refusal; auto
memory disabled.

## Delivery and validation

Repo changes: the skill directory, the eval directory, a row in the root
`README.md` and `CLAUDE.md` skill tables, a one-line pointer from
`skills/materialize-debug-freshness/references/attribution.md` to the new
skill. The docs skill's recursive-CTEs page is unchanged.

Order of work: fixture generator and reference implementation first; then
reference files, each verified against the fixture as written; then
`SKILL.md`; then the harness, a Haiku smoke run, and one graded Sonnet cell
per condition to calibrate the rubric. Opus cells are scheduled by the user.

Skill-text testing: a usability pass by a fresh agent with the skill and a
disposable fixture, reporting ambiguous or misleading text. Claims about
tool behavior are verified against Materialize before they stay in.

Definition of done: every SQL block passes `verify_skill_sql.sh`; the smoke
run completes end to end; at least one skill cell and one bare cell are
graded and recorded in the eval README; `claude plugin validate . --strict`
passes.

Assumptions: Materialize runs locally in Docker from the `materialized`
image already present; the eval uses the Claude Code CLI; nothing depends
on a live customer environment.

## Out of scope

Live-cluster diagnosis of recursive views, relationship modeling, numeric
fixpoint algorithms as supported patterns, SQL/PGQ, bi-temporal modeling
beyond effective-dated edge filtering.
