<!-- mz-docs page: ingest-data/postgres/replication-slot-active -->

# Troubleshooting: Replication slot is active
How to troubleshoot and resolve the replication slot is active error with PostgreSQL sources in Materialize
This guide helps you troubleshoot and resolve the "replication slot... is active"
error that can occur with PostgreSQL sources in Materialize.

## What this error means

When you see an error like:

```nofmt
postgres: ERROR replication slot "materialize_1002f37c6eeb4c28b052fa3805d46baa" is active for PID 610
```

This means that PostgreSQL has detected an attempt to use a replication slot that
is already in use by another active connection. Each replication slot can only
have one active consumer at a time, and this error occurs when Materialize tries
to connect to a slot that PostgreSQL considers already active. This error is
generally transient and indicates a race condition during connection management
between Materialize and PostgreSQL.

## Common causes

- **PostgreSQL or Materialize maintenance**: During maintenance windows,
  Materialize clusters or PostgreSQL instances may restart, causing active
  replication connections to be temporarily interrupted. When the cluster comes
  back online, it attempts to reconnect to the replication slot before PostgreSQL
  has fully released the previous connection.
- **Cluster replica changes**: Adding replicas to your Materialize source cluster
  can cause the ingestion process to restart from a different replica, triggering
  this error as multiple replicas attempt to use the same replication slot.
- **Source restarts or failover**: When a source cluster restarts or fails over
  to another replica, the new replica may attempt to connect to the replication
  slot before PostgreSQL has released the previous connection.
- **Network interruptions**: Brief network disconnections can leave PostgreSQL
  thinking a connection is still active when Materialize has already moved to a
  new connection attempt.
- **PostgreSQL connection cleanup delays**: PostgreSQL may not immediately
  release replication slots when connections are terminated, especially if the
  termination was not graceful.
- **Multiple environments or sources**: Accidentally configuring multiple
  Materialize sources to use the same replication slot.

## Diagnosing the issue

### Check replication slot status in PostgreSQL

Connect to your PostgreSQL database and run:

```sql
-- Replace <slot_name> with the replication slot name shown in the error message
SELECT
  slot_name,
  active,
  active_pid,
  restart_lsn,
  confirmed_flush_lsn
FROM pg_replication_slots
WHERE slot_name = '<slot_name>';
```

Look for:

- **active = true**: The slot is currently in use
- **active_pid**: The PostgreSQL backend process ID that is using the slot
- Multiple slots with similar names that might indicate configuration issues

### Check for active connections

Check which connections are using the replication slot:

```sql
-- Replace <slot_name> with the replication slot name shown in the error message
SELECT
  pid,
  usename,
  application_name,
  client_addr,
  state,
  backend_start
FROM pg_stat_activity
WHERE pid IN (
  SELECT active_pid
  FROM pg_replication_slots
  WHERE slot_name = '<slot_name>'
);
```

## Resolution

### Immediate fix: Wait for automatic recovery

In most cases, Materialize will automatically reconnect and recover from this
error. The error is typically transient and resolves itself within a few minutes
as PostgreSQL releases the previous connection.

### If automatic recovery fails: Terminate stale connections

If the error persists and you've verified that there are no legitimate active
connections, you can terminate the stale connection in PostgreSQL:

> **Warning:** Only terminate connections if you're certain they are stale. Terminating an
> active replication connection will interrupt data ingestion.

```sql
-- First, identify the PID from the error message or from pg_replication_slots
-- Replace <slot_name> with the replication slot name shown in the error message
SELECT
  slot_name,
  active_pid
FROM pg_replication_slots
WHERE slot_name = '<slot_name>' AND active = true;

-- Terminate the connection (replace ### with the actual PID)
SELECT pg_terminate_backend(###);
```

After terminating the connection, Materialize should be able to reconnect to
the replication slot.

## Prevention

**Best practices to avoid this error:**

- **Avoid frequent replica changes**: Minimize adding or removing replicas from
  source clusters during active replication. Plan cluster sizing changes during
  maintenance windows when possible.
- **Ensure stable network connectivity**: Maintain reliable network connections
  between Materialize and PostgreSQL to prevent connection interruptions.
- **Monitor source health**: Regularly check source status to detect and address
  issues early:

```mzsql
SELECT *
FROM mz_internal.mz_source_statuses;
```

- **Configure connection timeouts appropriately**: Ensure PostgreSQL connection
  timeout settings allow for proper cleanup of disconnected sessions.
- **Use unique replication slots**: Verify that each Materialize source uses a
  unique replication slot and avoid reusing slot names across different sources
  or environments.
- **Plan for graceful restarts**: When performing maintenance that requires
  source restarts, allow sufficient time for PostgreSQL to release connections
  before restarting.

<!-- mz-docs page: ingest-data/postgres/self-hosted -->

# Ingest data from self-hosted PostgreSQL
How to stream data from self-hosted PostgreSQL database to Materialize
This page shows you how to stream data from a self-hosted PostgreSQL database to
Materialize using the [PostgreSQL source](/sql/create-source/postgres/).

