# SQL Server

Connecting Materialize to a SQL Server database for Change Data Capture (CDC).

## Change Data Capture (CDC)

Materialize supports SQL Server as a real-time data source. The [SQL Server source](/sql/create-source/sql-server/)
uses SQL Server's change data capture feature to **continually ingest changes**
resulting from CRUD operations in the upstream database. The native support for
SQL Server Change Data Capture (CDC) in Materialize gives you the following benefits:

* **No additional infrastructure:** Ingest SQL Server change data into Materialize in
    real-time with no architectural changes or additional operational overhead.
    In particular, you **do not need to deploy Kafka and Debezium** for SQL Server
    CDC.

* **Transactional consistency:** The SQL Server source ensures that transactions in
    the upstream SQL Server database are respected downstream. Materialize will
    **never show partial results** based on partially replicated transactions.

* **Incrementally updated materialized views:** Incrementally updated Materialized
    views are considerably **limited in SQL Server**, so you can use Materialize as
    a read-replica to build views on top of your SQL Server data that are
    efficiently maintained and always up-to-date.

## Supported versions

Materialize supports replicating data from SQL Server 2016 or higher with Change
Data Capture (CDC) support.

## Integration Guides

- [Azure SQL Database](/ingest-data/sql-server/azure-db/)
- [Self-hosted SQL Server](/ingest-data/sql-server/self-hosted/)

## Considerations

### Supported types

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

### Timestamp Rounding

The `time`, `datetime2`, and `datetimeoffset` types in SQL Server have a default
scale of 7 decimal places, or in other words a accuracy of 100 nanoseconds. But
the corresponding types in Materialize only support a scale of 6 decimal places.
If a column in SQL Server has a higher scale than what Materialize can support, it
will be rounded up to the largest scale possible.

```
-- In SQL Server
CREATE TABLE my_timestamps (a datetime2(7));
INSERT INTO my_timestamps VALUES
  ('2000-12-31 23:59:59.99999'),
  ('2000-12-31 23:59:59.999999'),
  ('2000-12-31 23:59:59.9999999');

-- Replicated into Materialize
SELECT * FROM my_timestamps;
'2000-12-31 23:59:59.999990'
'2000-12-31 23:59:59.999999'
'2001-01-01 00:00:00'
```

### Snapshot latency for inactive databases

When a new Source is created, Materialize performs a snapshotting operation to sync
the data. However, for a new SQL Server source, if none of the replicating tables
are receiving write queries, snapshotting may take up to an additional 5 minutes
to complete. The 5 minute interval is due to a hardcoded interval in the SQL Server
Change Data Capture (CDC) implementation which only notifies CDC consumers every
5 minutes when no changes are made to replicating tables.

