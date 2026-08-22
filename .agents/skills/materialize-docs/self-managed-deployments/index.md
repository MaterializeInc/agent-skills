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
  environmentdImageRef: materialize/environmentd:v26.37.0
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
  environmentdImageRef: materialize/environmentd:v26.37.0
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

For a comprehensive overview of clusters in Materialize, see the [Clusters concept page](/concepts/clusters/).

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
- [Clusters concept page](/concepts/clusters/)
- [Materialize architecture overview](/concepts/)

---

## Appendix

## Table of contents

- [Appendix: Cluster sizes](./appendix-cluster-sizes/)
- [Appendix: Prepare for swap and upgrade to v26.0](./upgrade-to-swap/)

---

## Configuring System Parameters

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
  environmentdImageRef: materialize/environmentd:v26.37.0
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
  environmentdImageRef: materialize/environmentd:v26.37.0
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

Kubernetes uses the kubelet to periodically sync ConfigMap updates to mounted
volumes. By default, this sync occurs approximately every 60 seconds. This
means changes to your ConfigMap may take up to a minute to be reflected in
the running Materialize instance.

Once the ConfigMap is synced to the volume, Materialize checks for configuration
changes every second and applies them automatically.

To force an immediate sync of the ConfigMap from Kubernetes, you can update an
annotation on the Materialize resource, which triggers a pod re-reconciliation:

```shell
kubectl annotate materialize <instance-name> \
  -n materialize-environment \
  configmap-reload-trigger="$(date +%s)" \
  --overwrite
```

Alternatively, you can add the `configmap-reload-trigger` annotation to your
Materialize custom resource YAML and update it whenever you need to force a
ConfigMap reload:

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
  annotations:
    configmap-reload-trigger: "1234567890"  # Update this value to force reload
spec:
  # ... rest of spec
```

**v1:**

<p>The <code>v1</code> CRD is available starting in v26.30. It is opt-in for the Helm chart and the default for the Terraform modules starting in v4.0.0. See <a href="/self-managed-deployments/upgrading/adopting-the-v1-crd/">Adopting the v1 CRD</a> to enable it.</p>

```yaml
apiVersion: materialize.cloud/v1
kind: Materialize
metadata:
  name: 12345678-1234-1234-1234-123456789012
  namespace: materialize-environment
  annotations:
    configmap-reload-trigger: "1234567890"  # Update this value to force reload
spec:
  # ... rest of spec
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

- [Materialize Operator Configuration](/installation/configuration/)
- [Materialize CRD Field Descriptions](/installation/appendix-materialize-crd-field-descriptions/)
- [Troubleshooting](/installation/troubleshooting/)

---

## Deployment guidelines

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

## FAQ

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

---

## Installation

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

---

## Materialize CRD Field Descriptions

Select the CRD API version for your Materialize deployment:

- [v1 (Available starting v26.30+; Terraform module default starting in v4.0.0)](/self-managed-deployments/materialize-crd-field-descriptions/v1/)
- [v1alpha1 (*Helm chart default*)](/self-managed-deployments/materialize-crd-field-descriptions/v1alpha1/)

---

## Materialize Operator Configuration

## Configure the Materialize operator

To configure the Materialize operator, you can:

- Use a configuration YAML file (e.g., `values.yaml`) that specifies the
  configuration values and then install the chart with the `-f` flag:

  ```shell
  # Assumes you have added the Materialize operator Helm chart repository
  helm install my-materialize-operator materialize/materialize-operator \
     -f /path/to/your/config/values.yaml
  ```

- Specify each parameter using the `--set key=value[,key=value]` argument to
  `helm install`. For example:

  ```shell
  # Assumes you have added the Materialize operator Helm chart repository
  helm install my-materialize-operator materialize/materialize-operator  \
    --set observability.podMetrics.enabled=true
  ```

<table>
<thead>
<tr>
<th>Parameter</th>
<th>Default</th>

</tr>
</thead>
<tbody>

<tr>
<td><a href='#balancerdaffinity'><code>balancerd.affinity</code></a></td>
<td>

</td>
</tr>

<tr>
<td><a href='#balancerddefaultresourceslimits'><code>balancerd.defaultResources.limits</code></a></td>
<td>
<code>{&quot;memory&quot;:&quot;256Mi&quot;}</code>
</td>
</tr>

<tr>
<td><a href='#balancerddefaultresourcesrequests'><code>balancerd.defaultResources.requests</code></a></td>
<td>
<code>{&quot;cpu&quot;:&quot;500m&quot;,&quot;memory&quot;:&quot;256Mi&quot;}</code>
</td>
</tr>

<tr>
<td><a href='#balancerdenabled'><code>balancerd.enabled</code></a></td>
<td>
<code>true</code>
</td>
</tr>

<tr>
<td><a href='#balancerdnodeselector'><code>balancerd.nodeSelector</code></a></td>
<td>

</td>
</tr>

<tr>
<td><a href='#balancerdtolerations'><code>balancerd.tolerations</code></a></td>
<td>

</td>
</tr>

<tr>
<td><a href='#clusterdaffinity'><code>clusterd.affinity</code></a></td>
<td>

</td>
</tr>

<tr>
<td><a href='#clusterdnodeselector'><code>clusterd.nodeSelector</code></a></td>
<td>

</td>
</tr>

<tr>
<td><a href='#clusterdscratchfsnodeselector'><code>clusterd.scratchfsNodeSelector</code></a></td>
<td>

</td>
</tr>

<tr>
<td><a href='#clusterdswapnodeselector'><code>clusterd.swapNodeSelector</code></a></td>
<td>

</td>
</tr>

<tr>
<td><a href='#clusterdtolerations'><code>clusterd.tolerations</code></a></td>
<td>

</td>
</tr>

<tr>
<td><a href='#consoleaffinity'><code>console.affinity</code></a></td>
<td>

</td>
</tr>

<tr>
<td><a href='#consoledefaultresourceslimits'><code>console.defaultResources.limits</code></a></td>
<td>
<code>{&quot;memory&quot;:&quot;256Mi&quot;}</code>
</td>
</tr>

<tr>
<td><a href='#consoledefaultresourcesrequests'><code>console.defaultResources.requests</code></a></td>
<td>
<code>{&quot;cpu&quot;:&quot;500m&quot;,&quot;memory&quot;:&quot;256Mi&quot;}</code>
</td>
</tr>

<tr>
<td><a href='#consoleenabled'><code>console.enabled</code></a></td>
<td>
<code>true</code>
</td>
</tr>

<tr>
<td><a href='#consoleimagetagmapoverride'><code>console.imageTagMapOverride</code></a></td>
<td>
<code>{}</code>
</td>
</tr>

<tr>
<td><a href='#consolenodeselector'><code>console.nodeSelector</code></a></td>
<td>

</td>
</tr>

<tr>
<td><a href='#consoletolerations'><code>console.tolerations</code></a></td>
<td>

</td>
</tr>

<tr>
<td><a href='#environmentdaffinity'><code>environmentd.affinity</code></a></td>
<td>

</td>
</tr>

<tr>
<td><a href='#environmentddefaultresourceslimits'><code>environmentd.defaultResources.limits</code></a></td>
<td>
<code>{&quot;memory&quot;:&quot;4Gi&quot;}</code>
</td>
</tr>

<tr>
<td><a href='#environmentddefaultresourcesrequests'><code>environmentd.defaultResources.requests</code></a></td>
<td>
<code>{&quot;cpu&quot;:&quot;1&quot;,&quot;memory&quot;:&quot;4095Mi&quot;}</code>
</td>
</tr>

