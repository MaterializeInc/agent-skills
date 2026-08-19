# CREATE TABLE: Kafka source table
Create a read-only table from a Kafka/Redpanda source (new syntax).
In Materialize, you can create read-only tables from [Kafka/Redpanda sources
created using the new syntax](/sql/create-source/kafka-v2/).

## Syntax

> **Note:** Source-populated tables are **read-only** tables. Users **cannot** perform write
> operations
> ([`INSERT`](/sql/insert/)/[`UPDATE`](/sql/update/)/[`DELETE`](/sql/delete/)) on
> these tables.

**Format Avro:**

Materialize can decode Avro messages by integrating with a schema registry
to retrieve a schema, and automatically determine the columns and data types
to use in the table.

```mzsql
CREATE TABLE [IF NOT EXISTS] <table_name>
FROM SOURCE <src_name>
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
];

```

| Syntax element | Description |
| --- | --- |
| **IF NOT EXISTS** | *Optional.* If specified, do not throw an error if the table with the same name already exists. Instead, issue a notice and skip the table creation.  {{< include-md file="shared-content/create-table-if-not-exists-tip.md" >}}  |
| `<table_name>` |  The name of the table to create. Names for tables must follow the [naming guidelines](/sql/identifiers/#naming-restrictions).  |
| `<src_name>` |  The name of the [Kafka source](/sql/create-source/kafka-v2/) to read from.  |
| `<csr_connection_name>` | The [Confluent Schema Registry connection](/sql/create-connection/#confluent-schema-registry) to use in the source. Applies to both the key and value.  |
| `<glue_connection_name>` (**SCHEMA NAME** `'<schema_name>'`) | **Private preview.** This feature is under active development.  Decode Avro messages using a schema managed in AWS Glue Schema Registry. `<glue_connection_name>` is the [AWS Glue Schema Registry connection](/sql/create-connection/#aws-glue-schema-registry), and `SCHEMA NAME` (**required**) is the name of the schema to read from the connection's registry. The schema is pinned at the time the source is created.  A single `FORMAT AVRO USING AWS GLUE SCHEMA REGISTRY` clause resolves one schema. To set the key and value independently (for example, under `ENVELOPE UPSERT` or `ENVELOPE DEBEZIUM`), specify `KEY FORMAT ... VALUE FORMAT ...` explicitly.  |
| **KEY STRATEGY** `<key_strategy>` | Optional. Define how an Avro reader schema will be chosen for the message key. \| Strategy \| Description \| \|--------\|-------------\| \| **LATEST** \| (Default) Use the latest writer schema from the schema registry as the reader schema. \| \| **ID** \| Use a specific schema from the registry. \| \| **INLINE** \| Use the inline schema. \|  |
| **VALUE STRATEGY** `<value_strategy>` | Optional. Define how an Avro reader schema will be chosen for the message value. \| Strategy \| Description \| \|--------\|-------------\| \| **LATEST** \| (Default) Use the latest writer schema from the schema registry as the reader schema. \| \| **ID** \| Use a specific schema from the registry. \| \| **INLINE** \| Use the inline schema. \|  |
| **INCLUDE** `<include_option>` | Optional. If specified, include the additional information as column(s) in the table. The following `<include_option>`s are supported:  {{% include-headless "/headless/kafka-include-metadata-options" %}}  |
| **ENVELOPE** `<envelope>` | Optional. Specifies how Materialize interprets incoming records. Valid envelope types:  \| Envelope \| Description \| \|----------\|-------------\| \| `NONE` \| Append-only envelope (default). Each message is inserted as a new row. \| \| `DEBEZIUM` \| Decode Kafka messages produced by [Debezium](https://debezium.io/). \| \| `UPSERT [ ( VALUE DECODING ERRORS = INLINE [AS <name>] ) ]` \| Use the standard key-value convention to support inserts, updates, and deletes. Required to consume [log compacted topics](https://docs.confluent.io/platform/current/kafka/design.html#log-compaction). \|  |

See also [Avro details](#avro).

**Format JSON:**

Materialize can decode JSON messages into a single column named `data` with
type `jsonb`. Refer to the [`jsonb` type](/sql/types/jsonb) documentation for
the supported operations on this type.

```mzsql
CREATE TABLE [IF NOT EXISTS] <table_name>
FROM SOURCE <src_name>
FORMAT JSON
[INCLUDE
    PARTITION [AS <name>]
  | OFFSET [AS <name>]
  | TIMESTAMP [AS <name>]
  | HEADERS [AS <name>]
  | HEADER '<key>' AS <name> [BYTES]
  [, ...]
]
[ENVELOPE NONE];

```

| Syntax element | Description |
| --- | --- |
| **IF NOT EXISTS** | *Optional.* If specified, do not throw an error if the table with the same name already exists. Instead, issue a notice and skip the table creation.  {{< include-md file="shared-content/create-table-if-not-exists-tip.md" >}}  |
| `<table_name>` |  The name of the table to create. Names for tables must follow the [naming guidelines](/sql/identifiers/#naming-restrictions).  |
| `<src_name>` |  The name of the [Kafka source](/sql/create-source/kafka-v2/) to read from.  |
| **INCLUDE** `<include_option>` | Optional. If specified, include the additional information as column(s) in the table. The following `<include_option>`s are supported:  {{% include-headless "/headless/kafka-include-metadata-options" %}}  |
| **ENVELOPE** NONE | Optional. Specifies how Materialize interprets incoming records. Valid envelope type(s):  \| Envelope \| Description \| \|----------\|-------------\| \| `NONE` \| Append-only envelope (default). Each message is inserted as a new row. \|  |

See also [JSON details](#json).

**Format TEXT/BYTES:**

Materialize can parse **new-line delimited** data as plain text, or read raw
bytes without applying any formatting or decoding. Text-formatted tables have
a single column, by default named `text`. Raw byte-formatted tables have a
single column, by default named `data`.

```mzsql
CREATE TABLE [IF NOT EXISTS] <table_name>
FROM SOURCE <src_name>
FORMAT TEXT | BYTES
[INCLUDE
    PARTITION [AS <name>]
  | OFFSET [AS <name>]
  | TIMESTAMP [AS <name>]
  | HEADERS [AS <name>]
  | HEADER '<key>' AS <name> [BYTES]
  [, ...]
]
[ENVELOPE NONE];

```

| Syntax element | Description |
| --- | --- |
| **IF NOT EXISTS** | *Optional.* If specified, do not throw an error if the table with the same name already exists. Instead, issue a notice and skip the table creation.  {{< include-md file="shared-content/create-table-if-not-exists-tip.md" >}}  |
| `<table_name>` |  The name of the table to create. Names for tables must follow the [naming guidelines](/sql/identifiers/#naming-restrictions).  |
| `<src_name>` |  The name of the [Kafka source](/sql/create-source/kafka-v2/) to read from.  |
| **INCLUDE** `<include_option>` | Optional. If specified, include the additional information as column(s) in the table. The following `<include_option>`s are supported:  {{% include-headless "/headless/kafka-include-metadata-options" %}}  |
| **ENVELOPE** NONE | Optional. Specifies how Materialize interprets incoming records. Valid envelope type(s):  \| Envelope \| Description \| \|----------\|-------------\| \| `NONE` \| Append-only envelope (default). Each message is inserted as a new row. \|  |

**Format CSV:**

Materialize can parse CSV-formatted data. The data in CSV tables is read as
[`text`](/sql/types/text).

```mzsql
CREATE TABLE [IF NOT EXISTS] <table_name>
FROM SOURCE <src_name>
FORMAT CSV WITH <n> COLUMNS [DELIMITED BY <char>]
[INCLUDE
    PARTITION [AS <name>]
  | OFFSET [AS <name>]
  | TIMESTAMP [AS <name>]
  | HEADERS [AS <name>]
  | HEADER '<key>' AS <name> [BYTES]
  [, ...]
]
[ENVELOPE NONE];

```

| Syntax element | Description |
| --- | --- |
| **IF NOT EXISTS** | *Optional.* If specified, do not throw an error if the table with the same name already exists. Instead, issue a notice and skip the table creation.  {{< include-md file="shared-content/create-table-if-not-exists-tip.md" >}}  |
| `<table_name>` |  The name of the table to create. Names for tables must follow the [naming guidelines](/sql/identifiers/#naming-restrictions).  |
| `<src_name>` |  The name of the [Kafka source](/sql/create-source/kafka-v2/) to read from.  |
| `<n>` **COLUMNS** | The number of columns in the CSV message.  |
| **DELIMITED BY** `<char>` | *Optional.* If specified, the delimiter character. By default, uses a comma `,` as the delimiter.  |
| **INCLUDE** `<include_option>` | Optional. If specified, include the additional information as column(s) in the table. The following `<include_option>`s are supported:  {{% include-headless "/headless/kafka-include-metadata-options" %}}  |
| **ENVELOPE** NONE | Optional. Specifies how Materialize interprets incoming records. Valid envelope type(s):  \| Envelope \| Description \| \|----------\|-------------\| \| `NONE` \| Append-only envelope (default). Each message is inserted as a new row. \|  |

**Format Protobuf:**

Materialize can decode Protobuf messages by integrating with a schema
registry or parsing an inline schema to retrieve a `.proto` schema
definition. It can then automatically define the columns and data types to
use in the table.

```mzsql
CREATE TABLE [IF NOT EXISTS] <table_name>
FROM SOURCE <src_name>
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
];

```

| Syntax element | Description |
| --- | --- |
| **IF NOT EXISTS** | *Optional.* If specified, do not throw an error if the table with the same name already exists. Instead, issue a notice and skip the table creation.  {{< include-md file="shared-content/create-table-if-not-exists-tip.md" >}}  |
| `<table_name>` |  The name of the table to create. Names for tables must follow the [naming guidelines](/sql/identifiers/#naming-restrictions).  |
| `<src_name>` |  The name of the [Kafka source](/sql/create-source/kafka-v2/) to read from.  |
| `<csr_connection_name>` | The [Confluent Schema Registry connection](/sql/create-connection/#confluent-schema-registry) to use to retrieve the `.proto` schema definition.  |
| **MESSAGE** `'<message_name>'` **USING SCHEMA** `'<schema_bytes>'` | Decode Protobuf messages using an inline schema instead of a schema registry. `<message_name>` is the top-level message name and `<schema_bytes>` is the encoded `FileDescriptorSet`.  |
| **INCLUDE** `<include_option>` | Optional. If specified, include the additional information as column(s) in the table. The following `<include_option>`s are supported:  {{% include-headless "/headless/kafka-include-metadata-options" %}}  |
| **ENVELOPE** `<envelope>` | Optional. Specifies how Materialize interprets incoming records. Valid envelope types:  \| Envelope \| Description \| \|----------\|-------------\| \| `NONE` \| Append-only envelope (default). Each message is inserted as a new row. \| \| `UPSERT [ ( VALUE DECODING ERRORS = INLINE [AS <name>] ) ]` \| Use the standard key-value convention to support inserts, updates, and deletes. Required to consume [log compacted topics](https://docs.confluent.io/platform/current/kafka/design.html#log-compaction). \|  |

See also [Protobuf details](#protobuf).

**KEY FORMAT VALUE FORMAT:**

By default, the message key is decoded using the same format as the message
value. However, you can set the key and value encodings explicitly using
`KEY FORMAT ... VALUE FORMAT`.

```mzsql
CREATE TABLE [IF NOT EXISTS] <table_name>
FROM SOURCE <src_name>
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
];

```

| Syntax element | Description |
| --- | --- |
| **IF NOT EXISTS** | *Optional.* If specified, do not throw an error if the table with the same name already exists. Instead, issue a notice and skip the table creation.  {{< include-md file="shared-content/create-table-if-not-exists-tip.md" >}}  |
| `<table_name>` |  The name of the table to create. Names for tables must follow the [naming guidelines](/sql/identifiers/#naming-restrictions).  |
| `<src_name>` |  The name of the [Kafka source](/sql/create-source/kafka-v2/) to read from.  |
| **KEY FORMAT** `<key_format>` **VALUE FORMAT** `<value_format>` | Set the key and value encodings explicitly, instead of decoding both with a single `FORMAT`. Each of `<key_format>` and `<value_format>` can be `AVRO`, `JSON`, `TEXT`, `BYTES`, `CSV`, or `PROTOBUF`. See [supported formats](/sql/create-table/kafka/#syntax).  |
| **INCLUDE** `<include_option>` | Optional. If specified, include the additional information as column(s) in the table. The following `<include_option>`s are supported:  {{% include-headless "/headless/kafka-include-metadata-options" %}}  |
| **ENVELOPE** `<envelope>` | Optional. Specifies how Materialize interprets incoming records. Valid envelope types:  \| Envelope \| Description \| \|----------\|-------------\| \| `NONE` \| Append-only envelope (default). Each message is inserted as a new row. \| \| `DEBEZIUM` \| Decode Kafka messages produced by [Debezium](https://debezium.io/). \| \| `UPSERT [ ( VALUE DECODING ERRORS = INLINE [AS <name>] ) ]` \| Use the standard key-value convention to support inserts, updates, and deletes. Required to consume [log compacted topics](https://docs.confluent.io/platform/current/kafka/design.html#log-compaction). \|  |

## Envelopes

In addition to determining how to decode incoming records, Materialize also
needs to understand how to interpret them. Whether a new record inserts,
updates, or deletes existing data in Materialize depends on the `ENVELOPE`
specified. For where the `ENVELOPE` clause goes, see [Syntax](#syntax).

### Append-only envelope

<p style="font-size:14px"><b>Syntax:</b> <code>ENVELOPE NONE</code></p>

The append-only envelope treats all records as inserts. This is the **default** envelope, if no envelope is specified.

### Upsert envelope

<p style="font-size:14px"><b>Syntax:</b> <code>ENVELOPE UPSERT</code></p>

The upsert envelope uses the standard key-value convention to support inserts,
updates, and deletes within Materialize. It treats all records as having a
**key** and a **value**:

- If the key does not match a preexisting record, it inserts the record's key and value.

- If the key matches a preexisting record and the value is _non-null_, Materialize updates
  the existing record with the new value.

- If the key matches a preexisting record and the value is _null_, Materialize deletes the record.

> **Note:** - Using this envelope is required to consume [log compacted topics](https://docs.confluent.io/platform/current/kafka/design.html#log-compaction).
> - This envelope can lead to high memory and disk utilization in the cluster
>   maintaining the source. We recommend using a standard-sized cluster, rather
>   than a legacy-sized cluster, to automatically spill the workload to disk. See
>   [spilling to disk](/sql/create-source/kafka/#spilling-to-disk) for details.

#### Null keys

If a message with a `NULL` key is detected, Materialize sets the source into an
error state. To recover an errored source, you must produce a record with a
`NULL` value and a `NULL` key to the topic, to force a retraction.

As an example, you can use [`kcat`](https://docs.confluent.io/platform/current/clients/kafkacat-usage.html)
to produce an empty message:

```bash
echo ":" | kcat -b $BROKER -t $TOPIC -Z -K: \
  -X security.protocol=SASL_SSL \
  -X sasl.mechanisms=SCRAM-SHA-256 \
  -X sasl.username=$KAFKA_USERNAME \
  -X sasl.password=$KAFKA_PASSWORD
```

#### Value decoding errors

By default, if an error happens while decoding the value of a message for a
specific key, Materialize sets the source into an error state. You can
configure the source to continue ingesting data in the presence of value
decoding errors using the `VALUE DECODING ERRORS = INLINE` option:

```mzsql
ENVELOPE UPSERT (VALUE DECODING ERRORS = INLINE)
```

When this option is specified the source will include an additional column named
`error` with type `record(description: text)`.

This column and all value columns will be nullable, such that if the most recent value
for the given Kafka message key cannot be decoded, this `error` column will contain
the error message. If the most recent value for a key has been successfully decoded,
this column will be `NULL`.

To use an alternative name for the error column, use `INLINE AS ..` to specify the
column name to use:

```mzsql
ENVELOPE UPSERT (VALUE DECODING ERRORS = (INLINE AS my_error_col))
```

It might be convenient to implement a parsing view on top of your Kafka upsert source that
excludes keys with decoding errors:

```mzsql
CREATE VIEW kafka_upsert_parsed
SELECT *
FROM kafka_upsert
WHERE error IS NULL;
```

### Debezium envelope

<p style="font-size:14px"><b>Syntax:</b> <code>ENVELOPE DEBEZIUM</code></p>

<div class="note">
  <strong class="gutter">NOTE:</strong> Currently, Materialize only supports Avro-encoded Debezium records. If you're interested in JSON support, please reach out in the community Slack or submit a <a href="https://github.com/MaterializeInc/materialize/discussions/new?category=feature-requests">feature request</a>.
</div>

Materialize provides a dedicated envelope (`ENVELOPE DEBEZIUM`) to decode Kafka
messages produced by [Debezium](https://debezium.io/).

Any materialized view defined on top of a Debezium source will be incrementally
updated as new change events stream in through Kafka, as a result of `INSERT`,
`UPDATE` and `DELETE` operations in the original database.

This envelope treats all records as [change events](https://debezium.io/documentation/reference/stable/connectors/postgresql.html#postgresql-events) with a diff structure that indicates whether each record should be interpreted as an insert, update or delete within Materialize:

|    |   |
 ----|---
 **Insert** | If the `before` field is _null_, the record represents an upstream [`create` event](https://debezium.io/documentation/reference/stable/connectors/postgresql.html#postgresql-create-events), and Materialize inserts the record's key and value.
 **Update** | If the `before` and `after` fields are _non-null_, the record represents an upstream [`update` event](https://debezium.io/documentation/reference/stable/connectors/postgresql.html#postgresql-update-events), and Materialize updates the existing record with the new value.
 **Delete** | If the `after` field is _null_, the record represents an upstream [`delete` event](https://debezium.io/documentation/reference/stable/connectors/postgresql.html#postgresql-delete-events), and Materialize deletes the record.

> **Note:** - This envelope can lead to high memory utilization in the cluster maintaining
>   the source. Materialize can automatically offload processing to
>   disk as needed. See [spilling to disk](/sql/create-source/kafka/#spilling-to-disk) for details.
> - Materialize expects a specific message structure that includes the row data
>   before and after the change event, which is **not guaranteed** for every
>   Debezium connector. For more details, check the [Debezium integration
>   guide](/integrations/debezium/).

#### Truncation

The Debezium envelope does not support upstream [`truncate` events](https://debezium.io/documentation/reference/stable/connectors/postgresql.html#postgresql-truncate-events).

#### Debezium metadata

The envelope exposes the `before` and `after` value fields from change events.

#### Duplicate handling

Debezium may produce duplicate records if the connector is interrupted. Materialize makes a best-effort attempt to detect and filter out duplicates.

## Details

### Avro

#### Schema registries

Materialize can retrieve Avro schemas from either of two schema registries,
selected by the `USING` clause:

- **[Confluent Schema Registry](/sql/create-connection/#confluent-schema-registry)**
  (`USING CONFLUENT SCHEMA REGISTRY`): schemas are looked up by topic using the
  `TopicNameStrategy`, and the message's embedded schema ID resolves the writer
  schema at decode time.

- **[AWS Glue Schema Registry](/sql/create-connection/#aws-glue-schema-registry)**
  (`USING AWS GLUE SCHEMA REGISTRY`) <a class="private-preview-inline" href="https://materialize.com/preview-terms/">(feature in private preview)</a>
: schemas are
  looked up by the `SCHEMA NAME` you provide, and the message's embedded schema
  version ID resolves the writer schema at decode time. Each `FORMAT AVRO USING
  AWS GLUE` clause resolves a single schema. To decode keys and values from
  different schemas (for example, under `ENVELOPE UPSERT` or `ENVELOPE
  DEBEZIUM`), you must specify `KEY FORMAT ... VALUE FORMAT ...` explicitly.

#### Schema versioning

The schema is resolved when the source or table is created. With
[Confluent Schema Registry](/sql/create-connection/#confluent-schema-registry),
the _latest_ schema is retrieved using the
[`TopicNameStrategy`](https://docs.confluent.io/current/schema-registry/serdes-develop/index.html)
strategy. With [AWS Glue Schema
Registry](/sql/create-connection/#aws-glue-schema-registry), the latest version
of the schema named by `SCHEMA NAME` is retrieved.

#### Schema evolution

As long as the writer schema changes in a [compatible way](https://avro.apache.org/docs/++version++/specification/#schema-resolution), Materialize will continue using the original reader schema definition by mapping values from the new to the old schema version. This applies to both Confluent Schema Registry and AWS Glue Schema Registry.

To pick up the new version of the writer schema, the approach depends on the syntax you used:

- **Legacy syntax** (`CREATE SOURCE ... FORMAT AVRO ...`): you need to **drop and recreate** the source, which incurs downtime.
- **New syntax** (`CREATE SOURCE` plus [`CREATE TABLE ... FROM SOURCE`](/sql/create-table/)): you can create a new table that reads the evolved schema and cut over without downtime. See [Handle upstream schema changes with zero downtime](/ingest-data/kafka/source-versioning/).

#### Name collision

To avoid [case-sensitivity](/sql/identifiers/#case-sensitivity) conflicts with Materialize identifiers, we recommend double-quoting all field names when working with Avro-formatted sources.

#### Supported types

Materialize supports all [Avro
types](https://avro.apache.org/docs/++version++/specification/), _except for_
recursive types and union types in arrays.

### JSON

If your JSON messages have a consistent shape, we recommend creating a parsing
[view](/concepts/views) that maps the individual fields to
columns with the required data types:

```mzsql
-- extract jsonb into typed columns
CREATE VIEW my_typed_source AS
  SELECT
    (data->>'field1')::boolean AS field_1,
    (data->>'field2')::int AS field_2,
    (data->>'field3')::float AS field_3
  FROM my_jsonb_source;
```

To avoid doing this task manually, you can use [this **JSON parsing
widget**](/sql/types/jsonb/#parsing).

#### Schema registry integration

Retrieving schemas from a schema registry is not supported yet for JSON-formatted sources. This means that Materialize cannot decode messages serialized using the [JSON Schema](https://docs.confluent.io/platform/current/schema-registry/serdes-develop/serdes-json.html#json-schema-serializer-and-deserializer) serialization format (`JSON_SR`).

### Protobuf

Unlike Avro, Protobuf does not serialize a schema with the message, so Materialize expects:

* A `FileDescriptorSet` that encodes the Protobuf message schema. You can generate the `FileDescriptorSet` with [`protoc`](https://grpc.io/docs/protoc-installation/), for example:

  ```shell
  protoc --include_imports --descriptor_set_out=SCHEMA billing.proto
  ```

* A top-level message name and its package name, so Materialize knows which message from the `FileDescriptorSet` is the top-level message to decode, in the following format:

  ```shell
  <package name>.<top-level message>
  ```

  For example, if the `FileDescriptorSet` were from a `.proto` file in the
    `billing` package, and the top-level message was called `Batch`, the
    _message&lowbar;name_ value would be `billing.Batch`.

#### Schema versioning

The _latest_ schema is retrieved using the [`TopicNameStrategy`](https://docs.confluent.io/current/schema-registry/serdes-develop/index.html) strategy at the time the source or table is created.

#### Schema evolution

As long as the `.proto` schema definition changes in a [compatible way](https://developers.google.com/protocol-buffers/docs/overview#updating-defs), Materialize will continue using the original schema definition by mapping values from the new to the old schema version. To pick up the new version of the schema with the legacy syntax (`CREATE SOURCE ... FORMAT PROTOBUF ...`), you need to **drop and recreate** the source. With the new syntax (`CREATE SOURCE` plus [`CREATE TABLE ... FROM SOURCE`](/sql/create-table/)), you can instead create a new table that reads the evolved schema and cut over without downtime, following the approach in [Handle upstream schema changes with zero downtime](/ingest-data/kafka/source-versioning/).

#### Supported types

Materialize supports all [well-known](https://developers.google.com/protocol-buffers/docs/reference/google.protobuf) Protobuf types from the `proto2` and `proto3` specs, _except for_ recursive `Struct` values and map types.

#### Multiple message schemas

When using a schema registry with Protobuf sources, the registered schemas must contain exactly one `Message` definition.

### Exposing source metadata

In addition to the message value, Materialize can expose the message key,
headers and other source metadata fields to SQL through the `INCLUDE` clause.
For where the `INCLUDE` clause goes, see [Syntax](#syntax).

#### Key

The message key is exposed via the `INCLUDE KEY` option. Composite keys are also
supported.

```mzsql
INCLUDE KEY AS renamed_id
```

Note that:

- This option requires specifying the key and value encodings explicitly using the `KEY FORMAT ... VALUE FORMAT` [syntax](#syntax).

- The `UPSERT` envelope always includes keys.

- The `DEBEZIUM` envelope is incompatible with this option.

#### Headers

Message headers can be retained in Materialize and exposed as part of the source data.

Note that:
- The `DEBEZIUM` envelope is incompatible with this option.

**All headers**

All of a message's headers can be exposed using `INCLUDE HEADERS`, followed by
an `AS <header_col>`.

This introduces column with the name specified or `headers` if none was
specified. The column has the type `record(key: text, value: bytea?) list`,
i.e. a list of records containing key-value pairs, where the keys are `text`
and the values are nullable `bytea`s.

```mzsql
INCLUDE HEADERS
```

To simplify turning the headers column into a `map` (so individual headers can
be searched), you can use the [`map_build`](/sql/functions/#map_build) function:

```mzsql
SELECT
    id,
    seller,
    item,
    convert_from(map_build(headers)->'client_id', 'utf-8') AS client_id,
    map_build(headers)->'encryption_key' AS encryption_key,
FROM kafka_metadata;
```

<p></p>

```nofmt
 id | seller |        item        | client_id |    encryption_key
----+--------+--------------------+-----------+----------------------
  2 |   1592 | Custom Art         |        23 | \x796f75207769736821
  3 |   1411 | City Bar Crawl     |        42 | \x796f75207769736821
```

**Individual headers**

Individual message headers can be exposed via the `INCLUDE HEADER key AS name`
option.

The `bytea` value of the header is automatically parsed into an UTF-8 string. To
expose the raw `bytea` instead, the `BYTES` option can be used.

```mzsql
INCLUDE HEADER 'c_id' AS client_id, HEADER 'key' AS encryption_key BYTES
```

Headers can be queried as any other column in the source:

```mzsql
SELECT
    id,
    seller,
    item,
    client_id::numeric,
    encryption_key
FROM kafka_metadata;
```

<p></p>

```nofmt
 id | seller |        item        | client_id |    encryption_key
----+--------+--------------------+-----------+----------------------
  2 |   1592 | Custom Art         |        23 | \x796f75207769736821
  3 |   1411 | City Bar Crawl     |        42 | \x796f75207769736821
```

Note that:

- Messages that do not contain all header keys as specified in the source DDL
  will cause an error that prevents further querying the source.

- Header values containing badly formed UTF-8 strings will cause an error in the
  source that prevents querying it, unless the `BYTES` option is specified.

#### Partition, offset, timestamp

These metadata fields are exposed via the `INCLUDE PARTITION`, `INCLUDE OFFSET`
and `INCLUDE TIMESTAMP` options.

```mzsql
INCLUDE PARTITION, OFFSET, TIMESTAMP AS ts
```

```mzsql
SELECT "offset" FROM kafka_metadata WHERE ts > '2021-01-01';
```

<p></p>

```nofmt
offset
------
15
14
13
```

### Excluding or recasting a field

A Kafka table's columns are determined entirely by its format (for Avro, the
reader schema). To exclude or recast a field, project or cast it in a view on
top of the table.

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

### Handling table schema changes

The use of `CREATE SOURCE` (new syntax) with `CREATE TABLE FROM SOURCE` allows
for the handling of the upstream schema changes, specifically adding or dropping
columns, without downtime. For details, see [Kafka: Handling upstream schema
changes with zero downtime](/ingest-data/kafka/source-versioning/).

## Privileges

The privileges required to execute this statement are:

- `CREATE` privileges on the containing schema.
- `USAGE` privileges on all types used in the table definition.
- `USAGE` privileges on the schemas that all types in the statement are
  contained in.

## Examples

### Create a table

To create a **read-only** table from a Kafka source, use the `CREATE TABLE
... FROM SOURCE` statement. Unlike other source types, a Kafka source
exposes a single topic, so the statement does **not** take a `(REFERENCE
...)` clause. The following example creates a **read-only** table `orders`
that decodes the topic as [JSON](/sql/create-table/kafka/#json).

{{< note >}}

- You can create multiple tables from the same Kafka source, each decoding
the topic with a different format or envelope.

- For `JSON`-formatted topics, we recommend creating a
[parsing view](/sql/create-table/kafka/#json) on top of the table to map the
individual fields to columns with the appropriate data types.

{{< /note >}}
```mzsql
/* This example assumes:
  - In Materialize:
    - You have defined a connection to the upstream Kafka broker.
    - You have used the connection to create a source.

   For example (substitute with your configuration):
      CREATE CONNECTION kafka_connection TO KAFKA (
        BROKER '<broker>',            -- substitute
        SECURITY PROTOCOL = SASL_SSL,
        SASL MECHANISMS = 'SCRAM-SHA-256',
        SASL USERNAME = '<user>',     -- substitute
        SASL PASSWORD = SECRET kafka_password
      );

      CREATE SOURCE orders_src
      FROM KAFKA CONNECTION kafka_connection (
        TOPIC 'orders'                -- substitute
      );
*/

CREATE TABLE orders
FROM SOURCE orders_src
FORMAT JSON
;

```
{{< include-md
file="content/headless/create-table-from-source-snapshotting.md" >}}

{{< include-md file="content/headless/create-table-if-not-exists-tip.md" >}}

To verify that the table has been created, you can run [`SHOW
TABLES`](/sql/show-tables/) to list all tables in the current
[schema](/sql/namespaces/#namespace-hierarchy):
```mzsql
SHOW TABLES;

```The results should include the `orders` table:

```hc {hl_lines="3"}
| name    | comment |
| ------- | ------- |
| orders  |         |
```

Inspect the table columns using the [`SHOW COLUMNS`](/sql/show-columns/)
command:
```mzsql
SHOW COLUMNS FROM orders;

```Because the table decodes the topic as `JSON`, the message value is exposed
as a single `data` column of type [`jsonb`](/sql/types/jsonb/):

```hc
| name | nullable | type  | comment |
| ---- | -------- | ----- | ------- |
| data | false    | jsonb |         |
```

Once the snapshotting process completes and the table is in the running
state, you can query the table. For `JSON`-formatted data, use the
[`jsonb` operators](/sql/types/jsonb/#operators) to extract individual
fields:
```mzsql
SELECT
    (data->>'id')::bigint AS id,
    data->>'item' AS item,
    (data->>'quantity')::bigint AS quantity
FROM orders
ORDER BY id;

``````hc
| id | item   | quantity |
| -- | ------ | -------- |
| 1  | widget | 5        |
| 2  | gadget | 2        |
```

## Related pages

- [`CREATE SOURCE: Kafka/Redpanda (New Syntax)`](/sql/create-source/kafka-v2/)
- [`DROP TABLE`](/sql/drop-table)
