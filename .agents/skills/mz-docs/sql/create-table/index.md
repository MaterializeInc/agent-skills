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
  | EXCLUDE CONSTRAINTS ('<constraint_name>' [, ...])
  | EXCLUDE ALL CONSTRAINTS
  | EXCLUDE ALL NOT NULL CONSTRAINTS
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
  | EXCLUDE CONSTRAINTS ('<constraint_name>' [, ...])
  | EXCLUDE ALL CONSTRAINTS
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

## Pages in this section

- [CREATE TABLE: Kafka source table](/sql/create-table/kafka/index.md): Create a read-only table from a Kafka/Redpanda source (new syntax).
- [CREATE TABLE: MySQL source table](/sql/create-table/mysql/index.md): Create a read-only table from a MySQL source (new syntax).
- [CREATE TABLE: PostgreSQL source table](/sql/create-table/postgres/index.md): Create a read-only table from a PostgreSQL source (new syntax).
- [CREATE TABLE: Read-write table](/sql/create-table/user-populated/index.md): Create a read-write, user-populated table in Materialize.
- [CREATE TABLE: SQL Server source table](/sql/create-table/sql-server/index.md): Create a read-only table from a SQL Server source (new syntax).
