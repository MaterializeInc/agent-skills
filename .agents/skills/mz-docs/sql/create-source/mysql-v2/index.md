# CREATE SOURCE: MySQL (New Syntax)
Connecting Materialize to a MySQL database for Change Data Capture (CDC).
> **Disambiguation:** This page reflects the new syntax which allows Materialize to handle upstream DDL changes, specifically adding or dropping columns, without downtime. For the deprecated syntax, see the [old reference page](/sql/create-source/mysql/).

Creates a new source from MySQL.  Materialize
supports creating sources from MySQL version 8.0.1&#43;.  Once a new source is created, you can <a href="/sql/create-table/mysql/" ><code>CREATE TABLE FROM SOURCE</code></a>
to create the corresponding tables in Materialize and start the data ingestion
process.

## Prerequisites

To create a source from MySQL(8.0.1+), you must first:
- **Configure upstream MySQL instance**
  - Enable [GTID-based binary log(binlog)
    replication](#change-data-capture). You **must** set
    [`binlog_row_metadata=FULL`](#change-data-capture) to use the new
    `CREATE SOURCE` syntax.
  - Create a replication user and password for Materialize to use to
    connect.
- **Configure network security**
  - Ensure Materialize can connect to your MySQL instance.
- **Create a connection to MySQL in Materialize**
  - The [connection setup](/sql/create-connection/#mysql) depends on the
    network security configuration.

## Syntax

To create a source from an external MySQL database:

```mzsql
CREATE SOURCE [IF NOT EXISTS] <source_name>
[IN CLUSTER <cluster_name>]
FROM MYSQL CONNECTION <connection_name>
[WITH ( <with_option> [, ...] )]
;

```

| Syntax element | Description |
| --- | --- |
| **IF NOT EXISTS** | *Optional.* If specified, do not throw an error if a source with the same name already exists. Instead, issue a notice and skip the source creation.  |
| `<source_name>` | The name of the source to create. Names for sources must follow the [naming guidelines](/sql/identifiers/#naming-restrictions).  |
| **IN CLUSTER** `<cluster_name>` | *Optional.* The [cluster](/sql/create-cluster) to maintain this source. Otherwise, the source will be created in the active cluster.  {{< tip >}} If possible, use a cluster dedicated just for sources. See also [Operational guidelines](/clusters/operational-guidelines/#sources). {{< /tip >}}  |
| `<connection_name>` | The name of the MySQL connection to use for the source. For details on creating connections, see [`CREATE CONNECTION`](/sql/create-connection/#mysql).  A connection is **reusable** across multiple `CREATE SOURCE` statements.  To start ingesting data, create a [`CREATE TABLE FROM SOURCE`](/sql/create-table/) statement for each upstream table to replicate.  |
| **WITH** (`<with_option>` [, ...]) | *Optional.* The following `<with_option>`s are supported:  \| Option \| Description \| \|--------\|-------------\| \| `TIMESTAMP INTERVAL [=] <interval>` \| The interval at which timestamps are assigned to data read from this source. Accepts positive [interval](/sql/types/interval/) values (e.g. `'500ms'`, `'1s'`). The value must be between the system parameters `min_timestamp_interval` and `max_timestamp_interval`. Default: the value of the `default_timestamp_interval` system parameter (`1s`). The interval can also be changed after creation with [`ALTER SOURCE`](/sql/alter-source/). \|  |

## Ingesting data

After a source is created, you can create tables from the source referencing
upstream MySQL tables that have [GTID-based binlog replication
enabled](#change-data-capture) (Note: `binlog_row_metadata=FULL` is required to
use the new syntax). You can create multiple tables that reference the same
upstream table. See [`CREATE TABLE FROM SOURCE`](/sql/create-table/) for
details.

### Handling table schema changes

The use of `CREATE SOURCE` with the new [`CREATE TABLE FROM
SOURCE`](/sql/create-table/) allows for the handling of certain upstream schema
changes, specifically adding or dropping columns in the upstream tables, without
downtime.

See [Handle upstream schema
changes](/ingest-data/mysql/source-versioning/) for details.

See also [Handling upstream operations](#handling-upstream-operations) for
additional upstream operation considerations.

### Supported types

With the new syntax, after a MySQL source is created, you [`CREATE TABLE FROM
SOURCE`](/sql/create-table/) to create a corresponding table in Materialize and
start ingesting data.

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

For more information, including strategies for handling unsupported types,
see [`CREATE TABLE FROM SOURCE`](/sql/create-table/).

### Change data capture

> **Note:** For step-by-step instructions on enabling GTID-based binlog replication for your
> MySQL service, see the integration guides:
> - [Amazon Aurora for MySQL](/ingest-data/mysql/amazon-aurora/)
> - [Amazon RDS for MySQL](/ingest-data/mysql/amazon-rds/)
> - [Azure DB for MySQL](/ingest-data/mysql/azure-db/)
> - [Google Cloud SQL for MySQL](/ingest-data/mysql/google-cloud-sql/)
> - [Self-hosted MySQL](/ingest-data/mysql/self-hosted/)

The source uses MySQL's binlog replication protocol to **continually ingest
changes** resulting from `INSERT`, `UPDATE` and `DELETE` operations in the
upstream database. This process is known as _change data capture_.

The replication method used is based on [global transaction identifiers
(GTIDs)](https://dev.mysql.com/doc/refman/8.0/en/replication-gtids.html), and
guarantees **transactional consistency** — any operation inside a MySQL
transaction is assigned the same timestamp in Materialize, which means that the
source will never show partial results based on partially replicated
transactions.

Before creating a source in Materialize, you **must** configure the upstream
MySQL database for GTID-based binlog replication:

<table>
<thead>
<tr>

<th>MySQL Configuration</th>

<th>Value</th>

<th>Notes</th>

</tr>
</thead>
<tbody>

<tr>

<td>
<code>log_bin</code>
</td>

<td>
<code>ON</code>
</td>

<td>

</td>

</tr>

<tr>

<td>
<code>binlog_row_image</code>
</td>

<td>
<code>FULL</code>
</td>

<td>

</td>

</tr>

<tr>

<td>
<code>binlog_row_metadata</code>
</td>

<td>
<code>FULL</code>
</td>

<td>
<ul>
<li><strong>Required</strong> to use <a href="/sql/create-source/mysql-v2/" ><code>CREATE SOURCE</code> (New
syntax)</a>.</li>
<li>Highly recommended for use with the <a href="/sql/create-source/mysql/" ><code>CREATE SOURCE</code> (Legacy
syntax)</a>.</li>
</ul>

</td>

</tr>

<tr>

<td>
<code>binlog_format</code>
</td>

<td>
<code>ROW</code>
</td>

<td>
<a href="https://dev.mysql.com/doc/refman/8.0/en/replication-options-binary-log.html#sysvar_binlog_format" >Deprecated as of MySQL 8.0.34</a>. Newer versions of MySQL default to row-based logging.
</td>

</tr>

<tr>

<td>
<code>gtid_mode</code>
</td>

<td>
<code>ON</code>
</td>

<td>

</td>

</tr>

<tr>

<td>
<code>enforce_gtid_consistency</code>
</td>

<td>
<code>ON</code>
</td>

<td>

</td>

</tr>

<tr>

<td>
<code>replica_preserve_commit_order</code>
</td>

<td>
<code>ON</code>
</td>

<td>
Only required when connecting Materialize to a read-replica.
</td>

</tr>

</tbody>
</table>

> **Tip:** For `binlog_row_metadata`, using `SET GLOBAL binlog_row_metadata = FULL;` does
> not persist across MySQL server restarts. To make
> the setting durable, use `SET PERSIST` (MySQL 8.0.11+) or set
> `binlog_row_metadata=FULL` in the server's configuration file. On managed
> services, set the variable through the service's parameter configuration
> instead.

If you're running MySQL using a managed service, additional configuration
changes might be required. To enable GTID-based binlog replication for your
MySQL service, see the integration guides.

#### Binlog retention

> **Warning:** If Materialize tries to resume replication and finds GTID gaps due to missing
> binlog files, the source enters an errored state and you have to drop and
> recreate it. See [Binlog files removed before the resume
> point](#binlog-files-removed-before-the-resume-point).

By default, MySQL retains binlog files for **30 days** (i.e., 2592000 seconds)
before automatically removing them. This is configurable via the
[`binlog_expire_logs_seconds`](https://dev.mysql.com/doc/mysql-replication-excerpt/8.0/en/replication-options-binary-log.html#sysvar_binlog_expire_logs_seconds)
system variable. We recommend using the default value for this configuration in
order to not compromise Materialize's ability to resume replication in case of
failures or restarts.

In some MySQL managed services, binlog expiration can be overridden by a
service-specific configuration parameter. It's important that you double-check
if such a configuration exists, and ensure it's set to the maximum interval
available.

As an example, [Amazon RDS for MySQL](/ingest-data/mysql/amazon-rds/) has its
own configuration parameter for binlog retention ([`binlog retention hours`](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/mysql-stored-proc-configuring.html#mysql_rds_set_configuration-usage-notes.binlog-retention-hours))
that overrides `binlog_expire_logs_seconds` and is set to `NULL` by default.

### Monitoring source progress

By default, MySQL sources expose progress metadata as a subsource that you can
use to monitor source **ingestion progress**. The name of the progress subsource
can be specified when creating a source using the `EXPOSE PROGRESS AS` clause;
otherwise, it will be named `<src_name>_progress`.

The following metadata is available for each source as a progress subsource:

| Field             | Type                                   | Details                                                                                          |
| ----------------- | -------------------------------------- | ------------------------------------------------------------------------------------------------ |
| `source_id_lower` | [`uuid`](/sql/types/uuid/)             | The lower-bound GTID `source_id` of the GTIDs covered by this range.                             |
| `source_id_upper` | [`uuid`](/sql/types/uuid/)             | The upper-bound GTID `source_id` of the GTIDs covered by this range.                             |
| `transaction_id`  | [`uint8`](/sql/types/uint/#uint8-info) | The `transaction_id` of the next GTID possible from the GTID `source_id`s covered by this range. |

And can be queried using:

```mzsql
SELECT transaction_id
FROM <src_name>_progress;
```

Progress metadata is represented as a [GTID set](https://dev.mysql.com/doc/refman/8.0/en/replication-gtids-concepts.html)
of future possible GTIDs, which is similar to the
[`gtid_executed`](https://dev.mysql.com/doc/refman/8.0/en/replication-options-gtids.html#sysvar_gtid_executed)
system variable on a MySQL replica. The reported `transaction_id` should
increase as Materialize consumes **new** binlog records from the upstream MySQL
database. For more information, see [Troubleshooting](/ops/troubleshooting/).

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

## Source failure states and recovery

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

## Example

> **Important:** Before creating a MySQL source, you must enable [GTID-based binary log (binlog)
> replication](#change-data-capture), including setting
> [`binlog_row_metadata=FULL`](#change-data-capture) to use the new syntax.

### Prerequisites

To create a source from MySQL(8.0.1+), you must first:
- **Configure upstream MySQL instance**
  - Enable [GTID-based binary log(binlog)
    replication](#change-data-capture). You **must** set
    [`binlog_row_metadata=FULL`](#change-data-capture) to use the new
    `CREATE SOURCE` syntax.
  - Create a replication user and password for Materialize to use to
    connect.
- **Configure network security**
  - Ensure Materialize can connect to your MySQL instance.
- **Create a connection to MySQL in Materialize**
  - The [connection setup](/sql/create-connection/#mysql) depends on the
    network security configuration.

For details, see the [MySQL integration
guides](/ingest-data/mysql/#integration-guides).

### Create a source

Once you have configured the upstream MySQL, network security, and created
the [connection to MySQL](/sql/create-connection/#mysql), you can create
the source. In this example, assume the connection you created is named
`mysql_connection`.
```mzsql
CREATE SOURCE mysql_source
FROM MYSQL CONNECTION mysql_connection;

```

After a source is created, you can [create a table from the
source](/sql/create-table/), referencing specific upstream table(s). Use a
[DDL transaction block](/sql/begin/#ddl-only-transactions) to create
multiple tables from the same source.
```mzsql
BEGIN;
CREATE TABLE items
FROM SOURCE mysql_source (REFERENCE mydb.items);

CREATE TABLE orders
FROM SOURCE mysql_source (REFERENCE mydb.orders);
COMMIT;

```

## Related pages

- [`CREATE TABLE`](/sql/create-table/)
- [`CREATE SECRET`](/sql/create-secret)
- [`CREATE CONNECTION`](/sql/create-connection)
- [`CREATE SOURCE`](../)
- [MySQL integration guides](/ingest-data/mysql/#integration-guides)