> **Tip:** For help getting started with your own data, you can schedule a [free guided
> trial](https://materialize.com/demo/?utm_campaign=General&utm_source=documentation).

> **Note:** Connecting directly to your primary, as described here, is the recommended
> setup. In the exceptional case where you can't reconfigure the primary, or need
> to keep WAL-retention risk off it, you can point Materialize at a dedicated
> replica instead. See [Ingest from a dedicated PostgreSQL
> replica](/ingest-data/postgres/logical-replica/).

## Before you begin

- Make sure you are running PostgreSQL 11 or higher.

- Make sure you have access to your PostgreSQL instance via [`psql`](https://www.postgresql.org/docs/current/app-psql.html),
  or your preferred SQL client.

## A. Configure PostgreSQL

### 1. Enable logical replication

Materialize uses PostgreSQL's [logical
replication](https://www.postgresql.org/docs/current/logical-replication.html)
protocol to track changes in your database and propagate them to Materialize.
Enable your PostgreSQL's logical replication.

1. As a _superuser_, use `psql` (or your preferred SQL client) to connect to
   your PostgreSQL database.

1. Check if logical replication is enabled; that is, check if the `wal_level` is
   set to `logical`:

    ```postgres
    SHOW wal_level;
    ```

1. If `wal_level` setting is **not** set to `logical`:

    1. In the  database configuration file (`postgresql.conf`), set `wal_level`
       value to `logical`.

    1. Restart the database in order for the new `wal_level` to take effect.
       Restarting can affect database performance.

    1. In the SQL client connected to PostgreSQL, verify that replication is now
  enabled (i.e., verify `wal_level` setting is set to `logical`).

        ```postgres
        SHOW wal_level;
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
    operations. This setting enables Materialize to ingest PostgreSQL data with
    minimal in-memory state. However, you should expect increased disk usage in
    your PostgreSQL database.

1. Create a [publication](https://www.postgresql.org/docs/current/logical-replication-publication.html)
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

1. Create a user for Materialize, if you don't already have one:

    ```postgres
    CREATE USER materialize PASSWORD '<password>';
    ```

1. Grant the user permission to manage replication:

    ```postgres
    ALTER ROLE materialize WITH REPLICATION;
    ```

1. Grant the user the required permissions on the tables you want to replicate:

    ```postgres
    GRANT CONNECT ON DATABASE <dbname> TO materialize;
    ```

    ```postgres
    GRANT USAGE ON SCHEMA <schema> TO materialize;
    ```

    ```postgres
    GRANT SELECT ON <table1> TO materialize;
    ```

    ```postgres
    GRANT SELECT ON <table2> TO materialize;
    ```

    Once connected to your database, Materialize will take an initial snapshot
    of the tables in your publication. `SELECT` privileges are required for
    this initial snapshot.

    If you expect to add tables to your publication, you can grant `SELECT` on
    all tables in the schema instead of naming the specific tables:

    ```postgres
    GRANT SELECT ON ALL TABLES IN SCHEMA <schema> TO materialize;
    ```

## B. (Optional) Configure network security

> **Note:** If you are prototyping and your PostgreSQL instance is publicly
> accessible, **you can skip this step**. For production scenarios, we recommend
> configuring one of the network security options below.

**Cloud:**

There are various ways to configure your database's network to allow Materialize
to connect:

- **Allow Materialize IPs:** If your database is publicly accessible, you can
    configure your database's firewall to allow connections from a set of
    static Materialize IP addresses.

- **Use an SSH tunnel:** If your database is running in a private network, you
    can use an SSH tunnel to connect Materialize to the database.

Select the option that works best for you.

**Allow Materialize IPs:**

1. In the [Materialize console's SQL Shell](/developer-tools/console/),
   or your preferred SQL client connected to Materialize, find the static egress
   IP addresses for the Materialize region you are running in:

    ```mzsql
    SELECT * FROM mz_egress_ips;
    ```

1. Update your database firewall rules to allow traffic from each IP address
   from the previous step.

**Use AWS PrivateLink:**

Materialize can connect to a PostgreSQL database through an [AWS PrivateLink](https://aws.amazon.com/privatelink/)
service. Your PostgreSQL database must be running on AWS in order to use this
option.

1. Create a dedicated [target
    group](https://docs.aws.amazon.com/elasticloadbalancing/latest/network/create-target-group.html)
    for your Postgres instance with the following details:

    a. Target type as **IP address**.

    b. Protocol as **TCP**.

    c. Port as **5432**, or the port that you are using in case it is not 5432.

    d. Make sure that the target group is in the same VPC as the PostgreSQL
    instance.

    e. Click next, and register the respective PostgreSQL instance to the target
    group using its IP address.

1. Create a [Network Load
    Balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/network/create-network-load-balancer.html)
    that is **enabled for the same subnets** that the PostgreSQL instance is in.

1. Create a [TCP
    listener](https://docs.aws.amazon.com/elasticloadbalancing/latest/network/create-listener.html)
    for your PostgreSQL instance that forwards to the corresponding target group
    you created.

1. Once the TCP listener has been created, make sure that the [health
    checks](https://docs.aws.amazon.com/elasticloadbalancing/latest/network/target-group-health-checks.html)
    are passing and that the target is reported as healthy.

    If you have set up a security group for your PostgreSQL instance, you must
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

1. Retrieve the AWS principal for the AWS PrivateLink connection you just
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

    1. In the [Materialize console's SQL
       Shell](/developer-tools/console/), or your preferred SQL client
       connected to Materialize, get the static egress IP addresses for the
       Materialize region you are running in:

       ```mzsql
       SELECT * FROM mz_egress_ips;
       ```

    1. Update your SSH bastion host's firewall rules to allow traffic from each
       IP address from the previous step.

1. Update your database firewall rules to allow traffic from the SSH bastion
   host.

**Self-Managed:**

Configure your network to allow Materialize to connect to your database. For
example, you can:

- **Allow Materialize IPs:** Configure your database's security group to allow
    connections from Materialize.

- **Use an SSH tunnel:** Use an SSH tunnel to connect Materialize to the
  database.

> **Note:** The steps to allow Materialize to connect to your database  depends on your
> deployment setup. Refer to your company’s network/security policies and
> procedures.

**Allow Materialize IPs:**

1. Update your database firewall rules to allow traffic from Materialize.

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

1. Update your database firewall rules to allow traffic from the SSH bastion
   host.

## C. Ingest data in Materialize

### 1. (Optional) Create a cluster

> **Note:** If you are prototyping and already have a cluster to host your PostgreSQL
> source (e.g. `quickstart`), **you can skip this step**. For production
> scenarios, we recommend separating your workloads into multiple clusters for
> [resource isolation](/sql/create-cluster/#resource-isolation).

In Materialize, a [cluster](/fundamentals/concepts/clusters/) is an isolated environment,
similar to a virtual warehouse in Snowflake. When you create a cluster, you
choose the size of its compute resource allocation based on the work you need
the cluster to do, whether ingesting data from a source, computing
always-up-to-date query results, serving results to external clients, or a
combination.

In this step, you'll create a dedicated cluster for ingesting source data from
your PostgreSQL database.

1. In the [SQL Shell](/developer-tools/console/), or your preferred SQL
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

**Allow Materialize IPs:**

1. In the [Materialize Console's SQL Shell](/developer-tools/console/), or your preferred SQL
client connected to Materialize, use the [`CREATE
SECRET`](/sql/create-secret/) command to securely store the password for the
`materialize` PostgreSQL user you created
[earlier](#2-create-a-publication-and-a-replication-user):   ```mzsql
   CREATE SECRET pgpass AS '<PASSWORD>';

   ```

1. Use the [`CREATE CONNECTION`](/sql/create-connection/) command to create a
connection object with access and authentication details for Materialize to
use:
   ```mzsql
   CREATE CONNECTION pg_connection TO POSTGRES (
     HOST '<host>',
     PORT 5432,
     USER materialize,
     PASSWORD SECRET pgpass,
     SSL MODE 'require',
     DATABASE '<database>'
   );

   ```

   - Replace `<host>` with your PostgreSQL endpoint.

   - Replace `<database>` with the name of the database containing the tables
     you want to replicate to Materialize.

**Use AWS PrivateLink (Cloud-only):**

1. Use the [`CREATE SECRET`](/sql/create-secret/) command to securely store the
password for the `materialize` PostgreSQL user you created
[earlier](#2-create-a-publication-and-a-replication-user):
   ```mzsql
   CREATE SECRET pgpass AS '<PASSWORD>';

   ```

1. Use the [`CREATE CONNECTION`](/sql/create-connection/) command to create
another connection object, this time with database access and authentication
details for Materialize to use:
   ```mzsql
   CREATE CONNECTION pg_connection TO POSTGRES (
     HOST '<host>',
     PORT 5432,
     USER 'materialize',
     PASSWORD SECRET pgpass,
     DATABASE '<database>',
     AWS PRIVATELINK privatelink_svc
     );

   ```

   - Replace `<host>` with your database endpoint.

   - Replace `<database>` with the name of the database containing the tables
     you want to replicate to Materialize.

**Use an SSH tunnel:**

1. In the [Materialize Console's SQL Shell](/developer-tools/console/), or your preferred SQL
client connected to Materialize, use the [`CREATE
CONNECTION`](/sql/create-connection/#ssh-tunnel) command to create an SSH
tunnel connection:   ```mzsql
   CREATE CONNECTION ssh_connection TO SSH TUNNEL (
       HOST '<SSH_BASTION_HOST>',
       PORT <SSH_BASTION_PORT>,
       USER '<SSH_BASTION_USER>'
   );

   ```

   - Replace `<SSH_BASTION_HOST>` and `<SSH_BASTION_PORT>` with the public IP
   address and port of the SSH bastion host you created
   [earlier](#b-optional-configure-network-security).

   - Replace `<SSH_BASTION_USER>` with the username for the key pair you
   created for your SSH bastion host.

1. Get Materialize's public keys for the SSH tunnel connection:
   ```mzsql
   SELECT
       mz_connections.name,
       mz_ssh_tunnel_connections.*
   FROM
       mz_connections
   JOIN
       mz_ssh_tunnel_connections USING(id)
   WHERE
       mz_connections.name = 'ssh_connection';

   ```

1. Log in to your SSH bastion host and add Materialize's public keys to the
`authorized_keys` file, for example:
   ```mzsql
   echo "ssh-ed25519 AAAA...76RH materialize" >> <AUTHORIZED_KEYS_FILE>
   echo "ssh-ed25519 AAAA...hLYV materialize" >> <AUTHORIZED_KEYS_FILE>

   ```

1. Back in the SQL client connected to Materialize, validate the SSH tunnel
connection you created using the [`VALIDATE
CONNECTION`](/sql/validate-connection) command:
   ```mzsql
   VALIDATE CONNECTION ssh_connection;

   ```   If no validation error is returned, move to the next step.

1. Use the [`CREATE SECRET`](/sql/create-secret/) command to securely store the
password for the `materialize` PostgreSQL user you created
[earlier](#2-create-a-publication-and-a-replication-user):
   ```mzsql
   CREATE SECRET pgpass AS '<PASSWORD>';

   ```

1. 
Use the [`CREATE CONNECTION`](/sql/create-connection/) command to create another connection object, this time with database access and authentication details for Materialize to use:
   ```mzsql
   CREATE CONNECTION pg_connection TO POSTGRES (
     HOST '<host>',
     PORT 5432,
     USER 'materialize',
     PASSWORD SECRET pgpass,
     DATABASE '<database>',
     SSH TUNNEL ssh_connection
     );

   ```

   - Replace `<host>` with your PostgreSQL endpoint.

   - Replace `<database>` with the name of the database containing the tables
   you want to replicate to Materialize.

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
   [`mz_source_statuses`](/sql/system-catalog/mz_internal/#mz_source_statuses)
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

2. Once the source is running, use the [`mz_source_statistics`](/sql/system-catalog/mz_internal/#mz_source_statistics)
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
    PostgreSQL source from the [`mz_internal.mz_postgres_sources`](/sql/system-catalog/mz_internal/#mz_postgres_sources)
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

- Check out the [tools and integrations](/developer-tools/integrations/) supported by
  Materialize.

## Considerations

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
<h3 id="partitioned-tables">Partitioned tables</h3>
<p>When you add a <a href="https://www.postgresql.org/docs/current/ddl-partitioning.html" >declaratively partitioned
table</a> to a
publication, PostgreSQL expands it to the table&rsquo;s leaf partitions; the parent
table is not itself replicated. Materialize ingests one table per partition,
which you can reassemble into the parent table using <code>UNION ALL</code>.</p>
<p>Materialize does <strong>not</strong> support ingesting from a publication created with
<a href="https://www.postgresql.org/docs/current/sql-createpublication.html" ><code>publish_via_partition_root = true</code></a>,
and doing so can produce incorrect results.</p>
<p>See <a href="/ingest-data/postgres/partitioned-tables/" >Ingest from partitioned
tables</a> for the supported
approaches, including how to add and remove partitions over time.</p>
<h3 id="modifying-an-existing-source">Modifying an existing source</h3>
<p>When you add a new subsource to an existing source (<a href="/sql/alter-source/" ><code>ALTER SOURCE ... ADD SUBSOURCE ...</code></a>), Materialize starts the snapshotting
process for the new subsource. During this snapshotting, the data ingestion for
the existing subsources for the same source is temporarily blocked. As such, if
possible, you can resize the cluster to speed up the snapshotting process and
once the process finishes, resize the cluster for steady-state.</p>

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

If using the new [`CREATE SOURCE` and `CREATE TABLE FROM
SOURCE`](/sql/create-source/postgres-v2/) syntax, you can safely drop such a
constraint by first excluding it in Materialize. See [Handle upstream
constraint drop](/ingest-data/postgres/source-versioning/#handle-upstream-constraint-drop).

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

- Dropping a table (`DROP TABLE`), or removing it from the publication (`ALTER PUBLICATION ... DROP TABLE`).
- Renaming a table or moving it to a different schema.
- Setting a table's replica identity to anything other than `FULL` (`ALTER TABLE ... REPLICA IDENTITY`).
- Truncating a table (`TRUNCATE`). To clear a table without putting it into an error state, use an unqualified `DELETE FROM t;` instead.


<!-- mz-docs page: ingest-data/postgres/slot-overcompacted -->

# Troubleshooting: Slot overcompacted
How to troubleshoot and resolve the slot overcompacted error with PostgreSQL sources in Materialize
This guide helps you troubleshoot and resolve the "slot overcompacted" error that
can occur with PostgreSQL sources in Materialize.

## What this error means

When you see an error like:

```nofmt
postgres: slot overcompacted. Requested LSN 181146050392 but only LSNs >= 332129862840 are available
```

This means Materialize tried to read from a PostgreSQL replication slot at a
specific Log Sequence Number (LSN), but that data has already been removed from
PostgreSQL's Write-Ahead Log (WAL). The WAL was "compacted" or cleaned up before
Materialize could read the data it needed.

## Common causes

- **WAL retention limits**: PostgreSQL has a setting called
  `max_slot_wal_keep_size` that limits how much WAL data is kept for replication
  slots. If this value is too small, PostgreSQL may delete WAL data that
  Materialize still needs.
- **Long-running snapshot operations**: If your source is taking a long time to
  complete its initial snapshot (e.g., for very large tables), the upstream
  PostgreSQL database may clean up WAL data before Materialize finishes.
- **Paused or slow replication**: If your Materialize cluster is paused,
  undersized, or experiencing performance issues, the replication slot may not
  advance quickly enough, causing PostgreSQL to reclaim WAL space.
- **Provider-specific WAL policies**: Some managed PostgreSQL providers (such
  as Neon) may have aggressive WAL cleanup policies that can trigger this error
  more frequently.

## Diagnosing the issue

### Check replication slot status in PostgreSQL

Connect to your PostgreSQL database and run:

```sql
SELECT
  slot_name,
  active,
  restart_lsn,
  confirmed_flush_lsn,
  pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS replication_lag
FROM pg_replication_slots
WHERE slot_name LIKE 'materialize%';
```

Look for:

- **Large replication lag** - Indicates Materialize is falling behind
- **Inactive slots** - May indicate connection issues

### Check PostgreSQL WAL settings

Check your `max_slot_wal_keep_size` setting:

```sql
SHOW max_slot_wal_keep_size;
```

If this is set too low (or to `-1` which means unlimited but may be overridden
by provider policies), you may experience this error.

### Check for long-running transactions

Long-running transactions can prevent WAL cleanup:

```sql
SELECT
  pid,
  age(clock_timestamp(), xact_start) AS transaction_age,
  state,
  query
FROM pg_stat_activity
WHERE xact_start IS NOT NULL
ORDER BY age DESC;
```

## Resolution

### Immediate fix: Recreate the source

> **Warning:** This will cause Materialize to take a new snapshot, which may take
> time and temporarily increase load on your PostgreSQL database.

Once a slot has been overcompacted, the data is permanently lost from the WAL.
You must **drop and recreate the source**. Dropping the source will also drop
any dependent objects; be prepared to recreate them as part of the recovery process.

### Long-term fixes

**1. Increase WAL retention**

Increase `max_slot_wal_keep_size` in your PostgreSQL configuration:

```sql
ALTER SYSTEM SET max_slot_wal_keep_size = '10GB';
SELECT pg_reload_conf();
```

The appropriate value depends on:

- Your data change rate
- How long snapshots take
- How often you pause/unpause clusters

**2. Ensure adequate cluster sizing**

Make sure your Materialize source cluster has enough resources to keep up with
replication:

```mzsql
ALTER CLUSTER your_source_cluster SET (SIZE = '800cc');
```

**3. Monitor replication lag**

Regularly check that your sources are keeping up:

```mzsql
-- Check source statistics
SELECT *
FROM mz_internal.mz_source_statistics
WHERE id = 'your_source_id';
```

## Prevention

**Best practices to avoid this error:**

- Set `max_slot_wal_keep_size` to a value appropriate for your workload
  (typically 5-10GB or more).
- Size your source clusters appropriately for your data ingestion rate.
- Avoid pausing clusters for extended periods when sources are active.
- Monitor replication lag regularly.
- Consider limiting initial snapshot size by using `FOR TABLES` instead of
  `FOR ALL TABLES` if you have very large databases.
- If using a managed PostgreSQL provider, verify their replication slot and WAL
  retention policies.

## Provider-specific considerations

### Neon

Neon has been observed to have more aggressive WAL cleanup policies. If you're
using Neon:

- Monitor replication lag more frequently.
- Consider using a dedicated Neon branch for replication.
- Contact Neon support about their replication slot retention policies.

### Amazon RDS

RDS respects `max_slot_wal_keep_size` but also has instance storage limits.
Ensure your RDS instance has adequate storage for WAL retention.

### Self-managed PostgreSQL

You have full control over WAL retention settings, but ensure you also monitor
disk space to prevent storage issues.

<!-- mz-docs page: ingest-data/postgres/source-versioning -->

# Handle upstream schema changes
How to add a column, drop a column, or drop a constraint in your source PostgreSQL database, without any downtime in Materialize
> **Public Preview:** This feature is in public preview.

> **Note:** - Changing column types is currently unsupported.

Materialize allows you to handle certain types of upstream
table schema changes seamlessly, specifically:

- Adding a column in the upstream database.
- Dropping a column in the upstream database.
- Dropping a `PRIMARY KEY` or `UNIQUE` constraint in the upstream database.

This guide walks you through how to handle these changes without any downtime in Materialize.

## Prerequisites

Some familiarity with Materialize. If you've never used Materialize before,
start with our [guide to getting started](/get-started/quickstart/).

### Set up a PostgreSQL database

For this guide, setup a PostgreSQL 11+ database. In your PostgreSQL, create a
table `T` and populate:

```sql
CREATE TABLE T (
    A INT,
    CONSTRAINT t_pkey PRIMARY KEY (A)
);

INSERT INTO T (A) VALUES
    (10);
```

### Connect your source database to Materialize

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

## Create a source using the new syntax

In Materialize, create a source using the updated [`CREATE SOURCE`
syntax](/sql/create-source/postgres-v2/).

```sql
CREATE SOURCE IF NOT EXISTS my_source
    FROM POSTGRES CONNECTION my_connection (PUBLICATION 'mz_source');
```

Unlike the [legacy syntax](/sql/create-source/postgres/), the new syntax does
not include the `FOR [[ALL] TABLES|SCHEMAS]` clause; i.e., the new syntax does
not create corresponding subsources in Materialize automatically. Instead, the
new syntax requires a separate [`CREATE TABLE ... FROM
SOURCE`](/sql/create-table/), which will create the corresponding tables and
start the snapshotting process. See [Create a table from the
source](#create-a-table-from-the-source).

> **Note:** The [legacy syntax](/sql/create-source/postgres/) is still supported. However,
> the legacy syntax doesn't support upstream schema changes.

## Create a table from the source
To start ingesting specific tables from your source database, you can create a
table in Materialize. We'll add it into the v1 schema in Materialize.

```sql
CREATE SCHEMA v1;

CREATE TABLE v1.T
    FROM SOURCE my_source(REFERENCE public.T);
```

Once you've created a table from source, the [initial
snapshot](/ingest-data/#snapshotting) of table `v1.T` will begin.

> **Note:** During the snapshotting, the data ingestion for the existing tables for the same
> source is temporarily blocked. As such, if possible, you can resize the cluster
> to speed up the snapshotting process and once the process finishes, resize the
> cluster for steady-state. You can monitor the snapshot progress on the overview
> page for the source in the Materialize console.

## Create a view on top of the table.

For this guide, add a materialized view `matview` (also in schema `v1`) that
sums column `A` from table `T`.

```sql
CREATE MATERIALIZED VIEW v1.matview AS
    SELECT SUM(A) from v1.T;
```

## Handle upstream column addition

### A. Add a column in your upstream PostgreSQL database

In your upstream PostgreSQL database, add a new column `B` to the table `T`:

```sql
ALTER TABLE T
    ADD COLUMN B BOOLEAN DEFAULT false;

INSERT INTO T (A, B) VALUES
    (20, true);
```

This operation will have no immediate effect in Materialize. In Materialize,
`v1.T` will continue to ingest only column `A`. The materialized view
`v1.matview` will continue to have access to column `A` as well.

### B. Incorporate the new column in Materialize

To incorporate the new column into Materialize, create a new `v2` schema and
recreate the table in the new schema:

```sql
CREATE SCHEMA v2;

CREATE TABLE v2.T
    FROM SOURCE my_source(REFERENCE public.T);
```

The [snapshotting](/ingest-data/#snapshotting) of table `v2.T` will begin.
`v2.T` will include columns `A` and `B`.

> **Note:** During the snapshotting, the data ingestion for the existing tables for the same
> source is temporarily blocked. As such, if possible, you can resize the cluster
> to speed up the snapshotting process and once the process finishes, resize the
> cluster for steady-state. You can monitor the snapshot progress on the overview
> page for the source in the Materialize console.

When the new `v2.T` table has finished snapshotting, create a new materialized
view `matview` in the new schema.  Since the new `v2.matview` is referencing the
new `v2.T`, it can reference column `B`:

```sql {hl_lines="4"}
CREATE MATERIALIZED VIEW v2.matview AS
    SELECT SUM(A)
    FROM v2.T
    WHERE B = true;
```

## Handle upstream column drop

### A. Exclude the column in Materialize

To drop a column safely, in Materialize, first, create a new `v3` schema, and
recreate table `T` in the new schema but exclude the column to drop. In this
example, we'll drop the column B.

```sql
CREATE SCHEMA v3;
CREATE TABLE v3.T
    FROM SOURCE my_source(REFERENCE public.T) WITH (EXCLUDE COLUMNS (B));
```

> **Note:** During the snapshotting, the data ingestion for the existing tables for the same
> source is temporarily blocked. As such, if possible, you can resize the cluster
> to speed up the snapshotting process and once the process finishes, resize the
> cluster for steady-state. You can monitor the snapshot progress on the overview
> page for the source in the Materialize console.

### B. Drop a column in your upstream PostgreSQL database

In your upstream PostgreSQL database, drop the column `B` from the table `T`:

```sql
ALTER TABLE T DROP COLUMN B;
```

Dropping the column B will have no effect on `v3.T`. However, the drop affects
`v2.T` and `v2.matview` from our earlier examples. When the user attempts to
read from either, Materialize will report an error that the source table schema
has been altered.

## Handle upstream constraint drop

> **Public Preview:** This feature is in public preview.

Materialize ignores the following constraints: foreign key, `CHECK`, and
`EXCLUSION`. As such, you can add or drop them without affecting ingestion.
To handle changes in `PRIMARY KEY`, `UNIQUE`, and `NOT NULL` constraints,
follow the steps below.

### A. Exclude the constraint in Materialize

To drop a `PRIMARY KEY`, `UNIQUE`, or `NOT NULL` constraint, in Materialize,
first, create a new `v4` schema, and recreate table `T` in the new schema but
exclude the constraint to drop. In this example, we'll drop the primary key
`t_pkey`. The constraint name is a string literal and must match the upstream
name exactly, including case.

```sql
CREATE SCHEMA v4;
CREATE TABLE v4.T
    FROM SOURCE my_source(REFERENCE public.T) WITH (EXCLUDE CONSTRAINTS ('t_pkey'));
```

Materialize does not record the excluded constraint as a key of `v4.T`.

`EXCLUDE CONSTRAINTS` only accepts `PRIMARY KEY` and `UNIQUE` constraint
names. A `NOT NULL` constraint on a specific column cannot be excluded by
name. To drop a `NOT NULL` constraint safely, use `EXCLUDE ALL CONSTRAINTS`
instead, which records no constraints at all: the table has no keys and every
column is nullable, so any later constraint drop is safe.

```sql
CREATE SCHEMA v4;
CREATE TABLE v4.T
    FROM SOURCE my_source(REFERENCE public.T) WITH (EXCLUDE ALL CONSTRAINTS);
```

> **Note:** During the snapshotting, the data ingestion for the existing tables for the same
> source is temporarily blocked. As such, if possible, you can resize the cluster
> to speed up the snapshotting process and once the process finishes, resize the
> cluster for steady-state. You can monitor the snapshot progress on the overview
> page for the source in the Materialize console.

### B. Drop the constraint in your upstream PostgreSQL database

In your upstream PostgreSQL database, drop the constraint `t_pkey` from the
table `T`:

```sql
ALTER TABLE T DROP CONSTRAINT t_pkey;
```

Dropping the constraint will have no effect on `v4.T`. However, the drop affects
`v3.T` from our earlier example, which still records `t_pkey` as a key. When the
user attempts to read from it, Materialize will report an error that the
constraint was dropped upstream.

<!-- mz-docs page: ingest-data/postgres/troubleshooting -->

# Troubleshooting
Troubleshooting guides for PostgreSQL source errors in Materialize
This section contains troubleshooting guides for specific errors you may
encounter when using PostgreSQL sources in Materialize. These guides focus on
errors that are unique to the PostgreSQL replication workflow, including issues
with replication slots, WAL management, and other CDC-specific scenarios.

For general data ingestion troubleshooting that applies to all source types, see
the main [Troubleshooting](/ingest-data/troubleshooting/) guide. For answers to
common questions about PostgreSQL sources, see the [FAQ](/ingest-data/postgres/faq/).

## Troubleshooting guides

| Guide | Description |
|-------|-------------|
| [Slot overcompacted](/ingest-data/postgres/slot-overcompacted/) | Resolve errors when PostgreSQL removes WAL data before Materialize can read it |
| [Connection Closed](/ingest-data/postgres/connection-closed/) | Resolve unexpected networking connection terminations between Materialize and PostgreSQL |
| [Replication slot is active](/ingest-data/postgres/replication-slot-active/) | Resolve errors when Materialize attempts to use a replication slot that is already in use by another active connection |

<!-- mz-docs page: ingest-data/redpanda -->

# Redpanda

Get details about using Materialize with Redpanda

[//]: # "TODO(morsapaes) The Kafka guides need to be rewritten for consistency
with the Postgres ones. We should include spill to disk in the guidance then."

Because [Redpanda](https://www.redpanda.com/) is Kafka API-compatible,
Materialize can process data from it in the same way it processes data from
Kafka sources.

> **Tip:** For help getting started with your own data, you can schedule a [free guided
> trial](https://materialize.com/demo/?utm_campaign=General&utm_source=documentation).

## Configuration

Two configuration parameters that are enabled by default in Kafka need to be
enabled explicitly in Redpanda:

```nofmt
--set redpanda.enable_transactions=true
--set redpanda.enable_idempotence=true
```

For more information on general Redpanda configuration, see the
[Redpanda documentation](https://docs.redpanda.com/home/).

## Supported versions

Materialize supports **Redpanda 24.1+** and is compatible with most common Redpanda hosted services. This includes [all officially supported versions of Redpanda](https://support.redpanda.com/hc/en-us/articles/20617574366743-Redpanda-Supported-Versions).

## Related pages

- [`CREATE SOURCE`](/sql/create-source/kafka/)
- [`CREATE SINK`](/sql/create-sink/)

<!-- mz-docs page: ingest-data/redpanda/redpanda-cloud -->

# Redpanda Cloud
How to securely connect a Redpanda Cloud cluster as a source to Materialize.
[//]: # "TODO(morsapaes) The Kafka guides need to be rewritten for consistency
with the Postgres ones."

This guide goes through the required steps to connect Materialize to a Redpanda
Cloud cluster. If you already have a Redpanda Cloud cluster up and running,
skip straight to [Step 2](#step-2-create-a-user).

> **Tip:** For help getting started with your own data, you can schedule a [free guided
> trial](https://materialize.com/demo/?utm_campaign=General&utm_source=documentation).

## Step 1. Create a Redpanda Cloud cluster

> **Note:** Once created, provisioning a Dedicated Redpanda Cloud cluster can take up to 40 minutes.
> Serverless clusters are provisioned in a few minutes.

1. Sign in to the [Redpanda Cloud console](https://cloud.redpanda.com/).

1. Create a new namespace or select an existing one where you want to create the cluster.

1. Choose the type of cluster you want to create.

1. Enter a cluster name, and specify the rest of the settings based on your
needs.

1. Click **Next** and select the network settings for your cluster.

1. Next, click **Create** to create the cluster.

## Step 2. Create a user

1. Navigate to the [Redpanda Cloud console](https://cloud.redpanda.com/).

1. Choose the Redpanda cluster you created in **Step 1**.

1. Click on the **Security** tab.

1. In the **Security** section, choose **Create User**.

1. Specify a name and a password along with the SASL Mechanism
for the user and click **Create**.

Take note of the user you just created, as well as the password and the SASL Mechanism you chose;
you'll need them later on. Keep in mind that the password contains sensitive information, and you
should store it somewhere safe!

## Step 3. Create an Access Control List

1. Next, still in the **Security** section, click on the **ACL** tab.

1. Click **Add ACL**,

1. Choose the **User** you just created.

1. Choose the **Read** and **Write** permissions for the **Topics** section.

1. You can grant access on a per-topic basis, but you can also choose to grant
access to all topics by adding a `*` in the **Topics ID** input field.

1. Click **Create**.

## Step 4. Create a topic

To start using Materialize with Redpanda, you need to point it to an existing
Redpanda topic you want to read data from. If the topic you want to ingest
already exists, you can skip this step.

Otherwise, you can install Redpanda Keeper (aka `rpk`) on the client machine
from the previous step to create a topic. For guidance on how to use `rpk`,
check the [Redpanda documentation](https://docs.redpanda.com/docs/reference/rpk-commands/#rpk-topic-create).

## Step 5. Create a connection

Now that you’ve configured your Redpanda cluster, you can start ingesting data
into Materialize. The exact steps depend on your networking configuration, so
start by selecting the relevant option.

**Public cluster:**

1. Open the [Redpanda Cloud console](https://cloud.redpanda.com/) and select your cluster.

1. Click on **Overview**

1. Copy the URL under **Cluster hosts**. This will be your
`<redpanda-broker-url>` going forward.

1. In the Materialize [SQL shell](/developer-tools/console/), or your
preferred SQL client, create a connection with your Redpanda Cloud cluster
access and authentication details using the [`CREATE CONNECTION`](/sql/create-connection/)
command:

    ```mzsql
      -- The credentials of your Redpanda Cloud user.
      CREATE SECRET redpanda_username AS '<your-username>';
      CREATE SECRET redpanda_password AS '<your-password>';

      CREATE CONNECTION rp_connection TO KAFKA (
          BROKER '<redpanda-broker-url>',
          SASL MECHANISMS = 'SCRAM-SHA-256', -- The SASL mechanism you chose in Step 2.
          SASL USERNAME = SECRET redpanda_username,
          SASL PASSWORD = SECRET redpanda_password
      );
    ```

**Use AWS PrivateLink (Cloud-only):**

[AWS PrivateLink](https://aws.amazon.com/privatelink/) lets you connect
Materialize to your Redpanda Cloud instance without exposing traffic to the
public internet. To use AWS PrivateLink, your Redpanda cluster must be deployed
in a region supported by Materialize: `us-east-1`,`us-west-2`, or `eu-west-1`.

1. **Enable PrivateLink in your Redpanda Cloud cluster.**

    Alter your cluster to enable PrivateLink with an empty `allowed_principals`
    field using the template script below. Make sure to record the PrivateLink
    service name.

    **Note:** This can take up to 15 minutes. You can re-run the script (or just
      the `GET` request) periodically until it resolves.

    ```bash
    PUBLIC_API_ENDPOINT="https://api.cloud.redpanda.com"
    REGION=US-EAST-1
    CLOUD_CLIENT_ID="<your-redpanda-client-id>"
    <CLOUD_CLIENT_SECRET>="<your-redpanda-client-secret>"
    CLUSTER_ID="<your-redpanda-cluster-id>"

    <AUTH_TOKEN>=$(
      curl -s -X POST 'https://auth.prd.cloud.redpanda.com/oauth/token' \
             -H 'content-type: application/x-www-form-urlencoded' \
             -d grant_type=client_credentials \
             -d client_id=$CLOUD_CLIENT_ID \
             -d client_secret=<CLOUD_CLIENT_SECRET> \
             -d audience=cloudv2-production.redpanda.cloud | jq .access_token | sed 's/"//g'
    )

    CLUSTER_PATCH_BODY="$(cat <<EOF
     {
       "aws_private_link": {
         "enabled": true,
         "allowed_principals": [ ]
       }
     }
    EOF
    )"

    curl -X PATCH \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer <AUTH_TOKEN>" \
       -d "$CLUSTER_PATCH_BODY" \
        $PUBLIC_API_ENDPOINT/v1beta2/clusters/$CLUSTER_ID

    curl -X GET \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer <AUTH_TOKEN>" \
        $PUBLIC_API_ENDPOINT/v1beta2/clusters/$CLUSTER_ID | jq \
        '.cluster.aws_private_link'
    ```

1. In the Materialize [SQL shell](/developer-tools/console/), or your
preferred SQL client, create a [PrivateLink connection](/ingest-data/network-security/privatelink/)
using the service name from the previous step. Be sure to specify **all
availability zones** of your Redpanda Cloud cluster.

    ```mzsql
    CREATE CONNECTION rp_privatelink TO AWS PRIVATELINK (
      SERVICE NAME 'com.amazonaws.vpce.us-east-1.vpce-svc-abcdefghijk',
      AVAILABILITY ZONES ('use1-az4','use1-az1','use1-az2')
    );
    ```

1. Retrieve the AWS principal for the AWS PrivateLink connection you just
created:

    ```mzsql
    SELECT principal
    FROM mz_aws_privatelink_connections plc
    JOIN mz_connections c ON plc.id = c.id
    WHERE c.name = 'rp_privatelink';
    ```
    <p></p>

    ```
                                     principal
    ---------------------------------------------------------------------------
     arn:aws:iam::664411391173:role/mz_20273b7c-2bbe-42b8-8c36-8cc179e9bbc3_u1
    ```

1. Patch your Redpanda Cloud cluster to accept connections from the AWS
principal:

    ```bash
    PUBLIC_API_ENDPOINT="https://api.cloud.redpanda.com"
    REGION=US-EAST-1
    CLOUD_CLIENT_ID="<your-redpanda-client-id>"
    <CLOUD_CLIENT_SECRET>="<your-redpanda-client-secret>"
    CLUSTER_ID="<your-redpanda-cluster-id>"

    MATERIALIZE_CONNECTION_ARN="<arn-created-for-materialize-aws-privatelink-connection>"

    <AUTH_TOKEN>=$(
    curl -s -X POST 'https://auth.prd.cloud.redpanda.com/oauth/token' \
           -H 'content-type: application/x-www-form-urlencoded' \
           -d grant_type=client_credentials \
           -d client_id=$CLOUD_CLIENT_ID \
           -d client_secret=<CLOUD_CLIENT_SECRET> \
           -d audience=cloudv2-production.redpanda.cloud | jq .access_token | sed 's/"//g'
    )

    CLUSTER_PATCH_BODY="$(cat <<EOF
     {
       "aws_private_link": {
         "enabled": true,
         "allowed_principals": ["$MATERIALIZE_CONNECTION_ARN"]
       }
     }
    EOF
    )"

    curl -X PATCH \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer <AUTH_TOKEN>" \
       -d "$CLUSTER_PATCH_BODY" \
       $PUBLIC_API_ENDPOINT/v1beta2/clusters/$CLUSTER_ID
    ```

1. In Materialize, validate the AWS PrivateLink connection you created using the
[`VALIDATE CONNECTION`](/sql/validate-connection) command:

    ```mzsql
    VALIDATE CONNECTION rp_privatelink;
    ```

    If no validation error is returned, move to the next step.

    This can take several minutes, and report errors like `Error: Endpoint cannot be
    discovered` while the policies are being updated and the endpoint resources are
    being re-evaluated. If the validation errors persist for longer than 10
    minutes, double-check the ARNs and service names and [contact our team](/support/).

1. Finally, create a connection to your Redpanda Cloud cluster using the AWS
Privatelink connection you created earlier:

    ```mzsql
    -- The credentials of your Redpanda Cloud user.
    CREATE SECRET redpanda_username AS '<your-username>';
    CREATE SECRET redpanda_password AS '<your-password>';

    CREATE CONNECTION rp_connection TO KAFKA (
        AWS PRIVATELINK rp_privatelink (PORT 30292)
        SASL MECHANISMS = 'SCRAM-SHA-256', -- The SASL mechanism you chose in Step 2.
        SASL USERNAME = SECRET redpanda_username,
        SASL PASSWORD = SECRET redpanda_password
    );
    ```

## Step 6. Start ingesting data

Once you have created the connection, you can use the connection in the [`CREATE
SOURCE`](/sql/create-source/) command to your Redpanda Cloud cluster and start
ingesting data from your target topic. By default, the source will be created in
the active cluster; to use a different cluster, use the `IN CLUSTER` clause.

**Legacy Syntax:**

With the legacy syntax, the source decodes the topic directly and is itself
queryable. Picking up an upstream schema change requires dropping and recreating
the source, which incurs downtime.

```mzsql
CREATE SOURCE rp_source
    FROM KAFKA CONNECTION redpanda_cloud (TOPIC '<topic-name>')
    FORMAT JSON;
