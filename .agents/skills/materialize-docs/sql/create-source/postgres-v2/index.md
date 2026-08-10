# CREATE SOURCE: PostgreSQL (New Syntax)
Creates a new source from PostgreSQL 11+.
> **Disambiguation:** This page reflects the new syntax which allows Materialize to handle upstream DDL changes, specifically adding or dropping columns, without downtime. For the deprecated syntax, see the [old reference page](/sql/create-source/postgres/).

Creates a new source from PostgreSQL.  Materialize
supports creating sources from PostgreSQL version 11&#43;.  Once a new source is created, you can <a href="/sql/create-table/postgres/" ><code>CREATE TABLE FROM SOURCE</code></a>
to create the corresponding tables in Materialize and start the data ingestion
process.

PostgreSQL 16+ is required for connecting Materialize to a physical replica.

## Prerequisites

To create a source from PostgreSQL 11+, you must first:

- **Configure upstream PostgreSQL instance**
  - Set up logical replication.
  - Create a publication.
  - Create a replication user and password for Materialize to use to connect.
- **Configure network security**
  - Ensure Materialize can connect to your PostgreSQL instance.
- **Create a connection to PostgreSQL in Materialize**
  - The connection setup depends on the network security configuration.

For details, see the [PostgreSQL integration
guides](/ingest-data/postgres/#integration-guides).

## Syntax

To create a source from an external PostgreSQL:

```mzsql
CREATE SOURCE [IF NOT EXISTS] <source_name>
[IN CLUSTER <cluster_name>]
FROM POSTGRES CONNECTION <connection_name> (PUBLICATION '<publication_name>')
[WITH ( <with_option> [, ...] )]
;

```

| Syntax element | Description |
| --- | --- |
| **IF NOT EXISTS** | *Optional.* If specified, do not throw an error if a source with the same name already exists. Instead, issue a notice and skip the source creation.  |
| `<source_name>` |  The name of the source to create. Names for sources must follow the [naming guidelines](/sql/identifiers/#naming-restrictions).  |
| **IN CLUSTER** `<cluster_name>` | *Optional.* The [cluster](/sql/create-cluster) to maintain this source. Otherwise, the source will be created in the active cluster.  {{< tip >}} If possible, use a cluster dedicated just for sources. See also [Operational guidelines](/manage/operational-guidelines/#sources). {{< /tip >}}  |
| `<connection_name>` | The name of the PostgreSQL connection to use for the source. For details on creating connections, check the [`CREATE CONNECTION`](/sql/create-connection/#postgresql) documentation page.  A connection is **reusable** across multiple `CREATE SOURCE` statements.  |
| `<publication_name>` | The name of the PostgreSQL publication to associate with the source. For details on creating a publication in your PostgreSQL database, see the [integration guides for your PostgreSQL](/ingest-data/postgres/#integration-guides).  |
| **WITH** (`<with_option>` [, ...]) | *Optional.* The following `<with_option>`s are supported:  \| Option \| Description \| \|--------\|-------------\| \| `TIMESTAMP INTERVAL [=] <interval>` \| The interval at which timestamps are assigned to data read from this source. Accepts positive [interval](/sql/types/interval/) values (e.g. `'500ms'`, `'1s'`). The value must be between the system parameters `min_timestamp_interval` and `max_timestamp_interval`. Default: the value of the `default_timestamp_interval` system parameter (`1s`). The interval can also be changed after creation with [`ALTER SOURCE`](/sql/alter-source/). \|  |

## Details

### Ingesting data

After a source is created, you can create tables from the source, referencing
the tables in the publication, to start ingesting data. You can create multiple
tables that reference the same table in the publication.

See [`CREATE TABLE FROM SOURCE`](/sql/create-table/) for details.

#### Handling table schema changes

The use of the `CREATE SOURCE` with the new [`CREATE TABLE FROM
SOURCE`](/sql/create-table/) allows for the handling of certain upstream DDL
changes without downtime.

See [`CREATE TABLE FROM
SOURCE`](/sql/create-table/postgres/#handling-table-schema-changes) for details.

See also [Handling upstream operations](#handling-upstream-operations) for
additional upstream operation considerations.

#### Supported types

With the new syntax, after a PostgreSQL source is created, you [`CREATE TABLE
FROM SOURCE`](/sql/create-table/) to create a corresponding table in
Matererialize and start ingesting data.

<p>Materialize natively supports the following PostgreSQL types (including the
array type for each of the types):</p>
<ul style="column-count: 3"><li><code>bool</code></li><li><code>bpchar</code></li><li><code>bytea</code></li><li><code>char</code></li><li><code>date</code></li><li><code>daterange</code></li><li><code>float4</code></li><li><code>float8</code></li><li><code>int2</code></li><li><code>int2vector</code></li><li><code>int4</code></li><li><code>int4range</code></li><li><code>int8</code></li><li><code>int8range</code></li><li><code>interval</code></li><li><code>json</code></li><li><code>jsonb</code></li><li><code>numeric</code></li><li><code>numrange</code></li><li><code>oid</code></li><li><code>text</code></li><li><code>time</code></li><li><code>timestamp</code></li><li><code>timestamptz</code></li><li><code>tsrange</code></li><li><code>tstzrange</code></li><li><code>uuid</code></li><li><code>varchar</code></li></ul>

For more information, including strategies for handling unsupported types,
see [`CREATE TABLE FROM SOURCE`](/sql/create-table/).

### Publication membership

PostgreSQL's logical replication API does not provide a signal when users
remove tables from publications. Because of this, Materialize relies on
periodic checks to determine if a table has been removed from a publication,
at which time it generates an irrevocable error, preventing any values from
being read from the table.

However, it is possible to remove a table from a publication and then re-add
it before Materialize notices that the table was removed. In this case,
Materialize can no longer provide any consistency guarantees about the data
we present from the table and, unfortunately, is wholly unaware that this
occurred.

To mitigate this issue, if you need to drop and re-add a table to a
publication, ensure that you remove the table/subsource from the source
_before_ re-adding it using the [`DROP SOURCE`](/sql/drop-source/) command.

### PostgreSQL replication slots

When you define a source, Materialize will automatically create a **replication
slot** in the upstream PostgreSQL database (see [PostgreSQL replication
slots](#postgresql-replication-slots)). Each source ingests the raw replication
stream data for all tables in the specified publication using **a single**
replication slot. This allows you to minimize the performance impact on the
upstream database as well as reuse the same source across multiple
materializations.

The name of the replication slot created by Materialize is prefixed with
`materialize_`. In Materialize, you can query the
`mz_internal.mz_postgres_sources` to find the replication slots created:

```mzsql
SELECT id, replication_slot FROM mz_internal.mz_postgres_sources;
```

```
    id   |             replication_slot
---------+----------------------------------------------
  u8     | materialize_7f8a72d0bf2a4b6e9ebc4e61ba769b71
```

> **Tip:** - For PostgreSQL 13+, set a reasonable value
> for [`max_slot_wal_keep_size`](https://www.postgresql.org/docs/13/runtime-config-replication.html#GUC-MAX-SLOT-WAL-KEEP-SIZE)
> to limit the amount of storage used by replication slots.
> - If you stop using Materialize, or if either the Materialize instance or
> the PostgreSQL instance crash, delete any replication slots. You can query
> the `mz_internal.mz_postgres_sources` table to look up the name of the
> replication slot created for each source.
> - If you delete all objects that depend on a source without also dropping
> the source, the upstream replication slot remains and will continue to
> accumulate data so that the source can resume in the future. To avoid
> unbounded disk space usage, make sure to use [`DROP
> SOURCE`](/sql/drop-source/) or manually delete the replication slot.

### Reading from a physical standby

Materialize can replicate from a PostgreSQL physical standby (read
replica) instead of the primary, using logical decoding on the standby.
This requires **PostgreSQL 16+** on both the primary and the standby, since
earlier versions do not support creating logical replication slots on a
standby.

When the upstream is a standby, the replication slot is created on the
standby and Materialize only connects to the standby. Note that slot
creation on a standby can block until the primary emits a standby snapshot
(a `RUNNING_XACTS` WAL record). On an idle primary, run
[`SELECT pg_log_standby_snapshot()`](https://www.postgresql.org/docs/16/functions-admin.html#FUNCTIONS-SNAPSHOT-SYNCHRONIZATION)
on the primary to unblock source creation.

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

## Examples

### Prerequisites

To create a source from PostgreSQL 11+, you must first:

- **Configure upstream PostgreSQL instance**
  - Set up logical replication.
  - Create a publication.
  - Create a replication user and password for Materialize to use to connect.
- **Configure network security**
  - Ensure Materialize can connect to your PostgreSQL instance.
- **Create a connection to PostgreSQL in Materialize**
  - The connection setup depends on the network security configuration.

For details, see the [PostgreSQL integration
guides](/ingest-data/postgres/#integration-guides).

### Create a source {#create-source-example}

Once you have configured the upstream PostgreSQL, network security, and
created the connection, you can create the source. In this example, the
PostgreSQL publication is `mz_source` and the connection to PostgreSQL is
`pg_connection`.
```mzsql
/* This example assumes:
- In the upstream PostgreSQL, you have defined:
  - replication user and password with the appropriate access.
  - a publication named `mz_source` for the `public.items` and `public.orders` tables.
- In Materialize:
  - You have created a secret for the PostgreSQL password.
  - You have defined the connection to the upstream PostgreSQL.
  - You have used the connection to create a source.

  For example (substitute with your configuration):
    CREATE SECRET pgpass AS '<replication user password>'; -- substitute
    CREATE CONNECTION pg_connection TO POSTGRES (
      HOST '<hostname>',          -- substitute
      DATABASE <db>,              -- substitute
      USER <replication user>,    -- substitute
      PASSWORD SECRET pgpass
      -- [, <network security configuration> ]
    );
*/

CREATE SOURCE pg_source
FROM POSTGRES CONNECTION pg_connection (
  PUBLICATION 'mz_source'
);

```

After a source is created, you can create tables from the source,
referencing specific upstream table(s). Use a [DDL transaction block](/sql/begin/#ddl-only-transactions) to create multiple tables from the same source.
```mzsql
BEGIN;
CREATE TABLE items
FROM SOURCE pg_source(REFERENCE public.items)
;
CREATE TABLE orders
FROM SOURCE pg_source(REFERENCE public.orders)
;
COMMIT;

```
{{< note >}}

- Although the example creates the tables with the same name as the upstream tables, the tables in Materialize can have different names.
- You can create multiple tables that reference the same upstream table.
{{< /note >}}

For more information, see [`CREATE TABLE`](/sql/create-table/).

## Related pages

- [`CREATE TABLE`](/sql/create-table/)
- [`CREATE SECRET`](/sql/create-secret)
- [`CREATE CONNECTION`](/sql/create-connection)
- [PostgreSQL integration guides](/ingest-data/postgres/#integration-guides)

[`enum`]: https://www.postgresql.org/docs/current/datatype-enum.html
[`money`]: https://www.postgresql.org/docs/current/datatype-money.html
