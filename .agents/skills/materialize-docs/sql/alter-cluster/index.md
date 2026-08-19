# ALTER CLUSTER
`ALTER CLUSTER` changes the configuration of a cluster.
Use `ALTER CLUSTER` to:

- Change configuration of a cluster, such as the `SIZE` or
`REPLICATON FACTOR`.
- Rename a cluster.
- Change owner of a cluster.

For completeness, the syntax for `SWAP WITH` operation is provided. However, in
general, you will not need to manually perform this operation.

## Syntax

`ALTER CLUSTER` has the following syntax variations:

**Set a configuration:**

To set a cluster configuration:

```mzsql
ALTER CLUSTER <cluster_name>
SET (
    [SIZE = <text>]
    [, REPLICATION FACTOR = <int>]
    [, MANAGED = <bool>]
    [, AUTO SCALING STRATEGY = (
        ON HYDRATION (
            HYDRATION SIZE = <text>
            [, LINGER DURATION = <interval>]
        )
    )]
    [, EXPERIMENTAL ARRANGEMENT COMPRESSION = <bool>]
)
[WITH ( <with_option>[,...])]
;

```

| Syntax element | Description |
| --- | --- |
| `<cluster_name>` | The name of the cluster you want to alter.  |
| `SIZE` | <a name="alter-cluster-size"></a> Optional. The size of the resource allocations for the cluster. For valid size values, see [Available sizes](#available-sizes). {{< warning >}} Changing the size of a cluster may incur downtime. For more information, see [Resizing considerations](#resizing). {{< /warning >}} Not available for `ALTER CLUSTER ... RESET` since there is no default `SIZE` value. |
| `REPLICATION FACTOR` | Optional. The number of replicas to provision for the cluster. Each replica of the cluster provisions a new pool of compute resources to perform exactly the same computations on exactly the same data. For more information, see [Replication factor considerations](#replication-factor).  Default: `1`  |
| `MANAGED` | Optional. Whether to automatically manage the cluster's replicas based on the configured size and replication factor.  If `FALSE`, enables the use of the <em>deprecated</em> [`CREATE CLUSTER REPLICA`](/sql/create-cluster-replica) command.  Default: `TRUE`  |
| `AUTO SCALING STRATEGY` | Optional. While the cluster has un-hydrated objects, provisions an extra burst replica at a larger size to speed up hydration. The steady-size replicas will continue to run, and hydrate in parallel. Once a steady-size replica hydrates and catches up with the burst, the burst replica is retired. This helps optimize costs while speeding up hydration. Only available on managed clusters.  Specify a single `ON HYDRATION` sub-policy, which supports the following options:  \| Option \| Description \| \|--------\|-------------\| \| `HYDRATION SIZE` \| The size of the burst replica provisioned while the cluster has un-hydrated objects. Must differ from the cluster's steady `SIZE`. Choose a larger size to speed up hydration. For valid size values, see [Available sizes](#available-sizes). \| \| `LINGER DURATION` \| Optional. How long the burst replica lingers after a steady-size replica catches up, before it is removed. Default: `0s`. \|  Set an empty strategy (`AUTO SCALING STRATEGY = ()`) to disable autoscaling.  |
| `EXPERIMENTAL ARRANGEMENT COMPRESSION` | {{< warn-if-unreleased-inline "v26.38" >}}  Optional. Whether to enable [dictionary compression](#dictionary-compression) for the arrangements maintained by the cluster's replicas. Compression reduces the memory those arrangements use, at the cost of CPU, and does not benefit every workload. Only available on managed clusters.  {{< warning >}} Because changing this option never changes an existing replica, Materialize creates a new set of replicas carrying the new setting and cuts over to them once they have hydrated. For more information, see [Dictionary compression](#dictionary-compression). {{< /warning >}}  Default: `FALSE`  |
| `WITH (<with_option>[,...])` |  The following `<with_option>`s are supported: \| Option  \| Description \| \|--------\|-------------\| \| `WAIT UNTIL READY(...)`    \| ***Private preview.** This option has known performance or stability issues and is under active development.* {{< include-from-yaml data="examples/alter_cluster" name="wait-until-ready-cmd-option" >}} \| \| `WAIT FOR` \|  ***Private preview.** This option has known performance or stability issues and is under active development.* A fixed duration to wait for the new replicas to be ready. This option can lead to downtime. As such, we recommend using the `WAIT UNTIL READY` option instead.\|  |

**Reset to default:**

To reset a cluster configuration back to its default value:

```mzsql
ALTER CLUSTER <cluster_name>
RESET (
    REPLICATION FACTOR | MANAGED | AUTO SCALING STRATEGY
    | EXPERIMENTAL ARRANGEMENT COMPRESSION,
    ...
)
;

```

| Syntax element | Description |
| --- | --- |
| `<cluster_name>` | The name of the cluster you want to alter.  |
| `REPLICATION FACTOR` | Optional. The number of replicas to provision for the cluster.  Default: `1`  |
| `MANAGED` | Optional. Whether to automatically manage the cluster's replicas based on the configured size and replication factor.  Default: `TRUE`  |
| `AUTO SCALING STRATEGY` | Optional. Resetting removes any autoscaling strategy from the cluster.  Default: no autoscaling strategy.  |
| `EXPERIMENTAL ARRANGEMENT COMPRESSION` | {{< warn-if-unreleased-inline "v26.38" >}}  Optional. Resetting turns [dictionary compression](#dictionary-compression) off for the cluster. Because this never changes an existing replica, Materialize creates a new set of replicas without the setting and cuts over to them once they have hydrated.  Default: `FALSE`  |

**Rename:**

To rename a cluster:

```mzsql
ALTER CLUSTER <cluster_name> RENAME TO <new_cluster_name>;

```

| Syntax element | Description |
| --- | --- |
| `<cluster_name>` | The current name of the cluster.  |
| `<new_cluster_name>` | The new name of the cluster.  |

> **Note:** You cannot rename system clusters, such as `mz_system` and `mz_catalog_server`.

**Change owner:**

To change the owner of a cluster:

```mzsql
ALTER CLUSTER <cluster_name> OWNER TO <new_owner_role>;

```

| Syntax element | Description |
| --- | --- |
| `<cluster_name>` | The name of the cluster you want to change ownership of.  |
| `<new_owner_role>` | The new owner of the cluster.  |
To change the owner, you must have ownership of the cluster and membership in
the `<new_owner_role>`. See also [Required privileges](#required-privileges).

**Swap with:**

> **Important:** Information about the `SWAP WITH` operation is provided for completeness.  The
> `SWAP WITH` operation is used for blue/green deployments. In general, you will
> not need to manually perform this operation.

To swap the name of this cluster with another cluster:

```mzsql
ALTER CLUSTER <cluster1> SWAP WITH <cluster2>;

```

| Syntax element | Description |
| --- | --- |
| `<cluster1>` | The name of the first cluster.  |
| `<cluster2>` | The name of the second cluster.  |

## Considerations

### Resizing

> **Tip:** For help sizing your clusters, navigate to **Materialize Console >**
> [**Monitoring**](/console/monitoring/)>**Environment Overview**. This page
> displays cluster resource utilization and sizing advice.

#### Available sizes

**cc Clusters:**

Valid cc cluster sizes are:

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

Resource allocations are proportional to the number in the size name. For
example, a cluster of size `600cc` has 2x as much CPU, memory, and disk as a
cluster of size `300cc`, and 1.5x as much CPU, memory, and disk as a cluster of
size `400cc`.

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

See also:

- [cc to M.1 size mapping](/sql/m1-cc-mapping/).

- [Materialize service consumption
  table](https://materialize.com/pdfs/pricing.pdf).

- [Blog:Scaling Beyond Memory: How Materialize Uses Swap for Larger
  Workloads](https://materialize.com/blog/scaling-beyond-memory/).

#### Resource allocation

To determine the specific resource allocation for a given cluster size, query
the [`mz_cluster_replica_sizes`](/reference/system-catalog/mz_catalog/#mz_cluster_replica_sizes)
system catalog table.

> **Warning:** The values in the `mz_cluster_replica_sizes` table may change at any
> time. You should not rely on them for any kind of capacity planning.

#### Downtime considerations for v26.35 or after
Starting in v26.35, ALTER CLUSTER <name> SET (SIZE = ...) by default resizes
the cluster gracefully and without downtime. For example:

```mzsql
ALTER CLUSTER c1 SET (SIZE = '100cc');
```

##### Resizing process
The resize proceeds in the background, allowing the command to return
immediately.

During a graceful resize, Materialize:
1. Provisions new replicas at the target size, alongside the current replicas.
2. Waits for the new replicas to
   [hydrate](/concepts/hydration/).
3. Retires the old replicas.

Throughout, the cluster keeps serving queries, first from the old replicas,
then from both sets as the new replicas come up, so the resize incurs no
downtime.

If the new replicas do not hydrate within the reconfiguration timeout (24 hours
by default), Materialize rolls back the resize and the cluster keeps its current
size. To customize the timeout behavior, use the `WAIT UNTIL READY` or `WAIT FOR` options.
The resize still proceeds in the background.

- `WAIT UNTIL READY (TIMEOUT = ..., ON TIMEOUT = ...)` sets the timeout for the
  resize. On timeout, `ON TIMEOUT` selects whether to `COMMIT` (retire the old
  replicas and proceed with the not-yet-hydrated new ones, which can cause
  downtime) or `ROLLBACK` (keep the current size). Default: `ROLLBACK`.

  ```mzsql
  ALTER CLUSTER c1
  SET (SIZE = '100cc') WITH (WAIT UNTIL READY (TIMEOUT = '10m'));
  ```

- `WAIT FOR '<duration>'` sets the timeout and commits when it expires,
  regardless of hydration status, which can cause downtime. Prefer
  `WAIT UNTIL READY`.

See [Monitoring a resize](#monitoring-a-resize) to track progress and
[cancel](#monitoring-a-resize) an in-flight resize.

##### Monitoring a resize
You can monitor a resize through the following:

- The `activity` column of [`SHOW CLUSTERS`](/sql/show-clusters/), which
  summarizes any in-flight reconfiguration or hydration burst, and is `NULL`
  when the cluster is steady.

- [`mz_internal.mz_cluster_reconfigurations`](/reference/system-catalog/mz_internal/#mz_cluster_reconfigurations),
  which shows the target shape, deadline, timeout action, and lifecycle status
  of the latest reconfiguration.

- [`mz_internal.mz_cluster_auto_scaling_strategies`](/reference/system-catalog/mz_internal/#mz_cluster_auto_scaling_strategies),
  which shows any in-flight hydration burst.

- [`mz_internal.mz_hydration_statuses`](/reference/system-catalog/mz_internal/#mz_hydration_statuses),
  which shows per-object hydration status.

- The audit log
  ([`mz_catalog.mz_audit_events`](/reference/system-catalog/mz_catalog/#mz_audit_events)),
  which records each reconfiguration transition.

##### Cancel a resize
To **cancel** an in-flight resize, reissue `ALTER CLUSTER` with the cluster's
current size. Materialize drops the pending replicas and keeps the current
configuration.

#### Downtime considerations for v26.34 or before

You can use the `WAIT UNTIL READY` option to perform a zero-downtime resizing,
which incurs **no downtime**. Instead of restarting the cluster, this approach
spins up an additional cluster replica under the covers with the desired new
size, waits for the replica to be hydrated, and then replaces the original
replica.

```sql
ALTER CLUSTER c1
SET (SIZE '100cc') WITH (WAIT UNTIL READY (TIMEOUT = '10m', ON TIMEOUT = 'COMMIT'));
```

The `ALTER` statement is blocking and will return only when the new replica
becomes ready. This could take as long as the specified timeout. During this
operation, any other reconfiguration command issued against this cluster will
fail. Additionally, any connection interruption or statement cancelation will
cause a rollback — no size change will take effect in that case.

> **Note:** Using `WAIT UNTIL READY` requires that the session remain open: you need to
> make sure the Console tab remains open or that your `psql` connection remains
> stable.
> Any interruption will cause a cancellation, no cluster changes will take
> effect.

### Speed up hydration by autoscaling to a larger size

Beyond a one-off resize, you can configure a standing **autoscaling strategy**
so the cluster provisions a burst replica at a larger size on its own whenever
it has un-hydrated objects. You can set the strategy when you first create the cluster
with `CREATE CLUSTER ... (AUTO SCALING STRATEGY = ...)`, or add it to an
existing cluster with `ALTER CLUSTER ... SET (AUTO SCALING STRATEGY = ...)`. The
example below uses `CREATE CLUSTER`; see [Configure
autoscaling](#configure-autoscaling) for the `ALTER CLUSTER` form.

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

<div class="warning">
    <strong class="gutter">Unreleased</strong>
    This feature will be released in
    <a href="/releases#release-notes"><strong>v26.38</strong></a>.
    It may not be available in your region yet.
    The release is scheduled to complete by <strong>August 19, 2026</strong>.
  </div>

Starting in v26.38, dictionary compression will be available (as **public
preview**) for managed clusters. Dictionary compression reduces the memory that
[arrangements](/get-started/arrangements/#arrangements) use when a column holds
the same values repeatedly. Instead of storing a repeated column value each time
it appears, Materialize stores that value once and has each row reference it.

Dictionary compression is off by default. You opt in per cluster with the
`EXPERIMENTAL ARRANGEMENT COMPRESSION` option.

Turn compression on for an existing cluster with `ALTER CLUSTER ... SET
(EXPERIMENTAL ARRANGEMENT COMPRESSION = true)`, and go back to the default with
`ALTER CLUSTER ... RESET (EXPERIMENTAL ARRANGEMENT COMPRESSION)`.

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
Each replica incurs cost, calculated as `cluster size * replication factor` per
second. See [Usage & billing](/administration/billing/) for more details.

#### Replication factor and fault tolerance

Provisioning more than one replica provides **fault tolerance**. Clusters with
multiple replicas can tolerate failures of the underlying hardware that cause a
replica to become unreachable. As long as one replica of the cluster remains
available, the cluster can continue to maintain dataflows and serve queries.

> **Note:** - Each replica incurs cost, calculated as `cluster size *
>   replication factor` per second. See [Usage &
>   billing](/administration/billing/) for more details.
> - Increasing the replication factor does **not** increase the cluster's work
>   capacity. Replicas are exact copies of one another: each replica must do
>   exactly the same work (i.e., maintain the same dataflows and process the same
>   queries) as all the other replicas of the cluster.
>   To increase the capacity of a cluster, you must increase its
>   [size](#resizing).

Materialize automatically assigns names to replicas (e.g., `r1`, `r2`). You can
view information about individual replicas in the Materialize console and the system
catalog.

#### Availability guarantees

When provisioning replicas,

- For clusters sized **under `3200cc`**, Materialize guarantees that all
  provisioned replicas in a cluster are spread across the underlying cloud
  provider's availability zones.

- For clusters sized at **`3200cc` and above**, even distribution of replicas
  across availability zones **cannot** be guaranteed.

## Required privileges

To execute the `ALTER CLUSTER` command, you need:

- Ownership of the cluster.

- To rename a cluster, you must also have membership in the `<new_owner_role>`.

- To swap names with another cluster, you must also have ownership of the other
  cluster.

See also:

- [Access control (Materialize Cloud)](/security/cloud/access-control/)
- [Access control (Materialize
  Self-Managed)](/security/self-managed/access-control/)

### Rename restrictions

You cannot rename system clusters, such as `mz_system` and `mz_catalog_server`.

## Examples

### Replication factor

The following example uses `ALTER CLUSTER` to update the `REPLICATION
FACTOR` of cluster `c1` to ``2``:

```mzsql
ALTER CLUSTER c1 SET (REPLICATION FACTOR 2);
```

Increasing the `REPLICATION FACTOR` increases the cluster's [fault
tolerance](#replication-factor-and-fault-tolerance), not its work capacity.

### Resizing

By default, altering the cluster size is graceful and incurs **no downtime**.
The command returns immediately and the resize proceeds in the background. See
[Resizing process](#resizing-process) and
[Monitoring a resize](#monitoring-a-resize).

```mzsql
ALTER CLUSTER c1 SET (SIZE = '100cc');
```

To customize the timeout and what happens when it expires, use the `WAIT UNTIL
READY` [option](#syntax):

```mzsql
ALTER CLUSTER c1
SET (SIZE = '100cc') WITH (WAIT UNTIL READY (TIMEOUT = '10m', ON TIMEOUT = 'ROLLBACK'));
```

### Configure autoscaling

To [speed up hydration](#speed-up-hydration-by-autoscaling-to-a-larger-size),
configure an autoscaling strategy that provisions a burst replica at a larger
size while the cluster has un-hydrated objects:

```mzsql
ALTER CLUSTER c1 SET (
    AUTO SCALING STRATEGY = (
        ON HYDRATION (HYDRATION SIZE = '800cc', LINGER DURATION = '15s')
    )
);
```

To remove the strategy:

```mzsql
ALTER CLUSTER c1 RESET (AUTO SCALING STRATEGY);
```

To inspect the configured strategy and any in-flight burst, query
[`mz_internal.mz_cluster_auto_scaling_strategies`](/reference/system-catalog/mz_internal/#mz_cluster_auto_scaling_strategies).
The `strategy` column holds the configured policy, and the `state` column holds
the in-flight burst details, or `NULL` when no burst is running:

```mzsql
SELECT
    c.name AS cluster,
    s.strategy->'on_hydration'->>'hydration_size' AS hydration_size,
    (s.strategy->'on_hydration'->'linger_duration'->>'secs')::int AS linger_seconds,
    s.state->'burst'->>'burst_size' AS inflight_burst_size
FROM mz_internal.mz_cluster_auto_scaling_strategies AS s
JOIN mz_clusters AS c ON c.id = s.cluster_id;
```

```nofmt
 cluster | hydration_size | linger_seconds | inflight_burst_size
---------+----------------+----------------+---------------------
 c1      | 800cc          |             15 |
```

Here, `c1` is configured to provision an `800cc` burst replica that lingers 15
seconds, and no burst is currently running (`inflight_burst_size` is `NULL`).
While a burst is in flight, `inflight_burst_size` reports the burst replica's
size.

[`SHOW CLUSTERS`](/sql/show-clusters/) also summarizes any in-flight hydration
burst in its `activity` column.

### Converting unmanaged to managed clusters

> **Note:** When getting started with Materialize, we recommend using managed clusters. You
> can convert any unmanaged clusters to managed clusters by following the
> instructions below.

Alter the `managed` status of a cluster to managed:

```mzsql
ALTER CLUSTER c1 SET (MANAGED);
```

Materialize permits converting an unmanged cluster to a managed cluster if
the following conditions are met:

* The cluster replica names are `r1`, `r2`, ..., `rN`.
* All replicas have the same size.
* If there are no replicas, `SIZE` needs to be specified.
* If specified, the replication factor must match the number of replicas.

Note that the cluster will not have settings for the availability zones, and
compute-specific settings. If needed, these can be set explicitly.

## See also

- [`CREATE CLUSTER`](/sql/create-cluster/)
- [`SHOW CLUSTERS`](/sql/show-clusters/)
- [`DROP CLUSTER`](/sql/drop-cluster/)
- [Dictionary compression](/transform-data/dictionary-compression/)
