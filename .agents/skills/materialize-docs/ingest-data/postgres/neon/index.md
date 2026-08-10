# Ingest data from Neon
How to stream data from Neon to Materialize
> **Tip:** For help getting started with your own data, you can schedule a [free guided
> trial](https://materialize.com/demo/?utm_campaign=General&utm_source=documentation).

[Neon](https://neon.tech) is a fully managed serverless PostgreSQL provider. It
separates compute and storage to offer features like **autoscaling**,
**branching** and **bottomless storage**.

This page shows you how to stream data from a Neon database to Materialize using
the [PostgreSQL source](/sql/create-source/postgres/).

## Before you begin

- Make sure you have [a Neon account](https://neon.tech).

- Make sure you have access to your Neon instance via [`psql`](https://www.postgresql.org/docs/current/app-psql.html)
  or the SQL editor in the Neon Console.

## A. Configure Neon

The steps in this section are specific to Neon. You can run them by connecting
to your Neon database using a `psql` client or the SQL editor in the Neon
Console.

### 1. Enable logical replication

> **Warning:** Enabling logical replication applies **globally** to all databases in your Neon
> project, and **cannot be reverted**. It also **restarts all computes**, which
> means that any active connections are dropped and have to reconnect.

Materialize uses PostgreSQL's [logical replication](https://www.postgresql.org/docs/current/logical-replication.html)
protocol to track changes in your database and propagate them to Materialize.

As a first step, you need to make sure logical replication is enabled in Neon.

1. Select your project in the Neon Console.

2. On the Neon **Dashboard**, select **Settings**.

3. Select **Logical Replication**.

4. Click **Enable** to enable logical replication.

You can verify that logical replication is enabled by running:

```sql
SHOW wal_level;
```

The result should be:

```
 wal_level
-----------
 logical
```

### 2. Create a publication and a replication user

Once logical replication is enabled, the next step is to create a publication
with the tables that you want to replicate to Materialize. You'll also need a
user for Materialize with sufficient privileges to manage replication.

1. For each table that you want to replicate to Materialize, set the
   [replica identity](https://www.postgresql.org/docs/current/sql-altertable.html#SQL-ALTERTABLE-REPLICA-IDENTITY)
   to `FULL`:

   ```postgres
   ALTER TABLE <table1> REPLICA IDENTITY FULL;
   ```

   ```postgres
   ALTER TABLE <table2> REPLICA IDENTITY FULL;
   ```

   `REPLICA IDENTITY FULL` ensures that the replication stream includes the
    previous data of changed rows, in the case of `UPDATE` and `DELETE`
    operations. This setting enables Materialize to ingest Neon data with
    minimal in-memory state. However, you should expect increased disk usage in
    your Neon database.

2. Create a [publication](https://www.postgresql.org/docs/current/logical-replication-publication.html)
   with the tables you want to replicate:

   _For specific tables:_

    ```postgres
    CREATE PUBLICATION mz_source FOR TABLE <table1>, <table2>;
    ```

    _For all tables in the database:_

    ```postgres
    CREATE PUBLICATION mz_source FOR ALL TABLES;
    ```

    The `mz_source` publication will contain the set of change events generated
    from the specified tables, and will later be used to ingest the replication
    stream.

    Be sure to include only the tables you need. If the publication includes
    additional tables, Materialize will waste resources on ingesting and then
    immediately discarding the data.

3. Create a dedicated user for Materialize, if you don't already have one. The default user created with your Neon project and users created using the
Neon CLI, Console or API are granted membership in the [`neon_superuser`](https://neon.tech/docs/manage/roles#the-neonsuperuser-role)
role, which has the required `REPLICATION` privilege.

   While you can use the default user for replication, we recommend creating a
   dedicated user for security reasons.

**Neon CLI:**

Use the [`roles create` CLI command](https://neon.tech/docs/reference/cli-roles)
to create a new role.

```bash
neon roles create --name materialize
```

**Neon Console:**

1. Navigate to the [Neon Console](https://console.neon.tech).
2. Select a project.
3. Select **Branches**.
4. Select the branch where you want to create the role.
5. Select the **Roles & Databases** tab.
6. Click **Add Role**.
7. In the role creation dialog, specify the role name as "materialize".
8. Click **Create**. The role is created, and you are provided with the
password for the role.

**API:**

Use the [`roles` endpoint](https://api-docs.neon.tech/reference/createprojectbranchrole)
to create a new role.

```bash
curl 'https://console.neon.tech/api/v2/projects/<project_id>/branches/<branch_id>/roles' \
-H 'Accept: application/json' \
-H "Authorization: Bearer $NEON_API_KEY" \
-H 'Content-Type: application/json' \
-d '{
"role": {
    "name": "materialize"
}
}' | jq
```

4. Grant the user the required permissions on the schema(s) you want to
   replicate:

   ```postgres
   GRANT USAGE ON SCHEMA public TO materialize;

   GRANT SELECT ON ALL TABLES IN SCHEMA public TO materialize;

   ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO materialize;
   ```

   Granting `SELECT ON ALL TABLES IN SCHEMA` instead of on specific tables
   avoids having to add privileges later if you add tables to your
   publication.

## B. (Optional) Configure network security

> **Note:** If you are prototyping and your Neon instance is publicly accessible, **you can
> skip this step**. For production scenarios, we recommend using [**IP Allow**](https://neon.tech/docs/introduction/ip-allow)
> to limit the IP addresses that can connect to your Neon instance.

**Cloud:**

If you use Neon's [**IP Allow**](https://neon.tech/docs/introduction/ip-allow)
feature to limit the IP addresses that can connect to your Neon instance, you
will need to allow inbound traffic from Materialize IP addresses.

1. In the [Materialize console's SQL Shell](/console/),
   or your preferred SQL client connected to
   Materialize, run the following query to find the static egress IP addresses,
   for the Materialize region you are running in:

    ```mzsql
    SELECT * FROM mz_egress_ips;
    ```

2. In your Neon project, add the IPs to your **IP Allow** list:

   1. Select your project in the Neon Console.
   2. On the Neon **Dashboard**, select **Settings**.
   3. Select **IP Allow**.
   4. Add each Materialize IP address to the list.

**Self-Managed:**

> **Note:** If you are prototyping and your Neon instance is publicly accessible, **you can
> skip this step**. For production scenarios, we recommend using [**IP Allow**](https://neon.tech/docs/introduction/ip-allow)
> to limit the IP addresses that can connect to your Neon instance.

If you use Neon's [**IP Allow**](https://neon.tech/docs/introduction/ip-allow)
feature to limit the IP addresses that can connect to your Neon instance, you
will need to allow inbound traffic from Materialize IP addresses.

2. In your Neon project, add the IPs to your **IP Allow** list:

   1. Select your project in the Neon Console.
   2. On the Neon **Dashboard**, select **Settings**.
   3. Select **IP Allow**.
   4. Add Materialize IP addresses to the list.

## C. Ingest data in Materialize

The steps in this section are specific to Materialize. You can run them in the
[Materialize console's SQL Shell](/console/) or your
preferred SQL client connected to Materialize.

### 1. (Optional) Create a cluster

> **Note:** If you are prototyping and already have a cluster to host your PostgreSQL
> source (e.g. `quickstart`), **you can skip this step**. For production
> scenarios, we recommend separating your workloads into multiple clusters for
> [resource isolation](/sql/create-cluster/#resource-isolation).

In Materialize, a [cluster](/concepts/clusters/) is an isolated environment,
similar to a virtual warehouse in Snowflake. When you create a cluster, you
choose the size of its compute resource allocation based on the work you need
the cluster to do, whether ingesting data from a source, computing
always-up-to-date query results, serving results to external clients, or a
combination.

In this step, you'll create a dedicated cluster for ingesting source data from
your PostgreSQL database.

1. In the [SQL Shell](/console/), or your preferred SQL
   client connected to Materialize, use the [`CREATE CLUSTER`](/sql/create-cluster/)
   command to create the new cluster:

    ```mzsql
    CREATE CLUSTER ingest_postgres (SIZE = '50cc');

    SET CLUSTER = ingest_postgres;
    ```

    A cluster of [size](/sql/create-cluster/#available-sizes) `50cc` should be enough to
    accommodate multiple PostgreSQL sources, depending on the source
    characteristics (e.g., sources with [`ENVELOPE UPSERT`](/sql/create-source/kafka/#upsert-envelope)
    or [`ENVELOPE DEBEZIUM`](/sql/create-source/kafka/#debezium-envelope) will be more
    memory-intensive) and the upstream traffic patterns. You can readjust the
    size of the cluster at any time using the [`ALTER CLUSTER`](/sql/alter-cluster) command:

    ```mzsql
    ALTER CLUSTER <cluster_name> SET ( SIZE = <new_size> );
    ```

### 2. Create a connection

Once you have configured your network, create a connection in Materialize per
your networking configuration.

1. Run the [`CREATE SECRET`](/sql/create-secret/) command to securely store the
   password for the `materialize` PostgreSQL user you created [earlier](#2-create-a-publication-and-a-replication-user):

    ```mzsql
    CREATE SECRET pgpass AS '<PASSWORD>';
    ```

    You can access the password for your Neon user from
    the **Connection Details** widget on the Neon **Dashboard**.

2. Use the [`CREATE CONNECTION`](/sql/create-connection/) command to create a
   connection object with access and authentication details for Materialize to
   use:

    ```mzsql
    CREATE CONNECTION pg_connection TO POSTGRES (
      HOST '<host>',
      PORT 5432,
      USER '<user_name>',
      PASSWORD SECRET pgpass,
      SSL MODE 'require',
      DATABASE '<database>'
    );
    ```

    You can find the connection details for your replication user in
    the **Connection Details** widget on the Neon **Dashboard**. A Neon
    connection string looks like this:

    ```bash
    postgresql://materialize:AbC123dEf@ep-cool-darkness-123456.us-east-2.aws.neon.tech/dbname?sslmode=require
    ```

    - Replace `<host>` with your Neon hostname
      (e.g., `ep-cool-darkness-123456.us-east-2.aws.neon.tech`).
    - Replace `<role_name>` with the dedicated replication user
      (e.g., `materialize`).
    - Replace `<database>` with the name of the database containing the tables
      you want to replicate to Materialize (e.g., `dbname`).

### 3. Start ingesting data

{{< tip >}}
When snapshotting, Materialize uses PostgreSQL statistics to estimate the amount of data and
number of rows to read. Before creating the source in Materialize, check that the PostgreSQL
statistics are up to date by running PostgreSQL `ANALYZE`.  See
[Snapshotting considerations](#snapshotting) for more information.
{{< /tip >}}

{{< tabs level=4 >}}
{{< tab "Legacy Syntax" >}}

{{% include-example file="examples/ingest_data/postgres/create_source_cloud" example="create-source-legacy" %}}
{{% include-example file="examples/ingest_data/postgres/create_source_cloud" example="schema-changes" %}}
{{< /tab >}}

{{< tab "New Syntax" >}}

{{% include-example file="examples/ingest_data/postgres/create_source_cloud" example="create-source" %}}
{{% include-example file="examples/ingest_data/postgres/create_source_cloud" example="schema-changes" %}}
{{< /tab >}}
{{< /tabs >}}

### 4. Monitor the ingestion status

Before it starts consuming the replication stream, Materialize takes a snapshot
of the relevant tables in your publication. Until this snapshot is complete,
Materialize won't have the same view of your data as your PostgreSQL database.

In this step, you'll first verify that the source is running and then check the
status of the snapshotting process.

1. Back in the SQL client connected to Materialize, use the
   [`mz_source_statuses`](/reference/system-catalog/mz_internal/#mz_source_statuses)
   table to check the overall status of your source:

    ```mzsql
    WITH
      source_ids AS
      (SELECT id FROM mz_sources WHERE name = 'mz_source')
    SELECT *
    FROM
      mz_internal.mz_source_statuses
        JOIN
          (
            SELECT referenced_object_id
            FROM mz_internal.mz_object_dependencies
            WHERE
              object_id IN (SELECT id FROM source_ids)
            UNION SELECT id FROM source_ids
          )
          AS sources
        ON mz_source_statuses.id = sources.referenced_object_id;
    ```

    For each `subsource`, make sure the `status` is `running`. If you see
    `stalled` or `failed`, there's likely a configuration issue for you to fix.
    Check the `error` field for details and fix the issue before moving on.
    Also, if the `status` of any subsource is `starting` for more than a few
    minutes, [contact our team](/support/).

2. Once the source is running, use the [`mz_source_statistics`](/reference/system-catalog/mz_internal/#mz_source_statistics)
   table to check the status of the initial snapshot:

    ```mzsql
    WITH
      source_ids AS
      (SELECT id FROM mz_sources WHERE name = 'mz_source')
    SELECT sources.referenced_object_id AS id, mz_sources.name, snapshot_committed
    FROM
      mz_internal.mz_source_statistics
        JOIN
          (
            SELECT object_id, referenced_object_id
            FROM mz_internal.mz_object_dependencies
            WHERE
              object_id IN (SELECT id FROM source_ids)
            UNION SELECT id, id FROM source_ids
          )
          AS sources
        ON mz_source_statistics.id = sources.referenced_object_id
        JOIN mz_sources ON mz_sources.id = sources.referenced_object_id;
    ```
    <p></p>

    ```nofmt
    object_id | snapshot_committed
    ----------|------------------
     u144     | t
    (1 row)
    ```

    Once `snapshot_commited` is `t`, move on to the next step. Snapshotting can
    take between a few minutes to several hours, depending on the size of your
    dataset and the size of the cluster the source is running in.

### 5. Right-size the cluster

After the snapshotting phase, Materialize starts ingesting change events from
the PostgreSQL replication stream. For this work, Materialize generally
performs well with an `100cc` replica, so you can resize the cluster
accordingly.

1. Still in a SQL client connected to Materialize, use the [`ALTER CLUSTER`](/sql/alter-cluster/)
   command to downsize the cluster to `100cc`:

    ```mzsql
    ALTER CLUSTER ingest_postgres SET (SIZE '100cc');
    ```

    Behind the scenes, this command adds a new `100cc` replica and removes the
    `50cc` replica.

1. Use the [`SHOW CLUSTER REPLICAS`](/sql/show-cluster-replicas/) command to
   check the status of the new replica:

    ```mzsql
    SHOW CLUSTER REPLICAS WHERE cluster = 'ingest_postgres';
    ```
    <p></p>

    ```nofmt
         cluster     | replica |  size  | ready
    -----------------+---------+--------+-------
     ingest_postgres | r1      | 100cc  | t
    (1 row)
    ```

1. Going forward, you can verify that your new cluster size is sufficient as
follows:

    1. In Materialize, get the replication slot name associated with your
    PostgreSQL source from the [`mz_internal.mz_postgres_sources`](/reference/system-catalog/mz_internal/#mz_postgres_sources)
    table:

        ```mzsql
        SELECT
            d.name AS database_name,
            n.name AS schema_name,
            s.name AS source_name,
            pgs.replication_slot
        FROM
            mz_sources AS s
            JOIN mz_internal.mz_postgres_sources AS pgs ON s.id = pgs.id
            JOIN mz_schemas AS n ON n.id = s.schema_id
            JOIN mz_databases AS d ON d.id = n.database_id;
        ```

    1. In PostgreSQL, check the replication slot lag, using the replication slot
       name from the previous step:

        ```postgres
        SELECT
            pg_size_pretty(pg_current_wal_lsn() - confirmed_flush_lsn)
            AS replication_lag_bytes
        FROM pg_replication_slots
        WHERE slot_name = '<slot_name>';
        ```

        The result of this query is the amount of data your PostgreSQL cluster
        must retain in its replication log because of this replication slot.
        Typically, this means Materialize has not yet communicated back to
        PostgreSQL that it has committed this data. A high value can indicate
        that the source has fallen behind and that you might need to scale up
        your ingestion cluster.

## D. Explore your data

With Materialize ingesting your PostgreSQL data into durable storage, you can
start exploring the data, computing real-time results that stay up-to-date as
new data arrives, and serving results efficiently.

- Explore your data with [`SHOW SOURCES`](/sql/show-sources) and [`SELECT`](/sql/select/).

- Compute real-time results in memory with [`CREATE VIEW`](/sql/create-view/)
  and [`CREATE INDEX`](/sql/create-index/) or in durable
  storage with [`CREATE MATERIALIZED VIEW`](/sql/create-materialized-view/).

- Serve results to a PostgreSQL-compatible SQL client or driver with [`SELECT`](/sql/select/)
  or [`SUBSCRIBE`](/sql/subscribe/) or to an external message broker with
  [`CREATE SINK`](/sql/create-sink/).

- Check out the [tools and integrations](/integrations/) supported by
  Materialize.

## Considerations

<h3 id="publication-membership">Publication membership</h3>
<p>PostgreSQL&rsquo;s logical replication API does not provide a signal when users
remove tables from publications. Because of this, Materialize relies on
periodic checks to determine if a table has been removed from a publication,
at which time it generates an irrevocable error, preventing any values from
being read from the table.</p>
<p>However, it is possible to remove a table from a publication and then re-add
it before Materialize notices that the table was removed. In this case,
Materialize can no longer provide any consistency guarantees about the data
we present from the table and, unfortunately, is wholly unaware that this
occurred.</p>
<p>To mitigate this issue, if you need to drop and re-add a table to a
publication, ensure that you remove the table/subsource from the source
<em>before</em> re-adding it using the <a href="/sql/drop-source/" ><code>DROP SOURCE</code></a> command.</p>
<h3 id="supported-types">Supported types</h3>
<p>Materialize natively supports the following PostgreSQL types (including the
array type for each of the types):</p>
<ul style="column-count: 3"><li><code>bool</code></li><li><code>bpchar</code></li><li><code>bytea</code></li><li><code>char</code></li><li><code>date</code></li><li><code>daterange</code></li><li><code>float4</code></li><li><code>float8</code></li><li><code>int2</code></li><li><code>int2vector</code></li><li><code>int4</code></li><li><code>int4range</code></li><li><code>int8</code></li><li><code>int8range</code></li><li><code>interval</code></li><li><code>json</code></li><li><code>jsonb</code></li><li><code>numeric</code></li><li><code>numrange</code></li><li><code>oid</code></li><li><code>text</code></li><li><code>time</code></li><li><code>timestamp</code></li><li><code>timestamptz</code></li><li><code>tsrange</code></li><li><code>tstzrange</code></li><li><code>uuid</code></li><li><code>varchar</code></li></ul>
<p>Replicating tables that contain <strong>unsupported <a href="/sql/types/" >data types</a></strong> is
possible via the <code>TEXT COLUMNS</code> option. The specified columns will be
treated as <code>text</code>; i.e., will not have the expected PostgreSQL type
features. For example:</p>
<ul>
<li>
<p><a href="https://www.postgresql.org/docs/current/datatype-enum.html" ><code>enum</code></a>: When decoded as <code>text</code>, the implicit ordering of the original
PostgreSQL <code>enum</code> type is not preserved; instead, Materialize will sort values
as <code>text</code>.</p>
</li>
<li>
<p><a href="https://www.postgresql.org/docs/current/datatype-money.html" ><code>money</code></a>: When decoded as <code>text</code>, resulting <code>text</code> value cannot be cast
back to <code>numeric</code>, since PostgreSQL adds typical currency formatting to the
output.</p>
</li>
</ul>
<h3 id="inherited-tables">Inherited tables</h3>
<p>When using <a href="https://www.postgresql.org/docs/current/tutorial-inheritance.html" >PostgreSQL table inheritance</a>,
PostgreSQL serves data from <code>SELECT</code>s as if the inheriting tables&rsquo; data is
also present in the inherited table. However, both PostgreSQL&rsquo;s logical
replication and <code>COPY</code> only present data written to the tables themselves,
i.e. the inheriting data is <em>not</em> treated as part of the inherited table.</p>
<p>PostgreSQL sources use logical replication and <code>COPY</code> to ingest table data,
so inheriting tables&rsquo; data will only be ingested as part of the inheriting
table, i.e. in Materialize, the data will not be returned when serving
<code>SELECT</code>s from the inherited table.</p>
<ul>
<li>
<p>If using legacy syntax <a href="/sql/create-source/postgres/" ><code>CREATE SOURCE ... FOR ...</code></a>:</p>
<p>You can mimic PostgreSQL&rsquo;s <code>SELECT</code> behavior with inherited tables by
creating a materialized view that unions data from the inherited and
inheriting tables (using <code>UNION ALL</code>). However, if new tables inherit from
the table, data from the inheriting tables will not be available in the
view. You will need to add the inheriting tables via <code>ADD SUBSOURCE</code> and
create a new view (materialized or non-) that unions the new table.</p>
</li>
<li>
<p>If using new <a href="/sql/create-table/" ><code>CREATE TABLE FROM SOURCE</code></a> syntax:</p>
<p>You can mimic PostgreSQL&rsquo;s <code>SELECT</code> behavior with inherited tables by
creating a materialized view that unions data from the inherited and
inheriting tables (using <code>UNION ALL</code>). However, if new tables inherit from
the table, data from the inheriting tables will not be available in the
view. You will need to add the inheriting tables via <code>CREATE TABLE .. FROM SOURCE</code> and create a new view (materialized or non-) that unions the new
table.</p>
</li>
</ul>
<h3 id="replication-slots">Replication slots</h3>
<p>Each source ingests the raw replication stream data for all tables in the
specified publication using <strong>a single</strong> replication slot. To manage
replication slots:</p>
<ul>
<li>
<p>For PostgreSQL 13+, set a reasonable value
for <a href="https://www.postgresql.org/docs/13/runtime-config-replication.html#GUC-MAX-SLOT-WAL-KEEP-SIZE" ><code>max_slot_wal_keep_size</code></a>
to limit the amount of storage used by replication slots.</p>
</li>
<li>
<p>If you stop using Materialize, or if either the Materialize instance or
the PostgreSQL instance crash, delete any replication slots. You can query
the <code>mz_internal.mz_postgres_sources</code> table to look up the name of the
replication slot created for each source.</p>
</li>
<li>
<p>If you delete all objects that depend on a source without also dropping
the source, the upstream replication slot remains and will continue to
accumulate data so that the source can resume in the future. To avoid
unbounded disk space usage, make sure to use <a href="/sql/drop-source/" ><code>DROP SOURCE</code></a> or manually delete the replication slot.</p>
</li>
</ul>
<h3 id="modifying-an-existing-source">Modifying an existing source</h3>
<p>When you add a new subsource to an existing source (<a href="/sql/alter-source/" ><code>ALTER SOURCE ... ADD SUBSOURCE ...</code></a>), Materialize starts the snapshotting
process for the new subsource. During this snapshotting, the data ingestion for
the existing subsources for the same source is temporarily blocked. As such, if
possible, you can resize the cluster to speed up the snapshotting process and
once the process finishes, resize the cluster for steady-state.</p>
<h3 id="snapshotting">Snapshotting</h3>
<p>The PostgreSQL source performs parallel snapshotting of tables by distributing rows among
workers using ranges of
<a href="https://www.postgresql.org/docs/current/ddl-system-columns.html#DDL-SYSTEM-COLUMNS-CTID" ><code>CTID</code></a>.
Materialize uses
<a href="https://www.postgresql.org/docs/current/row-estimation-examples.html" >PostgreSQL statistics to estimate</a>
the amount of data and number of rows to read. Missing or stale statistics can result in uneven
work distribution, reducing snapshot performance. They can also cause incorrect snapshot
progress reporting in the Console.</p>
<p>To avoid this situation, before creating the source in Materialize, ensure statistics are up to
date by running PostgreSQL <code>ANALYZE</code> command.</p>

## Handling upstream operations

This section describes how changes to upstream tables that Materialize ingests
affect the corresponding Materialize tables.

### Adding a column

When you add a new column to your upstream table, Materialize continues to
ingest only the existing columns.

To incorporate the new column:

- If using the new [`CREATE SOURCE` and `CREATE TABLE FROM
SOURCE`](/sql/create-source/postgres-v2/) syntax, create a new table from
the source. See [Handle upstream column addition](/ingest-data/postgres/source-versioning/#handle-upstream-column-addition).

- If using the legacy [`CREATE SOURCE ... FOR ...`](/sql/create-source/postgres/) syntax that creates subsources, use [`DROP
SOURCE`](/sql/drop-source/) to drop the affected subsource, and then add the
table back to the source using [`ALTER SOURCE ... ADD
SUBSOURCE`](/sql/alter-source/). The re-added subsource includes the new column.

### Dropping a column

Dropping columns that Materialize does not ingest (for example, columns added
after the source was created, or columns that are excluded) is supported. As
these columns were never ingested, you can drop them without issue.

If your Materialize source ingests a column, dropping that column from your
upstream table puts the affected table into an error state.

- If using the new [`CREATE SOURCE` and `CREATE TABLE FROM
SOURCE`](/sql/create-source/postgres-v2/) syntax, you can safely drop a
column by first ignoring it in Materialize. See [Handle upstream column
drop](/ingest-data/postgres/source-versioning/#handle-upstream-column-drop).

- If using legacy [`CREATE SOURCE ... FOR ...`](/sql/create-source/postgres/) syntax, use [`DROP SOURCE`](/sql/drop-source/) to drop the affected
subsource, and then add the table back to the source using [`ALTER
SOURCE ... ADD SUBSOURCE`](/sql/alter-source/).

### Changing constraints

Materialize ignores the following constraint changes: foreign
key, `CHECK`, and `EXCLUSION`.
As such, you can add or drop them without affecting ingestion.

Materialize also ignores `NOT NULL`, `UNIQUE`, and `PRIMARY KEY` constraints that
are added after the Materialize table is created (that is, the table was created
without them). Adding such a constraint, and later dropping it, does not affect
ingestion.

Dropping a `NOT NULL`, `UNIQUE`, or `PRIMARY KEY` constraint that existed when
the table was created puts the affected table into an error state.

### Changing a column's data type

Changing an ingested column's data type upstream puts the affected
Materialize table into an error state unless the column was ingested as `text`
via the `TEXT COLUMNS` option. Ingestion for that table stops, and you must
drop and recreate the table in Materialize to resume ingestion.

### Renaming a column

Renaming a column that Materialize ingests puts the affected table into an error
state. Ingestion for that table stops, and you must drop and recreate the table
in Materialize to resume ingestion.

### Table-level operations

The following upstream operations put the affected table into an error state.
Ingestion for that table stops, and you must drop and recreate the affected
table in Materialize to resume:

- Dropping a table (`DROP TABLE`), removing it from the publication (`ALTER PUBLICATION ... DROP TABLE`), or dropping the publication (`DROP PUBLICATION`).
- Renaming a table or moving it to a different schema.
- Setting a table's replica identity to anything other than `FULL` (`ALTER TABLE ... REPLICA IDENTITY`).
- Truncating a table (`TRUNCATE`). To clear a table without putting it into an error state, use an unqualified `DELETE FROM t;` instead.