<tr>
<td><a href='#environmentdnodeselector'><code>environmentd.nodeSelector</code></a></td>
<td>

</td>
</tr>

<tr>
<td><a href='#environmentdtolerations'><code>environmentd.tolerations</code></a></td>
<td>

</td>
</tr>

<tr>
<td><a href='#networkpoliciesegresscidrs'><code>networkPolicies.egress.cidrs</code></a></td>
<td>
<code>[&quot;0.0.0.0/0&quot;]</code>
</td>
</tr>

<tr>
<td><a href='#networkpoliciesegressenabled'><code>networkPolicies.egress.enabled</code></a></td>
<td>
<code>false</code>
</td>
</tr>

<tr>
<td><a href='#networkpoliciesenabled'><code>networkPolicies.enabled</code></a></td>
<td>
<code>false</code>
</td>
</tr>

<tr>
<td><a href='#networkpoliciesingresscidrs'><code>networkPolicies.ingress.cidrs</code></a></td>
<td>
<code>[&quot;0.0.0.0/0&quot;]</code>
</td>
</tr>

<tr>
<td><a href='#networkpoliciesingressenabled'><code>networkPolicies.ingress.enabled</code></a></td>
<td>
<code>false</code>
</td>
</tr>

<tr>
<td><a href='#networkpoliciesinternalenabled'><code>networkPolicies.internal.enabled</code></a></td>
<td>
<code>false</code>
</td>
</tr>

<tr>
<td><a href='#observabilityenabled'><code>observability.enabled</code></a></td>
<td>
<code>true</code>
</td>
</tr>

<tr>
<td><a href='#observabilitypodmetricsenabled'><code>observability.podMetrics.enabled</code></a></td>
<td>
<code>false</code>
</td>
</tr>

<tr>
<td><a href='#observabilityprometheusscrapeannotationsenabled'><code>observability.prometheus.scrapeAnnotations.enabled</code></a></td>
<td>
<code>true</code>
</td>
</tr>

<tr>
<td><a href='#operatoradditionalmaterializecrdcolumns'><code>operator.additionalMaterializeCRDColumns</code></a></td>
<td>
<code>{}</code>
</td>
</tr>

<tr>
<td><a href='#operatoraffinity'><code>operator.affinity</code></a></td>
<td>

</td>
</tr>

<tr>
<td><a href='#operatorargsenableinternalstatementlogging'><code>operator.args.enableInternalStatementLogging</code></a></td>
<td>
<code>true</code>
</td>
</tr>

<tr>
<td><a href='#operatorargsenablelicensekeychecks'><code>operator.args.enableLicenseKeyChecks</code></a></td>
<td>
<code>false</code>
</td>
</tr>

<tr>
<td><a href='#operatorargsinstallv1crd'><code>operator.args.installV1CRD</code></a></td>
<td>
<code>false</code>
</td>
</tr>

<tr>
<td><a href='#operatorargsstartuplogfilter'><code>operator.args.startupLogFilter</code></a></td>
<td>
<code>&quot;INFO,mz_orchestratord=TRACE&quot;</code>
</td>
</tr>

<tr>
<td><a href='#operatorargswebhookcertreloadinterval'><code>operator.args.webhookCertReloadInterval</code></a></td>
<td>
<code>nil</code>
</td>
</tr>

<tr>
<td><a href='#operatorcertificatecaduration'><code>operator.certificate.caDuration</code></a></td>
<td>
<code>&quot;87600h&quot;</code>
</td>
</tr>

<tr>
<td><a href='#operatorcertificatecarenewbefore'><code>operator.certificate.caRenewBefore</code></a></td>
<td>
<code>&quot;8760h&quot;</code>
</td>
</tr>

<tr>
<td><a href='#operatorcertificatesecretname'><code>operator.certificate.secretName</code></a></td>
<td>
<code>nil</code>
</td>
</tr>

<tr>
<td><a href='#operatorcertificatesource'><code>operator.certificate.source</code></a></td>
<td>
<code>&quot;cert-manager&quot;</code>
</td>
</tr>

<tr>
<td><a href='#operatorcloudproviderprovidersawsaccountid'><code>operator.cloudProvider.providers.aws.accountID</code></a></td>
<td>
<code>&quot;&quot;</code>
</td>
</tr>

<tr>
<td><a href='#operatorcloudproviderprovidersawsenabled'><code>operator.cloudProvider.providers.aws.enabled</code></a></td>
<td>
<code>false</code>
</td>
</tr>

<tr>
<td><a href='#operatorcloudproviderprovidersawsiamrolesconnection'><code>operator.cloudProvider.providers.aws.iam.roles.connection</code></a></td>
<td>
<code>&quot;&quot;</code>
</td>
</tr>

<tr>
<td><a href='#operatorcloudproviderprovidersawsiamrolesenvironment'><code>operator.cloudProvider.providers.aws.iam.roles.environment</code></a></td>
<td>
<code>&quot;&quot;</code>
</td>
</tr>

<tr>
<td><a href='#operatorcloudproviderprovidersgcp'><code>operator.cloudProvider.providers.gcp</code></a></td>
<td>
<code>{&quot;enabled&quot;:false,&quot;nodeUpgradeRolloutTrigger&quot;:{&quot;clusterLocation&quot;:&quot;&quot;,&quot;clusterName&quot;:&quot;&quot;,&quot;enabled&quot;:false,&quot;notificationSubscription&quot;:&quot;&quot;,&quot;watchedNodePools&quot;:[]}}</code>
</td>
</tr>

<tr>
<td><a href='#operatorcloudproviderprovidersgcpnodeupgraderollouttriggerclusterlocation'><code>operator.cloudProvider.providers.gcp.nodeUpgradeRolloutTrigger.clusterLocation</code></a></td>
<td>
<code>&quot;&quot;</code>
</td>
</tr>

<tr>
<td><a href='#operatorcloudproviderprovidersgcpnodeupgraderollouttriggerclustername'><code>operator.cloudProvider.providers.gcp.nodeUpgradeRolloutTrigger.clusterName</code></a></td>
<td>
<code>&quot;&quot;</code>
</td>
</tr>

<tr>
<td><a href='#operatorcloudproviderprovidersgcpnodeupgraderollouttriggernotificationsubscription'><code>operator.cloudProvider.providers.gcp.nodeUpgradeRolloutTrigger.notificationSubscription</code></a></td>
<td>
<code>&quot;&quot;</code>
</td>
</tr>

<tr>
<td><a href='#operatorcloudproviderprovidersgcpnodeupgraderollouttriggerwatchednodepools'><code>operator.cloudProvider.providers.gcp.nodeUpgradeRolloutTrigger.watchedNodePools</code></a></td>
<td>
<code>[]</code>
</td>
</tr>

<tr>
<td><a href='#operatorcloudproviderregion'><code>operator.cloudProvider.region</code></a></td>
<td>
<code>&quot;kind&quot;</code>
</td>
</tr>

<tr>
<td><a href='#operatorcloudprovidertype'><code>operator.cloudProvider.type</code></a></td>
<td>
<code>&quot;local&quot;</code>
</td>
</tr>

<tr>
<td><a href='#operatorclustersdefaultreplicationfactoranalytics'><code>operator.clusters.defaultReplicationFactor.analytics</code></a></td>
<td>
<code>0</code>
</td>
</tr>

<tr>
<td><a href='#operatorclustersdefaultreplicationfactorprobe'><code>operator.clusters.defaultReplicationFactor.probe</code></a></td>
<td>
<code>0</code>
</td>
</tr>

