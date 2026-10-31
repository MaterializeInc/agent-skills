# S3-compatible storage and Iceberg REST catalogs
How to export results from Materialize to Apache Iceberg tables in an Iceberg REST catalog, such as Apache Polaris, backed by S3-compatible object storage, such as MinIO.
> **Public Preview:** This feature is in public preview.

This guide walks you through setting up an Iceberg sink to a catalog that
implements the [Iceberg REST catalog
specification](https://iceberg.apache.org/rest-catalog-spec/), with tables
stored in Amazon S3 or S3-compatible object storage. The examples use [Apache
Polaris](https://polaris.apache.org/) as the catalog and MinIO as the object
store.

Materialize does not take a storage endpoint or storage credentials of its own.
The catalog supplies both: with [credential
vending](/sql/create-connection/#iceberg-catalog-access-delegation), it hands
Materialize temporary credentials scoped to the table it writes.

> **Tip:** Some catalogs have their own guide: [AWS S3 Tables](/export-data/iceberg-aws/),
> [GCP BigLake](/export-data/iceberg-gcp/), and [Databricks Unity
> Catalog](/export-data/iceberg-databricks/).

## Prerequisites

- A Polaris deployment, and an S3-compatible bucket for its warehouse. The
  examples use a bucket named `warehouse`.

- Polaris configured with storage credentials that can call the object store's
  STS `AssumeRole` API, for example through the `AWS_ACCESS_KEY_ID` and
  `AWS_SECRET_ACCESS_KEY` environment variables.

- Polaris's API and the object store reachable from Materialize. Iceberg
  catalog connections cannot tunnel through [AWS
  PrivateLink](/sql/create-connection/#aws-privatelink) or an [SSH
  bastion host](/sql/create-connection/#ssh-tunnel). If either endpoint sits
  behind a firewall, allow traffic from the [static egress IP
  addresses](/ingest-data/network-security/static-ips/) of your Materialize
  region.

- An access token for a Polaris principal that can manage catalogs and
  principals, such as the `root` principal created at bootstrap:

  ```bash
  POLARIS=https://<polaris_host>
  read -rs ROOT_CLIENT_SECRET

  TOKEN=$(curl -sS "$POLARIS/api/catalog/v1/oauth/tokens" \
    -d grant_type=client_credentials \
    -d client_id=<root_client_id> \
    --data-urlencode "client_secret=$ROOT_CLIENT_SECRET" \
    -d scope=PRINCIPAL_ROLE:ALL | jq -r .access_token)
  ```

## Set up Polaris

### Step 1. Create a catalog backed by your bucket

Create a catalog whose `storageConfigInfo` points at your object store. Polaris
vends `endpoint` to Materialize, so it must be reachable from Materialize. If
Polaris reaches the object store at a different address, add that address as
`endpointInternal`. S3-compatible stores such as MinIO generally need
`pathStyleAccess`.

```bash
curl -sS --fail-with-body "$POLARIS/api/management/v1/catalogs" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{
    "catalog": {
      "name": "materialize_catalog",
      "type": "INTERNAL",
      "properties": {
        "default-base-location": "s3://warehouse/materialize_catalog/"
      },
      "storageConfigInfo": {
        "storageType": "S3",
        "allowedLocations": ["s3://warehouse/materialize_catalog/"],
        "endpoint": "https://<minio_host>:9000",
        "pathStyleAccess": true,
        "region": "us-east-1"
      }
    }
  }'
```

Leave `s3.access-key-id` and `s3.secret-access-key` out of the catalog's
`properties`. Polaris returns catalog properties to every client, so long-lived
credentials placed there are shared with anyone who can load a table.

### Step 2. Create a principal for Materialize

Create a principal, and save the `clientId` and `clientSecret` that Polaris
returns. Polaris does not show the secret again.

```bash
curl -sS --fail-with-body "$POLARIS/api/management/v1/principals" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"principal": {"name": "materialize"}}' | jq .credentials
```

### Step 3. Grant the principal access to the catalog

Polaris grants privileges to catalog roles, which are assigned to principal
roles, which are assigned to principals. `CATALOG_MANAGE_CONTENT` lets the
principal create and commit to tables, and includes the `TABLE_READ_DATA` and
`TABLE_WRITE_DATA` privileges that authorize credential vending.

```bash
H=(-H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json")
API="$POLARIS/api/management/v1"

# Create a principal role and assign it to the principal.
curl -sS --fail-with-body "${H[@]}" "$API/principal-roles" \
  -d '{"principalRole": {"name": "materialize_role"}}'
curl -sS --fail-with-body "${H[@]}" -X PUT "$API/principals/materialize/principal-roles" \
  -d '{"principalRole": {"name": "materialize_role"}}'

# Create a catalog role, grant it privileges, and assign it to the principal role.
curl -sS --fail-with-body "${H[@]}" "$API/catalogs/materialize_catalog/catalog-roles" \
  -d '{"catalogRole": {"name": "materialize_writer"}}'
curl -sS --fail-with-body "${H[@]}" -X PUT \
  "$API/catalogs/materialize_catalog/catalog-roles/materialize_writer/grants" \
  -d '{"grant": {"type": "catalog", "privilege": "CATALOG_MANAGE_CONTENT"}}'
curl -sS --fail-with-body "${H[@]}" -X PUT \
  "$API/principal-roles/materialize_role/catalog-roles/materialize_catalog" \
  -d '{"catalogRole": {"name": "materialize_writer"}}'
```

### Step 4. Create a namespace

Materialize creates the table a sink writes to, but not its namespace.

```bash
curl -sS --fail-with-body "$POLARIS/api/catalog/v1/materialize_catalog/namespaces" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"namespace": ["materialize"]}'
```

## Create the Iceberg catalog connection in Materialize

### Step 1. Store the principal's credentials

Store the `clientId` and `clientSecret` from [Step 2](#step-2-create-a-principal-for-materialize)
as a single value, separated by a colon:

```mzsql
CREATE SECRET polaris_credential AS '<client_id>:<client_secret>';
```

### Step 2. Create the connection

```mzsql
CREATE CONNECTION iceberg_catalog_connection TO ICEBERG CATALOG (
    CATALOG TYPE = 'rest',
    URL = 'https://<polaris_host>/api/catalog',
    WAREHOUSE = 'materialize_catalog',
    CREDENTIAL = SECRET polaris_credential,
    SCOPE = 'PRINCIPAL_ROLE:ALL',
    ACCESS DELEGATION = 'vended-credentials'
);
```

| Option | Value for Polaris |
| --- | --- |
| `URL` | Polaris's API base URL followed by `/api/catalog`. |
| `WAREHOUSE` | The catalog name. |
| `SCOPE` | `PRINCIPAL_ROLE:ALL`, or `PRINCIPAL_ROLE:<name>` to activate a single principal role. Required: Polaris rejects the token request without it. |
| `ACCESS DELEGATION` | `'vended-credentials'`, so that Materialize writes with the credentials Polaris vends. |
| `STORAGE PROVIDER` | Omit it for S3 and S3-compatible storage such as MinIO, the default. Set it to `'gcs'` or `'adls'` if the catalog stores its tables in Google Cloud Storage or Azure Data Lake Storage Gen2. |

`CREATE CONNECTION` validates the connection by listing the catalog's
namespaces, so a wrong URL, scope, or credential fails here. For all options,
see [`CREATE CONNECTION`](/sql/create-connection/#iceberg-catalog).

## Other REST catalogs

The same connection works with other Iceberg REST catalogs, with these
differences:

- Without `ACCESS DELEGATION`, Materialize uses the storage properties the
  catalog returns: `s3.endpoint`, `s3.region`, `s3.path-style-access`,
  `s3.access-key-id`, and `s3.secret-access-key`. Materialize adds nothing to
  them, so they must describe the store completely.
- Materialize exchanges `CREDENTIAL` at `<URL>/v1/oauth/tokens` and ignores the
  token endpoint the catalog advertises. Set `OAUTH2 SERVER URL` if the catalog
  serves it elsewhere.
- Materialize refreshes vended credentials through the catalog's
  `loadCredentials` endpoint. Sinks on a catalog that vends credentials but does
  not implement `loadCredentials` fail once the first credential expires.
- For storage other than S3, set `STORAGE PROVIDER`.

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

### Verify the sink

Once the first commit interval elapses, check that the sink is running:

```mzsql
SELECT name, status, error
FROM mz_internal.mz_sink_statuses
WHERE name = '<sink_name>';
```

```nofmt
    name     | status  | error
-------------+---------+-------
 <sink_name> | running |
```

The table's data and metadata files appear in your bucket under
`s3://warehouse/materialize_catalog/<namespace>/<table>/`.

## Considerations

### Commit interval tradeoffs

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

### Credential refresh

Materialize refreshes both its OAuth2 token and the vended storage credentials
while the sink runs. Rotating the principal's secret in Polaris requires
updating the Materialize secret:

```mzsql
ALTER SECRET polaris_credential AS '<client_id>:<new_client_secret>';
```

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

- Iceberg catalog connections cannot be modified with [`ALTER
  CONNECTION`](/sql/alter-connection). To change any option, drop the connection
  and the sinks that depend on it, then recreate them.

- You cannot create an Iceberg sink into an existing Iceberg table. Materialize creates and manages the target Iceberg table itself, so the table named by the sink must not already exist.

- Partitioned tables are not supported.

- Schema evolution of an Iceberg table is not supported. If the `SINK FROM` object's schema changes, you must drop and recreate the sink.

## Troubleshooting

| Error | Cause |
| --- | --- |
| `CREATE CONNECTION` fails with `invalid_scope` | `SCOPE` is missing. |
| `CREATE CONNECTION` fails with `401 Unauthorized` | The credential is wrong, or `SCOPE` names a principal role that is not assigned to the principal. |
| The sink stalls with `403 Forbidden` and `is not authorized for op CREATE_TABLE_DIRECT_WITH_WRITE_DELEGATION` | The principal's catalog role lacks either `CATALOG_MANAGE_CONTENT` or both `TABLE_READ_DATA` and `TABLE_WRITE_DATA`, so Polaris refuses to vend credentials. |
| The sink stalls with `500 Internal Server Error` from Polaris | Polaris cannot reach the object store, or its storage credentials cannot call `AssumeRole`. Check the Polaris logs. |
| The sink stalls with `Failed to close batch writer` and `signing http request` | Materialize has no storage credentials. Set `ACCESS DELEGATION = 'vended-credentials'` on the connection. |
| The sink stalls with `Failed to close batch writer` for another reason | The `endpoint` in the catalog's `storageConfigInfo` is not reachable from Materialize. |
| A namespace-not-found error when the sink starts | The namespace named by `NAMESPACE` does not exist, or the principal cannot see it. |

### Sink creation fails with "input compacted past resume upper"

This error occurs when the source data has been compacted beyond the point where
the sink last committed. This can happen after a Materialize backup/restore
operation. You may need to drop and recreate the sink, which will re-snapshot
the entire source relation.

### Commit conflicts

If another process modifies the Iceberg table while Materialize is committing,
you may see commit conflict errors. Materialize will automatically retry, but
if conflicts persist, ensure no other writers are modifying the same table.

### Sink falls behind and does not catch up

An Iceberg sink can fall behind its input when each commit to the catalog takes
longer than the sink's `COMMIT INTERVAL`. In steady state, the sink commits one
snapshot per interval of data. If a commit takes longer than the interval, the
sink falls further behind with every commit, and its lag keeps growing even
though the input relation is up to date. How long a commit takes depends on
your catalog and object store, and can be several seconds.

To check whether the sink is behind its input, compare their lag:

```mzsql
SELECT o.name, l.lag
FROM mz_internal.mz_wallclock_global_lag AS l
JOIN mz_catalog.mz_objects AS o ON o.id = l.object_id
WHERE o.name IN ('<sink_name>', '<input_relation_name>');
```

If the input's lag is low but the sink's lag is high and growing, recover the
sink in one of the following ways:

- Increase the commit interval to a value that comfortably exceeds the time a
   commit takes. Outside of development environments, use at least `1m`. See
   [Commit interval tradeoffs](/sql/create-sink/iceberg/#commit-interval-tradeoffs).

   ```mzsql
   ALTER SINK <sink_name> SET (COMMIT INTERVAL = '1m');
   ```

   Changing the commit interval restarts the sink.

- If the commit interval is already appropriate, restart the sink by
   restarting the replicas of the cluster that hosts it. Restarting the
   replicas also restarts every other object on that cluster, which must then
   rehydrate.

   For a managed cluster:

   ```mzsql
   ALTER CLUSTER <cluster_name> SET (REPLICATION FACTOR = 0);
   ALTER CLUSTER <cluster_name> SET (REPLICATION FACTOR = <original replication factor>);
   ```

   For an unmanaged cluster, drop and recreate each replica:

   ```mzsql
   DROP CLUSTER REPLICA <cluster_name>.<replica_name>;
   CREATE CLUSTER REPLICA <cluster_name>.<replica_name> (SIZE = '<original size>');
   ```

When the sink restarts, it writes all data between its last committed point and
the current state of its input in a single catch-up commit, then resumes
committing at the configured interval. Restarting the sink without increasing a
commit interval that is too short only recovers temporarily, and the sink falls
behind again.

## Related pages

- [`CREATE SINK`](/sql/create-sink/iceberg)
- [`CREATE CONNECTION`](/sql/create-connection/#iceberg-catalog)
- [Storage access delegation](/sql/create-connection/#iceberg-catalog-access-delegation)
- [Apache Polaris documentation](https://polaris.apache.org/)