```

**New Syntax:**

With the new syntax, create a source for the topic and then a table that decodes
it. Each table pins its own reader schema, which lets you pick up upstream schema
changes without downtime. For details, see [Handle upstream schema changes with
zero downtime](/ingest-data/kafka/source-versioning/).

```mzsql
CREATE SOURCE rp_source
    FROM KAFKA CONNECTION redpanda_cloud (TOPIC '<topic-name>');

CREATE TABLE rp_table
    FROM SOURCE rp_source
    FORMAT JSON;
```

<!-- mz-docs page: ingest-data/sql-server -->

# SQL Server

Connecting Materialize to a SQL Server database for Change Data Capture (CDC).

## Ingest from SQL Server via change data capture

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

### Supported versions

Materialize supports replicating data from SQL Server 2016 or higher with Change
Data Capture (CDC) support.

### Integration guides

- [Azure SQL Database](/ingest-data/sql-server/azure-db/)
- [Self-hosted SQL Server](/ingest-data/sql-server/self-hosted/)

## Supported data types

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

### Timestamp rounding

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

## How ingestion from SQL Server works

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
| Dropping an excluded column | No impact. |
| [Adding a column](#adding-a-column) | Handled automatically. Materialize keeps ingesting the existing columns; incorporate the new column with a new table (current syntax) or by re-adding the subsource (legacy syntax). |
| [Dropping an ingested column](#dropping-a-column) | Table enters an error state. Re-create the table. |
| [Renaming an ingested column](#renaming-a-column) | Table enters an error state. Re-create the table. |
| Any [`ALTER COLUMN`](#changing-a-columns-data-type) (type, collation, sparseness, masking, nullability) | Table enters an error state. Re-create the table. |
| Dropping a `UNIQUE` constraint | Table enters an error state. Re-create the table. |
| [Disabling CDC on a table](#disabling-cdc-on-a-table) (`sys.sp_cdc_disable_table`) | Table enters an error state. Drop and re-create just that table; the rest of the source keeps replicating. |
| [Removing the in-use capture instance](#removing-a-capture-instance) | Table enters an error state. Re-create the table. |
| [Dropping or renaming a table, or moving it to another schema](#table-level-operations) | Table enters an error state. Re-create the table. |

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

### Disabling CDC on a table

Running `sys.sp_cdc_disable_table` removes the capture instance Materialize is
ingesting from, which puts the affected table into an error state. The other
tables in the source keep replicating. You can recover without re-creating the
whole source by dropping just the affected table in Materialize:

```mzsql
DROP TABLE table_1;
```

Then re-create it, optionally after re-enabling CDC on the upstream table with
`sys.sp_cdc_enable_table`.

### Table-level operations

The following upstream operations put the affected table into an error state.
Ingestion for that table stops, and you must drop and recreate the affected
table in Materialize to resume:

- Dropping a table (`DROP TABLE`).
- Renaming a table or moving it to a different schema.

## Supported database operations

The following table summarizes how Materialize handles operational events on
the upstream SQL Server database. See the details below the table for the
error text and any required configuration.

| Operation | Resolution |
| --- | --- |
| Restarting or patching SQL Server (including OS-level restarts) | Supported automatically. |
| Restarting Materialize | Supported automatically. |
| Transient network interruptions between Materialize and SQL Server | Supported automatically. |
| Taking the database `OFFLINE` and back `ONLINE` | Supported automatically. |
| Toggling `SINGLE_USER`/`MULTI_USER` or `READ_ONLY`/`READ_WRITE` | Supported automatically. |
| Data-file, filegroup, or index maintenance that rewrites data in place | Supported automatically. |
| [Availability group failover](#always-on-failovers) | Supported automatically, with a configuration change. |
| [Point-in-time restore](#point-in-time-restore) | Requires re-creating the source. |
| [CDC disabled at the database level](#cdc-disabled-at-the-database-level) | Requires re-creating the source. |
| [Change-table retention](#change-table-retention) exceeded during an outage | Requires re-creating the source. |

### Operations that do not require re-creating the source
For operations that are supported automatically, Materialize is able to resume
replication from a [log sequence number
(LSN)](https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-transaction-log-architecture-and-management-guide)
that it tracks as it consumes the upstream change data capture (CDC) change
tables. Because LSNs live in the SQL Server transaction log, they survive
routine operational events: after a transient interruption the source stalls,
then resumes from its last committed LSN and catches up automatically. **No
action is required** for the operations in the first section below.

The source recovers on its own. It will briefly reports a `stalled` status while the
condition persists, then returns to `running` and catch up for all of the
following scenarios:

- Restarting or patching SQL Server (including OS-level restarts).
- Restarting Materialize. The source resumes from its tracked LSN and does
  **not** re-snapshot already-ingested data.
- Transient network interruptions between Materialize and SQL Server.
- Taking the database `OFFLINE` and back `ONLINE`.
- Toggling the database between `SINGLE_USER`/`MULTI_USER` or
  `READ_ONLY`/`READ_WRITE` (for example, during patching).
- Data-file, filegroup, or index maintenance that rewrites data in place.
- [Availability group failover](#always-on-failovers), with the
  configuration change described below.

> **Note:** Recovery after an interruption depends on the required LSNs still being present
> in the SQL Server CDC change tables. If the interruption lasts longer than the
> CDC **retention period** (3 days by default) and SQL Server's cleanup job
> removes change-table rows past the source's resume point, the source can no
> longer recover on its own. See [Change-table retention](#change-table-retention).

> **Warning:** If a maintenance script places the database into `SINGLE_USER` mode, note that an
> active Materialize source's reconnection attempts can occupy the single available
> connection and cause `ALTER DATABASE ... SET MULTI_USER` to fail with error 5064.
> Terminate the Materialize session (or use `SET MULTI_USER WITH ROLLBACK
> IMMEDIATE` after terminating it) before returning the database to multi-user
> mode.

### Operations that require re-creating the source
A smaller set of events breaks LSN or CDC-change-table continuity. When this
happens, Materialize cannot guarantee a correct, gap-free view of your data, so
it puts the **entire source** into an error state that requires **re-creating**
the source. Re-creating triggers a fresh [snapshot](/ingest-data/#snapshotting)
and rehydration of dependent objects. Upstream changes to an individual table's
schema are handled separately, and do not error the entire source.

The following events put the **entire source** into an error state. In each
case, the remediation is to drop and re-create the source:

```mzsql
DROP SOURCE mz_source CASCADE;

