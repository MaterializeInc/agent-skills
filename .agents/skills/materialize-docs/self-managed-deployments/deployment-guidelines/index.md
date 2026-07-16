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
- A 8:1 ratio of GiB local instance storage to GiB memory when using swap.

When operating in AWS, we recommend the following instances:

| EC2 Instances  |
| ---------------|
| `r8g`, `r7g`, and `r6g` families when running without local disk. |
| `r7gd` and `r6gd` families (and `r8gd` once available) when running with local disk.  *Recommended for production.* |

Starting in v0.3.1, the Materialize on AWS Terraform uses `["r7gd.2xlarge"]` as
the default [`node_group_instance_types`].

[`node_group_instance_types`]:
    https://github.com/MaterializeInc/terraform-aws-materialize?tab=readme-ov-file#input_node_group_instance_types

## Locally-attached NVMe storage

Configuring swap on nodes to use locally-attached NVMe storage allows
Materialize to spill to disk when operating on datasets larger than main memory.
This setup can provide significant cost savings and provides a more graceful
degradation rather than OOMing. Network-attached storage (like EBS volumes) can
significantly degrade performance and is not supported.

### Swap support

**New Terraform:**

#### New Terraform

The new Materialize [Terraform module](https://github.com/MaterializeInc/materialize-terraform-self-managed/tree/main/aws/examples/simple) supports configuring swap out of the box.

**Legacy Terraform:**
#### Legacy Terraform

The Legacy Terraform provider adds preliminary swap support in v0.6.1, via the [`swap_enabled`](https://github.com/MaterializeInc/terraform-aws-materialize?tab=readme-ov-file#input_swap_enabled) variable.
With this change, the Terraform:
  - Creates a node group for Materialize.
  - Configures NVMe instance store volumes as swap using a daemonset.
  - Enables swap at the Kubelet.

See [Upgrade Notes](https://github.com/MaterializeInc/terraform-aws-materialize?tab=readme-ov-file#v061).

> **Note:** If deploying `v25.2`, Materialize clusters will not automatically use swap unless they are configured with a `memory_request` less than their `memory_limit`. In `v26`, this will be handled automatically.

## TLS

When running with TLS in production, run with certificates from an official
Certificate Authority (CA) rather than self-signed certificates.

## Upgrading guideline

<p>Whe upgrading:</p>
<ul>
<li>
<p><strong>Always</strong> check the <a href="/self-managed-deployments/upgrading/version-notes/" >version-specific upgrade
notes</a>.</p>
</li>
<li>
<p><strong>Always</strong> upgrade the operator <strong>first</strong> and ensure version compatibility
between the operator and the Materialize instance you are upgrading to.</p>
</li>
<li>
<p><strong>Always</strong> upgrade your Materialize instances <strong>after</strong> upgrading the operator
to ensure compatibility.</p>
</li>
</ul>

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
- An 8:1 ratio of GiB local instance storage to GiB memory when using swap.

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

**New Terraform:**
#### New Terraform

The new Materialize [Terraform module](https://github.com/MaterializeInc/materialize-terraform-self-managed/tree/main/azure/examples/simple) supports configuring swap out of the box.

**Legacy Terraform:**
#### Legacy Terraform

The Legacy Terraform provider, adds preliminary swap support in v0.6.1, via the [`swap_enabled`](https://github.com/MaterializeInc/terraform-azurerm-materialize?tab=readme-ov-file#input_swap_enabled) variable.
With this change, the Terraform:
  - Creates a node group for Materialize.
  - Configures NVMe instance store volumes as swap using a daemonset.
  - Enables swap at the Kubelet.

See [Upgrade Notes](https://github.com/MaterializeInc/terraform-azurerm-materialize?tab=readme-ov-file#v061).

> **Note:** If deploying `v25.2`, Materialize clusters will not automatically use swap unless they are configured with a `memory_request` less than their `memory_limit`. In `v26`, this will be handled automatically.

## Recommended Azure Blob Storage

Materialize writes **block** blobs on Azure. As a general guideline, we
recommend **Premium block blob** storage accounts.

## TLS

When running with TLS in production, run with certificates from an official
Certificate Authority (CA) rather than self-signed certificates.

## Upgrading guideline

<p>Whe upgrading:</p>
<ul>
<li>
<p><strong>Always</strong> check the <a href="/self-managed-deployments/upgrading/version-notes/" >version-specific upgrade
notes</a>.</p>
</li>
<li>
<p><strong>Always</strong> upgrade the operator <strong>first</strong> and ensure version compatibility
between the operator and the Materialize instance you are upgrading to.</p>
</li>
<li>
<p><strong>Always</strong> upgrade your Materialize instances <strong>after</strong> upgrading the operator
to ensure compatibility.</p>
</li>
</ul>

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
- An 8:1 ratio of GiB local instance storage to GiB memory when using swap.

When operating on GCP in production, we recommend the following machine types
that support local SSD attachment:

| Series | Examples   |
| ------ | ---------- |
| [N2 high-memory series] | `n2-highmem-16` or `n2-highmem-32` with local NVMe SSDs |
| [N2D  high-memory series] | `n2d-highmem-16` or `n2d-highmem-32` with local NVMe SSDs |

To maintain the recommended 8:1 disk-to-RAM ratio for your machine type, see
[Number of local SSDs](#number-of-local-ssds) to determine the number of local
SSDs to use.

See also [Locally attached NVMe storage](#locally-attached-nvme-storage).

## Number of local SSDs

Each local NVMe SSD in GCP provides 375GB of storage. Use the appropriate number
of local SSDs to ensure your total disk space is at least twice the amount of RAM in your
machine type for optimal Materialize performance.

> **Note:** Your machine type may only supports predefined number of local SSDs. For instance, `n2d-highmem-32` allows only the following number of local
> SSDs: `4`,`8`,`16`, or `24`. To determine the valid number of Local SSDs to attach for your machine type, see the [GCP
> documentation](https://cloud.google.com/compute/docs/disks/local-ssd#lssd_disk_options).

For example, the following table provides a minimum local SSD count to ensure
the 2:1 disk-to-RAM ratio. Your actual
count will depend on the [your machine
type](https://cloud.google.com/compute/docs/disks/local-ssd#lssd_disk_options).

| Machine Type    | RAM     | Required Disk | Minimum Local SSD Count | Total SSD Storage |
|-----------------|---------|---------------|-----------------------------|-------------------|
| `n2-highmem-8`  | `64GB`  | `128GB`       | 1                           | `375GB`           |
| `n2-highmem-16` | `128GB` | `256GB`       | 1                           | `375GB`           |
| `n2-highmem-32` | `256GB` | `512GB`       | 2                           | `750GB`           |
| `n2-highmem-64` | `512GB` | `1024GB`      | 3                           | `1125GB`          |
| `n2-highmem-80` | `640GB` | `1280GB`      | 4                           | `1500GB`          |

[N2 high-memory series]: https://cloud.google.com/compute/docs/general-purpose-machines#n2-high-mem

[N2D high-memory series]: https://cloud.google.com/compute/docs/general-purpose-machines#n2d_machine_types

## Locally-attached NVMe storage

Configuring swap on nodes to use locally-attached NVMe storage allows
Materialize to spill to disk when operating on datasets larger than main memory.
This setup can provide significant cost savings and provides a more graceful
degradation rather than OOMing. Network-attached storage (like EBS volumes) can
significantly degrade performance and is not supported.

### Swap support

**New Terraform:**

#### New Terraform

The Materialize [Terraform module](https://github.com/MaterializeInc/materialize-terraform-self-managed/tree/main/gcp/examples/simple) supports configuring swap out of the box.

**Legacy Terraform:**
#### Legacy Terraform

The Legacy Terraform provider, adds preliminary swap support in v0.6.1, via the [`swap_enabled`](https://github.com/MaterializeInc/terraform-google-materialize?tab=readme-ov-file#input_swap_enabled) variable.
With this change, the Terraform:
  - Creates a node group for Materialize.
  - Configures NVMe instance store volumes as swap using a daemonset.
  - Enables swap at the Kubelet.

See [Upgrade Notes](https://github.com/MaterializeInc/terraform-google-materialize?tab=readme-ov-file#v061).

> **Note:** If deploying `v25.2`, Materialize clusters will not automatically use swap unless they are configured with a `memory_request` less than their `memory_limit`. In `v26`, this will be handled automatically.

## CPU affinity

It is strongly recommended to enable the Kubernetes `static` [CPU management policy](https://kubernetes.io/docs/tasks/administer-cluster/cpu-management-policies/#static-policy).
This ensures that each worker thread of Materialize is given exclusively access to a vCPU. Our benchmarks have shown this
to substantially improve the performance of compute-bound workloads.

## TLS

When running with TLS in production, run with certificates from an official
Certificate Authority (CA) rather than self-signed certificates.

## Upgrading guideline

<p>Whe upgrading:</p>
<ul>
<li>
<p><strong>Always</strong> check the <a href="/self-managed-deployments/upgrading/version-notes/" >version-specific upgrade
notes</a>.</p>
</li>
<li>
<p><strong>Always</strong> upgrade the operator <strong>first</strong> and ensure version compatibility
between the operator and the Materialize instance you are upgrading to.</p>
</li>
<li>
<p><strong>Always</strong> upgrade your Materialize instances <strong>after</strong> upgrading the operator
to ensure compatibility.</p>
</li>
</ul>

## Node pool resizing

The VM type of a Kubernetes node pool is immutable on EKS, AKS, and GKE, so
changing it triggers a `destroy + create` that fails while Materialize pods are
still running on the pool. The supported pattern is to add a second pool with
the new VM type, roll out the Materialize instance so new pods land on it, and
then drop the old pool.

For the full procedure, see
[Resize node pools](/self-managed-deployments/deployment-guidelines/resize-node-pools/).

---

## Resize node pools

When you need a larger (or smaller) VM type for a node pool that Materialize
runs on, the change cannot be applied in place. The underlying cloud APIs do
not support an in-place "change VM type" operation on an existing managed node
pool, so the Terraform providers mark the VM type field `ForceNew` on all three
clouds:

- GKE: `google_container_node_pool.node_config.machine_type`
- AKS: `azurerm_kubernetes_cluster_node_pool.vm_size`
- EKS: `aws_eks_node_group.instance_types`

Changing the value makes Terraform plan a `destroy + create`. The destroy step
fails if the pool still has Materialize pods running on it, because nothing in
the Terraform graph migrates the workloads to a replacement pool first.

The supported pattern is to **add a second pool, trigger a Materialize rollout
so the new generation of pods lands on it, then drop the old pool**.

> **Note:** This guide applies to deployments that use static node groups (the default for
> the GCP and Azure modules, and for the AWS modules when Karpenter is disabled).
> If you're using [Karpenter](https://karpenter.sh/) for dynamic node provisioning,
> resizing is just a `NodePool` template change because Karpenter sizes nodes per
> pod rather than per pool.

## Steps

### 1. Declare a second node pool with the new VM type

Add a second node pool alongside the existing one. Give it the same labels and
taints as the existing pool so Materialize pods are eligible to schedule on it,
but a distinct name and the new VM type.

The exact shape depends on which module or resource you're using. For example,
with `terraform-google-modules/kubernetes-engine` on GCP:

```hcl
module "gke" {
  # ...
  node_pools = [
    {
      name         = "materialize"
      machine_type = "n2-highmem-8"
      # ...
    },
    {
      name         = "materialize-xl"
      machine_type = "n2-highmem-16"
      # ... same labels and taints as above ...
    },
  ]
}
```

Or, if you're using a single-pool module wrapper, instantiate it twice:

```hcl
module "materialize_nodepool" {
  # ... existing pool config ...
  machine_type = "n2-highmem-8"
}

module "materialize_nodepool_xl" {
  # ... copy the existing config, change name and machine_type ...
  machine_type = "n2-highmem-16"
}
```

The Azure and AWS equivalents change `vm_size` (Azure) or `instance_types` (AWS)
instead of `machine_type`.

Apply. Both pools now exist. Materialize pods have not yet been scheduled on
the new pool.

### 2. Cordon the old pool so new pods schedule on the new one

```bash
# Cordon every node in the old pool so the scheduler stops placing new pods there
for node in $(kubectl get nodes -l <your-old-pool-label> -o name); do
  kubectl cordon "$node"
done
```

DaemonSets and existing pods stay in place; only new pods are kept off the
cordoned nodes.

### 3. Roll out the Materialize instance to land new pods on the new pool

Use the Materialize CR's rollout machinery to have the operator create a new
generation of `environmentd` and `clusterd` pods. With the old pool cordoned,
the new generation schedules onto the new pool's nodes.

If you're using the `materialize-instance` Terraform module, bump both
`force_rollout` and `request_rollout` inputs to a new UUID and apply:

```hcl
module "materialize_instance" {
  # ...
  rollout_strategy = "WaitUntilReady"  # default
  request_rollout  = "00000000-0000-0000-0000-000000000002"  # any new UUID
  force_rollout    = "00000000-0000-0000-0000-000000000002"  # any new UUID
}
```

```bash
terraform apply
```

If you're managing the Materialize CR directly, the equivalent kubectl
command is:

```bash
kubectl patch materialize <instance-name> \
  -n <materialize-instance-namespace> \
  --type='merge' \
  -p "{\"spec\": {\"requestRollout\": \"$(uuidgen)\", \"forceRollout\": \"$(uuidgen)\"}}"
```

Both paths set `requestRollout` and `forceRollout` to new UUIDs, which is what
the operator watches for. Because the Materialize spec itself is unchanged (the
node pool move happens at the Kubernetes cluster level and not in the
Materialize CR), you need to update `forceRollout` (in addition to
`requestRollout`).

The default `rolloutStrategy` is `WaitUntilReady`, which creates the new
generation alongside the old, waits for it to catch up, then promotes it and
tears down the old generation. This briefly doubles the resource footprint
during the rollout (so make sure the new pool has the capacity) but is
otherwise zero-downtime. For other rollout strategies (manual promotion,
immediate-with-downtime), see
[Rollout Configuration](/self-managed-deployments/upgrading/#rollout-configuration).

Watch the rollout progress:

```bash
kubectl get materialize <instance-name> -n <materialize-instance-namespace> -w
kubectl get pods -n <materialize-instance-namespace> -o wide
```

You should see the new generation pods come up on the new pool's nodes, the
`UpToDate` condition flip to `True`, and the old generation pods get
terminated.

### 4. Remove the old pool

Once the rollout has completed, the old pool's nodes have no Materialize
workloads on them. Remove the original node pool entry (or module call) from
your Terraform configuration and apply.

The destroy step now succeeds because the pool has no running workloads.

### 5. Optional: rename the new pool back

If you want the pool to keep the original name (for example because other
Terraform or kubectl tooling references it), repeat the same pattern in
reverse: add a third pool with the original name, roll out onto it, then drop
the renamed pool. Otherwise, accept the new name and update any references.

## Why not change the VM type in place

It's tempting to update the existing pool's `machine_type` / `vm_size` /
`instance_types` and re-apply. The Terraform plan correctly shows `destroy +
create`, but the apply gets stuck on the destroy because the pool still has
running pods that nothing has moved off. You end up with an error like:

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

