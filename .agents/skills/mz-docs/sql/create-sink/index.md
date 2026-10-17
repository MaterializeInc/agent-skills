# CREATE SINK

`CREATE SINK` connects Materialize to an external data sink.

A [sink](/fundamentals/concepts/sinks/) describes an external system you
want Materialize to write data to, and provides details about how to encode
that data. You can define a sink over a materialized view, source, or table.

## Syntax summary

<!--"Docs Note: Using include-example shortcode instead of include-syntax since only want the code snippet on this page."
-->

**Kafka/Redpanda:**

**Format Avro:**

```mzsql
CREATE SINK [IF NOT EXISTS] <sink_name>
[IN CLUSTER <cluster_name>]
FROM <item_name>
INTO KAFKA CONNECTION <connection_name> (
  TOPIC '<topic>'
  [, COMPRESSION TYPE <compression_type>]
  [, TRANSACTIONAL ID PREFIX '<transactional_id_prefix>']
  [, PARTITION BY = <expression>]
  [, PROGRESS GROUP ID PREFIX '<progress_group_id_prefix>']
  [, TOPIC REPLICATION FACTOR <replication_factor>]
  [, TOPIC PARTITION COUNT <partition_count>]
  [, TOPIC CONFIG <topic_config>]
)
[KEY ( <key_col1> [, ...] ) [NOT ENFORCED]]
[HEADERS <headers_column>]
FORMAT AVRO
    USING CONFLUENT SCHEMA REGISTRY CONNECTION <csr_connection_name> [
      (
        [AVRO KEY FULLNAME '<avro_key_fullname>']
        [, AVRO VALUE FULLNAME '<avro_value_fullname>']
        [, NULL DEFAULTS <null_defaults>]
        [, DOC ON <doc_on_option> [, ...]]
        [, KEY COMPATIBILITY LEVEL '<key_compatibility_level>']
        [, VALUE COMPATIBILITY LEVEL '<value_compatibility_level>']
      )
    ]
  | USING AWS GLUE SCHEMA REGISTRY CONNECTION <glue_connection_name> [
      (
        [KEY SCHEMA NAME '<key_schema_name>']
        [, VALUE SCHEMA NAME '<value_schema_name>']
        [, KEY COMPATIBILITY LEVEL '<key_compatibility_level>']
        [, VALUE COMPATIBILITY LEVEL '<value_compatibility_level>']
      )
    ]
[ENVELOPE DEBEZIUM | UPSERT]
[WITH (SNAPSHOT = <snapshot>)]

```

**Format JSON:**

```mzsql
CREATE SINK [IF NOT EXISTS] <sink_name>
[IN CLUSTER <cluster_name>]
FROM <item_name>
INTO KAFKA CONNECTION <connection_name> (
  TOPIC '<topic>'
  [, COMPRESSION TYPE <compression_type>]
  [, TRANSACTIONAL ID PREFIX '<transactional_id_prefix>']
  [, PARTITION BY = <expression>]
  [, PROGRESS GROUP ID PREFIX '<progress_group_id_prefix>']
  [, TOPIC REPLICATION FACTOR <replication_factor>]
  [, TOPIC PARTITION COUNT <partition_count>]
  [, TOPIC CONFIG <topic_config>]
)
[KEY ( <key_col1> [, ...] ) [NOT ENFORCED]]
[HEADERS <headers_column>]
FORMAT JSON
[ENVELOPE DEBEZIUM | UPSERT]
[WITH (SNAPSHOT = <snapshot>)]

```

**Format TEXT/BYTES:**

```mzsql
CREATE SINK [IF NOT EXISTS] <sink_name>
[IN CLUSTER <cluster_name>]
FROM <item_name>
INTO KAFKA CONNECTION <connection_name> (
  TOPIC '<topic>'
  [, COMPRESSION TYPE <compression_type>]
  [, TRANSACTIONAL ID PREFIX '<transactional_id_prefix>']
  [, PARTITION BY = <expression>]
  [, PROGRESS GROUP ID PREFIX '<progress_group_id_prefix>']
  [, TOPIC REPLICATION FACTOR <replication_factor>]
  [, TOPIC PARTITION COUNT <partition_count>]
  [, TOPIC CONFIG <topic_config>]
)
FORMAT TEXT | BYTES
[ENVELOPE DEBEZIUM | UPSERT]
[WITH (SNAPSHOT = <snapshot>)]

```

**KEY FORMAT VALUE FORMAT:**

By default, the message key is encoded using the same format as the message value. However, you can set the key and value encodings explicitly using the `KEY FORMAT ... VALUE FORMAT`.

