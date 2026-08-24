# Datadog
How to monitor the performance and overall health of Self-Managed Materialize using Datadog.
This guide walks you through the steps required to monitor the performance and
overall health of your Materialize region using [Datadog
⧉](https://www.datadoghq.com/). Self-Managed Materialize pushes metrics, and
optionally logs, to Datadog from the monitoring stack the Materialize Terraform
modules install.

## How it works

The stack collects metrics and logs before any destination is involved. For the
collection pipeline and where that data is stored by default, see [How logs and
metrics are stored](/manage/monitor/self-managed/storage/#how-it-works).

Datadog is an **additive** destination. It receives its own filtered copy of the
metrics, and the bundled [Thanos](/manage/monitor/self-managed/storage/),
Grafana, and Alertmanager keep working as before. You do not give anything up by
turning it on.

The exporter authenticates directly against the Datadog intake with an API key,
so the only decisions are which site to send to and how much to send.

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

- A [Datadog API key
  ⧉](https://docs.datadoghq.com/account_management/api-app-keys/). An application
  key is not needed and is not accepted: the metrics intake authenticates with
  the API key alone.

- Your [Datadog site ⧉](https://docs.datadoghq.com/getting_started/site/), such
  as `datadoghq.com`, `datadoghq.eu`, or `us3.datadoghq.com`. A wrong site is a
  403 from the intake rather than a routing error, so confirm it before you
  apply.

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

### Step 2. Configure the Datadog destination

Datadog is configured on the `monitoring` module block, not through a root
variable of the examples. It provisions no cloud resources, so there is no
`enable_datadog` toggle: setting `datadog_metrics` is what turns it on.

1. In the `monitoring` module block of your Terraform, add:

   ```hcl
   module "monitoring" {
     # ...

     datadog_metrics = {
       site           = "datadoghq.com"
       min_importance = "essential"
     }
     datadog_api_key = var.datadog_api_key
   }
   ```

   The examples ship this block commented out, so you can uncomment it in place.

   | Field | Default | Purpose |
   |-------|---------|---------|
   | `site` | `datadoghq.com` | Your Datadog site. Determines the intake the exporter writes to. |
   | `min_importance` | `essential` | Which metrics to send. See [How to control which metrics Datadog receives](#how-to-control-which-metrics-datadog-receives). |
   | `metric_endpoint` | derived from `site` | Override the metrics intake URL. Only for a proxy or PrivateLink. |
   | `logs_endpoint` | derived from `site` | Override the logs intake URL. Only for a proxy or PrivateLink. |

   > **Warning:** A hand-written `metric_endpoint` or `logs_endpoint` that disagrees with `site`
>    fails at the intake, not at plan time. Leave both unset unless you are routing
>    through a proxy.

1. Declare the API key as a sensitive variable and pass it in the way you pass
   other secrets, for example through an environment variable:

   ```hcl
   variable "datadog_api_key" {
     type      = string
     sensitive = true
   }
   ```

   ```bash
   export TF_VAR_datadog_api_key='<your-datadog-api-key>'
   ```

1. Apply the configuration:

   ```bash
   terraform apply
   ```

Credentials do not travel through the Helm values. The monitoring module puts
them in a Kubernetes Secret that the gateway mounts, so they are not recoverable
with `helm get values` and do not land in the rendered manifests. Rotating one
rolls the gateway, because environment variables are fixed at container start
and a running pod would otherwise keep authenticating with the credential it
started with, indefinitely.

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

In Datadog, **Metrics > Summary** filtered to `mz_` is the quickest place to look.

### Step 4. Build alerts

With metrics in Datadog, build [monitors ⧉](https://docs.datadoghq.com/monitors/)
from the metrics and thresholds in
[Alerting](/manage/monitor/self-managed/alerting/).

The monitoring stack also ships Alertmanager rules that evaluate against the
bundled Thanos. Decide which system owns which alerts rather than running both
against the same thresholds and paging twice.

## How to control which metrics Datadog receives

Datadog bills per custom metric, so the volume you send is a cost decision.

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

`datadog_metrics.min_importance` defaults to `essential`, a tighter floor than the
other destinations use, for exactly this reason. `all` is a diagnostic setting,
not a steady state.

## How to forward logs

The gateway collects logs as well as metrics, and can forward them to the same
OpenTelemetry destinations. The bundled Loki continues to receive them either
way. Enable it through `additional_values` on the `monitoring` module block:

```hcl
additional_values = [
  <<-EOT
    pipeline:
      logging:
        gateway:
          destination:
            otel:
              enabled: true
  EOT
]
```

The switch is not per-destination. It turns on the log path to every logs-capable
exporter the gateway has enabled, so if you have both a Datadog and a generic
OTLP destination configured, both receive the logs. Google Cloud Monitoring is
metrics-only and cannot receive them, and enabling the switch with no logs-capable
exporter configured fails the install rather than silently dropping the logs.

Logs are considerably higher volume than metrics, and backends generally bill for
them separately from metrics. Turn this on deliberately.

Datadog bills for logs separately from custom metrics. For the log storage
options in full, see [How logs and metrics are stored](/manage/monitor/self-managed/storage/).

## Instructions when using Helm

If you install the `materialize-monitoring` chart directly rather than through the
Terraform modules, the Datadog destination is a chart value and the API key is a
Secret you create.

1. Enable the exporter:

   ```yaml
   pipeline:
     metrics:
       gateway:
         destination:
           otel:
             enabled: true
             datadogExporter:
               enabled: true
               url: datadoghq.com
               minMetricImportance: essential
   ```

1. Create the gateway Secret with the API key. The chart does not create it, and
   mounts it optionally, so a wrong name or namespace is ignored silently rather
   than failing:

   ```bash
   kubectl create secret generic mzmon-alloy-gateway-env \
     --namespace monitoring \
     --from-literal=GATEWAY_OTEL_DEST_DATADOG_API_KEY='<your-datadog-api-key>'
   ```

   > **Warning:** The Secret name must match the release, so with the default
>    `fullnameOverride: mzmon` it is `mzmon-alloy-gateway-env`, in the namespace the
>    gateway runs in. In production, source it from Sealed Secrets, External
>    Secrets, or SOPS rather than committing a raw credential.

For a ready-made starting point that fans metrics out to several backends at
once, see the [`otel-metrics-fanout.values.yaml`
⧉](https://github.com/MaterializeInc/materialize-monitoring/blob/main/charts/materialize-monitoring/profiles/otel-metrics-fanout.values.yaml)
profile, and for the full value reference, [Metrics > Storing
⧉](https://materializeinc.github.io/materialize-monitoring/metrics/storing/).

## See also

- [How logs and metrics are stored](/manage/monitor/self-managed/storage/), for the
  bundled stores and the other backends you can send metrics and logs to.

- [Honeycomb](/manage/monitor/self-managed/honeycomb/) and
  [OpenTelemetry](/manage/monitor/self-managed/opentelemetry/), which follow the
  same additive model over OTLP.

- [Alerting](/manage/monitor/self-managed/alerting/), for the metrics and
  thresholds to alert on.