See [Monitoring freshness status](/ingest-data/monitoring-data-ingestion/#monitoring-hydrationdata-freshness-status)

### Capture Instance Selection

When a new source is created, Materialize selects a capture instance for each
table. SQL Server permits at most two capture instances per table, which are
listed in the
[`sys.cdc_change_tables`](https://learn.microsoft.com/en-us/sql/relational-databases/system-tables/cdc-change-tables-transact-sql)
system table. For each table, Materialize picks the capture instance with the
most recent `create_date`.

If two capture instances for a table share the same timestamp (unlikely given the millisecond resolution), Materialize selects the `capture_instance` with the lexicographically larger name.

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

---

## Guide: Handle upstream schema changes with zero downtime

> **Public Preview:** This feature is in public preview.

> **Note:** Changing column types is currently unsupported.

Materialize allows you to handle certain types of upstream
table schema changes seamlessly, specifically:

- Adding a column in the upstream database.
- Dropping a column in the upstream database.

This guide walks you through how to handle these changes without any downtime in Materialize.

## Prerequisites

Some familiarity with Materialize. If you've never used Materialize before,
start with our [guide to getting started](/get-started/quickstart/).

### Set up a SQL Server database

For this guide, setup a SQL Server 2016+ database. In your SQL Server, create a
table `t1` and populate:

```sql
CREATE TABLE t1 (
    a INT
);

INSERT INTO t1 (a) VALUES
    (10);
GO -- The GO terminator may be unsupported or unnecessary for your client.
```

### Configure your SQL Server Database

Configure your SQL Server database using the [configuration instructions for self hosted SQL Server.](/ingest-data/sql-server/self-hosted/#a-configure-sql-server)

### Connect your source database to Materialize

Create a connection to your SQL Server database using the [`CREATE CONNECTION` syntax.](/sql/create-connection/)

## Create a source using the new syntax

In Materialize, create a source using the [`CREATE SOURCE`
syntax](/sql/create-source/sql-server-v2/).

```mzsql
CREATE SOURCE my_source
  FROM SQL SERVER CONNECTION sqlserver_connection;
```

## Create a table from the source
To start ingesting specific tables from your source database, you can create a
table in Materialize. We'll add it into the v1 schema in Materialize.

```mzsql
CREATE SCHEMA v1;

CREATE TABLE v1.t1
    FROM SOURCE my_source(REFERENCE dbo.t1);
```

Once you've created a table from source, the [initial
snapshot](/ingest-data/#snapshotting) of table `v1.t1` will begin.

> **Note:** During the snapshotting, the data ingestion for the existing tables for the same
> source is temporarily blocked. As such, if possible, you can resize the cluster
> to speed up the snapshotting process and once the process finishes, resize the
> cluster for steady-state. You can monitor the snapshot progress on the overview
> page for the source in the Materialize console.

## Create a view on top of the table.

For this guide, add a materialized view `matview` (also in schema `v1`) that
sums column `a` from table `t1`.

```mzsql
CREATE MATERIALIZED VIEW v1.matview AS
    SELECT SUM(a) from v1.t1;
```

## Handle upstream column addition

### A. Add a column in your upstream SQL Server database

In your upstream SQL Server database, add a new column `b` to the table `t1`:

```sql
ALTER TABLE t1
    ADD b BIT NULL;

INSERT INTO t1 (a,b) VALUES
    (20, 1);
GO -- The GO terminator may be unsupported or unnecessary for your client.
```

This operation does not impact the SQL Server CDC output; the SQL Server
continues to publish CDC changes only for column `a`. As such, the addition of a
new column has no immediate effect in Materialize. In Materialize:

- The table `v1.t1` will continue to ingest only column `a`.
- The materialized view `v1.matview` will continue to have access to column `a`
  only.

### B. Enable CDC for your table under a new capture instance in your upstream SQL Server database

In order for Materialize to begin receiving data for this new column, you must
create a new capture instance for your table, explicitly specifing a new
[`@capture_instance`
name](https://learn.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sys-sp-cdc-enable-table-transact-sql?view=sql-server-ver17#----capture_instance).

> **Note:** SQL Server only allows a [maximum of 2 capture
> instances](https://learn.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sys-sp-cdc-enable-table-transact-sql?view=sql-server-ver17#----capture_instance).
> If you already have 2 capture instances, you will have to [disable one of
> them](#disable-unused-capture-instance), possibly resulting in downtime for your
> Materialize source.

```sql
EXEC sys.sp_cdc_enable_table
  @source_schema = 'dbo',
  @source_name = 't1',
  @role_name = 'materialize_role',
  @capture_instance = 'dbo_t1_v2', -- MUST BE SPECIFIED
  @supports_net_changes = 0;
GO -- The GO terminator may be unsupported or unnecessary for your client.
```

The newly created capture instance will include CDC data for column `b`. Now,
when you create a new table `t1` from your source in Materialize (see next
step), Materialize will select the most [recently created capture
instance](/ingest-data/sql-server/#capture-instance-selection) (i.e., the
capture instance with the newly added column `b`).

See also:

- [Capture instance
  selection](/ingest-data/sql-server/#capture-instance-selection)
- [Enable Change-Data-Capture for the
tables](/ingest-data/sql-server/self-hosted/#4-enable-change-data-capture-for-the-tables)

### C. Create a new table from the source in Materialize

To incorporate the new column into Materialize, create a new `v2` schema and
recreate the table in the new schema. When creating the table, Materialize uses
the  most [recently created capture
instance](/ingest-data/sql-server/#capture-instance-selection) (i.e., the
capture instance with the newly added column `b`):

```mzsql
CREATE SCHEMA v2;

CREATE TABLE v2.t1
    FROM SOURCE my_source(REFERENCE dbo.t1);
```

The [snapshotting](/ingest-data/#snapshotting) of table `v2.t1` will begin.
`v2.t1` will include columns `a` and `b`.

> **Note:** During the snapshotting, the data ingestion for the existing tables for the same
> source is temporarily blocked. As such, if possible, you can resize the cluster
> to speed up the snapshotting process and once the process finishes, resize the
> cluster for steady-state. You can monitor the snapshot progress on the overview
> page for the source in the Materialize console.

When the new `v2.t1` table has finished snapshotting, create a new materialized
view `matview` in the new schema.  Since the new `v2.matview` is referencing the
new `v2.t1`, it can reference column `b`:

```mzsql {hl_lines="4"}
CREATE MATERIALIZED VIEW v2.matview AS
    SELECT SUM(a)
    FROM v2.t1
    WHERE b = true;
```

## Handle upstream column drop

### A. Exclude the column in Materialize

To drop a column safely, in Materialize, first, create a new `v3` schema, and
recreate table `t1` in the new schema but exclude the column to drop. In this
example, we'll drop the column `b`.

```mzsql
CREATE SCHEMA v3;
CREATE TABLE v3.t1
    FROM SOURCE my_source(REFERENCE dbo.t1) WITH (EXCLUDE COLUMNS (b));
```

> **Note:** During the snapshotting, the data ingestion for the existing tables for the same
> source is temporarily blocked. As such, if possible, you can resize the cluster
> to speed up the snapshotting process and once the process finishes, resize the
> cluster for steady-state. You can monitor the snapshot progress on the overview
> page for the source in the Materialize console.

### B. Drop a column in your upstream SQL Server database

In your upstream SQL Server database, drop the column `b` from the table `t1`:

```sql
ALTER TABLE t1 DROP COLUMN b;
GO -- The GO terminator may be unsupported or unnecessary for your client.
```

Dropping the column `b` in SQL Server will not affect `v3.t1` (or on `v1.t1`) in
Materialize. However, the drop affects `v2.t1` and `v2.matview` from our earlier
examples. When the user attempts to read from either, Materialize will report an
error that the source table schema has been altered.

## Optional

### Disable unused capture instance

SQL Server only allows a [maximum of 2 capture
instances](https://learn.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sys-sp-cdc-enable-table-transact-sql?view=sql-server-ver17#----capture_instance)
per table.

To find the capture instance(s) for a table:

```sql
SELECT capture_instance
FROM cdc.change_tables
WHERE source_schema = '<schema>'
  AND source_table = '<table>';
```

After you have fully cut over to the new source version for the table, and you
previously [created a new capture instance for your upstream
table](#b-enable-cdc-for-your-table-under-a-new-capture-instance-in-your-upstream-sql-server-database),
you may wish to disable the old capture instance if it is no longer in use.

> **Warning:** Ensure that no other source tables or other applications are using the old
> capture instance; otherwise, they will break.

To disable a capture instance for a table:

```sql
EXEC sys.sp_cdc_disable_table
    @source_schema = '<schema>',
    @source_name = '<source_table_name>',
    @capture_instance = '<old_capture_instance_name>';
```

---

## Ingest data from Azure SQL Database

This page shows you how to stream data from [Azure SQL Database](https://azure.microsoft.com/en-us/products/azure-sql/database)
to Materialize using the [SQL Server source](/sql/create-source/sql-server/).

> **Note:** This guide covers **Azure SQL Database**, the single-database service. For
> **Azure SQL Managed Instance**, which runs a SQL Server Agent and exposes
> `msdb`, follow the [self-hosted SQL Server guide](/ingest-data/sql-server/self-hosted/)
> instead.

> **Tip:** For help getting started with your own data, you can schedule a [free guided
> trial](https://materialize.com/demo/?utm_campaign=General&utm_source=documentation).

## Before you begin

- Make sure Change Data Capture (CDC) is available on your Azure SQL Database.
  CDC has compute requirements and is not supported on lower service tiers. See
  [Azure SQL documentation](https://learn.microsoft.com/en-us/azure/azure-sql/database/change-data-capture-overview?view=azuresql)
  for details on service tiers and CDC configuration.

- Ensure you have access to your database via the [`sqlcmd` client](https://learn.microsoft.com/en-us/sql/tools/sqlcmd/sqlcmd-utility),
  or your preferred SQL client, as a member of `db_owner`.

## A. Configure Azure SQL Database

> **Note:** To configure Azure SQL Database for data ingestion into Materialize, you must
> connect to the database you want to replicate as a member of `db_owner`, which
> can enable CDC and create/manage the user, role, and privileges.

### 1. Create a Materialize user in Azure SQL Database.

Azure SQL Database is a single-database service. Because it does not provide
reusable server logins or access to the master database for granting
server-scoped permissions, create a [contained database user](https://learn.microsoft.com/en-us/sql/relational-databases/security/contained-database-users-making-your-database-portable) directly in the
database you want to replicate.

Connect to the database you want to replicate as a member of `db_owner`, then
create the user (replace `<PASSWORD>` with your own password):

```sql
CREATE USER materialize WITH PASSWORD = '<PASSWORD>';
```

Create a gating role for the capture instances and add the user to it:

```sql
CREATE ROLE materialize_role;
ALTER ROLE materialize_role ADD MEMBER materialize;
```

Grant the privileges Materialize needs:

```sql
-- SELECT on the replicated tables and the CDC change tables.
ALTER ROLE db_datareader ADD MEMBER materialize;

-- Read access to the transaction-state views used to track replication
-- progress, in place of the server-scoped VIEW SERVER STATE used for
-- self-hosted SQL Server.
GRANT VIEW DATABASE STATE TO materialize;
```

> **Note:** Unlike self-hosted SQL Server, no explicit grants are issued on the
> `sys.fn_cdc_*` functions or the `INFORMATION_SCHEMA` views. They are executable
> and readable by default.

### 2. Enable Change-Data-Capture for the database.

Azure SQL Database drives CDC from an internal scheduler, so **no SQL Server
Agent is required**. Enabling CDC requires the database to be on a service tier
that supports it and that you are a member of `db_owner`.

Connect to the database you want to replicate and run:

```sql
EXEC sys.sp_cdc_enable_db;
```

For guidance on enabling Change Data Capture on Azure SQL Database, see the
[Azure documentation](https://learn.microsoft.com/en-us/sql/relational-databases/track-changes/about-change-data-capture-sql-server?view=azuresqldb-current).

### 3. Enable `SNAPSHOT` transaction isolation.

Enable `SNAPSHOT` transaction isolation for the database. Because Azure SQL
Database connections cannot switch databases, use the `CURRENT` keyword to target
the connected database:

```sql
ALTER DATABASE CURRENT SET ALLOW_SNAPSHOT_ISOLATION ON;
```

### 4. Enable Change-Data-Capture for the tables.

Enable Change Data Capture for each table you wish to replicate, gated by the
role you created above (replace `<SCHEMA_NAME>` and `<TABLE_NAME>` with your
schema and table names):

```sql
EXEC sys.sp_cdc_enable_table
  @source_schema = '<SCHEMA_NAME>',
  @source_name = '<TABLE_NAME>',
  @role_name = 'materialize_role',
  @supports_net_changes = 0;
```

## B. (Optional) Configure network security

> **Note:** If you are prototyping and your Azure SQL Database is publicly accessible, **you
> can skip this step**. For production scenarios, we recommend configuring one of
> the network security options below.

There are various ways to configure your database's network to allow Materialize
to connect:

- **Allow Materialize IPs:** If your database is publicly accessible, you can
    configure your database's firewall to allow connections from a set of
    static Materialize IP addresses.

- **Use an SSH tunnel:** If your database is running in a private network, you
    can use an SSH tunnel to connect Materialize to the database.

Select the option that works best for you.

**Allow Materialize IPs:**

1. In the [SQL Shell](/console/), or your preferred SQL
   client connected to Materialize, find the static egress IP addresses for the
   Materialize region you are running in:

    ```mzsql
    SELECT * FROM mz_egress_ips;
    ```

1. Update your [Azure SQL Database firewall rules](https://learn.microsoft.com/en-us/azure/azure-sql/database/firewall-configure?view=azuresql)
   to allow traffic from each IP address from the previous step.

**Use an SSH tunnel:**

This assumes your Azure SQL Database is already reachable over a private IP in a
virtual network via an [Azure Private Endpoint](https://learn.microsoft.com/en-us/azure/azure-sql/database/private-endpoint-overview?view=azuresql),
with the `privatelink.database.windows.net` DNS zone integrated so
`<server>.database.windows.net` resolves to the private IP.

To create the SSH tunnel, you launch an instance to serve as an SSH bastion host
in that network and configure the bastion host to allow traffic from Materialize.
The bastion forwards traffic to the database's private endpoint.

1. [Launch a Linux VM with a static public IP address](https://learn.microsoft.com/en-us/azure/virtual-machines/linux/quick-create-portal)
to serve as your SSH bastion host.

    - Make sure the VM is publicly accessible and in the same virtual network as
      the private endpoint (or a peered network).
    - Add a key pair and note the username. You'll use this username when
      connecting Materialize to your bastion host.
    - Make sure the VM has a static public IP address. You'll use this IP
      address when connecting Materialize to your bastion host.

1. Configure the SSH bastion host to allow traffic from Materialize.

    1. In the [SQL Shell](/console/), or your preferred
       SQL client connected to Materialize, get the static egress IP addresses for
       the Materialize region you are running in:

       ```mzsql
       SELECT * FROM mz_egress_ips;
       ```

    1. Update your SSH bastion host's [firewall rules](https://learn.microsoft.com/en-us/azure/virtual-network/tutorial-filter-network-traffic?toc=%2Fazure%2Fvirtual-machines%2Ftoc.json)
    to allow SSH traffic from each IP address from the previous step.

1. Set the server's [connection policy](https://learn.microsoft.com/en-us/azure/azure-sql/database/connectivity-architecture?view=azuresql#connection-policy)
   to **Proxy**:

    ```sh
    az sql server conn-policy update \
      --resource-group <resource-group> \
      --server <server-name> \
      --connection-type Proxy
    ```

    With the `Redirect` policy, the gateway tells the client to reconnect
    directly to the backend node on a high port, which bypasses the single port
    the SSH tunnel forwards. `Proxy` keeps all traffic on the gateway at port
    1433, which is the port the tunnel forwards.

    If the connection policy is left as `Redirect`, creating the source or
    validating the connection fails with an error like:

    ```text
    Server requested a connection to an alternative address:
    `<backend-node>.worker.database.windows.net:<high-port>`
    ```

## C. Ingest data in Materialize

### 1. (Optional) Create a cluster

> **Note:** If you are prototyping and already have a cluster to host your SQL Server
> source (e.g. `quickstart`), **you can skip this step**. For production
> scenarios, we recommend separating your workloads into multiple clusters for
> [resource isolation](/sql/create-cluster/#resource-isolation).

In Materialize, a [cluster](/concepts/clusters/) is an isolated
environment, similar to a virtual warehouse in Snowflake. When you create a
cluster, you choose the size of its compute resource allocation based on the
work you need the cluster to do, whether ingesting data from a source,
computing always-up-to-date query results, serving results to clients, or a
combination.

In this case, you'll create a dedicated cluster for ingesting source data from
your SQL Server database.

1. In the [SQL Shell](/console/), or your preferred SQL
   client connected to Materialize, use the [`CREATE CLUSTER`](/sql/create-cluster/)
   command to create the new cluster:

    ```mzsql
    CREATE CLUSTER ingest_sqlserver (SIZE = '200cc');

    SET CLUSTER = ingest_sqlserver;
    ```

    A cluster of [size](/sql/create-cluster/#available-sizes) `200cc` should be enough to
    process the initial snapshot of the tables in your SQL Server database. For
    very large snapshots, consider using a larger size to speed up processing.
    Once the snapshot is finished, you can readjust the size of the cluster to fit
    the volume of changes being replicated from your upstream SQL Server database.

### 2. Create a connection

Once you have configured your network, create a connection in Materialize per
your networking configuration. Azure SQL Database **requires an encrypted
connection**, so the SQL Server connection must specify `SSL MODE 'required'`.

**Allow Materialize IPs:**

1. In the [SQL Shell](/console/), or your preferred SQL
   client connected to Materialize, use the [`CREATE SECRET`](/sql/create-secret/)
   command to securely store the password for the SQL Server role you'll use to
   replicate data into Materialize:

    ```mzsql
    CREATE SECRET sqlserver_pass AS '<PASSWORD>';
    ```

1. Use the [`CREATE CONNECTION`](/sql/create-connection/) command to create a
   connection object with access and authentication details for Materialize to
   use:

    ```mzsql
    CREATE CONNECTION sqlserver_connection TO SQL SERVER (
        HOST <host>,
        PORT 1433,
        USER 'materialize',
        PASSWORD SECRET sqlserver_pass,
        DATABASE <database>,
        SSL MODE 'required'
    );
    ```

    - Replace `<host>` with your SQL Server endpoint, and `<database>` with the database you'd like to connect to.

**Use an SSH tunnel:**

1. In the [SQL Shell](/console/), or your preferred SQL
   client connected to Materialize, use the [`CREATE CONNECTION`](/sql/create-connection/#ssh-tunnel)
   command to create an SSH tunnel connection:

    ```mzsql
    CREATE CONNECTION ssh_connection TO SSH TUNNEL (
        HOST '<SSH_BASTION_HOST>',
        PORT <SSH_BASTION_PORT>,
        USER '<SSH_BASTION_USER>'
    );
    ```

    - Replace `<SSH_BASTION_HOST>` and `<SSH_BASTION_PORT>` with the public IP
      address and port of the SSH bastion host you created
      [earlier](#b-optional-configure-network-security).

    - Replace `<SSH_BASTION_USER>` with the username for the key pair you created
      for your SSH bastion host.

1. Get Materialize's public keys for the SSH tunnel connection:

    ```mzsql
    SELECT * FROM mz_ssh_tunnel_connections;
    ```

1. Log in to your SSH bastion host and add Materialize's public keys to the
   `authorized_keys` file, for example:

    ```sh
    # Command for Linux
    echo "ssh-ed25519 AAAA...76RH materialize" >> ~/.ssh/authorized_keys
    echo "ssh-ed25519 AAAA...hLYV materialize" >> ~/.ssh/authorized_keys
    ```

1. Back in the SQL client connected to Materialize, validate the SSH tunnel
   connection you created using the [`VALIDATE CONNECTION`](/sql/validate-connection)
   command:

    ```mzsql
    VALIDATE CONNECTION ssh_connection;
    ```

    If no validation error is returned, move to the next step.

1. Use the [`CREATE SECRET`](/sql/create-secret/) command to securely store the
   password for the `materialize` user
   [you created](#1-create-a-materialize-user-in-azure-sql-database):

    ```mzsql
    CREATE SECRET sqlserver_pass AS '<PASSWORD>';
    ```

1. Use the [`CREATE CONNECTION`](/sql/create-connection/) command to create the
   SQL Server connection, routed through the SSH tunnel. Azure SQL Database
   requires an encrypted connection, so include `SSL MODE 'required'`:

    ```mzsql
    CREATE CONNECTION sqlserver_connection TO SQL SERVER (
        HOST '<host>',
        PORT 1433,
        USER 'materialize',
        PASSWORD SECRET sqlserver_pass,
        DATABASE '<database>',
        SSL MODE 'required',
        SSH TUNNEL ssh_connection
    );
    ```

    - Replace `<host>` with your Azure SQL Database endpoint, and `<database>`
      with the database you'd like to connect to.

### 3. Start ingesting data

> **Note:** For a new SQL Server source, if none of the replicating tables
> are receiving write queries, snapshotting may take up to an additional 5 minutes
> to complete. For details, see [snapshot latency for inactive databases](#snapshot-latency-for-inactive-databases)

Use the [`CREATE SOURCE`](/sql/create-source/) command to connect
Materialize to your SQL Server instance and start ingesting data:
```mzsql
CREATE SOURCE mz_source
  FROM SQL SERVER CONNECTION sqlserver_connection
  FOR ALL TABLES;

```

- By default, the source will be created in the active cluster; to use a
  different cluster, use the `IN CLUSTER` clause.
- To ingest data from specific tables use the `FOR TABLES
  (<table1>, <table2>)` options instead of `FOR ALL TABLES`.
- To handle unsupported data types, use the `TEXT COLUMNS` or `EXCLUDE
  COLUMNS` options. Check out the [reference
  documentation](#supported-types) for guidance.

After source creation, refer to [schema changes
considerations](#handling-upstream-operations) for information on handling upstream schema changes.

### 4. Right-size the cluster

After the snapshotting phase, Materialize starts ingesting change events from
the SQL Server replication stream. For this work, Materialize generally
performs well with a `100cc` replica, so you can resize the cluster
accordingly.

1. Still in a SQL client connected to Materialize, use the [`ALTER CLUSTER`](/sql/alter-cluster/)
   command to downsize the cluster to `100cc`:

    ```mzsql
    ALTER CLUSTER ingest_sqlserver SET (SIZE '100cc');
    ```

    Behind the scenes, this command adds a new `100cc` replica and removes the
    `200cc` replica.

1. Use the [`SHOW CLUSTER REPLICAS`](/sql/show-cluster-replicas/) command to
   check the status of the new replica:

    ```mzsql
    SHOW CLUSTER REPLICAS WHERE cluster = 'ingest_sqlserver';
    ```
    <p></p>

    ```nofmt
         cluster       | replica |  size  | ready
    -------------------+---------+--------+-------
     ingest_sqlserver  | r1      | 100cc  | t
    (1 row)
    ```

## D. Explore your data

With Materialize ingesting your SQL Server data into durable storage, you can
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

### Supported types

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

### Timestamp Rounding

The `time`, `datetime2`, and `datetimeoffset` types in SQL Server have a default
scale of 7 decimal places, or in other words a accuracy of 100 nanoseconds. But
the corresponding types in Materialize only support a scale of 6 decimal places.
If a column in SQL Server has a higher scale than what Materialize can support, it
will be rounded up to the largest scale possible.

```
-- In SQL Server
CREATE TABLE my_timestamps (a datetime2(7));
INSERT INTO my_timestamps VALUES
  ('2000-12-31 23:59:59.99999'),
  ('2000-12-31 23:59:59.999999'),
  ('2000-12-31 23:59:59.9999999');

-- Replicated into Materialize
SELECT * FROM my_timestamps;
'2000-12-31 23:59:59.999990'
'2000-12-31 23:59:59.999999'
'2001-01-01 00:00:00'
```

### Snapshot latency for inactive databases

When a new Source is created, Materialize performs a snapshotting operation to sync
the data. However, for a new SQL Server source, if none of the replicating tables
are receiving write queries, snapshotting may take up to an additional 5 minutes
to complete. The 5 minute interval is due to a hardcoded interval in the SQL Server
Change Data Capture (CDC) implementation which only notifies CDC consumers every
5 minutes when no changes are made to replicating tables.

See [Monitoring freshness status](/ingest-data/monitoring-data-ingestion/#monitoring-hydrationdata-freshness-status)

### Capture Instance Selection

When a new source is created, Materialize selects a capture instance for each
table. SQL Server permits at most two capture instances per table, which are
listed in the
[`sys.cdc_change_tables`](https://learn.microsoft.com/en-us/sql/relational-databases/system-tables/cdc-change-tables-transact-sql)
system table. For each table, Materialize picks the capture instance with the
most recent `create_date`.

If two capture instances for a table share the same timestamp (unlikely given the millisecond resolution), Materialize selects the `capture_instance` with the lexicographically larger name.

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

---

## Ingest data from self-hosted SQL Server

This page shows you how to stream data from a self-hosted SQL Server database
to Materialize using the [SQL Server Source](/sql/create-source/sql-server/).

> **Tip:** For help getting started with your own data, you can schedule a [free guided
> trial](https://materialize.com/demo/?utm_campaign=General&utm_source=documentation).

## Before you begin

- Make sure you are running SQL Server 2016 or higher with  Change Data Capture
(CDC) support. Materialize uses [Change Data
Capture](https://learn.microsoft.com/en-us/sql/relational-databases/track-changes/about-change-data-capture-sql-server)
which is not readily available on older versions of SQL Server.

- Ensure you have access to your SQL Server instance via the [`sqlcmd` client](https://learn.microsoft.com/en-us/sql/tools/sqlcmd/sqlcmd-utility),
  or your preferred SQL client.

- Ensure SQL Server Agent is running.
  ```mzsql
  USE msdb;
  SELECT
    servicename,
    status_desc,
    startup_type_desc
  FROM sys.dm_server_services
  WHERE servicename LIKE 'SQL Server Agent%';
  ```

## A. Configure SQL Server

> **Note:** To configure SQL Server for data ingestion into Materialize, you must be a user
> with privileges to enable CDC and create/manage login, users, roles, and
> privileges.

### 1. Create a Materialize user in SQL Server.

Create a user that Materialize will use to connect when ingesting data.

1. In `master`:

   1. Create a login `materialize` (replace `<PASSWORD>` with your own
      password):

      ```sql
      USE master;

      -- Specify additional options per your company's security policy
      CREATE LOGIN materialize WITH PASSWORD = '<PASSWORD>',
      DEFAULT_DATABASE = <DATABASE_NAME>;
      GO -- The GO terminator may be unsupported or unnecessary for your client.
      ```

   1. Create a user `materialize` for the login and role `materialize_role`:

      ```sql
      USE master;
      CREATE USER materialize FOR LOGIN materialize;
      CREATE ROLE materialize_role;
      ALTER ROLE materialize_role ADD MEMBER materialize;
      GO -- The GO terminator may be unsupported or unnecessary for your client.
      ```

   1. Grant permissions to the `materialize_role` to enable discovery of the
      tables to be replicated and monitoring replication progress:

      ```sql
      USE master;

      -- Required for schema discovery for replicated tables.
      GRANT SELECT ON INFORMATION_SCHEMA.KEY_COLUMN_USAGE TO materialize_role;
      GRANT SELECT ON INFORMATION_SCHEMA.TABLE_CONSTRAINTS TO materialize_role;
      GRANT SELECT ON OBJECT::INFORMATION_SCHEMA.TABLE_CONSTRAINTS TO materialize_role;

      -- Allows checking the minimum and maximum Log Sequence Numbers (LSN) for CDC,
      -- required for the Source to be able to track progress.
      GRANT EXECUTE ON sys.fn_cdc_get_min_lsn TO materialize_role;
      GRANT EXECUTE ON sys.fn_cdc_get_max_lsn TO materialize_role;
      GRANT EXECUTE ON sys.fn_cdc_increment_lsn TO materialize_role;

      GRANT VIEW SERVER STATE TO materialize;
      GO -- The GO terminator may be unsupported or unnecessary for your client.
      ```

1. In the database from which which you want to ingest data,

   1. Create a second `materialize` user and a second `materialize_role`.

   1. Add `materialize` user as a member to the `materialize_role` and
   `db_datareader` roles (replace `<DATABASE_NAME>` with your database name).

   ```sql
   USE <DATABASE_NAME>;

   -- Use the same user name and role name as those created in master
   CREATE USER materialize FOR LOGIN materialize;
   CREATE ROLE materialize_role;
   ALTER ROLE materialize_role ADD MEMBER materialize;
   ALTER ROLE db_datareader ADD MEMBER materialize;
   GO -- The GO terminator may be unsupported or unnecessary for your client.
   ```

### 2. Enable Change-Data-Capture for the database.

In SQL Server, for the database from which you want to ingest data, enable
change data capture  (replace `<DATABASE_NAME>` with your database name):

```sql
USE <DATABASE_NAME>;
GO -- The GO terminator may be unsupported or unnecessary for your client.
EXEC sys.sp_cdc_enable_db;
GO -- The GO terminator may be unsupported or unnecessary for your client.
```

For guidance on enabling Change Data Capture, see the [SQL Server documentation](https://learn.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sys-sp-cdc-enable-db-transact-sql).

### 3. Enable `SNAPSHOT` transaction isolation.

Enable `SNAPSHOT` transaction isolation for the database (replace
`<DATABASE_NAME>` with your database name):

```sql
ALTER DATABASE <DATABASE_NAME> SET ALLOW_SNAPSHOT_ISOLATION ON;
GO -- The GO terminator may be unsupported or unnecessary for your client.
```

For guidance on enabling `SNAPSHOT` transaction isolation, see the [SQL Server documentation](https://learn.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sys-sp-cdc-enable-table-transact-sql)

### 4. Enable Change-Data-Capture for the tables.

Enable Change Data Capture for each table you wish to replicate (replace
`<DATABASE_NAME>`, `<SCHEMA_NAME>`, and `<TABLE_NAME>` with the your database,
schema name, and table name):

```sql
USE <DATABASE_NAME>;

EXEC sys.sp_cdc_enable_table
  @source_schema = '<SCHEMA_NAME>',
  @source_name = '<TABLE_NAME>',
  @role_name = 'materialize_role',
  @supports_net_changes = 0;
GO -- The GO terminator may be unsupported or unnecessary for your client.
```

## B. (Optional) Configure network security

> **Note:** If you are prototyping and your SQL Server instance is publicly accessible, **you can
> skip this step**. For production scenarios, we recommend configuring one of the
> network security options below.

There are various ways to configure your database's network to allow Materialize
to connect:

- **Allow Materialize IPs:** If your database is publicly accessible, you can
    configure your database's firewall to allow connections from a set of
    static Materialize IP addresses.

- **Use an SSH tunnel:** If your database is running in a private network, you
    can use an SSH tunnel to connect Materialize to the database.

Select the option that works best for you.

**Allow Materialize IPs:**

1. In the [SQL Shell](/console/), or your preferred SQL
   client connected to Materialize, find the static egress IP addresses for the
   Materialize region you are running in:

    ```mzsql
    SELECT * FROM mz_egress_ips;
    ```

1. Update your database firewall rules to allow traffic from each IP address
   from the previous step.

**Use AWS PrivateLink:**

Materialize can connect to a SQL Server database through an [AWS PrivateLink](https://aws.amazon.com/privatelink/)
service. Your SQL Server database must be running on AWS in order to use this
option.

1. Create a dedicated [target
    group](https://docs.aws.amazon.com/elasticloadbalancing/latest/network/create-target-group.html)
    for your SQL Server instance with the following details:

    a. Target type as **IP address**.

    b. Protocol as **TCP**.

    c. Port as **1433**, or the port that you are using in case it is not 1433.

    d. Make sure that the target group is in the same VPC as the SQL Server
    instance.

    e. Click next, and register the respective SQL Server instance to the target
    group using its IP address.

1. Create a [Network Load
    Balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/network/create-network-load-balancer.html)
    that is **enabled for the same subnets** that the SQL Server instance is in.

1. Create a [TCP
    listener](https://docs.aws.amazon.com/elasticloadbalancing/latest/network/create-listener.html)
    for your SQL Server instance that forwards to the corresponding target group
    you created.

1. Verify security groups and health checks. Once the TCP listener has been
    created, make sure that the [health
    checks](https://docs.aws.amazon.com/elasticloadbalancing/latest/network/target-group-health-checks.html)
    are passing and that the target is reported as healthy.

    If you have set up a security group for your SQL Server instance, you must
    ensure that it allows traffic on the health check port.

    **Remarks**:

    - By default, Network Load Balancers do not have associated security
      groups. In addition, target security groups cannot use client security
      groups as a traffic source. Therefore, the security groups for your
      targets must allow traffic using IP address ranges rather than security
      group references. For more information, see the [AWS
      documentation](https://docs.aws.amazon.com/elasticloadbalancing/latest/network/target-group-register-targets.html).

    - If you use [network ACLs
      (NACLs)](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-network-acls.html)
      and traffic between the NLB and its targets crosses subnet boundaries,
      the NACLs must allow both the application port and the ephemeral port
      range (1024–65535) for return traffic. This can occur when cross-zone
      load balancing is enabled, or when the NLB and its targets reside in
      different subnets, even within the same Availability Zone.

      For example, if a target application listens on port 9098, the target
      subnet must allow ingress on port 9098 from the NLB's IP ranges and
      egress on the ephemeral port range (1024–65535) to those ranges
      for return traffic. Likewise, the NLB subnet must allow egress on
      port 9098 to the target IP ranges and ingress on the ephemeral port
      range from them.

    - If you have associated a security group with your Network Load Balancer
      and enabled **Enforce inbound rules on PrivateLink traffic**, the
      security group's inbound rules also apply to traffic from Materialize's
      VPC endpoint. Any traffic not explicitly permitted, including
      Materialize's, will be silently blocked.

      To resolve this, either:
      - Add inbound rules to the NLB's security group that permit the listener
        port and the health check port from a source covering Materialize's
        VPC endpoint traffic, or
      - Disable **Enforce inbound rules on PrivateLink traffic**.

1. Create a VPC [endpoint
    service](https://docs.aws.amazon.com/vpc/latest/privatelink/create-endpoint-service.html)
    and associate it with the **Network Load Balancer** that you’ve just
    created.

    Note the **service name** that is generated for the endpoint service.

    **Remarks**:

    By disabling [Acceptance Required](https://docs.aws.amazon.com/vpc/latest/privatelink/configure-endpoint-service.html#accept-reject-connection-requests),
    while still strictly managing who can view your endpoint via IAM,
    Materialze will be able to seamlessly recreate and migrate endpoints as we
    work to stabilize this feature.

1. In Materialize, create a [`AWS
     PRIVATELINK`](/sql/create-connection/#aws-privatelink) connection that
     references the endpoint service that you created in the previous step.

     ```mzsql
    CREATE CONNECTION privatelink_svc TO AWS PRIVATELINK (
        SERVICE NAME 'com.amazonaws.vpce.<region_id>.vpce-svc-<endpoint_service_id>',
        AVAILABILITY ZONES ('use1-az1', 'use1-az2', 'use1-az3')
    );
    ```

    Update the list of the availability zones to match the ones that you are
    using in your AWS account.

1. Configure the AWS PrivateLink service.

    Retrieve the AWS principal for the AWS PrivateLink connection you just
    created:

    ```mzsql
    SELECT principal
    FROM mz_aws_privatelink_connections plc
    JOIN mz_connections c ON plc.id = c.id
    WHERE c.name = 'privatelink_svc';
    ```

    ```
                                     principal
    ---------------------------------------------------------------------------
     arn:aws:iam::664411391173:role/mz_20273b7c-2bbe-42b8-8c36-8cc179e9bbc3_u1
    ```

    Follow the instructions in the [AWS PrivateLink documentation](https://docs.aws.amazon.com/vpc/latest/privatelink/add-endpoint-service-permissions.html)
    to configure your VPC endpoint service to accept connections from the
    provided AWS principal.

    If your AWS PrivateLink service is configured to require acceptance of
    connection requests, you must manually approve the connection request from
    Materialize after executing the `CREATE CONNECTION` statement. For more
    details, check the [AWS PrivateLink documentation](https://docs.aws.amazon.com/vpc/latest/privatelink/configure-endpoint-service.html#accept-reject-connection-requests).

    **Note:** It might take some time for the endpoint service connection to
      show up, so you would need to wait for the endpoint service connection to
      be ready before you create a source.

**Use an SSH tunnel:**

To create an SSH tunnel from Materialize to your database, you launch an VM to
serve as an SSH bastion host, configure the bastion host to allow traffic only
from Materialize, and then configure your database's private network to allow
traffic from the bastion host.

1. Launch a VM to serve as your SSH bastion host.

    - Make sure the VM is publicly accessible and in the same VPC as your
      database.
    - Add a key pair and note the username. You'll use this username when
      connecting Materialize to your bastion host.
    - Make sure the VM has a static public IP address. You'll use this IP
      address when connecting Materialize to your bastion host.

1. Configure the SSH bastion host to allow traffic only from Materialize.

    1. In the [SQL Shell](/console/), or your preferred
       SQL client connected to Materialize, get the static egress IP addresses for
       the Materialize region you are running in:

       ```mzsql
       SELECT * FROM mz_egress_ips;
       ```

    1. Update your SSH bastion host's firewall rules to allow traffic from each
       IP address from the previous step.

1. Update your database firewall rules to allow traffic from the SSH bastion
   host.

## C. Ingest data in Materialize

### 1. (Optional) Create a cluster

> **Note:** If you are prototyping and already have a cluster to host your SQL Server
> source (e.g. `quickstart`), **you can skip this step**. For production
> scenarios, we recommend separating your workloads into multiple clusters for
> [resource isolation](/sql/create-cluster/#resource-isolation).

In Materialize, a [cluster](/concepts/clusters/) is an isolated
environment, similar to a virtual warehouse in Snowflake. When you create a
cluster, you choose the size of its compute resource allocation based on the
work you need the cluster to do, whether ingesting data from a source,
computing always-up-to-date query results, serving results to clients, or a
combination.

In this case, you'll create a dedicated cluster for ingesting source data from
your SQL Server database.

1. In the [SQL Shell](/console/), or your preferred SQL
   client connected to Materialize, use the [`CREATE CLUSTER`](/sql/create-cluster/)
   command to create the new cluster:

    ```mzsql
    CREATE CLUSTER ingest_sqlserver (SIZE = '200cc');

    SET CLUSTER = ingest_sqlserver;
    ```

    A cluster of [size](/sql/create-cluster/#available-sizes) `200cc` should be enough to
    process the initial snapshot of the tables in your SQL Server database. For
    very large snapshots, consider using a larger size to speed up processing.
    Once the snapshot is finished, you can readjust the size of the cluster to fit
    the volume of changes being replicated from your upstream SQL Server database.

### 2. Create a connection

Once you have configured your network, create a connection in Materialize per
your networking configuration.

**Allow Materialize IPs:**

1. In the [SQL Shell](/console/), or your preferred SQL
   client connected to Materialize, use the [`CREATE SECRET`](/sql/create-secret/)
   command to securely store the password for the SQL Server role you'll use to
   replicate data into Materialize:

    ```mzsql
    CREATE SECRET sqlserver_pass AS '<PASSWORD>';
    ```

1. Use the [`CREATE CONNECTION`](/sql/create-connection/) command to create a
   connection object with access and authentication details for Materialize to
   use:

    ```mzsql
    CREATE CONNECTION sqlserver_connection TO SQL SERVER (
        HOST <host>,
        PORT 1433,
        USER 'materialize',
        PASSWORD SECRET sqlserver_pass,
        DATABASE <database>,
        SSL MODE 'required'
    );
    ```

    - Replace `<host>` with your SQL Server endpoint, and `<database>` with the database you'd like to connect to.

**Use an AWS Privatelink (Cloud-only):**
1. In the [SQL Shell](/console/), or your preferred SQL
client connected to Materialize, use the [`CREATE CONNECTION`](/sql/create-connection/#aws-privatelink)
command to create an AWS PrivateLink connection:

    ↕️ **In-region connections**

    To connect to an AWS PrivateLink endpoint service in the **same region** as your
    Materialize environment:

      ```mzsql
      CREATE CONNECTION privatelink_svc TO AWS PRIVATELINK (
        SERVICE NAME 'com.amazonaws.vpce.<region_id>.vpce-svc-<endpoint_service_id>',
        AVAILABILITY ZONES ('use1-az1', 'use1-az2', 'use1-az4')
      );
      ```

    - Replace the `SERVICE NAME` value with the service name you noted [earlier](#b-optional-configure-network-security).

    - Replace the `AVAILABILITY ZONES` list with the IDs of the availability
      zones in your AWS account. For in-region connections the availability
      zones of the NLB and the consumer VPC **must match**.

      To find your availability zone IDs, select your database in the RDS
      Console and click the subnets under **Connectivity & security**. For each
      subnet, look for **Availability Zone ID** (e.g., `use1-az6`),
      not **Availability Zone** (e.g., `us-east-1d`).

    ↔️ **Cross-region connections**

    To connect to an AWS PrivateLink endpoint service in a **different region** to
    the one where your Materialize environment is deployed:

      ```mzsql
      CREATE CONNECTION privatelink_svc TO AWS PRIVATELINK (
        SERVICE NAME 'com.amazonaws.vpce.us-west-1.vpce-svc-<endpoint_service_id>',
        -- For now, the AVAILABILITY ZONES clause **is** required, but will be
        -- made optional in a future release.
        AVAILABILITY ZONES ()
      );
      ```

    - Replace the `SERVICE NAME` value with the service name you noted [earlier](#b-optional-configure-network-security).

    - The service name region refers to where the endpoint service was created.
      You **do not need** to specify `AVAILABILITY ZONES` manually — these will
      be optimally auto-assigned when none are provided.

1. Retrieve the AWS principal for the AWS PrivateLink connection you just
created:

     ```mzsql
     SELECT principal
       FROM mz_aws_privatelink_connections plc
       JOIN mz_connections c ON plc.id = c.id
       WHERE c.name = 'privatelink_svc';
     ```
    <p></p>

    ```
    principal
    ---------------------------------------------------------------------------
    arn:aws:iam::664411391173:role/mz_20273b7c-2bbe-42b8-8c36-8cc179e9bbc3_u1
    ```

1. Update your VPC endpoint service to [accept connections from the AWS
principal](https://docs.aws.amazon.com/vpc/latest/privatelink/add-endpoint-service-permissions.html).

1. If your AWS PrivateLink service is configured to require acceptance of
connection requests, [manually approve the connection request from
Materialize](https://docs.aws.amazon.com/vpc/latest/privatelink/configure-endpoint-service.html#accept-reject-connection-requests).

    **Note:** It can take some time for the connection request to show up. Do
    not move on to the next step until you've approved the connection.

1. Validate the AWS PrivateLink connection you created using the
[`VALIDATE CONNECTION`](/sql/validate-connection) command:

    ```mzsql
    VALIDATE CONNECTION privatelink_svc;
    ```

    If no validation error is returned, move to the next step.

1. Use the [`CREATE SECRET`](/sql/create-secret/) command to securely store the password for the `materialize` SQL Server user [you created](#1-create-a-materialize-user-in-sql-server):

    ```mzsql
    CREATE SECRET sql_server_pass AS '<PASSWORD>';
    ```

1. Use the [`CREATE CONNECTION`](/sql/create-connection/) command to create
another connection object, this time with database access and authentication
details for Materialize to use:

    ```mzsql
    CREATE CONNECTION sql_server_connection TO SQL SERVER (
    HOST <host>,
      PORT 1433,
      USER 'materialize',
      PASSWORD SECRET sql_server_pass,
      SSL MODE REQUIRED,
      AWS PRIVATELINK privatelink_svc
    );
    ```

    - Replace `<host>` with your RDS endpoint. To find your RDS endpoint, select
      your database in the RDS Console, and look under **Connectivity &
      security**.

      - Replace `<database>` with the name of the database containing the tables
        you want to replicate to Materialize.

    AWS IAM authentication is also available, see the [`CREATE CONNECTION`](/sql/create-connection/#mysql) command for details.

**Use an SSH tunnel:**

1. In the [SQL Shell](/console/), or your preferred SQL
   client connected to Materialize, use the [`CREATE CONNECTION`](/sql/create-connection/#ssh-tunnel)
   command to create an SSH tunnel connection:

    ```mzsql
    CREATE CONNECTION ssh_connection TO SSH TUNNEL (
        HOST '<SSH_BASTION_HOST>',
        PORT <SSH_BASTION_PORT>,
        USER '<SSH_BASTION_USER>'
    );
    ```

    - Replace `<SSH_BASTION_HOST>` and `<SSH_BASTION_PORT`> with the public IP address and port of the SSH bastion host you created [earlier](#b-optional-configure-network-security).

    - Replace `<SSH_BASTION_USER>` with the username for the key pair you created for your SSH bastion host.

1. Get Materialize's public keys for the SSH tunnel connection:

    ```mzsql
    SELECT * FROM mz_ssh_tunnel_connections;
    ```

1. Log in to your SSH bastion host and add Materialize's public keys to the `authorized_keys` file, for example:

    ```sh
    # Command for Linux
    echo "ssh-ed25519 AAAA...76RH materialize" >> ~/.ssh/authorized_keys
    echo "ssh-ed25519 AAAA...hLYV materialize" >> ~/.ssh/authorized_keys
    ```

1. Back in the SQL client connected to Materialize, validate the SSH tunnel connection you created using the [`VALIDATE CONNECTION`](/sql/validate-connection) command:

    ```mzsql
    VALIDATE CONNECTION ssh_connection;
    ```

    If no validation error is returned, move to the next step.

1. Use the [`CREATE SECRET`](/sql/create-secret/) command to securely store the password for the `materialize` SQL Server user [you created](#1-create-a-materialize-user-in-sql-server):

    ```mzsql
    CREATE SECRET sql_server_pass AS '<PASSWORD>';
    ```

    For AWS IAM authentication, you must create a connection to AWS.  See the [`CREATE CONNECTION`](/sql/create-connection/#aws) command for details.

1. Use the [`CREATE CONNECTION`](/sql/create-connection/) command to create another connection object, this time with database access and authentication details for Materialize to use:

    ```mzsql
    CREATE CONNECTION sql_server_connection TO SQL SERVER (
    HOST '<host>',
    SSH TUNNEL ssh_connection
    );
    ```

    - Replace `<host>` with your SQL Server endpoint.

### 3. Start ingesting data

> **Note:** For a new SQL Server source, if none of the replicating tables
> are receiving write queries, snapshotting may take up to an additional 5 minutes
> to complete. For details, see [snapshot latency for inactive databases](#snapshot-latency-for-inactive-databases)

Use the [`CREATE SOURCE`](/sql/create-source/) command to connect
Materialize to your SQL Server instance and start ingesting data:
```mzsql
CREATE SOURCE mz_source
  FROM SQL SERVER CONNECTION sqlserver_connection
  FOR ALL TABLES;

```

- By default, the source will be created in the active cluster; to use a
  different cluster, use the `IN CLUSTER` clause.
- To ingest data from specific tables use the `FOR TABLES
  (<table1>, <table2>)` options instead of `FOR ALL TABLES`.
- To handle unsupported data types, use the `TEXT COLUMNS` or `EXCLUDE
  COLUMNS` options. Check out the [reference
  documentation](#supported-types) for guidance.

After source creation, refer to [schema changes
considerations](#handling-upstream-operations) for information on handling upstream schema changes.

### 4. Right-size the cluster

After the snapshotting phase, Materialize starts ingesting change events from
the SQL Server replication stream. For this work, Materialize generally
performs well with a `100cc` replica, so you can resize the cluster
accordingly.

1. Still in a SQL client connected to Materialize, use the [`ALTER CLUSTER`](/sql/alter-cluster/)
   command to downsize the cluster to `100cc`:

    ```mzsql
    ALTER CLUSTER ingest_sqlserver SET (SIZE '100cc');
    ```

    Behind the scenes, this command adds a new `100cc` replica and removes the
    `200cc` replica.

1. Use the [`SHOW CLUSTER REPLICAS`](/sql/show-cluster-replicas/) command to
   check the status of the new replica:

    ```mzsql
    SHOW CLUSTER REPLICAS WHERE cluster = 'ingest_sqlserver';
    ```
    <p></p>

    ```nofmt
         cluster       | replica |  size  | ready
    -------------------+---------+--------+-------
     ingest_sqlserver  | r1      | 100cc  | t
    (1 row)
    ```

## D. Explore your data

With Materialize ingesting your SQL Server data into durable storage, you can
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

### Supported types

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

### Timestamp Rounding

The `time`, `datetime2`, and `datetimeoffset` types in SQL Server have a default
scale of 7 decimal places, or in other words a accuracy of 100 nanoseconds. But
the corresponding types in Materialize only support a scale of 6 decimal places.
If a column in SQL Server has a higher scale than what Materialize can support, it
will be rounded up to the largest scale possible.

```
-- In SQL Server
CREATE TABLE my_timestamps (a datetime2(7));
INSERT INTO my_timestamps VALUES
  ('2000-12-31 23:59:59.99999'),
  ('2000-12-31 23:59:59.999999'),
  ('2000-12-31 23:59:59.9999999');

-- Replicated into Materialize
SELECT * FROM my_timestamps;
'2000-12-31 23:59:59.999990'
'2000-12-31 23:59:59.999999'
'2001-01-01 00:00:00'
```

### Snapshot latency for inactive databases

When a new Source is created, Materialize performs a snapshotting operation to sync
the data. However, for a new SQL Server source, if none of the replicating tables
are receiving write queries, snapshotting may take up to an additional 5 minutes
to complete. The 5 minute interval is due to a hardcoded interval in the SQL Server
Change Data Capture (CDC) implementation which only notifies CDC consumers every
5 minutes when no changes are made to replicating tables.

See [Monitoring freshness status](/ingest-data/monitoring-data-ingestion/#monitoring-hydrationdata-freshness-status)

### Capture Instance Selection

When a new source is created, Materialize selects a capture instance for each
table. SQL Server permits at most two capture instances per table, which are
listed in the
[`sys.cdc_change_tables`](https://learn.microsoft.com/en-us/sql/relational-databases/system-tables/cdc-change-tables-transact-sql)
system table. For each table, Materialize picks the capture instance with the
most recent `create_date`.

If two capture instances for a table share the same timestamp (unlikely given the millisecond resolution), Materialize selects the `capture_instance` with the lexicographically larger name.

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

