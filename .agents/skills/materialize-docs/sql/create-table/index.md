# CREATE TABLE

`CREATE TABLE` creates a table that is persisted in durable storage.

`CREATE TABLE` defines a table that is persisted in durable storage.

In Materialize, you can create:

- [Read-write tables](/sql/create-table/user-populated/). With read-write
  tables, users can read ([`SELECT`]) and write to the tables ([`INSERT`],
  [`UPDATE`], [`DELETE`]).

- Read-only tables from sources that use the new syntax:
  [PostgreSQL](/sql/create-table/postgres/),
  [MySQL](/sql/create-table/mysql/),
  [SQL Server](/sql/create-table/sql-server/), and
  [Kafka/Redpanda](/sql/create-table/kafka/). Users cannot write ([`INSERT`],
  [`UPDATE`], [`DELETE`]) to these tables. These tables are populated by [data
  ingestion from a source](/ingest-data/).
  You must be on **v26+** to use the new syntax.

[//]: # "TODO(morsapaes) Bring back When to use a table? once there's more
clarity around best practices."

## Syntax summary

**Read-write table:**

To create a new read-write table (i.e., users can perform
[`SELECT`](/sql/select/), [`INSERT`](/sql/insert/),
[`UPDATE`](/sql/update/), and [`DELETE`](/sql/delete/) operations):
```mzsql
CREATE [TEMP|TEMPORARY] TABLE [IF NOT EXISTS] <table_name> (
  <column_name> <column_type> [NOT NULL][DEFAULT <default_expr>]
  [, ...]
)
[WITH (
  PARTITION BY (<column_name> [, ...]) |
  RETAIN HISTORY [=] FOR <duration>
)]
;

```

For details, see [CREATE TABLE: Read-write
table](/sql/create-table/user-populated/).

**PostgreSQL source table:**

To create a read-only table from a [source](/sql/create-source/) connected
(via native connector) to an external PostgreSQL:
```mzsql
CREATE TABLE [IF NOT EXISTS] <table_name> FROM SOURCE <source_name> (REFERENCE <upstream_table>)
[WITH (
    TEXT COLUMNS (<column_name> [, ...])
  | EXCLUDE COLUMNS (<column_name> [, ...])
  | PARTITION BY (<column_name> [, ...])
  [, ...]
)]
;

```{{< include-md
file="content/headless/create-table-from-source-snapshotting.md"
>}}

For details, see [CREATE TABLE: PostgreSQL source
table](/sql/create-table/postgres/).

**MySQL source table:**

To create a read-only table from a [source](/sql/create-source/) connected
(via native connector) to an external MySQL database:
```mzsql
CREATE TABLE [IF NOT EXISTS] <table_name> FROM SOURCE <source_name> (REFERENCE <upstream_schema>.<upstream_table>)
[WITH (
    TEXT COLUMNS (<column_name> [, ...])
  | EXCLUDE COLUMNS (<column_name> [, ...])
  | PARTITION BY (<column_name> [, ...])
  [, ...]
)]
;

```{{< include-md
file="content/headless/create-table-from-source-snapshotting.md"
>}}

For details, see [CREATE TABLE: MySQL source table](/sql/create-table/mysql/).

**SQL Server source table:**

To create a read-only table from a [source](/sql/create-source/) connected
(via native connector) to an external SQL Server database:
```mzsql
CREATE TABLE [IF NOT EXISTS] <table_name> FROM SOURCE <source_name> (REFERENCE <upstream_table>)
[WITH (
    TEXT COLUMNS (<column_name> [, ...])
  | EXCLUDE COLUMNS (<column_name> [, ...])
  | PARTITION BY (<column_name> [, ...])
  [, ...]
)]
;

```{{% include-headless "/headless/create-table-from-source-snapshotting.md"
%}}

For details, see [CREATE TABLE: SQL Server source
table](/sql/create-table/sql-server/).

**Kafka source table:**

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

For details, see [CREATE TABLE: Kafka source table](/sql/create-table/kafka/).

## Related pages

- [`INSERT`]
- [`DROP TABLE`](/sql/drop-table)

[`INSERT`]: /sql/insert/
[`SELECT`]: /sql/select/
[`UPDATE`]: /sql/update/
[`DELETE`]: /sql/delete/

---

## CREATE TABLE: Kafka source table

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

Creating the tables from sources starts the [snapshotting](/ingest-data/#snapshotting) process. Snapshotting syncs the
currently available data into Materialize. Because the initial snapshot is
persisted in the storage layer atomically (i.e., at the same ingestion
timestamp), you are not able to query the table until snapshotting is complete.

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

---

## CREATE TABLE: MySQL source table

In Materialize, you can create read-only tables from [MySQL sources created
using the new syntax](/sql/create-source/mysql-v2/).

> **Note:** You must be on **v26.25+** to use the new syntax.

## Syntax

> **Note:** Source-populated tables are **read-only** tables. Users **cannot** perform write
> operations
> ([`INSERT`](/sql/insert/)/[`UPDATE`](/sql/update/)/[`DELETE`](/sql/delete/)) on
> these tables.

To create a read-only table from a [source](/sql/create-source/) connected
(via native connector) to an external MySQL database:

```mzsql
CREATE TABLE [IF NOT EXISTS] <table_name> FROM SOURCE <source_name> (REFERENCE <upstream_schema>.<upstream_table>)
[WITH (
    TEXT COLUMNS (<column_name> [, ...])
  | EXCLUDE COLUMNS (<column_name> [, ...])
  | PARTITION BY (<column_name> [, ...])
  [, ...]
)]
;

```

| Syntax element | Description |
| --- | --- |
| **IF NOT EXISTS** | *Optional.* If specified, do not throw an error if the table with the same name already exists. Instead, issue a notice and skip the table creation.  {{< include-md file="content/headless/create-table-if-not-exists-tip.md" >}}  |
| `<table_name>` |  The name of the table to create. Names for tables must follow the [naming guidelines](/sql/identifiers/#naming-restrictions).  |
| `<source_name>` |  The name of the [source](/sql/create-source/) associated with the reference object from which to create the table.  |
| **(REFERENCE <upstream_schema>.<upstream_table>)** |  The fully-qualified name of the upstream MySQL table from which to create the table. You can create multiple tables from the same upstream table.  To find the upstream tables available in your [source](/sql/create-source/), you can use the following query, substituting your source name for `<source_name>`:  <br>  ```mzsql SELECT refs.* FROM mz_internal.mz_source_references refs, mz_sources s WHERE s.name = '<source_name>' -- substitute with your source name AND refs.source_id = s.id; ```  |
| **WITH (<with_option>[,...])** | The following `<with_option>`s are supported:  \| Option \| Description \| \|--------\|-------------\| \| `TEXT COLUMNS (<column_name> [, ...])` \| *Optional.* If specified, decode data as `text` for the listed column(s), such as for unsupported data types. See also [supported types](#supported-data-types). \| \| `EXCLUDE COLUMNS (<column_name> [, ...])` \| *Optional.* If specified, exclude the listed column(s) from the table, such as for unsupported data types. See also [supported types](#supported-data-types). \| \| `PARTITION BY (<column_name> [, ...])` \| {{< include-md file="content/headless/partition-by-option-description.md" >}} \|  |

## Details

### DDL transaction block

For performance, when issuing multiple `CREATE TABLE FROM SOURCE...` statements,
use within a [transaction block](/sql/begin/#ddl-only-transactions).

### Source-populated tables and snapshotting

Creating the tables from sources starts the [snapshotting](/ingest-data/#snapshotting) process. Snapshotting syncs the
currently available data into Materialize. Because the initial snapshot is
persisted in the storage layer atomically (i.e., at the same ingestion
timestamp), you are not able to query the table until snapshotting is complete.

> **Note:** During the snapshotting, the data ingestion for the existing tables for the same
> source is temporarily blocked. As such, if possible, you can resize the cluster
> to speed up the snapshotting process and once the process finishes, resize the
> cluster for steady-state. You can monitor the snapshot progress on the overview
> page for the source in the Materialize console.

### Supported data types

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

### Handling table schema changes

The use of `CREATE SOURCE` (new syntax) with `CREATE TABLE FROM SOURCE` allows
for the handling of the upstream DDL changes, specifically adding or dropping
columns in the upstream tables, without downtime. For details, see [MySQL:
Handling upstream schema changes with zero
downtime](/ingest-data/mysql/source-versioning/).

See also [Handling upstream operations](#handling-upstream-operations) for
additional upstream operation considerations.

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

## Privileges

The privileges required to execute this statement are:

- `CREATE` privileges on the containing schema.
- `USAGE` privileges on all types used in the table definition.
- `USAGE` privileges on the schemas that all types in the statement are
  contained in.

## Examples

### Create a table

To create new **read-only** tables from a source table, use the `CREATE
TABLE ... FROM SOURCE ... (REFERENCE <upstream_schema>.<upstream_table>)`
statement in a [DDL transaction
block](/sql/begin/#ddl-only-transactions). The following example creates
**read-only** tables `items` and `orders` from the MySQL source's
`mydb.items` and `mydb.orders` tables.

{{< note >}}

- Although the example creates the tables with the same names as the
upstream tables, the tables in Materialize can have names that differ from
the referenced table names.

- For supported MySQL data types, refer to [supported
types](/sql/create-table/mysql/#supported-data-types).

{{< /note >}}
```mzsql
/* This example assumes:
  - In the upstream MySQL, you have configured:
    - GTID-based binary log replication.
    - `binlog_row_metadata = FULL`.
    - A replication user and password with the appropriate access.
  - In Materialize:
    - You have created a secret for the MySQL password.
    - You have defined the connection to the upstream MySQL.
    - You have used the connection to create a source.

   For example (substitute with your configuration):
      CREATE SECRET mysqlpass AS '<replication user password>'; -- substitute
      CREATE CONNECTION mysql_connection TO MYSQL (
        HOST '<hostname>',          -- substitute
        PORT 3306,
        USER <replication user>,    -- substitute
        PASSWORD SECRET mysqlpass
        -- [, <network security configuration> ]
      );

      CREATE SOURCE mysql_source
      FROM MYSQL CONNECTION mysql_connection;
*/

BEGIN;
CREATE TABLE items
FROM SOURCE mysql_source (REFERENCE mydb.items)
;
CREATE TABLE orders
FROM SOURCE mysql_source (REFERENCE mydb.orders)
;
COMMIT;

```
{{< include-md
file="content/headless/create-table-from-source-snapshotting.md" >}}

{{< include-md file="content/headless/create-table-if-not-exists-tip.md" >}}

## Related pages

- [`CREATE SOURCE: MySQL (New Syntax)`](/sql/create-source/mysql-v2/)
- [`DROP TABLE`](/sql/drop-table)

---

## CREATE TABLE: PostgreSQL source table

In Materialize, you can create read-only tables from [PostgreSQL sources created
using the new syntax](/sql/create-source/postgres-v2/).

> **Note:** You must be on **v26+** to use the new syntax.

## Syntax

> **Note:** Source-populated tables are **read-only** tables. Users **cannot** perform write
> operations
> ([`INSERT`](/sql/insert/)/[`UPDATE`](/sql/update/)/[`DELETE`](/sql/delete/)) on
> these tables.

To create a read-only table from a [source](/sql/create-source/) connected
(via native connector) to an external PostgreSQL:

```mzsql
CREATE TABLE [IF NOT EXISTS] <table_name> FROM SOURCE <source_name> (REFERENCE <upstream_table>)
[WITH (
    TEXT COLUMNS (<column_name> [, ...])
  | EXCLUDE COLUMNS (<column_name> [, ...])
  | PARTITION BY (<column_name> [, ...])
  [, ...]
)]
;

```

| Syntax element | Description |
| --- | --- |
| **IF NOT EXISTS** | *Optional.* If specified, do not throw an error if the table with the same name already exists. Instead, issue a notice and skip the table creation.  {{< include-md file="content/headless/create-table-if-not-exists-tip.md" >}}  |
| `<table_name>` |  The name of the table to create. Names for tables must follow the [naming guidelines](/sql/identifiers/#naming-restrictions).  |
| `<source_name>` |  The name of the [source](/sql/create-source/) associated with the reference object from which to create the table.  |
| **(REFERENCE <upstream_table>)** |  The name of the upstream table from which to create the table. You can create multiple tables from the same upstream table.  To find the upstream tables available in your [source](/sql/create-source/), you can use the following query, substituting your source name for `<source_name>`:  <br>  ```mzsql SELECT refs.* FROM mz_internal.mz_source_references refs, mz_sources s WHERE s.name = '<source_name>' -- substitute with your source name AND refs.source_id = s.id; ```  |
| **WITH (<with_option>[,...])** | The following `<with_option>`s are supported:  \| Option \| Description \| \|--------\|-------------\| \| `TEXT COLUMNS (<column_name> [, ...])` \|*Optional.* If specified, decode data as `text` for the listed column(s),such as for unsupported data types. See also [supported types](#supported-data-types). \| \| `EXCLUDE COLUMNS (<column_name> [, ...])`\| *Optional.* If specified,exclude the listed column(s) from the table, such as for unsupported data types. See also [supported types](#supported-data-types).\| \| `PARTITION BY (<column_name> [, ...])` \| {{< include-md file="content/headless/partition-by-option-description.md" >}} \|  |

## Details

### DDL transaction block

For performance, when issuing multiple `CREATE TABLE FROM SOURCE...` statements,
use within a [transaction block](/sql/begin/#ddl-only-transactions).

### Source-populated tables and snapshotting

Creating the tables from sources starts the [snapshotting](/ingest-data/#snapshotting) process. Snapshotting syncs the
currently available data into Materialize. Because the initial snapshot is
persisted in the storage layer atomically (i.e., at the same ingestion
timestamp), you are not able to query the table until snapshotting is complete.

> **Note:** During the snapshotting, the data ingestion for the existing tables for the same
> source is temporarily blocked. As such, if possible, you can resize the cluster
> to speed up the snapshotting process and once the process finishes, resize the
> cluster for steady-state. You can monitor the snapshot progress on the overview
> page for the source in the Materialize console.

### Supported data types

<p>Materialize natively supports the following PostgreSQL types (including the
array type for each of the types):</p>
<ul style="column-count: 3"><li><code>bool</code></li><li><code>bpchar</code></li><li><code>bytea</code></li><li><code>char</code></li><li><code>date</code></li><li><code>daterange</code></li><li><code>float4</code></li><li><code>float8</code></li><li><code>int2</code></li><li><code>int2vector</code></li><li><code>int4</code></li><li><code>int4range</code></li><li><code>int8</code></li><li><code>int8range</code></li><li><code>interval</code></li><li><code>json</code></li><li><code>jsonb</code></li><li><code>numeric</code></li><li><code>numrange</code></li><li><code>oid</code></li><li><code>text</code></li><li><code>time</code></li><li><code>timestamp</code></li><li><code>timestamptz</code></li><li><code>tsrange</code></li><li><code>tstzrange</code></li><li><code>uuid</code></li><li><code>varchar</code></li></ul>

Replicating tables that contain **unsupported [data types](/sql/types/)** is
possible via the `TEXT COLUMNS` option. The specified columns will be
treated as `text`; i.e., will not have the expected PostgreSQL type
features. For example:

* [`enum`]: When decoded as `text`, the implicit ordering of the original
  PostgreSQL `enum` type is not preserved; instead, Materialize will sort values
  as `text`.

* [`money`]: When decoded as `text`, resulting `text` value cannot be cast
back to `numeric`, since PostgreSQL adds typical currency formatting to the
output.

[`enum`]: https://www.postgresql.org/docs/current/datatype-enum.html
[`money`]: https://www.postgresql.org/docs/current/datatype-money.html

### Handling table schema changes

The use of `CREATE SOURCE` (new syntax) with `CREATE TABLE FROM SOURCE` allows
for the handling of the upstream DDL changes, specifically adding or dropping
columns in the upstream tables, without downtime. For details, see [PostgreSQL:
Handling upstream schema changes with zero
downtime](/ingest-data/postgres/source-versioning/).

See also [Handling upstream operations](#handling-upstream-operations) for
additional upstream operation considerations.

### Inherited tables

When using [PostgreSQL table inheritance](https://www.postgresql.org/docs/current/tutorial-inheritance.html),
PostgreSQL serves data from `SELECT`s as if the inheriting tables' data is
also present in the inherited table. However, both PostgreSQL's logical
replication and `COPY` only present data written to the tables themselves,
i.e. the inheriting data is _not_ treated as part of the inherited table.

PostgreSQL sources use logical replication and `COPY` to ingest table data,
so inheriting tables' data will only be ingested as part of the inheriting
table, i.e. in Materialize, the data will not be returned when serving
`SELECT`s from the inherited table.

You can mimic PostgreSQL's `SELECT` behavior with inherited tables by
creating a materialized view that unions data from the inherited and
inheriting tables (using `UNION ALL`). However, if new tables inherit from
the table, data from the inheriting tables will not be available in the
view. You will need to add the inheriting tables via `CREATE TABLE .. FROM
SOURCE` and create a new view (materialized or non-) that unions the new
table.

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

- Dropping a table (`DROP TABLE`), removing it from the publication (`ALTER PUBLICATION ... DROP TABLE`), or dropping the publication (`DROP PUBLICATION`).
- Renaming a table or moving it to a different schema.
- Setting a table's replica identity to anything other than `FULL` (`ALTER TABLE ... REPLICA IDENTITY`).
- Truncating a table (`TRUNCATE`). To clear a table without putting it into an error state, use an unqualified `DELETE FROM t;` instead.

## Privileges

The privileges required to execute this statement are:

- `CREATE` privileges on the containing schema.
- `USAGE` privileges on all types used in the table definition.
- `USAGE` privileges on the schemas that all types in the statement are
  contained in.

## Examples

### Create a table

> **Note:** You must be on **v26+** to use the new syntax.
> The example assumes you have configured your upstream PostgreSQL 11+ (i.e.,
> enabled logical replication, created the publication for the various tables and
> replication user, and updated the network configuration).
> For details about configuring your upstream system, see the [PostgreSQL
> integration guides](/ingest-data/postgres/#supported-versions-and-services).

To create new **read-only** tables from a source table, use the `CREATE
TABLE ... FROM SOURCE ... (REFERENCE <upstream_table>)` statement in a [DDL
transaction block](/sql/begin/#ddl-only-transactions). The following example
creates **read-only** tables `items` and `orders` from the PostgreSQL
source's `public.items` and `public.orders` tables (the schema is `public`).

{{< note >}}

- Although the example creates the tables with the same names as the
upstream tables, the tables in Materialize can have names that differ from
the referenced table names.

- For supported PostgreSQL data types, refer to [supported
types](/sql/create-table/postgres/#supported-data-types).

{{< /note >}}
```mzsql
/* This example assumes:
  - In the upstream PostgreSQL, you have defined:
    - replication user and password with the appropriate access.
    - a publication named `mz_source` for the `items` and `orders` tables.
  - In Materialize:
    - You have created a secret for the PostgreSQL password.
    - You have defined the connection to the upstream PostgreSQL.
    - You have used the connection to create a source.

   For example (substitute with your configuration):
      CREATE SECRET pgpass AS '<replication user password>'; -- substitute
      CREATE CONNECTION pg_connection TO POSTGRES (
        HOST '<hostname>',          -- substitute
        DATABASE <db>,              -- substitute
        USER <replication user>,    -- substitute
        PASSWORD SECRET pgpass
        -- [, <network security configuration> ]
      );

      CREATE SOURCE pg_source
      FROM POSTGRES CONNECTION pg_connection (
        PUBLICATION 'mz_source'       -- substitute
      );
*/

BEGIN;
CREATE TABLE items
FROM SOURCE pg_source(REFERENCE public.items)
;
CREATE TABLE orders
FROM SOURCE pg_source(REFERENCE public.orders)
;
COMMIT;

```
{{< include-md
file="content/headless/create-table-from-source-snapshotting.md" >}}

{{< include-md file="content/headless/create-table-if-not-exists-tip.md" >}}

Once the snapshotting process completes and the table is in the running state, you can query the table:
```mzsql
SELECT * FROM items;

```

## Related pages

- [`CREATE SOURCE: PostgreSQL (New Syntax)`](/sql/create-source/postgres-v2/)
- [`DROP TABLE`](/sql/drop-table)

---

## CREATE TABLE: Read-write table

Read-write tables let you read ([`SELECT`](/sql/select/)) and write
([`INSERT`](/sql/insert/), [`UPDATE`](/sql/update/), [`DELETE`](/sql/delete/))
to the table.

## Syntax

To create a new read-write table (i.e., users can perform
[`SELECT`](/sql/select/), [`INSERT`](/sql/insert/),
[`UPDATE`](/sql/update/), and [`DELETE`](/sql/delete/) operations):

```mzsql
CREATE [TEMP|TEMPORARY] TABLE [IF NOT EXISTS] <table_name> (
  <column_name> <column_type> [NOT NULL][DEFAULT <default_expr>]
  [, ...]
)
[WITH (
  PARTITION BY (<column_name> [, ...]) |
  RETAIN HISTORY [=] FOR <duration>
)]
;

```

| Syntax element | Description |
| --- | --- |
| **TEMP** / **TEMPORARY** | *Optional.* If specified, mark the table as temporary.  Temporary tables are: - Automatically dropped at the end of the session; - Not visible to other connections; - Created in the special `mz_temp` schema.  Temporary tables may depend upon other temporary database objects, but non-temporary tables may not depend on temporary objects.  |
| **IF NOT EXISTS** | *Optional.* If specified, do not throw an error if the table with the same name already exists. Instead, issue a notice and skip the table creation.  |
| `<table_name>` |  The name of the table to create. Names for tables must follow the [naming guidelines](/sql/identifiers/#naming-restrictions).  |
| `<column_name>` |  The name of a column to be created in the new table. Names for columns must follow the [naming guidelines](/sql/identifiers/#naming-restrictions).  |
| `<column_type>` |  The type of the column. For supported types, see [SQL data types](/sql/types/).  |
| **NOT NULL** | *Optional.* If specified, disallow  _NULL_ values for the column. Columns without this constraint can contain _NULL_ values.  |
| **DEFAULT <default_expr>** | *Optional.* If specified, use the `<default_expr>` as the default value for the column. If not specified, `NULL` is used as the default value.  |
| **WITH (<with_option>[,...])** |  The following `<with_option>`s are supported:  \| Option \| Description \| \|--------\|-------------\| \| `PARTITION BY (<column> [, ...])` \| {{< include-md file="content/headless/partition-by-option-description.md" >}} \| \| `RETAIN HISTORY <duration>` \| *Optional.* ***Private preview.** This option has known performance or stability issues and is under active development.* <br>If specified, Materialize retains historical data for the specified duration, which is useful to implement [durable subscriptions](/transform-data/patterns/durable-subscriptions/#history-retention-period).<br>Accepts positive [interval](/sql/types/interval/) values (e.g., `'1hr'`).\|  |

## Table names and column names

Names for tables and column(s) must follow the [naming
guidelines](/sql/identifiers/#naming-restrictions).

## Known limitations

Tables do not currently support:

- Primary keys
- Unique constraints
- Check constraints

See also the known limitations for [`INSERT`](/sql/insert#known-limitations),
[`UPDATE`](/sql/update#known-limitations), and [`DELETE`](/sql/delete#known-limitations).

## Privileges

The privileges required to execute this statement are:

- `CREATE` privileges on the containing schema.
- `USAGE` privileges on all types used in the table definition.
- `USAGE` privileges on the schemas that all types in the statement are
  contained in.

## Examples

### Create a table

The following example uses `CREATE TABLE` to create a new read-write table
`mytable` with two columns `a` (of type `int`) and `b` (of type `text` and
not nullable):
```mzsql
CREATE TABLE mytable (a int, b text NOT NULL);

```

Once a user-populated table is created, you can perform CRUD
(Create/Read/Update/Delete) operations on it.

The following example uses [`INSERT`](/sql/insert/) to write two rows to the table:
```mzsql
INSERT INTO mytable VALUES
(1, 'hello'),
(2, 'goodbye')
;

```

The following example uses [`SELECT`](/sql/select/) to read all rows from the table:
```mzsql
SELECT * FROM mytable;

```The results should display the two rows inserted:

```hc {hl_lines="3-4"}
| a | b       |
| - | ------- |
| 1 | hello   |
| 2 | goodbye |
```

## Related pages

- [`INSERT`](/sql/insert/)
- [`DROP TABLE`](/sql/drop-table)

---

## CREATE TABLE: SQL Server source table

In Materialize, you can create read-only tables from [SQL Server sources created
using the new syntax](/sql/create-source/sql-server-v2/).

> **Note:** You must be on **v26.14.1+** to use the syntax.

## Syntax

> **Note:** Source-populated tables are **read-only** tables. Users **cannot** perform write
> operations
> ([`INSERT`](/sql/insert/)/[`UPDATE`](/sql/update/)/[`DELETE`](/sql/delete/)) on
> these tables.

To create a read-only table from a [source](/sql/create-source/) connected
(via native connector) to an external SQL Server database:

```mzsql
CREATE TABLE [IF NOT EXISTS] <table_name> FROM SOURCE <source_name> (REFERENCE <upstream_table>)
[WITH (
    TEXT COLUMNS (<column_name> [, ...])
  | EXCLUDE COLUMNS (<column_name> [, ...])
  | PARTITION BY (<column_name> [, ...])
  [, ...]
)]
;

```

| Syntax element | Description |
| --- | --- |
| **IF NOT EXISTS** | *Optional.* If specified, do not throw an error if the table with the same name already exists. Instead, issue a notice and skip the table creation.  {{< include-md file="content/headless/create-table-if-not-exists-tip.md" >}}  |
| `<table_name>` |  The name of the table to create. Names for tables must follow the [naming guidelines](/sql/identifiers/#naming-restrictions).  |
| `<source_name>` |  The name of the [source](/sql/create-source/) associated with the reference object from which to create the table.  |
| **(REFERENCE <upstream_table>)** |  The name of the upstream table from which to create the table. You can create multiple tables from the same upstream table.  To find the upstream tables available in your [source](/sql/create-source/), you can use the following query, substituting your source name for `<source_name>`:  <br>  ```mzsql SELECT refs.* FROM mz_internal.mz_source_references refs, mz_sources s WHERE s.name = '<source_name>' -- substitute with your source name AND refs.source_id = s.id; ```  |
| **WITH (<with_option>[,...])** | The following `<with_option>`s are supported:  \| Option \| Description \| \|--------\|-------------\| \| `TEXT COLUMNS (<column_name> [, ...])` \|*Optional.* If specified, decode data as `text` for the listed column(s),such as for unsupported data types. See also [supported types](#supported-data-types). \| \| `EXCLUDE COLUMNS (<column_name> [, ...])`\| *Optional.* If specified,exclude the listed column(s) from the table, such as for unsupported data types. See also [supported types](#supported-data-types).\| \| `PARTITION BY (<column_name> [, ...])` \| {{< include-md file="content/headless/partition-by-option-description.md" >}} \|  |

## Details

### DDL transaction block

For performance, when issuing multiple `CREATE TABLE FROM SOURCE...` statements,
use within a [transaction block](/sql/begin/#ddl-only-transactions).

### Source-populated tables and snapshotting

Creating the tables from sources starts the [snapshotting](/ingest-data/#snapshotting) process. Snapshotting syncs the
currently available data into Materialize. Because the initial snapshot is
persisted in the storage layer atomically (i.e., at the same ingestion
timestamp), you are not able to query the table until snapshotting is complete.

> **Note:** During the snapshotting, the data ingestion for the existing tables for the same
> source is temporarily blocked. As such, if possible, you can resize the cluster
> to speed up the snapshotting process and once the process finishes, resize the
> cluster for steady-state. You can monitor the snapshot progress on the overview
> page for the source in the Materialize console.

### Supported data types

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

### Handling table schema changes

The use of `CREATE SOURCE` (new syntax) with `CREATE TABLE FROM SOURCE` allows
for the handling of the upstream DDL changes, specifically adding or dropping
columns in the upstream tables, without downtime. For details, see [SQL Server:
Handling upstream schema changes with zero
downtime](/ingest-data/sql-server/source-versioning/).

See also [Handling upstream operations](#handling-upstream-operations) for
additional upstream operation considerations.

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

## Privileges

The privileges required to execute this statement are:

- `CREATE` privileges on the containing schema.
- `USAGE` privileges on all types used in the table definition.
- `USAGE` privileges on the schemas that all types in the statement are
  contained in.

## Examples

### Create a table

To create new **read-only** tables from a source table, use the `CREATE
TABLE ... FROM SOURCE ... (REFERENCE <upstream_table>)` statement in a [DDL
transaction block](/sql/begin/#ddl-only-transactions). The following example
creates **read-only** tables `items` and `orders` from the SQL Server
source's `dbo.items` and `dbo.orders` tables.

{{< note >}}

- Although the example creates the tables with the same names as the
upstream tables, the tables in Materialize can have names that differ from
the referenced table names.

- The upstream table must have [Change Data Capture
(CDC)](/ingest-data/sql-server/) enabled.

- For supported SQL Server data types, refer to [supported
types](/sql/create-table/sql-server/#supported-data-types).

{{< /note >}}
```mzsql
/* This example assumes:
  - In the upstream SQL Server, you have:
    - Enabled Change Data Capture (CDC) on the database and the tables.
    - A user and password with the appropriate access.
  - In Materialize:
    - You have created a secret for the SQL Server password.
    - You have defined the connection to the upstream SQL Server.
    - You have used the connection to create a source.

   For example (substitute with your configuration):
      CREATE SECRET sqlserver_pass AS '<password>'; -- substitute
      CREATE CONNECTION sql_server_connection TO SQL SERVER (
        HOST '<hostname>',          -- substitute
        PORT 1433,
        DATABASE <db>,              -- substitute
        USER <user>,                -- substitute
        PASSWORD SECRET sqlserver_pass
        -- [, <network security configuration> ]
      );

      CREATE SOURCE sql_server_source
      FROM SQL SERVER CONNECTION sql_server_connection;
*/

BEGIN;
CREATE TABLE items
FROM SOURCE sql_server_source (REFERENCE dbo.items)
;
CREATE TABLE orders
FROM SOURCE sql_server_source (REFERENCE dbo.orders)
;
COMMIT;

```
{{< include-md
file="content/headless/create-table-from-source-snapshotting.md" >}}

{{< include-md file="content/headless/create-table-if-not-exists-tip.md" >}}

To verify that the tables have been created, you can run [`SHOW
TABLES`](/sql/show-tables/) to list all tables in the current
[schema](/sql/namespaces/#namespace-hierarchy):
```mzsql
SHOW TABLES;

```The results should include the tables `items` and `orders`:

```hc {hl_lines="3-4"}
| name   | comment |
| ------ | ------- |
| items  |         |
| orders |         |
```

Inspect the table columns using the [`SHOW COLUMNS`](/sql/show-columns/)
command:
```mzsql
SHOW COLUMNS FROM items;

```The results should display the table columns, with types mapped from the
upstream SQL Server table. For the list of supported SQL Server data types,
refer to [supported
types](/sql/create-table/sql-server/#supported-data-types).

```hc
| name     | nullable | type              | comment |
| -------- | -------- | ----------------- | ------- |
| id       | false    | integer           |         |
| item     | true     | character varying |         |
| quantity | true     | integer           |         |
```

Once the snapshotting process completes and the tables are in the running
state, you can query them:
```mzsql
SELECT * FROM items ORDER BY id;

``````hc
| id | item   | quantity |
| -- | ------ | -------- |
| 1  | widget | 5        |
| 2  | gadget | 2        |
```

## Related pages

- [`CREATE SOURCE: SQL Server (New Syntax)`](/sql/create-source/sql-server-v2/)
- [`DROP TABLE`](/sql/drop-table)