CREATE SOURCE mz_source
  FROM SQL SERVER CONNECTION sql_server_connection;

-- Re-create the tables you were ingesting.
CREATE TABLE table_1 FROM SOURCE mz_source (REFERENCE dbo.table_1);
```

#### Point-in-time restore

Restoring the source database from a backup — including restoring to a different
server for disaster recovery — is detected as a discontinuity. The source fails
with an error of the form:

```
source must be dropped and recreated due to failure: Restore history id changed
from None to Some(<n>)
```

Materialize detects the restore by reading `msdb.dbo.restorehistory`. (This check
does not apply to Azure SQL Database, which does not expose `msdb`.)

#### CDC disabled at the database level

Running `sys.sp_cdc_disable_db` drops all change tables. The source stalls with:

```
invalid SQL Server system setting 'database CDC'. Expected 'true'. Got 'Some(false)'.
```

Re-enable CDC on the database and on each table (`sys.sp_cdc_enable_db`,
`sys.sp_cdc_enable_table`), then re-create the source.

#### Change-table retention

SQL Server's CDC cleanup job removes change-table rows older than the retention
period (3 days by default). If Materialize is disconnected long enough that
cleanup removes rows past the source's resume LSN, the source stalls with:

```
the requested LSN '...' is less than the minimum '...' for `dbo_<table>`
```

To avoid this during a planned outage, keep the outage shorter than the retention
period, or increase retention beforehand with
[`sys.sp_cdc_change_job`](https://learn.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sys-sp-cdc-change-job-transact-sql)
(`@job_type = 'cleanup'`, `@retention`).

### Always-On failovers

Materialize supports SQL Server configured with Always On availability groups,
including failover between replicas, with one configuration change.

By default, an availability group failover is misdetected as a point-in-time
restore and fails the source with the `Restore history id changed` error
described above. This is a false positive: the LSN stream is continuous across an
availability group failover, but seeding a secondary replica writes rows to
`msdb.dbo.restorehistory`, which the restore-detection check reads as a restore.

To allow the source to survive failover, disable restore-history validation with
the [`sql_server_source_validate_restore_history`](/sql/alter-system-set/) system
parameter:

```mzsql
ALTER SYSTEM SET sql_server_source_validate_restore_history = false;
```

> **Warning:** Disabling this check is a trade-off: with it off, Materialize will also **not**
> detect a genuine [point-in-time restore](#point-in-time-restore) of the source
> database. Only disable it when the source connects to a database that fails over
> between availability group replicas.

With the check disabled, the source no longer fails on failover. Because `msdb`
is per-instance, the CDC capture and cleanup jobs do not move with the
availability group database — after a failover, confirm that CDC is healthy on
the new primary (the capture and cleanup jobs exist, SQL Server Agent is running,
and the change tables are advancing) so that replication continues. Adding the
jobs on a replica that lacks them is done with
[`sys.sp_cdc_add_job`](https://learn.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sys-sp-cdc-add-job-transact-sql).

<!-- mz-docs page: ingest-data/sql-server/azure-db -->

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

1. In the [SQL Shell](/developer-tools/console/), or your preferred SQL
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

    1. In the [SQL Shell](/developer-tools/console/), or your preferred
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

In Materialize, a [cluster](/fundamentals/concepts/clusters/) is an isolated
environment, similar to a virtual warehouse in Snowflake. When you create a
cluster, you choose the size of its compute resource allocation based on the
work you need the cluster to do, whether ingesting data from a source,
computing always-up-to-date query results, serving results to clients, or a
combination.

In this case, you'll create a dedicated cluster for ingesting source data from
your SQL Server database.

1. In the [SQL Shell](/developer-tools/console/), or your preferred SQL
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

1. In the [SQL Shell](/developer-tools/console/), or your preferred SQL
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

1. In the [SQL Shell](/developer-tools/console/), or your preferred SQL
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
    echo "ssh-ed25519 AAAA...76RH materialize" >> <AUTHORIZED_KEYS_FILE>
    echo "ssh-ed25519 AAAA...hLYV materialize" >> <AUTHORIZED_KEYS_FILE>
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

- Check out the [tools and integrations](/developer-tools/integrations/) supported by
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

### Timestamp rounding

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

### Adding a table to an existing source

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

### Disabling CDC on a table

Running `sys.sp_cdc_disable_table` removes the capture instance Materialize is
ingesting from, which puts the affected table into an error state. The other
tables in the source keep replicating. You can recover without re-creating the
whole source by dropping just the affected table in Materialize:

```mzsql
DROP TABLE table_1;
```

Then re-create it, optionally after re-enabling CDC on the upstream table with
`sys.sp_cdc_enable_table`.

### Table-level operations

The following upstream operations put the affected table into an error state.
Ingestion for that table stops, and you must drop and recreate the affected
table in Materialize to resume:

- Dropping a table (`DROP TABLE`).
- Renaming a table or moving it to a different schema.


<!-- mz-docs page: ingest-data/sql-server/self-hosted -->

# Ingest data from self-hosted SQL Server
How to stream data from self-hosted SQL Server database to Materialize
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

1. In the [SQL Shell](/developer-tools/console/), or your preferred SQL
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

    1. In the [SQL Shell](/developer-tools/console/), or your preferred
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

In Materialize, a [cluster](/fundamentals/concepts/clusters/) is an isolated
environment, similar to a virtual warehouse in Snowflake. When you create a
cluster, you choose the size of its compute resource allocation based on the
work you need the cluster to do, whether ingesting data from a source,
computing always-up-to-date query results, serving results to clients, or a
combination.

In this case, you'll create a dedicated cluster for ingesting source data from
your SQL Server database.

1. In the [SQL Shell](/developer-tools/console/), or your preferred SQL
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

1. In the [SQL Shell](/developer-tools/console/), or your preferred SQL
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
1. In the [SQL Shell](/developer-tools/console/), or your preferred SQL
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

1. In the [SQL Shell](/developer-tools/console/), or your preferred SQL
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
    echo "ssh-ed25519 AAAA...76RH materialize" >> <AUTHORIZED_KEYS_FILE>
    echo "ssh-ed25519 AAAA...hLYV materialize" >> <AUTHORIZED_KEYS_FILE>
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

- Check out the [tools and integrations](/developer-tools/integrations/) supported by
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

### Timestamp rounding

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

### Adding a table to an existing source

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

### Disabling CDC on a table

Running `sys.sp_cdc_disable_table` removes the capture instance Materialize is
ingesting from, which puts the affected table into an error state. The other
tables in the source keep replicating. You can recover without re-creating the
whole source by dropping just the affected table in Materialize:

```mzsql
DROP TABLE table_1;
```

Then re-create it, optionally after re-enabling CDC on the upstream table with
`sys.sp_cdc_enable_table`.

### Table-level operations

The following upstream operations put the affected table into an error state.
Ingestion for that table stops, and you must drop and recreate the affected
table in Materialize to resume:

- Dropping a table (`DROP TABLE`).
- Renaming a table or moving it to a different schema.


<!-- mz-docs page: ingest-data/sql-server/source-versioning -->

# Handle upstream schema changes
How to add a column, or drop a column, from your source SQL Server database, without any downtime in Materialize
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

<!-- mz-docs page: ingest-data/striim -->

# Striim Cloud
How to ingest Striim Change Data Capture (CDC) data into Materialize using the Kafka source
[Striim](https://www.striim.com/) is a real-time data integration platform that
offers a variety of connectors for databases, messaging systems, and other data
sources. This guide walks through the steps to ingest Striim Change Data
Capture (CDC) into Materialize using the [Kafka source](/sql/create-source/kafka/).

## Before you begin

Integrating Striim Cloud with Materialize requires using a message broker (like
Apache Kafka) and a schema registry (like Confluent Schema Registry) configured
for Avro schema management.

Ensure that you have:

- An active [Striim account](https://go2.striim.com/free-trial) and [Striim Cloud service](https://www.striim.com/docs/en/create-a-striim-cloud-service.html).
- A Kafka cluster up and running with access to a Confluent Schema Registry
  service.

## Step 1. Configure Striim CDC

### Database configuration

Follow Striim's guidance to enable and configure CDC from your source relational
database:

   * [Oracle Database CDC guide](https://www.striim.com/docs/en/oracle-database-cdc.html).
   * [SQL Server CDC guide](https://www.striim.com/docs/en/sql-server-cdc.html).

### Kafka writer configuration

1. In Striim, create a [`KafkaWriter`](https://www.striim.com/docs/en/kafka-writer.html)
   using the version that corresponds to your target Kafka broker.

1. Select the writer created in the previous step as the **Input stream**.

1. Configure the Kafka broker details and the target topic name.

   1. Under **Advanced settings > Kafka Config**, add the
      `value.serializer=io.confluent.kafka.serializers.KafkaAvroSerializer`
      configuration to serialize records using the [Confluent wire format](https://docs.confluent.io/platform/current/schema-registry/fundamentals/serdes-develop/index.html#wire-format).

   1. Add a `MESSAGE KEY` field to specify the primary key of the table. This
      will configure the `KafkaWriter` to use the table’s primary key as the Kafka
      message key.

### Schema registry configuration

1. From the **Formatter** dropdown menu, select `AvroFormatter` to serialize records using the [Avro](https://avro.apache.org/) format.

1. Configure the Schema Registry URL, and its authentication credentials
(if necessary).

1. Set the format to `Table`.

1. Leave the **Schema Registry Subject Name** and **Schema Registry Subject Name
Mapping** fields empty.

### Known limitations

#### Supported types

Some data types might not be correctly supported in Striim's Avro handling (e.g.
[`bigint`](https://community.striim.com/product-q-a-6/suitable-avro-type-not-found-for-field-error-when-using-mysql-striim-kafka-125)).
If you run into Avro serialization issues with the `KafkaWriter`, please reach
out to [Striim support](https://striim.zendesk.com/) or the [Striim community](https://community.striim.com/community).

<br>

Once your Striim Cloud service is configured for CDC, **start the app** to begin
streaming changes from your source relational database into the specified Kafka
cluster. Next, you'll configure Materialize to consume this data.

## Step 2. Start ingesting data

> **Note:** If you are prototyping and already have a cluster to host your Kafka source
> (e.g. `quickstart`), you don't need to create a new cluster. For production
> scenarios, we recommend separating your workloads into multiple clusters for
> [resource isolation](/sql/create-cluster/#resource-isolation).

1. In the [SQL Shell](/developer-tools/console/), or your preferred SQL
   client connected to Materialize, use the [`CREATE CONNECTION`](/sql/create-connection/)
   command to create connection objects with access and authentication details
   to your Kafka cluster and schema registry:

   ```mzsql
    CREATE SECRET kafka_password AS '<your-password>';
    CREATE SECRET csr_password AS '<your-password>';

    CREATE CONNECTION kafka_connection TO KAFKA (
        BROKER '<broker-url>',
        SECURITY PROTOCOL = 'SASL_PLAINTEXT',
        SASL MECHANISMS = 'SCRAM-SHA-256', -- or `PLAIN` or `SCRAM-SHA-512`
        SASL USERNAME = '<your-username>',
        SASL PASSWORD = SECRET kafka_password
        SSH TUNNEL ssh_connection
    );

    CREATE CONNECTION csr_connection TO CONFLUENT SCHEMA REGISTRY (
        URL '<schema-registry-url>',
        USERNAME = '<your-username>',
        PASSWORD = SECRET csr_password
    );
    ```

1. Use the [`CREATE SOURCE`](/sql/create-source/kafka/) command to connect
   Materialize to your Kafka broker and schema registry using the connections you
   created in the previous step.

   ```mzsql
   CREATE SOURCE src
     FROM KAFKA CONNECTION kafka_connection (TOPIC '<topic-name>')
     KEY FORMAT TEXT
     VALUE FORMAT AVRO USING CONFLUENT SCHEMA REGISTRY CONNECTION csr_connection
     VALUE STRATEGY ID <id>
   ENVELOPE UPSERT;
   ```

   **Fetching the `VALUE STRATEGY ID`**

   Striim uses nonstandard subject names in the schema registry, which prevents
   Materialize from finding the schema using the default configuration. You
   must manually fetch and add the schema identifier. To get this value,
   open a terminal and use the following command:

   ```bash
   curl <schema-registry-url>:8081/subjects/<schema-name>/versions/latest | jq .id
   ```

## Related pages

- [`CREATE SECRET`](/sql/create-secret)
- [`CREATE CONNECTION`](/sql/create-connection/)
- [`CREATE SOURCE`: Kafka](/sql/create-source/kafka/)

<!-- mz-docs page: ingest-data/troubleshooting -->

# Troubleshooting
How to troubleshoot common data ingestion scenarios where Materialize is not working as expected.
As you wire up data ingestion in Materialize, you might run into some snags or
unexpected scenarios. This guide collects common questions around data ingestion
to help you troubleshoot your sources. See also [Monitoring data
ingestion](/ingest-data/monitoring-data-ingestion/)

If you're looking for troubleshooting guidance for slow or unresponsive queries,
check out the [`Transform data`
troubleshooting](/serve-results/troubleshooting) guide instead.

> **Tip:** For help getting started with your own data, you can schedule a [free guided
> trial](https://materialize.com/demo/?utm_campaign=General&utm_source=documentation).

## Why isn't my source ingesting data?

First, check the status of your source in the Materialize console by navigating
to https://console.materialize.com/, clicking the **Sources** tab in the
navigation bar, and clicking the affected source.

Alternatively, you can get this information from the system catalog by querying
the [`mz_source_statuses`](/sql/system-catalog/mz_internal/#mz_source_statuses)
table:

```mzsql
SELECT * FROM mz_internal.mz_source_statuses
WHERE name = <SOURCE_NAME>;
```

| Status        | Description/recommendation                                                                                                                                             |
|---------------|---------------------------------------------------------------------------------------------------------------------------------------------------------|
| `paused`      | Source is running on a cluster with 0 replicas. To resolve this, [increase the replication factor](/sql/alter-cluster/#replication-factor-1) of the cluster.                                                                                                          |
| `stalled` | You likely have a configuration issue. The returned `error` field will provide more details.                                                     |
| `failed` | You likely have a configuration issue. The returned `error` field will provide more details.                                                     |
| `starting`    | If this status persists for more than a few minutes, [reach out to our team](http://materialize.com/convert-account/) for support.      |
| `running`     | If your source is in a `running` state but you are not receiving data when you query the source, the source may still be ingesting its initial snapshot. See [Has my source ingested its initial snapshot?](#has-my-source-ingested-its-initial-snapshot). |

## Has my source ingested its initial snapshot?

[//]: # "This page as a whole (as well as some of our other troubleshooting
    pages) can undergo a rewrite since the page is a bit of troubleshooting/faq.
    That is, the troubleshooting might relate to 'why is my query not returning'
    and the answer is check if the source is still snapshotting.  For now, just
    tweaking the changes made for this PR and will address how to rework this
    page in the future."

While a source is [snapshotting](/ingest-data/#snapshotting), the source (and the associated subsources)
cannot serve queries. That is, queries issued to the snapshotting source (and
its subsources) will return after the snapshotting completes (unless the user
breaks out of the query).

Snapshotting can take anywhere from a few minutes to several hours, depending on the size of your dataset,
the upstream database, the number of tables (more tables can be parallelized in Postgres), and the [size of your ingestion cluster](/sql/create-cluster/#available-sizes).

We've observed the following approximate snapshot rates from PostgreSQL:
| Cluster Size | Snapshot Rate |
|--------------|---------------|
| 25 cc | ~20 MB/s |
| 100 cc | ~50 MB/s |
| 800 cc | ~200 MB/s |

To determine whether your source has completed ingesting the initial snapshot,
you can query the [`mz_source_statistics`](/sql/system-catalog/mz_internal/#mz_source_statistics)
system catalog table:

```mzsql
SELECT snapshot_committed
FROM mz_internal.mz_source_statistics
WHERE id = <SOURCE_ID>;
```

You generally want to aggregate the `snapshot_committed` field across all worker
threads, as done in the above query. The snapshot is only considered committed
for the source as a whole once all worker threads have committed their
components of the snapshot.

Even if your source has not yet committed its initial snapshot, you can still
monitor its progress. See [Monitoring data ingestion](/ingest-data/monitoring-data-ingestion/).

## How do I speed up the snapshotting process?

Snapshotting can take anywhere from a few minutes to several hours, depending on the size of your dataset,
the upstream database, the number of tables (more tables can be parallelized in Postgres), and the [size of your ingestion cluster](/sql/create-cluster/#available-sizes).

We've observed the following approximate snapshot rates from PostgreSQL:
| Cluster Size | Snapshot Rate |
|--------------|---------------|
| 25 cc | ~20 MB/s |
| 100 cc | ~50 MB/s |
| 800 cc | ~200 MB/s |

To speed up the snapshotting process, you can scale up the [size of the cluster
](/sql/alter-cluster/#alter-cluster-size) used for snapshotting, then scale it
back down once the snapshot completes.

```sql
ALTER CLUSTER <cluster_name> SET ( SIZE = <new_size> );
```

> **Note:** Resizing a cluster with sources requires the cluster to restart. This operation
> incurs downtime for the duration it takes for all objects in the cluster to
> [hydrate](/ingest-data/#hydration).
> You might want to let the new-sized replica hydrate before shutting down the
> current replica. See the [resizing
> process](/sql/alter-cluster/#resizing-process) about automating
> this process.

Once the initial snapshot has completed, you can resize the cluster for steady
state.

For upsert sources, a larger cluster can not only speed up snapshotting, but may
also be necessary to support increased memory usage during the process. For more
information, see [Use a larger cluster for upsert source
snapshotting](/ingest-data/#use-a-larger-cluster-for-upsert-source-snapshotting).

## Is the upstream database overloaded?

Snapshotting can put significant load on the upstream database (see [Impact
on upstream system](/fundamentals/concepts/snapshotting/#impact-on-upstream-system)).

Check the upstream database when a snapshot progresses more slowly than
expected, when applications sharing the database slow down while
it runs, or when the source reports upstream connection errors or timeouts.
The relevant metrics are in your cloud provider's monitoring console, or in
OS tools like `iostat` and the database's activity views for self-hosted
databases. Look for:

- **Read IOPS or throughput** flat at a provisioned cap.
- **CPU** pinned at the instance's limit for the duration of the snapshot.
- **Network throughput** at the instance type's cap.
- **Connections** near the database's limit. For PostgreSQL and MySQL
  sources, snapshotting opens connections in proportion to the source
  cluster's workers.

Also watch disk usage on the upstream database during a long-running
snapshot: CDC database sources must retain their change log until Materialize
consumes it (see [Impact on upstream
system](/fundamentals/concepts/snapshotting/#impact-on-upstream-system)).

If the database is overloaded, you can upsize the source database or cancel
the snapshot by dropping the source, and retry:

- on a smaller source cluster to spread the load over a longer window.
- with more IOPS, throughput, or instance capacity provisioned for the
  database.
- during off-peak hours when the database is less busy, as recommended in the
  [ingestion best practices](/ingest-data/#scheduling).
- with a smaller [volume of data to
  sync](/ingest-data/#limit-the-volume-of-data).

## Adding a new subsource to an existing source blocks replication. Should I just create a new source instead?

It depends. Materialize provides transactional guarantees for subsource of the
same source, not across different sources. So, if you need transactional
guarantees across the tables between the two sources, you cannot use a new
source. In addition, creating a new source means that you are reading the
replication stream twice.

To use the same source, consider resizing the cluster to speed up the
snapshotting process for the new subsource and once the process finishes, resize
the cluster for steady-state.

## See also

- [Monitoring data ingestion](/ingest-data/monitoring-data-ingestion/)
- [Postgres troubleshooting guides](/ingest-data/postgres/troubleshooting/)
- [MySQL troubleshooting guides](/ingest-data/mysql/troubleshooting/)

<!-- mz-docs page: ingest-data/webhooks/amazon-eventbridge -->

# Amazon EventBridge
How to stream data from Amazon EventBridge to Materialize using webhooks
This guide walks through the steps to ingest data from [Amazon EventBridge](https://aws.amazon.com/eventbridge/)
into Materialize using the [Webhook source](/sql/create-source/webhook/).

> **Tip:** For help getting started with your own data, you can schedule a [free guided
> trial](https://materialize.com/demo/?utm_campaign=General&utm_source=documentation).

## Before you begin

Ensure that you have:

- An [EventBridge-enabled Amazon Simple Storage Service (S3) bucket](https://docs.aws.amazon.com/AmazonS3/latest/user-guide/Welcome.html).

## Step 1. (Optional) Create a cluster

> **Note:** If you are prototyping and already have a cluster to host your webhook
> source (e.g. `quickstart`), **you can skip this step**. For production
> scenarios, we recommend separating your workloads into multiple clusters for
> [resource isolation](/sql/create-cluster/#resource-isolation).

To create a cluster in Materialize, use the [`CREATE CLUSTER` command](/sql/create-cluster):

```mzsql
CREATE CLUSTER webhooks_cluster (SIZE = '25cc');