<tr>
<td><a href='#operatorclustersdefaultreplicationfactorsupport'><code>operator.clusters.defaultReplicationFactor.support</code></a></td>
<td>
<code>0</code>
</td>
</tr>

<tr>
<td><a href='#operatorclustersdefaultreplicationfactorsystem'><code>operator.clusters.defaultReplicationFactor.system</code></a></td>
<td>
<code>0</code>
</td>
</tr>

<tr>
<td><a href='#operatorclustersdefaultsizesanalytics'><code>operator.clusters.defaultSizes.analytics</code></a></td>
<td>
<code>&quot;25cc&quot;</code>
</td>
</tr>

<tr>
<td><a href='#operatorclustersdefaultsizescatalogserver'><code>operator.clusters.defaultSizes.catalogServer</code></a></td>
<td>
<code>&quot;25cc&quot;</code>
</td>
</tr>

<tr>
<td><a href='#operatorclustersdefaultsizesdefault'><code>operator.clusters.defaultSizes.default</code></a></td>
<td>
<code>&quot;25cc&quot;</code>
</td>
</tr>

<tr>
<td><a href='#operatorclustersdefaultsizesprobe'><code>operator.clusters.defaultSizes.probe</code></a></td>
<td>
<code>&quot;mz_probe&quot;</code>
</td>
</tr>

<tr>
<td><a href='#operatorclustersdefaultsizessupport'><code>operator.clusters.defaultSizes.support</code></a></td>
<td>
<code>&quot;25cc&quot;</code>
</td>
</tr>

<tr>
<td><a href='#operatorclustersdefaultsizessystem'><code>operator.clusters.defaultSizes.system</code></a></td>
<td>
<code>&quot;25cc&quot;</code>
</td>
</tr>

<tr>
<td><a href='#operatorclustersswap_enabled'><code>operator.clusters.swap_enabled</code></a></td>
<td>
<code>true</code>
</td>
</tr>

<tr>
<td><a href='#operatorimagepullpolicy'><code>operator.image.pullPolicy</code></a></td>
<td>
<code>&quot;IfNotPresent&quot;</code>
</td>
</tr>

<tr>
<td><a href='#operatorimagerepository'><code>operator.image.repository</code></a></td>
<td>
<code>&quot;materialize/orchestratord&quot;</code>
</td>
</tr>

<tr>
<td><a href='#operatorimagetag'><code>operator.image.tag</code></a></td>
<td>
<code>&quot;v26.38.1&quot;</code>
</td>
</tr>

<tr>
<td><a href='#operatornodeselector'><code>operator.nodeSelector</code></a></td>
<td>

</td>
</tr>

<tr>
<td><a href='#operatorpoddisruptionbudgetenabled'><code>operator.podDisruptionBudget.enabled</code></a></td>
<td>
<code>true</code>
</td>
</tr>

<tr>
<td><a href='#operatorpoddisruptionbudgetmaxunavailable'><code>operator.podDisruptionBudget.maxUnavailable</code></a></td>
<td>
<code>1</code>
</td>
</tr>

<tr>
<td><a href='#operatorreplicas'><code>operator.replicas</code></a></td>
<td>
<code>2</code>
</td>
</tr>

<tr>
<td><a href='#operatorresourceslimits'><code>operator.resources.limits</code></a></td>
<td>
<code>{&quot;memory&quot;:&quot;512Mi&quot;}</code>
</td>
</tr>

<tr>
<td><a href='#operatorresourcesrequests'><code>operator.resources.requests</code></a></td>
<td>
<code>{&quot;cpu&quot;:&quot;100m&quot;,&quot;memory&quot;:&quot;512Mi&quot;}</code>
</td>
</tr>

<tr>
<td><a href='#operatorsecretscontroller'><code>operator.secretsController</code></a></td>
<td>
<code>&quot;kubernetes&quot;</code>
</td>
</tr>

<tr>
<td><a href='#operatortolerations'><code>operator.tolerations</code></a></td>
<td>

</td>
</tr>

<tr>
<td><a href='#rbaccreate'><code>rbac.create</code></a></td>
<td>
<code>true</code>
</td>
</tr>

<tr>
<td><a href='#schedulername'><code>schedulerName</code></a></td>
<td>
<code>nil</code>
</td>
</tr>

<tr>
<td><a href='#serviceaccountannotations'><code>serviceAccount.annotations</code></a></td>
<td>
<code>{}</code>
</td>
</tr>

<tr>
<td><a href='#serviceaccountcreate'><code>serviceAccount.create</code></a></td>
<td>
<code>true</code>
</td>
</tr>

<tr>
<td><a href='#serviceaccountname'><code>serviceAccount.name</code></a></td>
<td>
<code>&quot;orchestratord&quot;</code>
</td>
</tr>

<tr>
<td><a href='#storagestorageclassallowvolumeexpansion'><code>storage.storageClass.allowVolumeExpansion</code></a></td>
<td>
<code>false</code>
</td>
</tr>

<tr>
<td><a href='#storagestorageclasscreate'><code>storage.storageClass.create</code></a></td>
<td>
<code>false</code>
</td>
</tr>

<tr>
<td><a href='#storagestorageclassname'><code>storage.storageClass.name</code></a></td>
<td>
<code>&quot;&quot;</code>
</td>
</tr>

<tr>
<td><a href='#storagestorageclassparameters'><code>storage.storageClass.parameters</code></a></td>
<td>
<code>{&quot;fsType&quot;:&quot;ext4&quot;,&quot;storage&quot;:&quot;lvm&quot;,&quot;volgroup&quot;:&quot;instance-store-vg&quot;}</code>
</td>
</tr>

<tr>
<td><a href='#storagestorageclassprovisioner'><code>storage.storageClass.provisioner</code></a></td>
<td>
<code>&quot;&quot;</code>
</td>
</tr>

<tr>
<td><a href='#storagestorageclassreclaimpolicy'><code>storage.storageClass.reclaimPolicy</code></a></td>
<td>
<code>&quot;Delete&quot;</code>
</td>
</tr>

<tr>
<td><a href='#storagestorageclassvolumebindingmode'><code>storage.storageClass.volumeBindingMode</code></a></td>
<td>
<code>&quot;WaitForFirstConsumer&quot;</code>
</td>
</tr>

<tr>
<td><a href='#telemetryenabled'><code>telemetry.enabled</code></a></td>
<td>
<code>true</code>
</td>
</tr>

<tr>
<td><a href='#telemetrysegmentapikey'><code>telemetry.segmentApiKey</code></a></td>
<td>
<code>&quot;hMWi3sZ17KFMjn2sPWo9UJGpOQqiba4A&quot;</code>
</td>
</tr>

<tr>
<td><a href='#telemetrysegmentclientside'><code>telemetry.segmentClientSide</code></a></td>
<td>
<code>true</code>
</td>
</tr>

<tr>
<td><a href='#tlsdefaultcertificatespecs'><code>tls.defaultCertificateSpecs</code></a></td>
<td>
<code>{}</code>
</td>
</tr>

</tbody>
</table>

## Parameters

### `balancerd` parameters

#### balancerd.affinity

**Default**: 

Affinity to use for balancerd pods spawned by the operator

#### balancerd.defaultResources.limits

**Default**: <code>{&quot;memory&quot;:&quot;256Mi&quot;}</code>

Default resource limits for balancerd&rsquo;s CPU and memory if not set in the Materialize CR

#### balancerd.defaultResources.requests

**Default**: <code>{&quot;cpu&quot;:&quot;500m&quot;,&quot;memory&quot;:&quot;256Mi&quot;}</code>

