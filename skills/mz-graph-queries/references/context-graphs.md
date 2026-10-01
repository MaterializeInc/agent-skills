# Context graphs for agents

An agent asking "what is this, what is it connected to, and what breaks if it
changes" is asking a graph question over the ontology's objects and their
registered relationships. This file is a map. It routes those questions to the
patterns in the other reference files, turns the ontology's relationship
registry into one typed edge relation every pattern can walk, and gives the one
pattern specific to agent work: a traversal that reconstructs the graph as it
stood at a past instant.

Fixture tables used: `transfers`. Every runnable block assumes
`references/fixture.sql` is loaded.

## What people mean

The term covers decision-trace graphs in the venture sense (Foundation
Capital), the metadata and lineage graphs catalog vendors ship, agent-memory
graphs, and Materialize's sense: a set of live, governed data products with
maintained relationships between them. The senses disagree about what the nodes
are and agree about what gets asked of them, so all of them reduce to the same
traversals, and those traversals are the patterns in this skill.

## Agent questions to patterns

| The agent asks | Pattern | Where |
|---|---|---|
| What is related to X within n hops | `hops` | [reachability.md#within-k-hops](reachability.md#within-k-hops) |
| What breaks if X changes | `downstream` | [reachability.md#impact-analysis-both-directions](reachability.md#impact-analysis-both-directions) |
| Why is X wrong, what fed it | `upstream` | [reachability.md#impact-analysis-both-directions](reachability.md#impact-analysis-both-directions) |
| Which precedent or decision chain led here | `chain` over a `caused_by` edge, carrying depth | [hierarchies.md#ancestors-of-one-node](hierarchies.md#ancestors-of-one-node) |
| Is this the same customer as that one | `label` over match edges | [components.md#entity-resolution-clusters-and-golden-records](components.md#entity-resolution-clusters-and-golden-records) |
| Can this agent see this record | `user_access` | [permissions.md#per-user-and-a-point-check](permissions.md#per-user-and-a-point-check) |
| Who is in the same ring | `scc_trim` | [components.md#strongly-connected-components-without-the-closure](components.md#strongly-connected-components-without-the-closure) |
| What did the relationship graph look like when the decision was made | the as-of filter below | this file |

## Edges from the relationship registry

`core.public.relationships` is the ontology's registry of direct reference
edges. Its columns are `relationship_name`, `table_name`, `columns` (a jsonb
array), `referenced_table`, `referenced_columns` (a jsonb array),
`cardinality`, `optionality`, and `description`. It is the authority on which
edges exist, so generate the traversable edge relation from it rather than from
column-name conventions.

The registry describes edges; it does not carry them. Emit one `SELECT` per
registered relationship, reading the referencing object into a common
five-column shape, and union them into one `edges` view. Ids are unique only
within an object, so `(src_object, src_id)` is the node identity a traversal
joins on, and every pattern in this skill walks that pair in place of a bare
id.

<!-- verify: skip -->
```sql
CREATE VIEW edges AS
-- orders_customer: many_to_one, required.
SELECT 'orders'      AS src_object, order_id::text                AS src_id,
       'customers'   AS dst_object, customer_id::text             AS dst_id,
       'orders_customer' AS relationship
FROM core.public.orders
UNION ALL
-- order_items_order: composite reference, encoded positionally on both sides.
SELECT 'order_items', store_id::text || ':' || order_item_id::text,
       'orders',      store_id::text || ':' || order_id::text,
       'order_items_order'
FROM core.public.order_items
UNION ALL
-- employees_manager: optional, so the null side is not an edge.
SELECT 'employees', employee_id::text,
       'employees', manager_id::text,
       'employees_manager'
FROM core.public.employees
WHERE manager_id IS NOT NULL;

CREATE INDEX edges_by_src ON edges (src_object, src_id);

-- Every pattern in this skill then walks `edges` with the type in the key.
WITH MUTUALLY RECURSIVE (ERROR AT RECURSION LIMIT 100)
    reach(object text, id text) AS (
        SELECT dst_object, dst_id FROM edges
        WHERE src_object = 'customers' AND src_id = 'c1'
        UNION
        SELECT e.dst_object, e.dst_id
        FROM reach r
        JOIN edges e ON e.src_object = r.object AND e.src_id = r.id
    )
SELECT object, id FROM reach ORDER BY 1, 2;
```

An `optionality` of `optional` means the referencing columns may be null, and a
null is the absence of an edge rather than an edge to nothing.

Identity resolution is not a traversal problem. The ontology skill resolves
cross-source identity once in `core.internal` and publishes the result; this
skill walks the edges `core.public` publishes and takes their node identity as
given. The `label` pattern in
[components.md#entity-resolution-clusters-and-golden-records](components.md#entity-resolution-clusters-and-golden-records)
is how that resolution is computed inside the boundary, not a reason to
re-resolve identity in a use-case database.

## As-of traversal on effective-dated edges

"What did the graph look like when the decision was made" is a filter, not a
different traversal. Bound the edge relation by that instant and walk it.

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

On the fixture this returns a1, a2 and a3. The a3 to a4 transfer is stamped
00:04, after the cutoff, so a4 and a5 are not in the graph the decision saw.

It converges because the binding is topped by `UNION` over a set of nodes
bounded by `transfers`, and the filter only ever removes edges. A traversal
that terminates on a graph terminates on every subgraph of it.

An effective-dated edge table with a valid-from and a valid-to pair is filtered
the same way, with `WHERE valid_from <= <as_of> AND (valid_to IS NULL OR
valid_to > <as_of>)` in place of the single comparison. Three properties of
the shape matter:

- The filter goes inside the binding. Predicates are never pushed into a
  recursive binding
  ([semantics.md#what-the-optimizer-will-not-do](semantics.md#what-the-optimizer-will-not-do)),
  so the same `WHERE` in the outer query prunes the answer and not the walk.
- It goes on both branches. The seed branch and the recursive branch read the
  edge relation separately, and filtering one says nothing about the other.
- Replacing the constant with `mz_now()` turns the one-shot as-of query into a
  maintained "current" graph whose edges age in and out on the clock
  ([reachability.md#edges-that-expire](reachability.md#edges-that-expire)).

## Keep the loop narrow

An agent-facing traversal is read constantly and the graph it walks is wide.
Carry ids and the columns the recursion actually needs. Projection pushdown
does not happen inside a binding, so every declared column is materialized
every iteration
([semantics.md#what-the-optimizer-will-not-do](semantics.md#what-the-optimizer-will-not-do)).
Join names, descriptions and payload back in the body, after the fixpoint.

Index the edge relation on the join key. Imported indexes are used inside the
loop, so `CREATE INDEX ... ON edges (src_object, src_id)` is the main lever
available: it indexes the static side of the join the recursion repeats
([semantics.md#what-the-optimizer-will-not-do](semantics.md#what-the-optimizer-will-not-do)).

Put `ERROR AT RECURSION LIMIT` on anything maintained, with the limit well
above the expected diameter. On a `UNION`-topped traversal every change is a
row change and the guard always fires. On a binding topped by a reduce it goes
silent once only values are changing, so guard those with
`RETURN AT RECURSION LIMIT` plus a check on the returned state
([semantics.md#recursion-limits](semantics.md#recursion-limits)).

Check update locality before promoting a traversal to a maintained view.
Reachability and rollups have it; all-pairs scores do not, and a view without
it recomputes most of its state for one input change
([semantics.md#update-locality](semantics.md#update-locality)).

## Pitfalls

- Deriving edges from column-name conventions instead of the registry. The
  ontology treats `core.public.relationships` as the complete record of
  reference edges; a convention finds the edges someone remembered to name.
- Unioning ids from different objects into one key column. Order 1 and product
  1 become the same node. The object type is part of the key.
- Encoding the two sides of a composite reference differently. The join finds
  nothing and the traversal looks like a graph with no edges.
- Publishing heuristic matches as reference edges. They belong in `edges` as
  the reference edges of a match object, with confidence and effective time
  attached, so a traversal can filter on them.
- Putting the as-of filter in the outer query. It filters the answer, not the
  walk, so the traversal still expands the whole present-day graph
  ([semantics.md#what-the-optimizer-will-not-do](semantics.md#what-the-optimizer-will-not-do)).
- Filtering only the seed branch. That yields a graph whose first hop is
  as-of and whose every later hop is current
  ([reachability.md#edges-that-expire](reachability.md#edges-that-expire)).
- Maintaining every traversal because an agent might ask for it. Check update
  locality first: without it the view redoes a large fraction of its work on
  every input change
  ([semantics.md#update-locality](semantics.md#update-locality)).