SET CLUSTER = webhooks_cluster;
```

## Step 2. Create a secret

To validate requests between Amazon EventBridge and Materialize, you must create
a [secret](/sql/create-secret/):

```mzsql
CREATE SECRET eventbridge_webhook_secret AS '<secret_value>';
```

Change the `<secret_value>` to a unique value that only you know and store it in
a secure location.

## Step 3. Set up a webhook source

Using the secret from the previous step, create a [webhook source](/sql/create-source/webhook/)
in Materialize to ingest data from Amazon EventBridge. By default, the source
will be created in the active cluster; to use a different cluster, use the `IN
CLUSTER` clause.

```mzsql
CREATE SOURCE eventbridge_source
FROM WEBHOOK
  BODY FORMAT JSON
  -- Include all headers, but filter out the secret.
  INCLUDE HEADERS ( NOT 'x-mz-api-key' )
  CHECK (
    WITH ( HEADERS, SECRET eventbridge_webhook_secret AS validation_secret)
    -- The constant_time_eq validation function **does not support** fully
    -- qualified secret names. We recommend always aliasing the secret name
    -- for ease of use.
    constant_time_eq(headers->'x-mz-api-key', validation_secret)
  );
```

After a successful run, the command returns a `NOTICE` message containing the
unique [webhook URL](/sql/create-source/webhook/#webhook-url)
that allows you to `POST` events to the source. Copy and store it. You will need
it for the next step.

The URL will have the following format:

```
https://<HOST>/api/webhook/<database>/<schema>/<src_name>
```

If you missed the notice, you can find the URLs for all webhook sources in the
[`mz_internal.mz_webhook_sources`](/sql/system-catalog/mz_internal/#mz_webhook_sources)
system table.

### Access and authentication

> **Warning:** Without a `CHECK` statement, **all requests will be accepted**. To prevent bad
> actors from injecting data into your source, it is **strongly encouraged** that
> you define a `CHECK` statement with your webhook sources.

The above webhook source uses [basic authentication](https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#basic_authentication_scheme).
This enables a simple and rudimentary way to grant authorization to your webhook source.

### Throughput

If your throughput exceeds the [maximum request rate](/sql/create-source/webhook/#request-limits),
we recommend [batching multiple events](/sql/create-source/webhook/#handling-batch-events)
into a single request, for example using [EventBridge Pipes](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-pipes-batching-concurrency.html).

## Step 4. Create an API destination in Amazon EventBridge

[//]: # "TODO(morsapaes) This needs to be broken down into instructions, same as
the other guides."

For guidance on creating an API destination in Amazon EventBridge to connect to
Materialize, check out [this guide](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-tutorial-datadog.html).
Use the secret created in **Step 2.** as the **API key name** for request
validation.

## Step 5. Validate incoming data

With the source set up in Materialize and the API destination configured in
Amazon EventBridge, you can now query the incoming data:

1. [In the Materialize console](/developer-tools/console/), navigate to
   the **SQL Shell**.

1. Use SQL queries to inspect and analyze the incoming data:

    ```mzsql
    SELECT * FROM eventbridge_source LIMIT 10;
    ```

## Step 6. Transform incoming data

### JSON parsing

Webhook data is ingested as a JSON blob. We recommend creating a parsing view on
top of your webhook source that uses [`jsonb` operators](/sql/types/jsonb/#operators)
to map the individual fields to columns with the required data types.

Manually parsing JSON-formatted data in SQL can be tedious. You can use the [interactive JSON parser widget](https://materialize.com/docs/sql/types/jsonb/#parsing) to automatically turn a sample JSON payload into a parsing view with the individual fields mapped to columns.

### Timestamp handling

We highly recommend using the [`try_parse_monotonic_iso8601_timestamp`](/transform-data/patterns/temporal-filters/#temporal-filter-pushdown)
function when casting from `text` to `timestamp`, which enables [temporal filter
pushdown](/transform-data/patterns/temporal-filters/#temporal-filter-pushdown).

### Deduplication

With the vast amount of data processed and potential network issues, it's not
uncommon to receive duplicate records. You can use the `DISTINCT ON` clause to
efficiently remove duplicates. For more details, refer to the webhook source
[reference documentation](/sql/create-source/webhook/#handling-duplicated-and-partial-events).

## Next steps

With Materialize ingesting your Amazon EventBridge data, you can start exploring it,
computing real-time results that stay up-to-date as new data arrives, and
serving results efficiently. For more details, check out the
[Amazon EventBridge documentation](https://docs.aws.amazon.com/eventbridge/) and the
[webhook source reference documentation](/sql/create-source/webhook/).

<!-- mz-docs page: ingest-data/webhooks/change-included-headers -->

# Change a webhook source's included headers
Use ALTER SCHEMA ... SWAP WITH to change which headers a webhook source exposes, without changing the endpoint URL your senders use.
A webhook source fixes its column shape when you create it, including which
request headers it exposes through [`INCLUDE HEADER` /
`INCLUDE HEADERS`](/sql/create-source/webhook/#exposing-headers). You cannot alter
the header configuration of an existing webhook source in place. To change it,
create a new source with the header configuration you want in a separate schema,
then swap it into place with [`ALTER SCHEMA ...
SWAP WITH`](/sql/alter-schema/). Because the swap only renames schemas,
the [webhook endpoint URL](/sql/create-source/webhook/#webhook-url) that your
senders post to stays the same.

> **Tip:** For help getting started with your own data, you can schedule a [free guided
> trial](https://materialize.com/demo/?utm_campaign=General&utm_source=documentation).

> **Warning:** Unlike a Kafka or database source, a webhook source has no upstream system to
> re-read. The replacement source starts **empty**: it only contains webhook calls
> received **after** the swap. Events delivered to the original source are **not**
> copied to the replacement, and are lost for good once you drop the original
> source. Only perform the swap when losing the original source's history is
> acceptable, or keep the original source around to continue querying its past
> data.

## How it works

The webhook endpoint URL is derived from the source's fully qualified name:

```
https://<HOST>/api/webhook/<database>/<schema>/<src_name>
```

Because the schema is part of the URL, building the replacement in a different
schema and then swapping the two schemas atomically leaves the original URL
resolving to the new source. Senders keep posting to the same URL, and downstream
objects keep referencing the same name.

## Before you begin

You need a Materialize account and a cluster to host the source. The examples
below use the `quickstart` cluster and omit the `CHECK` clause for brevity. In
production, always [validate requests](/sql/create-source/webhook/#validating-requests)
with a `CHECK` clause.

## Step 1. Create the initial source

Create the original source in a `prod` schema. This version exposes a single
`foo` header as its own column:

```mzsql
CREATE SCHEMA prod;