Default resources requested for balancerd&rsquo;s CPU and memory if not set in the Materialize CR

#### balancerd.enabled

**Default**: <code>true</code>

Flag to indicate whether to create balancerd pods for the environments

#### balancerd.nodeSelector

**Default**: 

Node selector to use for balancerd pods spawned by the operator

#### balancerd.tolerations

**Default**: 

Tolerations to use for balancerd pods spawned by the operator

### `clusterd` parameters

#### clusterd.affinity

**Default**: 

Affinity to use for clusterd pods spawned by the operator

#### clusterd.nodeSelector

**Default**: 

Node selector to use for all clusterd pods spawned by the operator

#### clusterd.scratchfsNodeSelector

**Default**: 

Additional node selector to use for clusterd pods when using an LVM scratch disk. This will be merged with the values in <code>nodeSelector</code>.

#### clusterd.swapNodeSelector

**Default**: 

Additional node selector to use for clusterd pods when using swap. This will be merged with the values in <code>nodeSelector</code>.

#### clusterd.tolerations

**Default**: 

Tolerations to use for clusterd pods spawned by the operator

### `console` parameters

#### console.affinity

**Default**: 

Affinity to use for console pods spawned by the operator

#### console.defaultResources.limits

**Default**: <code>{&quot;memory&quot;:&quot;256Mi&quot;}</code>

Default resource limits for the console&rsquo;s CPU and memory if not set in the Materialize CR

#### console.defaultResources.requests

**Default**: <code>{&quot;cpu&quot;:&quot;500m&quot;,&quot;memory&quot;:&quot;256Mi&quot;}</code>

Default resources requested for the console&rsquo;s CPU and memory if not set in the Materialize CR

#### console.enabled

**Default**: <code>true</code>

Flag to indicate whether to create console pods for the environments

#### console.imageTagMapOverride

**Default**: <code>{}</code>

Override the mapping of environmentd versions to console versions

#### console.nodeSelector

**Default**: 

Node selector to use for console pods spawned by the operator

#### console.tolerations

**Default**: 

Tolerations to use for console pods spawned by the operator

### `environmentd` parameters

#### environmentd.affinity

**Default**: 

Affinity to use for environmentd pods spawned by the operator

#### environmentd.defaultResources.limits

**Default**: <code>{&quot;memory&quot;:&quot;4Gi&quot;}</code>

Default resource limits for environmentd&rsquo;s CPU and memory if not set in the Materialize CR

#### environmentd.defaultResources.requests

**Default**: <code>{&quot;cpu&quot;:&quot;1&quot;,&quot;memory&quot;:&quot;4095Mi&quot;}</code>

Default resources requested for environmentd&rsquo;s CPU and memory if not set in the Materialize CR

#### environmentd.nodeSelector

**Default**: 

Node selector to use for environmentd pods spawned by the operator

#### environmentd.tolerations

**Default**: 

Tolerations to use for environmentd pods spawned by the operator

### `networkPolicies` parameters

#### networkPolicies.egress.cidrs

**Default**: <code>[&quot;0.0.0.0/0&quot;]</code>

CIDR blocks to allow egress to

#### networkPolicies.egress.enabled

**Default**: <code>false</code>

Whether to enable egress network policies to sources and sinks

#### networkPolicies.enabled

**Default**: <code>false</code>

Whether to enable network policies for securing communication between pods

#### networkPolicies.ingress.cidrs

**Default**: <code>[&quot;0.0.0.0/0&quot;]</code>

CIDR blocks to allow ingress from

#### networkPolicies.ingress.enabled

**Default**: <code>false</code>

Whether to enable ingress network policies to the SQL and HTTP interfaces on environmentd and balancerd

#### networkPolicies.internal.enabled

**Default**: <code>false</code>

Whether to enable network policies for internal communication between Materialize pods

### `observability` parameters

#### observability.enabled

**Default**: <code>true</code>

Whether to enable observability features

#### observability.podMetrics.enabled

**Default**: <code>false</code>

Whether to enable the pod metrics scraper which populates the Environment Overview Monitoring tab in the web console (requires metrics-server to be installed)

#### observability.prometheus.scrapeAnnotations.enabled

**Default**: <code>true</code>

Whether to annotate pods with common keys used for prometheus scraping.

### `operator` parameters

#### operator.additionalMaterializeCRDColumns

**Default**: <code>{}</code>

Additional columns to display when printing the Materialize CRD in table format.

#### operator.affinity

**Default**: 

Affinity to use for the operator pod

#### operator.args.enableInternalStatementLogging

**Default**: <code>true</code>

#### operator.args.enableLicenseKeyChecks

**Default**: <code>false</code>

#### operator.args.installV1CRD

**Default**: <code>false</code>

Whether to install the v1 version of the Materialize CRD and the conversion webhook that converts between v1 and v1alpha1. When false, only the v1alpha1 CRD version is installed and no webhook serving certificate or service is created.

#### operator.args.startupLogFilter

**Default**: <code>&quot;INFO,mz_orchestratord=TRACE&quot;</code>

Log filtering settings for startup logs

#### operator.args.webhookCertReloadInterval

**Default**: <code>nil</code>

How often orchestratord reloads its webhook TLS certificate from disk and, when the CA changes, refreshes the conversion webhook&rsquo;s CA bundle. Must be shorter than the certificate&rsquo;s lifetime. Accepts a humantime duration (e.g. &ldquo;1h&rdquo;, &ldquo;30m&rdquo;). Leave null to use the binary default. Only used if <code>installV1CRD</code> is true.

#### operator.certificate.caDuration

**Default**: <code>&quot;87600h&quot;</code>

Lifetime of the root CA that signs the webhook serving certificate, when <code>source</code> is &ldquo;cert-manager&rdquo;. The serving certificate is signed by this CA, so the CA outlives individual serving-certificate rotations.

#### operator.certificate.caRenewBefore

**Default**: <code>&quot;8760h&quot;</code>

How long before the root CA expires to renew it. Must be less than <code>caDuration</code>.

#### operator.certificate.secretName

**Default**: <code>nil</code>

Name of a secret in the operator&rsquo;s namespace containing ca.crt, tls.crt, and tls.key entries. Only used if <code>source</code> is &ldquo;secret&rdquo;.

#### operator.certificate.source

**Default**: <code>&quot;cert-manager&quot;</code>

Where to obtain the certificate for orchestratord. Valid values are &lsquo;cert-manager&rsquo; and &lsquo;secret&rsquo;. Only used if <code>operator.args.installV1CRD</code> is true.

#### operator.cloudProvider.providers.aws.accountID

**Default**: <code>&quot;&quot;</code>

When using AWS, accountID is required

#### operator.cloudProvider.providers.aws.enabled

**Default**: <code>false</code>

#### operator.cloudProvider.providers.aws.iam.roles.connection

**Default**: <code>&quot;&quot;</code>

ARN for CREATE CONNECTION feature

#### operator.cloudProvider.providers.aws.iam.roles.environment

**Default**: <code>&quot;&quot;</code>

ARN of the IAM role for environmentd

#### operator.cloudProvider.providers.gcp

**Default**: <code>{&quot;enabled&quot;:false,&quot;nodeUpgradeRolloutTrigger&quot;:{&quot;clusterLocation&quot;:&quot;&quot;,&quot;clusterName&quot;:&quot;&quot;,&quot;enabled&quot;:false,&quot;notificationSubscription&quot;:&quot;&quot;,&quot;watchedNodePools&quot;:[]}}</code>

GCP Configuration

