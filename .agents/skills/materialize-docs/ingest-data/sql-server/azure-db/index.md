# Ingest data from Azure SQL Database
How to stream data from Azure SQL Database to Materialize
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
considerations](#schema-changes) for information on handling upstream schema changes.

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

### Schema changes
Materialize supports schema changes in the upstream database as follows:

#### Compatible schema changes (Legacy syntax)

> **Note:** This section refer to the legacy [`CREATE SOURCE ... FOR
> ...`](/sql/create-source/sql-server/) that creates subsources as part of the
> `CREATE SOURCE` operation.  To be able to handle the upstream column additions
> and drops, use [`CREATE SOURCE (New Syntax)`](/sql/create-source/sql-server-v2/)
> and [`CREATE TABLE FROM SOURCE`](/sql/create-table) instead.  For details, see
> [SQL Server: Source versioning
> guide](/ingest-data/sql-server/source-versioning/).

- Adding columns to tables. Materialize will **not ingest** new columns added
  upstream unless you use [`DROP SOURCE`](/sql/alter-source/#context) to first
  drop the affected subsource, and then add the table back to the source using
  [`ALTER SOURCE...ADD SUBSOURCE`](/sql/alter-source/).

- Dropping columns that were added after the source was created. These columns
  are never ingested, so you can drop them without issue.

- Adding or removing `NOT NULL` constraints to tables that were nullable when
  the source was created.

#### Incompatible schema changes

All other schema changes to upstream tables will set the corresponding subsource
into an error state, which prevents you from reading from the source.

To handle incompatible [schema changes](#schema-changes), use [`DROP SOURCE`](/sql/alter-source/#context)
and [`ALTER SOURCE...ADD SUBSOURCE`](/sql/alter-source/) to first drop the
affected subsource, and then add the table back to the source. When you add the
subsource, it will have the updated schema from the corresponding upstream
table.

### Supported types

Materialize natively supports the following SQL Server types:

<ul style="column-count: 3"><li><code>tinyint</code></li><li><code>smallint</code></li><li><code>int</code></li><li><code>bigint</code></li><li><code>real</code></li><li><code>double precision</code></li><li><code>float</code></li><li><code>bit</code></li><li><code>decimal</code></li><li><code>numeric</code></li><li><code>money</code></li><li><code>smallmoney</code></li><li><code>char</code></li><li><code>nchar</code></li><li><code>varchar</code></li><li><code>varchar(max)</code></li><li><code>nvarchar</code></li><li><code>nvarchar(max)</code></li><li><code>sysname</code></li><li><code>binary</code></li><li><code>varbinary</code></li><li><code>json</code></li><li><code>date</code></li><li><code>time</code></li><li><code>smalldatetime</code></li><li><code>datetime</code></li><li><code>datetime2</code></li><li><code>datetimeoffset</code></li><li><code>uniqueidentifier</code></li></ul>

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