CREATE SOURCE prod.events
  IN CLUSTER quickstart
  FROM WEBHOOK
  BODY FORMAT JSON
  INCLUDE HEADER 'foo' AS foo;
```

The source has a `foo` column alongside the `body`:

Column | Type    | Nullable?
-------|---------|-----------
 body  | `jsonb` | No
 foo   | `text`  | Yes

Point your webhook sender at
`https://<HOST>/api/webhook/materialize/prod/events`. Incoming events accumulate
in `prod.events`.

## Step 2. Create the replacement with the new header configuration

Suppose you now want to expose **all** headers except a sensitive `bar` header,
rather than only `foo`. Build the replacement in a separate `staging` schema
using the `INCLUDE HEADERS ( NOT ... )` syntax:

```mzsql
CREATE SCHEMA staging;

CREATE SOURCE staging.events
  IN CLUSTER quickstart
  FROM WEBHOOK
  BODY FORMAT JSON
  INCLUDE HEADERS ( NOT 'bar' );
```

Instead of a single `foo` column, this version has a `headers` map column that
contains every header except `bar`:

Column  | Type                | Nullable?
--------|---------------------|-----------
 body   | `jsonb`             | No
 headers | `map[text => text]` | No

At this point nothing is posting to `staging.events` yet, so it is empty. Your
senders are still delivering to `prod.events`.

