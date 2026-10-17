# CREATE SOURCE

`CREATE SOURCE` connects Materialize to an external data source.

A source in Materialize represents an external data source. More concretely, it
specifies the connection and the ingestion configuration to use for a particular
external data source (e.g., PostgreSQL, Kafka). For those familiar with
PostgreSQL's foreign servers and foreign tables, a source is like a foreign
server, and the tables (or subsources) created from the source are like foreign
tables.

Before creating a source in Materialize, you must ensure that the external data
source is properly configured and accessible so that Materialize can establish a
connection and ingest its data. The exact configuration depends on the type of
data source.

## Syntax summary

<!--"Docs Note: Using include-example shortcode instead of include-syntax since only want the code snippet on this page."
-->

### New syntax

The new `CREATE SOURCE` syntax allows Materialize to handle certain upstream
schema changes, specifically adding or dropping columns, without downtime. It is
used in conjunction with the new [`CREATE TABLE ... FROM
SOURCE`](/sql/create-table/) syntax.

**PostgreSQL (New):**

To create a source from an external PostgreSQL:
```mzsql
CREATE SOURCE [IF NOT EXISTS] <source_name>
[IN CLUSTER <cluster_name>]
FROM POSTGRES CONNECTION <connection_name> (PUBLICATION '<publication_name>')
[WITH ( <with_option> [, ...] )]
;

```

For details, see [CREATE SOURCE: PostgreSQL (New Syntax)](/sql/create-source/postgres-v2/).

**MySQL (New):**

To create a source from an external MySQL database:
```mzsql
CREATE SOURCE [IF NOT EXISTS] <source_name>
[IN CLUSTER <cluster_name>]
FROM MYSQL CONNECTION <connection_name>
[WITH ( <with_option> [, ...] )]
;

```

For details, see [CREATE SOURCE: MySQL (New Syntax)](/sql/create-source/mysql-v2/).

**SQL Server (New):**

```mzsql
CREATE SOURCE [IF NOT EXISTS] <src_name>
[IN CLUSTER <cluster_name>]
FROM SQL SERVER CONNECTION <connection_name>
[WITH ( <with_option> [, ...] )]

```

For details, see [CREATE SOURCE: SQL Server (New Syntax)](/sql/create-source/sql-server-v2/).

**Kafka/Redpanda (New):**

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

For details, see [CREATE SOURCE: Kafka/Redpanda (New Syntax)](/sql/create-source/kafka-v2/).

**Webhook:**

```mzsql
CREATE SOURCE [IF NOT EXISTS] <src_name>
[IN CLUSTER <cluster_name>]
FROM WEBHOOK
  BODY FORMAT <TEXT | JSON [ARRAY] | BYTES>
  [INCLUDE HEADER <header_name> AS <column_alias> [BYTES] |
   INCLUDE HEADERS [ ( [NOT] <header_name> [, [NOT] <header_name> ... ] ) ]
  ][...]
  [CHECK (
      [WITH ( <BODY|HEADERS|SECRET <secret_name>> [AS <alias>] [BYTES] [, ...])]
      <check_expression>
    )
  ]

```

For details, see [CREATE SOURCE: Webhook](/sql/create-source/webhook/).

### Legacy syntax

