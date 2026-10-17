# SQL commands

SQL commands reference.

## Create/Alter/Drop Objects

| CREATE | ALTER | DROP |
| --- | --- | --- |
| [`CREATE CLUSTER`](/sql/create-cluster) | [`ALTER CLUSTER`](/sql/alter-cluster) | [`DROP CLUSTER`](/sql/drop-cluster) |
| [`CREATE CLUSTER REPLICA`](/sql/create-cluster-replica) | [`ALTER CLUSTER REPLICA`](/sql/alter-cluster-replica) | [`DROP CLUSTER REPLICA`](/sql/drop-cluster-replica) |
| [`CREATE CONNECTION`](/sql/create-connection) | [`ALTER CONNECTION`](/sql/alter-connection) | [`DROP CONNECTION`](/sql/drop-connection) |
| [`CREATE DATABASE`](/sql/create-database) | [`ALTER DATABASE`](/sql/alter-database) | [`DROP DATABASE`](/sql/drop-database) |
| [`CREATE INDEX`](/sql/create-index) | [`ALTER INDEX`](/sql/alter-index) | [`DROP INDEX`](/sql/drop-index) |
| [`CREATE MATERIALIZED VIEW`](/sql/create-materialized-view) | [`ALTER MATERIALIZED VIEW`](/sql/alter-materialized-view) | [`DROP MATERIALIZED VIEW`](/sql/drop-materialized-view) |
| [`CREATE NETWORK POLICY`](/sql/create-network-policy) | [`ALTER NETWORK POLICY`](/sql/alter-network-policy) | [`DROP NETWORK POLICY`](/sql/drop-network-policy) |
| [`CREATE ROLE`](/sql/create-role) | [`ALTER ROLE`](/sql/alter-role) | [`DROP ROLE`](/sql/drop-role) <br>[`DROP USER`](/sql/drop-user) |
| [`CREATE SCHEMA`](/sql/create-schema) | [`ALTER SCHEMA`](/sql/alter-schema) | [`DROP SCHEMA`](/sql/drop-schema) |
| [`CREATE SECRET`](/sql/create-secret) | [`ALTER SECRET`](/sql/alter-secret) | [`DROP SECRET`](/sql/drop-secret) |
| [`CREATE SINK`](/sql/create-sink) | [`ALTER SINK`](/sql/alter-sink) | [`DROP SINK`](/sql/drop-sink) |
| [`CREATE SOURCE`](/sql/create-source) | [`ALTER SOURCE`](/sql/alter-source) | [`DROP SOURCE`](/sql/drop-source) |
| [`CREATE TABLE`](/sql/create-table) | [`ALTER TABLE`](/sql/alter-table) | [`DROP TABLE`](/sql/drop-table) |
| [`CREATE TYPE`](/sql/create-type) | [`ALTER TYPE`](/sql/alter-type) | [`DROP TYPE`](/sql/drop-type) |
| [`CREATE VIEW`](/sql/create-view) | [`ALTER VIEW`](/sql/alter-view) | [`DROP VIEW`](/sql/drop-view) |

## Create/Read/Update/Delete Data

The following commands perform CRUD operations on materialized views, views,
sources, and tables:

| <strong>Select/Subscribe</strong> |  - [`SELECT`](/sql/select)  - [`SUBSCRIBE`](/sql/subscribe)    |
| <strong>Cursor</strong> |  - [`CLOSE`](/sql/close)  - [`DECLARE`](/sql/declare)  - [`FETCH`](/sql/fetch)   |
| <strong>Sink</strong> |  - [`ALTER SINK`](/sql/alter-sink)  - [`CREATE SINK`](/sql/create-sink)  - [`DROP SINK`](/sql/drop-sink)   |
| <strong>Transactions</strong> |  - [`BEGIN`](/sql/begin)  - [`COMMIT`](/sql/commit)  - [`ROLLBACK`](/sql/rollback)   |
| <strong>Copy</strong> |  - [`COPY FROM`](/sql/copy-from)  - [`COPY TO`](/sql/copy-to)   |

## RBAC

Commands to manage roles and privileges and owners:

