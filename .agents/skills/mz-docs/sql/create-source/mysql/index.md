# CREATE SOURCE: MySQL (Legacy syntax)
Connecting Materialize to a MySQL database for Change Data Capture (CDC).
> **Disambiguation:** This page reflects the legacy syntax, which requires downtime to handle upstream DDL changes. For the new syntax which can handle adding or dropping columns to the upstream tables without downtime, see the [new reference page](/sql/create-source/mysql-v2).

Creates a new source from MySQL. Materialize supports creating sources from
MySQL (8.0.1+).

To connect to a MySQL database, you first need to update its configuration to
enable [GTID-based binary log (binlog) replication](#change-data-capture), and
then [create a connection](#creating-a-connection) in Materialize that specifies
access and authentication parameters.

> **Note:** Connections using AWS PrivateLink is for Materialize Cloud only.

## Syntax

> **Note:** Although `schema` and `database` are [synonyms in MySQL](https://dev.mysql.com/doc/refman/8.0/en/glossary.html#glos_schema),
> the MySQL source documentation and syntax **standardize on `schema`** as the
> preferred keyword.

```mzsql
CREATE SOURCE [IF NOT EXISTS] <src_name>
[IN CLUSTER <cluster_name>]
FROM MYSQL CONNECTION <connection_name> [
  (
    [TEXT COLUMNS ( <col1> [, ...] ) ]
    [, EXCLUDE COLUMNS ( <col1> [, ...] ) ]
  )
]
<FOR ALL TABLES | FOR SCHEMAS ( <schema1> [, ...] ) | FOR TABLES ( <table1> [AS <subsrc_name>] [, ...] )>
[EXPOSE PROGRESS AS <progress_subsource_name>]
[WITH ( <with_option> [, ...] )]

```

| Syntax element | Description |
| --- | --- |
| `<src_name>` | The name for the source.  |
| **IF NOT EXISTS** | Optional. If specified, do not throw an error if a source with the same name already exists. Instead, issue a notice and skip the source creation.  |
| **IN CLUSTER** `<cluster_name>` | Optional. The [cluster](/sql/create-cluster) to maintain this source.  |
| **CONNECTION** `<connection_name>` | The name of the MySQL connection to use in the source. For details on creating connections, check the [`CREATE CONNECTION`](/sql/create-connection/#mysql) documentation page.  |
| **TEXT COLUMNS** ( `<col1>` [, ...] ) | Optional. Decode data as `text` for specific columns that contain MySQL types that are [unsupported in Materialize](#supported-types).  |
| **EXCLUDE COLUMNS** ( `<col1>` [, ...] ) | Optional. Exclude specific columns that cannot be decoded or should not be included in the subsources created in Materialize.  |
| **FOR** `<table_schema_specification>` | Specifies which tables to create subsources for. The following `<table_schema_specification>`s are supported:  \| Option \| Description \| \|--------\|-------------\| \| `ALL TABLES` \| Create subsources for all tables in all schemas upstream. The [`mysql` system schema](https://dev.mysql.com/doc/refman/8.3/en/system-schema.html) is ignored. \| \| `SCHEMAS ( <schema1> [, ...] )` \| Create subsources for specific schemas upstream. \| \| `TABLES ( <table1> [AS <subsrc_name>] [, ...] )` \| Create subsources for specific tables upstream. Requires fully-qualified table names (`<schema1>.<table1>`). \|  |
| **EXPOSE PROGRESS AS** `<progress_subsource_name>` | Optional. The name of the progress collection for the source. If this is not specified, the progress collection will be named `<src_name>_progress`. For more information, see [Monitoring source progress](#monitoring-source-progress).  |
| **WITH** (`<with_option>` [, ...]) | Optional. The following `<with_option>`s are supported:  \| Option \| Description \| \|--------\|-------------\| \| `RETAIN HISTORY FOR <retention_period>` \| ***Private preview.** This option has known performance or stability issues and is under active development.* Duration for which Materialize retains historical data, which is useful to implement [durable subscriptions](/transform-data/patterns/durable-subscriptions/#history-retention-period). Accepts positive [interval](/sql/types/interval/) values (e.g. `'1hr'`). Default: `1s`. \| \| `TIMESTAMP INTERVAL [=] <interval>` \| The interval at which timestamps are assigned to data read from this source. Accepts positive [interval](/sql/types/interval/) values (e.g. `'500ms'`, `'1s'`). The value must be between the system parameters `min_timestamp_interval` and `max_timestamp_interval`. Default: the value of the `default_timestamp_interval` system parameter (`1s`). The interval can also be changed after creation with [`ALTER SOURCE`](/sql/alter-source/). \|  |

### `CONNECTION` options

| Field             | Value                           | Description                                                                                                                  |
| ----------------- | ------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `EXCLUDE COLUMNS` | A list of fully-qualified names | Exclude specific columns that cannot be decoded or should not be included in the subsources created in Materialize.          |
| `TEXT COLUMNS`    | A list of fully-qualified names | Decode data as `text` for specific columns that contain MySQL types that are [unsupported in Materialize](#supported-types). |

## Features

### Change data capture

> **Note:** For step-by-step instructions on enabling GTID-based binlog replication for your
> MySQL service, see the integration guides:
> [Amazon RDS](/ingest-data/mysql/amazon-rds/),
> [Amazon Aurora](/ingest-data/mysql/amazon-aurora/),
> [Azure DB](/ingest-data/mysql/azure-db/),
> [Google Cloud SQL](/ingest-data/mysql/google-cloud-sql/),
> [Self-hosted](/ingest-data/mysql/self-hosted/).

The source uses MySQL's binlog replication protocol to **continually ingest
changes** resulting from `INSERT`, `UPDATE` and `DELETE` operations in the
upstream database. This process is known as _change data capture_.

The replication method used is based on [global transaction identifiers (GTIDs)](https://dev.mysql.com/doc/refman/8.0/en/replication-gtids.html),
and guarantees **transactional consistency** — any operation inside a MySQL
transaction is assigned the same timestamp in Materialize, which means that the
source will never show partial results based on partially replicated
transactions.

Before creating a source in Materialize, you **must** configure the upstream
MySQL database for GTID-based binlog replication. Ensure the upstream MySQL
database has been configured for GTID-based binlog replication:

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

If you're running MySQL using a managed service, additional configuration
changes might be required. For step-by-step instructions on enabling GTID-based
binlog replication for your MySQL service, see the integration guides.

#### Binlog retention

> **Warning:** If Materialize tries to resume replication and finds GTID gaps due to missing
> binlog files, the source enters an errored state and you have to drop and
> recreate it.

By default, MySQL retains binlog files for **30 days** (i.e., 2592000 seconds)
before automatically removing them. This is configurable via the
[`binlog_expire_logs_seconds`](https://dev.mysql.com/doc/mysql-replication-excerpt/8.0/en/replication-options-binary-log.html#sysvar_binlog_expire_logs_seconds)
system variable. We recommend using the default value for this configuration in
order to not compromise Materialize's ability to resume replication in case of
failures or restarts.

In some MySQL managed services, binlog expiration can be overriden by a
service-specific configuration parameter. It's important that you double-check
if such a configuration exists, and ensure it's set to the maximum interval
available.

As an example, [Amazon RDS for MySQL](/ingest-data/mysql/amazon-rds/) has its
own configuration parameter for binlog retention ([`binlog retention hours`](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/mysql-stored-proc-configuring.html#mysql_rds_set_configuration-usage-notes.binlog-retention-hours))
that overrides `binlog_expire_logs_seconds` and is set to `NULL` by default.

#### Creating a source

Materialize ingests the raw replication stream data for all (or a specific set
of) tables in your upstream MySQL database.

```mzsql
CREATE SOURCE mz_source
  FROM MYSQL CONNECTION mysql_connection
  FOR ALL TABLES;
```

When you define a source, Materialize will automatically:

1. Create a **subsource** for each original table upstream, and perform an
   initial, snapshot-based sync of the tables before it starts ingesting change
   events.

    ```mzsql
    SHOW SOURCES;
    ```

    ```nofmt
             name         |   type    |  cluster  |
    ----------------------+-----------+------------
     mz_source            | mysql     |
     mz_source_progress   | progress  |
     table_1              | subsource |
     table_2              | subsource |
    ```

1. Incrementally update any materialized or indexed views that depend on the
   source as change events stream in, as a result of `INSERT`, `UPDATE` and
   `DELETE` operations in the upstream MySQL database.

##### MySQL schemas

`CREATE SOURCE` will attempt to create each upstream table in the same schema as
the source. This may lead to naming collisions if, for example, you are
replicating `schema1.table_1` and `schema2.table_1`. Use the `FOR TABLES`
clause to provide aliases for each upstream table, in such cases, or to specify
an alternative destination schema in Materialize.

```mzsql
CREATE SOURCE mz_source
  FROM MYSQL CONNECTION mysql_connection
  FOR TABLES (schema1.table_1 AS s1_table_1, schema2.table_1 AS s2_table_1);
```

### Monitoring source progress

[//]: # "TODO(morsapaes) Replace this section with guidance using the new
progress metrics in mz_source_statistics + console monitoring, when available
(also for PostgreSQL)."

By default, MySQL sources expose progress metadata as a subsource that you
can use to monitor source **ingestion progress**. The name of the progress
subsource can be specified when creating a source using the `EXPOSE PROGRESS
AS` clause; otherwise, it will be named `<src_name>_progress`.

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
of future possible GTIDs, which is similar to the [`gtid_executed`](https://dev.mysql.com/doc/refman/8.0/en/replication-options-gtids.html#sysvar_gtid_executed)
system variable on a MySQL replica. The reported `transaction_id` should
increase as Materialize consumes **new** binlog records from the upstream MySQL
database. For more details on monitoring source ingestion progress and
debugging related issues, see [Troubleshooting](/ops/troubleshooting/).

## Known limitations

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

### Modifying an existing source

When you add a new subsource to an existing source ([`ALTER SOURCE ... ADD
SUBSOURCE ...`](/sql/alter-source/)), Materialize starts the snapshotting
process for the new subsource. During this snapshotting, the data ingestion for
the existing subsources for the same source is temporarily blocked. As such, if
possible, you can resize the cluster to speed up the snapshotting process and
once the process finishes, resize the cluster for steady-state.

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

## Examples

> **Important:** Before creating a MySQL source, you must enable GTID-based binlog replication in the
> upstream database. For step-by-step instructions, see the integration guide for
> your MySQL service: [Amazon RDS](/ingest-data/mysql/amazon-rds/),
> [Amazon Aurora](/ingest-data/mysql/amazon-aurora/),
> [Azure DB](/ingest-data/mysql/azure-db/),
> [Google Cloud SQL](/ingest-data/mysql/google-cloud-sql/),
> [Self-hosted](/ingest-data/mysql/self-hosted/).

### Creating a connection

A connection describes how to connect and authenticate to an external system you
want Materialize to read data from.

Once created, a connection is **reusable** across multiple `CREATE SOURCE`
statements. For more details on creating connections, check the
[`CREATE CONNECTION`](/sql/create-connection/#mysql) documentation page.

```mzsql
CREATE SECRET mysqlpass AS '<MYSQL_PASSWORD>';

CREATE CONNECTION mysql_connection TO MYSQL (
    HOST 'instance.foo000.us-west-1.rds.amazonaws.com',
    PORT 3306,
    USER 'materialize',
    PASSWORD SECRET mysqlpass
);
```

If your MySQL server is not exposed to the public internet, you can [tunnel the
connection](/sql/create-connection/#network-security-connections) through an AWS
PrivateLink service (Materialize Cloud) or an SSH bastion host SSH bastion host.

**AWS PrivateLink (Materialize Cloud):**

> **Note:** Connections using AWS PrivateLink is for Materialize Cloud only.

```mzsql
CREATE CONNECTION privatelink_svc TO AWS PRIVATELINK (
   SERVICE NAME 'com.amazonaws.vpce.us-east-1.vpce-svc-0e123abc123198abc',
   AVAILABILITY ZONES ('use1-az1', 'use1-az4')
);

CREATE CONNECTION mysql_connection TO MYSQL (
    HOST 'instance.foo000.us-west-1.rds.amazonaws.com',
    PORT 3306,
    USER 'root',
    PASSWORD SECRET mysqlpass,
    AWS PRIVATELINK privatelink_svc
);
```

For step-by-step instructions on creating AWS PrivateLink connections and
configuring an AWS PrivateLink service to accept connections from Materialize,
check [this guide](/ops/network-security/privatelink/).

**SSH tunnel:**

```mzsql
CREATE CONNECTION ssh_connection TO SSH TUNNEL (
    HOST 'bastion-host',
    PORT 22,
    USER 'materialize'
);
```

```mzsql
CREATE CONNECTION mysql_connection TO MYSQL (
    HOST 'instance.foo000.us-west-1.rds.amazonaws.com',
    SSH TUNNEL ssh_connection
);
```

For step-by-step instructions on creating SSH tunnel connections and configuring
an SSH bastion server to accept connections from Materialize, check
[this guide](/ops/network-security/ssh-tunnel/).

### Creating a source {#create-source-example}

_Create subsources for all tables in MySQL_

```mzsql
CREATE SOURCE mz_source
    FROM MYSQL CONNECTION mysql_connection
    FOR ALL TABLES;
```

_Create subsources for all tables from specific schemas in MySQL_

```mzsql
CREATE SOURCE mz_source
  FROM MYSQL CONNECTION mysql_connection
  FOR SCHEMAS (mydb, project);
```

_Create subsources for specific tables in MySQL_

```mzsql
CREATE SOURCE mz_source
  FROM MYSQL CONNECTION mysql_connection
  FOR TABLES (mydb.table_1, mydb.table_2 AS alias_table_2);
```

#### Handling unsupported types

If you're replicating tables that use [data types unsupported](#supported-types)
by Materialize, use the `TEXT COLUMNS` option to decode data as `text` for the
affected columns. `TEXT COLUMNS` should also be used for columns that contain
MySQL zero-value `DATE`, `DATETIME`, or `TIMESTAMP` data.

This option expects the upstream fully-qualified names of the
replicated table and column (i.e. as defined in your MySQL database).

```mzsql
CREATE SOURCE mz_source
  FROM MYSQL CONNECTION mysql_connection (
    TEXT COLUMNS (mydb.table_1.column_of_unsupported_type)
  )
  FOR ALL TABLES;
```

#### Excluding columns

MySQL doesn't provide a way to filter out columns from the replication stream.
To exclude specific upstream columns from being ingested, use the `EXCLUDE
COLUMNS` option.

```mzsql
CREATE SOURCE mz_source
  FROM MYSQL CONNECTION mysql_connection (
    EXCLUDE COLUMNS (mydb.table_1.column_to_ignore)
  )
  FOR ALL TABLES;
```

### Handling errors and schema changes

> **Note:** Work to more smoothly support ddl changes to upstream tables is currently in
> progress. The work introduces the ability to re-ingest the same upstream table
> under a new schema and switch over without downtime.

To handle upstream [schema changes](#handling-upstream-operations) or errored subsources, use
the [`DROP SOURCE`](/sql/alter-source/#context) syntax to drop the affected
subsource, and then [`ALTER SOURCE...ADD SUBSOURCE`](/sql/alter-source/) to add
the subsource back to the source.

```mzsql
-- List all subsources in mz_source
SHOW SUBSOURCES ON mz_source;

-- Get rid of an outdated or errored subsource
DROP SOURCE table_1;

-- Start ingesting the table with the updated schema or fix
ALTER SOURCE mz_source ADD SUBSOURCE table_1;
```

## Related pages

- [`CREATE SECRET`](/sql/create-secret)
- [`CREATE CONNECTION`](/sql/create-connection)
- [`CREATE SOURCE`](../)
- MySQL integration guides:
    - [Amazon RDS](/ingest-data/mysql/amazon-rds/)
    - [Amazon Aurora](/ingest-data/mysql/amazon-aurora/)
    - [Azure DB](/ingest-data/mysql/azure-db/)
    - [Google Cloud SQL](/ingest-data/mysql/google-cloud-sql/)
    - [Self-hosted](/ingest-data/mysql/self-hosted/)