#### operator.cloudProvider.providers.gcp.nodeUpgradeRolloutTrigger.clusterLocation

**Default**: <code>&quot;&quot;</code>

The location (region or zone) of the GKE cluster.

#### operator.cloudProvider.providers.gcp.nodeUpgradeRolloutTrigger.clusterName

**Default**: <code>&quot;&quot;</code>

The name of the GKE cluster.

#### operator.cloudProvider.providers.gcp.nodeUpgradeRolloutTrigger.notificationSubscription

**Default**: <code>&quot;&quot;</code>

The Pub/Sub subscription receiving GKE cluster notifications for this cluster, in <code>projects/{project}/subscriptions/{subscription}</code> form. The cluster must be configured to publish upgrade notifications to the corresponding topic, and the operator&rsquo;s service account must be able to subscribe to it and to read the cluster&rsquo;s node pools.

#### operator.cloudProvider.providers.gcp.nodeUpgradeRolloutTrigger.watchedNodePools

**Default**: <code>[]</code>

The node pools to watch. An empty list watches all node pools.

#### operator.cloudProvider.region

**Default**: <code>&quot;kind&quot;</code>

Common cloud provider settings

#### operator.cloudProvider.type

**Default**: <code>&quot;local&quot;</code>

Specifies cloud provider. Valid values are &lsquo;aws&rsquo;, &lsquo;gcp&rsquo;, &lsquo;azure&rsquo; , &lsquo;generic&rsquo;, or &rsquo;local&rsquo;

#### operator.clusters.defaultReplicationFactor.analytics

**Default**: <code>0</code>

#### operator.clusters.defaultReplicationFactor.probe

**Default**: <code>0</code>

#### operator.clusters.defaultReplicationFactor.support

**Default**: <code>0</code>

#### operator.clusters.defaultReplicationFactor.system

**Default**: <code>0</code>

#### operator.clusters.defaultSizes.analytics

**Default**: <code>&quot;25cc&quot;</code>

#### operator.clusters.defaultSizes.catalogServer

**Default**: <code>&quot;25cc&quot;</code>

#### operator.clusters.defaultSizes.default

**Default**: <code>&quot;25cc&quot;</code>

#### operator.clusters.defaultSizes.probe

**Default**: <code>&quot;mz_probe&quot;</code>

#### operator.clusters.defaultSizes.support

**Default**: <code>&quot;25cc&quot;</code>

#### operator.clusters.defaultSizes.system

**Default**: <code>&quot;25cc&quot;</code>

#### operator.clusters.swap_enabled

**Default**: <code>true</code>

Configure sizes such that the pod QoS class is not Guaranteed, as is required for swap to be enabled. Disk doesn&rsquo;t make much sense with swap, as swap performs better than lgalloc, so it also gets disabled.

#### operator.image.pullPolicy

**Default**: <code>&quot;IfNotPresent&quot;</code>

Policy for pulling the image: &ldquo;IfNotPresent&rdquo; avoids unnecessary re-pulling of images

#### operator.image.repository

**Default**: <code>&quot;materialize/orchestratord&quot;</code>

The Docker repository for the operator image

#### operator.image.tag

**Default**: <code>&quot;v26.38.1&quot;</code>

The tag/version of the operator image to be used

#### operator.nodeSelector

**Default**: 

Node selector to use for the operator pod

#### operator.podDisruptionBudget.enabled

**Default**: <code>true</code>

Whether to create a PodDisruptionBudget for the operator. Only created when <code>replicas</code> is greater than 1, since a budget over a single replica either blocks node drains or protects nothing.

#### operator.podDisruptionBudget.maxUnavailable

**Default**: <code>1</code>

Maximum number of operator pods that may be unavailable at once during voluntary disruptions. Expressed as a maximum rather than a minimum so that node drains are never blocked outright, they are only serialized.

#### operator.replicas

**Default**: <code>2</code>

Number of operator replicas. The operator uses leader election so that only one replica reconciles at a time. Running more than one replica avoids downtime of the CRD conversion webhook during rollouts and node drains.

#### operator.resources.limits

**Default**: <code>{&quot;memory&quot;:&quot;512Mi&quot;}</code>

Resource limits for the operator&rsquo;s CPU and memory

#### operator.resources.requests

**Default**: <code>{&quot;cpu&quot;:&quot;100m&quot;,&quot;memory&quot;:&quot;512Mi&quot;}</code>

Resources requested by the operator for CPU and memory

#### operator.secretsController

**Default**: <code>&quot;kubernetes&quot;</code>

Which secrets controller to use for storing secrets. Valid values are &lsquo;kubernetes&rsquo; and &lsquo;aws-secrets-manager&rsquo;. Setting &lsquo;aws-secrets-manager&rsquo; requires a configured AWS cloud provider and IAM role for the environment with Secrets Manager permissions.

#### operator.tolerations

**Default**: 

Tolerations to use for the operator pod

### `rbac` parameters

#### rbac.create

**Default**: <code>true</code>

Whether to create necessary RBAC roles and bindings

### `schedulerName` parameters

#### schedulerName

**Default**: <code>nil</code>

Optionally use a non-default kubernetes scheduler.

### `serviceAccount` parameters

#### serviceAccount.annotations

**Default**: <code>{}</code>

Annotations to add to the service account, e.g. <code>iam.gke.io/gcp-service-account</code> to link it to a GCP service account via workload identity.

#### serviceAccount.create

**Default**: <code>true</code>

Whether to create a new service account for the operator

#### serviceAccount.name

**Default**: <code>&quot;orchestratord&quot;</code>

The name of the service account to be created

### `storage` parameters

#### storage.storageClass.allowVolumeExpansion

**Default**: <code>false</code>

#### storage.storageClass.create

**Default**: <code>false</code>

Set to false to use an existing StorageClass instead. Refer to the <a href="https://kubernetes.io/docs/concepts/storage/storage-classes/" >Kubernetes StorageClass documentation</a>

#### storage.storageClass.name

**Default**: <code>&quot;&quot;</code>

Name of the StorageClass to create/use: eg &ldquo;openebs-lvm-instance-store-ext4&rdquo;

#### storage.storageClass.parameters

**Default**: <code>{&quot;fsType&quot;:&quot;ext4&quot;,&quot;storage&quot;:&quot;lvm&quot;,&quot;volgroup&quot;:&quot;instance-store-vg&quot;}</code>

Parameters for the CSI driver

#### storage.storageClass.provisioner

**Default**: <code>&quot;&quot;</code>

CSI driver to use, eg &ldquo;local.csi.openebs.io&rdquo;

#### storage.storageClass.reclaimPolicy

**Default**: <code>&quot;Delete&quot;</code>

#### storage.storageClass.volumeBindingMode

**Default**: <code>&quot;WaitForFirstConsumer&quot;</code>

### `telemetry` parameters

#### telemetry.enabled

**Default**: <code>true</code>

#### telemetry.segmentApiKey

**Default**: <code>&quot;hMWi3sZ17KFMjn2sPWo9UJGpOQqiba4A&quot;</code>

#### telemetry.segmentClientSide

**Default**: <code>true</code>

### `tls` parameters

#### tls.defaultCertificateSpecs

**Default**: <code>{}</code>

## See also

- [Installation](/installation/)
- [Troubleshooting](/installation/troubleshooting/)

---

## Self-managed release versions

## V26 releases

