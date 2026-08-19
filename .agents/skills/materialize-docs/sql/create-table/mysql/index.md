# CREATE TABLE: MySQL source table
Create a read-only table from a MySQL source (new syntax).
In Materialize, you can create read-only tables from [MySQL sources created
using the new syntax](/sql/create-source/mysql-v2/).

> **Note:** You must be on **v26.25+** to use the new syntax.

## Syntax

> **Note:** Source-populated tables are **read-only** tables. Users **cannot** perform write
> operations
> ([`INSERT`](/sql/insert/)/[`UPDATE`](/sql/update/)/[`DELETE`](/sql/delete/)) on
> these tables.

To create a read-only table from a [source](/sql/create-source/) connected
(via native connector) to an external MySQL database:

```mzsql
CREATE TABLE [IF NOT EXISTS] <table_name> FROM SOURCE <source_name> (REFERENCE <upstream_schema>.<upstream_table>)
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
| **(REFERENCE <upstream_schema>.<upstream_table>)** |  The fully-qualified name of the upstream MySQL table from which to create the table. You can create multiple tables from the same upstream table.  To find the upstream tables available in your [source](/sql/create-source/), you can use the following query, substituting your source name for `<source_name>`:  <br>  ```mzsql SELECT refs.* FROM mz_internal.mz_source_references refs, mz_sources s WHERE s.name = '<source_name>' -- substitute with your source name AND refs.source_id = s.id; ```  |
| **WITH (<with_option>[,...])** | The following `<with_option>`s are supported:  \| Option \| Description \| \|--------\|-------------\| \| `TEXT COLUMNS (<column_name> [, ...])` \| *Optional.* If specified, decode data as `text` for the listed column(s), such as for unsupported data types. See also [supported types](#supported-data-types). \| \| `EXCLUDE COLUMNS (<column_name> [, ...])` \| *Optional.* If specified, exclude the listed column(s) from the table, such as for unsupported data types. See also [supported types](#supported-data-types). \| \| `PARTITION BY (<column_name> [, ...])` \| {{< include-md file="content/headless/partition-by-option-description.md" >}} \|  |

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

<p>Materialize natively supports the following MySQL types:</p>
<ul style="column-count: 3"><li><code>bigint</code></li><li><code>binary</code></li><li><code>bit</code></li><li><code>blob</code></li><li><code>boolean</code></li><li><code>char</code></li><li><code>date</code></li><li><code>datetime</code></li><li><code>decimal</code></li><li><code>double</code></li><li><code>float</code></li><li><code>int</code></li><li><code>json</code></li><li><code>longblob</code></li><li><code>longtext</code></li><li><code>mediumblob</code></li><li><code>mediumint</code></li><li><code>mediumtext</code></li><li><code>numeric</code></li><li><code>real</code></li><li><code>smallint</code></li><li><code>text</code></li><li><code>time</code></li><li><code>timestamp</code></li><li><code>tinyblob</code></li><li><code>tinyint</code></li><li><code>tinytext</code></li><li><code>varbinary</code></li><li><code>varchar</code></li></ul>

When replicating tables that contain the **unsupported [data
types](/sql/types/)**, you can:

- Use [`TEXT COLUMNS`
  option](/sql/create-source/mysql/#handling-unsupported-types) for the
  following unsupported  MySQL types:

  - `enum`
  - `year`

  The specified columns will be treated as `text` and will not offer the
  expected MySQL type features.

- Use the [`EXCLUDE COLUMNS`](/sql/create-source/mysql/#excluding-columns)
option to exclude any columns that contain unsupported data types.

#### Zero values for `date`, `datetime`, and `timestamp`

MySQL allows the special "zero" values `0000-00-00`, `0000-00-00
00:00:00` in `date`, `datetime`, and `timestamp` columns when the server
`sql_mode` does not include `NO_ZERO_DATE` or `NO_ZERO_IN_DATE`. These
values are not representable in Materialize's corresponding native types,
so they will cause ingestion to fail for the affected column.

To ingest columns that contain zero values, use [`TEXT
COLUMNS`](/sql/create-source/mysql/#handling-unsupported-types) to
decode the affected columns as `text`. The zero values for `date`,
`datetime`, `timestamp`, and `year` are preserved verbatim as strings
(e.g. `"0000-00-00 00:00:00"`, `"0000"`).

### Handling table schema changes

The use of `CREATE SOURCE` (new syntax) with `CREATE TABLE FROM SOURCE` allows
for the handling of the upstream DDL changes, specifically adding or dropping
columns in the upstream tables, without downtime. For details, see [MySQL:
Handling upstream schema changes with zero
downtime](/ingest-data/mysql/source-versioning/).

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
SOURCE`](/sql/create-source/mysql-v2/) syntax, create a new table from
the source. See [Handle upstream column addition](/ingest-data/mysql/source-versioning/#handle-upstream-column-addition).

- If using the legacy [`CREATE SOURCE ... FOR ...`](/sql/create-source/mysql/) syntax that creates subsources, use [`DROP
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
SOURCE`](/sql/create-source/mysql-v2/) syntax, you can safely drop a
column by first ignoring it in Materialize. See [Handle upstream column
drop](/ingest-data/mysql/source-versioning/#handle-upstream-column-drop).

- If using legacy [`CREATE SOURCE ... FOR ...`](/sql/create-source/mysql/) syntax, use [`DROP SOURCE`](/sql/drop-source/) to drop the affected
subsource, and then add the table back to the source using [`ALTER
SOURCE ... ADD SUBSOURCE`](/sql/alter-source/).

### Changing constraints

Materialize ignores the following constraint changes: foreign
key and `CHECK`.
As such, you can add or drop them without affecting ingestion.

Materialize also ignores `NOT NULL`, `UNIQUE`, and `PRIMARY KEY` constraints that
are added after the Materialize table is created (that is, the table was created
without them). Adding such a constraint, and later dropping it, does not affect
ingestion.

Dropping a `NOT NULL`, `UNIQUE`, or `PRIMARY KEY` constraint that existed when
the table was created puts the affected table into an error state.

### Changing a column's data type

Changing an ingested column's data type upstream so that it maps to a different
Materialize type than before puts the affected Materialize table into an
error state. Ingestion for that table stops, and you must drop and recreate the
table in Materialize to resume ingestion.

Changing an ingested column's upstream data type so that it continues to map to
the same Materialize type does not interrupt ingestion. For example, changing
`tinyint` to `smallint`, changing within the
`text`/`tinytext`/`mediumtext`/`longtext` family, and adjusting `bit(n)`
precision are all safe.

Appending new values to the **end** of an existing enum does not put the table
into an error state. However, the newly-added values are not recognized, so rows
that use them fail to decode until you drop and recreate the table. Existing
enum values remain recognized, and rows that use them continue to decode
successfully.

Any other enum change puts the affected Materialize table into an
error state, including inserting a value before the end, reordering or renaming
values, and removing values.

### Renaming a column

Renaming a column that Materialize ingests puts the affected table into an error
state. Ingestion for that table stops, and you must drop and recreate the table
in Materialize to resume ingestion.

### Table-level operations

The following upstream operations put the affected table into an error state.
Ingestion for that table stops, and you must drop and recreate the affected
table in Materialize to resume:

- Dropping a table (`DROP TABLE`).
- Renaming a table or moving it to a different schema.
- Truncating a table (`TRUNCATE`). To clear a table without putting it into an error state, use an unqualified `DELETE FROM t;` instead.

## Privileges

The privileges required to execute this statement are:

- `CREATE` privileges on the containing schema.
- `USAGE` privileges on all types used in the table definition.
- `USAGE` privileges on the schemas that all types in the statement are
  contained in.

## Examples

### Create a table

To create new **read-only** tables from a source table, use the `CREATE
TABLE ... FROM SOURCE ... (REFERENCE <upstream_schema>.<upstream_table>)`
statement in a [DDL transaction
block](/sql/begin/#ddl-only-transactions). The following example creates
**read-only** tables `items` and `orders` from the MySQL source's
`mydb.items` and `mydb.orders` tables.

{{< note >}}

- Although the example creates the tables with the same names as the
upstream tables, the tables in Materialize can have names that differ from
the referenced table names.

- For supported MySQL data types, refer to [supported
types](/sql/create-table/mysql/#supported-data-types).

{{< /note >}}
```mzsql
/* This example assumes:
  - In the upstream MySQL, you have configured:
    - GTID-based binary log replication.
    - `binlog_row_metadata = FULL`.
    - A replication user and password with the appropriate access.
  - In Materialize:
    - You have created a secret for the MySQL password.
    - You have defined the connection to the upstream MySQL.
    - You have used the connection to create a source.

   For example (substitute with your configuration):
      CREATE SECRET mysqlpass AS '<replication user password>'; -- substitute
      CREATE CONNECTION mysql_connection TO MYSQL (
        HOST '<hostname>',          -- substitute
        PORT 3306,
        USER <replication user>,    -- substitute
        PASSWORD SECRET mysqlpass
        -- [, <network security configuration> ]
      );

      CREATE SOURCE mysql_source
      FROM MYSQL CONNECTION mysql_connection;
*/

BEGIN;
CREATE TABLE items
FROM SOURCE mysql_source (REFERENCE mydb.items)
;
CREATE TABLE orders
FROM SOURCE mysql_source (REFERENCE mydb.orders)
;
COMMIT;

```
{{< include-md
file="content/headless/create-table-from-source-snapshotting.md" >}}

{{< include-md file="content/headless/create-table-if-not-exists-tip.md" >}}

## Related pages

- [`CREATE SOURCE: MySQL (New Syntax)`](/sql/create-source/mysql-v2/)
- [`DROP TABLE`](/sql/drop-table)
