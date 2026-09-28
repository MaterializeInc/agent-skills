# Google Cloud Monitoring
How to monitor the performance and overall health of Self-Managed Materialize using Google Cloud Monitoring.
This guide walks you through the steps required to monitor the performance and
overall health of your Materialize region using [Google Cloud Monitoring
⧉](https://cloud.google.com/monitoring). Self-Managed Materialize pushes metrics
to Cloud Monitoring from the monitoring stack the Materialize Terraform modules
install.

This destination is **GCP only**, and it is the one destination that needs cloud
resources the monitoring chart cannot create for itself. That is why it is enabled
with a flat variable rather than a configuration block: Terraform has to know at
plan time whether to create the service account and the Workload Identity binding
that authenticate it.

## How it works

The stack collects metrics and logs before any destination is involved. For the
collection pipeline and where that data is stored by default, see [How logs and
metrics are stored](/manage/monitor/self-managed/storage/#how-it-works).

Cloud Monitoring is an **additive** destination. It receives its own filtered copy
of the metrics, and the bundled [Thanos](/manage/monitor/self-managed/storage/),
Grafana, and Alertmanager keep working as before.

Authentication is **ambient**, not a credential you supply. The module creates a
Google service account, grants it `roles/monitoring.metricWriter`, and binds the
gateway's in-cluster ServiceAccount to it through Workload Identity. The exporter
then authenticates with Application Default Credentials.

> **Note:** Cloud Monitoring is metrics-only. Its exporter cannot receive logs, and enabling
> the log path with Cloud Monitoring as the only OpenTelemetry destination fails the
> install rather than silently dropping them. For logs on GCP, use an [OTLP
> destination](/manage/monitor/self-managed/opentelemetry/) or keep them in the
> bundled [Loki](/manage/monitor/self-managed/storage/).

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

- A deployment on **GCP**, created with the GCP Terraform modules. Workload
  Identity must be enabled on the cluster, which the `gke` module already sets.

- Permission to create a service account and IAM bindings in the project.

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

### Step 2. Configure the Cloud Monitoring destination

1. On the `monitoring` module block of your Terraform, set:

   ```hcl
   module "monitoring" {
     # ...

     enable_google_cloud_metrics         = true
     google_cloud_metrics_min_importance = "recommended"
   }
   ```

   | Variable | Default | Purpose |
   |----------|---------|---------|
   | `enable_google_cloud_metrics` | `false` | Turns the destination on, and creates the service account and Workload Identity binding it authenticates with. |
   | `google_cloud_metrics_min_importance` | `recommended` | Which metrics to send. See [How to control which metrics Cloud Monitoring receives](#how-to-control-which-metrics-cloud-monitoring-receives). |
   | `google_cloud_metrics_prefix` | `workload.googleapis.com/mzmon` | The metric name prefix in Cloud Monitoring. |

1. Apply the configuration:

   ```bash
   terraform apply
   ```

> **Warning:** Authentication is Application Default Credentials only. There is no key-file path.
> Without the Workload Identity binding the module creates, the exporter falls back
> to the node's service account, which works only if that account happens to hold
> `roles/monitoring.metricWriter`, and fails opaquely if it does not.

### Step 3. Confirm metrics are arriving

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

In Cloud Monitoring, use **Metrics explorer** and filter to the prefix, which is
`workload.googleapis.com/mzmon` unless you changed it.

### Step 4. Build alerts

Build Cloud Monitoring [alerting policies
⧉](https://cloud.google.com/monitoring/alerts) from the metrics and thresholds in
[Alerting](/manage/monitor/self-managed/alerting/).

The monitoring stack also ships Alertmanager rules that evaluate against the
bundled Thanos. Decide which system owns which alerts rather than running both
against the same thresholds.

## How to control which metrics Cloud Monitoring receives

Cloud Monitoring bills per custom metric and per sample, so the tier you pick sets
the bill.

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

`google_cloud_metrics_min_importance` defaults to `recommended`, which covers the
metrics the dashboards and alerts use. `all` is a diagnostic setting, not a steady
state.

## Instructions when using Helm

If you install the `materialize-monitoring` chart directly rather than through the
Terraform modules, you create the identity and binding yourself, then point the
chart at it.

1. Create a Google service account, grant it `roles/monitoring.metricWriter` on
   the project, and bind the gateway's ServiceAccount to it with
   `roles/iam.workloadIdentityUser`.

1. Enable the exporter and annotate the gateway ServiceAccount so the binding
   applies:

   ```yaml
   alloy-gateway:
     serviceAccount:
       annotations:
         iam.gke.io/gcp-service-account: <gsa>@<project>.iam.gserviceaccount.com

   pipeline:
     metrics:
       gateway:
         destination:
           otel:
             enabled: true
             googleCloudExporter:
               enabled: true
               minMetricImportance: recommended
   ```

There is no Secret to create, because the exporter authenticates with the ambient
identity. Cloud Monitoring supports `gzip` compression only.

For the full value reference, see [Metrics > Storing
⧉](https://materializeinc.github.io/materialize-monitoring/metrics/storing/).

## See also

- [How logs and metrics are stored](/manage/monitor/self-managed/storage/), for the
  bundled stores and the other backends you can send metrics and logs to.

- [OpenTelemetry](/manage/monitor/self-managed/opentelemetry/), for OTLP
  destinations, which can also carry logs.

- [Alerting](/manage/monitor/self-managed/alerting/), for the metrics and
  thresholds to alert on.
