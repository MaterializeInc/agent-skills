# AWS deployment guidelines
General guidelines when deploying Self-Managed Materialize on AWS.
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

| Deployment size | Instance | vCPU / memory | Continuously-active objects (~60% CPU) |
|---|---|---|---|
| Entry / small production | `db.r6g.large` | 2 / 16 GiB | ~4,500 |
| Recommended default | `db.r6g.2xlarge` | 8 / 64 GiB | ~18,000 |

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