## Step 3. Swap the schemas

Swap the two schemas to cut over. The swap is atomic:

```mzsql
ALTER SCHEMA prod SWAP WITH staging;
```

After the swap:

- `prod.events` now resolves to the new source (the `headers` map version), so
  the unchanged endpoint URL `.../materialize/prod/events` and any downstream
  objects that reference `prod.events` immediately pick up the new shape.
- The original source now lives at `staging.events`, retaining the data it
  ingested before the swap.

New webhook calls to `prod.events` land in the new source and expose the
`headers` map. As noted in the warning above, the events that arrived before the
swap remain only in `staging.events` (the old source) and are **not** present in
the new `prod.events`.

## Step 4. Clean up

Once you have validated the cutover, drop the retired source. This permanently
discards the data it ingested before the swap:

```mzsql
DROP SCHEMA staging CASCADE;
```

If you need to preserve the original source's historical events, copy them into a
table or downstream object **before** dropping it, or leave the `staging` schema
in place and query it as needed.

## See also

- [`CREATE SOURCE: Webhook`](/sql/create-source/webhook/)
- [`ALTER SCHEMA ... SWAP WITH`](/sql/alter-schema/)
- [Webhooks quickstart](/ingest-data/webhooks/webhook-quickstart/)

<!-- mz-docs page: ingest-data/webhooks/hubspot -->

