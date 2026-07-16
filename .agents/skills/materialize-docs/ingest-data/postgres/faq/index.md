# FAQ: PostgreSQL sources
Frequently asked questions about PostgreSQL sources in Materialize
This page addresses common questions and challenges when working with PostgreSQL
sources in Materialize. For general ingestion questions/troubleshooting, see:
- [Monitoring data ingestion](/ingest-data/monitoring-data-ingestion/).
- [Troubleshooting/FAQ](/ingest-data/troubleshooting/).

## For my trial/POC, what if I cannot use `REPLICA IDENTITY FULL`?

Materialize requires `REPLICA IDENTITY FULL` on PostgreSQL tables to capture all
column values in change events. If for your trial/POC (Proof-of-concept) you
cannot modify your existing tables, here are some common alternatives:

- **Outbox Pattern (shadow tables)**

  > **Note:** With the Outbox pattern, you will need to implement dual writes so that all changes apply to both the original and shadow tables.

  With the Outbox pattern, you create duplicate "shadow" tables for the ones you
  want to replicate and set the shadow tables to `REPLICA IDENTITY FULL`. You
  can then use these shadow tables for Materialize instead of the originals.

- **Sidecar Pattern**

  > **Note:** With the Sidecar pattern, you will need to keep the sidecar in sync with the
>   source database (e.g., via logical replication or ETL processes).

  With the Sidecar pattern, you create a separate PostgreSQL instance as an
  integration layer. That is, in the sidecar instance, you recreate the tables
  you want to replicate, setting these tables with `REPLICA IDENTITY FULL`. You
  can then use the sidecar for Materialize instead of your primary database.

  For step-by-step instructions, see [Ingest from a dedicated PostgreSQL
  replica](/ingest-data/postgres/logical-replica/).

- **Debezium + Kafka**

  With [Debezium + Kafka](/ingest-data/postgres/postgres-debezium/), if the
  tables to replicate each have a **primary key** defined, you can use the
  default replica identity. However, without `REPLICA IDENTITY FULL`, you cannot
  ingest unchanged
  [TOASTed](https://www.postgresql.org/docs/current/storage-toast.html) values.

  > **Note:** - We **strongly recommend** using the native
>     [PostgreSQL](/sql/create-source/postgres-v2/) source connector with `REPLICA
>     IDENTITY FULL` instead.
>   - [Contact Support](/support/) to discuss strategies for enabling `REPLICA
>     IDENTITY FULL`.

## For production, what if I cannot use `REPLICA IDENTITY FULL`?

With [Debezium + Kafka](/ingest-data/postgres/postgres-debezium/), if the tables
to replicate each have a **primary key** defined, you can use the default
replica identity. However, without `REPLICA IDENTITY FULL`, you cannot ingest
unchanged [TOASTed](https://www.postgresql.org/docs/current/storage-toast.html)
values.

> **Note:** - We **strongly recommend** using the native
>   [PostgreSQL](/sql/create-source/postgres-v2/) source connector with `REPLICA
>   IDENTITY FULL` instead.
> - [Contact Support](/support/) to discuss strategies for enabling `REPLICA
>   IDENTITY FULL`.

## What if my table contains data types that are unsupported in Materialize?

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

See also: [PostgreSQL considerations](/ingest-data/postgres/#considerations).
