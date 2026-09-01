# Deployment guidelines

Self-managed Materialize requires: a Kubernetes (v1.31+) cluster; PostgreSQL as
a metadata database; blob storage; and a license key.

## Available deployment guidelines

The following guides outline recommended configurations for deploying Materialize across different cloud environments.

- [AWS Deployment
  Guidelines](/self-managed-deployments/deployment-guidelines/aws-deployment-guidelines/)
- [Azure Deployment
  Guidelines](/self-managed-deployments/deployment-guidelines/azure-deployment-guidelines/)
- [GCP Deployment
  Guidelines](/self-managed-deployments/deployment-guidelines/gcp-deployment-guidelines/)

---

## AWS deployment guidelines

Self-managed Materialize requires: a Kubernetes (v1.31+) cluster; PostgreSQL as
a metadata database; blob storage; and a license key.

## Recommended instance types

As a general guideline, we recommend:

- ARM-based CPU
- A 1:8 ratio of vCPU to GiB memory.
- At least a 2:1 ratio of GiB local instance storage to GiB memory when using swap.

When operating in AWS, we recommend the following instances:

| EC2 Instances  |
| ---------------|
| `r8g`, `r7g`, and `r6g` families when running without local disk. |
| `r7gd` and `r6gd` families (and `r8gd` once available) when running with local disk.  *Recommended for production.* |

## Locally-attached NVMe storage

Configuring swap on nodes to use locally-attached NVMe storage allows
Materialize to spill to disk when operating on datasets larger than main memory.
This setup can provide significant cost savings and provides a more graceful
degradation rather than OOMing. Network-attached storage (like EBS volumes) can
significantly degrade performance and is not supported.

### Swap support

