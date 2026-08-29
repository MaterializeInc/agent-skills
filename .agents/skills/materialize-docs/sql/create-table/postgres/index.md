# CREATE TABLE: PostgreSQL source table
Create a read-only table from a PostgreSQL source (new syntax).
In Materialize, you can create read-only tables from [PostgreSQL sources created
using the new syntax](/sql/create-source/postgres-v2/).

> **Note:** You must be on **v26+** to use the new syntax.

## Syntax

> **Note:** Source-populated tables are **read-only** tables. Users **cannot** perform write
> operations
> ([`INSERT`](/sql/insert/)/[`UPDATE`](/sql/update/)/[`DELETE`](/sql/delete/)) on
> these tables.

To create a read-only table from a [source](/sql/create-source/) connected
(via native connector) to an external PostgreSQL:

```mzsql
CREATE TABLE [IF NOT EXISTS] <table_name> FROM SOURCE <source_name> (REFERENCE <upstream_table>)
[WITH (
    TEXT COLUMNS (<column_name> [, ...])
  | EXCLUDE COLUMNS (<column_name> [, ...])
  | PARTITION BY (<column_name> [, ...])
  [, ...]
)]
;

```

| Syntax element | Description |
| --- | --- |
| **IF NOT EXISTS** | *Optional.* If specified, do not throw an error if the table with the same name already exists. Instead, issue a notice and skip the table creation.  {{< include-md file="content/headless/create-table-if-not-exists-tip.md" >}}  |
| `<table_name>` |  The name of the table to create. Names for tables must follow the [naming guidelines](/sql/identifiers/#naming-restrictions).  |
| `<source_name>` |  The name of the [source](/sql/create-source/) associated with the reference object from which to create the table.  |
| **(REFERENCE <upstream_table>)** |  The name of the upstream table from which to create the table. You can create multiple tables from the same upstream table.  To find the upstream tables available in your [source](/sql/create-source/), you can use the following query, substituting your source name for `<source_name>`:  <br>  ```mzsql SELECT refs.* FROM mz_internal.mz_source_references refs, mz_sources s WHERE s.name = '<source_name>' -- substitute with your source name AND refs.source_id = s.id; ```  This list is recorded when the source is created. To update the list with tables added to the upstream since source creation, run [`ALTER SOURCE <source_name> REFRESH REFERENCES`](/sql/alter-source/#refreshing-available-upstream-references).  The statement returns an error if the source's publication is empty.  |
| **WITH (<with_option>[,...])** | The following `<with_option>`s are supported:  \| Option \| Description \| \|--------\|-------------\| \| `TEXT COLUMNS (<column_name> [, ...])` \|*Optional.* If specified, decode data as `text` for the listed column(s),such as for unsupported data types. See also [supported types](#supported-data-types). \| \| `EXCLUDE COLUMNS (<column_name> [, ...])`\| *Optional.* If specified,exclude the listed column(s) from the table, such as for unsupported data types. See also [supported types](#supported-data-types).\| \| `PARTITION BY (<column_name> [, ...])` \| {{< include-md file="content/headless/partition-by-option-description.md" >}} \|  |

## Details

### DDL transaction block

For performance, when issuing multiple `CREATE TABLE FROM SOURCE...` statements,
use within a [transaction block](/sql/begin/#ddl-only-transactions).

### Source-populated tables and snapshotting

Creating a table from a source starts the
[snapshotting](/ingest-data/#snapshotting) process.

Snapshotting is the initial sync of a table's data. It reads from the upstream
system and writes the data into Materialize's storage. The initial snapshot is
committed to storage atomically, with all records assigned the same ingestion
timestamp.

You cannot query the table until its snapshot completes.

> **Note:** During the snapshotting, the data ingestion for the existing tables for the same
> source is temporarily blocked. As such, if possible, you can resize the cluster
> to speed up the snapshotting process and once the process finishes, resize the
> cluster for steady-state. You can monitor the snapshot progress on the overview
> page for the source in the Materialize console.

### Supported data types

<p>Materialize natively supports the following PostgreSQL types (including the
array type for each of the types):</p>
<ul style="column-count: 3"><li><code>bool</code></li><li><code>bpchar</code></li><li><code>bytea</code></li><li><code>char</code></li><li><code>date</code></li><li><code>daterange</code></li><li><code>float4</code></li><li><code>float8</code></li><li><code>int2</code></li><li><code>int2vector</code></li><li><code>int4</code></li><li><code>int4range</code></li><li><code>int8</code></li><li><code>int8range</code></li><li><code>interval</code></li><li><code>json</code></li><li><code>jsonb</code></li><li><code>numeric</code></li><li><code>numrange</code></li><li><code>oid</code></li><li><code>text</code></li><li><code>time</code></li><li><code>timestamp</code></li><li><code>timestamptz</code></li><li><code>tsrange</code></li><li><code>tstzrange</code></li><li><code>uuid</code></li><li><code>varchar</code></li></ul>

Replicating tables that contain **unsupported [data types](/sql/types/)** is
possible via the `TEXT COLUMNS` option. The specified columns will be
treated as `text`; i.e., will not have the expected PostgreSQL type
features. For example:

* [`enum`]: When decoded as `text`, the implicit ordering of the original
  PostgreSQL `enum` type is not preserved; instead, Materialize will sort values
  as `text`.

* [`money`]: When decoded as `text`, resulting `text` value cannot be cast
back to `numeric`, since PostgreSQL adds typical currency formatting to the
output.

[`enum`]: https://www.postgresql.org/docs/current/datatype-enum.html
[`money`]: https://www.postgresql.org/docs/current/datatype-money.html

### Handling table schema changes

The use of `CREATE SOURCE` (new syntax) with `CREATE TABLE FROM SOURCE` allows
for the handling of the upstream DDL changes, specifically adding or dropping
columns in the upstream tables, without downtime. For details, see [PostgreSQL:
Handling upstream schema changes with zero
downtime](/ingest-data/postgres/source-versioning/).

See also [Handling upstream operations](#handling-upstream-operations) for
additional upstream operation considerations.

### Inherited tables

When using [PostgreSQL table inheritance](https://www.postgresql.org/docs/current/tutorial-inheritance.html),
PostgreSQL serves data from `SELECT`s as if the inheriting tables' data is
also present in the inherited table. However, both PostgreSQL's logical
replication and `COPY` only present data written to the tables themselves,
i.e. the inheriting data is _not_ treated as part of the inherited table.

PostgreSQL sources use logical replication and `COPY` to ingest table data,
so inheriting tables' data will only be ingested as part of the inheriting
table, i.e. in Materialize, the data will not be returned when serving
`SELECT`s from the inherited table.

You can mimic PostgreSQL's `SELECT` behavior with inherited tables by
creating a materialized view that unions data from the inherited and
inheriting tables (using `UNION ALL`). However, if new tables inherit from
the table, data from the inheriting tables will not be available in the
view. You will need to add the inheriting tables via `CREATE TABLE .. FROM
SOURCE` and create a new view (materialized or non-) that unions the new
table.

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

## Privileges

The privileges required to execute this statement are:

- `CREATE` privileges on the containing schema.
- `USAGE` privileges on all types used in the table definition.
- `USAGE` privileges on the schemas that all types in the statement are
  contained in.
- For `CREATE TABLE ... FROM SOURCE`, `SELECT` privileges on the source and
  `USAGE` privileges on its schema. `SELECT` on a source permits attaching any
  reference that source ingests, so grant it only to roles that should be able
  to read all of the source's data.

## Examples

### Create a table

> **Note:** You must be on **v26+** to use the new syntax.
> The example assumes you have configured your upstream PostgreSQL 11+ (i.e.,
> enabled logical replication, created the publication for the various tables and
> replication user, and updated the network configuration).
> For details about configuring your upstream system, see the [PostgreSQL
> integration guides](/ingest-data/postgres/#supported-versions-and-services).

To create new **read-only** tables from a source table, use the `CREATE
TABLE ... FROM SOURCE ... (REFERENCE <upstream_table>)` statement in a [DDL
transaction block](/sql/begin/#ddl-only-transactions). The following example
creates **read-only** tables `items` and `orders` from the PostgreSQL
source's `public.items` and `public.orders` tables (the schema is `public`).

{{< note >}}

- Although the example creates the tables with the same names as the
upstream tables, the tables in Materialize can have names that differ from
the referenced table names.

- For supported PostgreSQL data types, refer to [supported
types](/sql/create-table/postgres/#supported-data-types).

{{< /note >}}
```mzsql
/* This example assumes:
  - In the upstream PostgreSQL, you have defined:
    - replication user and password with the appropriate access.
    - a publication named `mz_source` for the `items` and `orders` tables.
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

      CREATE SOURCE pg_source
      FROM POSTGRES CONNECTION pg_connection (
        PUBLICATION 'mz_source'       -- substitute
      );
*/

BEGIN;
CREATE TABLE items
FROM SOURCE pg_source(REFERENCE public.items)
;
CREATE TABLE orders
FROM SOURCE pg_source(REFERENCE public.orders)
;
COMMIT;

```
{{< include-md
file="content/headless/create-table-from-source-snapshotting.md" >}}

{{< include-md file="content/headless/create-table-if-not-exists-tip.md" >}}

Once the snapshotting process completes and the table is in the running state, you can query the table:
```mzsql
SELECT * FROM items;

```

## Related pages

- [`CREATE SOURCE: PostgreSQL (New Syntax)`](/sql/create-source/postgres-v2/)
- [`DROP TABLE`](/sql/drop-table)