| Materialize Operator | orchestratord version | environmentd version | Release date | Notes |
| --- | --- | --- | --- | --- |
| v26.38 | v26.38 | v26.38 | 2026-08-20 | See <a href="/releases/#v26380" >v26.38 release notes</a> |
| v26.37 | v26.37 | v26.37 | 2026-08-13 | See <a href="/releases/#v26370" >v26.37 release notes</a> |
| v26.36 | v26.36 | v26.36 | 2026-08-07 | See <a href="/releases/#v26360" >v26.36 release notes</a> |
| v26.35 | v26.35 | v26.35 | 2026-07-30 | See <a href="/releases/#v26350" >v26.35 release notes</a> |
| v26.34.1 | v26.34.1 | v26.34.1 | 2026-07-24 | See <a href="/releases/#v26341" >v26.34.1 release notes</a> |
| v26.34 | v26.34 | v26.34 | 2026-07-21 | See <a href="/releases/#v26340" >v26.34 release notes</a> |
| v26.33 | v26.33 | v26.33 | 2026-07-17 | See <a href="/releases/#v26330" >v26.33 release notes</a> |
| v26.32 | v26.32 | v26.32 | 2026-07-10 | See <a href="/releases/#v26320" >v26.32 release notes</a> |
| v26.31.2 | v26.31.2 | v26.31.2 | 2026-07-08 | See <a href="/releases/#v26312" >v26.31.2 release notes</a> |
| v26.31 | v26.31 | v26.31 | 2026-07-03 | See <a href="/releases/#v26310" >v26.31 release notes</a> |
| v26.30.1 | v26.30.1 | v26.30.1 | 2026-06-26 | See <a href="/releases/#v26301" >v26.30.1 release notes</a> |
| v26.29 | v26.29 | v26.29 | 2026-06-19 | See <a href="/releases/#v26290" >v26.29 release notes</a> |
| v26.28 | v26.28 | v26.28 | 2026-06-12 | See <a href="/releases/#v26280" >v26.28 release notes</a> |
| v26.27 | v26.27 | v26.27 | 2026-06-05 | See <a href="/releases/#v26270" >v26.27 release notes</a> |
| v26.26 | v26.26 | v26.26 | 2026-05-29 | See <a href="/releases/#v26260" >v26.26 release notes</a> |
| v26.24.3 | v26.24.3 | v26.24.3 | 2026-05-20 | See <a href="/releases/#v26243" >v26.24.3 release notes</a> |
| v26.24.2 | v26.24.2 | v26.24.2 | 2026-05-18 | See <a href="/releases/#v26242" >v26.24.2 release notes</a> |
| v26.24.1 | v26.24.1 | v26.24.1 | 2026-05-15 | See <a href="/releases/#v26241" >v26.24.1 release notes</a> |
| v26.24.0 | v26.24.0 | v26.24.0 | 2026-05-15 | See <a href="/releases/#v26241" >v26.24.1 release notes</a> |
| v26.22.0 | v26.22.0 | v26.22.0 | 2026-05-01 | See <a href="/releases/#v26220" >v26.22.0 release notes</a> |
| v26.20.2 | v26.20.2 | v26.20.2 | 2026-04-18 | See <a href="/releases/#v26202" >v26.20.2 release notes</a> |
| v26.20.0 | v26.20.0 | v26.20.0 | 2026-04-17 |  |
| v26.19.0 | v26.19.0 | v26.19.0 | 2026-04-10 | See <a href="/releases/#v26190" >v26.19.0 release notes</a> |
| v26.18.0 | v26.18.0 | v26.18.0 | 2026-04-03 | See <a href="/releases/#v26180" >v26.18.0 release notes</a> |
| v26.17.1 | v26.17.1 | v26.17.1 | 2026-03-27 |  |
| v26.17.0 | v26.17.0 | v26.17.0 | 2026-03-27 | See <a href="/releases/#v26170" >v26.17.0 release notes</a> |
| v26.16.0 | v26.16.0 | v26.16.0 | 2026-03-20 | See <a href="/releases/#v26160" >v26.16.0 release notes</a> |
| v26.15.0 | v26.15.0 | v26.15.0 | 2026-03-13 |  |
| v26.15.0 | v26.15.0 | v26.15.0 | 2026-03-13 | See <a href="/releases/#v26150" >v26.15.0 release notes</a> |
| v26.14.1 | v26.14.1 | v26.14.1 | 2026-03-06 | See <a href="/releases/#v26141" >v26.14 release notes</a> |
| v26.14.0 | v26.14.0 | v26.14.0 | 2026-03-06 |  |
| v26.13.0 | v26.13.0 | v26.13.0 | 2026-02-27 | See <a href="/releases/#v26130" >v26.13.0 release notes</a> |
| v26.12.1 | v26.12.1 | v26.12.1 | 2026-02-20 |  |
| v26.12.0 | v26.12.0 | v26.12.0 | 2026-02-20 | See <a href="/releases/#v26120" >v26.12.0 release notes</a> |
| v26.11.0 | v26.11.0 | v26.11.0 | 2026-02-13 | See <a href="/releases/#v26110" >v26.11.0 release notes</a> |
| v26.10.2 | v26.10.2 | v26.10.2 | 2026-02-09 |  |
| v26.10.1 | v26.10.1 | v26.10.1 | 2026-02-06 | See <a href="/releases/#v26101" >v26.10.1 release notes</a> |
| v26.9.0 | v26.9.0 | v26.9.0 | 2026-01-30 | See <a href="/releases/#v2690" >v26.9.0 release notes</a> |
| v26.8.0 | v26.8.0 | v26.8.0 | 2026-01-23 | See <a href="/releases/#v2680" >v26.8.0 release notes</a> |
| v26.7.0 | v26.7.0 | v26.7.0 | 2026-01-16 | See <a href="/releases/#v2670" >v26.7.0 release notes</a> |
| v26.6.0 | v26.6.0 | v26.6.0 | 2026-01-12 | See <a href="/releases/#v2660" >v26.6.0 release notes</a> |
| v26.5.1 | v26.5.1 | v26.5.1 | 2025-12-23 | See <a href="/releases/#v2651" >v26.5.1 release notes</a> |
| v26.5.0 | v26.5.0 | v26.5.0 | 2025-12-23 | Do not use. |
| v26.4.0 | v26.4.0 | v26.4.0 | 2025-12-17 | See <a href="/releases/#v2640" >v26.4.0 release notes</a>. |
| v26.3.0 | v26.3.0 | v26.3.0 | 2025-12-12 | See <a href="/releases/#v2630" >v26.3.0 release notes</a>. |
| v26.2.0 | v26.2.0 | v26.2.0 | 2025-12-09 | See <a href="/releases/#v2620" >v26.2.0 release notes</a>. |
| v26.1.0 | v26.1.0 | v26.1.0 | 2025-11-26 | See <a href="/releases/#v2610" >v26.1.0 release notes</a>. |
| v26.0.0 | v26.0.0 | v26.0.0 | 2025-11-18 | See <a href="/releases/#self-managed-v2600" >v26.0.0 release notes</a> |

---

## Troubleshooting

## Troubleshooting Kubernetes

To check the status of the Materialize operator:

```shell
kubectl -n materialize get all
```

If you encounter issues with the Materialize operator,

- Check the operator logs, using the label selector:

  ```shell
  kubectl -n materialize logs -l app.kubernetes.io/name=materialize-operator
  ```

- Check the log of a specific object (pod/deployment/etc) running in
  your namespace:

  ```shell
  kubectl -n materialize logs <type>/<name>
  ```

  In case of a container restart, to get the logs for previous instance, include
  the `--previous` flag.