# HubSpot
How to stream data from HubSpot to Materialize using webhooks
This guide walks through the steps to ingest data from [HubSpot](https://www.hubspot.com/)
into Materialize using the [Webhook source](/sql/create-source/webhook/).

> **Tip:** For help getting started with your own data, you can schedule a [free guided
> trial](https://materialize.com/demo/?utm_campaign=General&utm_source=documentation).

### Before you begin

Ensure that you have:

- A HubSpot account with an [Operations Hub subscription](https://www.hubspot.com/pricing/operations).

## Step 1. (Optional) Create a cluster

> **Note:** If you are prototyping and already have a cluster to host your webhook
> source (e.g. `quickstart`), **you can skip this step**. For production
> scenarios, we recommend separating your workloads into multiple clusters for
> [resource isolation](/sql/create-cluster/#resource-isolation).

To create a cluster in Materialize, use the [`CREATE CLUSTER` command](/sql/create-cluster):

```mzsql
CREATE CLUSTER webhooks_cluster (SIZE = '25cc');

SET CLUSTER = webhooks_cluster;
```

## Step 2. Create a secret

To validate requests between HubSpot and Materialize, you must create a [secret](/sql/create-secret/):

```mzsql
CREATE SECRET hubspot_webhook_secret AS '<secret_value>';
```

Change the `<secret_value>` to a unique value that only you know and store it in
a secure location.

## Step 3. Set up a webhook source

Using the secret the previous step, create a [webhook source](/sql/create-source/webhook/)
in Materialize to ingest data from HubSpot. By default, the source will be
created in the active cluster; to use a different cluster, use the `IN
CLUSTER` clause.

```mzsql
CREATE SOURCE hubspot_source
  FROM WEBHOOK
    BODY FORMAT JSON
    CHECK (
      WITH (
        HEADERS,
        BODY AS body,
        SECRET hubspot_webhook_secret AS validation_secret
      )
      -- The constant_time_eq validation function **does not support** fully
      -- qualified secret names. We recommend always aliasing the secret name
      -- for ease of use.
      constant_time_eq(headers->'authorization', validation_secret)
);
```

After a successful run, the command returns a `NOTICE` message containing the
unique [webhook URL](/sql/create-source/webhook/#webhook-url)
that allows you to `POST` events to the source. Copy and store it. You will need
it for the next step.

The URL will have the following format:

```
https://<HOST>/api/webhook/<database>/<schema>/<src_name>
```

If you missed the notice, you can find the URLs for all webhook sources in the
[`mz_internal.mz_webhook_sources`](/sql/system-catalog/mz_internal/#mz_webhook_sources)
system table.

### Access and authentication

> **Warning:** Without a `CHECK` statement, **all requests will be accepted**. To prevent bad
> actors from injecting data into your source, it is **strongly encouraged** that
> you define a `CHECK` statement with your webhook sources.

The `CHECK` clause defines how to validate each request. At the time of writing,
HubSpot supports API key authentication, which you can use to validate
requests.

The above webhook source uses [basic authentication](https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#basic_authentication_scheme).
This enables a simple and rudimentary way to grant authorization to your webhook
source.

## Step 4. Create a webhook workflow in HubSpot

A [webhook in HubSpot](https://knowledge.hubspot.com/workflows/how-do-i-use-webhooks-with-hubspot-workflows)
is a workflow action that sends data to a webhook URL. You can create a webhook
workflow in HubSpot to send data to the webhook source you created in the
previous step.

1. In HubSpot, go to **Automation > Workflows**.

1. Click the **Name** of the workflow you want to add the webhook to, or create a new one.

1. Click the **+** icon to add an action.

1. In the right panel, search for **Send a webhook**.

1. Click the **Method** dropdown menu, then select `POST`.

1. Enter the URL from **Step 3.**.

1. Authenticate the request using the **API key** option. Use the secret created in **Step 2.**.

1. For the **API Key Name**, enter `authorization`. This is the key used in the `CHECK` clause of the webhook source.

1. Click **Save**.

## Step 5. Configure the request body in HubSpot

The request body is the data that HubSpot sends to the webhook URL. You can
configure the request body to send the data you want to ingest into
Materialize.

1. In HubSpot, go to the webhook workflow created in **Step 4.**.

1. Go to the **Request body** section, and click **Customize request body**.

1. In the **Request body** section, click **Add property**.

1. From the dropdown menu, select the property you want to send to Materialize.
   Repeat this step for each property you want to send to Materialize.

1. Click **Test Mapping** to validate that the webhook is working. If **Test Mapping** fails and throws a `failed to validate the request` error, this means that the secret is not correct. To fix this:

    1. In **HubSpot**, go to the webhook workflow.
    1. Go to the **Authentication** section.
    1. Enter the secret created in **Step 2.**.
    1. Verify that the **API Key Name** is `authorization`.
    1. Click **Save**.

1. After a succesful test, click **Save**.

## Step 6. Validate incoming data

With the source set up in Materialize and the webhook workflow configured in
HubSpot, you can now query the incoming data:

1. [In the Materialize console](/developer-tools/console/), navigate to
   the **SQL Shell**.

1. Use SQL queries to inspect and analyze the incoming data:

    ```mzsql
    SELECT * FROM hubspot_source LIMIT 10;
    ```

## Step 7. Transform incoming data

### JSON parsing

Webhook data is ingested as a JSON blob. We recommend creating a parsing view on
top of your webhook source that uses [`jsonb` operators](/sql/types/jsonb/#operators)
to map the individual fields to columns with the required data types.

```mzsql
CREATE VIEW parse_hubspot AS SELECT
    body->>'city' AS city,
    body->>'firstname' AS firstname,
    body->>'ip_city' AS ip_city,
    -- Add all of the fields you want to ingest
FROM hubspot_source;
```

Manually parsing JSON-formatted data in SQL can be tedious. You can use the [interactive JSON parser widget](https://materialize.com/docs/sql/types/jsonb/#parsing) to automatically turn a sample JSON payload into a parsing view with the individual fields mapped to columns.

### Timestamp handling

We highly recommend using the [`try_parse_monotonic_iso8601_timestamp`](/transform-data/patterns/temporal-filters/#temporal-filter-pushdown)
function when casting from `text` to `timestamp`, which enables [temporal filter
pushdown](/transform-data/patterns/temporal-filters/#temporal-filter-pushdown).

### Deduplication

With the vast amount of data processed and potential network issues, it's not
uncommon to receive duplicate records. You can use the `DISTINCT ON` clause to
efficiently remove duplicates. For more details, refer to the webhook source
[reference documentation](/sql/create-source/webhook/#handling-duplicated-and-partial-events).

## Next steps

With Materialize ingesting your HubSpot data, you can start exploring it,
computing real-time results that stay up-to-date as new data arrives, and
serving results efficiently. For more details, check out the
[HubSpot documentation](https://knowledge.hubspot.com/workflows/how-do-i-use-webhooks-with-hubspot-workflows) and the
[webhook source reference documentation](/sql/create-source/webhook/).

<!-- mz-docs page: ingest-data/webhooks/rudderstack -->

# RudderStack
How to stream data from RudderStack to Materialize using webhooks
This guide walks through the steps to ingest data from [RudderStack](https://rudderstack.com/)
into Materialize using the [Webhook source](/sql/create-source/webhook/).

> **Tip:** For help getting started with your own data, you can schedule a [free guided
> trial](https://materialize.com/demo/?utm_campaign=General&utm_source=documentation).

## Before you begin

Ensure that you have:

- A RudderStack [account](https://app.rudderstack.com/signup)
- A RudderStack [source](https://www.rudderstack.com/docs/sources/overview/) set up and running.

## Step 1. (Optional) Create a cluster

> **Note:** If you are prototyping and already have a cluster to host your webhook
> source (e.g. `quickstart`), **you can skip this step**. For production
> scenarios, we recommend separating your workloads into multiple clusters for
> [resource isolation](/sql/create-cluster/#resource-isolation).

To create a cluster in Materialize, use the [`CREATE CLUSTER` command](/sql/create-cluster):

```mzsql
CREATE CLUSTER webhooks_cluster (SIZE = '25cc');

SET CLUSTER = webhooks_cluster;
```

## Step 2. Create a secret

To validate requests between Rudderstack and Materialize, you must create a [secret](/sql/create-secret/):

```mzsql
CREATE SECRET rudderstack_webhook_secret AS '<secret_value>';
```

Change the `<secret_value>` to a unique value that only you know and store it in a secure location.

## Step 3. Set up a webhook source

Using the secret from the previous step, create a [webhook source](/sql/create-source/webhook/)
in Materialize to ingest data from RudderStack. By default, the source will be
created in the active cluster; to use a different cluster, use the `IN
CLUSTER` clause.

```mzsql
CREATE SOURCE rudderstack_source
  FROM WEBHOOK
    BODY FORMAT JSON
    CHECK (
      WITH (
        HEADERS,
        BODY AS request_body,
        SECRET rudderstack_webhook_secret AS validation_secret
      )
      -- The constant_time_eq validation function **does not support** fully
      -- qualified secret names. We recommend always aliasing the secret name
      -- for ease of use.
      constant_time_eq(headers->'authorization', validation_secret)
);
```

After a successful run, the command returns a `NOTICE` message containing the
unique [webhook URL](/sql/create-source/webhook/#webhook-url)
that allows you to `POST` events to the source. Copy and store it. You will need
it for the next step.

The URL will have the following format:

```
https://<HOST>/api/webhook/<database>/<schema>/<src_name>
```

If you missed the notice, you can find the URLs for all webhook sources in the
[`mz_internal.mz_webhook_sources`](/sql/system-catalog/mz_internal/#mz_webhook_sources)
system table.

### Access and authentication

> **Warning:** Without a `CHECK` statement, **all requests will be accepted**. To prevent bad
> actors from injecting data into your source, it is **strongly encouraged** that
> you define a `CHECK` statement with your webhook sources.

The above webhook source uses [basic authentication](https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#basic_authentication_scheme).
This enables a simple and rudimentary way to grant authorization to your webhook source.

## Step 4. Create a webhook destination in RudderStack

To configure the webhook endpoint as a destination in RudderStack, follow the
steps outlined below:

1.  **Select your RudderStack source**

    Identify the source you wish to add a webhook endpoint to. If you don't have
    a source set up, follow the steps outlined in the Rudderstack
    [Getting Started](https://www.rudderstack.com/docs/dashboard-guides/sources/) guide.

1.  **Add a webhook destination and connect it to the Rudderstack source**
    1. Navigate to the **Add Destination** menu.
    1. Select the **Webhook** option.
    1. Assign a name to your destination and click **Continue**.

#### Connection settings

On the **Connection Settings** page:

- **Webhook URL**: Define the endpoint where events will be dispatched by RudderStack. Use the URL from **Step 3.**.

- **URL method**: Use the `POST` method to send events to Materialize.

- **Headers**: These headers get added to the RudderStack request sent to your webhook. For this setup, ensure that the following headers are added:

    - `Content-Type`: `application/json`
    - `Authorization`: Use the secret created in **Step 2.**.

## Step 5. Validate incoming data

With the source set up in Materialize and the webhook destination configured in
Rudderstack, you can now query the incoming data:

1. [In the Materialize console](/developer-tools/console/), navigate to
   the **SQL Shell**.

1. Use SQL queries to inspect and analyze the incoming data:

    ```mzsql
    SELECT * FROM rudderstack_source LIMIT 10;
    ```

    If you don't see any data, head over to the [RudderStack console](https://app.rudderstack.com/)
    and try to sync your source to trigger a new data ingestion.

## Step 6. Transform incoming data

### JSON parsing

Webhook data is ingested as a JSON blob. We recommend creating a parsing view on
top of your webhook source that uses [`jsonb` operators](/sql/types/jsonb/#operators)
to map the individual fields to columns with the required data types.

```mzsql
CREATE VIEW json_parsed AS
  SELECT
    (body -> '_metadata' ->> 'nodeVersion')::text AS nodeVersion,
    (body ->> 'channel')::text AS channel,
    (body ->> 'event')::text AS event,
    (body ->> 'userId')::text AS userId
  FROM rudderstack_source;
```

Manually parsing JSON-formatted data in SQL can be tedious. You can use the [interactive JSON parser widget](https://materialize.com/docs/sql/types/jsonb/#parsing) to automatically turn a sample JSON payload into a parsing view with the individual fields mapped to columns.

### Timestamp handling

We highly recommend using the [`try_parse_monotonic_iso8601_timestamp`](/transform-data/patterns/temporal-filters/#temporal-filter-pushdown)
function when casting from `text` to `timestamp`, which enables [temporal filter
pushdown](/transform-data/patterns/temporal-filters/#temporal-filter-pushdown).

### Deduplication

With the vast amount of data processed and potential network issues, it's not
uncommon to receive duplicate records. You can use the `DISTINCT ON` clause to
efficiently remove duplicates. For more details, refer to the webhook source
[reference documentation](/sql/create-source/webhook/#handling-duplicated-and-partial-events).

## Next steps

With Materialize ingesting your Rudderstack data, you can start exploring it,
computing real-time results that stay up-to-date as new data arrives, and
serving results efficiently. For more details, check out the
[Rudderstack documentation](https://rudderstack.com/docs/) and the
[webhook source reference documentation](/sql/create-source/webhook/).

