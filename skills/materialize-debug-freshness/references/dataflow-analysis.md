# Dataflow analysis with EXPLAIN

This guide covers Steps 6 to 8 of the freshness workflow. It explains which `EXPLAIN` commands to use, what they return, and how to read them.

- [Command reference](#command-reference)
- [Cluster level](#cluster-level)
- [Object level](#object-level)
- [Reading operators](#reading-operators)
- [Operator costs](#operator-costs)
- [Operator skew](#operator-skew)
- [Mapping to SQL](#mapping-to-sql)

Use these commands with the `query` tool and a specific cluster. `EXPLAIN ANALYZE` runs on one replica. If your cluster has more than one replica, pass `cluster_replica` as well. `EXPLAIN` output can change between versions, so check what your environment returns.

## Command reference

| Command | What it returns | Use it when |
|---|---|---|
| `EXPLAIN ANALYZE CLUSTER CPU, MEMORY` | One row per dataflow: `object`, `global_id`, `total_elapsed`, `total_memory`, `total_records`. | You want to find a compute problem. It ranks dataflows on the replica. |
| `EXPLAIN ANALYZE CLUSTER MEMORY, CPU` | Same rows, but memory columns come first and are sorted by memory. | You want to find a memory problem. The first property listed is the sort key. |
| `EXPLAIN ANALYZE CLUSTER CPU WITH SKEW` | Adds `worker_id`, `max_operator_cpu_ratio`, `worker_elapsed`, `avg_elapsed`. | You want to see if a dataflow has work spread unevenly across workers. |
| `EXPLAIN ANALYZE CPU, MEMORY FOR MATERIALIZED VIEW <name>` | A tree plan. Each row is one operator with its own cost. | You want to find where time and memory go inside one dataflow. |
| `EXPLAIN ANALYZE CPU, MEMORY FOR INDEX <name>` | Same as above, but for an index. | Same as above, but the object is an index. |
| `EXPLAIN ANALYZE CPU WITH SKEW FOR ...` | One row per worker per operator: `cpu_ratio`, `worker_elapsed`, `avg_elapsed`, `total_elapsed`. | You want to find one operator where the work lands on a single worker. |
| `EXPLAIN ANALYZE MEMORY WITH SKEW FOR ...` | Same shape as above with `memory_ratio`, `worker_memory`, `records_ratio`, `worker_records`. | You want to see if arrangements are unevenly sized across workers. |
| `EXPLAIN ANALYZE HINTS FOR ...` | Per TopK: `levels`, `to_cut`, `hint`, `savings`. | A TopK holds many more records than the result needs. The hint is for your report. |
| `EXPLAIN ANALYZE ... AS SQL` | The query that `EXPLAIN ANALYZE` would run, without running it. | You want to sort operators by cost, add `lir_id`, or filter a large plan. |
| `EXPLAIN PHYSICAL PLAN WITH (node identifiers) AS TEXT FOR ...` | The plan tree with `LirId(N)` labels. It shows column names, predicates, and `project`, `filter`, and `pushdown` for each source. | You want to turn an operator into the SQL code behind it. |
| `SHOW CREATE MATERIALIZED VIEW <name>` | The definition of the object. | You want to find which part of the SQL a plan node came from. |

Syntax:

```
EXPLAIN ANALYZE
      CPU [, MEMORY] [WITH SKEW]
    | MEMORY [, CPU] [WITH SKEW]
    | HINTS
FOR INDEX <name> | MATERIALIZED VIEW <name>
[ AS SQL ];

EXPLAIN ANALYZE CLUSTER
      CPU [, MEMORY] [WITH SKEW]
    | MEMORY [, CPU] [WITH SKEW]
[ AS SQL ];
```

You can use `CPU` and `MEMORY` in any order, but only once each. The order decides the column order and the sort key. You need `USAGE` on the schemas for all relations in the explainee to run these.

## Cluster level

Start here. Dataflows on a replica share its CPU and memory. A slow object might be waiting on an unrelated one.

```sql
EXPLAIN ANALYZE CLUSTER CPU, MEMORY;
```

| Column | Meaning |
|---|---|
| `object` | The full name of the object. |
| `global_id` | The dataflow's id. Indexes look like `u<N>`. Materialized views usually look like `t<N>`. |
| `total_elapsed` | Total CPU time across all workers since the dataflow started. |
| `total_memory` | Memory used by the dataflow. |
| `total_records` | Records held in its arrangements. |

How to read it:

- `total_elapsed` is a total sum, not a rate. A dataflow that has run for weeks will look larger than one created this morning, even if the new one is the current problem. Compare it to the object's age from [object age](attribution.md#object-age).
- One object can have several rows if it runs more than one dataflow. Read each `global_id` separately.
- If metrics are null, the dataflow has not reported yet.
- `global_id` is a dataflow id, and for a materialized view it is a transient
  `t<N>` that appears in no catalog table. The `object` column is the fully
  qualified name and is the only identifier to carry forward into
  [operator costs](#operator-costs) or any catalog query.

Then look for skew on the replica:

```sql
EXPLAIN ANALYZE CLUSTER CPU WITH SKEW;
```

Ratios near 1 mean work is spread evenly. This helps you decide which dataflow to check next.

## Object level

```sql
EXPLAIN ANALYZE CPU, MEMORY FOR MATERIALIZED VIEW materialize.public.my_view;
EXPLAIN ANALYZE CPU, MEMORY FOR INDEX materialize.public.my_index;
```

The output is a tree plan. Each row is one operator. The tree is indented by nesting. `total_elapsed` does not include child operators, so the cost belongs to the operator on that row.

Large plans use bindings: `With l13 = ...` starts a subplan. Other parts of the tree call it `Arranged l13`, `Read l13`, or `Stream l13`. Expensive work is often in bindings because they are used more than once.

The tree is ordered for reading. To order by cost, use the `AS SQL` method below.

Per-worker numbers:

```sql
EXPLAIN ANALYZE CPU WITH SKEW FOR INDEX materialize.public.my_index;
```

Columns are `operator`, `worker_id`, `cpu_ratio`, `worker_elapsed`, `avg_elapsed`, and `total_elapsed`. There is one row per worker per operator. A ratio below 1 means a worker does less than its share. A ratio above 1 means more. Some difference is normal. If one worker is much higher than 1 and others are near 0, that is skew. The dataflow moves at that worker's speed.

## Reading operators

What the costly operators tell you:

| Operator | What it tells you |
|---|---|
| `Arrange` with an empty key | Every record goes to one worker. This happens with cross joins or joins where all predicates are inequalities. Every join needs at least one equality to spread work. Check this first for skew. |
| `Differential Join %0 » %1 » ...` | The join order from left to right. In a long chain, an early stage that grows will slow down everything after it. |
| `Delta Join` | A different join strategy. It does not build intermediate arrangements the same way. |
| `Non-monotonic TopK` | A generic TopK. It holds more records than the result needs if group sizes are too high. Compare `total_records` to the actual rows returned, then run `EXPLAIN ANALYZE HINTS`. |
| `Bucketed Hierarchical GroupAggregate` | A `MIN`/`MAX` aggregate held as a tower of arrangements. It shows bucket sizes. It is heavy on large groups. |
| `Accumulable GroupAggregate` | Used for `SUM`, `COUNT`, etc. It is cheap per update. The arrangement grows with the number of groups. |
| `Non-incremental GroupAggregate` | Used for window functions. These are recomputed rather than updated. This is the most expensive reduction. |
| `Threshold Diffs`, `Consolidating Union` | Points that hold memory based on input size. Common in `EXCEPT` and `DISTINCT` shapes. |
| `Table Function` | Creates more rows: `jsonb_each`, `unnest`, `generate_series`. Each one increases the record count for all operators above it. |
| `Read <id>` / `Stream <id>` / `Arranged <id>` | Where the input comes from and if it is in memory. |
| `Fused ...` | This operator is combined with the one below it. This is an optimization. |

The `Source` section in a plan shows `project`, `filter`, and `pushdown` for each source. `filter` is what is applied. `pushdown` is what is sent to storage. If a predicate is in `filter` but not in `pushdown`, it is read first and then discarded. This is an un-pushed predicate to report.

## Operator costs

This ranks the operators of one dataflow by CPU. It is the skill's own query
rather than something derived from `EXPLAIN ANALYZE`, so nothing needs
hand-editing.

`mz_introspection` is cluster-scoped, so run this with `query` against the
cluster that hosts the dataflow. `mz_mappable_objects.name` is already a fully
qualified name, so it is the only input.

```sql
with per_operator as (
    select
        mlm.global_id
        , mlm.lir_id
        , sum(mse.elapsed_ns) as total_ns
    from mz_introspection.mz_lir_mapping as mlm
    cross join generate_series(
        (mlm.operator_id_start)::int8, (mlm.operator_id_end - 1)::int8
    ) as valid_id
    join mz_introspection.mz_scheduling_elapsed_per_worker as mse
        on mse.id = valid_id
    join mz_introspection.mz_mappable_objects as mo
        on mo.global_id = mlm.global_id
    where mo.name = 'materialize.public.my_view'
    group by 1, 2
)

select
    mlm.lir_id
    , mlm.operator
    , p.total_ns / 1000 * '1 microsecond'::interval as total_elapsed
    , round(100.0 * p.total_ns / sum(p.total_ns) over (), 1) as percent_of_dataflow
from mz_introspection.mz_lir_mapping as mlm
left join per_operator as p on p.global_id = mlm.global_id and p.lir_id = mlm.lir_id
join mz_introspection.mz_mappable_objects as mo on mo.global_id = mlm.global_id
where mo.name = 'materialize.public.my_view'
order by p.total_ns desc nulls last
limit 15;
```

`lir_id` is the join key to the plan in [mapping to SQL](#mapping-to-sql).
The object name appears twice on purpose: once inside the aggregate and once in
the outer query. With a left join the aggregate no longer constrains which plan
nodes come back, so without the outer filter the result is every object's plan on
the cluster.

The join to the per-operator costs is a left join on purpose. A plan node whose
`operator_id_start` equals its `operator_id_end` owns no dataflow operators, so
its cost is null rather than zero. That node is a passthrough, and an inner join
would delete the row, returning an empty result for a plan that genuinely has one
node. A single operator with a null cost is therefore an answer, not a failure:
the work lives in whatever that node reads, and the object name in `Read <name>`
or `Arranged <name>` is where to go next.

`percent_of_dataflow` says how much of the dataflow one operator accounts for, so
operators stay comparable however long the dataflow has run. Read the top of the
list against the
rest of it. One operator holding most of the dataflow is where to start; a list
that declines gradually means the cost is spread and no single operator is the
answer.

For an index, pass the index's own fully qualified name. For an index on a
materialized view this returns almost nothing, which is itself the answer. See
[mapping to SQL](#mapping-to-sql).

## Operator skew

Whether an operator's work is spread across workers or landing on one. Same
input, same cluster rule.

```sql
with per_worker as (
    select
        mlm.global_id
        , mlm.lir_id
        , mse.worker_id
        , sum(mse.elapsed_ns) as worker_ns
    from mz_introspection.mz_lir_mapping as mlm
    cross join generate_series(
        (mlm.operator_id_start)::int8, (mlm.operator_id_end - 1)::int8
    ) as valid_id
    join mz_introspection.mz_scheduling_elapsed_per_worker as mse
        on mse.id = valid_id
    join mz_introspection.mz_mappable_objects as mo
        on mo.global_id = mlm.global_id
    where mo.name = 'materialize.public.my_view'
    group by 1, 2, 3
)

, summary as (
    select
        global_id
        , lir_id
        , sum(worker_ns) as total_ns
        , max(worker_ns) as max_worker_ns
        , avg(worker_ns) as avg_worker_ns
    from per_worker
    group by 1, 2
)

select
    mlm.lir_id
    , mlm.operator
    , s.total_ns / 1000 * '1 microsecond'::interval as total_elapsed
    , round((s.max_worker_ns / nullif(s.avg_worker_ns, 0))::numeric, 2) as max_worker_ratio
from mz_introspection.mz_lir_mapping as mlm
left join summary as s on s.global_id = mlm.global_id and s.lir_id = mlm.lir_id
join mz_introspection.mz_mappable_objects as mo on mo.global_id = mlm.global_id
where mo.name = 'materialize.public.my_view'
order by s.total_ns desc nulls last
limit 15;
```

`max_worker_ratio` is the busiest worker against the average for that operator.
A ratio of 1 means work is evenly distributed. The maximum skew is equal to the
worker count, so on a replica with 8 workers a ratio near 8 means one worker is
doing all the work. Compare the expensive operators against each other and
against the worker count.

Read the ratio only for operators that are already expensive. A skewed operator
accounting for a fraction of a percent of the dataflow is not the problem, and
empty-key arrangements are common enough that hunting the pattern first produces
false positives.

## Mapping to SQL

An operator name becomes a finding once you link it to the SQL that made it.
Three things to settle: which object owns the SQL, which upstream views were
inlined into the same dataflow, and which plan node each cost belongs to.

### Step 1: Find which object owns the SQL

A materialized view owns its dataflow, so its own definition is the SQL.

An index does not. Resolve what it indexes:

```sql
select
    idb.name || '.' || isch.name || '.' || io.name as index_name
    , odb.name || '.' || osch.name || '.' || o.name as indexed_object
    , o.type as indexed_object_type
from mz_catalog.mz_indexes i
join mz_catalog.mz_objects io on io.id = i.id
join mz_catalog.mz_schemas isch on isch.id = io.schema_id
join mz_catalog.mz_databases idb on idb.id = isch.database_id
join mz_catalog.mz_objects o on o.id = i.on_id
join mz_catalog.mz_schemas osch on osch.id = o.schema_id
join mz_catalog.mz_databases odb on odb.id = osch.database_id
where idb.name || '.' || isch.name || '.' || io.name = 'materialize.public.my_index';
```

Where that lands changes what you analyze:

| Indexed object | Where the work is | What to do |
|---|---|---|
| Materialized view | In the materialized view's own dataflow. The index's dataflow is just an `Arrange` over a `Stream` of it. | Re-run `EXPLAIN ANALYZE` against the materialized view, and read its definition. |
| Plain view | In the index's dataflow. A plain view has no dataflow of its own, so its whole body is built here. | Keep analyzing `FOR INDEX`, and read the view's definition. |
| Table | In the index's dataflow, and it is just an arrangement of the table. | Little to find in SQL. Look at the table's size and the index keys. |

An index on a materialized view that shows high lag is inheriting it. The
lag belongs to the materialized view.

### Step 2: Find the views inlined into the dataflow

A plain view has no dataflow of its own, so wherever it is used its body is
inlined into the consumer. The expensive operator may come from an upstream
view's SQL rather than from the definition you just read, and that holds
recursively: a view inlined into the dataflow brings its own view dependencies
with it.

`mz_object_dependencies` gives the logical dependencies. Any dependency of type
`view` was inlined; a materialized view, table, source, or index is a boundary
with its own dataflow, so the walk stops there.

```sql
with mutually recursive
    inlined (object_id text, depth int) as (
        select o.id, 0
        from mz_catalog.mz_objects o
        join mz_catalog.mz_schemas s on s.id = o.schema_id
        join mz_catalog.mz_databases db on db.id = s.database_id
        where db.name || '.' || s.name || '.' || o.name = 'materialize.public.my_view'
        union
        select d.referenced_object_id, n.depth + 1
        from inlined n
        join mz_internal.mz_object_dependencies d on d.object_id = n.object_id
        join mz_catalog.mz_objects dep on dep.id = d.referenced_object_id
        where dep.type = 'view'
          and n.depth < 20
    )

select
    n.depth
    , db.name || '.' || s.name || '.' || o.name as full_name
    , o.type
from (select object_id, min(depth) as depth from inlined group by object_id) n
join mz_catalog.mz_objects o on o.id = n.object_id
left join mz_catalog.mz_schemas s on s.id = o.schema_id
left join mz_catalog.mz_databases db on db.id = s.database_id
order by n.depth, full_name;
```

Seed it with the object whose SQL owns the dataflow from Step 1, named
directly. Group by `min(depth)`, because a view reached along two paths
appears at several depths. Depth 0 is the object itself; everything below it
is inlined SQL that is part of this dataflow's cost.

Read those definitions too, with `SHOW CREATE VIEW`. They are as much a part of
the dataflow as the object's own body.

### Step 3: Attach each cost to a plan node

```sql
EXPLAIN PHYSICAL PLAN WITH (node identifiers) AS TEXT
FOR MATERIALIZED VIEW materialize.public.my_view;
```

Every node is labelled, and human-readable column names are on by default:

```
materialize.public.my_view:
  →Map/Filter/Project // { node_id: LirId(10) }
    Project: #0..=#11
      →Non-monotonic TopK // { node_id: LirId(9) }
        Group By #0
        Order By #12 asc nulls_last
        Limit 1
        →Union // { node_id: LirId(7) }
          →Non-monotonic TopK // { node_id: LirId(5) }
            Group By #0
            Order By #1 desc nulls_first
            Limit 1
            →Read raw.public.events // { node_id: LirId(4) }

Source raw.public.events
  project=(#0, #1, #4..=#6)
  filter=((#2{type} = "company") AND (#5{domain}) IS NOT NULL)
  pushdown=((#2{type} = "company") AND (#5{domain}) IS NOT NULL)
```

`LirId(5)` is the same as `lir_id = 5` in the cost query, so a cost of 46 seconds
on `lir_id` 5 belongs to that TopK.

The named objects in the plan tell you where a boundary is. `Read`, `Stream`, or
`Arranged` followed by an object name is data arriving from something with its own
dataflow. Operators with no such name are built here, from either the object's own
SQL or an inlined view's.

Group keys, join predicates, and filters carry their original column names, which
ties an operator to a clause across the definitions from Steps 1 and 2.

Report it as: this operator, costing this much, comes from this clause, in this
view, inlined into this dataflow.
