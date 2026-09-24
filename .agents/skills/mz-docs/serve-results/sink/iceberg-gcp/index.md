# GCP BigLake
How to export results from Materialize to Apache Iceberg tables on Google Cloud BigLake.

> **Warning:** [Iceberg tables managed by the Lakehouse runtime catalog (BigLake API)](https://docs.cloud.google.com/lakehouse/docs/key-concepts#metastore-iceberg)
> do not receive automated maintenance like expiring old snapshots and compacting manifests and data files.
> Without table maintenance, table metadata grows over time and will eventually exceed BigLake's allowed limit.
> This will prevent Materialize Iceberg sinks from committing new data.
> [Iceberg tables managed by BigQuery](https://docs.cloud.google.com/lakehouse/docs/key-concepts#iceberg-managed-tables)
> do receive automated maintenance, but only BigQuery can write to them.

This guide walks you through the steps required to set up Iceberg sinks in
Materialize Cloud.

## Prerequisites

- Google Cloud project with the [BigLake API enabled](https://docs.cloud.google.com/lakehouse/docs/lakehouse-iceberg-rest-catalog#before_you_begin).
- Google Cloud [Storage bucket](https://console.cloud.google.com/storage/browser) to serve as the Iceberg warehouse.
- [Lakehouse runtime catalog](https://docs.cloud.google.com/lakehouse/docs/lakehouse-iceberg-rest-catalog#create_a_catalog) backed by your warehouse bucket.
  For **Authentication method**, you can select either _End-user credentials_ or _Credential vending mode_.
  Materialize authenticates separately with a [GCP service account key](https://docs.cloud.google.com/iam/docs/keys-create-delete#iam-service-account-keys-create-gcloud)
  (provided in the next step), so both modes work.
- [Namespace in the catalog](https://docs.cloud.google.com/lakehouse/docs/lakehouse-iceberg-rest-catalog#create_a_namespace_or_schema).

## Create the Iceberg catalog connection in Materialize

### Step 1. Set up permissions in GCP

Materialize uses a Google Cloud [service account](https://docs.cloud.google.com/iam/docs/service-account-overview) to
authenticate to BigLake.

1. Create the [service account](https://console.cloud.google.com/iam-admin/serviceaccounts).
2. Grant the service account these roles on your **project**:
    - `biglake.editor` (BigLake Editor)
    - `serviceusage.serviceUsageConsumer` (Service Usage Consumer)
3. Grant the service account this role on your **Iceberg warehouse bucket**:
    - `storage.objectUser` (Storage Object User)
4. [Create a service account key in JSON format.](https://docs.cloud.google.com/iam/docs/keys-create-delete#iam-service-account-keys-create-gcloud)

5. Base64-encode the entire JSON key (e.g. `base64 < sa_key.json`). In the [next
   step](#step-2-create-a-gcp-connection-and-iceberg-catalog-connection-in-materialize),
   you will decode the resulting string in the `CREATE SECRET` statement.
   Encoding the key first and decoding it in the `CREATE SECRET` statement
   avoids escaping quotes and newlines in the SQL string literal.

### Step 2. Create a GCP connection and Iceberg catalog connection in Materialize

The following example creates a [GCP connection](/sql/create-connection/#gcp) and an [Iceberg catalog connection](/sql/create-connection/#iceberg-catalog) for Google Cloud BigLake:
```mzsql
-- Using the base64-encoded service account key (e.g. base64 < sa_key.json)
CREATE SECRET gcp_service_account_key
  AS decode('<base64-encoded service account key JSON>', 'base64');

-- Create a GCP connection that uses the service-account key.
CREATE CONNECTION gcp_connection TO GCP (
    SERVICE ACCOUNT KEY = SECRET gcp_service_account_key
);

-- Create the Iceberg catalog connection pointing to BigLake.
CREATE CONNECTION iceberg_catalog_connection TO ICEBERG CATALOG (
    CATALOG TYPE = 'rest',
    URL = 'https://biglake.googleapis.com/iceberg/v1/restcatalog',
    WAREHOUSE = 'gs://<bucket>',
    GCP CONNECTION = gcp_connection
);

```

## Create the Iceberg sink in Materialize

In Materialize, you can sink from a materialized view, table, or source. Use
[`CREATE SINK`](/sql/create-sink/iceberg) to create an Iceberg sink, replacing:

- `<sink_name>` with a name for your sink.
- `<sink_cluster>` with the name of your sink cluster.
- `<my_materialize_object>` with the name of your materialized view, table, or source.
- `<my_iceberg_namespace>` with your catalog namespace.
- `<my_iceberg_table>` with the name of your Iceberg table. If the Iceberg table
  does not exist, Materialize creates the table. For details, see [`CREATE SINK`
  reference page](/sql/create-sink/iceberg/#iceberg-table-creation).
- `<commit_interval>` with your commit interval (e.g., `1m`). The commit
  interval specifies how frequently Materialize commits snapshots to Iceberg.
  The minimum commit interval is `1s`. See [Commit interval
  tradeoffs](#commit-interval-tradeoffs) below.

For the full list of syntax options, see the [`CREATE SINK` reference](/sql/create-sink/iceberg).

### Upsert mode

In upsert mode, replace `<key>` with the column(s) that uniquely identify rows.
```mzsql
CREATE SINK <sink_name>
  IN CLUSTER <sink_cluster>
  FROM <my_materialize_object>
  INTO ICEBERG CATALOG CONNECTION iceberg_catalog_connection (
    NAMESPACE = '<my_iceberg_namespace>',
    TABLE = '<my_iceberg_table>'
  )
  KEY (<key>)
  MODE UPSERT
  WITH (COMMIT INTERVAL = '<commit_interval>');

```

### Append mode

In append mode, no `KEY` clause is used. The Iceberg table includes all source
columns plus `_mz_diff` (`int`) and `_mz_timestamp` (`long`).
```mzsql
CREATE SINK <sink_name>
  IN CLUSTER <sink_cluster>
  FROM <my_materialize_object>
  INTO ICEBERG CATALOG CONNECTION iceberg_catalog_connection (
    NAMESPACE = '<my_iceberg_namespace>',
    TABLE = '<my_iceberg_table>'
  )
  MODE APPEND
  WITH (COMMIT INTERVAL = '<commit_interval>');

```

## Considerations

### Commit interval tradeoffs {#commit-interval-tradeoffs}

The `COMMIT INTERVAL` setting controls how frequently Materialize commits
snapshots to your Iceberg table, making the data available to downstream query
engines. This setting involves tradeoffs:

| Shorter intervals (e.g., < `1m`) | Longer intervals (e.g., `5m`) |
|---------------------------------|-------------------------------|
| Lower latency - data visible sooner in downstream systems | Higher latency - data takes longer to appear |
| More small files - can degrade query performance over time | Fewer, larger files - better query performance |
| More frequent snapshot commits - higher catalog overhead | Less catalog overhead |
| Lower throughput efficiency | Higher throughput efficiency |

**Recommendations:**
- For production, use intervals of `1m` or longer
- For batch analytics, use longer intervals (`5m` to `15m`)

Starting in v26.34, you can change the commit interval of an existing sink with
[`ALTER SINK`](/sql/alter-sink/).

> **Note:** Outside of development environments, commit intervals should be at least `1m`.
> Short commit intervals increase catalog overhead and produce many small files.
> Small files will result in degraded query performance. It also increases load on
> the Iceberg metadata, which can result in a degraded catalog, and non-responsive
> queries.

### Exactly-once delivery

Iceberg sinks provide **exactly-once delivery**. After a restart,
Materialize resumes from the last committed snapshot without duplicating
data.

Materialize stores progress information in Iceberg snapshot metadata
properties (`mz-frontier` and `mz-sink-version`).

### Type mapping

Materialize converts SQL types to Iceberg/Parquet types:

| SQL type | Iceberg type |
|----------|--------------|
| `boolean` | `boolean` |
| `smallint`, `integer` | `int` |
| `uint2` | `int` |
| `bigint` | `long` |
| `uint4` | `long` |
| `uint8` | `decimal(20, 0)` |
| `real` | `float` |
| `double precision` | `double` |
| `numeric` | `decimal(38, scale)` |
| `date` | `date` |
| `time` | `time` (microsecond) |
| `timestamp` | `timestamp` (microsecond) |
| `timestamptz` | `timestamptz` (microsecond) |
| `text`, `varchar` | `string` |
| `bytea` | `binary` |
| `uuid` | `fixed(16)` |
| `jsonb` | `string` |
| `interval` | `string` |
| `int4range`, `int8range`, `numrange`, `daterange`, `tsrange`, `tstzrange` | `struct` (fields: `lower`, `upper`, `lower_inclusive`, `upper_inclusive`, `empty`) |
| `record` | `struct` |
| `list` | `list` |
| `map` | `map` |

### Limitations

- [Iceberg tables managed by the Lakehouse runtime catalog (BigLake API)](https://docs.cloud.google.com/lakehouse/docs/key-concepts#metastore-iceberg)
do not receive automated maintenance like expiring old snapshots and compacting manifests and data files.

Without table maintenance, table metadata grows over time and will eventually exceed BigLake's allowed limit.
This will prevent Materialize Iceberg sinks from committing new data.

- [Iceberg tables managed by BigQuery](https://docs.cloud.google.com/lakehouse/docs/key-concepts#iceberg-managed-tables)
do receive automated maintenance, but only BigQuery can write to them.

- You cannot create an Iceberg sink into an existing Iceberg table. Materialize creates and manages the target Iceberg table itself, so the table named by the sink must not already exist.

- Partitioned tables are not supported.

- Schema evolution of an Iceberg table is not supported. If the `SINK FROM` object's schema changes, you must drop and recreate the sink.

## Troubleshooting

### Sink creation fails with "input compacted past resume upper"

This error occurs when the source data has been compacted beyond the point where
the sink last committed. This can happen after a Materialize backup/restore
operation. You may need to drop and recreate the sink, which will re-snapshot
the entire source relation.

### Commit conflicts

If another process modifies the Iceberg table while Materialize is committing,
you may see commit conflict errors. Materialize will automatically retry, but
if conflicts persist, ensure no other writers are modifying the same table.

## Related pages

- [`CREATE SINK`](/sql/create-sink/iceberg)
- [`CREATE CONNECTION`](/sql/create-connection)
- [Apache Iceberg documentation](https://iceberg.apache.org/docs/latest/)
