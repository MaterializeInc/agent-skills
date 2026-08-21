# Prometheus remote write
How to send metrics from Self-Managed Materialize to an external Prometheus remote-write store such as Mimir, Amazon Managed Prometheus, or Grafana Cloud.
This guide walks you through the steps required to store the metrics from your
Materialize region in an external Prometheus remote-write store, such as Grafana
Mimir, Amazon Managed Prometheus, Grafana Cloud, or a Thanos you run elsewhere.

> **Warning:** Unlike other destinations, remote write is a **replacement**,
> not an addition. It is the single sink the bundled Thanos already occupies, so
> pointing it at an external store means Thanos stops receiving metrics, and the
> bundled Grafana dashboards go empty unless you also repoint their data source.
> If you want an external copy *and* the bundled store, use an [OTLP
> destination](/manage/monitor/self-managed/opentelemetry/) instead, which runs
> alongside Thanos. That only works if your platform exposes an OTLP ingest
> endpoint. A remote-write-only backend cannot be reached additively, so with one of
> those the choice really is external store or bundled store, not both.

## How it works

The stack collects metrics and logs before any destination is involved. For the
collection pipeline and where that data is stored by default, see [How logs and
metrics are stored](/manage/monitor/self-managed/storage/#how-it-works).

The gateway writes metrics with the Prometheus remote-write protocol, and the
bundled Thanos is simply the default endpoint for that write. Repointing it is a
change of address rather than a new code path, which is why it needs no separate
exporter and why there can only be one of them.

Because the external store replaces Thanos, consider turning the bundled one off
in the same change rather than paying to run a store nothing writes to.

## Instructions

### Before you begin

Ensure you have:

- A Materialize deployment created with the [Materialize Terraform
  modules](/self-managed-deployments/), with the monitoring stack enabled. See
  [Step 1](#step-1-enable-observability).

- [Terraform ⧉](https://developer.hashicorp.com/terraform/install) installed.

- [kubectl ⧉](https://kubernetes.io/docs/tasks/tools/) installed and configured
  to connect to your cluster.

> **Note:** The Terraform steps on this page require **v11.0.0** or later of the Materialize
> Terraform Modules, which is where the monitoring module accepts these
> destinations. If you install the
> `materialize-monitoring` chart with Helm rather than through the Terraform
> modules, no Terraform release applies and neither does `enable_observability`.
> Follow the Helm instructions at the end of this page instead.

You also need:

- Your store's remote-write endpoint, as a full URL including the scheme and path,
  such as `https://<host>/api/v1/write`. Note that this differs from the OTLP
  destinations, which take a bare `host[:port]`.

- The credential it expects: basic auth, a bearer token, OAuth2 client
  credentials, or AWS SigV4 signing.

- A decision about the bundled Grafana. Its data source points at Thanos, so if
  you retire Thanos you either repoint that data source at the external store or
  use the external platform's own query interface.

### Step 1. Enable observability

The Materialize Terraform Modules take an `enable_observability` variable.
Starting with **v11.0.0** it defaults to `true`, so a fresh apply installs the
monitoring stack without any configuration, and bumping `ref=<tag>` to v11.0.0
or later installs it on a deployment that never set the variable.

1. To confirm the setting, or to change it, set it explicitly in your
   `terraform.tfvars`:

   ```hcl
   enable_observability = true    # default starting with Materialize Terraform Modules v11.0.0
   ```

1. Apply the configuration:

   ```bash
   terraform apply
   ```

   The apply creates the object storage and cloud identities for metrics and
   logs, and installs the stack into the `monitoring` namespace.

> **Warning:** The stack and its supporting resources are billable, and the `generic` node pool
> may need to grow before the first apply can schedule everything. If you do not
> want it, set `enable_observability = false` before upgrading to Materialize
> Terraform Modules v11.0.0.

### Step 2. Repoint the remote-write destination

Remote write is not modelled as a Terraform input, because unlike the additive
destinations it changes where the stack's own storage lives. Set it through
`additional_values` on the `monitoring` module block, which is appended last and so
wins over anything the modules compute.

1. In the `monitoring` module block of your Terraform, add:

   ```hcl
   module "monitoring" {
     # ...

     additional_values = [
       <<-EOT
         pipeline:
           metrics:
             gateway:
               destination:
                 prometheusRemoteWrite:
                   url: https://<your-endpoint>/api/v1/write
                   authType: basicAuth
                   minMetricImportance: all
       EOT
     ]
   }
   ```

   `authType` is one of `none`, `basicAuth`, `bearer`, `oauth2`, or `sigv4`.

1. Set the `cluster` label so series from different deployments stay distinct once
   they land in a shared store. Every sample carries it, and it defaults to
   `default`:

   ```hcl
   additional_values = [
     <<-EOT
       env:
         CLUSTER_NAME: prod-us-east-1
     EOT
   ]
   ```

1. Supply the credential through the gateway Secret rather than inline in the
   values. The remote-write block accepts a credential inline, but anything set
   there is baked into the gateway's ConfigMap in plaintext:

   ```bash
   kubectl create secret generic mzmon-alloy-gateway-env \
     --namespace monitoring \
     --from-literal=GATEWAY_PROMETHEUS_DEST_USERNAME='<user>' \
     --from-literal=GATEWAY_PROMETHEUS_DEST_PASSWORD='<password>'
   ```

   | Auth type | Secret keys |
   |-----------|-------------|
   | `basicAuth` | `GATEWAY_PROMETHEUS_DEST_USERNAME`, `GATEWAY_PROMETHEUS_DEST_PASSWORD` |
   | `bearer` | `GATEWAY_PROMETHEUS_DEST_BEARER_TOKEN` |
   | `oauth2` | `GATEWAY_PROMETHEUS_DEST_OAUTH2_CLIENT_ID`, `..._CLIENT_SECRET`, `..._TOKEN_URL` |
   | client TLS | `GATEWAY_PROMETHEUS_DEST_TLS_CA`, `..._TLS_CERT`, `..._TLS_KEY` |
   | `sigv4` | none. It signs with the gateway pod's IRSA identity |

   > **Warning:** The Secret name must match the release, so with the default
>    `fullnameOverride: mzmon` it is `mzmon-alloy-gateway-env`, in the namespace the
>    gateway runs in. Because the mount is optional, a wrong name or namespace is
>    ignored silently and the destination then authenticates with empty credentials
>    rather than failing loudly.

1. Apply the configuration:

   ```bash
   terraform apply
   ```

### Step 3. Amazon Managed Prometheus

Amazon Managed Prometheus is the one remote-write store that needs no credential
in the cluster at all. `sigv4` signs requests with the gateway pod's IRSA
identity.

1. Create an IAM role with remote-write permission on the workspace, and a trust
   policy scoped to the gateway's namespace and ServiceAccount.

1. Point remote write at the workspace and annotate the gateway ServiceAccount so
   IRSA applies:

   ```hcl
   additional_values = [
     <<-EOT
       pipeline:
         metrics:
           gateway:
             destination:
               prometheusRemoteWrite:
                 authType: sigv4
                 url: https://aps-workspaces.<region>.amazonaws.com/workspaces/<workspace-id>/api/v1/remote_write

       alloy-gateway:
         serviceAccount:
           annotations:
             eks.amazonaws.com/role-arn: arn:aws:iam::<account-id>:role/<amp-role>
     EOT
   ]
   ```

A ready-made starting point lives at [`aws-amp-example.values.yaml`
⧉](https://github.com/MaterializeInc/materialize-monitoring/blob/main/charts/materialize-monitoring/profiles/aws-amp-example.values.yaml).
Note that it also sets `thanos.enabled: false`, which is the next step.

### Step 4. Retire the bundled metric store

Once the external store is receiving metrics, the bundled Thanos is a component
nothing writes to. Turning it off frees its compute and stops new writes to its
object storage:

```hcl
additional_values = [
  <<-EOT
    thanos:
      enabled: false
  EOT
]
```

> **Warning:** Do this only after confirming the external store is receiving metrics. Disabling
> Thanos does not delete its bucket, so historical blocks survive, but nothing serves
> queries against them while it is off. Repoint the bundled Grafana's data source at
> the external store in the same change, or its dashboards will show no data.

### Step 5. Confirm metrics are arriving

1. Check that the gateway picked up the new configuration and is healthy:

   ```bash
   kubectl -n monitoring rollout status deployment/alloy-gateway
   ```

1. Query the receiving backend for recent samples of a metric you expect, such
   as `mz_dataflow_wallclock_lag_seconds`.

> **Note:** A backend's metric summary, schema, or column browser is cumulative, so a metric
> listed there is not proof that it is arriving now. It may be left over from
> before a configuration change. Query for recent samples instead.

> **Warning:** The gateway shards scrape targets across its replicas. During a partial rollout a
> metric can look missing simply because its target is being scraped by a pod that
> has not picked up the new configuration yet. Let all gateway replicas roll out
> before concluding that a metric is being filtered.

### Step 6. Configure alerts

The Alertmanager rules the stack ships evaluate against the bundled Thanos, so
retiring it moves alerting to the external platform. Rebuild the alerts there from
the metrics and thresholds in [Alerting](/manage/monitor/self-managed/alerting/).

## How to control which metrics the store receives

Every metric the stack collects carries an *importance* tier, and each
destination keeps only the metrics at or above a floor you choose. The tiers
below run from most to least important, and the floor is cumulative: it keeps
that tier and every tier above it.

| Tier | What it covers |
|------|----------------|
| `essential` | The metrics that are critical and that you would always want available. These are the ones used in alerting. |
| `recommended` | The metrics used in dashboards, and generally desirable for troubleshooting. |
| `extended` | The metrics used by optional and experimental dashboards. |
| `diagnostic` | The metrics used for in-depth troubleshooting and analysis. |
| `all` | Absolutely everything scraped, including metrics no tier classifies. Suited to cheap storage such as the bundled Thanos, not to a metered backend. |

The tiers are shared across the stack, so a tier selected in Terraform means the
same set of metrics as the same tier selected in Helm. For the membership of each
tier, see [List of metrics
⧉](https://materializeinc.github.io/materialize-monitoring/reference/stable-metrics/list-metrics/).
For the metrics Materialize recommends dashboarding and alerting on, see
[essential metrics](/manage/monitor/essential-metrics/), and for everything it
exposes, the [appendix of all metrics](/manage/monitor/appendix-metrics/).

> **Note:** The `extended` and `diagnostic` tiers are still being populated, so today they
> resolve to the same set as `recommended`. To send everything that is scraped, use
> `all`, not `diagnostic`.

> **Warning:** The filter fails open. If the allowlist reaches the gateway empty, the gateway
> sends everything to that destination rather than nothing. That is safe for
> visibility and expensive on a metered backend, so check the receiving backend's
> ingest volume after a configuration change.

The remote-write destination defaults to `all`, on the assumption that it is
backed by cheap storage. If you repoint it at a metered platform, lower the floor
in the same change:

```yaml
pipeline:
  metrics:
    gateway:
      destination:
        prometheusRemoteWrite:
          minMetricImportance: recommended
```

## Instructions when using Helm

The values above are chart values, so a Helm install uses them directly rather
than through `additional_values`. The gateway Secret and its keys are identical.

For the full value reference, including the per-`authType` blocks and the client
TLS settings, see [Metrics > Storing
⧉](https://materializeinc.github.io/materialize-monitoring/metrics/storing/).

## See also

- [How logs and metrics are stored](/manage/monitor/self-managed/storage/), for the
  bundled stores and the additive backends that keep them in place.

- [OpenTelemetry](/manage/monitor/self-managed/opentelemetry/), the additive
  alternative where your platform accepts OTLP.

- [Alerting](/manage/monitor/self-managed/alerting/), for the metrics and
  thresholds to alert on.
