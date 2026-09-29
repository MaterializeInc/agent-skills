<!-- mz-docs page: transform-data -->

# Overview

Learn how to efficiently transform data using Materialize SQL.

With Materialize, you use SQL to transform your fast-changing data into **live
data products**: the business objects (e.g., a customer, an order, a store) that
your applications, services, dashboards, and AI agents read.

## From SQL to live data products

You use [views](/fundamentals/concepts/views/) and [materialized
views](/fundamentals/concepts/views/#materialized-views) to define your business objects in
SQL. Materialize keeps the results of **indexed views** and **materialized
views** up to date as it ingests your data.

Structuring your transformations as views gives you:

- **Reuse:** define a query once, then reference it from multiple places.
- **Readability:** save complex logic under a clear, meaningful name.
- **Composability:** break complex logic into stacked view definitions, building
  richer business objects on top of simpler ones.
- **Efficiency:** project only the columns you need, filter out unnecessary
  rows, and convert values to more [compact data types](/sql/types/) where
  possible.

## SQL in Materialize

Materialize follows the SQL standard (SQL-92) implementation and aims for
compatibility with the PostgreSQL dialect. It **does not** aim for
compatibility with a specific version of PostgreSQL. This means that
Materialize might support syntax from any released PostgreSQL version, but does
not provide full coverage of the PostgreSQL dialect. The implementation and
performance of specific features (like [window functions](/transform-data/idiomatic-materialize-sql/appendix/window-function-to-materialize))
might also differ, because Materialize uses an entirely different database
engine based on [Timely and Differential Dataflow](/fundamentals/#incremental-updates).

If you need specific syntax or features that are not currently supported in
Materialize, please submit a [feature request](/support/#share-your-feedback).

## Explore this section

<div class="multilinkbox">
<div class="linkbox ">
  <div class="title">
    Write idiomatic SQL
  </div>
  <ul>
<li><a href="/transform-data/idiomatic-materialize-sql/" >Idiomatic Materialize SQL</a></li>
<li><a href="/transform-data/patterns/" >Common query patterns</a></li>
</ul>

</div>

<div class="linkbox ">
  <div class="title">
    Optimize and operate
  </div>
  <ul>
<li><a href="/transform-data/optimization/" >Query optimization</a></li>
<li><a href="/transform-data/updating-materialized-views/" >Updating materialized views</a></li>
<li><a href="/fundamentals/concepts/indexes/#best-practices" >Indexes: best practices</a></li>
</ul>

</div>

<div class="linkbox ">
  <div class="title">
    Troubleshoot
  </div>
  <ul>
<li><a href="/serve-results/troubleshooting/" >Troubleshooting</a></li>
<li><a href="/transform-data/freshness-troubleshooting/" >Freshness troubleshooting</a></li>
<li><a href="/transform-data/dataflow-troubleshooting/" >Dataflow troubleshooting</a></li>
<li><a href="/transform-data/faq/" >FAQ: Indexes</a></li>
</ul>

</div>

</div>

<!-- mz-docs page: transform-data/dataflow-troubleshooting -->

# Dataflow troubleshooting
How to troubleshoot common dataflow-level scenarios where Materialize is not working as expected.
If you're unable to troubleshoot your issue using the [`Ingest data`](/ingest-data/troubleshooting/)
and [`Transform data`](/serve-results/troubleshooting/) troubleshooting guides,
going a level deeper in the stack might be needed. This guide collects common
questions around dataflows to help you troubleshoot your queries.

<!-- Copied over from the old manage/troubleshooting guide -->
## Dataflows: mental model and basic terminology

When you create a materialized view, an index, or issue an ad-hoc query,
Materialize creates a so-called dataflow. A dataflow consists of instructions
on how to respond to data input and to changes to that data. Once executed, the
dataflow computes the result of the SQL query, waits for updates from the
sources, and then incrementally updates the query results when new data
arrives.

Materialize dataflows act on collections of data. To provide fast access to the
changes to individual records, the records can be stored in an indexed
representation called [arrangements](/fundamentals/concepts/arrangements/#arrangements).
Arrangements can be manually created by users on views by creating an index on
the view. But they are also used internally in dataflows, for instance, when
joining relations.

### Translating SQL to dataflows

To make these concepts a bit more tangible, let's look at the example from the
[getting started guide](/get-started/quickstart/).

```mzsql
CREATE SOURCE auction_house
  FROM LOAD GENERATOR AUCTION
  (TICK INTERVAL '1s', AS OF 100000)
  FOR ALL TABLES;

CREATE MATERIALIZED VIEW num_bids AS
  SELECT auctions.item, count(bids.id) AS number_of_bids
  FROM bids
  JOIN auctions ON bids.auction_id = auctions.id
  WHERE bids.bid_time < auctions.end_time
  GROUP BY auctions.item;

CREATE INDEX num_bids_idx ON num_bids (item);
```

The query of the materialized view joins the relations `bids` and `auctions`,
groups by `auctions.item` and determines the number of bids per auction. To
understand how this SQL query is translated to a dataflow, we can use
[`EXPLAIN PLAN`](/sql/explain-plan/) to display the
plan used to evaluate the join.

```mzsql
EXPLAIN MATERIALIZED VIEW num_bids;
```
```
                               Optimized Plan
-----------------------------------------------------------------------------
 materialize.public.num_bids:                                               +
   Reduce group_by=[#0{item}] aggregates=[count(*)] // { arity: 2 }         +
     Project (#3) // { arity: 1 }                                           +
       Filter (#1{bid_time} < #4{end_time}) // { arity: 5 }                 +
         Join on=(#0{auction_id} = #2{id}) type=differential // { arity: 5 }+
           ArrangeBy keys=[[#0{auction_id}]] // { arity: 2 }                +
             Project (#2, #4) // { arity: 2 }                               +
               ReadStorage materialize.public.bids // { arity: 5 }          +
           ArrangeBy keys=[[#0{id}]] // { arity: 3 }                        +
             Project (#0{id}, #2{end_time}, #3) // { arity: 3 }             +
               ReadStorage materialize.public.auctions // { arity: 4 }      +
                                                                            +
 Source materialize.public.auctions                                         +
 Source materialize.public.bids                                             +
                                                                            +
 Target cluster: quickstart                                                 +

(1 row)
```

The plan describes the specific operators that are used to evaluate the query.
Some of these operators resemble relational algebra or map reduce style
operators (`Filter`, `Join`, `Project`). Others are specific to Materialize
(`ArrangeBy`, `ReadStorage`).

In general, a high level understanding of what these operators do is sufficient
for effective debugging: `Filter` filters records, `Join` joins records from
two or more inputs, `Map` applies a function to transform records, etc. You can
find more details on these operators in the [`EXPLAIN PLAN` documentation](/sql/explain-plan/#reference-plan-operators).
But it's not important to have a deep understanding of all these operators for
effective debugging.

Behind the scenes, the operator graph is turned into a dataflow. The dataflow is
organized in a hierarchical structure that contains operators and _regions_,
which define a hierarchy on the operators. In our example, the dataflow
contains an `InputRegion`, a `BuildRegion`, and a region for the sink.

![Regions and operator visualization](/images/regions-and-operators-hierarchy.png)

Again, it's not too important for our purposes to understand what these regions
do and how they are used to structure the operator graph. For our purposes it's
just important to know than that they define a hierarchy on the operators.

## The system catalog and introspection relations

Materialize collects a lot of useful information about the dataflows and
operators in the system catalog in [introspection relations](/sql/system-catalog/mz_introspection).
The introspection relations are useful to troubleshoot and understand what is
happening under the hood when Materialize is not behaving as expected. However,
it is important to understand that most of the statistics we need for
troubleshooting purposes are specific to the cluster that is running the
queries we want to debug.

> **Warning:** Indexes and dataflows are local to a cluster, so their introspection information
> will vary across clusters depending on the active cluster and replica. As a
> consequence, you should expect the results of the queries below to vary
> depending on the values set for the `cluster` and `cluster_replica`
> [configuration parameters](/sql/set/#other-configuration-parameters).

<!--
[//]: # "TODO(joacoc) We should share ways for the user to diagnose and troubleshoot if and how fast a source is consuming."
``` -->

## Where is Materialize spending compute time?

Materialize spends time in various dataflow operators. Dataflows are created to
maintain materialized views or indexes. In addition, temporary dataflow will be
created for ad-hoc queries that don't just make a lookup to an existing index.

If Materialize is taking more time to update results than you expect, you can
identify which operators take the largest total amount of time.

### Identifying expensive dataflows

To understand which dataflow is taking the most time we can query the
`mz_scheduling_elapsed` relation. The `elapsed_time` metric shows the absolute
time the dataflows was busy since the system started and the dataflow was
created.

```mzsql
-- Extract raw elapsed time information for dataflows
SELECT
    mdo.id,
    mdo.name,
    mse.elapsed_ns / 1000 * '1 MICROSECONDS'::interval AS elapsed_time
FROM mz_introspection.mz_scheduling_elapsed AS mse,
    mz_introspection.mz_dataflow_operators AS mdo,
    mz_introspection.mz_dataflow_addresses AS mda
WHERE mse.id = mdo.id AND mdo.id = mda.id AND list_length(address) = 1
ORDER BY elapsed_ns DESC;
```
```
 id  |                  name                  |  elapsed_time
-----+----------------------------------------+-----------------
 354 | Dataflow: materialize.qck.num_bids     | 02:05:25.756836
 578 | Dataflow: materialize.qck.num_bids_idx | 00:15:04.838741
 (2 rows)
```

These results show that Materialize spends the most time keeping the
materialized view `num_bids` up to date, followed by the work on the index
`avg_bids_idx`.

### Identifying expensive operators in a dataflow

The previous query is a good starting point to get an overview of the work
happening in the cluster because it only returns dataflows.

The `mz_scheduling_elapsed` relation also contains details for regions and
operators. Removing the condition `list_length(address) = 1` will include the
regions and operators in the result. But be aware that every row shows
aggregated times for all the elements it contains. The `elapsed_time` reported
for the dataflows above also includes the elapsed time for all the regions and
operators they contain.

But because the parent-child relationship is not always obvious, the results
containing a mixture of dataflows, regions, and operators can be a bit hard to
interpret. The following query therefore only returns operators from the
`mz_scheduling_elapsed` relation. You can further drill down by adding a filter
condition that matches the name of a specific dataflow.

```mzsql
SELECT
    mdod.id,
    mdod.name,
    mdod.dataflow_name,
    mse.elapsed_ns / 1000 * '1 MICROSECONDS'::interval AS elapsed_time
FROM mz_introspection.mz_scheduling_elapsed AS mse,
    mz_introspection.mz_dataflow_addresses AS mda,
    mz_introspection.mz_dataflow_operator_dataflows AS mdod
WHERE
    mse.id = mdod.id AND mdod.id = mda.id
    -- exclude regions and just return operators
    AND mda.address NOT IN (
        SELECT DISTINCT address[:list_length(address) - 1]
        FROM mz_introspection.mz_dataflow_addresses
    )
ORDER BY elapsed_ns DESC;
```
```
 id  |                      name                       |             dataflow_name              |  elapsed_time
-----+-------------------------------------------------+----------------------------------------+-----------------
 431 | ArrangeBy[[Column(0)]]                          | Dataflow: materialize.qck.num_bids     | 01:12:58.964875
 442 | ArrangeBy[[Column(0)]]                          | Dataflow: materialize.qck.num_bids     | 00:06:06.080178
 528 | shard_source_fetch(u517)                        | Dataflow: materialize.qck.num_bids     | 00:04:04.076344
 594 | shard_source_fetch(u517)                        | Dataflow: materialize.qck.num_bids_idx | 00:03:34.803234
 590 | persist_source_backpressure(backpressure(u517)) | Dataflow: materialize.qck.num_bids_idx | 00:03:33.626036
 400 | persist_source_backpressure(backpressure(u510)) | Dataflow: materialize.qck.num_bids     | 00:03:03.575832
...
```

From the results of this query we can see that most of the elapsed time of the
dataflow is caused by the time it takes to maintain the updates in one of the
arrangements of the dataflow of the materialized view.

### Debugging expensive dataflows and operators

A large class of problems can be identified by using [`elapsed_time`](#identifying-expensive-operators-in-a-dataflow)
to estimate the most expensive dataflows and operators. However, `elapsed_time`
contains all work since the operator or dataflow was first created. Sometimes,
a lot of work happens initially when the operator is created, but later on it
takes only little continuous effort. If you want to see what operator is taking
the most time **right now**, the `elapsed_time` metric is not enough.

The relation `mz_compute_operator_durations_histogram` also tracks the time
operators are busy, but instead of aggregating `elapsed_time` since an operator
got created, it tracks how long each operator was scheduled at a time in a
histogram. This information can show you two things: operators that block
progress for others and operators that are currently doing work.

If there is a very expensive operator that blocks progress for all other
operators, it will become visible in the histogram. The offending operator will
be scheduled in much longer intervals compared to other operators, which
reflects in the histogram as larger time buckets.

```mzsql
-- Extract raw scheduling histogram information for operators
WITH histograms AS (
    SELECT
        mdod.id,
        mdod.name,
        mdod.dataflow_name,
        mcodh.count,
        mcodh.duration_ns / 1000 * '1 MICROSECONDS'::interval AS duration
    FROM mz_introspection.mz_compute_operator_durations_histogram AS mcodh,
        mz_introspection.mz_dataflow_addresses AS mda,
        mz_introspection.mz_dataflow_operator_dataflows AS mdod
    WHERE
        mcodh.id = mdod.id
        AND mdod.id = mda.id
        -- exclude regions and just return operators
        AND mda.address NOT IN (
            SELECT DISTINCT address[:list_length(address) - 1]
            FROM mz_introspection.mz_dataflow_addresses
        )

)

SELECT *
FROM histograms
WHERE duration > '100 millisecond'::interval
ORDER BY duration DESC;
```
```
 id  |                 name                 |             dataflow_name              | count |    duration
-----+--------------------------------------+----------------------------------------+-------+-----------------
 408 | persist_source::decode_and_mfp(u510) | Dataflow: materialize.qck.num_bids     |     1 | 00:00:01.073741
 408 | persist_source::decode_and_mfp(u510) | Dataflow: materialize.qck.num_bids     |     1 | 00:00:00.53687
 374 | persist_source::decode_and_mfp(u509) | Dataflow: materialize.qck.num_bids     |     1 | 00:00:00.268435
 408 | persist_source::decode_and_mfp(u510) | Dataflow: materialize.qck.num_bids     |     2 | 00:00:00.268435
 429 | FormArrangementKey                   | Dataflow: materialize.qck.num_bids     |     2 | 00:00:00.134217
 (5 rows)
```

Note that this relation contains a lot of information. The query therefore
filters all durations below `100 millisecond`. In this example, the result of
the query shows that the longest an operator got scheduled is just over one
second. So it's unlikely that Materialize is unresponsive because of a single
operator blocking progress for others.

The reported duration is still reporting aggregated values since the operator
has been created. To get a feeling for which operators are currently doing
work, you can subscribe to the changes of the relation.

```mzsql
-- Observe changes to the raw scheduling histogram information
COPY(SUBSCRIBE(
    WITH histograms AS (
        SELECT
            mdod.id,
            mdod.name,
            mdod.dataflow_name,
            mcodh.count,
            mcodh.duration_ns / 1000 * '1 MICROSECONDS'::interval AS duration
        FROM mz_introspection.mz_compute_operator_durations_histogram AS mcodh,
            mz_introspection.mz_dataflow_addresses AS mda,
            mz_introspection.mz_dataflow_operator_dataflows AS mdod
        WHERE
            mcodh.id = mdod.id
            AND mdod.id = mda.id
            -- exclude regions and just return operators
            AND mda.address NOT IN (
                SELECT DISTINCT address[:list_length(address) - 1]
                FROM mz_introspection.mz_dataflow_addresses
            )

    )

    SELECT *
    FROM histograms
    WHERE duration > '100 millisecond'::interval
) WITH (SNAPSHOT = false, PROGRESS)) TO STDOUT;
```
```
1691667343000	t	\N	\N	\N	\N	\N	\N
1691667344000	t	\N	\N	\N	\N	\N	\N
1691667344000	f	-1	431	ArrangeBy[[Column(0)]]	Dataflow: materialize.qck.num_bids	7673	00:00:00.104800
1691667344000	f	1	431	ArrangeBy[[Column(0)]]	Dataflow: materialize.qck.num_bids	7674	00:00:00.104800
1691667345000	t	\N	\N	\N	\N	\N	\N
...
```

In this way you can see that currently the only operator that is doing more than
100 milliseconds worth of work is the `ArrangeBy` operator from the
materialized view `num_bids`.

## Why is Materialize using so much memory?

[Arrangements](/overview/arrangements) take up most of Materialize's memory use.
Arrangements maintain indexes for data as it changes. These queries extract the
numbers of records and the size of the arrangements. The reported records may
exceed the number of logical records; the report reflects the uncompacted
state.

```mzsql
-- Extract dataflow records and sizes
SELECT
    s.id,
    s.name,
    s.records,
    pg_size_pretty(s.size) AS size
FROM mz_introspection.mz_dataflow_arrangement_sizes AS s
ORDER BY s.size DESC;
```
```
  id   |                   name                    | records  |    size
-------+-------------------------------------------+----------+------------
 49030 | Dataflow: materialize.public.num_bids     | 10000135 | 165 MB
 49031 | Dataflow: materialize.public.num_bids_idx |       33 | 1661 bytes
```

If you need to drill down into individual operators, you can query
`mz_arrangement_sizes` instead.

```mzsql
-- Extract operator records and sizes
SELECT
    mdod.id,
    mdod.name,
    mdod.dataflow_name,
    mas.records,
    pg_size_pretty(mas.size) AS size
FROM mz_introspection.mz_arrangement_sizes AS mas,
    mz_introspection.mz_dataflow_operator_dataflows AS mdod
WHERE mas.operator_id = mdod.id
ORDER BY mas.size DESC;
```
```
    id    |              name               |               dataflow_name               | records |    size
----------+---------------------------------+-------------------------------------------+---------+------------
 16318351 | ArrangeBy[[Column(0)]]          | Dataflow: materialize.public.num_bids     | 8462247 | 110 MB
 16318370 | ArrangeBy[[Column(0)]]          | Dataflow: materialize.public.num_bids     | 1537865 | 55 MB
 16318418 | ArrangeAccumulable [val: empty] | Dataflow: materialize.public.num_bids     |       5 | 1397 bytes
 16318550 | ArrangeBy[[Column(0)]]          | Dataflow: materialize.public.num_bids_idx |      13 | 1277 bytes
 16318422 | ReduceAccumulable               | Dataflow: materialize.public.num_bids     |       5 | 1073 bytes
 16318426 | AccumulableErrorCheck           | Dataflow: materialize.public.num_bids     |       0 | 256 bytes
 16318559 | ArrangeBy[[Column(0)]]-errors   | Dataflow: materialize.public.num_bids_idx |       0 | 0 bytes
```

In the [Materialize Console](https://console.materialize.com),

- The [**Cluster Overview**](/developer-tools/console/clusters/) page displays the cluster
  resource utilization for a selected cluster as well as the resource intensive
  objects in the cluster.

- The [**Environment Overview**](/developer-tools/console/monitoring/) page displays the
  resource utilization for all your clusters. You can select a specific cluster
  to view its **Overview** page.

## Is work distributed equally across workers?

Work is distributed across workers by the hash of their keys. Thus, work can
become skewed if situations arise where Materialize needs to use arrangements
with very few or no keys. Example situations include:

* Views that maintain order by/limit/offset
* Cross joins
* Joins where the join columns have very few unique values

Additionally, the operators that implement data sources may demonstrate skew, as
they (currently) have a granularity determined by the source itself. For
example, Kafka topic ingestion work can become skewed if most of the data is in
only one out of multiple partitions.

```mzsql
-- Get operators where one worker has spent more than 2 times the average
-- amount of time spent. The number 2 can be changed according to the threshold
-- for the amount of skew deemed problematic.
SELECT
    mse.id,
    dod.name,
    mse.worker_id,
    elapsed_ns,
    avg_ns,
    elapsed_ns/avg_ns AS ratio
FROM
    mz_introspection.mz_scheduling_elapsed_per_worker mse,
    (
        SELECT
            id,
            avg(elapsed_ns) AS avg_ns
        FROM
            mz_introspection.mz_scheduling_elapsed_per_worker
        GROUP BY
            id
    ) aebi,
    mz_introspection.mz_dataflow_operator_dataflows dod
WHERE
    mse.id = aebi.id AND
    mse.elapsed_ns > 2 * aebi.avg_ns AND
    mse.id = dod.id
ORDER BY ratio DESC;
```

## I found a problematic operator. Where did it come from?

Look up the operator in `mz_dataflow_addresses`. If an operator has value `x` at
position `n`, then it is part of the `x` subregion of the region defined by
positions `0..n-1`. The example SQL query and result below shows an operator
whose `id` is 515 that belongs to "subregion 5 of region 1 of dataflow 21".

```mzsql
SELECT * FROM mz_introspection.mz_dataflow_addresses WHERE id=515;
```
```
 id  | worker_id | address
-----+-----------+----------
 515 |      0    | {21,1,5}
```

Usually, it is only important to know the name of the dataflow a problematic
operator comes from. Once the name is known, the dataflow can be correlated to
an index or materialized view in Materialize.

Each dataflow has an operator representing the entire dataflow. The address of
said operator has only a single entry. For the example operator 515 above, you
can find the name of the dataflow if you can find the name of the operator
whose address is just "dataflow 21."

```mzsql
-- get id and name of the operator representing the entirety of the dataflow
-- that a problematic operator comes from
SELECT
    mdo.id AS id,
    mdo.name AS name
FROM
    mz_introspection.mz_dataflow_addresses mda,
    -- source of operator names
    mz_introspection.mz_dataflow_operators mdo,
    -- view containing operators representing entire dataflows
    (SELECT
      mda.id AS dataflow_operator,
      mda.address[1] AS dataflow_address
    FROM
      mz_introspection.mz_dataflow_addresses mda
    WHERE
      list_length(mda.address) = 1) dataflows
WHERE
    mda.id = 515
    AND mda.address[1] = dataflows.dataflow_address
    AND mdo.id = dataflows.dataflow_operator;
```

## I dropped an index, why haven't my plans and dataflows changed?

It's likely that your index has **downstream dependencies**. If an index has
dependent objects downstream, its underlying dataflow will continue to be
maintained and take up resources until all dependent object are dropped or
altered, or Materialize is restarted.

[//]: # "TODO(chaas) Add reference to the console once it's available."

To check if there are residual dataflows on a specific cluster, run the
following query:

```mzsql
SET CLUSTER TO <cluster_name>;

SELECT ce.export_id AS dropped_index_id,
       s.name AS dropped_index_name,
       s.id AS dataflow_id
FROM mz_internal.mz_dataflow_arrangement_sizes s
JOIN mz_internal.mz_compute_exports ce ON ce.dataflow_id = s.id
LEFT JOIN mz_catalog.mz_objects o ON o.id = ce.export_id
WHERE o.id IS NULL;
```

You can then use the `dropped_index_id` object identifier to list the downstream
dependencies of the residual dataflow, using:

```mzsql
SELECT do.id AS dependent_object_id,
       do.name AS dependent_object_name,
       db.name AS dependent_object_database,
       s.name AS dependent_object_schema
FROM mz_internal.mz_compute_dependencies cd
LEFT JOIN mz_catalog.mz_objects do ON cd.object_id = do.id
LEFT JOIN mz_catalog.mz_schemas s ON do.schema_id = s.id
LEFT JOIN mz_catalog.mz_databases db ON s.database_id = db.id
WHERE cd.dependency_id = <dropped_index_id>;
```

To force a re-plan of the downstream objects that doesn't consider the dropped
index, you have to drop and recreate all downstream dependencies.

> **Warning:** Forcing a re-plan using the approach above **will trigger hydration**,
> which incurs downtime while the objects are recreated and backfilled with
> pre-existing data. We recommend doing a [blue/green deployment](/developer-tools/dbt/blue-green-deployments/)
> to handle these changes in production environments.


<!-- mz-docs page: transform-data/dictionary-compression -->

# Dictionary compression
Reduce arrangement memory for columns that hold a small set of repeated values.
> **Public Preview:** This feature is in public preview.

Starting in v26.38, dictionary compression is available for managed clusters.
Dictionary compression reduces the memory that
[arrangements](/fundamentals/concepts/arrangements/#arrangements) use when a column holds
the same values repeatedly. Instead of storing a repeated column value each time
it appears, Materialize stores that value once and has each row reference it. This can reduce steady state memory requirements after hydration has completed.

Dictionary compression is specified per cluster replica, and is set to off by default. You opt in using the `EXPERIMENTAL ARRANGEMENT COMPRESSION` option, while creating or altering a cluster or cluster replica.

Within a column, the values that repeat most often are the ones Materialize
stores once and references. Everything else is stored as-is, exactly as it would
be without compression. Materialize applies compression per column and decides
which columns to compress, so a wide row can have one column compressed and the
rest untouched.

## Enable dictionary compression

Set the `EXPERIMENTAL ARRANGEMENT COMPRESSION` option on each managed cluster
whose arrangements you want compressed.

The option is configured on the cluster, but the arrangements it applies to live
in the cluster's replicas, in each replica's memory. A replica picks up the
configured value when it is created and holds it for its lifetime.

> **Warning:** A replica's compression setting is fixed when the replica is created, so
> changing `EXPERIMENTAL ARRANGEMENT COMPRESSION` never changes an existing
> replica's arrangements. Materialize instead creates a new set of replicas
> carrying the new setting. The existing replicas keep serving until the new ones
> have hydrated, then Materialize retires them. As a result, the cluster
> temporarily uses roughly twice its usual memory until the switch completes,
> regardless of whether you enable or disable dictionary compression.
> Nothing else is needed to apply the setting. Plan for the switch the same way
> you would plan for resizing a cluster. Because hydration is slower with
> compression enabled, the switch takes longer when turning compression on than
> when turning it off.

### Set the option on a cluster

You can set the option when you create a cluster:

```mzsql
CREATE CLUSTER my_cluster (
    SIZE = '100cc',
    EXPERIMENTAL ARRANGEMENT COMPRESSION = true
);
```

Or change it on an existing cluster:

```mzsql
ALTER CLUSTER my_cluster SET (EXPERIMENTAL ARRANGEMENT COMPRESSION = true);
```

To go back to the default:

```mzsql
ALTER CLUSTER my_cluster RESET (EXPERIMENTAL ARRANGEMENT COMPRESSION);
```

[`SHOW CREATE CLUSTER`] reports the configured value.

## The tradeoff

Dictionary compression trades CPU for memory, and it does **not** reduce memory
on every workload. Use this section to judge whether it suits your workload, and
[contact our team](/support/) if you have questions.

> **Note:** A single arrangement usually holds both columns that compress well and columns
> that do not. Only the columns that compress save memory, and every column still
> pays the CPU cost. Materialize decides which columns get compressed, and you
> cannot select them yourself. You turn compression on per cluster, and the
> optimizer chooses which intermediate arrangements a dataflow builds.

### When it helps

- Columns that hold a small set of often-repeated, longer values. Typical
  examples are status strings, enum-like labels, country codes, and tenant IDs.
  Most or all of the memory savings come from columns like these. See [How
  distinct values affect the benefit](#how-distinct-values-affect-the-benefit)
  for how the benefit changes as that set grows.
- Large arrangements. Compression saves more memory when repeated values occur
  across more rows, so larger arrangements generally offer more opportunity for
  savings.

Only data held in an arrangement is affected. That means [indexes] and the
arrangements that a dataflow builds internally for joins and aggregations
(`GROUP BY`, `DISTINCT`). Data that is not arranged is untouched. A materialized
view's stored result is not an arrangement, but the dataflow that maintains it
builds these internal arrangements for any joins and aggregations it computes.

### When it does not help

- **High-cardinality or near-unique columns.** Unique values are not worth
  storing in a dictionary, so columns dominated by them see little or no memory
  savings. Materialize does not detect a high-cardinality column and skip it up
  front. It inspects every column of every row regardless, so a near-unique
  column pays the full CPU cost for little or no memory benefit. Unique
  identifiers, timestamps, and free-form text are typical examples.
- **Columns of short values.** Booleans, `NULL`s, and small integers are already
  stored compactly enough that a dictionary reference cannot beat storing the
  value itself. They are never compressed.
- **Small arrangements.** An arrangement built from scratch does not install a
  dictionary until it has seen on the order of 65,000 rows. Small arrangements
  are effectively unaffected.

### The CPU cost

The cost falls mainly on the write path. As updates arrive, Materialize keeps
approximate counts of which values repeat most in each column and maintains the
dictionary. The most
visible symptom is slower arrangement hydration. A replica in a cluster with
compression enabled takes longer to build its arrangements after it is created,
restarted, or resized.

Reads pay a smaller but ongoing cost. Resolving a compressed value requires an
extra indirection, and comparing compressed rows cannot use the fast path that
uncompressed rows use.

## How distinct values affect the benefit

The memory benefit is largest when a column repeats a small set of values across
many rows. It tapers off as the number of distinct values in a column grows past
roughly 64, and with enough distinct values the bookkeeping becomes overhead that
buys no memory saving at all.

This is not a limit. Nothing breaks when a column holds more distinct values
than that. Values that are not worth storing in a dictionary, including values
that appear only once, are stored as-is. The result is less memory saved, and
nothing else changes.

## Observe the effect

There is no metric or system catalog relation specific to dictionary
compression. The effect shows up in the existing arrangement-size introspection:

```mzsql
SELECT name, records, size
FROM mz_introspection.mz_dataflow_arrangement_sizes
ORDER BY size DESC;
```

See [`mz_introspection.mz_arrangement_sizes`] for per-operator numbers and
[`mz_introspection.mz_dataflow_arrangement_sizes`] for per-dataflow numbers. The
reported size includes the dictionary's own overhead, so on a workload that does
not compress well you may see the cost of the machinery rather than a saving.

To judge whether compression helped, compare arrangement sizes for the same
objects with the option on and off. For example, run the same workload on a
second cluster with the option set differently. Because changing the option
re-hydrates the cluster, wait until hydration has completed before you measure.

## Related pages

- [Arrangements]
- [Query optimization](/transform-data/optimization/)
- [Dataflow troubleshooting](/transform-data/dataflow-troubleshooting/)
- [`CREATE CLUSTER`](/sql/create-cluster/)
- [`ALTER CLUSTER`](/sql/alter-cluster/)
- [`SHOW CREATE CLUSTER`]

[Arrangements]: /fundamentals/concepts/arrangements/
[indexes]: /fundamentals/concepts/indexes/
[`SHOW CREATE CLUSTER`]: /sql/show-create-cluster/
[`mz_introspection.mz_arrangement_sizes`]: /sql/system-catalog/mz_introspection/#mz_arrangement_sizes
[`mz_introspection.mz_dataflow_arrangement_sizes`]: /sql/system-catalog/mz_introspection/#mz_dataflow_arrangement_sizes

<!-- mz-docs page: transform-data/faq -->

# FAQ: Indexes
Frequently asked questions about indexes.
## Are indexes in Materialize optimized for `ORDER BY`?

No.

The index data is distributed across the cluster's
workers by a hash of the key, which spreads the maintenance and lookup work
across the cluster.

Within each worker, index keys are ordered by their internal representation
(the encoded key's length, then its bytes), not by the data types' natural
ordering.

As such, Materialize indexes are not optimized for ordered access, including
`ORDER BY` clauses.

## Are indexes in Materialize optimized for range queries?

No.

The index data is distributed across the cluster's
workers by a hash of the key, which spreads the maintenance and lookup work
across the cluster.

Within each worker, index keys are ordered by their internal representation
(the encoded key's length, then its bytes), not by the data types' natural
ordering.

As such, Materialize indexes are not optimized for ordered access, including
range queries.

## Are indexes in Materialize optimized for `GROUP BY` aggregations?

No. An index on the grouping key does not reduce the work of computing the aggregation: Materialize reads the full index and maintains the aggregation separately.

<!-- mz-docs page: transform-data/freshness-troubleshooting -->

# Freshness troubleshooting
How to diagnose and resolve freshness problems in Materialize.
[Freshness](/fundamentals/concepts/reaction-time/#freshness) measures the time from when a
change occurs in an upstream system to when it becomes visible in the results of
a query. This guide can help diagnose why freshness is degraded for an object as
well as measure freshness across your deployment.

To track freshness for an object over time before a problem occurs, see [Monitor
freshness](/transform-data/monitor-freshness/).

## Key concepts

| Concept | Description |
| ------- | ----------- |
| **Write frontier** |  The next timestamp at which data for an object can change; i.e., for an object, all its data changes with timestamp less than the write frontier has been processed. Materialize measures freshness using **write frontiers**. Each object (source, table, materialized view, index, sink) has its own write frontier. |
| **Wallclock lag** | The difference between wall-clock time and an object's write frontier. |
| **Materialization lag** | The difference between an object's write frontier and the write frontier of its inputs. Materialization lag can be considered in two parts:  <ul><li>**local_lag**: The lag between the object and its direct inputs. It represents the portion of lag introduced by the object itself.</li><li>**global_lag**: The lag between the object and its root inputs (sources and tables). It represents the total accumulated lag across the dataflow.</li></ul>|

## Common causes

Common causes of lag include:

- [**Materialization lag**](#check-materialization-lag): The object itself
  (and/or a specific input in its dependency graph) introduces a lag.
- [**Cluster health**](#check-cluster-health): The cluster is overloaded, out of
  memory, or missing compute. All objects on the cluster are affected.
- [**Source ingestion**](#check-source-ingestion): The source is behind. All
  downstream objects for the source are affected.

## Check materialization lag

### Step 1. Find lagging object(s)

Query the top 20 user objects by lag:

```mzsql
SELECT
  o.id AS object_id,
  o.name,
  o.type,
  wl.lag,
  c.name as cluster_name,
  c.id as cluster_id
FROM mz_internal.mz_wallclock_global_lag wl
JOIN mz_catalog.mz_objects o ON wl.object_id = o.id
JOIN mz_catalog.mz_clusters c ON o.cluster_id = c.id
WHERE o.id LIKE 'u%'
ORDER BY wl.lag DESC NULLS LAST
LIMIT 20;
```

- Lag of a few seconds typically indicates a healthy system.
- Lag on the order of minutes or hours typically indicates a problem.[^1]

To inspect an object's lag, see [Step
2a](#step-2a-identify-materialization-lag-contributors).

[^1]: Some objects may report high lag without representing a real issue (e.g.,
    [intentionally paused clusters](#check-for-no-compute)). Exclude from the
    query as appropriate.

### Step 2a. Identify materialization lag contributors.

`mz_internal.mz_materialization_lag` breaks down lag for each materialization
(index, materialized view, sink) into two components:

* **`local_lag`**: the lag introduced by the object itself; i.e., how far behind
  the object is compared to its direct inputs.
* **`global_lag`**: the object's lag relative to its root inputs (sources and
  tables).

Use the following query to determine how much lag is introduced by the object
itself versus inherited from upstream dependencies. Replace `<object_id>` with
your object's id:

```mzsql {hl_lines="12"}
SELECT
    o.id AS object_id,
    o.name,
    ml.local_lag,                                  -- lag introduced by the object itself
    ml.global_lag - ml.local_lag AS inherited_lag, -- lag inherited from dependencies
    ml.global_lag,                                 -- total lag
    ml.slowest_local_input_id
FROM mz_internal.mz_materialization_lag ml
JOIN mz_catalog.mz_objects o ON ml.object_id = o.id
WHERE o.id = '<object_id>'
ORDER BY ml.global_lag DESC;
```

- To investigate a high `local_lag`, use [Dataflow
  troubleshooting](/transform-data/dataflow-troubleshooting/) to identify
  expensive operators for the object itself. If possible, optimize the query,
  resize the cluster, or move the object to a cluster with more resources.

- To investigate a high `inherited_lag`,

  - For indexes and materialized views, repeat Step 2a for
    `ml.slowest_local_input_id`, or use [Check dependency
    lags](#step-2b-check-dependency-lags) to see all upstream contributions to
    the lag.

  - For sinks, repeat Step 2a for `ml.slowest_local_input_id` to investigate the
    upstream object. Note that sinks can also introduce lag due to batching and
    commit intervals. Additionally, [swapping a
    sink](#check-for-ddl-or-deploy-activity) to point to a new upstream
    materialized view triggers reprocessing, which can temporarily increase lag.

### Step 2b. Check dependency lags

To find the lag contributions from upstream dependencies of a materialized view
or an index (replace `<object_id>` with the id of your materialized view/index):

```mzsql{hl_lines="3 30"}
WITH MUTUALLY RECURSIVE
    depends_on(probe text, prev text, next text) AS (
        SELECT '<object_id>', '<object_id>', '<object_id>' -- update
        UNION
        SELECT d.probe, dep.dependency_id, dep.object_id
        FROM mz_internal.mz_compute_dependencies dep
        JOIN depends_on d ON d.prev = dep.object_id
    )
SELECT
    o_probe.name AS object_name,
    o_prev.name AS from_name,
    o_prev.id   AS from_id,
    o_prev.type AS from_type,
    o_next.name AS to_name,
    o_next.type AS to_type,
    fp.write_frontier::text::numeric
        - fn.write_frontier::text::numeric AS lag_ms
FROM depends_on d
JOIN mz_internal.mz_frontiers fp ON d.prev = fp.object_id
JOIN mz_internal.mz_frontiers fn ON d.next = fn.object_id
JOIN mz_catalog.mz_objects o_probe ON d.probe = o_probe.id
JOIN mz_catalog.mz_objects o_prev ON d.prev = o_prev.id
JOIN mz_catalog.mz_objects o_next ON d.next = o_next.id
WHERE d.prev != d.next
  AND fp.write_frontier IS NOT NULL
  AND fn.write_frontier IS NOT NULL
  AND fn.write_frontier::text::numeric <=
      (SELECT write_frontier::text::numeric
         FROM mz_internal.mz_frontiers
        WHERE object_id = '<object_id>')                   -- update
ORDER BY lag_ms DESC;
```

Using the returned `from_id`, you can iterate Step 2a and Step 2b as needed. To
identify expensive operators for the object, use [Dataflow
troubleshooting](/transform-data/dataflow-troubleshooting/). If possible,
optimize the query, resize the cluster, or move the object to a cluster with
more resources.

## Check cluster health

A cluster can become overloaded if:

- It is undersized for its workload; or

- It contains an inefficient or overly expensive object that effectively makes
  the cluster undersized.

When a cluster is overloaded, this may manifest as high CPU utilization, high
memory utilization forcing data to disk, or Out of Memory (OOM) crash loops.

### Check the CPU or memory pressure

**Specific cluster:**

You can run the following query to check a cluster's resource utilization,
replacing `<cluster_name>` with the name of cluster:

```mzsql
SELECT
    c.name AS cluster_name,
    c.id as cluster_id,
    r.name AS replica_name,
    u.cpu_percent,
    u.memory_percent
FROM mz_internal.mz_cluster_replica_utilization u
JOIN mz_catalog.mz_cluster_replicas r ON u.replica_id = r.id
JOIN mz_catalog.mz_clusters c ON r.cluster_id = c.id
WHERE c.name = '<cluster_name>'
ORDER BY u.cpu_percent DESC;
```

**All clusters:**
You can run the following query to check resource utilization for all clusters:

```mzsql
SELECT
    c.name AS cluster_name,
    c.id as cluster_id,
    r.name AS replica_name,
    u.cpu_percent,
    u.memory_percent
FROM mz_internal.mz_cluster_replica_utilization u
JOIN mz_catalog.mz_cluster_replicas r ON u.replica_id = r.id
JOIN mz_catalog.mz_clusters c ON r.cluster_id = c.id
WHERE c.id LIKE 'u%'
ORDER BY u.cpu_percent DESC;
```

- If the returned `cpu_percent` is high, all objects on that cluster experience
  correlated freshness degradation.

- If the returned `memory_percent` is high, Materialize may force data to disk,
  which can slow down processing.

Note that `cpu_percent` averages over the replica's workers, so a cluster whose
work is concentrated on one worker can degrade while reporting unremarkable CPU.
To attribute CPU to a cause, see [Cluster CPU
troubleshooting](/clusters/troubleshoot-clusters/cpu-troubleshooting/).

To resolve, scale the cluster up to a larger size ([`ALTER CLUSTER ... SET (SIZE
= '<new size>')`](/sql/alter-cluster/)), and/or move enough objects to another
cluster to reduce load on the current cluster. If the pressure is caused by an
[inefficient/expensive object](#step-1-find-lagging-objects), optimize the query
if possible.

> **Tip:** When a sudden increase in lag (i.e., a spike in lag) that affects a
> single cluster cannot be explained by CPU or memory pressure, [check whether
> DDL or deploy activity](#check-for-ddl-or-deploy-activity) occurred during the
> same window.

### Check for OOM crash loops

A cluster that repeatedly runs out of memory (OOM) will have its replica crash
and restart. Each restart triggers rehydration, during which no progress is
made, causing recurring freshness degradation.

To check if a replica for a cluster is in an OOM crash loop, check its status
history, replacing `<cluster_name>` with your cluster name:

```mzsql
SELECT
    rsh.replica_id,
    rsh.status,
    rsh.reason,
    rsh.occurred_at
FROM mz_internal.mz_cluster_replica_status_history rsh
JOIN mz_internal.mz_cluster_replica_history rh ON rsh.replica_id = rh.replica_id
WHERE rh.cluster_name = '<cluster_name>'
ORDER BY rsh.occurred_at DESC
LIMIT 20;
```

A repeating pattern of `offline` with reason `oom-killed` followed by `online`
confirms a crash loop. A replica that OOMs every few minutes is fundamentally
too small for its workload.

To resolve, scale the cluster up to a larger size ([`ALTER CLUSTER ... SET (SIZE
= '<new size>')`](/sql/alter-cluster/)), and/or move enough objects to another
cluster to reduce load on the current cluster. If the pressure is caused by an
[inefficient/expensive object](#step-1-find-lagging-objects), optimize the query
if possible.

### Check for no compute

The cluster has `replication_factor = 0`, meaning no replicas (i.e., compute
resources) are assigned. On clusters without replicas, objects have frontiers
that are frozen, and their lag grows indefinitely.

> **Note:** Zero-replica clusters are common for scheduled batch jobs (e.g., dbt snapshot
> runs) where replicas are scaled to zero between runs to save costs. High lag
> on these clusters is expected and does not indicate a problem.

To check, you can query `mz_catalog.mz_clusters` for clusters whose
`replication_factor = 0`.

```mzsql
SELECT c.name, c.replication_factor
FROM mz_catalog.mz_clusters c
WHERE c.replication_factor = 0;
```

- If the cluster was paused intentionally, no further action is needed.

- If compute is needed, set the replication factor to a non-zero integer
  ([`ALTER CLUSTER ... SET (REPLICATION FACTOR = <int>)`](/sql/alter-cluster/)).

## Check source ingestion

A source ingestion bottleneck occurs when the source is not ingesting data fast
enough. This can be caused by upstream connectivity issues, replication lag,
credential expiration, or a deliberately paused source.

### Check source status

To check if a source or its associated subsource/table is unhealthy, query
[`mz_internal.mz_source_statuses`](/sql/system-catalog/mz_internal/#mz_source_statuses):

```mzsql
SELECT s.id, o.name, s.type, s.status, s.error, s.details
FROM mz_internal.mz_source_statuses s
JOIN mz_catalog.mz_objects o ON s.id = o.id
WHERE o.id LIKE 'u%'
  AND s.status <> 'running';
```

A source with status `stalled`, `paused`, or `starting` will hold back all its
downstream objects. If the `status` for a source shows:

| Status   | Description |
| -------  | ----------- |
| `stalled`| Common causes include network partitions, credential expiration, and upstream database restarts. Check the returned `error` field and address appropriately. Once the source reconnects, downstream objects should catch up automatically. |
| `paused` | The cluster associated with the source has no compute/replica assigned (`replication_factor = 0`). See [Check for no compute](#check-for-no-compute). |
| `starting` | Wait for the source to transition to running. Downstream objects should catch up automatically.  |

## Investigating spikes

A spike in lag refers to a sudden increase in lag. Materialize retains wallclock
lag history for at least 30 days in
[`mz_internal.mz_wallclock_global_lag_history`](/sql/system-catalog/mz_internal/#mz_wallclock_global_lag_history),
binned by minute. You can use this data to find past spikes and determine their
cause.

### Find spikes in lag

Identify objects that experienced the largest lag spikes over the last 7 days:

```mzsql
SELECT
    o.name,
    o.type,
    c.name AS cluster_name,
    max(wl.lag) AS peak_lag,
    min(wl.occurred_at) FILTER (WHERE wl.lag > INTERVAL '1 minute') AS earliest_spike_occurrence,
           -- earliest_spike_occurrence may differ from time of the peak_lag
    avg(extract(epoch FROM wl.lag))::int || 's' AS avg_lag,
    count(*) FILTER (WHERE wl.lag > INTERVAL '10 seconds') AS minutes_above_10s
FROM mz_internal.mz_wallclock_global_lag_history wl
JOIN mz_catalog.mz_objects o ON wl.object_id = o.id
LEFT JOIN mz_catalog.mz_clusters c ON o.cluster_id = c.id
WHERE wl.occurred_at > now() - INTERVAL '7 days'
  AND o.id LIKE 'u%'
  AND wl.lag IS NOT NULL
GROUP BY o.name, o.type, c.name, wl.object_id
HAVING max(wl.lag) > INTERVAL '1 minute'
ORDER BY max(wl.lag) DESC
LIMIT 30;
```

You can exclude intentionally paused sources by adding `AND o.id NOT IN (...)`
to the `WHERE` clause.

### Determine spike scope

When a spike is identified, determine whether it affected a single object, a
single cluster, or the entire environment. The following query summarizes a time
window by cluster (substitute `<spike_start>`
and `<spike_end>` with your spike window):

```mzsql {hl_lines = "9"}
SELECT
    c.name AS cluster_name,
    count(DISTINCT wl.object_id) AS objects_affected,
    max(wl.lag) AS peak_lag,
    min(wl.lag) FILTER (WHERE wl.lag IS NOT NULL) AS min_lag
FROM mz_internal.mz_wallclock_global_lag_history wl
JOIN mz_catalog.mz_objects o ON wl.object_id = o.id
LEFT JOIN mz_catalog.mz_clusters c ON o.cluster_id = c.id
WHERE wl.occurred_at BETWEEN '<spike_start>' AND '<spike_end>'
  AND o.id LIKE 'u%'
  AND wl.lag > INTERVAL '1 minute'
GROUP BY c.name
ORDER BY peak_lag DESC;
```

Interpreting the results:

* **Single object affected**: The problem is specific to that object's dataflow or its direct inputs.
* **All objects on one cluster affected**: The cluster was overloaded or
  experienced a replica restart.
  - [Check the CPU/Memory pressure for the
    cluster](#check-the-cpu-or-memory-pressure) during that time window.
  - [Check for DDL or deploy activity](#check-for-ddl-or-deploy-activity) during
    that time window.

* **All clusters affected, including progress sources**: A system-level event
  occurred (environment restart, upgrade, or storage layer disruption). Lag that
  grows linearly at 1 minute per minute indicates frontiers were completely
  frozen for the duration of the event. These spikes are typically transient and
  self-resolving. If they recur frequently, check environment upgrade schedules and storage layer health.

### Inspect a specific spike

To see the minute-by-minute progression of a spike for a specific object:

```mzsql
SELECT wl.lag, wl.occurred_at
FROM mz_internal.mz_wallclock_global_lag_history wl
WHERE wl.object_id = '<object_id>'
  AND wl.occurred_at BETWEEN '<spike_start>' AND '<spike_end>'
ORDER BY wl.occurred_at;
```

Lag that increases linearly (by ~1 minute per minute) indicates the object's frontier was completely frozen — no progress was being made.
Lag that fluctuates around a baseline indicates the object is processing but cannot keep up with its input rate.

### Check for DDL or deploy activity

Object creation, alteration, or deletion triggers rehydration, which can cause
transient freshness degradation.

When a decrease in freshness affects a single cluster but is not explained by
[CPU or memory pressure](#check-the-cpu-or-memory-pressure), check whether DDL
operations occurred during the spike window.
[`mz_catalog.mz_audit_events`](/sql/system-catalog/mz_catalog/#mz_audit_events)
records all `CREATE`, `DROP`, and `ALTER` operations (substitute `<spike_start>`
and `<spike_end>` with your spike window):

```mzsql {hl_lines = "3"}
SELECT occurred_at, event_type, object_type, details
FROM mz_catalog.mz_audit_events
WHERE occurred_at BETWEEN '<spike_start>' AND '<spike_end>'
  AND object_type IN ('materialized-view', 'index', 'sink', 'cluster', 'cluster-replica')
ORDER BY occurred_at
LIMIT 50;
```

Look for patterns such as:

* **Deploy clusters being created/dropped**: A blue-green deploy hydrating
  objects on a separate cluster can cause contention with live clusters. A
  typical symptom is all objects on the live cluster showing elevated wallclock
  lag (30 seconds to several minutes) for 10–20 minutes while source lag remains
  low. Use the [time-series correlation
  query](#distinguish-source-driven-vs-computation-driven-spikes) to confirm. If
  freshness degrades on objects that were *not* themselves modified during the
  deploy, [contact Support](/support/) with the spike time window and audit
  event output.

* **Sink `alter` events**: Sinks being swapped to point to new upstream MVs
  trigger reprocessing.

* **Bulk `drop`/`create` of MVs or indexes**: Mass DDL causes rehydration on the
  affected cluster.

### Distinguish source-driven vs. computation-driven spikes

`mz_materialization_lag` only shows the current breakdown of `local_lag` vs. `global_lag`.
To determine whether past spikes were caused by sources or by downstream computation, compare peak lag across clusters at each minute:

```mzsql
SELECT
    wl.occurred_at,
    max(wl.lag) FILTER (WHERE c.name = '<source_cluster>') AS source_peak_lag,
    max(wl.lag) FILTER (WHERE c.name = '<mv_cluster>') AS mv_peak_lag
FROM mz_internal.mz_wallclock_global_lag_history wl
JOIN mz_catalog.mz_objects o ON wl.object_id = o.id
LEFT JOIN mz_catalog.mz_clusters c ON o.cluster_id = c.id
WHERE wl.occurred_at > now() - INTERVAL '7 days'
  AND o.id LIKE 'u%'
  AND c.name IN ('<source_cluster>', '<mv_cluster>')
  AND wl.lag IS NOT NULL
GROUP BY wl.occurred_at
HAVING max(wl.lag) FILTER (WHERE c.name = '<mv_cluster>') > INTERVAL '10 seconds'
ORDER BY wl.occurred_at DESC
LIMIT 30;
```

Interpreting the results:

* **`source_peak_lag` and `mv_peak_lag` move together**: the source is the bottleneck, and the MV cluster is inheriting its lag.
* **`source_peak_lag` stays low while `mv_peak_lag` spikes**: the MV cluster itself is falling behind, independent of its sources.
  This can happen during DDL operations, deploy events, or when the cluster is overloaded.

## Measuring aggregate freshness

This section provides queries to measure overall freshness across your deployment.

### Peak and threshold-based freshness

To count how many minutes exceed specific thresholds:

> **Tip:** You may want to exclude non-production (e.g., development/testing/staging) clusters that may produce misleading results.

```mzsql
SELECT
    o.name,
    o.type,
    c.name AS cluster_name,
    max(wl.lag) AS peak_lag,
    avg(extract(epoch FROM wl.lag))::int || 's' AS avg_lag,
    count(*) AS total_minutes,
    count(*) FILTER (WHERE wl.lag > INTERVAL '10 seconds') AS above_10s,
    count(*) FILTER (WHERE wl.lag > INTERVAL '1 minute') AS above_1m,
    count(*) FILTER (WHERE wl.lag > INTERVAL '5 minutes') AS above_5m,
    count(*) FILTER (WHERE wl.lag > INTERVAL '30 minutes') AS above_30m
FROM mz_internal.mz_wallclock_global_lag_history wl
JOIN mz_catalog.mz_objects o ON wl.object_id = o.id
LEFT JOIN mz_catalog.mz_clusters c ON o.cluster_id = c.id
LEFT JOIN mz_internal.mz_source_statuses ss ON o.id = ss.id
WHERE wl.occurred_at > now() - INTERVAL '7 days'
  AND o.id LIKE 'u%'
  AND wl.lag IS NOT NULL
  -- Exclude paused sources
  AND (ss.id IS NULL OR ss.status <> 'paused')
  -- Exclude zero-replica clusters
  AND (c.id IS NULL OR c.replication_factor > 0)
GROUP BY o.id, o.name, o.type, c.name
HAVING max(wl.lag) > INTERVAL '10 seconds'
ORDER BY max(wl.lag) DESC
LIMIT 30;
```

### Cluster-level freshness summary

To get a per-cluster summary (useful for SLO reporting):

> **Tip:** You may want to exclude non-production (e.g., development/testing/staging) clusters that may produce misleading results.

```mzsql
SELECT
    c.name AS cluster_name,
    count(DISTINCT wl.object_id) AS objects,
    max(wl.lag) AS peak_lag,
    avg(extract(epoch FROM wl.lag))::int || 's' AS avg_lag,
    count(*) FILTER (WHERE wl.lag > INTERVAL '1 minute') AS minutes_above_1m
FROM mz_internal.mz_wallclock_global_lag_history wl
JOIN mz_catalog.mz_objects o ON wl.object_id = o.id
JOIN mz_catalog.mz_clusters c ON o.cluster_id = c.id
LEFT JOIN mz_internal.mz_source_statuses ss ON o.id = ss.id
WHERE wl.occurred_at > now() - INTERVAL '7 days'
  AND o.id LIKE 'u%'
  AND wl.lag IS NOT NULL
  AND (ss.id IS NULL OR ss.status <> 'paused')   -- Exclude paused sources
  AND c.replication_factor > 0                   -- Exclude zero-replica clusters
GROUP BY c.name
ORDER BY max(wl.lag) DESC;
```

### Steady-state freshness analysis

To measure freshness outside of known events (deploys, restarts, upgrades),
exclude the specific time windows where spikes occurred rather than filtering by
lag threshold. Filtering by lag (e.g., excluding all minutes with lag above 1
minute) risks hiding genuine problems.

First, identify the spike windows using the [Find spikes in
lag](#find-spikes-in-lag). Then exclude those windows explicitly:

```mzsql
SELECT
    c.name AS cluster_name,
    count(DISTINCT wl.object_id) AS objects,
    max(wl.lag) AS peak_lag,
    avg(extract(epoch FROM wl.lag))::int || 's' AS avg_lag,
    count(*) FILTER (WHERE wl.lag > INTERVAL '5 seconds') AS minutes_above_5s,
    count(*) FILTER (WHERE wl.lag > INTERVAL '10 seconds') AS minutes_above_10s,
    count(*) FILTER (WHERE wl.lag > INTERVAL '30 seconds') AS minutes_above_30s,
    count(*) AS total_minutes
FROM mz_internal.mz_wallclock_global_lag_history wl
JOIN mz_catalog.mz_objects o ON wl.object_id = o.id
JOIN mz_catalog.mz_clusters c ON o.cluster_id = c.id
LEFT JOIN mz_internal.mz_source_statuses ss ON o.id = ss.id
WHERE wl.occurred_at > now() - INTERVAL '7 days'
  AND o.id LIKE 'u%'
  AND wl.lag IS NOT NULL
  AND (ss.id IS NULL OR ss.status <> 'paused')
  AND c.replication_factor > 0
  -- Exclude known event windows
  AND wl.occurred_at NOT BETWEEN '<event1_start>' AND '<event1_end>'
  AND wl.occurred_at NOT BETWEEN '<event2_start>' AND '<event2_end>'
GROUP BY c.name
ORDER BY max(wl.lag) DESC;
```

This gives an accurate picture of baseline freshness without masking unknown problems.

<!-- mz-docs page: transform-data/idiomatic-materialize-sql -->

# Idiomatic Materialize SQL

Learn about idiomatic Materialize SQL. Materialize offers various idiomatic query patterns, such as for top-k query pattern, first value/last value query paterrns, etc.

Materialize follows the SQL standard (SQL-92) implementation and strives for
compatibility with the PostgreSQL dialect. However, for some use cases,
Materialize provides its own idiomatic query patterns that can provide better
performance.

## Window functions

| Window Function | Idiomatic Materialize |
| --- | --- |
| <a href="/transform-data/idiomatic-materialize-sql/first-value/" >First value within groups</a> | <a href="/transform-data/idiomatic-materialize-sql/first-value/" >Use <code>MIN/MAX ... GROUP BY</code> subquery</a>. |
| <a href="/transform-data/idiomatic-materialize-sql/lag/" >Lag over a regularly increasing field</a> | <a href="/transform-data/idiomatic-materialize-sql/lag/" >Use self join or a self <code>LEFT JOIN/LEFT OUTER JOIN</code> by an <strong>equality match</strong> on the regularly increasing field</a>. |
| <a href="/transform-data/idiomatic-materialize-sql/last-value/" >Last value within groups</a> | <a href="/transform-data/idiomatic-materialize-sql/last-value/" >Use <code>MIN/MAX ... GROUP BY</code> subquery</a> |
| <a href="/transform-data/idiomatic-materialize-sql/lead/" >Lead over a regularly increasing field</a> | <a href="/transform-data/idiomatic-materialize-sql/lead/" >Use self join or a self <code>LEFT JOIN/LEFT OUTER JOIN</code> by an <strong>equality match</strong> on the regularly increasing field</a>. |
| <a href="/transform-data/idiomatic-materialize-sql/top-k/" >Top-K</a> | <a href="/transform-data/idiomatic-materialize-sql/top-k/" >Use an <code>ORDER BY ... LIMIT</code> subquery with a <code>LATERAL JOIN</code> on a <code>DISTINCT</code> subquery (or, for K=1,  a <code>SELECT DISTINCT ON ... ORDER BY ... LIMIT</code> query)</a> |

## General query patterns

| Query Pattern | Idiomatic Materialize |
| --- | --- |
| <a href="/transform-data/idiomatic-materialize-sql/any/" >ANY() Equi-join condition</a> | <a href="/transform-data/idiomatic-materialize-sql/any/" >Use <code>UNNEST()</code> or <code>DISTINCT UNNEST()</code> to expand the values and join</a>. |
| <a href="/transform-data/idiomatic-materialize-sql/not-in/" ><code>NOT IN (&lt;subquery&gt;)</code> predicate</a> | <a href="/transform-data/idiomatic-materialize-sql/not-in/" >Rewrite to <code>NOT EXISTS</code>, or filter out <code>NULL</code>s on both sides of the <code>NOT IN</code></a>. |
| <a href="/transform-data/idiomatic-materialize-sql/mz_now/#mz_now-expressions-to-calculate-past-or-future-timestamp" ><code>mz_now()</code> with date/time operators</a> | <a href="/transform-data/idiomatic-materialize-sql/mz_now/#mz_now-expressions-to-calculate-past-or-future-timestamp" >Move the operation to the other side of the comparison</a>: |
| <a href="/transform-data/idiomatic-materialize-sql/mz_now/#disjunctions-or" ><code>mz_now()</code> with disjunctions (<code>OR</code>) in materialized/indexed view definitions and <code>SUBSCRIBE</code> statements</a>: | <a href="/transform-data/idiomatic-materialize-sql/mz_now/#disjunctions-or" >Rewrite using <code>UNION ALL</code> or <code>UNION</code> (deduplicating as necessary) expression</a> |

<!-- mz-docs page: transform-data/idiomatic-materialize-sql/any -->

# `ANY()` equi-join condition
Use idiomatic Materialize SQL for equi-join whose `ON` expression includes the `ANY()` operator.
## Overview

The "`field = ANY(...)`" equality condition returns true if the equality
comparison is true for any of the values in the `ANY()` expression.

For equi-join whose `ON` expression includes an [`ANY` operator
expression](/sql/functions/#expression-bool_op-any),
Materialize provides an idiomatic SQL as an alternative to the `ANY()`
expression.

> ### Materialize and equi-join `ON fieldX = ANY(<array|list|map>)`
> When evaluating an equi-join whose `ON` expression includes the [`ANY` operator
> expression](/sql/functions/#expression-bool_op-any)
> (i.e., `ON fieldX = ANY(<array|list|map>)`), Materialize performs a cross join,
> which can lead to a significant increase in memory usage. If possible, rewrite
> the query to perform an equi-join on the unnested values.

## Idiomatic Materialize SQL

**Idiomatic Materialize SQL:**  For equi-join whose `ON` expression includes
the [`ANY` operator expression](/sql/functions/#expression-bool_op-any) (`ON
fieldX = ANY(<array|list|map>)`), use [UNNEST()](/sql/functions/#unnest) in a
[Common Table Expression (CTE)](/sql/select/#common-table-expressions-ctes) to
unnest the values and perform the equi-join on the unnested values. If the
array/list/map contains duplicates, include [`DISTINCT`](/sql/select/#select-distinct) to remove duplicates.

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><blue>Materialize SQL</blue></td>
<td class="copyableCode">

**If no duplicates exist in the unnested field:** Use a Common Table
Expression (CTE) to [`UNNEST()`](/sql/functions/#unnest) the array of
values and perform the equi-join on the unnested values.

```mzsql
-- array_field contains no duplicates.--

WITH my_expanded_values AS
(SELECT UNNEST(array_field) AS fieldZ FROM tableB)
SELECT a.fieldA, ...
FROM tableA a
JOIN my_expanded_values t ON a.fieldZ = t.fieldZ
;
```

**Duplicates may exist in the unnested field:** Use a Common Table
Expression (CTE) to [`DISTINCT`](/sql/select/#select-distinct)
[`UNNEST()`](/sql/functions/#unnest) the array of values and perform the
equi-join on the unnested values.

```mzsql
-- array_field may contain duplicates.--

WITH my_expanded_values AS
(SELECT DISTINCT UNNEST(array_field) AS fieldZ FROM tableB)
SELECT a.fieldA, ...
FROM tableA a
JOIN my_expanded_values t ON a.fieldZ = t.fieldZ
;
```

</td>
</tr>
<tr>
<td><red>Anti-pattern</red> ❌</td>
<td>

<red>Avoid the use of [`ANY(...)` function](/sql/functions/#expression-bool_op-any) for equi-join
conditions.</red>

```nofmt
-- Anti-pattern. Avoid. --
SELECT a.fieldA, ...
FROM tableA a, tableB b
WHERE a.fieldZ = ANY(b.array_field) -- Anti-pattern. Avoid.
;
```

</td>
</tr>

</tbody>
</table>

## Examples

> **Note:** The example data can be found in the
> [Appendix](/transform-data/idiomatic-materialize-sql/appendix/example-orders).

### Find orders with any sales items

Using idiomatic Materialize SQL, the following example finds orders that contain
any of the sales items for the week of the order. That is, the example uses a
CTE to [`UNNEST()`](/sql/functions/#unnest) (or
[`DISTINCT`](/sql/select/#select-distinct)[`UNNEST()`](/sql/functions/#unnest))
the `items` field from the `sales_items` table, and then performs an equi-join
with the `orders` table on the unnested values.

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>

<tr>
<td><blue>Materialize SQL</blue> ✅</td>
<td class="copyableCode">

***If no duplicates in the unnested field***

```mzsql
-- sales_items.items contains no duplicates. --

WITH individual_sales_items AS
(SELECT unnest(items) as item, week_of FROM sales_items)
SELECT s.week_of, o.order_id, o.item, o.quantity
FROM orders o
JOIN individual_sales_items s ON o.item = s.item
WHERE date_trunc('week', o.order_date) = s.week_of
ORDER BY s.week_of, o.order_id, o.item, o.quantity
;
```

***To omit duplicates that may exist in the unnested field***

```mzsql
-- sales_items.items may contains duplicates --

WITH individual_sales_items AS
(SELECT DISTINCT unnest(items) as item, week_of FROM sales_items)
SELECT s.week_of, o.order_id, o.item, o.quantity
FROM orders o
JOIN individual_sales_items s ON o.item = s.item
WHERE date_trunc('week', o.order_date) = s.week_of
ORDER BY s.week_of, o.order_id, o.item, o.quantity
;
```

</td>
</tr>

<tr>
<td><red>Anti-pattern</red> ❌</td>
<td>

<red>Avoid the use of [`ANY()`](/sql/functions/#expression-bool_op-any) for the equi-join condition.</red>

```nofmt
-- Anti-pattern. Avoid. --
SELECT s.week_of, o.order_id, o.item, o.quantity
FROM orders o
JOIN sales_items s ON o.item = ANY(s.items)
WHERE date_trunc('week', o.order_date) = s.week_of
ORDER BY s.week_of, o.order_id, o.item, o.quantity
;
```

</td>
</tr>

</tbody>
</table>

## See also

- [`ANY()`](/sql/functions/#expression-bool_op-any)

- [Common Table Expression (CTE)](/sql/select/#common-table-expressions-ctes)

- [Idiomatic Materialize SQL
  Chart](/transform-data/idiomatic-materialize-sql/appendix/idiomatic-sql-chart/)

- [`UNNEST()`](/sql/functions/#unnest)

<!-- mz-docs page: transform-data/idiomatic-materialize-sql/appendix -->

# Appendix

Idiomatic Materialize appendix, containing example data and cheatsheets

<!-- mz-docs page: transform-data/idiomatic-materialize-sql/appendix/example-orders -->

# Example data: items and orders
Sample data used in various examples.
The following sample data is used in the various Idiomatic Materialize SQL
pages:

```mzsql
CREATE TABLE orders (
    order_id int NOT NULL,
    order_date timestamp NOT NULL,
    item text NOT NULL,
    quantity int NOT NULL,
    status text NOT NULL
);

INSERT INTO orders VALUES
(1,current_timestamp - (1 * interval '3 day') - (35 * interval '1 minute'),'brownies',12, 'Complete'),
(1,current_timestamp - (1 * interval '3 day') - (35 * interval '1 minute'),'cupcake',12, 'Complete'),
(1,current_timestamp - (1 * interval '3 day') - (35 * interval '1 minute'),'chocolate cake',1, 'Complete'),
(2,current_timestamp - (1 * interval '3 day') - (15 * interval '1 minute'),'cheesecake',1, 'Complete'),
(3,current_timestamp - (1 * interval '3 day'),'chiffon cake',1, 'Complete'),
(3,current_timestamp - (1 * interval '3 day'),'egg tart',6, 'Complete'),
(3,current_timestamp - (1 * interval '3 day'),'fruit tart',6, 'Complete'),
(4,current_timestamp - (1 * interval '2 day')- (30 * interval '1 minute'),'cupcake',6, 'Shipped'),
(4,current_timestamp - (1 * interval '2 day')- (30 * interval '1 minute'),'cupcake',6, 'Shipped'),
(5,current_timestamp - (1 * interval '2 day'),'chocolate cake',1, 'Processing'),
(6,current_timestamp,'brownie',10, 'Pending'),
(6,current_timestamp,'chocolate cake',1, 'Pending'),
(7,current_timestamp,'chocolate chip cookie',20, 'Processing'),
(8,current_timestamp,'coffee cake',1, 'Complete'),
(8,current_timestamp,'fruit tart',4, 'Complete'),
(9,current_timestamp + (15 * interval '1 minute'),'chocolate chip cookie',20, 'Pending'),
(9,current_timestamp + (15 * interval '1 minute'),'brownie',20, 'Processing'),
(10,current_timestamp + (30 * interval '1 minute'),'sugar cookie',10, 'Pending'),
(10,current_timestamp + (30 * interval '1 minute'),'donut',36, 'Pending'),
(11,current_timestamp + (30 * interval '1 minute'),'chiffon cake',2, 'Pending'),
(11,current_timestamp + (30 * interval '1 minute'),'egg tart',6, 'Pending'),
(12,current_timestamp + (1 * interval '1 day') + (35 * interval '1 minute'),'cheesecake',1, 'Pending'),
(13,current_timestamp + (1 * interval '1 day')+ (35 * interval '1 minute'),'chocolate chip cookie',20, 'Pending'),
(14,current_timestamp + (1 * interval '1 day')+ (35 * interval '1 minute'),'brownie',20, 'Pending'),
(14,current_timestamp + (1 * interval '1 day')+ (35 * interval '1 minute'),'cheesecake',1, 'Pending'),
(14,current_timestamp + (1 * interval '1 day')+ (35 * interval '1 minute'),'cupcake',6, 'Pending'),
(15,current_timestamp + (1 * interval '1 day')+ (35 * interval '1 minute'),'chocolate cake',1, 'Pending'),
(16,current_timestamp + (1 * interval '2 day'),'chocolate cake',1, 'Pending'),
(17,current_timestamp + (1 * interval '2 day')+ (10 * interval '1 minute'),'coffee cake',1, 'Pending'),
(17,current_timestamp + (1 * interval '2 day')+ (10 * interval '1 minute'),'egg tart',12, 'Pending'),
(18,current_timestamp + (1 * interval '2 day')+ (15 * interval '1 minute'),'chocolate chip cookie',12, 'Pending'),
(18,current_timestamp + (1 * interval '2 day')+ (15 * interval '1 minute'),'brownie',12, 'Pending'),
(18,current_timestamp + (1 * interval '2 day')+ (15 * interval '1 minute'),'sugar cookie',12, 'Pending'),
(18,current_timestamp + (1 * interval '2 day')+ (15 * interval '1 minute'),'donut',12, 'Pending'),
(19,current_timestamp + (1 * interval '2 day')+ (30 * interval '1 minute'),'cupcake',6, 'Pending'),
(20,current_timestamp + (1 * interval '3 day'),'chiffon cake',1, 'Pending'),
(20,current_timestamp + (1 * interval '3 day'),'egg tart',6, 'Pending'),
(20,current_timestamp + (1 * interval '3 day'),'fruit tart',6, 'Pending'),
(21,current_timestamp + (1 * interval '3 day') + (15 * interval '1 minute'),'cheesecake',1, 'Pending'),
(22,current_timestamp + (1 * interval '3 day') + (35 * interval '1 minute'),'brownies',12, 'Pending'),
(22,current_timestamp + (1 * interval '3 day') + (35 * interval '1 minute'),'cupcake',12, 'Pending'),
(22,current_timestamp + (1 * interval '3 day') + (35 * interval '1 minute'),'chocolate cake',1, 'Pending')
;

CREATE TABLE items(
    item text NOT NULL,
    price numeric(8,4) NOT NULL,
    currency text NOT NULL DEFAULT 'USD'
);

INSERT INTO items VALUES
('brownie',2.25,'USD'),
('cheesecake',40,'USD'),
('chiffon cake',30,'USD'),
('chocolate cake',30,'USD'),
('chocolate chip cookie',2.5,'USD'),
('coffee cake',25,'USD'),
('cupcake',3,'USD'),
('donut',1.25,'USD'),
('egg tart',2.5,'USD'),
('fruit tart',4.5,'USD'),
('sugar cookie',2.5,'USD');

CREATE VIEW orders_view AS
SELECT o.*,i.price,o.quantity * i.price as subtotal
FROM orders as o
JOIN items as i
ON o.item = i.item;

CREATE VIEW orders_daily_totals AS
SELECT date_trunc('day',order_date) AS order_date,
       sum(subtotal) AS daily_total
FROM orders_view
GROUP BY date_trunc('day',order_date);

CREATE TABLE sales_items (
  week_of date NOT NULL,
  items text[]
);

INSERT INTO sales_items VALUES
(date_trunc('week', current_timestamp),ARRAY['brownie','chocolate chip cookie','chocolate cake']),
(date_trunc('week', current_timestamp + (1* interval '7 day')),ARRAY['chocolate chip cookie','donut','cupcake']);
```

<!-- mz-docs page: transform-data/idiomatic-materialize-sql/appendix/idiomatic-sql-chart -->

# Idiomatic Materialize SQL chart
Cheatsheet of idiomatic Materialize SQL.
Materialize follows the SQL standard (SQL-92) implementation and strives for
compatibility with the PostgreSQL dialect. However, for some use cases,
Materialize provides its own idiomatic query patterns that can provide better
performance.

## General

### Query Patterns

|   | Idiomatic Materialize SQL Pattern |
| --- | --- |
| <a href="/transform-data/idiomatic-materialize-sql/any/" ><code>ANY()</code> Equi-join condition</a> | <p><strong>If no duplicates exist in the unnested field:</strong> Use a Common Table Expression (CTE) to <a href="/sql/functions/#unnest" ><code>UNNEST()</code></a> the array of values and perform the equi-join on the unnested values.</p> <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="c1">-- array_field contains no duplicates.-- </span></span></span><span class="line"><span class="cl"><span class="c1"></span> </span></span><span class="line"><span class="cl"><span class="k">WITH</span> <span class="n">my_expanded_values</span> <span class="k">AS</span> </span></span><span class="line"><span class="cl"><span class="p">(</span><span class="k">SELECT</span> <span class="k">UNNEST</span><span class="p">(</span><span class="n">array_field</span><span class="p">)</span> <span class="k">AS</span> <span class="n">fieldZ</span> <span class="k">FROM</span> <span class="n">tableB</span><span class="p">)</span> </span></span><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="n">a</span><span class="mf">.</span><span class="n">fieldA</span><span class="p">,</span> <span class="mf">...</span> </span></span><span class="line"><span class="cl"><span class="k">FROM</span> <span class="n">tableA</span> <span class="n">a</span> </span></span><span class="line"><span class="cl"><span class="k">JOIN</span> <span class="n">my_expanded_values</span> <span class="n">t</span> <span class="k">ON</span> <span class="n">a</span><span class="mf">.</span><span class="n">fieldZ</span> <span class="o">=</span> <span class="n">t</span><span class="mf">.</span><span class="n">fieldZ</span> </span></span><span class="line"><span class="cl"><span class="p">;</span> </span></span></code></pre></div><p><strong>Duplicates may exist in the unnested field:</strong> Use a Common Table Expression (CTE) to <a href="/sql/select/#select-distinct" ><code>DISTINCT</code></a> <a href="/sql/functions/#unnest" ><code>UNNEST()</code></a> the array of values and perform the equi-join on the unnested values.</p> <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="c1">-- array_field may contain duplicates.-- </span></span></span><span class="line"><span class="cl"><span class="c1"></span> </span></span><span class="line"><span class="cl"><span class="k">WITH</span> <span class="n">my_expanded_values</span> <span class="k">AS</span> </span></span><span class="line"><span class="cl"><span class="p">(</span><span class="k">SELECT</span> <span class="k">DISTINCT</span> <span class="k">UNNEST</span><span class="p">(</span><span class="n">array_field</span><span class="p">)</span> <span class="k">AS</span> <span class="n">fieldZ</span> <span class="k">FROM</span> <span class="n">tableB</span><span class="p">)</span> </span></span><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="n">a</span><span class="mf">.</span><span class="n">fieldA</span><span class="p">,</span> <span class="mf">...</span> </span></span><span class="line"><span class="cl"><span class="k">FROM</span> <span class="n">tableA</span> <span class="n">a</span> </span></span><span class="line"><span class="cl"><span class="k">JOIN</span> <span class="n">my_expanded_values</span> <span class="n">t</span> <span class="k">ON</span> <span class="n">a</span><span class="mf">.</span><span class="n">fieldZ</span> <span class="o">=</span> <span class="n">t</span><span class="mf">.</span><span class="n">fieldZ</span> </span></span><span class="line"><span class="cl"><span class="p">;</span> </span></span></code></pre></div> |
| <a href="/transform-data/idiomatic-materialize-sql/not-in/" ><code>NOT IN (&lt;subquery&gt;)</code> predicate</a> | <p><strong>Rewrite to <code>NOT EXISTS</code> with a correlated subquery.</strong></p> <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="n">t1</span><span class="mf">.</span><span class="o">*</span> </span></span><span class="line"><span class="cl"><span class="k">FROM</span> <span class="n">t1</span> </span></span><span class="line"><span class="cl"><span class="k">WHERE</span> <span class="k">NOT</span> <span class="k">EXISTS</span> <span class="p">(</span><span class="k">SELECT</span> <span class="mf">1</span> <span class="k">FROM</span> <span class="n">t2</span> <span class="k">WHERE</span> <span class="n">t2</span><span class="mf">.</span><span class="n">a</span> <span class="o">=</span> <span class="n">t1</span><span class="mf">.</span><span class="n">a</span><span class="p">)</span> </span></span><span class="line"><span class="cl"><span class="p">;</span> </span></span></code></pre></div><p><strong>Filter out <code>NULL</code>s on both sides of the <code>NOT IN</code>.</strong></p> <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="n">t1</span><span class="mf">.</span><span class="o">*</span> </span></span><span class="line"><span class="cl"><span class="k">FROM</span> <span class="n">t1</span> </span></span><span class="line"><span class="cl"><span class="k">WHERE</span> <span class="n">t1</span><span class="mf">.</span><span class="n">a</span> <span class="k">IS</span> <span class="k">NOT</span> <span class="k">NULL</span> </span></span><span class="line"><span class="cl">  <span class="k">AND</span> <span class="n">t1</span><span class="mf">.</span><span class="n">a</span> <span class="k">NOT</span> <span class="k">IN</span> <span class="p">(</span><span class="k">SELECT</span> <span class="n">t2</span><span class="mf">.</span><span class="n">a</span> <span class="k">FROM</span> <span class="n">t2</span> <span class="k">WHERE</span> <span class="n">t2</span><span class="mf">.</span><span class="n">a</span> <span class="k">IS</span> <span class="k">NOT</span> <span class="k">NULL</span><span class="p">)</span> </span></span><span class="line"><span class="cl"><span class="p">;</span> </span></span></code></pre></div> |
| <a href="/transform-data/idiomatic-materialize-sql/mz_now/#mz_now-expressions-to-calculate-past-or-future-timestamp" ><code>mz_now()</code> with date/time operators</a> | Rewrite the query expression; specifically, move the operation to the other side of the comparison. |
| <a href="/transform-data/idiomatic-materialize-sql/mz_now/#disjunctions-or" ><code>mz_now()</code> with disjunctions (<code>OR</code>) in materialized/indexed view definitions and <code>SUBSCRIBE</code> statements</a> | <p>Rewrite as <code>UNION ALL</code> or <code>UNION</code>, deduplicating as necessary:</p> <ul> <li> <p>In some cases, you may need to modify the conditions to deduplicate results when using <code>UNION ALL</code>. For example, you might add the negation of one input&rsquo;s condition to the other as a conjunction.</p> </li> <li> <p>In some cases, using <code>UNION</code> instead of <code>UNION ALL</code> may suffice if the inputs do not contain other duplicates that need to be retained.</p> </li> </ul>  |

### Examples

|   | Example |
| --- | --- |
| <a href="/transform-data/idiomatic-materialize-sql/any/" ><code>ANY()</code> Equi-join condition</a> | <p><em><strong>If no duplicates in the unnested field</strong></em></p> <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="c1">-- sales_items.items contains no duplicates. -- </span></span></span><span class="line"><span class="cl"><span class="c1"></span> </span></span><span class="line"><span class="cl"><span class="k">WITH</span> <span class="n">individual_sales_items</span> <span class="k">AS</span> </span></span><span class="line"><span class="cl"><span class="p">(</span><span class="k">SELECT</span> <span class="k">unnest</span><span class="p">(</span><span class="n">items</span><span class="p">)</span> <span class="k">as</span> <span class="n">item</span><span class="p">,</span> <span class="n">week_of</span> <span class="k">FROM</span> <span class="n">sales_items</span><span class="p">)</span> </span></span><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="n">s</span><span class="mf">.</span><span class="n">week_of</span><span class="p">,</span> <span class="n">o</span><span class="mf">.</span><span class="n">order_id</span><span class="p">,</span> <span class="n">o</span><span class="mf">.</span><span class="n">item</span><span class="p">,</span> <span class="n">o</span><span class="mf">.</span><span class="n">quantity</span> </span></span><span class="line"><span class="cl"><span class="k">FROM</span> <span class="n">orders</span> <span class="n">o</span> </span></span><span class="line"><span class="cl"><span class="k">JOIN</span> <span class="n">individual_sales_items</span> <span class="n">s</span> <span class="k">ON</span> <span class="n">o</span><span class="mf">.</span><span class="n">item</span> <span class="o">=</span> <span class="n">s</span><span class="mf">.</span><span class="n">item</span> </span></span><span class="line"><span class="cl"><span class="k">WHERE</span> <span class="n">date_trunc</span><span class="p">(</span><span class="s1">&#39;week&#39;</span><span class="p">,</span> <span class="n">o</span><span class="mf">.</span><span class="n">order_date</span><span class="p">)</span> <span class="o">=</span> <span class="n">s</span><span class="mf">.</span><span class="n">week_of</span> </span></span><span class="line"><span class="cl"><span class="k">ORDER</span> <span class="k">BY</span> <span class="n">s</span><span class="mf">.</span><span class="n">week_of</span><span class="p">,</span> <span class="n">o</span><span class="mf">.</span><span class="n">order_id</span><span class="p">,</span> <span class="n">o</span><span class="mf">.</span><span class="n">item</span><span class="p">,</span> <span class="n">o</span><span class="mf">.</span><span class="n">quantity</span> </span></span><span class="line"><span class="cl"><span class="p">;</span> </span></span></code></pre></div><p><em><strong>To omit duplicates that may exist in the unnested field</strong></em></p> <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="c1">-- sales_items.items may contains duplicates -- </span></span></span><span class="line"><span class="cl"><span class="c1"></span> </span></span><span class="line"><span class="cl"><span class="k">WITH</span> <span class="n">individual_sales_items</span> <span class="k">AS</span> </span></span><span class="line"><span class="cl"><span class="p">(</span><span class="k">SELECT</span> <span class="k">DISTINCT</span> <span class="k">unnest</span><span class="p">(</span><span class="n">items</span><span class="p">)</span> <span class="k">as</span> <span class="n">item</span><span class="p">,</span> <span class="n">week_of</span> <span class="k">FROM</span> <span class="n">sales_items</span><span class="p">)</span> </span></span><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="n">s</span><span class="mf">.</span><span class="n">week_of</span><span class="p">,</span> <span class="n">o</span><span class="mf">.</span><span class="n">order_id</span><span class="p">,</span> <span class="n">o</span><span class="mf">.</span><span class="n">item</span><span class="p">,</span> <span class="n">o</span><span class="mf">.</span><span class="n">quantity</span> </span></span><span class="line"><span class="cl"><span class="k">FROM</span> <span class="n">orders</span> <span class="n">o</span> </span></span><span class="line"><span class="cl"><span class="k">JOIN</span> <span class="n">individual_sales_items</span> <span class="n">s</span> <span class="k">ON</span> <span class="n">o</span><span class="mf">.</span><span class="n">item</span> <span class="o">=</span> <span class="n">s</span><span class="mf">.</span><span class="n">item</span> </span></span><span class="line"><span class="cl"><span class="k">WHERE</span> <span class="n">date_trunc</span><span class="p">(</span><span class="s1">&#39;week&#39;</span><span class="p">,</span> <span class="n">o</span><span class="mf">.</span><span class="n">order_date</span><span class="p">)</span> <span class="o">=</span> <span class="n">s</span><span class="mf">.</span><span class="n">week_of</span> </span></span><span class="line"><span class="cl"><span class="k">ORDER</span> <span class="k">BY</span> <span class="n">s</span><span class="mf">.</span><span class="n">week_of</span><span class="p">,</span> <span class="n">o</span><span class="mf">.</span><span class="n">order_id</span><span class="p">,</span> <span class="n">o</span><span class="mf">.</span><span class="n">item</span><span class="p">,</span> <span class="n">o</span><span class="mf">.</span><span class="n">quantity</span> </span></span><span class="line"><span class="cl"><span class="p">;</span> </span></span></code></pre></div> |
| <a href="/transform-data/idiomatic-materialize-sql/not-in/" ><code>NOT IN (&lt;subquery&gt;)</code> predicate</a> | <p>Because the subquery uses <a href="/sql/functions/#unnest" ><code>UNNEST()</code></a> on a column of the outer-correlated row, factor the <code>UNNEST()</code> into an uncorrelated <a href="/sql/select/#common-table-expressions-ctes" >Common Table Expression (CTE)</a> first.</p> <p><em><strong>Rewrite to <code>NOT EXISTS</code> with a CTE for the <code>UNNEST()</code></strong></em></p> <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="k">WITH</span> <span class="n">this_weeks_sales</span> <span class="k">AS</span> <span class="p">(</span> </span></span><span class="line"><span class="cl">  <span class="k">SELECT</span> <span class="k">unnest</span><span class="p">(</span><span class="n">items</span><span class="p">)</span> <span class="k">AS</span> <span class="n">sale_item</span> </span></span><span class="line"><span class="cl">  <span class="k">FROM</span> <span class="n">sales_items</span> </span></span><span class="line"><span class="cl">  <span class="k">WHERE</span> <span class="n">week_of</span> <span class="o">=</span> <span class="n">date_trunc</span><span class="p">(</span><span class="s1">&#39;week&#39;</span><span class="p">,</span> <span class="n">current_timestamp</span><span class="p">)</span> </span></span><span class="line"><span class="cl"><span class="p">)</span> </span></span><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="n">i</span><span class="mf">.</span><span class="n">item</span><span class="p">,</span> <span class="n">i</span><span class="mf">.</span><span class="n">price</span> </span></span><span class="line"><span class="cl"><span class="k">FROM</span> <span class="n">items</span> <span class="n">i</span> </span></span><span class="line"><span class="cl"><span class="k">WHERE</span> <span class="k">NOT</span> <span class="k">EXISTS</span> <span class="p">(</span> </span></span><span class="line"><span class="cl">  <span class="k">SELECT</span> <span class="mf">1</span> <span class="k">FROM</span> <span class="n">this_weeks_sales</span> <span class="n">s</span> <span class="k">WHERE</span> <span class="n">s</span><span class="mf">.</span><span class="n">sale_item</span> <span class="o">=</span> <span class="n">i</span><span class="mf">.</span><span class="n">item</span> </span></span><span class="line"><span class="cl"><span class="p">)</span> </span></span><span class="line"><span class="cl"><span class="k">ORDER</span> <span class="k">BY</span> <span class="n">i</span><span class="mf">.</span><span class="n">item</span> </span></span><span class="line"><span class="cl"><span class="p">;</span> </span></span></code></pre></div><p><em><strong>Filter out <code>NULL</code>s with a CTE for the <code>UNNEST()</code></strong></em></p> <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="k">WITH</span> <span class="n">this_weeks_sales</span> <span class="k">AS</span> <span class="p">(</span> </span></span><span class="line"><span class="cl">  <span class="k">SELECT</span> <span class="k">unnest</span><span class="p">(</span><span class="n">items</span><span class="p">)</span> <span class="k">AS</span> <span class="n">sale_item</span> </span></span><span class="line"><span class="cl">  <span class="k">FROM</span> <span class="n">sales_items</span> </span></span><span class="line"><span class="cl">  <span class="k">WHERE</span> <span class="n">week_of</span> <span class="o">=</span> <span class="n">date_trunc</span><span class="p">(</span><span class="s1">&#39;week&#39;</span><span class="p">,</span> <span class="n">current_timestamp</span><span class="p">)</span> </span></span><span class="line"><span class="cl"><span class="p">)</span> </span></span><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="n">i</span><span class="mf">.</span><span class="n">item</span><span class="p">,</span> <span class="n">i</span><span class="mf">.</span><span class="n">price</span> </span></span><span class="line"><span class="cl"><span class="k">FROM</span> <span class="n">items</span> <span class="n">i</span> </span></span><span class="line"><span class="cl"><span class="k">WHERE</span> <span class="n">i</span><span class="mf">.</span><span class="n">item</span> <span class="k">IS</span> <span class="k">NOT</span> <span class="k">NULL</span> </span></span><span class="line"><span class="cl">  <span class="k">AND</span> <span class="n">i</span><span class="mf">.</span><span class="n">item</span> <span class="k">NOT</span> <span class="k">IN</span> <span class="p">(</span> </span></span><span class="line"><span class="cl">    <span class="k">SELECT</span> <span class="n">sale_item</span> <span class="k">FROM</span> <span class="n">this_weeks_sales</span> <span class="k">WHERE</span> <span class="n">sale_item</span> <span class="k">IS</span> <span class="k">NOT</span> <span class="k">NULL</span> </span></span><span class="line"><span class="cl">  <span class="p">)</span> </span></span><span class="line"><span class="cl"><span class="k">ORDER</span> <span class="k">BY</span> <span class="n">i</span><span class="mf">.</span><span class="n">item</span> </span></span><span class="line"><span class="cl"><span class="p">;</span> </span></span></code></pre></div> |
| <a href="/transform-data/idiomatic-materialize-sql/mz_now/#mz_now-expressions-to-calculate-past-or-future-timestamp" ><code>mz_now()</code> with date/time operators</a> | <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="o">*</span> <span class="k">from</span> <span class="n">orders</span> </span></span><span class="line"><span class="cl"><span class="k">WHERE</span> <span class="n">mz_now</span><span class="p">()</span> <span class="o">&gt;</span> <span class="n">order_date</span> <span class="o">+</span> <span class="nb">INTERVAL</span> <span class="s1">&#39;5min&#39;</span> </span></span><span class="line"><span class="cl"><span class="p">;</span> </span></span></code></pre></div> |
| <a href="/transform-data/idiomatic-materialize-sql/mz_now/#disjunctions-or" ><code>mz_now()</code> with disjunctions (<code>OR</code>) in materialized/indexed view definitions and <code>SUBSCRIBE</code> statements</a> | <p><strong>Rewrite as <code>UNION ALL</code> with possible duplicates</strong></p> <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="k">CREATE</span> <span class="k">MATERIALIZED</span> <span class="k">VIEW</span> <span class="n">forecast_completed_orders_duplicates_possible</span> <span class="k">AS</span> </span></span><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="n">item</span><span class="p">,</span> <span class="n">quantity</span><span class="p">,</span> <span class="n">status</span> <span class="k">from</span> <span class="n">orders</span> </span></span><span class="line"><span class="cl"><span class="k">WHERE</span> <span class="n">status</span> <span class="o">=</span> <span class="s1">&#39;Shipped&#39;</span> </span></span><span class="line"><span class="cl"><span class="k">UNION</span> <span class="k">ALL</span> </span></span><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="n">item</span><span class="p">,</span> <span class="n">quantity</span><span class="p">,</span> <span class="n">status</span> <span class="k">from</span> <span class="n">orders</span> </span></span><span class="line"><span class="cl"><span class="k">WHERE</span> <span class="n">order_date</span> <span class="o">+</span> <span class="nb">interval</span> <span class="s1">&#39;30&#39;</span> <span class="k">minutes</span> <span class="o">&gt;=</span> <span class="n">mz_now</span><span class="p">()</span> </span></span><span class="line"><span class="cl"><span class="p">;</span> </span></span></code></pre></div><p><strong>Rewrite as <code>UNION ALL</code> that avoids duplicates across queries</strong></p> <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="k">CREATE</span> <span class="k">MATERIALIZED</span> <span class="k">VIEW</span> <span class="n">forecast_completed_orders_deduplicated_union_all</span> <span class="k">AS</span> </span></span><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="n">item</span><span class="p">,</span> <span class="n">quantity</span><span class="p">,</span> <span class="n">status</span> <span class="k">from</span> <span class="n">orders</span> </span></span><span class="line"><span class="cl"><span class="k">WHERE</span> <span class="n">status</span> <span class="o">=</span> <span class="s1">&#39;Shipped&#39;</span> </span></span><span class="line"><span class="cl"><span class="k">UNION</span> <span class="k">ALL</span> </span></span><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="n">item</span><span class="p">,</span> <span class="n">quantity</span><span class="p">,</span> <span class="n">status</span> <span class="k">from</span> <span class="n">orders</span> </span></span><span class="line"><span class="cl"><span class="k">WHERE</span> <span class="n">order_date</span> <span class="o">+</span> <span class="nb">interval</span> <span class="s1">&#39;30&#39;</span> <span class="k">minutes</span> <span class="o">&gt;=</span> <span class="n">mz_now</span><span class="p">()</span> </span></span><span class="line"><span class="cl"><span class="k">AND</span> <span class="n">status</span> <span class="o">!=</span> <span class="s1">&#39;Shipped&#39;</span> <span class="c1">-- Deduplicate by excluding those with status &#39;Shipped&#39; </span></span></span><span class="line"><span class="cl"><span class="c1"></span><span class="p">;</span> </span></span></code></pre></div><p><strong>Rewrite as <code>UNION</code> to deduplicate any and all duplicated results</strong></p> <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="k">CREATE</span> <span class="k">MATERIALIZED</span> <span class="k">VIEW</span> <span class="n">forecast_completed_orders_deduplicated_results</span> <span class="k">AS</span> </span></span><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="n">item</span><span class="p">,</span> <span class="n">quantity</span><span class="p">,</span> <span class="n">status</span> <span class="k">from</span> <span class="n">orders</span> </span></span><span class="line"><span class="cl"><span class="k">WHERE</span> <span class="n">status</span> <span class="o">=</span> <span class="s1">&#39;Shipped&#39;</span> </span></span><span class="line"><span class="cl"><span class="k">UNION</span> </span></span><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="n">item</span><span class="p">,</span> <span class="n">quantity</span><span class="p">,</span> <span class="n">status</span> <span class="k">from</span> <span class="n">orders</span> </span></span><span class="line"><span class="cl"><span class="k">WHERE</span> <span class="n">order_date</span> <span class="o">+</span> <span class="nb">interval</span> <span class="s1">&#39;30&#39;</span> <span class="k">minutes</span> <span class="o">&gt;=</span> <span class="n">mz_now</span><span class="p">()</span> </span></span><span class="line"><span class="cl"><span class="p">;</span> </span></span></code></pre></div> |

## Window Functions
> ### Materialize and window functions
> For indexed views and materialized views that contain [window
> functions](/sql/functions/#window-functions) (including aggregate functions used
> with an `OVER` clause), when an input record in a partition is
> added/removed/changed, Materialize **recomputes the results from scratch** for
> that partition (instead of using incremental computation).
> The `PARTITION BY` clause of your window function determines your partitions. If
> `PARTITION BY` is omitted, all records belong to a single partition (i.e., any
> record change results in a recomputation from scratch over the whole input).
> To avoid performance issues that may arise as the number of records grows,
> consider rewriting your indexed views and materialized views to use idiomatic
> Materialize SQL instead of window functions. If your view definitions cannot be
> rewritten without the window functions and the performance of window functions
> is insufficient for your use case, please [contact our team](/support/).

### Query Patterns

|   | Idiomatic Materialize SQL Pattern |
| --- | --- |
| <a href="/transform-data/idiomatic-materialize-sql/top-k/#for-k--1" >Top-K over partition<br>(K &gt;= 1)</a> | <p>Use a subquery to <a href="/sql/select/#select-distinct" >SELECT DISTINCT</a> on the grouping key (e.g., <code>fieldA</code>), and perform a <a href="/sql/select/join/#lateral-subqueries" >LATERAL</a> join (by the grouping key <code>fieldA</code>) with another subquery that specifies the ordering (e.g., <code>fieldZ [ASC\|DESC]</code>) and the limit K.</p> <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="n">fieldA</span><span class="p">,</span> <span class="n">fieldB</span><span class="p">,</span> <span class="mf">...</span> </span></span><span class="line"><span class="cl"><span class="k">FROM</span> <span class="p">(</span><span class="k">SELECT</span> <span class="k">DISTINCT</span> <span class="n">fieldA</span> <span class="k">FROM</span> <span class="n">tableA</span><span class="p">)</span> <span class="n">grp</span><span class="p">,</span> </span></span><span class="line"><span class="cl">     <span class="k">LATERAL</span> <span class="p">(</span><span class="k">SELECT</span> <span class="n">fieldB</span><span class="p">,</span> <span class="mf">...</span> <span class="p">,</span> <span class="n">fieldZ</span> <span class="k">FROM</span> <span class="n">tableA</span> </span></span><span class="line"><span class="cl">        <span class="k">WHERE</span> <span class="n">fieldA</span> <span class="o">=</span> <span class="n">grp</span><span class="mf">.</span><span class="n">fieldA</span> </span></span><span class="line"><span class="cl">        <span class="k">ORDER</span> <span class="k">BY</span> <span class="n">fieldZ</span> <span class="mf">...</span> <span class="k">LIMIT</span> <span class="n">K</span><span class="p">)</span>   <span class="c1">-- K is a number &gt;= 1 </span></span></span><span class="line"><span class="cl"><span class="c1"></span><span class="k">ORDER</span> <span class="k">BY</span> <span class="n">fieldA</span><span class="p">,</span> <span class="n">fieldZ</span> <span class="mf">...</span> <span class="p">;</span> </span></span></code></pre></div> |
| <a href="/transform-data/idiomatic-materialize-sql/top-k/#for-k--1-1" >Top-K over partition<br>(K = 1)</a> | <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="k">DISTINCT</span> <span class="k">ON</span><span class="p">(</span><span class="n">fieldA</span><span class="p">)</span> <span class="n">fieldA</span><span class="p">,</span> <span class="n">fieldB</span><span class="p">,</span> <span class="mf">...</span> </span></span><span class="line"><span class="cl"><span class="k">FROM</span> <span class="n">tableA</span> </span></span><span class="line"><span class="cl"><span class="k">ORDER</span> <span class="k">BY</span> <span class="n">fieldA</span><span class="p">,</span> <span class="n">fieldZ</span> <span class="mf">...</span> <span class="p">;</span> </span></span></code></pre></div> |
| <a href="/transform-data/idiomatic-materialize-sql/first-value/" >First value over partition<br>order by &hellip;</a> | <p>Use a subquery that uses the <a href="/sql/functions/#min" >MIN()</a> or <a href="/sql/functions/#max" >MAX()</a> aggregate function.</p> <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="n">tableA</span><span class="mf">.</span><span class="n">fieldA</span><span class="p">,</span> <span class="n">tableA</span><span class="mf">.</span><span class="n">fieldB</span><span class="p">,</span> <span class="n">minmax</span><span class="mf">.</span><span class="n">Z</span> </span></span><span class="line"><span class="cl"> <span class="k">FROM</span> <span class="n">tableA</span><span class="p">,</span> </span></span><span class="line"><span class="cl"> <span class="p">(</span><span class="k">SELECT</span> <span class="n">fieldA</span><span class="p">,</span> </span></span><span class="line"><span class="cl">    <span class="n">MIN</span><span class="p">(</span><span class="n">fieldZ</span><span class="p">),</span> </span></span><span class="line"><span class="cl">    <span class="k">MAX</span><span class="p">(</span><span class="n">fieldZ</span><span class="p">)</span> </span></span><span class="line"><span class="cl"> <span class="k">FROM</span> <span class="n">tableA</span> </span></span><span class="line"><span class="cl"> <span class="k">GROUP</span> <span class="k">BY</span> <span class="n">fieldA</span><span class="p">)</span> <span class="n">minmax</span> </span></span><span class="line"><span class="cl"><span class="k">WHERE</span> <span class="n">tableA</span><span class="mf">.</span><span class="n">fieldA</span> <span class="o">=</span> <span class="n">minmax</span><span class="mf">.</span><span class="n">fieldA</span> </span></span><span class="line"><span class="cl"><span class="k">ORDER</span> <span class="k">BY</span> <span class="n">fieldA</span> <span class="mf">...</span> <span class="p">;</span> </span></span></code></pre></div> |
| <a href="/transform-data/idiomatic-materialize-sql/last-value/" >Last value over partition<br>order by &hellip;<br>range between unbounded preceding<br>and unbounded following</a> | <p>Use a subquery that uses the <a href="/sql/functions/#min" >MIN()</a> or <a href="/sql/functions/#max" >MAX()</a> aggregate function.</p> <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="n">tableA</span><span class="mf">.</span><span class="n">fieldA</span><span class="p">,</span> <span class="n">tableA</span><span class="mf">.</span><span class="n">fieldB</span><span class="p">,</span> <span class="n">minmax</span><span class="mf">.</span><span class="n">Z</span> </span></span><span class="line"><span class="cl"> <span class="k">FROM</span> <span class="n">tableA</span><span class="p">,</span> </span></span><span class="line"><span class="cl"> <span class="p">(</span><span class="k">SELECT</span> <span class="n">fieldA</span><span class="p">,</span> </span></span><span class="line"><span class="cl">    <span class="k">MAX</span><span class="p">(</span><span class="n">fieldZ</span><span class="p">),</span> </span></span><span class="line"><span class="cl">    <span class="n">MIN</span><span class="p">(</span><span class="n">fieldZ</span><span class="p">)</span> </span></span><span class="line"><span class="cl"> <span class="k">FROM</span> <span class="n">tableA</span> </span></span><span class="line"><span class="cl"> <span class="k">GROUP</span> <span class="k">BY</span> <span class="n">fieldA</span><span class="p">)</span> <span class="n">minmax</span> </span></span><span class="line"><span class="cl"><span class="k">WHERE</span> <span class="n">tableA</span><span class="mf">.</span><span class="n">fieldA</span> <span class="o">=</span> <span class="n">minmax</span><span class="mf">.</span><span class="n">fieldA</span> </span></span><span class="line"><span class="cl"><span class="k">ORDER</span> <span class="k">BY</span> <span class="n">fieldA</span> <span class="mf">...</span> <span class="p">;</span> </span></span></code></pre></div> |
| <a href="/transform-data/idiomatic-materialize-sql/lag/" >Lag over (order by) whose ordering can be represented by some equality condition.</a> | <p><em><strong>To exclude the first row since it has no previous row</strong></em></p> <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="c1">-- Excludes the first row in the results -- </span></span></span><span class="line"><span class="cl"><span class="c1"></span><span class="k">SELECT</span> <span class="n">t1</span><span class="mf">.</span><span class="n">fieldA</span><span class="p">,</span> <span class="n">t2</span><span class="mf">.</span><span class="n">fieldB</span> <span class="k">as</span> <span class="n">previous_row_value</span> </span></span><span class="line"><span class="cl"><span class="k">FROM</span> <span class="n">tableA</span> <span class="n">t1</span><span class="p">,</span> <span class="n">tableA</span> <span class="n">t2</span> </span></span><span class="line"><span class="cl"><span class="k">WHERE</span> <span class="n">t1</span><span class="mf">.</span><span class="n">fieldA</span> <span class="o">=</span> <span class="n">t2</span><span class="mf">.</span><span class="n">fieldA</span> <span class="o">+</span> <span class="mf">...</span> <span class="c1">-- or some other operand </span></span></span><span class="line"><span class="cl"><span class="c1"></span><span class="k">ORDER</span> <span class="k">BY</span> <span class="n">fieldA</span><span class="p">;</span> </span></span></code></pre></div><p><em><strong>To include the first row</strong></em></p> <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="c1">-- Includes the first row in the results -- </span></span></span><span class="line"><span class="cl"><span class="c1"></span><span class="k">SELECT</span> <span class="n">t1</span><span class="mf">.</span><span class="n">fieldA</span><span class="p">,</span> <span class="n">t2</span><span class="mf">.</span><span class="n">fieldB</span> <span class="k">as</span> <span class="n">previous_row_value</span> </span></span><span class="line"><span class="cl"><span class="k">FROM</span> <span class="n">tableA</span> <span class="n">t1</span> </span></span><span class="line"><span class="cl"><span class="k">LEFT</span> <span class="k">JOIN</span> <span class="n">tableA</span> <span class="n">t2</span> </span></span><span class="line"><span class="cl"><span class="k">ON</span> <span class="n">t1</span><span class="mf">.</span><span class="n">fieldA</span> <span class="o">=</span> <span class="n">t2</span><span class="mf">.</span><span class="n">fieldA</span> <span class="o">+</span> <span class="mf">...</span> <span class="c1">-- or some other operand </span></span></span><span class="line"><span class="cl"><span class="c1"></span><span class="k">ORDER</span> <span class="k">BY</span> <span class="n">fieldA</span><span class="p">;</span> </span></span></code></pre></div> |
| <a href="/transform-data/idiomatic-materialize-sql/lead/" >Lead over (order by) whose ordering can be represented by some equality condition.</a> | <p><em><strong>To exclude the last row since it has no next row</strong></em></p> <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="c1">-- Excludes the last row in the results -- </span></span></span><span class="line"><span class="cl"><span class="c1"></span><span class="k">SELECT</span> <span class="n">t1</span><span class="mf">.</span><span class="n">fieldA</span><span class="p">,</span> <span class="n">t2</span><span class="mf">.</span><span class="n">fieldB</span> <span class="k">as</span> <span class="n">next_row_value</span> </span></span><span class="line"><span class="cl"><span class="k">FROM</span> <span class="n">tableA</span> <span class="n">t1</span><span class="p">,</span> <span class="n">tableA</span> <span class="n">t2</span> </span></span><span class="line"><span class="cl"><span class="k">WHERE</span> <span class="n">t1</span><span class="mf">.</span><span class="n">fieldA</span> <span class="o">=</span> <span class="n">t2</span><span class="mf">.</span><span class="n">fieldA</span> <span class="o">-</span> <span class="mf">...</span> <span class="c1">-- or some other operand </span></span></span><span class="line"><span class="cl"><span class="c1"></span><span class="k">ORDER</span> <span class="k">BY</span> <span class="n">fieldA</span><span class="p">;</span> </span></span></code></pre></div><p><em><strong>To include the last row</strong></em></p> <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="c1">-- Includes the last row in the results -- </span></span></span><span class="line"><span class="cl"><span class="c1"></span><span class="k">SELECT</span> <span class="n">t1</span><span class="mf">.</span><span class="n">fieldA</span><span class="p">,</span> <span class="n">t2</span><span class="mf">.</span><span class="n">fieldB</span> <span class="k">as</span> <span class="n">next_row_value</span> </span></span><span class="line"><span class="cl"><span class="k">FROM</span> <span class="n">tableA</span> <span class="n">t1</span> </span></span><span class="line"><span class="cl"><span class="k">LEFT</span> <span class="k">JOIN</span> <span class="n">tableA</span> <span class="n">t2</span> </span></span><span class="line"><span class="cl"><span class="k">ON</span> <span class="n">t1</span><span class="mf">.</span><span class="n">fieldA</span> <span class="o">=</span> <span class="n">t2</span><span class="mf">.</span><span class="n">fieldA</span> <span class="o">-</span> <span class="mf">...</span> <span class="c1">-- or some other operand </span></span></span><span class="line"><span class="cl"><span class="c1"></span><span class="k">ORDER</span> <span class="k">BY</span> <span class="n">fieldA</span><span class="p">;</span> </span></span></code></pre></div> |

### Examples

|   | Example |
| --- | --- |
| <a href="/transform-data/idiomatic-materialize-sql/top-k/#for-k--1" >Top-K over partition<br>(K &gt;= 1)</a> | <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="n">order_id</span><span class="p">,</span> <span class="n">item</span><span class="p">,</span> <span class="n">subtotal</span> </span></span><span class="line"><span class="cl"><span class="k">FROM</span> <span class="p">(</span><span class="k">SELECT</span> <span class="k">DISTINCT</span> <span class="n">order_id</span> <span class="k">FROM</span> <span class="n">orders_view</span><span class="p">)</span> <span class="n">grp</span><span class="p">,</span> </span></span><span class="line"><span class="cl">     <span class="k">LATERAL</span> <span class="p">(</span><span class="k">SELECT</span> <span class="n">item</span><span class="p">,</span> <span class="n">subtotal</span> <span class="k">FROM</span> <span class="n">orders_view</span> </span></span><span class="line"><span class="cl">        <span class="k">WHERE</span> <span class="n">order_id</span> <span class="o">=</span> <span class="n">grp</span><span class="mf">.</span><span class="n">order_id</span> </span></span><span class="line"><span class="cl">        <span class="k">ORDER</span> <span class="k">BY</span> <span class="n">subtotal</span> <span class="k">DESC</span> <span class="k">LIMIT</span> <span class="mf">3</span><span class="p">)</span> </span></span><span class="line"><span class="cl"><span class="k">ORDER</span> <span class="k">BY</span> <span class="n">order_id</span><span class="p">,</span> <span class="n">subtotal</span> <span class="k">DESC</span><span class="p">;</span> </span></span></code></pre></div> |
| <a href="/transform-data/idiomatic-materialize-sql/top-k/#for-k--1-1" >Top-K over partition<br>(K = 1)</a> | <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="k">DISTINCT</span> <span class="k">ON</span><span class="p">(</span><span class="n">order_id</span><span class="p">)</span> <span class="n">order_id</span><span class="p">,</span> <span class="n">item</span><span class="p">,</span> <span class="n">subtotal</span> </span></span><span class="line"><span class="cl"><span class="k">FROM</span> <span class="n">orders_view</span> </span></span><span class="line"><span class="cl"><span class="k">ORDER</span> <span class="k">BY</span> <span class="n">order_id</span><span class="p">,</span> <span class="n">subtotal</span> <span class="k">DESC</span><span class="p">;</span> </span></span></code></pre></div> |
| <a href="/transform-data/idiomatic-materialize-sql/first-value/" >First value over partition<br>order by &hellip;</a> | <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="n">o</span><span class="mf">.</span><span class="n">order_id</span><span class="p">,</span> <span class="n">minmax</span><span class="mf">.</span><span class="n">lowest_price</span><span class="p">,</span> <span class="n">minmax</span><span class="mf">.</span><span class="n">highest_price</span><span class="p">,</span> <span class="n">o</span><span class="mf">.</span><span class="n">item</span><span class="p">,</span> <span class="n">o</span><span class="mf">.</span><span class="n">price</span><span class="p">,</span> </span></span><span class="line"><span class="cl">  <span class="n">o</span><span class="mf">.</span><span class="n">price</span> <span class="o">-</span> <span class="n">minmax</span><span class="mf">.</span><span class="n">lowest_price</span> <span class="k">AS</span> <span class="n">diff_lowest_price</span><span class="p">,</span> </span></span><span class="line"><span class="cl">  <span class="n">o</span><span class="mf">.</span><span class="n">price</span> <span class="o">-</span> <span class="n">minmax</span><span class="mf">.</span><span class="n">highest_price</span> <span class="k">AS</span> <span class="n">diff_highest_price</span> </span></span><span class="line"><span class="cl"><span class="k">FROM</span> <span class="n">orders_view</span> <span class="n">o</span><span class="p">,</span> </span></span><span class="line"><span class="cl">      <span class="p">(</span><span class="k">SELECT</span> <span class="n">order_id</span><span class="p">,</span> </span></span><span class="line"><span class="cl">         <span class="n">MIN</span><span class="p">(</span><span class="n">price</span><span class="p">)</span> <span class="k">AS</span> <span class="n">lowest_price</span><span class="p">,</span> </span></span><span class="line"><span class="cl">         <span class="k">MAX</span><span class="p">(</span><span class="n">price</span><span class="p">)</span> <span class="k">AS</span> <span class="n">highest_price</span> </span></span><span class="line"><span class="cl">      <span class="k">FROM</span> <span class="n">orders_view</span> </span></span><span class="line"><span class="cl">      <span class="k">GROUP</span> <span class="k">BY</span> <span class="n">order_id</span><span class="p">)</span> <span class="n">minmax</span> </span></span><span class="line"><span class="cl"><span class="k">WHERE</span> <span class="n">o</span><span class="mf">.</span><span class="n">order_id</span> <span class="o">=</span> <span class="n">minmax</span><span class="mf">.</span><span class="n">order_id</span> </span></span><span class="line"><span class="cl"><span class="k">ORDER</span> <span class="k">BY</span> <span class="n">o</span><span class="mf">.</span><span class="n">order_id</span><span class="p">,</span> <span class="n">o</span><span class="mf">.</span><span class="n">item</span><span class="p">;</span> </span></span></code></pre></div> |
| <a href="/transform-data/idiomatic-materialize-sql/last-value/" >Last value over partition<br>order by &hellip;<br>range between unbounded preceding<br>and unbounded following</a> | <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="n">o</span><span class="mf">.</span><span class="n">order_id</span><span class="p">,</span> <span class="n">minmax</span><span class="mf">.</span><span class="n">lowest_price</span><span class="p">,</span> <span class="n">minmax</span><span class="mf">.</span><span class="n">highest_price</span><span class="p">,</span> <span class="n">o</span><span class="mf">.</span><span class="n">item</span><span class="p">,</span> <span class="n">o</span><span class="mf">.</span><span class="n">price</span><span class="p">,</span> </span></span><span class="line"><span class="cl">  <span class="n">o</span><span class="mf">.</span><span class="n">price</span> <span class="o">-</span> <span class="n">minmax</span><span class="mf">.</span><span class="n">lowest_price</span> <span class="k">AS</span> <span class="n">diff_lowest_price</span><span class="p">,</span> </span></span><span class="line"><span class="cl">  <span class="n">o</span><span class="mf">.</span><span class="n">price</span> <span class="o">-</span> <span class="n">minmax</span><span class="mf">.</span><span class="n">highest_price</span> <span class="k">AS</span> <span class="n">diff_highest_price</span> </span></span><span class="line"><span class="cl"><span class="k">FROM</span> <span class="n">orders_view</span> <span class="n">o</span><span class="p">,</span> </span></span><span class="line"><span class="cl">      <span class="p">(</span><span class="k">SELECT</span> <span class="n">order_id</span><span class="p">,</span> </span></span><span class="line"><span class="cl">         <span class="n">MIN</span><span class="p">(</span><span class="n">price</span><span class="p">)</span> <span class="k">AS</span> <span class="n">lowest_price</span><span class="p">,</span> </span></span><span class="line"><span class="cl">         <span class="k">MAX</span><span class="p">(</span><span class="n">price</span><span class="p">)</span> <span class="k">AS</span> <span class="n">highest_price</span> </span></span><span class="line"><span class="cl">      <span class="k">FROM</span> <span class="n">orders_view</span> </span></span><span class="line"><span class="cl">      <span class="k">GROUP</span> <span class="k">BY</span> <span class="n">order_id</span><span class="p">)</span> <span class="n">minmax</span> </span></span><span class="line"><span class="cl"><span class="k">WHERE</span> <span class="n">o</span><span class="mf">.</span><span class="n">order_id</span> <span class="o">=</span> <span class="n">minmax</span><span class="mf">.</span><span class="n">order_id</span> </span></span><span class="line"><span class="cl"><span class="k">ORDER</span> <span class="k">BY</span> <span class="n">o</span><span class="mf">.</span><span class="n">order_id</span><span class="p">,</span> <span class="n">o</span><span class="mf">.</span><span class="n">item</span><span class="p">;</span> </span></span></code></pre></div> |
| <a href="/transform-data/idiomatic-materialize-sql/lag/" >Lag over (order by) whose ordering can be represented by some equality condition.</a> | <p><em><strong>To exclude the first row since it has no previous row</strong></em></p> <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="n">o1</span><span class="mf">.</span><span class="n">order_date</span><span class="p">,</span> <span class="n">o1</span><span class="mf">.</span><span class="n">daily_total</span><span class="p">,</span> </span></span><span class="line"><span class="cl">    <span class="n">o2</span><span class="mf">.</span><span class="n">daily_total</span> <span class="k">as</span> <span class="n">previous_daily_total</span> </span></span><span class="line"><span class="cl"><span class="k">FROM</span> <span class="n">orders_daily_totals</span> <span class="n">o1</span><span class="p">,</span> <span class="n">orders_daily_totals</span> <span class="n">o2</span> </span></span><span class="line"><span class="cl"><span class="k">WHERE</span> <span class="n">o1</span><span class="mf">.</span><span class="n">order_date</span> <span class="o">=</span> <span class="n">o2</span><span class="mf">.</span><span class="n">order_date</span> <span class="o">+</span> <span class="nb">INTERVAL</span> <span class="s1">&#39;1&#39;</span> <span class="k">DAY</span> </span></span><span class="line"><span class="cl"><span class="k">ORDER</span> <span class="k">BY</span> <span class="n">order_date</span><span class="p">;</span> </span></span></code></pre></div><p><em><strong>To include the first row</strong></em></p> <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="n">o1</span><span class="mf">.</span><span class="n">order_date</span><span class="p">,</span> <span class="n">o1</span><span class="mf">.</span><span class="n">daily_total</span><span class="p">,</span> </span></span><span class="line"><span class="cl">    <span class="n">o2</span><span class="mf">.</span><span class="n">daily_total</span> <span class="k">as</span> <span class="n">previous_daily_total</span> </span></span><span class="line"><span class="cl"><span class="k">FROM</span> <span class="n">orders_daily_totals</span> <span class="n">o1</span> </span></span><span class="line"><span class="cl"><span class="k">LEFT</span> <span class="k">JOIN</span> <span class="n">orders_daily_totals</span> <span class="n">o2</span> </span></span><span class="line"><span class="cl"><span class="k">ON</span> <span class="n">o1</span><span class="mf">.</span><span class="n">order_date</span> <span class="o">=</span> <span class="n">o2</span><span class="mf">.</span><span class="n">order_date</span> <span class="o">+</span> <span class="nb">INTERVAL</span> <span class="s1">&#39;1&#39;</span> <span class="k">DAY</span> </span></span><span class="line"><span class="cl"><span class="k">ORDER</span> <span class="k">BY</span> <span class="n">order_date</span><span class="p">;</span> </span></span></code></pre></div> |
| <a href="/transform-data/idiomatic-materialize-sql/lead/" >Lead over (order by) whose ordering can be represented by some equality condition.</a> | <p><em><strong>To exclude the last row since it has no next row</strong></em></p> <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="n">o1</span><span class="mf">.</span><span class="n">order_date</span><span class="p">,</span> <span class="n">o1</span><span class="mf">.</span><span class="n">daily_total</span><span class="p">,</span> </span></span><span class="line"><span class="cl">    <span class="n">o2</span><span class="mf">.</span><span class="n">daily_total</span> <span class="k">as</span> <span class="n">next_daily_total</span> </span></span><span class="line"><span class="cl"><span class="k">FROM</span> <span class="n">orders_daily_totals</span> <span class="n">o1</span><span class="p">,</span> <span class="n">orders_daily_totals</span> <span class="n">o2</span> </span></span><span class="line"><span class="cl"><span class="k">WHERE</span> <span class="n">o1</span><span class="mf">.</span><span class="n">order_date</span> <span class="o">=</span> <span class="n">o2</span><span class="mf">.</span><span class="n">order_date</span> <span class="o">-</span> <span class="nb">INTERVAL</span> <span class="s1">&#39;1&#39;</span> <span class="k">DAY</span> </span></span><span class="line"><span class="cl"><span class="k">ORDER</span> <span class="k">BY</span> <span class="n">order_date</span><span class="p">;</span> </span></span></code></pre></div><p><em><strong>To include the last row</strong></em></p> <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="n">o1</span><span class="mf">.</span><span class="n">order_date</span><span class="p">,</span> <span class="n">o1</span><span class="mf">.</span><span class="n">daily_total</span><span class="p">,</span> </span></span><span class="line"><span class="cl">    <span class="n">o2</span><span class="mf">.</span><span class="n">daily_total</span> <span class="k">as</span> <span class="n">next_daily_total</span> </span></span><span class="line"><span class="cl"><span class="k">FROM</span> <span class="n">orders_daily_totals</span> <span class="n">o1</span> </span></span><span class="line"><span class="cl"><span class="k">LEFT</span> <span class="k">JOIN</span> <span class="n">orders_daily_totals</span> <span class="n">o2</span> </span></span><span class="line"><span class="cl"><span class="k">ON</span> <span class="n">o1</span><span class="mf">.</span><span class="n">order_date</span> <span class="o">=</span> <span class="n">o2</span><span class="mf">.</span><span class="n">order_date</span> <span class="o">-</span> <span class="nb">INTERVAL</span> <span class="s1">&#39;1&#39;</span> <span class="k">DAY</span> </span></span><span class="line"><span class="cl"><span class="k">ORDER</span> <span class="k">BY</span> <span class="n">order_date</span><span class="p">;</span> </span></span></code></pre></div> |

## See also

- [SQL Functions](/sql/functions/)
- [SQL Types](/sql/types/)
- [SELECT](/sql/select/)
- [DISTINCT](/sql/select/#select-distinct)
- [DISTINCT ON](/sql/select/#select-distinct-on)

<!-- mz-docs page: transform-data/idiomatic-materialize-sql/appendix/window-function-to-materialize -->

# Window function to idiomatic Materialize
Cheatsheet for window functions to idiomatic Materialize SQL.
Materialize offers a wide range of [window
functions](/sql/functions/#window-functions). However, for some
[`LAG()`](/sql/functions/#lag), [`LEAD()`](/sql/functions/#lead),
[`ROW_NUMBER()`](/sql/functions/#row_number),
[`FIRST_VALUE()`](/sql/functions/#first_value), and
[`LAST_VALUE()`](/sql/functions/#last_value) use cases, Materialize provides its
own idiomatic query patterns that do <red>not</red> use the window functions and
can provide better performance.

> ### Materialize and window functions
> For indexed views and materialized views that contain [window
> functions](/sql/functions/#window-functions) (including aggregate functions used
> with an `OVER` clause), when an input record in a partition is
> added/removed/changed, Materialize **recomputes the results from scratch** for
> that partition (instead of using incremental computation).
> The `PARTITION BY` clause of your window function determines your partitions. If
> `PARTITION BY` is omitted, all records belong to a single partition (i.e., any
> record change results in a recomputation from scratch over the whole input).
> To avoid performance issues that may arise as the number of records grows,
> consider rewriting your indexed views and materialized views to use idiomatic
> Materialize SQL instead of window functions. If your view definitions cannot be
> rewritten without the window functions and the performance of window functions
> is insufficient for your use case, please [contact our team](/support/).

<table>
<thead>
<tr>
<th>
Windows function anti-pattern
</th>
<th>
Materialize idiomatic SQL
</th>
</tr>
</thead>
<tbody>

<tr>
<td colspan=2>

**First value within groups.** For more information and examples, see [Idiomatic Materialize SQL: First
value](/transform-data/idiomatic-materialize-sql/first-value/).

</td>
</tr>
<tr>
<td>
<div style="background-color: var(--code-block)">

```nofmt
-- Anti-pattern. Avoid. --
SELECT fieldA, fieldB,
 FIRST_VALUE(fieldZ)
   OVER (PARTITION BY fieldA ORDER BY ...)
FROM tableA
ORDER BY fieldA, ...;
```

</div>
</td>
<td class="copyableCode">

```mzsql
SELECT tableA.fieldA, tableA.fieldB, minmax.Z
FROM tableA,
     (SELECT fieldA,
        MIN(fieldZ)
      FROM tableA
      GROUP BY fieldA) minmax
WHERE tableA.fieldA = minmax.fieldA
ORDER BY fieldA ... ;
```

</td>
</tr>

<tr>
<td colspan=2>

**Lag over whose order by field advances in a regular pattern.**
For more information and examples, see [Idiomatic Materialize SQL: Lag
over](/transform-data/idiomatic-materialize-sql/lag/).

</td>
</tr>
<tr>
<td>
<div style="background-color: var(--code-block)">

```nofmt
-- Anti-pattern. Avoid --
SELECT fieldA, ...
  LAG(fieldZ)
    OVER (ORDER BY fieldA) as previous_row_value
FROM tableA;
```

</div>
</td>
<td class="copyableCode">

```mzsql
-- Excludes the first row in the results --
SELECT t1.fieldA, t2.fieldB as previous_row_value
FROM tableA t1, tableA t2
WHERE t1.fieldA = t2.fieldA + ...
ORDER BY fieldA;
```

</td>
</tr>

<tr>
<td colspan=2>

**Last value within groups.** For more information and examples, see [Idiomatic Materialize SQL: Last value in
group](/transform-data/idiomatic-materialize-sql/last-value/).

</td>
</tr>
<tr>
<td>
<div style="background-color: var(--code-block)">

```nofmt
-- Anti-pattern. Unsupported range. --
SELECT fieldA, fieldB,
  LAST_VALUE(fieldZ)
    OVER (PARTITION BY fieldA ORDER BY fieldZ
          RANGE BETWEEN
            UNBOUNDED PRECEDING AND
            UNBOUNDED FOLLOWING)
FROM tableA
ORDER BY fieldA, ...;
```

</div>
</td>
<td class="copyableCode">

```mzsql
SELECT tableA.fieldA, tableA.fieldB, minmax.Z
 FROM tableA,
      (SELECT fieldA,
         MAX(fieldZ)
       FROM tableA
       GROUP BY fieldA) minmax
WHERE tableA.fieldA = minmax.fieldA
ORDER BY fieldA ... ;
```

</td>
</tr>

<tr>
<td colspan=2>

**Lead over whose order by field advances in a regular pattern.** For more
information and examples, see [Idiomatic Materialize SQL: Lead
over](/transform-data/idiomatic-materialize-sql/lead/).

</td>
</tr>
<tr>
<td>
<div style="background-color: var(--code-block)">

```nofmt
-- Anti-pattern. Avoid. --
SELECT fieldA, ...
    LEAD(fieldZ)
      OVER (ORDER BY fieldA) as next_row_value
FROM tableA;
```

</div>
</td>
<td class="copyableCode">

```mzsql
-- Excludes the last row in the results --
SELECT t1.fieldA, t2.fieldB as next_row_value
FROM tableA t1, tableA t2
WHERE t1.fieldA = t2.fieldA - ...
ORDER BY fieldA;
```

</td>
</tr>

<tr>
<td colspan=2>

**Top-K queries.** For more information and examples, see [Idiomatic Materialize SQL: Top-K in
group](/transform-data/idiomatic-materialize-sql/top-k/).

</td>
</tr>
<tr>
<td>
<div style="background-color: var(--code-block)">

```nofmt
-- Anti-pattern. Avoid. --
SELECT fieldA, fieldB, ...
FROM (
  SELECT fieldA, fieldB, ... , fieldZ,
     ROW_NUMBER() OVER (PARTITION BY fieldA
     ORDER BY fieldZ ... ) as rn
  FROM tableA)
WHERE rn <= K
ORDER BY fieldA, fieldZ ...;
```

</div>
</td>
<td class="copyableCode">

```mzsql
SELECT fieldA, fieldB, ...
FROM (SELECT DISTINCT fieldA FROM tableA) grp,
  LATERAL (SELECT fieldB, ... , fieldZ FROM tableA
           WHERE fieldA = grp.fieldA
           ORDER BY fieldZ ... LIMIT K)
ORDER BY fieldA, fieldZ ... ;
```

</td>
</tr>
</tbody>
</table>

<!-- mz-docs page: transform-data/idiomatic-materialize-sql/first-value -->

# First value in group
Use idiomatic Materialize SQL to find the first value in each group.
## Overview

The "first value in each group" query pattern returns the first value, according
to some ordering, in each group.

> ### Materialize and window functions
> For indexed views and materialized views that contain [window
> functions](/sql/functions/#window-functions) (including aggregate functions used
> with an `OVER` clause), when an input record in a partition is
> added/removed/changed, Materialize **recomputes the results from scratch** for
> that partition (instead of using incremental computation).
> The `PARTITION BY` clause of your window function determines your partitions. If
> `PARTITION BY` is omitted, all records belong to a single partition (i.e., any
> record change results in a recomputation from scratch over the whole input).
> To avoid performance issues that may arise as the number of records grows,
> consider rewriting your indexed views and materialized views to use idiomatic
> Materialize SQL instead of window functions. If your view definitions cannot be
> rewritten without the window functions and the performance of window functions
> is insufficient for your use case, please [contact our team](/support/).

## Idiomatic Materialize SQL

**Idiomatic Materialize SQL:** To find the first value in each group, use
[MIN()](/sql/functions/#min) or [MAX()](/sql/functions/#max) aggregate function
in a subquery.

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><blue>Materialize SQL</blue></td>
<td class="copyableCode">

Use a subquery that uses the [MIN()](/sql/functions/#min) or
[MAX()](/sql/functions/#max) aggregate function.

```mzsql
SELECT tableA.fieldA, tableA.fieldB, minmax.Z
 FROM tableA,
 (SELECT fieldA,
    MIN(fieldZ),
    MAX(fieldZ)
 FROM tableA
 GROUP BY fieldA) minmax
WHERE tableA.fieldA = minmax.fieldA
ORDER BY fieldA ... ;
```

</td>
</tr>

<tr>
<td><red>Anti-pattern</red> ❌</td>
<td>

<red>Avoid the use of [`FIRST_VALUE() OVER (PARTITION BY ... ORDER BY ...)`
window function](/sql/functions/#first_value) for first value within groups
queries.</red>

```nofmt
-- Anti-pattern. Avoid. --
SELECT fieldA, fieldB,
 FIRST_VALUE(fieldZ) OVER (PARTITION BY fieldA ORDER BY ...),
 FIRST_VALUE(fieldZ) OVER (PARTITION BY fieldA ORDER BY ... DESC)
FROM tableA
ORDER BY fieldA, ...;
```

</td>
</tr>

</tbody>
</table>

### Query hints

To further improve the memory usage of the idiomatic Materialize SQL, you can
specify a [`AGGREGATE INPUT GROUP SIZE` query hint](/sql/select/#query-hints) in
the idiomatic Materialize SQL.

```mzsql
SELECT tableA.fieldA, tableA.fieldB, minmax.Z
 FROM tableA,
 (SELECT fieldA,
    MIN(fieldZ),
    MAX(fieldZ)
 FROM tableA
 GROUP BY fieldA
 OPTIONS (AGGREGATE INPUT GROUP SIZE = ...)
 ) minmax
WHERE tableA.fieldA = minmax.fieldA
ORDER BY fieldA ... ;
```

For more information on setting `AGGREGATE INPUT GROUP SIZE`, see
[Optimization](/transform-data/optimization/#query-hints).

## Examples

> **Note:** The example data can be found in the
> [Appendix](/transform-data/idiomatic-materialize-sql/appendix/example-orders).

### Use MIN() to find the first value

Using idiomatic Materialize SQL, the following example finds the lowest item
price in each order and calculates the difference between the price of each item
in the order and the lowest price. The example uses a subquery that groups by
the `order_id` and selects `MIN(price)` to find the lowest price (i.e., first
value if ordered by ascending price values).

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><blue>Materialize SQL</blue> ✅</td>
<td class="copyableCode">

```mzsql
SELECT o.order_id, minmax.lowest_price, o.item, o.price,
  o.price - minmax.lowest_price AS diff_lowest_price
FROM orders_view o,
      (SELECT order_id,
         MIN(price) AS lowest_price
      FROM orders_view
      GROUP BY order_id) minmax
WHERE o.order_id = minmax.order_id
ORDER BY o.order_id, o.item;
```

</td>
</tr>
<tr>
<td><red>Anti-pattern</red> ❌</td>
<td>

<red>Avoid the use of [`FIRST_VALUE() OVER (PARTITION BY ... ORDER BY ...)`
window function](/sql/functions/#first_value) for first value within groups queries.</red>

```nofmt
-- Anti-pattern --
SELECT order_id,
  FIRST_VALUE(price)
    OVER (PARTITION BY order_id ORDER BY price) AS lowest_price,
  item,
  price,
  price - FIRST_VALUE(price)
    OVER (PARTITION BY order_id ORDER BY price) AS diff_lowest_price
FROM orders_view
ORDER BY order_id, item;
```

</td>
</tr>
</tbody>
</table>

### Use MAX() to find the first value

Using idiomatic Materialize SQL, the following example finds the highest item
price in each order and calculates the difference between the price of each item
in the order and the highest price. The example uses a subquery that groups by
the `order_id` and selects `MAX(price)` to find the highest price (i.e., first
value if ordered by descending price values).

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><blue>Materialize SQL</blue> ✅</td>
<td class="copyableCode">

```mzsql
SELECT o.order_id, minmax.highest_price, o.item, o.price,
  o.price - minmax.highest_price AS diff_highest_price
FROM orders_view o,
      (SELECT order_id,
         MAX(price) AS highest_price
      FROM orders_view
      GROUP BY order_id) minmax
WHERE o.order_id = minmax.order_id
ORDER BY o.order_id, o.item;
```

</td>
</tr>
<tr>
<td><red>Anti-pattern</red> ❌</td>
<td>

<red>Avoid the use of [`FIRST_VALUE() OVER (PARTITION BY ... ORDER BY ...)`
window function](/sql/functions/#first_value) for first value within groups
queries.</red>

```nofmt
-- Anti-pattern --
SELECT order_id,
  FIRST_VALUE(price)
    OVER (PARTITION BY order_id ORDER BY price DESC) AS highest_price,
  item,
  price,
  price - FIRST_VALUE(price)
    OVER (PARTITION BY order_id ORDER BY price DESC) AS diff_highest_price
FROM orders_view
ORDER BY order_id, item;
```

</td>
</tr>
</tbody>
</table>

### Use MIN() and MAX() to find the first values

Using idiomatic Materialize SQL, the following example finds the lowest and the
highest item price in each order and calculates the difference between each item
in the order and these prices. The example uses a subquery that groups by the
`order_id` and selects `MIN(price)` as the lowest price (i.e., first
value if ordered by price values) and `MAX(price)` as the
highest price (i.e., first
value if ordered by descending price values).

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><blue>Materialize SQL</blue> ✅</td>
<td class="copyableCode">

```mzsql
SELECT o.order_id, minmax.lowest_price, minmax.highest_price, o.item, o.price,
  o.price - minmax.lowest_price AS diff_lowest_price,
  o.price - minmax.highest_price AS diff_highest_price
FROM orders_view o,
      (SELECT order_id,
         MIN(price) AS lowest_price,
         MAX(price) AS highest_price
      FROM orders_view
      GROUP BY order_id) minmax
WHERE o.order_id = minmax.order_id
ORDER BY o.order_id, o.item;
```

</td>
</tr>
<tr>
<td><red>Anti-pattern</red> ❌</td>
<td>

<red>Avoid the use of [`FIRST_VALUE() OVER (PARTITION BY ... ORDER BY ...)`
window function](/sql/functions/#first_value) for first value within groups
queries.</red>

```nofmt
-- Anti-pattern --
SELECT order_id,
  FIRST_VALUE(price)
    OVER (PARTITION BY order_id ORDER BY price) AS lowest_price,
  FIRST_VALUE(price)
    OVER (PARTITION BY order_id ORDER BY price DESC) AS highest_price,
  item,
  price,
  price - FIRST_VALUE(price)
    OVER (PARTITION BY order_id ORDER BY price) AS diff_lowest_price,
  price - FIRST_VALUE(price)
    OVER (PARTITION BY order_id ORDER BY price DESC) AS diff_highest_price
FROM orders_view
ORDER BY order_id, item;
```

</td>
</tr>
</tbody>
</table>

## See also

- [Last value in a group](/transform-data/idiomatic-materialize-sql/last-value)
- [`MIN()`](/sql/functions/#min)
- [`MAX()`](/sql/functions/#max)
- [Query hints for MIN/MAX](/transform-data/optimization/#query-hints)
- [Window functions](/sql/functions/#window-functions)

<!-- mz-docs page: transform-data/idiomatic-materialize-sql/lag -->

# Lag over
Use idiomatic Materialize SQL to access the previous row's value (lag) when ordered by a field that advances in a regular pattern, such as in regular intervals.
## Overview

The "lag over (order by )" query pattern accesses the field value of the
previous row as determined by some ordering.

For "lag over (order by)" queries whose ordering can be represented by some
equality condition (such as when ordering by a field that increases at a regular
interval), Materialize provides an idiomatic SQL as an alternative to the window
function.

> ### Materialize and window functions
> For indexed views and materialized views that contain [window
> functions](/sql/functions/#window-functions) (including aggregate functions used
> with an `OVER` clause), when an input record in a partition is
> added/removed/changed, Materialize **recomputes the results from scratch** for
> that partition (instead of using incremental computation).
> The `PARTITION BY` clause of your window function determines your partitions. If
> `PARTITION BY` is omitted, all records belong to a single partition (i.e., any
> record change results in a recomputation from scratch over the whole input).
> To avoid performance issues that may arise as the number of records grows,
> consider rewriting your indexed views and materialized views to use idiomatic
> Materialize SQL instead of window functions. If your view definitions cannot be
> rewritten without the window functions and the performance of window functions
> is insufficient for your use case, please [contact our team](/support/).

## Idiomatic Materialize SQL

> **Important:** Do not use if the "lag over (order by)" ordering cannot be represented by an
> equality match.

### Exclude the first row in results

**Idiomatic Materialize SQL:** To access the lag (previous row's field value)
ordered by some field that increases in a **regular** pattern, use a self join
that specifies an **equality condition** on the order by field (e.g., `WHERE
t1.order_field = t2.order_field + 1`, `WHERE t1.order_field = t2.order_field *
2`, etc.). The query *excludes* the first row since it does not have a previous
row.

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><blue>Idiomatic Materialize SQL</blue></td>
<td class="copyableCode">

<p>Use a self join that specifies an <strong>equality match</strong> on the lag&rsquo;s order by field
(e.g., <code>fieldA</code>). The order by field must increment in a regular pattern in
order to be represented by an equality condition (e.g., <code>WHERE t1.fieldA = t2.fieldA + ...</code>). The
query <em>excludes</em> the first row in the results since it does not have a previous
row.</p>
> **Important:** The idiomatic Materialize SQL applies only to those "lag over" queries whose
> ordering can be represented by some **equality condition**.

<div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="c1">-- Excludes the first row in the results --
</span></span></span><span class="line"><span class="cl"><span class="c1"></span><span class="k">SELECT</span> <span class="n">t1</span><span class="mf">.</span><span class="n">fieldA</span><span class="p">,</span> <span class="n">t2</span><span class="mf">.</span><span class="n">fieldB</span> <span class="k">as</span> <span class="n">previous_row_value</span>
</span></span><span class="line"><span class="cl"><span class="k">FROM</span> <span class="n">tableA</span> <span class="n">t1</span><span class="p">,</span> <span class="n">tableA</span> <span class="n">t2</span>
</span></span><span class="line"><span class="cl"><span class="k">WHERE</span> <span class="n">t1</span><span class="mf">.</span><span class="n">fieldA</span> <span class="o">=</span> <span class="n">t2</span><span class="mf">.</span><span class="n">fieldA</span> <span class="o">+</span> <span class="mf">...</span> <span class="c1">-- or some other operand
</span></span></span><span class="line"><span class="cl"><span class="c1"></span><span class="k">ORDER</span> <span class="k">BY</span> <span class="n">fieldA</span><span class="p">;</span>
</span></span></code></pre></div>

</td>
</tr>

<tr>
<td><red>Anti-pattern</red> ❌</td>
<td>

<red>Avoid the use of [`LAG(fieldZ) OVER (ORDER BY ...)`](/sql/functions/#lag)
window function when the order by field increases in a regular pattern.</red>

```nofmt
-- Anti-pattern. Avoid. --
SELECT fieldA, ...
    LAG(fieldZ) OVER (ORDER BY fieldA) as previous_row_value
FROM tableA;
```

</td>
</tr>

</tbody>
</table>

### Include the first row in results

**Idiomatic Materialize SQL:** To access the lag (previous row's field value)
ordered by some field that increases in a **regular** pattern, use a self
[`LEFT JOIN/LEFT OUTER JOIN`](/sql/select/join/#left-outer-join) that specifies
an **equality condition** on the order by field (e.g., `ON t1.order_field =
t2.order_field + 1`, `ON t1.order_field = t2.order_field * 2`, etc.). The `LEFT
JOIN/LEFT OUTER JOIN` query *includes* the first row, returning `null` as its
lag value.

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><blue>Idiomatic Materialize SQL</blue></td>
<td class="copyableCode">

<p>Use a self <a href="/sql/select/join/#left-outer-join" ><code>LEFT JOIN/LEFT OUTER JOIN</code></a>
(e.g., <code>FROM tableA t1 LEFT JOIN tableA t2</code>) that specifies an <strong>equality
match</strong> on the lag&rsquo;s order by field (e.g., <code>fieldA</code>). The order by field must
increment in a regular pattern in order to be represented by an equality
condition (e.g., <code>ON t1.fieldA = t2.fieldA + ...</code>). The
query <em>includes</em> the first row, returning <code>null</code> as its lag value.</p>
> **Important:** The idiomatic Materialize SQL applies only to those "lag over" queries whose
> ordering can be represented by some **equality condition**.

<div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="c1">-- Includes the first row in the results --
</span></span></span><span class="line"><span class="cl"><span class="c1"></span><span class="k">SELECT</span> <span class="n">t1</span><span class="mf">.</span><span class="n">fieldA</span><span class="p">,</span> <span class="n">t2</span><span class="mf">.</span><span class="n">fieldB</span> <span class="k">as</span> <span class="n">previous_row_value</span>
</span></span><span class="line"><span class="cl"><span class="k">FROM</span> <span class="n">tableA</span> <span class="n">t1</span>
</span></span><span class="line"><span class="cl"><span class="k">LEFT</span> <span class="k">JOIN</span> <span class="n">tableA</span> <span class="n">t2</span>
</span></span><span class="line"><span class="cl"><span class="k">ON</span> <span class="n">t1</span><span class="mf">.</span><span class="n">fieldA</span> <span class="o">=</span> <span class="n">t2</span><span class="mf">.</span><span class="n">fieldA</span> <span class="o">+</span> <span class="mf">...</span> <span class="c1">-- or some other operand
</span></span></span><span class="line"><span class="cl"><span class="c1"></span><span class="k">ORDER</span> <span class="k">BY</span> <span class="n">fieldA</span><span class="p">;</span>
</span></span></code></pre></div>

</td>
</tr>

<tr>
<td><red>Anti-pattern</red> ❌</td>
<td>

<red>Avoid the use of [`LAG(fieldZ) OVER (ORDER BY ...)`](/sql/functions/#lag)
window function when the order by field increases in a regular pattern.</red>

```nofmt
-- Anti-pattern. Avoid. --
SELECT fieldA, ...
    LAG(fieldZ) OVER (ORDER BY fieldA) as previous_row_value
FROM tableA;
```

</td>
</tr>

</tbody>
</table>

## Examples

> **Note:** The example data can be found in the
> [Appendix](/transform-data/idiomatic-materialize-sql/appendix/example-orders).

### Find previous row's value (exclude the first row in results)

Using idiomatic Materialize SQL, the following example finds the previous day's
order total. That is, the example uses a self join on `orders_daily_totals`. The
row ordering on the `order_date` field is represented by an **equality
condition** using an [interval of `1
DAY`](/sql/types/interval/#valid-operations). The
query excludes the first row in the results since the first row does not have a
previous row.

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>

<tr>
<td><blue>Materialize SQL</blue> ✅</td>
<td class="copyableCode">

<div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="c1">-- Excludes the first row in results --
</span></span></span><span class="line"><span class="cl"><span class="c1"></span><span class="k">SELECT</span> <span class="n">o1</span><span class="mf">.</span><span class="n">order_date</span><span class="p">,</span> <span class="n">o1</span><span class="mf">.</span><span class="n">daily_total</span><span class="p">,</span>
</span></span><span class="line"><span class="cl">    <span class="n">o2</span><span class="mf">.</span><span class="n">daily_total</span> <span class="k">as</span> <span class="n">previous_daily_total</span>
</span></span><span class="line"><span class="cl"><span class="k">FROM</span> <span class="n">orders_daily_totals</span> <span class="n">o1</span><span class="p">,</span> <span class="n">orders_daily_totals</span> <span class="n">o2</span>
</span></span><span class="line"><span class="cl"><span class="k">WHERE</span> <span class="n">o1</span><span class="mf">.</span><span class="n">order_date</span> <span class="o">=</span> <span class="n">o2</span><span class="mf">.</span><span class="n">order_date</span> <span class="o">+</span> <span class="nb">INTERVAL</span> <span class="s1">&#39;1&#39;</span> <span class="k">DAY</span>
</span></span><span class="line"><span class="cl"><span class="k">ORDER</span> <span class="k">BY</span> <span class="n">order_date</span><span class="p">;</span>
</span></span></code></pre></div>> **Important:** The idiomatic Materialize SQL applies only to those "lag over" queries whose
> ordering can be represented by some **equality condition**.

</td>
</tr>

<tr>
<td><red>Anti-pattern</red> ❌</td>
<td>

<red>Avoid the use of [`LAG() OVER (ORDER BY ...)` window
function](/sql/functions/#lag) to access previous row's value if the order by
field increases in a regular pattern.</red>

```nofmt
-- Anti-pattern. Includes the first row's value. --
SELECT order_date, daily_total,
    LAG(daily_total) OVER (ORDER BY order_date) as previous_daily_total
FROM orders_daily_totals;
```

</td>
</tr>
</tbody>
</table>

### Find previous row's value (include the first row in results)

Using idiomatic Materialize SQL, the following example finds the previous day's
order total. The example uses a self [`LEFT JOIN/LEFT OUTER
JOIN`](/sql/select/join/#left-outer-join) on `orders_daily_totals`. The
row ordering on the `order_date` field is represented by an **equality
condition** using an [interval of `1
DAY`](/sql/types/interval/#valid-operations). The
query includes the first row in the results, using `null` as the previous value.

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>

<tr>
<td><blue>Materialize SQL</blue> ✅</td>
<td class="copyableCode">

<div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="c1">-- Include the first row in results --
</span></span></span><span class="line"><span class="cl"><span class="c1"></span><span class="k">SELECT</span> <span class="n">o1</span><span class="mf">.</span><span class="n">order_date</span><span class="p">,</span> <span class="n">o1</span><span class="mf">.</span><span class="n">daily_total</span><span class="p">,</span>
</span></span><span class="line"><span class="cl">    <span class="n">o2</span><span class="mf">.</span><span class="n">daily_total</span> <span class="k">as</span> <span class="n">previous_daily_total</span>
</span></span><span class="line"><span class="cl"><span class="k">FROM</span> <span class="n">orders_daily_totals</span> <span class="n">o1</span>
</span></span><span class="line"><span class="cl"><span class="k">LEFT</span> <span class="k">JOIN</span> <span class="n">orders_daily_totals</span> <span class="n">o2</span>
</span></span><span class="line"><span class="cl"><span class="k">ON</span> <span class="n">o1</span><span class="mf">.</span><span class="n">order_date</span> <span class="o">=</span> <span class="n">o2</span><span class="mf">.</span><span class="n">order_date</span> <span class="o">+</span> <span class="nb">INTERVAL</span> <span class="s1">&#39;1&#39;</span> <span class="k">DAY</span>
</span></span><span class="line"><span class="cl"><span class="k">ORDER</span> <span class="k">BY</span> <span class="n">order_date</span><span class="p">;</span>
</span></span></code></pre></div>> **Important:** The idiomatic Materialize SQL applies only to those "lag over" queries whose
> ordering can be represented by some **equality condition**.

</td>
</tr>

<tr>
<td><red>Anti-pattern</red> ❌</td>
<td>

<red>Avoid the use of [`LAG() OVER (ORDER BY ...)` window
function](/sql/functions/#lag) to access previous row's value if the order by
field increases in a regular pattern.</red>

```nofmt
-- Anti-pattern. Includes the first row's value. --
SELECT order_date, daily_total,
    LAG(daily_total) OVER (ORDER BY order_date) as previous_daily_total
FROM orders_daily_totals;
```

</td>
</tr>

</tbody>
</table>

## See also

- [Lead over](/transform-data/idiomatic-materialize-sql/lead)
- [`INTERVAL`](/sql/types/interval/)
- [`LEFT JOIN/LEFT OUTER JOIN`](/sql/select/join/#left-outer-join)
- [`LAG()`](/sql/functions/#lag)
- [Window functions](/sql/functions/#window-functions)

<!-- mz-docs page: transform-data/idiomatic-materialize-sql/last-value -->

# Last value in group
Use idiomatic Materialize SQL to find the last value in each group.
## Overview

The "last value in each group" query pattern returns the last value, according
to some ordering, in each group.

> ### Materialize and window functions
> For indexed views and materialized views that contain [window
> functions](/sql/functions/#window-functions) (including aggregate functions used
> with an `OVER` clause), when an input record in a partition is
> added/removed/changed, Materialize **recomputes the results from scratch** for
> that partition (instead of using incremental computation).
> The `PARTITION BY` clause of your window function determines your partitions. If
> `PARTITION BY` is omitted, all records belong to a single partition (i.e., any
> record change results in a recomputation from scratch over the whole input).
> To avoid performance issues that may arise as the number of records grows,
> consider rewriting your indexed views and materialized views to use idiomatic
> Materialize SQL instead of window functions. If your view definitions cannot be
> rewritten without the window functions and the performance of window functions
> is insufficient for your use case, please [contact our team](/support/).

## Idiomatic Materialize SQL

**Idiomatic Materialize SQL:** To find the last value in each group, use the
[MIN()](/sql/functions/#min) or [MAX()](/sql/functions/#max) aggregate function
in a subquery.

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><blue>Idiomatic Materialize SQL</blue></td>
<td class="copyableCode">

Use a subquery that uses the [MIN()](/sql/functions/#min) or
[MAX()](/sql/functions/#max) aggregate function.

```mzsql
SELECT tableA.fieldA, tableA.fieldB, minmax.Z
 FROM tableA,
 (SELECT fieldA,
    MAX(fieldZ),
    MIN(fieldZ)
 FROM tableA
 GROUP BY fieldA) minmax
WHERE tableA.fieldA = minmax.fieldA
ORDER BY fieldA ... ;
```

</td>
</tr>

<tr>
<td><red>Anti-pattern</red> ❌</td>
<td>

<p><red>Do not use <a href="/sql/functions/#last_value" ><code>LAST_VALUE() OVER (PARTITION BY ... ORDER BY ... RANGE ...)</code> window function</a> for last value in each group
queries.</red></p>
> **Note:** Materialize does not support `RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED
> FOLLOWING`.

<pre tabindex="0"><code class="language-nofmt" data-lang="nofmt">-- Unsupported --
SELECT fieldA, fieldB,
  LAST_VALUE(fieldZ)
    OVER (PARTITION BY fieldA ORDER BY fieldZ
          RANGE BETWEEN
            UNBOUNDED PRECEDING AND
            UNBOUNDED FOLLOWING),
  LAST_VALUE(fieldZ)
    OVER (PARTITION BY fieldA ORDER BY fieldZ DESC
          RANGE BETWEEN
            UNBOUNDED PRECEDING AND
            UNBOUNDED FOLLOWING)
FROM tableA
ORDER BY fieldA, ...;
</code></pre>

</td>
</tr>

</tbody>
</table>

### Query hints

To further improve the memory usage of the idiomatic Materialize SQL, you can
specify a [`AGGREGATE INPUT GROUP SIZE` query hint](/sql/select/#query-hints) in
the idiomatic Materialize SQL.

```mzsql
SELECT tableA.fieldA, tableA.fieldB, minmax.Z
 FROM tableA,
 (SELECT fieldA,
    MAX(fieldZ),
    MIN(fieldZ)
 FROM tableA
 GROUP BY fieldA
 OPTIONS (AGGREGATE INPUT GROUP SIZE = ...)
 ) minmax
WHERE tableA.fieldA = minmax.fieldA
ORDER BY fieldA ... ;
```

For more information on setting `AGGREGATE INPUT GROUP SIZE`, see
[Optimization](/transform-data/optimization/#query-hints).

## Examples

> **Note:** The example data can be found in the
> [Appendix](/transform-data/idiomatic-materialize-sql/appendix/example-orders).

### Use MAX() to find the last value

Using idiomatic Materialize SQL, the following example finds the highest item
price in each order and calculates the difference between the price of each item
in the order and the highest price. The example uses a subquery that groups by
the `order_id` and selects [`MAX(price)`](/sql/functions/#max)  to find the
highest price (i.e., the last price if ordered by ascending price values):

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><blue>Idiomatic Materialize SQL</blue> ✅</td>
<td class="copyableCode">

```mzsql
SELECT o.order_id, minmax.highest_price, o.item, o.price,
  o.price - minmax.highest_price AS diff_highest_price
FROM orders_view o,
     (SELECT order_id,
        MAX(price) AS highest_price
     FROM orders_view
     GROUP BY order_id) minmax
WHERE o.order_id = minmax.order_id
ORDER BY o.order_id, o.item;
```

</td>
</tr>

<tr>
<td><red>Anti-pattern</red> ❌</td>
<td>

<p><red>Do not use of <code>LAST_VALUE() OVER (PARTITION BY ... ORDER BY ... RANGE ...)</code>
for last value in each group queries.</red></p>
> **Note:** Materialize does not support `RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED
> FOLLOWING`.

<pre tabindex="0"><code class="language-nofmt" data-lang="nofmt">-- Unsupported --
SELECT order_id,
  LAST_VALUE(price)
    OVER (PARTITION BY order_id ORDER BY price
          RANGE BETWEEN
            UNBOUNDED PRECEDING AND
            UNBOUNDED FOLLOWING) AS highest_price,
  item,
  price,
  price - LAST_VALUE(price)
    OVER (PARTITION BY order_id ORDER BY price
           RANGE BETWEEN
            UNBOUNDED PRECEDING AND
            UNBOUNDED FOLLOWING) AS diff_highest_price
FROM orders_view
ORDER BY order_id, item;
</code></pre>

</td>
</tr>
</tbody>
</table>

### Use MIN() to find the last values

Using idiomatic Materialize SQL, the following example finds the lowest item
price in each order and calculates the difference between the price of each item
in the order and the lowest price.  That is, use a subquery that groups by the
`order_id` and selects [`MIN(price)`](/sql/functions/#min)  as the lowest price
(i.e.,  last price if ordered by descending price value)

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><blue>Idiomatic Materialize SQL</blue> ✅</td>
<td class="copyableCode">

```mzsql
SELECT o.order_id, minmax.lowest_price, o.item, o.price,
  o.price - minmax.lowest_price AS diff_lowest_price
FROM orders_view o,
     (SELECT order_id,
        MIN(price) AS lowest_price
     FROM orders_view
     GROUP BY order_id) minmax
WHERE o.order_id = minmax.order_id
ORDER BY o.order_id, o.item;
```

</td>
</tr>

<tr>
<td><red>Anti-pattern</red> ❌</td>
<td>

<p><red>Do not use <code>LAST_VALUE() OVER (PARTITION BY ... ORDER BY ... RANGE ... )</code>
for last value in each group queries.</red></p>
> **Note:** Materialize does not support `RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED
> FOLLOWING`.

<pre tabindex="0"><code class="language-nofmt" data-lang="nofmt">-- Unsupported --
SELECT order_id,
  LAST_VALUE(price)
    OVER (PARTITION BY order_id ORDER BY price DESC
          RANGE BETWEEN
            UNBOUNDED PRECEDING AND
            UNBOUNDED FOLLOWING) AS lowest_price,
  item,
  price,
  price - LAST_VALUE(price)
    OVER (PARTITION BY order_id ORDER BY price DESC
          RANGE BETWEEN
            UNBOUNDED PRECEDING AND
            UNBOUNDED FOLLOWING) AS diff_lowest_price
FROM orders_view
ORDER BY order_id, item;
</code></pre>

</td>
</tr>
</tbody>
</table>

### Use MIN() and MAX() to find the last values

Using idiomatic Materialize SQL, the following example finds the lowest and
highest item price in each order and calculate the difference for each item in
the order from these prices. That is, use a subquery that groups by the
`order_id` and selects [`MIN(price)`](/sql/functions/#min) as the lowest price
(i.e., last value if ordered by descending price values) and
[`MAX(price)`](/sql/functions/#max) as the highest price (i.e., last value if
ordered by ascending price values).

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><blue>Idiomatic Materialize SQL</blue> ✅</td>
<td class="copyableCode">

```mzsql
SELECT o.order_id, minmax.lowest_price, minmax.highest_price, o.item, o.price,
  o.price - minmax.lowest_price AS diff_lowest_price,
  o.price - minmax.highest_price AS diff_highest_price
FROM orders_view o,
      (SELECT order_id,
         MIN(price) AS lowest_price,
         MAX(price) AS highest_price
      FROM orders_view
      GROUP BY order_id) minmax
WHERE o.order_id = minmax.order_id
ORDER BY o.order_id, o.item;
```

</td>
</tr>
<tr>
<td><red>Anti-pattern</red> ❌</td>
<td>

<p><red>Do not use <code>LAST_VALUE() OVER (PARTITION BY ... ORDER BY ...)</code> for last
value within groups queries.</red></p>
> **Note:** Materialize does not support `RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED
> FOLLOWING`.

<pre tabindex="0"><code class="language-nofmt" data-lang="nofmt">-- Unsupported --
SELECT order_id,
  LAST_VALUE(price)
    OVER (PARTITION BY order_id ORDER BY price DESC
          RANGE BETWEEN
            UNBOUNDED PRECEDING AND
            UNBOUNDED FOLLOWING) AS lowest_price,
  LAST_VALUE(price)
    OVER (PARTITION BY order_id ORDER BY price
          RANGE BETWEEN
            UNBOUNDED PRECEDING AND
            UNBOUNDED FOLLOWING) AS highest_price,
  item,
  price,
  price - LAST_VALUE(price)
    OVER (PARTITION BY order_id ORDER BY price DESC
          RANGE BETWEEN
            UNBOUNDED PRECEDING AND
            UNBOUNDED FOLLOWING) AS diff_lowest_price,
  price - LAST_VALUE(price)
    OVER (PARTITION BY order_id ORDER BY price
           RANGE BETWEEN
            UNBOUNDED PRECEDING AND
            UNBOUNDED FOLLOWING) AS diff_highest_price
FROM orders_view
ORDER BY order_id, item;
</code></pre>

</td>
</tr>

</tbody>
</table>

## See also

- [First value in a
  group](/transform-data/idiomatic-materialize-sql/first-value)
- [`MIN()`](/sql/functions/#min)
- [`MAX()`](/sql/functions/#max)
- [Query hints for MIN/MAX](/transform-data/optimization/#query-hints)
- [Window functions](/sql/functions/#window-functions)

<!-- mz-docs page: transform-data/idiomatic-materialize-sql/lead -->

# Lead over
Use idiomatic Materialize SQL to access the next row's value (lead) when ordered by a field that advances in a regular pattern, such as in regular intervals.
## Overview

The "lead over" query pattern accesses the field value of the next row as
determined by some ordering.

For "lead over (order by)" queries whose ordering can be represented by some
equality condition (such as when ordering by a field that increases at a regular
interval), Materialize provides an idiomatic SQL as an alternative to the window
function.

> ### Materialize and window functions
> For indexed views and materialized views that contain [window
> functions](/sql/functions/#window-functions) (including aggregate functions used
> with an `OVER` clause), when an input record in a partition is
> added/removed/changed, Materialize **recomputes the results from scratch** for
> that partition (instead of using incremental computation).
> The `PARTITION BY` clause of your window function determines your partitions. If
> `PARTITION BY` is omitted, all records belong to a single partition (i.e., any
> record change results in a recomputation from scratch over the whole input).
> To avoid performance issues that may arise as the number of records grows,
> consider rewriting your indexed views and materialized views to use idiomatic
> Materialize SQL instead of window functions. If your view definitions cannot be
> rewritten without the window functions and the performance of window functions
> is insufficient for your use case, please [contact our team](/support/).

## Idiomatic Materialize SQL

> **Important:** Do not use if the "lead over (order by)" ordering cannot be represented by an
> equality match.

### Exclude the last row in results

**Idiomatic Materialize SQL:** To access the lead (next row's field value)
ordered by some field that increases in **regular** intervals, use a self join
that specifies an **equality condition** on the order by field (e.g., `WHERE
t1.order_field = t2.order_field - 1`, `WHERE t1.order_field = t2.order_field *
2`, etc.). The query *excludes* the last row in the results since it does not
have a next row.

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><blue>Idiomatic Materialize SQL</blue></td>
<td class="copyableCode">

<p>Use a self join that specifies an <strong>equality match</strong> on the lead&rsquo;s order by
field (e.g., <code>fieldA</code>). The order by field must increment in a regular pattern
in order to be represented by an equality condition (e.g., <code>WHERE t1.fieldA = t2.fieldA - ...</code>). The query <em>excludes</em> the last row in the results since it
does not have a next row.</p>
> **Important:** The idiomatic Materialize SQL applies only to those "lead over" queries whose
> ordering can be represented by some **equality condition**.

<div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="c1">-- Excludes the last row in the results --
</span></span></span><span class="line"><span class="cl"><span class="c1"></span><span class="k">SELECT</span> <span class="n">t1</span><span class="mf">.</span><span class="n">fieldA</span><span class="p">,</span> <span class="n">t2</span><span class="mf">.</span><span class="n">fieldB</span> <span class="k">as</span> <span class="n">next_row_value</span>
</span></span><span class="line"><span class="cl"><span class="k">FROM</span> <span class="n">tableA</span> <span class="n">t1</span><span class="p">,</span> <span class="n">tableA</span> <span class="n">t2</span>
</span></span><span class="line"><span class="cl"><span class="k">WHERE</span> <span class="n">t1</span><span class="mf">.</span><span class="n">fieldA</span> <span class="o">=</span> <span class="n">t2</span><span class="mf">.</span><span class="n">fieldA</span> <span class="o">-</span> <span class="mf">...</span>  <span class="c1">-- or some other operand
</span></span></span><span class="line"><span class="cl"><span class="c1"></span><span class="k">ORDER</span> <span class="k">BY</span> <span class="n">fieldA</span><span class="p">;</span>
</span></span></code></pre></div>

</td>
</tr>

<tr>
<td><red>Anti-pattern</red> ❌</td>
<td>

<red>Avoid the use of [`LEAD(fieldZ) OVER (ORDER BY ...)`](/sql/functions/#lead)
window function when the order by field increases in a regular pattern.</red>

```nofmt
-- Anti-pattern. Avoid. --
SELECT fieldA, ...
    LEAD(fieldZ) OVER (ORDER BY fieldA) as next_row_value
FROM tableA;
```

</td>
</tr>

</tbody>
</table>

### Include the last row in results

**Idiomatic Materialize SQL:** To access the lead (next row's field value)
ordered by some field that increases in **regular** intervals, use a self [`LEFT
JOIN/LEFT OUTER JOIN`](/sql/select/join/#left-outer-join) that specifies an
**equality condition** on the order by field (e.g., `ON t1.order_field =
t2.order_field - 1`, `ON t1.order_field = t2.order_field * 2`, etc.). The `LEFT
JOIN/LEFT OUTER JOIN` query *includes* the last row, returning `null` as its
lead value.

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><blue>Idiomatic Materialize SQL</blue></td>
<td class="copyableCode">

<p>Use a self <a href="/sql/select/join/#left-outer-join" ><code>LEFT JOIN/LEFT OUTER JOIN</code></a>
(e.g., <code>FROM tableA t1 LEFT JOIN tableA t2</code>) that specifies an <strong>equality
match</strong> on the lag&rsquo;s order by field (e.g., <code>fieldA</code>).  The order by field must
increment in a regular pattern in order to be represented by an equality
condition (e.g., <code>ON t1.fieldA = t2.fieldA - ...</code>). The query <em>includes</em> the
last row, returning <code>null</code> as its lead value.</p>
> **Important:** The idiomatic Materialize SQL applies only to those "lead over" queries whose
> ordering can be represented by some **equality condition**.

<div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="c1">-- Includes the last row in the response --
</span></span></span><span class="line"><span class="cl"><span class="c1"></span><span class="k">SELECT</span> <span class="n">t1</span><span class="mf">.</span><span class="n">fieldA</span><span class="p">,</span> <span class="n">t2</span><span class="mf">.</span><span class="n">fieldB</span> <span class="k">as</span> <span class="n">next_row_value</span>
</span></span><span class="line"><span class="cl"><span class="k">FROM</span> <span class="n">tableA</span> <span class="n">t1</span>
</span></span><span class="line"><span class="cl"><span class="k">LEFT</span> <span class="k">JOIN</span> <span class="n">tableA</span> <span class="n">t2</span>
</span></span><span class="line"><span class="cl"><span class="k">ON</span> <span class="n">t1</span><span class="mf">.</span><span class="n">fieldA</span> <span class="o">=</span> <span class="n">t2</span><span class="mf">.</span><span class="n">fieldA</span> <span class="o">-</span> <span class="mf">...</span> <span class="c1">-- or some other operand
</span></span></span><span class="line"><span class="cl"><span class="c1"></span><span class="k">ORDER</span> <span class="k">BY</span> <span class="n">fieldA</span><span class="p">;</span>
</span></span></code></pre></div>

</td>
</tr>

<tr>
<td><red>Anti-pattern</red> ❌</td>
<td>

<red>Avoid the use of [`LEAD(fieldZ) OVER (ORDER BY ...)`](/sql/functions/#lead)
window function when the order by field increases in a regular pattern.</red>

```nofmt
-- Anti-pattern. Avoid. --
SELECT fieldA, ...
    LEAD(fieldZ) OVER (ORDER BY fieldA) as next_row_value
FROM tableA;
```

</td>
</tr>

</tbody>
</table>

## Examples

> **Note:** The example data can be found in the
> [Appendix](/transform-data/idiomatic-materialize-sql/appendix/example-orders).

### Find next row's value (exclude the last row in results)

Using idiomatic Materialize SQL, the following example finds the next day's
order total. That is, the example uses a self join on `orders_daily_totals`. The
row ordering on the `order_date` field is represented by an **equality
condition** using an [interval of `1
DAY`](/sql/types/interval/#valid-operations). The
query excludes the last row in the results since the last row does not have a
next row.

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>

<tr>
<td><blue>Materialize SQL</blue> ✅</td>
<td class="copyableCode">

<div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="c1">-- Excludes the last row in results --
</span></span></span><span class="line"><span class="cl"><span class="c1"></span><span class="k">SELECT</span> <span class="n">o1</span><span class="mf">.</span><span class="n">order_date</span><span class="p">,</span> <span class="n">o1</span><span class="mf">.</span><span class="n">daily_total</span><span class="p">,</span>
</span></span><span class="line"><span class="cl">    <span class="n">o2</span><span class="mf">.</span><span class="n">daily_total</span> <span class="k">as</span> <span class="n">next_daily_total</span>
</span></span><span class="line"><span class="cl"><span class="k">FROM</span> <span class="n">orders_daily_totals</span> <span class="n">o1</span><span class="p">,</span> <span class="n">orders_daily_totals</span> <span class="n">o2</span>
</span></span><span class="line"><span class="cl"><span class="k">WHERE</span> <span class="n">o1</span><span class="mf">.</span><span class="n">order_date</span> <span class="o">=</span> <span class="n">o2</span><span class="mf">.</span><span class="n">order_date</span> <span class="o">-</span> <span class="nb">INTERVAL</span> <span class="s1">&#39;1&#39;</span> <span class="k">DAY</span>
</span></span><span class="line"><span class="cl"><span class="k">ORDER</span> <span class="k">BY</span> <span class="n">order_date</span><span class="p">;</span>
</span></span></code></pre></div>> **Important:** The idiomatic Materialize SQL applies only to those "lead over" queries whose
> ordering can be represented by some **equality condition**.

</td>
</tr>

<tr>
<td><red>Anti-pattern</red> ❌</td>
<td>

<red>Avoid the use of [`LEAD() OVER (ORDER BY ...)` window
function](/sql/functions/#lead) to access next row's value if the order by
field increases in a regular pattern.</red>

```nofmt
-- Anti-pattern. Includes the last row's value. --
SELECT order_date, daily_total,
    LEAD(daily_total) OVER (ORDER BY order_date) as next_daily_total
FROM orders_daily_totals;
```

</td>
</tr>
</tbody>
</table>

### Find next row's value (include the last row in results)

Using idiomatic Materialize SQL, the following example finds the next day's
order total. The example uses a self [`LEFT JOIN/LEFT OUTER
JOIN`](/sql/select/join/#left-outer-join) on `orders_daily_totals`. The row
ordering on the `order_date` field is represented by an **equality condition**
using an [interval of `1
DAY`](/sql/types/interval/#valid-operations)). The
query includes the last row in the results, using `null` as the next row's
value.

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>

<tr>
<td><blue>Materialize SQL</blue> ✅</td>
<td class="copyableCode">

<div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="c1">-- Include the last row in the results --
</span></span></span><span class="line"><span class="cl"><span class="c1"></span><span class="k">SELECT</span> <span class="n">o1</span><span class="mf">.</span><span class="n">order_date</span><span class="p">,</span> <span class="n">o1</span><span class="mf">.</span><span class="n">daily_total</span><span class="p">,</span>
</span></span><span class="line"><span class="cl">    <span class="n">o2</span><span class="mf">.</span><span class="n">daily_total</span> <span class="k">as</span> <span class="n">next_daily_total</span>
</span></span><span class="line"><span class="cl"><span class="k">FROM</span> <span class="n">orders_daily_totals</span> <span class="n">o1</span>
</span></span><span class="line"><span class="cl"><span class="k">LEFT</span> <span class="k">JOIN</span> <span class="n">orders_daily_totals</span> <span class="n">o2</span>
</span></span><span class="line"><span class="cl"><span class="k">ON</span> <span class="n">o1</span><span class="mf">.</span><span class="n">order_date</span> <span class="o">=</span> <span class="n">o2</span><span class="mf">.</span><span class="n">order_date</span> <span class="o">-</span> <span class="nb">INTERVAL</span> <span class="s1">&#39;1&#39;</span> <span class="k">DAY</span>
</span></span><span class="line"><span class="cl"><span class="k">ORDER</span> <span class="k">BY</span> <span class="n">order_date</span><span class="p">;</span>
</span></span></code></pre></div>> **Important:** The idiomatic Materialize SQL applies only to those "lead over" queries whose
> ordering can be represented by some **equality condition**.

</td>
</tr>

<tr>
<td><red>Anti-pattern</red> ❌</td>
<td>

<red>Avoid the use of [`LEAD() OVER (ORDER BY ...)` window
function](/sql/functions/#lead) to access next row's value if the order by
field increases in a regular pattern.</red>

```nofmt
-- Anti-pattern. Includes the last row's value. --
SELECT order_date, daily_total,
    LEAD(daily_total) OVER (ORDER BY order_date) as next_daily_total
FROM orders_daily_totals;
```

</td>
</tr>

</tbody>
</table>

## See also

- [Lag over](/transform-data/idiomatic-materialize-sql/lag)
- [`INTERVAL`](/sql/types/interval/)
- [`LEFT JOIN/LEFT OUTER JOIN`](/sql/select/join/#left-outer-join)
- [`LEAD()`](/sql/functions/#lead)
- [Window functions](/sql/functions/#window-functions)

<!-- mz-docs page: transform-data/idiomatic-materialize-sql/mz_now -->

# mz_now() expressions
 `mz_now()` expressions can only take comparison operators. `mz_now()` expressions cannot be used with disjunctions `OR` in view definitions.
## Overview

In Materialize, [`mz_now()`](/sql/functions/now_and_mz_now/) function returns
Materialize's current virtual timestamp (i.e., returns
[`mz_timestamp`](/sql/types/mz_timestamp/)). The function can be used in
[temporal filters](/transform-data/patterns/temporal-filters/) to reduce the
working dataset.

`mz_now()` expression has the following form:

```mzsql
mz_now() <comparison_operator> <numeric_expr | timestamp_expr>
```

## Idiomatic Materialize SQL

### `mz_now()` expressions to calculate past or future timestamp

**Idiomatic Materialize SQL**: <code>mz_now()</code> must be used with one of the following comparison operators: <code>=</code>,
<code>&lt;</code>, <code>&lt;=</code>, <code>&gt;</code>, <code>&gt;=</code>, or an operator that desugars to them or to a conjunction
(<code>AND</code>) of them (for example, <code>BETWEEN...AND...</code>). That is, you cannot use
date/time operations directly on  <code>mz_now()</code> to calculate a timestamp in the
past or future. Instead, rewrite the query expression to move the operation to
the other side of the comparison.

#### Examples

| <blue>Materialize SQL</blue> ✅ | <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="k">WHERE</span> <span class="n">mz_now</span><span class="p">()</span> <span class="o">&gt;</span> <span class="n">order_date</span> <span class="o">+</span> <span class="nb">INTERVAL</span> <span class="s1">&#39;5min&#39;</span><span class="p">;</span> </span></span></code></pre></div> |
| <red>Anti-pattern</red> ❌ | <p><red>Not supported</red></p> <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="k">WHERE</span> <span class="n">mz_now</span><span class="p">()</span> <span class="o">-</span> <span class="nb">INTERVAL</span> <span class="s1">&#39;5min&#39;</span> <span class="o">&gt;</span> <span class="n">order_date</span><span class="p">;</span> </span></span></code></pre></div> |

### Disjunctions (`OR`)

When used in a materialized view definition, a view definition that is being
indexed (i.e., although you can create the view and perform ad-hoc query on
the view, you cannot create an index on that view), or a `SUBSCRIBE`
statement:

- `mz_now()` clauses can only be combined using an `AND`, and

- All top-level `WHERE` or `HAVING` conditions must be combined using an `AND`,
  even if the `mz_now()` clause is nested.

For example:

| mz_now() Compound Clause | Valid/Invalid |
| --- | --- |
| <span class="copyableCode"> <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="o">*</span> <span class="k">FROM</span> <span class="n">orders</span> </span></span><span class="line"><span class="cl"><span class="k">WHERE</span> <span class="n">status</span> <span class="o">=</span> <span class="s1">&#39;Shipped&#39;</span> </span></span><span class="line"><span class="cl"><span class="k">OR</span> <span class="n">order_date</span> <span class="o">+</span> <span class="nb">interval</span> <span class="s1">&#39;1&#39;</span> <span class="k">days</span> <span class="o">&lt;=</span> <span class="n">mz_now</span><span class="p">()</span> </span></span><span class="line"><span class="cl"><span class="p">;</span> </span></span></code></pre></div></span>  | <p>✅ <strong>Valid</strong></p> <p>Ad-hoc queries do not have the same restrictions.</p>  |
| <span class="copyableCode"> <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="k">CREATE</span> <span class="k">MATERIALIZED</span> <span class="k">VIEW</span> <span class="n">forecast_completed_orders</span> <span class="k">AS</span> </span></span><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="o">*</span> <span class="k">FROM</span> <span class="n">orders</span> </span></span><span class="line"><span class="cl"><span class="k">WHERE</span> <span class="n">order_date</span> <span class="o">+</span> <span class="nb">interval</span> <span class="s1">&#39;3&#39;</span> <span class="k">days</span> <span class="o">&gt;</span> <span class="n">mz_now</span><span class="p">()</span> </span></span><span class="line"><span class="cl"><span class="k">AND</span> <span class="n">order_date</span> <span class="o">+</span> <span class="nb">interval</span> <span class="s1">&#39;1&#39;</span> <span class="k">days</span> <span class="o">&lt;</span> <span class="n">mz_now</span><span class="p">()</span> </span></span><span class="line"><span class="cl"><span class="p">;</span> </span></span></code></pre></div></span>  | ✅ <strong>Valid</strong> |
| <span class="copyableCode"> <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="k">CREATE</span> <span class="k">MATERIALIZED</span> <span class="k">VIEW</span> <span class="n">forecast_completed_orders</span> <span class="k">AS</span> </span></span><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="o">*</span> <span class="k">FROM</span> <span class="n">orders</span> </span></span><span class="line"><span class="cl"><span class="k">WHERE</span> <span class="p">(</span><span class="n">status</span> <span class="o">=</span> <span class="s1">&#39;Complete&#39;</span> <span class="k">OR</span> <span class="n">status</span> <span class="o">=</span> <span class="s1">&#39;Shipped&#39;</span><span class="p">)</span> </span></span><span class="line"><span class="cl"><span class="k">AND</span> <span class="n">order_date</span> <span class="o">+</span> <span class="nb">interval</span> <span class="s1">&#39;1&#39;</span> <span class="k">days</span> <span class="o">&lt;=</span> <span class="n">mz_now</span><span class="p">()</span> </span></span><span class="line"><span class="cl"><span class="p">;</span> </span></span></code></pre></div></span>  | ✅ <strong>Valid</strong> |
| <div style="background-color: var(--code-block)"> <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="k">CREATE</span> <span class="k">MATERIALIZED</span> <span class="k">VIEW</span> <span class="n">forecast_completed_orders</span> <span class="k">AS</span> </span></span><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="o">*</span> <span class="k">FROM</span> <span class="n">orders</span> </span></span><span class="line"><span class="cl"><span class="k">WHERE</span> <span class="n">status</span> <span class="o">=</span> <span class="s1">&#39;Shipped&#39;</span> </span></span><span class="line"><span class="cl"><span class="k">OR</span> <span class="n">order_date</span> <span class="o">+</span> <span class="nb">interval</span> <span class="s1">&#39;1&#39;</span> <span class="k">days</span> <span class="o">&lt;=</span> <span class="n">mz_now</span><span class="p">()</span> </span></span><span class="line"><span class="cl"><span class="p">;</span> </span></span></code></pre></div></div>  | <p>❌ <strong>Invalid</strong></p> <p>In materialized view definitions, <code>mz_now()</code> clause can only be combined using an <code>AND</code>.</p>  |
| <div style="background-color: var(--code-block)"> <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="k">CREATE</span> <span class="k">MATERIALIZED</span> <span class="k">VIEW</span> <span class="n">forecast_completed_orders</span> <span class="k">AS</span> </span></span><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="o">*</span> <span class="k">FROM</span> <span class="n">orders</span> </span></span><span class="line"><span class="cl"><span class="k">WHERE</span> <span class="n">status</span> <span class="o">=</span> <span class="s1">&#39;Complete&#39;</span> </span></span><span class="line"><span class="cl"><span class="k">OR</span> <span class="p">(</span><span class="n">status</span> <span class="o">=</span> <span class="s1">&#39;Shipped&#39;</span> <span class="k">AND</span> <span class="n">order_date</span> <span class="o">+</span> <span class="nb">interval</span> <span class="s1">&#39;1&#39;</span> <span class="k">days</span> <span class="o">&lt;=</span> <span class="n">mz_now</span><span class="p">())</span> </span></span></code></pre></div></div>  | <p>❌ <strong>Invalid</strong></p> <p>In materialized view definitions with <code>mz_now()</code> clauses, top-level conditions must be combined using an <code>AND</code>.</p>  |
| <div style="background-color: var(--code-block)"> <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="k">CREATE</span> <span class="k">VIEW</span> <span class="n">forecast_completed_orders</span> <span class="k">AS</span> </span></span><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="o">*</span> <span class="k">FROM</span> <span class="n">orders</span> </span></span><span class="line"><span class="cl"><span class="k">WHERE</span> <span class="n">status</span> <span class="o">=</span> <span class="s1">&#39;Complete&#39;</span> </span></span><span class="line"><span class="cl"><span class="k">OR</span> <span class="p">(</span><span class="n">status</span> <span class="o">=</span> <span class="s1">&#39;Shipped&#39;</span> <span class="k">AND</span> <span class="n">order_date</span> <span class="o">+</span> <span class="nb">interval</span> <span class="s1">&#39;1&#39;</span> <span class="k">days</span> <span class="o">&lt;=</span> <span class="n">mz_now</span><span class="p">())</span> </span></span><span class="line"><span class="cl"><span class="p">;</span> </span></span><span class="line"><span class="cl"> </span></span><span class="line"><span class="cl"><span class="k">CREATE</span> <span class="k">INDEX</span> <span class="n">idx_forecast_completed_orders</span> <span class="k">ON</span> <span class="n">forecast_completed_orders</span> </span></span><span class="line"><span class="cl"><span class="p">(</span><span class="n">order_date</span><span class="p">);</span> <span class="c1">-- Unsupported because of the `mz_now()` clause </span></span></span></code></pre></div></div>  | <p>❌ <strong>Invalid</strong></p> <p>To index a view whose definitions includes <code>mz_now()</code> clauses, top-level conditions must be combined using an <code>AND</code> in the view definition.</p>  |

**Idiomatic Materialize SQL**: When `mz_now()` is included in a materialized
view definition, a view definition that is being indexed, or a `SUBSCRIBE`
statement, instead of using disjunctions (`OR`) when using `mz_now()`, rewrite
the query to use `UNION ALL` or `UNION` instead, deduplicating as necessary:

- In some cases, you may need to modify the conditions to deduplicate results
  when using `UNION ALL`. For example, you might add the negation of one input's
  condition to the other as a conjunction.

- In some cases, using `UNION` instead of `UNION ALL` may suffice if the inputs
  do not contain other duplicates that need to be retained.

#### Examples

| <blue>Materialize SQL</blue> ✅ | <p><strong>Rewrite as UNION ALL with possible duplicates</strong></p> <span class="copyableCode"> <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="k">CREATE</span> <span class="k">MATERIALIZED</span> <span class="k">VIEW</span> <span class="n">forecast_completed_orders_duplicates_possible</span> <span class="k">AS</span> </span></span><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="n">item</span><span class="p">,</span> <span class="n">quantity</span><span class="p">,</span> <span class="n">status</span> <span class="k">from</span> <span class="n">orders</span> </span></span><span class="line"><span class="cl"><span class="k">WHERE</span> <span class="n">status</span> <span class="o">=</span> <span class="s1">&#39;Shipped&#39;</span> </span></span><span class="line"><span class="cl"><span class="k">UNION</span> <span class="k">ALL</span> </span></span><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="n">item</span><span class="p">,</span> <span class="n">quantity</span><span class="p">,</span> <span class="n">status</span> <span class="k">from</span> <span class="n">orders</span> </span></span><span class="line"><span class="cl"><span class="k">WHERE</span> <span class="n">order_date</span> <span class="o">+</span> <span class="nb">interval</span> <span class="s1">&#39;30&#39;</span> <span class="k">minutes</span> <span class="o">&gt;=</span> <span class="n">mz_now</span><span class="p">()</span> </span></span><span class="line"><span class="cl"><span class="p">;</span> </span></span></code></pre></div></span> <p><strong>Rewrite as UNION ALL that avoids duplicates across queries</strong></p> <span class="copyableCode"> <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="k">CREATE</span> <span class="k">MATERIALIZED</span> <span class="k">VIEW</span> <span class="n">forecast_completed_orders_deduplicated_union_all</span> <span class="k">AS</span> </span></span><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="n">item</span><span class="p">,</span> <span class="n">quantity</span><span class="p">,</span> <span class="n">status</span> <span class="k">from</span> <span class="n">orders</span> </span></span><span class="line"><span class="cl"><span class="k">WHERE</span> <span class="n">status</span> <span class="o">=</span> <span class="s1">&#39;Shipped&#39;</span> </span></span><span class="line"><span class="cl"><span class="k">UNION</span> <span class="k">ALL</span> </span></span><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="n">item</span><span class="p">,</span> <span class="n">quantity</span><span class="p">,</span> <span class="n">status</span> <span class="k">from</span> <span class="n">orders</span> </span></span><span class="line"><span class="cl"><span class="k">WHERE</span> <span class="n">order_date</span> <span class="o">+</span> <span class="nb">interval</span> <span class="s1">&#39;30&#39;</span> <span class="k">minutes</span> <span class="o">&gt;=</span> <span class="n">mz_now</span><span class="p">()</span> </span></span><span class="line"><span class="cl"><span class="k">AND</span> <span class="n">status</span> <span class="o">!=</span> <span class="s1">&#39;Shipped&#39;</span> <span class="c1">-- Deduplicate by excluding those with status &#39;Shipped&#39; </span></span></span><span class="line"><span class="cl"><span class="c1"></span><span class="p">;</span> </span></span></code></pre></div></span> <p><strong>Rewrite as UNION to deduplicate any and all duplicated results</strong></p> <span class="copyableCode"> <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="k">CREATE</span> <span class="k">MATERIALIZED</span> <span class="k">VIEW</span> <span class="n">forecast_completed_orders_deduplicated_results</span> <span class="k">AS</span> </span></span><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="n">item</span><span class="p">,</span> <span class="n">quantity</span><span class="p">,</span> <span class="n">status</span> <span class="k">from</span> <span class="n">orders</span> </span></span><span class="line"><span class="cl"><span class="k">WHERE</span> <span class="n">status</span> <span class="o">=</span> <span class="s1">&#39;Shipped&#39;</span> </span></span><span class="line"><span class="cl"><span class="k">UNION</span> </span></span><span class="line"><span class="cl"><span class="k">SELECT</span> <span class="n">item</span><span class="p">,</span> <span class="n">quantity</span><span class="p">,</span> <span class="n">status</span> <span class="k">from</span> <span class="n">orders</span> </span></span><span class="line"><span class="cl"><span class="k">WHERE</span> <span class="n">order_date</span> <span class="o">+</span> <span class="nb">interval</span> <span class="s1">&#39;30&#39;</span> <span class="k">minutes</span> <span class="o">&gt;=</span> <span class="n">mz_now</span><span class="p">()</span> </span></span><span class="line"><span class="cl"><span class="p">;</span> </span></span></code></pre></div></span>  |
| <red>Anti-pattern</red> ❌ | <p><red>Not supported</red></p> <div style="background-color: var(--code-block)"> <pre tabindex="0"><code class="language-none" data-lang="none">-- Unsupported CREATE MATERIALIZED VIEW forecast_completed_orders_unsupported AS SELECT item, quantity, status from orders WHERE status = &#39;Shipped&#39; OR order_date + interval &#39;30&#39; minutes &gt;= mz_now(); </code></pre></div> |


<!-- mz-docs page: transform-data/idiomatic-materialize-sql/not-in -->

# `NOT IN` subquery
Use idiomatic Materialize SQL for `NOT IN (subquery)` predicates to avoid a cross join in the dataflow plan.
## Overview

The `fieldX NOT IN (<subquery>)` predicate returns `true` if `fieldX` does not
equal any value returned by the subquery. For predicates where `fieldX` or the
`<subquery>` can contain `NULL` values, Materialize provides idiomatic SQL
alternatives.

### Materialize and `NOT IN (<subquery>)`

When evaluating a `WHERE fieldX NOT IN (<subquery>)` predicate involving
possible `NULL` values for `fieldX` or `<subquery>`, Materialize performs a
cross join between the outer relation and the subquery to preserve SQL `NULL`
semantics, which can significantly increase memory usage. If possible, rewrite
the query to avoid the cross join.

## Idiomatic Materialize SQL

For `fieldX NOT IN (<subquery>)` predicates involving possible `NULL` values,
the following rewrites are available:

> **Note:** Neither rewrite is strictly equivalent to `NOT IN (<subquery>)`.
> Both rewrites avoid the `NULL` propagation semantics of `NOT IN`; that is, they
> treat subquery `NULL` values as non-matches rather than allowing them to
> invalidate the comparison. In addition, the `NOT EXISTS` rewrite retains outer
> rows whose value is `NULL`, whereas both `NOT IN` and the filter-`NULL`s rewrite
> exclude them.

- Rewrite to [`NOT EXISTS`](/sql/functions/#not-exists) with a correlated
  subquery.
- Retain `NOT IN`, but filter out `NULL` values from both the outer field and
  the subquery.

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><blue>Materialize SQL</blue></td>
<td class="copyableCode">

**Rewrite to `NOT EXISTS` with a correlated subquery.**

```mzsql
SELECT t1.*
FROM t1
WHERE NOT EXISTS (SELECT 1 FROM t2 WHERE t2.a = t1.a)
;
```

**Filter out `NULL`s on both sides of the `NOT IN`.**

```mzsql
SELECT t1.*
FROM t1
WHERE t1.a IS NOT NULL
  AND t1.a NOT IN (SELECT t2.a FROM t2 WHERE t2.a IS NOT NULL)
;
```

</td>
</tr>
<tr>
<td><red>Anti-pattern</red> ❌</td>
<td>

<red>Avoid `NOT IN (<subquery>)` predicates, which force a cross join
between the outer relation and the subquery.</red>

```nofmt
-- Anti-pattern. Avoid. --
SELECT t1.*
FROM t1
WHERE t1.a NOT IN (SELECT t2.a FROM t2) -- Anti-pattern. Avoid.
;
```

</td>
</tr>

</tbody>
</table>

If the subquery uses [`UNNEST()`](/sql/functions/#unnest) on a column whose
value depends on the outer row:
- Factor the `UNNEST()` into an uncorrelated [Common Table Expression
  (CTE)](/sql/select/#common-table-expressions-ctes) first.
- Then apply the rewrite against the CTE. See the [example
  below](#find-items-not-currently-on-sale).

## Examples

> **Note:** The example data can be found in the
> [Appendix](/transform-data/idiomatic-materialize-sql/appendix/example-orders).

### Find items not currently on sale

Using idiomatic Materialize SQL, the following examples find items in the
`items` table whose `item` value (declared `NOT NULL`) does not appear in any of
this week's sales arrays in `sales_items`, a nullable `text[]`. The subquery
uses [`UNNEST()`](/sql/functions/#unnest) to expand each week's `items` array
into individual values for comparison.

If the subquery uses [`UNNEST()`](/sql/functions/#unnest) on a column whose
value depends on the outer row:

- First, factor the `UNNEST()` into an uncorrelated [Common Table Expression
  (CTE)](/sql/select/#common-table-expressions-ctes).
- Then, apply the rewrite against the CTE.

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>

<tr>
<td><blue>Materialize SQL</blue> ✅</td>
<td class="copyableCode">

Because the subquery uses [`UNNEST()`](/sql/functions/#unnest) on a column
of the outer-correlated row, factor the `UNNEST()` into an uncorrelated
[Common Table Expression
(CTE)](/sql/select/#common-table-expressions-ctes) first.

***Rewrite to `NOT EXISTS` with a CTE for the `UNNEST()`***

```mzsql
WITH this_weeks_sales AS (
  SELECT unnest(items) AS sale_item
  FROM sales_items
  WHERE week_of = date_trunc('week', current_timestamp)
)
SELECT i.item, i.price
FROM items i
WHERE NOT EXISTS (
  SELECT 1 FROM this_weeks_sales s WHERE s.sale_item = i.item
)
ORDER BY i.item
;
```

***Filter out `NULL`s with a CTE for the `UNNEST()`***

```mzsql
WITH this_weeks_sales AS (
  SELECT unnest(items) AS sale_item
  FROM sales_items
  WHERE week_of = date_trunc('week', current_timestamp)
)
SELECT i.item, i.price
FROM items i
WHERE i.item IS NOT NULL
  AND i.item NOT IN (
    SELECT sale_item FROM this_weeks_sales WHERE sale_item IS NOT NULL
  )
ORDER BY i.item
;
```

</td>
</tr>

<tr>
<td><red>Anti-pattern</red> ❌</td>
<td>

<red>Avoid `NOT IN (<subquery>)`, which forces a cross join.</red>

```nofmt
-- Anti-pattern. Avoid. --
SELECT i.item, i.price
FROM items i
WHERE i.item NOT IN (
  SELECT unnest(items) FROM sales_items
  WHERE week_of = date_trunc('week', current_timestamp)
)
ORDER BY i.item
;
```

</td>
</tr>

</tbody>
</table>

## See also

- [`NOT EXISTS`](/sql/functions/#not-exists)

- [Idiomatic Materialize SQL
  Chart](/transform-data/idiomatic-materialize-sql/appendix/idiomatic-sql-chart/)