```mzsql
CREATE SINK [IF NOT EXISTS] <sink_name>
[IN CLUSTER <cluster_name>]
FROM <item_name>
INTO KAFKA CONNECTION <connection_name> (
  TOPIC '<topic>'
  [, COMPRESSION TYPE <compression_type>]
  [, TRANSACTIONAL ID PREFIX '<transactional_id_prefix>']
  [, PARTITION BY = <expression>]
  [, PROGRESS GROUP ID PREFIX '<progress_group_id_prefix>']
  [, TOPIC REPLICATION FACTOR <replication_factor>]
  [, TOPIC PARTITION COUNT <partition_count>]
  [, TOPIC CONFIG <topic_config>]
)
[KEY ( <key_col1> [, ...] ) [NOT ENFORCED]]
[HEADERS <headers_column>]
KEY FORMAT <key_format> VALUE FORMAT <value_format>
-- <key_format> and <value_format> can be:
-- AVRO USING CONFLUENT SCHEMA REGISTRY CONNECTION <csr_connection_name> [
--     (
--       [AVRO KEY FULLNAME '<avro_key_fullname>']
--       [, AVRO VALUE FULLNAME '<avro_value_fullname>']
--       [, NULL DEFAULTS <null_defaults>]
--       [, DOC ON <doc_on_option> [, ...]]
--       [, KEY COMPATIBILITY LEVEL '<key_compatibility_level>']
--       [, VALUE COMPATIBILITY LEVEL '<value_compatibility_level>']
--     )
-- ]
-- | AVRO USING AWS GLUE SCHEMA REGISTRY CONNECTION <glue_connection_name> [
--     (
--       [KEY SCHEMA NAME '<key_schema_name>']
--       [, VALUE SCHEMA NAME '<value_schema_name>']
--       [, KEY COMPATIBILITY LEVEL '<key_compatibility_level>']
--       [, VALUE COMPATIBILITY LEVEL '<value_compatibility_level>']
--     )
-- ]
-- | JSON | TEXT | BYTES
[ENVELOPE DEBEZIUM | UPSERT]
[WITH (SNAPSHOT = <snapshot>)]

```

For details, see [CREATE Sink: Kafka/Redpanda](/sql/create-sink/kafka/).

**Iceberg:**

> **Public Preview:** This feature is in public preview.

**MODE UPSERT:**

```mzsql
CREATE SINK [IF NOT EXISTS] <sink_name>
[IN CLUSTER <cluster_name>]
FROM <item_name>
INTO ICEBERG CATALOG CONNECTION <catalog_connection> (
  NAMESPACE = '<namespace>',
  TABLE = '<table>'
)
KEY ( <key_col> [, ...] ) [NOT ENFORCED]
MODE UPSERT
WITH (COMMIT INTERVAL = '<interval>')

```

**MODE APPEND:**

```mzsql
CREATE SINK [IF NOT EXISTS] <sink_name>
[IN CLUSTER <cluster_name>]
FROM <item_name>
INTO ICEBERG CATALOG CONNECTION <catalog_connection> (
  NAMESPACE = '<namespace>',
  TABLE = '<table>'
)
MODE APPEND
WITH (COMMIT INTERVAL = '<interval>')

```

For details, see [CREATE Sink: Iceberg](/sql/create-sink/iceberg/).

## Best practices

### Sizing a sink

Some sinks require relatively few resources to handle data ingestion, while
others are high traffic and require hefty resource allocations. The cluster in
which you place a sink determines the amount of CPU and memory available to the
sink.

Sinks share the resource allocation of their cluster with all other objects in
the cluster. Colocating multiple sinks onto the same cluster can be more
resource efficient when you have many low-traffic sinks that occasionally need
some burst capacity.

## Details

A sink cannot be created directly on a catalog object. As a workaround you can
create a materialized view on a catalog object and create a sink on the
materialized view.

[//]: # "TODO(morsapaes) Add best practices for sizing sinks."

## Privileges

The privileges required to execute this statement are:

- `CREATE` privileges on the containing schema.
- `SELECT` privileges on the item being written out to an external system.
  - NOTE: if the item is a materialized view, then the view owner must also have the necessary privileges to
    execute the view definition.
- `CREATE` privileges on the containing cluster if the sink is created in an existing cluster.
- `CREATECLUSTER` privileges on the system if the sink is not created in an existing cluster.
- `USAGE` privileges on all connections and secrets used in the sink definition.
- `USAGE` privileges on the schemas that all connections and secrets in the
  statement are contained in.

## Related pages

- [Sinks](/fundamentals/concepts/sinks/)
- [`SHOW SINKS`](/sql/show-sinks/)
- [`SHOW COLUMNS`](/sql/show-columns/)
- [`SHOW CREATE SINK`](/sql/show-create-sink/)

## Pages in this section

- [CREATE SINK: Iceberg](/sql/create-sink/iceberg/index.md): Connecting Materialize to an Apache Iceberg table
- [CREATE SINK: Kafka/Redpanda](/sql/create-sink/kafka/index.md): Connecting Materialize to a Kafka or Redpanda broker sink
