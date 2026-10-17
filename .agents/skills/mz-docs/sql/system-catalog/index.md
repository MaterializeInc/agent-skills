# System catalog

The system catalog stores metadata about your Materialize instance.

Materialize exposes a system catalog that contains metadata about the running
Materialize instance.

The system catalog consists of several schemas that are implicitly available in
all databases. These schemas contain sources, tables, and views that expose
different types of metadata.

  * [`mz_catalog`](mz_catalog), which exposes metadata in Materialize's
    native format.

  * [`pg_catalog`](pg_catalog), which presents the data in `mz_catalog` in
    the format used by PostgreSQL.

  * [`information_schema`](information_schema), which presents the data in
    `mz_catalog` in the format used by the SQL standard's information_schema.

  * [`mz_internal`](mz_internal), which exposes internal metadata about
    Materialize in an unstable format that is likely to change.

  * [`mz_introspection`](mz_introspection), which contains replica
    introspection relations.

These schemas contain sources, tables, and views that expose metadata like:

  * Descriptions of each database, schema, source, table, view, sink, and
    index in the system.

  * Descriptions of all running dataflows.

  * Metrics about dataflow execution.

Whenever possible, applications should prefer to query `mz_catalog` over
`pg_catalog`. The mapping between Materialize concepts and PostgreSQL concepts
is not one-to-one, and so the data in `pg_catalog` cannot accurately represent
the particulars of Materialize.

## Pages in this section

- [information_schema](/sql/system-catalog/information_schema/index.md): information_schema is a system catalog that presents metadata in the format used by SQL standard.
- [mz_catalog](/sql/system-catalog/mz_catalog/index.md): mz_catalog is a system catalog that exposes metadata in Materialize's native format.
- [mz_internal](/sql/system-catalog/mz_internal/index.md): mz_internal is a system catalog schema which exposes internal metadata about Materialize. This schema is not part of Materialize's stable interface.
- [mz_introspection](/sql/system-catalog/mz_introspection/index.md): mz_introspection is a system catalog schema which contains replica introspection relations. This schema is not part of Materialize's stable interface.
- [pg_catalog](/sql/system-catalog/pg_catalog/index.md): pg_catalog is a system catalog that presents metadata in the format used by PostgreSQL.
