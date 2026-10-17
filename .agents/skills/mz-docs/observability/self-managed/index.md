# Self-Managed

Monitor and alert on Self-Managed Materialize with the bundled monitoring stack or your own observability platform.

This section covers monitoring and alerting for Self-Managed Materialize.

## Built-in monitoring stack

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

## Deliver data to your observability platform

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

## Alerting

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

- [Alerting](/observability/self-managed/alerting/index.md): How to send the alerts the Self-Managed Materialize monitoring stack raises to PagerDuty, Slack, Microsoft Teams, email, or a webhook, and which thresholds to alert on in another platform.
- [Customize alerting](/observability/self-managed/customize-alerting/index.md): How to route, tune, and silence the alerts the Self-Managed Materialize monitoring stack raises.
- [Datadog](/observability/self-managed/datadog/index.md): How to monitor the performance and overall health of Self-Managed Materialize using Datadog.
- [Google Cloud Monitoring](/observability/self-managed/google-cloud-monitoring/index.md): How to monitor the performance and overall health of Self-Managed Materialize using Google Cloud Monitoring.
- [Grafana](/observability/self-managed/grafana/index.md): How to enable, reach, and use the Grafana that ships with the Self-Managed Materialize monitoring stack.
- [Honeycomb](/observability/self-managed/honeycomb/index.md): How to monitor the performance and overall health of Self-Managed Materialize using Honeycomb.
- [How logs and metrics are stored and delivered](/observability/self-managed/storage/index.md): Where Self-Managed Materialize stores the metrics and logs it collects, and the backends it can forward them to.
- [OpenTelemetry](/observability/self-managed/opentelemetry/index.md): How to push metrics and logs from Self-Managed Materialize to any OpenTelemetry-compatible destination.
- [Prometheus remote write](/observability/self-managed/prometheus-remote-write/index.md): How to send metrics from Self-Managed Materialize to an external Prometheus remote-write store such as Mimir, Amazon Managed Prometheus, or Grafana Cloud.
