# Attribution queries

Catalog queries for Steps 1 to 5 of the freshness workflow. Lag numbers live in
the catalog, so these read the catalog.

- [Name resolution](#name-resolution)
- [Current lag](#current-lag)
- [Status sweep](#status-sweep)
- [Recent peaks](#recent-peaks)
- [Lag history](#lag-history)
- [Object age](#object-age)
- [Attribution walk](#attribution-walk)
- [Ingestion](#ingestion)
- [Sink status](#sink-status)
- [Compute gates](#compute-gates)

## Name resolution

Every query here takes a fully qualified `database.schema.object` name and
returns one. Ids stay inside the queries. This matters because ids are not
stable and not always resolvable: a blue/green deploy replaces objects, and
`EXPLAIN ANALYZE CLUSTER` reports materialized-view dataflows under transient
`t<N>` ids that appear in no catalog table.

The name is built the same way everywhere, and is the filter predicate:

```sql
db.name || '.' || s.name || '.' || o.name
```

which needs this join spine:

```sql
from mz_catalog.mz_objects o
join mz_catalog.mz_schemas s on s.id = o.schema_id
join mz_catalog.mz_databases db on db.id = s.database_id
```

Substitute the object you are investigating for `materialize.public.my_view` in
every query below.

## Current lag

This ranks every object by how far it is behind the current time, with its name, type, and cluster. `mz_objects` carries `cluster_id`, so one join covers every object type.

```sql
select
    db.name || '.' || s.name || '.' || o.name as full_name
    , o.type
    , c.name as cluster
    , l.lag
from mz_internal.mz_wallclock_global_lag l
join mz_catalog.mz_objects o on o.id = l.object_id
join mz_catalog.mz_schemas s on s.id = o.schema_id
join mz_catalog.mz_databases db on db.id = s.database_id
left join mz_catalog.mz_clusters c on c.id = o.cluster_id
where l.object_id like 'u%'
order by l.lag desc, full_name
limit 20;
```

The `u%` filter keeps system introspection objects out of the ranking.

Ordering by `full_name` after `lag` makes the result deterministic. Without it,
hundreds of objects tie at the same lag and the top 20 is arbitrary.

Read the ranking as a distribution, not a pass/fail list. What matters is
whether the top of it stands apart from the rest. One object at a minute while
the next is at two seconds is an outlier worth chasing; twenty objects within a
second of each other are all doing the same thing, and none of them is a
culprit.

To check one named object, add
`and db.name || '.' || s.name || '.' || o.name = 'materialize.public.my_view'`.

## Status sweep

Run this alongside the ranking, every time. A stalled source does not appear as
lag: its write frontier keeps advancing while its data sits frozen. Verified on a
source stalled for three days: the ranking showed three seconds of lag and the
frontier read the current wall-clock time to the second, while
`mz_source_statuses` reported it stalled throughout.

```sql
select
    'source' as kind
    , db.name || '.' || s.name || '.' || o.name as full_name
    , st.status
    , st.error
    , st.last_status_change_at::text as since
from mz_internal.mz_source_statuses st
join mz_catalog.mz_objects o on o.id = st.id
join mz_catalog.mz_schemas s on s.id = o.schema_id
join mz_catalog.mz_databases db on db.id = s.database_id
where st.status <> 'running'

union all

select
    'sink' as kind
    , db.name || '.' || s.name || '.' || o.name as full_name
    , st.status
    , st.error
    , st.last_status_change_at::text as since
from mz_internal.mz_sink_statuses st
join mz_catalog.mz_objects o on o.id = st.id
join mz_catalog.mz_schemas s on s.id = o.schema_id
join mz_catalog.mz_databases db on db.id = s.database_id
where st.status <> 'running'

order by since desc;
```

Zero rows means ingestion and delivery are healthy. Any row is a finding on its
own, whatever the ranking says. For ingestion health the status and its error
text are authoritative; lag and write frontier are not.

## Recent peaks

Also run this alongside the ranking. The ranking describes this instant, so a
peak that has already recovered leaves no trace in it.

```sql
select
    db.name || '.' || s.name || '.' || o.name as full_name
    , o.type
    , c.name as cluster
    , round(max(extract(epoch from h.lag))) as max_lag_s
    , round(avg(extract(epoch from h.lag))) as avg_lag_s
    , max(h.occurred_at)::text as last_sample
from mz_internal.mz_wallclock_global_lag_recent_history h
join mz_catalog.mz_objects o on o.id = h.object_id
join mz_catalog.mz_schemas s on s.id = o.schema_id
join mz_catalog.mz_databases db on db.id = s.database_id
left join mz_catalog.mz_clusters c on c.id = o.cluster_id
where h.object_id like 'u%'
group by 1, 2, 3
order by max_lag_s desc, full_name
limit 20;
```

An object whose `max_lag_s` towers over its `avg_lag_s` peaked and recovered.
Take its name into [lag history](#lag-history) for the shape, and read the
restart history in [compute gates](#compute-gates): a peak shared by several
objects across clusters in the same minute is a restart, and those dataflows were
rehydrating afterwards.

## Lag history

`mz_wallclock_global_lag_recent_history` has one sample per minute for the last 24 hours. Aggregate `extract(epoch from lag)`, which is the supported way to average and sum these values.

```sql
select
    db.name || '.' || s.name || '.' || o.name as full_name
    , count(*) as samples
    , min(h.occurred_at)::text as first_sample
    , max(h.occurred_at)::text as last_sample
    , round(avg(extract(epoch from h.lag))) as avg_lag_s
    , round(max(extract(epoch from h.lag))) as max_lag_s
from mz_internal.mz_wallclock_global_lag_recent_history h
join mz_catalog.mz_objects o on o.id = h.object_id
join mz_catalog.mz_schemas s on s.id = o.schema_id
join mz_catalog.mz_databases db on db.id = s.database_id
where db.name || '.' || s.name || '.' || o.name in (
    'materialize.public.my_view'
    , 'materialize.public.my_other_view'
)
group by full_name
order by max_lag_s desc;
```

A full day has about 1440 rows. Fewer rows means the object was created or replaced that recently. Whether it is still catching up is a separate question, answered by hydration status in [compute gates](#compute-gates).

To see the lag trend for one object:

```sql
select
    h.occurred_at::text as occurred_at
    , round(extract(epoch from h.lag)) as lag_s
from mz_internal.mz_wallclock_global_lag_recent_history h
join mz_catalog.mz_objects o on o.id = h.object_id
join mz_catalog.mz_schemas s on s.id = o.schema_id
join mz_catalog.mz_databases db on db.id = s.database_id
where db.name || '.' || s.name || '.' || o.name = 'materialize.public.my_view'
order by h.occurred_at desc
limit 60;
```

This view shows the lowest lag across all replicas. For per-replica numbers use `mz_wallclock_lag_history`, which has a `replica_id` column. It is a large relation, so filter it to one object and a short window:

```sql
select
    db.name || '.' || s.name || '.' || o.name as full_name
    , h.replica_id
    , count(*) as samples
    , round(max(extract(epoch from h.lag))) as max_lag_s
from mz_internal.mz_wallclock_lag_history h
join mz_catalog.mz_objects o on o.id = h.object_id
join mz_catalog.mz_schemas s on s.id = o.schema_id
join mz_catalog.mz_databases db on db.id = s.database_id
where db.name || '.' || s.name || '.' || o.name = 'materialize.public.my_view'
  and h.occurred_at > now() - interval '15 minutes'
group by 1, 2;
```

There will be one row with a null `replica_id` alongside the other rows.

## Object age

`EXPLAIN ANALYZE` reports `total_elapsed` as a running total since the dataflow
started, so an object that has been up for weeks outranks one created this
morning. Age makes those numbers comparable.

```sql
select
    db.name || '.' || s.name || '.' || o.name as full_name
    , count(*) as history_minutes
    , min(h.occurred_at)::text as first_sample
from mz_internal.mz_wallclock_global_lag_recent_history h
join mz_catalog.mz_objects o on o.id = h.object_id
join mz_catalog.mz_schemas s on s.id = o.schema_id
join mz_catalog.mz_databases db on db.id = s.database_id
where db.name || '.' || s.name || '.' || o.name in (
    'materialize.public.my_view'
    , 'materialize.public.the_top_consumer'
)
group by full_name
order by history_minutes;
```

The history holds 24 hours, so 1440 samples means "at least a day old" and
anything less is the object's age in minutes. Compare the candidates from
`EXPLAIN ANALYZE CLUSTER` against each other: a dataflow with 120 samples and
4 hours of CPU is working far harder than one with 1440 samples and 12 hours.

When every candidate reports 1440, the history cannot separate them. Divide
`total_elapsed` by the worker count from [compute gates](#compute-gates) to get
per-worker busy time, and compare that against the 24-hour window instead.

## Attribution walk

`mz_materialization_lag` shows lag for materialized views, indexes, and sinks. Start by looking up one object:

```sql
select
    db.name || '.' || s.name || '.' || o.name as full_name
    , ml.local_lag
    , ml.global_lag
    , ml.slowest_local_input_id
    , ml.slowest_global_input_id
from mz_internal.mz_materialization_lag ml
join mz_catalog.mz_objects o on o.id = ml.object_id
join mz_catalog.mz_schemas s on s.id = o.schema_id
join mz_catalog.mz_databases db on db.id = s.database_id
where db.name || '.' || s.name || '.' || o.name = 'materialize.public.my_view';
```

`local_lag` is the lag added by this object. `global_lag` is the lag from the root inputs. `slowest_global_input_id` is the root input. `slowest_local_input_id` is one hop toward that root; follow it repeatedly to trace the path.

Walk the local chain in one query. Materialize spells recursion `with mutually recursive` (the `mz-graph-queries` skill covers writing such queries in general):

```sql
with mutually recursive
    chain (object_id text, depth int) as (
        select o.id, 0
        from mz_catalog.mz_objects o
        join mz_catalog.mz_schemas s on s.id = o.schema_id
        join mz_catalog.mz_databases db on db.id = s.database_id
        where db.name || '.' || s.name || '.' || o.name = 'materialize.public.my_view'
        union
        select ml.slowest_local_input_id, ch.depth + 1
        from chain ch
        join mz_internal.mz_materialization_lag ml on ml.object_id = ch.object_id
        where ml.slowest_local_input_id is not null
          and ch.depth < 20
    )

select
    ch.depth
    , db.name || '.' || s.name || '.' || o.name as full_name
    , o.type
    , ml.local_lag
    , ml.global_lag
from (select object_id, min(depth) as depth from chain group by object_id) ch
join mz_catalog.mz_objects o on o.id = ch.object_id
left join mz_catalog.mz_schemas s on s.id = o.schema_id
left join mz_catalog.mz_databases db on db.id = s.database_id
left join mz_internal.mz_materialization_lag ml on ml.object_id = ch.object_id
order by ch.depth;
```

`mz_materialization_lag` covers materialized views, indexes, and sinks. A table
or a source has no row in it, which is why the type from
[current lag](#current-lag) decides whether this walk applies at all.

The chain ends at a source or table. Read `local_lag` down the chain and compare
the hops against each other: the hop carrying most of the object's `global_lag`
is where the delay enters, and hops near zero are passing it through. When no hop
stands out and `global_lag` is already present at the root, the lag is entering
at the root rather than inside the dependency graph.

## Ingestion

Check source status. The error text usually explains the problem:

```sql
select
    db.name || '.' || s.name || '.' || o.name as full_name
    , st.status
    , st.error
    , st.last_status_change_at::text as last_status_change_at
from mz_internal.mz_source_statuses st
join mz_catalog.mz_objects o on o.id = st.id
join mz_catalog.mz_schemas s on s.id = o.schema_id
join mz_catalog.mz_databases db on db.id = s.database_id
where st.status <> 'running'
order by st.last_status_change_at desc;
```

The timestamp column is `last_status_change_at`. Cast it to `::text` for a readable value.

Snapshot progress. A source still taking its initial snapshot is not behind, it
is not streaming yet, and the distinction changes the verdict:

```sql
select
    db.name || '.' || s.name || '.' || o.name as full_name
    , st.snapshot_committed
    , st.snapshot_records_known
    , st.snapshot_records_staged
    , st.offset_known
    , st.offset_committed
    , st.rehydration_latency
from mz_internal.mz_source_statistics st
join mz_catalog.mz_objects o on o.id = st.id
join mz_catalog.mz_schemas s on s.id = o.schema_id
join mz_catalog.mz_databases db on db.id = s.database_id
where db.name || '.' || s.name || '.' || o.name = 'raw.public.my_source';
```

`snapshot_committed` false means the initial snapshot is still running, and
`snapshot_records_staged` against `snapshot_records_known` is how far through it
is. Once it is true, `offset_committed` against `offset_known` is the streaming
backlog.

Write frontiers, oldest first. `write_frontier` is an `mz_timestamp`, so convert it through `text` to read it as a time. Filtering to user objects keeps system indexes, which sit at a frontier of zero, out of the result:

```sql
select
    db.name || '.' || s.name || '.' || o.name as full_name
    , o.type
    , f.write_frontier::text as write_frontier
    , to_timestamp(f.write_frontier::text::bigint / 1000)::text as frontier_time
from mz_internal.mz_frontiers f
join mz_catalog.mz_objects o on o.id = f.object_id
join mz_catalog.mz_schemas s on s.id = o.schema_id
join mz_catalog.mz_databases db on db.id = s.database_id
where f.write_frontier is not null
  and o.id like 'u%'
order by f.write_frontier asc
limit 20;
```

## Sink status

A lagging sink is diagnosed from its status, not from its plan: there is no
`EXPLAIN ANALYZE ... FOR SINK`.

```sql
select
    db.name || '.' || s.name || '.' || o.name as full_name
    , st.status
    , st.error
    , st.last_status_change_at::text as last_status_change_at
from mz_internal.mz_sink_statuses st
join mz_catalog.mz_objects o on o.id = st.id
join mz_catalog.mz_schemas s on s.id = o.schema_id
join mz_catalog.mz_databases db on db.id = s.database_id
where st.status <> 'running'
order by st.last_status_change_at desc;
```

A sink's own lag is inherited from what it reads, so run the
[attribution walk](#attribution-walk) on it: `mz_materialization_lag` does cover
sinks, and the culprit will be upstream.

## Compute gates

Hydration for the object under investigation. Filter to that object: the view also covers system introspection indexes.

```sql
select
    db.name || '.' || s.name || '.' || o.name as full_name
    , h.replica_id
    , r.name as replica
    , h.hydrated
from mz_internal.mz_hydration_statuses h
join mz_catalog.mz_objects o on o.id = h.object_id
join mz_catalog.mz_schemas s on s.id = o.schema_id
join mz_catalog.mz_databases db on db.id = s.database_id
left join mz_catalog.mz_cluster_replicas r on r.id = h.replica_id
where db.name || '.' || s.name || '.' || o.name = 'materialize.public.my_view';
```

`mz_compute_hydration_statuses` adds a `hydration_time` interval. This shows how long the current hydration has been running.

Check replica health to pick a replica or see if the cluster is saturated. `mz_cluster_replica_utilization` only has `replica_id`. Join it to get names:

```sql
select
    c.name as cluster
    , r.name as replica
    , u.cpu_percent
    , u.memory_percent
    , u.disk_percent
from mz_internal.mz_cluster_replica_utilization u
join mz_catalog.mz_cluster_replicas r on r.id = u.replica_id
join mz_catalog.mz_clusters c on c.id = r.cluster_id
order by u.cpu_percent desc nulls last;
```

These are evidence for the report. They say how much headroom the replica has,
not whether it is healthy. `cpu_percent` and `memory_percent` both near 100 means
the replica has no capacity left, whatever is consuming it. Between two replicas
of one cluster, the one to analyze is whichever is doing less work and has no
recent `offline` entry in `mz_cluster_replica_status_history`.

Check recent restarts. An `offline` status followed by `online` means a restart happened. Everything on that replica rehydrated after the restart:

```sql
select
    c.name as cluster
    , r.name as replica
    , h.status
    , h.reason
    , h.occurred_at::text as occurred_at
from mz_internal.mz_cluster_replica_status_history h
join mz_catalog.mz_cluster_replicas r on r.id = h.replica_id
join mz_catalog.mz_clusters c on c.id = r.cluster_id
where h.occurred_at > now() - interval '24 hours'
order by h.occurred_at desc;
```

Check worker counts to see the replica size. This is used to measure the skew ratio:

```sql
select
    c.name as cluster
    , r.name as replica
    , r.size
    , z.processes
    , z.workers
from mz_catalog.mz_cluster_replicas r
join mz_catalog.mz_clusters c on c.id = r.cluster_id
join mz_catalog.mz_cluster_replica_sizes z on z.size = r.size
order by c.name;
```
