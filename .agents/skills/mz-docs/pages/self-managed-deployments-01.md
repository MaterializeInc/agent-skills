<!-- mz-docs page: self-managed-deployments -->

# Self-Managed Deployments

Learn about the key components and architecture of self-managed Materialize deployments.

## Overview

Whereas Materialize Cloud gives you a fully managed service for Materialize,
Self-Managed Materialize allows you to deploy Materialize in your own
infrastructure.

Self-Managed Materialize deployments on Kubernetes consist of several layers of
components that work together to provide a fully functional database
environment. Understanding these components and how they interact is essential
for deploying, managing, and troubleshooting your Self-Managed Materialize.

## Getting started

To help you get started, the following installation guides are available:

### Install using Helm Commands

|  Guide         | Description  |
| ------------- | -------|
| [Install locally on Kind](/self-managed-deployments/installation/install-on-local-kind/) | Uses standard Helm commands to deploy Materialize to a Kind cluster in Docker.

### Install using Terraform Modules

> **Note:** We recommend pinning your module sources to specific tags to avoid unexpected breaking
> changes in future versions.
> We recommend updating your module source tags when updating Materialize versions,
> taking care to follow any instructions in the release notes.

Materialize provides [**Terraform
modules**](https://github.com/MaterializeInc/materialize-terraform-self-managed/tree/main?tab=readme-ov-file#materialize-self-managed-terraform-modules),
which provides concrete examples and an opinionated model for deploying Materialize.

| Module | Description |
| --- | --- |
| <a href="https://github.com/MaterializeInc/materialize-terraform-self-managed/tree/main/aws" >Amazon Web Services (AWS)</a> | An example Terraform module for deploying Materialize on AWS. See <a href="/self-managed-deployments/installation/install-on-aws/" >Install on AWS</a> for detailed instructions usage. |
| <a href="https://github.com/MaterializeInc/materialize-terraform-self-managed/tree/main/azure" >Azure</a> | An example Terraform module for deploying Materialize on Azure. See <a href="/self-managed-deployments/installation/install-on-azure/" >Install on Azure</a> for detailed instructions usage. |
| <a href="https://github.com/MaterializeInc/materialize-terraform-self-managed/tree/main/gcp" >Google Cloud Platform (GCP)</a> | An example Terraform module for deploying Materialize on GCP. See <a href="/self-managed-deployments/installation/install-on-gcp/" >Install on GCP</a> for detailed instructions usage. |

## Architecture layers

A Self-Managed Materialize deployment is organized into the following layers:

Layer | Component | Description
------|-----------|------------
**Infrastructure** | [Helm Chart](#helm-chart) | Package manager component that bootstraps the Kubernetes deployment
**Orchestration** | [Materialize Operator](#materialize-operator) | Kubernetes operator that manages Materialize instances
**Database** | [Materialize Instance](#materialize-instance) | The Materialize database instance itself
**Compute** | [Clusters and Replicas](#clusters-and-replicas) | Isolated compute resources for workloads

### Helm chart

The Helm chart is the entry point for deploying Materialize in a self-managed
Kubernetes environment. It defines and deploys the Materialize Operator as part
of the Helm package management workflow.

The Helm repository is hosted at `https://materializeinc.github.io/materialize`.

```sh
helm repo add materialize https://materializeinc.github.io/materialize
```

#### What gets installed

When you install the Materialize Helm Chart (e.g., `helm install materialize
materialize/materialize-operator ...`), it:

- Deploys the **Materialize Operator** as a Kubernetes deployment.
- Creates necessary cluster-wide resources (CRDs, RBAC roles, service accounts).
- Configures operator settings and permissions.

Once installed, the **Materialize Operator** handles the deployment and
management of Materialize instances.

### Materialize Operator

The Materialize Operator (implemented as `orchestratord`) is a Kubernetes operator that automates the deployment and lifecycle management of Materialize instances. It implements the [Kubernetes operator pattern](https://kubernetes.io/docs/concepts/extend-kubernetes/operator/) to extend Kubernetes with domain-specific knowledge about Materialize.

#### Managed resources

The operator watches for Materialize custom resources and creates/manages all the Kubernetes resources required to run a Materialize instance, including:

- **Namespaces**: Isolated Kubernetes namespaces for each instance
- **Services**: Network services for connecting to Materialize
- **Network Policies**: Network isolation and security rules
- **Certificates**: TLS certificates for secure connections
- **ConfigMaps and Secrets**: Configuration and sensitive data
- **Deployments**: These support the `balancerd` and `console` pod used as the ingress layer for Materialize.
- **StatefulSets**: `environmentd` and `clusterd` which are the database control plane and compute resources respectively.

#### Configuration

For configuration options for the Materialize Operator, see
the [Materialize Operator Configuration
page](/self-managed-deployments/operator-configuration/).

### Materialize Instance

A Materialize instance is the actual database that you connect to and interact
with. Each instance is an isolated Materialize deployment (deployed via a
Kubernetes Custom Resource) with its own data, configuration, and compute
resources.

#### Components

When you create a Materialize instance, the operator deploys three core
components as Kubernetes resources:

- **balancerd**: A pgwire and HTTP proxy that routes all Materialize client
  connections to `environmentd` for handling. `balancerd` is deployed as a
  Kubernetes Deployment.

- **environmentd**: The main database control plane, deployed as a
  StatefulSet.

  **`environmentd`** runs as a Kubernetes pod and is the primary component of a
  Materialize instance. It houses the control plane and contains:

  - **Adapter**: The SQL interface that handles client connections, query parsing, and planning.
  - **Storage Controller**: Maintains durable metadata for storage.
  - **Compute Controller**: Orchestrates compute resources and manages system state.

  On startup, `environmentd` will create several built-in clusters.

- **console**: Web-based administration interface, deployed as a Deployment.

#### Instance responsibilities

A Materialize instance manages:

- **SQL objects**: Sources, views, materialized views, indexes, sinks
- **Schemas and databases**: Logical organization of objects
- **User connections**: SQL client connections and authentication
- **Catalog metadata**: System information about all objects and configuration
- **Compute orchestration**: Coordination of work across clusters and replicas

#### Deploying with the operator

To deploy Materialize instances with the operator, create and apply Materialize
custom resource definitions(CRDs). For a full list of fields available for the
Materialize CR, see [Materialize CRD Field
Descriptions](/self-managed-deployments/materialize-crd-field-descriptions/).

**v1alpha1:**

<p><code>v1alpha1</code> is the default CRD version for the Materialize Helm
chart. The Terraform modules default to <code>v1</code> starting in v4.0.0.
With <code>v1alpha1</code>, instance rollouts require manually rotating a
UUID.</p>

```yaml
apiVersion: materialize.cloud/v1alpha1
kind: Materialize
metadata:
  name: 12345678-1234-1234-1234-123456789012
  namespace: materialize-environment
spec:
  environmentdImageRef: materialize/environmentd:v26.43.0
# ... additional fields omitted for brevity
```

**v1:**

<p>The <code>v1</code> CRD is available starting in v26.30. It is opt-in for the Helm chart and the default for the Terraform modules starting in v4.0.0. See <a href="/self-managed-deployments/upgrading/adopting-the-v1-crd/">Adopting the v1 CRD</a> to enable it.</p>

```yaml
apiVersion: materialize.cloud/v1
kind: Materialize
metadata:
  name: 12345678-1234-1234-1234-123456789012
  namespace: materialize-environment
spec:
  environmentdImageRef: materialize/environmentd:v26.43.0
# ... additional fields omitted for brevity
```

When you first apply the Materialize custom resource, the operator automatically
creates all required Kubernetes resources.

#### Modifying the custom resource

**v1alpha1:**

<p><code>v1alpha1</code> is the default CRD version for the Materialize Helm
chart. The Terraform modules default to <code>v1</code> starting in v4.0.0.
With <code>v1alpha1</code>, instance rollouts require manually rotating a
UUID.</p>

To modify a custom resource, update the CRD with your changes, including the
`requestRollout` field with a new UUID value. When you apply the CRD, the
operator will roll out the changes.

> **Note:** If you do not specify a new `requestRollout` UUID, the operator
> watches for updates but does not roll out the changes.

**v1:**

<p>The <code>v1</code> CRD is available starting in v26.30. It is opt-in for the Helm chart and the default for the Terraform modules starting in v4.0.0. See <a href="/self-managed-deployments/upgrading/adopting-the-v1-crd/">Adopting the v1 CRD</a> to enable it.</p>

To modify a custom resource, update the CRD with your changes.
When you apply the CRD, the operator will roll out the changes.

For a full list of fields available for the Materialize CR, see [Materialize CRD
Field
Descriptions](/self-managed-deployments/materialize-crd-field-descriptions/).

See also:

- [Upgrade Overview](/self-managed-deployments/upgrading/)

#### Connecting to an instance

Once deployed, you interact with a Materialize instance through the Materialize
Console or standard PostgreSQL-compatible tools and drivers:

```bash
# Connect with psql
psql "postgres://materialize@<host>:6875/materialize"
```

Once connected, you can issue SQL commands to create sources, define views, run queries, and manage the database:

```sql
-- Create a source
CREATE SOURCE my_source FROM KAFKA ...;

-- Create a materialized view
CREATE MATERIALIZED VIEW my_view AS
  SELECT ... FROM my_source ...;

-- Query the view
SELECT * FROM my_view;
```

### Clusters and Replicas

Clusters are isolated pools of compute resources that execute workloads in Materialize. They provide resource isolation and fault tolerance for your data processing pipelines.

For a comprehensive overview of clusters in Materialize, see the [Clusters concept page](/fundamentals/concepts/clusters/).

#### Cluster architecture

- **Clusters**: Logical groupings of compute resources dedicated to specific workloads (sources, sinks, indexes, materialized views, queries)
- **Replicas**: Physical instantiations of a cluster's compute resources, deployed as Kubernetes StatefulSets

Each replica contains identical compute resources and processes the same data independently, providing fault tolerance and high availability.

#### Kubernetes resources

When you create a cluster with one or more replicas in Materialize, the instance coordinates with the operator to create:

- One or more **StatefulSet** resources (one per replica)
- **Pods** within each StatefulSet that execute the actual compute workload
- **Persistent volumes** (if configured) for scratch disk space

For example:

```sql
-- Create a cluster with 2 replicas
CREATE CLUSTER my_cluster SIZE = '100cc', REPLICATION FACTOR = 2;
```

This creates two separate StatefulSets in Kubernetes, each running compute processes.

#### Managing clusters

You interact with clusters primarily through SQL:

```sql
-- Create a cluster
CREATE CLUSTER ingest_cluster SIZE = '50cc', REPLICATION FACTOR = 1;

-- Use the previous cluster for a source
CREATE SOURCE my_source
  IN CLUSTER ingest_cluster
  FROM KAFKA ...;

-- Create a cluster for materialized views
CREATE CLUSTER compute_cluster SIZE = '100cc', REPLICATION FACTOR = 2;

-- Use the previous cluster for a materialized view
CREATE MATERIALIZED VIEW my_view
  IN CLUSTER compute_cluster AS
  SELECT ... FROM my_source ...;

-- Resize a cluster
ALTER CLUSTER compute_cluster SET (SIZE = '200cc');
```

Materialize handles the underlying Kubernetes resource creation and management automatically.

### Workflow

The following outlines the workflow process, summarizing how the various
components work together:

1. **Install the Helm chart**: This deploys the Materialize Operator to your
   Kubernetes cluster.

1. **Create a Materialize instance**: Apply a Materialize custom resource. The
   operator detects this and creates all necessary Kubernetes resources,
   including the `environmentd`, `balancerd`, and `console` pods.

1. **Connect to the instance**: Use the Materialize Console on port 8080 to
   connect to the `console` service endpoint or SQL client on port 6875 to
   connect to the `balancerd` service endpoint.

   If authentication is enabled, you must first connect to the Materialize
   Console and set up users.

1. **Create clusters**: Issue SQL commands to create clusters. Materialize
   coordinates with the operator to provision StatefulSets for replicas.

1. **Run your workloads**: Create sources, materialized views, indexes, and
   sinks on your clusters.

## Related pages

- [Installation guides](/self-managed-deployments/installation/)
- [Materialize Operator
  Configuration](/self-managed-deployments/operator-configuration/)
- [Materialize CRD Field
  Descriptions](/self-managed-deployments/materialize-crd-field-descriptions/)
- [Operational guidelines](/self-managed-deployments/deployment-guidelines/)
- [Clusters concept page](/fundamentals/concepts/clusters/)
- [Materialize architecture overview](/fundamentals/concepts/)

<!-- mz-docs page: self-managed-deployments/appendix -->

# Appendix

## Table of contents

- [Appendix: Cluster sizes](./appendix-cluster-sizes/)
- [Appendix: Prepare for swap and upgrade to v26.0](./upgrade-to-swap/)

<!-- mz-docs page: self-managed-deployments/appendix/appendix-cluster-sizes -->

# Cluster sizes
Reference page on self-managed cluster sizes
## Default Cluster Sizes

For Self-Managed Materialize, the cluster sizes are configured with the
following default resource allocations:

<table>
<thead>
<tr>
<th>Size</th>
<th>Scale</th>
<th>CPU Limit</th>
<th>Disk Limit</th>
<th>Memory Limit</th>
</tr>
</thead>
<tbody>

<tr>
<td><code>25cc</code></td>
<td><code>1</code></td>
<td><code>0.5</code></td>
<td><code>7762MiB</code></td>
<td><code>3881MiB</code></td>
</tr>

<tr>
<td><code>50cc</code></td>
<td><code>1</code></td>
<td><code>1</code></td>
<td><code>15525MiB</code></td>
<td><code>7762MiB</code></td>
</tr>

<tr>
<td><code>100cc</code></td>
<td><code>1</code></td>
<td><code>2</code></td>
<td><code>31050MiB</code></td>
<td><code>15525MiB</code></td>
</tr>

<tr>
<td><code>200cc</code></td>
<td><code>1</code></td>
<td><code>4</code></td>
<td><code>62100MiB</code></td>
<td><code>31050MiB</code></td>
</tr>

<tr>
<td><code>300cc</code></td>
<td><code>1</code></td>
<td><code>6</code></td>
<td><code>93150MiB</code></td>
<td><code>46575MiB</code></td>
</tr>

<tr>
<td><code>400cc</code></td>
<td><code>1</code></td>
<td><code>8</code></td>
<td><code>124201MiB</code></td>
<td><code>62100MiB</code></td>
</tr>

<tr>
<td><code>600cc</code></td>
<td><code>1</code></td>
<td><code>12</code></td>
<td><code>186301MiB</code></td>
<td><code>93150MiB</code></td>
</tr>

<tr>
<td><code>800cc</code></td>
<td><code>1</code></td>
<td><code>16</code></td>
<td><code>248402MiB</code></td>
<td><code>124201MiB</code></td>
</tr>

<tr>
<td><code>1200cc</code></td>
<td><code>1</code></td>
<td><code>24</code></td>
<td><code>372603MiB</code></td>
<td><code>186301MiB</code></td>
</tr>

<tr>
<td><code>1600cc</code></td>
<td><code>1</code></td>
<td><code>31</code></td>
<td><code>481280MiB</code></td>
<td><code>240640MiB</code></td>
</tr>

<tr>
<td><code>3200cc</code></td>
<td><code>1</code></td>
<td><code>62</code></td>
<td><code>962560MiB</code></td>
<td><code>481280MiB</code></td>
</tr>

<tr>
<td><code>6400cc</code></td>
<td><code>2</code></td>
<td><code>62</code></td>
<td><code>962560MiB</code></td>
<td><code>481280MiB</code></td>
</tr>

</tbody>
</table>

## Custom Cluster Sizes

When installing the Materialize Helm chart, you can override the [default
cluster sizes and resource allocations](#default-cluster-sizes). These
cluster sizes are used for both internal clusters, such as the `system_cluster`,
as well as user clusters.

> **Tip:** In general, you should not have to override the defaults. At minimum, we
> recommend that you keep the 25-200cc cluster sizes.

```yaml
operator:
  clusters:
    sizes:
      <size>:
        workers: <int>
        scale: 1                  # Generally, should be set to 1.
        cpu_exclusive: <bool>
        cpu_limit: <float>         # e.g., 6
        cpu_request: <float>       # e.g., 4 (optional, defaults to cpu_limit, may not be higher than cpu_limit)
        credits_per_hour: "0.0"    # N/A for self-managed.
        disk_limit: <string>       # e.g., "93150MiB"
        memory_limit: <string>     # e.g., "46575MiB"
        swap_enabled: <bool>       # optional, defaults to the cluster-level swap_enabled
        selectors: <map>           # k8s label selectors
        # ex: kubernetes.io/arch: amd64
```

| Field | Type | Description | Recommendation |
| --- | --- | --- | --- |
| <strong>workers</strong> | int | The number of timely workers in your cluster replica. | Use 1 worker per CPU core, with a minimum of 1 worker. |
| <strong>scale</strong> | int | The number of pods (i.e., processes) to use in a cluster replica; used to scale out replicas horizontally. Each pod will be provisioned using the settings defined in the size definition. | Generally, this should be set to 1. This should only be greater than 1 when a replica needs to take on limits that are greater than the maximum limits permitted on a single node. |
| <strong>cpu_exclusive</strong> | bool | The flag that determines if the workers should attempt to pin to a particular CPU core. | <p><a name="cpu_exclusive"></a></p> <p>Set to true <strong>if and only if</strong> the <a href="#cpu_limit" ><code>cpu_limit</code></a> is a whole number and the CPU management policy in the k8s cluster is set to static.</p>  |
| <strong>cpu_limit</strong> | float | <a name="cpu_limit"></a> The Kubernetes CPU limit for a replica pod, in cores. | <p>Prefer whole number values to enable CPU affinity. Kubernetes only allows CPU Affinity for pods taking a whole number of cores.</p> <p>If the value is not a whole number, set <a href="#cpu_exclusive" ><code>cpu_exclusive</code></a> to false.</p>  |
| <strong>cpu_request</strong> | float | <a name="cpu_request"></a> The Kubernetes CPU request for a replica pod, in cores. If not set, defaults to the value of <code>cpu_limit</code>. | In most cases, you do not need to set this. It is useful when you want to allow CPU bursting by setting a request lower than the limit. |
| <strong>memory_limit</strong> | string | The Kubernetes memory limit for a replica pod (e.g., <code>&quot;46575MiB&quot;</code>). | <dl> <dt>For most workloads, use an approximate <strong>1:8</strong> CPU-to-memory ratio (1 core</dt> <dd>8 GiB). This can vary depending on your workload characteristics.</dd> </dl>  |
| <strong>disk_limit</strong> | string | The size of the persistent volume to provision for a replica pod (e.g., <code>&quot;93150MiB&quot;</code>). | When spill-to-disk is enabled, use a <strong>1:2</strong> memory-to-disk ratio. Materialize spills data to disk when memory is insufficient, which can impact performance. When <code>swap_enabled</code> is true, this field is automatically set to <code>&quot;0&quot;</code> by the Helm chart. |
| <strong>credits_per_hour</strong> | string | This is a cloud attribute that should be set to &ldquo;0.00&rdquo; in self-managed. | Set to &ldquo;0.00&rdquo; for self-managed deployments. |
| <strong>swap_enabled</strong> | bool | Enables swap as the spill-to-disk mechanism for this size. When enabled, the replica uses swap instead of a provisioned persistent volume for spilling data. This also causes <code>disk_limit</code> to be set to <code>&quot;0&quot;</code>. | This defaults to the global <code>swap_enabled</code> value if not specified per size. Swap generally performs better than spill-to-disk via persistent volumes. |
| <strong>selectors</strong> | map | A map of Kubernetes label selector keys to values used to schedule pods for this cluster size on specific nodes. | It is generally not required to set this. |

> **Note:** If you have modified the default cluster size configurations, you can query the
> [`mz_cluster_replica_sizes`](/sql/system-catalog/mz_catalog/#mz_cluster_replica_sizes)
> system catalog table for the specific resource allocations.


<!-- mz-docs page: self-managed-deployments/appendix/upgrade-to-swap -->

# Prepare for swap and upgrade to v26.0
Upgrade procedure for v26.0.
> **Disambiguation:** This page outlines the general steps for upgrading from v25.2 to v26.0. See also [Upgrade Overview](/self-managed-deployments/upgrading/). 

<p>Starting in v26.0.0, Self-Managed Materialize enables swap by default. Swap
allows for infrequently accessed data to be moved from memory to disk. Enabling
swap reduces the memory required to operate Materialize and improves cost
efficiency.</p>
<p>To facilitate upgrades, Self-Managed Materialize added new labels to the node
selectors for <code>clusterd</code> pods. To upgrade, you must prepare your nodes with the
new labels. This guide provides general instructions for preparing for swap and
upgrading to v26.0.0 if you are <red><strong>not</strong></red> using the
Materialize-provided Terraforms.</p>
<h2 id="upgrade-to-v260-without-materialize-provided-terraforms">Upgrade to v26.0 without Materialize-provided Terraforms</h2>
> **Tip:** <p>Whe upgrading:</p>
> <ul>
> <li>
> <p><strong>Always</strong> check the <a href="/self-managed-deployments/upgrading/version-notes/" >version-specific upgrade
> notes</a>.</p>
> </li>
> <li>
> <p><strong>Always</strong> upgrade the operator <strong>first</strong> and ensure version compatibility
> between the operator and the Materialize instance you are upgrading to.</p>
> </li>
> <li>
> <p><strong>Always</strong> upgrade your Materialize instances <strong>after</strong> upgrading the operator
> to ensure compatibility.</p>
> </li>
> </ul>
> See also [General notes for upgrades](/self-managed-deployments/upgrading/)

<ol>
<li>
<p>Label existing scratchfs/lgalloc node groups.</p>
<p>If using lgalloc on scratchfs volumes, add the additional
<code>&quot;materialize.cloud/scratch-fs&quot;: &quot;true&quot;</code> label to your existing node groups
and nodes running Materialize workloads.</p>
<p>Adding this label to the node group (or nodepool) configuration will apply the label to newly spawned nodes, but depending on your cloud provider may not apply the label to existing nodes.</p>
<p>If not automatically applied, you may need to use <code>kubectl label</code> to apply the change to existing nodes.</p>
</li>
<li>
<p>Modify existing scratchfs/lgalloc disk setup daemonset selector labels</p>
<p>If using our <a href="https://github.com/MaterializeInc/ephemeral-storage-setup-image/" >ephemeral-storage-setup image</a> as a daemonset to configure scratchfs LVM volumes for lgalloc, you must add the additional <code>&quot;materialize.cloud/scratch-fs&quot;: &quot;true&quot;</code> label to multiple places:</p>
<ul>
<li><code>spec.selector.matchLabels</code></li>
<li><code>spec.template.metadata.labels</code></li>
<li>(if using <code>nodeAffinity</code>) <code>spec.template.spec.affinity.nodeAffinity.requiredDuringSchedulingIgnoredDuringExecution.nodeSelectorTerms</code></li>
<li>(if using <code>nodeSelector</code>) <code>spec.template.spec.nodeSelector</code></li>
</ul>
<p>You <strong>must</strong> use at least one of <code>nodeAffinity</code> or <code>nodeSelector</code>.</p>
<p>It is recommended to rename this daemonset to make it clear that it is only for the legacy scratchfs/lgalloc nodes (for example, change the name <code>disk-setup</code> to <code>disk-setup-scratchfs</code>).</p>
</li>
<li>
<p>Create a new node group for swap</p>
<ol>
<li>
<p>Create a new node group (or ec2nodeclass and nodepool if using Karpenter in AWS) using an instance type with local NVMe disks. If in GCP, the disks must be in <code>raw</code> mode.</p>
</li>
<li>
<p>Label the node group with <code>&quot;materialize.cloud/swap&quot;: &quot;true&quot;</code>.</p>
</li>
<li>
<p>If using AWS Bottlerocket AMIs (highly recommended if running in AWS), set the following in the userdata to configure the disks for swap, and enable swap in the kubelet:</p>
<div class="highlight"><pre tabindex="0" class="chroma"><code class="language-toml" data-lang="toml"><span class="line"><span class="cl"><span class="p">[</span><span class="nx">settings</span><span class="p">.</span><span class="nx">oci-defaults</span><span class="p">.</span><span class="nx">resource-limits</span><span class="p">.</span><span class="nx">max-open-files</span><span class="p">]</span>
</span></span><span class="line"><span class="cl"><span class="nx">soft-limit</span> <span class="p">=</span> <span class="mi">1048576</span>
</span></span><span class="line"><span class="cl"><span class="nx">hard-limit</span> <span class="p">=</span> <span class="mi">1048576</span>
</span></span><span class="line"><span class="cl">
</span></span><span class="line"><span class="cl"><span class="p">[</span><span class="nx">settings</span><span class="p">.</span><span class="nx">bootstrap-containers</span><span class="p">.</span><span class="nx">diskstrap</span><span class="p">]</span>
</span></span><span class="line"><span class="cl"><span class="nx">source</span> <span class="p">=</span> <span class="s2">&#34;docker.io/materialize/ephemeral-storage-setup-image:v0.4.0&#34;</span>
</span></span><span class="line"><span class="cl"><span class="nx">mode</span> <span class="p">=</span> <span class="s2">&#34;once&#34;</span>
</span></span><span class="line"><span class="cl"><span class="nx">essential</span> <span class="p">=</span> <span class="s2">&#34;true&#34;</span>
</span></span><span class="line"><span class="cl"><span class="c"># [&#34;swap&#34;, &#34;--cloud-provider&#34;, &#34;aws&#34;, &#34;--bottlerocket-enable-swap&#34;]</span>
</span></span><span class="line"><span class="cl"><span class="nx">user-data</span> <span class="p">=</span> <span class="s2">&#34;WyJzd2FwIiwgIi0tY2xvdWQtcHJvdmlkZXIiLCAiYXdzIiwgIi0tYm90dGxlcm9ja2V0LWVuYWJsZS1zd2FwIl0=&#34;</span>
</span></span><span class="line"><span class="cl">
</span></span><span class="line"><span class="cl"><span class="p">[</span><span class="nx">kernel</span><span class="p">.</span><span class="nx">sysctl</span><span class="p">]</span>
</span></span><span class="line"><span class="cl"><span class="s2">&#34;vm.swappiness&#34;</span> <span class="p">=</span> <span class="s2">&#34;100&#34;</span>
</span></span><span class="line"><span class="cl"><span class="s2">&#34;vm.min_free_kbytes&#34;</span> <span class="p">=</span> <span class="s2">&#34;1048576&#34;</span>
</span></span><span class="line"><span class="cl"><span class="s2">&#34;vm.watermark_scale_factor&#34;</span> <span class="p">=</span> <span class="s2">&#34;100&#34;</span>
</span></span></code></pre></div></li>
<li>
<p>If not using AWS or not using Bottlerocket AMIs, and your node group supports it (Azure does not as of 2025-11-05), add a startup taint. This taint will be removed after the disk is configured for swap.</p>
<div class="highlight"><pre tabindex="0" class="chroma"><code class="language-yaml" data-lang="yaml"><span class="line"><span class="cl"><span class="nt">taints</span><span class="p">:</span><span class="w">
</span></span></span><span class="line"><span class="cl"><span class="w">  </span>- <span class="nt">key</span><span class="p">:</span><span class="w"> </span><span class="l">startup-taint.cluster-autoscaler.kubernetes.io/disk-unconfigured</span><span class="w">
</span></span></span><span class="line"><span class="cl"><span class="w">    </span><span class="nt">value</span><span class="p">:</span><span class="w"> </span><span class="s2">&#34;true&#34;</span><span class="w">
</span></span></span><span class="line"><span class="cl"><span class="w">    </span><span class="nt">effect</span><span class="p">:</span><span class="w"> </span><span class="l">NoSchedule</span><span class="w">
</span></span></span></code></pre></div></li>
</ol>
</li>
<li>
<p>Create a new disk-setup-swap daemonset</p>
<p>If using Bottlerocket AMIs in AWS, you may skip this step, as you should have configured swap using userdata previously.</p>
<p>Create a new daemonset using our <a href="https://github.com/MaterializeInc/ephemeral-storage-setup-image/" >ephemeral-storage-setup image</a> to configure the disks for swap and to enable swap in the kubelet.</p>
<p>The arguments to the init container in this daemonset need to be configured for swap. See the examples in the linked git repository for more details.</p>
<p>This daemonset should run only on the new swap nodes, so we need to ensure it has the <code>&quot;materialize.cloud/swap&quot;: &quot;true&quot;</code> label in several places:</p>
<ul>
<li><code>spec.selector.matchLabels</code></li>
<li><code>spec.template.metadata.labels</code></li>
<li>(if using <code>nodeAffinity</code>) <code>spec.template.spec.affinity.nodeAffinity.requiredDuringSchedulingIgnoredDuringExecution.nodeSelectorTerms</code></li>
<li>(if using <code>nodeSelector</code>) <code>spec.template.spec.nodeSelector</code></li>
</ul>
<p>You <strong>must</strong> use at least one of <code>nodeAffinity</code> or <code>nodeSelector</code>.</p>
<p>It is recommended to name this daemonset to clearly indicate that it is for configuring swap (ie: <code>disk-setup-swap</code>), as opposed to other disk configurations.</p>
</li>
<li>
<p>(Optional) Configure environmentd to also use swap</p>
<p>Swap is enabled by default for clusterd, but not for environmentd. If you&rsquo;d like to enable swap for environmentd, add <code>&quot;materialize.cloud/swap&quot;: &quot;true&quot;</code> to the <code>environmentd.node_selector</code> helm value.</p>
</li>
<li>
<p>Upgrade the Materialize operator helm chart to v26</p>
<p>The cluster size definitions for existing Materialize instances will not be changed at this point, but any newly created Materialize instances, or upgraded Materialize instances will pick up the new sizes.</p>
<p>Do not create any new Materialize instances at versions less than v26, or perform any rollouts to existing Materialize instances to versions less than v26.</p>
</li>
<li>
<p>Upgrade existing Materialize instances to v26</p>
<p>The new v26 pods should go to the new swap nodes.</p>
<p>You can verify that swap is enabled and working by <code>exec</code>ing into a clusterd pod and running <code>cat /sys/fs/cgroup/memory.swap.max</code>. If you get a number greater than 0, swap is enabled and the pod is allowed to use it.</p>
</li>
<li>
<p>(Optional) Delete old scratchfs/lgalloc node groups and disk-setup-scratchfs daemonset</p>
<p>If you no longer have anything running on the old scratchfs/lgalloc nodes, you may delete their node group and the disk-setup-scratchfs daemonset.</p>
</li>
</ol>
<h2 id="how-to-disable-swap">How to disable swap</h2>
<p>If you wish to opt out of swap and retain the old behavior, you may set <code>operator.clusters.swap_enabled: false</code> in your Helm values.</p>


<!-- mz-docs page: self-managed-deployments/configuration-system-parameters -->

# Configuring System Parameters
How to configure system parameters for Materialize using a Kubernetes ConfigMap
This guide explains how to configure system parameters for your Materialize
deployment using a Kubernetes ConfigMap.

## Overview

System parameters allow you to customize the behavior of your Materialize
instance at runtime. These parameters can control various aspects such as
connection limits, cluster replica sizes, and other operational settings.

There are two ways to configure system parameters:

- **Using SQL**: Connect to your Materialize instance and use the [`ALTER SYSTEM
  SET`](/sql/alter-system-set/) command to modify parameters dynamically. This
  is useful for one-off changes or testing.

- **Using a ConfigMap**: Create a Kubernetes ConfigMap containing the parameters
  in JSON format and reference it in your Materialize custom resource. This is
  the recommended approach for persistent configuration that survives restarts
  and upgrades.

This guide focuses on the ConfigMap approach for self-managed deployments.

For balancerd settings, such as its connection limit, see
[Configure balancerd dynamic configuration](#configure-balancerd-dynamic-configuration).

> **Public Preview:** This feature is in public preview.

## Configure System Parameters via ConfigMap

### Step 1: Create a System Parameters ConfigMap

In the same namespace as your Materialize environment, create a
ConfigMap that includes a key named `system-params.json`. Set
`system-params.json` to a valid JSON object containing your desired system
parameters.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: mz-system-params
  namespace: materialize-environment
data:
  system-params.json: |
    {
      "max_connections": 1000,
      "allowed_cluster_replica_sizes": "'25cc', '50cc', '100cc'"
    }
```

Apply the ConfigMap to your cluster:

```shell
kubectl apply -f system-params-configmap.yaml
```

### Step 2: Configure the Materialize Custom Resource

Reference the ConfigMap in your Materialize custom resource by setting the
`systemParameterConfigmapName` field to the name of your ConfigMap:

**v1alpha1:**

<p><code>v1alpha1</code> is the default CRD version for the Materialize Helm
chart. The Terraform modules default to <code>v1</code> starting in v4.0.0.
With <code>v1alpha1</code>, instance rollouts require manually rotating a
UUID.</p>

```yaml {hl_lines="9-10"}
apiVersion: materialize.cloud/v1alpha1
kind: Materialize
metadata:
  name: 12345678-1234-1234-1234-123456789012
  namespace: materialize-environment
spec:
  environmentdImageRef: materialize/environmentd:v26.43.0
  backendSecretName: materialize-backend
  systemParameterConfigmapName: mz-system-params
  requestRollout: 00000000-0000-0000-0000-000000000003 # Changing the CR requires a rollout
```

**v1:**

<p>The <code>v1</code> CRD is available starting in v26.30. It is opt-in for the Helm chart and the default for the Terraform modules starting in v4.0.0. See <a href="/self-managed-deployments/upgrading/adopting-the-v1-crd/">Adopting the v1 CRD</a> to enable it.</p>

```yaml {hl_lines="9"}
apiVersion: materialize.cloud/v1
kind: Materialize
metadata:
  name: 12345678-1234-1234-1234-123456789012
  namespace: materialize-environment
spec:
  environmentdImageRef: materialize/environmentd:v26.43.0
  backendSecretName: materialize-backend
  systemParameterConfigmapName: mz-system-params
```

Apply the updated Materialize resource:

```shell
kubectl apply -f materialize.yaml
```

## Updating ConfigMap System Parameters

To update system parameters defined in your ConfigMap, you can either:

- Use `kubectl edit configmap` to edit the ConfigMap and apply the changes:

  ```shell
  kubectl edit configmap mz-system-params -n materialize-environment
  ```

- Or, edit the ConfigMap YAML file and reapply:

  ```shell
  kubectl apply -f system-params-configmap.yaml
  ```

Unlike changes to the Materialize custom resource, updating the parameters in
your ConfigMap does **not** require a rollout.

### ConfigMap sync behavior

Kubernetes periodically refreshes mounted ConfigMaps. The delay depends on
the kubelet sync period and its ConfigMap cache. With a one-minute sync period
and a one-minute cache lifetime, propagation can take up to two minutes.
See [Kubernetes ConfigMap update behavior](https://kubernetes.io/docs/tasks/configure-pod-container/configure-pod-configmap/#mounted-configmaps-are-updated-automatically).

Once the ConfigMap is synced to the volume, Materialize checks for configuration
changes every second and applies them automatically.

To request an earlier refresh, update an annotation on each affected pod,
replacing `<pod-name>` with the pod's name:

```shell
kubectl annotate pod <pod-name> \
  -n materialize-environment \
  configmap-reload-trigger="$(date +%s)" \
  --overwrite
```

> **Note:** Even after the ConfigMap is synced, some system parameters may require a restart to
> take effect.

## Available System Parameters

The system parameters that can be configured via the ConfigMap are the same
parameters that can be modified using the [`ALTER SYSTEM SET`](/sql/alter-system-set/)
SQL command.

The following are some commonly configured system parameters:

| Parameter | Description |
|-----------|-------------|
| `max_connections` | Maximum number of concurrent connections allowed |
| `allowed_cluster_replica_sizes` | List of allowed cluster replica sizes |
| `max_clusters` | Maximum number of clusters in the region |
| `max_sources` | Maximum number of sources in the region |
| `max_sinks` | Maximum number of sinks in the region |
| `statement_logging_max_sample_rate` | Cap on the fraction of statements recorded in [query history](/self-managed-deployments/query-history/). Setting it here overrides the Helm chart value. |
| `statement_logging_target_data_rate` | Sustained bytes per second that statement logging may write. Bounds query history growth on busy instances. |

For a complete list of available system parameters and their descriptions, see
the [configuration parameters](/sql/alter-system-set/#key-configuration-parameters)
documentation, or run the following SQL command in your Materialize instance:

```sql
SHOW ALL;
```

### Sample ConfigMap: Setting Connection Limits

The following sample ConfigMap YAML sets the `max_connections` parameter:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: mz-system-params
  namespace: materialize-environment
data:
  system-params.json: |
    {
      "max_connections": 500
    }
```

### Sample ConfigMap: Configuring Allowed Cluster Sizes

The following sample ConfigMap YAML sets the `allowed_cluster_replica_sizes` parameter:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: mz-system-params
  namespace: materialize-environment
data:
  system-params.json: |
    {
      "allowed_cluster_replica_sizes": "'25cc', '50cc', '100cc', '200cc'"
    }
```

### Sample ConfigMap: Configuring Connection Limits and Allowed Cluster Sizes

The following sample ConfigMap YAML sets both the `max_connections` parameter
and the `allowed_cluster_replica_sizes` parameter:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: mz-system-params
  namespace: materialize-environment
data:
  system-params.json: |
    {
      "max_connections": 500,
      "allowed_cluster_replica_sizes": "'25cc', '50cc', '100cc', '200cc'"
    }
```

## Configure balancerd dynamic configuration

  <div class="warning">
    <strong class="gutter">Unreleased</strong>
    This feature will be released in
    <a href="/releases#release-notes"><strong>v26.44</strong></a>.
    It may not be available in your region yet.
    The release is scheduled to complete by <strong>September 30, 2026</strong>.
  </div>

To configure balancerd, use a separate ConfigMap referenced by
`spec.balancerdConfigmapName`. This example requires Materialize Operator and a
Materialize instance running v26.44 or later, with balancerd enabled. The field is
supported in both the `v1` and `v1alpha1` Materialize custom resources.

Balancerd configuration is separate from environmentd system parameters.
For example, `balancerd_max_connections` limits connections per balancerd process,
while `max_connections` controls connections in environmentd. Do not put
`balancerd_*` settings in `system-params.json` or set them with `ALTER SYSTEM SET`.

### Create the balancerd ConfigMap

Save the following as `balancerd-configmap.yaml`, using the same namespace as your
Materialize instance:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: mz-balancerd-config
  namespace: materialize-environment
data:
  config.json: |
    {
      "balancerd_max_connections": 10000
    }
```

The `config.json` key must contain a valid JSON object. Use `{}` if you do not
need any overrides yet. Apply the ConfigMap before referencing it:

```shell
kubectl apply -f balancerd-configmap.yaml
```

You manage this ConfigMap, either directly or through your deployment tooling.
The operator mounts it without creating, overwriting, or deleting it.

### Reference the ConfigMap

Set `spec.balancerdConfigmapName` in your Materialize manifest and apply it.
For an existing instance, you can also patch the resource. Replace
`<instance-name>` with the name of your Materialize resource:

```shell
kubectl patch materialize <instance-name> -n materialize-environment \
  --type merge \
  -p '{"spec":{"balancerdConfigmapName":"mz-balancerd-config"}}'
```

Adding, changing, or removing this reference rolls the balancerd pods but does
not require an environmentd rollout or a change to `requestRollout`. If the
ConfigMap or its `config.json` key is missing, the new pods cannot start.

For a standalone `Balancer` custom resource, set `spec.configmapName` instead.

### Verify the configured connection limit

Find the balancerd pods for your instance, replacing `<instance-name>` with your
Materialize resource's name:

```shell
kubectl get pods -n materialize-environment \
  -l 'app=balancerd,materialize.cloud/organization-name=<instance-name>'
```

Forward a pod's internal HTTP port. Replace `<balancerd-pod-name>` with one of
those pod names. The default internal HTTP port is `8080`:

```shell
kubectl port-forward -n materialize-environment pod/<balancerd-pod-name> 8080:8080
```

In another terminal, check the configured limit:

```shell
curl -s http://localhost:8080/metrics | grep '^mz_balancer_connection_limit '
```

For this example, the result is:

```nofmt
mz_balancer_connection_limit 10000
```

Repeat for each balancerd pod. This metric reports the configured limit, not the
number of active connections.

### Update balancerd configuration

Edit `config.json` in `balancerd-configmap.yaml` and reapply the file:

```shell
kubectl apply -f balancerd-configmap.yaml
```

Changing the ConfigMap contents does not restart balancerd. After Kubernetes
projects the update into the pod, balancerd reads it on its next one-second sync
tick. Allow for the additional [ConfigMap propagation delay](#configmap-sync-behavior)
before verifying the updated metric.

Keep these behaviors in mind:

- Removing a setting from the JSON object does not reset its running value. To
  reset a setting at runtime, explicitly set its default value.
- Invalid JSON at startup prevents the file sync loop from starting. Correct the
  ConfigMap and restart the affected balancerd pods. Invalid JSON introduced
  after a successful startup leaves the previous values in use, and syncing
  resumes after the JSON is corrected.
- `balancerd_max_connections` defaults to `5000` per process and covers pgwire
  and HTTPS connections together. Setting it to `0` disables this limit. The
  separate environmentd `max_connections` limit still applies.

## Troubleshooting

### ConfigMap not being applied

If your system parameters are not being applied, check the following:

1. **Verify the ConfigMap exists** in the correct namespace:
   ```shell
   kubectl get configmap mz-system-params -n materialize-environment
   ```

2. **Check the ConfigMap content** is valid JSON:
   ```shell
   kubectl get configmap mz-system-params -n materialize-environment -o jsonpath='{.data.system-params\.json}'
   ```

3. **Verify the Materialize resource** references the correct ConfigMap name:
   ```shell
   kubectl get materialize -n materialize-environment -o yaml | grep systemParameterConfigmapName
   ```

4. **Check environmentd logs** for any errors related to configuration loading:
   ```shell
   kubectl logs -l app=environmentd -n materialize-environment
   ```

### Invalid parameter values

If a system parameter value is invalid, Materialize will log an error but
continue running with the previous valid configuration. Check the environmentd
logs for error messages:

```shell
kubectl logs -l app=environmentd -n materialize-environment | grep -i "system.*param"
```

## See also

- [Query History](/self-managed-deployments/query-history/)
- [Materialize Operator Configuration](/installation/configuration/)
- [Materialize CRD Field Descriptions](/installation/appendix-materialize-crd-field-descriptions/)
- [Troubleshooting](/installation/troubleshooting/)

<!-- mz-docs page: self-managed-deployments/deployment-guidelines -->

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

<!-- mz-docs page: self-managed-deployments/deployment-guidelines/aws-deployment-guidelines -->

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

<!-- mz-docs page: self-managed-deployments/deployment-guidelines/azure-deployment-guidelines -->

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

<!-- mz-docs page: self-managed-deployments/deployment-guidelines/gcp-deployment-guidelines -->

# GCP deployment guidelines
General guidelines when deploying Self-Managed Materialize on GCP.
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

<!-- mz-docs page: self-managed-deployments/deployment-guidelines/gke-node-pool-upgrades -->

# GKE node pool upgrades
Configure graceful Materialize rollouts when GKE upgrades the node pools underneath it.
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

<!-- mz-docs page: self-managed-deployments/deployment-guidelines/resize-node-pools -->

# Resize node pools
Safely change the VM type of a node pool in a Self-Managed Materialize deployment.
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

<!-- mz-docs page: self-managed-deployments/faq -->

# FAQ
Frequently asked questions about self-managed deployments.
## How long do license keys last?

Community edition license keys are valid for one year. Enterprise license
keys will vary based on the terms of your contract.

## How do I get a license key?

| License key type | Deployment type | Action |
| --- | --- | --- |
| Community | New deployments | <p>To get a license key:</p> <ul> <li>If you have a Cloud account, visit the <a href="https://console.materialize.com/license/" ><strong>License</strong> page in the Materialize Console</a>.</li> <li>If you do not have a Cloud account, visit <a href="https://materialize.com/self-managed/community-license/" >https://materialize.com/self-managed/community-license/</a>.</li> </ul> |
| Community | Existing deployments | Contact <a href="https://materialize.com/docs/support/" >Materialize support</a>. |
| Enterprise | New deployments | Visit <a href="https://materialize.com/self-managed/enterprise-license/" >https://materialize.com/self-managed/enterprise-license/</a> to purchase an Enterprise license. |
| Enterprise | Existing deployments | Contact <a href="https://materialize.com/docs/support/" >Materialize support</a>. |

## How do I add a license key to an existing installation?

The license key should be configured in the Kubernetes Secret resource
created during the installation process. To configure a license key in an
existing installation, run:

```bash
kubectl -n materialize-environment patch secret materialize-backend -p '{"stringData":{"license_key":"<your license key goes here>"}}' --type=merge
```

## How can I downgrade Self-Managed Materialize?

Downgrading is not supported.


<!-- mz-docs page: self-managed-deployments/installation -->

# Installation

Installation guides for Self-Managed Materialize.

<p>You can install Self-Managed Materialize on a Kubernetes cluster running
locally or on a cloud provider. Self-Managed Materialize requires:</p>
<ul>
<li>A Kubernetes (v1.31+) cluster.</li>
<li>PostgreSQL as a metadata database.</li>
<li>Blob storage.</li>
<li>A license key.</li>
</ul>
<h2 id="license-key">License key</h2>
<p>Starting in v26.0, Materialize requires a license key.</p>

| License key type | Deployment type | Action |
| --- | --- | --- |
| Community | New deployments | <p>To get a license key:</p> <ul> <li>If you have a Cloud account, visit the <a href="https://console.materialize.com/license/" ><strong>License</strong> page in the Materialize Console</a>.</li> <li>If you do not have a Cloud account, visit <a href="https://materialize.com/self-managed/community-license/" >https://materialize.com/self-managed/community-license/</a>.</li> </ul> |
| Community | Existing deployments | Contact <a href="https://materialize.com/docs/support/" >Materialize support</a>. |
| Enterprise | New deployments | Visit <a href="https://materialize.com/self-managed/enterprise-license/" >https://materialize.com/self-managed/enterprise-license/</a> to purchase an Enterprise license. |
| Enterprise | Existing deployments | Contact <a href="https://materialize.com/docs/support/" >Materialize support</a>. |

<h2 id="installation-guides">Installation guides</h2>
<p>The following installation guides are available to help you get started:</p>

### Install using Helm Commands

|  Guide         | Description  |
| ------------- | -------|
| [Install locally on Kind](/self-managed-deployments/installation/install-on-local-kind/) | Uses standard Helm commands to deploy Materialize to a Kind cluster in Docker.

<h3 id="install-using-terraform-modules">Install using Terraform Modules</h3>
> **Note:** We recommend pinning your module sources to specific tags to avoid unexpected breaking
> changes in future versions.
> We recommend updating your module source tags when updating Materialize versions,
> taking care to follow any instructions in the release notes.

<table>
  <thead>
      <tr>
          <th>Guide</th>
          <th>Description</th>
      </tr>
  </thead>
  <tbody>
      <tr>
          <td><a href="/self-managed-deployments/installation/install-on-aws/" >Install on AWS</a></td>
          <td>Uses Terraform module to deploy Materialize to AWS Elastic Kubernetes Service (EKS).</td>
      </tr>
      <tr>
          <td><a href="/self-managed-deployments/installation/install-on-azure/" >Install on Azure</a></td>
          <td>Uses Terraform module to deploy Materialize to Azure Kubernetes Service (AKS).</td>
      </tr>
      <tr>
          <td><a href="/self-managed-deployments/installation/install-on-gcp/" >Install on GCP</a></td>
          <td>Uses Terraform module to deploy Materialize to Google Kubernetes Engine (GKE).</td>
      </tr>
  </tbody>
</table>

<!-- mz-docs page: self-managed-deployments/installation/install -->

# Install Self-Managed Materialize
Install Self-Managed Materialize.
<p>You can install Self-Managed Materialize on a Kubernetes cluster running
locally or on a cloud provider. Self-Managed Materialize requires:</p>
<ul>
<li>A Kubernetes (v1.31+) cluster.</li>
<li>PostgreSQL as a metadata database.</li>
<li>Blob storage.</li>
<li>A license key.</li>
</ul>
<h2 id="license-key">License key</h2>
<p>Starting in v26.0, Materialize requires a license key.</p>

| License key type | Deployment type | Action |
| --- | --- | --- |
| Community | New deployments | <p>To get a license key:</p> <ul> <li>If you have a Cloud account, visit the <a href="https://console.materialize.com/license/" ><strong>License</strong> page in the Materialize Console</a>.</li> <li>If you do not have a Cloud account, visit <a href="https://materialize.com/self-managed/community-license/" >https://materialize.com/self-managed/community-license/</a>.</li> </ul> |
| Community | Existing deployments | Contact <a href="https://materialize.com/docs/support/" >Materialize support</a>. |
| Enterprise | New deployments | Visit <a href="https://materialize.com/self-managed/enterprise-license/" >https://materialize.com/self-managed/enterprise-license/</a> to purchase an Enterprise license. |
| Enterprise | Existing deployments | Contact <a href="https://materialize.com/docs/support/" >Materialize support</a>. |

<h2 id="installation-guides">Installation guides</h2>
<p>The following installation guides are available to help you get started:</p>

### Install using Helm Commands

|  Guide         | Description  |
| ------------- | -------|
| [Install locally on Kind](/self-managed-deployments/installation/install-on-local-kind/) | Uses standard Helm commands to deploy Materialize to a Kind cluster in Docker.

<h3 id="install-using-terraform-modules">Install using Terraform Modules</h3>
> **Note:** We recommend pinning your module sources to specific tags to avoid unexpected breaking
> changes in future versions.
> We recommend updating your module source tags when updating Materialize versions,
> taking care to follow any instructions in the release notes.

<table>
  <thead>
      <tr>
          <th>Guide</th>
          <th>Description</th>
      </tr>
  </thead>
  <tbody>
      <tr>
          <td><a href="/self-managed-deployments/installation/install-on-aws/" >Install on AWS</a></td>
          <td>Uses Terraform module to deploy Materialize to AWS Elastic Kubernetes Service (EKS).</td>
      </tr>
      <tr>
          <td><a href="/self-managed-deployments/installation/install-on-azure/" >Install on Azure</a></td>
          <td>Uses Terraform module to deploy Materialize to Azure Kubernetes Service (AKS).</td>
      </tr>
      <tr>
          <td><a href="/self-managed-deployments/installation/install-on-gcp/" >Install on GCP</a></td>
          <td>Uses Terraform module to deploy Materialize to Google Kubernetes Engine (GKE).</td>
      </tr>
  </tbody>
</table>


<!-- mz-docs page: self-managed-deployments/installation/install-on-aws -->

# Install on AWS
Install Materialize on AWS using the Terraform module.
Materialize provides a set of modular [Terraform
modules](https://github.com/MaterializeInc/materialize-terraform-self-managed/tree/main)
that can be used to deploy all services required for Materialize to run on AWS.
These modules serve as composable building blocks that you can integrate into
existing DevOps workflows, either as a full set or individually.

Self-managed Materialize requires: a Kubernetes (v1.31+) cluster; PostgreSQL as
a metadata database; blob storage; and a license key.
 The example on this page
deploys a complete Materialize environment on AWS using the modular Terraform
setup from this repository.

> **Note:** We recommend pinning your module sources to specific tags to avoid unexpected breaking
> changes in future versions.
> We recommend updating your module source tags when updating Materialize versions,
> taking care to follow any instructions in the release notes.

## What Gets Created

This example provisions the following infrastructure:

### Networking

| Resource | Description |
|----------|-------------|
| VPC | 10.0.0.0/16 with DNS hostnames and support enabled |
| Subnets | 3 private subnets (10.0.1.0/24, 10.0.2.0/24, 10.0.3.0/24) and 3 public subnets (10.0.101.0/24, 10.0.102.0/24, 10.0.103.0/24) across availability zones us-east-1a, us-east-1b, us-east-1c |
| NAT Gateway | Single NAT Gateway for all private subnets |
| Internet Gateway | For public subnet connectivity |

### Compute

| Resource | Description |
|----------|-------------|
| EKS Cluster | Version 1.34 with CloudWatch logging (API, audit) |
| Base Node Group | 2 nodes (t4g.medium) for Karpenter and CoreDNS |
| Karpenter | Auto-scaling controller with two node classes: Generic nodepool (t4g.xlarge instances for general workloads) and Materialize nodepool (r7gd.2xlarge instances with swap enabled and dedicated taints to run materialize instance workloads) |

### Database

| Resource | Description |
|----------|-------------|
| RDS PostgreSQL | Version 15, db.t3.large instance |
| Storage | 50GB allocated, autoscaling up to 100GB |
| Deployment | Single-AZ (non-production configuration) |
| Backups | 7-day retention |
| Security | Dedicated security group with access from EKS cluster and nodes |

### Storage

| Resource | Description |
|----------|-------------|
| S3 Bucket | Dedicated bucket for Materialize persistence |
| Encryption | Disabled (for testing; enable in production) |
| Versioning | Disabled (for testing; enable in production) |
| IAM Role | IRSA role for Kubernetes service account access |

### Kubernetes Add-ons

| Resource | Description |
|----------|-------------|
| AWS Load Balancer Controller | For managing Network Load Balancers |
| cert-manager | Certificate management controller for Kubernetes that automates TLS certificate provisioning and renewal |
| Self-signed ClusterIssuer | Provides self-signed TLS certificates for Materialize instance internal communication (balancerd, console). Used by the Materialize instance for secure inter-component communication. |

### Materialize

| Resource | Description |
|----------|-------------|
| Operator | Materialize Kubernetes operator in the `materialize` namespace |
| Instance | Single Materialize instance in the `materialize-environment` namespace |
| Network Load Balancer | Dedicated NLB for access to Materialize 
| Port | Description |
| --- | --- |
| 6875 | For SQL connections to the database |
| 6876 | For HTTP(S) connections to the database |
| 8080 | For HTTP(S) connections to Materialize Console |
 |

### Observability

On by default starting with v11.0.0 of the Materialize Terraform Modules.
Whenever `enable_observability` is `true`,
the following are created as well:

| Resource | Description |
|----------|-------------|
| Monitoring stack | Grafana, Thanos, Loki, Grafana Alloy, and Alertmanager in the `monitoring` namespace, with the Materialize dashboards pre-installed |
| S3 Buckets | Dedicated buckets for metrics and logs |
| Grafana RDS PostgreSQL | `db.t4g.micro` instance holding Grafana's own state (users, API tokens, annotations, dashboard versions) |
| Grafana Network Load Balancer | Internal NLB for reaching Grafana, allowlisted to `ingress_cidr_blocks` |

This stack requires v10.0.0 or later of the Materialize Terraform Modules,
which replaced an earlier Prometheus-and-Grafana pair. The Grafana database
and load balancer were added in v10.1.0, and are both billable. Starting with
v11.0.0, `enable_observability` defaults to `true`, so set it to `false` if you
do not want the stack. For what the stack stores and where else it can send
it, see [How logs and metrics are
stored](/observability/self-managed/storage/). For reaching Grafana, see
[Grafana](/observability/self-managed/grafana/).

## Prerequisites

### AWS Account Requirements

An active AWS account with appropriate permissions to create:
- EKS clusters
- RDS instances
- S3 buckets
- VPCs and networking resources
- IAM roles and policies

### Required Tools

- [Terraform](https://developer.hashicorp.com/terraform/install?product_intent=terraform)
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
- [kubectl](https://docs.aws.amazon.com/eks/latest/userguide/install-kubectl.html)
- [Helm 3.2.0+](https://helm.sh/docs/intro/install/)

### License Key

| License key type | Deployment type | Action |
| --- | --- | --- |
| Community | New deployments | <p>To get a license key:</p> <ul> <li>If you have a Cloud account, visit the <a href="https://console.materialize.com/license/" ><strong>License</strong> page in the Materialize Console</a>.</li> <li>If you do not have a Cloud account, visit <a href="https://materialize.com/self-managed/community-license/" >https://materialize.com/self-managed/community-license/</a>.</li> </ul> |
| Community | Existing deployments | Contact <a href="https://materialize.com/docs/support/" >Materialize support</a>. |
| Enterprise | New deployments | Visit <a href="https://materialize.com/self-managed/enterprise-license/" >https://materialize.com/self-managed/enterprise-license/</a> to purchase an Enterprise license. |
| Enterprise | Existing deployments | Contact <a href="https://materialize.com/docs/support/" >Materialize support</a>. |

## Getting started: Simple example

> **Note:** We recommend pinning your module sources to specific tags to avoid unexpected breaking
> changes in future versions.
> We recommend updating your module source tags when updating Materialize versions,
> taking care to follow any instructions in the release notes.

> **Tip:** * The `examples/simple` example, used in this tutorial, is provided for illustration and to help you get started. In practice, we recommend instantiating these modules within your own Terraform code rather than relying on the example configuration directly.
> * The simple example used in this tutorial enables [Password
> authentication](https://github.com/MaterializeInc/materialize-terraform-self-managed/blob/v10.1.0/aws/examples/simple/main.tf#L518)
> for the Materialize instance. To use a different authentication method, update
> [`authenticator_kind`](https://github.com/MaterializeInc/materialize-terraform-self-managed/blob/v10.1.0/kubernetes/modules/materialize-instance/README.md#input_authenticator_kind).
> See [Authentication](/security/self-managed/authentication/) for the supported
> authentication mechanisms.

### Step 1: Set Up the Environment

1. Open a terminal window.

1. Clone the Materialize Terraform repository and go to the
   `aws/examples/simple` directory.

   ```bash
   git clone https://github.com/MaterializeInc/materialize-terraform-self-managed.git
   cd materialize-terraform-self-managed/aws/examples/simple
   ```

1. Ensure your AWS CLI is configured with the appropriate profile, substitute
   `<your-aws-profile>` with the profile to use:

   ```bash
   # Set your AWS profile for the session
   export AWS_PROFILE=<your-aws-profile>
   ```

### Step 2: Configure Terraform Variables

1. Create a `terraform.tfvars` file with the following variables:

   | Variable      | Description                 |
   | -----------   | ----------------------------|
   | `name_prefix` | Prefix for all resource names (e.g., `simple-demo`). |
   | `aws_region`  | AWS region for deployment (e.g., `us-east-1`). |
   | `aws_profile` | AWS CLI profile to use. |
   | `license_key` | Materialize license key. |
   | `crd_version` | CRD API version to use for the Materialize instance: `v1` (default starting with Materialize Terraform Modules v4.0.0) or `v1alpha1`. |
   | `tags`        | Map of tags to apply to resources. |

   > **Tip:** Starting in Materialize Terraform module version v4.0.0, `crd_version`
   > defaults to [CRD API version
   > `v1`](/self-managed-deployments/upgrading/adopting-the-v1-crd/). `v1`
   > requires Materialize v26.30 or greater and is available starting in
   > Terraform module version v3.1.1. To use `v1alpha1` instead, set
   > `crd_version = "v1alpha1"`.

   ```hcl
   name_prefix = "simple-demo"
   aws_region  = "us-east-1"
   aws_profile = "your-aws-profile"
   license_key = "your-materialize-license-key"
   crd_version = "v1"   # Default starting with Materialize Terraform Modules v4.0.0. v1 requires Materialize v26.30+.
   tags = {
     environment = "demo"
   }
   # internal_load_balancer = false   # default = true (internal load balancer). You can set to false = public load balancer.
   # ingress_cidr_blocks = ["x.x.x.x/n", ...]
   # k8s_apiserver_authorized_networks  = ["x.x.x.x/n", ...]
   # enable_observability = false   # default = true (install the observability stack).
   # grafana_host = "grafana.example.com"   # Only used when enable_observability = true.
   ```

   > **Note:** With `enable_observability` on, the modules also create a `db.t4g.micro`
>    RDS instance for Grafana's own state and an internal NLB to reach Grafana
>    on. Both are billable. See
>    [Grafana](/observability/self-managed/grafana/).

   <p><strong>Additional variables</strong>:</p>
   <ul>
   <li><code>internal_load_balancer</code>: Flag that determines whether the load balancer
   is internal (default) or public.</li>
   <li><code>ingress_cidr_blocks</code>: List of CIDR blocks allowed to reach the load
   balancer if the load balancer is public (<code>internal_load_balancer: false</code>).
   If unset, defaults to <code>[&quot;0.0.0.0/0&quot;]</code> (i.e., <red><strong>all</strong></red> IPv4
   addresses on the internet). <strong>Only applied when the load balancer is public</strong>.</li>
   <li><code>k8s_apiserver_authorized_networks</code>: List of CIDR
   blocks allowed to access your cluster endpoint. If unset, defaults to
   <code>[&quot;0.0.0.0/0&quot;]</code> (<red><strong>all</strong></red> IPv4 addresses on the internet).</li>
   <li><code>enable_observability</code>: Flag that determines whether to deploy the
   monitoring stack (Grafana, metrics, and logs) alongside Materialize.
   Defaults to <code>false</code> in the <code>simple</code> example. See
   <a href="/observability/self-managed/grafana/" >Grafana</a>.</li>
   </ul>
   > **Note:** Refer to your organization's security practices to set these values accordingly.

### Step 3: Apply the Terraform

1. Initialize the Terraform directory to download the required providers
    and modules:

    ```bash
    terraform init
    ```

1. Apply the Terraform configuration to create the infrastructure.

   ```bash
   terraform apply
   ```

   If you are satisfied with the planned changes, type `yes` when prompted to
   proceed.

   > **Tip:** If you previously logged in to Amazon ECR Public, a cached auth token may cause 403 errors even when pulling public images. To remove the token, run:
>    ```bash
>    docker logout public.ecr.aws
>    ```
>    Then, re-apply the Terraform configuration.

1. From the output, you will need the following fields to connect using the
   Materialize Console and PostgreSQL-compatible clients/drivers:
   - `nlb_dns_name`
   - `external_login_password_mz_system`.

   ```bash
   terraform output -raw <field_name>
   ```

   > **Tip:** Your shell may show an ending marker (such as `%`) because the
>    output did not end with a newline. Do not include the marker when using the value.

1. Configure `kubectl` to connect to your cluster, replacing:

   - `<your-eks-cluster-name>` with the your cluster name; i.e., the
     `eks_cluster_name` in the Terraform output. For the
     sample example, your cluster name has the form `{prefix_name}-eks`; e.g.,
     `simple-demo-eks`.

   - `<your-region>` with the region of your cluster. Your region can be
     found in your `terraform.tfvars` file; e.g., `us-east-1`.

   ```bash
   # aws eks update-kubeconfig --name <your-eks-cluster-name> --region <your-region>
   aws eks update-kubeconfig --name $(terraform output -raw eks_cluster_name) --region <your-region>
   ```

### Step 4. Optional. Verify the deployment.

1. Check the status of your deployment:
   **Operator:**
   To check the status of the Materialize operator, which runs in the `materialize` namespace:
   ```bash
   kubectl -n materialize get all
   ```

   **Materialize instance:**
   To check the status of the Materialize instance, which runs in the `materialize-environment` namespace:
   ```bash
   kubectl -n materialize-environment get all
   ```

   <p>If you run into an error during deployment, refer to the
   <a href="/self-managed-deployments/troubleshooting/" >Troubleshooting</a>.</p>

1. Check the CRD version of the Materialize manifest.
   To check the CRD version of the Materialize manifest that was applied, run
   the following:

   ```sh
   terraform state show 'module.materialize_instance.kubectl_manifest.materialize_instance' \
     | grep -iE 'api_?version|kind'
   ```

### Step 5: Connect to Materialize

Using the `nlb_dns_name` and `external_login_password_mz_system` from the Terraform
output, you can connect to Materialize via the Materialize Console or
PostgreSQL-compatible tools/drivers using the following ports:

| Port | Description |
| --- | --- |
| 6875 | For SQL connections to the database |
| 6876 | For HTTP(S) connections to the database |
| 8080 | For HTTP(S) connections to Materialize Console |

#### Connect to the Materialize Console

> **Note:** - **If using a public NLB:** Both SQL and Console are available via the
> public NLB. You can connect directly using the NLB's DNS name from anywhere
> on the internet (subject to your `ingress_cidr_blocks` configuration).
> - **If using a private (internal) NLB:** You can connect from inside the same VPC or from networks that are privately connected to it. Alternatively, use Kubernetes port-forwarding for both SQL and Console.

1. To connect to the Materialize Console, open a browser to
    `https://<nlb_dns_name>:8080`, substituting your `<nlb_dns_name>`.

   From the terminal, you can type:

   ```sh
   open "https://$(terraform output -raw  nlb_dns_name):8080/materialize"
   ```

   > **Tip:** The example uses a self-signed ClusterIssuer. As such, you may encounter a
>    warning with regards to the certificate. In production, run with
>    certificates from an official Certificate Authority (CA) rather than
>    self-signed certificates.

1. Log in as `mz_system`, using `external_login_password_mz_system` as the
   password.

1. Create new users and log out.

   In general, other than the initial login to create new users for new
   deployments, avoid using `mz_system` since `mz_system` also used by the
   Materialize Operator for upgrades and maintenance tasks.

   For more information on authentication and authorization for Self-Managed
   Materialize, see:

   - [Authentication](/security/self-managed/authentication/)
   - [Access Control](/security/self-managed/access-control/)

1. Login as one of the created user.

#### Connect using `psql`

> **Note:** - **If using a public NLB:** Both SQL and Console are available via the
> public NLB. You can connect directly using the NLB's DNS name from anywhere
> on the internet (subject to your `ingress_cidr_blocks` configuration).
> - **If using a private (internal) NLB:** You can connect from inside the same VPC or from networks that are privately connected to it. Alternatively, use Kubernetes port-forwarding for both SQL and Console.

1. To connect using `psql`, in the connection string, specify:

   - `mz_system` as the user
   - Your `<nlb_dns_name>` as the host
   - `6875` as the port:

   ```sh
   psql "postgres://mz_system@$(terraform output -raw  nlb_dns_name):6875/materialize"
   ```

   When prompted for the password, enter the
   `external_login_password_mz_system` value.

1. Create new users and log out.

   In general, other than the initial login to create new users for new
   deployments, avoid using `mz_system` since `mz_system` also used by the
   Materialize Operator for upgrades and maintenance tasks.

   For more information on authentication and authorization for Self-Managed
   Materialize, see:

   - [Authentication](/security/self-managed/authentication/)
   - [Access Control](/security/self-managed/access-control/)

1. Login as one of the created user.

## Customizing Your Deployment

> **Tip:** To reduce cost in your demo environment, you can tweak subnet CIDRs
> and instance types in `main.tf`.

You can customize each Terraform module independently.

- For details on the Terraform modules, see both the [top
level](https://github.com/MaterializeInc/materialize-terraform-self-managed/tree/main)
and [AWS
specific](https://github.com/MaterializeInc/materialize-terraform-self-managed/tree/main/aws) READMEs.

- For details on recommended instance sizing and configuration, see the [AWS
deployment
guide](/self-managed-deployments/deployment-guidelines/aws-deployment-guidelines/).

See also:

- [Configuring System
  Parameters](/self-managed-deployments/configuration-system-parameters/)
- [Materialize Operator
  Configuration](/self-managed-deployments/operator-configuration/)
- [Materialize CRD Field
  Descriptions](/self-managed-deployments/materialize-crd-field-descriptions/)

## Cleanup

To delete the whole sample infrastructure and deployment (including the
Materialize operator and Materialize instances and data), run from the Terraform
directory:

```bash
terraform destroy
```

When prompted to proceed, type `yes` to confirm the deletion.

## See Also

- [Troubleshooting](/self-managed-deployments/troubleshooting/)
- [Security](/security/self-managed/)

<!-- mz-docs page: self-managed-deployments/installation/install-on-azure -->

# Install on Azure
Install Materialize on Azure using the Terraform module.
Materialize provides a set of modular [Terraform
modules](https://github.com/MaterializeInc/materialize-terraform-self-managed/tree/main)
that can be used to deploy all services required for Materialize to run on Azure.
These modules serve as composable building blocks that you can integrate into
existing DevOps workflows, either as a full set or individually.

Self-managed Materialize requires: a Kubernetes (v1.31+) cluster; PostgreSQL as
a metadata database; blob storage; and a license key.
 The example on this page
deploys a complete Materialize environment on Azure using the modular Terraform
setup from this repository.

> **Note:** We recommend pinning your module sources to specific tags to avoid unexpected breaking
> changes in future versions.
> We recommend updating your module source tags when updating Materialize versions,
> taking care to follow any instructions in the release notes.

## What Gets Created

This example provisions the following infrastructure:

### Resource Group

| Resource | Description |
|----------|-------------|
| Resource Group | New resource group to contain all resources |

### Networking

| Resource | Description |
|----------|-------------|
| Virtual Network | 20.0.0.0/16 address space |
| AKS Subnet | 20.0.0.0/20 with NAT Gateway association and service endpoints for Storage and SQL |
| PostgreSQL Subnet | 20.0.16.0/24 delegated to PostgreSQL Flexible Server |
| NAT Gateway | Standard SKU with static public IP for outbound connectivity |
| Private DNS Zone | For PostgreSQL private endpoint resolution with VNet link |

### Compute

| Resource | Description |
|----------|-------------|
| AKS Cluster | Version 1.34 with Cilium networking (network plugin: azure, data plane: cilium, policy: cilium) |
| Default Node Pool | Standard_D4pds_v6 VMs, autoscaling 2-5 nodes, labeled for generic workloads |
| Materialize Node Pool | Standard_E4pds_v6 VMs with 100GB disk, autoscaling 2-5 nodes, swap enabled, dedicated taints for Materialize workloads |
| Managed Identities | AKS cluster identity (used by AKS control plane to provision Azure resources like load balancers and network interfaces) and Workload identity (used by Materialize pods for secure, passwordless authentication to Azure Storage) |

### Database

| Resource | Description |
|----------|-------------|
| Azure PostgreSQL Flexible Server | Version 15 |
| SKU | GP_Standard_D2s_v3 (2 vCores, 4GB memory) |
| Storage | 32GB with 7-day backup retention |
| Network Access | Public Network Access is disabled, Private access only (no public endpoint) |
| Database | `materialize` database pre-created |

### Storage

| Resource | Description |
|----------|-------------|
| Storage Account | Premium BlockBlobStorage with LRS replication for Materialize persistence |
| Container | `materialize` blob container |
| Access Control | Workload Identity federation for Kubernetes service account (passwordless authentication via OIDC) |
| Network Access | Currently allows <red>**all traffic**</red>(production deployments should restrict to AKS subnet only traffic) |

### Kubernetes Add-ons

| Resource | Description |
|----------|-------------|
| cert-manager | Certificate management controller for Kubernetes that automates TLS certificate provisioning and renewal |
| Self-signed ClusterIssuer | Provides self-signed TLS certificates for Materialize instance internal communication (balancerd, console). Used by the Materialize instance for secure inter-component communication. |

### Materialize

| Resource | Description |
|----------|-------------|
| Operator | Materialize Kubernetes operator in the `materialize` namespace |
| Instance | Single Materialize instance in the `materialize-environment` namespace |
| Load Balancers | Azure Load Balancers for access to Materialize 
| Port | Description |
| --- | --- |
| 6875 | For SQL connections to the database |
| 6876 | For HTTP(S) connections to the database |
| 8080 | For HTTP(S) connections to Materialize Console |
  |

### Observability

On by default starting with v11.0.0 of the Materialize Terraform Modules.
Whenever `enable_observability` is `true`,
the following are created as well:

| Resource | Description |
|----------|-------------|
| Monitoring stack | Grafana, Thanos, Loki, Grafana Alloy, and Alertmanager in the `monitoring` namespace, with the Materialize dashboards pre-installed |
| Blob Containers | Dedicated containers for metrics and logs |
| Grafana PostgreSQL Flexible Server | `B_Standard_B1ms` server holding Grafana's own state (users, API tokens, annotations, dashboard versions) |
| Grafana Load Balancer | Internal Azure Load Balancer for reaching Grafana, allowlisted to `ingress_cidr_blocks` |

This stack requires v10.0.0 or later of the Materialize Terraform Modules,
which replaced an earlier Prometheus-and-Grafana pair. The Grafana database
and load balancer were added in v10.1.0, and are both billable. Starting with
v11.0.0, `enable_observability` defaults to `true`, so set it to `false` if you
do not want the stack. For what the stack stores and where else it can send
it, see [How logs and metrics are
stored](/observability/self-managed/storage/). For reaching Grafana, see
[Grafana](/observability/self-managed/grafana/).

## Prerequisites

### Azure Account Requirements

An active Azure subscription with appropriate permissions to create:
- AKS clusters
- Azure PostgreSQL Flexible Server instances
- Storage accounts
- Virtual networks and networking resources
- Managed identities and role assignments

### Required Tools

- [Terraform](https://developer.hashicorp.com/terraform/install?product_intent=terraform)
- [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- [Helm 3.2.0+](https://helm.sh/docs/intro/install/)

### License Key

| License key type | Deployment type | Action |
| --- | --- | --- |
| Community | New deployments | <p>To get a license key:</p> <ul> <li>If you have a Cloud account, visit the <a href="https://console.materialize.com/license/" ><strong>License</strong> page in the Materialize Console</a>.</li> <li>If you do not have a Cloud account, visit <a href="https://materialize.com/self-managed/community-license/" >https://materialize.com/self-managed/community-license/</a>.</li> </ul> |
| Community | Existing deployments | Contact <a href="https://materialize.com/docs/support/" >Materialize support</a>. |
| Enterprise | New deployments | Visit <a href="https://materialize.com/self-managed/enterprise-license/" >https://materialize.com/self-managed/enterprise-license/</a> to purchase an Enterprise license. |
| Enterprise | Existing deployments | Contact <a href="https://materialize.com/docs/support/" >Materialize support</a>. |

## Getting started: Simple example

> **Note:** We recommend pinning your module sources to specific tags to avoid unexpected breaking
> changes in future versions.
> We recommend updating your module source tags when updating Materialize versions,
> taking care to follow any instructions in the release notes.

> **Tip:** * The `examples/simple` example, used in this tutorial, is provided for illustration and to help you get started. In practice, we recommend instantiating these modules within your own Terraform code rather than relying on the example configuration directly.
> * The simple example used in this tutorial enables [Password
> authentication](https://github.com/MaterializeInc/materialize-terraform-self-managed/blob/v10.1.0/azure/examples/simple/main.tf#L429)
> for the Materialize instance. To use a different authentication method, update
> [`authenticator_kind`](https://github.com/MaterializeInc/materialize-terraform-self-managed/blob/v10.1.0/kubernetes/modules/materialize-instance/README.md#input_authenticator_kind).
> See [Authentication](/security/self-managed/authentication/) for the supported
> authentication mechanisms.

### Step 1: Set Up the Environment

1. Open a terminal window.

1. Clone the Materialize Terraform repository and go to the
   `azure/examples/simple` directory.

   ```bash
   git clone https://github.com/MaterializeInc/materialize-terraform-self-managed.git
   cd materialize-terraform-self-managed/azure/examples/simple
   ```

1. Authenticate with Azure.

    ```bash
    az login
    ```

   The command opens a browser window to sign in to Azure. Sign in.

1. Select the subscription and tenant to use. After you have signed in, back in
   the terminal, your tenant and subscription information is displayed.

    ```none
    Retrieving tenants and subscriptions for the selection...

    [Tenant and subscription selection]

    No     Subscription name    Subscription ID                       Tenant
    -----  -------------------  ------------------------------------  ----------------
    [1]*   ...                  ...                                   ...

   The default is marked with an *; the default tenant is '<Tenant>' and
   subscription is '<Subscription Name>' (<Subscription ID>).
   ```

   Select the subscription and tenant.

### Step 2: Configure Terraform Variables

1. Create a `terraform.tfvars` file with the following variables:

   | Variable      | Description                 |
   | -----------   | ----------------------------|
   | `subscription_id`     | Azure subscription ID. |
   | `resource_group_name` | Name for the resource group to create (e.g., `mz-demo-rg`). |
   | `name_prefix`         | Prefix for all resource names (e.g., `simple-demo`). |
   | `location`            | Azure region for deployment (e.g., `westus2`). |
   | `license_key`         | Materialize license key. |
   | `crd_version`         | CRD API version to use for the Materialize instance: `v1` (default starting with Materialize Terraform Modules v4.0.0) or `v1alpha1`. |
   | `tags`                | Map of tags to apply to resources. |

   > **Tip:** Starting in Materialize Terraform module version v4.0.0, `crd_version`
   > defaults to [CRD API version
   > `v1`](/self-managed-deployments/upgrading/adopting-the-v1-crd/). `v1`
   > requires Materialize v26.30 or greater and is available starting in
   > Terraform module version v3.1.1. To use `v1alpha1` instead, set
   > `crd_version = "v1alpha1"`.

   ```hcl
   subscription_id     = "your-subscription-id"
   resource_group_name = "mz-demo-rg"
   name_prefix         = "simple-demo"
   location            = "westus2"
   license_key         = "your-materialize-license-key"
   crd_version = "v1"   # Default starting with Materialize Terraform Modules v4.0.0. v1 requires Materialize v26.30+.
   tags = {
     environment = "demo"
   }
   # internal_load_balancer = false   # default = true (internal load balancer). You can set to false = public load balancer.
   # ingress_cidr_blocks = ["x.x.x.x/n", ...]
   # k8s_apiserver_authorized_networks  = ["x.x.x.x/n", ...]
   # enable_observability = false   # default = true (install the observability stack).
   # grafana_host = "grafana.example.com"   # Only used when enable_observability = true.
   ```

   > **Note:** With `enable_observability` on, the modules also create a
>    `B_Standard_B1ms` PostgreSQL Flexible Server for Grafana's own state and an
>    internal load balancer to reach Grafana on. Both are billable. See
>    [Grafana](/observability/self-managed/grafana/).

   <p><strong>Additional variables</strong>:</p>
   <ul>
   <li><code>internal_load_balancer</code>: Flag that determines whether the load balancer
   is internal (default) or public.</li>
   <li><code>ingress_cidr_blocks</code>: List of CIDR blocks allowed to reach the load
   balancer if the load balancer is public (<code>internal_load_balancer: false</code>).
   If unset, defaults to <code>[&quot;0.0.0.0/0&quot;]</code> (i.e., <red><strong>all</strong></red> IPv4
   addresses on the internet). <strong>Only applied when the load balancer is public</strong>.</li>
   <li><code>k8s_apiserver_authorized_networks</code>: List of CIDR
   blocks allowed to access your cluster endpoint. If unset, defaults to
   <code>[&quot;0.0.0.0/0&quot;]</code> (<red><strong>all</strong></red> IPv4 addresses on the internet).</li>
   <li><code>enable_observability</code>: Flag that determines whether to deploy the
   monitoring stack (Grafana, metrics, and logs) alongside Materialize.
   Defaults to <code>false</code> in the <code>simple</code> example. See
   <a href="/observability/self-managed/grafana/" >Grafana</a>.</li>
   </ul>
   > **Note:** Refer to your organization's security practices to set these values accordingly.

### Step 3: Apply the Terraform

1. Initialize the Terraform directory to download the required providers
   and modules:

   ```bash
   terraform init
   ```

1. Apply the Terraform configuration to create the infrastructure.

   ```bash
   terraform apply
   ```

   If you are satisfied with the planned changes, type `yes` when prompted
   to proceed.

1. From the output, you will need the following field(s) to connect:
   - `console_load_balancer_ip` for the Materialize Console
   - `balancerd_load_balancer_ip` to connect PostgreSQL-compatible
     clients/drivers.
   - `external_login_password_mz_system`.

   ```bash
   terraform output -raw <field_name>
   ```

   > **Tip:** Your shell may show an ending marker (such as `%`) because the
>    output did not end with a newline. Do not include the marker when using the value.

1. Configure `kubectl` to connect to your cluster, replacing:
   - `<your-resource-group-name>` with your resource group name; i.e., the
     `resource_group_name` in the Terraform output or in the
     `terraform.tfvars` file.

   - `<your-aks-cluster-name>` with your cluster name; i.e., the
     `aks_cluster_name` in the Terraform output. For the sample example,
     your cluster name has the form `{prefix_name}-aks`; e.g., `simple-demo-aks`.

   ```bash
   # az aks get-credentials --resource-group <your-resource-group-name> --name <your-aks-cluster-name>
   az aks get-credentials --resource-group $(terraform output -raw resource_group_name) --name $(terraform output -raw aks_cluster_name)
   ```

### Step 4. Optional. Verify the deployment.

1. Check the status of your deployment:
   **Operator:**
   To check the status of the Materialize operator, which runs in the `materialize` namespace:
   ```bash
   kubectl -n materialize get all
   ```

   **Materialize instance:**
   To check the status of the Materialize instance, which runs in the `materialize-environment` namespace:
   ```bash
   kubectl -n materialize-environment get all
   ```

   <p>If you run into an error during deployment, refer to the
   <a href="/self-managed-deployments/troubleshooting/" >Troubleshooting</a>.</p>

1. Check the CRD version of the Materialize manifest.
   To check the CRD version of the Materialize manifest that was applied, run
   the following:

   ```sh
   terraform state show 'module.materialize_instance.kubectl_manifest.materialize_instance' \
     | grep -iE 'api_?version|kind'
   ```

### Step 5: Connect to Materialize

You can connect to Materialize via the Materialize Console or
PostgreSQL-compatible tools/drivers using the following ports:

| Port | Description |
| --- | --- |
| 6875 | For SQL connections to the database |
| 6876 | For HTTP(S) connections to the database |
| 8080 | For HTTP(S) connections to Materialize Console |

#### Connect using the Materialize Console

> **Note:** - **If using a public NLB:** Both SQL and Console are available via the
> public NLB. You can connect directly using the NLB's DNS name from anywhere
> on the internet (subject to your `ingress_cidr_blocks` configuration).
> - **If using a private (internal) NLB:** You can connect from inside the same VPC or from networks that are privately connected to it. Alternatively, use Kubernetes port-forwarding for both SQL and Console.

Using the `console_load_balancer_ip` and `external_login_password_mz_system`
from the Terraform output, you can connect to Materialize via the Materialize
Console.

1. To connect to the Materialize Console, open a browser to
   `https://<console_load_balancer_ip>:8080`, substituting your
   `<console_load_balancer_ip>`.

   From the terminal, you can type:

   ```sh
   open "https://$(terraform output -raw  console_load_balancer_ip):8080/materialize"
   ```

   > **Tip:** The example uses a self-signed ClusterIssuer. As such, you may encounter a
>    warning with regards to the certificate. In production, run with
>    certificates from an official Certificate Authority (CA) rather than
>    self-signed certificates.

1. Log in as `mz_system`, using `external_login_password_mz_system` as the
   password.

1. Create new users and log out.

   In general, other than the initial login to create new users for new
   deployments, avoid using `mz_system` since `mz_system` also used by the
   Materialize Operator for upgrades and maintenance tasks.

   For more information on authentication and authorization for Self-Managed
   Materialize, see:

   - [Authentication](/security/self-managed/authentication/)
   - [Access Control](/security/self-managed/access-control/)

1. Login as one of the created user.

#### Connect using `psql`

> **Note:** - **If using a public NLB:** Both SQL and Console are available via the
> public NLB. You can connect directly using the NLB's DNS name from anywhere
> on the internet (subject to your `ingress_cidr_blocks` configuration).
> - **If using a private (internal) NLB:** You can connect from inside the same VPC or from networks that are privately connected to it. Alternatively, use Kubernetes port-forwarding for both SQL and Console.

Using the `balancerd_load_balancer_ip` and `external_login_password_mz_system`
from the Terraform output, you can connect to Materialize via
PostgreSQL-compatible clients/drivers, such as `psql`.

1. To connect using `psql`, in the connection string, specify:
   - `mz_system` as the user
   - `balancerd_load_balancer_ip` as the host
   - `6875` as the port:

   ```bash
   psql "postgres://mz_system@$(terraform output -raw balancerd_load_balancer_ip):6875/materialize"
   ```

   When prompted for the password, enter the
   `external_login_password_mz_system` value.

1. Create new users and log out.

   In general, other than the initial login to create new users for new
   deployments, avoid using `mz_system` since `mz_system` also used by the
   Materialize Operator for upgrades and maintenance tasks.

   For more information on authentication and authorization for Self-Managed
   Materialize, see:

   - [Authentication](/security/self-managed/authentication/)
   - [Access Control](/security/self-managed/access-control/)

1. Login as one of the created user.

## Customizing Your Deployment

> **Tip:** To reduce cost in your demo environment, you can tweak VM sizes and database tiers in `main.tf`.

You can customize each Terraform module independently.

- For details on the Terraform modules, see both the [top
level](https://github.com/MaterializeInc/materialize-terraform-self-managed/tree/main)
and [Azure
specific](https://github.com/MaterializeInc/materialize-terraform-self-managed/tree/main/azure) modules.

- For details on recommended instance sizing and configuration, see the [Azure
deployment
guide](/self-managed-deployments/deployment-guidelines/azure-deployment-guidelines/).

> **Note:** Autoscaling: Uses Azure's native cluster autoscaler that integrates directly with Azure Virtual Machine Scale Sets for automated node scaling.

See also:
- [Configuring System
  Parameters](/self-managed-deployments/configuration-system-parameters/)
- [Materialize Operator
  Configuration](/self-managed-deployments/operator-configuration/)
- [Materialize CRD Field
  Descriptions](/self-managed-deployments/materialize-crd-field-descriptions/)

## Cleanup

To delete the whole sample infrastructure and deployment (including the
Materialize operator and Materialize instances and data), run from the Terraform
directory:

```bash
terraform destroy
```

When prompted to proceed, type `yes` to confirm the deletion.

## See Also

- [Troubleshooting](/self-managed-deployments/troubleshooting/)
- [Security](/security/self-managed/)

<!-- mz-docs page: self-managed-deployments/installation/install-on-gcp -->

# Install on GCP
Materialize provides a set of modular [Terraform
modules](https://github.com/MaterializeInc/materialize-terraform-self-managed/tree/main)
that can be used to deploy all services required for Materialize to run on Google Cloud.
These modules serve as composable building blocks that you can integrate into
existing DevOps workflows, either as a full set or individually.

Self-managed Materialize requires: a Kubernetes (v1.31+) cluster; PostgreSQL as
a metadata database; blob storage; and a license key.
 The example on this page
deploys a complete Materialize environment on GCP using the modular Terraform
setup from this repository.

> **Note:** We recommend pinning your module sources to specific tags to avoid unexpected breaking
> changes in future versions.
> We recommend updating your module source tags when updating Materialize versions,
> taking care to follow any instructions in the release notes.

## What Gets Created

This example provisions the following infrastructure:

### Networking

| Resource | Description |
|----------|-------------|
| VPC Network | Custom VPC with auto-create subnets disabled |
| Subnet | 192.168.0.0/20 primary range with private Google access enabled |
| Secondary Ranges | Pods: 192.168.64.0/18, Services: 192.168.128.0/20 |
| Cloud Router | For NAT and routing configuration |
| Cloud NAT | For outbound internet access from private nodes |
| VPC Peering | Service networking connection for Cloud SQL private access |

### Compute

| Resource | Description |
|----------|-------------|
| GKE Cluster | Regional cluster with Workload Identity enabled |
| Generic Node Pool | c4-standard-8 machines, autoscaling 2-5 nodes, 50GB disk, for general workloads |
| Materialize Node Pool | c4a-highmem-8-lssd machines (Arm-based), autoscaling 2-5 nodes, 100GB disk, 2 bundled local SSDs, swap enabled, dedicated taints for Materialize workloads |
| Service Account | GKE service account with workload identity binding |

### Database

| Resource | Description |
|----------|-------------|
| Cloud SQL PostgreSQL | Private IP only (no public IP) |
| Tier | db-custom-N4-2-4096 (N4 series, 2 vCPUs, 4GB memory) |
| Database | `materialize` database with UTF8 charset |
| User | `materialize` user with auto-generated password |
| Network | Connected via VPC peering for private access |

### Storage

| Resource | Description |
|----------|-------------|
| Cloud Storage Bucket | Regional bucket for Materialize persistence |
| Access | HMAC keys for S3-compatible access (Workload Identity service account with storage permissions is configured but not currently used by Materialize for GCS access, in future we will remove HMAC keys and support access to GCS either via Workload Identity Federation or via Kubernetes ServiceAccounts that impersonate IAM service accounts) |
| Versioning | Disabled (for testing; enable in production) |

### Kubernetes Add-ons

| Resource | Description |
|----------|-------------|
| cert-manager | Certificate management controller for Kubernetes that automates TLS certificate provisioning and renewal |
| Self-signed ClusterIssuer | Provides self-signed TLS certificates for Materialize instance internal communication (balancerd, console). Used by the Materialize instance for secure inter-component communication. |

### Materialize

| Resource | Description |
|----------|-------------|
| Operator | Materialize Kubernetes operator in the `materialize` namespace |
| Instance | Single Materialize instance in the `materialize-environment` namespace |
| Load Balancers | GCP Load Balancers for access to Materialize 
| Port | Description |
| --- | --- |
| 6875 | For SQL connections to the database |
| 6876 | For HTTP(S) connections to the database |
| 8080 | For HTTP(S) connections to Materialize Console |
 |

### Observability

On by default starting with v11.0.0 of the Materialize Terraform Modules.
Whenever `enable_observability` is `true`,
the following are created as well:

| Resource | Description |
|----------|-------------|
| Monitoring stack | Grafana, Thanos, Loki, Grafana Alloy, and Alertmanager in the `monitoring` namespace, with the Materialize dashboards pre-installed |
| Cloud Storage Buckets | Dedicated buckets for metrics and logs |
| Grafana Cloud SQL PostgreSQL | `db-f1-micro` instance holding Grafana's own state (users, API tokens, annotations, dashboard versions) |
| Grafana Load Balancer | Internal GCP Load Balancer for reaching Grafana, allowlisted to `ingress_cidr_blocks` |

This stack requires v10.0.0 or later of the Materialize Terraform Modules,
which replaced an earlier Prometheus-and-Grafana pair. The Grafana database
and load balancer were added in v10.1.0, and are both billable. Starting with
v11.0.0, `enable_observability` defaults to `true`, so set it to `false` if you
do not want the stack. For what the stack stores and where else it can send
it, see [How logs and metrics are
stored](/observability/self-managed/storage/). For reaching Grafana, see
[Grafana](/observability/self-managed/grafana/).

## Prerequisites

### GCP Account Requirements

A Google account with permission to:
- Enable Google Cloud APIs/services on for your project.
- Create:
  - GKE clusters
  - Cloud SQL instances
  - Cloud Storage buckets
  - VPC networks and networking resources
  - Service accounts and IAM bindings

### Required Tools

- [Terraform](https://developer.hashicorp.com/terraform/install?product_intent=terraform)
- [gcloud CLI](https://cloud.google.com/sdk/docs/install)
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- [Helm 3.2.0+](https://helm.sh/docs/intro/install/)
- [kubectl gke plugin](https://cloud.google.com/kubernetes-engine/docs/how-to/cluster-access-for-kubectl#install_plugin)

### License Key

| License key type | Deployment type | Action |
| --- | --- | --- |
| Community | New deployments | <p>To get a license key:</p> <ul> <li>If you have a Cloud account, visit the <a href="https://console.materialize.com/license/" ><strong>License</strong> page in the Materialize Console</a>.</li> <li>If you do not have a Cloud account, visit <a href="https://materialize.com/self-managed/community-license/" >https://materialize.com/self-managed/community-license/</a>.</li> </ul> |
| Community | Existing deployments | Contact <a href="https://materialize.com/docs/support/" >Materialize support</a>. |
| Enterprise | New deployments | Visit <a href="https://materialize.com/self-managed/enterprise-license/" >https://materialize.com/self-managed/enterprise-license/</a> to purchase an Enterprise license. |
| Enterprise | Existing deployments | Contact <a href="https://materialize.com/docs/support/" >Materialize support</a>. |

## Getting started: Simple example

> **Note:** We recommend pinning your module sources to specific tags to avoid unexpected breaking
> changes in future versions.
> We recommend updating your module source tags when updating Materialize versions,
> taking care to follow any instructions in the release notes.

> **Tip:** * The `examples/simple` example, used in this tutorial, is provided for illustration and to help you get started. In practice, we recommend instantiating these modules within your own Terraform code rather than relying on the example configuration directly.
> * The simple example used in this tutorial enables [Password
> authentication](https://github.com/MaterializeInc/materialize-terraform-self-managed/blob/v10.1.0/gcp/examples/simple/main.tf#L500)
> for the Materialize instance. To use a different authentication method, update
> [`authenticator_kind`](https://github.com/MaterializeInc/materialize-terraform-self-managed/blob/v10.1.0/kubernetes/modules/materialize-instance/README.md#input_authenticator_kind).
> See [Authentication](/security/self-managed/authentication/) for the supported
> authentication mechanisms.

### Step 1: Set Up the Environment

1. Open a terminal window.

1. Clone the Materialize Terraform repository and go to the
   `gcp/examples/simple` directory.

   ```bash
   git clone https://github.com/MaterializeInc/materialize-terraform-self-managed.git
   cd materialize-terraform-self-managed/gcp/examples/simple
   ```

1. Authenticate to GCP with your user account.

   ```bash
   gcloud auth login
   ```

1. Find the list of GCP projects:

   ```bash
   gcloud projects list
   ```

1. Set your active GCP project, substitute with your `<PROJECT_ID>`.

   ```bash
   gcloud config set project <PROJECT_ID>
   ```

1. Enable the following APIs for your project:

   ```bash
   gcloud services enable container.googleapis.com               # For creating Kubernetes clusters
   gcloud services enable compute.googleapis.com                 # For creating GKE nodes and other compute resources
   gcloud services enable sqladmin.googleapis.com                # For creating databases
   gcloud services enable cloudresourcemanager.googleapis.com    # For managing GCP resources
   gcloud services enable servicenetworking.googleapis.com       # For private network connections
   gcloud services enable iamcredentials.googleapis.com          # For security and authentication
   gcloud services enable iam.googleapis.com                     # For managing IAM service accounts and policies
   gcloud services enable storage.googleapis.com                 # For Cloud Storage buckets
   ```

1. Authenticate application default credentials for Terraform

   ```bash
   gcloud auth application-default login
   ```

### Step 2: Configure Terraform Variables

1. Create a `terraform.tfvars` file and specify the following variables:

   | Variable      | Description                 |
   | -----------   | ----------------------------|
   | `project_id`  | Set to your GCP project ID. |
   | `name_prefix` | Set a prefix for all resource names (e.g., `simple-demo`) as well as your release name for the Operator |
   | `region`      | Set the GCP region for the deployment (e.g., `us-central1`).  |
   | `license_key` | Set to your Materialize license key.     |
   | `crd_version` | CRD API version to use for the Materialize instance: `v1` (default starting with Materialize Terraform Modules v4.0.0) or `v1alpha1`. |
   | `labels`      | Set to the labels to apply to resources. |

   > **Tip:** Starting in Materialize Terraform module version v4.0.0, `crd_version`
   > defaults to [CRD API version
   > `v1`](/self-managed-deployments/upgrading/adopting-the-v1-crd/). `v1`
   > requires Materialize v26.30 or greater and is available starting in
   > Terraform module version v3.1.1. To use `v1alpha1` instead, set
   > `crd_version = "v1alpha1"`.

   ```hcl
   project_id  = "my-gcp-project"
   name_prefix = "simple-demo"
   region      = "us-central1"
   license_key = "your-materialize-license-key"
   crd_version = "v1"   # Default starting with Materialize Terraform Modules v4.0.0. v1 requires Materialize v26.30+.
   labels = {
     environment = "demo"
     created_by  = "terraform"
   }
   # internal_load_balancer = false   # default = true (internal load balancer). You can set to false = public load balancer.
   # ingress_cidr_blocks = ["x.x.x.x/n", ...]
   # k8s_apiserver_authorized_networks  = ["x.x.x.x/n", ...]
   # enable_observability = false   # default = true (install the observability stack).
   # grafana_host = "grafana.example.com"   # Only used when enable_observability = true.
   ```

   > **Note:** With `enable_observability` on, the modules also create a `db-f1-micro`
>    Cloud SQL instance for Grafana's own state and an internal load balancer to
>    reach Grafana on.
>    Both are billable. See
>    [Grafana](/observability/self-managed/grafana/).

   <p><strong>Additional variables</strong>:</p>
   <ul>
   <li><code>internal_load_balancer</code>: Flag that determines whether the load balancer
   is internal (default) or public.</li>
   <li><code>ingress_cidr_blocks</code>: List of CIDR blocks allowed to reach the load
   balancer if the load balancer is public (<code>internal_load_balancer: false</code>).
   If unset, defaults to <code>[&quot;0.0.0.0/0&quot;]</code> (i.e., <red><strong>all</strong></red> IPv4
   addresses on the internet). <strong>Only applied when the load balancer is public</strong>.</li>
   <li><code>k8s_apiserver_authorized_networks</code>: List of CIDR
   blocks allowed to access your cluster endpoint. If unset, defaults to
   <code>[&quot;0.0.0.0/0&quot;]</code> (<red><strong>all</strong></red> IPv4 addresses on the internet).</li>
   <li><code>enable_observability</code>: Flag that determines whether to deploy the
   monitoring stack (Grafana, metrics, and logs) alongside Materialize.
   Defaults to <code>false</code> in the <code>simple</code> example. See
   <a href="/observability/self-managed/grafana/" >Grafana</a>.</li>
   </ul>
   > **Note:** Refer to your organization's security practices to set these values accordingly.

### Step 3: Apply the Terraform

1. Initialize the Terraform directory to download the required providers
   and modules:

   ```bash
   terraform init
   ```

1. Apply the Terraform configuration to create the infrastructure.

   ```bash
   terraform apply
   ```

   If you are satisfied with the planned changes, type `yes` when prompted
   to proceed.

1. From the output, you will need the following field(s) to connect:
   - `console_load_balancer_ip` for the Materialize Console
   - `balancerd_load_balancer_ip` to connect PostgreSQL-compatible
     clients/drivers.
   - `external_login_password_mz_system`.

   ```bash
   terraform output -raw <field_name>
   ```

   > **Tip:** Your shell may show an ending marker (such as `%`) because the
>    output did not end with a newline. Do not include the marker when using the value.

1. Configure `kubectl` to connect to your GKE cluster, replacing:

   - `<your-gke-cluster-name>` with your cluster name; i.e., the
     `gke_cluster_name` in the Terraform output. For the sample example, your
     cluster name has the form `<name_prefix>-gke`; e.g., `simple-demo-gke`

   - `<your-region>` with your cluster location; i.e., the
     `gke_cluster_location` in the Terraform output. Your
     region can also be found in your `terraform.tfvars` file.

   - `<your-project-id>` with your GCP project ID.

   ```bash
   # gcloud container clusters get-credentials <your-gke-cluster-name> --region <your-region> --project <your-project-id>
   gcloud container clusters get-credentials $(terraform output -raw gke_cluster_name) \
    --region $(terraform output -raw gke_cluster_location) \
    --project <your-project-id>
   ```

### Step 4. Optional. Verify the status of your deployment

1. Check the status of your deployment:
   **Operator:**
   To check the status of the Materialize operator, which runs in the `materialize` namespace:
   ```bash
   kubectl -n materialize get all
   ```

   **Materialize instance:**
   To check the status of the Materialize instance, which runs in the `materialize-environment` namespace:
   ```bash
   kubectl -n materialize-environment get all
   ```

   <p>If you run into an error during deployment, refer to the
   <a href="/self-managed-deployments/troubleshooting/" >Troubleshooting</a>.</p>

1. Check the CRD version of the Materialize manifest.
   To check the CRD version of the Materialize manifest that was applied, run
   the following:

   ```sh
   terraform state show 'module.materialize_instance.kubectl_manifest.materialize_instance' \
     | grep -iE 'api_?version|kind'
   ```

### Step 5: Connect to Materialize

You can connect to Materialize via the Materialize Console or
PostgreSQL-compatible tools/drivers using the following ports:

| Port | Description |
| --- | --- |
| 6875 | For SQL connections to the database |
| 6876 | For HTTP(S) connections to the database |
| 8080 | For HTTP(S) connections to Materialize Console |

#### Connect using the Materialize Console

> **Note:** - **If using a public NLB:** Both SQL and Console are available via the
> public NLB. You can connect directly using the NLB's DNS name from anywhere
> on the internet (subject to your `ingress_cidr_blocks` configuration).
> - **If using a private (internal) NLB:** You can connect from inside the same VPC or from networks that are privately connected to it. Alternatively, use Kubernetes port-forwarding for both SQL and Console.

Using the `console_load_balancer_ip`  and `external_login_password_mz_system`
from the Terraform output, you can connect to Materialize via the Materialize
Console.

1. To connect to the Materialize Console, open a browser to
   `https://<console_load_balancer_ip>:8080`, substituting your
   `<console_load_balancer_ip>`.

   From the terminal, you can type:

   ```sh
   open "https://$(terraform output -raw console_load_balancer_ip):8080/materialize"
   ```

   > **Tip:** The example uses a self-signed ClusterIssuer. As such, you may encounter a
>    warning with regards to the certificate. In production, run with
>    certificates from an official Certificate Authority (CA) rather than
>    self-signed certificates.

1. Log in as `mz_system`, using `external_login_password_mz_system` as the
   password.

1. Create new users and log out.

   In general, other than the initial login to create new users for new
   deployments, avoid using `mz_system` since `mz_system` also used by the
   Materialize Operator for upgrades and maintenance tasks.

   For more information on authentication and authorization for Self-Managed
   Materialize, see:

   - [Authentication](/security/self-managed/authentication/)
   - [Access Control](/security/self-managed/access-control/)

1. Login as one of the created user.

#### Connect using `psql`

> **Note:** - **If using a public NLB:** Both SQL and Console are available via the
> public NLB. You can connect directly using the NLB's DNS name from anywhere
> on the internet (subject to your `ingress_cidr_blocks` configuration).
> - **If using a private (internal) NLB:** You can connect from inside the same VPC or from networks that are privately connected to it. Alternatively, use Kubernetes port-forwarding for both SQL and Console.

Using the `balancerd_load_balancer_ip` and `external_login_password_mz_system`
from the Terraform output, you can connect to Materialize via
PostgreSQL-compatible clients/drivers, such as `psql`:

1. To connect using `psql`, in the connection string, specify:
   - `mz_system` as the user
   - `balancerd_load_balancer_ip` as the host
   - `6875` as the port:

   ```bash
   psql "postgres://mz_system@$(terraform output -raw balancerd_load_balancer_ip):6875/materialize"
   ```

   When prompted for the password, enter the
   `external_login_password_mz_system` value.

1. Create new users and log out.

   In general, other than the initial login to create new users for new
   deployments, avoid using `mz_system` since `mz_system` also used by the
   Materialize Operator for upgrades and maintenance tasks.

   For more information on authentication and authorization for Self-Managed
   Materialize, see:

   - [Authentication](/security/self-managed/authentication/)
   - [Access Control](/security/self-managed/access-control/)

1. Login as one of the created user.

## Customizing Your Deployment

> **Tip:** To reduce cost in your demo environment, you can tweak machine types and database tiers in `main.tf`.

You can customize each module independently.

- For details on the Terraform modules, see both the [top
level](https://github.com/MaterializeInc/materialize-terraform-self-managed/tree/main)
and [GCP
specific](https://github.com/MaterializeInc/materialize-terraform-self-managed/tree/main/gcp)
modules.

- For details on recommended instance sizing and configuration, see the [GCP
deployment
guide](/self-managed-deployments/deployment-guidelines/gcp-deployment-guidelines/).

> **Note:** **GCP Storage Authentication Limitation:** Materialize currently only supports HMAC key authentication for GCS access (S3-compatible API). While the modules configure both HMAC keys and Workload Identity, Materialize uses HMAC keys for actual storage access.

See also:
- [Configuring System
  Parameters](/self-managed-deployments/configuration-system-parameters/)
- [Materialize Operator
  Configuration](/self-managed-deployments/operator-configuration/)
- [Materialize CRD Field
  Descriptions](/self-managed-deployments/materialize-crd-field-descriptions/)

## Cleanup

To delete the whole sample infrastructure and deployment (including the
Materialize operator and Materialize instances and data), run from the Terraform
directory:

```bash
terraform destroy
```

When prompted to proceed, type `yes` to confirm the deletion.

## See Also

- [Troubleshooting](/self-managed-deployments/troubleshooting/)
- [Security](/security/self-managed/)

<!-- mz-docs page: self-managed-deployments/installation/install-on-local-kind -->

# Install locally on kind
Deploy Self-managed Materialize to a local kind cluster.
Self-managed Materialize requires: a Kubernetes (v1.31+) cluster; PostgreSQL as
a metadata database; blob storage; and a license key.

The following tutorial uses a local [`kind`](https://kind.sigs.k8s.io/) cluster
and deploys the following components:

- Materialize Operator using Helm into your local `kind` cluster.
- MinIO object storage as the blob storage for your Materialize.
- PostgreSQL database as the metadata database for your Materialize.
- Materialize as a containerized application into your local `kind` cluster.

> **Important:** This tutorial is for local evaluation/testing purposes only.
> - The tutorial uses sample configuration files that are for evaluation/testing
>   purposes only.
> - The tutorial uses a Kubernetes metrics server with TLS disabled. In practice,
>   refer to your organization's official security practices.

## Prerequisites

### kind

Install [`kind`](https://kind.sigs.k8s.io/docs/user/quick-start/).

### Docker

Install [`Docker`](https://docs.docker.com/get-started/get-docker/).

#### Docker resource requirements

For this local deployment, you will need the following Docker resource
requirements:

- 5 CPUs
- 15GB memory

### Helm 3.2.0+

If you don't have Helm version 3.2.0+ installed, install. For details, see the
[Helm documentation](https://helm.sh/docs/intro/install/).

### `kubectl`

This tutorial uses `kubectl`. To install, refer to the [`kubectl`
documentationq](https://kubernetes.io/docs/tasks/tools/).

For help with `kubectl` commands, see [kubectl Quick
reference](https://kubernetes.io/docs/reference/kubectl/quick-reference/).

### License key

Starting in v26.0, Self-Managed Materialize requires a license key.

| License key type | Deployment type | Action |
| --- | --- | --- |
| Community | New deployments | <p>To get a license key:</p> <ul> <li>If you have a Cloud account, visit the <a href="https://console.materialize.com/license/" ><strong>License</strong> page in the Materialize Console</a>.</li> <li>If you do not have a Cloud account, visit <a href="https://materialize.com/self-managed/community-license/" >https://materialize.com/self-managed/community-license/</a>.</li> </ul> |
| Community | Existing deployments | Contact <a href="https://materialize.com/docs/support/" >Materialize support</a>. |
| Enterprise | New deployments | Visit <a href="https://materialize.com/self-managed/enterprise-license/" >https://materialize.com/self-managed/enterprise-license/</a> to purchase an Enterprise license. |
| Enterprise | Existing deployments | Contact <a href="https://materialize.com/docs/support/" >Materialize support</a>. |

## Installation

1. Start Docker if it is not already running.

   For this local deployment, you will need the following Docker resource
   requirements:

   - 5 CPUs
   - 15GB memory

1. Open a Terminal window.

1. Create a working directory and go to the directory.

   ```shell
   mkdir my-local-mz
   cd my-local-mz
   ```

1. Create a `kind` cluster.

   ```shell
   kind create cluster
   ```

1. Add labels `materialize.cloud/disk=true`, `materialize.cloud/swap=true` and
   `workload=materialize-instance` to the `kind` node (in this example, the
   `kind-control-plane` node).

   ```shell
   MYNODE=$(kubectl get nodes --no-headers | awk '{print $1}')
   kubectl label node  $MYNODE materialize.cloud/disk=true
   kubectl label node  $MYNODE materialize.cloud/swap=true
   kubectl label node  $MYNODE workload=materialize-instance
   ```

   Verify that the labels were successfully applied by running the following
   command:

   ```shell
   kubectl get nodes --show-labels
   ```

1. <a name="install-cert-manager" ></a>Install `cert-manager`. `cert-manager` is
   used for generating TLS certificates needed by the Materialize operator for
   CRD conversion webhooks if enabling CRD `v1`. To simplify future transition,
   we recommend installing it even if you are not yet enabling CRD `v1`.

   ```shell
   helm install cert-manager oci://quay.io/jetstack/charts/cert-manager \
       --version v1.19.2 \
       --namespace cert-manager \
       --create-namespace \
       --set crds.enabled=true
   ```

1. To help you get started for local evaluation/testing, Materialize provides
   some sample configuration files. Download the sample configuration files from
   the Materialize repo:

   ```shell
   mz_version=v26.43.0

   curl -o sample-values.yaml https://raw.githubusercontent.com/MaterializeInc/materialize/refs/tags/$mz_version/misc/helm-charts/operator/values.yaml
   curl -o sample-postgres.yaml https://raw.githubusercontent.com/MaterializeInc/materialize/refs/tags/$mz_version/misc/helm-charts/testing/postgres.yaml
   curl -o sample-minio.yaml https://raw.githubusercontent.com/MaterializeInc/materialize/refs/heads/main/misc/helm-charts/testing/minio.yaml
   curl -o sample-materialize.yaml https://raw.githubusercontent.com/MaterializeInc/materialize/refs/tags/$mz_version/misc/helm-charts/testing/materialize.yaml
   ```

   - `sample-values.yaml`: Used to configure the Materialize Operator.
   - `sample-postgres.yaml`: Used to configure PostgreSQL as the metadata
     database.
   - `sample-minio.yaml`: Used to configure MinIO as the blob storage.
   - `sample-materialize.yaml`: Used to configure Materialize instance.

   These configuration files are for local evaluation/testing purposes only and
   not intended for production use.

1. Add your license key:

   a. To get your license key:

      | License key type | Deployment type | Action |
      | --- | --- | --- |
      | Community | New deployments | <p>To get a license key:</p> <ul> <li>If you have a Cloud account, visit the <a href="https://console.materialize.com/license/" ><strong>License</strong> page in the Materialize Console</a>.</li> <li>If you do not have a Cloud account, visit <a href="https://materialize.com/self-managed/community-license/" >https://materialize.com/self-managed/community-license/</a>.</li> </ul> |
      | Community | Existing deployments | Contact <a href="https://materialize.com/docs/support/" >Materialize support</a>. |
      | Enterprise | New deployments | Visit <a href="https://materialize.com/self-managed/enterprise-license/" >https://materialize.com/self-managed/enterprise-license/</a> to purchase an Enterprise license. |
      | Enterprise | Existing deployments | Contact <a href="https://materialize.com/docs/support/" >Materialize support</a>. |

   b. Edit `sample-materialize.yaml` to add your license key to the
   `license_key` field in the backend secret.

   ```yaml {hl_lines="10"}
   ---
   apiVersion: v1
   kind: Secret
   metadata:
   name: materialize-backend
   namespace: materialize-environment
   stringData:
     metadata_backend_url: "postgres://materialize_user:materialize_pass@postgres.materialize.svc.cluster.local:5432/materialize_db?sslmode=disable"
     persist_backend_url: "s3://minio:minio123@bucket/12345678-1234-1234-1234-123456789012?endpoint=http%3A%2F%2Fminio.materialize.svc.cluster.local%3A9000&region=minio"
     license_key: "<enter your license key here>"
   ---
   ```

1. Install the Materialize Helm chart.

   1. Add the Materialize Helm chart repository.

      ```shell
      helm repo add materialize https://materializeinc.github.io/materialize
      ```

   1. Update the repository.

      ```shell
      helm repo update materialize
      ```

   1. Install the Materialize Operator. The operator will be installed in the
      `materialize` namespace.

      <a name="step-enable-v1"></a>

      Starting in v26.30, you can choose between CRD versions: [`v1` (which
      provides a simplified rollout behavior and is available starting in
      v26.30)](/self-managed-deployments/upgrading/adopting-the-v1-crd/) and
      `v1alpha1` (default). The following enables the use of `v1` CRD version by
      setting `operator.args.installV1CRD=true`. To use `v1` CRD requires
      `cert-manager`, installed in an [earlier step](#install-cert-manager) in this
      guide.

      ```shell {hl_lines="5"}
      helm install my-materialize-operator materialize/materialize-operator \
          --namespace=materialize --create-namespace \
          --version v26.43.0 \
          --set observability.podMetrics.enabled=true \
          --set operator.args.installV1CRD=true \
          -f sample-values.yaml
      ```

      Even if using the default `v1alpha1` CRD version, you can still enable the
      `v1` CRD to simplify the transition to `v1` in the future. However, you can
      also omit `--set operator.args.installV1CRD=true` if you prefer.

   1. Verify the installation and check the status:

      ```shell
      kubectl get all -n materialize
      ```

      Wait for the components to be ready and in the `Running` state:

      ```none
      NAME                                           READY   STATUS    RESTARTS   AGE
      pod/my-materialize-operator-6c9d55567f-ldmd7   1/1     Running   0          4s
      pod/my-materialize-operator-6c9d55567f-svwks   1/1     Running   0          4s

      NAME                              TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)    AGE
      service/my-materialize-operator   ClusterIP   10.96.231.91   <none>        8001/TCP   4s

      NAME                                      READY   UP-TO-DATE   AVAILABLE   AGE
      deployment.apps/my-materialize-operator   2/2     2            2           4s

      NAME                                                 DESIRED   CURRENT   READY   AGE
      replicaset.apps/my-materialize-operator-6c9d55567f   2         2         2       4s
      ```

      If you run into an error during deployment, refer to the
      [Troubleshooting](/installation/troubleshooting) guide.

1. Install PostgreSQL and MinIO.

    1. Use the `sample-postgres.yaml` file to install PostgreSQL as the
       metadata database:

        ```shell
        kubectl apply -f sample-postgres.yaml
        ```

    1. Use the `sample-minio.yaml` file to install MinIO as the blob storage:

        ```shell
        kubectl apply -f sample-minio.yaml
        ```

    1. Verify the installation and check the status:

       ```shell
       kubectl get all -n materialize
       ```

       Wait for the components to be ready. The `minio-setup` job creates the
       buckets and then shows `Completed`:

       ```none
       NAME                                           READY   STATUS      RESTARTS   AGE
       pod/minio-bfdd6b7c-5n6sw                       1/1     Running     0          20s
       pod/minio-setup-cmfk8                          0/1     Completed   0          20s
       pod/my-materialize-operator-6c9d55567f-g59v2   1/1     Running     0          28s
       pod/my-materialize-operator-6c9d55567f-nx9s6   1/1     Running     0          28s
       pod/postgres-979c9b755-ddb4m                   1/1     Running     0          20s

       NAME                              TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
       service/minio                     ClusterIP   10.96.27.17     <none>        9000/TCP   20s
       service/my-materialize-operator   ClusterIP   10.96.175.204   <none>        8001/TCP   28s
       service/postgres                  ClusterIP   10.96.5.180     <none>        5432/TCP   20s

       NAME                                      READY   UP-TO-DATE   AVAILABLE   AGE
       deployment.apps/minio                     1/1     1            1           20s
       deployment.apps/my-materialize-operator   2/2     2            2           28s
       deployment.apps/postgres                  1/1     1            1           20s

       NAME                                                 DESIRED   CURRENT   READY   AGE
       replicaset.apps/minio-bfdd6b7c                       1         1         1       20s
       replicaset.apps/my-materialize-operator-6c9d55567f   2         2         2       28s
       replicaset.apps/postgres-979c9b755                   1         1         1       20s

       NAME                    STATUS     COMPLETIONS   DURATION   AGE
       job.batch/minio-setup   Complete   1/1           20s        20s
       ```

1. Install the metrics service to the `kube-system` namespace.

   1. Add the metrics server Helm repository.

      ```shell
      helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/
      ```

   1. Update the repository.

      ```shell
      helm repo update metrics-server
      ```

   1. Install the metrics server to the `kube-system` namespace.

      > **Important:** This tutorial is for local evaluation/testing purposes only. For simplicity,
>       the tutorial uses a Kubernetes metrics server with TLS disabled. In practice,
>       refer to your organization's official security practices.

      ```shell
      helm install metrics-server metrics-server/metrics-server \
         --namespace kube-system \
         --set args="{--kubelet-insecure-tls,--kubelet-preferred-address-types=InternalIP\,Hostname\,ExternalIP}"
      ```

      You can verify the installation by running the following command:

      ```bash
      kubectl get pods -n kube-system -l app.kubernetes.io/instance=metrics-server
      ```

      Wait for the `metrics-server` pod to be ready and in the `Running` state:

      ```none
      NAME                             READY   STATUS    RESTARTS   AGE
      metrics-server-89dfdc559-bq59m   1/1     Running   0          2m6s
      ```

1. Install Materialize into a new `materialize-environment` namespace:

   1. If you [enabled the use of `v1` CRD](#step-enable-v1), update
      `sample-materialize.yaml` to use it.
      [`v1`](/self-managed-deployments/upgrading/adopting-the-v1-crd/) provides
      a simplified rollout behavior. In the `Materialize` resource section of
      the file (`kind: Materialize`):
      - Change the `apiVersion` from `materialize.cloud/v1alpha1` to
        `materialize.cloud/v1`.
      - Remove the `requestRollout` field, if present.

      ```none{hl_lines=2}
      ---
      apiVersion: materialize.cloud/v1     # <-- updated to use v1
      kind: Materialize
      metadata:
         name: 12345678-1234-1234-1234-123456789012
         namespace: materialize-environment
      ```

      To use the default `v1alpha1` CRD version instead, leave
      `sample-materialize.yaml` unchanged.

   1. Use the `sample-materialize.yaml` file to create the
      `materialize-environment` namespace and install Materialize:

      ```shell
      kubectl apply -f sample-materialize.yaml
      ```

   1. Verify the installation and check the status:

       > **Note:** It may take approximately 1-2 minutes for all resources to appear in the
>        namespace. Allow up to 90 seconds before verifying resource creation with
>        `kubectl get` commands.

       ```shell
       kubectl get all -n materialize-environment
       ```

       Wait for the components to be ready and in the `Running` state.

       ```none
       NAME                                             READY   STATUS    RESTARTS   AGE
       pod/mzeemp0ion69-balancerd-7c74d9775-2qrp9       1/1     Running   0          17s
       pod/mzeemp0ion69-balancerd-7c74d9775-z4n4z       1/1     Running   0          17s
       pod/mzeemp0ion69-cluster-s2-replica-s1-gen-1-0   1/1     Running   0          17s
       pod/mzeemp0ion69-cluster-u1-replica-u1-gen-1-0   1/1     Running   0          17s
       pod/mzeemp0ion69-console-85748c74cd-tfpkd        1/1     Running   0          5s
       pod/mzeemp0ion69-console-85748c74cd-wzssw        1/1     Running   0          5s
       pod/mzeemp0ion69-environmentd-1-0                1/1     Running   0          25s

       NAME                                               TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)                                        AGE
       service/mzeemp0ion69-balancerd                     ClusterIP   None           <none>        6876/TCP,6875/TCP                              17s
       service/mzeemp0ion69-cluster-s2-replica-s1-gen-1   ClusterIP   None           <none>        2100/TCP,2103/TCP,2101/TCP,2102/TCP,6878/TCP   17s
       service/mzeemp0ion69-cluster-u1-replica-u1-gen-1   ClusterIP   None           <none>        2100/TCP,2103/TCP,2101/TCP,2102/TCP,6878/TCP   17s
       service/mzeemp0ion69-console                       ClusterIP   None           <none>        8080/TCP                                       5s
       service/mzeemp0ion69-environmentd                  ClusterIP   None           <none>        6875/TCP,6876/TCP,6877/TCP,6878/TCP            17s
       service/mzeemp0ion69-environmentd-1                ClusterIP   10.96.207.11   <none>        6875/TCP,6876/TCP,6877/TCP,6878/TCP            25s
       service/mzeemp0ion69-persist-pubsub-1              ClusterIP   None           <none>        6879/TCP                                       25s

       NAME                                     READY   UP-TO-DATE   AVAILABLE   AGE
       deployment.apps/mzeemp0ion69-balancerd   2/2     2            2           17s
       deployment.apps/mzeemp0ion69-console     2/2     2            2           5s

       NAME                                               DESIRED   CURRENT   READY   AGE
       replicaset.apps/mzeemp0ion69-balancerd-7c74d9775   2         2         2       17s
       replicaset.apps/mzeemp0ion69-console-85748c74cd    2         2         2       5s

       NAME                                                        READY   AGE
       statefulset.apps/mzeemp0ion69-cluster-s2-replica-s1-gen-1   1/1     17s
       statefulset.apps/mzeemp0ion69-cluster-u1-replica-u1-gen-1   1/1     17s
       statefulset.apps/mzeemp0ion69-environmentd-1                1/1     25s
       ```

       If you run into an error during deployment, refer to the
       [Troubleshooting](/self-hosted/troubleshooting) guide.

   1. Optional. Check the CRD version being used:

      To determine which CRD version is in use, run the following command,
      replacing <instance-name> with your instance name. For the
      `sample-materialize.yaml` used in this example, the instance name is
      `12345678-1234-1234-1234-123456789012`:

      ```sh
      kubectl get materialize <instance-name> -n materialize-environment \
        -o jsonpath='{.metadata.annotations.kubectl\.kubernetes\.io/last-applied-configuration}' \
      | python3 -c 'import sys,json; print(json.load(sys.stdin)["apiVersion"])'
      ```

1. Open the Materialize Console in your browser:

   1. Find your console service name.

      ```shell
      MZ_SVC_CONSOLE=$(kubectl -n materialize-environment get svc \
        -o custom-columns="NAME:.metadata.name" --no-headers | grep console)
      echo $MZ_SVC_CONSOLE
      ```

   1. Port forward the Materialize Console service to your local machine:[^1]

      ```shell
      (
        while true; do
           kubectl port-forward svc/$MZ_SVC_CONSOLE 8080:8080 -n materialize-environment 2>&1 | tee /dev/stderr |
           grep -q "portforward.go" && echo "Restarting port forwarding due to an error." || break;
        done;
      ) &
      ```

      The command is run in background.
      <br>- To list the background jobs, use `jobs`.
      <br>- To bring back to foreground, use `fg %<job-number>`.
      <br>- To kill the background job, use `kill %<job-number>`.

   1. Open a browser and navigate to
      [http://localhost:8080](http://localhost:8080).

   [^1]: The port forwarding command uses a while loop to handle a [known
   Kubernetes issue 78446](https://github.com/kubernetes/kubernetes/issues/78446),
   where interrupted long-running requests through a standard port-forward cause
   the port forward to hang. The command automatically restarts the port forwarding
   if an error occurs, ensuring a more stable connection. It detects failures by
   monitoring for "portforward.go" error messages.

      > **Tip:** If you experience long loading screens or unresponsiveness in the Materialize
>       Console, we recommend increasing the size of the `mz_catalog_server` cluster.
>       Refer to the [Troubleshooting Console
>       Unresponsiveness](/self-managed-deployments/troubleshooting/#troubleshooting-console-unresponsiveness)
>       guide.

## Next steps

- From the Console, you can get started with the
[Quickstart](/get-started/quickstart/).

- To start ingesting your own data from an external system like Kafka, MySQL or
  PostgreSQL, see [Ingest data](/ingest-data/).

- To enable authentication and authorization, see
  [Security](/security/self-managed/).

## Clean up

To delete the whole local deployment (including Materialize instances and data):

```bash
kind delete cluster
```

## See also

- [Materialize Operator Configuration](/installation/configuration/)
- [Troubleshooting](/installation/troubleshooting/)
- [Installation](/installation/)

<!-- mz-docs page: self-managed-deployments/materialize-crd-field-descriptions -->

# Materialize CRD Field Descriptions

Reference page on Materialize CRD Fields

Select the CRD API version for your Materialize deployment:

- [v1 (Available starting v26.30+; Terraform module default starting in v4.0.0)](/self-managed-deployments/materialize-crd-field-descriptions/v1/)
- [v1alpha1 (*Helm chart default*)](/self-managed-deployments/materialize-crd-field-descriptions/v1alpha1/)

