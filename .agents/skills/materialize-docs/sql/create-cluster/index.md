# CREATE CLUSTER
`CREATE CLUSTER` creates a new cluster.
`CREATE CLUSTER` creates a new [cluster](/concepts/clusters/).

## Syntax

```mzsql
CREATE CLUSTER [IF NOT EXISTS] <cluster_name> (
    SIZE = <text>
    [, REPLICATION FACTOR = <int>]
    [, MANAGED = <bool>]
    [, AUTO SCALING STRATEGY = (
        ON HYDRATION (
            HYDRATION SIZE = <text>
            [, LINGER DURATION = <interval>]
        )
    )]
    [, EXPERIMENTAL ARRANGEMENT COMPRESSION = <bool>]
);

```

| Syntax element | Description |
| --- | --- |
| **IF NOT EXISTS** | *Optional.* If specified, do not throw an error if a cluster with the same name already exists. Instead, issue a notice and skip the cluster creation. Note that the existing cluster is left untouched, its configuration is not updated to match the statement.  |
| `<cluster_name>` | A name for the cluster.  |
| `SIZE` | The size of the resource allocations for the cluster.  For valid size values, see [Available sizes](#available-sizes).  |
| `REPLICATION FACTOR` | Optional. The number of replicas to provision for the cluster. See [Replication factor](#replication-factor) for details.  Default: `1`  |
| `MANAGED` | Optional. Whether to automatically manage the cluster's replicas based on the configured size and replication factor.  <a name="unmanaged-clusters"></a>  Specify `FALSE` to create an **unmanaged** cluster. With unmanaged clusters, you need to manually manage the cluster's replicas using the the [`CREATE CLUSTER REPLICA`](/sql/create-cluster-replica) and [`DROP CLUSTER REPLICA`](/sql/drop-cluster-replica) commands. When creating an unmanaged cluster, you must specify the `REPLICAS` option as well.  {{< tip >}} When getting started with Materialize, we recommend starting with managed clusters. {{</ tip >}}  Default: `TRUE`  |
| `AUTO SCALING STRATEGY` | Optional. While the cluster has un-hydrated objects, provisions an extra burst replica at a larger size to speed up hydration. The steady-size replicas will continue to run, and hydrate in parallel. Once a steady-size replica hydrates and catches up with the burst, the burst replica is retired. This helps optimize costs while speeding up hydration. Only available on managed clusters.  Specify a single `ON HYDRATION` sub-policy, which supports the following options:  \| Option \| Description \| \|--------\|-------------\| \| `HYDRATION SIZE` \| The size of the burst replica provisioned while the cluster has un-hydrated objects. Must differ from the cluster's steady `SIZE`. Choose a larger size to speed up hydration. For valid size values, see [Available sizes](#available-sizes). \| \| `LINGER DURATION` \| Optional. How long the burst replica lingers after a steady-size replica catches up, before it is removed. Default: `0s`. \|  |
| `EXPERIMENTAL ARRANGEMENT COMPRESSION` | {{< warn-if-unreleased-inline "v26.38" >}}  Optional. Whether to enable [dictionary compression](#dictionary-compression) for the arrangements maintained by the cluster's replicas. Compression reduces the memory those arrangements use, at the cost of CPU, and does not benefit every workload. Only available on managed clusters.  Default: `FALSE`  |

## Details

### Initial state

Each Materialize region initially contains a [pre-installed cluster](/sql/show-clusters/#pre-installed-clusters)
named `quickstart` with a size of `25cc` and a replication factor of `1`. You
can drop or alter this cluster to suit your needs.

### Choosing a cluster

When performing an operation that requires a cluster, you must specify which
cluster you want to use. Not explicitly naming a cluster uses your session's
active cluster.

To show your session's active cluster, use the [`SHOW`](/sql/show) command:

```mzsql
SHOW cluster;
```

To switch your session's active cluster, use the [`SET`](/sql/set) command:

```mzsql
SET cluster = other_cluster;
```

### Resource isolation

Clusters provide **resource isolation.** Each cluster provisions a dedicated
pool of CPU, memory, and, optionally, scratch disk space.

All workloads on a given cluster will compete for access to these compute
resources. However, workloads on different clusters are strictly isolated from
one another. A given workload has access only to the CPU, memory, and scratch
disk of the cluster that it is running on.

Clusters are commonly used to isolate different classes of workloads. For
example, you could place your development workloads in a cluster named
`dev` and your production workloads in a cluster named `prod`.

<a name="legacy-sizes"></a>

### Available sizes

The `SIZE` option determines the amount of compute resources available to the
cluster.

**cc Clusters:**

Materialize offers the following cc cluster sizes:

* `25cc`
* `50cc`
* `100cc`
* `200cc`
* `300cc`
* `400cc`
* `600cc`
* `800cc`
* `1200cc`
* `1600cc`
* `3200cc`
* `6400cc`
* `128C`
* `256C`
* `512C`

The resource allocations are proportional to the number in the size name. For
example, a cluster of size `600cc` has 2x as much CPU, memory, and disk as a
cluster of size `300cc`, and 1.5x as much CPU, memory, and disk as a cluster of
size `400cc`. To determine the specific resource allocations for a size,
query the [`mz_cluster_replica_sizes`](/reference/system-catalog/mz_catalog/#mz_cluster_replica_sizes) table.

> **Warning:** The values in the `mz_cluster_replica_sizes` table may change at any
> time. You should not rely on them for any kind of capacity planning.

Clusters of larger sizes can process data faster and handle larger data volumes.

**M.1 Clusters:**

> **Note:** M.1 sizes provide access to additional disk capacity compared to
> equivalently-priced cc sizes, which can be beneficial for disk-intensive
> workloads. However, cc sizes offer better compute performance per credit for
> most workloads. We recommend using cc sizes unless your workload specifically
> requires the additional disk capacity that M.1 sizes provide.

> **Note:** The values set forth in the table are solely for illustrative purposes.
> Materialize reserves the right to change the capacity at any time. As such, you
> acknowledge and agree that those values in this table may change at any time,
> and you should not rely on these values for any capacity planning.

| Cluster size | Compute Credits/Hour | Total Capacity | Notes |
| --- | --- | --- | --- |
| <strong>M.1-nano</strong> | 0.75 | 26 GiB |  |
| <strong>M.1-micro</strong> | 1.5 | 53 GiB |  |
| <strong>M.1-xsmall</strong> | 3 | 106 GiB |  |
| <strong>M.1-small</strong> | 6 | 212 GiB |  |
| <strong>M.1-medium</strong> | 9 | 318 GiB |  |
| <strong>M.1-large</strong> | 12 | 424 GiB |  |
| <strong>M.1-1.5xlarge</strong> | 18 | 636 GiB |  |
| <strong>M.1-2xlarge</strong> | 24 | 849 GiB |  |
| <strong>M.1-3xlarge</strong> | 36 | 1273 GiB |  |
| <strong>M.1-4xlarge</strong> | 48 | 1645 GiB |  |
| <strong>M.1-8xlarge</strong> | 96 | 3290 GiB |  |
| <strong>M.1-16xlarge</strong> | 192 | 6580 GiB | Available upon request |
| <strong>M.1-32xlarge</strong> | 384 | 13160 GiB | Available upon request |
| <strong>M.1-64xlarge</strong> | 768 | 26320 GiB | Available upon request |
| <strong>M.1-128xlarge</strong> | 1536 | 52640 GiB | Available upon request |

**Legacy t-shirt Clusters:**

Materialize also offers some legacy t-shirt cluster sizes for upsert sources.

> **Tip:** In most cases, you **should not** use legacy t-shirt sizes. We recommend using
> cc sizes for all new clusters, and recommend migrating existing legacy-sized
> clusters to cc sizes.
> The legacy size information is provided for completeness.

<blockquote>
<p><strong>Warning:</strong> Materialize regions that were enabled after 15 April 2024 do not have access
to legacy sizes.</p>
</blockquote>

When legacy sizes are enabled for a region, the following sizes are available:

* `3xsmall`
* `2xsmall`
* `xsmall`
* `small`
* `medium`
* `large`
* `xlarge`
* `2xlarge`
* `3xlarge`
* `4xlarge`
* `5xlarge`
* `6xlarge`

See also:

- [cc to M.1 size mapping](/sql/m1-cc-mapping/).

- [Materialize service consumption
  table](https://materialize.com/pdfs/pricing.pdf).

- [Blog:Scaling Beyond Memory: How Materialize Uses Swap for Larger
  Workloads](https://materialize.com/blog/scaling-beyond-memory/).

#### Cluster resizing

You can change the size of a cluster to respond to changes in your workload
using [`ALTER CLUSTER`](/sql/alter-cluster).

As of **v26.35**, resizing is graceful and incurs **no downtime**: Materialize
provisions new replicas at the target size, waits for them to hydrate, then
retires the old ones. See [Monitoring a
resize](/sql/alter-cluster/#monitoring-a-resize).

In versions before v26.35, resizing could incur downtime, and zero-downtime
resizing required the `WAIT UNTIL READY` option.

See the reference documentation for [`ALTER
CLUSTER`](/sql/alter-cluster/#resizing) for more details
on cluster resizing.

### Autoscaling

> **Public Preview:** This feature is in public preview.

When you create an index, materialized view, or Kafka upsert source, or when a
cluster restarts, the cluster must
[hydrate](/concepts/hydration/) the affected
objects before they can serve results. Hydration reads the input data
and rebuilds in-memory state, and its speed scales with the cluster
[size](#available-sizes).

The `AUTO SCALING STRATEGY (ON HYDRATION)` option lets a cluster **automatically
provision an extra burst replica at the configured `HYDRATION SIZE` while it has
un-hydrated objects**. This speeds up hydration without manually scaling the
cluster up before hydration and back down afterward. The steady-size replicas
continue hydrating in parallel, and once one of them catches up with the burst,
the burst replica lingers for the `LINGER DURATION` and is then removed. The
burst replica is an ordinary cluster replica, billed only for the time it is
provisioned. See [Usage & billing](/administration/billing/) for details.

`AUTO SCALING STRATEGY (ON HYDRATION)` is particularly useful for [blue/green
deployments](/manage/blue-green/), where a new cluster must hydrate before the
cutover. It is only available on **managed clusters**, and cannot be combined
with a cluster `SCHEDULE` other than the default `MANUAL`.

For example, the following cluster can provision a burst replica of size `800cc`:

```mzsql
CREATE CLUSTER fast_start (
    SIZE = '100cc',
    AUTO SCALING STRATEGY = (
        ON HYDRATION (
            HYDRATION SIZE = '800cc',
            LINGER DURATION = '15s'
        )
    )
);
```

You can specify the following options:

Option | Description
-------|------------
`HYDRATION SIZE` | The [size](#available-sizes) of the burst replica provisioned while the cluster has un-hydrated objects. Must differ from the cluster's steady `SIZE`. Choose a larger size to speed up hydration.
`LINGER DURATION` | Optional. How long the burst replica lingers after a steady-size replica catches up, before it is removed. Default: `0s`.

Provisioning the burst replica requires enough compute capacity to run it. In
Materialize Self-Managed, this means your Kubernetes cluster must have enough
spare resources (for example, available nodes) to schedule the burst replica.

The burst is best-effort and never blocks the cluster: if the burst replica
cannot be provisioned, the steady-size replicas still come up and hydrate as
usual, as long as there are enough resources for them.

To remove the autoscaling strategy from a cluster, use `ALTER CLUSTER ... RESET
(AUTO SCALING STRATEGY)` or set an empty strategy with `AUTO SCALING STRATEGY =
()`.

You can inspect the configured strategy and any in-flight burst in the
[`mz_internal.mz_cluster_auto_scaling_strategies`](/reference/system-catalog/mz_internal/#mz_cluster_auto_scaling_strategies)
catalog view.

### Dictionary compression

> **Public Preview:** This feature is in public preview.

Starting in v26.38, dictionary compression will be available (as **public
preview**) for managed clusters. Dictionary compression reduces the memory that
[arrangements](/get-started/arrangements/#arrangements) use when a column holds
the same values repeatedly. Instead of storing a repeated column value each time
it appears, Materialize stores that value once and has each row reference it.

Dictionary compression is off by default. You opt in per cluster with the
`EXPERIMENTAL ARRANGEMENT COMPRESSION` option.

Dictionary compression trades CPU for memory, and it does **not** reduce memory
on every workload. The savings come from large arrangements with columns that
hold a small set of longer values repeated across many rows, such as status
strings, enum-like labels, or tenant IDs. High-cardinality columns pay the CPU
cost with little or no memory benefit, and that cost is most visible as slower
hydration.

For the full tradeoff, guidance on whether your workload is a good fit, and how
to measure the effect, see [Dictionary
compression](/transform-data/dictionary-compression/).

### Replication factor

The `REPLICATION FACTOR` option determines the number of replicas provisioned
for the cluster. Each replica of the cluster provisions a new pool of compute
resources to perform exactly the same computations on exactly the same data.

Provisioning more than one replica improves **fault tolerance**. Clusters with
multiple replicas can tolerate failures of the underlying hardware that cause a
replica to become unreachable. As long as one replica of the cluster remains
available, the cluster can continue to maintain dataflows and serve queries.

Materialize makes the following guarantees when provisioning replicas:

- Replicas of a given cluster are never provisioned on the same underlying
  hardware.
- Replicas of a given cluster are spread as evenly as possible across the
  underlying cloud provider's availability zones.

Materialize automatically assigns names to replicas like `r1`, `r2`, etc. You
can view information about individual replicas in the console and the system
catalog, but you cannot directly modify individual replicas.

You can pause a cluster's work by specifying a replication factor of `0`. Doing
so removes all replicas of the cluster. Any indexes, materialized views,
sources, and sinks on the cluster will cease to make progress, and any queries
directed to the cluster will block. You can later resume the cluster's work by
using [`ALTER CLUSTER`] to set a nonzero replication factor.

> **Note:** A common misconception is that increasing a cluster's replication
> factor will increase its capacity for work. This is not the case. Increasing
> the replication factor increases the **fault tolerance** of the cluster, not its
> capacity for work. Replicas are exact copies of one another: each replica must
> do exactly the same work (i.e., maintain the same dataflows and process the same
> queries) as all the other replicas of the cluster.
> To increase a cluster's capacity, you should instead increase the cluster's
> [size](#available-sizes).

### Credit usage

Each [replica](#replication-factor) of the cluster consumes credits at a rate
determined by the cluster's size:

Size      | Legacy t-shirt size | Credits per replica per hour
----------|---------------------|-----------------------------
`25cc`    | `3xsmall`           | 0.25
`50cc`    | `2xsmall`           | 0.5
`100cc`   | `xsmall`            | 1
`200cc`   | `small`             | 2
`300cc`   | &nbsp;              | 3
`400cc`   | `medium`            | 4
`600cc`   | &nbsp;              | 6
`800cc`   | `large`             | 8
`1200cc`  | &nbsp;              | 12
`1600cc`  | `xlarge`            | 16
`3200cc`  | `2xlarge`           | 32
`6400cc`  | `3xlarge`           | 64
`128C`    | `4xlarge`           | 128
`256C`    | `5xlarge`           | 256
`512C`    | `6xlarge`           | 512

Credit usage is measured at a one second granularity. For a given replica,
credit usage begins when a `CREATE CLUSTER` or [`ALTER CLUSTER`] statement
provisions the replica and ends when an [`ALTER CLUSTER`] or [`DROP CLUSTER`]
statement deprovisions the replica.

A cluster with a [replication factor](#replication-factor) of zero uses no
credits.

As an example, consider the following sequence of events:

Time                | Event
--------------------|---------------------------------------------------------
2023-08-29 3:45:00  | `CREATE CLUSTER c (SIZE '400cc', REPLICATION FACTOR 2`)
2023-08-29 3:45:45  | `ALTER CLUSTER c SET (REPLICATION FACTOR 1)`
2023-08-29 3:47:15  | `DROP CLUSTER c`

Cluster `c` will have consumed 0.4 credits in total:

  * Replica `c.r1` was provisioned from 3:45:00 to 3:47:15, consuming 0.3
    credits.
  * Replica `c.r2` was provisioned from 3:45:00 to 3:45:45, consuming 0.1
    credits.

### Known limitations

Clusters have several known limitations:

* When a cluster using legacy cc size of `3200cc` or larger uses multiple
  replicas, those replicas are not guaranteed to be spread evenly across the
  underlying cloud provider's availability zones.

## Examples

### Basic

Create a cluster with two `200cc` replicas:

```mzsql
CREATE CLUSTER c1 (SIZE = '200cc', REPLICATION FACTOR = 2);
```

### Empty

Create a cluster with no replicas:

```mzsql
CREATE CLUSTER c1 (SIZE '100cc', REPLICATION FACTOR = 0);
```

You can later add replicas to this cluster with [`ALTER CLUSTER`].

## Privileges

The privileges required to execute this statement are:

- `CREATECLUSTER` privileges on the system.

## See also

- [`ALTER CLUSTER`]
- [`DROP CLUSTER`]
- [Dictionary compression](/transform-data/dictionary-compression/)

[AWS availability zone IDs]: https://docs.aws.amazon.com/ram/latest/userguide/working-with-az-ids.html
[`ALTER CLUSTER`]: /sql/alter-cluster/
[`DROP CLUSTER`]: /sql/drop-cluster/
[`SELECT`]: /sql/select
[`SUBSCRIBE`]: /sql/subscribe
[`mz_cluster_replica_sizes`]: /reference/system-catalog/mz_catalog#mz_cluster_replica_sizes