| <strong>Roles</strong> |  - [`ALTER ROLE`](/sql/alter-role)  - [`CREATE ROLE`](/sql/create-role)  - [`DROP ROLE`](/sql/drop-role) <br>[`DROP USER`](/sql/drop-user)  - [`GRANT ROLE`](/sql/grant-role)  - [`REVOKE ROLE`](/sql/revoke-role)  - [`SHOW ROLES`](/sql/show-roles)   |
| <strong>Privileges</strong> |  - [`ALTER DEFAULT PRIVILEGES`](/sql/alter-default-privileges)  - [`GRANT PRIVILEGE`](/sql/grant-privilege)  - [`REVOKE PRIVILEGE`](/sql/revoke-privilege)   |
| <strong>Owners</strong> |  - [`ALTER CLUSTER`](/sql/alter-cluster)  - [`ALTER CLUSTER REPLICA`](/sql/alter-cluster-replica)  - [`ALTER CONNECTION`](/sql/alter-connection)  - [`ALTER DATABASE`](/sql/alter-database)  - [`ALTER MATERIALIZED VIEW`](/sql/alter-materialized-view)  - [`ALTER SCHEMA`](/sql/alter-schema)  - [`ALTER SECRET`](/sql/alter-secret)  - [`ALTER SINK`](/sql/alter-sink)  - [`ALTER SOURCE`](/sql/alter-source)  - [`ALTER TABLE`](/sql/alter-table)  - [`ALTER TYPE`](/sql/alter-type)  - [`ALTER VIEW`](/sql/alter-view)  - [`DROP OWNED`](/sql/drop-owned)  - [`REASSIGN OWNED`](/sql/reassign-owned)   |

## Query Introspection (`Explain`)

- [`EXPLAIN ANALYZE`](/sql/explain-analyze)

- [`EXPLAIN FILTER PUSHDOWN`](/sql/explain-filter-pushdown)

- [`EXPLAIN PLAN`](/sql/explain-plan)

- [`EXPLAIN SCHEMA`](/sql/explain-schema)

- [`EXPLAIN TIMESTAMP`](/sql/explain-timestamp)

## Object Introspection (`SHOW`)

- [`SHOW`](/sql/show)

- [`SHOW CLUSTER REPLICAS`](/sql/show-cluster-replicas)

- [`SHOW CLUSTERS`](/sql/show-clusters)

- [`SHOW COLUMNS`](/sql/show-columns)

- [`SHOW CONNECTIONS`](/sql/show-connections)

- [`SHOW CREATE CLUSTER`](/sql/show-create-cluster)

- [`SHOW CREATE CONNECTION`](/sql/show-create-connection)

- [`SHOW CREATE INDEX`](/sql/show-create-index)

- [`SHOW CREATE MATERIALIZED VIEW`](/sql/show-create-materialized-view)

- [`SHOW CREATE SINK`](/sql/show-create-sink)

- [`SHOW CREATE SOURCE`](/sql/show-create-source)

- [`SHOW CREATE TABLE`](/sql/show-create-table)

- [`SHOW CREATE TYPE`](/sql/show-create-type)

- [`SHOW CREATE VIEW`](/sql/show-create-view)

- [`SHOW DATABASES`](/sql/show-databases)

- [`SHOW DEFAULT PRIVILEGES`](/sql/show-default-privileges)

- [`SHOW INDEXES`](/sql/show-indexes)

- [`SHOW MATERIALIZED VIEWS`](/sql/show-materialized-views)

- [`SHOW NETWORK POLICIES (Cloud)`](/sql/show-network-policies)

- [`SHOW OBJECTS`](/sql/show-objects)

- [`SHOW PRIVILEGES`](/sql/show-privileges)

- [`SHOW ROLE MEMBERSHIP`](/sql/show-role-membership)

- [`SHOW ROLES`](/sql/show-roles)

- [`SHOW SCHEMAS`](/sql/show-schemas)

- [`SHOW SECRETS`](/sql/show-secrets)

- [`SHOW SINKS`](/sql/show-sinks)

- [`SHOW SOURCES`](/sql/show-sources)

- [`SHOW SUBSOURCES`](/sql/show-subsources)

- [`SHOW TABLES`](/sql/show-tables)

