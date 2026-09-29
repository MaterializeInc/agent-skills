<!-- mz-docs page: security -->

# Security

## Cloud

| Guide | Description |
|-------|-------------|
| [User and service accounts](/security/cloud/users-service-accounts/) | Add user/service accounts |
| [Sync identity provider groups](/security/cloud/users-service-accounts/sync-idp-groups/) | Provision groups via SCIM and map them to database roles |
| [Access control](/security/cloud/access-control/) | Reference for role-based access management (RBAC) |
| [Manage network policies](/security/cloud/manage-network-policies/) | Set up network policies |

## Self-Managed

| Guide | Description |
|-------|-------------|
| [Authentication](/security/self-managed/authentication/) | Enable authentication |
| [Access control](/security/self-managed/access-control/) | Reference for role-based access management (RBAC) |

## Appendix

See also:

- [Appendix: Privileges](/security/appendix/appendix-privileges/)
- [Appendix: Privileges by commands](/security/appendix/appendix-command-privileges/)
- [Appendix: Built-in roles](/security/appendix/appendix-built-in-roles/)

<!-- mz-docs page: security/appendix -->

# Appendix

<!-- mz-docs page: security/appendix/appendix-built-in-roles -->

# Appendix: Built-in roles
List of predefined built-in roles in Materialize.
## `Public` role