The Materialize [Terraform module](https://github.com/MaterializeInc/materialize-terraform-self-managed/tree/main/aws/examples/simple) supports configuring swap out of the box.

## Recommended metadata database sizing

<p>Self-managed Materialize uses an external PostgreSQL <strong>metadata database</strong> to
store its catalog and to coordinate the state of the objects it keeps up to
date. Every durable object that updates continuously (materialized views,
sources, sinks, and tables) produces a steady stream of small writes to the
metadata database. Metadata-database load therefore scales with the <strong>number of
continuously-updating objects</strong>, not with the volume of data flowing through
them.</p>
> **Note:** The sizing figures below assume the
> [`persist_pg_consensus_read_committed`](/self-managed-deployments/configuration-system-parameters/)
> system parameter is **enabled**. Enable it before sizing against these
> numbers. Materialize version `v26.33+` is required to set this parameter.

<h3 id="safe-operating-point">Safe operating point</h3>
<p>The primary factor that dictates the size of the metadata database is the
number of durable objects Materialize keeps continuously fresh (materialized
views, sources, sinks, and tables). Data volume, the query rate against
Materialize, and cluster size do not materially change metadata database load.
For example, a larger cluster running the same number of materialized views
places roughly the same load on the metadata database.</p>
<p>It is recommended that you size the metadata database so that its
<strong>steady-state CPU stays below 60%</strong>. The headroom between ~60% and full
utilization provides capacity to absorb everyday load variance, background
database maintenance, and Materialize zero-downtime upgrades.</p>

### RDS instance types

For the RDS PostgreSQL metadata database, we recommend:

- **Graviton (ARM)** memory-optimized instances (the `r6g` / `r7g` families).
- **Multi-AZ** for production.
- **gp3** storage.

| Deployment size | Instance | vCPU / memory | Storage | Provisioned IOPS | Continuously-active objects (~60% CPU) |
|---|---|---|---|---|---|
| Entry / small production | `db.r6g.large` | 2 / 16 GiB | 200 GiB | 3,000 (baseline) | ~4,500 |
| Recommended default | `db.r6g.2xlarge` | 8 / 64 GiB | 400 GiB | 6,000 | ~18,000 |

## TLS

When running with TLS in production, run with certificates from an official
Certificate Authority (CA) rather than self-signed certificates.

## Upgrading guideline

Whe upgrading:

- **Always** check the [version-specific upgrade
  notes](/self-managed-deployments/upgrading/version-notes/).

- **Always** upgrade the operator **first** and ensure version compatibility
  between the operator and the Materialize instance you are upgrading to.

- **Always** upgrade your Materialize instances **after** upgrading the operator
  to ensure compatibility.

## Karpenter node expiry

We recommend setting `expire_after` to `Never` on the Materialize nodepool
since node expiry is not a voluntary disruption. With any other value,
Karpenter removes nodes that reach their configured lifetime even if they run
pods annotated with `karpenter.sh/do-not-disrupt`. This can cause downtime
unless you gracefully roll the nodes first. The [Materialize Terraform
modules](https://github.com/MaterializeInc/materialize-terraform-self-managed)
default `expire_after` to `Never`.

## Karpenter termination grace period

We recommend leaving `termination_grace_period` unset on nodepools that run
Materialize workloads. When this value is set, Karpenter terminates nodes after
the configured grace period following any change to the nodepool
configuration, even if they run pods annotated with
`karpenter.sh/do-not-disrupt`.

Before v6.0.0, the modules set `termination_grace_period` to `300s`. If you are
using a version earlier than v6.0.0, upgrade to v6.0.0 using the [v6.0.0
upgrade
notes](https://github.com/MaterializeInc/materialize-terraform-self-managed/blob/v6.0.0/README.md#v600).
Starting in v6.0.0, the Materialize Terraform modules leave
`termination_grace_period` unset by default.

## Node pool resizing

The VM type of a Kubernetes node pool is immutable on EKS, AKS, and GKE, so
changing it triggers a `destroy + create` that fails while Materialize pods are
still running on the pool. The supported pattern is to add a second pool with
the new VM type, roll out the Materialize instance so new pods land on it, and
then drop the old pool.

For the full procedure, see
[Resize node pools](/self-managed-deployments/deployment-guidelines/resize-node-pools/).

---

## Azure deployment guidelines

## Recommended instance types

As a general guideline, we recommend:

- ARM-based CPU.
- A 1:8 ratio of vCPU to GiB memory.
- At least a 2:1 ratio of GiB local instance storage to GiB memory when using swap.

### Recommended Azure VM Types with Local NVMe Disks

When operating on Azure in production, we recommend [Epdsv6
sizes](https://learn.microsoft.com/en-us/azure/virtual-machines/sizes/memory-optimized/epdsv6-series?tabs=sizebasic#sizes-in-series)
Azure VM Types with Local NVMe Disk:

| VM Size            | vCPUs | Memory  | Ephemeral Disk | Disk-to-RAM Ratio |
| ------------------ | ----- | ------- | -------------- | ----------------- |
| Standard_E2pds_v6  | 2     | 16 GiB  | 75 GiB         | ~4.7:1           |
| Standard_E4pds_v6  | 4     | 32 GiB  | 150 GiB        | ~4.7:1           |
| Standard_E8pds_v6  | 8     | 64 GiB  | 300 GiB        | ~4.7:1           |
| Standard_E16pds_v6 | 16    | 128 GiB | 600 GiB        | ~4.7:1           |
| Standard_E32pds_v6 | 32    | 256 GiB | 1,200 GiB      | ~4.7:1           |

> **Warning:** These VM types provide <red>**ephemeral**</red> local NVMe SSD disks. Data is
> <red>**lost**</red> when the VM is stopped or deleted.

## Locally-attached NVMe storage

Configuring swap on nodes to use locally-attached NVMe storage allows
Materialize to spill to disk when operating on datasets larger than main memory.
This setup can provide significant cost savings and provides a more graceful
degradation rather than OOMing. Network-attached storage (like EBS volumes) can
significantly degrade performance and is not supported.

### Swap support

The Materialize [Terraform module](https://github.com/MaterializeInc/materialize-terraform-self-managed/tree/main/azure/examples/simple) supports configuring swap out of the box.

## Recommended Azure Blob Storage

Materialize writes **block** blobs on Azure. As a general guideline, we
recommend **Premium block blob** storage accounts.

## Recommended metadata database sizing

<p>Self-managed Materialize uses an external PostgreSQL <strong>metadata database</strong> to
store its catalog and to coordinate the state of the objects it keeps up to
date. Every durable object that updates continuously (materialized views,
sources, sinks, and tables) produces a steady stream of small writes to the
metadata database. Metadata-database load therefore scales with the <strong>number of
continuously-updating objects</strong>, not with the volume of data flowing through
them.</p>
> **Note:** The sizing figures below assume the
> [`persist_pg_consensus_read_committed`](/self-managed-deployments/configuration-system-parameters/)
> system parameter is **enabled**. Enable it before sizing against these
> numbers. Materialize version `v26.33+` is required to set this parameter.

<h3 id="safe-operating-point">Safe operating point</h3>
<p>The primary factor that dictates the size of the metadata database is the
number of durable objects Materialize keeps continuously fresh (materialized
views, sources, sinks, and tables). Data volume, the query rate against
Materialize, and cluster size do not materially change metadata database load.
For example, a larger cluster running the same number of materialized views
places roughly the same load on the metadata database.</p>
<p>It is recommended that you size the metadata database so that its
<strong>steady-state CPU stays below 60%</strong>. The headroom between ~60% and full
utilization provides capacity to absorb everyday load variance, background
database maintenance, and Materialize zero-downtime upgrades.</p>

### Flexible Server SKUs

For the Azure Database for PostgreSQL flexible server that backs the metadata
database, we recommend:

- The **Memory Optimized** tier (E-series), which provides the 1:8
  vCore-to-memory ratio recommended for the metadata database.
- **Zone-redundant high availability** for production.
- **Premium SSD v2** storage, which includes 3,000 IOPS and 125 MB/s at any
  size.

| Deployment size | `sku_name` | vCores / memory | Storage | Provisioned IOPS | Continuously-active objects (~60% CPU) |
|---|---|---|---|---|---|
| Entry / small production | `MO_Standard_E4ds_v5` | 4 / 32 GiB | 128 GiB | 3,000 (included) | ~4,500 |
| Recommended default | `MO_Standard_E16ds_v5` | 16 / 128 GiB | 512 GiB | 6,000 | ~18,000 |

## TLS

When running with TLS in production, run with certificates from an official
Certificate Authority (CA) rather than self-signed certificates.

## Upgrading guideline

Whe upgrading:

- **Always** check the [version-specific upgrade
  notes](/self-managed-deployments/upgrading/version-notes/).

- **Always** upgrade the operator **first** and ensure version compatibility
  between the operator and the Materialize instance you are upgrading to.

- **Always** upgrade your Materialize instances **after** upgrading the operator
  to ensure compatibility.

## Node pool resizing

The VM type of a Kubernetes node pool is immutable on EKS, AKS, and GKE, so
changing it triggers a `destroy + create` that fails while Materialize pods are
still running on the pool. The supported pattern is to add a second pool with
the new VM type, roll out the Materialize instance so new pods land on it, and
then drop the old pool.

For the full procedure, see
[Resize node pools](/self-managed-deployments/deployment-guidelines/resize-node-pools/).

---

## GCP deployment guidelines

## Recommended instance types

As a general guideline, we recommend:

- ARM-based CPU.
- A 1:8 ratio of vCPU to GiB memory.
- At least a 2:1 ratio of GiB local instance storage to GiB memory when using swap.

When operating on GCP in production, we recommend the Arm-based [C4A
high-memory series]. Both C4A and C4 offer local SSDs only on their `-lssd`
machine variants, which bundle a fixed number of Titanium SSD disks.

| Series | Examples   |
| ------ | ---------- |
| [C4A high-memory series] (recommended) | `c4a-highmem-16-lssd` or `c4a-highmem-32-lssd` |
| [C4 high-memory series] | `c4-highmem-16-lssd` or `c4-highmem-32-lssd` |

C4A is not available in every region. Where it is unavailable, use the
x86-based [C4 high-memory series] instead.

To maintain the recommended disk-to-RAM ratio for your machine type, see
[Number of local SSDs](#number-of-local-ssds) to determine the number of local
SSDs to use.

See also [Locally attached NVMe storage](#locally-attached-nvme-storage).

## Number of local SSDs

Each local SSD in GCP provides 375GB of storage. Use the appropriate number
of local SSDs to ensure your total disk space is at least twice the amount of RAM in your
machine type for optimal Materialize performance.

C4A and C4 bundle a fixed number of Titanium SSD disks in each `-lssd`
machine variant. The count is not configurable, but every high-memory `-lssd`
variant satisfies the 2:1 disk-to-RAM ratio:

| Machine Type          | RAM     | Bundled Local SSDs | Total SSD Storage |
|-----------------------|---------|--------------------|-------------------|
| `c4a-highmem-8-lssd`  | `64GB`  | 2                  | `750GB`           |
| `c4a-highmem-16-lssd` | `128GB` | 4                  | `1500GB`          |
| `c4a-highmem-32-lssd` | `256GB` | 6                  | `2250GB`          |
| `c4a-highmem-64-lssd` | `512GB` | 14                 | `5250GB`          |
| `c4-highmem-8-lssd`   | `62GB`  | 1                  | `375GB`           |
| `c4-highmem-16-lssd`  | `124GB` | 2                  | `750GB`           |
| `c4-highmem-32-lssd`  | `248GB` | 5                  | `1875GB`          |
| `c4-highmem-48-lssd`  | `372GB` | 8                  | `3000GB`          |

For other machine series, the local SSD count is configurable but may only
support predefined values. To determine the valid number of local SSDs to
attach for your machine type, see the [GCP
documentation](https://cloud.google.com/compute/docs/disks/local-ssd#lssd_disk_options).

[C4A high-memory series]: https://cloud.google.com/compute/docs/general-purpose-machines#c4a_series

[C4 high-memory series]: https://cloud.google.com/compute/docs/general-purpose-machines#c4_series

## Locally-attached NVMe storage

Configuring swap on nodes to use locally-attached NVMe storage allows
Materialize to spill to disk when operating on datasets larger than main memory.
This setup can provide significant cost savings and provides a more graceful
degradation rather than OOMing. Network-attached storage (like EBS volumes) can
significantly degrade performance and is not supported.

### Swap support

The Materialize [Terraform module](https://github.com/MaterializeInc/materialize-terraform-self-managed/tree/main/gcp/examples/simple) supports configuring swap out of the box.

## CPU affinity

It is strongly recommended to enable the Kubernetes `static` [CPU management policy](https://kubernetes.io/docs/tasks/administer-cluster/cpu-management-policies/#static-policy).
This ensures that each worker thread of Materialize is given exclusively access to a vCPU. Our benchmarks have shown this
to substantially improve the performance of compute-bound workloads.

## Recommended metadata database sizing

<p>Self-managed Materialize uses an external PostgreSQL <strong>metadata database</strong> to
store its catalog and to coordinate the state of the objects it keeps up to
date. Every durable object that updates continuously (materialized views,
sources, sinks, and tables) produces a steady stream of small writes to the
metadata database. Metadata-database load therefore scales with the <strong>number of
continuously-updating objects</strong>, not with the volume of data flowing through
them.</p>
> **Note:** The sizing figures below assume the
> [`persist_pg_consensus_read_committed`](/self-managed-deployments/configuration-system-parameters/)
> system parameter is **enabled**. Enable it before sizing against these
> numbers. Materialize version `v26.33+` is required to set this parameter.

<h3 id="safe-operating-point">Safe operating point</h3>
<p>The primary factor that dictates the size of the metadata database is the
number of durable objects Materialize keeps continuously fresh (materialized
views, sources, sinks, and tables). Data volume, the query rate against
Materialize, and cluster size do not materially change metadata database load.
For example, a larger cluster running the same number of materialized views
places roughly the same load on the metadata database.</p>
<p>It is recommended that you size the metadata database so that its
<strong>steady-state CPU stays below 60%</strong>. The headroom between ~60% and full
utilization provides capacity to absorb everyday load variance, background
database maintenance, and Materialize zero-downtime upgrades.</p>

### Cloud SQL machine types

For the Cloud SQL for PostgreSQL instance that backs the metadata database, we
recommend:

- The **Enterprise Plus** edition with a **performance-optimized (N-series)**
  machine type, which provides the 1:8 vCPU-to-memory ratio recommended for the
  metadata database. Avoid shared-core machine types (`db-f1-micro`,
  `db-g1-small`) in production.
- A **regional (highly available)** configuration for production.
- **SSD** storage. IOPS and throughput cannot be configured independently: they
  scale with the provisioned size at 30 IOPS and 0.48 MB/s per GB.

| Deployment size | `tier` | vCPU / memory | Storage | Provisioned IOPS | Continuously-active objects (~60% CPU) |
|---|---|---|---|---|---|
| Entry / small production | `db-perf-optimized-N-4` | 4 / 32 GB | 200 GB | 6,000 (set by size) | ~4,500 |
| Recommended default | `db-perf-optimized-N-16` | 16 / 128 GB | 500 GB | 15,000 (set by size) | ~18,000 |

## TLS

When running with TLS in production, run with certificates from an official
Certificate Authority (CA) rather than self-signed certificates.

## Upgrading guideline

Whe upgrading:

- **Always** check the [version-specific upgrade
  notes](/self-managed-deployments/upgrading/version-notes/).

- **Always** upgrade the operator **first** and ensure version compatibility
  between the operator and the Materialize instance you are upgrading to.

- **Always** upgrade your Materialize instances **after** upgrading the operator
  to ensure compatibility.

## Node pool resizing

The VM type of a Kubernetes node pool is immutable on EKS, AKS, and GKE, so
changing it triggers a `destroy + create` that fails while Materialize pods are
still running on the pool. The supported pattern is to add a second pool with
the new VM type, roll out the Materialize instance so new pods land on it, and
then drop the old pool.

For the full procedure, see
[Resize node pools](/self-managed-deployments/deployment-guidelines/resize-node-pools/).

## Node pool upgrades

GKE upgrades node pools automatically, and this cannot be disabled. Configure
the operator's node upgrade rollout trigger so Materialize moves its pods to
the replacement nodes gracefully instead of being evicted. See [GKE node pool
upgrades](/self-managed-deployments/deployment-guidelines/gke-node-pool-upgrades/).

---

## GKE node pool upgrades

GKE upgrades node pools automatically, for example to roll out new node
images. This cannot be disabled, only delayed with maintenance windows and
exclusions. An upgrade eventually drains the nodes Materialize runs on, and
without coordination that means `environmentd` and `clusterd` pods are
evicted, causing an outage until they reschedule and rehydrate.

The Materialize operator (v26.36.0 and later) can watch for GKE node pool
upgrades and move the pods with the normal rollout machinery before GKE
drains anything. This gives the same minimal-downtime behavior as any other
Materialize rollout instead of an eviction.

> **Note:** If you deploy with the [Materialize Terraform
> modules](https://github.com/MaterializeInc/materialize-terraform-self-managed)
> (v9.0.0 and later), this is configured for you and no action is needed. The
> rest of this page describes the setup for deployments that do not use those
> modules.

## How it works

The trigger relies on the [blue-green node upgrade
strategy](https://cloud.google.com/kubernetes-engine/docs/concepts/node-pool-upgrade-strategies#blue-green-upgrade-strategy),
where GKE creates a replacement (green) pool, cordons all of the original
(blue) nodes, waits, then drains the blue nodes in batches and finally
deletes them after a soak period. The operator uses that wait window:

1. **Arm.** A GKE `UpgradeEvent` cluster notification, pulled from a Pub/Sub
   subscription, arms a watched node pool. The GKE API is also polled at
   startup and hourly, so a notification missed while the operator was
   restarting does not lose the upgrade.

2. **Gate.** The armed pool's blue-green upgrade phase is polled until it
   reports `WAITING_TO_DRAIN_BLUE_POOL` or later, meaning every blue node has
   been cordoned. Triggering earlier risks scheduling the new generation of
   pods onto a blue node that simply had not been cordoned yet.

3. **Trigger.** Each Materialize instance with `environmentd` or `clusterd`
   pods on the cordoned nodes gets a forced rollout, by way of the
   `materialize.cloud/force-rollout` annotation on the `v1` Materialize
   resource. The new generation can only schedule onto the green nodes, and
   the old generation is torn down gracefully once the new one is ready.
   Instances that already have a rollout in progress are skipped.

Arming on upgrade notifications rather than on any cordon avoids expensive
spurious rollouts when a node is cordoned for reasons that do not mean it is
going away, such as an administrator debugging it.

## Requirements

- Materialize operator and Helm chart v26.36.0 or later.
- The `v1` Materialize CRD (`operator.args.installV1CRD=true`), since
  rollouts are triggered through it. See [Adopting the v1
  CRD](/self-managed-deployments/upgrading/adopting-the-v1-crd/).
- `operator.cloudProvider.type=gcp`.
- [Workload Identity
  Federation](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity)
  enabled on the cluster, for the operator's access to the Pub/Sub and GKE
  APIs. The node pool the operator runs on also needs the `GKE_METADATA`
  workload metadata mode, otherwise its pods cannot reach the metadata server
  to fetch credentials.
- A GKE control plane on 1.34.0-gke.2201000 or later, for the autoscaled
  blue-green rollout policy.
- Cluster autoscaling enabled on the node pools running Materialize. GKE
  requires it for the autoscaled rollout policy, which relies on the
  autoscaler to grow the replacement pool.

## Setup

Throughout, replace `CLUSTER_NAME`, `CONTROL_PLANE_LOCATION` (the cluster's
region or zone), `PROJECT_ID`, `NODE_POOL_NAME`, and `OPERATOR_NAMESPACE`
with your own values.

### 1. Put the Materialize node pools on autoscaled blue-green upgrades

The autoscaled rollout policy creates the green pool empty and lets the
cluster autoscaler scale it up as pods move over, so you do not pay for a
duplicate pool for the whole upgrade.

```bash
gcloud container node-pools update NODE_POOL_NAME \
  --cluster=CLUSTER_NAME \
  --project=PROJECT_ID \
  --location=CONTROL_PLANE_LOCATION \
  --enable-blue-green-upgrade \
  --autoscaled-rollout-policy=wait-for-drain-duration=259200s
```

`wait-for-drain-duration` is how long GKE waits after cordoning the blue
nodes before it starts draining them. This is the window the operator has to
complete its rollouts, so size it against how long a rollout of your largest
instance takes. `259200s` (3 days) is the GKE default and 7 days is the
maximum.

Upgrade settings apply in place, without replacing the pool.

### 2. Publish upgrade notifications to Pub/Sub

Create a topic for the cluster's notifications, and a **pull** subscription
for the operator:

```bash
gcloud pubsub topics create gke-upgrade-notifications --project=PROJECT_ID

gcloud pubsub subscriptions create orchestratord-upgrade-notifications \
  --project=PROJECT_ID \
  --topic=gke-upgrade-notifications \
  --message-retention-duration=86400s \
  --expiration-period=never
```

`--expiration-period=never` matters: node pool upgrades can be weeks apart,
and a subscription that expires from inactivity stops delivering
notifications. Message retention only needs to cover an operator restart,
since the hourly GKE API poll catches anything that expires.

Then point the cluster at the topic, filtered to upgrade events:

```bash
gcloud container clusters update CLUSTER_NAME \
  --location=CONTROL_PLANE_LOCATION \
  --notification-config=pubsub=ENABLED,pubsub-topic=projects/PROJECT_ID/topics/gke-upgrade-notifications,filter="UpgradeEvent"
```

If the topic lives in a different project than the cluster, grant the GKE
service agent
(`service-PROJECT_NUMBER@container-engine-robot.iam.gserviceaccount.com`)
`roles/pubsub.viewer` and `roles/pubsub.publisher` on the topic.

### 3. Grant the operator access to Pub/Sub and the GKE API

Create a GCP service account, grant it the two roles the trigger needs, and
link it to the operator's Kubernetes service account through workload
identity:

```bash
gcloud iam service-accounts create orchestratord --project=PROJECT_ID

SA="orchestratord@PROJECT_ID.iam.gserviceaccount.com"

# Pull the cluster notifications.
gcloud pubsub subscriptions add-iam-policy-binding \
  orchestratord-upgrade-notifications \
  --project=PROJECT_ID \
  --role=roles/pubsub.subscriber \
  --member="serviceAccount:$SA"

# Read node pool upgrade state.
gcloud projects add-iam-policy-binding PROJECT_ID \
  --role=roles/container.clusterViewer \
  --member="serviceAccount:$SA"

# Let the operator's Kubernetes service account impersonate it.
gcloud iam service-accounts add-iam-policy-binding "$SA" \
  --project=PROJECT_ID \
  --role=roles/iam.workloadIdentityUser \
  --member="serviceAccount:PROJECT_ID.svc.id.goog[OPERATOR_NAMESPACE/orchestratord]"
```

The member above uses `orchestratord`, the default
`serviceAccount.name` of the Helm chart. Use your own value if you have
overridden it.

The Kubernetes-side permissions (reading nodes and pods, patching Materialize
resources) are part of the chart's RBAC and need no extra configuration.

### 4. Configure the Helm chart

```yaml
serviceAccount:
  annotations:
    iam.gke.io/gcp-service-account: orchestratord@PROJECT_ID.iam.gserviceaccount.com

operator:
  args:
    installV1CRD: true
  cloudProvider:
    type: gcp
    providers:
      gcp:
        enabled: true
        nodeUpgradeRolloutTrigger:
          enabled: true
          notificationSubscription: "projects/PROJECT_ID/subscriptions/orchestratord-upgrade-notifications"
          clusterName: "CLUSTER_NAME"
          clusterLocation: "CONTROL_PLANE_LOCATION"
          # Empty watches every node pool in the cluster.
          watchedNodePools:
            - "NODE_POOL_NAME"
```

Restrict `watchedNodePools` to the pools that run Materialize workloads.
Watching pools that never host `environmentd` or `clusterd` pools costs
nothing but adds noise.

### 5. Allow egress to the GKE metadata server

If you restrict the operator's egress with network policies, allow it to
reach the metadata server. Workload identity credentials are fetched over
plain HTTP on `169.254.169.254:80`, and under [GKE Dataplane
V2](https://cloud.google.com/kubernetes-engine/docs/concepts/dataplane-v2)
the metadata server also answers on `169.254.169.252:988`, which is the
destination policy is enforced against after DNAT. Allow both to ensure the trigger
can authenticate otherwise you may see failures logging `no available authentication
method found`.

Plain HTTP is not a concern here. Both addresses are link-local and served by
the `gke-metadata-server` agent running on the pod's own node, so credentials
never travel over the network.

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-metadata-server-egress
  namespace: OPERATOR_NAMESPACE
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: materialize-operator
  policyTypes:
    - Egress
  egress:
    - to:
        - ipBlock:
            cidr: 169.254.169.254/32
      ports:
        - protocol: TCP
          port: 80
    - to:
        - ipBlock:
            cidr: 169.254.169.252/32
      ports:
        - protocol: TCP
          port: 988
```

## Verify

Nothing happens until GKE next upgrades a watched pool, so the check after
setup is that the operator started the watcher and authenticated. It logs
`starting GCP node upgrade watcher` at startup, `arming node pool` when it
picks up an upgrade, and `triggering rollout` when it acts on one. A failure
to authenticate is retried and logged as `failed to initialize GCP
credentials`:

```bash
kubectl logs -n OPERATOR_NAMESPACE -l app.kubernetes.io/name=materialize-operator \
  | grep -iE "node upgrade watcher|node pool|triggering rollout|GCP credentials"
```

The polling itself is only logged at debug level, so on a healthy cluster
with no upgrade in flight the startup line is the only output.

During an upgrade, the triggered rollouts are visible on the Materialize
resources and behave like any other rollout:

```bash
kubectl get materialize <instance-name> \
  -n <materialize-instance-namespace> \
  -o jsonpath='{.metadata.annotations.materialize\.cloud/force-rollout}'
kubectl get pods -n <materialize-instance-namespace> -o wide
```

See [Rollout
behavior](/self-managed-deployments/deployment-guidelines/resize-node-pools/#rollout-behavior)
for what to expect. The default `WaitUntilReady` strategy runs both
generations at once, so the green pool needs headroom for the new generation
on top of the old one. With the autoscaled rollout policy the cluster
autoscaler provides it, subject to the pool's `--max-nodes`.

## Limitations

- Only `environmentd` and `clusterd` pods are moved. `balancerd`, the
  console, and other pods are ordinary deployments and stay on the cordoned
  blue nodes until GKE drains them.
- There are no pod disruption budgets for `environmentd` and `clusterd`. A
  pool left on the default `SURGE` upgrade strategy, or an upgrade whose
  wait window elapses before the rollouts finish, will still evict pods.
- Rollouts are triggered through the `v1` Materialize CRD only.
- Instances using the `ManuallyPromote` rollout strategy are not protected
  unless someone promotes the new generation within the wait window. The
  triggered rollout brings the new generation up on the green nodes, but the
  serving generation stays on the cordoned blue nodes until it is promoted.
  An unpromoted rollout is cancelled once it exceeds `rolloutRequestTimeout`
  (24 hours by default), leaving the instance back on the blue nodes, and the
  trigger then requests another rollout, repeating until the upgrade
  finishes. `ImmediatelyPromoteCausingDowntime` moves the pods to the green
  nodes, but with the downtime that strategy always incurs. `WaitUntilReady`
  is the only strategy this feature makes an upgrade transparent under.

## See also

- [GCP deployment
  guidelines](/self-managed-deployments/deployment-guidelines/gcp-deployment-guidelines/)
- [Resize node
  pools](/self-managed-deployments/deployment-guidelines/resize-node-pools/)
- [Operator configuration](/self-managed-deployments/operator-configuration/)

---

## Resize node pools

When you need a larger (or smaller) VM type for the nodes that Materialize
runs on, how to proceed depends on how the nodes are managed:

- **Static node pools** (the GCP and Azure modules, and AWS node groups when
  not using Karpenter) cannot change VM type in place. The underlying cloud
  APIs do not support it, so the Terraform providers mark the VM type field
  `ForceNew` (GKE: `machine_type`, AKS: `vm_size`, EKS node groups:
  `instance_types`), and changing it plans a `destroy + create`. The destroy
  fails if the pool still has Materialize pods on it, because nothing in the
  Terraform graph migrates the workloads to a replacement pool first. The
  supported pattern is to **add a second pool, taint the old pool so no new
  pods schedule on it, trigger a Materialize rollout so the new generation of
  pods lands on the new pool, then drop the old pool**.

- **Karpenter-managed nodes** (the default for Materialize nodes in the AWS
  modules) size nodes per pod rather than per pool. Changing the VM type is a
  template change on the Karpenter `NodePool`, followed by a Materialize
  rollout to move the pods onto new-spec nodes.

> **Note:** The default rollout strategy (`WaitUntilReady`) used in the outlined steps
> temporarily runs the old and new generations of Materialize simultaneously. Make
> sure the new node pool has enough capacity to accommodate both generations
> during the rollout.

## Steps

**Terraform:**

These steps apply to the [Materialize Terraform
modules](https://github.com/MaterializeInc/materialize-terraform-self-managed).

**GCP:**

##### 1. Declare a second node pool with the new VM type

Add a new nodepool module instance alongside the existing one, keeping the old
pool unchanged. Copy the existing configuration, then change:

- The `prefix`, so the pool gets a distinct name.
- The `machine_type`.
- For a swap-enabled pool, a distinct `disk_setup_name` (e.g.
  `disk-setup-xl`). It names the disk-setup namespace and daemonset, which
  otherwise collide with the old pool's.
- The `local_ssd_count`, if the new machine type bundles a different number of
  local SSDs (`c4a-highmem-16-lssd` has 4, for example).

Keep the same labels and taints as the existing pool so Materialize pods are
eligible to schedule on it. For example:

```hcl
module "materialize_nodepool" {
  # ... existing pool config, unchanged ...
  machine_type = "c4a-highmem-8-lssd"
}

module "materialize_nodepool_xl" {
  # ... copy of the existing config, with a new prefix ...
  machine_type    = "c4a-highmem-16-lssd"
  local_ssd_count = 4
  disk_setup_name = "disk-setup-xl"
}
```

Run `terraform init` to pick up the new module instance, then apply:

```bash
terraform init
terraform apply
```

Both pools now exist. Materialize pods have not yet been scheduled on the new
pool.

##### 2. Taint the old pool so no new pods schedule on it

Add a decommission taint to the old pool's `node_taints`:

```hcl
node_taints = [
  # ... existing taints ...
  {
    key    = "materialize.cloud/decommissioned"
    value  = "true"
    effect = "NO_SCHEDULE"
  }
]
```

Taints update in place (no pool replacement) on the provider versions the
modules require. Running pods are not evicted, but no new pods schedule to the
old pool, and the cluster autoscaler will not scale it up for pending pods,
since they don't tolerate the taint. Use a taint key the Materialize pods
don't tolerate (not `materialize.cloud/workload` or `kubernetes.io/arch`).

Apply:

```bash
terraform apply
```

##### 3. Roll out the Materialize instance

With the old pool tainted, a forced rollout lands the new generation of pods
on the new pool.

The Materialize spec itself is unchanged (the node move happens at the
Kubernetes cluster level and not in the Materialize CR), so you need to force
the rollout.

**Materialize CRD v1:**

The `v1` version of the Materialize CRD is the default starting in v4.0.0 of
the Terraform modules. Set the `force_rollout` input of the
`materialize-instance` module to a new UUID:

```hcl
module "materialize_instance" {
  # ...
  rollout_strategy = "WaitUntilReady"  # default
  force_rollout    = "00000000-0000-0000-0000-000000000002"  # any new UUID
}
```

**Materialize CRD v1alpha1:**

If you have reverted to the `v1alpha1` version of the Materialize CRD, set
both the `request_rollout` and `force_rollout` inputs of the
`materialize-instance` module to the same new UUID:

```hcl
module "materialize_instance" {
  # ...
  rollout_strategy = "WaitUntilReady"  # default
  request_rollout  = "00000000-0000-0000-0000-000000000002"  # any new UUID
  force_rollout    = "00000000-0000-0000-0000-000000000002"  # same UUID
}
```

Apply:

```bash
terraform apply
```

See [Rollout behavior](#rollout-behavior) for what to expect during the
rollout. Verify the new `environmentd` and `clusterd` pods are only scheduled
onto the new pool.

##### 4. Remove the old pool

Once the rollout has completed, the old pool's nodes have no Materialize
workloads on them. Remove the old nodepool module instance from your Terraform
configuration and apply:

```bash
terraform apply
```

The destroy step now succeeds because the pool has no running workloads.

##### 5. Optional: rename the new pool back

If you want the pool to keep the original name (for example because other
Terraform or kubectl tooling references it), repeat these steps with a third
pool that carries the original name. Otherwise, accept the new name and update
any references.

**Azure:**

##### 1. Declare a second node pool with the new VM type

Add a new nodepool module instance alongside the existing one, keeping the old
pool unchanged. Copy the existing configuration, then change:

- The `prefix`, so the pool gets a distinct name. The AKS node pool name is
  the prefix with dashes removed, truncated to 12 characters, so the new
  prefix must differ from the old one within those characters. A suffix
  appended to a long prefix is silently truncated away and the apply fails
  because the pool name already exists.
- The `vm_size`.
- For a swap-enabled pool, a distinct `disk_setup_name` (e.g.
  `disk-setup-xl`). It names the disk-setup namespace and daemonset, which
  otherwise collide with the old pool's.

Keep the same labels and taints as the existing pool so Materialize pods are
eligible to schedule on it. For example:

```hcl
module "materialize_nodepool" {
  # ... existing pool config, unchanged ...
  prefix  = "mzpool"
  vm_size = "Standard_E4pds_v6"
}

module "materialize_nodepool_xl" {
  # ... copy of the existing config ...
  prefix          = "mzpoolxl"
  vm_size         = "Standard_E8pds_v6"
  disk_setup_name = "disk-setup-xl"
}
```

Run `terraform init` to pick up the new module instance, then apply:

```bash
terraform init
terraform apply
```

Both pools now exist. Materialize pods have not yet been scheduled on the new
pool.

##### 2. Taint the old pool so no new pods schedule on it

Add a decommission taint to the old pool's `node_taints`:

```hcl
node_taints = [
  # ... existing taints ...
  {
    key    = "materialize.cloud/decommissioned"
    value  = "true"
    effect = "NO_SCHEDULE"
  }
]
```

Taints update in place (no pool replacement) on the provider versions the
modules require. Running pods are not evicted, but no new pods schedule to the
old pool, and the cluster autoscaler will not scale it up for pending pods,
since they don't tolerate the taint. Use a taint key the Materialize pods
don't tolerate (not `materialize.cloud/workload` or `kubernetes.io/arch`).

Apply:

```bash
terraform apply
```

##### 3. Roll out the Materialize instance

With the old pool tainted, a forced rollout lands the new generation of pods
on the new pool.

The Materialize spec itself is unchanged (the node move happens at the
Kubernetes cluster level and not in the Materialize CR), so you need to force
the rollout.

**Materialize CRD v1:**

The `v1` version of the Materialize CRD is the default starting in v4.0.0 of
the Terraform modules. Set the `force_rollout` input of the
`materialize-instance` module to a new UUID:

```hcl
module "materialize_instance" {
  # ...
  rollout_strategy = "WaitUntilReady"  # default
  force_rollout    = "00000000-0000-0000-0000-000000000002"  # any new UUID
}
```

**Materialize CRD v1alpha1:**

If you have reverted to the `v1alpha1` version of the Materialize CRD, set
both the `request_rollout` and `force_rollout` inputs of the
`materialize-instance` module to the same new UUID:

```hcl
module "materialize_instance" {
  # ...
  rollout_strategy = "WaitUntilReady"  # default
  request_rollout  = "00000000-0000-0000-0000-000000000002"  # any new UUID
  force_rollout    = "00000000-0000-0000-0000-000000000002"  # same UUID
}
```

Apply:

```bash
terraform apply
```

See [Rollout behavior](#rollout-behavior) for what to expect during the
rollout. Verify the new `environmentd` and `clusterd` pods are only scheduled
onto the new pool.

##### 4. Remove the old pool

Once the rollout has completed, the old pool's nodes have no Materialize
workloads on them. Remove the old nodepool module instance from your Terraform
configuration and apply:

```bash
terraform apply
```

The destroy step now succeeds because the pool has no running workloads.

##### 5. Optional: rename the new pool back

If you want the pool to keep the original name (for example because other
Terraform or kubectl tooling references it), repeat these steps with a third
pool that carries the original name. Otherwise, accept the new name and update
any references.

**AWS:**

> **Warning:** Prior to v6.0.0 of the Terraform modules, the nodepools had `termination_grace_period`
> set to `300s`. This caused nodes to be terminated five minutes after any change to the
> nodepool configuration, ignoring the `karpenter.sh/do-not-disrupt` annotation on pods.
> If you are running an older version of the Terraform modules, to avoid downtime,
> we recommend upgrading to at least v6.0.0, following the steps in the
> [upgrade notes](https://github.com/MaterializeInc/materialize-terraform-self-managed/blob/v6.0.0/README.md#v600).
> On later versions, the `termination_grace_period` is unset by default.
> We recommend keeping it unset on nodepools for Materialize workloads.

The AWS modules provision Materialize nodes with Karpenter, so there is no
second pool to create. Karpenter provisions new-spec nodes on demand.

If you have disabled Karpenter and run Materialize on a static EKS node
group, follow the blue-green pattern from the GCP and Azure tabs instead,
changing `instance_types` on a second node group module instance.

##### 1. Update the instance types

Change `instance_types` on the Materialize `karpenter-ec2nodeclass` and
`karpenter-nodepool` module instances and apply:

```hcl
module "ec2nodeclass_materialize" {
  # ...
  instance_types = ["r7gd.4xlarge"]
}

module "nodepool_materialize" {
  # ...
  instance_types = ["r7gd.4xlarge"]
}
```

```bash
terraform apply
```

Karpenter marks the existing nodes as drifted but does not drain them: the
`environmentd` and `clusterd` pods carry the `karpenter.sh/do-not-disrupt`
annotation, which blocks voluntary disruption while they run. This relies on
the nodepool's `expire_after` being `Never`, see [Karpenter node
expiry](/self-managed-deployments/deployment-guidelines/aws-deployment-guidelines/#karpenter-node-expiry).

##### 2. Cordon the drifted nodes

Cordon the existing Materialize nodes so the rollout's new pods cannot
schedule onto them and instead trigger Karpenter to provision nodes with the
new instance types:

```bash
# The nodepool name is the `name` input of the karpenter-nodepool module
# ("materialize" in the examples).
for node in $(kubectl get nodes -l karpenter.sh/nodepool=materialize -o name); do
  kubectl cordon "$node"
done
```

Nodes that Karpenter provisions after this point are not cordoned.

##### 3. Roll out the Materialize instance

The Materialize spec itself is unchanged (the node move happens at the
Kubernetes cluster level and not in the Materialize CR), so you need to force
the rollout.

**Materialize CRD v1:**

The `v1` version of the Materialize CRD is the default starting in v4.0.0 of
the Terraform modules. Set the `force_rollout` input of the
`materialize-instance` module to a new UUID:

```hcl
module "materialize_instance" {
  # ...
  rollout_strategy = "WaitUntilReady"  # default
  force_rollout    = "00000000-0000-0000-0000-000000000002"  # any new UUID
}
```

**Materialize CRD v1alpha1:**

If you have reverted to the `v1alpha1` version of the Materialize CRD, set
both the `request_rollout` and `force_rollout` inputs of the
`materialize-instance` module to the same new UUID:

```hcl
module "materialize_instance" {
  # ...
  rollout_strategy = "WaitUntilReady"  # default
  request_rollout  = "00000000-0000-0000-0000-000000000002"  # any new UUID
  force_rollout    = "00000000-0000-0000-0000-000000000002"  # same UUID
}
```

Apply:

```bash
terraform apply
```

Karpenter provisions new-spec nodes for the pending pods of the new
generation. See [Rollout behavior](#rollout-behavior) for what to expect
during the rollout. Verify the new `environmentd` and `clusterd` pods are
only scheduled onto the new nodes.

##### 4. Verify the old nodes are removed

Once the rollout has completed and the old generation's pods are gone, the
cordoned nodes are empty and Karpenter consolidates them away (the modules
configure `consolidationPolicy: WhenEmpty`). Confirm they disappear:

```bash
kubectl get nodes -l karpenter.sh/nodepool=materialize
```

**Manual:**

If you manage your infrastructure without the Materialize Terraform modules:

##### 1. Create a second node pool with the new VM type

Using your cloud provider's tooling, create a second node pool with the same
labels and taints as the existing pool (so Materialize pods are eligible to
schedule on it), a distinct name, and the new VM type.

If your nodes are managed by Karpenter, skip this step and instead update the
instance requirements on the Karpenter `NodePool`. Karpenter provisions
new-spec nodes on demand once the old nodes are cordoned.

##### 2. Keep new pods off the old nodes

For a static pool, add a decommission taint, such as
`materialize.cloud/decommissioned=true:NoSchedule`, to the old pool. Apply the
taint at the node pool level through your cloud provider rather than with
`kubectl taint`: node-level taints do not carry over to nodes the cluster
autoscaler adds to the pool later. Running pods are not evicted, but no new
pods schedule to the old pool, and the cluster autoscaler will not scale it
up for pending pods, since they don't tolerate the taint. Use a taint key the
Materialize pods don't tolerate (not `materialize.cloud/workload` or
`kubernetes.io/arch`).

For Karpenter-managed nodes, cordon the old nodes instead. Nodes that
Karpenter provisions afterwards are not cordoned.

##### 3. Roll out the Materialize instance to land new pods on the new nodes

Use the Materialize CR's rollout machinery to have the operator create a new
generation of `environmentd` and `clusterd` pods. Because the Materialize
spec itself is unchanged (the node move happens at the Kubernetes cluster
level and not in the Materialize CR), you need to force the rollout.

**Materialize CRD v1:**

Set `forceRollout` to a new UUID:

```bash
kubectl patch materialize <instance-name> \
  -n <materialize-instance-namespace> \
  --type='merge' \
  -p "{\"spec\": {\"forceRollout\": \"$(uuidgen)\"}}"
```

**Materialize CRD v1alpha1:**

Set both `requestRollout` and `forceRollout` to the same new UUID:

```bash
UUID="$(uuidgen)"
kubectl patch materialize <instance-name> \
  -n <materialize-instance-namespace> \
  --type='merge' \
  -p "{\"spec\": {\"requestRollout\": \"$UUID\", \"forceRollout\": \"$UUID\"}}"
```

See [Rollout behavior](#rollout-behavior) for what to expect. Verify the new
`environmentd` and `clusterd` pods are only scheduled onto the new nodes.

##### 4. Remove the old pool

Once the rollout has completed, the old nodes have no Materialize workloads
on them. Delete the old node pool using your cloud provider's tooling. For
Karpenter-managed nodes, empty drifted nodes are consolidated away
automatically.

## Rollout behavior

The default rollout strategy, `WaitUntilReady`, creates the new generation
alongside the old, waits for it to catch up, then promotes it and tears down
the old generation. This briefly doubles the resource footprint during the
rollout (so make sure the new nodes have the capacity) but otherwise incurs
minimal downtime. For other rollout strategies (manual promotion,
immediate-with-downtime), see
[Rollout Configuration](/self-managed-deployments/upgrading/#rollout-configuration).

Watch the rollout progress:

```bash
kubectl get materialize <instance-name> -n <materialize-instance-namespace> -w
kubectl get pods -n <materialize-instance-namespace> -o wide
```

You should see the new generation pods come up on the new nodes, the
`UpToDate` condition flip to `True`, and the old generation pods get
terminated.

## Why not change the VM type in place

For static node pools, it's tempting to update the existing pool's
`machine_type` / `vm_size` / `instance_types` and re-apply. The Terraform
plan correctly shows `destroy + create`, but the apply gets stuck on the
destroy because the pool still has running pods that nothing has moved off.
You end up with an error like:

```
cannot update node types in pool
```

The pattern above avoids the wedge by bringing up a replacement pool first and
using the operator's rollout machinery to migrate the workloads, instead of
relying on `kubectl drain` or the cloud provider's pool deletion logic to do
the right thing on its own.

## See also

- [AWS deployment guidelines](/self-managed-deployments/deployment-guidelines/aws-deployment-guidelines/)
- [Azure deployment guidelines](/self-managed-deployments/deployment-guidelines/azure-deployment-guidelines/)
- [GCP deployment guidelines](/self-managed-deployments/deployment-guidelines/gcp-deployment-guidelines/)
- [Upgrading](/self-managed-deployments/upgrading/) -- rollout configuration
  reference (`requestRollout`, `rolloutStrategy`)

