# Azure deployment guidelines
General guidelines when deploying Self-Managed Materialize on Azure.
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

| Deployment size | `sku_name` | vCores / memory | Continuously-active objects (~60% CPU) |
|---|---|---|---|
| Entry / small production | `MO_Standard_E4ds_v5` | 4 / 32 GiB | ~4,500 |
| Recommended default | `MO_Standard_E16ds_v5` | 16 / 128 GiB | ~18,000 |

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
