# Upgrade on Azure
Upgrade Materialize on Azure using the Terraform module.
The following tutorial upgrades your Materialize deployment running on Azure
Kubernetes Service (AKS). The tutorial assumes you have installed the
example on [Install on
Azure](/self-managed-deployments/installation/install-on-azure/).

## Upgrade guidelines

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

> **Note:** Downgrading is not supported.

## Prerequisites

### Required Tools

- [Terraform](https://developer.hashicorp.com/terraform/install?product_intent=terraform)
- [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)

## Upgrade process

> **Important:** The following procedure performs a rolling upgrade, where both the old and new Materialize instances are running before the old instances are removed. When performing a rolling upgrade, ensure you have enough resources to support having both the old and new Materialize instances running.

### Step 1: Update TF module source version

Update each module's `source` to point to the desired release tag, substituting
`<RELEASE_TAG>` in the code block below with your tag version:

> **Important:** The following code block is not comprehensive. Only the core modules and their
> dependency chain are shown below.
> If your configuration includes additional modules (networking, storage,
> database, node pools, etc.) provided by Materialize, **update those to the same
> release tag as well**.

```hcl
module "aks" {
  source = "github.com/MaterializeInc/materialize-terraform-self-managed//azure/modules/aks?ref=<RELEASE_TAG>"
  # ... your existing configuration ...
}

module "cert_manager" {
  source = "github.com/MaterializeInc/materialize-terraform-self-managed//kubernetes/modules/cert-manager?ref=<RELEASE_TAG>"
  # ... your existing configuration ...

  # Your configuration may have additional dependencies here.
  depends_on = [module.aks]
}

module "operator" {
  source = "github.com/MaterializeInc/materialize-terraform-self-managed//azure/modules/operator?ref=<RELEASE_TAG>"
  # ... your existing configuration ...

  # Your configuration may have additional dependencies here.
  depends_on = [module.cert_manager]
}

module "materialize_instance" {
  source = "github.com/MaterializeInc/materialize-terraform-self-managed//kubernetes/modules/materialize-instance?ref=<RELEASE_TAG>"
  # ... your existing configuration ...

  # Your configuration may have additional dependencies here.
  depends_on = [module.operator]
}

# Update the source of any additional Materialize-provided modules to the same release tag
```

### Step 2: Explicitly request rollout if using v1alpha1

<p><code>v1alpha1</code> is the default CRD version for the Materialize Helm
chart. The Terraform modules default to <code>v1</code> starting in v4.0.0.
With <code>v1alpha1</code>, instance rollouts require manually rotating a
UUID.</p>

> **Important:** Starting in Terraform module version v4.0.0, `crd_version` defaults to
> `v1`. If your instance uses `v1alpha1` and you are upgrading to module
> version v4.0.0 or greater, set `crd_version = "v1alpha1"` explicitly to
> stay on `v1alpha1`. Otherwise, applying migrates the instance to `v1` and
> triggers a rollout. See [Adopting the v1
> CRD](/self-managed-deployments/upgrading/adopting-the-v1-crd/).

To check the CRD version of the Materialize manifest that was applied, run
the following:

```sh
terraform state show 'module.materialize_instance.kubectl_manifest.materialize_instance' \
  | grep -iE 'api_?version|kind'
```

- If you are using `v1`, skip to the [Apply the updated TF
  step](#step-3-apply-the-updated-tf).
- **If you are using `v1alpha1`**, you need to update your `terraform.tfvars`
file to set the `request_rollout` variable to a new UUID value, substituting
the example value in the code block below with a UUID you generate (for
example, with `uuidgen`):

```hcl
# ...
# ...
request_rollout = "DBB4FCEC-1837-44F6-9CF2-3894678DD8D5" # ONLY for v1alpha1
```

### Step 3: Apply the updated TF

1. Initialize the Terraform directory to download the required providers
    and modules:

    ```bash
    terraform init
    ```

1. Review the execution plan before applying. In particular, check for any
  resources Terraform plans to destroy and recreate (shown as `-/+` in the
  plan), especially stateful resources such as your cluster, storage, and
  database:

    ```bash
    terraform plan
    ```

1. After reviewing the plan, apply the Terraform configuration.

    ```bash
    terraform apply
    ```

### Step 4: Verify the upgrade

Configure `kubectl` to connect to your AKS cluster:

```bash
# az aks get-credentials --resource-group <your-resource-group-name> --name <your-aks-cluster-name>
az aks get-credentials --resource-group $(terraform output -raw resource_group_name) --name $(terraform output -raw aks_cluster_name)
```

> **Note:** `terraform apply` returns once the Materialize custom resource is updated.
> The Operator then rolls out the new generation asynchronously, so the new
> `environmentd` pods may take a few minutes to become ready.

<ol>
<li>
<p>Check the status of the <code>materialize</code> namespace:</p>
<div class="highlight"><pre tabindex="0" class="chroma"><code class="language-bash" data-lang="bash"><span class="line"><span class="cl">kubectl -n materialize get all
</span></span></code></pre></div></li>
<li>
<p>Check the status of the <code>materialize-environment</code> namespace:</p>
<div class="highlight"><pre tabindex="0" class="chroma"><code class="language-bash" data-lang="bash"><span class="line"><span class="cl">kubectl -n materialize-environment get all
</span></span></code></pre></div></li>
<li>
<p>Once a new <code>environmentd</code> is up (may take a few minutes), confirm the
running <code>environmentd</code> version matches the version you upgraded to. Check
the <code>Image</code> field in the pod description.</p>
<div class="highlight"><pre tabindex="0" class="chroma"><code class="language-bash" data-lang="bash"><span class="line"><span class="cl">kubectl -n materialize-environment describe pod -l <span class="nv">app</span><span class="o">=</span>environmentd
</span></span></code></pre></div></li>
</ol>
<p>If you run into an error during the upgrade, refer to the
<a href="/self-managed-deployments/troubleshooting/" >Troubleshooting</a>.</p>

## Enable the monitoring stack

The Terraform modules can install a monitoring stack — Grafana, Thanos, Loki,
Grafana Alloy, and Alertmanager — alongside your deployment, with the
Materialize dashboards pre-installed. You can turn it on during an upgrade, in
the same `terraform apply` as the version bump.

The stack below arrived in **TF v10.0.0**, replacing the earlier single
Prometheus and Grafana. **TF v10.1.0** then added durable state for Grafana and
a load balancer to reach it on.

> **Warning:** `kubernetes/modules/prometheus` and `kubernetes/modules/grafana` were **removed**
> in v10.0.0, not deprecated in place. If your configuration references either
> directly, that reference breaks — pin the previous major until you have
> migrated.
> If you were running the old stack, upgrading **destroys** its Helm releases and
> PersistentVolumeClaims. Up to 15 days of local Prometheus data goes with them,
> along with anything hand-created in the old Grafana. There is no backfill. See
> [Upgrading from the previous
> stack](/manage/monitor/self-managed/grafana/#upgrading-from-the-previous-stack).

### If you use the example configuration

Set the following in your `terraform.tfvars`:

```hcl
enable_observability = true
```

### If you instantiate the modules yourself

1. Add the `monitoring` module, using the same release tag as the rest of your
   modules:

   ```hcl
   module "monitoring" {
     source = "github.com/MaterializeInc/materialize-terraform-self-managed//azure/modules/monitoring?ref=<RELEASE_TAG>"

     prefix              = var.name_prefix
     resource_group_name = azurerm_resource_group.materialize.name
     location            = var.location

     namespace = "monitoring"
     # The operator module already creates this namespace.
     create_namespace = false

     oidc_issuer_url = module.aks.cluster_oidc_issuer_url

     materialize_instance_namespace = "materialize-environment"
     materialize_operator_namespace = "materialize"

     # Grafana's own state. Omit to leave Grafana on SQLite.
     grafana_database = {
       subnet_id           = module.networking.postgres_subnet_id
       private_dns_zone_id = module.networking.private_dns_zone_id
     }

     # Reach Grafana without port forwarding. Omit to keep it on ClusterIP.
     grafana_load_balancer = {
       ingress_cidr_blocks = var.ingress_cidr_blocks
     }

     tags = var.tags

     depends_on = [module.operator]
   }
   ```

1. Turn on the operator's scrape annotations so its pods are collected:

   ```hcl
   module "operator" {
     # ...
     helm_values = {
       observability = {
         enabled = true
         prometheus = {
           scrapeAnnotations = {
             enabled = true
           }
         }
       }
     }
   }
   ```

### What this creates

Applying the above adds blob containers for metrics and logs, and — from TF
v10.1.0 — a `B_Standard_B1ms` PostgreSQL Flexible Server for Grafana's own state
and an internal load balancer to reach Grafana on. The database and the load
balancer are both billable.

> **Warning:** The Grafana load balancer terminates no TLS, and Grafana has no identity
> provider until you configure one. Keep it internal until both are addressed. A
> public load balancer whose allowlist is still `0.0.0.0/0` is refused at plan
> time for Grafana specifically.

> **Note:** The monitoring stack runs several components: Loki, Thanos, Grafana,
> Alertmanager, kube-state-metrics, and two Alloy roles. Your generic node pool
> may need to grow before the apply can schedule all of them.

For accessing Grafana, pointing the stack at a database you already run, sizing
profiles, and retention, see
[Grafana](/manage/monitor/self-managed/grafana/).

## See also

- [Materialize Operator
  Configuration](/self-managed-deployments/operator-configuration/)
- [Materialize CRD Field
  Descriptions](/self-managed-deployments/materialize-crd-field-descriptions/)
- [Troubleshooting](/self-managed-deployments/troubleshooting/)
