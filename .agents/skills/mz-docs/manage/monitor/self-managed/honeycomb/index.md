# Honeycomb
How to monitor the performance and overall health of Self-Managed Materialize using Honeycomb.
This guide walks you through the steps required to monitor the performance and
overall health of your Materialize region using [Honeycomb
⧉](https://www.honeycomb.io/). Self-Managed Materialize pushes metrics, and
optionally logs, to Honeycomb over OTLP from the monitoring stack the Materialize
Terraform modules install.

Honeycomb is an OpenTelemetry destination, so the mechanism is the one described
in [OpenTelemetry](/manage/monitor/self-managed/opentelemetry/). This page covers
the Honeycomb-specific parts: the endpoint, the two request headers it expects,
and which of them is a secret.

## How it works

The stack collects metrics and logs before any destination is involved. For the
collection pipeline and where that data is stored by default, see [How logs and
metrics are stored](/manage/monitor/self-managed/storage/#how-it-works).

Honeycomb is an **additive** destination. It receives its own filtered copy of the
metrics, and the bundled [Thanos](/manage/monitor/self-managed/storage/),
Grafana, and Alertmanager keep working as before.

Honeycomb authenticates with an API-key **request header** rather than a bearer
token, and it takes the target dataset as a second header. That split matters
here, because the two headers are configured in different places: the dataset
renders into the gateway's configuration as a literal, and the API key is
delivered through a Secret.

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

- A Honeycomb [API key
  ⧉](https://docs.honeycomb.io/configure/environments/manage-api-keys/) with
  permission to send events, from the environment you want the metrics in.

- The name of the Honeycomb **dataset** the metrics should land in. Honeycomb
  creates it on first write, so this is a name you choose rather than one you look
  up.

- Your Honeycomb region's endpoint: `api.honeycomb.io`, or
  `api.eu1.honeycomb.io` for the EU instance.

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

### Step 2. Configure the Honeycomb destination

Honeycomb is configured on the `monitoring` module block, not through a root
variable of the examples. It provisions no cloud resources, so there is no
`enable_honeycomb` toggle: setting `otlp_metrics` is what turns it on.

1. In the `monitoring` module block of your Terraform, add:

   ```hcl
   module "monitoring" {
     # ...

     otlp_metrics = {
       url            = "api.honeycomb.io"
       protocol       = "grpc"
       min_importance = "recommended"
       auth_headers   = { "x-honeycomb-dataset" = "mzmon" }
     }
     otlp_auth_header_secrets = { "x-honeycomb-team" = var.honeycomb_api_key }
   }
   ```

   The examples ship this block commented out, so you can uncomment it in place.

   | Field | Value | Why |
   |-------|-------|-----|
   | `url` | `api.honeycomb.io` | A `host[:port]` with **no** scheme. |
   | `protocol` | `grpc` | Honeycomb accepts OTLP over gRPC and HTTP. `grpc` is the default. |
   | `min_importance` | `recommended` | Honeycomb is metered. See [How to control which metrics Honeycomb receives](#how-to-control-which-metrics-honeycomb-receives). |
   | `auth_headers` | `x-honeycomb-dataset` | The target dataset. Not a secret, so it goes here and renders inline. |
   | `otlp_auth_header_secrets` | `x-honeycomb-team` | The API key. Delivered through a Secret. |

   > **Warning:** `url` takes no scheme. A `https://` prefix fails when the gateway starts, not
>    at plan time.

   > **Note:** Put the API key in `otlp_auth_header_secrets`, never in
>    `otlp_metrics.auth_headers`. The latter renders its values into the gateway's
>    configuration in plaintext. The two compose into one header set, so the
>    non-secret dataset header and the secret key header work together.

1. Declare the API key as a sensitive variable and pass it in the way you pass
   other secrets, for example through an environment variable:

   ```hcl
   variable "honeycomb_api_key" {
     type      = string
     sensitive = true
   }
   ```

   ```bash
   export TF_VAR_honeycomb_api_key='<your-honeycomb-api-key>'
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

In Honeycomb, select the dataset you named and query for a recent metric.

> **Note:** Honeycomb's schema view is cumulative, so a metric shown there may predate a
> configuration change. Confirm against a recent time window.

### Step 4. Build alerts

Build Honeycomb [triggers
⧉](https://docs.honeycomb.io/investigate/alerts/triggers/) from the metrics and
thresholds in [Alerting](/manage/monitor/self-managed/alerting/).

The monitoring stack also ships Alertmanager rules that evaluate against the
bundled Thanos. Decide which system owns which alerts rather than running both
against the same thresholds.

## How to control which metrics Honeycomb receives

Honeycomb is metered, so the volume you send is a cost decision.

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

`otlp_metrics.min_importance` defaults to `recommended`, which covers the metrics
the dashboards and alerts use. `all` is a diagnostic setting, not a steady state.

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

For the log storage options in full, see
[How logs and metrics are stored](/manage/monitor/self-managed/storage/).

## Instructions when using Helm

If you install the `materialize-monitoring` chart directly rather than through the
Terraform modules, the destination is a chart value and the API key is a Secret
you create.

1. Enable the generic OTLP exporter and set header auth:

   ```yaml
   pipeline:
     metrics:
       gateway:
         destination:
           otel:
             enabled: true
             otlpExporter:
               enabled: true
               url: api.honeycomb.io
               protocol: grpc
               minMetricImportance: recommended
             auth:
               authType: headers
               headers:
                 headers:
                   - key: x-honeycomb-team
                     valueEnv: GATEWAY_OTEL_DEST_HONEYCOMB_API_KEY
                   - key: x-honeycomb-dataset
                     value: mzmon
   ```

   Each header sets exactly one of `value` or `valueEnv`. `value` renders into the
   gateway's configuration in plaintext, so keep it for routing headers such as
   the dataset; `valueEnv` names an environment variable the gateway reads at
   startup, which is where the credential belongs. The variable name is yours to
   pick.

1. Create the gateway Secret with the API key. The chart does not create it, and
   mounts it optionally, so a wrong name or namespace is ignored silently rather
   than failing:

   ```bash
   kubectl create secret generic mzmon-alloy-gateway-env \
     --namespace monitoring \
     --from-literal=GATEWAY_OTEL_DEST_HONEYCOMB_API_KEY='<your-honeycomb-api-key>'
   ```

The chart validates the header shape at render time: an empty header list, a
header missing its `key`, a header setting both `value` and `valueEnv` or neither,
and a `valueEnv` that nothing could supply all fail the install rather than
authenticating with an empty header at run time.

A ready-made starting point for exactly this setup lives at
[`otlp-metrics-honeycomb.values.yaml`
⧉](https://github.com/MaterializeInc/materialize-monitoring/blob/main/charts/materialize-monitoring/profiles/otlp-metrics-honeycomb.values.yaml).

## See also

- [OpenTelemetry](/manage/monitor/self-managed/opentelemetry/), for OTLP
  destinations generally, including bearer-token authentication and your own
  collector.

- [How logs and metrics are stored](/manage/monitor/self-managed/storage/), for the
  bundled stores and the other backends you can send metrics and logs to.

- [Alerting](/manage/monitor/self-managed/alerting/), for the metrics and
  thresholds to alert on.