- Check the events for the operator pod:

  - You can use `kubectl describe`, substituting your pod name for `<pod-name>`:

    ```shell
    kubectl -n materialize describe pod/<pod-name>
    ```

  - You can use `kubectl get events`, substituting your pod name for
    `<pod-name>`:

    ```shell
    kubectl -n materialize get events --sort-by=.metadata.creationTimestamp --field-selector involvedObject.name=<pod-name>
    ```

### Materialize deployment

- To check the status of your Materialize deployment, run:

  ```shell
  kubectl  -n materialize-environment get all
  ```

- To check the log of a specific object (pod/deployment/etc) running in your
  namespace:

  ```shell
  kubectl -n materialize-environment logs <type>/<name>
  ```

  In case of a container restart, to get the logs for previous instance, include
  the `--previous` flag.

- To describe an object, you can use `kubectl describe`:

  ```shell
  kubectl -n materialize-environment describe <type>/<name>
  ```

For additional `kubectl` commands, see [kubectl Quick reference](https://kubernetes.io/docs/reference/kubectl/quick-reference/).

## Troubleshooting Console unresponsiveness

If you experience long loading screens or unresponsiveness in the Materialize
Console, it may be that the size of the `mz_catalog_server` cluster (where the
majority of the Console's queries are run) is insufficient (default size is
`25cc`).

To increase the cluster's size, you can follow the following steps:

1. Login as the `mz_system` user in order to update `mz_catalog_server`.

   1. To login as `mz_system` you'll need the internal-sql port found in the
      `environmentd` pod (`6877` by default). You can port forward via `kubectl
      port-forward svc/mzXXXXXXXXXX 6877:6877 -n materialize-environment`.

   1. Connect using a pgwire compatible client (e.g., `psql`) and connect using
      the port and user `mz_system`. For example:

       ```
       psql -h localhost -p 6877 --user mz_system
       ```

3. Run the following [ALTER CLUSTER](/sql/alter-cluster/#resizing) statement
   to change the cluster size to `50cc`:

    ```mzsql
    ALTER CLUSTER mz_catalog_server SET (SIZE = '50cc');
    ```

4. Verify your changes via `SHOW CLUSTERS;`

   ```mzsql
   show clusters;
   ```

   Resizing a cluster is a graceful reconfiguration: Materialize brings up a
   replica at the new size, waits for it to hydrate, and only then retires the
   old one. Until that finishes, `SHOW CLUSTERS` reports the old size, and
   briefly both. Re-run the statement until it settles. The replacement replica
   also gets a fresh name, so the resized cluster reports `r2` rather than `r1`.

   The output should include the `mz_catalog_server` cluster with a size of `50cc`:

   ```none
          name        | replicas  | comment
    -------------------+-----------+---------
    mz_analytics      |           |
    mz_catalog_server | r2 (50cc) |
    mz_probe          |           |
    mz_support        |           |
    mz_system         |           |
    quickstart        | r1 (25cc) |
    (6 rows)
    ```

---

## Upgrading

Materialize releases new Self-Managed versions per the schedule outlined in [Release schedule](/releases/schedule/#self-managed-release-schedule).

## General rules for upgrading

<p>When upgrading:</p>
<ul>
<li>
<p><strong>Always</strong> check the <a href="/self-managed-deployments/upgrading/version-notes/" >version-specific upgrade
notes</a> for your target
version:</p>
<ul>
<li><a href="/self-managed-deployments/upgrading/version-notes/#upgrading-to-v2630-and-later-versions" >Upgrading to <code>v26.30</code> and later versions</a></li>
<li><a href="/self-managed-deployments/upgrading/version-notes/#upgrading-to-v261-and-later-versions" >Upgrading to <code>v26.1</code> and later versions</a></li>
<li><a href="/self-managed-deployments/upgrading/version-notes/#upgrading-to-v260" >Upgrading to <code>v26.0</code></a></li>
<li><a href="/self-managed-deployments/upgrading/version-notes/#upgrading-between-minor-versions-less-than-v26" >Upgrading between minor versions less than <code>v26</code></a></li>
</ul>
</li>
<li>
**Always** upgrade the Materialize Operator **before**
upgrading the Materialize instances.

</li>
</ul>

> **Note:** For major version upgrades, you can **only** upgrade **one** major version
> at a time. For example, upgrades from **v26**.1.0 to **v27**.3.0 is
> permitted but **v26**.1.0 to **v28**.0.0 is not.

## Upgrade guides

The following upgrade guides are available as examples:

#### Upgrade using Helm Commands

|  Guide         | Description  |
| ------------- | -------|
| [Upgrade on Kind](/self-managed-deployments/upgrading/upgrade-on-kind/) | Uses standard Helm commands to upgrade Materialize on a Kind cluster in Docker.

<h4 id="upgrade-using-terraform-modules">Upgrade using Terraform Modules</h4>
> **Tip:** The Terraform modules are provided as examples. They are not required for
> upgrading Materialize.

<table>
  <thead>
      <tr>
          <th>Guide</th>
          <th>Description</th>
      </tr>
  </thead>
  <tbody>
      <tr>
          <td><a href="/self-managed-deployments/upgrading/upgrade-on-aws/" >Upgrade on AWS (Terraform)</a></td>
          <td>Uses Terraform module to deploy Materialize to AWS Elastic Kubernetes Service (EKS).</td>
      </tr>
      <tr>
          <td><a href="/self-managed-deployments/upgrading/upgrade-on-azure/" >Upgrade on Azure (Terraform)</a></td>
          <td>Uses Terraform module to deploy Materialize to Azure Kubernetes Service (AKS).</td>
      </tr>
      <tr>
          <td><a href="/self-managed-deployments/upgrading/upgrade-on-gcp/" >Upgrade on GCP (Terraform)</a></td>
          <td>Uses Terraform module to deploy Materialize to Google Kubernetes Engine (GKE).</td>
      </tr>
  </tbody>
</table>

## Upgrading the Helm Chart and Materialize Operator

> **Important:** When upgrading Materialize, always upgrade the Helm Chart and Materialize
> Operator first.

### Update the Helm Chart repository

To update your Materialize Helm Chart repository:

```shell
helm repo update materialize
```

View the available chart versions:

```shell
helm search repo materialize/materialize-operator --versions
```

### Upgrade your Materialize Operator

The Materialize Kubernetes Operator is deployed via Helm and can be updated
through standard `helm upgrade` command:

```mzsql
helm upgrade -n <namespace> <release-name> materialize/materialize-operator \
  --version <new_version> \
  -f <your-custom-values.yml>

```

| Syntax element | Description |
| --- | --- |
| `<namespace>` | The namespace where the Operator is running. (e.g., `materialize`)  |
| `<release-name>` | The release name. You can use `helm list -n <namespace>` to find your release name.  |
| `<new_version>` | The upgrade version.  |
| `<your-custom-values.yml>` | The name of your customization file, if using. If you are configuring using `--set key=value` options, include them as well.  |

You can use `helm list` to find your release name. For example, if your Operator
is running in the namespace `materialize`, run `helm list`:

```shell
helm list -n materialize
```

Retrieve the name associated with the `materialize-operator` **CHART**; for
example, `my-demo` in the following helm list:

```none
NAME    	  NAMESPACE  	REVISION	UPDATED                             	STATUS  	CHART                                          APP VERSION
my-demo	materialize	1      2025-12-08 11:39:50.185976 -0500 EST	deployed	materialize-operator-v26.1.0    v26.1.0
```

Then, to upgrade:

```shell
helm upgrade -n materialize my-demo materialize/operator \
  -f my-values.yaml \
  --version v26.37.0
```

## Upgrading Materialize Instances

After upgrading the operator, upgrade each Materialize instance to the
operator's **App Version** by updating its `environmentdImageRef`. For
step-by-step instructions, use the [upgrade guide](#upgrade-guides) for your
environment (Kind, AWS, Azure, or GCP). This section explains how instance
rollouts work.

## Rollout configuration

Materialize supports two CRD API versions: `v1alpha1` and `v1` (available
starting in v26.30). The Helm chart defaults to `v1alpha1`. The Terraform
modules default to `v1` starting in v4.0.0.

How you trigger a rollout depends on the CRD API version of your instances.

> **Tip:** To migrate a `v1alpha1` instance to `v1`, see
> [Adopting the v1 CRD](/self-managed-deployments/upgrading/adopting-the-v1-crd/).

**v1alpha1:**

Specify a new `UUID` value for `requestRollout` to roll out changes to the
Materialize instance.

> **Note:** `requestRollout` without the `forceRollout` field only rolls out if changes exist
> to the Materialize instance. To roll out even if there are no changes to the
> instance, use it with `forceRollout`.

```shell
# Only rolls out if there are changes
kubectl patch materialize <instance-name> \
  -n <materialize-instance-namespace> \
  --type='merge' \
  -p "{\"spec\": {\"requestRollout\": \"$(uuidgen)\"}}"
```

To force a rollout even when there are no other changes, set a new `forceRollout`
UUID alongside `requestRollout`:

```shell
kubectl patch materialize <instance-name> \
  -n <materialize-instance-namespace> \
  --type='merge' \
  -p "{\"spec\": {\"requestRollout\": \"$(uuidgen)\", \"forceRollout\": \"$(uuidgen)\"}}"
```

**v1:**

With v1, updating the spec automatically triggers a rollout and there is no
`requestRollout` field. For details on the underlying mechanism, see [How it
works](/self-managed-deployments/upgrading/adopting-the-v1-crd/#how-the-switchover-works).

To trigger a rollout even when there are no other changes to the instance,
specify a new `UUID` value for `forceRollout`. That is:

- Set it in your manifest:

  ```yaml
  spec:
    forceRollout: <new-uuid>  # e.g. the output of `uuidgen`
  ```

- Then reapply.

  ```shell
  kubectl apply -f materialize.yaml
  ```

## Rollout strategies

Rollout strategies control how Materialize transitions from the current
generation to a new generation during an upgrade. The behavior follows your
`rolloutStrategy` setting.

### *WaitUntilReady* — ***Default***

`WaitUntilReady` creates a new generation of pods and automatically promotes them
as soon as they catch up to the old generation and become `ReadyToPromote`.
Because both generations run simultaneously until the promotion, this strategy
temporarily doubles the required resources to run Materialize.

> **Note:** While the new generation waits to become `ReadyToPromote`, it runs in a
> read-only, un-promoted state and holds back compaction. To prevent it from
> sitting in this state indefinitely (which can cause incident-inducing load when
> it is eventually promoted), the rollout is bounded by the `rolloutRequestTimeout`
> field in the Materialize spec, which defaults to `24h`.
> If the new generation does not become `ReadyToPromote` within
> `rolloutRequestTimeout`, the operator cancels the rollout: the new generation is
> torn down and the previously-active generation continues serving. You can then
> trigger a new rollout (in v1, set a new `forceRollout`; in v1alpha1, set a new
> `requestRollout`).

### *ImmediatelyPromoteCausingDowntime*

> **Warning:** Using the `ImmediatelyPromoteCausingDowntime` rollout flag will cause downtime.

`ImmediatelyPromoteCausingDowntime` tears down the prior generation and
immediately promotes the new generation without waiting for it to hydrate. This
causes downtime until the new generation has hydrated. However, it does not
require additional resources.

### *ManuallyPromote*

`ManuallyPromote` allows you to choose when to promote the new generation. This
means you can time the promotion for periods when load is low, minimizing the
impact of potential downtime for any clients connected to Materialize. This
strategy temporarily doubles the required resources to run Materialize.

To minimize downtime, wait until the new generation has fully hydrated and caught
up to the prior generation before promoting. To check hydration status, inspect
the `UpToDate` condition in the Materialize resource status. When hydration
completes, the condition will be `ReadyToPromote`.

To promote, update the `forcePromote` field to match the current rollout
identifier (in v1, the `status.requestedRolloutHash`; in v1alpha1, the
`requestRollout` UUID in the spec). If you need to promote before hydration
completes, you can set `forcePromote` immediately, but clients may experience
downtime.

> **Warning:** Leaving a new generation unpromoted for over 6 hours may cause downtime.

**Do not leave new generations unpromoted indefinitely**. They should either be
promoted or canceled. New generations open a read hold on the metadata database
that prevents compaction. This hold is only released when the generation is
promoted or canceled. If left open too long, promoting or canceling can trigger a
spike in deletion load on the metadata database, potentially causing downtime. It
is not recommended to leave generations unpromoted for over 6 hours.

### *inPlaceRollout* — ***Deprecated*** (v1alpha1 only)

The setting is ignored.

## Verifying the upgrade

After initiating the rollout, you can monitor the status field of the Materialize
custom resource to check on the upgrade.

```shell
# Watch the status of your Materialize environment
kubectl get materialize -n materialize-environment -w

# Check the logs of the operator
kubectl logs -l app.kubernetes.io/name=materialize-operator -n materialize
```

## Cancelling the upgrade

You may want to cancel an in-progress rollout if the upgrade has failed (for
example, new pods are not healthy). Before cancelling, verify that the upgrade has
not already completed by checking that the deploy generation (found via
`status.activeGeneration`) is still the one from before the upgrade. Once an
upgrade has already happened, you cannot revert using this method.

**v1alpha1:**

To cancel an in-progress rollout and revert to the last completed rollout state,
revert both `requestRollout` and `environmentdImageRef` back to the values from
the last completed rollout. Reverting `environmentdImageRef` alongside
`requestRollout` keeps the spec aligned with what is actually running, so a later
rollout doesn't accidentally pick up the previously attempted upgrade image.

First, retrieve the last completed rollout request ID and the matching
environmentd image ref from your Materialize CR:

```shell
kubectl get materialize <instance-name> -n materialize-environment \
  -o jsonpath='{.status.lastCompletedRolloutRequest} {.status.lastCompletedRolloutEnvironmentdImageRef}'
```

Then set both fields back to these values in a single patch:

```shell
kubectl patch materialize <instance-name> \
  -n materialize-environment \
  --type='merge' \
  -p "{\"spec\": {\"requestRollout\": \"<lastCompletedRolloutRequest-value>\", \"environmentdImageRef\": \"<lastCompletedRolloutEnvironmentdImageRef-value>\"}}"
```

**v1:**

To cancel an in-progress rollout and revert to the last completed rollout state,
reapply the Materialize resource with the spec it had before the rollout (notably
the previous `environmentdImageRef`). Because v1 derives the rollout from the
spec hash, restoring the previous spec produces the previous hash and returns the
instance to the last completed state.

```shell
kubectl apply -f previous_materialize_configuration.yaml
```

## See also

- [Version-specific upgrade
  notes](/self-managed-deployments/upgrading/version-notes/)

- [Adopting the v1
  CRD](/self-managed-deployments/upgrading/adopting-the-v1-crd/)

- [Materialize Operator
  Configuration](/self-managed-deployments/operator-configuration/)

- [Materialize CRD Field
  Descriptions](/self-managed-deployments/materialize-crd-field-descriptions/)

- [Troubleshooting](/self-managed-deployments/troubleshooting/)

