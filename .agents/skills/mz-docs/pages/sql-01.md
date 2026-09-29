<!-- mz-docs page: sql -->

# SQL commands

SQL commands reference.

## Create/Alter/Drop Objects

| CREATE | ALTER | DROP |
| --- | --- | --- |
| [`CREATE CLUSTER`](/sql/create-cluster) | [`ALTER CLUSTER`](/sql/alter-cluster) | [`DROP CLUSTER`](/sql/drop-cluster) |
| [`CREATE CLUSTER REPLICA`](/sql/create-cluster-replica) | [`ALTER CLUSTER REPLICA`](/sql/alter-cluster-replica) | [`DROP CLUSTER REPLICA`](/sql/drop-cluster-replica) |
| [`CREATE CONNECTION`](/sql/create-connection) | [`ALTER CONNECTION`](/sql/alter-connection) | [`DROP CONNECTION`](/sql/drop-connection) |
| [`CREATE DATABASE`](/sql/create-database) | [`ALTER DATABASE`](/sql/alter-database) | [`DROP DATABASE`](/sql/drop-database) |
| [`CREATE INDEX`](/sql/create-index) | [`ALTER INDEX`](/sql/alter-index) | [`DROP INDEX`](/sql/drop-index) |
| [`CREATE MATERIALIZED VIEW`](/sql/create-materialized-view) | [`ALTER MATERIALIZED VIEW`](/sql/alter-materialized-view) | [`DROP MATERIALIZED VIEW`](/sql/drop-materialized-view) |
| [`CREATE NETWORK POLICY`](/sql/create-network-policy) | [`ALTER NETWORK POLICY`](/sql/alter-network-policy) | [`DROP NETWORK POLICY`](/sql/drop-network-policy) |
| [`CREATE ROLE`](/sql/create-role) | [`ALTER ROLE`](/sql/alter-role) | [`DROP ROLE`](/sql/drop-role) <br>[`DROP USER`](/sql/drop-user) |
| [`CREATE SCHEMA`](/sql/create-schema) | [`ALTER SCHEMA`](/sql/alter-schema) | [`DROP SCHEMA`](/sql/drop-schema) |
| [`CREATE SECRET`](/sql/create-secret) | [`ALTER SECRET`](/sql/alter-secret) | [`DROP SECRET`](/sql/drop-secret) |
| [`CREATE SINK`](/sql/create-sink) | [`ALTER SINK`](/sql/alter-sink) | [`DROP SINK`](/sql/drop-sink) |
| [`CREATE SOURCE`](/sql/create-source) | [`ALTER SOURCE`](/sql/alter-source) | [`DROP SOURCE`](/sql/drop-source) |
| [`CREATE TABLE`](/sql/create-table) | [`ALTER TABLE`](/sql/alter-table) | [`DROP TABLE`](/sql/drop-table) |
| [`CREATE TYPE`](/sql/create-type) | [`ALTER TYPE`](/sql/alter-type) | [`DROP TYPE`](/sql/drop-type) |
| [`CREATE VIEW`](/sql/create-view) | [`ALTER VIEW`](/sql/alter-view) | [`DROP VIEW`](/sql/drop-view) |

## Create/Read/Update/Delete Data

The following commands perform CRUD operations on materialized views, views,
sources, and tables:

| <strong>Select/Subscribe</strong> |  - [`SELECT`](/sql/select)  - [`SUBSCRIBE`](/sql/subscribe)    |
| <strong>Cursor</strong> |  - [`CLOSE`](/sql/close)  - [`DECLARE`](/sql/declare)  - [`FETCH`](/sql/fetch)   |
| <strong>Sink</strong> |  - [`ALTER SINK`](/sql/alter-sink)  - [`CREATE SINK`](/sql/create-sink)  - [`DROP SINK`](/sql/drop-sink)   |
| <strong>Transactions</strong> |  - [`BEGIN`](/sql/begin)  - [`COMMIT`](/sql/commit)  - [`ROLLBACK`](/sql/rollback)   |
| <strong>Copy</strong> |  - [`COPY FROM`](/sql/copy-from)  - [`COPY TO`](/sql/copy-to)   |

## RBAC

Commands to manage roles and privileges and owners:

| <strong>Roles</strong> |  - [`ALTER ROLE`](/sql/alter-role)  - [`CREATE ROLE`](/sql/create-role)  - [`DROP ROLE`](/sql/drop-role) <br>[`DROP USER`](/sql/drop-user)  - [`GRANT ROLE`](/sql/grant-role)  - [`REVOKE ROLE`](/sql/revoke-role)  - [`SHOW ROLES`](/sql/show-roles)   |
| <strong>Privileges</strong> |  - [`ALTER DEFAULT PRIVILEGES`](/sql/alter-default-privileges)  - [`GRANT PRIVILEGE`](/sql/grant-privilege)  - [`REVOKE PRIVILEGE`](/sql/revoke-privilege)   |
| <strong>Owners</strong> |  - [`ALTER CLUSTER`](/sql/alter-cluster)  - [`ALTER CLUSTER REPLICA`](/sql/alter-cluster-replica)  - [`ALTER CONNECTION`](/sql/alter-connection)  - [`ALTER DATABASE`](/sql/alter-database)  - [`ALTER MATERIALIZED VIEW`](/sql/alter-materialized-view)  - [`ALTER SCHEMA`](/sql/alter-schema)  - [`ALTER SECRET`](/sql/alter-secret)  - [`ALTER SINK`](/sql/alter-sink)  - [`ALTER SOURCE`](/sql/alter-source)  - [`ALTER TABLE`](/sql/alter-table)  - [`ALTER TYPE`](/sql/alter-type)  - [`ALTER VIEW`](/sql/alter-view)  - [`DROP OWNED`](/sql/drop-owned)  - [`REASSIGN OWNED`](/sql/reassign-owned)   |

## Query Introspection (`Explain`)

- [`EXPLAIN ANALYZE`](/sql/explain-analyze)

- [`EXPLAIN FILTER PUSHDOWN`](/sql/explain-filter-pushdown)

- [`EXPLAIN PLAN`](/sql/explain-plan)

- [`EXPLAIN SCHEMA`](/sql/explain-schema)

- [`EXPLAIN TIMESTAMP`](/sql/explain-timestamp)

## Object Introspection (`SHOW`) { #show }

- [`SHOW`](/sql/show)

- [`SHOW CLUSTER REPLICAS`](/sql/show-cluster-replicas)

- [`SHOW CLUSTERS`](/sql/show-clusters)

- [`SHOW COLUMNS`](/sql/show-columns)

- [`SHOW CONNECTIONS`](/sql/show-connections)

- [`SHOW CREATE CLUSTER`](/sql/show-create-cluster)

- [`SHOW CREATE CONNECTION`](/sql/show-create-connection)

- [`SHOW CREATE INDEX`](/sql/show-create-index)

- [`SHOW CREATE MATERIALIZED VIEW`](/sql/show-create-materialized-view)

- [`SHOW CREATE SINK`](/sql/show-create-sink)

- [`SHOW CREATE SOURCE`](/sql/show-create-source)

- [`SHOW CREATE TABLE`](/sql/show-create-table)

- [`SHOW CREATE TYPE`](/sql/show-create-type)

- [`SHOW CREATE VIEW`](/sql/show-create-view)

- [`SHOW DATABASES`](/sql/show-databases)

- [`SHOW DEFAULT PRIVILEGES`](/sql/show-default-privileges)

- [`SHOW INDEXES`](/sql/show-indexes)

- [`SHOW MATERIALIZED VIEWS`](/sql/show-materialized-views)

- [`SHOW NETWORK POLICIES (Cloud)`](/sql/show-network-policies)

- [`SHOW OBJECTS`](/sql/show-objects)

- [`SHOW PRIVILEGES`](/sql/show-privileges)

- [`SHOW ROLE MEMBERSHIP`](/sql/show-role-membership)

- [`SHOW ROLES`](/sql/show-roles)

- [`SHOW SCHEMAS`](/sql/show-schemas)

- [`SHOW SECRETS`](/sql/show-secrets)

- [`SHOW SINKS`](/sql/show-sinks)

- [`SHOW SOURCES`](/sql/show-sources)

- [`SHOW SUBSOURCES`](/sql/show-subsources)

- [`SHOW TABLES`](/sql/show-tables)

- [`SHOW TYPES`](/sql/show-types)

- [`SHOW VIEWS`](/sql/show-views)

## Session

Commands related with session state and configurations:

- [`DISCARD`](/sql/discard)

- [`RESET`](/sql/reset)

- [`SET`](/sql/set)

- [`SHOW`](/sql/show)

## Validations

- [`VALIDATE CONNECTION`](/sql/validate-connection)

## Prepared Statements

- [`DEALLOCATE`](/sql/deallocate)

- [`EXECUTE`](/sql/execute)

- [`PREPARE`](/sql/prepare)

