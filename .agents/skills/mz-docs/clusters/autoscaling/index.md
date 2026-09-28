# Autoscaling for hydration
Speed up cluster hydration with a temporary burst replica, monitor it, and know what to expect if the steady-size replica never catches up or the burst can't be provisioned.
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

## Configure autoscaling on an existing cluster

You can also add, change, or remove the strategy after the cluster already
exists:

```mzsql
ALTER CLUSTER fast_start SET (
    AUTO SCALING STRATEGY = (
        ON HYDRATION (HYDRATION SIZE = '800cc', LINGER DURATION = '15s')
    )
);
```

```mzsql
ALTER CLUSTER fast_start RESET (AUTO SCALING STRATEGY);
```

For the full option reference, see the `AUTO SCALING STRATEGY` option on
[`CREATE CLUSTER`](/sql/create-cluster/#autoscaling) and
[`ALTER CLUSTER`](/sql/alter-cluster/#speed-up-hydration-by-autoscaling-to-a-larger-size).

## Monitor an autoscaling event

To check whether a burst is currently running and what it's configured to do,
query
[`mz_internal.mz_cluster_auto_scaling_strategies`](/sql/system-catalog/mz_internal/#mz_cluster_auto_scaling_strategies):

```mzsql
SELECT
    c.name AS cluster,
    s.strategy->'on_hydration'->>'hydration_size' AS hydration_size,
    s.state->'burst'->>'burst_size' AS inflight_burst_size
FROM mz_internal.mz_cluster_auto_scaling_strategies AS s
JOIN mz_clusters AS c ON c.id = s.cluster_id;
```

`inflight_burst_size` is `NULL` when no burst is running, and reports the burst
replica's size while one is up. [`SHOW CLUSTERS`](/sql/show-clusters/) also
summarizes an in-flight burst in its `activity` column, and lists the burst
replica itself, at its larger size, in `replicas`:

```nofmt
   name      |   replicas             |          activity
-------------+------------------------+-----------------------------
 fast_start  | r1 (100cc), r2 (800cc) | hydration burst at 800cc
```

To check whether the objects driving the burst have finished hydrating on the
steady-size replicas, query
[`mz_internal.mz_hydration_statuses`](/sql/system-catalog/mz_internal/#mz_hydration_statuses)
for the cluster's steady-size replica IDs. Once every object is hydrated on a
steady-size replica, the burst replica lingers for the configured `LINGER
DURATION` and is then removed.

The [audit log](/sql/system-catalog/mz_catalog/#mz_audit_events) records when a
burst replica is created and dropped, so you can look back at past autoscaling
events after the fact.

## If the steady-size replica never hydrates

The burst replica has no maximum lifetime: if a steady-size replica never
catches up (for example, it's undersized and runs out of memory during
hydration), the burst replica keeps serving indefinitely at the configured
`HYDRATION SIZE`, billed for as long as it runs. This is deliberate: the burst
replica may be the only thing keeping the cluster able to serve results, so
Materialize does not tear it down just because it has been up a while.

If you find yourself in this situation, [resize the cluster](/sql/alter-cluster/#resizing)
to a `SIZE` that can hydrate the objects at steady state. The burst replica
keeps serving throughout the resize, so there's no gap in availability while
you find the right size.

## If capacity is unavailable

Provisioning the burst replica requires enough compute capacity to run it. In
**Materialize Self-Managed**, this means your Kubernetes cluster needs enough
spare resources (for example, available nodes) to schedule the burst replica's
pods. If it doesn't, Materialize keeps retrying automatically; no action is
required on your part, though the burst can't speed up hydration until
capacity frees up.

Either way, the burst is best-effort and never blocks the cluster: the
steady-size replicas come up and hydrate as usual, independently of whether the
burst replica could be provisioned, as long as there are enough resources for
them. If you plan to lean on autoscaling for hydration in a capacity-
constrained Self-Managed deployment, make sure your node pools have enough
spare capacity for the burst replicas you expect to run; see [Resize node
pools](/self-managed-deployments/deployment-guidelines/resize-node-pools/).

## Limitations

- Autoscaling for hydration only speeds up the initial hydration of indexes,
  materialized views, and Kafka upsert sources. It does not help with ongoing
  freshness or staleness, and it has no effect on
  [single-replica sources](/fundamentals/concepts/hydration/#objects-and-hydration)
  (PostgreSQL, MySQL, and SQL Server sources), which stay pinned to one replica
  regardless of the strategy.
- `AUTO SCALING STRATEGY` cannot be combined with a `SCHEDULE` other than the
  default `MANUAL`, and is only available on managed clusters.
- Autoscaling for hydration does not apply to the new generation during a
  Materialize Self-Managed version upgrade. Until it's promoted, the new
  generation runs read-only and can't provision a burst replica, so it
  hydrates only at its configured steady `SIZE`. See [Rollout
  strategies](/self-managed-deployments/upgrading/#rollout-strategies).

## Related pages

- [Hydration](/fundamentals/concepts/hydration/)
- [Optimize hydration requirements](/clusters/optimize-hydration-requirements/)
- [`CREATE CLUSTER`](/sql/create-cluster/#autoscaling)
- [`ALTER CLUSTER`](/sql/alter-cluster/#speed-up-hydration-by-autoscaling-to-a-larger-size)
- [`mz_internal.mz_cluster_auto_scaling_strategies`](/sql/system-catalog/mz_internal/#mz_cluster_auto_scaling_strategies)
- [Blue/green deployments](/developer-tools/dbt/blue-green-deployments/)
