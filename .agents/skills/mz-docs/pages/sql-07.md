<!-- mz-docs page: sql/reset -->

# RESET
Reset a configuration parameter to its default value.
`RESET` restores the value of a configuration parameter to its default value.
This command is an alternative spelling for [`SET...TO DEFAULT`](../set).

To see the current value of a configuration parameter, use [`SHOW`](../show).

## Syntax

```mzsql
RESET <parameter_name>;
```

Syntax element | Description
---------------|------------
`<parameter_name>` | The configuration parameter's name.

### Key configuration parameters

Name                                        | Default value             |  Description                                                          | Modifiable?
--------------------------------------------|---------------------------|-----------------------------------------------------------------------|--------------
`cluster`                                   | `quickstart`              | The current cluster.                                                  | Yes
`cluster_replica`                           |                           | The target cluster replica for `SELECT` queries.                      | Yes
`database`                                  | `materialize`             | The current database.                                                 | Yes
`search_path`                               | `public`                  | The schema search order for names that are not schema-qualified.      | Yes
`transaction_isolation`                     | `strict serializable`     | The transaction isolation level. For more information, see [Isolation level](/serve-results/isolation-level/). <br/><br/> Accepts values: `serializable`, `strict serializable`

, `bounded staleness <duration>` (for example, `bounded staleness 5s`)

. | Yes

### Other configuration parameters

