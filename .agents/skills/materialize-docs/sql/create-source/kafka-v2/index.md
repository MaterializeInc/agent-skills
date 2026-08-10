# CREATE SOURCE: Kafka/Redpanda (New Syntax)
Connecting Materialize to a Kafka or Redpanda broker using the new source syntax
> **Disambiguation:** This page reflects the new syntax. For the legacy syntax, see the [old reference page](/sql/create-source/kafka/).

Creates a new source from Kafka or Redpanda broker.  Once a new source is created, you can <a href="/sql/create-table/kafka" ><code>CREATE TABLE FROM SOURCE</code></a>
to create the corresponding tables in Materialize and start the data ingestion
process.

The decoding options (`FORMAT`, `INCLUDE`, and `ENVELOPE`) are set on the
[`CREATE TABLE ... FROM SOURCE`](/sql/create-table/kafka) statement that reads
from the source. For the full catalog of formats, envelopes, and exposed
metadata, see [CREATE TABLE: Kafka source table](/sql/create-table/kafka/).

> **Note:** The same syntax, supported formats and features can be used to connect to a
> [Redpanda](/integrations/redpanda/) broker.

## Prerequisites

To create a source from Kafka/Redpanda broker, you first need to [create a
connection](/sql/create-connection/#kafka). Once created, a connection is
**reusable** across multiple `CREATE SOURCE` and `CREATE SINK` statements.

## Syntax

The `CREATE SOURCE` statement connects to a Kafka/Redpanda topic.

```mzsql
CREATE SOURCE [IF NOT EXISTS] <src_name>
[IN CLUSTER <cluster_name>]
FROM KAFKA CONNECTION <connection_name> (
  TOPIC '<topic>'
  [, GROUP ID PREFIX '<group_id_prefix>']
  [, START OFFSET ( <partition_offset> [, ...] ) ]
  [, START TIMESTAMP <timestamp> ]
)
[EXPOSE PROGRESS AS <progress_subsource_name>]
[WITH ( <with_option> [, ...] )];

```

| Syntax element | Description |
| --- | --- |
| `<src_name>` | The name for the source.  |
| **IF NOT EXISTS** | Optional. If specified, do not throw an error if a source with the same name already exists. Instead, issue a notice and skip the source creation.  |
| **IN CLUSTER** `<cluster_name>` | Optional. The [cluster](/sql/create-cluster) to maintain this source.  |
| `<connection_name>` | The name of the Kafka connection to use in the source. For details on creating connections, check the [`CREATE CONNECTION`](/sql/create-connection) documentation page.  |
| `'<topic>'` | The Kafka topic you want to subscribe to.  |
| **GROUP ID PREFIX** `<group_id_prefix>` | Optional. The prefix of the consumer group ID to use. See [Monitoring consumer lag](#monitoring-consumer-lag).<br>Default: `materialize-{REGION-ID}-{CONNECTION-ID}-{SOURCE_ID}`  |
| **START OFFSET** (`<partition_offset>` [, ...]) | Optional. Read partitions from the specified offset. You cannot update the offsets once a source has been created; you will need to recreate the source. Offset values must be zero or positive integers. See [Setting start offsets](#setting-start-offsets) for details.  |
| **START TIMESTAMP** `<timestamp>` | Optional. Use the specified value to set `START OFFSET` based on the Kafka timestamp. Negative values will be interpreted as relative to the current system time in milliseconds (e.g. `-1000` means 1000 ms ago). See [Time-based offsets](#time-based-offsets) for details.  |
| **EXPOSE PROGRESS AS** `<progress_subsource_name>` | Optional. The name of the progress collection for the source. If this is not specified, the progress collection will be named `<src_name>_progress`. See [Monitoring source progress](#monitoring-source-progress) for details.  |
| **WITH** (`<with_option>` [, ...]) | Optional. The following `<with_option>`s are supported:  \| Option \| Description \| \|--------\|-------------\| \| `RETAIN HISTORY FOR <retention_period>` \| ***Private preview.** This option has known performance or stability issues and is under active development.* Duration for which Materialize retains historical data, which is useful to implement [durable subscriptions](/transform-data/patterns/durable-subscriptions/#history-retention-period). Accepts positive [interval](/sql/types/interval/) values (e.g. `'1hr'`). Default: `1s`. \| \| `TIMESTAMP INTERVAL [=] <interval>` \| The interval at which timestamps are assigned to data read from this source. Accepts positive [interval](/sql/types/interval/) values (e.g. `'500ms'`, `'1s'`). The value must be between the system parameters `min_timestamp_interval` and `max_timestamp_interval`. Default: the value of the `default_timestamp_interval` system parameter (`1s`). The interval can also be changed after creation with [`ALTER SOURCE`](/sql/alter-source/). \|  |

## Details

### Ingesting data

After the source is created, each [`CREATE TABLE ... FROM
SOURCE`](/sql/create-table/kafka/) statement creates a table that decodes the
topic and starts ingesting data. You can create multiple tables from the same
source, each with its own format and envelope.

### Handling schema changes

Because each table pins its own reader schema when it is created, you can pick up
a [compatible upstream schema
change](https://avro.apache.org/docs/++version++/specification/#schema-resolution)
without downtime: create a new table that reads the evolved schema, recreate the
downstream objects, and swap them into place. See [Handle upstream schema changes
with zero downtime](/ingest-data/kafka/source-versioning/) for the full
procedure.

## Features

### Setting start offsets

To start consuming a Kafka stream from a specific offset, you can use the `START
OFFSET` option.

```mzsql
CREATE SOURCE kafka_offset
  FROM KAFKA CONNECTION kafka_connection (
    TOPIC 'data',
    -- Start reading from the earliest offset in the first partition,
    -- the second partition at 10, and the third partition at 100.
    START OFFSET (0, 10, 100)
  );
```

Note that:

- If fewer offsets than partitions are provided, the remaining partitions will
  start at offset 0. This is true if you provide `START OFFSET (1)` or `START
  OFFSET (1, ...)`.

- Providing more offsets than partitions is not supported.

#### Time-based offsets

It's also possible to set a start offset based on Kafka timestamps, using the
`START TIMESTAMP` option. This approach sets the start offset for each
available partition based on the Kafka timestamp and the source behaves as if
`START OFFSET` was provided directly.

It's important to note that `START TIMESTAMP` is a property of the source: it
will be calculated _once_ at the time the `CREATE SOURCE` statement is issued.
This means that the computed start offsets will be the **same** for all views
depending on the source and **stable** across restarts.

If you need to limit the amount of data maintained as state after source
creation, consider using [temporal filters](/sql/patterns/temporal-filters/)
instead.

### Monitoring source progress

By default, Kafka sources expose progress metadata as a subsource that you can
use to monitor source **ingestion progress**. The name of the progress
subsource can be specified when creating a source using the `EXPOSE PROGRESS
AS` clause; otherwise, it will be named `<src_name>_progress`.

The following metadata is available for each source as a progress subsource:

Field          | Type                                     | Meaning
---------------|------------------------------------------|--------
`partition`    | `numrange`                               | The upstream Kafka partition.
`offset`       | [`uint8`](/sql/types/uint/#uint8-info)   | The greatest offset consumed from each upstream Kafka partition.

And can be queried using:

```mzsql
SELECT
  partition, "offset"
FROM
  (
    SELECT
      -- Take the upper of the range, which is null for non-partition rows
      -- Cast partition to u64, which is more ergonomic
      upper(partition)::uint8 AS partition, "offset"
    FROM
      <src_name>_progress
  )
WHERE
  -- Remove all non-partition rows
  partition IS NOT NULL;
```

As long as any offset continues increasing, Materialize is consuming data from
the upstream Kafka broker. For more details on monitoring source ingestion
progress and debugging related issues, see [Troubleshooting](/ops/troubleshooting/).

### Monitoring consumer lag

To support Kafka tools that monitor consumer lag, Kafka sources commit offsets
once the messages up through that offset have been durably recorded in
Materialize's storage layer.

However, rather than relying on committed offsets, Materialize suggests using
our native [progress monitoring](#monitoring-source-progress), which contains
more up-to-date information.

> **Note:** Some Kafka monitoring tools may indicate that Materialize's consumer groups have
> no active members. This is **not a cause for concern**.
> Materialize does not participate in the consumer group protocol nor does it
> recover on restart by reading the committed offsets. The committed offsets are
> provided solely for the benefit of Kafka monitoring tools.

Committed offsets are associated with a consumer group specific to the source.
The ID of the consumer group consists of the prefix configured with the [`GROUP
ID PREFIX` option](#syntax) followed by a Materialize-generated
suffix.

You should not make assumptions about the number of consumer groups that
Materialize will use to consume from a given source. The only guarantee is that
the ID of each consumer group will begin with the configured prefix.

The consumer group ID prefix for each Kafka source in the system is available in
the `group_id_prefix` column of the [`mz_kafka_sources`] table. To look up the
`group_id_prefix` for a source by name, use:

```mzsql
SELECT group_id_prefix
FROM mz_internal.mz_kafka_sources ks
JOIN mz_sources s ON s.id = ks.id
WHERE s.name = '<src_name>'
```

For spilling to disk, see the [Features section of the Kafka/Redpanda reference
page](/sql/create-source/kafka/#spilling-to-disk). This feature is configured on
the `CREATE SOURCE` statement and behaves the same regardless of syntax.

## Examples

### Prerequisite: Creating a connection

A connection describes how to connect and authenticate to an external system you
want Materialize to read data from.

Once created, a connection is **reusable** across multiple `CREATE SOURCE`
statements. For more details on creating connections, check the
[`CREATE CONNECTION`](/sql/create-connection) documentation page.

#### Broker

**SSL:**
```mzsql
CREATE SECRET kafka_ssl_key AS '<BROKER_SSL_KEY>';
CREATE SECRET kafka_ssl_crt AS '<BROKER_SSL_CRT>';

CREATE CONNECTION kafka_connection TO KAFKA (
    BROKER 'unique-jellyfish-0000.us-east-1.aws.confluent.cloud:9093',
    SSL KEY = SECRET kafka_ssl_key,
    SSL CERTIFICATE = SECRET kafka_ssl_crt
);
```

**SASL:**

```mzsql
CREATE SECRET kafka_password AS '<BROKER_PASSWORD>';

CREATE CONNECTION kafka_connection TO KAFKA (
    BROKER 'unique-jellyfish-0000.us-east-1.aws.confluent.cloud:9092',
    SASL MECHANISMS = 'SCRAM-SHA-256',
    SASL USERNAME = 'foo',
    SASL PASSWORD = SECRET kafka_password
);
```

If your Kafka broker is not exposed to the public internet, you can [tunnel the connection](/sql/create-connection/#network-security-connections)
through an AWS PrivateLink service (Materialize Cloud) or an SSH bastion host:

**AWS PrivateLink (Materialize Cloud):**

> **Note:** Connections using AWS PrivateLink is for Materialize Cloud only.

```mzsql
CREATE CONNECTION privatelink_svc TO AWS PRIVATELINK (
    SERVICE NAME 'com.amazonaws.vpce.us-east-1.vpce-svc-0e123abc123198abc',
    AVAILABILITY ZONES ('use1-az1', 'use1-az4')
);
```

```mzsql
CREATE CONNECTION kafka_connection TO KAFKA (
    BROKERS (
        'broker1:9092' USING AWS PRIVATELINK privatelink_svc,
        'broker2:9092' USING AWS PRIVATELINK privatelink_svc (PORT 9093)
    )
);
```

For step-by-step instructions on creating AWS PrivateLink connections and
configuring an AWS PrivateLink service to accept connections from Materialize,
check [this guide](/ops/network-security/privatelink/).

**SSH tunnel:**

```mzsql
CREATE CONNECTION ssh_connection TO SSH TUNNEL (
    HOST '<SSH_BASTION_HOST>',
    USER '<SSH_BASTION_USER>',
    PORT <SSH_BASTION_PORT>
);
```

```mzsql
CREATE CONNECTION kafka_connection TO KAFKA (
BROKERS (
    'broker1:9092' USING SSH TUNNEL ssh_connection,
    'broker2:9092' USING SSH TUNNEL ssh_connection
    )
);
```

For step-by-step instructions on creating SSH tunnel connections and configuring
an SSH bastion server to accept connections from Materialize, check [this guide](/ops/network-security/ssh-tunnel/).

#### Confluent Schema Registry

**SSL:**
```mzsql
CREATE SECRET csr_ssl_crt AS '<CSR_SSL_CRT>';
CREATE SECRET csr_ssl_key AS '<CSR_SSL_KEY>';
CREATE SECRET csr_password AS '<CSR_PASSWORD>';

CREATE CONNECTION csr_connection TO CONFLUENT SCHEMA REGISTRY (
    URL 'https://unique-jellyfish-0000.us-east-1.aws.confluent.cloud:9093',
    SSL KEY = SECRET csr_ssl_key,
    SSL CERTIFICATE = SECRET csr_ssl_crt,
    USERNAME = 'foo',
    PASSWORD = SECRET csr_password
);
```

**Basic HTTP Authentication:**
```mzsql
CREATE SECRET IF NOT EXISTS csr_username AS '<CSR_USERNAME>';
CREATE SECRET IF NOT EXISTS csr_password AS '<CSR_PASSWORD>';

CREATE CONNECTION csr_connection TO CONFLUENT SCHEMA REGISTRY (
  URL '<CONFLUENT_REGISTRY_URL>',
  USERNAME = SECRET csr_username,
  PASSWORD = SECRET csr_password
);
```

If your Confluent Schema Registry server is not exposed to the public internet,
you can [tunnel the connection](/sql/create-connection/#network-security-connections)
through an AWS PrivateLink service (Materialize Cloud) or an SSH bastion host:

**AWS PrivateLink (Materialize Cloud):**

> **Note:** Connections using AWS PrivateLink is for Materialize Cloud only.

```mzsql
CREATE CONNECTION privatelink_svc TO AWS PRIVATELINK (
    SERVICE NAME 'com.amazonaws.vpce.us-east-1.vpce-svc-0e123abc123198abc',
    AVAILABILITY ZONES ('use1-az1', 'use1-az4')
);
```

```mzsql
CREATE CONNECTION csr_connection TO CONFLUENT SCHEMA REGISTRY (
    URL 'http://my-confluent-schema-registry:8081',
    AWS PRIVATELINK privatelink_svc
);
```

For step-by-step instructions on creating AWS PrivateLink connections and
configuring an AWS PrivateLink service to accept connections from Materialize,
check [this guide](/ops/network-security/privatelink/).

**SSH tunnel:**
```mzsql
CREATE CONNECTION ssh_connection TO SSH TUNNEL (
    HOST '<SSH_BASTION_HOST>',
    USER '<SSH_BASTION_USER>',
    PORT <SSH_BASTION_PORT>
);
```

```mzsql
CREATE CONNECTION csr_connection TO CONFLUENT SCHEMA REGISTRY (
    URL 'http://my-confluent-schema-registry:8081',
    SSH TUNNEL ssh_connection
);
```

For step-by-step instructions on creating SSH tunnel connections and configuring
an SSH bastion server to accept connections from Materialize, check [this guide](/ops/network-security/ssh-tunnel/).

#### AWS Glue Schema Registry

An [AWS Glue Schema Registry connection](/sql/create-connection/#aws-glue-schema-registry)
authenticates through a separate [AWS connection](/sql/create-connection/#aws),
which supplies the credentials and region:

```mzsql
CREATE CONNECTION aws_connection TO AWS (
    ASSUME ROLE ARN = 'arn:aws:iam::123456789000:role/MaterializeGlue'
);

CREATE CONNECTION glue_connection TO AWS GLUE SCHEMA REGISTRY (
    AWS CONNECTION = aws_connection,
    REGISTRY = 'default-registry'
);
```

The AWS connection must be allowed to read schemas from the registry. See
[Permissions](/sql/create-connection/#glue-permissions) for the required IAM
actions.

### Create a source and table

```mzsql
CREATE SOURCE orders_src
  FROM KAFKA CONNECTION kafka_connection (TOPIC 'orders');

CREATE TABLE orders
  FROM SOURCE orders_src
  FORMAT AVRO USING CONFLUENT SCHEMA REGISTRY CONNECTION csr_connection
  ENVELOPE UPSERT;
```

For connection setup, required Kafka ACLs, and worked examples for each format,
see the [Kafka/Redpanda reference page](/sql/create-source/kafka/).

## Related pages

- [`CREATE TABLE`](/sql/create-table/)
- [`CREATE SECRET`](/sql/create-secret)
- [`CREATE CONNECTION`](/sql/create-connection)
- [CREATE SOURCE: Kafka/Redpanda (Legacy Syntax)](/sql/create-source/kafka/)
- [Handle upstream schema changes with zero downtime](/ingest-data/kafka/source-versioning/)