- [`SHOW TYPES`](/sql/show-types)

- [`SHOW VIEWS`](/sql/show-views)

## Session

Commands related with session state and configurations:

- [`DISCARD`](/sql/discard)

- [`RESET`](/sql/reset)

- [`SET`](/sql/set)

- [`SHOW`](/sql/show)

## Validations

- [`VALIDATE CONNECTION`](/sql/validate-connection)

## Prepared Statements

- [`DEALLOCATE`](/sql/deallocate)

- [`EXECUTE`](/sql/execute)

- [`PREPARE`](/sql/prepare)

## Pages in this section

- [Namespaces](/sql/namespaces/index.md): SQL namespaces let you create a taxonomy of objects in Materialize.
- [ALTER CLUSTER](/sql/alter-cluster/index.md): `ALTER CLUSTER` changes the configuration of a cluster.
- [ALTER CLUSTER REPLICA](/sql/alter-cluster-replica/index.md): `ALTER CLUSTER REPLICA` changes properties of a cluster replica.
- [ALTER CONNECTION](/sql/alter-connection/index.md): `ALTER CONNECTION` allows you to modify the value of connection options; rotate secrets associated with connections; rename a connection; and change owner of a connection.
- [ALTER DATABASE](/sql/alter-database/index.md): `ALTER DATABASE` changes properties of a database.
- [ALTER DEFAULT PRIVILEGES](/sql/alter-default-privileges/index.md): `ALTER DEFAULT PRIVILEGES` defines default privileges that will be applied to objects created in the future.
- [ALTER INDEX](/sql/alter-index/index.md): `ALTER INDEX` changes the parameters of an index.
- [ALTER MATERIALIZED VIEW](/sql/alter-materialized-view/index.md): `ALTER MATERIALIZED VIEW` changes the parameters of a materialized view.
- [ALTER NETWORK POLICY (Cloud)](/sql/alter-network-policy/index.md): `ALTER NETWORK POLICY` alters an existing network policy.
- [ALTER ROLE](/sql/alter-role/index.md): `ALTER ROLE` alters the attributes of an existing role.
- [ALTER SCHEMA](/sql/alter-schema/index.md): `ALTER SCHEMA` change properties of a schema
- [ALTER SECRET](/sql/alter-secret/index.md): `ALTER SECRET` changes the contents of a secret.
- [ALTER SINK](/sql/alter-sink/index.md): `ALTER SINK` allows cutting a sink over to a new upstream relation without causing disruption to downstream consumers.
- [ALTER SOURCE](/sql/alter-source/index.md): `ALTER SOURCE` changes certain characteristics of a source.
- [ALTER SYSTEM RESET](/sql/alter-system-reset/index.md): Globally reset a configuration parameter to its default value.
- [ALTER SYSTEM SET](/sql/alter-system-set/index.md): `ALTER SYSTEM SET` globally modifies the value of a configuration parameter.
- [ALTER TABLE](/sql/alter-table/index.md): `ALTER TABLE` changes properties of a table.
- [ALTER TYPE](/sql/alter-type/index.md): `ALTER TYPE` changes properties of a type.
- [ALTER VIEW](/sql/alter-view/index.md): `ALTER VIEW` changes properties of a view.
- [BEGIN](/sql/begin/index.md): `BEGIN` starts a transaction block.
- [CLOSE](/sql/close/index.md): `CLOSE` closes a cursor.
- [COMMENT ON](/sql/comment-on/index.md): `COMMENT ON` adds or updates the comment of an object.
- [COMMIT](/sql/commit/index.md): `COMMIT` ends a transaction block and commits all changes if the transaction statements succeed.
- [COPY FROM](/sql/copy-from/index.md): `COPY FROM` copies data into a table using the COPY protocol.
- [COPY TO](/sql/copy-to/index.md): `COPY TO` outputs results from Materialize to standard output or object storage.
- [CREATE CLUSTER](/sql/create-cluster/index.md): `CREATE CLUSTER` creates a new cluster.
- [CREATE CLUSTER REPLICA](/sql/create-cluster-replica/index.md): `CREATE CLUSTER REPLICA` provisions a new replica of a cluster.
- [CREATE CONNECTION](/sql/create-connection/index.md): `CREATE CONNECTION` describes how to connect and authenticate to an external system in Materialize
- [CREATE DATABASE](/sql/create-database/index.md): `CREATE DATABASE` creates a new database.
- [CREATE INDEX](/sql/create-index/index.md): `CREATE INDEX` creates an in-memory index on a source, view, or materialized view.
- [CREATE MATERIALIZED VIEW](/sql/create-materialized-view/index.md): `CREATE MATERIALIZED VIEW` defines a view that is persisted in durable storage and incrementally updated as new data arrives.
- [CREATE NETWORK POLICY (Cloud)](/sql/create-network-policy/index.md): `CREATE NETWORK POLICY` creates a network policy that restricts access to a Materialize Cloud region using IP-based rules.
- [CREATE ROLE](/sql/create-role/index.md): `CREATE ROLE` creates a new role.
- [CREATE SCHEMA](/sql/create-schema/index.md): `CREATE SCHEMA` creates a new schema.
- [CREATE SECRET](/sql/create-secret/index.md): `CREATE SECRET` securely stores credentials in Materialize's secret management system.
- [CREATE SINK](/sql/create-sink/index.md): `CREATE SINK` connects Materialize to an external data sink.
- [CREATE SOURCE](/sql/create-source/index.md): `CREATE SOURCE` connects Materialize to an external data source.
- [CREATE TABLE](/sql/create-table/index.md): `CREATE TABLE` creates a table that is persisted in durable storage.
- [CREATE TYPE](/sql/create-type/index.md): `CREATE TYPE` defines a new data type.
- [CREATE VIEW](/sql/create-view/index.md): `CREATE VIEW` defines view, which provides an alias for the embedded `SELECT` statement.
- [DEALLOCATE](/sql/deallocate/index.md): `DEALLOCATE` clears a prepared statement.
- [DECLARE](/sql/declare/index.md): `DECLARE` creates a cursor.
- [DELETE](/sql/delete/index.md): `DELETE` removes values stored in tables.
- [DISCARD](/sql/discard/index.md): Discard resets state associated with the current session.
- [DROP CLUSTER](/sql/drop-cluster/index.md): `DROP CLUSTER` removes an existing cluster from Materialize.
- [DROP CLUSTER REPLICA](/sql/drop-cluster-replica/index.md): `DROP CLUSTER REPLICA` removes an existing replica for the specified cluster.
- [DROP CONNECTION](/sql/drop-connection/index.md): `DROP CONNECTION` removes a connection from Materialize.
- [DROP DATABASE](/sql/drop-database/index.md): `DROP DATABASE` removes a database from Materialize.
- [DROP INDEX](/sql/drop-index/index.md): DROP INDEX removes an index
- [DROP MATERIALIZED VIEW](/sql/drop-materialized-view/index.md): `DROP MATERIALIZED VIEW` removes a materialized view from Materialize.
- [DROP NETWORK POLICY (Cloud)](/sql/drop-network-policy/index.md): `DROP NETWORK POLICY` removes an existing network policy from Materialize.
- [DROP OWNED](/sql/drop-owned/index.md): `DROP OWNED` drops all the objects that are owned by one of the specified roles.
- [DROP ROLE](/sql/drop-role/index.md): `DROP ROLE` removes a role from Materialize.
- [DROP SCHEMA](/sql/drop-schema/index.md): `DROP SCHEMA` removes a schema from Materialize.
- [DROP SECRET](/sql/drop-secret/index.md): `DROP SECRET` removes a secret from Materialize's secret management system.
- [DROP SINK](/sql/drop-sink/index.md): `DROP SINK` removes a sink from Materialize.
- [DROP SOURCE](/sql/drop-source/index.md): `DROP SOURCE` removes a source from Materialize.
- [DROP TABLE](/sql/drop-table/index.md): `DROP TABLE` removes a table from Materialize.
- [DROP TYPE](/sql/drop-type/index.md): `DROP TYPE` removes a user-defined data type.
- [DROP USER](/sql/drop-user/index.md): `DROP USER` removes a role from Materialize.
- [DROP VIEW](/sql/drop-view/index.md): `DROP VIEW` removes a view from Materialize.
- [EXECUTE](/sql/execute/index.md): `EXECUTE`
- [EXECUTE UNIT TEST](/sql/execute-unit-test/index.md): `EXECUTE UNIT TEST` defines a unit test for a view, run by mz-deploy against mocked input data.
- [EXPLAIN ANALYZE](/sql/explain-analyze/index.md): Reference page for `EXPLAIN ANALYZE`. `EXPLAIN ANALYZE` is used to understand the performance of indexes and materialized views.
- [EXPLAIN FILTER PUSHDOWN](/sql/explain-filter-pushdown/index.md): `EXPLAIN FILTER PUSHDOWN` reports filter pushdown statistics for `SELECT` statements and materialized views.
- [EXPLAIN PLAN](/sql/explain-plan/index.md): Reference page for `EXPLAIN PLAN`. `EXPLAIN PLAN` is used to inspect the plans of `SELECT` statements, `SUBSCRIBE` statements, indexes, and materialized views.
- [Explain plan operators](/sql/explain-plan-operators/index.md)
- [EXPLAIN SCHEMA](/sql/explain-schema/index.md): `EXPLAIN KEY SCHEMA` or `EXPLAIN VALUE SCHEMA` is used to see the generated schemas for a `CREATE SINK` statement
- [EXPLAIN TIMESTAMP](/sql/explain-timestamp/index.md): `EXPLAIN TIMESTAMP` displays the timestamps used for a `SELECT` statement.
- [FETCH](/sql/fetch/index.md): `FETCH` retrieves rows from a cursor.
- [GRANT PRIVILEGE](/sql/grant-privilege/index.md): Grant privileges on a database object.
- [GRANT ROLE](/sql/grant-role/index.md): `GRANT` grants membership of one role to another role.
- [Identifiers](/sql/identifiers/index.md): SQL identifiers are names of columns and database objects such as sources and views.
- [INSERT](/sql/insert/index.md): `INSERT` inserts values into a table.
- [PREPARE](/sql/prepare/index.md): `PREPARE` creates a prepared statement.
- [REASSIGN OWNED](/sql/reassign-owned/index.md): `REASSIGN OWNED` reassigns the owner of all the objects that are owned by one of the specified roles.
- [RESET](/sql/reset/index.md): Reset a configuration parameter to its default value.
- [REVOKE PRIVILEGE](/sql/revoke-privilege/index.md): `REVOKE` revokes privileges from a database object.
- [REVOKE ROLE](/sql/revoke-role/index.md): `REVOKE` revokes membership of one role from another role.
- [ROLLBACK](/sql/rollback/index.md)
- [SELECT](/sql/select/index.md): `SELECT` binds SQL queries to named views or materialized views, and allows to interactively query data maintained in Materialize .
- [SET](/sql/set/index.md): Modify the value of a configuration parameter in the current session.
- [SHOW](/sql/show/index.md): Display the value of a configuration parameter.
- [SHOW CLUSTER REPLICAS](/sql/show-cluster-replicas/index.md): `SHOW CLUSTER REPLICAS` lists the replicas for each cluster configured in Materialize.
- [SHOW CLUSTERS](/sql/show-clusters/index.md): `SHOW CLUSTERS` lists the clusters configured in Materialize.
- [SHOW COLUMNS](/sql/show-columns/index.md): `SHOW COLUMNS` lists the columns available for an object.
- [SHOW CONNECTIONS](/sql/show-connections/index.md): `SHOW CONNECTIONS` lists the connections configured in Materialize.
- [SHOW CREATE CLUSTER](/sql/show-create-cluster/index.md): `SHOW CREATE CLUSTER` returns the DDL statement used to create the cluster.
- [SHOW CREATE CONNECTION](/sql/show-create-connection/index.md): `SHOW CREATE CONNECTION` returns the statement used to create the connection.
- [SHOW CREATE INDEX](/sql/show-create-index/index.md): `SHOW CREATE INDEX` returns the statement used to create the index.
- [SHOW CREATE MATERIALIZED VIEW](/sql/show-create-materialized-view/index.md): `SHOW CREATE MATERIALIZED VIEW` returns the statement used to create the materialized view
- [SHOW CREATE SINK](/sql/show-create-sink/index.md): `SHOW CREATE SINK` returns the statement used to create the sink.
- [SHOW CREATE SOURCE](/sql/show-create-source/index.md): `SHOW CREATE SOURCE` returns the statement used to create the source.
- [SHOW CREATE TABLE](/sql/show-create-table/index.md): `SHOW CREATE TABLE` returns the SQL used to create the table.
- [SHOW CREATE TYPE](/sql/show-create-type/index.md): `SHOW CREATE TYPE` returns the DDL statement used to create the custom type.
- [SHOW CREATE VIEW](/sql/show-create-view/index.md): `SHOW CREATE VIEW` returns the `SELECT` statement used to create the view.
- [SHOW DATABASES](/sql/show-databases/index.md): `SHOW DATABASES` returns a list of all databases in Materialize.
- [SHOW DEFAULT PRIVILEGES](/sql/show-default-privileges/index.md): SHOW DEFAULT PRIVILEGES lists the default privileges granted on objects in Materialize.
- [SHOW INDEXES](/sql/show-indexes/index.md): SHOW INDEXES provides details about indexes built on a source, view, or materialized view
- [SHOW MATERIALIZED VIEWS](/sql/show-materialized-views/index.md): `SHOW MATERIALIZED VIEWS` returns a list of materialized views being maintained in Materialize.
- [SHOW NETWORK POLICIES (Cloud)](/sql/show-network-policies/index.md): `SHOW NETWORK POLICIES` returns a list of all network policies configured in Materialize.
- [SHOW OBJECTS](/sql/show-objects/index.md): `SHOW OBJECTS` returns a list of all objects in Materialize for a given schema.
- [SHOW PRIVILEGES](/sql/show-privileges/index.md): SHOW PRIVILEGES lists the privileges granted on all objects via role-based access control (RBAC).
- [SHOW ROLE MEMBERSHIP](/sql/show-role-membership/index.md): SHOW ROLE MEMBERSHIP lists the members of each role granted via role-based access control (RBAC).
- [SHOW ROLES](/sql/show-roles/index.md): `SHOW ROLES` lists the roles available in Materialize.
- [SHOW SCHEMAS](/sql/show-schemas/index.md): `SHOW SCHEMAS` returns a list of all schemas available in Materialize.
- [SHOW SECRETS](/sql/show-secrets/index.md): `SHOW SECRETS` lists the names of the secrets securely stored in Materialize's secret management system.
- [SHOW SINKS](/sql/show-sinks/index.md): `SHOW SINKS` returns a list of all sinks available in Materialize.
- [SHOW SOURCES](/sql/show-sources/index.md): `SHOW SOURCES` returns a list of all sources available in Materialize.
- [SHOW SUBSOURCES](/sql/show-subsources/index.md): `SHOW SUBSOURCES` returns the subsources in the current schema.
- [SHOW TABLES](/sql/show-tables/index.md): `SHOW TABLES` returns a list of all tables available in Materialize.
- [SHOW TYPES](/sql/show-types/index.md): `SHOW TYPES` returns a list of the data types in Materialize.
- [SHOW VIEWS](/sql/show-views/index.md): `SHOW VIEWS` returns a list of views in Materialize.
- [SQL data types](/sql/types/index.md): Learn more about the SQL data types supported in Materialize
- [SQL functions & operators](/sql/functions/index.md): Learn more about the SQL functions and operators supported in Materialize
- [SUBSCRIBE](/sql/subscribe/index.md): `SUBSCRIBE` streams updates from a source, table, view, or materialized view as they occur.
- [System catalog](/sql/system-catalog/index.md): The system catalog stores metadata about your Materialize instance.
- [TABLE](/sql/table/index.md): `TABLE` retrieves all rows from a single table.
- [UPDATE](/sql/update/index.md): `UPDATE` changes values stored in tables.
- [VALIDATE CONNECTION](/sql/validate-connection/index.md): `VALIDATE CONNECTION` validates the connection and authentication parameters provided in a `CREATE CONNECTION` statement against the target external system
- [VALUES](/sql/values/index.md): `VALUES` constructs a relation from value expressions.
