# CREATE TABLE: SQL Server source table
Create a read-only table from a SQL Server source (new syntax).
In Materialize, you can create read-only tables from [SQL Server sources created
using the new syntax](/sql/create-source/sql-server-v2/).

> **Note:** You must be on **v26.14.1+** to use the syntax.

## Syntax

> **Note:** Source-populated tables are **read-only** tables. Users **cannot** perform write
> operations
> ([`INSERT`](/sql/insert/)/[`UPDATE`](/sql/update/)/[`DELETE`](/sql/delete/)) on
> these tables.

To create a read-only table from a [source](/sql/create-source/) connected
(via native connector) to an external SQL Server database:

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
| **(REFERENCE <upstream_table>)** |  The name of the upstream table from which to create the table. You can create multiple tables from the same upstream table.  To find the upstream tables available in your [source](/sql/create-source/), you can use the following query, substituting your source name for `<source_name>`:  <br>  ```mzsql SELECT refs.* FROM mz_internal.mz_source_references refs, mz_sources s WHERE s.name = '<source_name>' -- substitute with your source name AND refs.source_id = s.id; ```  |
| **WITH (<with_option>[,...])** | The following `<with_option>`s are supported:  \| Option \| Description \| \|--------\|-------------\| \| `TEXT COLUMNS (<column_name> [, ...])` \|*Optional.* If specified, decode data as `text` for the listed column(s),such as for unsupported data types. See also [supported types](#supported-data-types). \| \| `EXCLUDE COLUMNS (<column_name> [, ...])`\| *Optional.* If specified,exclude the listed column(s) from the table, such as for unsupported data types. See also [supported types](#supported-data-types).\| \| `PARTITION BY (<column_name> [, ...])` \| {{< include-md file="content/headless/partition-by-option-description.md" >}} \|  |

## Details

### DDL transaction block

For performance, when issuing multiple `CREATE TABLE FROM SOURCE...` statements,
use within a [transaction block](/sql/begin/#ddl-only-transactions).

### Source-populated tables and snapshotting

Creating the tables from sources starts the [snapshotting](/ingest-data/#snapshotting) process. Snapshotting syncs the
currently available data into Materialize. Because the initial snapshot is
persisted in the storage layer atomically (i.e., at the same ingestion
timestamp), you are not able to query the table until snapshotting is complete.

> **Note:** During the snapshotting, the data ingestion for the existing tables for the same
> source is temporarily blocked. As such, if possible, you can resize the cluster
> to speed up the snapshotting process and once the process finishes, resize the
> cluster for steady-state. You can monitor the snapshot progress on the overview
> page for the source in the Materialize console.

### Supported data types

Materialize natively supports the following SQL Server types:

<ul style="column-count: 3"><li><code>tinyint</code></li><li><code>smallint</code></li><li><code>int</code></li><li><code>bigint</code></li><li><code>real</code></li><li><code>double precision</code></li><li><code>float</code></li><li><code>bit</code></li><li><code>decimal</code></li><li><code>numeric</code></li><li><code>money</code></li><li><code>smallmoney</code></li><li><code>char</code></li><li><code>nchar</code></li><li><code>varchar</code></li><li><code>varchar(max)</code></li><li><code>nvarchar</code></li><li><code>nvarchar(max)</code></li><li><code>sysname</code></li><li><code>binary</code></li><li><code>varbinary</code></li><li><code>json</code></li><li><code>date</code></li><li><code>time</code></li><li><code>smalldatetime</code></li><li><code>datetime</code></li><li><code>datetime2</code></li><li><code>datetimeoffset</code></li><li><code>uniqueidentifier</code></li></ul>

#### `char` and `nchar` columns

To preserve values exactly as SQL Server returns them, `char` and `nchar` columns
are replicated as `text` rather than fixed-length. SQL Server and Materialize
measure fixed-length character types differently, so replicating as text avoids
truncation and padding mismatches.

To replicate tables that contain the following unsupported data types, you can
use either the `TEXT COLUMNS` or the `EXCLUDE COLUMNS` option:

| Unsupported type | Supported option(s)                                         |
| ---------------- | ----------------------------------------------------------- |
| `text`           | `TEXT COLUMNS` (exposed as `varchar`) or `EXCLUDE COLUMNS`  |
| `ntext`          | `TEXT COLUMNS` (exposed as `nvarchar`) or `EXCLUDE COLUMNS` |
| `image`          | `EXCLUDE COLUMNS`                                           |
| `varbinary(max)` | `EXCLUDE COLUMNS`                                           |

### Handling table schema changes

The use of `CREATE SOURCE` (new syntax) with `CREATE TABLE FROM SOURCE` allows
for the handling of the upstream DDL changes, specifically adding or dropping
columns in the upstream tables, without downtime. For details, see [SQL Server:
Handling upstream schema changes with zero
downtime](/ingest-data/sql-server/source-versioning/).

See also [Handling upstream operations](#handling-upstream-operations) for
additional upstream operation considerations.

## Handling upstream operations

This section describes how changes to upstream tables that Materialize ingests
affect the corresponding Materialize tables.

### Adding a column

When you add a new column to your upstream table, Materialize continues to
ingest only the existing columns.

To incorporate the new column:

- If using the new [`CREATE SOURCE` and `CREATE TABLE FROM
SOURCE`](/sql/create-source/sql-server-v2/) syntax, create a new table from
the source. See [Handle upstream column addition](/ingest-data/sql-server/source-versioning/#handle-upstream-column-addition).

- If using the legacy [`CREATE SOURCE ... FOR ...`](/sql/create-source/sql-server/) syntax that creates subsources, use [`DROP
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
SOURCE`](/sql/create-source/sql-server-v2/) syntax, you can safely drop a
column by first ignoring it in Materialize. See [Handle upstream column
drop](/ingest-data/sql-server/source-versioning/#handle-upstream-column-drop).

- If using legacy [`CREATE SOURCE ... FOR ...`](/sql/create-source/sql-server/) syntax, use [`DROP SOURCE`](/sql/drop-source/) to drop the affected
subsource, and then add the table back to the source using [`ALTER
SOURCE ... ADD SUBSOURCE`](/sql/alter-source/).

### Changing constraints

Materialize ignores foreign key and `CHECK` constraint changes. You can add or
drop them without affecting ingestion.

Adding a `UNIQUE` constraint does not affect ingestion. Dropping a `UNIQUE`
constraint puts the affected table into an error state.

SQL Server does not allow dropping a `PRIMARY KEY` from a table while change data
capture is enabled on it. A primary key that existed when Materialize began
ingesting the table therefore cannot be dropped upstream.

Adding or removing a `NOT NULL` constraint on an ingested column requires an
upstream `ALTER COLUMN`, which puts the affected table into an error state. See
[Changing a column's data type](#changing-a-columns-data-type).
### Changing a column's data type

Any upstream `ALTER COLUMN` on an ingested column puts the affected Materialize
table into an error state. This covers every `ALTER COLUMN` operation, not just
data-type changes. Changing a column's collation, sparseness, masking, or
nullability all error the table the same way. Ingestion for that table stops,
and you must drop and recreate the table in Materialize to resume ingestion.

### Renaming a column

Renaming a column that Materialize ingests puts the affected table into an error
state. Ingestion for that table stops, and you must drop and recreate the table
in Materialize to resume ingestion.

### Removing a capture instance

SQL Server allows up to two capture instances to exist for a table at once.
Materialize ingests from one of them.

Removing the capture instance that Materialize is using puts the affected table
into an error state. Removing a capture instance that Materialize is not using does not affect
ingestion.

### Table-level operations

The following upstream operations put the affected table into an error state.
Ingestion for that table stops, and you must drop and recreate the affected
table in Materialize to resume:

- Dropping a table (`DROP TABLE`).
- Renaming a table or moving it to a different schema.

## Privileges

The privileges required to execute this statement are:

- `CREATE` privileges on the containing schema.
- `USAGE` privileges on all types used in the table definition.
- `USAGE` privileges on the schemas that all types in the statement are
  contained in.

## Examples

### Create a table

To create new **read-only** tables from a source table, use the `CREATE
TABLE ... FROM SOURCE ... (REFERENCE <upstream_table>)` statement in a [DDL
transaction block](/sql/begin/#ddl-only-transactions). The following example
creates **read-only** tables `items` and `orders` from the SQL Server
source's `dbo.items` and `dbo.orders` tables.

{{< note >}}

- Although the example creates the tables with the same names as the
upstream tables, the tables in Materialize can have names that differ from
the referenced table names.

- The upstream table must have [Change Data Capture
(CDC)](/ingest-data/sql-server/) enabled.

- For supported SQL Server data types, refer to [supported
types](/sql/create-table/sql-server/#supported-data-types).

{{< /note >}}
```mzsql
/* This example assumes:
  - In the upstream SQL Server, you have:
    - Enabled Change Data Capture (CDC) on the database and the tables.
    - A user and password with the appropriate access.
  - In Materialize:
    - You have created a secret for the SQL Server password.
    - You have defined the connection to the upstream SQL Server.
    - You have used the connection to create a source.

   For example (substitute with your configuration):
      CREATE SECRET sqlserver_pass AS '<password>'; -- substitute
      CREATE CONNECTION sql_server_connection TO SQL SERVER (
        HOST '<hostname>',          -- substitute
        PORT 1433,
        DATABASE <db>,              -- substitute
        USER <user>,                -- substitute
        PASSWORD SECRET sqlserver_pass
        -- [, <network security configuration> ]
      );

      CREATE SOURCE sql_server_source
      FROM SQL SERVER CONNECTION sql_server_connection;
*/

BEGIN;
CREATE TABLE items
FROM SOURCE sql_server_source (REFERENCE dbo.items)
;
CREATE TABLE orders
FROM SOURCE sql_server_source (REFERENCE dbo.orders)
;
COMMIT;

```
{{< include-md
file="content/headless/create-table-from-source-snapshotting.md" >}}

{{< include-md file="content/headless/create-table-if-not-exists-tip.md" >}}

To verify that the tables have been created, you can run [`SHOW
TABLES`](/sql/show-tables/) to list all tables in the current
[schema](/sql/namespaces/#namespace-hierarchy):
```mzsql
SHOW TABLES;

```The results should include the tables `items` and `orders`:

```hc {hl_lines="3-4"}
| name   | comment |
| ------ | ------- |
| items  |         |
| orders |         |
```

Inspect the table columns using the [`SHOW COLUMNS`](/sql/show-columns/)
command:
```mzsql
SHOW COLUMNS FROM items;

```The results should display the table columns, with types mapped from the
upstream SQL Server table. For the list of supported SQL Server data types,
refer to [supported
types](/sql/create-table/sql-server/#supported-data-types).

```hc
| name     | nullable | type              | comment |
| -------- | -------- | ----------------- | ------- |
| id       | false    | integer           |         |
| item     | true     | character varying |         |
| quantity | true     | integer           |         |
```

Once the snapshotting process completes and the tables are in the running
state, you can query them:
```mzsql
SELECT * FROM items ORDER BY id;

``````hc
| id | item   | quantity |
| -- | ------ | -------- |
| 1  | widget | 5        |
| 2  | gadget | 2        |
```

## Related pages

- [`CREATE SOURCE: SQL Server (New Syntax)`](/sql/create-source/sql-server-v2/)
- [`DROP TABLE`](/sql/drop-table)
