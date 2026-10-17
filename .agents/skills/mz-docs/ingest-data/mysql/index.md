# MySQL

Connecting Materialize to a MySQL database for Change Data Capture (CDC).

## Ingest from MySQL via change data capture

Materialize supports MySQL (8.0.1+) as a real-time data source. The [MySQL source](/sql/create-source/mysql-v2/)
uses MySQL's [binlog replication protocol](/sql/create-source/mysql-v2/#change-data-capture)
to **continually ingest changes** resulting from CRUD operations in the upstream
database. The native support for MySQL Change Data Capture (CDC) in Materialize
gives you the following benefits:

- **No additional infrastructure:** Ingest MySQL change data into Materialize in
  real-time with no architectural changes or additional operational overhead.
  In particular, you **do not need to deploy Kafka and Debezium** for MySQL
  CDC.

- **Transactional consistency:** The MySQL source ensures that transactions in
  the upstream MySQL database are respected downstream. Materialize will
  **never show partial results** based on partially replicated transactions.

- **Incrementally updated materialized views:** Materialized views are **not
  supported in MySQL**, so you can use Materialize as a
  read-replica to build views on top of your MySQL data that are efficiently
  maintained and always up-to-date.

### Supported versions and services

> **Note:** MySQL-compatible database systems are not guaranteed to work with the MySQL
> source out-of-the-box. [MariaDB](https://mariadb.org/), [Vitess](https://vitess.io/)
> and [PlanetScale](https://planetscale.com/) are currently **not supported**.

The MySQL source requires **MySQL 8.0.1+** and is compatible with most common
MySQL hosted services.

### Integration guides

To help you get started, the following integration guides are available:

- [Amazon Aurora for MySQL](/ingest-data/mysql/amazon-aurora/)
- [Amazon RDS for MySQL](/ingest-data/mysql/amazon-rds/)
- [Azure DB for MySQL](/ingest-data/mysql/azure-db/)
- [Google Cloud SQL for MySQL](/ingest-data/mysql/google-cloud-sql/)
- [Self-hosted MySQL](/ingest-data/mysql/self-hosted/)

## Supported data types

### Supported types

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

## How ingestion from MySQL works

### Snapshot parallelism

When a source is created, Materialize parallelizes the initial snapshot across
the cluster's workers, and can split the read of a large table across workers
when the table meets certain requirements. See [Snapshot
parallelism](/ingest-data/mysql/snapshot-parallelism/).

### Adding a table to an existing source

When you add a new subsource to an existing source ([`ALTER SOURCE ... ADD
SUBSOURCE ...`](/sql/alter-source/)), Materialize starts the snapshotting
process for the new subsource. During this snapshotting, the data ingestion for
the existing subsources for the same source is temporarily blocked. As such, if
possible, you can resize the cluster to speed up the snapshotting process and
once the process finishes, resize the cluster for steady-state.

## Supported schema and table changes

The following table summarizes how Materialize handles changes to an upstream
table it is ingesting. See the details below the table for recovery commands.

| Change | Effect |
| --- | --- |
| Foreign key or `CHECK` constraint changes | No impact: Materialize ignores these changes. |
| Adding a `NOT NULL`, `UNIQUE`, or `PRIMARY KEY` constraint after the Materialize table was created | No impact. |
| Dropping an excluded column, or a column added after the Materialize table was created | No impact. |
| [Adding a column](#adding-a-column) | Handled automatically. Materialize keeps ingesting the existing columns; incorporate the new column with a new table (current syntax) or by re-adding the subsource (legacy syntax). |
| [Dropping an ingested column](#dropping-a-column) | Table enters an error state. Re-create the table. |
| [Renaming an ingested column](#renaming-a-column) | Table enters an error state. Re-create the table. |
| [Changing an ingested column's data type](#changing-a-columns-data-type) so that it maps to a different Materialize type | Table enters an error state. Re-create the table. |
| Changing an ingested column's data type so that it still maps to the same Materialize type | No impact. |
| [Appending a value to the end of an enum](#changing-a-columns-data-type) | Ingestion continues, but rows that use the new value fail to decode. Re-create the table to pick up the value. |
| [Any other enum change](#changing-a-columns-data-type) | Table enters an error state. Re-create the table. |
| [Dropping a `NOT NULL`, `UNIQUE`, or `PRIMARY KEY` constraint](#changing-constraints) that existed when the Materialize table was created | Table enters an error state. Re-create the table. |
| [Dropping, renaming, truncating, or moving a table to another schema](#table-level-operations) | Table enters an error state. Re-create the table. |

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

If using the new [`CREATE SOURCE` and `CREATE TABLE FROM
SOURCE`](/sql/create-source/mysql-v2/) syntax, you can safely drop such a
constraint by first excluding it in Materialize. See [Handle upstream
constraint drop](/ingest-data/mysql/source-versioning/#handle-upstream-constraint-drop).
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

## Supported database operations

The following table summarizes how Materialize handles operational events on
the upstream MySQL database. See the details below the table for the error text
and any required configuration.

| Operation | Resolution |
| --- | --- |
| Restarting or patching MySQL (including OS-level restarts) | Supported automatically. |
| Restarting Materialize | Supported automatically. |
| Transient network interruptions between Materialize and MySQL | Supported automatically. |
| The upstream server running out of disk space | Supported automatically. |
| A long-running upstream transaction blocking the initial snapshot | Supported automatically. |
| [Failing over to a replica](#failovers) | Supported automatically, with the checks below. |
| [Binlog files covering the resume point removed](#binlog-files-removed-before-the-resume-point) | Requires re-creating the source. |
| [Resetting the binary log](#resetting-the-binary-log) | Requires re-creating the source. |
| [Changing a required replication setting](#changing-a-required-replication-setting) | Requires re-creating the source. |
| [Restoring the upstream database from a backup](#restoring-the-upstream-database) | Requires re-creating the source. |
| [Out-of-order GTIDs](#out-of-order-gtids) | Requires re-creating the source. |
| [Lowering `binlog_row_metadata`](#lowering-binlog_row_metadata) | Requires re-creating the affected tables. |

### Operations that do not require re-creating the source

Materialize tracks its position in the upstream binary log as a set of [global
transaction identifiers
(GTIDs)](https://dev.mysql.com/doc/refman/8.0/en/replication-gtids.html), which
it persists alongside the ingested data. A GTID identifies a transaction across
the whole replication topology, not a byte offset in a particular binlog file,
so it survives routine operational events: after an interruption the source
reconnects, asks the server for the transactions after its last committed GTID,
and catches up.

The source recovers on its own. It briefly reports a `stalled` status while the
condition persists, then returns to `running` and catches up for all of the
following:

- Restarting or patching MySQL (including OS-level restarts).
- Restarting Materialize. The source resumes from its tracked GTID set and does
  **not** re-snapshot already-ingested data.
- Transient network interruptions between Materialize and MySQL.
- The upstream server running out of disk space, until space is reclaimed.
- A long-running upstream transaction blocking the initial snapshot. The source
  stalls until that transaction commits or rolls back.
- [Failing over to a replica](#failovers), with the checks described below.

> **Note:** Recovery after an interruption depends on the binlog files that contain the
> source's resume point still existing on the upstream server. If the
> interruption outlasts the binlog retention window, the source can no longer
> recover on its own. See [Binlog files removed before the resume
> point](#binlog-files-removed-before-the-resume-point).

### Operations that require re-creating the source

A smaller set of events breaks GTID continuity or makes the binlog stream
unreadable. Materialize cannot then guarantee a correct, gap-free view of your
data, so it puts the **entire source** into an error state that requires
**re-creating** the source. Upstream changes to an individual table's schema
are handled separately, and do not error the entire source.

In each case, the remediation is to drop the source and create it again with
the statements you originally used, which triggers a fresh
[snapshot](/ingest-data/#snapshotting):

```mzsql
DROP SOURCE mz_source CASCADE;
```

> **Warning:** `CASCADE` drops **every object that depends on the source**, including views,
> materialized views, indexes, and sinks. Take stock of them before you drop the
> source, because you have to re-create them yourself.

Once the source is back, it is healthy when `status` is `running` and `error`
is `NULL`:

```mzsql
SELECT status, error FROM mz_internal.mz_source_statuses WHERE name = 'mz_source';
```

#### Binlog files removed before the resume point

MySQL expires binlog files on a retention schedule, and `PURGE BINARY LOGS`
removes them on demand. If Materialize is disconnected or lagging long enough
that the files holding its resume point are removed, the source fails with one
of:

```nofmt
mysql server does not have the binlog available at the requested gtid set
```

```nofmt
mysql server binlog frontier at <frontier> is beyond required frontier <frontier>
```

To avoid this, keep planned outages shorter than the retention window and
monitor source lag against it. For how retention is configured, including the
service-specific parameters that override it, see [Binlog
retention](/sql/create-source/mysql-v2/#binlog-retention).

#### Resetting the binary log

`RESET BINARY LOGS AND GTIDS` (`RESET MASTER` before MySQL 8.4) discards the
binlog files and the server's GTID history, so the source's resume point no
longer exists. The source fails with:

```nofmt
mysql server does not have the binlog available at the requested gtid set
```

or, if the server then reissues GTIDs the source has already seen, with an
[out-of-order GTID error](#out-of-order-gtids).

#### Changing a required replication setting

Materialize re-validates the upstream replication settings each time it
(re-)establishes the replication stream. If one no longer holds its required
value, the source fails with:

```nofmt
mysql server configuration: invalid mysql system setting '<setting>'. Expected '<expected>'. Got '<actual>'.
```

The validated settings are `log_bin`, `binlog_format`, `binlog_row_image`,
`gtid_mode`, `enforce_gtid_consistency`, `gtid_next`, and, when
`replica_parallel_workers` is greater than `1`,
`replica_preserve_commit_order` (`slave_preserve_commit_order` on servers
older than MySQL 8.0). For the required values, see [Change data
capture](/sql/create-source/mysql-v2/#change-data-capture). Restore the setting
upstream, then re-create the source.

#### Restoring the upstream database

Materialize has no dedicated check for a restore of the upstream database.
Depending on how the restore handles GTIDs, the source either fails with one of
the errors above or with:

```nofmt
received a gtid set from the server that violates our requirements: <detail>
```

or, if the restore reuses GTIDs the source has already ingested, it keeps
replicating against a history that no longer matches its state. Materialize
cannot detect that case, so re-create the source after any restore of the
upstream database, including a disaster-recovery restore onto a new server,
rather than relying on an error.

#### Out-of-order GTIDs

If Materialize observes GTIDs in an order it cannot reconcile, the source fails
with:

```nofmt
received out of order gtids for source <source_id> at transaction-id <transaction_id>
```

This is most common when Materialize replicates from a MySQL replica that
applies transactions with multiple threads. See [Troubleshooting: Received out
of order GTIDs](/ingest-data/mysql/received-out-of-order-gtids/) for the
diagnosis steps and the upstream settings that make it less likely.

### Operations that require re-creating only the affected tables

#### Lowering `binlog_row_metadata`

A table that Materialize began ingesting while `binlog_row_metadata` was `FULL`
can no longer be decoded once the setting is lowered, and enters an error state
with:

```nofmt
unable to decode: Table <table> was created with binlog_row_metadata=FULL but
binlog_row_metadata has since been set to a different value, meaning we cannot
reliably decode the columns
```

Restoring `binlog_row_metadata=FULL` does not clear the error. Set it back to
`FULL` and re-create the affected tables. Tables that were created while the
setting was lower keep replicating.

> **Note:** `binlog_row_metadata=FULL` is required to use the [current `CREATE SOURCE`
> syntax](/sql/create-source/mysql-v2/#change-data-capture), so for a source
> created with that syntax this affects every table in the source. A common cause
> is a MySQL restart discarding a `SET GLOBAL` that was never persisted.

### Failovers

Because Materialize replicates by GTID rather than by binlog file and position,
it can follow a failover to a replica that was replicating from the failed
server with GTIDs enabled. Point the connection at the new primary with [`ALTER
CONNECTION`](/sql/alter-connection/), or at an endpoint that always resolves to
the current primary.

On the new primary, confirm that:

- The binlog files covering the source's resume point are present. A replica
  configured with a shorter retention than the old primary can leave the source
  with no way to resume. See [Binlog files removed before the resume
  point](#binlog-files-removed-before-the-resume-point).
- The [required replication settings](#changing-a-required-replication-setting)
  hold, including `replica_preserve_commit_order` while the server is still
  applying replication from another server. Multi-threaded apply is the main
  source of [out-of-order GTIDs](#out-of-order-gtids); preserving commit order
  reduces but does not eliminate the risk, so keep
  `replica_parallel_workers` at `0` or `1` where you can.

## Pages in this section

- [Handle upstream schema changes](/ingest-data/mysql/source-versioning/index.md): How to add a column, drop a column, or drop a constraint in your source MySQL database, without any downtime in Materialize
- [Ingest data from Amazon Aurora](/ingest-data/mysql/amazon-aurora/index.md): How to stream data from Amazon Aurora for MySQL to Materialize
- [Ingest data from Amazon RDS](/ingest-data/mysql/amazon-rds/index.md): How to stream data from Amazon RDS for MySQL to Materialize
- [Ingest data from Azure DB](/ingest-data/mysql/azure-db/index.md): How to stream data from Azure DB for MySQL to Materialize
- [Ingest data from Google Cloud SQL](/ingest-data/mysql/google-cloud-sql/index.md): How to stream data from Google Cloud SQL for MySQL to Materialize
- [Ingest data from self-hosted MySQL](/ingest-data/mysql/self-hosted/index.md): How to stream data from self-hosted MySQL database to Materialize
- [MySQL CDC using Kafka and Debezium](/ingest-data/mysql/mysql-debezium/index.md): How to propagate Change Data Capture (CDC) data from a MySQL database to Materialize using Kafka and Debezium
- [Snapshot parallelism](/ingest-data/mysql/snapshot-parallelism/index.md): How Materialize splits the snapshot of a single MySQL table across the workers of a cluster.
- [Troubleshooting](/ingest-data/mysql/troubleshooting/index.md): Troubleshooting guides for MySQL source errors in Materialize
- [Troubleshooting: Received out of order GTIDs](/ingest-data/mysql/received-out-of-order-gtids/index.md): How to troubleshoot and resolve the received out of order GTIDs error with MySQL sources in Materialize
