# Monitoring and alerting

Monitor the performance of your Materialize region with Datadog and Grafana.

## Cloud

### Monitoring

You can monitor the performance and overall health of your Materialize region.
To help you get started, the following guides are available:

- [Datadog](/manage/monitor/cloud/datadog/)

- [Grafana](/manage/monitor/cloud/grafana/)

### Alerting

After setting up a monitoring tool, you can configure alert rules. Alert rules
send a notification when a metric surpasses a threshold. This will help you
prevent operational incidents. For alert rules guidelines, see
[Alerting](/manage/monitor/cloud/alerting/).

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

- [How logs and metrics are stored](/manage/monitor/self-managed/storage/), including
  the backends you can forward them to.

- [Grafana](/manage/monitor/self-managed/grafana/), the dashboards and query
  interface that ship with the stack.

To configure the stack outside the Materialize Terraform modules, or to see the
full set of module variables, see the [`materialize-monitoring` Terraform
installation guide
⧉](https://materializeinc.github.io/materialize-monitoring/getting-started/terraform/).

To send metrics and logs to a platform you already run, a guide is available for
each destination:

- [Datadog](/manage/monitor/self-managed/datadog/)

- [Honeycomb](/manage/monitor/self-managed/honeycomb/)

- [OpenTelemetry](/manage/monitor/self-managed/opentelemetry/), for any other OTLP
  endpoint, including your own collector.

- [Google Cloud Monitoring](/manage/monitor/self-managed/google-cloud-monitoring/)

- [Prometheus remote
  write](/manage/monitor/self-managed/prometheus-remote-write/), for Mimir,
  Amazon Managed Prometheus, Grafana Cloud, or a Thanos you run elsewhere.

### Alerting

After setting up a monitoring tool, you can configure alert rules. Alert rules
send a notification when a metric surpasses a threshold. This will help you
prevent operational incidents. For alert rules guidelines, see
[Alerting](/manage/monitor/self-managed/alerting/).

---

## Appendix: Metrics

This page lists the Prometheus metrics exposed by Materialize, along with their
descriptions. A `*` in a metric name denotes a family of metrics
whose name is completed at runtime (for example, `mz_persist_*_bytes`).

<table>
  <thead>
    <tr>
      <th>Metric</th>
      <th>Description</th>
      <th>Labels</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>*_postgres_connpool_acquire_seconds</code></td>
      <td>time spent acquiring connections from pool</td>
      <td></td>
    </tr>
    <tr>
      <td><code>*_postgres_connpool_acquires</code></td>
      <td>times a connection has been acquired from pool</td>
      <td></td>
    </tr>
    <tr>
      <td><code>*_postgres_connpool_available</code></td>
      <td>available connections in the pool</td>
      <td></td>
    </tr>
    <tr>
      <td><code>*_postgres_connpool_connection_errors</code></td>
      <td>number of errors when establishing a new connection</td>
      <td></td>
    </tr>
    <tr>
      <td><code>*_postgres_connpool_connections_created</code></td>
      <td>times a connection was created</td>
      <td></td>
    </tr>
    <tr>
      <td><code>*_postgres_connpool_size</code></td>
      <td>number of connections currently in pool</td>
      <td></td>
    </tr>
    <tr>
      <td><code>*_postgres_connpool_ttl_reconnections</code></td>
      <td>times a connection was recycled due to ttl</td>
      <td></td>
    </tr>
    <tr>
      <td><code>*_request_duration_seconds_bucket</code></td>
      <td>How long it takes for a request to complete in seconds.</td>
      <td><code>le</code>, <code>path</code>, <code>source</code></td>
    </tr>
    <tr>
      <td><code>*_request_duration_seconds_count</code></td>
      <td>How long it takes for a request to complete in seconds.</td>
      <td><code>path</code>, <code>source</code></td>
    </tr>
    <tr>
      <td><code>*_request_duration_seconds_sum</code></td>
      <td>How long it takes for a request to complete in seconds.</td>
      <td><code>path</code>, <code>source</code></td>
    </tr>
    <tr>
      <td><code>*_requests_active</code></td>
      <td>Number of currently active/open http requests.</td>
      <td><code>path</code>, <code>source</code></td>
    </tr>
    <tr>
      <td><code>*_requests_total</code></td>
      <td>Total number of http requests received since process start.</td>
      <td><code>path</code>, <code>source</code>, <code>status</code></td>
    </tr>
    <tr>
      <td><code>environmentd_needs_update</code></td>
      <td>Count of organizations in this cluster which are running outdated pod templates. Only the operator replica holding the leadership lease reconciles, so the others report zero.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>jemalloc_active</code></td>
      <td>Total number of bytes in active pages allocated by the application</td>
      <td></td>
    </tr>
    <tr>
      <td><code>jemalloc_allocated</code></td>
      <td>Total number of bytes allocated by the application</td>
      <td></td>
    </tr>
    <tr>
      <td><code>jemalloc_metadata</code></td>
      <td>Total number of bytes dedicated to metadata.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>jemalloc_resident</code></td>
      <td>Maximum number of bytes in physically resident data pages mapped</td>
      <td></td>
    </tr>
    <tr>
      <td><code>jemalloc_retained</code></td>
      <td>Total number of bytes in virtual memory mappings</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_active_copy_tos</code></td>
      <td>The number of active COPY TO queries.</td>
      <td><code>session_type</code></td>
    </tr>
    <tr>
      <td><code>mz_active_internal_subscribes</code></td>
      <td>The number of active internal subscribes used by read-then-write operations and background maintenance.</td>
      <td><code>session_type</code></td>
    </tr>
    <tr>
      <td><code>mz_active_sessions</code></td>
      <td>The number of active coordinator sessions.</td>
      <td><code>session_type</code></td>
    </tr>
    <tr>
      <td><code>mz_active_subscribes</code></td>
      <td>The number of active SUBSCRIBE queries.</td>
      <td><code>session_type</code></td>
    </tr>
    <tr>
      <td><code>mz_adapter_commands</code></td>
      <td>The total number of adapter commands issued of the given type since process start.</td>
      <td><code>application_name</code>, <code>command_type</code>, <code>status</code></td>
    </tr>
    <tr>
      <td><code>mz_append_table_duration_seconds_bucket</code></td>
      <td>Latency for appending to any (user or system) table.</td>
      <td><code>le</code></td>
    </tr>
    <tr>
      <td><code>mz_append_table_duration_seconds_count</code></td>
      <td>Latency for appending to any (user or system) table.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_append_table_duration_seconds_sum</code></td>
      <td>Latency for appending to any (user or system) table.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_apply_catalog_implications_seconds_bucket</code></td>
      <td>The time it takes to apply catalog implications.</td>
      <td><code>le</code></td>
    </tr>
    <tr>
      <td><code>mz_apply_catalog_implications_seconds_count</code></td>
      <td>The time it takes to apply catalog implications.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_apply_catalog_implications_seconds_sum</code></td>
      <td>The time it takes to apply catalog implications.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_arrangement_maintenance_active_info</code></td>
      <td>Whether maintenance is currently occuring.</td>
      <td><code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_arrangement_maintenance_seconds_total</code></td>
      <td>The total time spent maintaining arrangements.</td>
      <td><code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_arrangement_sizes_collection_time_seconds_bucket</code></td>
      <td>Seconds to read mz_object_arrangement_sizes and prepare history records for one snapshot.</td>
      <td><code>le</code></td>
    </tr>
    <tr>
      <td><code>mz_arrangement_sizes_collection_time_seconds_count</code></td>
      <td>Seconds to read mz_object_arrangement_sizes and prepare history records for one snapshot.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_arrangement_sizes_collection_time_seconds_sum</code></td>
      <td>Seconds to read mz_object_arrangement_sizes and prepare history records for one snapshot.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_arrangement_sizes_rows_written_total</code></td>
      <td>Total rows appended to mz_object_arrangement_size_history since process start.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_auth_refresh_tasks_active</code></td>
      <td>The number of active refresh tasks we have running.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_auth_request_count</code></td>
      <td>Total number of HTTP requests made to Frontegg for authentication</td>
      <td><code>path</code>, <code>status</code></td>
    </tr>
    <tr>
      <td><code>mz_auth_request_duration_seconds_bucket</code></td>
      <td>How long it takes for a request to Frontegg to complete in seconds.</td>
      <td><code>le</code>, <code>path</code></td>
    </tr>
    <tr>
      <td><code>mz_auth_request_duration_seconds_count</code></td>
      <td>How long it takes for a request to Frontegg to complete in seconds.</td>
      <td><code>path</code></td>
    </tr>
    <tr>
      <td><code>mz_auth_request_duration_seconds_sum</code></td>
      <td>How long it takes for a request to Frontegg to complete in seconds.</td>
      <td><code>path</code></td>
    </tr>
    <tr>
      <td><code>mz_auth_session_refresh_count</code></td>
      <td>Total number of authentication sessions that get refreshed.</td>
      <td><code>outstanding_receivers</code>, <code>recent_drop</code></td>
    </tr>
    <tr>
      <td><code>mz_auth_session_request_count</code></td>
      <td>Total number of session start requests the Authenticator has received.</td>
      <td><code>existing_session</code></td>
    </tr>
    <tr>
      <td><code>mz_balancer_connection_active</code></td>
      <td>Count of currently open network connections.</td>
      <td><code>source</code></td>
    </tr>
    <tr>
      <td><code>mz_balancer_connection_status</code></td>
      <td>Count of completed network connections, by status</td>
      <td><code>source</code>, <code>status</code></td>
    </tr>
    <tr>
      <td><code>mz_balancer_metadata_seconds</code></td>
      <td>server uptime, labels are build metadata</td>
      <td><code>build_type</code>, <code>version</code></td>
    </tr>
    <tr>
      <td><code>mz_balancer_tenant_connection_active</code></td>
      <td>Count of opened network connections by tenant.</td>
      <td><code>source</code>, <code>tenant</code></td>
    </tr>
    <tr>
      <td><code>mz_balancer_tenant_connection_rx</code></td>
      <td>Number of bytes received from a client for a tenant.</td>
      <td><code>source</code>, <code>tenant</code></td>
    </tr>
    <tr>
      <td><code>mz_balancer_tenant_connection_tx</code></td>
      <td>Number of bytes sent to a client for a tenant.</td>
      <td><code>source</code>, <code>tenant</code></td>
    </tr>
    <tr>
      <td><code>mz_balancer_tenant_pgwire_sni_count</code></td>
      <td>Count of pgwire connections that have and do not have SNI available per tenant.</td>
      <td><code>has_sni</code>, <code>tenant</code></td>
    </tr>
    <tr>
      <td><code>mz_bytes_read_total</code></td>
      <td>Count of bytes read from sources</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_canceled_peeks_total</code></td>
      <td>The total number of canceled peeks since process start.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_catalog_allocate_id_seconds_bucket</code></td>
      <td>The time it takes to allocate IDs in the durable catalog.</td>
      <td><code>le</code></td>
    </tr>
    <tr>
      <td><code>mz_catalog_allocate_id_seconds_count</code></td>
      <td>The time it takes to allocate IDs in the durable catalog.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_catalog_allocate_id_seconds_sum</code></td>
      <td>The time it takes to allocate IDs in the durable catalog.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_catalog_arc_strong_count</code></td>
      <td>The number of strong references to the current catalog snapshot: roughly, in-flight users plus a small constant baseline.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_catalog_arc_weak_count</code></td>
      <td>The number of weak references to the current catalog snapshot: sessions whose snapshot cache points at the current catalog version (older versions are not counted). Drops on catalog changes and recovers as session caches repopulate.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_catalog_collection_entries</code></td>
      <td>Total number of entries, after consolidation, per catalog collection.</td>
      <td><code>collection</code></td>
    </tr>
    <tr>
      <td><code>mz_catalog_info_metrics_reconcile_seconds_bucket</code></td>
      <td>Time taken to rebuild the catalog info metrics from a catalog snapshot.</td>
      <td><code>le</code></td>
    </tr>
    <tr>
      <td><code>mz_catalog_info_metrics_reconcile_seconds_count</code></td>
      <td>Time taken to rebuild the catalog info metrics from a catalog snapshot.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_catalog_info_metrics_reconcile_seconds_sum</code></td>
      <td>Time taken to rebuild the catalog info metrics from a catalog snapshot.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_catalog_snapshot_cache</code></td>
      <td>Hits and misses of the session-side catalog snapshot cache. A miss costs a Coordinator round-trip.</td>
      <td><code>context</code>, <code>result</code></td>
    </tr>
    <tr>
      <td><code>mz_catalog_snapshot_consolidations</code></td>
      <td>Count of snapshot consolidation passes.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_catalog_snapshot_latency_seconds_bucket</code></td>
      <td>Latency for fetching a snapshot of the durable catalog.</td>
      <td><code>le</code></td>
    </tr>
    <tr>
      <td><code>mz_catalog_snapshot_latency_seconds_count</code></td>
      <td>Latency for fetching a snapshot of the durable catalog.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_catalog_snapshot_latency_seconds_sum</code></td>
      <td>Latency for fetching a snapshot of the durable catalog.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_catalog_snapshot_max_entries</code></td>
      <td>High-water mark of entries in the unconsolidated in-memory snapshot since process start.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_catalog_snapshot_seconds_bucket</code></td>
      <td>The time it takes to fetch a catalog snapshot from the Coordinator. Only observed on session snapshot cache misses.</td>
      <td><code>context</code>, <code>le</code></td>
    </tr>
    <tr>
      <td><code>mz_catalog_snapshot_seconds_count</code></td>
      <td>The time it takes to fetch a catalog snapshot from the Coordinator. Only observed on session snapshot cache misses.</td>
      <td><code>context</code></td>
    </tr>
    <tr>
      <td><code>mz_catalog_snapshot_seconds_sum</code></td>
      <td>The time it takes to fetch a catalog snapshot from the Coordinator. Only observed on session snapshot cache misses.</td>
      <td><code>context</code></td>
    </tr>
    <tr>
      <td><code>mz_catalog_snapshots_taken</code></td>
      <td>Count of snapshots taken.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_catalog_sync_latency_seconds_bucket</code></td>
      <td>Latency for syncing the in-memory state of the durable catalog with the persisted contents.</td>
      <td><code>le</code></td>
    </tr>
    <tr>
      <td><code>mz_catalog_sync_latency_seconds_count</code></td>
      <td>Latency for syncing the in-memory state of the durable catalog with the persisted contents.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_catalog_sync_latency_seconds_sum</code></td>
      <td>Latency for syncing the in-memory state of the durable catalog with the persisted contents.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_catalog_syncs</code></td>
      <td>Count of catalog syncs.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_catalog_transact_phase_seconds_bucket</code></td>
      <td>Wall time of the individual phases of a coordinator catalog transaction, to attribute where transact time is spent. Phases overlap and do not sum to mz_catalog_transact_seconds. The transact phase includes the durable catalog sync and commit.</td>
      <td><code>le</code>, <code>phase</code></td>
    </tr>
    <tr>
      <td><code>mz_catalog_transact_phase_seconds_count</code></td>
      <td>Wall time of the individual phases of a coordinator catalog transaction, to attribute where transact time is spent. Phases overlap and do not sum to mz_catalog_transact_seconds. The transact phase includes the durable catalog sync and commit.</td>
      <td><code>phase</code></td>
    </tr>
    <tr>
      <td><code>mz_catalog_transact_phase_seconds_sum</code></td>
      <td>Wall time of the individual phases of a coordinator catalog transaction, to attribute where transact time is spent. Phases overlap and do not sum to mz_catalog_transact_seconds. The transact phase includes the durable catalog sync and commit.</td>
      <td><code>phase</code></td>
    </tr>
    <tr>
      <td><code>mz_catalog_transact_seconds_bucket</code></td>
      <td>The time it takes to run various catalog transact methods.</td>
      <td><code>le</code>, <code>method</code></td>
    </tr>
    <tr>
      <td><code>mz_catalog_transact_seconds_count</code></td>
      <td>The time it takes to run various catalog transact methods.</td>
      <td><code>method</code></td>
    </tr>
    <tr>
      <td><code>mz_catalog_transact_seconds_sum</code></td>
      <td>The time it takes to run various catalog transact methods.</td>
      <td><code>method</code></td>
    </tr>
    <tr>
      <td><code>mz_catalog_transaction_commit_latency_seconds_bucket</code></td>
      <td>Latency for committing a durable catalog transaction.</td>
      <td><code>le</code></td>
    </tr>
    <tr>
      <td><code>mz_catalog_transaction_commit_latency_seconds_count</code></td>
      <td>Latency for committing a durable catalog transaction.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_catalog_transaction_commit_latency_seconds_sum</code></td>
      <td>Latency for committing a durable catalog transaction.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_catalog_transaction_commits</code></td>
      <td>Count of transaction commits.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_catalog_transactions_started</code></td>
      <td>Total number of started transactions.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_cluster_handle_command_duration_seconds_bucket</code></td>
      <td>Time spent in handling commands.</td>
      <td><code>cluster</code>, <code>command_type</code>, <code>le</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_cluster_handle_command_duration_seconds_count</code></td>
      <td>Time spent in handling commands.</td>
      <td><code>cluster</code>, <code>command_type</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_cluster_handle_command_duration_seconds_sum</code></td>
      <td>Time spent in handling commands.</td>
      <td><code>cluster</code>, <code>command_type</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_cluster_info</code></td>
      <td>Maps cluster IDs to the cluster&#39;s name and size. Constant 1.</td>
      <td><code>cluster_id</code>, <code>name</code>, <code>size</code></td>
    </tr>
    <tr>
      <td><code>mz_cluster_server_last_command_received</code></td>
      <td>The time (in seconds since the Unix epoch) at which the server last received data from the controller, including CTP keepalives. Used to detect controller connections that are no longer reachable.</td>
      <td><code>server_name</code></td>
    </tr>
    <tr>
      <td><code>mz_column_pager_budget_configured_bytes</code></td>
      <td>Most-recently-configured total budget for the column-pager tiered policy.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_column_pager_budget_remaining_bytes</code></td>
      <td>Bytes the column-pager tiered policy currently has available for resident columns.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_column_pager_paged_bytes_in_total</code></td>
      <td>Total uncompressed bytes handed to the pager for pageout, before any codec is applied.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_column_pager_paged_bytes_out_total</code></td>
      <td>Total on-storage bytes after codec / padding.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_column_pager_pagein_bytes_total</code></td>
      <td>Total uncompressed bytes delivered by page-in.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_column_pager_pageins_total</code></td>
      <td>Successful page-ins from `ColumnPager::take`.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_column_pager_pageouts_total</code></td>
      <td>Pager decisions that paged the chunk out.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_column_pager_resident_released_bytes_total</code></td>
      <td>Total bytes returned to the budget by ticket drops.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_column_pager_resident_released_total</code></td>
      <td>Resident-ticket drops returning budget.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_column_pager_skip_bytes_total</code></td>
      <td>Total bytes kept resident by skip decisions.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_column_pager_skip_decisions_total</code></td>
      <td>Pager decisions that kept the chunk resident.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_column_pool_admissions_budget_total</code></td>
      <td>Evicted chunks re-admitted to compressed-but-resident by an admitting read out of free budget headroom.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_column_pool_admissions_denied_total</code></td>
      <td>Admitting reads that found neither budget headroom nor a clean victim and were served as a plain decompress instead.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_column_pool_admissions_steal_total</code></td>
      <td>Evicted chunks re-admitted by an admitting read stealing the slot of a clean backed victim of the same size class.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_column_pool_eager_backs_total</code></td>
      <td>Chunks eagerly compressed to compressed-but-resident by idle spill threads; their later eviction is a pure page release.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_column_pool_evictions_cheap_total</code></td>
      <td>Evictions of already-backed chunks: physical pages released with no compression or extent write.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_column_pool_evictions_compress_total</code></td>
      <td>Evictions that compressed a chunk into a new swap-backed extent.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_column_pool_extent_arena_fallbacks_total</code></td>
      <td>Extent writes that fell back to the heap because their extent-arena class had no free slot. Heap-backed extents are never paged out.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_column_pool_extent_bytes_written_total</code></td>
      <td>Compressed bytes written into swap-backed extents.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_column_pool_extent_pageout_incomplete_total</code></td>
      <td>Pageout passes whose residency observation found pages still resident. Climbing steadily means pages cannot reach the swap device.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_column_pool_extent_pageouts_total</code></td>
      <td>Extents pushed to the swap device by RSS-target enforcement.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_column_pool_extent_resident_bytes</code></td>
      <td>Allocation bytes of compressed extents currently resident (the compressed-but-resident tier), bounded by the pool RSS target.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_column_pool_extent_unreclaimable_bytes</code></td>
      <td>Allocation bytes of resident extents the RSS target cannot push out (retry-capped and heap-fallback extents). Climbing steadily means pages cannot reach the swap device.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_column_pool_frees_total</code></td>
      <td>Chunks freed from the buffer pool.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_column_pool_inserts_total</code></td>
      <td>Chunks inserted into the buffer pool.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_column_pool_live_chunks</code></td>
      <td>Live pool chunks, whatever their residency: for backlog-shaped consumers, the un-drained backlog in chunks.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_column_pool_oversize_bytes</code></td>
      <td>Bytes held by oversize chunks that bypass pool paging.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_column_pool_oversize_payloads_total</code></td>
      <td>Inserts that went to unpageable heap chunks because the payload was larger than the largest size class.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_column_pool_resident_bytes</code></td>
      <td>Uncompressed bytes resident in the buffer pool.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_column_pool_slot_exhausted_fallbacks_total</code></td>
      <td>Inserts that fell back to unpageable heap chunks because their size class had no free slot.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_column_pool_spill_cancelled_total</code></td>
      <td>Compressions cancelled by a concurrent free, whatever their origin (budget eviction or eager backing), so this can exceed the scheduled count.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_column_pool_spill_in_flight</code></td>
      <td>Spill entries queued or being processed.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_column_pool_spill_scheduled_total</code></td>
      <td>Evictions handed to buffer-pool spill threads.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_column_pool_warm_bytes</code></td>
      <td>Class bytes of free slots kept warm for fault-free reuse; RSS exceeds resident bytes by up to this bounded amount.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_column_pool_warm_reuses_total</code></td>
      <td>Slot allocations served from the warm list: no page faults, no kernel page zeroing.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_column_pool_writes_elided_total</code></td>
      <td>Backing writes elided: chunks freed while unbacked or while queued for a spill thread, dead before their compression completed.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_compute_collection_count</code></td>
      <td>The number and hydration status of maintained compute collections.</td>
      <td><code>hydrated</code>, <code>type</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_compute_command_message_bytes_total</code></td>
      <td>The total number of bytes sent in compute command messages.</td>
      <td><code>instance_id</code>, <code>replica_id</code></td>
    </tr>
    <tr>
      <td><code>mz_compute_commands_total</code></td>
      <td>The total number of compute commands sent.</td>
      <td><code>command_type</code>, <code>instance_id</code>, <code>replica_id</code></td>
    </tr>
    <tr>
      <td><code>mz_compute_controller_collection_count</code></td>
      <td>The number of installed compute collections.</td>
      <td><code>instance_id</code></td>
    </tr>
    <tr>
      <td><code>mz_compute_controller_collection_unscheduled_count</code></td>
      <td>The number of installed but unscheduled compute collections.</td>
      <td><code>instance_id</code></td>
    </tr>
    <tr>
      <td><code>mz_compute_controller_command_queue_size</code></td>
      <td>The size of the compute command queue.</td>
      <td><code>instance_id</code>, <code>replica_id</code></td>
    </tr>
    <tr>
      <td><code>mz_compute_controller_connected_replica_count</code></td>
      <td>The number of replicas successfully connected to the compute controller.</td>
      <td><code>instance_id</code></td>
    </tr>
    <tr>
      <td><code>mz_compute_controller_copy_to_count</code></td>
      <td>The number of active copy tos.</td>
      <td><code>instance_id</code></td>
    </tr>
    <tr>
      <td><code>mz_compute_controller_history_command_count</code></td>
      <td>The number of commands in the controller&#39;s command history.</td>
      <td><code>command_type</code>, <code>instance_id</code></td>
    </tr>
    <tr>
      <td><code>mz_compute_controller_history_dataflow_count</code></td>
      <td>The number of dataflows in the controller&#39;s command history.</td>
      <td><code>instance_id</code></td>
    </tr>
    <tr>
      <td><code>mz_compute_controller_hydration_queue_size</code></td>
      <td>The size of the compute hydration queue.</td>
      <td><code>instance_id</code>, <code>replica_id</code></td>
    </tr>
    <tr>
      <td><code>mz_compute_controller_peek_count</code></td>
      <td>The number of pending peeks.</td>
      <td><code>instance_id</code></td>
    </tr>
    <tr>
      <td><code>mz_compute_controller_replica_connect_wait_time_seconds_total</code></td>
      <td>The total time the compute controller spent waiting for replica (re-)connection.</td>
      <td><code>instance_id</code>, <code>replica_id</code></td>
    </tr>
    <tr>
      <td><code>mz_compute_controller_replica_connects_total</code></td>
      <td>The total number of replica (re-)connections made by the compute controller.</td>
      <td><code>instance_id</code>, <code>replica_id</code></td>
    </tr>
    <tr>
      <td><code>mz_compute_controller_replica_count</code></td>
      <td>The number of replicas.</td>
      <td><code>instance_id</code></td>
    </tr>
    <tr>
      <td><code>mz_compute_controller_response_recv_count</code></td>
      <td>The number of receives on the compute response queue.</td>
      <td><code>instance_id</code></td>
    </tr>
    <tr>
      <td><code>mz_compute_controller_response_send_count</code></td>
      <td>The number of sends on the compute response queue.</td>
      <td><code>instance_id</code></td>
    </tr>
    <tr>
      <td><code>mz_compute_controller_subscribe_count</code></td>
      <td>The number of active subscribes.</td>
      <td><code>instance_id</code></td>
    </tr>
    <tr>
      <td><code>mz_compute_peek_duration_seconds_bucket</code></td>
      <td>A histogram of peek durations since restart.</td>
      <td><code>instance_id</code>, <code>le</code>, <code>result</code></td>
    </tr>
    <tr>
      <td><code>mz_compute_peek_duration_seconds_count</code></td>
      <td>A histogram of peek durations since restart.</td>
      <td><code>instance_id</code>, <code>result</code></td>
    </tr>
    <tr>
      <td><code>mz_compute_peek_duration_seconds_sum</code></td>
      <td>A histogram of peek durations since restart.</td>
      <td><code>instance_id</code>, <code>result</code></td>
    </tr>
    <tr>
      <td><code>mz_compute_peeks_total</code></td>
      <td>The total number of peeks served.</td>
      <td><code>instance_id</code>, <code>result</code></td>
    </tr>
    <tr>
      <td><code>mz_compute_reconciliation_replaced_dataflows_count_total</code></td>
      <td>The total number of dataflows that were replaced during compute reconciliation.</td>
      <td><code>reason</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_compute_reconciliation_reused_dataflows_count_total</code></td>
      <td>The total number of dataflows that were reused during compute reconciliation.</td>
      <td><code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_compute_replica_history_command_count</code></td>
      <td>The number of commands in the replica&#39;s command history.</td>
      <td><code>command_type</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_compute_replica_history_dataflow_count</code></td>
      <td>The number of dataflows in the replica&#39;s command history.</td>
      <td><code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_compute_response_message_bytes_total</code></td>
      <td>The total number of bytes sent in compute response messages.</td>
      <td><code>instance_id</code>, <code>replica_id</code></td>
    </tr>
    <tr>
      <td><code>mz_compute_responses_total</code></td>
      <td>The total number of compute responses sent.</td>
      <td><code>instance_id</code>, <code>replica_id</code>, <code>response_type</code></td>
    </tr>
    <tr>
      <td><code>mz_connection_status</code></td>
      <td>Count of completed network connections, by status</td>
      <td><code>source</code>, <code>status</code></td>
    </tr>
    <tr>
      <td><code>mz_coord_queue_busy_seconds_bucket</code></td>
      <td>The number of seconds the coord queue was processing before it was empty. This is a sampled metric and does not measure the full coord queue wait/idle times.</td>
      <td><code>le</code></td>
    </tr>
    <tr>
      <td><code>mz_coord_queue_busy_seconds_count</code></td>
      <td>The number of seconds the coord queue was processing before it was empty. This is a sampled metric and does not measure the full coord queue wait/idle times.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_coord_queue_busy_seconds_sum</code></td>
      <td>The number of seconds the coord queue was processing before it was empty. This is a sampled metric and does not measure the full coord queue wait/idle times.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_coordinator_message_batch_size_bucket</code></td>
      <td>Message batch size handled by the coordinator.</td>
      <td><code>le</code></td>
    </tr>
    <tr>
      <td><code>mz_coordinator_message_batch_size_count</code></td>
      <td>Message batch size handled by the coordinator.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_coordinator_message_batch_size_sum</code></td>
      <td>Message batch size handled by the coordinator.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_dataflow_events_read_total</code></td>
      <td>Count of events we have read from the wire</td>
      <td><code>format</code>, <code>status</code></td>
    </tr>
    <tr>
      <td><code>mz_dataflow_replica_expiration_remaining_seconds</code></td>
      <td>The remaining seconds until replica expiration. Can go negative, can lag behind.</td>
      <td><code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_dataflow_replica_expiration_timestamp_seconds</code></td>
      <td>The replica expiration timestamp in seconds since epoch.</td>
      <td><code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_dataflow_shared_row_heap_capacity_bytes</code></td>
      <td>The heap capacity of the shared row.</td>
      <td><code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_dataflow_wallclock_lag_seconds</code></td>
      <td>A summary of the second-by-second lag of the dataflow frontier relative to wallclock time, aggregated over the last minute.</td>
      <td><code>collection_id</code>, <code>instance_id</code>, <code>quantile</code>, <code>replica_id</code></td>
    </tr>
    <tr>
      <td><code>mz_dataflow_wallclock_lag_seconds_count</code></td>
      <td>The total count of dataflow wallclock lag measurements.</td>
      <td><code>collection_id</code>, <code>instance_id</code>, <code>replica_id</code></td>
    </tr>
    <tr>
      <td><code>mz_dataflow_wallclock_lag_seconds_sum</code></td>
      <td>The total sum of dataflow wallclock lag measurements.</td>
      <td><code>collection_id</code>, <code>instance_id</code>, <code>replica_id</code></td>
    </tr>
    <tr>
      <td><code>mz_determine_timestamp</code></td>
      <td>The total number of calls to determine_timestamp.</td>
      <td><code>compute_instance</code>, <code>isolation_level</code>, <code>respond_immediately</code></td>
    </tr>
    <tr>
      <td><code>mz_group_commit_catalog_upper_seconds_bucket</code></td>
      <td>The time it takes to advance the catalog shard upper for a txns-shard write (group commits and table register/forget).</td>
      <td><code>le</code></td>
    </tr>
    <tr>
      <td><code>mz_group_commit_catalog_upper_seconds_count</code></td>
      <td>The time it takes to advance the catalog shard upper for a txns-shard write (group commits and table register/forget).</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_group_commit_catalog_upper_seconds_sum</code></td>
      <td>The time it takes to advance the catalog shard upper for a txns-shard write (group commits and table register/forget).</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_hydration_history_mutations_total</code></td>
      <td>Total hydration-history collection and retention mutations since process start.</td>
      <td><code>operation</code>, <code>outcome</code></td>
    </tr>
    <tr>
      <td><code>mz_hydration_history_retention_batch_full_total</code></td>
      <td>Total hydration-history retention batches that were full. Repeated increments mean retention may not be keeping up with its schedule.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_hydration_history_rows_affected_total</code></td>
      <td>Total rows changed by hydration-history maintenance since process start.</td>
      <td><code>action</code></td>
    </tr>
    <tr>
      <td><code>mz_hydration_history_sweep_duration_seconds_bucket</code></td>
      <td>Wall time of a complete hydration-history collection and retention sweep.</td>
      <td><code>le</code></td>
    </tr>
    <tr>
      <td><code>mz_hydration_history_sweep_duration_seconds_count</code></td>
      <td>Wall time of a complete hydration-history collection and retention sweep.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_hydration_history_sweep_duration_seconds_sum</code></td>
      <td>Wall time of a complete hydration-history collection and retention sweep.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_index_peek_cursor_setup_seconds_bucket</code></td>
      <td>Time opening the trace cursor and sorting the literal constraints, excluding the seek to those literals.</td>
      <td><code>le</code></td>
    </tr>
    <tr>
      <td><code>mz_index_peek_cursor_setup_seconds_count</code></td>
      <td>Time opening the trace cursor and sorting the literal constraints, excluding the seek to those literals.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_index_peek_cursor_setup_seconds_sum</code></td>
      <td>Time opening the trace cursor and sorting the literal constraints, excluding the seek to those literals.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_index_peek_error_scan_seconds_bucket</code></td>
      <td>Time scanning the error trace for errors, summed over the slices the scan was cut into and observed only for scans that find no error.</td>
      <td><code>le</code></td>
    </tr>
    <tr>
      <td><code>mz_index_peek_error_scan_seconds_count</code></td>
      <td>Time scanning the error trace for errors, summed over the slices the scan was cut into and observed only for scans that find no error.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_index_peek_error_scan_seconds_sum</code></td>
      <td>Time scanning the error trace for errors, summed over the slices the scan was cut into and observed only for scans that find no error.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_index_peek_frontier_check_seconds_bucket</code></td>
      <td>Time checking trace frontiers.</td>
      <td><code>le</code></td>
    </tr>
    <tr>
      <td><code>mz_index_peek_frontier_check_seconds_count</code></td>
      <td>Time checking trace frontiers.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_index_peek_frontier_check_seconds_sum</code></td>
      <td>Time checking trace frontiers.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_index_peek_offload_seconds_bucket</code></td>
      <td>Wall-clock time an offloaded index peek walk spent away from the timely worker, including the wait for a permit.</td>
      <td><code>le</code></td>
    </tr>
    <tr>
      <td><code>mz_index_peek_offload_seconds_count</code></td>
      <td>Wall-clock time an offloaded index peek walk spent away from the timely worker, including the wait for a permit.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_index_peek_offload_seconds_sum</code></td>
      <td>Wall-clock time an offloaded index peek walk spent away from the timely worker, including the wait for a permit.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_index_peek_permit_queue_depth</code></td>
      <td>The number of offloaded index peek walks waiting for a permit to run.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_index_peek_permit_wait_seconds_bucket</code></td>
      <td>Time an offloaded index peek walk waited for a permit, observed only for walks that were admitted.</td>
      <td><code>le</code></td>
    </tr>
    <tr>
      <td><code>mz_index_peek_permit_wait_seconds_count</code></td>
      <td>Time an offloaded index peek walk waited for a permit, observed only for walks that were admitted.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_index_peek_permit_wait_seconds_sum</code></td>
      <td>Time an offloaded index peek walk waited for a permit, observed only for walks that were admitted.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_index_peek_result_sort_rows_bucket</code></td>
      <td>Number of intermediate result rows handed to thinning during peek collection, summed across the times it ran.</td>
      <td><code>le</code></td>
    </tr>
    <tr>
      <td><code>mz_index_peek_result_sort_rows_count</code></td>
      <td>Number of intermediate result rows handed to thinning during peek collection, summed across the times it ran.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_index_peek_result_sort_rows_sum</code></td>
      <td>Number of intermediate result rows handed to thinning during peek collection, summed across the times it ran.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_index_peek_result_sort_seconds_bucket</code></td>
      <td>Time thinning intermediate results down to the rows a peek&#39;s finishing needs.</td>
      <td><code>le</code></td>
    </tr>
    <tr>
      <td><code>mz_index_peek_result_sort_seconds_count</code></td>
      <td>Time thinning intermediate results down to the rows a peek&#39;s finishing needs.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_index_peek_result_sort_seconds_sum</code></td>
      <td>Time thinning intermediate results down to the rows a peek&#39;s finishing needs.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_index_peek_row_collection_seconds_bucket</code></td>
      <td>Time constructing RowCollection from peek results, including converting the row counts the scan produced.</td>
      <td><code>le</code></td>
    </tr>
    <tr>
      <td><code>mz_index_peek_row_collection_seconds_count</code></td>
      <td>Time constructing RowCollection from peek results, including converting the row counts the scan produced.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_index_peek_row_collection_seconds_sum</code></td>
      <td>Time constructing RowCollection from peek results, including converting the row counts the scan produced.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_index_peek_row_iteration_rows_bucket</code></td>
      <td>Number of arrangement rows evaluated by the index peek result iterator.</td>
      <td><code>le</code></td>
    </tr>
    <tr>
      <td><code>mz_index_peek_row_iteration_rows_count</code></td>
      <td>Number of arrangement rows evaluated by the index peek result iterator.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_index_peek_row_iteration_rows_sum</code></td>
      <td>Number of arrangement rows evaluated by the index peek result iterator.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_index_peek_row_iteration_seconds_bucket</code></td>
      <td>Time iterating rows, seeking the cursor to the literal constraints, and evaluating MFP, summed over the slices the walk was cut into.</td>
      <td><code>le</code></td>
    </tr>
    <tr>
      <td><code>mz_index_peek_row_iteration_seconds_count</code></td>
      <td>Time iterating rows, seeking the cursor to the literal constraints, and evaluating MFP, summed over the slices the walk was cut into.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_index_peek_row_iteration_seconds_sum</code></td>
      <td>Time iterating rows, seeking the cursor to the literal constraints, and evaluating MFP, summed over the slices the walk was cut into.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_index_peek_seek_fulfillment_seconds_bucket</code></td>
      <td>Time in seek_fulfillment method including frontier checks and data collection.</td>
      <td><code>le</code></td>
    </tr>
    <tr>
      <td><code>mz_index_peek_seek_fulfillment_seconds_count</code></td>
      <td>Time in seek_fulfillment method including frontier checks and data collection.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_index_peek_seek_fulfillment_seconds_sum</code></td>
      <td>Time in seek_fulfillment method including frontier checks and data collection.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_index_peek_stashed_total</code></td>
      <td>The number of index peek walks that answered with a handle to the peek response stash, always a subset of the `offloaded` substrate of `mz_index_peek_walks_total`.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_index_peek_total_seconds_bucket</code></td>
      <td>Time one visit to an index peek spent on the timely worker. A peek whose walk was offloaded contributes only the inline slice that offloaded it, and its time away from the worker is `mz_index_peek_offload_seconds`.</td>
      <td><code>le</code></td>
    </tr>
    <tr>
      <td><code>mz_index_peek_total_seconds_count</code></td>
      <td>Time one visit to an index peek spent on the timely worker. A peek whose walk was offloaded contributes only the inline slice that offloaded it, and its time away from the worker is `mz_index_peek_offload_seconds`.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_index_peek_total_seconds_sum</code></td>
      <td>Time one visit to an index peek spent on the timely worker. A peek whose walk was offloaded contributes only the inline slice that offloaded it, and its time away from the worker is `mz_index_peek_offload_seconds`.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_index_peek_walks_total</code></td>
      <td>The number of index peek walks that reached an outcome, by the substrate they ended on: `inline` on the timely worker, `offloaded` away from it.</td>
      <td><code>substrate</code></td>
    </tr>
    <tr>
      <td><code>mz_kafka_partition_offset_max</code></td>
      <td>High watermark offset on broker for partition</td>
      <td><code>partition_id</code>, <code>source_id</code>, <code>topic</code></td>
    </tr>
    <tr>
      <td><code>mz_linearize_message_seconds_bucket</code></td>
      <td>The number of seconds it takes to linearize strict serializable messages</td>
      <td><code>immediately_handled</code>, <code>le</code>, <code>type</code></td>
    </tr>
    <tr>
      <td><code>mz_linearize_message_seconds_count</code></td>
      <td>The number of seconds it takes to linearize strict serializable messages</td>
      <td><code>immediately_handled</code>, <code>type</code></td>
    </tr>
    <tr>
      <td><code>mz_linearize_message_seconds_sum</code></td>
      <td>The number of seconds it takes to linearize strict serializable messages</td>
      <td><code>immediately_handled</code>, <code>type</code></td>
    </tr>
    <tr>
      <td><code>mz_mcp_requests_total</code></td>
      <td>Total number of MCP requests received.</td>
      <td><code>endpoint_type</code>, <code>method</code>, <code>status</code></td>
    </tr>
    <tr>
      <td><code>mz_mcp_tool_call_duration_seconds_bucket</code></td>
      <td>Duration of MCP tools/call invocations in seconds.</td>
      <td><code>endpoint_type</code>, <code>le</code>, <code>tool_name</code></td>
    </tr>
    <tr>
      <td><code>mz_mcp_tool_call_duration_seconds_count</code></td>
      <td>Duration of MCP tools/call invocations in seconds.</td>
      <td><code>endpoint_type</code>, <code>tool_name</code></td>
    </tr>
    <tr>
      <td><code>mz_mcp_tool_call_duration_seconds_sum</code></td>
      <td>Duration of MCP tools/call invocations in seconds.</td>
      <td><code>endpoint_type</code>, <code>tool_name</code></td>
    </tr>
    <tr>
      <td><code>mz_mcp_tool_calls_total</code></td>
      <td>Total number of MCP tools/call invocations.</td>
      <td><code>endpoint_type</code>, <code>status</code>, <code>tool_name</code></td>
    </tr>
    <tr>
      <td><code>mz_memory_limiter_burst_budget_byteseconds</code></td>
      <td>The remaining memory burst budget.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_memory_limiter_duration_seconds_bucket</code></td>
      <td>A histogram of the time it took to run the memory limiter.</td>
      <td><code>le</code></td>
    </tr>
    <tr>
      <td><code>mz_memory_limiter_duration_seconds_count</code></td>
      <td>A histogram of the time it took to run the memory limiter.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_memory_limiter_duration_seconds_sum</code></td>
      <td>A histogram of the time it took to run the memory limiter.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_memory_limiter_memory_limit_bytes</code></td>
      <td>The configured memory limit.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_memory_limiter_memory_usage_bytes</code></td>
      <td>The current memory usage.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_memory_limiter_vm_rss_bytes</code></td>
      <td>The current VmRSS metric.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_memory_limiter_vm_swap_bytes</code></td>
      <td>The current VmSwap metric.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_metrics_lgalloc_allocations_total</code></td>
      <td>Number of region allocations in size class</td>
      <td><code>size_class</code></td>
    </tr>
    <tr>
      <td><code>mz_metrics_lgalloc_area_total_bytes</code></td>
      <td>Number of bytes in all areas in size class</td>
      <td><code>size_class</code></td>
    </tr>
    <tr>
      <td><code>mz_metrics_lgalloc_areas_total</code></td>
      <td>Number of areas backing size class</td>
      <td><code>size_class</code></td>
    </tr>
    <tr>
      <td><code>mz_metrics_lgalloc_clean_regions_bytes_total</code></td>
      <td>Number of clean regions in size class</td>
      <td><code>size_class</code></td>
    </tr>
    <tr>
      <td><code>mz_metrics_lgalloc_clean_regions_total</code></td>
      <td>Number of clean regions in size class</td>
      <td><code>size_class</code></td>
    </tr>
    <tr>
      <td><code>mz_metrics_lgalloc_clear_eager_bytes_total</code></td>
      <td>Number of thread regions in size class</td>
      <td><code>size_class</code></td>
    </tr>
    <tr>
      <td><code>mz_metrics_lgalloc_clear_eager_total</code></td>
      <td>Number of thread regions in size class</td>
      <td><code>size_class</code></td>
    </tr>
    <tr>
      <td><code>mz_metrics_lgalloc_clear_slow_bytes_total</code></td>
      <td>Number of thread regions in size class</td>
      <td><code>size_class</code></td>
    </tr>
    <tr>
      <td><code>mz_metrics_lgalloc_clear_slow_total</code></td>
      <td>Number of thread regions in size class</td>
      <td><code>size_class</code></td>
    </tr>
    <tr>
      <td><code>mz_metrics_lgalloc_deallocations_total</code></td>
      <td>Number of region deallocations for size class</td>
      <td><code>size_class</code></td>
    </tr>
    <tr>
      <td><code>mz_metrics_lgalloc_file_allocated_size_bytes</code></td>
      <td>Sum of allocated sizes in size class</td>
      <td><code>size_class</code></td>
    </tr>
    <tr>
      <td><code>mz_metrics_lgalloc_file_size_bytes</code></td>
      <td>Sum of file sizes in size class</td>
      <td><code>size_class</code></td>
    </tr>
    <tr>
      <td><code>mz_metrics_lgalloc_free_regions_bytes_total</code></td>
      <td>Number of free regions in size class</td>
      <td><code>size_class</code></td>
    </tr>
    <tr>
      <td><code>mz_metrics_lgalloc_free_regions_total</code></td>
      <td>Number of free regions in size class</td>
      <td><code>size_class</code></td>
    </tr>
    <tr>
      <td><code>mz_metrics_lgalloc_global_regions_bytes_total</code></td>
      <td>Number of global regions in size class</td>
      <td><code>size_class</code></td>
    </tr>
    <tr>
      <td><code>mz_metrics_lgalloc_global_regions_total</code></td>
      <td>Number of global regions in size class</td>
      <td><code>size_class</code></td>
    </tr>
    <tr>
      <td><code>mz_metrics_lgalloc_refill_total</code></td>
      <td>Number of area refills for size class</td>
      <td><code>size_class</code></td>
    </tr>
    <tr>
      <td><code>mz_metrics_lgalloc_slow_path_total</code></td>
      <td>Number of slow path region allocations for size class</td>
      <td><code>size_class</code></td>
    </tr>
    <tr>
      <td><code>mz_metrics_lgalloc_thread_regions_bytes_total</code></td>
      <td>Number of thread regions in size class</td>
      <td><code>size_class</code></td>
    </tr>
    <tr>
      <td><code>mz_metrics_lgalloc_thread_regions_total</code></td>
      <td>Number of thread regions in size class</td>
      <td><code>size_class</code></td>
    </tr>
    <tr>
      <td><code>mz_metrics_lgalloc_vm_active_bytes</code></td>
      <td>Sum of active sizes in size class</td>
      <td><code>size_class</code></td>
    </tr>
    <tr>
      <td><code>mz_metrics_lgalloc_vm_dirty_bytes</code></td>
      <td>Sum of dirty sizes in size class</td>
      <td><code>size_class</code></td>
    </tr>
    <tr>
      <td><code>mz_metrics_lgalloc_vm_mapped_bytes</code></td>
      <td>Sum of mapped sizes in size class</td>
      <td><code>size_class</code></td>
    </tr>
    <tr>
      <td><code>mz_metrics_libc_ru_inblock_total</code></td>
      <td>block input operations</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_metrics_libc_ru_majflt_total</code></td>
      <td>page faults (hard page faults)</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_metrics_libc_ru_maxrss_bytes</code></td>
      <td>maximum resident set size</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_metrics_libc_ru_minflt_total</code></td>
      <td>page reclaims (soft page faults)</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_metrics_libc_ru_nivcsw_total</code></td>
      <td>involuntary context switches</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_metrics_libc_ru_nvcsw_total</code></td>
      <td>voluntary context switches</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_metrics_libc_ru_oublock_total</code></td>
      <td>block output operations</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_metrics_libc_ru_stime_seconds_total</code></td>
      <td>system CPU time used</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_metrics_libc_ru_utime_seconds_total</code></td>
      <td>user CPU time used</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_metrics_resource_usage</code></td>
      <td>Resource usage observations, by source and metric.</td>
      <td><code>metric</code>, <code>source</code></td>
    </tr>
    <tr>
      <td><code>mz_metrics_update_duration_bucket</code></td>
      <td>The time it took to update lgalloc stats</td>
      <td><code>le</code>, <code>name</code></td>
    </tr>
    <tr>
      <td><code>mz_metrics_update_duration_count</code></td>
      <td>The time it took to update lgalloc stats</td>
      <td><code>name</code></td>
    </tr>
    <tr>
      <td><code>mz_metrics_update_duration_sum</code></td>
      <td>The time it took to update lgalloc stats</td>
      <td><code>name</code></td>
    </tr>
    <tr>
      <td><code>mz_mysql_per_source_deletes</code></td>
      <td>The number of deletes for all tables in this source</td>
      <td><code>source_id</code></td>
    </tr>
    <tr>
      <td><code>mz_mysql_per_source_ignored_messages</code></td>
      <td>The number of messages ignored because of an irrelevant type or relation_id</td>
      <td><code>source_id</code></td>
    </tr>
    <tr>
      <td><code>mz_mysql_per_source_inserts</code></td>
      <td>The number of inserts for all tables in this source</td>
      <td><code>source_id</code></td>
    </tr>
    <tr>
      <td><code>mz_mysql_per_source_messages_total</code></td>
      <td>The total number of replication messages for this source, not expected to be the sum of the other values.</td>
      <td><code>source_id</code></td>
    </tr>
    <tr>
      <td><code>mz_mysql_per_source_tables_count</code></td>
      <td>The number of upstream tables for this source</td>
      <td><code>source_id</code></td>
    </tr>
    <tr>
      <td><code>mz_mysql_per_source_updates</code></td>
      <td>The number of updates for all tables in this source</td>
      <td><code>source_id</code></td>
    </tr>
    <tr>
      <td><code>mz_mysql_snapshot_count_latency</code></td>
      <td>The wall time used to obtain snapshot sizes.</td>
      <td><code>schema</code>, <code>source_id</code>, <code>table_name</code></td>
    </tr>
    <tr>
      <td><code>mz_mysql_sum_gtid_txns</code></td>
      <td>The sum of all transaction-ids committed for each GTID Source-ID UUID seen for this source</td>
      <td><code>source_id</code></td>
    </tr>
    <tr>
      <td><code>mz_oauth_protected_resource_metadata_requests_total</code></td>
      <td>Total number of requests to the OAuth Protected Resource Metadata endpoint.</td>
      <td><code>status</code></td>
    </tr>
    <tr>
      <td><code>mz_object_info</code></td>
      <td>Maps catalog object IDs to the object&#39;s name, schema, database, and type. Constant 1.</td>
      <td><code>database_name</code>, <code>global_id</code>, <code>name</code>, <code>object_id</code>, <code>schema_name</code>, <code>type</code></td>
    </tr>
    <tr>
      <td><code>mz_occ_read_then_write_retry_count_bucket</code></td>
      <td>Number of OCC retries per read-then-write operation.</td>
      <td><code>caller</code>, <code>le</code></td>
    </tr>
    <tr>
      <td><code>mz_occ_read_then_write_retry_count_count</code></td>
      <td>Number of OCC retries per read-then-write operation.</td>
      <td><code>caller</code></td>
    </tr>
    <tr>
      <td><code>mz_occ_read_then_write_retry_count_sum</code></td>
      <td>Number of OCC retries per read-then-write operation.</td>
      <td><code>caller</code></td>
    </tr>
    <tr>
      <td><code>mz_optimization_notices</code></td>
      <td>Number of optimization notices per notice type.</td>
      <td><code>notice_type</code></td>
    </tr>
    <tr>
      <td><code>mz_optimizer_e2e_optimization_time_seconds_bucket</code></td>
      <td>A histogram of end-to-end optimization times since restart.</td>
      <td><code>le</code>, <code>object_type</code></td>
    </tr>
    <tr>
      <td><code>mz_optimizer_e2e_optimization_time_seconds_count</code></td>
      <td>A histogram of end-to-end optimization times since restart.</td>
      <td><code>object_type</code></td>
    </tr>
    <tr>
      <td><code>mz_optimizer_e2e_optimization_time_seconds_sum</code></td>
      <td>A histogram of end-to-end optimization times since restart.</td>
      <td><code>object_type</code></td>
    </tr>
    <tr>
      <td><code>mz_optimizer_lowering_literal_constraints_total</code></td>
      <td>How often the MFP-based literal-constraint detector succeeded, by call site.</td>
      <td><code>case</code></td>
    </tr>
    <tr>
      <td><code>mz_otel_on_close</code></td>
      <td>count of on_close events sent to otel</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_parameter_frontend_last_cse_time_seconds</code></td>
      <td>The last known time when the LaunchDarkly client sent an event to the LaunchDarkly server (as unix timestamp).</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_parameter_frontend_last_sse_time_seconds</code></td>
      <td>The last known time when the LaunchDarkly client received an event from the LaunchDarkly server (as unix timestamp).</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_parameter_frontend_params_changed</code></td>
      <td>The number of parameter changes pulled from the LaunchDarkly frontend.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_parse_seconds_bucket</code></td>
      <td>The time it takes to parse a SQL statement. (Works for both Simple Queries and the Extended Query protocol.)</td>
      <td><code>le</code></td>
    </tr>
    <tr>
      <td><code>mz_parse_seconds_count</code></td>
      <td>The time it takes to parse a SQL statement. (Works for both Simple Queries and the Extended Query protocol.)</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_parse_seconds_sum</code></td>
      <td>The time it takes to parse a SQL statement. (Works for both Simple Queries and the Extended Query protocol.)</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_*_bytes</code></td>
      <td>total encoded size of * batches written</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_*_goodbytes</code></td>
      <td>total logical size of * batches written</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_*_key_lower_too_big</code></td>
      <td>count of * writes that were unable to write a key lower, because the size threshold was too low</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_*_step_inline</code></td>
      <td>time spent encoding * inline batches</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_*_step_part_writing</code></td>
      <td>blocking time spent writing parts for * updates</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_*_step_stats</code></td>
      <td>time spent computing * update stats</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_*_write_batch_order</code></td>
      <td>count of batches by the data ordering</td>
      <td><code>order</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_*_write_batch_part_seconds</code></td>
      <td>time spent writing * batches</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_*_write_stall_count</code></td>
      <td>count of * writes stalling to await max outstanding reqs</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_audit_blob_batch_part_bytes</code></td>
      <td>total size of batch parts in blob</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_audit_blob_batch_part_count</code></td>
      <td>count of batch parts in blob</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_audit_blob_bytes</code></td>
      <td>total size of blob</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_audit_blob_count</code></td>
      <td>count of all blobs</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_audit_blob_rollup_bytes</code></td>
      <td>total size of state rollups stored in blob</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_audit_blob_rollup_count</code></td>
      <td>count of all state rollups in blob</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_audit_step_seconds</code></td>
      <td>time spent on individual steps of audit</td>
      <td><code>step</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_backpressure_emitted_bytes</code></td>
      <td>A counter with the number of emitted bytes.</td>
      <td><code>name</code>, <code>shard</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_backpressure_last_backpressured_bytes</code></td>
      <td>The last count of bytes we are waiting to be retired in the operator. This cannot be directly compared to `retired_bytes`, but CAN indicate that backpressure is happening.</td>
      <td><code>name</code>, <code>shard</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_backpressure_retired_bytes</code></td>
      <td>A counter with the number of bytes retired by downstream processing.</td>
      <td><code>name</code>, <code>shard</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_blob_cache_evictions</code></td>
      <td>count of capacity-based cache evictions</td>
      <td><code>cache</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_blob_cache_hits_blobs</code></td>
      <td>count of blobs served via cache instead of s3</td>
      <td><code>cache</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_blob_cache_hits_bytes</code></td>
      <td>total size of blobs served via cache instead of s3</td>
      <td><code>cache</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_blob_cache_size_blobs</code></td>
      <td>count of blobs in the cache</td>
      <td><code>cache</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_blob_cache_size_bytes</code></td>
      <td>total size of blobs in the cache</td>
      <td><code>cache</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_blob_failures</code></td>
      <td>count of all blob operation failures</td>
      <td><code>honeycomb</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_blob_hedge_armed</code></td>
      <td>1 if this process opened a hedge sibling and can hedge when enabled</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_blob_hedge_errors</code></td>
      <td>hedge requests (the hedge leg only, not the primary) that completed with an error</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_blob_hedge_rtt_latency</code></td>
      <td>roundtrip-time of the most recent successful warm-path liveness gets on the hedge sibling</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_blob_hedge_warm_errors</code></td>
      <td>warm-path liveness gets on the hedge sibling that failed or timed out</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_blob_hedge_won_seconds_bucket</code></td>
      <td>end-to-end latency of blob gets won by the hedge request</td>
      <td><code>le</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_blob_hedge_won_seconds_count</code></td>
      <td>end-to-end latency of blob gets won by the hedge request</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_blob_hedge_won_seconds_sum</code></td>
      <td>end-to-end latency of blob gets won by the hedge request</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_blob_hedges_fired</code></td>
      <td>blob gets that fired a hedge request</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_blob_hedges_skipped</code></td>
      <td>hedge requests not fired for a get that exceeded the hedge delay, by reason</td>
      <td><code>reason</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_blob_hedges_won</code></td>
      <td>blob gets where the hedge request won the race</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_cmd_cas_mismatch_count</code></td>
      <td>count of command retries from CaS mismatch</td>
      <td><code>cmd</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_cmd_compare_and_append_noop</code></td>
      <td>count of compare_and_append retries that were discoverd to have already committed</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_cmd_failed_count</code></td>
      <td>count of commands failed</td>
      <td><code>cmd</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_cmd_fetch_upper_count</code></td>
      <td>count of fetch_upper calls</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_cmd_seconds</code></td>
      <td>time spent applying commands</td>
      <td><code>cmd</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_cmd_started_count</code></td>
      <td>count of commands started</td>
      <td><code>cmd</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_cmd_succeeded_count</code></td>
      <td>count of commands succeeded</td>
      <td><code>cmd</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_columnar_op_count</code></td>
      <td>number of rows we&#39;ve run the specified op on in our structured columnar format</td>
      <td><code>column</code>, <code>op</code>, <code>result</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_columnar_part_build_count</code></td>
      <td>number of times we&#39;ve encoded our structured columnar format</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_columnar_part_build_seconds</code></td>
      <td>number of seconds we&#39;ve spent encoding our structured columnar format</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_columnar_part_concat_bytes</code></td>
      <td>number of bytes we&#39;ve copied when concatenating updates</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_compaction_admin_count</code></td>
      <td>count of compaction requests that were performed by admin tooling</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_compaction_applied</code></td>
      <td>count of compactions applied to state</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_compaction_applied_exact_match</code></td>
      <td>count of merge results that exactly replaced a SpineBatch</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_compaction_applied_subset_match</code></td>
      <td>count of merge results that replaced a subset of a SpineBatch</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_compaction_chunks_compacted</code></td>
      <td>count of run chunks compacted</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_compaction_concurrency_waits</code></td>
      <td>count of compaction requests that ever blocked due to concurrency limit</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_compaction_disabled</code></td>
      <td>count of total compaction requests dropped because compaction was disabled</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_compaction_dropped</code></td>
      <td>count of total compaction requests dropped due to a full queue</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_compaction_failed</code></td>
      <td>count of compactions failed</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_compaction_fast_path_eligible</code></td>
      <td>count of compaction requests that could have used the fast-path optimization</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_compaction_memory_violations</code></td>
      <td>count of compaction memory requirement violations</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_compaction_noop</code></td>
      <td>count of compactions discarded (obsolete)</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_compaction_not_all_prefetched</code></td>
      <td>count of compactions where not all inputs were prefetched</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_compaction_not_applied_too_many_updates</code></td>
      <td>count of merge results that did not apply due to too many updates</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_compaction_parts_prefetched</code></td>
      <td>count of compaction parts completely prefetched by the time they&#39;re needed</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_compaction_parts_waited</code></td>
      <td>count of compaction parts that had to be waited on</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_compaction_queued_seconds</code></td>
      <td>time that compaction requests spent queued</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_compaction_requested</code></td>
      <td>count of total compaction requests</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_compaction_runs_compacted</code></td>
      <td>count of runs compacted</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_compaction_schema_selection</code></td>
      <td>count of compactions and how we did schema selection</td>
      <td><code>selection</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_compaction_seconds</code></td>
      <td>time spent in compaction</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_compaction_skipped</code></td>
      <td>count of compactions skipped due to heuristics</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_compaction_started</code></td>
      <td>count of compactions started</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_compaction_step_seconds</code></td>
      <td>time spent on individual steps of compaction</td>
      <td><code>step</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_compaction_timed_out</code></td>
      <td>count of compactions that timed out</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_consensus_failures</code></td>
      <td>count of determinate consensus operation failures</td>
      <td><code>honeycomb</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_consolidation_parts_fetched_count</code></td>
      <td>count of parts that were fetched and used during consolidation</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_consolidation_parts_skipped_count</code></td>
      <td>count of parts that were never needed during consolidation</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_consolidation_parts_wasted_count</code></td>
      <td>count of parts that were fetched but not needed during consolidation</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_consolidation_wrong_sort_count</code></td>
      <td>count of runs that were sorted using the wrong ordering for the current consolidation</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_decode_count</code></td>
      <td>count of op decodes</td>
      <td><code>op</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_decode_seconds</code></td>
      <td>time spent in op decodes</td>
      <td><code>op</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_encode_count</code></td>
      <td>count of op encodes</td>
      <td><code>op</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_encode_seconds</code></td>
      <td>time spent in op encodes</td>
      <td><code>op</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_external_blob_delete_noop_count</code></td>
      <td>count of blob delete calls that deleted a non-existent key</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_external_blob_sizes_bucket</code></td>
      <td>histogram of blob sizes at put time</td>
      <td><code>le</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_external_blob_sizes_count</code></td>
      <td>histogram of blob sizes at put time</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_external_blob_sizes_sum</code></td>
      <td>histogram of blob sizes at put time</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_external_bytes_count</code></td>
      <td>total size represented by external service calls</td>
      <td><code>op</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_external_consensus_truncated_count</code></td>
      <td>count of versions deleted by consensus truncate calls</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_external_failed_count</code></td>
      <td>count of external service calls failed</td>
      <td><code>op</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_external_op_latency_bucket</code></td>
      <td>rountrip latency observed by individual performance-critical operations</td>
      <td><code>le</code>, <code>op</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_external_op_latency_count</code></td>
      <td>rountrip latency observed by individual performance-critical operations</td>
      <td><code>op</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_external_op_latency_sum</code></td>
      <td>rountrip latency observed by individual performance-critical operations</td>
      <td><code>op</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_external_rtt_latency</code></td>
      <td>roundtrip-time to external service as seen by this process</td>
      <td><code>external</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_external_seconds</code></td>
      <td>time spent in external service calls</td>
      <td><code>op</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_external_started_count</code></td>
      <td>count of external service calls started</td>
      <td><code>op</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_external_succeeded_count</code></td>
      <td>count of external service calls succeeded</td>
      <td><code>op</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_gc_finished</code></td>
      <td>count of garbage collections finished</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_gc_merged_reqs</code></td>
      <td>count of garbage collection requests merged</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_gc_noop</code></td>
      <td>count of garbage collections skipped because they were already done</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_gc_seconds</code></td>
      <td>time spent in garbage collections</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_gc_started</code></td>
      <td>count of garbage collections started</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_gc_step_seconds</code></td>
      <td>time spent on individual steps of gc</td>
      <td><code>step</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_inline_part_commit_bytes</code></td>
      <td>total size of of inline parts committed to state</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_inline_part_commit_count</code></td>
      <td>count of inline parts committed to state</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_lease_dropped_part</code></td>
      <td>count of LeasedBatchParts that were dropped without being politely returned</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_lease_timeout_read</code></td>
      <td>count of readers whose lease timed out</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_lock_acquire_count</code></td>
      <td>count of locks acquired</td>
      <td><code>op</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_lock_blocking_acquire_count</code></td>
      <td>count of locks acquired that required blocking</td>
      <td><code>op</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_lock_blocking_seconds</code></td>
      <td>time spent blocked for a lock</td>
      <td><code>op</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_metadata_seconds</code></td>
      <td>server uptime, labels are build metadata</td>
      <td><code>build_type</code>, <code>version</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_parquet_column_size</code></td>
      <td>size in bytes of a column within a parquet file</td>
      <td><code>col</code>, <code>compressed</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_parquet_elided_null_buffer_count</code></td>
      <td>times we dropped an unnecessary null buffer returned by parquet decoding</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_parquet_encoded_size</code></td>
      <td>encoded size of a parquet file that we write to S3</td>
      <td><code>format</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_parquet_row_group_count</code></td>
      <td>count of row groups in a parquet file</td>
      <td><code>format</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_peek_seconds_bucket</code></td>
      <td>Time spent in (experimental) Persist fast-path peeks.</td>
      <td><code>le</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_peek_seconds_count</code></td>
      <td>Time spent in (experimental) Persist fast-path peeks.</td>
      <td><code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_peek_seconds_sum</code></td>
      <td>Time spent in (experimental) Persist fast-path peeks.</td>
      <td><code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_pubsub_client_approx_diff_apply_latency_seconds_bucket</code></td>
      <td>histogram of (approximate) latency between sending a diff and applying it</td>
      <td><code>le</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_pubsub_client_approx_diff_apply_latency_seconds_count</code></td>
      <td>histogram of (approximate) latency between sending a diff and applying it</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_pubsub_client_approx_diff_apply_latency_seconds_sum</code></td>
      <td>histogram of (approximate) latency between sending a diff and applying it</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_pubsub_client_call_bytes_sent</code></td>
      <td>number of bytes sent for a given pubsub client call</td>
      <td><code>call</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_pubsub_client_call_failed</code></td>
      <td>times a pubsub client call failed</td>
      <td><code>call</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_pubsub_client_call_received</code></td>
      <td>times a pubsub client call was received</td>
      <td><code>call</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_pubsub_client_call_succeeded</code></td>
      <td>times a pubsub client call succeeded</td>
      <td><code>call</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_pubsub_client_grpc_broadcast_recv_lagged_count</code></td>
      <td>times a message was missed by broadcast receiver due to lag</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_pubsub_client_grpc_connect_call_attempt_count</code></td>
      <td>count of connection call attempts (including retries) to pubsub server</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_pubsub_client_grpc_connected</code></td>
      <td>whether the grpc client is currently connected</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_pubsub_client_grpc_connection_established_count</code></td>
      <td>count of grpc connection establishments to pubsub server</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_pubsub_client_grpc_error_count</code></td>
      <td>count of grpc errors received</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_pubsub_client_receiver_state_push_diff_fast_path</code></td>
      <td>count fast-path state push_diff calls</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_pubsub_client_receiver_state_push_diff_slow_path_failed</code></td>
      <td>count of unsuccessful slow-path state push_diff calls</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_pubsub_client_receiver_state_push_diff_slow_path_succeeded</code></td>
      <td>count of successful slow-path state push_diff calls</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_pubsub_server_active_connections</code></td>
      <td>number of active connections to server</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_pubsub_server_broadcasted_diff_bytes</code></td>
      <td>count of total broadcast diff bytes sent</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_pubsub_server_broadcasted_diff_count</code></td>
      <td>count of total broadcast diff messages sent</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_pubsub_server_broadcasted_diff_dropped_channel_full</code></td>
      <td>count of diffs dropped due to full connection channel</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_pubsub_server_call_count</code></td>
      <td>count of each pubsub server message received</td>
      <td><code>call</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_pubsub_server_operation_seconds</code></td>
      <td>time spent in pubsub server performing each operation</td>
      <td><code>op</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_pushdown_parts_audited_bytes</code></td>
      <td>total size of parts fetched only for pushdown audit</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_pushdown_parts_audited_count</code></td>
      <td>count of parts fetched only for pushdown audit</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_pushdown_parts_faked_bytes</code></td>
      <td>total size of parts replaced with fakes by aggressive projection pushdown</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_pushdown_parts_faked_count</code></td>
      <td>count of parts faked because of aggressive projection pushdown</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_pushdown_parts_fetched_bytes</code></td>
      <td>total size of parts not filtered by pushdown in bytes</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_pushdown_parts_fetched_count</code></td>
      <td>count of parts not filtered by pushdown</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_pushdown_parts_filtered_bytes</code></td>
      <td>total size of parts filtered by pushdown in bytes</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_pushdown_parts_filtered_count</code></td>
      <td>count of parts filtered by pushdown</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_pushdown_parts_inline_bytes</code></td>
      <td>total size of parts not fetched because they were inline</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_pushdown_parts_inline_count</code></td>
      <td>count of parts not fetched because they were inline</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_pushdown_parts_mismatched_stats_count</code></td>
      <td>number of parts read with unexpectedly the incorrect type of stats</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_pushdown_parts_projection_trimmed_bytes</code></td>
      <td>total bytes trimmed from columnar data because of projection pushdown</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_pushdown_parts_stats_trimmed_bytes</code></td>
      <td>total bytes trimmed from part stats</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_pushdown_parts_stats_trimmed_count</code></td>
      <td>count of trimmed part stats</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_read_batch_part_bytes</code></td>
      <td>total encoded size of batch parts read</td>
      <td><code>op</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_read_batch_part_count</code></td>
      <td>count of batch parts read</td>
      <td><code>op</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_read_batch_part_goodbytes</code></td>
      <td>total logical size of batch parts read</td>
      <td><code>op</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_read_batch_part_seconds</code></td>
      <td>time spent reading batch parts</td>
      <td><code>op</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_read_ts_rewite</code></td>
      <td>count of updates read with rewritten ts</td>
      <td><code>op</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_retry_finished_count</code></td>
      <td>count of retry loops finished</td>
      <td><code>op</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_retry_retries_count</code></td>
      <td>count of total attempts by retry loops</td>
      <td><code>op</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_retry_sleep_seconds</code></td>
      <td>time spent in retry loop backoff</td>
      <td><code>op</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_retry_started_count</code></td>
      <td>count of retry loops started</td>
      <td><code>op</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_s3_connect_timeouts</code></td>
      <td>number of timeouts establishing a connection to S3</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_s3_errors</code></td>
      <td>errors</td>
      <td><code>code</code>, <code>op</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_s3_operation_attempt_timeouts</code></td>
      <td>number of operation attempt timeouts (within a single retry)</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_s3_operation_timeouts</code></td>
      <td>number of operation timeouts (including retries)</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_s3_operations</code></td>
      <td>number of raw s3 calls on behalf of Blob interface methods</td>
      <td><code>op</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_s3_read_timeouts</code></td>
      <td>number of timeouts waiting on first response byte from S3</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_schema_cache_added_count</code></td>
      <td>count of schema cache entries added</td>
      <td><code>op</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_schema_cache_cached_count</code></td>
      <td>count of schema cache entries served from cache</td>
      <td><code>op</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_schema_cache_computed_count</code></td>
      <td>count of schema cache entries computed</td>
      <td><code>op</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_schema_cache_dropped_count</code></td>
      <td>count of schema cache entries dropped</td>
      <td><code>op</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_schema_cache_fetch_state_count</code></td>
      <td>count of state fetches by the schema cache</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_schema_cache_unavailable_count</code></td>
      <td>count of schema cache entries unavailable at current state</td>
      <td><code>op</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_schema_migration_count</code></td>
      <td>count of fetch part migrations</td>
      <td><code>op</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_schema_migration_len</code></td>
      <td>count of migrated update records</td>
      <td><code>op</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_schema_migration_migrate_seconds</code></td>
      <td>seconds spent applying migration logic</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_schema_migration_new_count</code></td>
      <td>count of migrations constructed</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_schema_migration_new_seconds</code></td>
      <td>seconds spent constructing migration logic</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_semaphore_acquire_count</code></td>
      <td>count of acquire calls (not acquired permits count)</td>
      <td><code>name</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_semaphore_acquired_permits</code></td>
      <td>total sum of acquired permits</td>
      <td><code>name</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_semaphore_available_permits</code></td>
      <td>currently available permits according to the semaphore</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_semaphore_blocking_count</code></td>
      <td>count of acquire calls that had to block</td>
      <td><code>name</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_semaphore_blocking_seconds</code></td>
      <td>total time spent blocking on permit acquisition</td>
      <td><code>name</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_semaphore_released_permits</code></td>
      <td>total sum of released permits</td>
      <td><code>name</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_shard_batch_part_count</code></td>
      <td>count of batch parts by shard</td>
      <td><code>name</code>, <code>shard</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_shard_batch_part_version_bytes</code></td>
      <td>total bytes in batch parts by shard and version</td>
      <td><code>name</code>, <code>shard</code>, <code>version</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_shard_batch_part_version_count</code></td>
      <td>count of batch parts by shard and version</td>
      <td><code>name</code>, <code>shard</code>, <code>version</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_shard_blob_gets</code></td>
      <td>number of Blob::get calls for this shard</td>
      <td><code>name</code>, <code>shard</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_shard_blob_sets</code></td>
      <td>number of Blob::set calls for this shard</td>
      <td><code>name</code>, <code>shard</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_shard_cmd_succeeded</code></td>
      <td>count of commands succeeded by shard</td>
      <td><code>name</code>, <code>shard</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_shard_compact_batches</code></td>
      <td>number of fully compact batches in the shard</td>
      <td><code>name</code>, <code>shard</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_shard_compacting_batches</code></td>
      <td>number of batches in the shard with compactions in progress</td>
      <td><code>name</code>, <code>shard</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_shard_compaction_applied</code></td>
      <td>count of compactions applied to state by shard</td>
      <td><code>name</code>, <code>shard</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_shard_count</code></td>
      <td>count of all active shards on this process</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_shard_diff_size_bytes</code></td>
      <td>total encoded diff size by shard</td>
      <td><code>name</code>, <code>shard</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_shard_gc_finished</code></td>
      <td>count of garbage collections finished by shard</td>
      <td><code>name</code>, <code>shard</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_shard_gc_live_diffs</code></td>
      <td>the number of diffs (or, alternatively, the number of seqnos) present in consensus state at GC time</td>
      <td><code>name</code>, <code>shard</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_shard_gc_seqno_held_parts</code></td>
      <td>count of parts referenced by some live state but not the current state (ie. parts kept only to satisfy seqno holds) at GC time</td>
      <td><code>name</code>, <code>shard</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_shard_hollow_batch_count</code></td>
      <td>count of hollow batches by shard</td>
      <td><code>name</code>, <code>shard</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_shard_inline_backpressure_count</code></td>
      <td>count of CaA attempts retried because of inline backpressure</td>
      <td><code>name</code>, <code>shard</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_shard_inline_part_bytes</code></td>
      <td>total size of parts inline in shard metadata</td>
      <td><code>name</code>, <code>shard</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_shard_inline_part_count</code></td>
      <td>count of parts inline in shard metadata</td>
      <td><code>name</code>, <code>shard</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_shard_largest_batch_size</code></td>
      <td>largest encoded batch size by shard</td>
      <td><code>name</code>, <code>shard</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_shard_live_writers</code></td>
      <td>number of writers that have recently appended updates to this shard</td>
      <td><code>name</code>, <code>shard</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_shard_noncompact_batches</code></td>
      <td>number of batches in the shard that aren&#39;t compact and have no ongoing compaction</td>
      <td><code>name</code>, <code>shard</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_shard_pubsub_diff_applied</code></td>
      <td>number of diffs received via pubsub that applied</td>
      <td><code>name</code>, <code>shard</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_shard_pubsub_diff_not_applied_out_of_order</code></td>
      <td>number of diffs received via pubsub that did not apply due to out-of-order delivery</td>
      <td><code>name</code>, <code>shard</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_shard_pubsub_diff_not_applied_stale</code></td>
      <td>number of diffs received via pubsub that did not apply due to staleness</td>
      <td><code>name</code>, <code>shard</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_shard_rewrite_part_count</code></td>
      <td>count of batch parts with rewrites by shard</td>
      <td><code>name</code>, <code>shard</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_shard_rollup_count</code></td>
      <td>count of rollups by shard</td>
      <td><code>name</code>, <code>shard</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_shard_rollup_size_bytes</code></td>
      <td>total encoded rollup size by shard</td>
      <td><code>name</code>, <code>shard</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_shard_schema_registry_version_count</code></td>
      <td>count of versions in the schema registry</td>
      <td><code>name</code>, <code>shard</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_shard_seqnos_held</code></td>
      <td>maximum count of gc-ineligible states by shard</td>
      <td><code>name</code>, <code>shard</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_shard_seqnos_since_last_rollup</code></td>
      <td>count of seqnos since last rollup</td>
      <td><code>name</code>, <code>shard</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_shard_since</code></td>
      <td>since by shard</td>
      <td><code>name</code>, <code>shard</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_shard_spine_batch_count</code></td>
      <td>count of spine batches by shard</td>
      <td><code>name</code>, <code>shard</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_shard_stale_version</code></td>
      <td>indicates whether the current version of the shard is less than the current version of the code</td>
      <td><code>name</code>, <code>shard</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_shard_unconsolidated_snapshot</code></td>
      <td>in snapshot_and_read, the number of times consolidating the raw data wasn&#39;t enough to produce consolidated output</td>
      <td><code>name</code>, <code>shard</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_shard_update_count</code></td>
      <td>count of updates by shard</td>
      <td><code>name</code>, <code>shard</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_shard_upper</code></td>
      <td>upper by shard</td>
      <td><code>name</code>, <code>shard</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_shard_usage_current_state_batches_bytes</code></td>
      <td>data in batches/parts referenced by current version of state</td>
      <td><code>name</code>, <code>shard</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_shard_usage_current_state_rollups_bytes</code></td>
      <td>data in rollups referenced by current version of state</td>
      <td><code>name</code>, <code>shard</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_shard_usage_leaked_bytes</code></td>
      <td>data reclaimable by a leaked blob detector</td>
      <td><code>name</code>, <code>shard</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_shard_usage_not_leaked_not_referenced_bytes</code></td>
      <td>data written by an active writer but not referenced by any version of state</td>
      <td><code>name</code>, <code>shard</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_shard_usage_referenced_not_current_state_bytes</code></td>
      <td>data referenced only by a previous version of state</td>
      <td><code>name</code>, <code>shard</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_sink_correction_capacity_decreases_total</code></td>
      <td>The cumulative capacity decreases observed on the correction buffer across workers and persist sinks.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_sink_correction_capacity_increases_total</code></td>
      <td>The cumulative capacity increases observed on the correction buffer across workers and persist sinks.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_sink_correction_deletions_total</code></td>
      <td>The cumulative deletions observed on the correction buffer across workers and persist sinks.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_sink_correction_insertions_total</code></td>
      <td>The cumulative insertions observed on the correction buffer across workers and persist sinks.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_sink_correction_max_per_sink_worker_capacity_updates</code></td>
      <td>The maximum capacity observed for the correction buffer of any single persist sink per worker.</td>
      <td><code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_sink_correction_max_per_sink_worker_len_updates</code></td>
      <td>The maximum length observed for the correction buffer of any single persist sink per worker.</td>
      <td><code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_state_apply_spine_fast_path</code></td>
      <td>count of spine diff applications that hit the fast path</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_state_apply_spine_flattened</code></td>
      <td>count of spine diff applications that flatten the trace</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_state_apply_spine_slow_path</code></td>
      <td>count of spine diff applications that hit the slow path</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_state_apply_spine_slow_path_lenient</code></td>
      <td>count of spine diff applications that hit the lenient compaction apply path</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_state_apply_spine_slow_path_lenient_adjustment</code></td>
      <td>count of adjustments made by the lenient compaction apply path</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_state_apply_spine_slow_path_with_reconstruction</code></td>
      <td>count of spine diff applications that hit the slow path with extra spine reconstruction step</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_state_fetch_recent_live_diffs_fast_path</code></td>
      <td>count of fetch_recent_live_diffs that hit the fast path</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_state_fetch_recent_live_diffs_slow_path</code></td>
      <td>count of fetch_recent_live_diffs that hit the slow path</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_state_force_applied_hostname</code></td>
      <td>count of when hostname diffs needed to be force applied</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_state_rollup_at_seqno_migration</code></td>
      <td>count of fetch_rollup_at_seqno calls that only worked because of the migration</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_state_rollup_write_noop</code></td>
      <td>count of no-op rollup writes</td>
      <td><code>reason</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_state_rollup_write_success</code></td>
      <td>count of rollups written successful (may not be linked in to state)</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_state_update_state_empty_path</code></td>
      <td>count of state update applications that found no new updates</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_state_update_state_fast_path</code></td>
      <td>count of state update applications that hit the fast path</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_state_update_state_noop_path</code></td>
      <td>count of state update applications that no-oped due to shared state</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_state_update_state_slow_path</code></td>
      <td>count of state update applications that hit the slow path</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_state_writer_added</code></td>
      <td>count of writers added to the state</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_state_writer_removed</code></td>
      <td>count of writers removed from the state</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_task_total_idle_duration</code></td>
      <td>Seconds of time spent idling, ie. waiting for a task to be woken up.</td>
      <td><code>name</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_task_total_idled_count</code></td>
      <td>The total number of task idles. Useful for computing the average idle time.</td>
      <td><code>name</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_task_total_scheduled_count</code></td>
      <td>The total number of task schedules. Useful for computing the average scheduled time.</td>
      <td><code>name</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_task_total_scheduled_duration</code></td>
      <td>Seconds of time spent scheduled, ie. ready to poll but not yet polled.</td>
      <td><code>name</code></td>
    </tr>
    <tr>
      <td><code>mz_persist_wait_resolved_via_sleep</code></td>
      <td>count of wait-for-uppers resolved via sleep</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_wait_resolved_via_watch</code></td>
      <td>count of wait-for-uppers resolved via watch notify</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_wait_woken_via_sleep</code></td>
      <td>count of wait-for-uppers wakes via sleep</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_wait_woken_via_watch</code></td>
      <td>count of wait-for-uppers wakes via watch notify</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_watch_notify_lagged</code></td>
      <td>count of lagged events in the watch notification broadcast channel</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_watch_notify_noop</code></td>
      <td>count of watch notifications sent to an broadcast channel</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_watch_notify_recv</code></td>
      <td>count of watch notifications received from the broadcast channel</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_watch_notify_sent</code></td>
      <td>count of watch notifications sent to a non-empty broadcast channel</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_watch_notify_upper_sent</code></td>
      <td>count of strict shard upper advances signaled to upper waiters</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_watch_notify_wait_finished</code></td>
      <td>count of watch wait calls resolved</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_persist_watch_notify_wait_started</code></td>
      <td>count of watch wait calls started</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_pgwire_ensure_transaction_seconds_bucket</code></td>
      <td>The time it takes to run `ensure_transactions` when processing pgwire messages.</td>
      <td><code>le</code>, <code>message_type</code></td>
    </tr>
    <tr>
      <td><code>mz_pgwire_ensure_transaction_seconds_count</code></td>
      <td>The time it takes to run `ensure_transactions` when processing pgwire messages.</td>
      <td><code>message_type</code></td>
    </tr>
    <tr>
      <td><code>mz_pgwire_ensure_transaction_seconds_sum</code></td>
      <td>The time it takes to run `ensure_transactions` when processing pgwire messages.</td>
      <td><code>message_type</code></td>
    </tr>
    <tr>
      <td><code>mz_pgwire_message_processing_seconds_bucket</code></td>
      <td>The time it takes to process each of the pgwire message types, measured in the Adapter frontend</td>
      <td><code>le</code>, <code>message_type</code></td>
    </tr>
    <tr>
      <td><code>mz_pgwire_message_processing_seconds_count</code></td>
      <td>The time it takes to process each of the pgwire message types, measured in the Adapter frontend</td>
      <td><code>message_type</code></td>
    </tr>
    <tr>
      <td><code>mz_pgwire_message_processing_seconds_sum</code></td>
      <td>The time it takes to process each of the pgwire message types, measured in the Adapter frontend</td>
      <td><code>message_type</code></td>
    </tr>
    <tr>
      <td><code>mz_pgwire_recv_scheduling_delay_ms_bucket</code></td>
      <td>The time between a pgwire connection&#39;s receiver task being woken up by incoming data and getting polled.</td>
      <td><code>le</code>, <code>message_type</code></td>
    </tr>
    <tr>
      <td><code>mz_pgwire_recv_scheduling_delay_ms_count</code></td>
      <td>The time between a pgwire connection&#39;s receiver task being woken up by incoming data and getting polled.</td>
      <td><code>message_type</code></td>
    </tr>
    <tr>
      <td><code>mz_pgwire_recv_scheduling_delay_ms_sum</code></td>
      <td>The time between a pgwire connection&#39;s receiver task being woken up by incoming data and getting polled.</td>
      <td><code>message_type</code></td>
    </tr>
    <tr>
      <td><code>mz_postgres_per_source_deletes</code></td>
      <td>The number of deletes for all tables in this source</td>
      <td><code>source_id</code></td>
    </tr>
    <tr>
      <td><code>mz_postgres_per_source_ignored_messages</code></td>
      <td>The number of messages ignored because of an irrelevant type or relation_id</td>
      <td><code>source_id</code></td>
    </tr>
    <tr>
      <td><code>mz_postgres_per_source_inserts</code></td>
      <td>The number of inserts for all tables in this source</td>
      <td><code>source_id</code></td>
    </tr>
    <tr>
      <td><code>mz_postgres_per_source_messages_total</code></td>
      <td>The total number of replication messages for this source, not expected to be the sum of the other values.</td>
      <td><code>source_id</code></td>
    </tr>
    <tr>
      <td><code>mz_postgres_per_source_tables_count</code></td>
      <td>The number of upstream tables for this source</td>
      <td><code>source_id</code></td>
    </tr>
    <tr>
      <td><code>mz_postgres_per_source_transactions_total</code></td>
      <td>The number of committed transactions for all tables in this source</td>
      <td><code>source_id</code></td>
    </tr>
    <tr>
      <td><code>mz_postgres_per_source_updates</code></td>
      <td>The number of updates for all tables in this source</td>
      <td><code>source_id</code></td>
    </tr>
    <tr>
      <td><code>mz_postgres_per_source_wal_lsn</code></td>
      <td>LSN of the latest transaction committed for this source, see Postgres Replication docs for more details on LSN</td>
      <td><code>source_id</code></td>
    </tr>
    <tr>
      <td><code>mz_postgres_snapshot_count_latency</code></td>
      <td>The wall time used to obtain snapshot sizes.</td>
      <td><code>source_id</code>, <code>table_name</code></td>
    </tr>
    <tr>
      <td><code>mz_query_total</code></td>
      <td>The total number of queries issued of the given type since process start.</td>
      <td><code>session_type</code>, <code>statement_type</code></td>
    </tr>
    <tr>
      <td><code>mz_replica_info</code></td>
      <td>Maps cluster replica IDs to the replica&#39;s name and size. Constant 1.</td>
      <td><code>cluster_id</code>, <code>name</code>, <code>replica_id</code>, <code>size</code></td>
    </tr>
    <tr>
      <td><code>mz_result_rows_first_to_last_byte_seconds_bucket</code></td>
      <td>The time from just before sending the first result row to sending a final response message after having successfully flushed the last result row to the connection. (This can span multiple FETCH statements.) (This is never observed for unbounded SUBSCRIBEs, i.e., which have no last result row.)</td>
      <td><code>le</code>, <code>statement_type</code></td>
    </tr>
    <tr>
      <td><code>mz_result_rows_first_to_last_byte_seconds_count</code></td>
      <td>The time from just before sending the first result row to sending a final response message after having successfully flushed the last result row to the connection. (This can span multiple FETCH statements.) (This is never observed for unbounded SUBSCRIBEs, i.e., which have no last result row.)</td>
      <td><code>statement_type</code></td>
    </tr>
    <tr>
      <td><code>mz_result_rows_first_to_last_byte_seconds_sum</code></td>
      <td>The time from just before sending the first result row to sending a final response message after having successfully flushed the last result row to the connection. (This can span multiple FETCH statements.) (This is never observed for unbounded SUBSCRIBEs, i.e., which have no last result row.)</td>
      <td><code>statement_type</code></td>
    </tr>
    <tr>
      <td><code>mz_resume_upper</code></td>
      <td>The timestamp-domain resumption frontier chosen for a source&#39;s ingestion</td>
      <td><code>source_id</code></td>
    </tr>
    <tr>
      <td><code>mz_row_set_finishing_seconds_bucket</code></td>
      <td>The time it takes to run RowSetFinishing::finish.</td>
      <td><code>le</code></td>
    </tr>
    <tr>
      <td><code>mz_row_set_finishing_seconds_count</code></td>
      <td>The time it takes to run RowSetFinishing::finish.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_row_set_finishing_seconds_sum</code></td>
      <td>The time it takes to run RowSetFinishing::finish.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_session_startup_table_writes_seconds_bucket</code></td>
      <td>If we had to wait for builtin table writes before processing a query, how long did we wait for.</td>
      <td><code>le</code></td>
    </tr>
    <tr>
      <td><code>mz_session_startup_table_writes_seconds_count</code></td>
      <td>If we had to wait for builtin table writes before processing a query, how long did we wait for.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_session_startup_table_writes_seconds_sum</code></td>
      <td>If we had to wait for builtin table writes before processing a query, how long did we wait for.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_shard_finalization_op_failed</code></td>
      <td>count of shard finalization operations that failed</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_shard_finalization_op_started</code></td>
      <td>count of shard finalization operations that have started</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_shard_finalization_op_succeeded</code></td>
      <td>count of shard finalization operations that succeeded</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_shard_finalization_outstanding</code></td>
      <td>count of shards in need of finalization</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_shard_finalization_pending_commit</code></td>
      <td>count of shards for which finalization has completed but has not yet been durably recorded</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_sink_bytes_committed</code></td>
      <td>The number of bytes committed to the sink.</td>
      <td><code>sink_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sink_bytes_staged</code></td>
      <td>The number of bytes staged but possibly not committed to the sink.</td>
      <td><code>sink_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sink_consumed_progress_records</code></td>
      <td>The number of progress records consumed by the sink.</td>
      <td><code>sink_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sink_iceberg_commit_conflicts</code></td>
      <td>Number of commit conflicts in the iceberg sink</td>
      <td><code>sink_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sink_iceberg_commit_duration_seconds_bucket</code></td>
      <td>Time spent committing batches to Iceberg in seconds</td>
      <td><code>le</code>, <code>sink_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sink_iceberg_commit_duration_seconds_count</code></td>
      <td>Time spent committing batches to Iceberg in seconds</td>
      <td><code>sink_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sink_iceberg_commit_duration_seconds_sum</code></td>
      <td>Time spent committing batches to Iceberg in seconds</td>
      <td><code>sink_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sink_iceberg_commit_failures</code></td>
      <td>Number of commit failures in the iceberg sink</td>
      <td><code>sink_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sink_iceberg_data_files_written</code></td>
      <td>Number of data files written by the iceberg sink</td>
      <td><code>sink_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sink_iceberg_delete_files_written</code></td>
      <td>Number of delete files written by the iceberg sink</td>
      <td><code>sink_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sink_iceberg_snapshots_committed</code></td>
      <td>Number of snapshots committed by the iceberg sink</td>
      <td><code>sink_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sink_iceberg_stashed_rows</code></td>
      <td>Number of stashed rows in the iceberg sink</td>
      <td><code>sink_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sink_iceberg_writer_close_duration_seconds_bucket</code></td>
      <td>Time spent closing Iceberg DeltaWriters in seconds</td>
      <td><code>le</code>, <code>sink_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sink_iceberg_writer_close_duration_seconds_count</code></td>
      <td>Time spent closing Iceberg DeltaWriters in seconds</td>
      <td><code>sink_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sink_iceberg_writer_close_duration_seconds_sum</code></td>
      <td>Time spent closing Iceberg DeltaWriters in seconds</td>
      <td><code>sink_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sink_info</code></td>
      <td>Maps user sink IDs to the sink&#39;s type, envelope type, and cluster. Constant 1.</td>
      <td><code>cluster_id</code>, <code>envelope_type</code>, <code>sink_id</code>, <code>type</code></td>
    </tr>
    <tr>
      <td><code>mz_sink_messages_committed</code></td>
      <td>The number of messages committed to the sink.</td>
      <td><code>sink_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sink_messages_staged</code></td>
      <td>The number of messages staged but possibly not committed to the sink.</td>
      <td><code>sink_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sink_oustanding_progress_records</code></td>
      <td>The number of outstanding progress records that need to be read before the sink can resume.</td>
      <td><code>sink_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sink_partition_count</code></td>
      <td>The number of partitions this sink is publishing to.</td>
      <td><code>sink_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sink_rdkafka_connects</code></td>
      <td>The number of connection attempts, including successful and failed attempts, and name resolution failures across all brokers.</td>
      <td><code>sink_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sink_rdkafka_disconnects</code></td>
      <td>The number of disconnections, whether triggered by the broker, the network, the load balancer, or something else across all brokers.</td>
      <td><code>sink_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sink_rdkafka_msg_cnt</code></td>
      <td>The current number of messages in producer queues.</td>
      <td><code>sink_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sink_rdkafka_msg_size</code></td>
      <td>The current total size of messages in producer queues.</td>
      <td><code>sink_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sink_rdkafka_outbuf_cnt</code></td>
      <td>The number of requests awaiting transmission across all brokers.</td>
      <td><code>sink_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sink_rdkafka_outbuf_msg_cnt</code></td>
      <td>The number of messages awaiting transmission across all brokers.</td>
      <td><code>sink_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sink_rdkafka_req_timeouts</code></td>
      <td>The total number of requests that timed out across all brokers.</td>
      <td><code>sink_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sink_rdkafka_tx</code></td>
      <td>The total number of requests sent to brokers.</td>
      <td><code>sink_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sink_rdkafka_tx_bytes</code></td>
      <td>The total number of bytes transmitted to brokers.</td>
      <td><code>sink_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sink_rdkafka_txerrs</code></td>
      <td>The total number of transmission errors across all brokers.</td>
      <td><code>sink_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sink_rdkafka_txmsg_bytes</code></td>
      <td>The total number of bytes transmitted (produced) to brokers.</td>
      <td><code>sink_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sink_rdkafka_txmsgs</code></td>
      <td>The total number of messages transmitted (produced) to brokers.</td>
      <td><code>sink_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sink_rdkafka_txretries</code></td>
      <td>The total number of request retries across all brokers.</td>
      <td><code>sink_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sink_rdkafka_waitresp_cnt</code></td>
      <td>The number of requests in-flight across all brokers that are awaiting a response.</td>
      <td><code>sink_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sink_rdkafka_waitresp_msg_cnt</code></td>
      <td>The number of messages in-flight across all brokers that are awaiting a response.</td>
      <td><code>sink_id</code></td>
    </tr>
    <tr>
      <td><code>mz_slow_message_handling_bucket</code></td>
      <td>Latency for ALL coordinator messages. &#39;slow&#39; is in the name for legacy reasons, but is not accurate.</td>
      <td><code>le</code>, <code>message_kind</code></td>
    </tr>
    <tr>
      <td><code>mz_slow_message_handling_count</code></td>
      <td>Latency for ALL coordinator messages. &#39;slow&#39; is in the name for legacy reasons, but is not accurate.</td>
      <td><code>message_kind</code></td>
    </tr>
    <tr>
      <td><code>mz_slow_message_handling_sum</code></td>
      <td>Latency for ALL coordinator messages. &#39;slow&#39; is in the name for legacy reasons, but is not accurate.</td>
      <td><code>message_kind</code></td>
    </tr>
    <tr>
      <td><code>mz_source_bytes_indexed</code></td>
      <td>The number of bytes of the source envelope state kept. This will be specific to the envelope in use.</td>
      <td><code>parent_source_id</code>, <code>shard_id</code>, <code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_source_bytes_received</code></td>
      <td>The number of bytes worth of messages the worker has received from upstream. The way the bytes are counted is source-specific.</td>
      <td><code>parent_source_id</code>, <code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_source_commit_upper_accepted_times</code></td>
      <td>The number of accepted remap bindings that are held in the reclock commit upper operator.</td>
      <td><code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_source_commit_upper_ready_times</code></td>
      <td>The number of ready remap bindings that are held in the reclock commit upper operator.</td>
      <td><code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_source_envelope_state_tombstones</code></td>
      <td>The number of outstanding tombstones in the source envelope state. This will be specific to the envelope in use</td>
      <td><code>parent_source_id</code>, <code>shard_id</code>, <code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_source_error_inserts</code></td>
      <td>A counter representing the actual number of errors being inserted to the data shard</td>
      <td><code>shard</code>, <code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_source_error_retractions</code></td>
      <td>A counter representing the actual number of errors being retracted from the data shard</td>
      <td><code>shard</code>, <code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_source_info</code></td>
      <td>Maps user source IDs to the source&#39;s type, envelope type, and cluster. Constant 1.</td>
      <td><code>cluster_id</code>, <code>envelope_type</code>, <code>source_id</code>, <code>type</code></td>
    </tr>
    <tr>
      <td><code>mz_source_messages_received</code></td>
      <td>The number of raw messages the worker has received from upstream.</td>
      <td><code>parent_source_id</code>, <code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_source_offset_commit_failures</code></td>
      <td>A counter representing how many times we have failed to commit offsets for a source</td>
      <td><code>source_id</code></td>
    </tr>
    <tr>
      <td><code>mz_source_offset_committed</code></td>
      <td>The total number of _values_ (source-defined unit) we have fully processed, and storage and committed.</td>
      <td><code>shard_id</code>, <code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_source_offset_known</code></td>
      <td>The total number of _values_ (source-defined unit) present in upstream.</td>
      <td><code>shard_id</code>, <code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_source_processed_batches</code></td>
      <td>A counter representing the number of persist sink batches with actual data we have successfully processed.</td>
      <td><code>shard</code>, <code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_source_progress</code></td>
      <td>A timestamp gauge representing forward progess in the data shard</td>
      <td><code>shard</code>, <code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_source_records_indexed</code></td>
      <td>The number of records in the source envelope state. This will be specific to the envelope in use</td>
      <td><code>parent_source_id</code>, <code>shard_id</code>, <code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_source_rehydration_latency_ms</code></td>
      <td>The amount of time in milliseconds it took for the worker to rehydrate the source envelope state. This will be specific to the envelope in use.</td>
      <td><code>envelope</code>, <code>parent_source_id</code>, <code>shard_id</code>, <code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_source_row_inserts</code></td>
      <td>A counter representing the actual number of rows being inserted to the data shard</td>
      <td><code>shard</code>, <code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_source_row_retractions</code></td>
      <td>A counter representing the actual number of rows being retracted from the data shard</td>
      <td><code>shard</code>, <code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_source_snapshot_committed</code></td>
      <td>Whether or not the worker has committed the initial snapshot for a source.</td>
      <td><code>parent_source_id</code>, <code>shard_id</code>, <code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_source_snapshot_records_known</code></td>
      <td>The total number of records in the source&#39;s snapshot</td>
      <td><code>parent_source_id</code>, <code>shard_id</code>, <code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_source_snapshot_records_staged</code></td>
      <td>The total number of records read from the source&#39;s snapshot</td>
      <td><code>parent_source_id</code>, <code>shard_id</code>, <code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_source_updates_committed</code></td>
      <td>The number of updates (inserts &#43; deletes) the worker has committed into the storage layer.</td>
      <td><code>parent_source_id</code>, <code>shard_id</code>, <code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_source_updates_staged</code></td>
      <td>The number of updates (inserts &#43; deletes) the worker has written but not yet committed to the storage layer.</td>
      <td><code>parent_source_id</code>, <code>shard_id</code>, <code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sql_server_per_source_deletes</code></td>
      <td>The number of deletes for all tables in this source</td>
      <td><code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sql_server_per_source_ignored_messages</code></td>
      <td>The number of messages ignored because of an irrelevant type or relation_id</td>
      <td><code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sql_server_per_source_inserts</code></td>
      <td>The number of inserts for all tables in this source</td>
      <td><code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sql_server_per_source_updates</code></td>
      <td>The number of updates for all tables in this source</td>
      <td><code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sql_server_snapshot_count_latency</code></td>
      <td>The wall time used to obtain snapshot sizes.</td>
      <td><code>source_id</code>, <code>table_name</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sql_server_snapshot_table_count</code></td>
      <td>The number of tables that SQL Server still needs to snapshot</td>
      <td><code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sql_server_snapshot_table_lock</code></td>
      <td>The upstream tables locked for snapshot.</td>
      <td><code>source_id</code>, <code>table_name</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_start_time_environmentd</code></td>
      <td>Time in milliseconds from environmentd start until the adapter is ready.</td>
      <td><code>build_type</code>, <code>version</code></td>
    </tr>
    <tr>
      <td><code>mz_statement_logging_actual_bytes</code></td>
      <td>The total amount of SQL text that was logged by statement logging.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_statement_logging_record_count</code></td>
      <td>The total number of SQL statements tagged with whether or not they were recorded.</td>
      <td><code>sample</code></td>
    </tr>
    <tr>
      <td><code>mz_statement_logging_unsampled_bytes</code></td>
      <td>The total amount of SQL text that would have been logged if statement logging were unsampled.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_storage_command_message_bytes_total</code></td>
      <td>The total number of bytes sent in storage command messages.</td>
      <td><code>instance_id</code>, <code>replica_id</code></td>
    </tr>
    <tr>
      <td><code>mz_storage_commands_total</code></td>
      <td>The total number of storage commands sent.</td>
      <td><code>command_type</code>, <code>instance_id</code>, <code>replica_id</code></td>
    </tr>
    <tr>
      <td><code>mz_storage_controller_connected_replica_count</code></td>
      <td>The number of replicas successfully connected to the storage controller.</td>
      <td><code>instance_id</code></td>
    </tr>
    <tr>
      <td><code>mz_storage_controller_history_command_count</code></td>
      <td>The number of commands in the controller&#39;s command history.</td>
      <td><code>command_type</code>, <code>instance_id</code></td>
    </tr>
    <tr>
      <td><code>mz_storage_controller_replica_connect_wait_time_seconds_total</code></td>
      <td>The total time the storage controller spent waiting for replica (re-)connection.</td>
      <td><code>instance_id</code>, <code>replica_id</code></td>
    </tr>
    <tr>
      <td><code>mz_storage_controller_replica_connects_total</code></td>
      <td>The total number of replica (re-)connections made by the storage controller.</td>
      <td><code>instance_id</code>, <code>replica_id</code></td>
    </tr>
    <tr>
      <td><code>mz_storage_regressed_offset_known</code></td>
      <td>number of regressed offset_known stats for this id</td>
      <td><code>id</code></td>
    </tr>
    <tr>
      <td><code>mz_storage_response_message_bytes_total</code></td>
      <td>The total number of bytes received in storage response messages.</td>
      <td><code>instance_id</code>, <code>replica_id</code></td>
    </tr>
    <tr>
      <td><code>mz_storage_responses_total</code></td>
      <td>The total number of storage responses received.</td>
      <td><code>instance_id</code>, <code>replica_id</code>, <code>response_type</code></td>
    </tr>
    <tr>
      <td><code>mz_storage_rocksdb_multi_get_count_total</code></td>
      <td>The number of calls to rocksdb multi_get.</td>
      <td><code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_storage_rocksdb_multi_get_latency_bucket</code></td>
      <td>The latencies, in fractional seconds, of getting batches of values from RocksDB for this source.</td>
      <td><code>le</code>, <code>source_id</code></td>
    </tr>
    <tr>
      <td><code>mz_storage_rocksdb_multi_get_latency_count</code></td>
      <td>The latencies, in fractional seconds, of getting batches of values from RocksDB for this source.</td>
      <td><code>source_id</code></td>
    </tr>
    <tr>
      <td><code>mz_storage_rocksdb_multi_get_latency_sum</code></td>
      <td>The latencies, in fractional seconds, of getting batches of values from RocksDB for this source.</td>
      <td><code>source_id</code></td>
    </tr>
    <tr>
      <td><code>mz_storage_rocksdb_multi_get_result_bytes_total</code></td>
      <td>The total size of records returned, when getting batches of values from RocksDB for this source.</td>
      <td><code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_storage_rocksdb_multi_get_result_count_total</code></td>
      <td>The number of non-empty records returned, when getting batches of values from RocksDB for this source.</td>
      <td><code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_storage_rocksdb_multi_get_size_total</code></td>
      <td>The batch size, of getting batches of values from RocksDB for this source.</td>
      <td><code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_storage_rocksdb_multi_put_count_total</code></td>
      <td>The number of calls to rocksdb multi_put.</td>
      <td><code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_storage_rocksdb_multi_put_latency_bucket</code></td>
      <td>The latencies, in fractional seconds, of putting batches of values into RocksDB for this source.</td>
      <td><code>le</code>, <code>source_id</code></td>
    </tr>
    <tr>
      <td><code>mz_storage_rocksdb_multi_put_latency_count</code></td>
      <td>The latencies, in fractional seconds, of putting batches of values into RocksDB for this source.</td>
      <td><code>source_id</code></td>
    </tr>
    <tr>
      <td><code>mz_storage_rocksdb_multi_put_latency_sum</code></td>
      <td>The latencies, in fractional seconds, of putting batches of values into RocksDB for this source.</td>
      <td><code>source_id</code></td>
    </tr>
    <tr>
      <td><code>mz_storage_rocksdb_multi_put_size_total</code></td>
      <td>The batch size, of putting batches of values into RocksDB for this source.</td>
      <td><code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_storage_upsert_backpressure_emitted_bytes</code></td>
      <td>A counter with the number of emitted bytes.</td>
      <td><code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_storage_upsert_backpressure_last_backpressured_bytes</code></td>
      <td>The last count of bytes we are waiting to be retired in the operator. This cannot be directly compared to `retired_bytes`, but CAN indicate that backpressure is happening.</td>
      <td><code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_storage_upsert_backpressure_retired_bytes</code></td>
      <td>A counter with the number of bytes retired by downstream processing.</td>
      <td><code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_storage_upsert_deletes_total</code></td>
      <td>The number of deletes done by the upsert operator.</td>
      <td><code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_storage_upsert_inserts_total</code></td>
      <td>The number of inserts done by the upsert operator</td>
      <td><code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_storage_upsert_merge_snapshot_deletes_total</code></td>
      <td>The number of deletes in a batch for merging snapshot updates for this source.</td>
      <td><code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_storage_upsert_merge_snapshot_inserts_total</code></td>
      <td>The number of inserts in a batch for merging snapshot updates for this source.</td>
      <td><code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_storage_upsert_merge_snapshot_latency_bucket</code></td>
      <td>The latencies, in fractional seconds, of merging snapshot updates into upsert state for this source. Specific implementations of upsert state may have more detailed metrics about sub-batches.</td>
      <td><code>le</code>, <code>source_id</code></td>
    </tr>
    <tr>
      <td><code>mz_storage_upsert_merge_snapshot_latency_count</code></td>
      <td>The latencies, in fractional seconds, of merging snapshot updates into upsert state for this source. Specific implementations of upsert state may have more detailed metrics about sub-batches.</td>
      <td><code>source_id</code></td>
    </tr>
    <tr>
      <td><code>mz_storage_upsert_merge_snapshot_latency_sum</code></td>
      <td>The latencies, in fractional seconds, of merging snapshot updates into upsert state for this source. Specific implementations of upsert state may have more detailed metrics about sub-batches.</td>
      <td><code>source_id</code></td>
    </tr>
    <tr>
      <td><code>mz_storage_upsert_merge_snapshot_updates_total</code></td>
      <td>The batch size, of merging snapshot updates into upsert state for this source. Specific implementations of upsert state may have more detailed metrics about sub-batches.</td>
      <td><code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_storage_upsert_multi_get_latency_bucket</code></td>
      <td>The latencies, in fractional seconds, of getting values from the upsert state for this source. Specific implementations of upsert state may have more detailed metrics about sub-batches.</td>
      <td><code>le</code>, <code>source_id</code></td>
    </tr>
    <tr>
      <td><code>mz_storage_upsert_multi_get_latency_count</code></td>
      <td>The latencies, in fractional seconds, of getting values from the upsert state for this source. Specific implementations of upsert state may have more detailed metrics about sub-batches.</td>
      <td><code>source_id</code></td>
    </tr>
    <tr>
      <td><code>mz_storage_upsert_multi_get_latency_sum</code></td>
      <td>The latencies, in fractional seconds, of getting values from the upsert state for this source. Specific implementations of upsert state may have more detailed metrics about sub-batches.</td>
      <td><code>source_id</code></td>
    </tr>
    <tr>
      <td><code>mz_storage_upsert_multi_get_result_bytes_total</code></td>
      <td>The total size of records returned in a multi_get batch. Specific implementations of upsert state may have more detailed metrics about sub-batches.</td>
      <td><code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_storage_upsert_multi_get_result_count_total</code></td>
      <td>The number of non-empty records returned in a multi_get batch. Specific implementations of upsert state may have more detailed metrics about sub-batches.</td>
      <td><code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_storage_upsert_multi_get_size_total</code></td>
      <td>The batch size, of getting values from the upsert state for this source. Specific implementations of upsert state may have more detailed metrics about sub-batches.</td>
      <td><code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_storage_upsert_multi_put_latency_bucket</code></td>
      <td>The latencies, in fractional seconds, of getting values into the upsert state for this source. Specific implementations of upsert state may have more detailed metrics about sub-batches.</td>
      <td><code>le</code>, <code>source_id</code></td>
    </tr>
    <tr>
      <td><code>mz_storage_upsert_multi_put_latency_count</code></td>
      <td>The latencies, in fractional seconds, of getting values into the upsert state for this source. Specific implementations of upsert state may have more detailed metrics about sub-batches.</td>
      <td><code>source_id</code></td>
    </tr>
    <tr>
      <td><code>mz_storage_upsert_multi_put_latency_sum</code></td>
      <td>The latencies, in fractional seconds, of getting values into the upsert state for this source. Specific implementations of upsert state may have more detailed metrics about sub-batches.</td>
      <td><code>source_id</code></td>
    </tr>
    <tr>
      <td><code>mz_storage_upsert_multi_put_size_total</code></td>
      <td>The batch size, of getting values into the upsert state for this source. Specific implementations of upsert state may have more detailed metrics about sub-batches.</td>
      <td><code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_storage_upsert_state_rehydration_latency</code></td>
      <td>The latency, per-worker, in fractional seconds, of rehydrating the upsert state for this source</td>
      <td><code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_storage_upsert_state_rehydration_total</code></td>
      <td>The number of values per-worker, rehydrated into the upsert state for this source</td>
      <td><code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_storage_upsert_state_rehydration_updates</code></td>
      <td>The number of updates (both negative and positive), per-worker, rehydrated into the upsert state for this source</td>
      <td><code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_storage_upsert_updates_total</code></td>
      <td>The number of updates done by the upsert operator</td>
      <td><code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_storage_usage_collection_time_seconds_bucket</code></td>
      <td>The number of seconds the coord spends collecting usage metrics from storage.</td>
      <td><code>le</code></td>
    </tr>
    <tr>
      <td><code>mz_storage_usage_collection_time_seconds_count</code></td>
      <td>The number of seconds the coord spends collecting usage metrics from storage.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_storage_usage_collection_time_seconds_sum</code></td>
      <td>The number of seconds the coord spends collecting usage metrics from storage.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_subscribe_outputs</code></td>
      <td>The total number of different subscribe outputs used</td>
      <td><code>session_type</code>, <code>subscribe_output</code></td>
    </tr>
    <tr>
      <td><code>mz_subscribe_snapshots_skipped_total</code></td>
      <td>The number of collection snapshots that were skipped by the subscribe snapshot optimization.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_time_to_first_row_seconds_bucket</code></td>
      <td>Latency of an execute for a successful query from pgwire&#39;s perspective</td>
      <td><code>application_name</code>, <code>instance_id</code>, <code>isolation_level</code>, <code>le</code>, <code>strategy</code></td>
    </tr>
    <tr>
      <td><code>mz_time_to_first_row_seconds_count</code></td>
      <td>Latency of an execute for a successful query from pgwire&#39;s perspective</td>
      <td><code>application_name</code>, <code>instance_id</code>, <code>isolation_level</code>, <code>strategy</code></td>
    </tr>
    <tr>
      <td><code>mz_time_to_first_row_seconds_sum</code></td>
      <td>Latency of an execute for a successful query from pgwire&#39;s perspective</td>
      <td><code>application_name</code>, <code>instance_id</code>, <code>isolation_level</code>, <code>strategy</code></td>
    </tr>
    <tr>
      <td><code>mz_timely_step_duration_seconds_bucket</code></td>
      <td>The time spent in each compute step_or_park call</td>
      <td><code>cluster</code>, <code>le</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_timely_step_duration_seconds_count</code></td>
      <td>The time spent in each compute step_or_park call</td>
      <td><code>cluster</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_timely_step_duration_seconds_sum</code></td>
      <td>The time spent in each compute step_or_park call</td>
      <td><code>cluster</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_timestamp_difference_for_bounded_staleness_ms_bucket</code></td>
      <td>How much older bounded-staleness timestamps are compared to serializable, in milliseconds. Measures the actual staleness incurred.</td>
      <td><code>compute_instance</code>, <code>le</code></td>
    </tr>
    <tr>
      <td><code>mz_timestamp_difference_for_bounded_staleness_ms_count</code></td>
      <td>How much older bounded-staleness timestamps are compared to serializable, in milliseconds. Measures the actual staleness incurred.</td>
      <td><code>compute_instance</code></td>
    </tr>
    <tr>
      <td><code>mz_timestamp_difference_for_bounded_staleness_ms_sum</code></td>
      <td>How much older bounded-staleness timestamps are compared to serializable, in milliseconds. Measures the actual staleness incurred.</td>
      <td><code>compute_instance</code></td>
    </tr>
    <tr>
      <td><code>mz_tokio_blocking_queue_depth</code></td>
      <td>The number of tasks currently scheduled in the blocking thread pool, spawned using spawn_blocking.</td>
      <td><code>runtime</code></td>
    </tr>
    <tr>
      <td><code>mz_tokio_budget_forced_yield_count</code></td>
      <td>The number of times that tasks have been forced to yield back to the scheduler after exhausting their task budgets.</td>
      <td><code>runtime</code></td>
    </tr>
    <tr>
      <td><code>mz_tokio_global_queue_depth</code></td>
      <td>The number of tasks currently scheduled in the runtime&#39;s global queue.</td>
      <td><code>runtime</code></td>
    </tr>
    <tr>
      <td><code>mz_tokio_num_alive_tasks</code></td>
      <td>The current number of alive tasks in the runtime.</td>
      <td><code>runtime</code></td>
    </tr>
    <tr>
      <td><code>mz_tokio_num_blocking_threads</code></td>
      <td>The number of additional threads spawned by the runtime.</td>
      <td><code>runtime</code></td>
    </tr>
    <tr>
      <td><code>mz_tokio_num_idle_blocking_threads</code></td>
      <td>The number of idle threads which have spawned by the runtime for spawn_blocking calls.</td>
      <td><code>runtime</code></td>
    </tr>
    <tr>
      <td><code>mz_tokio_num_workers</code></td>
      <td>The number of worker threads used by the runtime.</td>
      <td><code>runtime</code></td>
    </tr>
    <tr>
      <td><code>mz_tokio_remote_schedule_count</code></td>
      <td>The number of tasks scheduled from outside of the runtime.</td>
      <td><code>runtime</code></td>
    </tr>
    <tr>
      <td><code>mz_tokio_spawned_tasks_count</code></td>
      <td>The number of tasks spawned in this runtime since it was created.</td>
      <td><code>runtime</code></td>
    </tr>
    <tr>
      <td><code>mz_tokio_worker_local_queue_depth</code></td>
      <td>The number of tasks currently scheduled in the workers&#39; local queues.</td>
      <td><code>runtime</code></td>
    </tr>
    <tr>
      <td><code>mz_tokio_worker_local_schedule_count</code></td>
      <td>The number of tasks scheduled from within the runtime on the given worker&#39;s local queue.</td>
      <td><code>runtime</code></td>
    </tr>
    <tr>
      <td><code>mz_tokio_worker_mean_poll_time</code></td>
      <td>The mean duration of task polls in seconds.</td>
      <td><code>runtime</code></td>
    </tr>
    <tr>
      <td><code>mz_tokio_worker_noop_count</code></td>
      <td>The number of times the given worker thread unparked but performed no work before parking again.</td>
      <td><code>runtime</code></td>
    </tr>
    <tr>
      <td><code>mz_tokio_worker_overflow_count</code></td>
      <td>The number of times the given worker thread saturated its local queue.</td>
      <td><code>runtime</code></td>
    </tr>
    <tr>
      <td><code>mz_tokio_worker_park_count</code></td>
      <td>The total number of times the worker threads have parked.</td>
      <td><code>runtime</code></td>
    </tr>
    <tr>
      <td><code>mz_tokio_worker_park_unpark_count</code></td>
      <td>The total number of times the worker threads have parked and unparked.</td>
      <td><code>runtime</code></td>
    </tr>
    <tr>
      <td><code>mz_tokio_worker_poll_count</code></td>
      <td>The number of tasks the given worker thread has polled.</td>
      <td><code>runtime</code></td>
    </tr>
    <tr>
      <td><code>mz_tokio_worker_steal_count</code></td>
      <td>The number of tasks the given worker thread stole from another worker thread.</td>
      <td><code>runtime</code></td>
    </tr>
    <tr>
      <td><code>mz_tokio_worker_steal_operations</code></td>
      <td>The number of times the given worker thread stole tasks from another worker thread.</td>
      <td><code>runtime</code></td>
    </tr>
    <tr>
      <td><code>mz_tokio_worker_total_busy_duration</code></td>
      <td>The amount of time the worker threads have been busy, in seconds.</td>
      <td><code>runtime</code></td>
    </tr>
    <tr>
      <td><code>mz_ts_oracle_batched_op_count</code></td>
      <td>count of batched operations</td>
      <td><code>op</code></td>
    </tr>
    <tr>
      <td><code>mz_ts_oracle_batches_count</code></td>
      <td>count of batches of operations</td>
      <td><code>op</code></td>
    </tr>
    <tr>
      <td><code>mz_ts_oracle_failed_count</code></td>
      <td>count of oracle operations failed</td>
      <td><code>op</code></td>
    </tr>
    <tr>
      <td><code>mz_ts_oracle_retry_finished_count</code></td>
      <td>count of retry loops finished</td>
      <td><code>op</code></td>
    </tr>
    <tr>
      <td><code>mz_ts_oracle_retry_retries_count</code></td>
      <td>count of total attempts by retry loops</td>
      <td><code>op</code></td>
    </tr>
    <tr>
      <td><code>mz_ts_oracle_retry_sleep_seconds</code></td>
      <td>time spent in retry loop backoff</td>
      <td><code>op</code></td>
    </tr>
    <tr>
      <td><code>mz_ts_oracle_retry_started_count</code></td>
      <td>count of retry loops started</td>
      <td><code>op</code></td>
    </tr>
    <tr>
      <td><code>mz_ts_oracle_seconds</code></td>
      <td>time spent in oracle operations</td>
      <td><code>op</code></td>
    </tr>
    <tr>
      <td><code>mz_ts_oracle_started_count</code></td>
      <td>count of oracle operations started</td>
      <td><code>op</code></td>
    </tr>
    <tr>
      <td><code>mz_ts_oracle_succeeded_count</code></td>
      <td>count of oracle operations succeeded</td>
      <td><code>op</code></td>
    </tr>
    <tr>
      <td><code>mz_txn_batch_commit_bytes</code></td>
      <td>total bytes committed via txn</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_txn_batch_commit_count</code></td>
      <td>count of batches committed via txn</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_txn_batch_unapplied_bytes</code></td>
      <td>total bytes committed via txn but not yet applied</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_txn_batch_unapplied_count</code></td>
      <td>count of batches committed via txn but not yet applied</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_txn_batch_unapplied_min_ts</code></td>
      <td>minimum ts of txn committed via txn but not yet applied</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_txn_data_shard_count</code></td>
      <td>count of data shards registered to the txn set</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_txn_op_duration_seconds</code></td>
      <td>time spent running a txn operation</td>
      <td><code>op</code></td>
    </tr>
    <tr>
      <td><code>mz_txn_op_errored_count</code></td>
      <td>count of times a txn operation errored</td>
      <td><code>op</code></td>
    </tr>
    <tr>
      <td><code>mz_txn_op_retry_count</code></td>
      <td>count of times a txn operation retried</td>
      <td><code>op</code></td>
    </tr>
    <tr>
      <td><code>mz_txn_op_started_count</code></td>
      <td>count of times a txn operation started</td>
      <td><code>op</code></td>
    </tr>
    <tr>
      <td><code>mz_txn_op_succeeded_count</code></td>
      <td>count of times a txn operation succeeded</td>
      <td><code>op</code></td>
    </tr>
    <tr>
      <td><code>mz_webhook_get_appender_count</code></td>
      <td>Count of getting a webhook appender from the Coordinator.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>mz_webhook_validation_reduce_failures</code></td>
      <td>Count of how many times we&#39;ve failed to reduce a webhook source&#39;s CHECK statement.</td>
      <td><code>reason</code></td>
    </tr>
    <tr>
      <td><code>orchestratord_is_leader</code></td>
      <td>Whether this operator replica holds the controller leadership lease, and is therefore the replica reconciling. Summed across the replicas this should be 1. A sustained 0 means no replica can take the lease, for instance because the service account lacks permission on leases, and the operator is reconciling nothing.</td>
      <td></td>
    </tr>
    <tr>
      <td><code>outer_join_lowering_cases</code></td>
      <td>How many times the different outer join lowering cases happened.</td>
      <td><code>case</code></td>
    </tr>
    <tr>
      <td><code>transform_hits</code></td>
      <td>How many times a given transform changed the plan.</td>
      <td><code>transform</code></td>
    </tr>
    <tr>
      <td><code>transform_total</code></td>
      <td>How many times a given transform was applied.</td>
      <td><code>transform</code></td>
    </tr>
  </tbody>
</table>

---

## Cloud

This section covers monitoring and alerting for Materialize Cloud.

### Monitoring

You can monitor the performance and overall health of your Materialize region.
To help you get started, the following guides are available:

- [Datadog](/manage/monitor/cloud/datadog/)

- [Grafana](/manage/monitor/cloud/grafana/)

### Alerting

After setting up a monitoring tool, you can configure alert rules. Alert rules
send a notification when a metric surpasses a threshold. This will help you
prevent operational incidents. For alert rules guidelines, see
[Alerting](/manage/monitor/cloud/alerting/).

---

## Essential metrics

This page lists the essential Prometheus metrics exposed by Materialize: the
ones we recommend building dashboards and alerts on. This list may evolve as
we add observability for new features and refine what's most useful.

The metrics are grouped by the component of Materialize they describe. A
grouping is shown only when it has at least one metric. For the complete list
of metrics Materialize exposes, see [Appendix:
Metrics](/manage/monitor/appendix-metrics/).

<h2 id="environment-level-metrics">Environment-level metrics</h2>
Metrics for the SQL control plane: client connections, availability, and the catalog.
<table>
  <thead>
    <tr>
      <th>Metric</th>
      <th>Description</th>
      <th>Labels</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>mz_active_sessions</code></td>
      <td>The number of active coordinator sessions.</td>
      <td><code>session_type</code></td>
    </tr>
    <tr>
      <td><code>mz_active_subscribes</code></td>
      <td>The number of active SUBSCRIBE queries.</td>
      <td><code>session_type</code></td>
    </tr>
    <tr>
      <td><code>mz_adapter_commands</code></td>
      <td>The total number of adapter commands issued of the given type since process start.</td>
      <td><code>application_name</code>, <code>command_type</code>, <code>status</code></td>
    </tr>
    <tr>
      <td><code>mz_object_info</code></td>
      <td>Maps catalog object IDs to the object&#39;s name, schema, database, and type. Constant 1.</td>
      <td><code>database_name</code>, <code>global_id</code>, <code>name</code>, <code>object_id</code>, <code>schema_name</code>, <code>type</code></td>
    </tr>
    <tr>
      <td><code>mz_query_total</code></td>
      <td>The total number of queries issued of the given type since process start.</td>
      <td><code>session_type</code>, <code>statement_type</code></td>
    </tr>
  </tbody>
</table>

<h2 id="compute-metrics">Compute metrics</h2>
Metrics for compute objects, such as indexes and materialized views, running on <a href="/concepts/clusters/" >clusters</a> and their replicas.
<table>
  <thead>
    <tr>
      <th>Metric</th>
      <th>Description</th>
      <th>Labels</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>mz_arrangement_maintenance_seconds_total</code></td>
      <td>The total time spent maintaining arrangements.</td>
      <td><code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_cluster_info</code></td>
      <td>Maps cluster IDs to the cluster&#39;s name and size. Constant 1.</td>
      <td><code>cluster_id</code>, <code>name</code>, <code>size</code></td>
    </tr>
    <tr>
      <td><code>mz_compute_commands_total</code></td>
      <td>The total number of compute commands sent.</td>
      <td><code>command_type</code>, <code>instance_id</code>, <code>replica_id</code></td>
    </tr>
    <tr>
      <td><code>mz_compute_controller_hydration_queue_size</code></td>
      <td>The size of the compute hydration queue.</td>
      <td><code>instance_id</code>, <code>replica_id</code></td>
    </tr>
    <tr>
      <td><code>mz_compute_peek_duration_seconds_bucket</code></td>
      <td>A histogram of peek durations since restart.</td>
      <td><code>instance_id</code>, <code>le</code>, <code>result</code></td>
    </tr>
    <tr>
      <td><code>mz_compute_peek_duration_seconds_count</code></td>
      <td>A histogram of peek durations since restart.</td>
      <td><code>instance_id</code>, <code>result</code></td>
    </tr>
    <tr>
      <td><code>mz_compute_peek_duration_seconds_sum</code></td>
      <td>A histogram of peek durations since restart.</td>
      <td><code>instance_id</code>, <code>result</code></td>
    </tr>
    <tr>
      <td><code>mz_compute_replica_history_dataflow_count</code></td>
      <td>The number of dataflows in the replica&#39;s command history.</td>
      <td><code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_dataflow_wallclock_lag_seconds</code></td>
      <td>A summary of the second-by-second lag of the dataflow frontier relative to wallclock time, aggregated over the last minute.</td>
      <td><code>collection_id</code>, <code>instance_id</code>, <code>quantile</code>, <code>replica_id</code></td>
    </tr>
    <tr>
      <td><code>mz_replica_info</code></td>
      <td>Maps cluster replica IDs to the replica&#39;s name and size. Constant 1.</td>
      <td><code>cluster_id</code>, <code>name</code>, <code>replica_id</code>, <code>size</code></td>
    </tr>
  </tbody>
</table>

<h2 id="source-metrics">Source metrics</h2>
Metrics for data ingestion from external systems.
<table>
  <thead>
    <tr>
      <th>Metric</th>
      <th>Description</th>
      <th>Labels</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>mz_dataflow_wallclock_lag_seconds</code></td>
      <td>A summary of the second-by-second lag of the dataflow frontier relative to wallclock time, aggregated over the last minute.</td>
      <td><code>collection_id</code>, <code>instance_id</code>, <code>quantile</code>, <code>replica_id</code></td>
    </tr>
    <tr>
      <td><code>mz_source_bytes_received</code></td>
      <td>The number of bytes worth of messages the worker has received from upstream. The way the bytes are counted is source-specific.</td>
      <td><code>parent_source_id</code>, <code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_source_info</code></td>
      <td>Maps user source IDs to the source&#39;s type, envelope type, and cluster. Constant 1.</td>
      <td><code>cluster_id</code>, <code>envelope_type</code>, <code>source_id</code>, <code>type</code></td>
    </tr>
    <tr>
      <td><code>mz_source_messages_received</code></td>
      <td>The number of raw messages the worker has received from upstream.</td>
      <td><code>parent_source_id</code>, <code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_source_offset_commit_failures</code></td>
      <td>A counter representing how many times we have failed to commit offsets for a source</td>
      <td><code>source_id</code></td>
    </tr>
    <tr>
      <td><code>mz_source_offset_committed</code></td>
      <td>The total number of _values_ (source-defined unit) we have fully processed, and storage and committed.</td>
      <td><code>shard_id</code>, <code>source_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_source_offset_known</code></td>
      <td>The total number of _values_ (source-defined unit) present in upstream.</td>
      <td><code>shard_id</code>, <code>source_id</code>, <code>worker_id</code></td>
    </tr>
  </tbody>
</table>

<h2 id="sink-metrics">Sink metrics</h2>
Metrics for data output to external systems.
<table>
  <thead>
    <tr>
      <th>Metric</th>
      <th>Description</th>
      <th>Labels</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>mz_dataflow_wallclock_lag_seconds</code></td>
      <td>A summary of the second-by-second lag of the dataflow frontier relative to wallclock time, aggregated over the last minute.</td>
      <td><code>collection_id</code>, <code>instance_id</code>, <code>quantile</code>, <code>replica_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sink_bytes_committed</code></td>
      <td>The number of bytes committed to the sink.</td>
      <td><code>sink_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sink_bytes_staged</code></td>
      <td>The number of bytes staged but possibly not committed to the sink.</td>
      <td><code>sink_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sink_iceberg_commit_conflicts</code></td>
      <td>Number of commit conflicts in the iceberg sink</td>
      <td><code>sink_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sink_iceberg_commit_duration_seconds_bucket</code></td>
      <td>Time spent committing batches to Iceberg in seconds</td>
      <td><code>le</code>, <code>sink_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sink_iceberg_commit_duration_seconds_count</code></td>
      <td>Time spent committing batches to Iceberg in seconds</td>
      <td><code>sink_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sink_iceberg_commit_duration_seconds_sum</code></td>
      <td>Time spent committing batches to Iceberg in seconds</td>
      <td><code>sink_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sink_iceberg_commit_failures</code></td>
      <td>Number of commit failures in the iceberg sink</td>
      <td><code>sink_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sink_iceberg_data_files_written</code></td>
      <td>Number of data files written by the iceberg sink</td>
      <td><code>sink_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sink_iceberg_delete_files_written</code></td>
      <td>Number of delete files written by the iceberg sink</td>
      <td><code>sink_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sink_iceberg_snapshots_committed</code></td>
      <td>Number of snapshots committed by the iceberg sink</td>
      <td><code>sink_id</code>, <code>worker_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sink_info</code></td>
      <td>Maps user sink IDs to the sink&#39;s type, envelope type, and cluster. Constant 1.</td>
      <td><code>cluster_id</code>, <code>envelope_type</code>, <code>sink_id</code>, <code>type</code></td>
    </tr>
    <tr>
      <td><code>mz_sink_rdkafka_connects</code></td>
      <td>The number of connection attempts, including successful and failed attempts, and name resolution failures across all brokers.</td>
      <td><code>sink_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sink_rdkafka_disconnects</code></td>
      <td>The number of disconnections, whether triggered by the broker, the network, the load balancer, or something else across all brokers.</td>
      <td><code>sink_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sink_rdkafka_outbuf_msg_cnt</code></td>
      <td>The number of messages awaiting transmission across all brokers.</td>
      <td><code>sink_id</code></td>
    </tr>
    <tr>
      <td><code>mz_sink_rdkafka_txerrs</code></td>
      <td>The total number of transmission errors across all brokers.</td>
      <td><code>sink_id</code></td>
    </tr>
  </tbody>
</table>

---

## Replica resource usage

Every process of a cluster replica reports its own resource usage through
[`mz_introspection.mz_cluster_replica_resource_usage`](/reference/system-catalog/mz_introspection/#mz_cluster_replica_resource_usage).
Each row is one measurement, taken from one source, reported as that source
gave it. Sources measure overlapping but distinct quantities, and the
differences between them are informative, so no row is a combination of two
others. Deciding which number is "the" memory usage of a replica, or how close
it is to its limit, is left to queries over the relation.

A metric whose name ends in `peak` is a high-water mark since the process
started, and the rest are instantaneous. Peaks the operating system maintains
itself are exact, and are unaffected by how often the replica reads them. Peaks
folded from samples are marked as such below and can miss a spike shorter than
the sampling interval, which makes them lower bounds. An observation the
replica could not read is absent rather than zero, so which metrics appear
depends on the platform and the kernel version.

## Sources

| Source        | Reads                                   | Measures                                                                                  |
|---------------|-----------------------------------------|-------------------------------------------------------------------------------------------|
| `cgroup`      | the process's cgroup v2 interface files | the whole container, and the accounting that limit enforcement and the OOM killer act on   |
| `proc_status` | `/proc/self/status`                     | this process only, with resident memory broken down by backing                             |
| `rusage`      | `getrusage(RUSAGE_SELF)`                | this process only                                                                          |
| `statvfs`     | the replica's scratch filesystem        | the filesystem as a whole, absent where disk is provided as swap                           |

## Metrics

| Source        | Metric            | Meaning                                                                                                                       |
|---------------|-------------------|--------------------------------------------------------------------------------------------------------------------------------|
| `cgroup`      | `memory_current`  | Memory charged to the cgroup: anonymous, page cache, kernel and socket memory.                                                  |
| `cgroup`      | `memory_peak`     | High-water mark of `memory_current`, maintained by the kernel.                                                                  |
| `cgroup`      | `memory_max`      | The cgroup's memory limit.                                                                                                     |
| `cgroup`      | `swap_current`    | Swap charged to the cgroup, including pages already read back whose swap slot is still allocated.                               |
| `cgroup`      | `swap_peak`       | High-water mark of `swap_current`, maintained by the kernel.                                                                    |
| `cgroup`      | `swap_max`        | The cgroup's swap limit.                                                                                                       |
| `cgroup`      | `anon`            | The part of `memory_current` backed by no file.                                                                                |
| `cgroup`      | `file`            | Page cache charged to the cgroup.                                                                                              |
| `cgroup`      | `shmem`           | Shared memory and tmpfs pages.                                                                                                 |
| `cgroup`      | `swapcached`      | Pages resident in memory whose swap slot is still allocated. Counted in both `anon` and `swap_current`.                          |
| `cgroup`      | `kernel`          | Kernel memory charged to the cgroup.                                                                                           |
| `cgroup`      | `slab`            | Kernel slab allocations, part of `kernel`.                                                                                     |
| `cgroup`      | `sock`            | Socket buffer memory.                                                                                                          |
| `cgroup`      | `events_max`      | Times an allocation hit `memory_max`. See the caveat below before using this as a limit-hit signal.                             |
| `cgroup`      | `events_oom_kill` | Processes in the cgroup killed by the OOM killer.                                                                              |
| `proc_status` | `vm_rss`          | Resident set size of this process, the sum of `rss_anon`, `rss_file` and `rss_shmem`.                                           |
| `proc_status` | `rss_anon`        | Resident memory backed by no file. The replica's own memory.                                                                    |
| `proc_status` | `rss_file`        | Resident file-backed memory, largely this binary's text. Shared between replicas and charged to whichever cgroup first faulted it in. |
| `proc_status` | `rss_shmem`       | Resident shared memory.                                                                                                        |
| `proc_status` | `vm_swap`         | This process's pages currently in swap. Excludes swap-cached pages, so it reads below `cgroup` `swap_current`.                   |
| `proc_status` | `vm_swap_peak`    | Maximum `vm_swap` over samples, so a lower bound on the true peak.                                                              |
| `proc_status` | `heap`            | `vm_rss` plus `vm_swap`, the quantity a replica is limited on.                                                                  |
| `proc_status` | `heap_peak`       | Maximum `heap` over samples, so a lower bound on the true peak.                                                                 |
| `rusage`      | `max_rss`         | Peak resident set size. Maintained by the kernel, but refreshed only at internal checkpoints, so it can read below a concurrent `vm_rss`. |
| `statvfs`     | `fs_used`         | Used bytes of the filesystem, which on a shared filesystem counts writes this replica never made.                               |
| `statvfs`     | `fs_used_peak`    | Maximum `fs_used` over samples, so a lower bound on the true peak.                                                              |

## Interpreting

Values from different sources are not interchangeable, and adding them together
generally produces a number that means nothing. In particular:

* **How close is this replica to its memory limit?** Compare `cgroup`
  `memory_current` against `memory_max`. **Did it ever reach it?** Compare
  `memory_peak` against `memory_max`. A `memory_peak` at the limit means the
  replica ran out of RAM and spilled to swap, even if the current reading is
  comfortable.
* **How close is it to its heap limit?** Compare `proc_status` `heap` against
  [`mz_internal.mz_cluster_replica_metrics`](/reference/system-catalog/mz_internal/#mz_cluster_replica_metrics)'s
  `heap_limit`. `heap_peak` bounds the high-water mark from below, and no source
  bounds it from above: the `cgroup` peaks describe a smaller quantity, and
  `max_rss` lags.
* **Do not use `events_max` as a limit-hit signal.** Where swap is configured it
  stays at zero even for a replica pinned at its ceiling, because reclaim
  succeeds by swapping instead of failing. `events_oom_kill` does report kills.
* **How much memory does this replica itself account for?** Use `proc_status`
  `rss_anon`. Do not use `vm_rss`: it includes `rss_file`, which is charged to
  another cgroup and so runs a roughly constant amount above the replica's own
  charge.
* **Do not add `memory_current` and `swap_current`.** A page read back from swap
  is counted in both, and `swapcached` reports how much is in that state.
* **Where disk is provided as swap**, disk usage appears as `swap_current` and
  there are no `statvfs` rows at all.
* **These readings live and die with the replica process.** A restart resets
  every peak. For history that survives restarts, see
  [`mz_internal.mz_cluster_replica_metrics_history`](/reference/system-catalog/mz_internal/#mz_cluster_replica_metrics_history).

## Example

Introspection relations are replica-local: a query reads the replica that
serves it, so pin both the cluster and the replica. This reports how close each
process came to a memory-limiter kill, comparing the quantity the limiter
enforces against the limit it enforces:

```mzsql
SET cluster = <cluster_name>;
SET cluster_replica = <replica_name>;

SELECT
    u.process_id,
    round((max(u.value) FILTER (WHERE u.metric = 'heap'))::numeric      / 1073741824, 2) AS heap_gib,
    round((max(u.value) FILTER (WHERE u.metric = 'heap_peak'))::numeric / 1073741824, 2) AS heap_peak_gib,
    round(m.heap_limit::numeric / 1073741824, 2)                                         AS limit_gib,
    round(100 * (max(u.value) FILTER (WHERE u.metric = 'heap_peak'))::numeric / m.heap_limit, 1) AS peak_pct
FROM mz_introspection.mz_cluster_replica_resource_usage u
JOIN mz_cluster_replicas r
     ON r.name = current_setting('cluster_replica')
    AND r.cluster_id = (SELECT id FROM mz_clusters WHERE name = current_setting('cluster'))
JOIN mz_internal.mz_cluster_replica_metrics m
     ON m.replica_id = r.id AND m.process_id = u.process_id
WHERE u.source = 'proc_status'
GROUP BY u.process_id, m.heap_limit
ORDER BY u.process_id;
```

`peak_pct` is a lower bound, because `heap_peak` is: a spike shorter than the
sampling interval can slip through it. No source provides a matching upper
bound. The query stays within `proc_status` deliberately. The `cgroup` metrics
measure a different quantity, and `memory_current` plus `swap_current`
double-counts every swap-cached page.

---

## Self-Managed

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

- [How logs and metrics are stored](/manage/monitor/self-managed/storage/), including
  the backends you can forward them to.

- [Grafana](/manage/monitor/self-managed/grafana/), the dashboards and query
  interface that ship with the stack.

To configure the stack outside the Materialize Terraform modules, or to see the
full set of module variables, see the [`materialize-monitoring` Terraform
installation guide
⧉](https://materializeinc.github.io/materialize-monitoring/getting-started/terraform/).

## Deliver data to your observability platform

To send metrics and logs to a platform you already run, a guide is available for
each destination:

- [Datadog](/manage/monitor/self-managed/datadog/)

- [Honeycomb](/manage/monitor/self-managed/honeycomb/)

- [OpenTelemetry](/manage/monitor/self-managed/opentelemetry/), for any other OTLP
  endpoint, including your own collector.

- [Google Cloud Monitoring](/manage/monitor/self-managed/google-cloud-monitoring/)

- [Prometheus remote
  write](/manage/monitor/self-managed/prometheus-remote-write/), for Mimir,
  Amazon Managed Prometheus, Grafana Cloud, or a Thanos you run elsewhere.

## Alerting

After setting up a monitoring tool, you can configure alert rules. Alert rules
send a notification when a metric surpasses a threshold. This will help you
prevent operational incidents. For alert rules guidelines, see
[Alerting](/manage/monitor/self-managed/alerting/).