The legacy `CREATE SOURCE` syntax requires downtime to handle upstream schema
changes. Prefer the [new syntax](#new-syntax) for new sources where available.

**PostgreSQL (Legacy):**

```mzsql
CREATE SOURCE [IF NOT EXISTS] <src_name>
[IN CLUSTER <cluster_name>]
FROM POSTGRES CONNECTION <connection_name> (
  PUBLICATION '<publication_name>'
  [, TEXT COLUMNS ( <col1> [, ...] ) ]
  [, EXCLUDE COLUMNS ( <col1> [, ...] ) ]
)
<FOR ALL TABLES | FOR SCHEMAS ( <schema1> [, ...] ) | FOR TABLES ( <table1> [AS <subsrc_name>] [, ...] )>
[EXPOSE PROGRESS AS <progress_subsource_name>]
[WITH ( <with_option> [, ...] )]

```

For details, see [CREATE SOURCE: PostgreSQL (Legacy)](/sql/create-source/postgres/).

**MySQL (Legacy):**

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

For details, see [CREATE SOURCE: MySQL (Legacy)](/sql/create-source/mysql/).

**SQL Server (Legacy):**

```mzsql
CREATE SOURCE [IF NOT EXISTS] <src_name>
[IN CLUSTER <cluster_name>]
FROM SQL SERVER CONNECTION <connection_name>
  [ ( EXCLUDE COLUMNS (<col1> [, ...]) ) ]
  [ ( TEXT COLUMNS (<col1> [, ...]) ) ]
<FOR ALL TABLES | FOR TABLES ( <table1> [AS <subsrc_name>] [, ...] )>
[WITH ( <with_option> [, ...] )]

```

For details, see [CREATE SOURCE: SQL Server(Legacy)](/sql/create-source/sql-server/).

**Kafka/Redpanda (Legacy):**

**Format Avro:**

```mzsql
CREATE SOURCE [IF NOT EXISTS] <src_name>
[IN CLUSTER <cluster_name>]
FROM KAFKA CONNECTION <connection_name> (
  TOPIC '<topic>'
  [, GROUP ID PREFIX '<group_id_prefix>']
  [, START OFFSET ( <partition_offset> [, ...] ) ]
  [, START TIMESTAMP <timestamp> ]
)
FORMAT AVRO
    USING CONFLUENT SCHEMA REGISTRY CONNECTION <csr_connection_name>
      [KEY STRATEGY <key_strategy>]
      [VALUE STRATEGY <value_strategy>]
  | USING AWS GLUE SCHEMA REGISTRY CONNECTION <glue_connection_name> (
      SCHEMA NAME = '<schema_name>'
    )
[INCLUDE
    KEY [AS <name>]
  | PARTITION [AS <name>]
  | OFFSET [AS <name>]
  | TIMESTAMP [AS <name>]
  | HEADERS [AS <name>]
  | HEADER '<key>' AS <name> [BYTES]
  [, ...]
]
[ENVELOPE
    NONE
  | DEBEZIUM
  | UPSERT [ ( VALUE DECODING ERRORS = INLINE [AS <name>] ) ]
]
[EXPOSE PROGRESS AS <progress_subsource_name>]
[WITH ( <with_option> [, ...] )]

```

**Format JSON:**

```mzsql
CREATE SOURCE [IF NOT EXISTS] <src_name>
[IN CLUSTER <cluster_name>]
FROM KAFKA CONNECTION <connection_name> (
  TOPIC '<topic>'
  [, GROUP ID PREFIX '<group_id_prefix>']
  [, START OFFSET ( <partition_offset> [, ...] ) ]
  [, START TIMESTAMP <timestamp> ]
)
FORMAT JSON
[INCLUDE
    PARTITION [AS <name>]
  | OFFSET [AS <name>]
  | TIMESTAMP [AS <name>]
  | HEADERS [AS <name>]
  | HEADER '<key>' AS <name> [BYTES]
  [, ...]
]
[ENVELOPE NONE]
[EXPOSE PROGRESS AS <progress_subsource_name>]
[WITH ( <with_option> [, ...] )]

```

**Format TEXT/BYTES:**

```mzsql
CREATE SOURCE [IF NOT EXISTS] <src_name>
[IN CLUSTER <cluster_name>]
FROM KAFKA CONNECTION <connection_name> (
  TOPIC '<topic>'
  [, GROUP ID PREFIX '<group_id_prefix>']
  [, START OFFSET ( <partition_offset> [, ...] ) ]
  [, START TIMESTAMP <timestamp> ]
)
FORMAT TEXT | BYTES
[INCLUDE
    PARTITION [AS <name>]
  | OFFSET [AS <name>]
  | TIMESTAMP [AS <name>]
  | HEADERS [AS <name>]
  | HEADER '<key>' AS <name> [BYTES]
  [, ...]
]
[ENVELOPE NONE]
[EXPOSE PROGRESS AS <progress_subsource_name>]
[WITH ( <with_option> [, ...] )]

```

**Format CSV:**

```mzsql
CREATE SOURCE [IF NOT EXISTS] <src_name> ( <col_name> [, ...] )
[IN CLUSTER <cluster_name>]
FROM KAFKA CONNECTION <connection_name> (
  TOPIC '<topic>'
  [, GROUP ID PREFIX '<group_id_prefix>']
  [, START OFFSET ( <partition_offset> [, ...] ) ]
  [, START TIMESTAMP <timestamp> ]
)
FORMAT CSV WITH <n> COLUMNS | WITH HEADER [ ( <col_name> [, ...] ) ]
[INCLUDE
    PARTITION [AS <name>]
  | OFFSET [AS <name>]
  | TIMESTAMP [AS <name>]
  | HEADERS [AS <name>]
  | HEADER '<key>' AS <name> [BYTES]
  [, ...]
]
[ENVELOPE NONE]
[EXPOSE PROGRESS AS <progress_subsource_name>]
[WITH ( <with_option> [, ...] )]

```

**Format Protobuf:**

```mzsql
CREATE SOURCE [IF NOT EXISTS] <src_name>
[IN CLUSTER <cluster_name>]
FROM KAFKA CONNECTION <connection_name> (
  TOPIC '<topic>'
  [, GROUP ID PREFIX '<group_id_prefix>']
  [, START OFFSET ( <partition_offset> [, ...] ) ]
  [, START TIMESTAMP <timestamp> ]
)
FORMAT PROTOBUF USING CONFLUENT SCHEMA REGISTRY CONNECTION <csr_connection_name>
  | FORMAT PROTOBUF MESSAGE '<message_name>' USING SCHEMA '<schema_bytes>'
[INCLUDE
    KEY [AS <name>]
  | PARTITION [AS <name>]
  | OFFSET [AS <name>]
  | TIMESTAMP [AS <name>]
  | HEADERS [AS <name>]
  | HEADER '<key>' AS <name> [BYTES]
  [, ...]
]
[ENVELOPE
    NONE
  | UPSERT [ ( VALUE DECODING ERRORS = INLINE [AS <name>] ) ]
]
[EXPOSE PROGRESS AS <progress_subsource_name>]
[WITH ( <with_option> [, ...] )]

```

**KEY FORMAT VALUE FORMAT:**

```mzsql
CREATE SOURCE [IF NOT EXISTS] <src_name>
[IN CLUSTER <cluster_name>]
FROM KAFKA CONNECTION <connection_name> (
  TOPIC '<topic>'
  [, GROUP ID PREFIX '<group_id_prefix>']
  [, START OFFSET ( <partition_offset> [, ...] ) ]
  [, START TIMESTAMP <timestamp> ]
)
KEY FORMAT <key_format> VALUE FORMAT <value_format>
-- <key_format> and <value_format> can be:
-- AVRO USING CONFLUENT SCHEMA REGISTRY CONNECTION <conn_name>
--     [KEY STRATEGY <strategy>]
--     [VALUE STRATEGY <strategy>]
-- | AVRO USING AWS GLUE SCHEMA REGISTRY CONNECTION <glue_conn_name> (SCHEMA NAME = '<schema_name>')
-- | CSV WITH <num> COLUMNS DELIMITED BY <char>
-- | JSON | TEXT | BYTES
-- | PROTOBUF USING CONFLUENT SCHEMA REGISTRY CONNECTION <conn_name>
-- | PROTOBUF MESSAGE '<message_name>' USING SCHEMA '<schema_bytes>'
[INCLUDE
    KEY [AS <name>]
  | PARTITION [AS <name>]
  | OFFSET [AS <name>]
  | TIMESTAMP [AS <name>]
  | HEADERS [AS <name>]
  | HEADER '<key>' AS <name> [BYTES]
  [, ...]
]
[ENVELOPE
    NONE
  | DEBEZIUM
  | UPSERT [(VALUE DECODING ERRORS = INLINE [AS name])]
]
[EXPOSE PROGRESS AS <progress_subsource_name>]
[WITH ( <with_option> [, ...] )]

```

For details, see [CREATE SOURCE: Kafka/Redpanda (Legacy Syntax)](/sql/create-source/kafka/).

**Webhook:**

```mzsql
CREATE SOURCE [IF NOT EXISTS] <src_name>
[IN CLUSTER <cluster_name>]
FROM WEBHOOK
  BODY FORMAT <TEXT | JSON [ARRAY] | BYTES>
  [INCLUDE HEADER <header_name> AS <column_alias> [BYTES] |
   INCLUDE HEADERS [ ( [NOT] <header_name> [, [NOT] <header_name> ... ] ) ]
  ][...]
  [CHECK (
      [WITH ( <BODY|HEADERS|SECRET <secret_name>> [AS <alias>] [BYTES] [, ...])]
      <check_expression>
    )
  ]

```

For details, see [CREATE SOURCE: Webhook](/sql/create-source/webhook/).

## Privileges

The privileges required to execute `CREATE SOURCE` are:

- `CREATE` privileges on the containing schema.
- `CREATE` privileges on the containing cluster if the source is created in an existing cluster.
- `CREATECLUSTER` privileges on the system if the source is not created in an existing cluster.
- `USAGE` privileges on all connections and secrets used in the source definition.
- `USAGE` privileges on the schemas that all connections and secrets in the
  statement are contained in.

## Available guides

The following guides step you through setting up sources:

| Type | External system |
|------|-----------------|
| **Databases (CDC): native connectors** | [PostgreSQL](/ingest-data/postgres/) <br> [MySQL](/ingest-data/mysql/) <br> [SQL Server](/ingest-data/sql-server/) |
| **Databases (CDC): via the Kafka connector** | [CockroachDB](/ingest-data/cdc-cockroachdb/) (using changefeeds) <br> [MongoDB](/ingest-data/mongodb/) (using Debezium) |
| **Message brokers** | [Kafka](/ingest-data/kafka/) <br> [Redpanda](/sql/create-source/kafka) |
| **Webhooks** | [Amazon EventBridge](/ingest-data/webhooks/amazon-eventbridge/) <br> [Segment](/ingest-data/webhooks/segment/) <br> [HubSpot](/ingest-data/webhooks/hubspot/) <br> [RudderStack](/ingest-data/webhooks/rudderstack/) <br> [SnowcatCloud](/ingest-data/webhooks/snowcatcloud/) <br> [Stripe](/ingest-data/webhooks/stripe/)|

## Best practices

### Separate cluster(s) for sources

In production, if possible, use a dedicated cluster for
[sources](/fundamentals/concepts/sources/); i.e., avoid putting sources on the same cluster
that hosts compute objects, sinks, and/or serves queries.

In addition, for upsert sources:

- Consider separating upsert sources from your other sources. Upsert sources
  have higher resource requirements (since, for upsert sources, Materialize
  maintains each key and associated last value for the key as well as to perform
  deduplication). As such, if possible, use a separate source cluster for upsert
  sources.

- Consider using a larger cluster size during snapshotting for upsert sources.
  Once the snapshotting operation is complete, you can downsize the cluster to
  align with the steady-state ingestion.

### Sizing a source

Some sources are low traffic and require relatively few resources to handle data ingestion, while others are high traffic and require hefty resource allocations. The cluster in which you place a source determines the amount of CPU, memory, and disk available to the source.

It's a good idea to size up the cluster hosting a source when:

  * You want to **increase throughput**. Larger sources will typically ingest data
    faster, as there is more CPU available to read and decode data from the
    upstream external system.

  * You are using the [upsert
    envelope](/sql/create-source/kafka/#upsert-envelope) or [Debezium
    envelope](/sql/create-source/kafka/#debezium-envelope), and your source
    contains **many unique keys**. These envelopes maintain state proportional
    to the number of unique keys in the upstream external system. Larger sizes
    can store more unique keys.

Sources share the resource allocation of their cluster with all other objects in
the cluster. Colocating multiple sources onto the same cluster can be more
resource efficient when you have many low-traffic sources that occasionally need
some burst capacity.

## Related pages

- [Sources](/fundamentals/concepts/sources/)
- [`SHOW SOURCES`](/sql/show-sources/)
- [`SHOW COLUMNS`](/sql/show-columns/)
- [`SHOW CREATE SOURCE`](/sql/show-create-source/)

## Pages in this section

- [Appendix: Load generator](/sql/create-source/load-generator/index.md): Using Materialize's built-in load generators
- [CREATE SOURCE: Kafka/Redpanda (Legacy Syntax)](/sql/create-source/kafka/index.md): Connecting Materialize to a Kafka or Redpanda broker
- [CREATE SOURCE: Kafka/Redpanda (New Syntax)](/sql/create-source/kafka-v2/index.md): Connecting Materialize to a Kafka or Redpanda broker using the new source syntax
- [CREATE SOURCE: MySQL (Legacy syntax)](/sql/create-source/mysql/index.md): Connecting Materialize to a MySQL database for Change Data Capture (CDC).
- [CREATE SOURCE: MySQL (New Syntax)](/sql/create-source/mysql-v2/index.md): Connecting Materialize to a MySQL database for Change Data Capture (CDC).
- [CREATE SOURCE: PostgreSQL (Legacy Syntax)](/sql/create-source/postgres/index.md): Connecting Materialize to a PostgreSQL database for Change Data Capture (CDC).
- [CREATE SOURCE: PostgreSQL (New Syntax)](/sql/create-source/postgres-v2/index.md): Creates a new source from PostgreSQL 11+.
- [CREATE SOURCE: SQL Server](/sql/create-source/sql-server-v2/index.md): Connecting Materialize to a SQL Server database for Change Data Capture (CDC).
- [CREATE SOURCE: SQL Server (Legacy Syntax)](/sql/create-source/sql-server/index.md): Connecting Materialize to a SQL Server database for Change Data Capture (CDC).
- [CREATE SOURCE: Webhook](/sql/create-source/webhook/index.md): Ingesting data into Materialize with HTTP requests
