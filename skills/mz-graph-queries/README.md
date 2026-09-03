# mz-graph-queries

A skill for writing graph and hierarchy queries in Materialize with
`WITH MUTUALLY RECURSIVE`. It takes a question about a tree, a DAG or a graph,
routes it to a verified pattern, and shows how to make that pattern converge,
guard it against a bad edge, and keep it cheap to maintain as the data changes.

## Install

```bash
npx skills add MaterializeInc/agent-skills@mz-graph-queries
```

## What it covers

`SKILL.md` is the decision procedure: classify the ask, write the recursion,
prove it terminates, guard and verify it, make it maintainable. Behind it are
nine reference files.

- `references/semantics.md`: how the fixpoint loop evaluates, why multisets
  and not sets decide convergence, the one-iteration delay idiom, mandatory
  column types, recursion limits and what they do and do not catch, the
  optimizations that stop at a recursive binding, how to read `EXPLAIN`, and
  update locality.
- `references/hierarchies.md`: descendants, ancestors, depth and root, a
  maintained closure table, indented ordered display, and cycles in a "tree".
- `references/rollups.md`: subtree sums with the aggregate inside the binding,
  height above the leaves, bill-of-materials explosion with quantities, kit
  cost, and counting a shared node once against once per path.
- `references/reachability.md`: reachable sets, whole-graph closure, k-hop
  neighborhoods, edges that expire on a clock, the cycle audit, topological
  level on a DAG, and impact analysis in both directions.
- `references/shortest-paths.md`: fewest hops, cheapest route, one witness
  path via breadcrumbs, and a single target.
- `references/components.md`: connected components by min-label propagation,
  match thresholds and golden records, and strongly connected components with
  and without the transitive closure.
- `references/permissions.md`: inheritance down a group tree with overrides,
  multiple parents and cycles, an indexed per-user view and point check,
  denies, and the Zanzibar relation-tuple shape.
- `references/migrating.md`: translating `WITH RECURSIVE`, SQL Server
  `MAXRECURSION`, Postgres `CYCLE`, Oracle `CONNECT BY` and DuckDB
  `USING KEY`, plus the habits from those dialects that are silently wrong
  here rather than loudly rejected.
- `references/context-graphs.md`: agent questions mapped onto the families
  above, typed edges generated from an ontology's relationship registry, and
  as-of traversal over effective-dated edges.

## Try it

`references/fixture.sql` is the world every example runs against: an org tree,
a bike bill of materials with a shared bolt, a ring of account transfers, a
group permission tree with an override, unsymmetrized customer links, a road
network stored one way, and a dbt-shaped dependency DAG.

```bash
psql "$MZ_URL" -c 'CREATE SCHEMA graph_demo' \
  -c 'SET search_path = graph_demo' \
  -f skills/mz-graph-queries/references/fixture.sql
```

Then paste any block from a reference file. Each one states the output it
produces on this fixture, so a difference is a real difference.

## How it was built

`DEVELOPMENT.md` records the provenance of every claim, the fixture and its
planted traps, and how to test a change. The verifier and the graded agent
evaluation live in `evals/mz-graph-queries/` in the
[agent-skills](https://github.com/MaterializeInc/agent-skills) repository.
