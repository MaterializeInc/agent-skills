# Monitoring and alerting

Monitor the performance of your Materialize region with Datadog and Grafana.

## Cloud

### Monitoring

You can monitor the performance and overall health of your Materialize region.
To help you get started, the following guides are available:

- [Datadog](/observability/cloud/datadog/)

- [Grafana](/observability/cloud/grafana/)

### Alerting

After setting up a monitoring tool, you can configure alert rules. Alert rules
send a notification when a metric surpasses a threshold. This will help you
prevent operational incidents. For alert rules guidelines, see
[Alerting](/observability/cloud/alerting/).

## Self-Managed

### Monitoring

You can monitor the performance and overall health of your Self-Managed
Materialize.

The Materialize Terraform modules ([AWS
⧉](https://github.com/MaterializeInc/materialize-terraform-self-managed/tree/main/aws),
[Azure
⧉](https://github.com/MaterializeInc/materialize-terraform-self-managed/tree/main/azure),
[GCP
⧉](https://github.com/MaterializeInc/materialize-terraform-self-managed/tree/main/gcp))
install a monitoring stack alongside your deployment. It is enabled by default
starting with v11.0.0 of the Materialize Terraform Modules. For the module
install steps, see [Install using Terraform
modules](/self-managed-deployments/installation/#install-using-terraform-modules).

The stack collects metrics and logs from Materialize and from the cluster,
stores them in your own infrastructure, and ships dashboards to query them:

- [How logs and metrics are stored](/observability/self-managed/storage/), including
  the backends you can forward them to.

- [Grafana](/observability/self-managed/grafana/), the dashboards and query
  interface that ship with the stack.

- [Alerting](/observability/self-managed/alerting/), the bundled alert rules
  and the Alertmanager that routes them to your receivers.

To configure the stack outside the Materialize Terraform modules, or to see the
full set of module variables, see the [`materialize-monitoring` Terraform
installation guide
⧉](https://materializeinc.github.io/materialize-monitoring/getting-started/terraform/).

To send metrics and logs to a platform you already run, a guide is available for
each destination:

- [Datadog](/observability/self-managed/datadog/)

- [Honeycomb](/observability/self-managed/honeycomb/)

- [OpenTelemetry](/observability/self-managed/opentelemetry/), for any other OTLP
  endpoint, including your own collector.

- [Google Cloud Monitoring](/observability/self-managed/google-cloud-monitoring/)

- [Prometheus remote
  write](/observability/self-managed/prometheus-remote-write/), for Mimir,
  Amazon Managed Prometheus, Grafana Cloud, or a Thanos you run elsewhere.

### Alerting

The monitoring stack installs Alertmanager and a default set of alert rules for
Materialize and the Kubernetes platform under it. A default install configures
no receiver, so no one is notified until you configure one. To route alerts to
PagerDuty, Slack, Microsoft Teams, email, or a webhook, see
[Alerting](/observability/self-managed/alerting/). To route, tune, and silence
them further, see [Customize
alerting](/observability/self-managed/customize-alerting/).

If you alert from a platform you already run instead, see [Thresholds for alerts
you build yourself](/observability/self-managed/alerting/#thresholds).

## Pages in this section

- [Appendix: Metrics](/observability/appendix-metrics/index.md): Reference list of the Prometheus metrics exposed by Materialize.
- [Cloud](/observability/cloud/index.md): Monitoring and alerting for Materialize Cloud
- [Essential metrics](/observability/essential-metrics/index.md): The Prometheus metrics Materialize recommends building dashboards and alerts on.
- [Replica resource usage](/observability/replica-resource-usage/index.md): The per-process memory, swap and disk observations a cluster replica reports about itself, and how to interpret them.
- [Self-Managed](/observability/self-managed/index.md): Monitor and alert on Self-Managed Materialize with the bundled monitoring stack or your own observability platform.