Name                                        | Default value             |  Description                                                                                                                                                           | Modifiable?
--------------------------------------------|---------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------
`allowed_cluster_replica_sizes`             | *Varies*                  | The allowed sizes when creating a new cluster replica.                                                                                                                 | [Contact support]
`application_name`                          |                           | The application name to be reported in statistics and logs. This parameter is typically set by an application upon connection to Materialize (e.g. `psql`).            | Yes
`auto_route_catalog_queries`                | `true`                    | Boolean flag indicating whether to force queries that depend only on system tables to run on the `mz_catalog_server` cluster for improved performance.                 | Yes
`client_encoding`                           | `UTF8`                    | The client's character set encoding. The only supported value is `UTF-8`.                                                                                              | Yes
`client_min_messages`                       | `notice`                  | The message levels that are sent to the client. <br/><br/> Accepts values: `debug5`, `debug4`, `debug3`, `debug2`, `debug1`, `log`, `notice`, `warning`, `error`. Each level includes all the levels that follow it. | Yes
`datestyle`                                 | `ISO, MDY`                | The display format for date and time values. The only supported value is `ISO, MDY`.                                                                                   | Yes
`default_timestamp_interval`                | `1s`                      | The interval at which timestamps are assigned to data ingested from sources and tables. New sources are created with this value unless overridden by the `TIMESTAMP INTERVAL` option of [`CREATE SOURCE`](/sql/create-source/). Accepts positive [interval](/sql/types/interval/) values (e.g. `'500ms'`, `'1s'`). This setting applies only when creating sources; changing this value does not affect existing sources. For existing sources, see [`ALTER SOURCE`](/sql/alter-source/). | [Contact support]
`emit_introspection_query_notice`           | `true`                    | Whether to print a notice when querying replica introspection relations.                                                                                               | Yes
`emit_timestamp_notice`                     | `false`                   | Boolean flag indicating whether to send a `notice` specifying query timestamps.                                                                                        | Yes
`emit_trace_id_notice`                      | `false`                   | Boolean flag indicating whether to send a `notice` specifying the trace ID, when available.                                                                            | Yes
`enable_rbac_checks`                        | `true`                    | Boolean flag indicating whether to apply RBAC checks before executing statements.                                                                                      | Yes
`enable_session_rbac_checks`                | `false`                   | Boolean flag indicating whether RBAC is enabled for the current session.                                                                                               | No
`extra_float_digits`                        | `1`                       | Adjusts the number of digits displayed for floating-point values.                                                                                                      | Yes
`failpoints`                                |                           | Allows failpoints to be dynamically activated.                                                                                                                         | No
`idle_in_transaction_session_timeout`       | `120s`                    | The maximum allowed duration that a session can sit idle in a transaction before being terminated. If this value is specified without units, it is taken as milliseconds (`ms`). A value of zero disables the timeout. | Yes
`integer_datetimes`                         | `true`                    | Boolean flag indicating whether the server uses 64-bit-integer dates and times.                                                                                        | No
`intervalstyle`                             | `postgres`                | The display format for interval values. The only supported value is `postgres`.                                                                                        | Yes
`is_superuser`                              |                           | Reports whether the current session is a _superuser_ with admin privileges.                                                                                            | No
`max_aws_privatelink_connections`           | `0`                       | The maximum number of AWS PrivateLink connections in the region, across all schemas.                                                                                   | [Contact support]
`max_clusters`                              | `10`                      | The maximum number of clusters in the region                                                                                                                           | [Contact support]
`max_connections`                           | `5000`                    | The maximum number of concurrent connections in the region                                                                                                             | [Contact support]
`max_credit_consumption_rate`               | `1024`                    | The maximum rate of credit consumption in a region. Credits are consumed based on the size of cluster replicas in use.                                                 | [Contact support]
`max_databases`                             | `1000`                    | The maximum number of databases in the region.                                                                                                                         | [Contact support]
`max_identifier_length`                     | `255`                     | The maximum length in bytes of object identifiers.                                                                                                                     | No
`max_kafka_connections`                     | `1000`                    | The maximum number of Kafka connections in the region, across all schemas.                                                                                             | [Contact support]
`max_mysql_connections`                     | `1000`                    | The maximum number of MySQL connections in the region, across all schemas.                                                                                             | [Contact support]
`max_objects_per_schema`                    | `1000`                    | The maximum number of objects in a schema.                                                                                                                             | [Contact support]
`max_postgres_connections`                  | `1000`                    | The maximum number of PostgreSQL connections in the region, across all schemas.                                                                                        | [Contact support]
`max_query_result_size`                     | `1073741824`              | The maximum size in bytes for a single query's result.                                                                                                                 | Yes
`max_replicas_per_cluster`                  | `5`                       | The maximum number of replicas of a single cluster                                                                                                                     | [Contact support]
`max_result_size`                           | `1 GiB`                   | The maximum size in bytes for a single query's result.                                                                                                                 | [Contact support]
`max_roles`                                 | `1000`                    | The maximum number of roles in the region.                                                                                                                             | [Contact support]
`max_schemas_per_database`                  | `1000`                    | The maximum number of schemas in a database.                                                                                                                           | [Contact support]
`max_secrets`                               | `100`                     | The maximum number of secrets in the region, across all schemas.                                                                                                       | [Contact support]
`max_sinks`                                 | `1000`                    | The maximum number of sinks in the region, across all schemas.                                                                                                         | [Contact support]
`max_sources`                               | `25`                      | The maximum number of sources in the region, across all schemas.                                                                                                       | [Contact support]
`max_tables`                                | `200`                     | The maximum number of tables in the region, across all schemas                                                                                                         | [Contact support]
`max_timestamp_interval`                    | `1s`                      | The upper bound for the `TIMESTAMP INTERVAL` option of [`CREATE SOURCE`](/sql/create-source/) and [`ALTER SOURCE`](/sql/alter-source/). Statements that request a timestamp interval larger than this value are rejected. Accepts positive [interval](/sql/types/interval/) values (e.g. `'500ms'`, `'1s'`). | [Contact support]
`min_timestamp_interval`                    | `1s`                      | The lower bound for the `TIMESTAMP INTERVAL` option of [`CREATE SOURCE`](/sql/create-source/) and [`ALTER SOURCE`](/sql/alter-source/). Statements that request a timestamp interval smaller than this value are rejected. Accepts positive [interval](/sql/types/interval/) values (e.g. `'500ms'`, `'1s'`). | [Contact support]
`mz_version`                                | Version-dependent         | Shows the Materialize server version.                                                                                                                                  | No
`network_policy`                            | `default`                 | The default network policy for the region. | Yes
`real_time_recency`                         | `false`                   | Boolean flag indicating whether [real-time recency](/serve-results/isolation-level/#real-time-recency) is enabled for the current session.                               | [Contact support]
`real_time_recency_timeout`                 | `10s`                     | Sets the maximum allowed duration of `SELECT` statements that actively use [real-time recency](/serve-results/isolation-level/#real-time-recency). If this value is specified without units, it is taken as milliseconds (`ms`).                      | Yes
`server_version_num`                        | Version-dependent         | The PostgreSQL compatible server version as an integer.                                                                                                                | No
`server_version`                            | Version-dependent         | The PostgreSQL compatible server version.                                                                                                                              | No
`sql_safe_updates`                          | `false`                   | Boolean flag indicating whether to prohibit SQL statements that may be overly destructive.                                                                             | Yes
`standard_conforming_strings`               | `true`                    | Boolean flag indicating whether ordinary string literals (`'...'`) should treat backslashes literally. The only supported value is `true`.                             | Yes
`statement_timeout`                         | `10s`                     | The maximum allowed duration of the read portion of write operations; i.e., the `SELECT` portion of `INSERT INTO ... (SELECT ...)`; the `WHERE` portion of `UPDATE ... WHERE ...` and `DELETE FROM ... WHERE ...`. If this value is specified without units, it is taken as milliseconds (`ms`). | Yes
`timezone`                                  | `UTC`                     | The time zone for displaying and interpreting timestamps. The only supported value is `UTC`.                                                                           | Yes

[Contact support]: /support

## Examples

### Reset search path

```mzsql
SHOW search_path;

 search_path
-------------
 qck

RESET search_path;

SHOW search_path;

 search_path
-------------
 public
```

## Related pages

- [`SHOW`](../show)
- [`SET`](../set)

<!-- mz-docs page: sql/revoke-privilege -->

# REVOKE PRIVILEGE
`REVOKE` revokes privileges from a database object.
`REVOKE` revokes privileges from a database object. The `PUBLIC` pseudo-role can
be used to indicate that the privileges should be revoked from all roles
(including roles that might not exist yet).

## Syntax

> **Note:** The syntax supports the `ALL [PRIVILEGES]` shorthand to refer to all
> [*applicable* privileges](#applicable-privileges-to-revoke) for the
> object type.
> For PostgreSQL compatibility, you can reference views, materialized views,
> and sources with the `TABLE` keyword. With `ON TABLE`, the `ALL [PRIVILEGES]`
> shorthand expands to the full table privilege set
> (`SELECT, INSERT, UPDATE, DELETE`). This clears every privilege previously
> granted through the same shorthand, including the non-applicable ones that
> have no runtime effect.

**Cluster:**

For specific cluster(s):

```mzsql
REVOKE <USAGE | CREATE | ALL [PRIVILEGES]> [, ... ]
ON CLUSTER <name> [, ...]
FROM <role_name> [, ... ]
;
```

For all clusters:

```mzsql
REVOKE <USAGE | CREATE | ALL [PRIVILEGES]> [, ... ]
ON ALL CLUSTERS
FROM <role_name> [, ... ]
;
```

**Connection:**

For specific connection(s):

```mzsql
REVOKE <USAGE | ALL [PRIVILEGES]>
ON CONNECTION <name> [, ...]
FROM <role_name> [, ... ];
```

For all connections or all connections in specific schema(s) or in database(s):

```mzsql
REVOKE <USAGE | ALL [PRIVILEGES]>
ON ALL CONNECTIONS
 [ IN <SCHEMA | DATABASE> <name> [, <name> ...] ]
FROM <role_name> [, ... ];
```

**Database:**

For specific database(s):

```mzsql
REVOKE <USAGE | CREATE | ALL [PRIVILEGES]> [, ... ]
ON DATABASE <name> [, ...]
FROM <role_name> [, ... ];
```

For all database:

```mzsql
REVOKE <USAGE | CREATE | ALL [PRIVILEGES]> [, ... ]
ON ALL DATABASES
FROM <role_name> [, ... ];
```

**Materialized view/view/source:**

> **Note:** To read from a views or a materialized views, you must have `SELECT` privileges
> on the view/materialized views. That is, having `SELECT` privileges on the
> underlying objects defining the view/materialized view is insufficient.

For specific materialized view(s)/view(s)/source(s):

```mzsql
REVOKE <SELECT | ALL [PRIVILEGES]>
ON <name> [, <name> ...]
FROM <role_name> [, ... ];
```

For PostgreSQL compatibility, the `TABLE` keyword is also accepted. With the
`TABLE` syntax, you can name `INSERT`, `UPDATE`, and `DELETE` explicitly, and
`ALL [PRIVILEGES]` expands to the full table privilege set
(`SELECT, INSERT, UPDATE, DELETE`). This clears every privilege previously
granted through the matching `GRANT ALL ON TABLE` shorthand.

```mzsql
REVOKE <SELECT | INSERT | UPDATE | DELETE | ALL [PRIVILEGES]> [, ...]
ON TABLE <name> [, <name> ...]
FROM <role_name> [, ... ];
```

**Network policy:**

For specific network policies:

```mzsql
REVOKE <USAGE | ALL [PRIVILEGES]>
ON NETWORK POLICY <name> [, ...]
FROM <role_name> [, ... ];
```

For all network policies:

```mzsql
REVOKE <USAGE | ALL [PRIVILEGES]>
ON ALL POLICIES
FROM <role_name> [, ... ];
```

**Schema:**

For specific schema(s):

```mzsql
REVOKE <USAGE | CREATE | ALL [PRIVILEGES]> [, ... ]
ON SCHEMA <name> [, ...]
FROM <role_name> [, ... ];
```

For all schemas or all schemas in a specific database(s):

```mzsql
REVOKE <USAGE | CREATE | ALL [PRIVILEGES]> [, ... ]
ON ALL SCHEMAS [IN DATABASE <name> [, <name> ...]]
FROM <role_name> [, ... ];
```

**Secret:**

For specific secret(s):

```mzsql
REVOKE <USAGE | ALL [PRIVILEGES]> [, ... ]
ON SECRET <name> [, ...]
FROM <role_name> [, ... ];
```

For all secrets or all secrets in a specific database(s):

```mzsql
REVOKE <USAGE | ALL [PRIVILEGES]> [, ... ]
ON ALL SECRET [IN DATABASE <name> [, <name> ...]]
FROM <role_name> [, ... ];
```

**System:**

```mzsql
REVOKE <CREATEROLE | CREATEDB | CREATECLUSTER | CREATENETWORKPOLICY | ALL [PRIVILEGES]> [, ... ]
ON SYSTEM
FROM <role_name> [, ... ];
```

**Type:**

For specific view(s):

```mzsql
REVOKE <USAGE | ALL [PRIVILEGES]>
ON TYPE <name> [, <name> ...]
FROM <role_name> [, ... ];
```

For all types or all types in a specific schema(s) or in a specific database(s):

```mzsql
REVOKE <USAGE | ALL [PRIVILEGES]>
ON ALL TYPES
  [ IN <SCHEMA|DATABASE> <name> [, <name> ...] ]
FROM <role_name> [, ... ];
```

**Table:**

For specific table(s):

```mzsql
REVOKE <SELECT | INSERT | UPDATE | DELETE | ALL [PRIVILEGES]> [, ...]
ON [TABLE] <name> [, <name> ...]
FROM <role_name> [, ... ];
```

For all tables or all tables in a specific schema(s) or in a specific database(s):

> **Note:** Granting privileges via `ALL TABLES [...]` also applies to sources, views, and
> materialized views (for the applicable privileges).

```mzsql
REVOKE <SELECT | INSERT | UPDATE | DELETE | ALL [PRIVILEGES]> [, ...]
ON ALL TABLES
  [ IN <SCHEMA|DATABASE> <name> [, <name> ...] ]
FROM <role_name> [, ... ];
```

## Details

### Applicable privileges to revoke

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

### Privileges

The privileges required to execute this statement are:

- Ownership of affected objects.
- `USAGE` privileges on the containing database if the affected object is a schema.
- `USAGE` privileges on the containing schema if the affected object is namespaced by a schema.
- _superuser_ status if the privilege is a system privilege.

## Examples

```mzsql
REVOKE SELECT ON mv FROM joe, mike;
```

```mzsql
REVOKE USAGE, CREATE ON DATABASE materialize FROM joe;
```

```mzsql
REVOKE ALL ON CLUSTER dev FROM joe;
```

```mzsql
REVOKE CREATEDB ON SYSTEM FROM joe;
```

## Useful views

- [`mz_internal.mz_show_system_privileges`](/sql/system-catalog/mz_internal/#mz_show_system_privileges)
- [`mz_internal.mz_show_my_system_privileges`](/sql/system-catalog/mz_internal/#mz_show_my_system_privileges)
- [`mz_internal.mz_show_cluster_privileges`](/sql/system-catalog/mz_internal/#mz_show_cluster_privileges)
- [`mz_internal.mz_show_my_cluster_privileges`](/sql/system-catalog/mz_internal/#mz_show_my_cluster_privileges)
- [`mz_internal.mz_show_database_privileges`](/sql/system-catalog/mz_internal/#mz_show_database_privileges)
- [`mz_internal.mz_show_my_database_privileges`](/sql/system-catalog/mz_internal/#mz_show_my_database_privileges)
- [`mz_internal.mz_show_schema_privileges`](/sql/system-catalog/mz_internal/#mz_show_schema_privileges)
- [`mz_internal.mz_show_my_schema_privileges`](/sql/system-catalog/mz_internal/#mz_show_my_schema_privileges)
- [`mz_internal.mz_show_object_privileges`](/sql/system-catalog/mz_internal/#mz_show_object_privileges)
- [`mz_internal.mz_show_my_object_privileges`](/sql/system-catalog/mz_internal/#mz_show_my_object_privileges)
- [`mz_internal.mz_show_all_privileges`](/sql/system-catalog/mz_internal/#mz_show_all_privileges)
- [`mz_internal.mz_show_all_my_privileges`](/sql/system-catalog/mz_internal/#mz_show_all_my_privileges)

## Related pages

- [`SHOW PRIVILEGES`](../show-privileges)
- [`CREATE ROLE`](../create-role)
- [`ALTER ROLE`](../alter-role)
- [`DROP ROLE`](../drop-role)
- [`DROP USER`](../drop-user)
- [`GRANT ROLE`](../grant-role)
- [`REVOKE ROLE`](../revoke-role)
- [`ALTER OWNER`](/sql/#rbac)
- [`GRANT PRIVILEGE`](../revoke-privilege)
- [`ALTER DEFAULT PRIVILEGES`](../alter-default-privileges)

<!-- mz-docs page: sql/revoke-role -->

# REVOKE ROLE
`REVOKE` revokes membership of one role from another role.
`REVOKE` revokes membership of a role from the target role.

## Syntax

```mzsql
REVOKE <role_to_remove> [, ...] FROM <target_role> [, ...];
```

Syntax element       | Description
---------------------|------------------
`<role_to_remove>`   | The name of the role to remove from the `<target_role>`.
`<target_role>`      | The name of the role from which the to remove the `<role_to_remove>`.

## Examples

```mzsql
REVOKE data_scientist FROM joe;
```

```mzsql
REVOKE data_scientist FROM joe, mike;
```

## Privileges

The privileges required to execute this statement are:

- `CREATEROLE` privileges on the systems.

## Useful views

- [`mz_internal.mz_show_role_members`](/sql/system-catalog/mz_internal/#mz_show_role_members)
- [`mz_internal.mz_show_my_role_members`](/sql/system-catalog/mz_internal/#mz_show_my_role_members)

## Related pages

- [`SHOW ROLE MEMBERSHIP`](../show-role-membership)
- [`CREATE ROLE`](../create-role)
- [`ALTER ROLE`](../alter-role)
- [`DROP ROLE`](../drop-role)
- [`DROP USER`](../drop-user)
- [`GRANT ROLE`](../grant-role)
- [`GRANT PRIVILEGE`](../grant-privilege)
- [`REVOKE PRIVILEGE`](../revoke-privilege)

<!-- mz-docs page: sql/rollback -->

# ROLLBACK
`ROLLBACK` aborts the current [transaction](/sql/begin/#details) and rolls back
all changes made by the transaction.

## Syntax

```mzsql
ROLLBACK;
```

## Details

Rolls back the current transaction, discarding all changes made by the transaction.

## See also

- [`BEGIN`](/sql/begin)
- [`COMMIT`](/sql/commit)

<!-- mz-docs page: sql/select -->

# SELECT

`SELECT` binds SQL queries to named views or materialized views, and allows to interactively query data maintained in Materialize .

[//]: # "TODO(morsapaes) More than adapting this to the new architecture,
rewrite the page entirely at some point."

The `SELECT` statement is the root of a SQL query, and is used both to bind SQL
queries to named [views](../create-view) or [materialized views](../create-materialized-view),
 and to interactively query data maintained in Materialize. For interactive queries, you should consider creating [indexes](../create-index)
on the underlying relations based on common query patterns.

## Syntax

```mzsql
[WITH <cte_binding> [, ...]]
SELECT [ALL | DISTINCT [ON ( <col_ref> [, ...] )]]
  <target_elem> [, ...]
[FROM <table_expr> [, ...] [<join_expr>]]
[WHERE <expression>]
[GROUP BY <col_ref> [, ...]]
[OPTIONS ( <option> = <val> [, ...] )]
[HAVING <expression>]
[ORDER BY <col_ref> [ASC | DESC] [NULLS FIRST | NULLS LAST] [, ...]]
[LIMIT <expression>]
[OFFSET <integer>]
[{UNION | INTERSECT | EXCEPT} [ALL | DISTINCT] <another_select_stmt>]

```

| Syntax element | Description |
| --- | --- |
| **WITH** `<cte_binding>` [, ...] | Optional. [Common table expressions](#common-table-expressions-ctes) (CTEs) for this query. See [Regular CTEs](#regular-ctes) for details.  |
| **ALL** \| **DISTINCT** [**ON** ( `<col_ref>` [, ...] )] | Optional. Specifies which rows to return:  \| Option \| Description \| \|--------\|-------------\| \| `ALL` \| Return all rows from query (default). \| \| `DISTINCT` \| <a id="select-distinct"></a>Return only distinct values. \| \| `DISTINCT ON ( <col_ref> [, ...] )` \| <a id="select-distinct-on"></a>Return only the first row with a distinct value for `<col_ref>`. If an `ORDER BY` clause is also present, then `DISTINCT ON` will respect that ordering when choosing which row to return for each distinct value. You should start the `ORDER BY` clause with the same `<col_ref>` as the `DISTINCT ON` clause. \|  |
| `<target_elem>` [, ...] | The columns or expressions to return. Can include column names, functions, or expressions.  |
| **FROM** `<table_expr>` [, ...] | The tables you want to read from. These can be table names, other `SELECT` statements, [Common Table Expressions](#common-table-expressions-ctes) (CTEs), or [table function calls](/sql/functions/table-functions).  |
| `<join_expr>` | Optional. A join expression to combine table expressions. For more details, see the [`JOIN` documentation](/sql/select/join/).  |
| **WHERE** `<expression>` | Optional. Filter tuples by `<expression>`.  |
| **GROUP BY** `<col_ref>` [, ...] | Optional. Group aggregations by `<col_ref>`. Column references may be the name of an output column, the ordinal number of an output column, or an arbitrary expression of only input columns.  |
| **OPTIONS** ( `<option>` = `<val>` [, ...] ) | Optional. Specify one or more [query hints](#query-hints). Valid hints:  \| Hint \| Value type \| Description \| \|------\|------------\|-------------\| \| `AGGREGATE INPUT GROUP SIZE` \| `uint8` \| How many rows will have the same group key in an aggregation. Materialize can render `min` and `max` expressions more efficiently with this information. \| \| `DISTINCT ON INPUT GROUP SIZE` \| `uint8` \| How many rows will have the same group key in a `DISTINCT ON` expression. Materialize can render [Top K patterns](/transform-data/idiomatic-materialize-sql/top-k/) based on `DISTINCT ON` more efficiently with this information. \| \| `LIMIT INPUT GROUP SIZE` \| `uint8` \| How many rows will be given as a group to a `LIMIT` restriction. Materialize can render [Top K patterns](/transform-data/idiomatic-materialize-sql/top-k/) based on `LIMIT` more efficiently with this information. \|  |
| **HAVING** `<expression>` | Optional. Filter aggregations by `<expression>`.  |
| **ORDER BY** `<col_ref>` [**ASC** \| **DESC**] [**NULLS FIRST** \| **NULLS LAST**] [, ...] | Optional. Sort results in either `ASC` (default) or `DESC` order. Use the `NULLS FIRST` and `NULLS LAST` options to determine whether nulls appear before or after non-null values in the sort ordering (default: `NULLS LAST` for `ASC`, `NULLS FIRST` for `DESC`). Column references may be the name of an output column, the ordinal number of an output column, or an arbitrary expression of only input columns.  |
| **LIMIT** `<expression>` | Optional. Limit the number of returned results to `<expression>`.  |
| **OFFSET** `<integer>` | Optional. Skip the first `<integer>` number of rows.  |
| **UNION** [**ALL** \| **DISTINCT**] `<another_select_stmt>` | Optional. Records present in `select_stmt` or `another_select_stmt`. `DISTINCT` returns only unique rows from these results (implied default). With `ALL` specified, each record occurs a number of times equal to the sum of the times it occurs in each input statement.  |
| **INTERSECT** [**ALL** \| **DISTINCT**] `<another_select_stmt>` | Optional. Records present in both `select_stmt` and `another_select_stmt`. `DISTINCT` returns only unique rows from these results (implied default). With `ALL` specified, each record occurs a number of times equal to the lesser of the times it occurs in each input statement.  |
| **EXCEPT** [**ALL** \| **DISTINCT**] `<another_select_stmt>` | Optional. Records present in `select_stmt` but not in `another_select_stmt`. `DISTINCT` returns only unique rows from these results (implied default). With `ALL` specified, each record occurs a number of times equal to the times it occurs in `select_stmt` less the times it occurs in `another_select_stmt`, or not at all if the former is greater than latter.  |

### Common table expressions (CTEs)

#### Regular CTEs

```mzsql
WITH <cte_ident> [( <col_ident> [, ...] )] AS ( <select_stmt> )
  [, <cte_ident> [( <col_ident> [, ...] )] AS ( <select_stmt> ) [, ...]]
<select_stmt>

```

| Syntax element | Description |
| --- | --- |
| `<cte_ident>` | The name of the common table expression (CTE).  |
| ( `<col_ident>` [, ...] ) | Optional. Rename the CTE's columns to the list of identifiers. The number of identifiers must match the number of columns returned by the CTE's `select_stmt`.  |
| **AS** ( `<select_stmt>` ) | The `SELECT` statement that defines the CTE. Any `cte_ident` alias can be referenced in subsequent `cte_binding` definitions and in the final `select_stmt`.  |

#### Recursive CTEs

```mzsql
WITH MUTUALLY RECURSIVE
  [((RETURN AT | ERROR AT) RECURSION LIMIT <limit>)]
  <cte_ident> ( <col_ident> <col_type> [, ...] ) AS ( <select_stmt> )
  [, <cte_ident> ( <col_ident> <col_type> [, ...] ) AS ( <select_stmt> ) [, ...]]
<select_stmt>

```

| Syntax element | Description |
| --- | --- |
| **(RETURN AT \| ERROR AT) RECURSION LIMIT** `<limit>` | Optional. Control the recursion behavior:  \| Option \| Description \| \|--------\|-------------\| \| `RETURN AT RECURSION LIMIT <limit>` \| Stop the fixpoint computation after `<limit>` iterations and use the current values computed for each recursive CTE binding in the `select_stmt`. Useful when debugging and validating the correctness of recursive queries. \| \| `ERROR AT RECURSION LIMIT <limit>` \| Stop the fixpoint computation after `<limit>` iterations and fail the query with an error. A good safeguard against accidentally running a non-terminating dataflow in production clusters. \|  |
| `<cte_ident>` ( `<col_ident>` `<col_type>` [, ...] ) | A binding that gives the SQL fragment defined under `select_stmt` a `cte_ident` alias. Unlike regular CTEs, a recursive CTE binding must explicitly state its type as a comma-separated list of (`col_ident` `col_type`) pairs. This alias can be used in the same binding or in all other (preceding and subsequent) bindings in the enclosing recursive CTE block.  |
| **AS** ( `<select_stmt>` ) | The `SELECT` statement that defines the recursive CTE. Any `cte_ident` alias can be referenced in all `recursive_cte_binding` definitions that live under the same block, as well as in the final `select_stmt` for that block.  |

For details and examples, see the [Recursive CTEs](/sql/select/recursive-ctes) page.

## Details

Because Materialize works very differently from a traditional RDBMS, it's
important to understand the implications that certain features of `SELECT` will
have on Materialize.

### Creating materialized views

Creating a [materialized view](/sql/create-materialized-view) generates a persistent dataflow, which has a
different performance profile from performing a `SELECT` in an RDBMS.

A materialized view has resource and latency costs that should
be carefully considered depending on its main usage. Materialize must maintain
the results of the query in durable storage, but often it must also maintain
additional intermediate state.

### Creating indexes

Creating an [index](/sql/create-index) also generates a persistent dataflow. The difference from a materialized view is that the results are maintained in memory rather than on persistent storage. This allows ad hoc queries to perform efficient point-lookups in indexes.

### Ad hoc queries

An ad hoc query (a.k.a. one-off `SELECT`) simply performs the query once and returns the results. Ad hoc queries can either read from an existing index, or they can start an ephemeral dataflow to compute the results.

Performing a `SELECT` on an **indexed** source, view or materialized view is
Materialize's ideal operation. When Materialize receives such a `SELECT` query,
it quickly returns the maintained results from memory.
Materialize also quickly returns results for queries that only filter, project, transform with scalar functions,
and re-order data that is maintained by an index.

Queries that can't simply read out from an index will create an ephemeral dataflow to compute
the results. These dataflows are bound to the active [cluster](/fundamentals/concepts/clusters/),
 which you can change using:

```mzsql
SET cluster = <cluster name>;
```

Materialize will remove the dataflow as soon as it has returned the query results to you.

#### Known limitations

CTEs have the following limitations, which we are working to improve:

- `INSERT`/`UPDATE`/`DELETE` (with `RETURNING`) is not supported inside a CTE.
- SQL99-compliant `WITH RECURSIVE` CTEs are not supported (use the [non-standard flavor](/sql/select/recursive-ctes) instead).

### Query hints

Users can specify query hints to help Materialize optimize queries.

The following query hints are valid within the `OPTIONS` clause.

Hint | Value type | Description
------|------------|------------
`AGGREGATE INPUT GROUP SIZE` | `uint8` | How many rows will have the same group key in an aggregation. Materialize can render `min` and `max` expressions more efficiently with this information.
`DISTINCT ON INPUT GROUP SIZE` | `uint8` | How many rows will have the same group key in a `DISTINCT ON` expression. Materialize can render [Top K patterns](/transform-data/idiomatic-materialize-sql/top-k/) based on `DISTINCT ON` more efficiently with this information. To determine the query hint size, see [`EXPLAIN ANALYZE HINTS`](/sql/explain-analyze/#explain-analyze-hints).
`LIMIT INPUT GROUP SIZE` | `uint8` | How many rows will be given as a group to a `LIMIT` restriction. Materialize can render [Top K patterns](/transform-data/idiomatic-materialize-sql/top-k/) based on `LIMIT` more efficiently with this information.

For examples, see the [Optimization](/transform-data/optimization/#query-hints) page.

### Column references

Within a given `SELECT` statement, we refer to the columns from the tables in
the `FROM` clause as the **input columns**, and columns in the `SELECT` list as
the **output columns**.

Expressions in the `SELECT` list, `WHERE` clause, and `HAVING` clause may refer
only to input columns.

Column references in the `ORDER BY` and `DISTINCT ON` clauses may be the name of
an output column, the ordinal number of an output column, or an arbitrary
expression of only input columns. If an unqualified name refers to both an input
and output column, `ORDER BY` chooses the output column.

Column references in the `GROUP BY` clause may be the name of an output column,
the ordinal number of an output column, or an arbitrary expression of only input
columns. If an unqualified name refers to both an input and output column,
`GROUP BY` chooses the input column.

### Connection pooling

Because Materialize is wire-compatible with PostgreSQL, you can use any
PostgreSQL connection pooler with Materialize. For example in using PgBouncer,
see [Connection Pooling](/serve-results/connection-pooling).

## Examples

### Creating an indexed view

This assumes you've already [created a source](../create-source).

The following query creates a view representing the total of all
purchases made by users per region, and then creates an index on this view.

```mzsql
CREATE VIEW purchases_by_region AS
    SELECT region.id, sum(purchase.total)
    FROM mysql_simple_purchase AS purchase
    JOIN mysql_simple_user AS user ON purchase.user_id = user.id
    JOIN mysql_simple_region AS region ON user.region_id = region.id
    GROUP BY region.id;

CREATE INDEX purchases_by_region_idx ON purchases_by_region(id);
```

In this case, Materialize will create a dataflow to maintain the results of
this query, and that dataflow will live on until the index it's maintaining is
dropped.

### Reading from a view

Assuming you've created the indexed view listed above, named `purchases_by_region`, you can simply read from the index with an ad hoc `SELECT` query:

```mzsql
SELECT * FROM purchases_by_region;
```

In this case, Materialize simply returns the results that the index is maintaining, by reading from memory.

### Ad hoc querying

```mzsql
SELECT region.id, sum(purchase.total)
FROM mysql_simple_purchase AS purchase
JOIN mysql_simple_user AS user ON purchase.user_id = user.id
JOIN mysql_simple_region AS region ON user.region_id = region.id
GROUP BY region.id;
```

In this case, Materialize will spin up a similar dataflow as it did for creating
the above indexed view, but it will tear down the dataflow once it's returned its
results to the client. If you regularly want to view the results of this query,
you may want to create an [index](/sql/create-index) (in memory) and/or a [materialized view](/sql/create-materialized-view) (on persistent storage) for it.

### Using regular CTEs

```mzsql
WITH
  regional_sales (region, total_sales) AS (
    SELECT region, sum(amount)
    FROM orders
    GROUP BY region
  ),
  top_regions AS (
    SELECT region
    FROM regional_sales
    ORDER BY total_sales DESC
    LIMIT 5
  )
SELECT region,
       product,
       SUM(quantity) AS product_units,
       SUM(amount) AS product_sales
FROM orders
WHERE region IN (SELECT region FROM top_regions)
GROUP BY region, product;
```

Both `regional_sales` and `top_regions` are CTEs. You could write a query that
produces the same results by replacing references to the CTE with the query it
names, but the CTEs make the entire query simpler to understand.

With regard to dataflows, this is similar to [ad hoc querying](#ad-hoc-querying)
above: Materialize tears down the created dataflow after returning the results.

## Privileges

The privileges required to execute this statement are:

- `SELECT` privileges on all **directly** referenced relations in the query. If
  the directly referenced relation is a view or materialized view:

  - `SELECT` privileges are required only on the directly referenced
    view/materialized view. `SELECT` privileges are **not** required for the
    underlying relations referenced in the view/materialized view definition
    unless those relations themselves are directly referenced in the query.

  - However, the owner of the view/materialized view (including those with
    **superuser** privileges) must have all required `SELECT` and `USAGE`
    privileges to run the view definition regardless of who is selecting from the
    view/materialized view.

- `USAGE` privileges on the schemas that contain the relations in the query.
- `USAGE` privileges on the active cluster.

## Related pages

- [`CREATE VIEW`](../create-view)
- [`CREATE MATERIALIZED VIEW`](../create-materialized-view)
- [`SHOW FULL VIEWS`](../show-views)

<!-- mz-docs page: sql/select/join -->

# JOIN
`JOIN` lets you combine two or more table expressions.
`JOIN` lets you combine two or more table expressions into a single table
expression.

## Conceptual framework

Much like an RDBMS, Materialize can join together any two table expressions (in
our case, either [sources](/sql/create-source) or [views](/sql/create-view)) into
a single table expression.

Materialize has much broader support for `JOIN` than most streaming platforms,
i.e. we support all types of SQL joins in all of the conditions you would
expect.

## Syntax

```mzsql
<select_pred>
[NATURAL] <join_type> JOIN
  [LATERAL] ( <select_stmt> | <table_func_call> | <table_ref> )
  [USING ( <col_ref> [, ...] ) [AS <join_using_alias>] | ON <expression>]
<select_post>

```

| Syntax element | Description |
| --- | --- |
| `<select_pred>` | The predicating [`SELECT`](/sql/select) clauses you want to use, e.g. `SELECT col_ref FROM table_ref...`. The `<table_ref>` from the `<select_pred>` is the left-hand table.  |
| **NATURAL** | Optional. Join table expressions on all columns with the same names in both tables. This is similar to the `USING` clause naming all identically named columns in both tables.  |
| `<join_type>` | The type of `JOIN` you want to use. Valid join types:  \| Join Type \| Description \| \|-----------\|-------------\| \| `INNER` \| (Default) Return all tuples from both tables where the join condition is valid. \| \| `LEFT` [**OUTER**] \| Return all tuples from the left-hand-side table, and all tuples from the right-hand-side table that match the join condition. Tuples from the left-hand table that are not joined contain `NULL` wherever the right-hand table is referenced. \| \| `RIGHT` [**OUTER**] \| Return all tuples from the right-hand-side table, and all tuples from the left-hand-side table that match the join condition. Tuples from the right-hand table that are not joined contain `NULL` wherever the left-hand table is referenced. \| \| `FULL` [**OUTER**] \| Return all tuples from both tables, joining them together where the join conditions are met. Tuples that are not joined contain `NULL` wherever the other table is referenced. \| \| `CROSS` \| Return the Cartesian product of the two tables, i.e. all combinations of tuples from the left-hand table combined with tuples from the right-hand table. \|  |
| **LATERAL** | Optional. Let the following subquery or table function call refer to columns from join's left-hand side. See [`LATERAL` subqueries](#lateral-subqueries) for details.  |
| ( `<select_stmt>` \| `<table_func_call>` \| `<table_ref>` ) | The table expression you want to join, i.e. the right-hand table. Can be a [`SELECT` statement](/sql/select), a [table function call](/sql/functions/#table-functions), or a table reference.  |
| **USING** ( `<col_ref>` [, ...] ) [**AS** `<join_using_alias>`] | Optional. If the join condition does not require table-level qualification (i.e. joining tables on columns with the same name), the columns to join the tables on. For example, `USING (customer_id)`. The optional `AS` clause provides a table alias for the join columns. The columns will remain referenceable by their original names. For example, given `lhs JOIN rhs USING (c) AS joint`, the column `c` will be referenceable as `lhs.c`, `rhs.c`, and `joint.c`.  |
| **ON** `<expression>` | Optional. The condition on which to join the tables. For example `ON purchase.customer_id = customer.id`.  |
| `<select_post>` | The remaining [`SELECT`](/sql/select) clauses you want to use, e.g. `...WHERE expr GROUP BY col_ref HAVING expr`.  |

**Note**: It's possible to join together table expressions as inner joins without using this clause whatsoever, e.g. `SELECT cols... FROM t1, t2 WHERE t1.x = t2.x GROUP BY cols...`

## Details

Unlike most other streaming platforms, `JOIN`s in Materialize have very few, if
any, restrictions. For example, Materialize:

- Does not require time windows when joining streams.
- Does not require any kind of partitioning.

Instead, `JOIN`s work over the available history of both streams, which
ultimately provides an experience more similar to an RDBMS than other streaming
platforms.

### `LATERAL` subqueries

To permit subqueries on the right-hand side of a `JOIN` to access the columns
defined by the left-hand side, declare the subquery as `LATERAL`. Normally, a
subquery only has access to the columns within its own context.

Table function invocations always have implicit access to the columns defined by
the left-hand side of the join, so declaring them as `LATERAL` is a permitted
no-op.

When a join contains a `LATERAL` cross-reference, the right-hand relation is
recomputed for each row in the left-hand relation, then joined to the
left-hand row according to the usual rules of the selected join type.

> **Warning:** `LATERAL` subqueries can be very expensive to compute. For best results, do not
> materialize a view containing a `LATERAL` subquery without first inspecting the
> plan via the [`EXPLAIN PLAN`](/sql/explain-plan/) statement. In many common patterns
> involving `LATERAL` joins, Materialize can optimize away the join entirely.

As a simple example, the following query uses `LATERAL` to count from 1 to `x`
for all the values of `x` in `xs`.

```mzsql
SELECT * FROM
  (VALUES (1), (3)) xs (x)
  CROSS JOIN LATERAL generate_series(1, x) y;
```
```nofmt
 x | y
---+---
 1 | 1
 3 | 1
 3 | 2
 3 | 3
```

For a real-world example of a `LATERAL` subquery, see the [Top-K by group
idiom](/transform-data/idiomatic-materialize-sql/top-k/).

## Examples

For these examples, we'll use a small data set:

**Employees**

```nofmt
 id |  name
----+--------
  1 | Frank
  2 | Arjun
  3 | Nikhil
  4 | Cuong
```

**Managers**

```nofmt
 id | name  | manages
----+-------+---------
  1 | Arjun |       4
  2 | Cuong |       3
  3 | Frank |
```

In this table:

- `Arjun` and `Frank` do not have managers.
- `Frank` is a manager but has no reports.

### Inner join

Inner joins return all tuples from both tables where the join condition is
valid.

![inner join diagram](/images/join-inner.png)

```mzsql
SELECT
  employees."name" AS employee,
  managers."name" AS manager
FROM employees
INNER JOIN managers ON employees.id = managers.manages;
```
```nofmt
 employee | manager
----------+---------
 Cuong    | Arjun
 Nikhil   | Cuong
```

### Left outer join

Left outer joins (also known as left joins) return all tuples from the
left-hand-side table, and all tuples from the right-hand-side table that match
the join condition. Tuples on from the left-hand table that are not joined with
a tuple from the right-hand table contain `NULL` wherever the right-hand table
is referenced.

![left outer join diagram](/images/join-left-outer.png)

```mzsql
SELECT
  employees."name" AS employee,
  managers."name" AS manager
FROM employees
LEFT OUTER JOIN managers ON employees.id = managers.manages;
```
```nofmt
 employee | manager
----------+---------
 Cuong    | Arjun
 Nikhil   | Cuong
 Arjun    |
 Frank    |
 ```

### Right outer join

Right outer joins (also known as right joins) are simply the right-hand-side
equivalent of left outer joins.

Right outer joins return all tuples from the right-hand-side table, and all
tuples from the left-hand-side table that match the join condition. Tuples on
from the right-hand table that are not joined with a tuple from the left-hand
table contain `NULL` wherever the left-hand table is referenced.

![right outer join diagram](/images/join-right-outer.png)

```mzsql
SELECT
  employees."name" AS employee,
  managers."name" AS manager
FROM employees
RIGHT OUTER JOIN managers ON employees.id = managers.manages;
```
```nofmt
 employee | manager
----------+---------
 Cuong    | Arjun
 Nikhil   | Cuong
          | Frank
 ```

### Full outer join

Full outer joins perform both a left outer join and a right outer join. They
return all tuples from both tables, and join them together where the join
conditions are met.

Tuples that are not joined with the other table contain `NULL` wherever the
other table is referenced.

![full outer join diagram](/images/join-full-outer.png)

```mzsql
SELECT
  employees."name" AS employee,
  managers."name" AS manager
FROM employees
FULL OUTER JOIN managers ON employees.id = managers.manages;
```
```nofmt
 employee | manager
----------+---------
 Cuong    | Arjun
 Nikhil   | Cuong
          | Frank
 Arjun    |
 Frank    |
```

### Cross join

Cross joins return the [Cartesian
product](https://en.wikipedia.org/wiki/Cartesian_product) of the two tables,
i.e. all combinations of tuples from the left-hand table combined with tuples
from the right-hand table.

![cross join diagram](/images/join-cross.png)

Our example dataset doesn't have a meaningful cross-join query, but the above
diagram shows how cross joins form the Cartesian product.

## Related pages

- [`SELECT`](/sql/select)
- [`CREATE VIEW`](/sql/create-view)

<!-- mz-docs page: sql/select/recursive-ctes -->

# Recursive CTEs
Recursive CTEs are used to define recursive queries.
Recursive CTEs operate on the recursively-defined structures like trees or graphs implied from queries over your data.

## Syntax

```mzsql
WITH MUTUALLY RECURSIVE
  [((RETURN AT | ERROR AT) RECURSION LIMIT <limit>)]
  <cte_ident> ( <col_ident> <col_type> [, ...] ) AS ( <select_stmt> )
  [, <cte_ident> ( <col_ident> <col_type> [, ...] ) AS ( <select_stmt> ) [, ...]]
<select_stmt>

```

| Syntax element | Description |
| --- | --- |
| **(RETURN AT \| ERROR AT) RECURSION LIMIT** `<limit>` | Optional. Control the recursion behavior:  \| Option \| Description \| \|--------\|-------------\| \| `RETURN AT RECURSION LIMIT <limit>` \| Stop the fixpoint computation after `<limit>` iterations and use the current values computed for each recursive CTE binding in the `select_stmt`. Useful when debugging and validating the correctness of recursive queries. \| \| `ERROR AT RECURSION LIMIT <limit>` \| Stop the fixpoint computation after `<limit>` iterations and fail the query with an error. A good safeguard against accidentally running a non-terminating dataflow in production clusters. \|  |
| `<cte_ident>` ( `<col_ident>` `<col_type>` [, ...] ) | A binding that gives the SQL fragment defined under `select_stmt` a `cte_ident` alias. Unlike regular CTEs, a recursive CTE binding must explicitly state its type as a comma-separated list of (`col_ident` `col_type`) pairs. This alias can be used in the same binding or in all other (preceding and subsequent) bindings in the enclosing recursive CTE block.  |
| **AS** ( `<select_stmt>` ) | The `SELECT` statement that defines the recursive CTE. Any `cte_ident` alias can be referenced in all `recursive_cte_binding` definitions that live under the same block, as well as in the final `select_stmt` for that block.  |

## Details

Within a recursive CTEs block, any `cte_ident` alias can be referenced in all `recursive_cte_binding` definitions that live under the same block, as well as in the final `select_stmt` for that block.

A `WITH MUTUALLY RECURSIVE` block with a general form

```mzsql
WITH MUTUALLY RECURSIVE
  -- A sequence of bindings, all in scope for all definitions.
  $R_1(...) AS ( $sql_cte_1 ),
  ...
  $R_n(...) AS ( $sql_cte_n )
  -- Compute the result from the final values of all bindings.
  $sql_body
```

is evaluated as if it was performing the following steps:

1. Initially, bind `$R_1, ..., $R_n` to the empty collection.
1. Repeat in a loop:
   1. Update `$R_1` using the current values bound to `$R_1, ..., $R_n` in `$sql_cte_1`.
   1. Update `$R_2` using the current values bound to `$R_1, ..., $R_n` in `$sql_cte_2`. Note that this includes the new value of `$R_1` bound above.
   1. ...
   1. Update `$R_n` using the current values bound to `$R_1, ..., $R_n` in `$sql_cte_n`. Note that this includes the new values of `$R_1, ..., $R_{n-1}` bound above.
1. Exit the loop when one of the following conditions is met:
   1. The values bound to all CTEs have stopped changing.
   1. The optional early exit condition to `RETURN` or `ERROR AT ITERATION $i` was set and we have reached iteration `$i`.

Note that Materialize's ability to [efficiently handle incremental changes to your inputs](https://materialize.com/guides/incremental-computation/) extends across loop iterations.
For each iteration, Materialize performs work resulting only from the input changes for this iteration and feeds back the resulting output changes to the next iteration.
When the set of changes for all bindings becomes empty, the recursive computation stops and the final `select_stmt` is evaluated.

> **Warning:** In the absence of recursive CTEs, every `SELECT` query is guaranteed to compute its result or fail with an error within a finite amount of time.
> However, introducing recursive CTEs complicates the situation as follows:
> 1. The query might not converge (and may never terminate).
>    Non-terminating queries never return a result and can consume a lot of your cluster resources. See [an example](#non-terminating-queries) below.
> 2. A small update to a few (or even one) data points in your input might cascade in big updates in your recursive computation.
>    This most likely will manifest in spikes of the cluster resources allocated to your recursive dataflows.
>    See [an example](#queries-with-update-locality) below.

## Examples

Let's consider a very simple schema consisting of `users` that belong to a
hierarchy of geographical `areas` and exchange `transfers` between each other.
Use the [SQL Shell](/developer-tools/console/) to run the sequence of
commands below.

### Example schema

```mzsql
-- A hierarchy of geographical locations with various levels of granularity.
CREATE TABLE areas(id int not null, parent int, name text);
-- A collection of users.
CREATE TABLE users(id char(1) not null, area_id int not null, name text);
-- A collection of transfers between these users.
CREATE TABLE transfers(src_id char(1), tgt_id char(1), amount numeric, ts timestamp);
```

### Example data

```mzsql
DELETE FROM areas;
DELETE FROM users;
DELETE FROM transfers;

INSERT INTO areas VALUES
  (1, 2    , 'Brooklyn'),
  (2, 3    , 'New York'),
  (3, 7    , 'United States of America'),
  (4, 5    , 'Kreuzberg'),
  (5, 6    , 'Berlin'),
  (6, 7    , 'Germany'),
  (7, null , 'Earth');
INSERT INTO users VALUES
  ('A', 1, 'Alice'),
  ('B', 4, 'Bob'),
  ('C', 2, 'Carol'),
  ('D', 5, 'Dan');
INSERT INTO transfers VALUES
  ('B', 'C', 20.0 , now()),
  ('A', 'D', 15.0 , now() + '05 seconds'),
  ('C', 'D', 25.0 , now() + '10 seconds'),
  ('A', 'B', 10.0 , now() + '15 seconds'),
  ('C', 'A', 35.0 , now() + '20 seconds');
```

### Transitive closure

The following view will compute `connected` as the transitive closure of a graph where:
* each `user` is a graph vertex, and
* a graph edge between users `x` and `y` exists only if a transfer from `x` to `y` was made recently (using the rather small `10 seconds` period here for the sake of illustration):

```mzsql
CREATE MATERIALIZED VIEW connected AS
WITH MUTUALLY RECURSIVE
  connected(src_id char(1), dst_id char(1)) AS (
    SELECT DISTINCT src_id, tgt_id FROM transfers WHERE mz_now() <= ts + interval '10s'
    UNION
    SELECT c1.src_id, c2.dst_id FROM connected c1 JOIN connected c2 ON c1.dst_id = c2.src_id
  )
SELECT src_id, dst_id FROM connected;
```

To see results change over time, you can [`SUBSCRIBE`](/sql/subscribe/) to the
materialized view and then use a different SQL Shell session to insert
some sample data into the base tables used in the view:

```mzsql
SUBSCRIBE(SELECT * FROM connected) WITH (SNAPSHOT = FALSE);
```

You'll see results change as new data is inserted. When you’re done, cancel out
of the `SUBSCRIBE` using **Stop streaming**.

> **Note:** Depending on your base data, the number of records in the `connected` result might get close to the square of the number of `users`.

### Strongly connected components

Another thing that you might be interested in is identifying maximal sub-graphs where every pair of `users` are `connected` (the so-called [_strongly connected components (SCCs)_](https://en.wikipedia.org/wiki/Strongly_connected_component)) of the graph defined above.
This information might be useful to identify clusters of closely-tight users in your application.

Since you already have `connected` defined as a `MATERIALIZED VIEW`, you can piggy-back on that information to derive the SCCs of your graph.
Two `users` will be in the same SCC only if they are `connected` in both directions.
Consequently, given the `connected` contents, we can:

1. Restrict `connected` to the subset of `symmetric` connections that go in both directions.
2. Identify the `scc` of each `users` entry with the lowest `dst_id` of all `symmetric` neighbors and its own `id`.

```mzsql
CREATE MATERIALIZED VIEW strongly_connected_components AS
  WITH
    symmetric(src_id, dst_id) AS (
      SELECT src_id, dst_id FROM connected
      INTERSECT ALL
      SELECT dst_id, src_id FROM connected
    )
  SELECT u.id, least(min(c.dst_id), u.id)
  FROM users u
  LEFT JOIN symmetric c ON(u.id = c.src_id)
  GROUP BY u.id;
```

Again, you can insert some sample data into the base tables and observe how the
materialized view contents change over time using `SUBSCRIBE`:

```mzsql
SUBSCRIBE(SELECT * FROM strongly_connected_components) WITH (SNAPSHOT = FALSE);
```

When you’re done, cancel out of the `SUBSCRIBE` using **Stop streaming**.

> **Note:** The `strongly_connected_components` definition given above is not recursive, but relies on the recursive CTEs from the `connected` definition.
> If you don't need to keep track of the `connected` contents for other reasons, you can use [this alternative SCC definition](https://twitter.com/frankmcsherry/status/1628519795971727366) which computes SCCs directly using repeated forward and backward label propagation.

### Aggregations over a hierarchy

You might want to keep track of the aggregated net balance per area for a recent period of time.
This can be achieved in three steps:

1. Sum up the aggregated net balance for the set period for each user in an `user_balances` CTE.
2. Sum up the `user_balances` of users directly associated with an area in a `direct_balances` CTE.
3. Recursively add to `direct_balances` the `indirect_balances` sum of all child areas.

A materialized view that does the above three steps in three CTEs (of which the last one is recursive) can be defined as follows:

```mzsql
CREATE MATERIALIZED VIEW area_balances AS
  WITH MUTUALLY RECURSIVE
    user_balances(id char(1), balance numeric) AS (
      WITH
        credits AS (
          SELECT src_id as id, sum(amount) credit
          FROM transfers
          WHERE mz_now() <= ts + interval '10s'
          GROUP BY src_id
        ),
        debits AS (
          SELECT tgt_id as id, sum(amount) debit
          FROM transfers
          WHERE mz_now() <= ts + interval '10s'
          GROUP BY tgt_id
        )
      SELECT
        id,
        coalesce(debit, 0) - coalesce(credit, 0) as balance
      FROM
        users
        LEFT JOIN credits USING(id)
        LEFT JOIN debits USING(id)
    ),
    direct_balances(id int, parent int, balance numeric) AS (
      SELECT
        a.id as id,
        a.parent as parent,
        coalesce(sum(ub.balance), 0) as balance
      FROM
        areas a
        LEFT JOIN users u ON (a.id = u.area_id)
        LEFT JOIN user_balances ub ON (u.id = ub.id)
      GROUP BY
        a.id, a.parent
    ),
    indirect_balances(id int, parent int, balance numeric) AS (
      SELECT
        db.id as id,
        db.parent as parent,
        db.balance + coalesce(sum(ib.balance), 0) as balance
      FROM
        direct_balances db
        LEFT JOIN indirect_balances ib ON (db.id = ib.parent)
      GROUP BY
        db.id, db.parent, db.balance
    )
  SELECT
    id, balance
  FROM
    indirect_balances;
```

As before, you can insert [the example data](#example-data) and observe how the materialized view contents change over time from the `psql` with the `\watch` command:

```mzsql
SELECT id, name, balance FROM area_balances JOIN areas USING(id) ORDER BY id;
\watch 1
```

### Non-terminating queries

Let's look at a slight variation of the [transitive closure example](#transitive-closure) from above with the following changes:

1. All `UNION` operators are replaced with `UNION ALL`.
2. The `mz_now() < ts + $period` predicate from the first `UNION` branch is omitted.
3. The `WITH MUTUALLY RECURSIVE` clause has an optional `ERROR AT RECURSION LIMIT 100`.
4. The final result in this example is ordered by `src_id, dst_id`.

```mzsql
WITH MUTUALLY RECURSIVE (ERROR AT RECURSION LIMIT 100)
  connected(src_id char(1), dst_id char(1)) AS (
    SELECT DISTINCT src_id, tgt_id FROM transfers
    UNION ALL
    SELECT src_id, dst_id FROM connected
    UNION ALL
    SELECT c1.src_id, c2.dst_id FROM connected c1 JOIN connected c2 ON c1.dst_id = c2.src_id
  )
SELECT src_id, dst_id FROM connected ORDER BY src_id, dst_id;
```

After inserting [the example data](#example-data) you can observe that executing the above statement returns the following error:

```text
ERROR:  Evaluation error: Recursive query exceeded the recursion limit 100. (Use RETURN AT RECURSION LIMIT to not error, but return the current state as the final result when reaching the limit.)
```

The recursive CTE `connected` has not converged to a fixpoint within the first 100 iterations!
To see why, you can run variants of the same query where the

```mzsql
ERROR AT RECURSION LIMIT 100
```

clause is replaced by

```mzsql
RETURN AT RECURSION LIMIT $n -- where $n = 1, 2, 3, ...
```

and observe how the result changes after `$n` iterations.

**After 1 iteration:**
```text
 src_id | dst_id
--------+--------
 A      | B
 ...
```

**After 2 iterations:**
```text
 src_id | dst_id
--------+--------
 A      | B
 A      | B
 ...
```

**After 3 iterations:**
```text
 src_id | dst_id
--------+--------
 A      | B
 A      | B
 A      | B
 ...
```

Changing the `UNION` to `UNION ALL` in the `connected` definition caused a full copy of `transfer` to be added to the current value of `connected` in each iteration!
Consequently, `connected` never stops growing and the recursive CTE computation never reaches a fixpoint.

### Queries with "update locality"

The examples presented so far have the following "update locality" property:

> **Note:** A change in a source collection will usually cause a _bounded amount_ of changes to the contents of the recursive CTE bindings derived after each iteration.

For example:

- Most of the time, inserting or removing `transfers` will not change the contents of the `connected` collection. This is true because:
  - An alternative path from `x` to `y` already existed before the insertion, or
  - An alternative path from `x` to `y` will exist after the removal.
- Inserting or removing `transfers` will not change most of the contents of the `area_balances` collection. This is true because:
  - Areas are organized in a hierarchy with a maximum height `h`.
  - A single transfer contributes directly only to the `area_balances` of the areas where the `src_id` and `tgt_id` belong.
  - A single transfer contributes indirectly only to the `area_balances` of the areas ancestor areas of the above two areas.
  - Consequently, each `transfer` change will affect at most `2` areas in each iteration and at most `2*h` areas in total.

However, note that not all iterative algorithms have this property. For example:

- In a naive PageRank implementation, the introduction of a link between two pages `x` and `y` will change the PageRank of these two pages and every page `z` transitively connected to either `x` or `y`.
  Since most graphs exhibit [small-world properties](https://en.wikipedia.org/wiki/Small-world_network), this might represent most of the existing pages.
- In a [naive k-means clustering algorithm](https://en.wikipedia.org/wiki/K-means_clustering), inserting or removing a new data point will affect the positions of the `k` mean points after each iteration.

Depending on the size and update frequency of your input collections, expressing algorithms that violate the "update locality" property (such as the examples above) using recursive CTEs in Materialize might lead to excessive CPU and memory consumption in the clusters that compute these recursive queries.

## Related pages

- [Regular CTEs](/sql/select/#regular-ctes)
- [`SELECT`](/sql/select)

<!-- mz-docs page: sql/set -->

# SET
Modify the value of a configuration parameter in the current session.
`SET` modifies the value of a configuration parameter for the current session.
By default, values are set for the duration of the current session.

To see the current value of a configuration parameter, use [`SHOW`](../show).

## Syntax

```mzsql
SET [SESSION|LOCAL] <config> TO|= <value|DEFAULT>;
```

Syntax element                | Description
------------------------------|------------
**SESSION**               | Optional. Set the value for the duration of the current session. **_(Default)_**
**LOCAL**                 | Optional. If specified, set the value for the duration of a single transaction.
`<config>`                | The name of the configuration parameter to modify.
`<value>`                 | The value to assign to the parameter.
**DEFAULT**               | Use the parameter's default value. Equivalent to [`RESET`](../reset).

### Key configuration parameters

Name                                        | Default value             |  Description                                                          | Modifiable?
--------------------------------------------|---------------------------|-----------------------------------------------------------------------|--------------
`cluster`                                   | `quickstart`              | The current cluster.                                                  | Yes
`cluster_replica`                           |                           | The target cluster replica for `SELECT` queries.                      | Yes
`database`                                  | `materialize`             | The current database.                                                 | Yes
`search_path`                               | `public`                  | The schema search order for names that are not schema-qualified.      | Yes
`transaction_isolation`                     | `strict serializable`     | The transaction isolation level. For more information, see [Isolation level](/serve-results/isolation-level/). <br/><br/> Accepts values: `serializable`, `strict serializable`

, `bounded staleness <duration>` (for example, `bounded staleness 5s`)

. | Yes

### Other configuration parameters

Name                                        | Default value             |  Description                                                                                                                                                           | Modifiable?
--------------------------------------------|---------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------
`allowed_cluster_replica_sizes`             | *Varies*                  | The allowed sizes when creating a new cluster replica.                                                                                                                 | [Contact support]
`application_name`                          |                           | The application name to be reported in statistics and logs. This parameter is typically set by an application upon connection to Materialize (e.g. `psql`).            | Yes
`auto_route_catalog_queries`                | `true`                    | Boolean flag indicating whether to force queries that depend only on system tables to run on the `mz_catalog_server` cluster for improved performance.                 | Yes
`client_encoding`                           | `UTF8`                    | The client's character set encoding. The only supported value is `UTF-8`.                                                                                              | Yes
`client_min_messages`                       | `notice`                  | The message levels that are sent to the client. <br/><br/> Accepts values: `debug5`, `debug4`, `debug3`, `debug2`, `debug1`, `log`, `notice`, `warning`, `error`. Each level includes all the levels that follow it. | Yes
`datestyle`                                 | `ISO, MDY`                | The display format for date and time values. The only supported value is `ISO, MDY`.                                                                                   | Yes
`default_timestamp_interval`                | `1s`                      | The interval at which timestamps are assigned to data ingested from sources and tables. New sources are created with this value unless overridden by the `TIMESTAMP INTERVAL` option of [`CREATE SOURCE`](/sql/create-source/). Accepts positive [interval](/sql/types/interval/) values (e.g. `'500ms'`, `'1s'`). This setting applies only when creating sources; changing this value does not affect existing sources. For existing sources, see [`ALTER SOURCE`](/sql/alter-source/). | [Contact support]
`emit_introspection_query_notice`           | `true`                    | Whether to print a notice when querying replica introspection relations.                                                                                               | Yes
`emit_timestamp_notice`                     | `false`                   | Boolean flag indicating whether to send a `notice` specifying query timestamps.                                                                                        | Yes
`emit_trace_id_notice`                      | `false`                   | Boolean flag indicating whether to send a `notice` specifying the trace ID, when available.                                                                            | Yes
`enable_rbac_checks`                        | `true`                    | Boolean flag indicating whether to apply RBAC checks before executing statements.                                                                                      | Yes
`enable_session_rbac_checks`                | `false`                   | Boolean flag indicating whether RBAC is enabled for the current session.                                                                                               | No
`extra_float_digits`                        | `1`                       | Adjusts the number of digits displayed for floating-point values.                                                                                                      | Yes
`failpoints`                                |                           | Allows failpoints to be dynamically activated.                                                                                                                         | No
`idle_in_transaction_session_timeout`       | `120s`                    | The maximum allowed duration that a session can sit idle in a transaction before being terminated. If this value is specified without units, it is taken as milliseconds (`ms`). A value of zero disables the timeout. | Yes
`integer_datetimes`                         | `true`                    | Boolean flag indicating whether the server uses 64-bit-integer dates and times.                                                                                        | No
`intervalstyle`                             | `postgres`                | The display format for interval values. The only supported value is `postgres`.                                                                                        | Yes
`is_superuser`                              |                           | Reports whether the current session is a _superuser_ with admin privileges.                                                                                            | No
`max_aws_privatelink_connections`           | `0`                       | The maximum number of AWS PrivateLink connections in the region, across all schemas.                                                                                   | [Contact support]
`max_clusters`                              | `10`                      | The maximum number of clusters in the region                                                                                                                           | [Contact support]
`max_connections`                           | `5000`                    | The maximum number of concurrent connections in the region                                                                                                             | [Contact support]
`max_credit_consumption_rate`               | `1024`                    | The maximum rate of credit consumption in a region. Credits are consumed based on the size of cluster replicas in use.                                                 | [Contact support]
`max_databases`                             | `1000`                    | The maximum number of databases in the region.                                                                                                                         | [Contact support]
`max_identifier_length`                     | `255`                     | The maximum length in bytes of object identifiers.                                                                                                                     | No
`max_kafka_connections`                     | `1000`                    | The maximum number of Kafka connections in the region, across all schemas.                                                                                             | [Contact support]
`max_mysql_connections`                     | `1000`                    | The maximum number of MySQL connections in the region, across all schemas.                                                                                             | [Contact support]
`max_objects_per_schema`                    | `1000`                    | The maximum number of objects in a schema.                                                                                                                             | [Contact support]
`max_postgres_connections`                  | `1000`                    | The maximum number of PostgreSQL connections in the region, across all schemas.                                                                                        | [Contact support]
`max_query_result_size`                     | `1073741824`              | The maximum size in bytes for a single query's result.                                                                                                                 | Yes
`max_replicas_per_cluster`                  | `5`                       | The maximum number of replicas of a single cluster                                                                                                                     | [Contact support]
`max_result_size`                           | `1 GiB`                   | The maximum size in bytes for a single query's result.                                                                                                                 | [Contact support]
`max_roles`                                 | `1000`                    | The maximum number of roles in the region.                                                                                                                             | [Contact support]
`max_schemas_per_database`                  | `1000`                    | The maximum number of schemas in a database.                                                                                                                           | [Contact support]
`max_secrets`                               | `100`                     | The maximum number of secrets in the region, across all schemas.                                                                                                       | [Contact support]
`max_sinks`                                 | `1000`                    | The maximum number of sinks in the region, across all schemas.                                                                                                         | [Contact support]
`max_sources`                               | `25`                      | The maximum number of sources in the region, across all schemas.                                                                                                       | [Contact support]
`max_tables`                                | `200`                     | The maximum number of tables in the region, across all schemas                                                                                                         | [Contact support]
`max_timestamp_interval`                    | `1s`                      | The upper bound for the `TIMESTAMP INTERVAL` option of [`CREATE SOURCE`](/sql/create-source/) and [`ALTER SOURCE`](/sql/alter-source/). Statements that request a timestamp interval larger than this value are rejected. Accepts positive [interval](/sql/types/interval/) values (e.g. `'500ms'`, `'1s'`). | [Contact support]
`min_timestamp_interval`                    | `1s`                      | The lower bound for the `TIMESTAMP INTERVAL` option of [`CREATE SOURCE`](/sql/create-source/) and [`ALTER SOURCE`](/sql/alter-source/). Statements that request a timestamp interval smaller than this value are rejected. Accepts positive [interval](/sql/types/interval/) values (e.g. `'500ms'`, `'1s'`). | [Contact support]
`mz_version`                                | Version-dependent         | Shows the Materialize server version.                                                                                                                                  | No
`network_policy`                            | `default`                 | The default network policy for the region. | Yes
`real_time_recency`                         | `false`                   | Boolean flag indicating whether [real-time recency](/serve-results/isolation-level/#real-time-recency) is enabled for the current session.                               | [Contact support]
`real_time_recency_timeout`                 | `10s`                     | Sets the maximum allowed duration of `SELECT` statements that actively use [real-time recency](/serve-results/isolation-level/#real-time-recency). If this value is specified without units, it is taken as milliseconds (`ms`).                      | Yes
`server_version_num`                        | Version-dependent         | The PostgreSQL compatible server version as an integer.                                                                                                                | No
`server_version`                            | Version-dependent         | The PostgreSQL compatible server version.                                                                                                                              | No
`sql_safe_updates`                          | `false`                   | Boolean flag indicating whether to prohibit SQL statements that may be overly destructive.                                                                             | Yes
`standard_conforming_strings`               | `true`                    | Boolean flag indicating whether ordinary string literals (`'...'`) should treat backslashes literally. The only supported value is `true`.                             | Yes
`statement_timeout`                         | `10s`                     | The maximum allowed duration of the read portion of write operations; i.e., the `SELECT` portion of `INSERT INTO ... (SELECT ...)`; the `WHERE` portion of `UPDATE ... WHERE ...` and `DELETE FROM ... WHERE ...`. If this value is specified without units, it is taken as milliseconds (`ms`). | Yes
`timezone`                                  | `UTC`                     | The time zone for displaying and interpreting timestamps. The only supported value is `UTC`.                                                                           | Yes

[Contact support]: /support

### Aliased configuration parameters

There are a few configuration parameters that act as aliases for other
configuration parameters.

- `schema`: `schema` is an alias for `search_path`. Only one schema can be specified using this syntax. The `TO` and `=` syntax are optional.
- `names`: `names` is an alias for `client_encoding`. The `TO` and `=` syntax must be omitted.
- `time zone`: `time zone` is an alias for `timezone`. The `TO` and `=` syntax must be omitted.

## Examples

### Set active cluster

```mzsql
SHOW cluster;

 cluster
---------
 default

SET cluster = 'quickstart';

SHOW cluster;

  cluster
------------
 quickstart
```

### Set transaction isolation level

```mzsql
SET transaction_isolation = 'serializable';
```

### Set search path

```mzsql
SET search_path = public, qck;
```

```mzsql
SET schema = qck;
```

## Related pages

- [`RESET`](../reset)
- [`SHOW`](../show)

<!-- mz-docs page: sql/show -->

# SHOW
Display the value of a configuration parameter.
`SHOW` displays the value of either a specified configuration parameter or all
configuration parameters.

## Syntax

```sql
SHOW [ <name> | ALL ];
```

### Aliased configuration parameters

There are a few configuration parameters that act as aliases for other
configuration parameters.

- `schema`: an alias for showing the first resolvable schema in `search_path`
- `time zone`: an alias for `timezone`

### Key configuration parameters

Name                                        | Default value             |  Description                                                          | Modifiable?
--------------------------------------------|---------------------------|-----------------------------------------------------------------------|--------------
`cluster`                                   | `quickstart`              | The current cluster.                                                  | Yes
`cluster_replica`                           |                           | The target cluster replica for `SELECT` queries.                      | Yes
`database`                                  | `materialize`             | The current database.                                                 | Yes
`search_path`                               | `public`                  | The schema search order for names that are not schema-qualified.      | Yes
`transaction_isolation`                     | `strict serializable`     | The transaction isolation level. For more information, see [Isolation level](/serve-results/isolation-level/). <br/><br/> Accepts values: `serializable`, `strict serializable`

, `bounded staleness <duration>` (for example, `bounded staleness 5s`)

. | Yes

### Other configuration parameters

Name                                        | Default value             |  Description                                                                                                                                                           | Modifiable?
--------------------------------------------|---------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------
`allowed_cluster_replica_sizes`             | *Varies*                  | The allowed sizes when creating a new cluster replica.                                                                                                                 | [Contact support]
`application_name`                          |                           | The application name to be reported in statistics and logs. This parameter is typically set by an application upon connection to Materialize (e.g. `psql`).            | Yes
`auto_route_catalog_queries`                | `true`                    | Boolean flag indicating whether to force queries that depend only on system tables to run on the `mz_catalog_server` cluster for improved performance.                 | Yes
`client_encoding`                           | `UTF8`                    | The client's character set encoding. The only supported value is `UTF-8`.                                                                                              | Yes
`client_min_messages`                       | `notice`                  | The message levels that are sent to the client. <br/><br/> Accepts values: `debug5`, `debug4`, `debug3`, `debug2`, `debug1`, `log`, `notice`, `warning`, `error`. Each level includes all the levels that follow it. | Yes
`datestyle`                                 | `ISO, MDY`                | The display format for date and time values. The only supported value is `ISO, MDY`.                                                                                   | Yes
`default_timestamp_interval`                | `1s`                      | The interval at which timestamps are assigned to data ingested from sources and tables. New sources are created with this value unless overridden by the `TIMESTAMP INTERVAL` option of [`CREATE SOURCE`](/sql/create-source/). Accepts positive [interval](/sql/types/interval/) values (e.g. `'500ms'`, `'1s'`). This setting applies only when creating sources; changing this value does not affect existing sources. For existing sources, see [`ALTER SOURCE`](/sql/alter-source/). | [Contact support]
`emit_introspection_query_notice`           | `true`                    | Whether to print a notice when querying replica introspection relations.                                                                                               | Yes
`emit_timestamp_notice`                     | `false`                   | Boolean flag indicating whether to send a `notice` specifying query timestamps.                                                                                        | Yes
`emit_trace_id_notice`                      | `false`                   | Boolean flag indicating whether to send a `notice` specifying the trace ID, when available.                                                                            | Yes
`enable_rbac_checks`                        | `true`                    | Boolean flag indicating whether to apply RBAC checks before executing statements.                                                                                      | Yes
`enable_session_rbac_checks`                | `false`                   | Boolean flag indicating whether RBAC is enabled for the current session.                                                                                               | No
`extra_float_digits`                        | `1`                       | Adjusts the number of digits displayed for floating-point values.                                                                                                      | Yes
`failpoints`                                |                           | Allows failpoints to be dynamically activated.                                                                                                                         | No
`idle_in_transaction_session_timeout`       | `120s`                    | The maximum allowed duration that a session can sit idle in a transaction before being terminated. If this value is specified without units, it is taken as milliseconds (`ms`). A value of zero disables the timeout. | Yes
`integer_datetimes`                         | `true`                    | Boolean flag indicating whether the server uses 64-bit-integer dates and times.                                                                                        | No
`intervalstyle`                             | `postgres`                | The display format for interval values. The only supported value is `postgres`.                                                                                        | Yes
`is_superuser`                              |                           | Reports whether the current session is a _superuser_ with admin privileges.                                                                                            | No
`max_aws_privatelink_connections`           | `0`                       | The maximum number of AWS PrivateLink connections in the region, across all schemas.                                                                                   | [Contact support]
`max_clusters`                              | `10`                      | The maximum number of clusters in the region                                                                                                                           | [Contact support]
`max_connections`                           | `5000`                    | The maximum number of concurrent connections in the region                                                                                                             | [Contact support]
`max_credit_consumption_rate`               | `1024`                    | The maximum rate of credit consumption in a region. Credits are consumed based on the size of cluster replicas in use.                                                 | [Contact support]
`max_databases`                             | `1000`                    | The maximum number of databases in the region.                                                                                                                         | [Contact support]
`max_identifier_length`                     | `255`                     | The maximum length in bytes of object identifiers.                                                                                                                     | No
`max_kafka_connections`                     | `1000`                    | The maximum number of Kafka connections in the region, across all schemas.                                                                                             | [Contact support]
`max_mysql_connections`                     | `1000`                    | The maximum number of MySQL connections in the region, across all schemas.                                                                                             | [Contact support]
`max_objects_per_schema`                    | `1000`                    | The maximum number of objects in a schema.                                                                                                                             | [Contact support]
`max_postgres_connections`                  | `1000`                    | The maximum number of PostgreSQL connections in the region, across all schemas.                                                                                        | [Contact support]
`max_query_result_size`                     | `1073741824`              | The maximum size in bytes for a single query's result.                                                                                                                 | Yes
`max_replicas_per_cluster`                  | `5`                       | The maximum number of replicas of a single cluster                                                                                                                     | [Contact support]
`max_result_size`                           | `1 GiB`                   | The maximum size in bytes for a single query's result.                                                                                                                 | [Contact support]
`max_roles`                                 | `1000`                    | The maximum number of roles in the region.                                                                                                                             | [Contact support]
`max_schemas_per_database`                  | `1000`                    | The maximum number of schemas in a database.                                                                                                                           | [Contact support]
`max_secrets`                               | `100`                     | The maximum number of secrets in the region, across all schemas.                                                                                                       | [Contact support]
`max_sinks`                                 | `1000`                    | The maximum number of sinks in the region, across all schemas.                                                                                                         | [Contact support]
`max_sources`                               | `25`                      | The maximum number of sources in the region, across all schemas.                                                                                                       | [Contact support]
`max_tables`                                | `200`                     | The maximum number of tables in the region, across all schemas                                                                                                         | [Contact support]
`max_timestamp_interval`                    | `1s`                      | The upper bound for the `TIMESTAMP INTERVAL` option of [`CREATE SOURCE`](/sql/create-source/) and [`ALTER SOURCE`](/sql/alter-source/). Statements that request a timestamp interval larger than this value are rejected. Accepts positive [interval](/sql/types/interval/) values (e.g. `'500ms'`, `'1s'`). | [Contact support]
`min_timestamp_interval`                    | `1s`                      | The lower bound for the `TIMESTAMP INTERVAL` option of [`CREATE SOURCE`](/sql/create-source/) and [`ALTER SOURCE`](/sql/alter-source/). Statements that request a timestamp interval smaller than this value are rejected. Accepts positive [interval](/sql/types/interval/) values (e.g. `'500ms'`, `'1s'`). | [Contact support]
`mz_version`                                | Version-dependent         | Shows the Materialize server version.                                                                                                                                  | No
`network_policy`                            | `default`                 | The default network policy for the region. | Yes
`real_time_recency`                         | `false`                   | Boolean flag indicating whether [real-time recency](/serve-results/isolation-level/#real-time-recency) is enabled for the current session.                               | [Contact support]
`real_time_recency_timeout`                 | `10s`                     | Sets the maximum allowed duration of `SELECT` statements that actively use [real-time recency](/serve-results/isolation-level/#real-time-recency). If this value is specified without units, it is taken as milliseconds (`ms`).                      | Yes
`server_version_num`                        | Version-dependent         | The PostgreSQL compatible server version as an integer.                                                                                                                | No
`server_version`                            | Version-dependent         | The PostgreSQL compatible server version.                                                                                                                              | No
`sql_safe_updates`                          | `false`                   | Boolean flag indicating whether to prohibit SQL statements that may be overly destructive.                                                                             | Yes
`standard_conforming_strings`               | `true`                    | Boolean flag indicating whether ordinary string literals (`'...'`) should treat backslashes literally. The only supported value is `true`.                             | Yes
`statement_timeout`                         | `10s`                     | The maximum allowed duration of the read portion of write operations; i.e., the `SELECT` portion of `INSERT INTO ... (SELECT ...)`; the `WHERE` portion of `UPDATE ... WHERE ...` and `DELETE FROM ... WHERE ...`. If this value is specified without units, it is taken as milliseconds (`ms`). | Yes
`timezone`                                  | `UTC`                     | The time zone for displaying and interpreting timestamps. The only supported value is `UTC`.                                                                           | Yes

[Contact support]: /support

## Examples

### Show active cluster

```mzsql
SHOW cluster;
```
```
 cluster
---------
 quickstart
```

### Show transaction isolation level

```mzsql
SHOW transaction_isolation;
```
```
 transaction_isolation
-----------------------
 strict serializable
```

## Related pages

- [`RESET`](../reset)
- [`SET`](../set)

<!-- mz-docs page: sql/show-cluster-replicas -->

# SHOW CLUSTER REPLICAS
`SHOW CLUSTER REPLICAS` lists the replicas for each cluster configured in Materialize.
`SHOW CLUSTER REPLICAS` lists the [replicas](/sql/create-cluster#replication-factor) for each
cluster configured in Materialize.

## Syntax

```sql
SHOW CLUSTER REPLICAS
[LIKE <pattern> | WHERE <condition(s)>]
;
```

Syntax element                | Description
------------------------------|------------
**LIKE** \<pattern\>          | If specified, only show clusters that match the pattern.
**WHERE** <condition(s)>      | If specified, only show clusters that match the condition(s).

## Output

Column       | Description
-------------|------------
**cluster**  | The name of the cluster.
**replica**  | The name of the replica.
**size**     | The [size](/sql/create-cluster#available-sizes) of the replica.
**ready**    | Whether all indexes, materialized views, sources, and sinks on the cluster have hydrated.
**comment**  | The [comment](/sql/comment-on) associated with the cluster replica, if any.

## Examples

```mzsql
SHOW CLUSTER REPLICAS;
```

```nofmt
    cluster    | replica |  size  | ready | comment
---------------+---------|--------|-------|--------
 auction_house | bigger  | 1600cc | t     |
 quickstart    | r1      | 25cc   | t     |
```

```mzsql
SHOW CLUSTER REPLICAS WHERE cluster = 'quickstart';
```

```nofmt
    cluster    | replica |  size  | ready | comment
---------------+---------|--------|-------|--------
 quickstart    | r1      | 25cc   | t     |
```

## Related pages

- [`CREATE CLUSTER REPLICA`](../create-cluster-replica)
- [`DROP CLUSTER REPLICA`](../drop-cluster-replica)

<!-- mz-docs page: sql/show-clusters -->

# SHOW CLUSTERS
`SHOW CLUSTERS` lists the clusters configured in Materialize.
`SHOW CLUSTERS` lists the [clusters](/fundamentals/concepts/clusters/) configured in Materialize.

## Syntax

```sql
SHOW CLUSTERS
[LIKE <pattern> | WHERE <condition(s)>]
;
```

Syntax element                | Description
------------------------------|------------
**LIKE** \<pattern\>          | If specified, only show clusters that match the pattern.
**WHERE** <condition(s)>      | If specified, only show clusters that match the condition(s).

## Output

`SHOW CLUSTERS` returns the following columns:

Column      | Description
------------|------------
`name`      | The name of the cluster.
`replicas`  | The cluster's replicas and their sizes.
`activity`  | A summary of any in-flight [resize](/sql/alter-cluster/#monitoring-a-resize) or [hydration burst](/sql/alter-cluster/#speed-up-hydration-by-autoscaling-to-a-larger-size) on the cluster, or `NULL` when the cluster is steady.
`comment`   | Any [comment](/sql/comment-on/) on the cluster.

## Pre-installed clusters

When you enable a Materialize region, several clusters that are used to improve
the user experience, as well as support system administration tasks, will be
pre-installed.

### `quickstart` cluster

A cluster named `quickstart` with a size of `25cc` and a replication factor of
`1` will be pre-installed in every environment. You can modify or drop this
cluster at any time.

> **Note:** The default value for the `cluster` session parameter is `quickstart`.
> If the `quickstart` cluster is dropped, you must run [`SET cluster`](/sql/select/#ad-hoc-queries)
> to choose a valid cluster in order to run `SELECT` queries. A _superuser_ (i.e. `Organization Admin`)
> can also run [`ALTER SYSTEM SET cluster`](/sql/alter-system-set) to change the
> default value.

### `mz_catalog_server` system cluster

A system cluster named `mz_catalog_server` will be pre-installed in every
environment. This cluster has several indexes installed to speed up `SHOW`
commands and queries using the system catalog.

To take advantage of these indexes, Materialize will automatically re-route
`SHOW` commands and queries using system catalog objects to the
`mz_catalog_server` system cluster. You can disable this behavior in
your session via the `auto_route_catalog_queries`
[configuration parameter](/sql/show/#other-configuration-parameters).

The following characteristics apply to the `mz_catalog_server` cluster:

  * You are **not billed** for this cluster.
  * You cannot create objects in this cluster.
  * You cannot drop this cluster.
  * You can run `SELECT` or `SUBSCRIBE` queries in this cluster as long
    as you only reference objects in the [system catalog](/sql/system-catalog/).

### `mz_probe` system cluster

A system cluster named `mz_probe` will be pre-installed in every environment.
This cluster is used for internal uptime monitoring.

The following characteristics apply to the `mz_probe` cluster:

  * You are **not billed** for this cluster.
  * You cannot create objects in this cluster.
  * You cannot drop this cluster.
  * You cannot run `SELECT` or `SUBSCRIBE` queries in this cluster.

### `mz_support` system cluster

A system cluster named `mz_support` will be pre-installed in every environment.
This cluster is used for internal support tasks.

The following characteristics apply to the `mz_support` cluster:

  * You are **not billed** for this cluster.
  * You cannot create objects in this cluster.
  * You cannot drop this cluster.
  * You cannot run `SELECT` or `SUBSCRIBE` queries in this cluster.

### `mz_system` system cluster

A system cluster named `mz_system` will be pre-installed in every environment.
This cluster is used for internal system jobs.

The following characteristics apply to the `mz_system` cluster:

  * You are **not billed** for this cluster.
  * You cannot create objects in this cluster.
  * You cannot drop this cluster.
  * You cannot run `SELECT` or `SUBSCRIBE` queries in this cluster.

## Examples

```mzsql
SET CLUSTER = mz_catalog_server;

SHOW CLUSTERS;
```

```nofmt
       name                  replicas
--------------------- | ------------------
 default              |  r1 (25cc)
 auction_house        |  r1 (25cc)
 mz_catalog_server    |  r1 (50cc)
 mz_system            |  r1 (50cc)
 mz_probe             |  r1 (mz_probe)
 mz_support           |
```

```mzsql
SHOW CLUSTERS LIKE 'auction_%';
```

```nofmt
      name                  replicas
--------------------- | ------------------
 auction_house        |  r1 (25cc)
```

While a cluster is being [resized](/sql/alter-cluster/#monitoring-a-resize) or
is running a [hydration
burst](/sql/alter-cluster/#speed-up-hydration-by-autoscaling-to-a-larger-size), the
`activity` column summarizes the in-flight operation:

```nofmt
      name          |  replicas   |             activity
--------------------+-------------+----------------------------------
 auction_house      |  r1 (25cc)  | reconfiguring size to 200cc
 billing            |  r1 (100cc) | hydration burst at 800cc
 default            |  r1 (25cc)  |
```

## Related pages

- [`CREATE CLUSTER`](../create-cluster)
- [`DROP CLUSTER`](../drop-cluster)

<!-- mz-docs page: sql/show-columns -->

# SHOW COLUMNS
`SHOW COLUMNS` lists the columns available for an object.
`SHOW COLUMNS` lists the columns available for an object. This can be a source,
subsource, materialized view, view, or table.

## Syntax

```sql
SHOW COLUMNS FROM <object_name>
[LIKE <pattern> | WHERE <condition(s)>]
;
```

Syntax element                | Description
------------------------------|------------
**LIKE** \<pattern\>          | If specified, only show columns that match the pattern.
**WHERE** <condition(s)>      | If specified, only show columns that match the condition(s).

## Details

### Output format

`SHOW COLUMNS`'s output is a table, with this structure:

```nofmt
+---------+------------+--------+
| name    | nullable   | type   |
|---------+------------+--------|
| ...     | ...        | ...    |
+---------+------------+--------+
```

Field | Meaning
------|--------
**name** | The name of the column
**nullable** | Does the column accept `null` values?
**type** | The column's [type](../types)

Rows are sorted by the order in which the fields are defined in the targeted
object.

## Examples

```mzsql
SHOW SOURCES;
```
```nofmt
   name
----------
my_sources
```
```mzsql
SHOW COLUMNS FROM my_source;
```
```nofmt
  name  | nullable | type
---------+----------+------
 column1 | f       | int4
 column2 | f       | text
```

## Privileges

The privileges required to execute this statement are:

- `USAGE` privileges on the schema containing `item_ref`.

## Related pages

- [`SHOW SOURCES`](../show-sources)
- [`SHOW VIEWS`](../show-views)
- [`SHOW INDEXES`](../show-indexes)

<!-- mz-docs page: sql/show-connections -->

# SHOW CONNECTIONS
`SHOW CONNECTIONS` lists the connections configured in Materialize.
`SHOW CONNECTIONS` lists the connections configured in Materialize.

## Syntax

```sql
SHOW CONNECTIONS
[FROM <schema_name>]
[LIKE <pattern> | WHERE <condition(s)>]
;
```

Syntax element                | Description
------------------------------|------------
**FROM** \<schema_name\>      | If specified, only show connections from the specified schema. For available schema names, see [`SHOW SCHEMAS`](/sql/show-schemas).
**LIKE** \<pattern\>          | If specified, only show connections that match the pattern.
**WHERE** <condition(s)>      | If specified, only show connections that match the condition(s).

## Examples

```mzsql
SHOW CONNECTIONS;
```

```nofmt
       name          | type
---------------------+---------
 kafka_connection    | kafka
 postgres_connection | postgres
```

```mzsql
SHOW CONNECTIONS LIKE 'kafka%';
```

```nofmt
       name       | type
------------------+------
 kafka_connection | kafka
```

## Related pages

- [`CREATE CONNECTION`](../create-connection)
- [`DROP CONNECTION`](../drop-connection)

<!-- mz-docs page: sql/show-create-cluster -->

# SHOW CREATE CLUSTER
`SHOW CREATE CLUSTER` returns the DDL statement used to create the cluster.
`SHOW CREATE CLUSTER` returns the DDL statement used to create the cluster.

## Syntax

```sql
SHOW CREATE CLUSTER <cluster_name>
```

For available cluster names, see [`SHOW CLUSTERS`](/sql/show-clusters).

## Examples

```sql
SHOW CREATE CLUSTER c;
```

```nofmt
    name          |    create_sql
------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 c                | CREATE CLUSTER "c" (INTROSPECTION DEBUGGING = false, INTROSPECTION INTERVAL = INTERVAL '00:00:01', MANAGED = true, REPLICATION FACTOR = 1, SIZE = '100cc', SCHEDULE = MANUAL)
```

## Privileges

There are no privileges required to execute this statement.

## Related pages

- [`SHOW CLUSTERS`](../show-clusters)
- [`CREATE CLUSTER`](../create-cluster)

<!-- mz-docs page: sql/show-create-connection -->

# SHOW CREATE CONNECTION
`SHOW CREATE CONNECTION` returns the statement used to create the connection.
`SHOW CREATE CONNECTION` returns the DDL statement used to create the connection.

## Syntax

```sql
SHOW [REDACTED] CREATE CONNECTION <connection_name>;
```

| Syntax element | Description |
| --- | --- |
| <strong>REDACTED</strong> | If specified, literals will be redacted. |

For available connection names, see [`SHOW CONNECTIONS`](/sql/show-connections).

## Examples

```mzsql
SHOW CREATE CONNECTION kafka_connection;
```

```nofmt
    name          |    create_sql
------------------+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 kafka_connection | CREATE CONNECTION "materialize"."public"."kafka_connection" TO KAFKA (BROKER 'unique-jellyfish-0000.us-east-1.aws.confluent.cloud:9092', SASL MECHANISMS = 'PLAIN', SASL USERNAME = SECRET sasl_username, SASL PASSWORD = SECRET sasl_password)
```

## Privileges

The privileges required to execute this statement are:

- `USAGE` privileges on the schema containing the connection.

## Related pages

- [`SHOW CONNECTIONS`](../show-sources)
- [`CREATE CONNECTION`](../create-connection)

<!-- mz-docs page: sql/show-create-index -->

# SHOW CREATE INDEX
`SHOW CREATE INDEX` returns the statement used to create the index.
`SHOW CREATE INDEX` returns the DDL statement used to create the index.

## Syntax

```sql
SHOW [REDACTED] CREATE INDEX <index_name>;
```

| Syntax element | Description |
| --- | --- |
| <strong>REDACTED</strong> | If specified, literals will be redacted. |

For available index names, see [`SHOW INDEXES`](/sql/show-indexes).

## Examples

```mzsql
SHOW INDEXES FROM my_view;
```

```nofmt
     name    | on  | cluster    | key
-------------+-----+------------+--------------------------------------------
 my_view_idx | t   | quickstart | {a, b}
```

```mzsql
SHOW CREATE INDEX my_view_idx;
```

```nofmt
              name              |                                           create_sql
--------------------------------+------------------------------------------------------------------------------------------------
 materialize.public.my_view_idx | CREATE INDEX "my_view_idx" IN CLUSTER "default" ON "materialize"."public"."my_view" ("a", "b")
```

## Privileges

The privileges required to execute this statement are:

- `USAGE` privileges on the schema containing the index.

## Related pages

- [`SHOW INDEXES`](../show-indexes)
- [`CREATE INDEX`](../create-index)

<!-- mz-docs page: sql/show-create-materialized-view -->

# SHOW CREATE MATERIALIZED VIEW
`SHOW CREATE MATERIALIZED VIEW` returns the statement used to create the materialized view
`SHOW CREATE MATERIALIZED VIEW` returns the DDL statement used to create the materialized view.

## Syntax

```sql
SHOW [REDACTED] CREATE MATERIALIZED VIEW <view_name>;
```

| Syntax element | Description |
| --- | --- |
| <strong>REDACTED</strong> | If specified, literals will be redacted. |

For available materialized view names, see [`SHOW MATERIALIZED VIEWS`](/sql/show-materialized-views).

## Examples

```mzsql
SHOW CREATE MATERIALIZED VIEW winning_bids;
```
```nofmt
              name               |                                                                                                                       create_sql
---------------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 materialize.public.winning_bids | CREATE MATERIALIZED VIEW "materialize"."public"."winning_bids" IN CLUSTER "quickstart" AS SELECT * FROM "materialize"."public"."highest_bid_per_auction" WHERE "end_time" < "mz_catalog"."mz_now"()
```

## Privileges

The privileges required to execute this statement are:

- `USAGE` privileges on the schema containing the materialized view.

## Related pages

- [`SHOW MATERIALIZED VIEWS`](../show-materialized-views)
- [`CREATE MATERIALIZED VIEW`](../create-materialized-view)

<!-- mz-docs page: sql/show-create-sink -->

# SHOW CREATE SINK
`SHOW CREATE SINK` returns the statement used to create the sink.
`SHOW CREATE SINK` returns the DDL statement used to create the sink.

## Syntax

```sql
SHOW [REDACTED] CREATE SINK <sink_name>;
```

| Syntax element | Description |
| --- | --- |
| <strong>REDACTED</strong> | If specified, literals will be redacted. |

For available sink names, see [`SHOW SINKS`](/sql/show-sinks).

## Examples

```mzsql
SHOW SINKS
```

```nofmt
     name
--------------
 my_view_sink
```

```mzsql
SHOW CREATE SINK my_view_sink;
```

```nofmt
               name              |                                                                                                        create_sql
---------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 materialize.public.my_view_sink | CREATE SINK "materialize"."public"."my_view_sink" IN CLUSTER "c" FROM "materialize"."public"."my_view" INTO KAFKA CONNECTION "materialize"."public"."kafka_conn" (TOPIC 'my_view_sink') FORMAT AVRO USING CONFLUENT SCHEMA REGISTRY CONNECTION csr_connection ENVELOPE DEBEZIUM
```

## Privileges

The privileges required to execute this statement are:

- `USAGE` privileges on the schema containing the sink.

## Related pages

- [`SHOW SINKS`](../show-sinks)
- [`CREATE SINK`](../create-sink)

<!-- mz-docs page: sql/show-create-source -->

# SHOW CREATE SOURCE
`SHOW CREATE SOURCE` returns the statement used to create the source.
`SHOW CREATE SOURCE` returns the DDL statement used to create the source.

## Syntax

```sql
SHOW [REDACTED] CREATE SOURCE <source_name>;
```

| Syntax element | Description |
| --- | --- |
| <strong>REDACTED</strong> | If specified, literals will be redacted. |

For available source names, see [`SHOW SOURCES`](/sql/show-sources).

## Examples

```mzsql
SHOW CREATE SOURCE market_orders_raw;
```

```nofmt
                 name                 |                                      create_sql
--------------------------------------+--------------------------------------------------------------------------------------------------------------
 materialize.public.market_orders_raw | CREATE SOURCE "materialize"."public"."market_orders_raw" IN CLUSTER "c" FROM LOAD GENERATOR COUNTER
```

## Privileges

The privileges required to execute this statement are:

- `USAGE` privileges on the schema containing the source.

## Related pages

- [`SHOW SOURCES`](../show-sources)
- [`CREATE SOURCE`](../create-source)

<!-- mz-docs page: sql/show-create-table -->

# SHOW CREATE TABLE
`SHOW CREATE TABLE` returns the SQL used to create the table.
`SHOW CREATE TABLE` returns the SQL used to create the table.

## Syntax

```sql
SHOW [REDACTED] CREATE TABLE <table_name>;
```

| Syntax element | Description |
| --- | --- |
| <strong>REDACTED</strong> | If specified, literals will be redacted. |

For available table names, see [`SHOW TABLES`](/sql/show-tables).

## Examples

```mzsql
CREATE TABLE t (a int, b text NOT NULL);
```

```mzsql
SHOW CREATE TABLE t;
```
```nofmt
         name         |                                             create_sql
----------------------+-----------------------------------------------------------------------------------------------------
 materialize.public.t | CREATE TABLE "materialize"."public"."t" ("a" "pg_catalog"."int4", "b" "pg_catalog"."text" NOT NULL)
```

## Privileges

The privileges required to execute this statement are:

- `USAGE` privileges on the schema containing the table.

## Related pages

- [`SHOW TABLES`](../show-tables)
- [`CREATE TABLE`](../create-table)

<!-- mz-docs page: sql/show-create-type -->

# SHOW CREATE TYPE
`SHOW CREATE TYPE` returns the DDL statement used to create the custom type.
`SHOW CREATE TYPE` returns the DDL statement used to create the custom type.

## Syntax

```sql
SHOW [REDACTED] CREATE TYPE <type_name>;
```

| Syntax element | Description |
| --- | --- |
| <strong>REDACTED</strong> | If specified, literals will be redacted. |

For available type names, see [`SHOW TYPES`](/sql/show-types).

## Examples

```sql
SHOW CREATE TYPE point;

```

```nofmt
    name                    |    create_sql
----------------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 materialize.public.point   | CREATE TYPE materialize.public.point AS (x pg_catalog.int4, y pg_catalog.int4);
```

## Privileges

- `USAGE` privileges on the schema containing the type.

## Related pages

- [`SHOW TYPES`](../show-types)
- [`CREATE TYPE`](../create-type)

<!-- mz-docs page: sql/show-create-view -->

# SHOW CREATE VIEW
`SHOW CREATE VIEW` returns the `SELECT` statement used to create the view.
`SHOW CREATE VIEW` returns the [`SELECT`](../select) statement used to create the view.

## Syntax

```sql
SHOW [REDACTED] CREATE VIEW <view_name>;
```

| Syntax element | Description |
| --- | --- |
| <strong>REDACTED</strong> | If specified, literals will be redacted. |

For available view names, see [`SHOW VIEWS`](/sql/show-views).

## Examples

```mzsql
SHOW CREATE VIEW my_view;
```
```nofmt
            name            |                                            create_sql
----------------------------+--------------------------------------------------------------------------------------------------
 materialize.public.my_view | CREATE VIEW "materialize"."public"."my_view" AS SELECT * FROM "materialize"."public"."my_source"
```

## Privileges

The privileges required to execute this statement are:

- `USAGE` privileges on the schema containing the view.

## Related pages

- [`SHOW VIEWS`](../show-views)
- [`CREATE VIEW`](../create-view)

<!-- mz-docs page: sql/show-databases -->

# SHOW DATABASES
`SHOW DATABASES` returns a list of all databases in Materialize.
`SHOW DATABASES` returns a list of all databases in Materialize.

## Syntax

```sql
SHOW DATABASES
[LIKE <pattern> | WHERE <condition(s)>]
;
```

Syntax element                | Description
------------------------------|------------
**LIKE** \<pattern\>          | If specified, only show databases that match the pattern.
**WHERE** <condition(s)>      | If specified, only show databases that match the condition(s).

## Details

### Output format

`SHOW DATABASES`'s output is a table with one column, `name`.

## Examples

```mzsql
CREATE DATABASE my_db;
```
```mzsql
SHOW DATABASES;
```
```nofmt
materialize
my_db
```

<!-- mz-docs page: sql/show-default-privileges -->

# SHOW DEFAULT PRIVILEGES
SHOW DEFAULT PRIVILEGES lists the default privileges granted on objects in Materialize.
`SHOW DEFAULT PRIVILEGES` lists the default privileges granted on objects in Materialize.

## Syntax

```sql
SHOW DEFAULT PRIVILEGES [ON <object_type>] [FOR <role_name>];
```

Syntax element               | Description
-----------------------------|--------------------------------------
**ON** <object_type>         | If specified, only show default privileges for the specified object type. Accepted object types: <div style="display: flex;"> <ul style="margin-right: 20px;"> <li><strong>CLUSTERS</strong></li> <li><strong>CONNECTION</strong></li> <li><strong>DATABASES</strong></li> <li><strong>SCHEMAS</strong></li> </ul> <ul> <li><strong>SECRETS</strong></li> <li><strong>TABLES</strong></li> <li><strong>TYPES</strong></li> </ul> </div>
**FOR** <role_name>          | If specified, only show default privileges granted directly or indirectly to the specified role. For available role names, see [`SHOW ROLES`](/sql/show-roles).

[//]: # "TODO(morsapaes) Improve examples."

## Examples

```mzsql
SHOW DEFAULT PRIVILEGES;
```

```nofmt
 object_owner | database | schema | object_type | grantee | privilege_type
--------------+----------+--------+-------------+---------+----------------
 PUBLIC       |          |        | cluster     | interns | USAGE
 PUBLIC       |          |        | schema      | mike    | CREATE
 PUBLIC       |          |        | type        | PUBLIC  | USAGE
 mike         |          |        | table       | joe     | SELECT
```

```mzsql
SHOW DEFAULT PRIVILEGES ON SCHEMAS;
```

```nofmt
 object_owner | database | schema | object_type | grantee | privilege_type
--------------+----------+--------+-------------+---------+----------------
 PUBLIC       |          |        | schema      | mike    | CREATE
```

```mzsql
SHOW DEFAULT PRIVILEGES FOR joe;
```

```nofmt
 object_owner | database | schema | object_type | grantee | privilege_type
--------------+----------+--------+-------------+---------+----------------
 PUBLIC       |          |        | cluster     | interns | USAGE
 PUBLIC       |          |        | type        | PUBLIC  | USAGE
 mike         |          |        | table       | joe     | SELECT
```

## Related pages

- [`ALTER DEFAULT PRIVILEGES`](../alter-default-privileges)

<!-- mz-docs page: sql/show-indexes -->

# SHOW INDEXES
SHOW INDEXES provides details about indexes built on a source, view, or materialized view
`SHOW INDEXES` provides details about indexes built on a source, view, or materialized view.

## Syntax

```mzsql
SHOW INDEXES [ FROM <schema_name> | ON <object_name> ]
[ IN CLUSTER <cluster_name> ]
[ LIKE <pattern> | WHERE <condition(s)> ]
;
```

Syntax element                | Description
------------------------------|------------
**FROM** <schema_name>        | If specified, only show indexes from the specified schema. Defaults to first resolvable schema in the search path if neither `ON <object_name>` nor `IN CLUSTER <cluster_name>` are specified. For available schemas, see [`SHOW SCHEMAS`](../show-schemas).
**ON** <object_name>          | If specified, only show indexes for the specified object.
**IN CLUSTER** <cluster_name> | If specified, only show indexes from the specified cluster.
**LIKE** \<pattern\>          | If specified, only show indexes that match the pattern.
**WHERE** <condition(s)>      | If specified, only show indexes that match the condition(s).

## Details

### Output format

`SHOW INDEX`'s output is a table with the following structure:

```nofmt
name | on  | cluster | key
-----+-----+---------+----
 ... | ... | ...     | ...
```

Field | Meaning
------|--------
**name** | The name of the index.
**on** | The name of the table, source, or view the index belongs to.
**cluster** | The name of the [cluster](/fundamentals/concepts/clusters/) containing the index.
**key** | A text array describing the expressions in the index key.

## Examples

```mzsql
SHOW VIEWS;
```
```nofmt
          name
-------------------------
 my_nonmaterialized_view
 my_materialized_view
```

```mzsql
SHOW INDEXES ON my_materialized_view;
```
```nofmt
 name | on  | cluster | key
------+-----+---------+----
 ...  | ... | ...     | ...
```

## Related pages

- [`SHOW CREATE INDEX`](../show-create-index)
- [`DROP INDEX`](../drop-index)

<!-- mz-docs page: sql/show-materialized-views -->

# SHOW MATERIALIZED VIEWS
`SHOW MATERIALIZED VIEWS` returns a list of materialized views being maintained in Materialize.
`SHOW MATERIALIZED VIEWS` returns a list of materialized views being maintained
in Materialize.

## Syntax

```mzsql
SHOW MATERIALIZED VIEWS [ FROM <schema_name> ] [ IN <cluster_name> ];
```

Syntax element                | Description
------------------------------|------------
**FROM** <schema_name>      | If specified, only show materialized views from the specified schema. Defaults to first resolvable schema in the search path. For available schemas, see [`SHOW SCHEMAS`](../show-schemas).
**IN** <cluster_name>       | If specified, only show materialized views from the specified cluster.

## Examples

```mzsql
SHOW MATERIALIZED VIEWS;
```

```nofmt
     name     | cluster
--------------+----------
 winning_bids | quickstart
```

```mzsql
SHOW MATERIALIZED VIEWS LIKE '%bid%';
```

```nofmt
     name     | cluster
--------------+----------
 winning_bids | quickstart
```

## Related pages

- [`SHOW CREATE MATERIALIZED VIEW`](../show-create-materialized-view)
- [`CREATE MATERIALIZED VIEW`](../create-materialized-view)

<!-- mz-docs page: sql/show-network-policies -->

# SHOW NETWORK POLICIES (Cloud)
`SHOW NETWORK POLICIES` returns a list of all network policies configured in Materialize.
*Available for Materialize Cloud only*

`SHOW NETWORK POLICIES` returns a list of all network policies configured in
Materialize. Network policies are part of Materialize's framework for
[access control](/security/cloud/).

## Syntax

```mzsql
SHOW NETWORK POLICIES [ LIKE <pattern> ];
```

Syntax element                | Description
------------------------------|------------
**LIKE** \<pattern\>       | If specified, only show network policies whose name matches the pattern.

## Pre-installed network policy

When you enable a Materialize region, a default network policy named `default`
will be pre-installed. This policy has a wide open ingress rule `allow
0.0.0.0/0`. You can modify or drop this network policy at any time.

> **Note:** The default value for the `network_policy` session parameter is `default`.
> Before dropping the `default` network policy, a _superuser_ (i.e. `Organization
> Admin`) must run [`ALTER SYSTEM SET network_policy`](/sql/alter-system-set) to
> change the default value.

## Examples

```mzsql
SHOW NETWORK POLICIES;
```
```nofmt
| name                 | rules              | comment |
| -------------------- | ------------------ | ------- |
| default              | open_ingress       |         |
| office_access_policy | minnesota,new_york |         |
```

To see details for each rule in a network policy, you can query the
[`mz_internal.mz_network_policy_rules`](/sql/system-catalog/mz_internal/#mz_network_policy_rules)
system catalog table.

```mzsql
SELECT * FROM mz_internal.mz_network_policy_rules;
```
```nofmt
| name         | policy_id | action | address    | direction |
| ------------ | --------- | ------ | ---------- | --------- |
| new_york     | u3        | allow  | 1.2.3.4/28 | ingress   |
| minnesota    | u3        | allow  | 2.3.4.5/32 | ingress   |
| open_ingress | u1        | allow  | 0.0.0.0/0  | ingress   |
```

## Related pages

- [`CREATE NETWORK POLICY`](../create-network-policy)
- [`ALTER NETWORK POLICY`](../alter-network-policy)
- [`DROP NETWORK POLICY`](../drop-network-policy)

<!-- mz-docs page: sql/show-objects -->

# SHOW OBJECTS
`SHOW OBJECTS` returns a list of all objects in Materialize for a given schema.
`SHOW OBJECTS` returns a list of all objects in Materialize for a given schema.
Objects include tables, sources, sinks, views, materialized views, indexes,
secrets and connections.

## Syntax

```mzsql
SHOW OBJECTS [ FROM <schema_name> ];
```

Syntax element               | Description
-----------------------------|------------
**FROM** <schema_name>       | If specified, only show objects from the specified schema. Defaults to first resolvable schema in the search path. For available schemas, see [`SHOW SCHEMAS`](../show-schemas).

## Details

### Output format

`SHOW OBJECTS` will output a table with two columns, `name`and `type`.

## Examples

```mzsql
SHOW SCHEMAS;
```
```nofmt
  name
--------
 public
```
```mzsql
SHOW OBJECTS FROM public;
```
```nofmt
  name          | type
----------------+-------
my_table        | table
my_source       | source
my_view         | view
my_other_source | source
```
```mzsql
SHOW OBJECTS;
```
```nofmt
  name    | type
----------+-------
my_table  | table
my_source | source
my_view   | view
```

## Related pages

- [`SHOW TABLES`](../show-tables)
- [`SHOW SOURCES`](../show-sources)
- [`SHOW SINKS`](../show-sinks)
- [`SHOW VIEWS`](../show-views)
- [`SHOW INDEXES`](../show-indexes)
- [`SHOW SECRETS`](../show-secrets)
- [`SHOW CONNECTIONS`](../show-connections)

<!-- mz-docs page: sql/show-privileges -->

# SHOW PRIVILEGES
SHOW PRIVILEGES lists the privileges granted on all objects via role-based access control (RBAC).
`SHOW PRIVILEGES` lists the privileges granted on all objects via
[role-based access control](/security/) (RBAC).

## Syntax

```mzsql
SHOW PRIVILEGES [ ON <object_type> ] [ FOR <role_name> ];
```

Syntax element               | Description
-----------------------------|-----------------------------------------------
**ON** <object_type>         | If specified, only show privileges for the specified object type. Accepted object types: <div style="display: flex;"> <ul style="margin-right: 20px;"> <li><strong>CLUSTERS</strong></li> <li><strong>CONNECTION</strong></li> <li><strong>DATABASES</strong></li> <li><strong>SCHEMAS</strong></li> </ul> <ul> <li><strong>SECRETS</strong></li> <li><strong>SYSTEM</strong></li> <li><strong>TABLES</strong></li> <li><strong>TYPES</strong></li> </ul> </div>
**FOR** <role_name>          | If specified, only show privileges for the specified role.

[//]: # "TODO(morsapaes) Improve examples."

## Examples

```mzsql
SHOW PRIVILEGES;
```

```nofmt
  grantor  |   grantee   |  database   | schema |    name     | object_type | privilege_type
-----------+-------------+-------------+--------+-------------+-------------+----------------
 mz_system | PUBLIC      | materialize |        | public      | schema      | USAGE
 mz_system | PUBLIC      |             |        | quickstart  | cluster     | USAGE
 mz_system | PUBLIC      |             |        | materialize | database    | USAGE
 mz_system | materialize | materialize |        | public      | schema      | CREATE
 mz_system | materialize | materialize |        | public      | schema      | USAGE
 mz_system | materialize |             |        | quickstart  | cluster     | CREATE
 mz_system | materialize |             |        | quickstart  | cluster     | USAGE
 mz_system | materialize |             |        | materialize | database    | CREATE
 mz_system | materialize |             |        | materialize | database    | USAGE
 mz_system | materialize |             |        |             | system      | CREATECLUSTER
 mz_system | materialize |             |        |             | system      | CREATEDB
 mz_system | materialize |             |        |             | system      | CREATEROLE
```

```mzsql
SHOW PRIVILEGES ON SCHEMAS;
```

```nofmt
  grantor  |   grantee   |  database   | schema |  name  | object_type | privilege_type
-----------+-------------+-------------+--------+--------+-------------+----------------
 mz_system | PUBLIC      | materialize |        | public | schema      | USAGE
 mz_system | materialize | materialize |        | public | schema      | CREATE
 mz_system | materialize | materialize |        | public | schema      | USAGE
```

```mzsql
SHOW PRIVILEGES FOR materialize;
```

```nofmt
  grantor  |   grantee   |  database   | schema |    name     | object_type | privilege_type
-----------+-------------+-------------+--------+-------------+-------------+----------------
 mz_system | materialize | materialize |        | public      | schema      | CREATE
 mz_system | materialize | materialize |        | public      | schema      | USAGE
 mz_system | materialize |             |        | quickstart  | cluster     | CREATE
 mz_system | materialize |             |        | quickstart  | cluster     | USAGE
 mz_system | materialize |             |        | materialize | database    | CREATE
 mz_system | materialize |             |        | materialize | database    | USAGE
 mz_system | materialize |             |        |             | system      | CREATECLUSTER
 mz_system | materialize |             |        |             | system      | CREATEDB
 mz_system | materialize |             |        |             | system      | CREATEROLE
```

## Related pages

- [`GRANT PRIVILEGE`](../grant-privilege)
- [`REVOKE PRIVILEGE`](../revoke-privilege)

<!-- mz-docs page: sql/show-role-membership -->

# SHOW ROLE MEMBERSHIP
SHOW ROLE MEMBERSHIP lists the members of each role granted via role-based access control (RBAC).
`SHOW ROLE MEMBERSHIP` lists the members of each role granted (directly or
indirectly) via [role-based access
control](/security/) (RBAC).

## Syntax

```mzsql
SHOW ROLE MEMBERSHIP [ FOR <role_name> ];
```

Syntax element             | Description
---------------------------|------------
**FOR** <role_name>        | If specified, only show membership for the specified role.

[//]: # "TODO(morsapaes) Improve examples."

## Examples

```mzsql
SHOW ROLE MEMBERSHIP;
```

```nofmt
 role | member |  grantor
------+--------+-----------
 r2   | r1     | mz_system
 r3   | r2     | mz_system
 r4   | r3     | mz_system
 r6   | r5     | mz_system
```

```mzsql
SHOW ROLE MEMBERSHIP FOR r2;
```

```nofmt
 role | member |  grantor
------+--------+-----------
 r3   | r2     | mz_system
 r4   | r3     | mz_system
```

## Related pages

- [`GRANT ROLE`](../grant-role)
- [`REVOKE ROLE`](../revoke-role)

<!-- mz-docs page: sql/show-roles -->

# SHOW ROLES
`SHOW ROLES` lists the roles available in Materialize.
`SHOW ROLES` lists the roles available in Materialize.

## Syntax

```mzsql
SHOW ROLES [ LIKE <pattern>  | WHERE <condition(s)> ];
```

Syntax element             | Description
---------------------------|------------
**LIKE** \<pattern\>       | If specified, only show roles whose name matches the pattern.
**WHERE** <condition(s)>   | If specified, only show roles that meet the condition(s).

## Examples

```mzsql
SHOW ROLES;
```
```nofmt
 name
----------------
 joe@ko.sh
 mike@ko.sh
```

```mzsql
SHOW ROLES LIKE 'jo%';
```
```nofmt
 name
----------------
 joe@ko.sh
```

```mzsql
SHOW ROLES WHERE name = 'mike@ko.sh';
```
```nofmt
 name
----------------
 mike@ko.sh
```

## Related pages

- [`CREATE ROLE`](../create-role)
- [`DROP ROLE`](../drop-role)

<!-- mz-docs page: sql/show-schemas -->

# SHOW SCHEMAS
`SHOW SCHEMAS` returns a list of all schemas available in Materialize.
`SHOW SCHEMAS` returns a list of all schemas available in Materialize.

## Syntax

```mzsql
SHOW SCHEMAS [ FROM <database_name> ];
```

Syntax element                | Description
------------------------------|------------
**FROM** <database_name>      | If specified, only show schemas from the specified database. Defaults to the current database. For available databases, see [`SHOW DATABASES`](../show-databases).

## Details

### Output format

`SHOW SCHEMAS`'s output is a table with one column, `name`.

## Examples

```mzsql
SHOW DATABASES;
```
```nofmt
   name
-----------
materialize
my_db
```
```mzsql
SHOW SCHEMAS FROM my_db
```
```nofmt
  name
--------
 public
```

## Related pages

- [`CREATE SCHEMA`](../create-schema)
- [`DROP SCHEMA`](../drop-schema)

<!-- mz-docs page: sql/show-secrets -->

# SHOW SECRETS
`SHOW SECRETS` lists the names of the secrets securely stored in Materialize's secret management system.
`SHOW SECRETS` lists the names of the secrets securely stored in Materialize's
secret management system. There is no way to show the contents of an existing
secret, though you can override it using the [`ALTER SECRET`](../alter-secret)
statement.

## Syntax

```mzsql
SHOW SECRETS [ FROM <schema_name> ] [ LIKE <pattern>  | WHERE <condition(s)> ];
```

Syntax element                | Description
------------------------------|------------
**FROM** <schema_name>        | If specified, only show secrets from the specified schema.  Defaults to first resolvable schema in the search path. For available schemas, see [`SHOW SCHEMAS`](../show-schemas).
**LIKE** \<pattern\>          | If specified, only show secrets whose name matches the pattern.
**WHERE** <condition(s)>      | If specified, only show secrets that meet the condition(s).

## Examples

```mzsql
SHOW SECRETS;
```

```nofmt
         name
-----------------------
 kafka_ca_cert
 kafka_sasl_password
 kafka_sasl_username
```

```mzsql
SHOW SECRETS FROM public LIKE '%cert%';
```

```nofmt
         name
-----------------------
 kafka_ca_cert
```

## Related pages

- [`CREATE SECRET`](../create-secret)
- [`ALTER SECRET`](../alter-secret)
- [`DROP SECRET`](../drop-secret)

<!-- mz-docs page: sql/show-sinks -->

# SHOW SINKS
`SHOW SINKS` returns a list of all sinks available in Materialize.
`SHOW SINKS` returns a list of all sinks available in Materialize.

## Syntax

```mzsql
SHOW SINKS [ FROM <schema_name> ] [ IN CLUSTER <cluster_name> ];
```

## Details

Syntax element                | Description
------------------------------|------------
**FROM** <schema_name>        | If specified, only show sinks from the specified schema. Defaults to first resolvable schema in the search path. For available schemas, see [`SHOW SCHEMAS`](../show-schemas).
**IN CLUSTER** <cluster_name> | If specified, only show sinks from the specified cluster. For available clusters, see [`SHOW CLUSTERS`](../show-clusters).

### Output format

`SHOW SINKS`'s output is a table, with this structure:

```nofmt
name  | type | cluster
------+------+--------
...   | ...  | ...
```

Field       | Meaning
------------|--------
**name**    | The name of the sink.
**type**    | The type of the sink: currently only `kafka` is supported.
**cluster** | The cluster the sink is associated with.

## Examples

```mzsql
SHOW SINKS;
```
```nofmt
name          | type  | cluster
--------------+-------+--------
my_sink       | kafka | c1
my_other_sink | kafka | c2
```

```mzsql
SHOW SINKS IN CLUSTER c1;
```
```nofmt
name    | type  | cluster
--------+-------+--------
my_sink | kafka | c1
```

## Related pages

- [`CREATE SINK`](../create-sink)
- [`DROP SINK`](../drop-sink)
- [`SHOW CREATE SINK`](../show-create-sink)

<!-- mz-docs page: sql/show-sources -->

# SHOW SOURCES
`SHOW SOURCES` returns a list of all sources available in Materialize.
`SHOW SOURCES` returns a list of all sources available in Materialize.

## Syntax

```mzsql
SHOW SOURCES [ FROM <schema_name> ] [ IN CLUSTER <cluster_name> ];
```

Syntax element                | Description
------------------------------|------------
**FROM** <schema_name>        | If specified, only show sources from the specified schema. Defaults to first resolvable schema in the search path. For available schemas, see [`SHOW SCHEMAS`](../show-schemas).
**IN CLUSTER** <cluster_name> | If specified, only show sources from the specified cluster. For available clusters, see [`SHOW CLUSTERS`](../show-clusters).

## Details

### Output format for `SHOW SOURCES`

`SHOW SOURCES`'s output is a table, with this structure:

```nofmt
name  | type | cluster
------+------+--------
...   | ...  | ...
```

Field | Meaning
------|--------
**name** | The name of the source.
**type** | The type of the source: `kafka`, `postgres`, `load-generator`, `progress`, or `subsource`.
**cluster** | The cluster the source is associated with.

## Examples

```mzsql
SHOW SOURCES;
```
```nofmt
            name    | type     | cluster
--------------------+----------+---------
 my_kafka_source    | kafka    | c1
 my_postgres_source | postgres | c2
```

```mzsql
SHOW SOURCES IN CLUSTER c2;
```
```nofmt
name               | type     | cluster
-------------------+----------+--------
my_postgres_source | postgres | c2
```

## Related pages

- [`CREATE SOURCE`](../create-source)
- [`DROP SOURCE`](../drop-source)
- [`SHOW CREATE SOURCE`](../show-create-source)

<!-- mz-docs page: sql/show-subsources -->

# SHOW SUBSOURCES
`SHOW SUBSOURCES` returns the subsources in the current schema.
`SHOW SUBSOURCES` returns the subsources in the current schema.

## Syntax

```mzsql
SHOW SUBSOURCES [ FROM <schema_name> | ON <source_name> ];
```

Syntax element         | Description
-----------------------|------------
**FROM** <schema_name> | If specified, only show subsources from the specified schema. Defaults to first resolvable schema in the search path.
**ON** <source_name>   | If specified, only show subsources on the specified source.

## Details

A subsource is a relation associated with a source. There are two types of
subsources:

  * Subsources of type `progress` describe Materialize's ingestion progress for
    the parent source. Every source has exactly one subsource of type
    `progress`.

  * Subsources of type `subsource` are used by sources that need to ingest data
    into multiple tables, like PostgreSQL sources. For each upstream table that
    is selected for ingestion, Materialize creates a subsource of type
    `subsource`.

### Output format for `SHOW SUBSOURCES`

`SHOW SUBSOURCES`'s output is a table, with this structure:

```nofmt
 name  | type
-------+-----
 ...   | ...
```

Field    | Meaning
---------|--------
**name** | The name of the subsource.
**type** | The type of the subsource: `subsource` or `progress`.

## Examples

```mzsql
SHOW SOURCES;
```
```nofmt
    name
----------
 postgres
 kafka
```
```mzsql
SHOW SUBSOURCES ON pg;
```
```nofmt
        name        | type
--------------------+-----------
 postgres_progress  | progress
 table1_in_postgres | subsource
 table2_in_postgres | subsource
```
```mzsql
SHOW SUBSOURCES ON kafka;
```
```nofmt
            name    | typef
--------------------+----------
 kafka_progress     | progress
```

## Related pages

- [`SHOW CREATE SOURCE`](../show-create-source)
- [`CREATE SOURCE`](../create-source)

<!-- mz-docs page: sql/show-tables -->

# SHOW TABLES
`SHOW TABLES` returns a list of all tables available in Materialize.
`SHOW TABLES` returns a list of all tables available in Materialize.

## Syntax

```mzsql
SHOW TABLES [FROM <schema_name>];
```

Syntax element                | Description
------------------------------|------------
**FROM** <schema_name>        | If specified, only show tables from the specified schema. Defaults to first resolvable schema in the search path. For available schemas, see [`SHOW SCHEMAS`](../show-schemas).

## Details

### Output format

`SHOW TABLES`'s output is a table with one column, `name`.

## Examples

### Show user-created tables
```mzsql
SHOW TABLES;
```
```nofmt
 name
----------------
 my_table
 my_other_table
```

### Show tables from specified schema
```mzsql
SHOW SCHEMAS;
```
```nofmt
  name
--------
 public
```
```mzsql
SHOW TABLES FROM public;
```
```nofmt
 name
----------------
 my_table
 my_other_table
```

## Related pages

- [`SHOW CREATE TABLE`](../show-create-table)
- [`CREATE TABLE`](../create-table)

<!-- mz-docs page: sql/show-types -->

# SHOW TYPES
`SHOW TYPES` returns a list of the data types in Materialize.
`SHOW TYPES` returns a list of the data types in Materialize. Only custom types
are returned.

## Syntax

```mzsql
SHOW TYPES [FROM <schema_name>];
```

Syntax element                | Description
------------------------------|------------
**FROM** <schema_name>        | If specified, only show types from the specified schema. Defaults to first resolvable schema in the search path. For available schemas, see [`SHOW SCHEMAS`](../show-schemas).

## Examples

### Show custom data types

```mzsql
SHOW TYPES;
```
```
   name
-----------
 int4_list
```

## Related pages

* [`CREATE TYPE`](../create-type)
* [`DROP TYPE`](../drop-type)

<!-- mz-docs page: sql/show-views -->

# SHOW VIEWS
`SHOW VIEWS` returns a list of views in Materialize.
`SHOW VIEWS` returns a list of views in Materialize.

## Syntax

```mzsql
SHOW VIEWS [FROM <schema_name>];
```

Syntax element                | Description
------------------------------|------------
**FROM** <schema_name>        | If specified, only show views from the specified schema. Defaults to first resolvable schema in the search path. For available schemas, see [`SHOW SCHEMAS`](../show-schemas).

## Details

### Output format for `SHOW VIEWS`

`SHOW VIEWS`'s output is a table, with this structure:

```nofmt
 name
-------
 ...
```

Field | Meaning
------|--------
**name** | The name of the view.

## Examples

```mzsql
SHOW VIEWS;
```
```nofmt
  name
---------
 my_view
```

## Related pages

- [`SHOW CREATE VIEW`](../show-create-view)
- [`CREATE VIEW`](../create-view)

<!-- mz-docs page: sql/subscribe -->

# SUBSCRIBE
`SUBSCRIBE` streams updates from a source, table, view, or materialized view as they occur.
`SUBSCRIBE` streams updates from a source, table, view, or materialized view as
they occur.

## Conceptual framework

The `SUBSCRIBE` statement is a more general form of a [`SELECT`](/sql/select)
statement. While a `SELECT` statement computes a relation at a moment in time, a
subscribe operation computes how a relation *changes* over time.

Fundamentally, `SUBSCRIBE` produces a sequence of updates. An update describes either
the insertion or deletion of a row to the relation at a specific time. Taken
together, the updates describe the complete set of changes to a relation, in
order, while `SUBSCRIBE` is active.

You can use `SUBSCRIBE` to:

-   Power event processors that react to every change to a relation or an arbitrary `SELECT` statement.
-   Replicate the complete history of a relation while `SUBSCRIBE` is active.

## Syntax

```mzsql
SUBSCRIBE [TO] <object_name | (SELECT ...)>
[ENVELOPE UPSERT (KEY (<key1>, ...)) | ENVELOPE DEBEZIUM (KEY (<key1>, ...))]
[WITHIN TIMESTAMP ORDER BY <column1> [ASC | DESC] [NULLS LAST | NULLS FIRST], ...]
[WITH (<option_name> [= <option_value>], ...)]
[AS OF [AT LEAST] <timestamp_expression>]
[UP TO <timestamp_expression>]
;

```

where:

- `<object_name>` is the name of the source, table, view, or materialized view
  that you want to subscribe to.
- `<select_stmt>` is the [`SELECT` statement](/sql/select) whose output you want
  to subscribe to.

The generated schemas have a Debezium-style diff envelope to capture changes in
the input view or source.

| Syntax element                  | Description                                                                                                                                      |
| --------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| **ENVELOPE UPSERT (KEY (**\<key1\>, ...**))**                | If specified, use the upsert envelope, which takes a list of `KEY` columns. The upsert envelope supports inserts, updates and deletes in the subscription output. For more information, see [Modifying the output format](#modifying-the-output-format). |
| **ENVELOPE DEBEZIUM (KEY (**\<key1\>, ...**))**           | If specified, use a [Debezium-style diff envelope](/sql/create-sink/kafka/#debezium-envelope), which takes a list of `KEY` columns. The Debezium envelope supports inserts, updates and deletes in the subscription output along with the previous state of the key. For more information, see [Modifying the output format](#modifying-the-output-format). |
| **WITHIN TIMESTAMP ORDER BY** \<column1\>, ... | If specified, use an `ORDER BY` clause to sort the subscription output within a timestamp. For each `ORDER BY` column, you can optionally specify: <ul><li> `ASC` or `DESC`</li><li> `NULLS FIRST` or `NULLS LAST`</li></ul> For more information, see [Modifying the output format](#modifying-the-output-format). |
| **WITH** \<option_name\> [= \<option_value\>] | If specified, use the specified option. For more information, see [`WITH` options](#with-options). |
| **AS OF** \<timestamp_expression\> | If specified, no rows whose timestamp is earlier than the specified timestamp will be returned. For more information, see [`AS OF`](#as-of). |
| **UP TO** \<timestamp_expression\> | If specified, no rows whose timestamp is greater than or equal to the specified timestamp will be returned. For more information, see [`UP TO`](#up-to). |

#### `WITH` options

The following options are valid within the `WITH` clause.

| Option name | Value type | Default | Describes                                                                                                                         |
| ----------- | ---------- | ------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `SNAPSHOT`  | `boolean`  | `true`  | Whether to emit a snapshot of the current state of the relation at the start of the operation. See [`SNAPSHOT`](#snapshot). |
| `PROGRESS`  | `boolean`  | `false` | Whether to include detailed progress information. See [`PROGRESS`](#progress).                                              |

## Details

### Output

`SUBSCRIBE` emits a sequence of updates as rows. Each row contains all of the
columns of the subscribed relation or derived from the `SELECT` statement, prepended
with several additional columns that describe the nature of the update:

<table>
<thead>
  <tr>
    <th>Column</th>
    <th>Type</th>
    <th>Represents</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td><code>mz_timestamp</code></td>
    <td><code>numeric</code></td>
    <td>
      Materialize's internal logical timestamp. This will never be less than any
      timestamp previously emitted by the same <code>SUBSCRIBE</code> operation.
    </td>
  </tr>
  <tr>
    <td><code>mz_progressed</code></td>
    <td><code>boolean</code></td>
    <td>
      <p>
        <em>
          This column is only present if the
          <a href="#progress"><code>PROGRESS</code></a> option is specified.
        </em>
      </p>
      If <code>true</code>, indicates that the <code>SUBSCRIBE</code> will not emit
      additional records at times strictly less than <code>mz_timestamp</code>. See
      <a href="#progress"><code>PROGRESS</code></a> below.
    </td>
  </tr>
  <tr>
    <td><code>mz_diff</code></td>
    <td><code>bigint</code></td>
    <td>
      The change in frequency of the row. A positive number indicates that
      <code>mz_diff</code> copies of the row were inserted, while a negative
      number indicates that <code>|mz_diff|</code> copies of the row were deleted.
    </td>
  </tr>
  <tr>
    <td>Column 1</td>
    <td>Varies</td>
    <td rowspan="3" style="vertical-align: middle; border-left: 1px solid #ccc">
        The columns from the subscribed relation, each as its own column,
        representing the data that was inserted into or deleted from the
        relation.
    </td>
  </tr>
  <tr>
    <td colspan="2" style="text-align: center">...</td>
  </tr>
  <tr>
    <td>Column <em>N</em></td>
    <td>Varies</td>
  </tr>
</tbody>
</table>

### `AS OF`

When a [history rentention
period](/serve-results/durable-subscriptions/#history-retention-period)
is configured for the object(s) powering the subscription, the `AS OF` clause
allows specifying a timestamp at which the `SUBSCRIBE` command should begin
returning results. If `AS OF` is specified, no rows whose timestamp is earlier
than the specified timestamp will be returned. If the timestamp specified is
earlier than the earliest historical state retained by the underlying objects,
an error is thrown.

To configure the history retention period for objects used in a subscription,
see [Durable
subscriptions](/serve-results/durable-subscriptions/#history-retention-period).
If `AS OF` is unspecified, the system automatically chooses an `AS OF`
timestamp.

The value in the `AS OF` clause is automatically [cast to `mz_timestamp`](../../sql/types/mz_timestamp/#valid-casts) with an assignment or implicit cast.

### `UP TO`

The `UP TO` clause allows specifying a timestamp at which the `SUBSCRIBE` will cease running. If `UP TO` is specified, no rows whose timestamp is greater than or equal to the specified timestamp will be returned.

The value in the `UP TO` clause is automatically [cast to `mz_timestamp`](../../sql/types/mz_timestamp/#valid-casts) with an assignment or implicit cast.

### Interaction of `AS OF` and `UP TO`

The lower timestamp bound specified by `AS OF` is inclusive, whereas the upper bound specified by `UP TO` is exclusive. Thus, a `SUBSCRIBE` query whose `AS OF` is equal to its `UP TO` will terminate after returning zero rows.

A `SUBSCRIBE` whose `UP TO` is less than its `AS OF` timestamp (whether that
timestamp was specified in an `AS OF` clause or chosen by the system) will
signal an error.

### Duration

`SUBSCRIBE` will continue to run until canceled, the session ends, the `UP TO` timestamp is reached, or all updates have been presented. The latter case typically occurs when
tailing constant views (e.g. `CREATE VIEW v AS SELECT 1`).

> **Warning:** Many PostgreSQL drivers wait for a query to complete before returning its
> results. Since `SUBSCRIBE` can run forever, naively executing a `SUBSCRIBE` using your
> driver's standard query API may never return.
> Either use an API in your driver that does not buffer rows or use the
> [`FETCH`](/sql/fetch) statement or `AS OF` and `UP TO` bounds
> to fetch rows from `SUBSCRIBE` in batches.
> See the [examples](#examples) for details.

### `SNAPSHOT`

By default, `SUBSCRIBE` begins by emitting a snapshot of the subscribed relation, which
consists of a series of updates at its [`AS OF`](#as-of) timestamp describing the
contents of the relation. After the snapshot, `SUBSCRIBE` emits further updates as
they occur.

For updates in the snapshot, the `mz_timestamp` field will be fast-forwarded to the `AS OF` timestamp.
For example, an insert that occurred before the `SUBSCRIBE` began would appear in the snapshot.

To see only updates after the initial timestamp, specify `WITH (SNAPSHOT = false)`.

> **Note:** While `WITH (SNAPSHOT = false)` guarantees that the snapshot will not be sent to
> the client, Materialize may still need to fetch and process the snapshot data to
> compute the correct result.
> For example, consider:
> ```mzsql
> SUBSCRIBE TO SELECT SUM(column) FROM table WITH (SNAPSHOT = false)
> ```
> The latest update for the query depends on _all_ rows in `table`, not just the
> rows that have changed recently.
> However, when subscribing directly to a collection; e.g.,
> ```mzsql
> SUBSCRIBE TO <object> WITH (SNAPSHOT = false)
> ```
> where `<object>` is a materialized view, table, source, or index, Materialize can generally skip fetching or processing the snapshot data from that collection entirely.

### `PROGRESS`

If the `PROGRESS` option is specified via `WITH (PROGRESS)`:

  * An additional `mz_progressed` column appears in the output. When the column
    is `false`, the rest of the row is a valid update. When the column is `true`
    everything in the row except for `mz_timestamp` is not a valid update and its
    content should be ignored; the row exists only to communicate that timestamps have advanced.

  * The first update emitted by the `SUBSCRIBE` is guaranteed to be a progress
    message indicating the subscribe's [`AS OF`](#as-of) timestamp.

Intuitively, progress messages communicate that no updates have occurred in a
given time window. Without explicit progress messages, it is impossible to
distinguish between a stall in Materialize and a legitimate period of no
updates.

Not all timestamps that appear will have a corresponding row with `mz_progressed` set to `true`.
For example, the following is a valid sequence of updates:

```nofmt
mz_timestamp | mz_progressed | mz_diff | column1
-------------|---------------|---------|--------------
1            | false         | 1       | data
2            | false         | 1       | more data
3            | false         | 1       | even more data
4            | true          | NULL    | NULL
```

Notice how Materialize did not emit explicit progress messages for timestamps
`1` or `2`. The receipt of the update at timestamp `2` implies that there
are no more updates for timestamp `1`, because timestamps are always presented
in non-decreasing order. The receipt of the explicit progress message at
timestamp `4` implies that there are no more updates for either timestamp
`2` or `3`—but that there may be more data arriving at timestamp `4`.

### Connection pooling

Because Materialize is wire-compatible with PostgreSQL, you can use any
PostgreSQL connection pooler with Materialize. For example in using PgBouncer,
see [Connection Pooling](/serve-results/connection-pooling).

## Examples

`SUBSCRIBE` produces rows similar to a `SELECT` statement, except that `SUBSCRIBE` may never complete.
Many drivers buffer all results until a query is complete, and so will never return.
Below are the recommended ways to work around this.

### Creating an auction load generator

As an example, we'll create a [auction load generator](/sql/create-source/load-generator/#creating-an-auction-load-generator) that emits a row every second:

```mzsql
CREATE SOURCE auction FROM LOAD GENERATOR AUCTION FOR ALL TABLES;
```

### Subscribing with `FETCH`

The recommended way to use `SUBSCRIBE` is with [`DECLARE`](/sql/declare) and [`FETCH`](/sql/fetch).
These must be used within a transaction, with [a single `DECLARE`](/sql/begin/#read-only-transactions) per transaction.
This allows you to limit the number of rows and the time window of your requests.
Next, let's subscribe to the `bids` table of the `auction` load generator source that we've created above.

First, declare a `SUBSCRIBE` cursor:

```mzsql
BEGIN;
DECLARE c CURSOR FOR SUBSCRIBE (SELECT * FROM bids);
```

Then, use [`FETCH`](/sql/fetch) in a loop to retrieve each batch of results as soon as it's ready:

```mzsql
FETCH ALL c;
```

That will retrieve all of the rows that are currently available.
If there are no rows available, it will wait until there are some ready and return those.
A `timeout` can be used to specify a window in which to wait for rows. This will return up to the specified count (or `ALL`) of rows that are ready within the timeout. To retrieve up to 100 rows that are available in at most the next `1s`:

```mzsql
FETCH 100 c WITH (timeout='1s');
```

To retrieve all available rows available over the next `1s`:

```mzsql
FETCH ALL c WITH (timeout='1s');
```

A `0s` timeout can be used to return rows that are available now without waiting:

```mzsql
FETCH ALL c WITH (timeout='0s');
```

### Using clients

If you want to use `SUBSCRIBE` from an interactive SQL session (e.g.`psql`), wrap the query in `COPY`:

```mzsql
COPY (SUBSCRIBE (SELECT * FROM bids)) TO STDOUT;
```

| Additional guides |
| ---------------------- |
| [Go](/serve-results/client-libraries/golang/#stream)|
| [Java](/serve-results/client-libraries/java-jdbc/#stream)|
| [Node.js](/serve-results/client-libraries/node-js/#stream)|
| [PHP](/serve-results/client-libraries/php/#stream)|
| [Python](/serve-results/client-libraries/python/#stream)|
| [Ruby](/serve-results/client-libraries/ruby/#stream)|
| [Rust](/serve-results/client-libraries/rust/#stream)|

### Mapping rows to their updates

After all the rows from the [`SNAPSHOT`](#snapshot) have been transmitted, the updates will be emitted as they occur. How can you map each row to its corresponding update?

| mz_timestamp | mz_progressed | mz_diff | Column 1 | .... | Column N |
| ------------ | ------------- | ------- | -------- | ---- | -------- | --------------------------- |
| 1            | false         | 1       | id1      |      | value1   |
| 1            | false         | 1       | id2      |      | value2   |
| 1            | false         | 1       | id3      |      | value3   | <- Last row from `SNAPSHOT` |
| 2            | false         | -1      | id1      |      | value1   |
| 2            | false         | 1       | id1      |      | value4   |

If your row has a unique column key, it is possible to map the update to its corresponding origin row; if the key is unknown, you can use the output of `hash(columns_values)` instead.

In the example above, `Column 1` acts as the column key that uniquely identifies the origin row the update refers to; in case this was unknown, hashing the values from `Column 1` to `Column N` would identify the origin row.

[//]: # "TODO(morsapaes) This page is now complex enough that we should
restructure it using the same feature-oriented approach as CREATE SOURCE/SINK.
See materialize#18829 for the design doc."

### Modifying the output format

#### `ENVELOPE UPSERT`

To modify the output of `SUBSCRIBE` to support upserts, use `ENVELOPE UPSERT`.
This clause allows you to specify a `KEY` that Materialize uses to interpret
the rows as a series of inserts, updates and deletes within each distinct
timestamp.

The output columns are reordered so that all the key columns come before the
value columns.

* Using this modifier, the output rows will have the following
structure:

   ```mzsql
   SUBSCRIBE mview ENVELOPE UPSERT (KEY (key));
   ```

   ```mzsql
   mz_timestamp | mz_state | key  | value
   -------------|----------|------|--------
   100          | upsert   | 1    | 2
   100          | upsert   | 2    | 4
   ```

* For inserts and updates, the value columns for each key are set to the
  resulting value of the series of operations, and `mz_state` is set to
  `upsert`.

  _Insert_

  ```mzsql
   -- at time 200, add a new row with key=3, value=6
   mz_timestamp | mz_state | key  | value
   -------------|----------|------|--------
   ...
   200          | upsert   | 3    | 6
   ...
  ```

  _Update_

  ```mzsql
   -- at time 300, update key=1's value to 10
   mz_timestamp | mz_state | key  | value
   -------------|----------|------|--------
   ...
   300          | upsert   | 1    | 10
   ...
  ```

* If only deletes occur within a timestamp, the value columns for each key are
  set to `NULL`, and `mz_state` is set to `delete`.

  _Delete_

  ```mzsql
   -- at time 400, delete all rows
   mz_timestamp | mz_state | key  | value
   -------------|----------|------|--------
   ...
   400          | delete   | 1    | NULL
   400          | delete   | 2    | NULL
   400          | delete   | 3    | NULL
   ...
  ```

* Only use `ENVELOPE UPSERT` when there is at most one live value per key.
  If materialize detects that a given key has multiple values, it will generate
  an update with `mz_state` set to `"key_violation"`, the problematic key, and all
  the values nulled out. Materialize is not guaranteed to detect this case,
  please don't rely on it.

  _Key violation_

  ```mzsql
   -- at time 500, introduce a key_violation
   mz_timestamp | mz_state        | key  | value
   -------------|-----------------|------|--------
   ...
   500          | key_violation   | 1    | NULL
   ...
  ```

* If [`PROGRESS`](#progress) is set, Materialize also returns the `mz_progressed`
column. Each progress row will have a `NULL` key and a `NULL` value.

#### `ENVELOPE DEBEZIUM`

To modify the output of `SUBSCRIBE` to support upserts using a
[Debezium-style diff envelope](/sql/create-sink/kafka/#debezium-envelope),
use `ENVELOPE DEBEZIUM`. This clause allows you to specify a `KEY` that
Materialize uses to interpret the rows as a series of inserts, updates and
deletes within each distinct timestamp. Unlike `ENVELOPE UPSERT`, the output
includes the state of the row before and after the upsert operation.

The output columns are reordered so that all the key columns come before the
value columns. There are two copies of the value columns: one prefixed with
`before_`, which represents the value of the columns before the upsert
operation; and another prefixed with `after_`, which represents the current
value of the columns.

* Using this modifier, the output rows will have the following
structure:

   ```mzsql
   SUBSCRIBE mview ENVELOPE DEBEZIUM (KEY (key));
   ```

   ```mzsql
   mz_timestamp | mz_state | key  | before_value | after_value
   -------------|----------|------|--------------|-------
   100          | upsert   | 1    | NULL         | 2
   100          | upsert   | 2    | NULL         | 4
   ```

* For inserts: the before values are `NULL`, the current value is the newly inserted
  value and `mz_state` is set to `insert`.

  _Insert_

  ```mzsql
   -- at time 200, add a new row with key=3, value=6
   mz_timestamp | mz_state | key  | before_value | after_value
   -------------|----------|------|--------------|-------
   ...
   200          | insert   | 3    | NULL         | 6
   ...
  ```

* For updates: the before values are the old values, the value columns are the resulting
  values of the update, and `mz_state` is set to`upsert`.

  _Update_

  ```mzsql
   -- at time 300, update key=1's value to 10
   mz_timestamp | mz_state | key  | before_value | after_value
   -------------|----------|------|--------------|-------
   ...
   300          | upsert   | 1    | 2            | 10
   ...
  ```

* If only deletes occur within a timestamp, the value columns for each key are
  set to `NULL`, the before values are set to the old value and `mz_state` is set to `delete`.

  _Delete_

  ```mzsql
   -- at time 400, delete all rows
   mz_timestamp | mz_state | key  | before_value | after_value
   -------------|----------|------|--------------|-------
   ...
   400          | delete   | 1    | 10           | NULL
   400          | delete   | 2    | 4            | NULL
   400          | delete   | 3    | 6            | NULL
   ...
  ```

* Like `ENVELOPE UPSERT`, using `ENVELOPE DEBEZIUM` requires that there is at
  most one live value per key. If Materialize detects that a given key has
  multiple values, it will generate an update with `mz_state` set to
  `"key_violation"`, the problematic key, and all the values nulled out.
  Materialize identifies key violations on a best-effort basis.

  _Key violation_

  ```mzsql
   -- at time 500, introduce a key_violation
   mz_timestamp | mz_state        | key  | before_value | after_value
   -------------|-----------------|------|--------------|-------
   ...
   500          | key_violation   | 1    | NULL         | NULL
   ...
  ```

* If [`PROGRESS`](#progress) is set, Materialize also returns the
`mz_progressed` column. Each progress row will have a `NULL` key and a `NULL`
before and after value.

#### `WITHIN TIMESTAMP ORDER BY`

To modify the ordering of the output of `SUBSCRIBE`, use `WITHIN TIMESTAMP ORDER
BY`. This clause allows you to specify an `ORDER BY` expression which is used
to sort the rows within each distinct timestamp.

* The `ORDER BY` expression can take any column in the underlying object or
  query, including `mz_diff`.

   ```mzsql
   SUBSCRIBE mview WITHIN TIMESTAMP ORDER BY c1, c2 DESC NULLS LAST, mz_diff;

   mz_timestamp | mz_diff | c1            | c2   | c3
   -------------|---------|---------------|------|-----
   100          | +1      | 1             | 20   | foo
   100          | -1      | 1             | 2    | bar
   100          | +1      | 1             | 2    | boo
   100          | +1      | 1             | 0    | data
   100          | -1      | 2             | 0    | old
   100          | +1      | 2             | 0    | new
   ```

* If [`PROGRESS`](#progress) is set, progress messages are unaffected.

### Dropping the `auction` load generator source

When you're done, you can drop the `auction` load generator source:

```mzsql
DROP SOURCE auction CASCADE;
```

### Durable subscriptions

Because `SUBSCRIBE` requests happen over the network, these connections might
get disrupted for both expected and unexpected reasons. You can adjust the
[history retention
period](/serve-results/durable-subscriptions/#history-retention-period)
for the objects a subscription depends on, and then use [`AS OF`](#as-of) to
pick up where you left off on connection drops—this ensures that no data is lost
in the subscription process, and avoids the need for re-snapshotting the data.

For more information, see [durable
subscriptions](/serve-results/durable-subscriptions/).

## Privileges

The privileges required to execute this statement are:

- `USAGE` privileges on the schemas that all relations and types in the query are contained in.
- `SELECT` privileges on all relations in the query.
  - NOTE: if any item is a view, then the view owner must also have the necessary privileges to
  execute the view definition. Even if the view owner is a _superuser_, they still must explicitly be
    granted the necessary privileges.
- `USAGE` privileges on all types used in the query.
- `USAGE` privileges on the active cluster.

<!-- mz-docs page: sql/system-catalog -->

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

<!-- mz-docs page: sql/system-catalog/information_schema -->

# information_schema
information_schema is a system catalog that presents metadata in the format used by SQL standard.
Materialize has compatibility shims for the following relations from the
SQL standard [`information_schema`](https://www.postgresql.org/docs/current/infoschema-schema.html)
schema, which is automatically available in all databases:

  * [`applicable_roles`](https://www.postgresql.org/docs/current/infoschema-applicable-roles.html)
  * [`character_sets`](https://www.postgresql.org/docs/current/infoschema-character-sets.html)
  * [`columns`](https://www.postgresql.org/docs/current/infoschema-columns.html)
  * [`enabled_roles`](https://www.postgresql.org/docs/current/infoschema-enabled-roles.html)
  * [`key_column_usage`](https://www.postgresql.org/docs/current/infoschema-key-column-usage.html)
  * [`referential_constraints`](https://www.postgresql.org/docs/current/infoschema-referential-constraints.html)
  * [`role_table_grants`](https://www.postgresql.org/docs/current/infoschema-role-table-grants.html)
  * [`routines`](https://www.postgresql.org/docs/current/infoschema-routines.html)
  * [`schemata`](https://www.postgresql.org/docs/current/infoschema-schemata.html)
  * [`tables`](https://www.postgresql.org/docs/current/infoschema-tables.html)
  * [`table_constraints`](https://www.postgresql.org/docs/current/infoschema-table-constraints.html)
  * [`table_privileges`](https://www.postgresql.org/docs/current/infoschema-table-privileges.html)
  * [`triggers`](https://www.postgresql.org/docs/current/infoschema-triggers.html)
  * [`views`](https://www.postgresql.org/docs/current/infoschema-views.html)

These compatibility shims are largely incomplete. Most are lacking some columns
that are present in the SQL standard, or if they do include the column the
result set its value may always be `NULL`. The precise nature of the
incompleteness is intentionally undocumented. New tools developed against
Materialize should use the documented [`mz_catalog`](../mz_catalog) API instead.

