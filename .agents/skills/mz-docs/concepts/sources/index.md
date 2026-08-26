# Sources
Learn about sources in Materialize.
## Overview

A source in Materialize represents an external data source. More concretely, it
specifies the connection and the ingestion configuration to use for a particular
external data source (e.g., PostgreSQL, Kafka). For those familiar with
PostgreSQL's foreign servers and foreign tables, a source is like a foreign
server, and the tables (or subsources) created from the source are like foreign
tables.

## Supported external systems

Materialize supports ingesting data from the following external systems:

| Type | External system |
|------|-----------------|
| **Databases (CDC): native connectors** | [PostgreSQL](/ingest-data/postgres/) <br> [MySQL](/ingest-data/mysql/) <br> [SQL Server](/ingest-data/sql-server/) |
| **Databases (CDC): via the Kafka connector** | [CockroachDB](/ingest-data/cdc-cockroachdb/) (using changefeeds) <br> [MongoDB](/ingest-data/mongodb/) (using Debezium) |
| **Message brokers** | [Kafka](/ingest-data/kafka/) <br> [Redpanda](/sql/create-source/kafka) |
| **Webhooks** | [Amazon EventBridge](/ingest-data/webhooks/amazon-eventbridge/) <br> [Segment](/ingest-data/webhooks/segment/) <br> [HubSpot](/ingest-data/webhooks/hubspot/) <br> [RudderStack](/ingest-data/webhooks/rudderstack/) <br> [SnowcatCloud](/ingest-data/webhooks/snowcatcloud/) <br> [Stripe](/ingest-data/webhooks/stripe/)|

## Creating a source

### Prerequisites

Before creating a source in Materialize, you must ensure that the external data
source is properly configured and accessible so that Materialize can establish a
connection and ingest its data. The exact configuration depends on the type of
data source.

### CREATE SOURCE syntax

To create a source, you use the [`CREATE SOURCE`](/sql/create-source/) syntax.
There are two versions of the syntax:

- *Recommended.* The new [`CREATE SOURCE`](/sql/create-source/#new-syntax)
  syntax, used with [`CREATE TABLE ... FROM SOURCE`](/sql/create-table/). The
  new syntax allows Materialize to handle certain upstream schema changes,
  specifically adding or dropping columns, **without** downtime.

- The legacy [`CREATE SOURCE ... FOR <ALL
  TABLES|TABLES|SCHEMAS>`](/sql/create-source/#legacy-syntax) syntax, which
  creates a source and its subsources. *Subsource* is the legacy term for the
  read-only tables created from a source. With the legacy `CREATE SOURCE ...
  FOR ...` syntax, the subsources are automatically created when the `CREATE
  SOURCE ...` command is issued.

### Tables and subsources

A source makes external data available in Materialize through:

- The [tables](/sql/create-table/) created from it, when using the new
  `CREATE SOURCE` syntax.

- The subsources, when using the legacy `CREATE SOURCE` syntax.

Both the tables and subsources created from a source are **read-only**.
Materialize populates them by ingesting changes from the upstream system, and
you cannot insert, update, or delete their data directly.

## Snapshotting

When you create a table from a source (or, with the legacy syntax, when the
subsources are created), Materialize [snapshots](/concepts/snapshotting/) the
data currently available in the upstream system for that table.

<!--
Syntax-specific (legacy and source-versioning) query behavior during
snapshotting. For the generic (syntax-agnostic) version, see
headless/ingestion/snapshotting-ingestion.md.
-->

Queries on a table that is snapshotting are blocked until its snapshot
completes.

- With the legacy `CREATE` syntax:

  - None of the subsources created as part of `CREATE SOURCE ... FOR ...` are
    queryable until they have all finished snapshotting.

  - When altering a source to add a new subsource (`ALTER SOURCE ... ADD
    SUBSOURCE`), only the new subsource snapshots. The source's other subsources
    remain queryable. **However**, ingestion for these subsources is temporarily
    blocked, so they stop advancing until the snapshot completes.

- With the source-versioning `CREATE TABLE FROM SOURCE` syntax:

  - None of the tables created within a [transaction
    block](/sql/begin/#ddl-only-transactions) are queryable until all their
    snapshots complete.

  - When you create new tables from a source that already has tables, only the
    new tables snapshot. The source's existing tables remain queryable.
    **However**, ingestion for the existing tables is temporarily blocked, so
    they stop advancing until the snapshots for the new tables complete.

See [Snapshotting](/concepts/snapshotting/) for more information.

## Hydration

Hydration is the reconstruction of an object's in-memory state by reading
from Materialize's storage layer and existing indexes; hydration does not
read from the upstream system.

- For Kafka upsert sources, their associated read-only tables (or
  subsources if using the legacy syntax) rebuild their internal upsert
  index from storage on replica (re)start or cluster resize.

- For other sources, the hydration process is negligible or not applicable.

See [Hydration](/concepts/hydration/) for more information.

## Sources and clusters

Sources require compute resources in Materialize. That is, sources must be
associated with a [cluster](/concepts/clusters/). If possible, dedicate a
cluster just for sources.

See also [Operational guidelines](/manage/operational-guidelines/).

## Related pages

- [`CREATE SOURCE`](/sql/create-source)
- [`CREATE TABLE`](/sql/create-table)
- [Snapshotting](/concepts/snapshotting/)
- [Hydration](/concepts/hydration/)
