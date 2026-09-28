# Essential metrics
The Prometheus metrics Materialize recommends building dashboards and alerts on.
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

