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

**New Terraform:**
The new Materialize [Terraform module](https://github.com/MaterializeInc/materialize-terraform-self-managed/tree/main/azure/examples/simple) supports configuring swap out of the box.

**Legacy Terraform:**
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

**New Terraform:**

The Materialize [Terraform module](https://github.com/MaterializeInc/materialize-terraform-self-managed/tree/main/gcp/examples/simple) supports configuring swap out of the box.

**Legacy Terraform:**

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

**Legacy Terraform:**

The legacy Terraform modules
([terraform-aws-materialize](https://github.com/MaterializeInc/terraform-aws-materialize),
[terraform-google-materialize](https://github.com/MaterializeInc/terraform-google-materialize),
and
[terraform-azurerm-materialize](https://github.com/MaterializeInc/terraform-azurerm-materialize))
are no longer supported. Migrate to the [new Terraform
modules](https://github.com/MaterializeInc/materialize-terraform-self-managed)
first, then follow the steps in the **Terraform** tab.

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

