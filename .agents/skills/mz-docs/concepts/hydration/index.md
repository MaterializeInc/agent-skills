# Hydration
Learn about hydration in Materialize: reconstructing an object's in-memory state by reading from the storage layer.
Hydration is the reconstruction of an object's in-memory state by reading
from Materialize's storage layer and existing indexes; hydration does not
read from the upstream system.

## When hydration occurs

Depending on the object, hydration (or rehydration) occurs after:
- **An object is created**, triggering its hydration.
  * This includes dropping and recreating objects to force re-planning. For
    example, after dropping an index, you can drop and recreate its
    dependent objects to force them to re-plan. The recreated objects then
    hydrate like any newly created object.
- **A cluster replica restarts**, such as during Materialize Cloud's
  routine maintenance or after an out-of-memory event. Hydration can be
  memory-intensive and can itself trigger the out-of-memory event. The
  replica then restarts and rehydrates again, potentially creating a
  restart-and-rehydrate loop if the replica is undersized.
- **A cluster resize**. A cluster resize provisions new replicas at the
  target size and hydrates them before retiring the old ones. The cluster
  keeps serving throughout.
- **Adding a replica to a cluster**, which hydrates the new replica only.
  Existing replicas are unaffected and keep serving.

For when hydration occurs for each object type, see [Objects and
hydration](#objects-and-hydration).

## Objects and hydration

Hydration is per cluster replica: when a hydration trigger occurs, the
objects on the affected replicas hydrate. When a replica restarts, every
object on it re-hydrates. A resize or an added replica hydrates only the
new replicas.

The objects on the affected replicas hydrate as described in the following
table.

| Object | Hydration behavior |
| --- | --- |
| Materialized views | - **When**: Hydrates on creation and on every replica (re)start or cluster resize. - **What**: Rebuilds the dataflow's operator state: the arrangements that joins, aggregations, and similar operators keep to update results incrementally. Note: A materialized view's result lives in durable storage, so it rebuilds only this maintenance state, not the result. - **Memory Use**: Scales with the view's definition, which it holds at steady state, plus a transient output buffer up to twice the output size: the current output plus a read-back of the previously persisted output. On first creation, since there is no previous output, the buffer is a single output size.  |
| Indexes | - **When**: Hydrates on creation and on every replica (re)start or cluster resize. - **What**: Rebuilds the arranged (indexed) data it keeps in memory to serve reads, plus any operator arrangements its dataflow maintains (for joins, aggregations, and similar). - **Memory Use**: Its memory is proportional to the indexed data plus those arrangements, and is held for as long as the index exists.  |
| Kafka <strong>upsert</strong> sources and associated read-only tables/subsources | - **When**: On replica (re)start or cluster resize. These sources do not hydrate on creation; instead, on creation, their indexes are built as part of [snapshotting](/concepts/snapshotting/). - **What**: Rebuilds the table's or subsource's internal upsert index from storage. - **Memory Use**: The index holds the latest value per key, so its memory scales with the source's key space. On standard cluster sizes it can spill to disk when the key space exceeds memory.  |
| Append-only Kafka sources and CDC database sources (PostgreSQL, MySQL, SQL Server), and their read-only tables/subsources | - **When**: On replica (re)start or cluster resize, marked hydrated as soon as the dataflow starts. - **What**: Effectively nothing. These sources keep no internal index to rebuild and resume from their persisted position, so hydration is a no-op. - **Memory Use**: Negligible, since there is no index to hold.  |
| Webhook sources | Not applicable. A webhook source is not maintained by a dataflow. It receives data pushed over HTTP and writes the data directly to storage, so it does not hydrate.  |
| Sinks | - **When**: If created `WITH (SNAPSHOT = true)` (the default), hydrates:   - On creation, when the sink first emits its input snapshot.   - On a replica (re)start, but only if the sink restarted before recording     any progress: it then re-reads the whole input snapshot, and any data     already written to the external system is discarded, but the memory     cost still occurs. An established sink resumes from its recorded     progress without re-reading the snapshot.  - **What**: Loads a full copy of its input snapshot into the arrangement that feeds the sink before it can emit. - **Memory Use**: Peaks at roughly a full copy of the input snapshot, then decreases as the snapshot is written out. Negligible on a restart of an established sink. At steady state, a sink retains little in memory.  |
| Subscriptions | - **When**: On creation and, while it remains active, on every replica (re)start: the dataflow is re-installed on the (re)started replica and the subscription resumes. A subscription that targets a specific replica instead ends with an error when that replica restarts. A subscription ends with its session and is not reported in `mz_hydration_statuses`. - **What**: Rebuilds the dataflow when it starts. - **Memory Use**: Scales with the dataflow, held while the subscription runs.  |

## Hydration strategies

Hydration primarily impacts memory usage, and its speed scales with cluster
size. Some hydration-related strategies you may want to consider:

- Use a dedicated cluster for [sources](/concepts/sources/).

- In addition, use a dedicated cluster for upsert sources; i.e., do not
  co-locate with append-only Kafka sources or CDC database sources.

  - Keeping append-only Kafka sources and CDC database sources (PostgreSQL,
    MySQL, and SQL Server sources) on a separate cluster isolates ingestion from
    possible OOM loops caused by memory-heavy objects such as Kafka upsert
    sources.

  - Note: PostgreSQL, MySQL, and SQL Server sources run on a single
    replica, the oldest, and remain there until that replica is removed. As
    such, the use of a burst replica (through `AUTO SCALING STRATEGY (ON
    HYDRATION)`) has no impact on these single-replica sources.

- Add an [`AUTO SCALING STRATEGY (ON HYDRATION)`](/sql/alter-cluster/) to your
  cluster with memory-heavy objects. With this strategy, Materialize
  automatically provisions an extra, larger replica (a burst replica) while the
  cluster has unhydrated objects, then removes it once a steady-size replica
  catches up. You pay for the burst replica while it is provisioned, but not at
  steady state.

  - If a steady-size replica runs out of memory during hydration, resize the
    cluster. During the resize, the cluster continues to serve from the burst
    replica.

- Distribute materialized views and indexes across multiple clusters. Each
  cluster's replicas hydrate their objects independently, which distributes the
  memory required for hydration, lets objects on different clusters hydrate in
  parallel, and limits how much must re-hydrate when any one replica restarts.

- When changing a materialized view or index, or forcing dependents to re-plan
  (for example, after dropping an index and recreating the dependents), build
  the new version to the side to avoid downtime:

  - A [blue/green deployment](/manage/dbt/blue-green-deployments/) hydrates the
    new version alongside the old and cuts over when hydrated, with no serving
    gap. Note that blue/green requires sources and sinks to live on dedicated
    clusters that are excluded from the swap. For more information, see
    [blue/green deployment](/manage/dbt/blue-green-deployments/).

  - For a single materialized view, creating and hydrating a [replacement
    materialized view (public preview) and replacing the existing view in
    place](/transform-data/updating-materialized-views/replace-materialized-view/)
    may be simpler, but briefly reduces freshness. The replacement materialized
    view can be either on the same or different cluster.

> **Note:** The burst-replica and blue/green strategies run extra replicas alongside the
> existing ones, as do a resize or a zero-downtime upgrade. During the overlap,
> the cluster temporarily uses additional resources. Account for the additional
> cost and, on self-managed deployments, the additional capacity required.

In addition, consider the following strategies. These strategies trade off peak
hydration memory against added operational complexity, extra objects, and
potentially longer total hydration time. You can use them when peak hydration
memory is the bottleneck rather than as a default modeling pattern.

- <a name="index-order"></a>If multiple objects in the **same** cluster consume
  the same view, add an [index](/concepts/indexes/) to that view **before**
  creating the consumers. Consumers in that cluster can reuse the indexed
  arrangement instead of each building equivalent in-memory state, which can
  reduce both memory usage during hydration and steady-state memory. Note:
  - Index reuse is limited to the cluster the index is on, and the index must
    exist **before** its consumers are created for the optimizer to reuse it.
  - For a view with only one consumer, an index generally adds memory instead of
    saving it.

- For a very large materialized view, consider splitting it into several smaller
  materialized views, for example by a partition key such as customer, region,
  or date range. Smaller materialized views can hydrate as separate dataflows,
  which can bound peak memory compared with hydrating one very large
  materialized view.
  - This helps most when a cluster runs only a few large materialized views,
    where a single view's hydration spike can dictate the cluster size. A
    cluster with many materialized views already hydrates them as separate
    dataflows and gets this benefit naturally.
  - A re-plan or replacement of one split view affects only that portion of
    the data. A replica restart still re-hydrates all views on the replica,
    though in smaller units.
  - If the split views share expensive computation, put that computation in a
    [common indexed view first](#index-order), creating the index **before**
    creating the split views. Otherwise, each split view may rebuild its own
    copy of the shared work, increasing total memory.
  - Queries must target or combine the split views.

## Related pages

- [Snapshotting](/concepts/snapshotting/)
- [Clusters](/concepts/clusters/)
- [Sources](/concepts/sources/)
- [Troubleshooting](/transform-data/troubleshooting/#hydrating-objects)
- [Updating materialized views](/transform-data/updating-materialized-views/)