All roles in Materialize are automatically members of
[`PUBLIC`](/security/appendix/appendix-built-in-roles/#public-role). As
such, every role includes inherited privileges from `PUBLIC`.

By default, the `PUBLIC` role has the following privileges:

**Baseline privileges via PUBLIC role:**

| Privilege | Description | On database object(s) |
| --- | --- | --- |
| <code>USAGE</code> | Permission to use or reference an object. | <ul> <li>All <code>*.public</code> schemas (e.g., <code>materialize.public</code>);</li> <li><code>materialize</code> database; and</li> <li><code>quickstart</code> cluster.</li> </ul>  |

**Default privileges on future objects set up for PUBLIC:**

| Object(s) | Object owner | Default Privilege | Granted to | Description |
| --- | --- | --- | --- | --- |
| <a href="/sql/types/" ><code>TYPE</code></a> | <code>PUBLIC</code> | <code>USAGE</code> | <code>PUBLIC</code> | When a <a href="/sql/types/" >data type</a> is created (regardless of the owner), all roles are granted the <code>USAGE</code> privilege. However, to use a data type, the role must also have <code>USAGE</code> privilege on the schema containing the type. |

Default privileges apply only to objects created after these privileges are
defined. They do not affect objects that were created before the default
privileges were set.

You can modify the privileges of your organization's `PUBLIC` role as well as
the define default privileges for `PUBLIC`.

## System catalog roles

Certain internal objects may only be queried by superusers or by users
belonging to a particular builtin role, which superusers may
[grant](/sql/grant-role). These include the following:

| Name                  | Description                                                                                                                                                                                                                                                                                                                                                                                                   |
|-----------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `mz_monitor`          | Grants access to objects that reveal actions taken by other users, in particular, SQL statements they have issued. Includes [`mz_recent_activity_log`](/sql/system-catalog/mz_internal#mz_recent_activity_log) and [`mz_notices`](/sql/system-catalog/mz_internal#mz_notices).                                                                                                                                    |
| `mz_monitor_redacted` | Grants access to objects that reveal less sensitive information about actions taken by other users, for example, SQL statements they have issued with constant values redacted. Includes `mz_recent_activity_log_redacted`, [`mz_notices_redacted`](/sql/system-catalog/mz_internal#mz_notices_redacted), and [`mz_statement_lifecycle_history`](/sql/system-catalog/mz_internal#mz_statement_lifecycle_history). |

<!-- mz-docs page: security/appendix/appendix-command-privileges -->

# Appendix: Privileges by commands

| Command | Privileges |
| --- | --- |
| <a href="/sql/alter-cluster" ><code>ALTER CLUSTER</code></a> | <ul> <li> <p>Ownership of the cluster.</p> </li> <li> <p>To rename a cluster, you must also have membership in the <code>&lt;new_owner_role&gt;</code>.</p> </li> <li> <p>To swap names with another cluster, you must also have ownership of the other cluster.</p> </li> </ul>  |
| <a href="/sql/alter-cluster-replica" ><code>ALTER CLUSTER REPLICA</code></a> | <ul> <li>Ownership of the cluster replica.</li> <li>In addition, to change owners: <ul> <li>Role membership in <code>new_owner</code>.</li> <li><code>CREATE</code> privileges on the containing cluster.</li> </ul> </li> </ul>  |
| <a href="/sql/alter-connection" ><code>ALTER CONNECTION</code></a> | <ul> <li>Ownership of the connection.</li> <li>In addition, to set, reset, or drop connection options: <ul> <li><code>USAGE</code> privileges on all connections and secrets referenced by the resulting connection definition.</li> <li><code>USAGE</code> privileges on the schemas that contain those connections and secrets.</li> </ul> </li> <li>In addition, to change owners: <ul> <li>Role membership in <code>new_owner</code>.</li> <li><code>CREATE</code> privileges on the containing schema if the connection is namespaced by a schema.</li> </ul> </li> </ul>  |
| <a href="/sql/alter-database" ><code>ALTER DATABASE</code></a> | <ul> <li>Ownership of the database.</li> <li>In addition, to change owners: <ul> <li>Role membership in <code>new_owner</code>.</li> </ul> </li> </ul>  |
| <a href="/sql/alter-default-privileges" ><code>ALTER DEFAULT PRIVILEGES</code></a> | <ul> <li>Role membership in <code>role_name</code>.</li> <li><code>USAGE</code> privileges on the containing database if <code>database_name</code> is specified.</li> <li><code>USAGE</code> privileges on the containing schema if <code>schema_name</code> is specified.</li> <li><em>superuser</em> status if the <em>target_role</em> is <code>PUBLIC</code> or <strong>ALL ROLES</strong> is specified.</li> </ul>  |
| <a href="/sql/alter-index" ><code>ALTER INDEX</code></a> | <ul> <li>Ownership of the index.</li> </ul>  |
| <a href="/sql/alter-materialized-view" ><code>ALTER MATERIALIZED VIEW</code></a> | <ul> <li>Ownership of the materialized view.</li> <li>In addition, to change owners: <ul> <li>Role membership in <code>new_owner</code>.</li> <li><code>CREATE</code> privileges on the containing schema if the materialized view is namespaced by a schema.</li> </ul> </li> <li>In addition, to apply a replacement: <ul> <li>Ownership of the replacement materialized view.</li> </ul> </li> </ul>  |
| <a href="/sql/alter-network-policy" ><code>ALTER NETWORK POLICY</code></a> | <ul> <li>Ownership of the network policy.</li> </ul>  |
| <a href="/sql/alter-role" ><code>ALTER ROLE</code></a> | <ul> <li><code>CREATEROLE</code> privileges on the system.</li> </ul>  |
| <a href="/sql/alter-schema" ><code>ALTER SCHEMA</code></a> | <ul> <li>Ownership of the schema.</li> <li>In addition, <ul> <li>To swap with another schema: <ul> <li>Ownership of the other schema</li> </ul> </li> <li>To change owners: <ul> <li>Role membership in <code>new_owner</code>.</li> <li><code>CREATE</code> privileges on the containing database.</li> </ul> </li> </ul> </li> </ul>  |
| <a href="/sql/alter-secret" ><code>ALTER SECRET</code></a> | <ul> <li>Ownership of the secret being altered.</li> <li>In addition, to change owners: <ul> <li>Role membership in <code>new_owner</code>.</li> <li><code>CREATE</code> privileges on the containing schema if the secret is namespaced by a schema.</li> </ul> </li> </ul>  |
| <a href="/sql/alter-sink" ><code>ALTER SINK</code></a> | <ul> <li>Ownership of the sink being altered.</li> <li>In addition, <ul> <li>To change the sink from relation: <ul> <li><code>SELECT</code> privileges on the new relation being written out to an external system.</li> <li><code>CREATE</code> privileges on the cluster maintaining the sink.</li> <li><code>USAGE</code> privileges on all connections and secrets used in the sink definition.</li> <li><code>USAGE</code> privileges on the schemas that all connections and secrets in the statement are contained in.</li> </ul> </li> <li>To change owners: <ul> <li>Role membership in <code>new_owner</code>.</li> <li><code>CREATE</code> privileges on the containing schema if the sink is namespaced by a schema.</li> </ul> </li> </ul> </li> </ul>  |
| <a href="/sql/alter-source" ><code>ALTER SOURCE</code></a> | <ul> <li>Ownership of the source being altered.</li> <li>In addition, to change owners: <ul> <li>Role membership in <code>new_owner</code>.</li> <li><code>CREATE</code> privileges on the containing schema if the source is namespaced by a schema.</li> </ul> </li> </ul>  |
| <a href="/sql/alter-system-reset" ><code>ALTER SYSTEM RESET</code></a> | <ul> <li><a href="/security/cloud/users-service-accounts/#organization-roles" ><em>Superuser</em> privileges</a></li> </ul>  |
| <a href="/sql/alter-system-set" ><code>ALTER SYSTEM SET</code></a> | <ul> <li><a href="/security/cloud/users-service-accounts/#organization-roles" ><em>Superuser</em> privileges</a></li> </ul>  |
| <a href="/sql/alter-table" ><code>ALTER TABLE</code></a> | <ul> <li>Ownership of the table being altered.</li> <li>In addition, to change owners: <ul> <li>Role membership in <code>new_owner</code>.</li> <li><code>CREATE</code> privileges on the containing schema if the table is namespaced by a schema.</li> </ul> </li> </ul>  |
| <a href="/sql/alter-type" ><code>ALTER TYPE</code></a> | <ul> <li>Ownership of the type being altered.</li> <li>In addition, to change owners: <ul> <li>Role membership in <code>new_owner</code>.</li> <li><code>CREATE</code> privileges on the containing schema if the type is namespaced by a schema.</li> </ul> </li> </ul>  |
| <a href="/sql/alter-view" ><code>ALTER VIEW</code></a> | <ul> <li>Ownership of the view being altered.</li> <li>In addition, to change owners: <ul> <li>Role membership in <code>new_owner</code>.</li> <li><code>CREATE</code> privileges on the containing schema if the view is namespaced by a schema.</li> </ul> </li> </ul>  |
| <a href="/sql/comment-on" ><code>COMMENT ON</code></a> | <ul> <li>Ownership of the object being commented on (unless the object is a role).</li> <li>To comment on a role, you must have the <code>CREATEROLE</code> privilege.</li> </ul>  |
| <a href="/sql/copy-from" ><code>COPY FROM</code></a> | <ul> <li><code>USAGE</code> privileges on the schema containing the table.</li> <li><code>INSERT</code> privileges on the table.</li> </ul>  |
| <a href="/sql/copy-to" ><code>COPY TO</code></a> | <ul> <li><code>USAGE</code> privileges on the schemas that all relations and types in the query are contained in.</li> <li><code>SELECT</code> privileges on all relations in the query. <ul> <li>NOTE: if any item is a view, then the view owner must also have the necessary privileges to execute the view definition. Even if the view owner is a <em>superuser</em>, they still must explicitly be granted the necessary privileges.</li> </ul> </li> <li><code>USAGE</code> privileges on all types used in the query.</li> <li><code>USAGE</code> privileges on the active cluster.</li> </ul>  |
| <a href="/sql/create-cluster" ><code>CREATE CLUSTER</code></a> | <ul> <li><code>CREATECLUSTER</code> privileges on the system.</li> </ul>  |
| <a href="/sql/create-cluster-replica" ><code>CREATE CLUSTER REPLICA</code></a> | <ul> <li>Ownership of the cluster.</li> </ul>  |
| <a href="/sql/create-connection" ><code>CREATE CONNECTION</code></a> | <ul> <li><code>CREATE</code> privileges on the containing schema.</li> <li><code>USAGE</code> privileges on all connections and secrets used in the connection definition.</li> <li><code>USAGE</code> privileges on the schemas that all connections and secrets in the statement are contained in.</li> </ul>  |
| <a href="/sql/create-database" ><code>CREATE DATABASE</code></a> | <ul> <li><code>CREATEDB</code> privileges on the system.</li> </ul>  |
| <a href="/sql/create-index" ><code>CREATE INDEX</code></a> | <ul> <li>Ownership of the object on which to create the index.</li> <li><code>CREATE</code> privileges on the containing schema.</li> <li><code>CREATE</code> privileges on the containing cluster.</li> <li><code>USAGE</code> privileges on all types used in the index definition.</li> <li><code>USAGE</code> privileges on the schemas that all types in the statement are contained in.</li> </ul>  |
| <a href="/sql/create-materialized-view" ><code>CREATE MATERIALIZED VIEW</code></a> | <ul> <li><code>CREATE</code> privileges on the containing schema.</li> <li><code>CREATE</code> privileges on the containing cluster.</li> <li><code>USAGE</code> privileges on all types used in the materialized view definition.</li> <li><code>USAGE</code> privileges on the schemas for the types used in the statement.</li> </ul>  |
| <a href="/sql/create-network-policy/" ><code>CREATE NETWORK POLICY</code></a> | <ul> <li><code>CREATENETWORKPOLICY</code> privileges on the system.</li> </ul>  |
| <a href="/sql/create-role" ><code>CREATE ROLE</code></a> | <ul> <li><code>CREATEROLE</code> privileges on the system.</li> </ul>  |
| <a href="/sql/create-schema" ><code>CREATE SCHEMA</code></a> | <ul> <li><code>CREATE</code> privileges on the containing database.</li> </ul>  |
| <a href="/sql/create-secret" ><code>CREATE SECRET</code></a> | <ul> <li><code>CREATE</code> privileges on the containing schema.</li> </ul>  |
| <a href="/sql/create-sink" ><code>CREATE SINK</code></a> | <ul> <li><code>CREATE</code> privileges on the containing schema.</li> <li><code>SELECT</code> privileges on the item being written out to an external system. <ul> <li>NOTE: if the item is a materialized view, then the view owner must also have the necessary privileges to execute the view definition.</li> </ul> </li> <li><code>CREATE</code> privileges on the containing cluster if the sink is created in an existing cluster.</li> <li><code>CREATECLUSTER</code> privileges on the system if the sink is not created in an existing cluster.</li> <li><code>USAGE</code> privileges on all connections and secrets used in the sink definition.</li> <li><code>USAGE</code> privileges on the schemas that all connections and secrets in the statement are contained in.</li> </ul>  |
| <a href="/sql/create-source" ><code>CREATE SOURCE</code></a> | <ul> <li><code>CREATE</code> privileges on the containing schema.</li> <li><code>CREATE</code> privileges on the containing cluster if the source is created in an existing cluster.</li> <li><code>CREATECLUSTER</code> privileges on the system if the source is not created in an existing cluster.</li> <li><code>USAGE</code> privileges on all connections and secrets used in the source definition.</li> <li><code>USAGE</code> privileges on the schemas that all connections and secrets in the statement are contained in.</li> </ul>  |
| <a href="/sql/create-table" ><code>CREATE TABLE</code></a> | <ul> <li><code>CREATE</code> privileges on the containing schema.</li> <li><code>USAGE</code> privileges on all types used in the table definition.</li> <li><code>USAGE</code> privileges on the schemas that all types in the statement are contained in.</li> <li>For <code>CREATE TABLE ... FROM SOURCE</code>, <code>SELECT</code> privileges on the source and <code>USAGE</code> privileges on its schema. <code>SELECT</code> on a source permits attaching any reference that source ingests, so grant it only to roles that should be able to read all of the source&rsquo;s data.</li> </ul>  |
| <a href="/sql/create-type" ><code>CREATE TYPE</code></a> | <ul> <li><code>CREATE</code> privileges on the containing schema.</li> <li><code>USAGE</code> privileges on all types used in the type definition.</li> <li><code>USAGE</code> privileges on the schemas that all types in the statement are contained in.</li> </ul>  |
| <a href="/sql/create-view" ><code>CREATE VIEW</code></a> | <ul> <li><code>CREATE</code> privileges on the containing schema.</li> <li><code>USAGE</code> privileges on all types used in the view definition.</li> <li><code>USAGE</code> privileges on the schemas for the types in the statement.</li> <li>Ownership of the existing view if replacing an existing view with the same name (i.e., <code>OR REPLACE</code> is specified in <code>CREATE VIEW</code> command).</li> </ul>  |
| <a href="/sql/delete" ><code>DELETE</code></a> | <ul> <li><code>USAGE</code> privileges on the schemas that all relations and types in the query are contained in.</li> <li><code>DELETE</code> privileges on <code>table_name</code>.</li> <li><code>SELECT</code> privileges on all relations in the query. <ul> <li>NOTE: if any item is a view, then the view owner must also have the necessary privileges to execute the view definition. Even if the view owner is a <em>superuser</em>, they still must explicitly be granted the necessary privileges.</li> </ul> </li> <li><code>USAGE</code> privileges on all types used in the query.</li> <li><code>USAGE</code> privileges on the active cluster.</li> </ul>  |
| <a href="/sql/drop-cluster-replica" ><code>DROP CLUSTER REPLICA</code></a> | <ul> <li>Ownership of the dropped cluster replica.</li> <li><code>USAGE</code> privileges on the containing cluster.</li> </ul>  |
| <a href="/sql/drop-cluster" ><code>DROP CLUSTER</code></a> | <ul> <li>Ownership of the dropped cluster.</li> </ul>  |
| <a href="/sql/drop-connection" ><code>DROP CONNECTION</code></a> | <ul> <li>Ownership of the dropped connection.</li> <li><code>USAGE</code> privileges on the containing schema.</li> </ul>  |
| <a href="/sql/drop-database" ><code>DROP DATABASE</code></a> | <ul> <li>Ownership of the dropped database.</li> </ul>  |
| <a href="/sql/drop-index" ><code>DROP INDEX</code></a> | <ul> <li>Ownership of the dropped index.</li> <li><code>USAGE</code> privileges on the containing schema.</li> </ul>  |
| <a href="/sql/drop-materialized-view" ><code>DROP MATERIALIZED VIEW</code></a> | <ul> <li>Ownership of the dropped materialized view.</li> <li><code>USAGE</code> privileges on the containing schema.</li> </ul>  |
| <a href="/sql/drop-network-policy" ><code>DROP NETWORK POLICY</code></a> | <ul> <li><code>CREATENETWORKPOLICY</code> privileges on the system.</li> </ul>  |
| <a href="/sql/drop-owned" ><code>DROP OWNED</code></a> | <ul> <li>Role membership in <code>role_name</code>.</li> </ul>  |
| <a href="/sql/drop-role" ><code>DROP ROLE</code></a> | <ul> <li><code>CREATEROLE</code> privileges on the system.</li> </ul>  |
| <a href="/sql/drop-schema" ><code>DROP SCHEMA</code></a> | <ul> <li>Ownership of the dropped schema.</li> <li><code>USAGE</code> privileges on the containing database.</li> </ul>  |
| <a href="/sql/drop-secret" ><code>DROP SECRET</code></a> | <ul> <li>Ownership of the dropped secret.</li> <li><code>USAGE</code> privileges on the containing schema.</li> </ul>  |
| <a href="/sql/drop-sink" ><code>DROP SINK</code></a> | <ul> <li>Ownership of the dropped sink.</li> <li><code>USAGE</code> privileges on the containing schema.</li> </ul>  |
| <a href="/sql/drop-source" ><code>DROP SOURCE</code></a> | <ul> <li>Ownership of the dropped source.</li> <li><code>USAGE</code> privileges on the containing schema.</li> </ul>  |
| <a href="/sql/drop-table" ><code>DROP TABLE</code></a> | <ul> <li>Ownership of the dropped table.</li> <li><code>USAGE</code> privileges on the containing schema.</li> </ul>  |
| <a href="/sql/drop-type" ><code>DROP TYPE</code></a> | <ul> <li>Ownership of the dropped type.</li> <li><code>USAGE</code> privileges on the containing schema.</li> </ul>  |
| <a href="/sql/drop-user" ><code>DROP USER</code></a> | <ul> <li><code>CREATEROLE</code> privileges on the system.</li> </ul>  |
| <a href="/sql/drop-view" ><code>DROP VIEW</code></a> | <ul> <li>Ownership of the dropped view.</li> <li><code>USAGE</code> privileges on the containing schema.</li> </ul>  |
| <a href="/sql/explain-analyze" ><code>EXPLAIN ANALYZE</code></a> | <ul> <li><code>USAGE</code> privileges on the schemas that all relations in the explainee are contained in.</li> </ul>  |
| <a href="/sql/explain-filter-pushdown" ><code>EXPLAIN FILTER PUSHDOWN</code></a> | <ul> <li><code>USAGE</code> privileges on the schemas that all relations in the explainee are contained in.</li> </ul>  |
| <a href="/sql/explain-plan" ><code>EXPLAIN PLAN</code></a> | <ul> <li><code>USAGE</code> privileges on the schemas that all relations in the explainee are contained in.</li> </ul>  |
| <a href="/sql/explain-schema" ><code>EXPLAIN SCHEMA</code></a> | <ul> <li><code>USAGE</code> privileges on the schemas that all items in the query are contained in.</li> </ul>  |
| <a href="/sql/explain-timestamp" ><code>EXPLAIN TIMESTAMP</code></a> | <ul> <li><code>USAGE</code> privileges on the schemas that all relations in the query are contained in.</li> </ul>  |
| <a href="/sql/grant-privilege" ><code>GRANT PRIVILEGE</code></a> | <ul> <li>Ownership of affected objects.</li> <li><code>USAGE</code> privileges on the containing database if the affected object is a schema.</li> <li><code>USAGE</code> privileges on the containing schema if the affected object is namespaced by a schema.</li> <li><em>superuser</em> status if the privilege is a system privilege.</li> </ul>  |
| <a href="/sql/grant-role" ><code>GRANT ROLE</code></a> | <ul> <li><code>CREATEROLE</code> privileges on the system.</li> </ul>  |
| <a href="/sql/insert" ><code>INSERT</code></a> | <ul> <li><code>USAGE</code> privileges on the schemas that all relations and types in the query are contained in.</li> <li><code>INSERT</code> privileges on <code>table_name</code>.</li> <li><code>SELECT</code> privileges on all relations in the query. <ul> <li>NOTE: if any item is a view, then the view owner must also have the necessary privileges to execute the view definition. Even if the view owner is a <em>superuser</em>, they still must explicitly be granted the necessary privileges.</li> </ul> </li> <li><code>USAGE</code> privileges on all types used in the query.</li> <li><code>USAGE</code> privileges on the active cluster.</li> </ul>  |
| <a href="/sql/reassign-owned" ><code>REASSIGN OWNED</code></a> | <ul> <li>Role membership in <code>old_role</code> and <code>new_role</code>.</li> </ul>  |
| <a href="/sql/revoke-privilege" ><code>REVOKE PRIVILEGE</code></a> | <ul> <li>Ownership of affected objects.</li> <li><code>USAGE</code> privileges on the containing database if the affected object is a schema.</li> <li><code>USAGE</code> privileges on the containing schema if the affected object is namespaced by a schema.</li> <li><em>superuser</em> status if the privilege is a system privilege.</li> </ul>  |
| <a href="/sql/revoke-role" ><code>REVOKE ROLE</code></a> | <ul> <li><code>CREATEROLE</code> privileges on the systems.</li> </ul>  |
| <a href="/sql/select" ><code>SELECT</code></a> | <ul> <li> <p><code>SELECT</code> privileges on all <strong>directly</strong> referenced relations in the query. If the directly referenced relation is a view or materialized view:</p> <ul> <li> <p><code>SELECT</code> privileges are required only on the directly referenced view/materialized view. <code>SELECT</code> privileges are <strong>not</strong> required for the underlying relations referenced in the view/materialized view definition unless those relations themselves are directly referenced in the query.</p> </li> <li> <p>However, the owner of the view/materialized view (including those with <strong>superuser</strong> privileges) must have all required <code>SELECT</code> and <code>USAGE</code> privileges to run the view definition regardless of who is selecting from the view/materialized view.</p> </li> </ul> </li> <li> <p><code>USAGE</code> privileges on the schemas that contain the relations in the query.</p> </li> <li> <p><code>USAGE</code> privileges on the active cluster.</p> </li> </ul>  |
| <a href="/sql/show-columns" ><code>SHOW COLUMNS</code></a> | <ul> <li><code>USAGE</code> privileges on the schema containing <code>item_ref</code>.</li> </ul>  |
| <a href="/sql/show-create-cluster" ><code>SHOW CREATE CLUSTER</code></a> | There are no privileges required to execute this statement. |
| <a href="/sql/show-create-connection" ><code>SHOW CREATE CONNECTION</code></a> | <ul> <li><code>USAGE</code> privileges on the schema containing the connection.</li> </ul>  |
| <a href="/sql/show-create-index" ><code>SHOW CREATE INDEX</code></a> | <ul> <li><code>USAGE</code> privileges on the schema containing the index.</li> </ul>  |
| <a href="/sql/show-create-materialized-view" ><code>SHOW CREATE MATERIALIZED VIEW</code></a> | <ul> <li><code>USAGE</code> privileges on the schema containing the materialized view.</li> </ul>  |
| <a href="/sql/show-create-type" ><code>SHOW CREATE TYPE</code></a> | <ul> <li><code>USAGE</code> privileges on the schema containing the type.</li> </ul>  |
| <a href="/sql/show-create-sink" ><code>SHOW CREATE SINK</code></a> | <ul> <li><code>USAGE</code> privileges on the schema containing the sink.</li> </ul>  |
| <a href="/sql/show-create-source" ><code>SHOW CREATE SOURCE</code></a> | <ul> <li><code>USAGE</code> privileges on the schema containing the source.</li> </ul>  |
| <a href="/sql/show-create-table" ><code>SHOW CREATE TABLE</code></a> | <ul> <li><code>USAGE</code> privileges on the schema containing the table.</li> </ul>  |
| <a href="/sql/show-create-view" ><code>SHOW CREATE VIEW</code></a> | <ul> <li><code>USAGE</code> privileges on the schema containing the view.</li> </ul>  |
| <a href="/sql/subscribe" ><code>SUBSCRIBE</code></a> | <ul> <li><code>USAGE</code> privileges on the schemas that all relations and types in the query are contained in.</li> <li><code>SELECT</code> privileges on all relations in the query. <ul> <li>NOTE: if any item is a view, then the view owner must also have the necessary privileges to execute the view definition. Even if the view owner is a <em>superuser</em>, they still must explicitly be granted the necessary privileges.</li> </ul> </li> <li><code>USAGE</code> privileges on all types used in the query.</li> <li><code>USAGE</code> privileges on the active cluster.</li> </ul>  |
| <a href="/sql/update" ><code>UPDATE</code></a> | <ul> <li><code>USAGE</code> privileges on the schemas that all relations and types in the query are contained in.</li> <li><code>UPDATE</code> privileges on the table being updated.</li> <li><code>SELECT</code> privileges on all relations in the query. <ul> <li>NOTE: if any item is a view, then the view owner must also have the necessary privileges to execute the view definition. Even if the view owner is a <em>superuser</em>, they still must explicitly be granted the necessary privileges.</li> </ul> </li> <li><code>USAGE</code> privileges on all types used in the query.</li> <li><code>USAGE</code> privileges on the active cluster.</li> </ul>  |
| <a href="/sql/validate-connection" ><code>VALIDATE CONNECTION</code></a> | <ul> <li><code>USAGE</code> privileges on the containing schema.</li> <li><code>USAGE</code> privileges on the connection.</li> </ul>  |


<!-- mz-docs page: security/appendix/appendix-privileges -->

# Appendix: Privileges
List of available  privileges in Materialize.
> **Note:** Various SQL operations require additional privileges on related objects, such
> as:
> - For objects that use compute resources (e.g., indexes, materialized views,
>   replicas, sources, sinks), access is also required for the associated cluster.
> - For objects in a schema, access is also required for the schema.
> For details on SQL operations and needed privileges, see [Appendix: Privileges
> by command](/security/appendix/appendix-command-privileges/).

The following privileges are available in Materialize:

**By Privilege:**

| Privilege | Description | Abbreviation | Applies to |
| --- | --- | --- | --- |
| <strong>SELECT</strong> | Permission to read rows from an object. | <code>r</code> | <ul> <li><code>MATERIALIZED VIEW</code></li> <li><code>SOURCE</code></li> <li><code>TABLE</code></li> <li><code>VIEW</code></li> </ul>  |
| <strong>INSERT</strong> | Permission to insert rows into an object. | <code>a</code> | <ul> <li><code>TABLE</code></li> </ul>  |
| <strong>UPDATE</strong> | <p>Permission to modify rows in an object.</p> <p>Modifying rows may also require <strong>SELECT</strong> if a read is needed to determine which rows to update.</p>  | <code>w</code> | <ul> <li><code>TABLE</code></li> </ul>  |
| <strong>DELETE</strong> | <p>Permission to delete rows from an object.</p> <p>Deleting rows may also require <strong>SELECT</strong> if a read is needed to determine which rows to delete.</p>  | <code>d</code> | <ul> <li><code>TABLE</code></li> </ul>  |
| <strong>CREATE</strong> | Permission to create a new objects within the specified object. | <code>C</code> | <ul> <li><code>DATABASE</code></li> <li><code>SCHEMA</code></li> <li><code>CLUSTER</code></li> </ul>  |
| <strong>USAGE</strong> | <a name="privilege-usage"></a> Permission to use or reference an object (e.g., schema/type lookup). | <code>U</code> | <ul> <li><code>CLUSTER</code></li> <li><code>CONNECTION</code></li> <li><code>DATABASE</code></li> <li><code>SCHEMA</code></li> <li><code>SECRET</code></li> <li><code>TYPE</code></li> </ul>  |
| <strong>CREATEROLE</strong> | <p>Permission to create/modify/delete roles and manage role memberships for any role in the system.</p> > **Warning:** Roles with the `CREATEROLE` privilege can obtain the privileges of any other > role in the system by granting themselves that role. Avoid granting > `CREATEROLE` unnecessarily. | <code>R</code> | <ul> <li><code>SYSTEM</code></li> </ul>  |
| <strong>CREATEDB</strong> | Permission to create new databases. | <code>B</code> | <ul> <li><code>SYSTEM</code></li> </ul>  |
| <strong>CREATECLUSTER</strong> | Permission to create new clusters. | <code>N</code> | <ul> <li><code>SYSTEM</code></li> </ul>  |
| <strong>CREATENETWORKPOLICY</strong> | Permission to create network policies to control access at the network layer. | <code>P</code> | <ul> <li><code>SYSTEM</code></li> </ul>  |

**By Object:**

| Object | Privileges |
| --- | --- |
| <code>CLUSTER</code> | <ul> <li><code>USAGE</code></li> <li><code>CREATE</code></li> </ul>  |
| <code>CONNECTION</code> | <ul> <li><code>USAGE</code></li> </ul>  |
| <code>DATABASE</code> | <ul> <li><code>USAGE</code></li> <li><code>CREATE</code></li> </ul>  |
| <code>MATERIALIZED VIEW</code> | <ul> <li><code>SELECT</code></li> </ul>  |
| <code>SCHEMA</code> | <ul> <li><code>USAGE</code></li> <li><code>CREATE</code></li> </ul>  |
| <code>SECRET</code> | <ul> <li><code>USAGE</code></li> </ul>  |
| <code>SOURCE</code> | <ul> <li><code>SELECT</code></li> </ul>  |
| <code>SYSTEM</code> | <ul> <li><code>CREATEROLE</code></li> <li><code>CREATEDB</code></li> <li><code>CREATECLUSTER</code></li> <li><code>CREATENETWORKPOLICY</code></li> </ul>  |
| <code>TABLE</code> | <ul> <li><code>INSERT</code></li> <li><code>SELECT</code></li> <li><code>UPDATE</code></li> <li><code>DELETE</code></li> </ul>  |
| <code>TYPE</code> | <ul> <li><code>USAGE</code></li> </ul>  |
| <code>VIEW</code> | <ul> <li><code>SELECT</code></li> </ul>  |


<!-- mz-docs page: security/cloud -->

# Cloud

Security for Materialize Cloud

This section covers security for Materialize Cloud.

| Guide | Description |
|-------|-------------|
| [User and service accounts](/security/cloud/users-service-accounts/) | Add user/service accounts |
| [Access control](/security/cloud/access-control/) | Reference for role-based access management (RBAC) |
| [Manage network policies](/security/cloud/manage-network-policies/) | Set up network policies |

See also:

- [Appendix: Privileges](/security/appendix/appendix-privileges/)
- [Appendix: Privileges by commands](/security/appendix/appendix-command-privileges/)
- [Appendix: Built-in roles](/security/appendix/appendix-built-in-roles/)

<!-- mz-docs page: security/cloud/access-control -->

# Access control (Role-based)

How to configure and manage role-based database access control (RBAC) in Materialize.

> **Disambiguation:** Materialize uses roles to manage access control at two levels: - [Organization roles](/security/cloud/users-service-accounts/#organization-roles), which determines the access to the Console's administrative features and sets the **initial database roles** for the user/service account. - [Database roles](/security/cloud/access-control/#role-based-access-control-rbac), which controls access to database objects and operations within Materialize. This section focuses on the database access control. For information on organization roles, see [Users and service accounts](../users-service-accounts/). 

## Role-based access control (RBAC)

In Materialize, role-based access control (RBAC) governs access to **database
objects** through privileges granted to [database
roles](./manage-roles/).

> **Tip:** You can manage database role membership from your identity provider by
> [syncing IdP groups to database
> roles](/security/cloud/users-service-accounts/sync-idp-groups/).

## Roles and privileges

In Materialize, a database role is created:
- Automatically when a user/service account is created:
  - When a [user account is
  created](/security/cloud/users-service-accounts/invite-users/), an associated
  database role with the user email as its name is created.
  - When a [service account is
  created](/security/cloud/users-service-accounts/create-service-accounts/), an
  associated database role with the service account user as its name is created.
- Manually to create a role independent of any specific account,
  usually to define a set of shared privileges that can be granted to other
  user/service/standalone roles.

### Managing privileges

Once a role is created, you can:

- [Manage its current
  privileges](/security/cloud/access-control/manage-roles/#manage-current-privileges-for-a-role)
  (i.e., privileges on existing objects):
  - By granting privileges for a role or revoking privileges from a role.
  - By granting other roles to the role or revoking roles from the role.
    *Recommended for user account/service account roles.*
- [Manage its future
  privileges](/security/cloud/access-control/manage-roles/#manage-future-privileges-for-a-role)
  (i.e., privileges on objects created in the future):
  - By defining default privileges for objects. With default privileges in
   place, a role is automatically granted/revoked privileges as new objects are
   created by **others** (When an object is created, the creator is granted all
   [applicable privileges](/security/appendix/appendix-privileges/) for that
   object automatically).

> **Disambiguation:** - Use `GRANT|REVOKE ...` to modify privileges on **existing** objects. - Use `ALTER DEFAULT PRIVILEGES` to ensure that privileges are automatically granted or revoked when **new objects** of a certain type are created by others. Then, as needed, you can use `GRANT|REVOKE <privilege>` to adjust those privileges. 

### Initial privileges

All roles in Materialize are automatically members of
[`PUBLIC`](/security/appendix/appendix-built-in-roles/#public-role). As
such, every role includes inherited privileges from `PUBLIC`.

By default, the `PUBLIC` role has the following privileges:

**Baseline privileges via PUBLIC role:**

| Privilege | Description | On database object(s) |
| --- | --- | --- |
| <code>USAGE</code> | Permission to use or reference an object. | <ul> <li>All <code>*.public</code> schemas (e.g., <code>materialize.public</code>);</li> <li><code>materialize</code> database; and</li> <li><code>quickstart</code> cluster.</li> </ul>  |

**Default privileges on future objects set up for PUBLIC:**

| Object(s) | Object owner | Default Privilege | Granted to | Description |
| --- | --- | --- | --- | --- |
| <a href="/sql/types/" ><code>TYPE</code></a> | <code>PUBLIC</code> | <code>USAGE</code> | <code>PUBLIC</code> | When a <a href="/sql/types/" >data type</a> is created (regardless of the owner), all roles are granted the <code>USAGE</code> privilege. However, to use a data type, the role must also have <code>USAGE</code> privilege on the schema containing the type. |

Default privileges apply only to objects created after these privileges are
defined. They do not affect objects that were created before the default
privileges were set.

In addition, all roles have:
- `USAGE` on all built-in types and [all system catalog
schemas](/sql/system-catalog/).
- `SELECT` on [system catalog objects](/sql/system-catalog/).
- All [applicable privileges](/security/appendix/appendix-privileges/) for
  an object they create; for example, the creator of a schema gets `CREATE` and
  `USAGE`; the creator of a table gets `SELECT`, `INSERT`, `UPDATE`, and
  `DELETE`.

You can modify the privileges of your organization's `PUBLIC` role as well as
the modify default privileges for `PUBLIC`.

## Privilege inheritance and modular access control

In Materialize, when you grant a role to another role (user role/service account
role/independent role), the target role inherits privileges through the granted
role.

In general, to grant a user or service account privileges, create roles with the
desired privileges and grant these roles to the database role associated with
the user/service account email/name. Although you can grant privileges directly
to the associated roles, using separate, reusable roles is recommended for
better access management.

With privilege inheritance, you can compose more complex roles by
combining existing roles, enabling modular access control. However:

- Inheritance only applies to role privileges; role attributes and parameters
  are not inherited.
- When you revoke a role from another role (user role/service account
role/independent role), the target role is no longer a member of the revoked
role nor inherits the revoked role's privileges. **However**, privileges are
cumulative: if the target role inherits the same privilege(s) from another role,
the target role still has the privilege(s) through the other role.

## Best practices

### Follow the principle of least privilege

Role-based access control in Materialize should follow the principle of
least privilege. Grant only the minimum access necessary for users and
service accounts to perform their duties.

### Restrict the assignment of **Organization Admin** role

{{% include-headless "/headless/rbac-cloud/org-admin-recommendation" %}}

### Restrict the granting of `CREATEROLE` privilege

{{% include-headless "/headless/rbac-cloud/createrole-consideration" %}}

### Use Reusable Roles for Privilege Assignment

{{% include-headless "/headless/rbac-cloud/use-resusable-roles" %}}

See also [Manage database roles](/security/access-control/manage-roles/).

### Audit for unused roles and privileges.

{{% include-headless "/headless/rbac-cloud/audit-remove-roles" %}}

See also [Show roles in
system](/security/cloud/access-control/manage-roles/#show-roles-in-system) and [Drop
a role](/security/cloud/access-control/manage-roles/#drop-a-role) for more
information.

<!-- mz-docs page: security/cloud/access-control/manage-roles -->

# Manage database roles
Create and manage database roles and privileges in Materialize
In Materialize, role-based access control (RBAC) governs access to **database
objects** through privileges granted to database roles.

> **Disambiguation:** Materialize uses roles to manage access control at two levels: - [Organization roles](/security/cloud/users-service-accounts/#organization-roles), which determines the access to the Console's administrative features and sets the **initial database roles** for the user/service account. - [Database roles](/security/cloud/access-control/#role-based-access-control-rbac), which controls access to database objects and operations within Materialize. The focus of this page is on managing database roles. For information on organization roles, see [Users and service accounts](/security/cloud/users-service-accounts/). 

> **Tip:** Instead of granting role membership by hand, you can [sync groups from your
> identity provider](/security/cloud/users-service-accounts/sync-idp-groups/) to
> manage database role membership from your IdP.

## Required privileges for managing roles

> **Note:** With their **superuser** privileges, [**Organization
> admins**](/security/cloud/users-service-accounts/#organization-roles) can manage
> roles (including overriding ownership requirements when granting privileges on
> various objects).

| Role management operations | Required privileges |
| --- | --- |
| To create/revoke/grant roles | <ul> <li><code>CREATEROLE</code> privileges on the system. > **Warning:** Roles with the `CREATEROLE` privilege can obtain the privileges of any other > role in the system by granting themselves that role. Avoid granting > `CREATEROLE` unnecessarily. </li> </ul>  |
| To view privileges for a role | None |
| To grant/revoke role privileges | <ul> <li>Ownership of affected objects.</li> <li><code>USAGE</code> privileges on the containing database if the affected object is a schema.</li> <li><code>USAGE</code> privileges on the containing schema if the affected object is namespaced by a schema.</li> <li><em>superuser</em> status if the privilege is a system privilege.</li> </ul>  |
| To alter default privileges | <ul> <li>Role membership in <code>role_name</code>.</li> <li><code>USAGE</code> privileges on the containing database if <code>database_name</code> is specified.</li> <li><code>USAGE</code> privileges on the containing schema if <code>schema_name</code> is specified.</li> <li><em>superuser</em> status if the <em>target_role</em> is <code>PUBLIC</code> or <strong>ALL ROLES</strong> is specified.</li> </ul>  |

See also [Appendix: Privileges by
command](/security/appendix/appendix-command-privileges/)

## Create a role

In Materialize, a database role is created:
- Automatically when a user/service account is created:
  - When a [user account is
  created](/security/cloud/users-service-accounts/invite-users/), an associated
  database role with the user email as its name is created.
  - When a [service account is
  created](/security/cloud/users-service-accounts/create-service-accounts/), an
  associated database role with the service account user as its name is created.
- Manually to create a role independent of any specific account,
  usually to define a set of shared privileges that can be granted to other
  user/service/standalone roles.

To create a new role manually, use the [`CREATE ROLE`](/sql/create-role/)
statement.

> **Privilege(s) required to run the command:** - `CREATEROLE` privileges on the system. 

```mzsql
CREATE ROLE <role_name> [WITH INHERIT];
-- WITH INHERIT behavior is implied and does not need to be specified.
```

> **Tip:** Role names cannot start with `mz_` and `pg_` as they are reserved for system
> roles.

For example, the following creates:
- A role for users who need to perform compute/transform operations in the
  compute/transform.
- A role for users who need to manage indexes on the serving cluster(s).
- A role for users who need to read results from the serving cluster.

**View manager role:**

Create a role for users who need to perform compute/transform operations in
the compute/transform cluster(s). This role will handle creating views,
materialized views, and other transformation objects.
```mzsql
CREATE ROLE view_manager;

```

**Serving index manager role:**

Create a role for users who need to manage indexes on the serving
cluster(s). This role will handle creating indexes to serve results.
```mzsql
CREATE ROLE serving_index_manager;

```

**Data reader role:**

Create a role for users who need to read results from the serving cluster.
```mzsql
CREATE ROLE data_reader;

```

In Materialize, a role is created with inheritance support. With inheritance,
when a role is granted to another role (i.e., the target role), the target role
inherits privileges (not role attributes and parameters) through the other role.
All roles in Materialize are automatically members of
[`PUBLIC`](/security/appendix/appendix-built-in-roles/#public-role). As
such, every role includes inherited privileges from `PUBLIC`.

Once a role is created, you can:

- [Manage its current
  privileges](/security/cloud/access-control/manage-roles/#manage-current-privileges-for-a-role)
  (i.e., privileges on existing objects):
  - By granting privileges for a role or revoking privileges from a role.
  - By granting other roles to the role or revoking roles from the role.
    *Recommended for user account/service account roles.*
- [Manage its future
  privileges](/security/cloud/access-control/manage-roles/#manage-future-privileges-for-a-role)
  (i.e., privileges on objects created in the future):
  - By defining default privileges for objects. With default privileges in
   place, a role is automatically granted/revoked privileges as new objects are
   created by **others** (When an object is created, the creator is granted all
   [applicable privileges](/security/appendix/appendix-privileges/) for that
   object automatically).

> **Disambiguation:** - Use `GRANT|REVOKE ...` to modify privileges on **existing** objects. - Use `ALTER DEFAULT PRIVILEGES` to ensure that privileges are automatically granted or revoked when **new objects** of a certain type are created by others. Then, as needed, you can use `GRANT|REVOKE <privilege>` to adjust those privileges. 

See also:

- For a list of required privileges for specific operations, see [Appendix:
Privileges by command](/security/appendix/appendix-command-privileges/).

## Manage current privileges for a role

### Example prerequisites

The examples below assume:

- The existence of a `source_cluster`, a `compute_cluster`, and a
  `serving_cluster`. For example:

  <no value>```mzsql
  CREATE CLUSTER source_cluster (SIZE = '25cc');
  CREATE CLUSTER compute_cluster (SIZE = '25cc');
  CREATE CLUSTER serving_cluster (SIZE = '25cc');

  ```

- The existence of a `mydb` database and a `sales` schema within the `mydb`
  database. For example:

  <no value>```mzsql
  CREATE DATABASE IF NOT EXISTS mydb;
  CREATE SCHEMA IF NOT EXISTS mydb.sales;

  ```

- The existence of `items`, `orders`, and `sales_items` tables within the
  `mydb.sales` schema. For example:

  <no value>```mzsql
  SET CLUSTER = source_cluster;

  SET DATABASE = mydb;
  SET SCHEMA  = sales;

  CREATE TABLE items(
    item text NOT NULL,
    price numeric(8,4) NOT NULL,
    currency text NOT NULL DEFAULT 'USD'
  );

  CREATE TABLE orders (
      order_id int NOT NULL,
      order_date timestamp NOT NULL,
      item text NOT NULL,
      quantity int NOT NULL,
      status text NOT NULL
  );

  CREATE TABLE sales_items (
    week_of date NOT NULL,
    items text[]
  );

  INSERT INTO items VALUES
  ('brownie',2.25,'USD'),
  ('cheesecake',40,'USD'),
  ('chiffon cake',30,'USD');

  INSERT INTO orders VALUES
  (1,current_timestamp - (1 * interval '3 day') - (35 * interval '1 minute'),'brownies',12, 'Complete'),
  (1,current_timestamp - (1 * interval '3 day') - (35 * interval '1 minute'),'cupcake',12, 'Complete'),
  (2,current_timestamp - (1 * interval '3 day') - (15 * interval '1 minute'),'cheesecake',1, 'Complete'),
  (3,current_timestamp - (1 * interval '3 day'),'chiffon cake',1, 'Complete'),
  (3,current_timestamp - (1 * interval '3 day'),'egg tart',6, 'Complete'),
  (3,current_timestamp - (1 * interval '3 day'),'fruit tart',6, 'Complete'),
  (4,current_timestamp - (1 * interval '2 day')- (30 * interval '1 minute'),'cupcake',6, 'Shipped'),
  (4,current_timestamp - (1 * interval '2 day')- (30 * interval '1 minute'),'cupcake',6, 'Shipped'),
  (5,current_timestamp - (1 * interval '2 day'),'chocolate cake',1, 'Processing'),
  (6,current_timestamp,'brownie',10, 'Pending'),
  (6,current_timestamp,'chocolate cake',1, 'Pending');

  INSERT INTO sales_items VALUES
  (date_trunc('week', current_timestamp),ARRAY['brownie','chocolate chip cookie','chocolate cake']),
  (date_trunc('week', current_timestamp + (1* interval '7 day')), ARRAY['chocolate chip cookie','donut','cupcake']);

  ```

### View privileges for a role

> **Privilege(s) required to run the command:** No specific privilege is required to run the `SHOW PRIVILEGES` 

To view privileges granted to a role, you can use the [`SHOW
PRIVILEGES`](/sql/show-privileges) command, substituting `<role>` with the role
name (see [`SHOW PRIVILEGES`](/sql/show-default-privileges) for the full
syntax):

```mzsql
SHOW PRIVILEGES FOR <role>;
```

> **Note:** All roles in Materialize are automatically members of
> [`PUBLIC`](/security/appendix/appendix-built-in-roles/#public-role). As
> such, every role includes inherited privileges from `PUBLIC`.

For example:

**User:**

To view privileges for a
[user](/security/users-service-accounts/invite-users/), run [`SHOW
PRIVILEGES`](/sql/show-privileges) on the role named after the user's email
(automatically created when the account is activated; i.e., first time the
user logs in):
```mzsql
SHOW PRIVILEGES FOR "blue.berry@example.com";

```

The results show that the role currently has only the privileges inherited
through the `PUBLIC` role.

```none
| grantor           | grantee | database    | schema | name        | object_type | privilege_type |
| ----------------- | ------- | ----------- | ------ | ----------- | ----------- | -------------- |
| admin@example.com | PUBLIC  | mydb        | null   | public      | schema      | USAGE          |
| mz_system         | PUBLIC  | materialize | null   | public      | schema      | USAGE          |
| mz_system         | PUBLIC  | null        | null   | materialize | database    | USAGE          |
| mz_system         | PUBLIC  | null        | null   | quickstart  | cluster     | USAGE          |
```

**Service account role:**

To view privileges for a [service
account](/security/users-service-accounts/create-service-accounts/), run
[`SHOW PRIVILEGES`](/sql/show-privileges) on the role named after the
service account user (automatically created when the account is activated;
i.e., first time the service account connects):
```mzsql
SHOW PRIVILEGES FOR sales_report_app;

```

The results show that the role currently has only the privileges inherited
through the `PUBLIC` role.

```none
| grantor           | grantee | database    | schema | name        | object_type | privilege_type |
| ----------------- | ------- | ----------- | ------ | ----------- | ----------- | -------------- |
| admin@example.com | PUBLIC  | mydb        | null   | public      | schema      | USAGE          |
| mz_system         | PUBLIC  | materialize | null   | public      | schema      | USAGE          |
| mz_system         | PUBLIC  | null        | null   | materialize | database    | USAGE          |
| mz_system         | PUBLIC  | null        | null   | quickstart  | cluster     | USAGE          |
```

**Manually created functional roles:**

**View manager role:**

Show the privileges for the `view_manager` role created in the
[Create a role section](#create-a-role).
```mzsql
SHOW PRIVILEGES FOR view_manager;

```

The results show that the role currently has only the privileges inherited
through the `PUBLIC` role.

```none
| grantor           | grantee | database    | schema | name        | object_type | privilege_type |
| ----------------- | ------- | ----------- | ------ | ----------- | ----------- | -------------- |
| admin@example.com | PUBLIC  | mydb        | null   | public      | schema      | USAGE          |
| mz_system         | PUBLIC  | materialize | null   | public      | schema      | USAGE          |
| mz_system         | PUBLIC  | null        | null   | materialize | database    | USAGE          |
| mz_system         | PUBLIC  | null        | null   | quickstart  | cluster     | USAGE          |
```

**Serving index manager role:**

Show the privileges for the `serving_index_manager` role created in the
[Create a role section](#create-a-role).
```mzsql
SHOW PRIVILEGES FOR serving_index_manager;

```

The results show that the role currently has only the privileges inherited
through the `PUBLIC` role.

```none
| grantor           | grantee | database    | schema | name        | object_type | privilege_type |
| ----------------- | ------- | ----------- | ------ | ----------- | ----------- | -------------- |
| admin@example.com | PUBLIC  | mydb        | null   | public      | schema      | USAGE          |
| mz_system         | PUBLIC  | materialize | null   | public      | schema      | USAGE          |
| mz_system         | PUBLIC  | null        | null   | materialize | database    | USAGE          |
| mz_system         | PUBLIC  | null        | null   | quickstart  | cluster     | USAGE          |
```

**Data reader role:**

Show the privileges for the `data_reader` role created in the
[Create a role section](#create-a-role).
```mzsql
SHOW PRIVILEGES FOR data_reader;

```

The results show that the role currently has only the privileges inherited
through the `PUBLIC` role.

```none
| grantor           | grantee | database    | schema | name        | object_type | privilege_type |
| ----------------- | ------- | ----------- | ------ | ----------- | ----------- | -------------- |
| admin@example.com | PUBLIC  | mydb        | null   | public      | schema      | USAGE          |
| mz_system         | PUBLIC  | materialize | null   | public      | schema      | USAGE          |
| mz_system         | PUBLIC  | null        | null   | materialize | database    | USAGE          |
| mz_system         | PUBLIC  | null        | null   | quickstart  | cluster     | USAGE          |
```

> **Tip:** For the `SHOW PRIVILEGES` command, you can add a `WHERE` clause to filter by the
> return fields; e.g., `SHOW PRIVILEGES FOR view_manager WHERE
> name='quickstart';`.

### Grant privileges to a role

To grant [privileges](/security/appendix/appendix-command-privileges/) to
a role, use the [`GRANT PRIVILEGE`](/sql/grant-privilege/) statement (see
[`GRANT PRIVILEGE`](/sql/grant-privilege/) for the full syntax)

> **Privilege(s) required to run the command:** - Ownership of affected objects. - `USAGE` privileges on the containing database if the affected object is a schema. - `USAGE` privileges on the containing schema if the affected object is namespaced by a schema. - _superuser_ status if the privilege is a system privilege. To override the **object ownership** requirements to grant privileges, run as an Organization admin. 

```mzsql
GRANT <PRIVILEGE> ON <OBJECT_TYPE> <object_name> TO <role>;
```

When possible, avoid granting privileges directly to individual user or service
account roles (which are named after email addresses or service account user).
Instead, create reusable, functional roles (e.g., `data_reader`, `view_manager`)
with well-defined privileges, and grant these roles to the individual user or
service account roles. You can also grant functional roles to other functional
roles to compose more complex functional roles.

For example, the following grants privileges to the manually created functional
roles.

> **Note:** Various SQL operations require additional privileges on related objects, such
> as:
> - For objects that use compute resources (e.g., indexes, materialized views,
>   replicas, sources, sinks), access is also required for the associated cluster.
> - For objects in a schema, access is also required for the schema.
> For details on SQL operations and needed privileges, see [Appendix: Privileges
> by command](/security/appendix/appendix-command-privileges/).

**View manager role:**

The following example grants the `view_manager` role various privileges to
run:

- [`SELECT`](/sql/select/#privileges) from currently existing
  materialized views/views/tables/sources in the `mydb.sales` schema.
- [`CREATE MATERIALIZED VIEW`](/sql/create-materialized-view/#privileges)
  in the `mydb.sales` schema on the `compute_cluster`.
- [`CREATE VIEW`](/sql/create-view/#privileges) if using intermediate views
  as part of a stacked view definition (i.e., views whose definition depends
  on other views).

{{< note >}}
If a query directly references a view or materialized view:
{{% include-headless "/headless/rbac-cloud/select-views-privileges" %}}
{{</ note >}}
```mzsql
-- To SELECT from currently **existing** relations in `mydb.sales` schema:
-- Need USAGE on schema and cluster
-- Need SELECT on existing materialized views/views/tables/sources
GRANT USAGE ON SCHEMA mydb.sales TO view_manager;
GRANT USAGE ON CLUSTER compute_cluster TO view_manager;
GRANT SELECT ON ALL TABLES IN SCHEMA mydb.sales TO view_manager;
-- ALL TABLES encompasses tables, views, materialized views, and sources,
-- and refers only to currently existing objects.

-- To CREATE materialized views/views:
-- Need CREATE on cluster for materialized views
-- Need CREATE on schema for the materialized views/views
GRANT CREATE ON CLUSTER compute_cluster TO view_manager;
GRANT CREATE ON SCHEMA mydb.sales TO view_manager;

```

Review the privileges granted to the `view_manager` role:
```mzsql
SHOW PRIVILEGES FOR view_manager;

```
The results should reflect the new privileges granted to the `view_manager`
role in addition to those privileges inherited through the `PUBLIC` role.

```none
   grantor        |   grantee    |  database   | schema |         name        |    object_type    | privilege_type
------------------+--------------+-------------+--------+---------------------+-------------------+----------------
admin@example.com | view_manager | mydb        | sales  | items               | table             | SELECT
admin@example.com | view_manager | mydb        | sales  | orders              | table             | SELECT
admin@example.com | view_manager | mydb        | sales  | orders_daily_totals | materialized-view | SELECT
admin@example.com | view_manager | mydb        | sales  | orders_view         | view              | SELECT
admin@example.com | view_manager | mydb        | sales  | sales_items         | table             | SELECT
admin@example.com | view_manager | mydb        | <null> | sales               | schema            | CREATE
admin@example.com | view_manager | mydb        | <null> | sales               | schema            | USAGE
admin@example.com | view_manager | <null>      | <null> | compute_cluster     | cluster           | CREATE
admin@example.com | view_manager | <null>      | <null> | compute_cluster     | cluster           | USAGE
admin@example.com | PUBLIC       | mydb        | <null> | public              | schema            | USAGE
mz_system         | PUBLIC       | materialize | <null> | public              | schema            | USAGE
mz_system         | PUBLIC       | <null>      | <null> | materialize         | database          | USAGE
mz_system         | PUBLIC       | <null>      | <null> | quickstart          | cluster           | USAGE
```

{{< important >}}

The `GRANT SELECT ON ALL TABLES IN SCHEMA mydb.sales TO view_manager;`
statement results in `view_manager` having `SELECT` privileges on specific
objects, namely the three tables that existed in the `mydb.sales` schema at
the time of the grant. It **does not** grant `SELECT` privileges on any
tables, views, materialized views, or sources created by others in the
schema afterwards.

For new objects created by others, you can either:
- Manually grant privileges on new objects; or
- Use [default
privileges](/security/cloud/access-control/manage-roles/#manage-future-privileges-for-a-role)
to automatically grant privileges on new objects.

{{</ important >}}

**Serving index manager role:**

The following example grants the `serving_index_manager` role various
privileges to:

- [`CREATE INDEX`](/sql/create-index/#privileges) in the `mydb.sales`
  schema on the `serving_cluster`.

- Use the `serving_cluster` (i.e., `USAGE`). Although you can create an
index without the `USAGE`, this allows the person creating the index to use
the index to verify.

{{< note >}}

In addition to database privileges, to create an index, a role must be the
owner of the object on which the index is created.

{{</ note >}}
```mzsql
-- To create an index on an object **owned** by the role:
-- Need CREATE on the cluster.
-- Need CREATE on the schema.
GRANT CREATE ON CLUSTER serving_cluster TO serving_index_manager;
GRANT CREATE ON SCHEMA mydb.sales TO serving_index_manager;

-- Optional.
GRANT USAGE ON CLUSTER serving_cluster TO serving_index_manager;

```

Review the privileges granted to the `serving_index_manager` role:
```mzsql
SHOW PRIVILEGES FOR serving_index_manager;

```
The results should reflect the new privileges granted to the `index_manager`
role in addition to those privileges inherited through the `PUBLIC` role.

```none
   grantor        |        grantee        |  database   | schema |      name       | object_type | privilege_type
------------------+-----------------------+-------------+--------+-----------------+-------------+----------------
admin@example.com | serving_index_manager | mydb        | <null> | sales           | schema      | CREATE
admin@example.com | serving_index_manager | <null>      | <null> | serving_cluster | cluster     | CREATE
admin@example.com | serving_index_manager | <null>      | <null> | serving_cluster | cluster     | USAGE
admin@example.com | PUBLIC                | mydb        | <null> | public          | schema      | USAGE
mz_system         | PUBLIC                | materialize | <null> | public          | schema      | USAGE
mz_system         | PUBLIC                | <null>      | <null> | materialize     | database    | USAGE
mz_system         | PUBLIC                | <null>      | <null> | quickstart      | cluster     | USAGE
```

{{< note >}}

In addition to database privileges, a role must be the owner of the object
on which the index is created. In our examples, `view_manager` role has
privileges to create the various materialized views that will be indexed:

- See [Grant a role to another
role](/security/cloud/access-control/manage-roles/#grant-a-role-to-another-role) for
details and example of granting `serving_cluster` role to `view_manager`.

- See [Change ownership of
objects](/security/cloud/access-control/manage-roles/#change-ownership-of-objects)
for details and example of changing ownership of objects.

{{</ note >}}

**Data reader role:**
The following example grants the `data_reader` role privileges to run:

- [`SELECT`](/sql/select/#privileges) from all existing tables/materialized
  views/views/sources in the `mydb.sales` schema on the `serving_cluster`.

{{< note >}}
If a query directly references a view or materialized view:
{{% include-headless "/headless/rbac-cloud/select-views-privileges" %}}
{{</ note >}}
```mzsql
-- To select from **existing** views/materialized views/tables/sources:
-- Need USAGE on schema and cluster
-- Need SELECT on the materialized views/views/tables/sources
GRANT USAGE ON SCHEMA mydb.sales TO data_reader;
GRANT USAGE ON CLUSTER serving_cluster TO data_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA mydb.sales TO data_reader;
-- For PostgreSQL compatibility, ALL TABLES encompasses tables, views,
-- materialized views, and sources.

```

Review the privileges granted to the `data_reader` role:
```mzsql
SHOW PRIVILEGES FOR data_reader;

```
The results should reflect the new privileges granted to the `data_reader`
role in addition to those privileges inherited through the `PUBLIC` role.

```none
    grantor       |   grantee   |  database   | schema |        name         |    object_type    | privilege_type
------------------+-------------+-------------+--------+---------------------+-------------------+----------------
admin@example.com | data_reader | mydb        | sales  | items               | table             | SELECT
admin@example.com | data_reader | mydb        | sales  | orders              | table             | SELECT
admin@example.com | data_reader | mydb        | sales  | orders_daily_totals | materialized-view | SELECT
admin@example.com | data_reader | mydb        | sales  | orders_view         | view              | SELECT
admin@example.com | data_reader | mydb        | sales  | sales_items         | table             | SELECT
admin@example.com | data_reader | mydb        | <null> | sales               | schema            | USAGE
admin@example.com | data_reader | <null>      | <null> | serving_cluster     | cluster           | USAGE
admin@example.com | PUBLIC      | mydb        | <null> | public              | schema            | USAGE
mz_system         | PUBLIC      | materialize | <null> | public              | schema            | USAGE
mz_system         | PUBLIC      | <null>      | <null> | materialize         | database          | USAGE
mz_system         | PUBLIC      | <null>      | <null> | quickstart          | cluster           | USAGE
```

{{< important >}}

The `GRANT SELECT ON ALL TABLES IN SCHEMA mydb.sales TO data_reader;`
statement results in `data_reader` having `SELECT` privileges on specific
objects, namely the three tables that existed in the `mydb.sales` schema at
the time of the grant. It **does not** grant `SELECT` privileges on any
tables, views, materialized views, or sources created in the schema
afterwards by others.

For new objects created by others, you can either:
- Manually grant privileges on new objects; or
- Use [default
privileges](/security/cloud/access-control/manage-roles/#manage-future-privileges-for-a-role)
to automatically grant privileges on new objects.

{{</ important >}}

### Grant a role to another role

Once a role is created, you can modify its privileges either:

- Directly by [granting privileges for a role](#grant-privileges-to-a-role) or
  [revoking privileges from a role](#revoke-privileges-from-a-role).
- Indirectly (through inheritance) by granting other roles to the role or
  [revoking roles from the role](#revoke-a-role-from-another-role).

> **Tip:** When possible, avoid granting privileges directly to individual user or service
> account roles (which are named after email addresses or service account user).
> Instead, create reusable, functional roles (e.g., `data_reader`, `view_manager`)
> with well-defined privileges, and grant these roles to the individual user or
> service account roles. You can also grant functional roles to other functional
> roles to compose more complex functional roles.

To grant a role to another role (where the role can be a user role/service
account role/functional role), use the [`GRANT ROLE`](/sql/grant-role/)
statement (see [`GRANT ROLE`](/sql/grant-role/) for full syntax):

> **Privilege(s) required to run the command:** - `CREATEROLE` privileges on the system. Organization admin has the required privileges on the system. 

```mzsql
GRANT <role> [, <role>...] to <target_role> [, <target_role> ...];
```

When a role is granted to another role, the target role becomes a member of the
other role and inherits the privileges through the other role.

In the following examples,

- The functional role `view_manager` is granted to the user role
  `blue.berry@example.com`.
- The functional role `serving_index_manager` is granted to the functional role
  `view_manager`.
- The functional role `data_reader` is granted to the service account role
  `sales_report_app`.

**Grant view_manager role:**

The following grants the `view_manager` role to the role associated with the
user `blue.berry@example.com`.
```mzsql
GRANT view_manager TO "blue.berry@example.com";

```

Review the privileges granted to the `blue.berry@example.com` role:
```mzsql
SHOW PRIVILEGES FOR "blue.berry@example.com";

```
The results should include the privileges inherited through the
`view_manager` role in addition to those privileges through the `PUBLIC`
role. If the role had been granted direct privileges, those would also be
included.

```none
   grantor        |   grantee    |  database   | schema |        name       | object_type | privilege_type
------------------+--------------+-------------+--------+-------------------+-------------+----------------
admin@example.com | view_manager | mydb        | sales  | items             | table       | SELECT
admin@example.com | view_manager | mydb        | sales  | orders            | table       | SELECT
admin@example.com | view_manager | mydb        | sales  | sales_items       | table       | SELECT
admin@example.com | view_manager | mydb        |        | sales             | schema      | CREATE
admin@example.com | view_manager | mydb        |        | sales             | schema      | USAGE
admin@example.com | view_manager |             |        | compute_cluster   | cluster     | CREATE
admin@example.com | view_manager |             |        | compute_cluster   | cluster     | USAGE
admin@example.com | PUBLIC       | mydb        |        | public            | schema      | USAGE
mz_system         | PUBLIC       | materialize |        | public            | schema      | USAGE
mz_system         | PUBLIC       |             |        | materialize       | database    | USAGE
mz_system         | PUBLIC       |             |        | quickstart        | cluster     | USAGE
```

After the `view_manager` role is granted to `blue.berry@example.com`,
`blue.berry@example.com` can create objects in the `mydb.sales` schema on
the `compute_cluster`.
```mzsql
-- run as blue.berry@example.com
SET CLUSTER TO compute_cluster;
SET DATABASE TO mydb;
SET SCHEMA TO sales;

-- Create an intermediate view for a stacked materialized view
CREATE VIEW orders_view AS
SELECT o.*,i.price,o.quantity * i.price as subtotal
FROM orders as o
JOIN items as i
ON o.item = i.item;

-- Create a materialized view
CREATE MATERIALIZED VIEW orders_daily_totals AS
SELECT date_trunc('day',order_date) AS order_date,
      sum(subtotal) AS daily_total
FROM orders_view
GROUP BY date_trunc('day',order_date);

-- Select from the materialized view
SELECT * from orders_daily_totals;

```
In Materialize, a role automatically gets all [applicable
privileges](/security/appendix/appendix-privileges/) for an object they
create; for example, the creator of a schema gets `CREATE` and `USAGE`; the
creator of a table gets `SELECT`, `INSERT`, `UPDATE`, and `DELETE`.

For example, if you show privileges for `"blue.berry@example.com"` after
creating the view and materialized view, you will see that the role has
`SELECT` privileges on the `orders_daily_totals`  and `orders_view`.

```none
  grantor              |         grantee        |  database   | schema |      name           |     object_type   | privilege_type
-----------------------+------------------------+-------------+--------+---------------------+-------------------+---------------
blue.berry@example.com | blue.berry@example.com | mydb        | sales  | orders_daily_totals | materialized-view | SELECT
blue.berry@example.com | blue.berry@example.com | mydb        | sales  | orders_view         | view              | SELECT
admin@example.com      | view_manager           | mydb        | sales  | items               | table             | SELECT
admin@example.com      | view_manager           | mydb        | sales  | orders              | table             | SELECT
admin@example.com      | view_manager           | mydb        | sales  | sales_items         | table             | SELECT
... -- Rest omitted for brevity
```

{{< note >}}
If a query directly references a view or materialized view:
{{% include-headless "/headless/rbac-cloud/select-views-privileges" %}}
{{</ note >}}

However, with the current privileges, `"blue.berry@example.com"` cannot
select from new views/materialized views created by **others** in the
schema and vice versa. For privileges on new objects created by **others**, you can either:
- Manually grant privileges on new objects; or
- Use [default
privileges](/security/cloud/access-control/manage-roles/#manage-future-privileges-for-a-role)
to automatically grant privileges on new objects.

**Grant serving_index_manager role:**
The following grants the `serving_index_manager` role to the functional role
`view_manager`, which already has privileges to create materialized views in
`mydb.sales` schema. This allows members of the `view_manager` role to
create indexes on their objects on the `serving_cluster`.
```mzsql
GRANT serving_index_manager TO view_manager;

```

Review the privileges of `view_manager` as well as `"blue.berry@example.com"`
(a member of  `view_manager`) after the grant.

**Privileges for view_manager:**
Review the privileges granted to the `view_manager` role:
```mzsql
SHOW PRIVILEGES FOR view_manager;

```
The results include the privileges inherited through the
`serving_index_manager` role in addition to those privileges inherited
through the `PUBLIC` role as well as those granted directly to the role, if
any.

```none
  grantor         |        grantee        |  database   | schema |        name       | object_type | privilege_type
------------------+-----------------------+-------------+--------+-------------------+-------------+----------------
admin@example.com | serving_index_manager | mydb        |        | sales             | schema      | CREATE
admin@example.com | serving_index_manager |             |        | serving_cluster   | cluster     | CREATE
admin@example.com | serving_index_manager |             |        | serving_cluster   | cluster     | USAGE
admin@example.com | view_manager          | mydb        | sales  | items             | table       | SELECT
admin@example.com | view_manager          | mydb        | sales  | orders            | table       | SELECT
admin@example.com | view_manager          | mydb        | sales  | sales_items       | table       | SELECT
admin@example.com | view_manager          | mydb        |        | sales             | schema      | CREATE
admin@example.com | view_manager          | mydb        |        | sales             | schema      | USAGE
admin@example.com | view_manager          |             |        | compute_cluster   | cluster     | CREATE
admin@example.com | view_manager          |             |        | compute_cluster   | cluster     | USAGE
admin@example.com | PUBLIC                | mydb        |        | public            | schema      | USAGE
mz_system         | PUBLIC                | materialize |        | public            | schema      | USAGE
mz_system         | PUBLIC                |             |        | materialize       | database    | USAGE
mz_system         | PUBLIC                |             |        | quickstart        | cluster     | USAGE
```

**Privileges for blue.berry@example.com:**

Review the privileges for `"blue.berry@example.com"` (a member of `view_manager`):
```mzsql
SHOW PRIVILEGES FOR "blue.berry@example.com";

```
The results include the privileges inherited through the
`serving_index_manager` role in addition to those privileges inherited
through the `PUBLIC` role as well as those granted directly to the role, if
any. For example, after being granted the `view_manager` role,
`"blue.berry@example.com"` created the `orders_daily_totals` and
`orders_view`. As the creator, `"blue.berry@example.com"` automatically gets
all applicable privileges on the objects they create.

```none
  grantor              |         grantee        |  database   | schema |    name             |    object_type    | privilege_type
-----------------------+------------------------+-------------+--------+---------------------+-------------------+---------------
blue.berry@example.com | blue.berry@example.com | mydb        | sales  | orders_daily_totals | materialized-view | SELECT
blue.berry@example.com | blue.berry@example.com | mydb        | sales  | orders_view         | view              | SELECT
admin@example.com      | serving_index_manager  | mydb        |        | sales               | schema            | CREATE
admin@example.com      | serving_index_manager  |             |        | serving_cluster     | cluster           | CREATE
admin@example.com      | serving_index_manager  |             |        | serving_cluster     | cluster           | USAGE
admin@example.com      | view_manager           | mydb        | sales  | items               | table             | SELECT
admin@example.com      | view_manager           | mydb        | sales  | orders              | table             | SELECT
admin@example.com      | view_manager           | mydb        | sales  | sales_items         | table             | SELECT
admin@example.com      | view_manager           | mydb        |        | sales               | schema            | CREATE
admin@example.com      | view_manager           | mydb        |        | sales               | schema            | USAGE
admin@example.com      | view_manager           |             |        | compute_cluster     | cluster           | CREATE
admin@example.com      | view_manager           |             |        | compute_cluster     | cluster           | USAGE
admin@example.com      | PUBLIC                 | mydb        |        | public              | schema            | USAGE
mz_system              | PUBLIC                 | materialize |        | public              | schema            | USAGE
mz_system              | PUBLIC                 |             |        | materialize         | database          | USAGE
mz_system              | PUBLIC                 |             |        | quickstart          | cluster           | USAGE
```

To create indexes on an object, in addition to specific `CREATE` privileges
(granted by the `serving_index_manager` role), the user needs to be the
owner of the object.

After the `serving_index_manager` role is granted to the `view_manager`
role, members of `view_manager` can create indexes on the `serving_cluster`
for objects that they own. For example, `"blue.berry@example.com"` can
create an index on the `orders_daily_totals` materialized view.
```mzsql
-- run as "blue.berry@example.com"
SET CLUSTER TO serving_cluster;
SET DATABASE TO mydb;
SET SCHEMA TO sales;

CREATE INDEX ON orders_daily_totals (order_date);

-- If the role has `USAGE` on the `serving_cluster`:
SELECT * from orders_daily_totals;

```
To allow others in the `view_manager` role to create indexes, see [Change
ownership of objects](/security/cloud/access-control/manage-roles/#change-ownership-of-objects).

**Grant data_reader role:**

The following grants the `data_reader` role to the service account role
`sales_report_app`.
```mzsql
GRANT data_reader TO sales_report_app;

```

Review the privileges for `sales_report_app` after the grant:
```mzsql
SHOW PRIVILEGES FOR sales_report_app;

```The results should include the privileges inherited through the
`data_reader` role in addition to those privileges inherited through the
`PUBLIC` role. If the role had been granted direct privileges, those would
also be included.

```none
    grantor       |   grantee   |  database   | schema |        name         | object_type | privilege_type
------------------+-------------+-------------+--------+---------------------+-------------+----------------
admin@example.com | data_reader | mydb        | sales  | items               | table       | SELECT
admin@example.com | data_reader | mydb        | sales  | orders              | table       | SELECT
admin@example.com | data_reader | mydb        | sales  | sales_items         | table       | SELECT
admin@example.com | data_reader | mydb        |        | sales               | schema      | USAGE
admin@example.com | data_reader |             |        | serving_cluster     | cluster     | USAGE
admin@example.com | PUBLIC      | mydb        |        | public              | schema      | USAGE
mz_system         | PUBLIC      | materialize |        | public              | schema      | USAGE
mz_system         | PUBLIC      |             |        | materialize         | database    | USAGE
mz_system         | PUBLIC      |             |        | quickstart          | cluster     | USAGE
```

As the privileges show, after the `data_reader` role is granted to the
`sales_report_app` service account role, `sales_report_app` can read from
the three tables in the `mydb.sales` schema on the `serving_cluster`.
```mzsql
SET CLUSTER TO serving_cluster;
SET DATABASE TO mydb;
SET SCHEMA TO sales;

SELECT * FROM sales_items;

```
However, `sales_report_app` cannot read from the new objects in
`mydb.sales`; e.g., `orders_daily_totals` materialized view and its
underlying view `orders_view` that were created after the `SELECT`
privileges were granted to the `data_reader` role.

To allow `sales_report_app` or `data_reader` to read from the new objects in
`mydb.sales`, you can either:
- Manually grant `SELECT` privileges on the new objects; or
- Use [default
privileges](/security/cloud/access-control/manage-roles/#manage-future-privileges-for-a-role)
to automatically grant `SELECT` privileges on new objects.

### Revoke privileges from a role

To remove privileges from a role, use the [`REVOKE <privilege>`](/sql/revoke-privilege/) statement:

> **Privilege(s) required to run the command:** - Ownership of affected objects. - `USAGE` privileges on the containing database if the affected object is a schema. - `USAGE` privileges on the containing schema if the affected object is namespaced by a schema. - _superuser_ status if the privilege is a system privilege. 

```mzsql
REVOKE <PRIVILEGE> ON <OBJECT_TYPE> <object_name> FROM <role>;
```

### Revoke a role from another role

To revoke a role from another role, use the [`REVOKE <role>`](/sql/revoke-role/) statement:

> **Privilege(s) required to run the command:** - `CREATEROLE` privileges on the systems. 

```mzsql
REVOKE <role> FROM <target_role>;
```

For example:

```mzsql
REVOKE data_reader FROM sales_report_app;
```

> **Important:** When you revoke a role from another role (user role/service account
> role/independent role), the target role is no longer a member of the revoked
> role nor inherits the revoked role's privileges. **However**, privileges are
> cumulative: if the target role inherits the same privilege(s) from another role,
> the target role still has the privilege(s) through the other role.

## Manage future privileges for a role

In Materialize, a role automatically gets all [applicable
privileges](/security/appendix/appendix-privileges/) for an object they
create/own; for example, the creator of a schema gets `CREATE` and `USAGE`; the
creator of a table gets `SELECT`, `INSERT`, `UPDATE`, and `DELETE`. However, for
others to access the new object, you can either manually grant privileges on new
objects or use default privileges to automatically grant privileges to others as
new objects are created.

Default privileges can be specified for a given object type and scoped to:

- all future objects of that type;
- all future objects of that type within specific databases or schemas;
- all future objects of that type created by specific roles (or by all roles
  `PUBLIC`).

Default privileges apply only to objects created after these privileges are
defined. They do not affect objects that were created before the default
privileges were set.

> **Disambiguation:** - Use `GRANT|REVOKE ...` to modify privileges on **existing** objects. - Use `ALTER DEFAULT PRIVILEGES` to ensure that privileges are automatically granted or revoked when **new objects** of a certain type are created by others. Then, as needed, you can use `GRANT|REVOKE <privilege>` to adjust those privileges. 

### View default privileges

To view default privileges, you can use the [`SHOW DEFAULT
PRIVILEGES`](/sql/show-default-privileges) command, substituting `<role>` with
the role name (see [`SHOW DEFAULT PRIVILEGES`](/sql/show-default-privileges) for
the full syntax):

> **Privilege(s) required to run the command:** No specific privilege is required to run the `SHOW DEFAULT PRIVILEGES`. 

```mzsql
SHOW DEFAULT PRIVILEGES FOR <role>;
```

For example:

**User:**

To view default privileges for a
[user](/security/users-service-accounts/invite-users/), run [`SHOW DEFAULT
PRIVILEGES`](/sql/show-default-privileges) on the role named after the
user's email:
```mzsql
SHOW DEFAULT PRIVILEGES FOR "blue.berry@example.com";

```
The example results show that the default privileges for
`"blue.berry@example.com"` are the default privileges it has as a member of
the `PUBLIC` role.

{{% include-headless
"/headless/rbac-cloud/show-default-privileges-new-roles" %}}

**Service account role:**

To view default privileges for a [service
account](/security/users-service-accounts/create-service-accounts/), run
[`SHOW DEFAULT PRIVILEGES`](/sql/show-default-privileges) on the role named after the
service account user:
```mzsql
SHOW DEFAULT PRIVILEGES FOR sales_report_app;

```
The example results show that the default privileges for `sales_report_app`
are the default privileges it has as a member of the `PUBLIC` role.

{{% include-headless
"/headless/rbac-cloud/show-default-privileges-new-roles" %}}

**Manually created functional roles:**

**View manager role:**

Show the default privileges for the `view_manager` role created in the
[Create a role section](#create-a-role).
```mzsql
SHOW DEFAULT PRIVILEGES FOR view_manager;

```
The example results show that the default privileges for `view_manager` are
the default privileges it has as a member of the `PUBLIC` role.

{{% include-headless
"/headless/rbac-cloud/show-default-privileges-new-roles" %}}

**Serving index manager role:**

Show the default privileges for the `serving_index_manager` role created in
the [Create a role section](#create-a-role).
```mzsql
SHOW DEFAULT PRIVILEGES FOR serving_index_manager;

```
The example results show that the default privileges for
`serving_index_manager` are the default privileges it has as a member of
the `PUBLIC` role.

{{% include-headless
"/headless/rbac-cloud/show-default-privileges-new-roles" %}}

**Data reader role:**

Show the default privileges for the `data_reader` role created in the
[Create a role section](#create-a-role).
```mzsql
SHOW DEFAULT PRIVILEGES FOR data_reader;

```
The example results show that the default privileges for `data_reader` are
the default privileges it has as a member of the `PUBLIC` role.

{{% include-headless
"/headless/rbac-cloud/show-default-privileges-new-roles" %}}

### Alter default privileges

To define default privilege for objects created by a role, use the [`ALTER
DEFAULT PRIVILEGES`](/sql/alter-default-privileges) command (see  [`ALTER
DEFAULT PRIVILEGES`](/sql/alter-default-privileges) for the full syntax):

> **Privilege(s) required to run the command:** - Role membership in `role_name`. - `USAGE` privileges on the containing database if `database_name` is specified. - `USAGE` privileges on the containing schema if `schema_name` is specified. - _superuser_ status if the _target_role_ is `PUBLIC` or **ALL ROLES** is specified. 

```mzsql
ALTER DEFAULT PRIVILEGES FOR ROLE <object_creator>
   IN SCHEMA <schema>    -- Optional. If specified, need USAGE on database and schema.
   GRANT <privilege> ON <object_type> TO <target_role>;
```

> **Note:** - With the exception of the `PUBLIC` role, the `<object_creator>` role is
>   **not** transitive. That is, default privileges that specify a functional role
>   like `view_manager` as the `<object_creator>` do **not** apply to objects
>   created by its members.
>   However, you can approximate default privileges for a functional role by
>   restricting `CREATE` privileges for the objects to the desired functional
>   roles (e.g., only `view_managers` have privileges to create tables in
>   `mydb.sales` schema) and then specify `PUBLIC` as the `<object_creator>`.
> - As with any other grants, the privileges granted to the `<target_role>` are
>   inherited by the members of the `<target_role>`.

**Specify blue.berry as the object creator:**

The following updates the default privileges for new tables, views,
materialized views, and sources created in `mydb.sales` schema by the
`blue.berry@example.com` role; specifically, grants `SELECT` privileges on
these objects to `view_manager` and `data_reader` roles.
```mzsql
-- For new relations created by the `"blue.berry@example.com"` role
-- Grant `SELECT` privileges to the `view_manager` and `data_reader` roles
ALTER DEFAULT PRIVILEGES FOR ROLE "blue.berry@example.com"
IN SCHEMA mydb.sales  -- Optional. If specified, need USAGE on database and schema.
GRANT SELECT ON TABLES TO view_manager, data_reader;
-- `TABLES` refers to tables, views, materialized views, and sources.

```

Afterwards, if `blue.berry@example.com` creates a new materialized view in
the `mydb.sales` schema, the `view_manager` and `data_reader` roles are
automatically granted `SELECT` privileges on the new object.
```mzsql
-- Run as `blue.berry@example.com`
SET CLUSTER TO compute_cluster;
SET DATABASE TO mydb;
SET SCHEMA TO sales;

-- Create a materialized view
CREATE MATERIALIZED VIEW magic AS
SELECT o.*,i.price,o.quantity * i.price as subtotal
FROM orders as o
JOIN items as i
ON o.item = i.item;

```

To verify that the default privileges have been automatically granted, you can
run `SHOW PRIVILEGES`:

**view_manager:**

Verify the privileges for `view_manager`:
```mzsql
SHOW PRIVILEGES FOR view_manager where grantor = 'blue.berry@example.com';

```
The results include the `SELECT` privilege on newly created `magic`
materialized view:

```none
        grantor         |        grantee        |  database   | schema |        name         |    object_type    | privilege_type
------------------------+-----------------------+-------------+--------+---------------------+-------------------+----------------
 blue.berry@example.com | view_manager          | mydb        | sales  | magic               | materialized-view | SELECT
```

**data_reader:**

Verify the privileges for `data_reader`:
```mzsql
SHOW PRIVILEGES FOR data_reader where grantor = 'blue.berry@example.com';

```
The results include the `SELECT` privilege on newly created `magic`
materialized view:

```none
        grantor         |   grantee   |  database   | schema |        name         |    object_type    | privilege_type
------------------------+-------------+-------------+--------+---------------------+-------------------+----------------
 blue.berry@example.com | data_reader | mydb        | sales  | magic               | materialized-view | SELECT
```

**sales_report_app (a member of data_reader):**
Verify the privileges for `sales_report_app` (a member of the
`data_reader` role):
```mzsql
SHOW PRIVILEGES FOR sales_report_app where grantor = 'blue.berry@example.com';

```
The results include the `SELECT` privilege on the `magic` materialized view
it inherits through the `data_reader` role:

```none
        grantor         |   grantee   |  database   | schema |        name         |    object_type    | privilege_type
------------------------+-------------+-------------+--------+---------------------+-------------------+----------------
 blue.berry@example.com | data_reader | mydb        | sales  | magic               | materialized-view | SELECT
```

**Specify PUBLIC as the object creator:**

With the exception of the `PUBLIC` role, the `<object_creator>` role is
**not** transitive. That is, default privileges that specify a functional
role like `view_manager` as the `<object_creator>` do **not** apply to
objects created by its members.

To illustrate, the following adds a new member `lemon@example.com` to the
`view_manager` role and creates a new default privilege, specifying
`view_manager` as the `<object_creator>`.
```mzsql
GRANT view_manager TO "lemon@example.com";

ALTER DEFAULT PRIVILEGES FOR ROLE view_manager
IN SCHEMA mydb.sales -- Optional. If specified, need USAGE on database and schema.
GRANT INSERT ON TABLES TO view_manager;
-- Although `TABLES` refers to tables, views, materialized views, and
-- sources, the INSERT privilege will only apply to tables.

```

If `lemon@example.com` creates a new table `only_lemon`, the above default
`INSERT` privilege will not apply as the object creator must be
`view_manager`, not a member of `view_manager`.
```mzsql
-- Run as `lemon@example.com` (a member of `view_manager`)
SET CLUSTER TO compute_cluster;
SET DATABASE TO mydb;
SET SCHEMA TO sales;

CREATE TABLE only_lemon (id INT);

SHOW PRIVILEGES FOR view_manager where name = 'only_lemon';

```
The `SHOW PRIVILEGES FOR view_manager  where name = 'only_lemon';` returns 0
rows.

However, if `view_manager` is the **only role** that has `CREATE` privileges
on `mydb.sales` schema, you can specify `PUBLIC` as the `<object_creator>`.
Then, the default privilege will apply to all objects created by
`view_manager` and its members.
```mzsql
ALTER DEFAULT PRIVILEGES FOR ROLE PUBLIC
IN SCHEMA mydb.sales
GRANT INSERT ON TABLES TO view_manager;
-- Although `TABLES` refers to tables, views, materialized views, and
-- sources, the `CREATE` privilege will only apply to tables.

```

If `lemon@example.com` now creates a new table `shared_lemon`, the above
default `INSERT` privilege will be granted to `view_manager`.
```mzsql
-- Run as `lemon@example.com`
SET CLUSTER TO compute_cluster;
SET DATABASE TO mydb;
SET SCHEMA TO sales;

CREATE TABLE shared_lemon (id INT);

```

To verify that the default privileges have been automatically granted to others,
you can run `SHOW PRIVILEGES`:

**view_manager:**

Verify the privileges for `view_manager`:
```mzsql
SHOW PRIVILEGES FOR view_manager where name = 'shared_lemon';

```The returned privileges should include the `INSERT` privilege on the
`shared_lemon` table.

```none
      grantor       |   grantee    | database | schema |     name     | object_type | privilege_type
--------------------+--------------+----------+--------+--------------+-------------+----------------
  lemon@example.com | view_manager | mydb     | sales  | shared_lemon | table       | INSERT
```

**blue.berry@example.com:**

Verify the privileges for `blue.berry@example.com`:
```mzsql
SHOW PRIVILEGES FOR "blue.berry@example.com" where name = 'shared_lemon';

```The returned privileges should include the `INSERT` privilege on the
`shared_lemon` table.

```none
      grantor       |   grantee    | database | schema |     name     | object_type | privilege_type
--------------------+--------------+----------+--------+--------------+-------------+----------------
  lemon@example.com | view_manager | mydb     | sales  | shared_lemon | table       | INSERT
```

## Show roles in system

To view the roles in the system, use the [`SHOW ROLES`](/sql/show-roles/) command:

```mzsql
SHOW ROLES [ LIKE <pattern>  | WHERE <condition(s)> ];
```

For example, to show all roles:
```mzsql
SHOW ROLES;

```
The results should list all roles:

```none
         name          | comment
-----------------------+---------
blue.berry@example.com |
data_reader            |
lemon@example.com      |
sales_report_app       |
serving_index_manager  |
view_manager           |
```

## Drop a role

To remove a role from the system, use the [`DROP ROLE`](/sql/drop-role/)
command:

> **Privilege(s) required to run the command:** - `CREATEROLE` privileges on the system. 

```mzsql
DROP ROLE <role>;
```

> **Note:** You cannot drop a role if it contains any members. Before dropping a role,
> revoke the role from all its members. See [Revoke a role](#revoke-a-role-from-another-role).

## Alter role

When granting privileges, the privileges may be scoped to a particular cluster,
database, and schema.

You can use [`ALTER ROLE ... SET`](/sql/alter-role/) to set various
configuration parameters, including cluster, database, and schema.

```mzsql
ALTER ROLE <role> SET <config> =|TO <value>;
```

The following example configures the `blue.berry@example.com` role to use
the `compute_cluster` cluster, `mydb` database, and `sales` schema by
default.
```mzsql
ALTER ROLE "blue.berry@example.com" SET CLUSTER = compute_cluster;
ALTER ROLE "blue.berry@example.com" SET DATABASE = mydb;
ALTER ROLE "blue.berry@example.com" SET search_path = sales; -- i.e., schema

```
- These changes will take effect in the next session for the role; the
  changes have **NO** effect on the current session.

- These configurations are just the defaults. For example, the connection
  string can specify a different database for the session or the user can
  issue a `SET ...` command to override these values for the current
  session.

In Materialize, when you grant a role to another role (user role/service
account role/independent role), the target role inherits only the privileges
of the granted role. **Role configurations are not inherited.** For example,
the following example updates the `data_reader` role to use
`serving_cluster` by default.
```mzsql
ALTER ROLE data_reader SET CLUSTER = serving_cluster;

```
This change affects only the `data_reader` role and does not affect roles
that have been granted `data_reader`, such as `sales_report_app`. That is,
after this change:

- The default cluster for `data_reader` is `serving_cluster` for new
  sessions.

- The default cluster for `sales_report_app` is not affected.

{{< tip >}}
{{% include-headless "/headless/rbac-cloud/alter-role-tip" %}}
{{</ tip >}}

## Change ownership of objects

Certain [commands on an
object](/security/appendix/appendix-command-privileges/) (such as creating
an index on a materialized view or changing owner of an object) require
ownership of the object itself (or *superuser* privileges of an Organization
admin).

In Materialize, when a role creates an object, the role becomes the owner of the
object and is automatically  granted all [applicable
privileges](/security/appendix/appendix-privileges/) for the object. To
transfer ownership (and privileges) to another role (another user role/service
account role/functional role), you can use the [ALTER ... OWNER
TO](/sql/#rbac) commands:

> **Privilege(s) required to run the command:** - Ownership of the object being altered. - Role membership in `new_owner`. - `CREATE` privileges on the containing cluster if the object is a cluster replica. - `CREATE` privileges on the containing database if the object is a schema. - `CREATE` privileges on the containing schema if the object is namespaced by a schema. 

```mzsql
ALTER <object_type> <object_name> OWNER TO <role>;
```

Before changing the ownership, review the privileges of the current owner
(`lemon@example.com`) and the future owner (`view_manage`):

Review `lemon@example.com"`'s privileges on the `shared_lemon` table.
```mzsql
SHOW PRIVILEGES FOR "lemon@example.com" where name = 'shared_lemon';

```
As the owner, `lemon@example.com`  has all applicable privileges
(`INSERT`/`SELECT`/`UPDATE`/`DELETE`) for the table as well as the `INSERT`
through its membership in `view_manager` (from [Alter default privileges
example](/security/cloud/access-control/manage-roles/#alter-default-privileges)).

```none
      grantor      |      grantee      | database | schema |     name     | object_type | privilege_type
-------------------+-------------------+----------+--------+--------------+-------------+----------------
 lemon@example.com | lemon@example.com | mydb     | sales  | shared_lemon | table       | DELETE
 lemon@example.com | lemon@example.com | mydb     | sales  | shared_lemon | table       | INSERT
 lemon@example.com | lemon@example.com | mydb     | sales  | shared_lemon | table       | SELECT
 lemon@example.com | lemon@example.com | mydb     | sales  | shared_lemon | table       | UPDATE
 lemon@example.com | view_manager      | mydb     | sales  | shared_lemon | table       | INSERT
```

Review `view_manager`'s privileges on the `shared_lemon` table.
```mzsql
SHOW PRIVILEGES FOR view_manager where name = 'shared_lemon';

```
The results show that the `view_manager` role has `INSERT` privileges on the
`shared_lemon` table (from [Alter default privileges
example](/security/cloud/access-control/manage-roles/#alter-default-privileges)).

```none
      grantor      |   grantee    | database | schema |     name     | object_type | privilege_type
-------------------+--------------+----------+--------+--------------+-------------+----------------
 lemon@example.com | view_manager | mydb     | sales  | shared_lemon | table       | INSERT
```

Change the owner of the `shared_lemon` table to `view_manager`.
```mzsql
ALTER TABLE mydb.sales.shared_lemon OWNER TO view_manager;

```

After running the command, review `view_manager`'s privileges on the
`shared_lemon` table.
```mzsql
SHOW PRIVILEGES FOR view_manager where name = 'shared_lemon';

```
The results show that the `view_manager` role has all applicable privileges
for a table (`INSERT`, `SELECT`, `UPDATE`, `DELETE`):

```none
  grantor    |   grantee    | database | schema |     name     | object_type | privilege_type
-------------+--------------+----------+--------+--------------+-------------+----------------
view_manager | view_manager | mydb     | sales  | shared_lemon | table       | DELETE
view_manager | view_manager | mydb     | sales  | shared_lemon | table       | INSERT
view_manager | view_manager | mydb     | sales  | shared_lemon | table       | SELECT
view_manager | view_manager | mydb     | sales  | shared_lemon | table       | UPDATE
```

Review `lemon@example.com`'s privileges on the `shared_lemon` table.
```mzsql
SHOW PRIVILEGES FOR "lemon@example.com" where name = 'shared_lemon';

```
The results show that `lemon@example.com` now only has access through
`view_manager`.

```none
   grantor    |   grantee    | database | schema |     name     | object_type | privilege_type
--------------+--------------+----------+--------+--------------+-------------+----------------
 view_manager | view_manager | mydb     | sales  | shared_lemon | table       | DELETE
 view_manager | view_manager | mydb     | sales  | shared_lemon | table       | INSERT
 view_manager | view_manager | mydb     | sales  | shared_lemon | table       | SELECT
 view_manager | view_manager | mydb     | sales  | shared_lemon | table       | UPDATE
```

## See also

- [Access control best practices](/security/cloud/access-control/#best-practices)
- [Manage privileges with
  Terraform](/developer-tools/terraform/manage-rbac/)

<!-- mz-docs page: security/cloud/manage-network-policies -->

# Manage network policies
Manage/configure network policies to restrict access to a Materialize region using IP-based rules.
> **Tip:** We recommend using [Terraform](https://registry.terraform.io/providers/MaterializeInc/materialize/latest/docs/resources/network_policy)
> to configure and manage network policies.

By default, Materialize is available on the public internet without any
network-layer access control. As an **administrator** of a Materialize
organization, you can configure network policies to restrict access to a
Materialize region using IP-based rules.

Network policies are enforced at the database layer and apply to both SQL
(pgwire) and HTTP connections. Because the Materialize Console connects over
HTTP, network policies restrict Console access in addition to SQL access.

## Create a network policy

> **Note:** Network policies are applied **globally** (i.e., at the region level) and rules
> can only be configured for **ingress traffic**.

To create a new network policy, use the [`CREATE NETWORK POLICY`](/sql/create-network-policy)
statement to provide a list of rules for allowed ingress traffic.

```sql
CREATE NETWORK POLICY office_access_policy (
  RULES (
    new_york (action='allow', direction='ingress',address='1.2.3.4/28'),
    minnesota (action='allow',direction='ingress',address='2.3.4.5/32')
  )
);
```

## Alter a network policy

To alter an existing network policy, use the [`ALTER NETWORK POLICY`](/sql/alter-network-policy)
statement. Changes to a network policy will only affect new connections
and **will not** terminate active connections.

```mzsql
ALTER NETWORK POLICY office_access_policy SET (
  RULES (
    new_york (action='allow', direction='ingress',address='1.2.3.4/28'),
    minnesota (action='allow',direction='ingress',address='2.3.4.5/32'),
    boston (action='allow',direction='ingress',address='4.5.6.7/32')
  )
);
```

### Lockout prevention

To prevent lockout, the IP of the active user is validated against the policy
changes requested. This prevents users from modifying network policies in a way
that could lock them out of the system.

## Drop a network policy

To drop an existing network policy, use the [`DROP NETWORK POLICY`](/sql/drop-network-policy) statement.

```mzsql
DROP NETWORK POLICY office_access_policy;
```

To drop the pre-installed `default` network policy (or the network policy
subsequently set as default), you must first set a new system default using
the [`ALTER SYSTEM SET network_policy`](/sql/alter-system-set) statement.

<!-- mz-docs page: security/cloud/users-service-accounts -->

# User and service accounts

Manage users and service accounts.

As an administrator of a Materialize organization, you can manage the users and
apps (via service accounts) that can access your Materialize organization and
resources.

## Organization roles

During creation of a user/service account in Materialize, the account is
assigned an organization role:

| Organization role | Description |
| --- | --- |
| <strong>Organization Admin</strong> | <ul> <li> <p><strong>Console access</strong>: Has access to all Materialize console features, including administrative features (e.g., invite users, create service accounts, manage billing, and organization settings).</p> </li> <li> <p><strong>Database access</strong>: Has <red><strong>superuser</strong></red> privileges in the database.</p> </li> </ul>  |
| <strong>Organization Member</strong> | <ul> <li> <p><strong>Console access</strong>: Has no access to Materialize console administrative features.</p> </li> <li> <p><strong>Database access</strong>: Inherits role-level privileges defined by the <code>PUBLIC</code> role; may also have additional privileges via grants or default privileges. See <a href="/security/cloud/access-control/#roles-and-privileges" >Access control control</a>.</p> </li> </ul>  |

> **Note:** - The first user for an organization is automatically assigned the
>   **Organization Admin** role.
> - An [Organization
> Admin](/security/cloud/users-service-accounts/#organization-roles) has
> <red>**superuser**</red> privileges in the database. Following the principle of
> least privilege, only assign **Organization Admin** role to those users who
> require superuser privileges.
> - Users/service accounts can be granted additional database roles and privileges
>   as needed.

## User accounts

As an **Organization admin**, you can [invite new
users](./invite-users/) via the Materialize Console. When you invite a new user,
Materialize will email the user with an invitation link.

> **Note:** - Until the user accepts the invitation and logs in, the user is listed as
> **Pending Approval**.
> - When the user accepts the invitation, the user can set the user password and
> log in to activate their account. The first time the user logs in, a database
> role with the same name as their e-mail address is created, and the account
> creation is complete.

For instructions on inviting users to your Materialize organization, see [Invite
users](./invite-users/).

## Service accounts

> **Tip:** As a best practice, we recommend you use service accounts to connect external
> applications and services to Materialize.

As an **Organization admin**, you can create a new service account via
the [Materialize Console](/developer-tools/console/) or via
[Terraform](/developer-tools/terraform/).

> **Note:** - The new account creation is not finished until the first time you connect with
> the account.
> - The first time the account connects, a database role with the same name as the
> specified service account **User** is created, and the service account creation is complete.

For instructions on creating a new service account in your Materialize
organization, see [Create service accounts](./create-service-accounts/).

## Single sign-on (SSO)

As an **Organization admin**, you can configure single sign-on (SSO) as
an additional layer of account security using your existing
[SAML](https://auth0.com/blog/how-saml-authentication-works/)- or [OpenID
Connect](https://auth0.com/intro-to-iam/what-is-openid-connect-oidc)-based
identity provider. This ensures that all users can securely log in to the
Materialize Console using the same authentication scheme and credentials across
all systems in your organization.

To configure SSO for your Materialize organization, follow [this step-by-step
guide](./sso/).

## Group sync

As an **Organization admin**, you can provision groups from your identity
provider via SCIM and map them to existing Materialize database roles, so that
database role membership is managed from your identity provider. Roles you
grant manually are not affected by sync.

To configure group sync for your Materialize organization, see [Sync identity
provider groups to database roles](./sync-idp-groups/).

## See also

- [Role-based access control](/security/cloud/access-control/)
- [Manage with dbt](/developer-tools/dbt/)
- [Manage with Terraform](/developer-tools/terraform/)

<!-- mz-docs page: security/cloud/users-service-accounts/create-service-accounts -->

# Create service accounts
Create a new service account (i.e., non-human user) to connect external applications and services to Materialize.
It's a best practice to use service accounts (i.e., non-human users) to connect
external applications and services to Materialize. As an **administrator** of a
Materialize organization, you can create service accounts manually via the
[Materialize Console](#materialize-console) or programatically via
[Terraform](#terraform).

More granular permissions for the service account can then be configured using
[role-based access control (RBAC)](/security/cloud/access-control/).

> **Note:** - The new account creation is not finished until the first time you connect with
> the account.
> - The first time the account connects, a database role with the same name as the
> specified service account **User** is created, and the service account creation is complete.

## Materialize Console

1. [Log in to the Materialize Console](/developer-tools/console/).

1. In the side navigation bar, click **+ Create New** > **App Password**.

1. In the **New app password** modal, specify the type and required field(s):

   | Field | Details |
   | --- | --- |
   | <strong>Type</strong> | Select <strong>Service</strong> |
   | <strong>Name</strong> | Specify a descriptive name. |
   | <strong>User</strong> | Specify a service account user name. If the specified account user does not exist, it will be automatically created the <strong>first time</strong> the application connects with the user name and password. |
   | <strong>Roles</strong> | <p>Select the organization role:</p> <table>   <thead>       <tr>           <th>Organization role</th>           <th>Description</th>       </tr>   </thead>   <tbody>       <tr>           <td><strong>Organization Admin</strong></td>           <td><ul> <li> <p><strong>Console access</strong>: Has access to all Materialize console features, including administrative features (e.g., invite users, create service accounts, manage billing, and organization settings).</p> </li> <li> <p><strong>Database access</strong>: Has <red><strong>superuser</strong></red> privileges in the database.</p> </li> </ul></td>       </tr>       <tr>           <td><strong>Organization Member</strong></td>           <td><ul> <li> <p><strong>Console access</strong>: Has no access to Materialize console administrative features.</p> </li> <li> <p><strong>Database access</strong>: Inherits role-level privileges defined by the <code>PUBLIC</code> role; may also have additional privileges via grants or default privileges. See <a href="/security/cloud/access-control/#roles-and-privileges" >Access control control</a>.</p> </li> </ul></td>       </tr>   </tbody> </table> <blockquote> <p><strong>Note:</strong> - The first user for an organization is automatically assigned the <strong>Organization Admin</strong> role.</p> <ul> <li>An <a href="/security/cloud/users-service-accounts/#organization-roles" >Organization Admin</a> has <red><strong>superuser</strong></red> privileges in the database. Following the principle of least privilege, only assign <strong>Organization Admin</strong> role to those users who require superuser privileges.</li> <li>Users/service accounts can be granted additional database roles and privileges as needed.</li> </ul> </blockquote>  |

1. Click **Create Password** to generate a new password for your service
   account.

1. Store the new password securely.

   > **Note:** Do not reload or navigate away from the screen before storing the
>    password. This information is not displayed again.

1. Connect with the new service account to finish creating the new
   account.

   > **Note:** - The new account creation is not finished until the first time you connect with
>   the account.
> - The first time the account connects, a database role with the same name as the
> specified service account **User** is created, and the service account creation is complete.

   1. Find your new service account in the **App Passwords** table.

   1. Click on the **Connect** button to get details on connecting with the new
      account.

      **psql:**
If you have `psql` installed:

1. Click on the **Terminal** tab.
1. From a terminal, connect using the psql command displayed.
1. When prompted for the password, enter the app's password.

The first time the account connects, a database role with the same name as the
specified service account **User** is created, and the service account creation is complete.

      **Other clients:**
To use a different client to connect,

1. Click on the **External tools** tab to get the connection details.

1. Update the client to use these details and connect.

The first time the account connects, a database role with the same name as the
specified service account **User** is created, and the service account creation is complete.

## Terraform

**Minimum requirements:** `terraform-provider-materialize` v0.8.1+

1. Create a new service user using the [`materialize_role`](https://registry.terraform.io/providers/MaterializeInc/materialize/latest/docs/resources/role)
   resource:

    ```hcl
    resource "materialize_role" "production_dashboard" {
      name   = "svc_production_dashboard"
      region = "aws/us-east-1"
    }
    ```

1. Create a new `service` app password using the [`materialize_app_password`](https://registry.terraform.io/providers/MaterializeInc/materialize/latest/docs/resources/app_password)
   resource, and associate it with the service user created in the previous
   step:

    ```hcl
    resource "materialize_app_password" "production_dashboard" {
      name = "production_dashboard_app_password"
      type = "service"
      user = materialize_role.production_dashboard.name
      roles = ["Member"]
    }
    ```

1. Optionally, associate the new service user with existing roles to grant it
   existing database privileges.

    ```hcl
    resource "materialize_database_grant" "database_usage" {
      role_name     = materialize_role.production_dashboard.name
      privilege     = "USAGE"
      database_name = "production_analytics"
      region        = "aws/us-east-1"
    }
    ```

1. Export the user and password for use in the external application or service.

    ```hcl
    output "production_dashboard_user" {
      value = materialize_role.production_dashboard.name
    }
    output "production_dashboard_password" {
      value = materialize_app_password.production_dashboard.password
    }
    ```

For general guidance on using the Materialize Terraform provider to manage
resources in your region, see the [reference documentation](/developer-tools/terraform/).

## Next steps

The organization role for a user/service account determines the default level of
database access. Once the account creation is complete, you can use [role-based
access control
(RBAC)](/security/cloud/access-control/#role-based-access-control-rbac) to
control access for that account.

<!-- mz-docs page: security/cloud/users-service-accounts/invite-users -->

# Invite users
How to invite new users to a Materialize organization.
> **Note:** - Until the user accepts the invitation and logs in, the user is listed as
> **Pending Approval**.
> - When the user accepts the invitation, the user can set the user password and
> log in to activate their account. The first time the user logs in, a database
> role with the same name as their e-mail address is created, and the account
> creation is complete.

As an **Organization administrator**, you can invite new users via the
Materialize Console.

1. [Log in to the Materialize Console](/developer-tools/console/).

1. Navigate to **Account** > **Account Settings** > **Users**.

1. Click **Invite User** and fill in the user information.

1. In the **Select Role**, select the organization role for the user:

   | Organization role | Description |
   | --- | --- |
   | <strong>Organization Admin</strong> | <ul> <li> <p><strong>Console access</strong>: Has access to all Materialize console features, including administrative features (e.g., invite users, create service accounts, manage billing, and organization settings).</p> </li> <li> <p><strong>Database access</strong>: Has <red><strong>superuser</strong></red> privileges in the database.</p> </li> </ul>  |
   | <strong>Organization Member</strong> | <ul> <li> <p><strong>Console access</strong>: Has no access to Materialize console administrative features.</p> </li> <li> <p><strong>Database access</strong>: Inherits role-level privileges defined by the <code>PUBLIC</code> role; may also have additional privileges via grants or default privileges. See <a href="/security/cloud/access-control/#roles-and-privileges" >Access control control</a>.</p> </li> </ul>  |

   > **Note:** - The first user for an organization is automatically assigned the
   >   **Organization Admin** role.
   > - An [Organization
   > Admin](/security/cloud/users-service-accounts/#organization-roles) has
   > <red>**superuser**</red> privileges in the database. Following the principle of
   > least privilege, only assign **Organization Admin** role to those users who
   > require superuser privileges.
   > - Users/service accounts can be granted additional database roles and privileges
   >   as needed.

1. Click the **Invite** button at the bottom right section of the screen.

   Materialize will email the user with an invitation link.

   > **Note:** - Until the user accepts the invitation and logs in, the user is listed as
   > **Pending Approval**.
   > - When the user accepts the invitation, the user can set the user password and
   > log in to activate their account. The first time the user logs in, a database
   > role with the same name as their e-mail address is created, and the account
   > creation is complete.

## Next steps

The organization role for a user/service account determines the default level of
database access. Once the account creation is complete, you can use [role-based
access control
(RBAC)](/security/cloud/access-control/#role-based-access-control-rbac) to
control access for that account.

<!-- mz-docs page: security/cloud/users-service-accounts/sso -->

# Configure single sign-on (SSO)
Configure single sign-on (SSO) using SAML or Open ID Connect as an additional layer of account security.
As an **administrator** of a Materialize organization, you can configure single
sign-on (SSO) as an additional layer of account security using your existing
[SAML](https://auth0.com/blog/how-saml-authentication-works/)- or
[OpenID Connect](https://auth0.com/intro-to-iam/what-is-openid-connect-oidc)-based
identity provider. This ensures that all users can securely log in to the
Materialize console using the same authentication scheme and credentials across
all systems in your organization.

> **Note:** Single sign-on in Materialize only supports authentication into the Materialize
> console. Permissions within the database are handled separately using
> [role-based access control](/security/cloud/access-control/).

## Before you begin

To make Materialize metadata available to Datadog, you must configure and run the following additional services:

* You must have an existing SAML- or OpenID Connect-based identity provider.
* Only users assigned the `OrganizationAdmin` role can view and modify SSO settings.

## Configure authentication

* [Log in to the Materialize console](/developer-tools/console/).

* Navigate to **Account** > **Account Settings** > **SSO**.

**OpenID Connect:**

* Click **Add New** and choose the `OpenID Connect` connection type.

* Add the issuer URL, client ID, and secret key provided by your identity provider.

**SAML:**

* Click **Add New** and choose the `SAML` connection type.

* Add the SSO endpoint and public certificate provided by your identity provider.

* Optionally, add the SSO domain provided by your identity provider. Click **Proceed**.

* Select the organization role for the user:

  | Organization role | Description |
  | --- | --- |
  | <strong>Organization Admin</strong> | <ul> <li> <p><strong>Console access</strong>: Has access to all Materialize console features, including administrative features (e.g., invite users, create service accounts, manage billing, and organization settings).</p> </li> <li> <p><strong>Database access</strong>: Has <red><strong>superuser</strong></red> privileges in the database.</p> </li> </ul>  |
  | <strong>Organization Member</strong> | <ul> <li> <p><strong>Console access</strong>: Has no access to Materialize console administrative features.</p> </li> <li> <p><strong>Database access</strong>: Inherits role-level privileges defined by the <code>PUBLIC</code> role; may also have additional privileges via grants or default privileges. See <a href="/security/cloud/access-control/#roles-and-privileges" >Access control control</a>.</p> </li> </ul>  |

  > **Note:** - The first user for an organization is automatically assigned the
  >   **Organization Admin** role.
  > - An [Organization
  > Admin](/security/cloud/users-service-accounts/#organization-roles) has
  > <red>**superuser**</red> privileges in the database. Following the principle of
  > least privilege, only assign **Organization Admin** role to those users who
  > require superuser privileges.
  > - Users/service accounts can be granted additional database roles and privileges
  >   as needed.

## Next steps

The organization role for a user/service account determines the default level of
database access. Once the account creation is complete, you can use [role-based
access control
(RBAC)](/security/cloud/access-control/#role-based-access-control-rbac) to
control access for that account.

<!-- mz-docs page: security/cloud/users-service-accounts/sync-idp-groups -->

# Sync identity provider groups to database roles
Provision groups from your identity provider via SCIM and map them to Materialize database roles.
As an **administrator** of a Materialize organization, you can provision groups
from your identity provider (IdP) with [SCIM](https://scim.cloud/), assign those
groups organization roles, and map custom roles to database roles.

The mapping has three layers:

| Layer | Example | Managed in |
|-------|---------|------------|
| IdP group | `analytics-team` | Your identity provider |
| Custom organization role | `analytics_reader` | Materialize Console (**Account Settings** > **Roles**) or Terraform |
| Database role | `analytics_reader` | SQL or Terraform |

SCIM provisions the group and its members. You assign the group a custom
organization role. When a member connects, Materialize reads their organization
role keys from the authentication token (JWT) and reconciles membership in
existing database roles with matching names. The IdP group name can differ from
the database role name.

> **Important:** Create both the custom organization role and the database role. Creating one
> does not create the other. Database privileges come from grants to the database
> role, not from the permissions selected when creating the organization role.

> **Note:** $TODO: Before publishing this setup, verify that `oidc_group_role_sync_enabled`
> is enabled by default for Cloud organizations and confirm the production
> `oidc_group_claim` setting used for database role sync. Confirm how to obtain
> the JWT key for a role created in the Console.

## Before you begin

* Your Materialize organization must have an [SSO
  connection](/security/cloud/users-service-accounts/sso/) configured for your
  identity provider. Group sync builds on SSO, so set that up first. You can
  confirm your connection under **Account** > **Account Settings** > **SSO**.

  ![SSO connections in the Materialize Console](/images/console/console-account-settings-sso.png "SSO connections in the Materialize Console")

* You must have an identity provider that supports SCIM 2.0 provisioning
  (e.g., Okta or Microsoft Entra ID).
* Only users assigned the **Organization Admin** role can manage provisioning,
  groups, and custom organization roles.

## Step 1. Create a SCIM connection

* [Log in to the Materialize Console](/developer-tools/console/).

* Navigate to **Account** > **Account Settings** > **Provisioning**.

* Click **Add Connection**, name the integration, and select your identity
  provider (**Okta**, **Azure**, or **Custom SCIM** for any other SCIM
  2.0-compatible provider).

  ![Setup SCIM connection dialog in the Materialize Console](/images/console/console-account-settings-add-scim.png "Setup SCIM connection dialog in the Materialize Console")

* Follow the in-console guide for your provider. The Console generates a SCIM
  endpoint URL and an API token, which you enter into your identity provider's
  provisioning settings.

Once your identity provider connects successfully, the connection shows as
**Linked**.

![Provisioning connections in the Materialize Console](/images/console/console-account-settings-provisioning.png "Provisioning connections in the Materialize Console")

## Step 2. Choose which groups to sync

Materialize only syncs the groups you explicitly configure your identity
provider to send. Your other IdP groups are not visible to Materialize.

**Okta:**

* In the Okta Admin Console, open the SCIM application you connected in
  [Step 1](#step-1-create-a-scim-connection).

* On the **Assignments** tab, assign the users (or groups) that should be
  provisioned into Materialize.

* On the **Push Groups** tab, click **Push Groups** and select the groups to
  sync, either by name or by rule.

  ![Push Groups tab of the Okta SCIM application](/images/console/okta-push-groups.png "Push Groups tab of the Okta SCIM application")

Once pushed, the groups and their memberships appear in the Materialize
Console under **Account** > **Account Settings** > **Groups**, marked with a
SCIM badge. Manage group names and membership in the IdP. You can edit the
organization roles assigned to a SCIM-provisioned group in Materialize.

**Other providers:**

Configure your identity provider's SCIM provisioning to push the users and
groups that should exist in Materialize. Most providers let you scope
provisioning to specific groups, so only those groups and their members are
synced.

## Steps 3–5. Map groups to database roles {#map-groups-to-database-roles}

Wait until the group appears under **Account** > **Account Settings** >
**Groups**. Multiple groups can grant the same organization role, and one group
can grant multiple roles.

You can assign a built-in role to a SCIM group without creating a custom role:

| Role | JWT key |
|------|---------|
| **Organization Admin** | `MaterializePlatformAdmin` |
| **Organization Member** | `MaterializePlatform` |

Retain **Organization Member** alongside custom roles when users need its
permissions. Assigning **Organization Admin** makes a user a Materialize
superuser, so do not use it to grant limited database access.

Avoid creating database roles named after the built-in JWT keys unless you
intend everyone with the corresponding built-in organization role to inherit
their database privileges. See [Limitations](#limitations) for other reserved
names.

**Console:**

1. Under **Account** > **Account Settings** > **Roles**, create a custom
   organization role for database access, such as `analytics_reader`. Note its
   JWT key. Choose its organization permissions separately from its database
   privileges.

2. Under **Account** > **Account Settings** > **Groups**, edit the synced group
   `analytics-team` and assign it the new organization role. Retain any
   built-in role assignments the group still needs, such as **Organization
   Member**.

3. In each Materialize region where the group needs access, create a database
   role whose name exactly matches the custom organization role's JWT key,
   including case. For a key of `analytics_reader`:

   ```mzsql
   CREATE ROLE analytics_reader;
   ```

   Grant this database role the privileges the group's members need. See
   [Access control (RBAC)](/security/cloud/access-control/) for examples.
   Organization role permissions do not replace database grants.

**Terraform:**

Use version [v0.11.9](https://github.com/MaterializeInc/terraform-provider-materialize/releases/tag/v0.11.9)
or later of the [Materialize Terraform provider](/developer-tools/terraform/)
for custom organization roles and SCIM group-to-role assignments. Provision
IdP-owned groups and membership through your identity provider.

If you manage the SCIM connection with Terraform, create it with
`materialize_scim_config` before applying this configuration. Terraform cannot
wait for an IdP push simply by depending on the SCIM connection resource, so
wait for `analytics-team` to appear in Materialize first.

To assign a built-in role, include `Admin` or `Member` in the `roles` set of
`materialize_scim_group_roles`. These are Terraform's aliases for
**Organization Admin** and **Organization Member**. Do not manage built-in
organization roles with `materialize_organization_role`.

```hcl
resource "materialize_organization_role" "reader" {
  name           = "analytics_reader"
  base_role_name = "Member"
}

resource "materialize_role" "reader" {
  name = materialize_organization_role.reader.key
}

# Grant access to an existing schema; add grants for the objects readers need.
resource "materialize_schema_grant" "reader_usage" {
  role_name     = materialize_role.reader.name
  privilege     = "USAGE"
  database_name = "analytics"
  schema_name   = "reporting"
}

data "materialize_scim_groups" "all" {}

locals {
  analytics_groups = [
    for group in data.materialize_scim_groups.all.groups : group
    if group.name == "analytics-team" && contains(["scim", "scim2"], group.managed_by)
  ]
}

resource "materialize_scim_group_roles" "reader" {
  group_id = try(one(local.analytics_groups).id, "")
  roles    = ["Member", materialize_organization_role.reader.name]

  lifecycle {
    precondition {
      condition     = length(local.analytics_groups) == 1
      error_message = "Wait for exactly one SCIM group named analytics-team to be provisioned, then rerun Terraform."
    }
  }
}
```

The example uses the organization role's exported JWT `key` as the database
role name and copies **Organization Member** permissions as a starting point.
Later changes to the base role are not copied automatically. The schema grant
assumes `analytics.reporting` already exists; add grants for the specific
objects the group needs to access. The group filter accepts `scim` and `scim2`
as SCIM-managed values.

`materialize_scim_group_roles` manages the group's complete set of organization
role assignments. Include every role the group should retain. Do not use
`materialize_scim_group` or `materialize_scim_group_users` to take ownership of
IdP-provisioned groups or their membership.

## Step 6. Verify grants and revocations

Have a dedicated test user in the synced group sign in and open a new database connection,
for example with the [SQL Shell](/developer-tools/console/sql-shell/). On first sign-in,
Materialize creates the user's own database role. The shared database role
`analytics_reader` must already exist.

As an administrator, query the role memberships:

```mzsql
SELECT r.name AS role, m.name AS member, g.name AS grantor
FROM mz_role_members rm
JOIN mz_roles r ON rm.role_id = r.id
JOIN mz_roles m ON rm.member = m.id
JOIN mz_roles g ON rm.grantor = g.id
WHERE r.name = 'analytics_reader'
  AND g.name = 'mz_jwt_sync';
```

The result should include the user's database role as `member` and
`mz_jwt_sync` as `grantor`. To verify revocation:

1. Remove the test user from the IdP group. Under **Account** > **Account
   Settings** > **Groups**, wait until the SCIM group no longer lists the user.
2. Have the user sign out of all active Materialize sessions, then sign back in
   and open a new SQL Shell connection.
3. Rerun the query. The sync-managed grant should disappear unless another
   group or a direct organization role assignment still grants the same custom
   role.

Restore the test user's group membership after verifying revocation.

Grants and revokes performed by sync are recorded in
[`mz_audit_events`](/sql/system-catalog/mz_catalog/#mz_audit_events).

## How sync works

* **Sync happens at connection time.** When a user connects, Materialize
  compares the organization role keys in their JWT against their sync-managed role
  memberships and applies the difference. Materialize makes a best effort to
  apply changes made in the IdP on the user's next connection, but it may take
  several minutes for changes to be reflected. Changes are never applied to a
  session that is already connected.

* **Manual grants are never touched.** Group sync only manages memberships it
  granted itself (grantor `mz_jwt_sync`). A role granted manually with `GRANT`
  is never revoked by sync, even if the user leaves the corresponding group.
  Audit manual grants periodically to avoid users retaining access through
  stale manual grants.

* **Organization roles without a matching database role are skipped.** The
  connection proceeds and Materialize sends the client a `NOTICE` for each
  unmatched role key.

## Limitations

* **Reserved database role names are never mapped.** Organization role keys
  that collide with reserved database role names are skipped during sync.
  Reserved names are:

  * Any name beginning with `mz_`, `pg_`, or `external_`.
  * The `PUBLIC` role.
  * The role-specification keywords `current_user`, `current_role`,
    `session_user`, `user`, and `none`.

  Matching against reserved names is case-insensitive.

* **Built-in organization roles are reserved.** The names **Organization
  Admin** and **Organization Member**, and their keys `MaterializePlatformAdmin`
  and `MaterializePlatform`, belong to roles Materialize creates. You can map
  SCIM groups to these roles, but cannot edit or delete the roles. Create a
  separate custom organization role for database access mappings.
* **Database roles are never created or dropped by sync.** Group sync only
  assigns and unassigns database role membership. A custom organization role
  grants database access only after you
  [create a matching database role](#map-groups-to-database-roles).
* **Changes are not applied in real time.** See [How sync works](#how-sync-works).

## Migrate from direct group-name mapping

Before changing the mapping mechanism for an existing organization:

1. Create a custom organization role for every database role currently supplied
   by group sync. Set its `name` to the existing database role name. Terraform
   uses this name as the JWT key.
2. Assign each synced group its corresponding custom organization roles.
3. Coordinate the switch with Materialize support. The organization must use
   the role claim before the group-name mapping is retired.
4. Verify both grants and revocations using [Step 6](#step-6-verify-grants-and-revocations).

Keep existing database roles and their object grants. Switching to a role claim
without preparing equivalent assignments can revoke sync-managed memberships
when users reconnect.

## See also

- [Audit events](/sql/system-catalog/mz_catalog/#mz_audit_events)
- [Access control (RBAC)](/security/cloud/access-control/)
- [Configure single sign-on (SSO)](/security/cloud/users-service-accounts/sso/)
- [Invite users](/security/cloud/users-service-accounts/invite-users/)
- [Manage with Terraform](/developer-tools/terraform/)

<!-- mz-docs page: security/fine-grained-access-control -->

# Fine-grained access control
Restrict which rows and columns each role can read by combining RBAC, entitlement tables, and security views.
Materialize enforces row-level and column-level access with three pieces it
already gives you: role-based access control, entitlement tables that map roles
to the rows and columns they may read, and views that join the two. Materialize's
privilege model makes those views a real boundary.

> **Note:** - `SELECT` privileges are required only on the directly referenced
>   view/materialized view. `SELECT` privileges are **not** required for the
>   underlying relations referenced in the view/materialized view definition
>   unless those relations themselves are directly referenced in the query.
> - However, the owner of the view/materialized view (including those with
>   **superuser** privileges) must have all required `SELECT` and `USAGE`
>   privileges to run the view definition regardless of who is selecting from the
>   view/materialized view.

Privileges stop at the view you name. A role holding `SELECT` on
`secure.orders` reads `secure.orders`. Reaching the relations underneath
requires privileges on those relations.

> **Warning:** Materialize views have no `security_barrier` equivalent, so the optimizer, not
> the view, decides whether the filter runs before expressions supplied by the
> querying role. An expression whose behavior varies with the row it sees can
> disclose something about rows the filter removes. Where readers can run
> arbitrary SQL, treat the filter as one layer and keep the most sensitive
> columns out of the exposed views.

The result is one view per relation. Onboarding a tenant and widening a profile
are both an `INSERT`.

## Before you start

Confirm privilege checks are active, and know where your login roles come from.

**Cloud:**

Materialize Cloud enforces RBAC at all times.

Adding a [user or service account](/security/cloud/users-service-accounts/)
creates a database role named after the email address or service account user.
Those are your login roles.

**Self-managed:**

Enable RBAC so that privilege checks are enforced:

> **Warning:** If RBAC is not enabled, all users have <red>**superuser**</red> privileges.

By default, role-based access control (RBAC) checks are not enabled (i.e.,
enforced) when using [authentication](/security/self-managed/authentication/#configuring-authentication-type). To
enable RBAC, set the system parameter `enable_rbac_checks` to `'on'` or `True`.
You can enable the parameter in one of the following ways:

- For [local installations using
  Kind/Minikube](/self-managed-deployments/installation/#installation-guides), set `spec.enableRbac:
  true` option when instantiating the Materialize object.

- For [Cloud deployments using Materialize's
  Terraforms](/self-managed-deployments/installation/#installation-guides), set
  `enable_rbac_checks` in the environment CR via the `environmentdExtraArgs`
  flag option.

- After the Materialize instance is running, run the following command as
  `mz_system` user:

  ```mzsql
  ALTER SYSTEM SET enable_rbac_checks = 'on';
  ```

If more than one method is used, the `ALTER SYSTEM` command will take precedence
over the Kubernetes configuration.

To view the current value for `enable_rbac_checks`, run the following `SHOW`
command:

```mzsql
SHOW enable_rbac_checks;
```

> **Important:** If RBAC is not enabled, all users have <red>**superuser**</red> privileges.

Login roles are yours to define. `mz_system` creates them:

To create additional users or service accounts, login as the `mz_system` user,
using the `external_login_password_mz_system` password, and use [`CREATE ROLE
... WITH LOGIN PASSWORD ...`](/sql/create-role):

```mzsql
CREATE ROLE <user> WITH LOGIN PASSWORD '<password>';
```

## The model

```text
Login role  (alice@acme.example)
     │
     └── GRANT ──► tenant role   (acme_tenant)   ──► row entitlements
                   profile role  (orders_billing) ──► column entitlements
                   reader role   (orders_reader)  ──► SELECT on the exposed view

Every role the session inherits is a key into both entitlement tables.
```

Two tables, both keyed on role name:

| Table                          | Answers                               |
| ------------------------------ | ------------------------------------- |
| `security.row_entitlements`    | Which rows may this role read?         |
| `security.column_entitlements` | Which guarded columns may it read?     |

Three schemas keep the layers apart:

| Schema     | Contents                                                     | Who can use it |
| ---------- | ------------------------------------------------------------ | -------------- |
| `internal` | The maintained relations holding every row                    | The owner |
| `security` | The entitlement tables and the views that apply them          | The owner |
| `secure`   | The views tenants select from                                 | Reader roles |

## Build the layers

### Maintain the data once

Keep the expensive work below the filter, so every tenant reads one maintained
collection. `internal.orders` stands in for whatever holds your rows: a source,
a table, or an upstream view.

```mzsql
CREATE SCHEMA internal;

CREATE VIEW internal.enriched_orders AS
    SELECT id, customer_id, status, total, billing_email, created_at,
           date_trunc('day', created_at) AS order_day
    FROM internal.orders;

CREATE INDEX enriched_orders_by_customer
    ON internal.enriched_orders (customer_id);
```

Index the maintained view on the column the entitlement table keys on. That
turns the per-session filter into a lookup.

### Model entitlements as data

One table per dimension, each keyed and indexed on role name.

```mzsql
CREATE SCHEMA security;

CREATE TABLE security.row_entitlements (
    role_name   text,
    customer_id text
);

CREATE INDEX row_entitlements_by_role
    ON security.row_entitlements (role_name);

INSERT INTO security.row_entitlements VALUES
    ('acme_tenant',   'acme'),
    ('globex_tenant', 'globex');

CREATE TABLE security.column_entitlements (
    role_name   text,
    relation    text,
    column_name text
);

CREATE INDEX column_entitlements_by_role
    ON security.column_entitlements (role_name);

INSERT INTO security.column_entitlements VALUES
    ('orders_billing', 'orders', 'billing_email');
```

List only the columns you guard. Everything else is projected for every reader.

### Resolve the session's roles

`current_role()` returns only the role the session connected as. Entitlements
usually name a shared tenant role, so the filter has to follow role membership.
[`mz_session_role_memberships()`](/sql/functions/#mz_session_role_memberships)
returns the name of every role the session's role belongs to, directly or
through other roles, itself included:

```mzsql
CREATE VIEW security.session_roles AS
    SELECT unnest(mz_session_role_memberships()) AS name;
```

> **Note:** `pg_has_role(current_role(), oid, 'USAGE')` over `mz_catalog.mz_roles` yields
> the same set, but `pg_has_role` is implemented on a function that exposes the
> full role graph and is blocked for roles with
> [`restrict_to_user_objects`](/developer-tools/mcp-server/mcp-agent-tools/#restrict-to-user-objects)
> set, such as MCP agent roles. Views built on it cannot be read by those roles.
> `mz_session_role_memberships()` has no such limitation.

For a session connected as `alice@acme.example`, which is a member of
`acme_tenant`, which is a member of `orders_reader`:

```nofmt
      name
----------------
 acme_tenant
 alice@acme.example
 orders_reader
```

An entitlement row can name a tenant role or a login role. The same filter
handles both.

### Filter the rows

Join the maintained relation to the entitlement table and keep the rows whose
role the session inherits. This view carries every column, so it stays in
`security` and is never granted.

```mzsql
CREATE VIEW security.entitled_orders AS
    SELECT o.*
    FROM internal.enriched_orders o
    JOIN security.row_entitlements e ON e.customer_id = o.customer_id
    WHERE e.role_name IN (SELECT name FROM security.session_roles);
```

Entitlement rows, read at query time, decide what comes back.

### Mask the columns

Gather the columns the session is entitled to into one array, then guard each
sensitive column with a membership test. The array is a single-row aggregate, so
the cross join costs one row.

```mzsql
CREATE VIEW security.my_columns AS
    SELECT relation, column_name
    FROM security.column_entitlements
    WHERE role_name IN (SELECT name FROM security.session_roles);

CREATE SCHEMA secure;

CREATE VIEW secure.orders AS
WITH allowed AS (
    SELECT array_agg(column_name) AS cols
    FROM security.my_columns WHERE relation = 'orders'
)
SELECT o.id, o.customer_id, o.status, o.total, o.order_day,
       CASE WHEN 'billing_email' = ANY(a.cols) THEN o.billing_email END
           AS billing_email
FROM security.entitled_orders o CROSS JOIN allowed a;
```

A guarded column returns its value to entitled readers and `NULL` to everyone
else. One view serves every profile.

> **Note:** The guard fails closed. With no matching entitlements `array_agg` returns
> `NULL`, and `'billing_email' = ANY(NULL)` is `NULL`. Prefer `array_agg` over a
> construct that returns an empty set, which a membership test reads as "allow".

### Grant the reader role

One view means one grant. Create a reader role, give it schema `USAGE` and
`SELECT`, and grant it to every tenant role. Column profiles are roles too,
carrying entitlement rows instead of privileges.

```mzsql
CREATE ROLE orders_reader;
GRANT USAGE ON SCHEMA secure TO orders_reader;
GRANT SELECT ON secure.orders TO orders_reader;

CREATE ROLE orders_billing;
```

Grant these roles to tenant roles rather than login roles. A role granted to a
tenant role reaches everyone who inherits it.

## Onboard a tenant

Onboarding is grants and inserts. The views stay as they are.

```mzsql
CREATE ROLE initech_tenant;
GRANT orders_reader TO initech_tenant;

INSERT INTO security.row_entitlements VALUES ('initech_tenant', 'initech');

GRANT initech_tenant TO "carol@initech.example";
```

Widening a profile later needs no DDL. Grant the tenant a column profile:

```mzsql
GRANT orders_billing TO initech_tenant;
```

or entitle that tenant to one more column:

```mzsql
INSERT INTO security.column_entitlements
    VALUES ('initech_tenant', 'orders', 'billing_email');
```

The final `GRANT` assumes the login role exists. Where it comes from depends on
your deployment.

**Cloud:**

The database role already exists. [Inviting a
user](/security/cloud/users-service-accounts/invite-users/) or [creating a
service account](/security/cloud/users-service-accounts/create-service-accounts/)
creates it, so onboarding a person is the `GRANT` above.

> **Tip:** [Sync identity provider
> groups](/security/cloud/users-service-accounts/sync-idp-groups/) to database
> roles and that `GRANT` follows group membership in your IdP.

See [Manage database roles](/security/cloud/access-control/manage-roles/).

**Self-managed:**

Create the login role as `mz_system` before granting it a tenant role:

```mzsql
CREATE ROLE "carol@initech.example" WITH LOGIN PASSWORD '<password>';
```

The name is arbitrary, so pick a convention and hold to it. Under
[OIDC](/security/self-managed/sso/), roles are provisioned from the identity
provider.

See [Manage database
roles](/security/self-managed/access-control/manage-roles/).

Removing access is symmetric. Delete an entitlement row to take away rows or
columns, or [`REVOKE`](/sql/revoke-role/) the role to take away the account.
Both tables and role membership are read on every query, so these changes apply
to sessions that are already open.

## Verify the boundary

Check both dimensions before you rely on the pattern. Two readers query the
same view. `alice@acme.example` inherits `acme_tenant` and `orders_reader`,
while `bob@globex.example` also inherits `orders_billing`:

```mzsql
SELECT * FROM secure.orders ORDER BY id;
```
```nofmt
-- alice@acme.example
 id | customer_id | status  | total |       order_day        | billing_email
----+-------------+---------+-------+------------------------+---------------
  1 | acme        | shipped |   120 | 2026-09-01 00:00:00+00 |
  3 | acme        | open    | 45.25 | 2026-09-03 00:00:00+00 |

-- bob@globex.example
 id | customer_id | status | total |       order_day        |   billing_email
----+-------------+--------+-------+------------------------+-------------------
  2 | globex      | open   |  80.5 | 2026-09-02 00:00:00+00 | ap@globex.example
```

Each reader gets their own rows, and `billing_email` carries a value only for
the reader entitled to it.

## Keep the filter fast

Materialize evaluates `secure.orders` per query and answers it from indexes
maintained underneath, so one view serves every tenant and every profile from
shared state. Keep the maintained work below the filter:

* Index the maintained relation on the entitlement key, as
  `enriched_orders_by_customer` does above.
* Index both entitlement tables on `role_name`.
* Build the indexes on the cluster that serves tenant queries, and grant that
  cluster's `USAGE` to the reader role.

## Considerations

### Role names share one namespace

`security.session_roles` returns every role the session inherits, including the
reader role. An entitlement naming `orders_reader` therefore reaches every
tenant that reads through it. That is how you grant a baseline to everyone, and
how you leak one tenant to everyone, so decide which you mean. Keep tenant
roles, column profiles, and the reader role distinct, and restrict `INSERT` on
both entitlement tables to a controlled process.

### A masked column reads as null

A guarded column returns `NULL` when the reader has no entitlement, and the
column name stays in the result either way. Where that ambiguity matters,
publish a companion boolean built from the same array, or give that audience a
separate view that omits the column.

## See also

* [Access control (Cloud)](/security/cloud/access-control/)
* [Access control (self-managed)](/security/self-managed/access-control/)
* [Appendix: Privileges](/security/appendix/appendix-privileges/)
* [`GRANT PRIVILEGE`](/sql/grant-privilege/)
* [`GRANT ROLE`](/sql/grant-role/)
* [`CREATE VIEW`](/sql/create-view/)

<!-- mz-docs page: security/self-managed -->

# Self-managed

Authentication and authorization in Self-Managed Materialize.

This section covers security for Self-Managed Materialize.

| Guide | Description |
|-------|-------------|
| [Authentication](/security/self-managed/authentication/) | Enable authentication |
| [Single sign-on (SSO)](/security/self-managed/sso/) | Configure OIDC-based single sign-on with an external identity provider |
| [Access control](/security/self-managed/access-control/) | Reference for role-based access management (RBAC) |

See also

- [Appendix: Privileges](/security/appendix/appendix-privileges/)
- [Appendix: Privileges by commands](/security/appendix/appendix-command-privileges/)
- [Appendix: Built-in roles](/security/appendix/appendix-built-in-roles/)

<!-- mz-docs page: security/self-managed/access-control -->

# Access control (Role-based)

How to configure and manage role-based database access control (RBAC) in Materialize.

> **Note:** Initially, only the `mz_system` user (which has superuser/administrator
> privileges) is available to manage roles.

<a name="role-based-access-control-rbac" ></a>

## Role-based access control

In Materialize, role-based access control (RBAC) governs access to objects
through privileges granted to [database
roles](/security/self-managed/access-control/manage-roles/).

## Enabling RBAC

> **Warning:** If RBAC is not enabled, all users have <red>**superuser**</red> privileges.

By default, role-based access control (RBAC) checks are not enabled (i.e.,
enforced) when using [authentication](/security/self-managed/authentication/#configuring-authentication-type). To
enable RBAC, set the system parameter `enable_rbac_checks` to `'on'` or `True`.
You can enable the parameter in one of the following ways:

- For [local installations using
  Kind/Minikube](/self-managed-deployments/installation/#installation-guides), set `spec.enableRbac:
  true` option when instantiating the Materialize object.

- For [Cloud deployments using Materialize's
  Terraforms](/self-managed-deployments/installation/#installation-guides), set
  `enable_rbac_checks` in the environment CR via the `environmentdExtraArgs`
  flag option.

- After the Materialize instance is running, run the following command as
  `mz_system` user:

  ```mzsql
  ALTER SYSTEM SET enable_rbac_checks = 'on';
  ```

If more than one method is used, the `ALTER SYSTEM` command will take precedence
over the Kubernetes configuration.

To view the current value for `enable_rbac_checks`, run the following `SHOW`
command:

```mzsql
SHOW enable_rbac_checks;
```

> **Important:** If RBAC is not enabled, all users have <red>**superuser**</red> privileges.

## Roles and privileges

In Materialize, you can create both:
- Individual user or service account roles; i.e., roles associated with a
  specific user or service account.
- Functional roles, not associated with any single user or service
  account, but typically used to define a set of shared
  privileges that can be granted to other user/service/functional roles.

Initially, only the `mz_system` user is available.

To create additional users or service accounts, login as the `mz_system` user,
using the `external_login_password_mz_system` password, and use [`CREATE ROLE
... WITH LOGIN PASSWORD ...`](/sql/create-role):

```mzsql
CREATE ROLE <user> WITH LOGIN PASSWORD '<password>';
```

> **Note:** If you are using [OIDC authentication (SSO)](/security/self-managed/sso/), user
> roles are **automatically created** when a user first signs in. You do not need
> to manually create roles for OIDC users. See
> [Auto-provisioning roles](/security/self-managed/sso/#auto-provisioning-roles) for
> details.

To create functional roles, login as the `mz_system` user,
using the `external_login_password_mz_system` password, and use [`CREATE ROLE`](/sql/create-role):

```mzsql
CREATE ROLE <role>;
```

### Managing privileges

Once a role is created, you can:

- [Manage its current
  privileges](/security/self-managed/access-control/manage-roles/#manage-current-privileges-for-a-role)
  (i.e., privileges on existing objects):
  - By granting privileges for a role or revoking privileges from a role.
  - By granting other roles to the role or revoking roles from the role.
    *Recommended for user account/service account roles.*
- [Manage its future
  privileges](/security/self-managed/access-control/manage-roles/#manage-future-privileges-for-a-role)
  (i.e., privileges on objects created in the future):
  - By defining default privileges for objects. With default privileges in
   place, a role is automatically granted/revoked privileges as new objects are
   created by **others** (When an object is created, the creator is granted all
   [applicable privileges](/security/appendix/appendix-privileges/) for that
   object automatically).

> **Disambiguation:** - Use `GRANT|REVOKE ...` to modify privileges on **existing** objects. - Use `ALTER DEFAULT PRIVILEGES` to ensure that privileges are automatically granted or revoked when **new objects** of a certain type are created by others. Then, as needed, you can use `GRANT|REVOKE <privilege>` to adjust those privileges. 

### Initial privileges

All roles in Materialize are automatically members of
[`PUBLIC`](/security/appendix/appendix-built-in-roles/#public-role). As
such, every role includes inherited privileges from `PUBLIC`.

By default, the `PUBLIC` role has the following privileges:

**Baseline privileges via PUBLIC role:**

| Privilege | Description | On database object(s) |
| --- | --- | --- |
| <code>USAGE</code> | Permission to use or reference an object. | <ul> <li>All <code>*.public</code> schemas (e.g., <code>materialize.public</code>);</li> <li><code>materialize</code> database; and</li> <li><code>quickstart</code> cluster.</li> </ul>  |

**Default privileges on future objects set up for PUBLIC:**

| Object(s) | Object owner | Default Privilege | Granted to | Description |
| --- | --- | --- | --- | --- |
| <a href="/sql/types/" ><code>TYPE</code></a> | <code>PUBLIC</code> | <code>USAGE</code> | <code>PUBLIC</code> | When a <a href="/sql/types/" >data type</a> is created (regardless of the owner), all roles are granted the <code>USAGE</code> privilege. However, to use a data type, the role must also have <code>USAGE</code> privilege on the schema containing the type. |

Default privileges apply only to objects created after these privileges are
defined. They do not affect objects that were created before the default
privileges were set.

In addition, all roles have:
- `USAGE` on all built-in types and [all system catalog
schemas](/sql/system-catalog/).
- `SELECT` on [system catalog objects](/sql/system-catalog/).
- All [applicable privileges](/security/appendix/appendix-privileges/) for
  an object they create; for example, the creator of a schema gets `CREATE` and
  `USAGE`; the creator of a table gets `SELECT`, `INSERT`, `UPDATE`, and
  `DELETE`.

You can modify the privileges of your organization's `PUBLIC` role as well as
the modify default privileges for `PUBLIC`.

## Privilege inheritance and modular access control

In Materialize, when you grant a role to another role (user role/service account
role/independent role), the target role inherits privileges through the granted
role.

In general, to grant a user or service account privileges, create roles with the
desired privileges and grant these roles to the user or service account role.
Although you can grant privileges directly to the user or service account role,
using separate, reusable roles is recommended for better access management.

With privilege inheritance, you can compose more complex roles by
combining existing roles, enabling modular access control. However:

- Inheritance only applies to role privileges; role attributes and parameters
  are not inherited.
- When you revoke a role from another role (user role/service account
role/independent role), the target role is no longer a member of the revoked
role nor inherits the revoked role's privileges. **However**, privileges are
cumulative: if the target role inherits the same privilege(s) from another role,
the target role still has the privilege(s) through the other role.

## Best practices

### Follow the principle of least privilege

Role-based access control in Materialize should follow the principle of
least privilege. Grant only the minimum access necessary for users and
service accounts to perform their duties.

### Restrict the granting of `CREATEROLE` privilege

{{% include-headless "/headless/rbac-sm/createrole-consideration" %}}

### Use Reusable Roles for Privilege Assignment

{{% include-headless "/headless/rbac-sm/use-resusable-roles" %}}

See also [Manage database roles](/security/self-managed/access-control/manage-roles/).

### Audit for unused roles and privileges.

{{% include-headless "/headless/rbac-sm/audit-remove-roles" %}}

See also [Show roles in
system](/security/self-managed/access-control/manage-roles/#show-roles-in-system)
and [Drop a
role](/security/self-managed/access-control/manage-roles/#drop-a-role) for
more information.