<!-- mz-docs page: sql/alter-cluster -->

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
| `WITH (<with_option>[,...])` |  The following `<with_option>`s are supported: \| Option  \| Description \| \|--------\|-------------\| \| `WAIT UNTIL READY(...)`    \| {{< include-from-yaml data="examples/alter_cluster" name="wait-until-ready-cmd-option" >}} \| \| `WAIT FOR` \| Equivalent to `WAIT UNTIL READY` with `ON TIMEOUT = 'ROLLBACK'`. Materialize cuts over once the new replicas hydrate. When Materialize processes an expired timeout, it rolls back the resize and keeps the current size if the target replicas are still unhydrated.\|  |

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
> [**Monitoring**](/developer-tools/console/monitoring/)>**Environment Overview**. This page
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
the [`mz_cluster_replica_sizes`](/sql/system-catalog/mz_catalog/#mz_cluster_replica_sizes)
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
   [hydrate](/fundamentals/concepts/hydration/) and for their compute collections
   to catch up to the outgoing replicas within the configured lag allowance.
3. Retires the old replicas.

Throughout, the cluster keeps serving queries, first from the old replicas,
then from both sets as the new replicas come up, so the resize incurs no
downtime.

If the new replicas do not become ready within the reconfiguration
timeout (24 hours by default), Materialize rolls back the resize and the cluster
keeps its current size. To customize the timeout behavior, use the `WAIT UNTIL READY` or `WAIT FOR` options.
The resize still proceeds in the background.

- `WAIT UNTIL READY (TIMEOUT = ..., ON TIMEOUT = ...)` sets the timeout for the
  resize. On timeout, `ON TIMEOUT` selects whether to `COMMIT` (retire the old
  replicas and proceed with the new ones even if they are not ready) or
  `ROLLBACK` (keep the current size). Default: `ROLLBACK`.

  ```mzsql
  ALTER CLUSTER c1
  SET (SIZE = '100cc') WITH (WAIT UNTIL READY (TIMEOUT = '10m'));
  ```

- `WAIT FOR '<duration>'` is equivalent to `WAIT UNTIL READY (TIMEOUT =
  '<duration>', ON TIMEOUT = 'ROLLBACK')`. Materialize cuts over once the target
  replicas are ready. When Materialize processes an expired timeout,
  it rolls back the resize and keeps the current size if the target replicas
  are not ready.

See [Monitoring a resize](#monitoring-a-resize) to track progress and
[cancel](#monitoring-a-resize) an in-flight resize.

##### Monitoring a resize
You can monitor a resize through the following:

- The `activity` column of [`SHOW CLUSTERS`](/sql/show-clusters/), which
  summarizes any in-flight reconfiguration or hydration burst, and is `NULL`
  when the cluster is steady.

- [`mz_internal.mz_cluster_reconfigurations`](/sql/system-catalog/mz_internal/#mz_cluster_reconfigurations),
  which shows the target shape, deadline, timeout action, and lifecycle status
  of the latest reconfiguration.

- [`mz_internal.mz_cluster_auto_scaling_strategies`](/sql/system-catalog/mz_internal/#mz_cluster_auto_scaling_strategies),
  which shows any in-flight hydration burst.

- [`mz_internal.mz_hydration_statuses`](/sql/system-catalog/mz_internal/#mz_hydration_statuses),
  which shows per-object hydration status.

- The audit log
  ([`mz_catalog.mz_audit_events`](/sql/system-catalog/mz_catalog/#mz_audit_events)),
  which records each reconfiguration transition.

##### Cancel a resize
To **cancel** an in-flight resize, reissue `ALTER CLUSTER` with the cluster's
current size. Materialize drops the target replicas and keeps the current
configuration.

#### Downtime considerations for v26.34 or before

You can use the `WAIT UNTIL READY` option to perform a zero-downtime resizing,
which incurs **no downtime**. Instead of restarting the cluster, this approach
spins up an additional cluster replica under the covers with the desired new
size, waits for the replica to be hydrated, and then replaces the
original replica.

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
[hydrate](/fundamentals/concepts/hydration/) the affected
objects before they can serve results. Hydration reads the input data
and rebuilds in-memory state, and its speed scales with the cluster
[size](/sql/create-cluster/#available-sizes).

The `AUTO SCALING STRATEGY (ON HYDRATION)` option lets a cluster **automatically
provision an extra burst replica at the configured `HYDRATION SIZE` while it has
un-hydrated objects**. This speeds up hydration without manually scaling the
cluster up before hydration and back down afterward. The steady-size replicas
continue hydrating in parallel, and once one of them catches up with the burst,
the burst replica lingers for the `LINGER DURATION` and is then removed. The
burst replica is an ordinary cluster replica, billed only for the time it is
provisioned. See [Usage & billing](/materialize-cloud/billing/) for details.

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
`HYDRATION SIZE` | The [size](/sql/create-cluster/#available-sizes) of the burst replica provisioned while the cluster has un-hydrated objects. Must differ from the cluster's steady `SIZE`. Choose a larger size to speed up hydration.
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
[`mz_internal.mz_cluster_auto_scaling_strategies`](/sql/system-catalog/mz_internal/#mz_cluster_auto_scaling_strategies)
catalog view.

### Dictionary compression

> **Public Preview:** This feature is in public preview.

Starting in v26.38, dictionary compression is available for managed clusters.
Dictionary compression reduces the memory that
[arrangements](/fundamentals/concepts/arrangements/#arrangements) use when a column holds
the same values repeatedly. Instead of storing a repeated column value each time
it appears, Materialize stores that value once and has each row reference it. This can reduce steady state memory requirements after hydration has completed.

Dictionary compression is specified per cluster replica, and is set to off by default. You opt in using the `EXPERIMENTAL ARRANGEMENT COMPRESSION` option, while creating or altering a cluster or cluster replica.

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
second. See [Usage & billing](/materialize-cloud/billing/) for more details.

#### Replication factor and fault tolerance

Provisioning more than one replica provides **fault tolerance**. Clusters with
multiple replicas can tolerate failures of the underlying hardware that cause a
replica to become unreachable. As long as one replica of the cluster remains
available, the cluster can continue to maintain dataflows and serve queries.

> **Note:** - Each replica incurs cost, calculated as `cluster size *
>   replication factor` per second. See [Usage &
>   billing](/materialize-cloud/billing/) for more details.
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
[`mz_internal.mz_cluster_auto_scaling_strategies`](/sql/system-catalog/mz_internal/#mz_cluster_auto_scaling_strategies).
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

<!-- mz-docs page: sql/alter-cluster-replica -->

# ALTER CLUSTER REPLICA
`ALTER CLUSTER REPLICA` changes properties of a cluster replica.
Use `ALTER CLUSTER REPLICA` to:
- Rename a cluster replica.
- Change owner of a cluster replica.

## Syntax

**Rename:**

To rename a cluster replica:

```mzsql
ALTER CLUSTER REPLICA <name> RENAME TO <new_name>;

```

| Syntax element | Description |
| --- | --- |
| `<name>` | The current name of the cluster replica.  |
| `<new_name>` | The new name of the cluster replica.  |

> **Note:** You cannot rename replicas in system clusters.

**Change owner:**

To change the owner of a cluster replica:

```mzsql
ALTER CLUSTER REPLICA <name> OWNER TO <new_owner_role>;

```

| Syntax element | Description |
| --- | --- |
| `<name>` | The name of the cluster replica you want to change ownership of.  |
| `<new_owner_role>` | The new owner of the cluster replica.  |
To change the owner of a cluster replica, you must be the current owner and have
membership in the `<new_owner_role>`.

## Privileges

The privileges required to execute this statement are:

- Ownership of the cluster replica.
- In addition, to change owners:
  - Role membership in `new_owner`.
  - `CREATE` privileges on the containing cluster.

## Example

The following changes the owner of the cluster replica `production.r1` to
`admin`.  The user running the command must:
- Be the current owner;
- Be a member of `admin`; and
- Have `CREATE` privilege on the `production` cluster.

```mzsql
ALTER CLUSTER REPLICA production.r1 OWNER TO admin;
```

<!-- mz-docs page: sql/alter-connection -->

# ALTER CONNECTION
`ALTER CONNECTION` allows you to modify the value of connection options; rotate secrets associated with connections; rename a connection; and change owner of a connection.
Use `ALTER CONNECTION` to:

- Modify the parameters of a connection, such as the hostname to which it
  points.
- Rotate the key pairs associated with an [SSH tunnel connection].
- Rename a connection.
- Change owner of a connection.

## Syntax

**SET/DROP/RESET options:**

To modify connection parameters:

```mzsql
ALTER CONNECTION [IF EXISTS] <name>
  SET (<option> = <value>) | DROP (<option>) | RESET (<option>)
  [, ...]
  [WITH (VALIDATE [true|false])]
;

```

| Syntax element | Description |
| --- | --- |
| **IF EXISTS** | Optional. If specified, do not return an error if the specified connection does not exist.  |
| `<name>` | The identifier of the connection you want to alter.  |
| **SET** | Sets the option to the specified value.  |
| **DROP** | Resets the specified option to its default value. Synonym for **RESET**.  |
| **RESET** | Resets the specified option to its default value. Synonym for **DROP**.  |
| `<option>` | The connection option to modify. See [`CREATE CONNECTION`](/sql/create-connection) for available options.  |
| `<value>` | The value to assign to the option.  |
| **WITH (VALIDATE `<bool>`)** | Optional. Whether [connection validation](/sql/create-connection#connection-validation) should be performed. Defaults to `true`.  |

**ROTATE KEYS:**

To rotate SSH tunnel connection key pairs:

```mzsql
ALTER CONNECTION [IF EXISTS] <name> ROTATE KEYS;

```

| Syntax element | Description |
| --- | --- |
| **IF EXISTS** | Optional. If specified, do not return an error if the specified connection does not exist.  |
| `<name>` | The identifier of the SSH tunnel connection.  |

**Rename:**

To rename a connection

```mzsql
ALTER CONNECTION <name> RENAME TO <new_name>;

```

| Syntax element | Description |
| --- | --- |
| `<name>` | The current name of the connection.  |
| `<new_name>` | The new name of the connection.  |
See also [Renaming restrictions](/sql/identifiers/#renaming-restrictions).

**Change owner:**

To change the owner of a connection:

```mzsql
ALTER CONNECTION <name> OWNER TO <new_owner_role>;

```

| Syntax element | Description |
| --- | --- |
| `<name>` | The name of the connection you want to change ownership of.  |
| `<new_owner_role>` | The new owner of the connection.  |
To change the owner of a connection, you must be the owner of the connection and
have membership in the `<new_owner_role>`. See also [Privileges](#privileges).

## Details

### `SET`, `RESET`, `DROP`

These subcommands let you modify the parameters of a connection.

* **RESET** and **DROP** are synonyms and will return the parameter to its
    original state. For instance, if the connection has a default port, **DROP**
    will return it to the default value.
* All provided changes are applied atomically.
* The same parameter cannot have multiple modifications.

For the available parameters for each type of connection, see [`CREATE
CONNECTION`](/sql/create-connection).

### `ROTATE KEYS`

The `ROTATE KEYS` command can be used to change the key pairs associated with
an [SSH tunnel connection] without causing downtime.

Each SSH tunnel connection is associated with two key pairs. The public keys
for the key pairs are announced in the [`mz_ssh_tunnel_connections`]
system table in the `public_key_1` and `public_key_2` columns.

Upon executing the `ROTATE KEYS` command, Materialize deletes the first key
pair, promotes the second key pair to the first key pair, and generates a new
second key pair. The connection's row in `mz_ssh_tunnel_connections` is updated
accordingly: the `public_key_1` column will contain the public key that was
formely in the `public_key_2` column, and the `public_key_2` column will contain
a new public key.

After executing `ROTATE KEYS`, you should update your SSH bastion server with
the new public keys:

* Remove the public key that was formely in the `public_key_1` column.
* Add the new public key from the `public_key_2` column.

Throughout the entire process, the SSH bastion server is configured to permit
authentication from at least one of the keys that Materialize will authenticate
with, so Materialize's ability to connect is never interrupted.

You must take care to update the SSH bastion server with the new keys after
every execution of the `ROTATE KEYS` command. If you rotate keys twice in
succession without adding the new keys to the bastion server, Materialize will
be unable to authenticate with the bastion server.

## Privileges

The privileges required to execute this statement are:

- Ownership of the connection.
- In addition, to set, reset, or drop connection options:
  - `USAGE` privileges on all connections and secrets referenced by the
    resulting connection definition.
  - `USAGE` privileges on the schemas that contain those connections and
    secrets.
- In addition, to change owners:
  - Role membership in `new_owner`.
  - `CREATE` privileges on the containing schema if the connection is namespaced
  by a schema.

## Related pages

-   [`CREATE CONNECTION`](/sql/create-connection/)
-   [`SHOW CONNECTIONS`](/sql/show-connections)

[SSH tunnel connection]: /sql/create-connection/#ssh-tunnel
[`mz_ssh_tunnel_connections`]: /sql/system-catalog/mz_catalog/#mz_ssh_tunnel_connections

<!-- mz-docs page: sql/alter-database -->

# ALTER DATABASE
`ALTER DATABASE` changes properties of a database.
Use `ALTER DATABASE` to:
- Rename a database.
- Change owner of a database.

## Syntax

**Rename:**

To rename a database:

```mzsql
ALTER DATABASE <name> RENAME TO <new_name>;

```

| Syntax element | Description |
| --- | --- |
| `<name>` | The current name of the database.  |
| `<new_name>` | The new name of the database.  |
See also [Renaming restrictions](/sql/identifiers/#renaming-restrictions).

**Change owner:**

To change the owner of a database:

```mzsql
ALTER DATABASE <name> OWNER TO <new_owner_role>;

```

| Syntax element | Description |
| --- | --- |
| `<name>` | The name of the database you want to change ownership of.  |
| `<new_owner_role>` | The new owner of the database.  |
To change the owner of a database, you must be the current owner and have
membership in the `<new_owner_role>`.

## Privileges

The privileges required to execute this statement are:

- Ownership of the database.
- In addition, to change owners:
  - Role membership in `new_owner`.

<!-- mz-docs page: sql/alter-default-privileges -->

# ALTER DEFAULT PRIVILEGES
`ALTER DEFAULT PRIVILEGES` defines default privileges that will be applied to objects created in the future.
Use `ALTER DEFAULT PRIVILEGES` to:

- Define default privileges that will be applied to objects created in the
future. It does not affect any existing objects.

- Revoke previously created default privileges on objects created in the future.

All new environments are created with a single default privilege, `USAGE` is
granted on all `TYPES` to the `PUBLIC` role. This can be revoked like any other
default privilege.

## Syntax

**GRANT:**

`ALTER DEFAULT PRIVILEGES` defines default privileges that will be applied to
objects created by a role in the future. It does not affect any existing
objects.

Default privileges are specified for a certain object type and can be applied to
all objects of that type, all objects of that type created within a specific set
of databases, or all objects of that type created within a specific set of
schemas. Default privileges are also specified for objects created by a certain
set of roles or by all roles.

```mzsql
ALTER DEFAULT PRIVILEGES
  FOR ROLE <object_creator> [, ...] | ALL ROLES
  [IN SCHEMA <schema_name> [, ...] | IN DATABASE <database_name> [, ...]]
  GRANT [<privilege> [, ...] | ALL [PRIVILEGES]]
  ON TABLES | TYPES | SECRETS | CONNECTIONS | DATABASES | SCHEMAS | CLUSTERS
  TO <target_role> [, ...]
;

```

| Syntax element | Description |
| --- | --- |
| `<object_creator>` | The default privilege will apply to objects created by this role. Use the `PUBLIC` pseudo-role to target objects created by all roles.  |
| **ALL ROLES** | The default privilege will apply to objects created by all roles. This is shorthand for specifying `PUBLIC` as the target role.  |
| **IN SCHEMA** `<schema_name>` | Optional. The default privilege will apply only to objects created in this schema.  |
| **IN DATABASE** `<database_name>` | Optional. The default privilege will apply only to objects created in this database.  |
| `<privilege>` | A specific privilege (e.g., `SELECT`, `USAGE`, `CREATE`). See [Available privileges](#available-privileges).  |
| **ALL [PRIVILEGES]** | All applicable privileges for the provided object type.  |
| **TO** `<target_role>` | The role who will be granted the default privilege. Use the `PUBLIC` pseudo-role to grant privileges to all roles.  |

**REVOKE:**

> **Note:** `ALTER DEFAULT PRIVILEGES` cannot be used to revoke the default owner privileges
> on objects. Those privileges must be revoked manually after the object is
> created. Though owners can always re-grant themselves any privilege on an object
> that they own.

The `REVOKE` variant of `ALTER DEFAULT PRIVILEGES` is used to revoke previously
created default privileges on objects created in the future. It will not revoke
any privileges on objects that have already been created. When revoking a
default privilege, all the fields in the revoke statement (`creator_role`,
`schema_name`, `database_name`, `privilege`, `target_role`) must exactly match
an existing default privilege. The existing default privileges can easily be
viewed by the following query: `SELECT * FROM
mz_internal.mz_show_default_privileges`.

```mzsql
ALTER DEFAULT PRIVILEGES
  FOR ROLE <creator_role> [, ...] | ALL ROLES
  [IN SCHEMA <schema_name> [, ...] | IN DATABASE <database_name> [, ...]]
  REVOKE [<privilege> [, ...] | ALL [PRIVILEGES]]
  ON TABLES | TYPES | SECRETS | CONNECTIONS | DATABASES | SCHEMAS | CLUSTERS
  FROM <target_role> [, ...]
;

```

| Syntax element | Description |
| --- | --- |
| `<creator_role>` | The default privileges for objects created by this role. Use the `PUBLIC` pseudo-role to specify objects created by all roles.  |
| **ALL ROLES** | The default privilege for objects created by all roles. This is shorthand for specifying `PUBLIC` as the target role.  |
| **IN SCHEMA** `<schema_name>` | Optional. The default privileges for objects created in this schema.  |
| **IN DATABASE** `<database_name>` | Optional. The default privilege for objects created in this database.  |
| `<privilege>` | A specific privilege (e.g., `SELECT`, `USAGE`, `CREATE`). See [Available privileges](#available-privileges).  |
| **ALL [PRIVILEGES]** | All applicable privileges for the provided object type.  |
| **FROM** `<target_role>` | The role from whom to remove the default privilege. Use the `PUBLIC` pseudo-role to remove default privileges previously granted to `PUBLIC`.  |

## Details

### Available privileges

**By Privilege:**

| Privilege | Description | Abbreviation | Applies to |
| --- | --- | --- | --- |
| <strong>SELECT</strong> | Permission to read rows from an object. | <code>r</code> | <ul> <li><code>MATERIALIZED VIEW</code></li> <li><code>SOURCE</code></li> <li><code>TABLE</code></li> <li><code>VIEW</code></li> </ul>  |
| <strong>INSERT</strong> | Permission to insert rows into an object. | <code>a</code> | <ul> <li><code>TABLE</code></li> </ul>  |
| <strong>UPDATE</strong> | <p>Permission to modify rows in an object.</p> <p>Modifying rows may also require <strong>SELECT</strong> if a read is needed to determine which rows to update.</p>  | <code>w</code> | <ul> <li><code>TABLE</code></li> </ul>  |
| <strong>DELETE</strong> | <p>Permission to delete rows from an object.</p> <p>Deleting rows may also require <strong>SELECT</strong> if a read is needed to determine which rows to delete.</p>  | <code>d</code> | <ul> <li><code>TABLE</code></li> </ul>  |
| <strong>CREATE</strong> | Permission to create a new objects within the specified object. | <code>C</code> | <ul> <li><code>DATABASE</code></li> <li><code>SCHEMA</code></li> <li><code>CLUSTER</code></li> </ul>  |
| <strong>USAGE</strong> | <a name="privilege-usage"></a> Permission to use or reference an object (e.g., schema/type lookup). | <code>U</code> | <ul> <li><code>CLUSTER</code></li> <li><code>CONNECTION</code></li> <li><code>DATABASE</code></li> <li><code>SCHEMA</code></li> <li><code>SECRET</code></li> <li><code>TYPE</code></li> </ul>  |
| <strong>CREATEROLE</strong> | <p>Permission to create/modify/delete roles and manage role memberships for any role in the system.</p> > **Warning:** Roles with the `CREATEROLE` privilege can obtain the privileges of any other > role in the system by granting themselves that role. Avoid granting > `CREATEROLE` unnecessarily. | <code>R</code> | <ul> <li><code>SYSTEM</code></li> </ul>  |
| <strong>CREATEDB</strong> | Permission to create new databases. | <code>B</code> | <ul> <li><code>SYSTEM</code></li> </ul>  |
| <strong>CREATECLUSTER</strong> | Permission to create new clusters. | <code>N</code> | <ul> <li><code>SYSTEM</code></li> </ul>  |
| <strong>CREATENETWORKPOLICY</strong> | Permission to create network policies to control access at the network layer. | <code>P</code> | <ul> <li><code>SYSTEM</code></li> </ul>  |

**By Object:**

| Object | Privileges |
| --- | --- |
| <code>CLUSTER</code> | <ul> <li><code>USAGE</code></li> <li><code>CREATE</code></li> </ul>  |
| <code>CONNECTION</code> | <ul> <li><code>USAGE</code></li> </ul>  |
| <code>DATABASE</code> | <ul> <li><code>USAGE</code></li> <li><code>CREATE</code></li> </ul>  |
| <code>MATERIALIZED VIEW</code> | <ul> <li><code>SELECT</code></li> </ul>  |
| <code>SCHEMA</code> | <ul> <li><code>USAGE</code></li> <li><code>CREATE</code></li> </ul>  |
| <code>SECRET</code> | <ul> <li><code>USAGE</code></li> </ul>  |
| <code>SOURCE</code> | <ul> <li><code>SELECT</code></li> </ul>  |
| <code>SYSTEM</code> | <ul> <li><code>CREATEROLE</code></li> <li><code>CREATEDB</code></li> <li><code>CREATECLUSTER</code></li> <li><code>CREATENETWORKPOLICY</code></li> </ul>  |
| <code>TABLE</code> | <ul> <li><code>INSERT</code></li> <li><code>SELECT</code></li> <li><code>UPDATE</code></li> <li><code>DELETE</code></li> </ul>  |
| <code>TYPE</code> | <ul> <li><code>USAGE</code></li> </ul>  |
| <code>VIEW</code> | <ul> <li><code>SELECT</code></li> </ul>  |

### Compatibility

For PostgreSQL compatibility reasons, you must specify `TABLES` as the object
type for sources, views, and materialized views.

## Examples

```mzsql
ALTER DEFAULT PRIVILEGES FOR ROLE mike GRANT SELECT ON TABLES TO joe;
```

```mzsql
ALTER DEFAULT PRIVILEGES FOR ROLE interns IN DATABASE dev GRANT ALL PRIVILEGES ON TABLES TO intern_managers;
```

```mzsql
ALTER DEFAULT PRIVILEGES FOR ROLE developers REVOKE USAGE ON SECRETS FROM project_managers;
```

```mzsql
ALTER DEFAULT PRIVILEGES FOR ALL ROLES GRANT SELECT ON TABLES TO managers;
```

## Privileges

The privileges required to execute this statement are:

- Role membership in `role_name`.
- `USAGE` privileges on the containing database if `database_name` is specified.
- `USAGE` privileges on the containing schema if `schema_name` is specified.
- _superuser_ status if the _target_role_ is `PUBLIC` or **ALL ROLES** is
  specified.

## Useful views

- [`mz_internal.mz_show_default_privileges`](/sql/system-catalog/mz_internal/#mz_show_default_privileges)
- [`mz_internal.mz_show_my_default_privileges`](/sql/system-catalog/mz_internal/#mz_show_my_default_privileges)

## Related pages

- [`SHOW DEFAULT PRIVILEGES`](../show-default-privileges)
- [`CREATE ROLE`](../create-role)
- [`ALTER ROLE`](../alter-role)
- [`DROP ROLE`](../drop-role)
- [`DROP USER`](../drop-user)
- [`GRANT ROLE`](../grant-role)
- [`REVOKE ROLE`](../revoke-role)
- [`GRANT PRIVILEGE`](../grant-privilege)
- [`REVOKE PRIVILEGE`](../revoke-privilege)

<!-- mz-docs page: sql/alter-index -->

# ALTER INDEX
`ALTER INDEX` changes the parameters of an index.
Use `ALTER INDEX` to:
- Rename an index.

## Syntax

**Rename:**

To rename an index:

```mzsql
ALTER INDEX <name> RENAME TO <new_name>;

```

| Syntax element | Description |
| --- | --- |
| `<name>` | The current name of the index you want to alter.  |
| `<new_name>` | The new name of the index.  |
See also [Renaming restrictions](/sql/identifiers/#renaming-restrictions).

## Privileges

The privileges required to execute this statement are:

- Ownership of the index.

## Related pages

- [`SHOW INDEXES`](/sql/show-indexes)
- [`SHOW CREATE VIEW`](/sql/show-create-view)
- [`SHOW VIEWS`](/sql/show-views)
- [`SHOW SOURCES`](/sql/show-sources)
- [`SHOW SINKS`](/sql/show-sinks)

<!-- mz-docs page: sql/alter-materialized-view -->

# ALTER MATERIALIZED VIEW
`ALTER MATERIALIZED VIEW` changes the parameters of a materialized view.
Use `ALTER MATERIALIZED VIEW` to:

- Rename a materialized view.
- Change owner of a materialized view.
- Change retain history configuration for the materialized view.
- Replace a materialized view. (*Public preview*)

## Syntax

**Rename:**

To rename a materialized view:

```mzsql
ALTER MATERIALIZED VIEW <name> RENAME TO <new_name>;

```

| Syntax element | Description |
| --- | --- |
| `<name>` | The current name of the materialized view you want to alter.  |
| `<new_name>` | The new name of the materialized view.  |
See also [Renaming restrictions](/sql/identifiers/#renaming-restrictions).

**Change owner:**

To change the owner of a materialized view:

```mzsql
ALTER MATERIALIZED VIEW <name> OWNER TO <new_owner_role>;

```

| Syntax element | Description |
| --- | --- |
| `<name>` | The name of the materialized view you want to change ownership of.  |
| `<new_owner_role>` | The new owner of the materialized view.  |
To change the owner of a materialized view, you must be the owner of the materialized view and have
membership in the `<new_owner_role>`. See also [Privileges](#privileges).

**(Re)Set retain history config:**

To set the retention history for a materialized view:

```mzsql
ALTER MATERIALIZED VIEW <name> SET (RETAIN HISTORY [=] FOR <retention_period>);

```

| Syntax element | Description |
| --- | --- |
| `<name>` | The name of the materialized view you want to alter.  |
| `<retention_period>` | ***Private preview.** This option has known performance or stability issues and is under active development.* Duration for which Materialize retains historical data, which is useful to implement [durable subscriptions](/serve-results/durable-subscriptions/#history-retention-period). Accepts positive [interval](/sql/types/interval/) values (e.g. `'1hr'`). Default: `1s`.  |

To reset the retention history to the default for a materialized view:

```mzsql
ALTER MATERIALIZED VIEW <name> RESET (RETAIN HISTORY);

```

| Syntax element | Description |
| --- | --- |
| `<name>` | The name of the materialized view you want to alter.  |

**Replace materialized view:**

> **Public Preview:** This feature is in public preview.

To replace an existing materialized view in-place with a replacement
materialized view:

```mzsql
ALTER MATERIALIZED VIEW <name> APPLY REPLACEMENT <replacement_materialized_view>;

```

| Syntax element | Description |
| --- | --- |
| `<name>` | The name of the materialized view to replace.  |
| `<replacement_materialized_view>` | The name of a replacement materialized view specifically created for the target materialized view. See [`CREATE REPLACEMENT MATERIALIZED VIEW <replacement_view>...FOR <name>...`](/sql/create-materialized-view).  |

## Details

### Replacing a materialized view

> **Public Preview:** This feature is in public preview.

You can use [`CREATE REPLACEMENT MATERIALIZED
VIEW`](/sql/create-materialized-view/) with [`ALTER MATERIALIZED VIEW ... APPLY
REPLACEMENT`](/sql/alter-materialized-view) to replace materialized views
in-place without recreating dependent objects or incurring downtime.

When replacing a materialized view, the operation:

- Replaces the materialized view's definition with that of the replacement
  view and drops the replacement view at the same time.

- Emits a diff representing the changes between the old and new output.

See [Recommended checks before replacing a
view](/sql/alter-materialized-view/#recommended-checks-before-replacing-a-view).

#### Recommended checks before replacing a view

Before applying, verify that the replacement materialized view is hydrated
to avoid downtime:

  ```mzsql
  SELECT
     mv.name,
     h.hydrated
  FROM mz_catalog.mz_materialized_views AS mv
  JOIN mz_internal.mz_hydration_statuses AS h ON (mv.id = h.object_id)
  WHERE mv.name = '<replacement_view>';
  ```

#### Considerations

When applying the replacement, dependent objects must process the diff
emitted by the operation. Depending on the size of the changes, this may
cause temporary CPU and memory spikes.

#### Troubleshooting

**Issue:** Command does not return.

**Common cause:** The original materialized view is lagging behind the replacement. If
the original is lagging behind the replacement, the command waits for the
original view to catch up.

**Action:** Cancel the command and check whether the original materialized view is
lagging behind the replacement.

To check whether the original materialized view is lagging behind the replacement, run
the following query to check their write frontiers, substituting the names
of your original and replacement materialized views.

```mzsql
SELECT o.name, f.write_frontier
FROM mz_objects o, mz_cluster_replica_frontiers f
WHERE o.name in ('<view>', '<view_replacement>')
AND f.object_id = o.id;
```

If the original materialized view is behind, rerun the query to check the progress of the
original materialized view. If the rate of advancement suggests that catch
up will take an extended period of time, it is recommended to drop the
replacement view.

## Privileges

The privileges required to execute this statement are:

- Ownership of the materialized view.
- In addition, to change owners:
  - Role membership in `new_owner`.
  - `CREATE` privileges on the containing schema if the materialized view is
  namespaced by a schema.
- In addition, to apply a replacement:
  - Ownership of the replacement materialized view.

## Examples

### Replace a materialized view

> **Public Preview:** This feature is in public preview.

A replacement materialized view can only be applied to the target materialized
view specified in the `FOR` clause of the [`CREATE REPLACEMENT MATERIALIZED
VIEW`](/sql/create-materialized-view/) statement.

#### Example Prerequisite

The following example creates a replacement materialized view
`winning_bids_replacement` for the `winning_bids` materialized view. The
replacement view specifies a different filter `mz_now() > a.end_time` than
the existing view `mz_now() >= a.end_time`.
```mzsql
CREATE REPLACEMENT MATERIALIZED VIEW winning_bids_replacement
FOR winning_bids AS
SELECT DISTINCT ON (a.id) b.*, a.item, a.seller
FROM auctions AS a
JOIN bids AS b
  ON a.id = b.auction_id
WHERE b.bid_time < a.end_time
  AND mz_now() > a.end_time
ORDER BY a.id,
  b.amount DESC,
  b.bid_time,
  b.buyer;

```

The replacement view hydrates in the background.

#### Apply the replacement

Assume that `winning_bids_replacement` is hydrated to avoid downtime (see
[Recommended checks before replacing a
view](/sql/alter-materialized-view/#recommended-checks-before-replacing-a-view)
for details).

The following example replaces the `winning_bids` materialized view
with `winning_bids_replacement`:
```mzsql
ALTER MATERIALIZED VIEW winning_bids
APPLY REPLACEMENT winning_bids_replacement;

```

For a step-by-step tutorial on replacing a materialized view, see [Replace
materialized views
guide](/transform-data/updating-materialized-views/replace-materialized-view/).

## Related pages

- [`CREATE MATERIALIZED VIEW`](/sql/create-materialized-view)
- [`SHOW MATERIALIZED VIEWS`](/sql/show-materialized-views)
- [`SHOW CREATE MATERIALIZED VIEW`](/sql/show-create-materialized-view)
- [`DROP MATERIALIZED VIEW`](/sql/drop-materialized-view)

<!-- mz-docs page: sql/alter-network-policy -->

# ALTER NETWORK POLICY (Cloud)
`ALTER NETWORK POLICY` alters an existing network policy.
*Available for Materialize Cloud only*

`ALTER NETWORK POLICY` alters an existing network policy. Network policies are
part of Materialize's framework for [access control](/security/cloud/).

Changes to a network policy will only affect new connections
and **will not** terminate active connections.

## Syntax

```mzsql
ALTER NETWORK POLICY <name> SET (
  RULES (
    <rule_name> (action='allow', direction='ingress', address=<address>)
    [, ...]
  )
)
;

```

| Syntax element | Description |
| --- | --- |
| `<name>` | The name of the network policy to modify.  |
| `<rule_name>` | The name for the network policy rule. Must be unique within the network policy.  |
| `<address>` | The Classless Inter-Domain Routing (CIDR) block to which the rule applies.  |

## Details

### Pre-installed network policy

When you enable a Materialize region, a default network policy named `default`
will be pre-installed. This policy has a wide open ingress rule `allow
0.0.0.0/0`. You can modify or drop this network policy at any time.

> **Note:** The default value for the `network_policy` session parameter is `default`.
> Before dropping the `default` network policy, a _superuser_ (i.e. `Organization
> Admin`) must run [`ALTER SYSTEM SET network_policy`](/sql/alter-system-set) to
> change the default value.

### Lockout prevention

To prevent lockout, the IP of the active user is validated against the policy
changes requested. This prevents users from modifying network policies in a way
that could lock them out of the system.

## Privileges

The privileges required to execute this statement are:

- Ownership of the network policy.

## Examples

```mzsql
CREATE NETWORK POLICY office_access_policy (
  RULES (
    new_york (action='allow', direction='ingress',address='1.2.3.4/28'),
    minnesota (action='allow',direction='ingress',address='2.3.4.5/32')
  )
);
```

```mzsql
ALTER NETWORK POLICY office_access_policy SET (
  RULES (
    new_york (action='allow', direction='ingress',address='1.2.3.4/28'),
    minnesota (action='allow',direction='ingress',address='2.3.4.5/32'),
    boston (action='allow',direction='ingress',address='4.5.6.7/32')
  )
);
```

```mzsql
ALTER SYSTEM SET network_policy = office_access_policy;
```

## Related pages
- [`CREATE NETWORK POLICY`](../create-network-policy)
- [`DROP NETWORK POLICY`](../drop-network-policy)

<!-- mz-docs page: sql/alter-role -->

# ALTER ROLE
`ALTER ROLE` alters the attributes of an existing role.
`ALTER ROLE` alters the attributes of an existing role.[^1]

[^1]: Materialize does not support the `SET ROLE` command.

## Syntax

**Cloud:**

The following syntax is used to alter a role in Materialize Cloud.

```mzsql
ALTER ROLE <role_name>
[[WITH] INHERIT]
[SET <config> =|TO <value|DEFAULT> ]
[RESET <config>];

```

| Syntax element | Description |
| --- | --- |
| `INHERIT` | *Optional.* If specified, grants the role the ability to inherit privileges of other roles. *Default.*  |
| `SET <name> TO <value\|DEFAULT>` | *Optional.* If specified, sets the configuration parameter for the role to the `<value>` or if the value specified is `DEFAULT`, the system's default (equivalent to `ALTER ROLE ... RESET <name>`).  To view the configuration parameter defaults for a role, see [`mz_role_parameters`](/sql/system-catalog/mz_catalog#mz_role_parameters).  {{< note >}}  - Altering the configuration parameter for a role only affects **new sessions**. - Role configuration parameters are **not inherited**.  {{< /note >}}  |
| `RESET <name>` | *Optional.* If specified, resets the configuration parameter for the role to the system's default.  To view the configuration parameter defaults for a role, see [`mz_role_parameters`](/sql/system-catalog/mz_catalog#mz_role_parameters).  {{< note >}}  - Altering the configuration parameter for a role only affects **new sessions**. - Role configuration parameters are **not inherited**.  {{< /note >}}  |

**Note:**
- Materialize Cloud does not support the `NOINHERIT` option for `ALTER
ROLE`.
- Materialize Cloud does not support the `LOGIN` and `SUPERUSER` attributes
  for `ALTER ROLE`.  See [Organization
  roles](/security/cloud/users-service-accounts/#organization-roles)
  instead.
- Materialize Cloud does not use role attributes to determine a role's
ability to alter top level objects such as databases and other roles.
Instead, Materialize Cloud uses system level privileges. See [GRANT
PRIVILEGE](../grant-privilege) for more details.

**Self-Managed:**

The following syntax is used to alter a role in Materialize Self-Managed.

```mzsql
ALTER ROLE <role_name>
[WITH]
  [ SUPERUSER | NOSUPERUSER ]
  [ LOGIN | NOLOGIN ]
  [ INHERIT | NOINHERIT ]
  [ PASSWORD <text> ]]
[SET <name> TO <value|DEFAULT> ]
[RESET <name>]
;

```

| Syntax element | Description |
| --- | --- |
| `INHERIT` | *Optional.* If specified, grants the role the ability to inherit privileges of other roles. *Default.*  |
| `LOGIN` | *Optional.* If specified, allows a role to login via the PostgreSQL or web endpoints  |
| `NOLOGIN` | *Optional.* If specified, prevents a role from logging in. This is the default behavior if `LOGIN` is not specified.  |
| `SUPERUSER` | *Optional.* If specified, grants the role superuser privileges.  |
| `NOSUPERUSER` | *Optional.* If specified, prevents the role from having superuser privileges. This is the default behavior if `SUPERUSER` is not specified.  |
| `PASSWORD` | ***Public Preview***  *Optional.* This feature may have minor stability issues. If specified, allows you to set a password for the role.  |
| `SET <name> TO <value\|DEFAULT>` | *Optional.* If specified, sets the configuration parameter for the role to the `<value>` or if the value specified is `DEFAULT`, the system's default (equivalent to `ALTER ROLE ... RESET <name>`).  To view the configuration parameter defaults for a role, see [`mz_role_parameters`](/sql/system-catalog/mz_catalog#mz_role_parameters).  {{< note >}}  - Altering the configuration parameter for a role only affects **new sessions**. - Role configuration parameters are **not inherited**.  {{< /note >}}  |
| `RESET <name>` | *Optional.* If specified, resets the configuration parameter for the role to the system's default.  To view the configuration parameter defaults for a role, see [`mz_role_parameters`](/sql/system-catalog/mz_catalog#mz_role_parameters).  {{< note >}}  - Altering the configuration parameter for a role only affects **new sessions**. - Role configuration parameters are **not inherited**.  {{< /note >}}  |

**Note:**
- Self-Managed Materialize does not support the `NOINHERIT` option for
`ALTER ROLE`.
- With the exception of the `SUPERUSER` attribute, Self-Managed Materialize
does not use role attributes to determine a role's ability to create top
level objects such as databases and other roles. Instead, Self-Managed
Materialize uses system level privileges. See [GRANT
PRIVILEGE](../grant-privilege) for more details.

## Restrictions

You may not specify redundant or conflicting sets of options. For example,
Materialize will reject the statement `ALTER ROLE ... INHERIT INHERIT`.

## Examples

#### Altering the attributes of a role

```mzsql
ALTER ROLE rj INHERIT;
```
```mzsql
SELECT name, inherit FROM mz_roles WHERE name = 'rj';
```
```nofmt
rj  true
```

#### Setting configuration parameters for a role

```mzsql
SHOW cluster;
quickstart

ALTER ROLE rj SET cluster TO rj_compute;

-- Role parameters only take effect for new sessions.
SHOW cluster;
quickstart

-- Start a new SQL session with the role 'rj'.
SHOW cluster;
rj_compute

-- In a new SQL session with a role that is not 'rj'.
SHOW cluster;
quickstart
```

#### Making a role a superuser  (Self-Managed)

Unlike regular roles, superusers have unrestricted access to all objects in the system and can perform any action on them.

```mzsql
ALTER ROLE rj SUPERUSER;
```

To verify that the role has superuser privileges, you can query the `pg_authid` system catalog:

```mzsql
SELECT name, rolsuper FROM pg_authid WHERE rolname = 'rj';
```

```nofmt
rj  t
```

#### Removing the superuser attribute from a role (Self-Managed)

NOSUPERUSER will remove the superuser attribute from a role, preventing it from having unrestricted access to all objects in the system.

```mzsql
ALTER ROLE rj NOSUPERUSER;
```

```mzsql
SELECT name, rolsuper FROM pg_authid WHERE rolname = 'rj';
```

```nofmt
rj  f
```

#### Removing a role's password (Self-Managed)

> **Warning:** Setting a NULL password removes the password.

```mzsql
ALTER ROLE rj PASSWORD NULL;
```

#### Changing a role's password (Self-Managed)

```mzsql
ALTER ROLE rj PASSWORD 'new_password';
```
## Privileges

The privileges required to execute this statement are:

- `CREATEROLE` privileges on the system.

## Related pages

- [`CREATE ROLE`](../create-role)
- [`DROP ROLE`](../drop-role)
- [`DROP USER`](../drop-user)
- [`GRANT ROLE`](../grant-role)
- [`REVOKE ROLE`](../revoke-role)
- [`ALTER OWNER`](/sql/#rbac)
- [`GRANT PRIVILEGE`](../grant-privilege)
- [`REVOKE PRIVILEGE`](../revoke-privilege)

<!-- mz-docs page: sql/alter-schema -->

# ALTER SCHEMA
`ALTER SCHEMA` change properties of a schema
Use `ALTER SCHEMA` to:
- Swap the name of a schema with that of another schema.
- Rename a schema.
- Change owner of a schema.

## Syntax

**Swap with:**

To swap the name of a schema with that of another schema:

```mzsql
ALTER SCHEMA <schema1> SWAP WITH <schema2>;

```

| Syntax element | Description |
| --- | --- |
| `<schema1>` | The name of the schema you want to swap.  |
| `<schema2>` | The name of the other schema you want to swap with.  |

**Rename schema:**

To rename a schema:

```mzsql
ALTER SCHEMA <name> RENAME TO <new_name>;

```

| Syntax element | Description |
| --- | --- |
| `<name>` | The current name of the schema.  |
| `<new_name>` | The new name of the schema.  |
See also [Renaming restrictions](/sql/identifiers/#renaming-restrictions).

**Change owner to:**

To change the owner of a schema:

```mzsql
ALTER SCHEMA <name> OWNER TO <new_owner_role>;

```

| Syntax element | Description |
| --- | --- |
| `<name>` | The name of the schema you want to change ownership of.  |
| `<new_owner_role>` | The new owner of the schema.  |
To change the owner of a schema, you must be the owner of the schema and have
membership in the `<new_owner_role>`. See also [Privileges](#privileges).

## Examples

### Swap schema names

Swapping two schemas is useful for a blue/green deployment. The following swaps
the names of the `blue` and `green` schemas.

```mzsql
CREATE SCHEMA blue;
CREATE TABLE blue.numbers (n int);

CREATE SCHEMA green;
CREATE TABLE green.tags (tag text);

ALTER SCHEMA blue SWAP WITH green;

-- The schema which was previously named 'green' is now named 'blue'.
SELECT * FROM blue.tags;
```

## Privileges

The privileges required to execute this statement are:

- Ownership of the schema.
- In addition,
  - To swap with another schema:
    - Ownership of the other schema
  - To change owners:
    - Role membership in `new_owner`.
    - `CREATE` privileges on the containing database.

## See also

- [`SHOW CREATE VIEW`](/sql/show-create-view)
- [`SHOW VIEWS`](/sql/show-views)
- [`SHOW SOURCES`](/sql/show-sources)
- [`SHOW INDEXES`](/sql/show-indexes)
- [`SHOW SECRETS`](/sql/show-secrets)
- [`SHOW SINKS`](/sql/show-sinks)

<!-- mz-docs page: sql/alter-secret -->

# ALTER SECRET
`ALTER SECRET` changes the contents of a secret.
Use `ALTER SECRET` to:

- Change the value of the secret.
- Rename a secret.
- Change owner of a secret.

## Syntax

**Change value:**

To change the value of a secret:

```mzsql
ALTER SECRET [IF EXISTS] <name> AS <value>;

```

| Syntax element | Description |
| --- | --- |
| `<name>` | The identifier of the secret you want to alter.  |
| `<value>` | The new value for the secret. The _value_ expression may not reference any relations, and must be implicitly castable to `bytea`.  |

**Rename:**

To rename a secret:

```mzsql
ALTER SECRET [IF EXISTS] <name> RENAME TO <new_name>;

```

| Syntax element | Description |
| --- | --- |
| `<name>` | The current name of the secret.  |
| `<new_name>` | The new name of the secret.  |
See also [Renaming restrictions](/sql/identifiers/#renaming-restrictions).

**Change owner:**

To change the owner of a secret:

```mzsql
ALTER SECRET [IF EXISTS] <name> OWNER TO <new_owner_role>;

```

| Syntax element | Description |
| --- | --- |
| `<name>` | The name of the secret you want to change ownership of.  |
| `<new_owner_role>` | The new owner of the secret.  |
To change the owner, you must be a current owner as well as have membership in
the `<new_owner_role>`.

## Details

### Changing the secret value

After an `ALTER SECRET` command is executed:

  * Future [`CREATE CONNECTION`], [`CREATE SOURCE`], and [`CREATE SINK`]
    commands will use the new value of the secret immediately.

  * Running sources and sinks that reference the secret will **not** immediately
    use the new value of the secret. Sources and sinks may cache the old secret
    value for several weeks.

    To force a running source or sink to refresh its secrets, drop and recreate
    all replicas of the cluster hosting the source or sink.

    For a managed cluster:

    ```
    ALTER CLUSTER storage_cluster SET (REPLICATION FACTOR = 0);
    ALTER CLUSTER storage_cluster SET (REPLICATION FACTOR = 1);
    ```

    For an unmanaged cluster:

    ```
    DROP CLUSTER REPLICA storage_cluster.r1;
    CREATE CLUSTER REPLICA storage_cluster.r1 (SIZE = '<original size>');
        ```

## Examples

```mzsql
ALTER SECRET kafka_ca_cert AS decode('c2VjcmV0Cg==', 'base64');
```

## Privileges

The privileges required to execute this statement are:

- Ownership of the secret being altered.
- In addition, to change owners:
  - Role membership in `new_owner`.
  - `CREATE` privileges on the containing schema if the secret is namespaced
  by a schema.

## Related pages

- [`SHOW SECRETS`](/sql/show-secrets)
- [`DROP SECRET`](/sql/drop-secret)

[`CREATE CONNECTION`]: /sql/create-connection/
[`CREATE SOURCE`]: /sql/create-source
[`CREATE SINK`]: /sql/create-sink
[`ALTER SOURCE`]: /sql/alter-source
[`ALTER SINK`]: /sql/alter-sink

<!-- mz-docs page: sql/alter-sink -->

# ALTER SINK
`ALTER SINK` allows cutting a sink over to a new upstream relation without causing disruption to downstream consumers.
Use `ALTER SINK` to:
- Change the relation you want to sink from. This is useful in the context of
[blue/green deployments](/developer-tools/dbt/blue-green-deployments/).
- Change the commit interval of an [Iceberg sink](/sql/create-sink/iceberg/).
- Rename a sink.
- Change owner of a sink.

## Syntax

**Change sink from relation:**

### Change sink from relation

To change the relation you want to sink from:

```mzsql
ALTER SINK <name> SET FROM <relation_name>;

```

| Syntax element | Description |
| --- | --- |
| `<name>`  | The name of the sink you want to change.  |
| `<relation_name>`  | The name of the relation you want to sink from.  |

**Change commit interval:**

### Change commit interval

*Available starting in v26.34**

To change the commit interval of an [Iceberg sink](/sql/create-sink/iceberg/):

```mzsql
ALTER SINK <name> SET (COMMIT INTERVAL = '<interval>');

```

| Syntax element | Description |
| --- | --- |
| `<name>`  | The name of the sink you want to change.  |
| `<interval>`  | The new commit interval, for example `'1m'`. Only [Iceberg sinks](/sql/create-sink/iceberg/) support a commit interval.  |

**Rename:**

### Rename

To rename a sink:

```mzsql
ALTER SINK <name> RENAME TO <new_name>;

```

| Syntax element | Description |
| --- | --- |
| `<name>` | The current name of the sink.  |
| `<new_name>` | The new name of the sink.  |
See also [Renaming restrictions](/sql/identifiers/#renaming-restrictions).

**Change owner:**

### Change owner

To change the owner of a sink:

```mzsql
ALTER SINK <name> OWNER TO <new_owner_role>;

```

| Syntax element | Description |
| --- | --- |
| `<name>` | The name of the sink you want to change ownership of.  |
| `<new_owner_role>` | The new owner of the sink.  |
To change the owner, you must be a current owner as well as have membership
in the `<new_owner_role>`.

## Details

### Changing sink from relation

#### Valid schema changes

For `ALTER SINK` to be successful, the newly specified relation must lead to a
valid sink definition with the same conditions as the original `CREATE SINK`
statement.

When using the Avro format with a schema registry, the generated Avro
schema for the new relation must be compatible with the previously published
schema. If that's not the case, the `ALTER SINK` command will succeed, but the
subsequent execution of the sink will result in errors and will not be able to
make progress.

To monitor the status of a sink after an `ALTER SINK` command, navigate to the
respective object page in the [Materialize console](/developer-tools/console/),
or query the [`mz_internal.mz_sink_statuses`](/sql/system-catalog/mz_internal/#mz_sink_statuses)
system catalog view.

#### Cutover timestamp

To alter the upstream relation a sink depends on while ensuring continuity in
data processing, Materialize must pick a consistent cutover timestamp. When you
execute an `ALTER SINK` command, the resulting output will contain:
- all updates that happened before the cutover timestamp for the old
relation, and
- all updates that happened after the cutover timestamp for the new
relation.

> **Note:** To select a consistent timestamp, Materialize must wait for the previous
> definition of the sink to emit results up until the oldest timestamp at which
> the contents of the new upstream relation are known. Attempting to `ALTER` an
> unhealthy sink that can't make progress will result in the command timing out.

#### Cutover scenarios and workarounds

Because Materialize emits updates from the new relation **only** if
they occur after the cutover timestamp, the following scenarios may occur:

##### Scenario 1: Topic contains stale value for a key

Since cutting over a sink to a new upstream relation using `ALTER SINK` does not
emit a snapshot of the new relation, all keys will appear to have the old value
for the key in the previous relation until an update happens to them. At that
point, the current value will be published to the topic.

Consumers of the topic must be prepared to handle an old value for a key, for
example by filling in additional columns with default values.

**Workarounds**:

- Use an intermediary, temporary view to handle the cutover scenario difference.
See [Example: Handle cutover scenarios](#handle-cutover-scenarios).

- Alternatively, forcing an update to all the keys after `ALTER SINK` will force
the sink to re-emit all the updates.

##### Scenario 2: Topic is missing a key that exists in the new relation

As a consequence of not re-emitting a snapshot after `ALTER SINK`, if additional
keys exist in the new relation that are not present in the old one, these will
not be visible in the topic after the cutover. The keys will remain absent until
an update occurs for the keys, at which point Materialize will emit a record to
the topic containing the new value.

**Workarounds**:

- Use an intermediary, temporary view to handle the cutover scenario difference.
See [Example: Handle cutover scenarios](#handle-cutover-scenarios).

- Alternatively, ensure that both the old and the new relations have identical
keyspaces to avoid the scenario.

##### Scenario 3: Topic contains a key that does not exist in the new relation

Materialize does not compare the contents of the old relation with the new
relation when cutting a sink over. This means that, if the old relation
contains additional keys that are not present in the new one, these records
will remain in the topic without a corresponding tombstone record. This may
cause readers to assume that certain keys exist when they don't.

**Workarounds**:

- Use an intermediary, temporary view to handle the cutover scenario difference.
See [Example: Handle cutover scenarios](#handle-cutover-scenarios).

- Alternatively, ensure that both the old and the new relations have identical
keyspaces to avoid the scenario.

### Changing the commit interval

Starting in v26.34, you can change the commit interval of an existing sink.
Changing the commit interval restarts the sink with the new setting. Any data
that was buffered but not yet committed at the time of the change is committed
immediately after the restart. All subsequent commits follow the new interval.

Setting the commit interval to its current value is a no-op and does not restart the sink.
However, values are compared textually rather than by duration.
For example, setting `'1m'` when the current value is `'60s'` counts as a change and restarts the sink.

See [Commit interval tradeoffs](/sql/create-sink/iceberg/#commit-interval-tradeoffs)
for guidance on choosing a value.

### Catalog objects

A sink cannot be created directly on a [catalog object](/sql/system-catalog/).
As a workaround, you can create a materialized view on a catalog object and
create a sink on the materialized view.

## Privileges

The privileges required to execute this statement are:

- Ownership of the sink being altered.
- In addition,
  - To change the sink from relation:
    - `SELECT` privileges on the new relation being written out to an external system.
    - `CREATE` privileges on the cluster maintaining the sink.
    - `USAGE` privileges on all connections and secrets used in the sink definition.
    - `USAGE` privileges on the schemas that all connections and secrets in the
      statement are contained in.
  - To change owners:
    - Role membership in `new_owner`.
    - `CREATE` privileges on the containing schema if the sink is namespaced
  by a schema.

## Examples

### Alter sink

The following example alters a sink originally created from `matview_old` to use
`matview_new` instead.

That is, assume you have a Kafka sink `avro_sink` created from `matview_old`
(See [`CREATE SINK`:Kafka/Redpanda](/sql/create-sink/kafka/) for more
information):
```mzsql
CREATE SINK avro_sink
  FROM matview_old
  INTO KAFKA CONNECTION kafka_connection (TOPIC 'test_avro_topic')
  KEY (key_col)
  FORMAT AVRO USING CONFLUENT SCHEMA REGISTRY CONNECTION csr_connection
  ENVELOPE UPSERT
;

```

To have the sink read from `matview_new` instead of `matview_old`, you can
use `ALTER SINK` to change the `FROM <relation>`:

{{< note >}}
`matview_new` must be compatible with the previously published
schema. Otherwise, the `ALTER SINK` command will succeed, but the
subsequent execution of the sink will result in errors and will not be able
to make progress. See [Valid schema changes](#valid-schema-changes) for
details.
{{< /note >}}
```mzsql
ALTER SINK avro_sink
  SET FROM matview_new
;

```
{{< tip >}}

Because Materialize emits updates from the newly specified relation **only** if
they happen after the cutover timestamp, you might observe the following
scenarios:
- [Topic contains stale value for a
  key](#scenario-1-topic-contains-stale-value-for-a-key)
- [Topic is missing a key that exists in the new relation](#scenario-2-topic-is-missing-a-key-that-exists-in-the-new-relation)
- [Topic contains a key that does not exist in the new relation](#scenario-3-topic-contains-a-key-that-does-not-exist-in-the-new-relation)

For workaround, see [Example: Handle cutover scenarios](#handle-cutover-scenarios)
{{< /tip >}}

### Handle cutover scenarios

Because Materialize emits updates from the newly specified relation **only** if
they happen after the cutover timestamp, you might observe the following
scenarios:
- [Topic contains stale value for a
  key](#scenario-1-topic-contains-stale-value-for-a-key)
- [Topic is missing a key that exists in the new relation](#scenario-2-topic-is-missing-a-key-that-exists-in-the-new-relation)
- [Topic contains a key that does not exist in the new relation](#scenario-3-topic-contains-a-key-that-does-not-exist-in-the-new-relation)

To handle these scenarios, you can first alter sink to an intermediary
materialized view. The intermediary materialized view uses a temporary table
`switch` that switches the view's contents from old relation content to new
relation content. At the time of the switch, Materialize emits the diff of
the changes. Then, after the sink upper has advanced beyond the time of the
switch, you can `ALTER SINK` to the new relation (and remove the temporary
intermediary materialized view and table).

1. For example, create a table `switch` and a temporary materialized view
`transition` that contains either:
- the `matview_old` content if `switch.value` is `false`.
- the `matview_new` content if `switch.value` is `true`.

At first, the `switch.value` is `false`, so the `transition` materialized view contains the `matview_old` content.

   <no value>```mzsql
   CREATE TABLE switch (value bool);
   INSERT INTO switch VALUES (false); -- controls whether we want the new or the old materialized view.

   CREATE MATERIALIZED VIEW transition AS
   (SELECT matview_old.* FROM matview_old JOIN switch ON switch.value = false)
   UNION ALL
   (SELECT matview_new.* FROM matview_new JOIN switch ON switch.value = true)
   ;

   ```

1. `ALTER SINK` to use `transition`, which currently contains `matview_old` content:

   <no value>```mzsql
   ALTER SINK avro_sink SET FROM transition;

   ```

1. Update `switch.value` to `true`, which causes the `transition` materialized view to contain `matview_new` content:

   <no value>```mzsql
   UPDATE switch SET value = true;

   ```

1. Wait for the sink's upper frontier
([`mz_frontiers`](/sql/system-catalog/mz_internal/#mz_frontiers)) to advance
beyond the time of the switch update. Once advanced, alter sink to use
`matview_new`:

   <no value>```mzsql
   -- After sink upper has advanced beyond the time of the switch UPDATE.
   ALTER SINK avro_sink SET FROM matview_new;

   ```

1. Drop the `transition` materialized view and the `switch` table:

   <no value>```mzsql
   DROP MATERIALIZED VIEW transition;
   DROP TABLE switch;

   ```

## See also

- [`CREATE SINK`](/sql/create-sink/)
- [`SHOW SINKS`](/sql/show-sinks)

<!-- mz-docs page: sql/alter-source -->

# ALTER SOURCE
`ALTER SOURCE` changes certain characteristics of a source.
Use `ALTER SOURCE` to:

- Add a subsource to a source.
- Refresh the upstream references available to a source.
- Rename a source.
- Change owner of a source.
- Change retain history configuration for the source.
- Change timestamp interval for the source.

## Syntax

**Add subsource:**

To add the specified upstream table(s) to the specified PostgreSQL/MySQL/SQL Server source:

```mzsql
ALTER SOURCE [IF EXISTS] <name>
  ADD SUBSOURCE|TABLE <table> [AS <subsrc>] [, ...]
  [WITH (<options>)]
;

```

| Syntax element | Description |
| --- | --- |
| `<name>` | The name of the PostgreSQL/MySQL/SQL Server source you want to alter.  |
| `<table>` | The upstream table to add to the source.  |
| **AS** `<subsrc>` | Optional. The name for the subsource in Materialize.  |
| **WITH (TEXT COLUMNS (`<col>` [, ...]))** | Optional. List of columns to decode as `text` for types that are unsupported in Materialize.  |

> **Note:** When you add a new subsource to an existing source ([`ALTER SOURCE ... ADD
> SUBSOURCE ...`](/sql/alter-source/)), Materialize starts the snapshotting
> process for the new subsource. During this snapshotting, the data ingestion for
> the existing subsources for the same source is temporarily blocked. As such, if
> possible, you can resize the cluster to speed up the snapshotting process and
> once the process finishes, resize the cluster for steady-state.

**Refresh references:**

To refresh the list of upstream objects available to a source:

```mzsql
ALTER SOURCE [IF EXISTS] <name> REFRESH REFERENCES;

```

| Syntax element | Description |
| --- | --- |
| `<name>` | The name of the source whose available upstream references you want to refresh.  |
Refreshing references updates the upstream objects Materialize records for
the source in `mz_internal.mz_source_references`. It does not change the
data the source ingests. See [Refreshing available upstream
references](#refreshing-available-upstream-references).

**Rename:**

To rename a source:

```mzsql
ALTER SOURCE <name> RENAME TO <new_name>;

```

| Syntax element | Description |
| --- | --- |
| `<name>` | The current name of the source you want to alter.  |
| `<new_name>` | The new name of the source.  |
See also [Renaming restrictions](/sql/identifiers/#renaming-restrictions).

**Change owner:**

To change the owner of a source:

```mzsql
ALTER SOURCE <name> OWNER TO <new_owner_role>;

```

| Syntax element | Description |
| --- | --- |
| `<name>` | The name of the source you want to change ownership of.  |
| `<new_owner_role>` | The new owner of the source.  |
To change the owner of a source, you must be the owner of the source and have
membership in the `<new_owner_role>`. See also [Privileges](#privileges).

**(Re)Set retain history config:**

To set the retention history for a source:

```mzsql
ALTER SOURCE [IF EXISTS] <name> SET (RETAIN HISTORY [=] FOR <retention_period>);

```

| Syntax element | Description |
| --- | --- |
| `<name>` | The name of the source you want to alter.  |
| `<retention_period>` | ***Private preview.** This option has known performance or stability issues and is under active development.* Duration for which Materialize retains historical data, which is useful to implement [durable subscriptions](/serve-results/durable-subscriptions/#history-retention-period). Accepts positive [interval](/sql/types/interval/) values (e.g. `'1hr'`). Default: `1s`.  |

To reset the retention history to the default for a source:

```mzsql
ALTER SOURCE [IF EXISTS] <name>  RESET (RETAIN HISTORY);

```

| Syntax element | Description |
| --- | --- |
| `<name>` | The name of the source you want to alter.  |

**(Re)Set timestamp interval:**

To set the timestamp interval for a source:

```mzsql
ALTER SOURCE [IF EXISTS] <name> SET (TIMESTAMP INTERVAL [=] <interval>);

```

| Syntax element | Description |
| --- | --- |
| `<name>` | The name of the source you want to alter.  |
| `<interval>` | The interval at which timestamps are assigned to the data read from this source. Accepts positive [interval](/sql/types/interval/) values (e.g. `'500ms'`, `'1s'`). The value must be between the system parameters `min_timestamp_interval` and `max_timestamp_interval`. Default: `1s`.  |

To reset the timestamp interval to the system default for a source:

```mzsql
ALTER SOURCE [IF EXISTS] <name> RESET (TIMESTAMP INTERVAL);

```

| Syntax element | Description |
| --- | --- |
| `<name>` | The name of the source you want to alter.  |

## Context

### Adding subsources to a PostgreSQL/MySQL/SQL Server source

Note that using a combination of dropping and adding subsources lets you change
the schema of the PostgreSQL/MySQL/SQL Server tables that are ingested.

> **Important:** When you add a new subsource to an existing source ([`ALTER SOURCE ... ADD
> SUBSOURCE ...`](/sql/alter-source/)), Materialize starts the snapshotting
> process for the new subsource. During this snapshotting, the data ingestion for
> the existing subsources for the same source is temporarily blocked. As such, if
> possible, you can resize the cluster to speed up the snapshotting process and
> once the process finishes, resize the cluster for steady-state.

### Dropping subsources from a PostgreSQL/MySQL/SQL Server source

Dropping a subsource prevents Materialize from ingesting any data from it, in
addition to dropping any state that Materialize previously had for the table
(such as its contents).

If a subsource encounters a deterministic error, such as an incompatible schema
change (e.g. dropping an ingested column), you can drop the subsource. If you
want to ingest it with its new schema, you can then add it as a new subsource.

You cannot drop the "progress subsource".

### Refreshing available upstream references

When you create a source, Materialize records the objects that source could read
in `mz_internal.mz_source_references`. For a PostgreSQL, MySQL, or SQL Server
source, that list comes from querying the upstream database. Either way the list
is a snapshot taken at creation time, and Materialize does not update it as the
upstream changes. A table added to a PostgreSQL publication after the source was
created, for example, does not show up there.

`ALTER SOURCE ... REFRESH REFERENCES` recomputes that list and replaces the
recorded references for the source. Objects that have appeared since the last
refresh are added, and objects that no longer exist are removed.

Refreshing references only updates this metadata. It neither starts nor stops
ingesting anything. To ingest a newly available object, create a table from the
source with [`CREATE TABLE ... FROM SOURCE`](/sql/create-table/); to
stop ingesting one, drop the corresponding table.

The statement is accepted for any source that ingests from an external system,
but what it recomputes depends on the source type:

| Source type | Effect of a refresh |
| --- | --- |
| PostgreSQL, MySQL, SQL Server | Queries the upstream database for the tables the source can read. |
| Kafka | No practical effect. The only reference is the topic the source was configured with. |
| Load generator | Re-reads the load generator's built-in views, which change only when a Materialize upgrade adds views. |

[Webhook sources](/sql/create-source/webhook/), which are written to rather than
read from, return an error.

For PostgreSQL, MySQL, and SQL Server sources, the refresh connects to the
upstream database, so it fails if that database is unreachable or the source's
[connection](/sql/create-connection/) is no longer valid. For PostgreSQL
sources, it also fails if the source's publication is empty.

## Examples

### Adding subsources

```mzsql
ALTER SOURCE pg_src ADD SUBSOURCE tbl_a, tbl_b AS b WITH (TEXT COLUMNS [tbl_a.col]);
```

> **Important:** When you add a new subsource to an existing source ([`ALTER SOURCE ... ADD
> SUBSOURCE ...`](/sql/alter-source/)), Materialize starts the snapshotting
> process for the new subsource. During this snapshotting, the data ingestion for
> the existing subsources for the same source is temporarily blocked. As such, if
> possible, you can resize the cluster to speed up the snapshotting process and
> once the process finishes, resize the cluster for steady-state.

### Dropping subsources

To drop a subsource, use the [`DROP SOURCE`](/sql/drop-source/) command:

```mzsql
DROP SOURCE tbl_a, b CASCADE;
```

### Refreshing references

To refresh the upstream objects Materialize records for a source:

```mzsql
ALTER SOURCE pg_src REFRESH REFERENCES;
```

To then inspect the refreshed references:

```mzsql
SELECT refs.namespace, refs.name, refs.columns, refs.updated_at
FROM mz_internal.mz_source_references refs, mz_sources s
WHERE s.name = 'pg_src'
AND refs.source_id = s.id;
```

### Changing the timestamp interval

To set a custom timestamp interval for a source:

```mzsql
ALTER SOURCE kafka_src SET (TIMESTAMP INTERVAL = '500ms');
```

To reset the timestamp interval to the system default:

```mzsql
ALTER SOURCE kafka_src RESET (TIMESTAMP INTERVAL);
```

## Privileges

The privileges required to execute this statement are:

- Ownership of the source being altered.
- In addition, to change owners:
   - Role membership in `new_owner`.
  - `CREATE` privileges on the containing schema if the source is namespaced
  by a schema.

## See also

- [`CREATE SOURCE`](/sql/create-source/)
- [`CREATE TABLE ... FROM SOURCE`](/sql/create-table/)
- [`DROP SOURCE`](/sql/drop-source/)
- [`SHOW SOURCES`](/sql/show-sources)

<!-- mz-docs page: sql/alter-system-reset -->

# ALTER SYSTEM RESET
Globally reset a configuration parameter to its default value.
Use `ALTER SYSTEM RESET` to globally restore the value of a configuration
parameter to its default value. This command is an alternative spelling for
[`ALTER SYSTEM SET...TO DEFAULT`](../alter-system-set).

To see the current value of a configuration parameter, use [`SHOW`](../show).

## Syntax

```mzsql
ALTER SYSTEM RESET <config>;
```

Syntax element | Description
---------------|------------
`<config>`     | The configuration parameter's name.

### Key configuration parameters

Name                                        | Default value             |  Description                                                          | Modifiable?
--------------------------------------------|---------------------------|-----------------------------------------------------------------------|--------------
`cluster`                                   | `quickstart`              | The current cluster.                                                  | Yes
`cluster_replica`                           |                           | The target cluster replica for `SELECT` queries.                      | Yes
`database`                                  | `materialize`             | The current database.                                                 | Yes
`search_path`                               | `public`                  | The schema search order for names that are not schema-qualified.      | Yes
`transaction_isolation`                     | `strict serializable`     | The transaction isolation level. For more information, see [Isolation level](/serve-results/isolation-level/). <br/><br/> Accepts values: `serializable`, `strict serializable`

, `bounded staleness <duration>` (for example, `bounded staleness 5s`)

. | Yes

### Other configuration parameters

Name                                        | Default value             |  Description                                                                                                                                                           | Modifiable?
--------------------------------------------|---------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------
`allowed_cluster_replica_sizes`             | *Varies*                  | The allowed sizes when creating a new cluster replica.                                                                                                                 | [Contact support]
`application_name`                          |                           | The application name to be reported in statistics and logs. This parameter is typically set by an application upon connection to Materialize (e.g. `psql`).            | Yes
`auto_route_catalog_queries`                | `true`                    | Boolean flag indicating whether to force queries that depend only on system tables to run on the `mz_catalog_server` cluster for improved performance.                 | Yes
`client_encoding`                           | `UTF8`                    | The client's character set encoding. The only supported value is `UTF-8`.                                                                                              | Yes
`client_min_messages`                       | `notice`                  | The message levels that are sent to the client. <br/><br/> Accepts values: `debug5`, `debug4`, `debug3`, `debug2`, `debug1`, `log`, `notice`, `warning`, `error`. Each level includes all the levels that follow it. | Yes
`datestyle`                                 | `ISO, MDY`                | The display format for date and time values. The only supported value is `ISO, MDY`.                                                                                   | Yes
`default_timestamp_interval`                | `1s`                      | The interval at which timestamps are assigned to data ingested from sources and tables. New sources are created with this value unless overridden by the `TIMESTAMP INTERVAL` option of [`CREATE SOURCE`](/sql/create-source/). Accepts positive [interval](/sql/types/interval/) values (e.g. `'500ms'`, `'1s'`). This setting applies only when creating sources; changing this value does not affect existing sources. For existing sources, see [`ALTER SOURCE`](/sql/alter-source/). | [Contact support]
`emit_introspection_query_notice`           | `true`                    | Whether to print a notice when querying replica introspection relations.                                                                                               | Yes
`emit_timestamp_notice`                     | `false`                   | Boolean flag indicating whether to send a `notice` specifying query timestamps.                                                                                        | Yes
`emit_trace_id_notice`                      | `false`                   | Boolean flag indicating whether to send a `notice` specifying the trace ID, when available.                                                                            | Yes
`enable_rbac_checks`                        | `true`                    | Boolean flag indicating whether to apply RBAC checks before executing statements.                                                                                      | Yes
`enable_session_rbac_checks`                | `false`                   | Boolean flag indicating whether RBAC is enabled for the current session.                                                                                               | No
`extra_float_digits`                        | `1`                       | Adjusts the number of digits displayed for floating-point values.                                                                                                      | Yes
`failpoints`                                |                           | Allows failpoints to be dynamically activated.                                                                                                                         | No
`idle_in_transaction_session_timeout`       | `120s`                    | The maximum allowed duration that a session can sit idle in a transaction before being terminated. If this value is specified without units, it is taken as milliseconds (`ms`). A value of zero disables the timeout. | Yes
`integer_datetimes`                         | `true`                    | Boolean flag indicating whether the server uses 64-bit-integer dates and times.                                                                                        | No
`intervalstyle`                             | `postgres`                | The display format for interval values. The only supported value is `postgres`.                                                                                        | Yes
`is_superuser`                              |                           | Reports whether the current session is a _superuser_ with admin privileges.                                                                                            | No
`max_aws_privatelink_connections`           | `0`                       | The maximum number of AWS PrivateLink connections in the region, across all schemas.                                                                                   | [Contact support]
`max_clusters`                              | `10`                      | The maximum number of clusters in the region                                                                                                                           | [Contact support]
`max_connections`                           | `5000`                    | The maximum number of concurrent connections in the region                                                                                                             | [Contact support]
`max_credit_consumption_rate`               | `1024`                    | The maximum rate of credit consumption in a region. Credits are consumed based on the size of cluster replicas in use.                                                 | [Contact support]
`max_databases`                             | `1000`                    | The maximum number of databases in the region.                                                                                                                         | [Contact support]
`max_identifier_length`                     | `255`                     | The maximum length in bytes of object identifiers.                                                                                                                     | No
`max_kafka_connections`                     | `1000`                    | The maximum number of Kafka connections in the region, across all schemas.                                                                                             | [Contact support]
`max_mysql_connections`                     | `1000`                    | The maximum number of MySQL connections in the region, across all schemas.                                                                                             | [Contact support]
`max_objects_per_schema`                    | `1000`                    | The maximum number of objects in a schema.                                                                                                                             | [Contact support]
`max_postgres_connections`                  | `1000`                    | The maximum number of PostgreSQL connections in the region, across all schemas.                                                                                        | [Contact support]
`max_query_result_size`                     | `1073741824`              | The maximum size in bytes for a single query's result.                                                                                                                 | Yes
`max_replicas_per_cluster`                  | `5`                       | The maximum number of replicas of a single cluster                                                                                                                     | [Contact support]
`max_result_size`                           | `1 GiB`                   | The maximum size in bytes for a single query's result.                                                                                                                 | [Contact support]
`max_roles`                                 | `1000`                    | The maximum number of roles in the region.                                                                                                                             | [Contact support]
`max_schemas_per_database`                  | `1000`                    | The maximum number of schemas in a database.                                                                                                                           | [Contact support]
`max_secrets`                               | `100`                     | The maximum number of secrets in the region, across all schemas.                                                                                                       | [Contact support]
`max_sinks`                                 | `1000`                    | The maximum number of sinks in the region, across all schemas.                                                                                                         | [Contact support]
`max_sources`                               | `25`                      | The maximum number of sources in the region, across all schemas.                                                                                                       | [Contact support]
`max_tables`                                | `200`                     | The maximum number of tables in the region, across all schemas                                                                                                         | [Contact support]
`max_timestamp_interval`                    | `1s`                      | The upper bound for the `TIMESTAMP INTERVAL` option of [`CREATE SOURCE`](/sql/create-source/) and [`ALTER SOURCE`](/sql/alter-source/). Statements that request a timestamp interval larger than this value are rejected. Accepts positive [interval](/sql/types/interval/) values (e.g. `'500ms'`, `'1s'`). | [Contact support]
`min_timestamp_interval`                    | `1s`                      | The lower bound for the `TIMESTAMP INTERVAL` option of [`CREATE SOURCE`](/sql/create-source/) and [`ALTER SOURCE`](/sql/alter-source/). Statements that request a timestamp interval smaller than this value are rejected. Accepts positive [interval](/sql/types/interval/) values (e.g. `'500ms'`, `'1s'`). | [Contact support]
`mz_version`                                | Version-dependent         | Shows the Materialize server version.                                                                                                                                  | No
`network_policy`                            | `default`                 | The default network policy for the region. | Yes
`real_time_recency`                         | `false`                   | Boolean flag indicating whether [real-time recency](/serve-results/isolation-level/#real-time-recency) is enabled for the current session.                               | [Contact support]
`real_time_recency_timeout`                 | `10s`                     | Sets the maximum allowed duration of `SELECT` statements that actively use [real-time recency](/serve-results/isolation-level/#real-time-recency). If this value is specified without units, it is taken as milliseconds (`ms`).                      | Yes
`server_version_num`                        | Version-dependent         | The PostgreSQL compatible server version as an integer.                                                                                                                | No
`server_version`                            | Version-dependent         | The PostgreSQL compatible server version.                                                                                                                              | No
`sql_safe_updates`                          | `false`                   | Boolean flag indicating whether to prohibit SQL statements that may be overly destructive.                                                                             | Yes
`standard_conforming_strings`               | `true`                    | Boolean flag indicating whether ordinary string literals (`'...'`) should treat backslashes literally. The only supported value is `true`.                             | Yes
`statement_timeout`                         | `10s`                     | The maximum allowed duration of the read portion of write operations; i.e., the `SELECT` portion of `INSERT INTO ... (SELECT ...)`; the `WHERE` portion of `UPDATE ... WHERE ...` and `DELETE FROM ... WHERE ...`. If this value is specified without units, it is taken as milliseconds (`ms`). | Yes
`timezone`                                  | `UTC`                     | The time zone for displaying and interpreting timestamps. The only supported value is `UTC`.                                                                           | Yes

[Contact support]: /support

## Privileges

The privileges required to execute this statement are:

- [_Superuser_ privileges](/security/cloud/users-service-accounts/#organization-roles)

## Related pages

- [`SHOW`](../show)
- [`ALTER SYSTEM SET`](../alter-system-set)

<!-- mz-docs page: sql/alter-system-set -->

# ALTER SYSTEM SET
`ALTER SYSTEM SET` globally modifies the value of a configuration parameter.
Use `ALTER SYSTEM SET` to globally modify the value of a configuration parameter.

To see the current value of a configuration parameter, use [`SHOW`](../show).

## Syntax

```mzsql
ALTER SYSTEM SET <config> [TO|=] <value|DEFAULT>
```

Syntax element | Description
---------------|------------
`<config>`              | The name of the configuration parameter to modify.
`<value>`               | The value to assign to the configuration parameter.
**DEFAULT**             | Reset the configuration parameter's default value. Equivalent to [`ALTER SYSTEM RESET`](../alter-system-reset).

### Key configuration parameters

Name                                        | Default value             |  Description                                                          | Modifiable?
--------------------------------------------|---------------------------|-----------------------------------------------------------------------|--------------
`cluster`                                   | `quickstart`              | The current cluster.                                                  | Yes
`cluster_replica`                           |                           | The target cluster replica for `SELECT` queries.                      | Yes
`database`                                  | `materialize`             | The current database.                                                 | Yes
`search_path`                               | `public`                  | The schema search order for names that are not schema-qualified.      | Yes
`transaction_isolation`                     | `strict serializable`     | The transaction isolation level. For more information, see [Isolation level](/serve-results/isolation-level/). <br/><br/> Accepts values: `serializable`, `strict serializable`

, `bounded staleness <duration>` (for example, `bounded staleness 5s`)

. | Yes

### Other configuration parameters

Name                                        | Default value             |  Description                                                                                                                                                           | Modifiable?
--------------------------------------------|---------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------
`allowed_cluster_replica_sizes`             | *Varies*                  | The allowed sizes when creating a new cluster replica.                                                                                                                 | [Contact support]
`application_name`                          |                           | The application name to be reported in statistics and logs. This parameter is typically set by an application upon connection to Materialize (e.g. `psql`).            | Yes
`auto_route_catalog_queries`                | `true`                    | Boolean flag indicating whether to force queries that depend only on system tables to run on the `mz_catalog_server` cluster for improved performance.                 | Yes
`client_encoding`                           | `UTF8`                    | The client's character set encoding. The only supported value is `UTF-8`.                                                                                              | Yes
`client_min_messages`                       | `notice`                  | The message levels that are sent to the client. <br/><br/> Accepts values: `debug5`, `debug4`, `debug3`, `debug2`, `debug1`, `log`, `notice`, `warning`, `error`. Each level includes all the levels that follow it. | Yes
`datestyle`                                 | `ISO, MDY`                | The display format for date and time values. The only supported value is `ISO, MDY`.                                                                                   | Yes
`default_timestamp_interval`                | `1s`                      | The interval at which timestamps are assigned to data ingested from sources and tables. New sources are created with this value unless overridden by the `TIMESTAMP INTERVAL` option of [`CREATE SOURCE`](/sql/create-source/). Accepts positive [interval](/sql/types/interval/) values (e.g. `'500ms'`, `'1s'`). This setting applies only when creating sources; changing this value does not affect existing sources. For existing sources, see [`ALTER SOURCE`](/sql/alter-source/). | [Contact support]
`emit_introspection_query_notice`           | `true`                    | Whether to print a notice when querying replica introspection relations.                                                                                               | Yes
`emit_timestamp_notice`                     | `false`                   | Boolean flag indicating whether to send a `notice` specifying query timestamps.                                                                                        | Yes
`emit_trace_id_notice`                      | `false`                   | Boolean flag indicating whether to send a `notice` specifying the trace ID, when available.                                                                            | Yes
`enable_rbac_checks`                        | `true`                    | Boolean flag indicating whether to apply RBAC checks before executing statements.                                                                                      | Yes
`enable_session_rbac_checks`                | `false`                   | Boolean flag indicating whether RBAC is enabled for the current session.                                                                                               | No
`extra_float_digits`                        | `1`                       | Adjusts the number of digits displayed for floating-point values.                                                                                                      | Yes
`failpoints`                                |                           | Allows failpoints to be dynamically activated.                                                                                                                         | No
`idle_in_transaction_session_timeout`       | `120s`                    | The maximum allowed duration that a session can sit idle in a transaction before being terminated. If this value is specified without units, it is taken as milliseconds (`ms`). A value of zero disables the timeout. | Yes
`integer_datetimes`                         | `true`                    | Boolean flag indicating whether the server uses 64-bit-integer dates and times.                                                                                        | No
`intervalstyle`                             | `postgres`                | The display format for interval values. The only supported value is `postgres`.                                                                                        | Yes
`is_superuser`                              |                           | Reports whether the current session is a _superuser_ with admin privileges.                                                                                            | No
`max_aws_privatelink_connections`           | `0`                       | The maximum number of AWS PrivateLink connections in the region, across all schemas.                                                                                   | [Contact support]
`max_clusters`                              | `10`                      | The maximum number of clusters in the region                                                                                                                           | [Contact support]
`max_connections`                           | `5000`                    | The maximum number of concurrent connections in the region                                                                                                             | [Contact support]
`max_credit_consumption_rate`               | `1024`                    | The maximum rate of credit consumption in a region. Credits are consumed based on the size of cluster replicas in use.                                                 | [Contact support]
`max_databases`                             | `1000`                    | The maximum number of databases in the region.                                                                                                                         | [Contact support]
`max_identifier_length`                     | `255`                     | The maximum length in bytes of object identifiers.                                                                                                                     | No
`max_kafka_connections`                     | `1000`                    | The maximum number of Kafka connections in the region, across all schemas.                                                                                             | [Contact support]
`max_mysql_connections`                     | `1000`                    | The maximum number of MySQL connections in the region, across all schemas.                                                                                             | [Contact support]
`max_objects_per_schema`                    | `1000`                    | The maximum number of objects in a schema.                                                                                                                             | [Contact support]
`max_postgres_connections`                  | `1000`                    | The maximum number of PostgreSQL connections in the region, across all schemas.                                                                                        | [Contact support]
`max_query_result_size`                     | `1073741824`              | The maximum size in bytes for a single query's result.                                                                                                                 | Yes
`max_replicas_per_cluster`                  | `5`                       | The maximum number of replicas of a single cluster                                                                                                                     | [Contact support]
`max_result_size`                           | `1 GiB`                   | The maximum size in bytes for a single query's result.                                                                                                                 | [Contact support]
`max_roles`                                 | `1000`                    | The maximum number of roles in the region.                                                                                                                             | [Contact support]
`max_schemas_per_database`                  | `1000`                    | The maximum number of schemas in a database.                                                                                                                           | [Contact support]
`max_secrets`                               | `100`                     | The maximum number of secrets in the region, across all schemas.                                                                                                       | [Contact support]
`max_sinks`                                 | `1000`                    | The maximum number of sinks in the region, across all schemas.                                                                                                         | [Contact support]
`max_sources`                               | `25`                      | The maximum number of sources in the region, across all schemas.                                                                                                       | [Contact support]
`max_tables`                                | `200`                     | The maximum number of tables in the region, across all schemas                                                                                                         | [Contact support]
`max_timestamp_interval`                    | `1s`                      | The upper bound for the `TIMESTAMP INTERVAL` option of [`CREATE SOURCE`](/sql/create-source/) and [`ALTER SOURCE`](/sql/alter-source/). Statements that request a timestamp interval larger than this value are rejected. Accepts positive [interval](/sql/types/interval/) values (e.g. `'500ms'`, `'1s'`). | [Contact support]
`min_timestamp_interval`                    | `1s`                      | The lower bound for the `TIMESTAMP INTERVAL` option of [`CREATE SOURCE`](/sql/create-source/) and [`ALTER SOURCE`](/sql/alter-source/). Statements that request a timestamp interval smaller than this value are rejected. Accepts positive [interval](/sql/types/interval/) values (e.g. `'500ms'`, `'1s'`). | [Contact support]
`mz_version`                                | Version-dependent         | Shows the Materialize server version.                                                                                                                                  | No
`network_policy`                            | `default`                 | The default network policy for the region. | Yes
`real_time_recency`                         | `false`                   | Boolean flag indicating whether [real-time recency](/serve-results/isolation-level/#real-time-recency) is enabled for the current session.                               | [Contact support]
`real_time_recency_timeout`                 | `10s`                     | Sets the maximum allowed duration of `SELECT` statements that actively use [real-time recency](/serve-results/isolation-level/#real-time-recency). If this value is specified without units, it is taken as milliseconds (`ms`).                      | Yes
`server_version_num`                        | Version-dependent         | The PostgreSQL compatible server version as an integer.                                                                                                                | No
`server_version`                            | Version-dependent         | The PostgreSQL compatible server version.                                                                                                                              | No
`sql_safe_updates`                          | `false`                   | Boolean flag indicating whether to prohibit SQL statements that may be overly destructive.                                                                             | Yes
`standard_conforming_strings`               | `true`                    | Boolean flag indicating whether ordinary string literals (`'...'`) should treat backslashes literally. The only supported value is `true`.                             | Yes
`statement_timeout`                         | `10s`                     | The maximum allowed duration of the read portion of write operations; i.e., the `SELECT` portion of `INSERT INTO ... (SELECT ...)`; the `WHERE` portion of `UPDATE ... WHERE ...` and `DELETE FROM ... WHERE ...`. If this value is specified without units, it is taken as milliseconds (`ms`). | Yes
`timezone`                                  | `UTC`                     | The time zone for displaying and interpreting timestamps. The only supported value is `UTC`.                                                                           | Yes

[Contact support]: /support

## Privileges

The privileges required to execute this statement are:

- [_Superuser_ privileges](/security/cloud/users-service-accounts/#organization-roles)

## Related pages

- [`ALTER SYSTEM RESET`](../alter-system-reset)
- [`SHOW`](../show)

<!-- mz-docs page: sql/alter-table -->

# ALTER TABLE
`ALTER TABLE` changes properties of a table.
Use `ALTER TABLE` to:

- Rename a table.
- Change owner of a table.
- Change retain history configuration for the table.

## Syntax

**Rename:**

To rename a table:

```mzsql
ALTER TABLE <name> RENAME TO <new_name>;

```

| Syntax element | Description |
| --- | --- |
| `<name>` | The current name of the table you want to alter.  |
| `<new_name>` | The new name of the table.  |
See also [Renaming restrictions](/sql/identifiers/#renaming-restrictions).

**Change owner:**

To change the owner of a table:

```mzsql
ALTER TABLE <name> OWNER TO <new_owner_role>;

```

| Syntax element | Description |
| --- | --- |
| `<name>` | The name of the table you want to change ownership of.  |
| `<new_owner_role>` | The new owner of the table.  |
To change the owner of a table, you must be the owner of the table and have
membership in the `<new_owner_role>`. See also [Privileges](#privileges).

**(Re)Set retain history config:**

To set the retention history for a user-populated table:

```mzsql
ALTER TABLE <name> SET (RETAIN HISTORY [=] FOR <retention_period>);

```

| Syntax element | Description |
| --- | --- |
| `<name>` | The name of the table you want to alter.  |
| `<retention_period>` | ***Private preview.** This option has known performance or stability issues and is under active development.* Duration for which Materialize retains historical data, which is useful to implement [durable subscriptions](/serve-results/durable-subscriptions/#history-retention-period). Accepts positive [interval](/sql/types/interval/) values (e.g. `'1hr'`). Default: `1s`.  |

To reset the retention history to the default for a user-populated table:

```mzsql
ALTER TABLE <name> RESET (RETAIN HISTORY);

```

| Syntax element | Description |
| --- | --- |
| `<name>` | The name of the table you want to alter.  |

## Privileges

The privileges required to execute this statement are:

- Ownership of the table being altered.
- In addition, to change owners:
  - Role membership in `new_owner`.
  - `CREATE` privileges on the containing schema if the table is namespaced by
  a schema.

<!-- mz-docs page: sql/alter-type -->

# ALTER TYPE
`ALTER TYPE` changes properties of a type.
Use `ALTER TYPE` to:
- Rename a type.
- Change owner of a type.

## Syntax

**Rename:**

To rename a type:

```mzsql
ALTER TYPE <name> RENAME TO <new_name>;

```

| Syntax element | Description |
| --- | --- |
| `<name>` | The current name of the type.  |
| `<new_name>` | The new name of the type.  |
See also [Renaming restrictions](/sql/identifiers/#renaming-restrictions).

**Change owner:**

To change the owner of a type:

```mzsql
ALTER TYPE <name> OWNER TO <new_owner_role>;

```

| Syntax element | Description |
| --- | --- |
| `<name>` | The name of the type you want to change ownership of.  |
| `<new_owner_role>` | The new owner of the type.  |
To change the owner of a type, you must be the current owner and have
membership in the `<new_owner_role>`.

## Privileges

The privileges required to execute this statement are:

- Ownership of the type being altered.
- In addition, to change owners:
  - Role membership in `new_owner`.
  - `CREATE` privileges on the containing schema if the type is namespaced by a
    schema.

<!-- mz-docs page: sql/alter-view -->

# ALTER VIEW
`ALTER VIEW` changes properties of a view.
Use `ALTER VIEW` to:
- Rename a view.
- Change owner of a view.

## Syntax

**Rename:**

To rename a view:

```mzsql
ALTER VIEW <name> RENAME TO <new_name>;

```

| Syntax element | Description |
| --- | --- |
| `<name>` | The current name of the view.  |
| `<new_name>` | The new name of the view.  |
See also [Renaming restrictions](/sql/identifiers/#renaming-restrictions).

**Change owner:**

To change the owner of a view:

```mzsql
ALTER VIEW <name> OWNER TO <new_owner_role>;

```

| Syntax element | Description |
| --- | --- |
| `<name>` | The name of the view you want to change ownership of.  |
| `<new_owner_role>` | The new owner of the view.  |
To change the owner of a view, you must be the current owner and have
membership in the `<new_owner_role>`.

## Privileges

The privileges required to execute this statement are:

- Ownership of the view being altered.
- In addition, to change owners:
  - Role membership in `new_owner`.
  - `CREATE` privileges on the containing schema if the view is namespaced by
  a schema.

<!-- mz-docs page: sql/begin -->

# BEGIN
`BEGIN` starts a transaction block.
[`BEGIN`](/sql/begin/) starts a transaction block. Once a transaction is started:
- Statements within the transaction are executed sequentially.
- A transaction ends with either a [`COMMIT`](/sql/commit/) or a
  [`ROLLBACK`](/sql/rollback/) statement.
  - If all transaction statements succeed and a [`COMMIT`](/sql/commit/) is
  [issued](/sql/commit/#details), all changes are saved.
  - If all transaction statements succeed and a [`ROLLBACK`](/sql/rollback/)
  is issued, all changes are discarded.
  - If an error occurs and either a [`COMMIT`](/sql/commit/) or a
  [`ROLLBACK`](/sql/rollback/) is issued, all changes are discarded.

Materialize supports multi-statement[^ddltxn] transaction blocks for:
- [**read-only** statements](#read-only-transactions);
- [**write-only** (specifically, insert-only)
  statements](#write-only-transactions);
- [**DDL-only** statements](#ddl-only-transactions).

See [Details](#details) for more information.

[^ddltxn]: Materialize also supports single-statement transaction blocks for various
`CREATE ...` statements. However, single-statement transactions do not need to
be wrapped in an explicit transaction block.

## Syntax

```mzsql
BEGIN [ <option>, ... ];
```

You can specify the following optional settings for `BEGIN`:

Option | Description
-------|----------
`ISOLATION LEVEL <level>` | *Optional*. If specified, sets the transaction [isolation level](/serve-results/isolation-level).
`READ ONLY` | <a name="begin-option-read-only"></a> *Optional*. If specified, restricts the transaction to [**read-only** statements](#read-only-transactions). If unspecified, Materialize restricts the transaction to [**read-only** statements](#read-only-transactions), [**write-only** statements](#write-only-transactions), or [**DDL-only** statements](#ddl-only-transactions) based on the first statement in the transaction.

## Details

Multi-statement transactions in Materialize are [**read-only**
transactions](#read-only-transactions), [**write-only**
transactions](#write-only-transactions), or [**DDL-only**
transactions](#ddl-only-transactions) as determined by either:

- The first statement after the `BEGIN`, or
- The [`READ ONLY`](#begin-option-read-only) option is specified.

### Read-only transactions

In Materialize, read-only transactions can be either:

- a [`SELECT`only transaction](#select-only-transactions) that only contains
  [`SELECT`] statements or

- a [`SUBSCRIBE`-based transactions](#subscribe-based-transactions) that only
    contains a single [`DECLARE ... CURSOR FOR`] [`SUBSCRIBE`] statement
    followed by subsequent [`FETCH`](/sql/fetch) statement(s). [^1]

> **Note:** - During the first query, a timestamp is chosen that is valid for all of the
>   objects referenced in the query. This timestamp will be used for all other
>   queries in the transaction.
> - The transaction will additionally hold back normal compaction of the objects,
>   potentially increasing memory usage for very long running transactions.

#### SELECT-only transactions

A **SELECT-only** transaction only contains [`SELECT`](/sql/select) statement.

The first [`SELECT`](/sql/select) statement:

- Determines the timestamp that will be used for all other queries in the
  transaction.

- Determines  which objects can be queried in the transaction block.

Specifically,

- Subsequent [`SELECT`](/sql/select) statements in the transaction can only
  reference objects from the [schema(s)](/sql/namespaces/) referenced in the
  first [`SELECT`](/sql/select) statement (as well as a subset of objects from
  the `mz_catalog` and `mz_internal` schemas).

- These objects must have existed at beginning of the transaction.

For example, in the transaction block below, first `SELECT` statement in the
transaction restricts subsequent selects to objects from `test` and `public`
schemas.

```mzsql
BEGIN;
SELECT o.*,i.price,o.quantity * i.price as subtotal
FROM test.orders as o
JOIN public.items as i ON o.item = i.item;

-- Subsequent queries must only reference objects from the test and public schemas that existed at the start of the transaction.

SELECT * FROM test.auctions limit 1;
SELECT * FROM public.sales_items;
COMMIT;
```

Reading from a schema not referenced in the first statement or querying objects
created after the transaction started (even if in the allowed schema(s)) will
produce a [Same timedomain error](#same-timedomain-error).  [Same timedomain
error](#same-timedomain-error) provides a list of the allowed objects in the
transaction.

##### Same timedomain error

```none
Transactions can only reference objects in the same timedomain.
```

The first `SELECT` statement in a transaction determines which schemas the
subsequent `SELECT` statements in the transaction can query. If a subsequent
`SELECT` references an object from another schema or an object created after the
transaction started, the transaction will error with the same time domain error.

The timedomain error lists both the objects that are not in the timedomain as
well as the objects that can be referenced in the transaction (i.e., in the
timedomain).

If an object in the timedomain is a view, it will be replaced with the objects
in the view definition.

#### SUBSCRIBE-based transactions

A [`SUBSCRIBE`]-based transaction only contains a single [`DECLARE ... CURSOR
FOR`] [`SUBSCRIBE`] statement followed by subsequent [`FETCH`](/sql/fetch)
statement(s). [^1]

```mzsql
BEGIN;
DECLARE c CURSOR FOR SUBSCRIBE (SELECT * FROM flippers);

-- Subsequent queries must only FETCH from the cursor

FETCH 10 c WITH (timeout='1s');
FETCH 20 c WITH (timeout='1s');
COMMIT;
```

[^1]: A [`SUBSCRIBE`-based transaction](#subscribe-based-transactions) can start
with a  [`SUBSCRIBE`] statement (or `COPY (SUBSCRIBE ...) TO STDOUT`) instead of
a `DECLARE ... FOR SUBSCRIBE` but will end with a rollback since you must cancel
the SUBSCRIBE statementin order to issue the `COMMIT`/`ROLLBACK` statement to
end the transaction block.

### Write-only transactions

In Materialize, a write-only transaction is an [INSERT-only
transaction](#insert-only-transactions) that only contains [`INSERT`]
statements.

#### INSERT-only transactions

An **insert-only** transaction block only contains [`INSERT`](/sql/insert/)
statements that insert into the **same** table.

On a successful [`COMMIT`](/sql/commit/), all statements from the
transaction are committed at the same timestamp.

```mzsql
BEGIN;
INSERT INTO orders VALUES (11,current_timestamp,'brownie',10);

-- Subsequent INSERTs must write to sales_items table only
-- Otherwise, the COMMIT will error and roll back the transaction.

INSERT INTO orders VALUES (11,current_timestamp,'chocolate cake',1);
INSERT INTO orders VALUES (11,current_timestamp,'chocolate chip cookie',20);
COMMIT;
```

If, within the transaction, a statement inserts into a table different from
that of the first statement, on [`COMMIT`](/sql/commit/), the transaction
encounters an **internal ERROR** and rolls back:

```none
ERROR:  internal error, wrong set of locks acquired
```

### DDL-only transactions

In Materialize, a DDL-only transaction block is a transaction that can contain
multiple DDL statements. The following DDL statements are allowed in DDL-only
transactions:

- `ALTER ... RENAME` (e.g., [`ALTER TABLE ... RENAME`](/sql/alter-table/),
  [`ALTER SCHEMA ... RENAME`](/sql/alter-schema/))
- `ALTER ... SWAP` (e.g., [`ALTER SCHEMA ... SWAP`](/sql/alter-schema/))
- [`CREATE TABLE ... FROM SOURCE`](/sql/create-table/)
- [`CREATE SOURCE`](/sql/create-source/)

In practice, use DDL transaction blocks to create multiple tables from a source
in a single transaction. On a successful [`COMMIT`](/sql/commit/), all objects
in the transaction are created with the same timestamp.

```mzsql
BEGIN;
CREATE TABLE items FROM SOURCE pg_source (REFERENCE public.items);
CREATE TABLE orders FROM SOURCE pg_source (REFERENCE public.orders);
CREATE TABLE customers FROM SOURCE pg_source (REFERENCE public.customers);
COMMIT;
```

## See also

- [`COMMIT`](/sql/commit)
- [`ROLLBACK`](/sql/rollback)

[`BEGIN`]: /sql/begin/
[`ROLLBACK`]: /sql/rollback/
[`COMMIT`]: /sql/commit/
[`SELECT`]: /sql/select/
[`SUBSCRIBE`]: /sql/subscribe/
[`DECLARE ... CURSOR FOR`]: /sql/declare/
[`INSERT`]: /sql/insert/

<!-- mz-docs page: sql/close -->

# CLOSE
`CLOSE` closes a cursor.
Use `CLOSE` to close a cursor previously opened with [`DECLARE`](/sql/declare).

## Syntax

```mzsql
CLOSE <cursor_name>;
```

Syntax element | Description
---------------|------------
`<cursor_name>` | The name of an open cursor to close.

<!-- mz-docs page: sql/comment-on -->

# COMMENT ON
`COMMENT ON` adds or updates the comment of an object.
Use `COMMENT ON` to:

- Add a comment to an object.
- Update the comment to an object.
- Remove the comment from an object.

## Syntax

```mzsql
COMMENT ON <object_type> <name> IS <comment | NULL>;

```

| Syntax element | Description |
| --- | --- |
| `<object_type>` | The type of the object. Supported object types:  - `CLUSTER` - `CLUSTER REPLICA` - `COLUMN` - `CONNECTION` - `DATABASE` - `FUNCTION` - `INDEX` - `MATERIALIZED VIEW` - `NETWORK POLICY` - `ROLE` - `SCHEMA` - `SECRET` - `SINK` - `SOURCE` - `TABLE` - `TYPE` - `VIEW`  |
| `<name>` | The fully qualified name of the object.  |
| `<comment \| NULL>` | - The comment string for the object. - Use `NULL` to remove an existing comment.  |

## Details

`COMMENT ON` stores a comment about an object in the database. Each object can only have one
comment associated with it, so successive calls of `COMMENT ON` to a single object will overwrite
the previous comment.

To read the comment on an object you need to query the [mz_internal.mz_comments](/sql/system-catalog/mz_internal/#mz_comments)
catalog table.

## Privileges

The privileges required to execute this statement are:

- Ownership of the object being commented on (unless the object is a role).
- To comment on a role, you must have the `CREATEROLE` privilege.

For more information on ownership and privileges, see [Role-based access
control](/security/).

## Examples

```mzsql
--- Add comments.
COMMENT ON TABLE foo IS 'this table is important';
COMMENT ON COLUMN foo.x IS 'holds all of the important data';

--- Update a comment.
COMMENT ON TABLE foo IS 'holds non-important data';

--- Remove a comment.
COMMENT ON TABLE foo IS NULL;

--- Read comments.
SELECT * FROM mz_internal.mz_comments;
```

<!-- mz-docs page: sql/commit -->

# COMMIT
`COMMIT` ends a transaction block and commits all changes if the transaction statements succeed.
`COMMIT` ends the current [transaction](/sql/begin/#details). Upon the `COMMIT`
statement:

- If all transaction statements succeed, all changes are committed.

- If an error occurs, all changes are discarded; i.e., rolled back.

## Syntax

```mzsql
COMMIT;
```

## Details

[`BEGIN`](/sql/begin/) starts a transaction block. Once a transaction is started:
- Statements within the transaction are executed sequentially.
- A transaction ends with either a [`COMMIT`](/sql/commit/) or a
  [`ROLLBACK`](/sql/rollback/) statement.
  - If all transaction statements succeed and a [`COMMIT`](/sql/commit/) is
  [issued](/sql/commit/#details), all changes are saved.
  - If all transaction statements succeed and a [`ROLLBACK`](/sql/rollback/)
  is issued, all changes are discarded.
  - If an error occurs and either a [`COMMIT`](/sql/commit/) or a
  [`ROLLBACK`](/sql/rollback/) is issued, all changes are discarded.

Transactions in Materialize are **read-only** transactions, **write-only**
(more specifically, **insert-only**) transactions, or **DDL-only**
transactions.

For a [write-only (i.e., insert-only)
transaction](/sql/begin/#write-only-transactions), all statements in the
transaction are committed at the same timestamp.

For a [DDL-only transaction](/sql/begin/#ddl-only-transactions), all
statements in the transaction are committed at the same timestamp.

## Examples

### Commit a write-only transaction {#write-only-transactions}

In Materialize, write-only transactions are **insert-only** transactions.

An **insert-only** transaction block only contains [`INSERT`](/sql/insert/)
statements that insert into the **same** table.

On a successful [`COMMIT`](/sql/commit/), all statements from the
transaction are committed at the same timestamp.

```mzsql
BEGIN;
INSERT INTO orders VALUES (11,current_timestamp,'brownie',10);

-- Subsequent INSERTs must write to sales_items table only
-- Otherwise, the COMMIT will error and roll back the transaction.

INSERT INTO orders VALUES (11,current_timestamp,'chocolate cake',1);
INSERT INTO orders VALUES (11,current_timestamp,'chocolate chip cookie',20);
COMMIT;
```

If, within the transaction, a statement inserts into a table different from
that of the first statement, on [`COMMIT`](/sql/commit/), the transaction
encounters an **internal ERROR** and rolls back:

```none
ERROR:  internal error, wrong set of locks acquired
```

### Commit a read-only transaction

In Materialize, read-only transactions can be either:

- a `SELECT` only transaction that only contains [`SELECT`] statements or

- a `SUBSCRIBE`-based transactions that only contains a single[`DECLARE ...
  CURSOR FOR`] [`SUBSCRIBE`] statement followed by subsequent
  [`FETCH`](/sql/fetch) statement(s).

For example:

```mzsql
BEGIN;
DECLARE c CURSOR FOR SUBSCRIBE (SELECT * FROM flippers);

-- Subsequent queries must only FETCH from the cursor

FETCH 10 c WITH (timeout='1s');
FETCH 20 c WITH (timeout='1s');
COMMIT;
```

During the first query, a timestamp is chosen that is valid for all of the
objects referenced in the query. This timestamp will be used for all other
queries in the transaction.

> **Note:** The transaction will additionally hold back normal compaction of the objects,
> potentially increasing memory usage for very long running transactions.

## See also

- [`BEGIN`]
- [`ROLLBACK`]

[`BEGIN`]: /sql/begin/
[`ROLLBACK`]: /sql/rollback/
[`COMMIT`]: /sql/commit/
[`SELECT`]: /sql/select/
[`SUBSCRIBE`]: /sql/subscribe/
[`DECLARE ... CURSOR FOR`]: /sql/declare/
[`INSERT`]: /sql/insert

<!-- mz-docs page: sql/copy-from -->

# COPY FROM
`COPY FROM` copies data into a table using the COPY protocol.
`COPY FROM` copies data into a table using the [Postgres `COPY` protocol][pg-copy-from].

## Syntax

**Copy from STDIN:**

```mzsql
COPY [INTO] <table_name> [ ( <column> [, ...] ) ] FROM STDIN
[[WITH] ( <option1> [=] <val1> [, ...] ] )]
;

```

| Syntax element | Description |
| --- | --- |
| `<table_name>` | Name of an existing table to copy data into.  |
| `( <column> [, ...] )` | If specified, correlate the inserted rows' columns to `<table_name>`'s columns by ordinal position, i.e. the first column of the row to insert is correlated to the first named column. If not specified, all columns must have data provided, and will be referenced using their order in the table. With a partial column list, all unreferenced columns will receive their default value.  |
| `[WITH] ( <option1> [=] <val1> [, ...] )` | The following `<options>` are supported for the `COPY FROM` operation: \| Name \|  Description \| \|------\|---------------\| \| `FORMAT` \|  Sets the input formatting method. Valid input formats are `TEXT` and `CSV`. For more information see [Text formatting](#text-formatting) and [CSV formatting](#csv-formatting).<br><br> Default: `TEXT`. \| `DELIMITER` \| A single-quoted one-byte character to use as the column delimiter. Must be different from `QUOTE`.<br><br> Default: A tab character in `TEXT`  format, a comma in `CSV` format. \| `NULL`  \| A single-quoted string that represents a _NULL_ value.<br><br> Default: `\N` (backslash-N) in text format, an unquoted empty string in CSV format. \| `QUOTE` \| _For `FORMAT CSV` only._ A single-quoted one-byte character that specifies the character to signal a quoted string, which may contain the `DELIMITER` value (without beginning new columns). To include the `QUOTE` character itself in column, wrap the column's value in the `QUOTE` character and prefix all instance of the value you want to literally interpret with the `ESCAPE` value. Must be different from `DELIMITER`.<br><br> Default: `"`. \| `ESCAPE` \| _For `FORMAT CSV` only._ A single-quoted string that specifies the character to allow instances of the `QUOTE` character to be parsed literally as part of a column's value. <br><br> Default: `QUOTE`'s value. \| `HEADER`  \| _For `FORMAT CSV` only._ A boolean that specifies that the file contains a header line with the names of each column in the file. The first line is ignored on input. <br><br> Default: `false`.  |

**Copy from S3 and S3 compatible services:**

```mzsql
COPY [INTO] <table_name> [ ( <column> [, ...] ) ] FROM [<s3 URI> | <http URL>]
[[WITH] ( <option1> [=] <val1> [, ...] ] )]
;

```

| Syntax element | Description |
| --- | --- |
| `<table_name>` | Name of an existing [table](/sql/create-table/) to copy data into.  |
| `( <column> [, ...] )` | If specified, correlate the inserted rows' columns to `<table_name>`'s columns by ordinal position, i.e. the first column of the row to insert is correlated to the first named column. If not specified, all columns must have data provided, and will be referenced using their order in the table. With a partial column list, all unreferenced columns will receive their default value.  |
| `<s3 URI>` | The unique resource identifier (URI) of the Amazon S3 bucket (and prefix) to retrieve the file(s) to be copied from. If using an s3 URI, an AWS connection must be provided in the `WITH` clause.  |
| `<HTTP URL>` | The URL (for example, s3 presigned URL) to retrieve the file(s) to be copied from.  |
| `[WITH] ( <option1> [=] <val1> [, ...] )` | The following `<options>` are supported for the `COPY FROM` operation: Name \| Value type \| Default value \| Description -----\|-----------------\|---------------\|------------ `FORMAT` \| `CSV`, `PARQUET` \| None, must be provided \| Sets the input formatting method. For more information see [formatting details below](#details). `DELIMITER` \| Single-quoted one-byte character \| Format-dependent \| Overrides the format's default column delimiter. _`FORMAT CSV` only_ `NULL` \| Single-quoted strings \| Format-dependent \| Specifies the string that represents a _NULL_ value. _`FORMAT CSV` only_ `QUOTE` \| Single-quoted one-byte character \| `"` \| Specifies the character to signal a quoted string, which may contain the `DELIMITER` value (without beginning new columns). To include the `QUOTE` character itself in column, wrap the column's value in the `QUOTE` character and prefix all instance of the value you want to literally interpret with the `ESCAPE` value. _`FORMAT CSV` only_ `ESCAPE` \| Single-quoted strings \| `QUOTE`'s value \| Specifies the character to allow instances of the `QUOTE` character to be parsed literally as part of a column's value. _`FORMAT CSV` only_ `HEADER`  \| `boolean`   \| `false`  \| Specifies that the file contains a header line with the names of each column in the file. The first line is ignored on input.  _`FORMAT CSV` only._ `AWS CONNECTION` \| _connection_name_ \|  \|  The name of the AWS connection to use in the `COPY FROM` command. If using an s3 URI, must be specified. For details on creating connections, check the [`CREATE CONNECTION`](/sql/create-connection/#aws) documentation page. _Only valid with S3._ `FILES`   \| array \| \| A list of files to be appended to the URI. Example: `[ "top.csv", "files/a.csv", "files/b.csv" ]`. `PATTERN` \| string \| \| A glob used to identify files at at the URI. Example: `"files/**"`.  Note that `DELIMITER` and `QUOTE` must use distinct values.  |

## Details

### S3 Bucket IAM Policies

To use `COPY FROM` with S3, you need to allow the following actions in your IAM policy:

| Action type | Action name                                                                               | Action description                                                |
| ----------- | ----------------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| Read        | [`s3:GetObject`](https://docs.aws.amazon.com/AmazonS3/latest/API/API_GetObject.html)      | Grants permission to retrieve an object from a bucket.            |
| List        | [`s3:ListBucket`](https://docs.aws.amazon.com/AmazonS3/latest/API/API_ListObjectsV2.html) | Grants permission to list some or all of the objects in a bucket. |

> **Note:** For S3-compatible object storage services (e.g., Google Cloud Storage, Cloudflare R2, MinIO),
> you need to enable equivalent permissions on the service you are using. The specific
> configuration steps will vary by provider, but the access credentials must allow the same
> read and list operations on the target bucket.

### Text formatting

As described in the **Text Format** section of [PostgreSQL's documentation][pg-copy-from].

### CSV formatting

As described in the **CSV Format** section of [PostgreSQL's documentation][pg-copy-from]
except that:

- More than one layer of escaped quote characters returns the wrong result.

- Quote characters must immediately follow a delimiter to be treated as
  expected.

- Single-column rows containing quoted end-of-data markers (e.g. `"\."`) will be
  treated as end-of-data markers despite being quoted. In PostgreSQL, this data
  would be escaped and would not terminate the data processing.

- Quoted null strings will be parsed as nulls, despite being quoted. In
  PostgreSQL, this data would be escaped.

    To ensure proper null handling, we recommend specifying a unique string for
    null values, and ensuring it is never quoted.

- Unterminated quotes are allowed, i.e. they do not generate errors. In
  PostgreSQL, all open unescaped quotation punctuation must have a matching
  piece of unescaped quotation punctuation or it generates an error.

### PARQUET formatting

Supported PARQUET compression formats

- snappy
- gzip
- brotli
- zstd
- lz4

[//]: # "TODO: - Text can be imported as text or JSON/JSONB or a map.. do we document casting rules/make a whole section for casting?"

| [Arrow type](https://github.com/apache/arrow/blob/main/format/Schema.fbs) | [Parquet primitive type](https://parquet.apache.org/docs/file-format/types/) | [Parquet logical type](https://github.com/apache/parquet-format/blob/master/LogicalTypes.md) | Materialize type                                                                  |
| ------------------------------------------------------------------------- | ---------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| `bool`                                                                    | `BOOLEAN`                                                                    |                                                                                              | [`boolean`](/sql/types/boolean/)                                                  |
| `date32`                                                                  | `INT32`                                                                      | `DATE`                                                                                       | [`date`](/sql/types/date/)                                                        |
| `decimal128[38, 10 or max-scale]`                                         | `FIXED_LEN_BYTE_ARRAY`                                                       | `DECIMAL`                                                                                    | [`numeric`](/sql/types/numeric/)                                                  |
| `fixed_size_binary(16)`                                                   | `FIXED_LEN_BYTE_ARRAY`                                                       |                                                                                              | [`bytea`](/sql/types/bytea/)                                                      |
| `float32`                                                                 | `FLOAT`                                                                      |                                                                                              | [`real`](/sql/types/float/#real-info)                                             |
| `float64`                                                                 | `DOUBLE`                                                                     |                                                                                              | [`double precision`](/sql/types/float/#double-precision-info)                     |
| `int16`                                                                   | `INT32`                                                                      | `INT(16, true)`                                                                              | [`smallint`](/sql/types/integer/#smallint-info)                                   |
| `int32`                                                                   | `INT32`                                                                      |                                                                                              | [`integer`](/sql/types/integer/#integer-info)                                     |
| `int64`                                                                   | `INT64`                                                                      |                                                                                              | [`bigint`](/sql/types/integer/#bigint-info)                                       |
| `interval[year-month]`                                                    | `INT32`                                                                      | `INTERVAL(YEAR_MONTH)`                                                                       | [`interval`](/sql/types/interval/)                                                |
| `interval[day-time]`                                                      | `FIXED_LEN_BYTE_ARRAY(12)`                                                   | `INTERVAL`                                                                                   | [`interval`](/sql/types/interval/)                                                |
| `large_binary`                                                            | `BYTE_ARRAY`                                                                 |                                                                                              | [`bytea`](/sql/types/bytea/)                                                      |
| `large_utf8`                                                              | `BYTE_ARRAY`                                                                 |                                                                                              | [`jsonb`](/sql/types/jsonb/)                                                      |
| `list`                                                                    | Nested                                                                       |                                                                                              | [`list`](/sql/types/list/)                                                        |
| `map`                                                                     | Nested                                                                       | `MAP`                                                                                        | [`map`](/sql/types/map/)                                                          |
| `struct`                                                                  | Nested                                                                       |                                                                                              | [Arrays](/sql/types/array/) (`[]`)                                                |
| `time64[microsecond]`                                                     | `INT64`                                                                      | `TIMESTAMP[isAdjustedToUTC = false, unit = MICROS]`                                          | [`timestamp`](/sql/types/timestamp/#timestamp-info)                               |
| `time64[microsecond]`                                                     | `INT64`                                                                      | `TIMESTAMP[isAdjustedToUTC = true, unit = MICROS]`                                           | [`timestamp with time zone`](/sql/types/timestamp/#timestamp-with-time-zone-info) |
| `time64[nanosecond]`                                                      | `INT64`                                                                      | `TIME[isAdjustedToUTC = false, unit = NANOS]`                                                | [`time`](/sql/types/time/)                                                        |
| `uint16`                                                                  | `INT32`                                                                      | `INT(16, false)`                                                                             | [`uint2`](/sql/types/uint/#uint2-info)                                            |
| `uint32`                                                                  | `INT32`                                                                      | `INT(32, false)`                                                                             | [`uint4`](/sql/types/uint/#uint4-info)                                            |
| `uint64`                                                                  | `INT64`                                                                      | `INT(64, false)`                                                                             | [`uint8`](/sql/types/uint/#uint8-info)                                            |
| `utf8` or `large_utf8`                                                    | `BYTE_ARRAY`                                                                 | `STRING`                                                                                     | [`text`](/sql/types/text/)                                                        |

### Limits

You can copy up to 10 GiB of data at a time. If you need to copy more than that, please [contact support](/support/).

When importing parquet files, entire row groups are held in memory at once, so ensure that your
Materialize instance has enough available memory to accomodate your parquet files. If you are
encountering memory issues, and are unable to reduce the sizes of your row groups, please [contact support](/support/).

### Atomicity

`COPY FROM` is atomic. When you copy from a location that contains multiple
files, Materialize stages the data from every file and commits it in a single
transaction. If any part of the operation fails, for example a file cannot be
read or a row cannot be parsed, the entire `COPY FROM` fails and no data is
committed. You are never left with some files ingested and others missing.

## Examples

### From STDIN

```mzsql
COPY t FROM STDIN WITH (DELIMITER '|');
```

```mzsql
COPY t FROM STDIN (FORMAT CSV);
```

```mzsql
COPY t FROM STDIN (DELIMITER '|');
```

### From AWS S3

#### Using AWS connection

Perform bulk import:

Using `FILES` option:

```mzsql
COPY INTO csv_table FROM 's3://example_bucket' (FORMAT CSV, AWS CONNECTION = example_aws_conn, FILES = ['example_data.csv']);
```

Using the full s3 URI:

```mzsql
COPY INTO csv_table FROM 's3://example_bucket/example_data.csv' (FORMAT CSV, AWS CONNECTION = example_aws_conn);
```

Using `PATTERN` option:

```mzsql
COPY INTO parquet_table FROM 's3://example_bucket' (FORMAT PARQUET, AWS CONNECTION = example_aws_conn, PATTERN = '*parquet*');
```

#### Using S3-compatible object storage

You can use `COPY FROM` with any S3-compatible object storage service, such as
Google Cloud Storage, Cloudflare R2, or MinIO. First,
[create an AWS connection for S3-compatible storage](/sql/create-connection/#s3-compatible-object-storage),
then use it in the `COPY` command. Make sure your credentials have the necessary
permissions as described in [S3 Bucket IAM Policies](#s3-bucket-iam-policies).

```mzsql
COPY INTO csv_table FROM 's3://my_bucket/my_data.csv' (FORMAT CSV, AWS CONNECTION = gcs_connection);
```

#### Using presigned URL

```mzsql
COPY INTO csv_table FROM '<s3 presigned URL>' (FORMAT CSV);
```

> **Note:** Materialize does not follow HTTP redirects when fetching from a URL. If the
> server returns a `3xx` response, the `COPY FROM` will fail rather than follow
> the `Location` header. Use the final URL directly (for example, the resolved
> presigned URL) instead of one that redirects.

## Privileges

The privileges required to execute this statement are:

- `USAGE` privileges on the schema containing the table.
- `INSERT` privileges on the table.

[pg-copy-from]: https://www.postgresql.org/docs/14/sql-copy.html

<!-- mz-docs page: sql/copy-to -->

# COPY TO
`COPY TO` outputs results from Materialize to standard output or object storage.
`COPY TO` outputs results from Materialize to standard output or object storage.
This command is useful to output [`SUBSCRIBE`](/sql/subscribe/) results
[to `stdout`](#copy-to-stdout), or perform [bulk exports to Amazon S3](#copy-to-s3).

## Syntax

**Copy to stdout:**
### Copy to `stdout`  {#copy-to-stdout}

Copying results to `stdout` is useful to output the stream of updates from a
[`SUBSCRIBE`](/sql/subscribe/) command in interactive SQL clients like `psql`.

```mzsql
COPY ( <query> ) TO STDOUT [WITH ( <option> = <val> )];

```

| Syntax element | Description |
| --- | --- |
| `<query>` | The [`SELECT`](/sql/select) or [`SUBSCRIBE`](/sql/subscribe) query whose results are copied.  |
| `WITH ( <option> = <val> )` | Optional. The following `<option>` are supported: \| Name \|  Description \| \|------\|---------------\| `FORMAT` \| Sets the output format. Valid output formats are: `TEXT`,`BINARY`, `CSV`.<br><br> Default: `TEXT`.  |

**Copy to Amazon S3 and S3 compatible services:**
### Copy to Amazon S3 and S3 compatible services {#copy-to-s3}

Copying results to Amazon S3 (or S3-compatible services) is useful to perform
tasks like periodic backups for auditing, or downstream processing in
analytical data warehouses like Snowflake, Databricks or BigQuery. For
step-by-step instructions, see the integration guide for [Amazon S3](/serve-results/s3/).

The `COPY TO` command is _one-shot_: every time you want to export results, you
must run the command. To automate exporting results on a regular basis, you can
set up scheduling, for example using a simple `cron`-like service or an
orchestration platform like Airflow or Dagster.

```mzsql
COPY <query> TO '<s3_uri>'
WITH (
  AWS CONNECTION = <connection_name>,
  FORMAT = <format>
  [, MAX FILE SIZE = <size> ]
);

```

| Syntax element | Description |
| --- | --- |
| `<query>` | The [`SELECT`](/sql/select) query whose results are copied.  |
| `<s3_uri>` | The unique resource identifier (URI) of the Amazon S3 bucket (and prefix) to store the output results in.  |
| `AWS CONNECTION = <connection_name>` | The name of the AWS connection to use in the `COPY TO` command. For details on creating connections, check the [`CREATE CONNECTION`](/sql/create-connection/#aws) documentation page.  |
| `FORMAT = '<format>'` | The file format to write. Valid formats are `'csv'` and `'parquet'`.  - {{< include-from-yaml data="examples/copy_to" name="csv-writer-settings" >}}  - {{< include-from-yaml data="examples/copy_to" name="parquet-writer-settings" >}}  |
| [`MAX FILE SIZE = <size>`] | Optional. Sets the approximate maximum file size (in bytes) of each file uploaded to the S3 bucket.  |

## Details

### Copy to S3: CSV {#copy-to-s3-csv}

#### Writer settings

For `'csv'` format, Materialize writes CSV files using the following
writer settings:

| Setting | Value |
|---------|-------|
| delimiter | `,` |
| quote | `"` |
| escape | `"` |
| header | `false` |

### Copy to S3: Parquet {#copy-to-s3-parquet}

#### Writer settings

For `'parquet'` format, Materialize writes Parquet files that aim for
maximum compatibility with downstream systems. The following Parquet
writer settings are used:

| Setting | Value |
|---------|-------|
| Writer version | 1.0 |
| Compression | `snappy` |
| Default column encoding | Dictionary |
| Fallback column encoding | Plain |
| Dictionary page encoding | Plain |
| Dictionary data page encoding | `RLE_DICTIONARY` |

If you encounter issues trying to ingest Parquet files produced by
Materialize into your downstream systems, please [contact our
team](/support/).

#### Parquet data types

When using the `parquet` format, Materialize converts the values in the
result set to [Apache Arrow](https://arrow.apache.org/docs/index.html),
and then serializes this Arrow representation to Parquet. The Arrow schema is
embedded in the Parquet file metadata and allows reconstructing the Arrow
representation using a compatible reader.

Materialize also includes [Parquet `LogicalType` annotations](https://github.com/apache/parquet-format/blob/master/LogicalTypes.md#metadata)
where possible. However, many newer `LogicalType` annotations are not supported
in the 1.0 writer version.

Materialize also embeds its own type information into the Apache Arrow schema.
The field metadata in the schema contains an `ARROW:extension:name` annotation
to indicate the Materialize native type the field originated from.

Materialize type | Arrow extension name | [Arrow type](https://github.com/apache/arrow/blob/main/format/Schema.fbs) | [Parquet primitive type](https://parquet.apache.org/docs/file-format/types/) | [Parquet logical type](https://github.com/apache/parquet-format/blob/master/LogicalTypes.md)
----------------------------------|----------------------------|------------|-------------------|--------------
[`bigint`](/sql/types/integer/#bigint-info)         | `materialize.v1.bigint`    | `int64` | `INT64`
[`boolean`](/sql/types/boolean/)        | `materialize.v1.boolean`   | `bool` | `BOOLEAN`
[`bytea`](/sql/types/bytea/)            | `materialize.v1.bytea`     | `large_binary` | `BYTE_ARRAY`
[`date`](/sql/types/date/)              | `materialize.v1.date`      | `date32` | `INT32` | `DATE`
[`double precision`](/sql/types/float/#double-precision-info) | `materialize.v1.double`    | `float64` | `DOUBLE`
[`integer`](/sql/types/integer/#integer-info)        | `materialize.v1.integer`   | `int32` | `INT32`
[`jsonb`](/sql/types/jsonb/)            | `materialize.v1.jsonb`     | `large_utf8` | `BYTE_ARRAY`
[`map`](/sql/types/map/)                | `materialize.v1.map`       | `map` (`struct` with fields `keys` and `values`) | Nested | `MAP`
[`list`](/sql/types/list/)              | `materialize.v1.list`      | `list` | Nested
[`numeric`](/sql/types/numeric/)        | `materialize.v1.numeric`   | `decimal128[38, 10 or max-scale]` | `FIXED_LEN_BYTE_ARRAY`             | `DECIMAL`
[`real`](/sql/types/float/#real-info)             | `materialize.v1.real`      | `float32` | `FLOAT`
[`smallint`](/sql/types/integer/#smallint-info)       | `materialize.v1.smallint`  | `int16` | `INT32` | `INT(16, true)`
[`text`](/sql/types/text/)              | `materialize.v1.text`      | `utf8` or `large_utf8` | `BYTE_ARRAY` | `STRING`
[`time`](/sql/types/time/)              | `materialize.v1.time`      | `time64[nanosecond]` | `INT64` | `TIME[isAdjustedToUTC = false, unit = NANOS]`
[`uint2`](/sql/types/uint/#uint2-info)             | `materialize.v1.uint2`     | `uint16` | `INT32` | `INT(16, false)`
[`uint4`](/sql/types/uint/#uint4-info)             | `materialize.v1.uint4`     | `uint32` | `INT32` | `INT(32, false)`
[`uint8`](/sql/types/uint/#uint8-info)             | `materialize.v1.uint8`     | `uint64` | `INT64` | `INT(64, false)`
[`timestamp`](/sql/types/timestamp/#timestamp-info)    | `materialize.v1.timestamp` | `time64[microsecond]` | `INT64` | `TIMESTAMP[isAdjustedToUTC = false, unit = MICROS]`
[`timestamp with time zone`](/sql/types/timestamp/#timestamp-with-time-zone-info) | `materialize.v1.timestampz` | `time64[microsecond]` | `INT64` | `TIMESTAMP[isAdjustedToUTC = true, unit = MICROS]`
[Arrays](/sql/types/array/) (`[]`)      | `materialize.v1.array`     | `struct` with `list` field `items` and `uint8` field `dimensions` | Nested
[`uuid`](/sql/types/uuid/)              | `materialize.v1.uuid`      | `fixed_size_binary(16)` | `FIXED_LEN_BYTE_ARRAY`
[`oid`](/sql/types/oid/)                      | Unsupported
[`interval`](/sql/types/interval/)            | Unsupported
[`record`](/sql/types/record/)                | Unsupported

## Privileges

The privileges required to execute this statement are:

- `USAGE` privileges on the schemas that all relations and types in the query are contained in.
- `SELECT` privileges on all relations in the query.
    - NOTE: if any item is a view, then the view owner must also have the necessary privileges to
      execute the view definition. Even if the view owner is a _superuser_, they still must explicitly be
      granted the necessary privileges.
- `USAGE` privileges on all types used in the query.
- `USAGE` privileges on the active cluster.

## Examples

### Copy to stdout {#copy-to-stdout-examples}

```mzsql
COPY (SUBSCRIBE some_view) TO STDOUT WITH (FORMAT binary);
```

### Copy to S3 {#copy-to-s3-examples}

#### File format Parquet

```mzsql
COPY some_view TO 's3://mz-to-snow/parquet/'
WITH (
    AWS CONNECTION = aws_role_assumption,
    FORMAT = 'parquet'
  );
```

For `'parquet'` format, Materialize writes Parquet files that aim for
maximum compatibility with downstream systems. The following Parquet
writer settings are used:

| Setting | Value |
|---------|-------|
| Writer version | 1.0 |
| Compression | `snappy` |
| Default column encoding | Dictionary |
| Fallback column encoding | Plain |
| Dictionary page encoding | Plain |
| Dictionary data page encoding | `RLE_DICTIONARY` |

If you encounter issues trying to ingest Parquet files produced by
Materialize into your downstream systems, please [contact our
team](/support/).

See also [Copy to S3: Parquet Data Types](#parquet-data-types).

#### File format CSV

```mzsql
COPY some_view TO 's3://mz-to-snow/csv/'
WITH (
    AWS CONNECTION = aws_role_assumption,
    FORMAT = 'csv'
  );
```

For `'csv'` format, Materialize writes CSV files using the following
writer settings:

| Setting | Value |
|---------|-------|
| delimiter | `,` |
| quote | `"` |
| escape | `"` |
| header | `false` |

## Related pages

- [`CREATE CONNECTION`](/sql/create-connection)
- Integration guides:
  - [Amazon S3](/serve-results/s3/)
  - [Snowflake (via S3)](/serve-results/snowflake/)

<!-- mz-docs page: sql/create-cluster -->

# CREATE CLUSTER
`CREATE CLUSTER` creates a new cluster.
`CREATE CLUSTER` creates a new [cluster](/fundamentals/concepts/clusters/).

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
query the [`mz_cluster_replica_sizes`](/sql/system-catalog/mz_catalog/#mz_cluster_replica_sizes) table.

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
[hydrate](/fundamentals/concepts/hydration/) the affected
objects before they can serve results. Hydration reads the input data
and rebuilds in-memory state, and its speed scales with the cluster
[size](/sql/create-cluster/#available-sizes).

The `AUTO SCALING STRATEGY (ON HYDRATION)` option lets a cluster **automatically
provision an extra burst replica at the configured `HYDRATION SIZE` while it has
un-hydrated objects**. This speeds up hydration without manually scaling the
cluster up before hydration and back down afterward. The steady-size replicas
continue hydrating in parallel, and once one of them catches up with the burst,
the burst replica lingers for the `LINGER DURATION` and is then removed. The
burst replica is an ordinary cluster replica, billed only for the time it is
provisioned. See [Usage & billing](/materialize-cloud/billing/) for details.

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
`HYDRATION SIZE` | The [size](/sql/create-cluster/#available-sizes) of the burst replica provisioned while the cluster has un-hydrated objects. Must differ from the cluster's steady `SIZE`. Choose a larger size to speed up hydration.
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
[`mz_internal.mz_cluster_auto_scaling_strategies`](/sql/system-catalog/mz_internal/#mz_cluster_auto_scaling_strategies)
catalog view.

### Dictionary compression

> **Public Preview:** This feature is in public preview.

Starting in v26.38, dictionary compression is available for managed clusters.
Dictionary compression reduces the memory that
[arrangements](/fundamentals/concepts/arrangements/#arrangements) use when a column holds
the same values repeatedly. Instead of storing a repeated column value each time
it appears, Materialize stores that value once and has each row reference it. This can reduce steady state memory requirements after hydration has completed.

Dictionary compression is specified per cluster replica, and is set to off by default. You opt in using the `EXPERIMENTAL ARRANGEMENT COMPRESSION` option, while creating or altering a cluster or cluster replica.

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
[`mz_cluster_replica_sizes`]: /sql/system-catalog/mz_catalog#mz_cluster_replica_sizes

<!-- mz-docs page: sql/create-cluster-replica -->

# CREATE CLUSTER REPLICA
`CREATE CLUSTER REPLICA` provisions a new replica of a cluster.

`CREATE CLUSTER REPLICA` provisions a new replica for an [**unmanaged**
cluster](/sql/create-cluster/#unmanaged-clusters).

> **Tip:** When getting started with Materialize, we recommend starting with managed
> clusters.

## Syntax

```mzsql
CREATE CLUSTER REPLICA [IF NOT EXISTS] <cluster_name>.<replica_name> (
    SIZE = <text>
);

```

| Syntax element | Description |
| --- | --- |
| **IF NOT EXISTS** | *Optional.* If specified, do not throw an error if a replica with the same name already exists on the cluster. Instead, issue a notice and skip the replica creation. Note that the existing replica is left untouched, its configuration is not updated to match the statement.  |
| `<cluster_name>` | The cluster you want to attach a replica to.  |
| `<replica_name>` | A name for this replica.  |
| `SIZE` | The size of the resource allocations for the cluster.  For valid size values, see [Available sizes](#available-sizes).  |

## Details

### Available sizes

The `SIZE` option for replicas is identical to the [`SIZE` option for
clusters](/sql/create-cluster/#available-sizes) option, except that the size applies only
to the new replica.

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
query the [`mz_cluster_replica_sizes`](/sql/system-catalog/mz_catalog/#mz_cluster_replica_sizes) table.

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

See also:

- [cc to M.1 size mapping](/sql/m1-cc-mapping/).

- [Materialize service consumption
  table](https://materialize.com/pdfs/pricing.pdf).

- [Blog:Scaling Beyond Memory: How Materialize Uses Swap for Larger
  Workloads](https://materialize.com/blog/scaling-beyond-memory/).

### Homogeneous vs. heterogeneous hardware provisioning

Because Materialize uses active replication, all replicas will be instructed to
do the same work, irrespective of their resource allocation.

For the most stable performance, we recommend using the same size and disk
configuration for all replicas.

However, it is possible to use different replica configurations in the same
cluster. In these cases, the replicas with less resources will likely be
continually burdened with a backlog of work. If all of the faster replicas
become unreachable, the system might experience delays in replying to requests
while the slower replicas catch up to the last known time that the faster
machines had computed.

## Example

```mzsql
CREATE CLUSTER REPLICA c1.r1 (SIZE = '800cc');
```

## Privileges

The privileges required to execute this statement are:

- Ownership of the cluster.

## See also

- [`DROP CLUSTER REPLICA`]

[AWS availability zone ID]: https://docs.aws.amazon.com/ram/latest/userguide/working-with-az-ids.html
[`DROP CLUSTER REPLICA`]: /sql/drop-cluster-replica

