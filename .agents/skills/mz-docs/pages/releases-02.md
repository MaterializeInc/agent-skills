<!-- mz-docs page: releases/v0.49 -->

# Materialize v0.49
## v0.49.0

#### SQL

* Change the type of the following system catalog replica ID columns from integer to string:

    * [`mz_catalog.mz_cluster_replicas.id`](/sql/system-catalog/mz_catalog/#mz_cluster_replicas)
    * [`mz_internal.mz_cluster_replica_statuses.replica_id`](/sql/system-catalog/mz_internal/#mz_cluster_replica_statuses)
    * `mz_internal.mz_cluster_replica_heartbeats.replica_id`
    * [`mz_internal.mz_cluster_replica_metrics.replica_id`](/sql/system-catalog/mz_internal/#mz_cluster_replica_metrics)
    * `mz_internal.mz_cluster_replica_frontiers.replica_id`

    This is part of the work to introduce system replicas, which Materialize
    will use for verification and testing purposes and which will not affect
    user billing or system limits ([#11579](https://github.com/MaterializeInc/materialize/issues/11579)). Note that, since
    `mz_catalog` is part of Materialize’s stable interface, the change to
    `mz_catalog.mz_cluster_replicas.id` is a **breaking change**.
    If this change causes you friction, please [let us know](https://materialize.com/s/chat).

* Add the [`ALTER OWNER`](/sql/alter-owner/) command, which updates the owner
  of an object. This is part of the work to enable **Role-based access
  control** (RBAC)([#11579](https://github.com/MaterializeInc/materialize/issues/11579)).

* Add permission checks based on object ownership. To `DROP` or `ALTER` an
  object, the executing role must now be an owner of that object or a
  superuser. This is part of the work to enable **Role-based access control**
  (RBAC)([#11579](https://github.com/MaterializeInc/materialize/issues/11579)).

* Apply `PRIMARY KEY`, `UNIQUE`, and `NOT NULL` constraints to tables ingested
  from PostgreSQL sources.

* Rename [replica introspection views](https://materialize.com/docs/sql/system-catalog/mz_introspection)
  for consistency, and use the `_per_worker` name suffix for per-worker introspection views.

* Automatically restart failed SSH tunnels to improve the reliability of
  SSH-tunneled Kafka sources.

#### Bug fixes and other improvements

- Fix a correctness bug in Top K processing for monotonic, append-only sources.

- Fix a bug that prevented superusers from altering an object owner if they weren't a member of the new owner's role.

- Fix a bug that would cause PostgreSQL sources to error when columns are added to upstream tables. Note that dropping columns from upstream tables that Materialize ingests still results in error.

<!-- mz-docs page: releases/v0.50 -->

# Materialize v0.50
## v0.50.0

#### SQL

* Add [`mz_internal.mz_dataflow_arrangement_sizes`](/sql/system-catalog/mz_introspection/#mz_dataflow_arrangement_sizes)
  to the system catalog. This view describes how many records and batches are
  contained in operators under each dataflow, which is useful to approximate how
  much memory a dataflow is using.

#### Bug fixes and other improvements

* Improve the usability of subscriptions when using the [`WITH (PROGRESS)`](/sql/subscribe/#progress)
  option. Progress information is now guaranteed to include a progress message
  as the **first** update, indicating the `AS OF` time of the subscription.
  This helps distinguish between an empty snapshot and an "in-flight" snapshot.

* Improve the reliability of SSH tunnel connections when used with large cluster
  sizes, and add more verbose logging to make it easier to debug SSH connection
  errors during source and sink creation.

* Mitigate connection interruptions and ingestion hiccups for all connection
  types. If you observe ingestion lag in your sources or sinks, please [get in touch](https://materialize.com/s/chat)!

<!-- mz-docs page: releases/v0.51 -->

# Materialize v0.51
## v0.51.0

#### Sources and sinks

* Add support for replicating tables from specific schemas in the
  [PostgreSQL source](/sql/create-source/postgres/), using the new `FOR SCHEMAS(...)`
  option:

  ```mzsql
  CREATE SOURCE mz_source
    FROM POSTGRES CONNECTION pg_connection (PUBLICATION 'mz_source')
    FOR SCHEMAS (public, finance)
    WITH (SIZE = '3xsmall');
  ```

  With this option, only tables that are part of the publication _and_
  namespaced with the specified schema(s) will be replicated.

#### SQL

* Add `disk_bytes` to the `mz_internal.mz_cluster_replica_{metrics, sizes}`
  system catalog tables. This column is currently `NULL`.

* Add the `translate` [string function](/sql/functions/#string-functions), which
  replaces a set of characters in a string with another set of characters
  (one by one, regardless of the order of those characters):

  ```mzsql
  SELECT translate('12345', '134', 'ax');

	 translate
	-----------
	 a2x5
  ```

* Add new configuration parameters:

  | Configuration parameter      | Scope    | Description                                                                             |
  | ---------------------------- | -------- | --------------------------------------------------------------------------------------- |
  | `enable_session_rbac_checks` | Session  | **Read-only.** Boolean flag indicating whether RBAC is enabled for the current session. |
  | `enable_rbac_checks`         | System   | Boolean flag indicating whether to apply RBAC checks before executing statements. Setting this parameter requires _superuser_ privileges. |

  This is part of the work to enable **Role-based access control** (RBAC) in a
  future release ([#11579](https://github.com/MaterializeInc/materialize/issues/11579)).

#### Bug fixes and other improvements

* Improve the reliability of SSH tunnel connections in the presence of short
  idle TCP connection timeouts.

<!-- mz-docs page: releases/v0.52 -->

# Materialize v0.52
## v0.52.0

#### Sources and sinks

* Allow reading from all non-errored subsources in the [PostgreSQL source](/sql/create-source/postgres/),
  when a source error occurs. Prior to this release, if Materialize encountered
  an error during replication for _any_ table, it'd block reads from _all_
  replicated tables associated with the source.

#### SQL

[//]: # "NOTE(morsapaes) This feature was released in v0.49, but is only
considered production-ready after the changes shipping in v0.52 -— so
mentioning it here."

* Automatically run introspection queries in the [`mz_introspection` cluster](/sql/show-clusters/#mz_catalog_server-system-cluster),
  which has several indexes installed to speed up queries using system catalog
  objects (like `SHOW` commands). This behavior can be disabled via the new
  `auto_route_introspection_queries` [configuration parameter](/sql/set/#other-configuration-parameters).

* Add `reason` to the `mz_internal.mz_cluster_replica_statuses` system catalog
  table. If a cluster replica is in a `not-ready` state, this column provides
  details on the cause (if available). With this release, the only possible non-null
  value for `reason` is `oom-killed`, which indicates that a cluster replica was killed because it ran
  out of memory (OOM).

* Add `credits_per_hour` to the `mz_internal.mz_cluster_replica_sizes` system
  catalog table, and rate limit [free trial accounts](/free-trial-faqs/) to 4
  credits per hour.

  To see your current credit consumption rate, measured in credits per hour, run
  the following query:

  ```mzsql
  SELECT sum(s.credits_per_hour) AS credit_consumption_rate
    FROM mz_cluster_replicas r
    JOIN mz_internal.mz_cluster_replica_sizes s ON r.size = s.size;
  ```

* Add default privileges to databases objects. Each object-specific system table
  now has a `privileges` column that specifies the privileges belonging to the
  object. This is part of the work to enable **Role-based access control**
  (RBAC) ([#11579](https://github.com/MaterializeInc/materialize/issues/11579)).

  It's important to note that privileges cannot currently be modified, and are
  not considered when executing statements. This functionality will be added in
  a future release.

* Add the [`GRANT PRIVILEGE`](/sql/grant-privilege) and [`REVOKE PRIVILEGE`](/sql/revoke-privilege)
  commands, which allow granting/revoking privileges on a database object. To
  ensure compatibility with PostgreSQL, sources, views and materialized views
  must specify `TABLE` as the object type, or omit it altogether.

  This is part of the work to enable **Role-based access control** (RBAC) in a
  future release ([#11579](https://github.com/MaterializeInc/materialize/issues/11579)).

#### Bug fixes and other improvements

* **Breaking change.** Change the type of `id` in the `mz_schemas` and
    `mz_databases` system catalog tables from integer to string, for
    consistency with the rest of the catalog. This change should have no user
    impact, but please [let us know](https://materialize.com/s/chat) if you
    run into any issues.

* Fix a bug where the `before` field was still required in the schema of change
  events for Kafka sources using [`ENVELOPE DEBEZIUM`](https://materialize.com/docs/sql/create-source/kafka/#debezium-envelope)
  ([#18844](https://github.com/MaterializeInc/materialize/issues/18844)).

#### Known issues

* This release inadvertently broke compatibility with `dbt-materialize` <= v1.4.0. Please
  upgrade to `dbt-materialize` v1.4.1, which contains a workaround.

  The upcoming v0.53 release of Materialize will restore compatibility with
  `dbt-materialize` <= v1.4.0.

<!-- mz-docs page: releases/v0.53 -->

# Materialize v0.53
## v0.53.0

#### SQL

* Add support for table aliases in [joins](https://materialize.com/docs/transform-data/join/)
  that specify the `USING` clause. As an example, the column `c` used as the
  join condition in the statement below will be referenceable as `lhs.c`,
  `rhs.c`, and `joint.c`.

  ```mzsql
  SELECT *
  FROM lhs
  JOIN rhs USING (c) AS joint;
  ```

* Require the `CREATECLUSTER` attribute when creating sources or sinks using the
  `SIZE` parameter, which results in the creation of a linked cluster (see
  [Materialize v0.39](../v0.39)). This is part of the work to enable **Role-based
  access control** (RBAC) ([#11579](https://github.com/MaterializeInc/materialize/issues/11579)).

#### Bug fixes and other improvements

* Fix a bug that prevented the PostgreSQL source from replicating tables with
  identifiers that contained quotes (e.g. `"""table"""`) or needed to be
  quoted (e.g. `"select"`).

* This release restores compatibility with `dbt-materialize` <= v1.4.0, which
  broke in the previous release due to the changes in introspection routing
  (see [Materialize v0.52](../v0.52)).

<!-- mz-docs page: releases/v0.54 -->

# Materialize v0.54
## v0.54.0

#### SQL

* Add [`mz_internal.mz_cluster_replica_history`](/sql/system-catalog/mz_internal/#mz_cluster_replica_history)
  to the system catalog. This view contains information about the timespan of
  each replica, including the times at which it was created and dropped (if
  applicable).

* Add `envelope_state_bytes` and `envelope_state_count` to the
  [`mz_internal.mz_source_statistics`](/sql/system-catalog/mz_internal/#mz_source_statistics)
  system catalog table. These columns provide an approximation of the state
  size maintained for upsert sources (i.e. sources using `ENVELOPE
  UPSERT` or `ENVELOPE DEBEZIUM`). In the future, this will allow users to
  relate upsert state size to disk utilization.

* Improve and extend the base implementation of **Role-based
  access control** (RBAC):

  * Consider privileges on database objects when executing statements. If RBAC
    is enabled, Materialize will check the privileges for a role before
    executing any statements.

  * Improve the `GRANT` and `REVOKE` privilege commands to support multiple
    roles, as well as the `ALL` keyword to indicate that all privileges should
    be granted or revoked.

    ```mzsql
    GRANT SELECT ON mv TO joe, mike;

    GRANT ALL ON CLUSTER dev TO joe;
    ```

  * Add support for the [`DROP OWNED`](/sql/drop-owned/) command, which drops
    all the objects that are owned by one of the specified roles from a
    Materialize region. Any privileges granted to the given roles on objects
    will also be revoked.

  It's important to note that role-based access control (RBAC) is **disabled by
  default**. You must [contact us](https://materialize.com/contact/) to enable
  this feature in your Materialize region.

<!-- mz-docs page: releases/v0.55 -->

# Materialize v0.55
## v0.55.0

#### SQL

* Add `SET schema` and `SHOW schema` as aliases to `SET search_path` and `SELECT
  current_schema`, respectively. From this release, the following sequence of
  commands provide the same functionality:

  ```mzsql
  materialize=> SET schema = finance;
  SET
  materialize=> SHOW schema;
   schema
  ---------
   finance
  (1 row)
  ```

  ```mzsql
   materialize=> SET search_path = finance, public;
   SET
   materialize=> SELECT current_schema;
    current_schema
   ----------------
    finance
   (1 row)
  ```

* Improve and extend the base implementation of **Role-based
  access control** (RBAC):

  * Add support for the [`REASSIGN OWNED`](/sql/reassign-owned/) command, which
    allows reassigning the ownership of objects owned by one or more roles to a
    different role.

  It's important to note that role-based access control (RBAC) is **disabled by
  default**. You must [contact us](https://materialize.com/contact/) to enable
  this feature in your Materialize region.

<!-- mz-docs page: releases/v0.56 -->

# Materialize v0.56
## v0.56.0

#### Sources and sinks

* Add a `MARKETING` [load generator source](/sql/create-source/load-generator/#marketing),
  which provides synthetic data to simulate Machine Learning scenarios.

#### SQL

* Improve and extend the base implementation of **Role-based
  access control** (RBAC):

  * Add the `has_table_privilege` access control function, which allows a role
    to query if it has privileges on a specific relation:

    ```mzsql
    SELECT has_table_privilege('marta','auction_house','select');

	 has_table_privilege
	---------------------
	 t
	(1 row)
    ```

  It's important to note that role-based access control (RBAC) is **disabled by
  default**. You must [contact us](https://materialize.com/contact/) to enable
  this feature in your Materialize region.

<!-- mz-docs page: releases/v0.57 -->

# Materialize v0.57
## v0.57.0

#### SQL

* Improve and extend the base implementation of **Role-based
  access control** (RBAC):

  * Allow specifying multiple database objects in the [`GRANT PRIVILEGE`](/sql/grant-privilege)
    and [`REVOKE PRIVILEGE`](/sql/revoke-privilege) commands.

  It's important to note that role-based access control (RBAC) is **disabled by
  default**. You must [contact us](https://materialize.com/contact/) to enable
  this feature in your Materialize region.

* Add `RESET schema` as an alias to `RESET search_path`. From this release, the
  following sequence of commands provide the same functionality:

  ```mzsql
  materialize=> SET schema = finance;
  SET
  materialize=> SHOW schema;
   schema
  ---------
   finance
  (1 row)

  materialize=> RESET schema;
  RESET
  materialize=> SHOW schema;
   schema
  --------
   public
  (1 row)
  ```

  ```mzsql
   materialize=> SET search_path = finance, public;
   SET
   materialize=> SELECT current_schema;
    current_schema
   ----------------
    finance
   (1 row)

   materialize=> RESET schema;
   RESET
   materialize=> SELECT current_schema;
    current_schema
   ----------------
    public
   (1 row)
  ```

* Add support for new SQL functions:

  | Function                                        | Description                                                                                                 |
  | ----------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
  | [`array_position`](/sql/functions/#array-functions)  | Returns the subscript of the first occurrence of the second argument in the array. `NULL` if not found.     |
  | [`parse_ident`](/sql/functions/#string-functions)    | Splits a qualified identifier into an array of identifiers, removing any quoting of individual identifiers. |

#### Bug fixes and other improvements

* **Breaking change.** Change the `type` associated with progress subsources in
    the `mz_sources` system catalog table from `subsource` to `progress`. This
    change should have no user impact, but please [let us know](https://materialize.com/s/chat)
    if you run into any issues.

* **Breaking change.** Add `oid` and re-order the columns of the `mz_secrets`
    system catalog table. This change should have no user impact, but please
    [let us know](https://materialize.com/s/chat) if you run into any issues.

* Avoid panicking in the absence of the default `materialize` database ([#19874](https://github.com/MaterializeInc/materialize/issues/19874)).

<!-- mz-docs page: releases/v0.58 -->

# Materialize v0.58
## v0.58.0

#### SQL

* Add support for new SQL functions:

  | Function                                        | Description                                                                                                 |
  | ----------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
  | [`datediff`](/sql/functions/datediff/)  | Returns the difference between two date, time or timestamp expressions based on the specified date or time part.     |
  | [`pg_cancel_backend`](/sql/functions/#pg_cancel_backend)    | Cancels an in-progress query on the specified connection ID. Returns whether the connection ID existed. |

* Accept [scalar functions](/sql/functions/#scalar-functions) in the `FROM` clause of a query.

* Add support for the PostgreSQL `IS DISTINCT FROM` operator. This operator
  behaves like `<>`, except that it treats `NULL` like a normal value that
  compares equal to itself and not equal to all other values.

* Allow specifying a comma-separated list of schemas in the `DROP SCHEMA`.

* Add [`mz_internal.mz_object_transitive_dependencies`](/sql/system-catalog/mz_internal/#mz_object_transitive_dependencies)
  to the system catalog. This table describes the transitive dependency structure between all database objects in the system.

* Improve and extend the base implementation of **Role-based
  access control** (RBAC):

  * Allow specifying multiple role names in the [`GRANT ROLE`](/sql/grant-role)
    and [`REVOKE ROLE`](/sql/revoke-role) commands.

  * Add the [`ALTER DEFAULT PRIVILEGES`](/sql/alter-default-privileges/) command,
    which allows users to configure the default privileges for newly created
    objects.

  * Add the `has_system_privilege` function to query role's system privileges,
    which reports if a specified user has a system privilege.

  It's important to note that role-based access control (RBAC) is **disabled by
  default**. You must [contact us](https://materialize.com/contact/) to enable
  this feature in your Materialize region.

<!-- mz-docs page: releases/v0.59 -->

# Materialize v0.59
## v0.59.0

#### Sources and sinks

* Support dropping individual subsources in the [PostgreSQL source](/sql/create-source/postgres/)
using the new `ALTER SOURCE...DROP SUBSOURCE` syntax. Adding subsources will be
supported in the next release.

#### SQL

* Support parsing multi-dimensional arrays, including multi-dimensional empty arrays.

  ```mzsql
  materialize=> SELECT '{{1}, {2}}'::int[];
     arr
  -----------
   {{1},{2}}
  (1 row)
  ```

* Improve and extend the base implementation of **Role-based
  access control** (RBAC):

  * **Breaking change.** Replace role attributes with system privileges, which
      are inheritable and applied system-wide. This change improves the
      usability of RBAC by consolidating the semantics controlling role
      privileges, making it less cumbersome for admin users to grant(or revoke)
      privileges to manipulate top level objects to multiple users.

  * **Breaking change.** Remove the `create_role`, `create_db`, and
      `create_cluster` from the `mz_roles` system catalog table.

  It's important to note that role-based access control (RBAC) is **disabled by
  default**. You must [contact us](https://materialize.com/contact/) to enable
  this feature in your Materialize region.

#### Bug fixes and other improvements

* Make error messages using object names more consistent. In particular, error
  messages now consistently use the fully qualified object name
  (`database_name.schema_name.item_name`).

* **Breaking change.** Disallow `SHOW` commands in the creation of views and
    materialized views ([#20257](https://github.com/MaterializeInc/materialize/issues/20257)). This change should have no user
    impact, but please [let us know](https://materialize.com/s/chat) if you run
    into any issues.

<!-- mz-docs page: releases/v0.60 -->

# Materialize v0.60
## v0.60.0

#### Sources and sinks

* **Private preview.** Support filter pushdown, which can substantially improve
    latency for queries using temporal filters. For an overview of this new
    optimization mechanism, check the [updated documentation](/transform-data/patterns/temporal-filters/#temporal-filter-pushdown).

[//]: # "NOTE(morsapaes) This feature was released in v0.53 behind a feature
flag. The flag was raised in v0.60 -— so mentioning it here."

* Support `FORMAT JSON` for [Kafka sources](/sql/create-source/kafka/).
  This format option automatically decodes messages as `jsonb`, which is a
  quality-of-life improvement over JSON handling using `FORMAT BYTES`.

  **New syntax**

  ```mzsql
  CREATE SOURCE json_source
  FROM KAFKA CONNECTION kafka_connection (TOPIC 'ch_anges')
  FORMAT JSON
  WITH (SIZE = '3xsmall');

  CREATE VIEW extract_json_source AS
  SELECT
    (data->>'field1')::boolean AS field_1,
    (data->>'field2')::int AS field_2,
    (data->>'field3')::float AS field_3
  -- Automatic conversion to jsonb
  FROM json_source;
  ```

  **Old syntax**

  ```mzsql
  CREATE SOURCE json_source
  FROM KAFKA CONNECTION kafka_connection (TOPIC 'ch_anges')
  FORMAT BYTES
  WITH (SIZE = '3xsmall');

  CREATE VIEW extract_json_source AS
  SELECT
    (data->>'field1')::boolean AS field_1,
    (data->>'field2')::int AS field_2,
    (data->>'field3')::float AS field_3
  -- Manual conversion to jsonb
  FROM (SELECT CONVERT_FROM(data, 'utf8')::jsonb AS data FROM json_source);
  ```

#### SQL

* Improve and extend the base implementation of **Role-based
  access control** (RBAC):

  * Restrict granting and revoking [system privileges](/security/access-control/manage-roles/)
    to _superuser_ users with admin privileges.

  It's important to note that role-based access control (RBAC) is **disabled by
  default**. You must [contact us](https://materialize.com/contact/) to enable
  this feature in your Materialize region.

#### Bug fixes and other improvements

* Fix timestamp generation for transactions with multiple statements that could
  lead to crashes ([#20267](https://github.com/MaterializeInc/materialize/issues/20267)).

<!-- mz-docs page: releases/v0.61 -->

# Materialize v0.61
## v0.61.0

[//]: # "NOTE(morsapaes) v0.61 includes a first version of webhook sources
released behind a feature flag."

#### SQL

* Improve and extend the base implementation of **Role-based
  access control** (RBAC):

  * Include `GRANT`, `REVOKE`, `ALTER DEFAULT PRIVILEGES`, and `ALTER OWNER`
    events in the [`mz_audit_events`](/sql/system-catalog/mz_catalog/#mz_audit_events)
    system catalog table.

  * Require connection and secret `USAGE` privileges to execute [`CREATE SINK`](/sql/create-sink/)
    commands.

  It's important to note that role-based access control (RBAC) is **disabled by
  default**. You must [contact us](https://materialize.com/contact/) to enable
  this feature in your Materialize region.

#### Bug fixes and other improvements

* Do not require a valid active cluster to run specific types of queries, like
  `SELECT n` health checks ([#20420](https://github.com/MaterializeInc/materialize/issues/20420)). This fixes a known issue in the
  `dbt-materialize` adapter, where specific commands that run such queries as
  part of their execution (e.g. `dbt debug`) would fail in the absence of the
  pre-installed `default` cluster.

* Extend `pg_catalog` and `information_schema` system catalog coverage for
  compatibility with external tools like DBeaver and PopSQL ([#20429](https://github.com/MaterializeInc/materialize/issues/20429))
  ([#20314](https://github.com/MaterializeInc/materialize/issues/20314)) ([#20427](https://github.com/MaterializeInc/materialize/issues/20427)).

* Avoid panicking in the presence of concurrent DDL and `UPDATE`, `DELETE`, or
  `INSERT INTO` statements ([#20420](https://github.com/MaterializeInc/materialize/issues/20420)).

<!-- mz-docs page: releases/v0.62 -->

# Materialize v0.62
## v0.62.0

#### Sources and sinks

* Support adding individual subsources in the [PostgreSQL source](/sql/create-source/postgres/)
  using the new `ALTER SOURCE...ADD SUBSOURCE` syntax.

#### SQL

* Add the [`try_parse_monotonic_iso8601_timestamp`](/sql/functions/pushdown/)
  function, which should be used in temporal filters involving `string` timestamps
  (e.g. extracted from `jsonb` columns) to benefit from [filter pushdown optimization](/transform-data/patterns/temporal-filters/#temporal-filter-pushdown).

  For a given JSON-formatted source, the following query cannot
  benefit from filter pushdown:

  ```mzsql
  SELECT *
  FROM foo
  WHERE (data ->> 'timestamp')::timestamp > mz_now();
  ```

  But can be optimized as:

  ```mzsql
  SELECT *
  FROM foo
  WHERE try_parse_monotonic_iso8601_timestamp(data ->> 'timestamp') > mz_now();
  ```

  It's important to note that temporal filter pushdown is **disabled by
  default**. You must [contact us](https://materialize.com/contact/) to enable
  this feature in your Materialize region.

* Improve and extend the base implementation of **Role-based
  access control** (RBAC):

  * Add the `pg_has_role` function, which reports if a specified `user` has
    `USAGE` or `MEMBER` privileges for a specified `role`.

  It's important to note that role-based access control (RBAC) is **disabled by
  default**. You must [contact us](https://materialize.com/contact/) to enable
  this feature in your Materialize region.

#### Bug fixes and other improvements

* Extend `information_schema` system catalog coverage with RBAC-specific views:

  * [`applicable_roles`](https://www.postgresql.org/docs/15/infoschema-applicable-roles.html)
  * [`enabled_roles`](https://www.postgresql.org/docs/15/infoschema-enabled-roles.html)
  * [`role_table_grants`](https://www.postgresql.org/docs/15/infoschema-role-table-grants.html)
  * [`table_privileges`](https://www.postgresql.org/docs/15/infoschema-table-privileges.html)

<!-- mz-docs page: releases/v0.63 -->

# Materialize v0.63
## v0.63.0

#### SQL

* Improve and extend the base implementation of **Role-based
  access control** (RBAC):

  * Require `USAGE` privileges on the schemas of all connections, secrets, and types used in a query.

  * Add system catalog views that present privileges and role memberships using
    human-readable names instead of identifiers. Each view has two variants:
    one that presents all privileges or roles, and another that only presents
    privileges and roles that contain the current role.

    **Privileges**

    * [`mz_internal.mz_show_all_privileges`](/sql/system-catalog/mz_internal/#mz_show_all_privileges)
    * [`mz_internal.mz_show_[my_]cluster_privileges`](/sql/system-catalog/mz_internal/#mz_show_cluster_privileges)
    * [`mz_internal.mz_show_[my_]database_privileges`](/sql/system-catalog/mz_internal/#mz_show_database_privileges)
    * [`mz_internal.mz_show_[my_]default_privileges`](/sql/system-catalog/mz_internal/#mz_show_default_privileges)
    * [`mz_internal.mz_show_[my_]object_privileges`](/sql/system-catalog/mz_internal/#mz_show_object_privileges)
    * [`mz_internal.mz_show_[my_]schema_privileges`](/sql/system-catalog/mz_internal/#mz_show_schema_privileges)
    * [`mz_internal.mz_show_[my_]system_privileges`](/sql/system-catalog/mz_internal/#mz_show_system_privileges)

    **Roles**

    * [`mz_internal.mz_show_[my_]role_members`](/sql/system-catalog/mz_internal/#mz_show_role_members)

  It's important to note that role-based access control (RBAC) is **disabled by
  default**. You must [contact us](https://materialize.com/contact/) to enable
  this feature in your Materialize region.

#### Bug fixes and other improvements

* Add the `max_query_result_size` [configuration parameter](https://materialize.com/docs/sql/show/#other-configuration-parameters),
which allows limiting the size in bytes of a single query’s result.

* Support most single DDL statements in explicit transactions. This improves the
  integration experience with external tools like [Deepnote](https://deepnote.com/)
  and [Hex](https://hex.tech/).

<!-- mz-docs page: releases/v0.64 -->

# Materialize v0.64
## v0.64.0

#### SQL

* Improve and extend the base implementation of **Role-based
  access control** (RBAC):

  * Require specifying a target role in the `ALTER DEFAULT PRIVILEGES` command.
    Previously, the target role was optional and defaulted to the current role,
    which is seldom what users intend to achieve with this command.

  * Add the `has_role` function as an alias to `pg_has_role`. This function
    reports if a specified `user` has `USAGE` or `MEMBER` privileges for a
    specified `role`.

  It's important to note that role-based access control (RBAC) is **disabled by
  default**. You must [contact us](https://materialize.com/contact/) to enable
  this feature in your Materialize region.

#### Bug fixes and other improvements

* Fix a bug that let users specify the `DETAILS` option when creating a
  [PostgreSQL source](/sql/create-source/postgres/) ([#20944](https://github.com/MaterializeInc/materialize/issues/20944)).

* Extend support for single DDL statements in explicit transactions to the
  `ALTER` and `DROP` commands. This improves the integration experience with
  external tools like [Deepnote](https://deepnote.com/) and [Hex](https://hex.tech/).

<!-- mz-docs page: releases/v0.65 -->

# Materialize v0.65
## v0.65.0

#### SQL

* **Breaking change.** Limit the length of object identifiers to 255 bytes.

* Include the name and size of cluster replicas in the output of
  [`SHOW CLUSTERS`](/sql/show-clusters/) as a new column named `replicas`.

* Improve and extend the base implementation of **Role-based
  access control** (RBAC):

  * Add the [`SHOW ROLES`](/sql/show-roles/) command, which lists the roles
    available in the system.

  It's important to note that role-based access control (RBAC) is **disabled by
  default**. You must [contact us](https://materialize.com/contact/) to enable
  this feature in your Materialize region.

* Add [`mz_internal.mz_object_fully_qualified_names`](/sql/system-catalog/mz_internal/#mz_object_fully_qualified_names)
  and [`mz_internal.mz_object_lifetimes`](/sql/system-catalog/mz_internal/#mz_object_lifetimes)
  to the system catalog. These views enrich [`mz_objects`](/sql/system-catalog/mz_catalog/#mz_objects)
  with namespace and lifetime event information, respectively.

* Add [`mz_internal.mz_expected_group_size_advice`](/sql/system-catalog/mz_introspection/#mz_expected_group_size_advice)
  to the system catalog. This view provides advice on opportunities to set the
  `EXPECTED GROUP SIZE` [query hint](https://materialize.com/docs/sql/select/#query-hints).

#### Bug fixes and other improvements

* **Breaking change.** Disallow executing functions from the `mz_internal`
    schema ([#20998](https://github.com/MaterializeInc/materialize/issues/20998)). This change should have no user impact, but
    please [let us know](https://materialize.com/s/chat) if you run into any
    issues.

<!-- mz-docs page: releases/v0.66 -->

# Materialize v0.66
## v0.66.0

This release focuses on stabilization work and performance improvements. It does
not introduce any new user-facing features. 👷

#### Bug fixes and other improvements

* Fix a bug that prevented [`ALTER SOURCE...`](/sql/alter-source/) from
  completing in PostgreSQL sources when existing tables were listed in a
  publication in a different order than that observed when Materialize first
  processed them.

<!-- mz-docs page: releases/v0.67 -->

# Materialize v0.67
## v0.67.0

#### Sources and sinks

[//]: # "NOTE(morsapaes) This feature was released in v0.53 behind a feature
flag. The flag was raised in v0.67 for ENVELOPE UPSERT -— so mentioning it
here."

* Support upserts in the output of `SUBSCRIBE` via the new [`ENVELOPE UPSERT` clause](/sql/subscribe/#envelope-upsert).
  This clause allows you to specify a `KEY` that Materialize uses to interpret the
  rows as a series of inserts, updates and deletes within each distinct
  timestamp. The output rows will have the following structure:

  ```mzsql
   SUBSCRIBE mview ENVELOPE UPSERT (KEY (key));

   mz_timestamp | mz_state | key  | value
   -------------|----------|------|--------
   100          | upsert   | 1    | 2
   100          | upsert   | 2    | 4
  ```

#### SQL

* Add [`mz_internal.mz_compute_dependencies`](/sql/system-catalog/mz_internal/#mz_compute_dependencies)
  to the system catalog. This table describes the dependency structure between
  each compute object (index, materialized view, or subscription) and the
  sources of its data.

* Improve the output of [`EXPLAIN { OPTIMIZED | PHYSICAL } PLAN FOR MATERIALIZED VIEW`](/sql/explain-plan/)
  to return the plan generated at object creation time, rather than the plan that
  would be generated if the object was created with the current catalog state.

* Add support for [`TABLE`](/sql/table) expressions, which retrieve all rows
  from the named SQL table.

#### Bug fixes and other improvements

* Extend `pg_catalog` and `information_schema` system catalog coverage for
  compatibility with Power BI.

* Increase in precision for the `AVG`, `VAR_*`, and `STDDEV*` functions.

<!-- mz-docs page: releases/v0.68 -->

# Materialize v0.68
## v0.68.0

[//]: # "NOTE(morsapaes) v0.68 includes a first version of the COMMENT ON syntax
released behind a feature flag."

#### SQL

* Enable Role-based access control (RBAC) for all new environments. Check the
  [updated documentation](/security/access-control/) for guidance on setting up
  RBAC in your Materialize organization.

* Extend the [`EXPLAIN PLAN`](/sql/explain-plan/) syntax to allow explaining
  plans used for index maintenance.

#### Bug fixes and other improvements

* Extend `pg_catalog` and `information_schema` system catalog coverage for
  compatibility with Power BI.

<!-- mz-docs page: releases/v0.69 -->

# Materialize v0.69
## v0.69.0

#### Sources and sinks

[//]: # "NOTE(morsapaes) This feature was released in v0.59 behind a feature
flag. The flag was raised in v0.69 — so mentioning it here."

* Support validating the parameters provided in a `CREATE CONNECTION` statement
  against the target external system. For most connection types,
  Materialize **automatically validates** connections on creation.

  For connection types that require additional setup steps after creation
  (AWS PrivateLink, SSH tunnel), you can **manually validate** connections
  using the new [`VALIDATE CONNECTION`](https://materialize.com/docs/sql/validate-connection/)
  syntax:

   ```mzsql
   VALIDATE CONNECTION ssh_connection;
   ```

#### SQL

* Add support for new SQL functions:

  | Function                                                           | Description                                                 |
  | ------------------------------------------------------------------ | ----------------------------------------------------------- |
  | [`mz_is_superuser`](/sql/functions/#access-privilege-inquiry-functions) |  Reports whether the current role is a _superuser_ with administration privileges in Materialize. |
  | [`regexp_replace`](/sql/functions/#string-functions) | Replaces the first occurrence of the specified regular expression in a string with the specified replacement string.    |
  | [`regexp_split_to_array`](/sql/functions/#string-functions)      | Splits a string by the specified regular expression into an array. |
  | [`regexp_split_to_table`](/sql/functions/#table-functions)       | Splits a string by the specified regular expression.               |

<br>

* Add the `IN CLUSTER` option to the `SHOW { SOURCES | SINKS }` commands to
  restrict the objects listed to a specific cluster.

  ```mzsql
  SHOW SOURCES;
  ```
  ```nofmt
              name    | type     | size  | cluster
  --------------------+----------+-------+---------
   my_kafka_source    | kafka    |       | c1
   my_postgres_source | postgres |       | c2
  ```

  ```mzsql
  SHOW SOURCES IN CLUSTER c2;
  ```
  ```nofmt
  name       | type  | size     | cluster
  -----------+-------+----------+--------
  my_postgres_source | postgres | c2
  ```

* Make the syntax for [`GROUP SIZE` query hints](/transform-data/optimization/#query-hints)
  more intuitive by deprecating the `EXPECTED GROUP SIZE` hint and introducing
  three new hints: `AGGREGATE INPUT GROUP SIZE`, `DISTINCT ON INPUT GROUP SIZE`
  and `LIMIT INPUT GROUP SIZE`; which more clearly map to the target operation
  to optimize.

  The old `EXPECTED GROUP SIZE` hint is still supported for backwards
  compatibility, but its use is discouraged.

* Add `savings` to the [`mz_internal.mz_expected_group_size_advice`](/sql/system-catalog/mz_introspection/#mz_expected_group_size_advice)
  system catalog table. This column provides a conservative estimate of the memory
  savings that can be expected by using [`GROUP SIZE` query hints](/transform-data/optimization/#query-hints).

#### Bug fixes and other improvements

* Support SQL parameters in `SUBSCRIBE` and `DECLARE` statements.

<!-- mz-docs page: releases/v0.70 -->

# Materialize v0.70
## v0.70.0

#### Sources and sinks

* Automatically check if there are tables not currently configured to use `REPLICA IDENTITY FULL` in a publication used with a [PostgreSQL source](/sql/create-source/postgres/).

* Support constraining the precision of the fractional seconds in timestamps. This allows users to construct Avro-formatted sinks that use the `timestamp-millis` logical type instead of the `timestamp-micros` logical type.

#### Bug fixes and other improvements

* Limit the amount of data that can be copied using `COPY FROM` to 1 GiB. Please [contact us](https://materialize.com/contact/) if you need this limit increased in your Materialize region.

* Restrict transactions to execute on a single cluster, in order to improve use case isolation. The first query in a transaction now determines the time domain of the entire transaction ([#21854](https://github.com/MaterializeInc/materialize/issues/21854)).

<!-- mz-docs page: releases/v0.71 -->

# Materialize v0.71
## v0.71.0

[//]: # "NOTE(morsapaes) v0.71 shipped setting configuration parameters for roles
behind a feature flag."

#### Sources and sinks

* Support using the new `NULL DEFAULTS` option in Avro-formatted [Kafka sinks](/sql/create-sink/).
When specified, this option will generate an Avro schema where every nullable
field has a default of `NULL`.

#### SQL

* Add the [`EXPLAIN CREATE { MATERIALIZED VIEW | INDEX }`](/sql/explain-plan/#explained-object)
syntax options, which allow exploring what plan Materialize would create if one
were to re-create the object with the current catalog state.

<!-- mz-docs page: releases/v0.72 -->

# Materialize v0.72
## v0.72.0

#### Bug fixes and other improvements

* Refactor [`mz_internal.mz_dataflow_arrangement_sizes`](/sql/system-catalog/mz_introspection/#mz_dataflow_arrangement_sizes)
to include **all active dataflows**, not just the ones referenced from the
system catalog. This makes debugging issues like high memory usage caused by
arrangements more intuitive for users.

<!-- mz-docs page: releases/v0.73 -->

# Materialize v0.73
## v0.73.0

[//]: # "NOTE(morsapaes) v0.73 shipped the ASSERT NOT NULL option for sinks
behind a feature flag."

#### Sources and sinks

* **Private preview.** Allow propagating comments in materialized views to the
    Avro schema of [Kafka sinks](/sql/create-sink/kafka/), as well as manually
    specifying comments using the new `[KEY|VALUE] DOC ON
    [TYPE|COLUMN] <identifier>` [connection option](/sql/create-sink/kafka/#syntax).

    **Example:**

	```mzsql
	CREATE TABLE t (c1 int, c2 text);
	COMMENT ON TABLE t IS 'materialize comment on t';
	COMMENT ON COLUMN t.c2 IS 'materialize comment on t.c2';

	CREATE SINK avro_sink
	  IN CLUSTER my_io_cluster
	  FROM t
	  INTO KAFKA CONNECTION kafka_connection (TOPIC 'test_avro_topic')
	  KEY (c1)
	  FORMAT AVRO USING CONFLUENT SCHEMA REGISTRY CONNECTION csr_connection
	  (
	    DOC ON TYPE t = 'top-level comment for avro record in both key and value schemas',
	    KEY DOC ON COLUMN t.c1 = 'comment on column only in key schema',
	    VALUE DOC ON COLUMN t.c1 = 'comment on column only in value schema'
	  )
	  ENVELOPE UPSERT;
	```

	**Key schema:**
	```json
	{
	  "type": "record",
	  "name": "row",
	  "doc": "this is a materialized view",
	  "fields" : [
	    {"name": "a", "type": "string", "doc": "this is column a"},
	    {"name": "b", "type": "string"}
	  ]
	}{
	  "type": "record",
	  "name": "row",
	  "doc": "top-level comment for avro record in both key and value schemas",
	  "fields": [
	    {
	      "name": "c1",
	      "type": [
	        "null",
	        "int"
	      ],
	      "doc": "comment on column only in key schema"
	    }
	  ]
	}
	```

	**Value schema:**

	```json
	{
	  "type": "record",
	  "name": "envelope",
	  "doc": "top-level comment for avro record in both key and value schemas",
	  "fields": [
	    {
	      "name": "c1",
	      "type": [
	        "null",
	        "int"
	      ],
	      "doc": "comment on column only in value schema"
	    },
	    {
	      "name": "c2",
	      "type": [
	        "null",
	        "string"
	      ],
	      "doc": "materialize comment on t.c2"
	    }
	  ]
	}
	```

#### Bug fixes and other improvements

* Allow the value of the `SASL MECHANISM` option for [Kafka connections](/sql/create-connection/#kafka)
to be specified in any case style. Previously, Materialize only accepted
uppercase case style (as required by `librdkafka`).

<!-- mz-docs page: releases/v0.74 -->

# Materialize v0.74
## v0.74.0

[//]: # "NOTE(morsapaes) v0.74 shipped the ALTER SCHEMA...RENAME command behind
a feature flag. This work makes progress towards supporting blue/green
deployments."

#### SQL

* Bring back support for [window aggregations](/sql/functions/#window-functions), or
  aggregate functions (e.g., `sum`, `avg`) that use an `OVER` clause.

  ```mzsql
  CREATE TABLE sales(time int, amount int);

  INSERT INTO sales VALUES (1,3), (2,6), (3,1), (4,5), (5,5), (6,6);

  SELECT time, amount, SUM(amount) OVER (ORDER BY time) AS cumulative_amount
  FROM sales
  ORDER BY time;

   time | amount | cumulative_amount
  ------+--------+-------------------
      1 |      3 |                 3
      2 |      6 |                 9
      3 |      1 |                10
      4 |      5 |                15
      5 |      5 |                20
      6 |      6 |                26
  ```

  For an overview of window function support, check the [updated documentation](/transform-data/patterns/window-functions/).

* Add support for new `SHOW` commands related to [role-based access control](/security/cloud/access-control/#role-based-access-control-rbac) (RBAC):

  | Command                                                    | Description                                          |
  | ---------------------------------------------------------- | ---------------------------------------------------- |
  | [`SHOW PRIVILEGES`](/sql/show-privileges/)                 | Lists the privileges granted on all objects.         |
  | [`SHOW ROLE MEMBERSHIP`](/sql/show-role-membership/)       | Lists the members of each role.                      |
  | [`SHOW DEFAULT PRIVILEGES`](/sql/show-default-privileges/) | Lists any default privileges granted on any objects. |

#### Bug fixes and other improvements

* Improve error message for possibly mistyped column names, suggesting similarly
  named columns if the one specified cannot be found.

  ```mzsql
  CREATE SOURCE case_sensitive_names
  FROM POSTGRES CONNECTION pg (
    PUBLICATION 'mz_source',
    TEXT COLUMNS [pk_table."F2"]
  )
  FOR TABLES (
    "enum_table"
  );
  contains: invalid TEXT COLUMNS option value: column "pk_table.F2" does not exist
  hint: The similarly named column "pk_table.f2" does exist.
  ```

* Fix a bug where `ASSERT NOT NULL` options on materialized views were not
  persisted across restarts of the environment.

<!-- mz-docs page: releases/v0.75 -->

# Materialize v0.75
## v0.75.0

#### SQL

* Support [`ALTER [ CLUSTER | SCHEMA ] SWAP`](/sql/alter-swap/), which allows
  atomically renaming clusters and schemas. This is useful in the context of
  [Blue/Green deployments](/manage/blue-green/).

* Change the semantics and schema of the [`mz_internal.mz_frontiers`](https://materialize.com/docs/sql/system-catalog/mz_internal/#mz_frontiers)
  system catalog table, and add the [`mz_internal.mz_cluster_replica_frontiers`](https://materialize.com/docs/sql/system-catalog/mz_internal/#mz_cluster_replica_frontiers)
  system catalog table. These objects are mostly useful to support existing and
  upcoming features in Materialize.

#### Bug fixes and other improvements

* Remove the requirement of `USAGE` privileges on types for `SELECT` and
  `EXPLAIN` statements.

<!-- mz-docs page: releases/v0.76 -->

# Materialize v0.76
## v0.76.0

#### Sources and sinks

* Allow specifying a default SSH connection when creating a [Kafka connection over SSH](https://materialize.com/docs/sql/create-connection/#ssh-tunnel-t1)
  using the `SSH TUNNEL` top-level option. The default connection will be used
  to connect to any new or unlisted brokers.

  ```mzsql
  CREATE CONNECTION kafka_connection TO KAFKA (
      BROKER 'broker1:9092',
      SSH TUNNEL ssh_connection
  );
  ```

* Support previewing the Avro schema that will be generated for an
  Avro-formatted [Kafka sink](/sql/create-sink/kafka/) ahead of sink creation
  using the [`EXPLAIN { KEY | VALUE } SCHEMA`](/sql/explain-schema/) syntax.

#### Bug fixes and other improvements

* Improve [connection validation](/sql/create-connection/#connection-validation)
  for Confluent Schema Registry connections. Materialize will now attempt to
  connect to the identified service, rather than only building the client during
  validation.

<!-- mz-docs page: releases/v0.77 -->

# Materialize v0.77
## v0.77.0

#### Sources and sinks

* Support the `now()` function in the `CHECK` expression of [webhook sources](/sql/create-source/webhook/).
  This allows rejecting requests when a timestamp included in the headers is too
  far behind Materialize's clock, which is often recommended by webhook providers to
  help revent replay attacks.

  **Example**

  ```mzsql
  CREATE SOURCE webhook_with_time_based_rejection
  IN CLUSTER webhook_cluster
  FROM WEBHOOK
	  BODY FORMAT TEXT
	  CHECK (
	    WITH (HEADERS)
	    (headers->'timestamp'::text)::timestamp + INTERVAL '30s' >= now()
	  );
  ```

#### SQL

* Support using timezone abbreviations in contexts where timezone input is accepted.

  **Example**

  ```mzsql
  SELECT timezone_offset('America/New_York', '2023-11-05T06:00:00+00')
  ----
  (EST,-05:00:00,00:00:00)
  ```

* Add [`mz_internal.mz_materialization_lag`](/sql/system-catalog/mz_internal/#mz_materialization_lag)
  to the system catalog. This view describes the difference between the input
  frontiers and the output frontier for each materialized view, index, and sink
  in the system. For hydrated dataflows, this lag roughly corresponds to the time
  it takes for updates at the inputs to be reflected in the output.

#### Bug fixes and other improvements

* **Breaking change.** Fix timezone offset parsing ([#22896](https://github.com/MaterializeInc/materialize/issues/22896)) and remove
    support for the `time` type ([#22960](https://github.com/MaterializeInc/materialize/issues/22960)) in the `timezone` function
    and the `AT TIME ZONE` operator. These changes follow the PostgreSQL
    specification.

* Extend `pg_catalog` system catalog coverage to include the
  [`pg_timezone_abbrevs`](https://www.postgresql.org/docs/current/view-pg-timezone-abbrevs.html) and [`pg_timezone_names`](https://www.postgresql.org/docs/current/view-pg-timezone-names.html) views.
  This is useful to support custom timezone abbreviation logic while timezone
  support doesn't land in Materialize.

* Improve the output format of [`EXPLAIN...PLAN AS TEXT`](/sql/explain-plan/) when the `humanized_exprs`
  [output modifier](/sql/explain-plan/#output-modifiers) to avoid ambiguities when
  multiple columns have the same name.

<!-- mz-docs page: releases/v0.78 -->

# Materialize v0.78
## v0.78.0

#### Sources and sinks

* **Breaking change.** Use `SSL` as the default security protocol in Kafka
    connections when no `SSL...` or `SASL...` options are specified.
    Previously, `PLAINTEXT` was used as the default.

* Add support for the `PLAINTEXT` and `SASL_PLAINTEXT` security protocols for
  Kafka connections.

* Allow Kafka connections to enable the `SSL` security protocol without enabling
  TLS client authentication (i.e., using TLS only for encryption).

* Add the [`INCLUDE HEADER` option](/sql/create-source/kafka/#headers) to Kafka
sources, which allows extracting individual headers from Kafka messages and
expose them as columns of the source.

  ```mzsql
  CREATE SOURCE kafka_metadata
    FROM KAFKA CONNECTION kafka_connection (TOPIC 'data')
    FORMAT AVRO USING CONFLUENT SCHEMA REGISTRY CONNECTION csr_connection
    INCLUDE HEADER 'c_id' AS client_id, HEADER 'key' AS encryption_key BYTES,
    ENVELOPE NONE
  ```

  ```mzsql
  SELECT
      id,
      seller,
      item,
      client_id::numeric,
      encryption_key
  FROM kafka_metadata;

  id | seller |        item        | client_id |    encryption_key
  ----+--------+--------------------+-----------+----------------------
    2 |   1592 | Custom Art         |        23 | \x796f75207769736821
    3 |   1411 | City Bar Crawl     |        42 | \x796f75207769736821
```

#### SQL

* Add [`mz_timezone_names`](/sql/system-catalog/mz_catalog/#mz_timezone_names)
and [`mz_timezone_abbreviations`](/sql/system-catalog/mz_catalog/#mz_timezone_abbreviations)
to the system catalog. These views contains a row for each supported timezone
and each supported timezone abbreviation, respectively.

<!-- mz-docs page: releases/v0.79 -->

# Materialize v0.79
## v0.79.0

#### Sources and sinks

* For [PostgreSQL sources](https://materialize.com/docs/sql/create-source/postgres/),
  prevent the creation of new sources when the upstream database does not have a
  sufficient number of replication slots available.

* Fix a bug where subsources where created in the active schema, rather than the
  schema of the source, when using the `FOR SCHEMAS` option in
  [PostgreSQL sources](https://materialize.com/docs/sql/create-source/postgres/).

* Add [`mz_aws_privatelink_connection_status_history`](/sql/system-catalog/mz_internal/#mz_aws_privatelink_connection_status_history)
  to the system catalog. This table contains a row describing the historical
  status for each [AWS PrivateLink connection](/sql/create-connection/#aws-privatelink)
  in the system.

#### SQL

* Add [`mz_compute_hydration_status`](/sql/system-catalog/mz_internal/#mz_compute_hydration_statuses)
  to the system catalog. This table describes the per-replica hydration status of
  indexes, materialized views, or subscriptions, which is useful to track when
  objects are "caught up" in the context of [blue/green deployments](/manage/blue-green).

* Add `create_sql` to object-specific tables in `mz_catalog`(_e.g._ `mz_sources`).
  This column provides the DDL used to create the object.

* Allow calling functions from the `mz_internal` schema, which are considered
  safe but unstable (_e.g._ `is_rbac_enabled`).

#### Bug fixes and other improvements

* Improve type coercion in `WITH MUTUALLY RECURSIVE` common table expressions. For
  example, you can now return `NUMERIC` values of arbitrary scales (_e.g._ `NUMERIC
  (38,2)` for columns defined as `NUMERIC`.

* Automatically enable compaction when creating the progress topic for a Kafka
  sink. **Warning:** Versions of Redpanda before v22.3 do not support using
  compaction for Materialize's progress topics. You need to manually create the
  connection's progress topic with compaction disabled to use sinks with these
  versions of Redpanda.

<!-- mz-docs page: releases/v0.80 -->

# Materialize v0.80
## v0.80.0

[//]: # "NOTE(morsapaes) v0.80 shipped support for expressions in the LIMIT
clause and AWS connections behind a feature flag."

#### Sources and sinks

* **Breaking change.** Disallow specifying more starting offsets than the number
    of partitions for [Kafka sources](/sql/create-source/kafka/#setting-start-offsets).

* Allow configuring the group ID (`GROUP ID PREFIX`) for [Kafka sources](/sql/create-source/kafka/),
  and the group ID and transactional ID (`TRANSACTIONAL ID PREFIX`, `PROGRESS GROUP ID PREFIX`)
  for [Kafka sinks](/sql/create-sink/kafka/#syntax)).

#### SQL

* Add `statement_kind` to `mz_internal.mz_activity_log`.
This column provides the type of the logged statement, e.g. `select` for a
`SELECT` query, or `NULL` if the statement was empty.

* Add [mz_internal.mz_notices](/sql/system-catalog/mz_internal/#mz_notices) to
  the system catalog. This view contains a list of currently active notices
  emitted by the system, and requires `superuser` privileges for querying.

#### Bug fixes and other improvements

* Allow bare references to tables, views, and sources whose name matches the
  name of a type.

<!-- mz-docs page: releases/v0.81 -->

# Materialize v0.81
## v0.81.0

[//]: # "NOTE(morsapaes) v0.81 shipped a stub implementation of the MySQL source
behind a feature flag."

#### SQL

* Allow _superusers_ to modify the default value for certain [configuration parameters](/sql/set/#other-configuration-parameters)
  globally (i.e. for all users) using the[`ALTER SYSTEM...SET`](/sql/alter-system-set/)
  command.

* Support user-configured data retention for materialized views and sources
  (excluding multi-output sources, i.e. PostgreSQL sources) via the new `RETAIN
  HISTORY` syntax. Support in multi-output sources will be added in a future
  release.

* Add [`mz_hydration_statuses`](/sql/system-catalog/mz_internal/#mz_hydration_statuses)
  to the system catalog. This view describes the per-replica hydration status of
  each object powered by a dataflow.

#### Bug fixes and other improvements

* Rename `mz_compute_hydration_status` to [`mz_compute_hydration_statuses`](/sql/system-catalog/mz_internal/#mz_compute_hydration_statuses),
  for consistency with other objects in the system catalog.

* Fix a bug in which Avro-formatted Kafka sources could fail to decode records
  if the reader schema contained a field with a logical type of
  `timestamp-millis`, `timestamp-micros`, or `date` with a default value
  ([#24094](https://github.com/MaterializeInc/materialize/issues/24094)).

<!-- mz-docs page: releases/v0.82 -->

# Materialize v0.82
## v0.82.0

[//]: # "NOTE(morsapaes) v0.82 shipped support for REFRESH options in
materialized views and statement lifecycle logging behind a feature flag."

#### Bug fixes and other improvements

* Rename the [pre-installed cluster](/sql/show-clusters/#pre-installed-clusters)
  from `default` to `quickstart` for **new** Materialize regions. In existing
  regions where the pre-installed cluster has not been renamed or dropped, this
  cluster retains the `default` name.

<!-- mz-docs page: releases/v0.83 -->

# Materialize v0.83
## v0.83

#### Sources and sinks

* Improve status reporting for [PostgreSQL sources](/sql/create-source/postgres/)
  by ensuring definite errors (e.g. dropping a publication upstream) are exposed.

#### Bug fixes and other improvements

* Prevent users from creating indexes on system catalog objects. If you're using
  these objects in a context that requires indexing, we recommend creating a
  view over the catalog objects, and indexing that view instead.

  ```mzsql
  CREATE VIEW mz_objects_indexed AS
  SELECT  o.id AS object_id,
          s.name AS schema_name
  FROM mz_objects o
  LEFT JOIN mz_schemas s ON o.schema_id = s.id;

  CREATE INDEX cara_tmp_i on mz_objects_indexed (object_id);
  ```

* Fix a bug that allowed users to configure clusters containing storage objects
  (i.e., sources, sinks) with more than one replica. This is an unsupported
  state, since such clusters can, at most, have `REPLICATION FACTOR = 1`.

<!-- mz-docs page: releases/v0.84 -->

# Materialize v0.84
## v0.84

#### Sources and sinks

* **Breaking change.** Deprecate the `SIZE` option for sources and sinks, which
    transparently created a (linked) cluster to maintain the object. Use the
    `IN CLUSTER` clause to create a source or sink in a specific a cluster. If
    you omit the clause altogether, the object will be created in the active
    cluster for the session.

  **New syntax**

  ```mzsql
  --Create the object in a specific cluster
  CREATE SOURCE json_source
  IN CLUSTER some_cluster
  FROM KAFKA CONNECTION kafka_connection (TOPIC 'ch_anges')
  FORMAT JSON;

  --Create the object in the active cluster
  CREATE SOURCE json_source
  FROM KAFKA CONNECTION kafka_connection (TOPIC 'ch_anges')
  FORMAT JSON;
  ```

  **Deprecated syntax**

  ```mzsql
  --Create the object in a dedicated (linked) cluster
  CREATE SOURCE json_source
  FROM KAFKA CONNECTION kafka_connection (TOPIC 'ch_anges')
  FORMAT JSON
  WITH (SIZE = '3xsmall');
  ```

* Make timeouts (`transaction.timeout.ms`) configurable for
  [Kafka sinks](https://materialize.com/docs/sql/create-sink/). Default: 60000ms.

#### Bug fixes and other improvements

* Fix query results that rely on static views with temporal filters ([#24408](https://github.com/MaterializeInc/materialize/issues/24408)).

<!-- mz-docs page: releases/v0.85 -->

# Materialize v0.85
## v0.85

#### SQL

* Add [`mz_internal.mz_recent_activity_log`](/sql/system-catalog/mz_internal/#mz_recent_activity_log)
  to the system catalog. This view contains a log of the SQL statements that have
  been issued to Materialize in the past 3 days, along with various metadata
  about them. Querying this view is typically much faster than querying
  `mz_internal.mz_activity_log`.

#### Bug fixes and other improvements

* Fix a bug where [`DISCARD ALL`](/sql/discard/) did not consider system or role
  defaults ([#24601](https://github.com/MaterializeInc/materialize/issues/24601)).

* Fix a bug causing the `mz_monitor` and `mz_monitor_redacted` system roles to
  not show up in the `mz_roles` system catalog table ([#24617](https://github.com/MaterializeInc/materialize/issues/24617)).

<!-- mz-docs page: releases/v0.86 -->

# Materialize v0.86
## v0.86

#### Sources and sinks

* Add support for [handling batched events](https://materialize.com/docs/sql/create-source/webhook/#handling-batch-events)
  in the webhook source via the new `JSON ARRAY` format.

  ```mzsql
  CREATE SOURCE webhook_source_json_batch IN CLUSTER my_cluster FROM WEBHOOK
  BODY FORMAT JSON ARRAY
  INCLUDE HEADERS;
  ```

  ```
  POST webhook_source_json_batch
  [
    { "event_type": "a" },
    { "event_type": "b" },
    { "event_type": "c" }
  ]
  ```

  ```mzsql
  SELECT COUNT(body) FROM webhook_source_json_batch;
  ----
  3
  ```

* Decrease memory utilization for [unpacking Kafka headers](https://materialize.com/docs/sql/create-source/kafka/#headers).
  Use the new `mapbuild` function to turn all headers exposed via `INCLUDE
  HEADERS` into a `map`, which makes it easier to extract header values.

   ```mzsql
   SELECT
       id,
       seller,
       item,
       convert_from(mapbuild(headers)->'client_id', 'utf-8') AS client_id,
       mapbuild(headers)->'encryption_key' AS encryption_key,
   FROM kafka_metadata;

    id | seller |        item        | client_id |    encryption_key
   ----+--------+--------------------+-----------+----------------------
     2 |   1592 | Custom Art         |        23 | \x796f75207769736821
     3 |   1411 | City Bar Crawl     |        42 | \x796f75207769736821
   ```

#### SQL

* Add support for new SQL functions:

  | Function                                        | Description                                                                                                 |
  | ----------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
  | [`mapbuild`](/sql/functions/#map_build) | Builds a map from a list of records whose fields are two elements, the first of which is `text`.     |
  | [`map_agg`](/sql/functions/#map_agg)    | Aggregate keys and values (including nulls) as a map. |

#### Bug fixes and other improvements

* Mitigate queue saturation is Kafka sinks ([#24871](https://github.com/MaterializeInc/materialize/issues/24871)).

* Fix a correctness issue with subqueries that referred to ungrouped columns
  when columns of the same name existed in an outer scope ([#24354](https://github.com/MaterializeInc/materialize/issues/24354)).

* Fix casts from interval to time for large negative intervals ([#24795](https://github.com/MaterializeInc/materialize/issues/24795)).

* Prevent `INSERT`s with table references in `VALUES` in transactions ([#24697](https://github.com/MaterializeInc/materialize/issues/24697)).

<!-- mz-docs page: releases/v0.87 -->

# Materialize v0.87
## v0.87

#### Sources and sinks

* Add support for handling batched events formatted as `NDJSON` in the
  [webhook source](https://materialize.com/docs/sql/create-source/webhook/).

  ```mzsql
  CREATE SOURCE webhook_json IN CLUSTER quickstart FROM WEBHOOK
  BODY FORMAT JSON;

  -- Send multiple events delimited by newlines to the webhook source.
  HTTP POST to 'webhook_json'
    { 'event_type': 'foo' }
    { 'event_type': 'bar' }

  SELECT COUNT(*) FROM webhook_json;
  2
  ```

* Allow specifying a default AWS PrivateLink connection when creating a [Kafka connection over PrivateLink](https://materialize.com/docs/sql/create-connection/#aws-privatelink)
  using the `AWS PRIVATELINK` top-level option. The default connection will be
  used to connect to all brokers, and is exclusive with the `BROKER` and
  `BROKERS` options.

  ```mzsql
  CREATE CONNECTION privatelink_svc TO AWS PRIVATELINK (
      SERVICE NAME 'com.amazonaws.vpce.us-east-1.vpce-svc-0e123abc123198abc',
      AVAILABILITY ZONES ('use1-az1')
  );

  CREATE CONNECTION kafka_connection TO KAFKA (
      AWS PRIVATELINK (PORT 30292)
      SECURITY PROTOCOL = 'SASL_PLAINTEXT',
      SASL MECHANISMS = 'SCRAM-SHA-256',
      SASL USERNAME = 'foo',
      SASL PASSWORD = SECRET red_panda_password
  );
  ```

* Add `topic` to the [`mz_internal.mz_kafka_sources`](https://materialize.com/docs/sql/system-catalog/mz_catalog/#mz_kafka_sources)
  system catalog table. This column contains the name of the Kafka topic the
  source is reading from.

#### SQL

* Support user-configured data retention for tables via the `RETAIN HISTORY`
  syntax.

#### Bug fixes and other improvements

* Add a `node_ids` [output modifier](https://materialize.com/docs/sql/explain-plan/#output-modifiers)
for `EXPLAIN PHYSICAL PLAN` statements, to show the unique ID of each subplan in
the plan ([#24944](https://github.com/MaterializeInc/materialize/issues/24944)).

<!-- mz-docs page: releases/v0.88 -->

# Materialize v0.88
## v0.88

#### SQL

* Allow `LIMIT` expressions to contain parameters.

	```mzsql
	  PREPARE foo AS SELECT generate_series(1, 10) LIMIT $1;
	  EXECUTE foo (7::bigint);

	  generate_series
	  -----------------
	                 1
	                 2
	                 3
	                 4
	                 5
	                 6
	                 7
	```

#### Bug fixes and other improvements

* Fix a bug that potentially prevented timestamp with timezone data from being
  correctly parsed when ingested through PostgreSQL sources ([#25216](https://github.com/MaterializeInc/materialize/issues/25216)).

* Fix float parsing of certain zero values, such as `0.` and `.0` ([#25141](https://github.com/MaterializeInc/materialize/issues/25141)).

* Fix multiple bugs related to interval rounding ([#25202](https://github.com/MaterializeInc/materialize/issues/25202)).

<!-- mz-docs page: releases/v0.89 -->

# Materialize v0.89
## v0.89

#### Sources and sinks

* Improve source and sink statistics reporting to no longer reset on restarts,
  and include the following new metrics in [`mz_internal.mz_source_statistics`](https://materialize.com/docs/sql/system-catalog/mz_internal/#mz_source_statistics):

  | Metric                                        | Description                                                             |
  | --------------------------------------------- | ----------------------------------------------------------------------- |
  | `snapshot_records_known`                      | The size of the source's snapshot.                                      |
  | `snapshot_records_staged`                     | The amount of the source's snapshot Materialize has read.               |
  | `snapshot_committed`                          | Whether the initial snapshot for a source has been committed.           |
  | `offset_known`                                | The offset of the most recent data in the source's upstream service that Materialize knows about. |
  | `offset_committed`                            | The offset of the source's upstream service Materialize has fully committed.                      |

  These changes will be available in the Materialize console soon, so you can
  more easily monitor snapshot and ingestion progress for your sources.

#### SQL

* Remove the `mz_activity_log` system catalog view. These view was superseeded
by [`mz_recent_activity_log`](/sql/system-catalog/mz_internal/#mz_recent_activity_log),
which contains a log of the SQL statements that have been issued to
Materialize in the past 3 days.

* Add [`mz_internal.mz_compute_operator_hydration_statuses`](/sql/system-catalog/mz_internal/#mz_compute_operator_hydration_statuses)
to the system catalog. This table describes the dataflow operator hydration
status of compute objects (indexes or materialized views).

#### Bug fixes and other improvements

* Temporarily disallow `ALTER CONNECTION` commands on sources using the `UPSERT`
  envelope ([#25418](https://github.com/MaterializeInc/materialize/issues/25418)).

<!-- mz-docs page: releases/v0.90 -->

# Materialize v0.90
## v0.90

#### Sources and sinks

* Bump the maximum number of allowed concurrent connections in [wehbook sources](https://materialize.com/docs/sql/create-source/webhook/)
  from 250 to 500.

#### SQL

* Support using `LIKE`, `NOT LIKE`, `ILIKE`, and `NOT ILIKE` as operators within
  `ANY`, `SOME`, and `ALL` expressions.

* Add `mz_version` to the [`mz_internal.mz_recent_activity_log`](/sql/system-catalog/mz_internal/#mz_recent_activity_log)
  system catalog view. This column stores the version of Materialize that was
  running when the statement was executed.

#### Bug fixes and other improvements

* Fix the implementation of the `to_jsonb` function for `list` and `array`
  types ([#25536](https://github.com/MaterializeInc/materialize/issues/25536)). The return value is now a JSON array, rather than a
  JSON string literal containing the textual representation of the list or
  array.

<!-- mz-docs page: releases/v0.91 -->

# Materialize v0.91
## v0.91

[//]: # "NOTE(morsapaes) v0.91 shipped support for EXPLAIN FILTER PUSHDOWN
behind a feature flag."

#### Sources and sinks

* **Private preview.** Add a new [MySQL source](/sql/create-source/mysql/),
  which allows propagating change data from MySQL (5.7+) databases in real-time
  using [GTID-based binlog replication](https://dev.mysql.com/doc/refman/8.0/en/replication-gtids.html).

  **Syntax**

  ```mzsql
  CREATE SECRET mysqlpass AS '<MYSQL_PASSWORD>';

  CREATE CONNECTION mysql_connection TO MYSQL (
      HOST 'instance.foo000.us-west-1.rds.amazonaws.com',
      PORT 3306,
      USER 'materialize',
      PASSWORD SECRET mysqlpass
  );

  CREATE SOURCE mz_source
    FROM MYSQL CONNECTION mysql_connection
    FOR ALL TABLES;
  ```

    This source is compatible with MySQL managed services like
    [Amazon RDS for MySQL](/ingest-data/mysql/amazon-rds/),
    [Amazon Aurora MySQL](/ingest-data/mysql/amazon-aurora/),
    [Azure DB for MySQL](/ingest-data/mysql/azure-db/),
    and [Google Cloud SQL for MySQL](/ingest-data/mysql/google-cloud-sql/).

#### SQL

* Emit a notice if the `cluster` specified in the connection string used to
  connect to Materialize does not exist and the specified role does not have a
  default `cluster` set.

  ```bash
  NOTICE:  default cluster "quickstart" does not exist
  HINT:  Set a default cluster for the current role with ALTER ROLE <role> SET cluster TO <cluster>.
  psql (15.5 (Homebrew), server 9.5.0)
  Type "help" for help.

  materialize=>
  ```

#### Bug fixes and other improvements

* Bump the `max_connections` connection limit to `5000`, and enforce it for all
  users (including _superusers_).

* Correctly initialize source statistics in `mz_internal.mz_sources_statistics`
  when subsources are dropped and recreated using the `ALTER SOURCE...{ ADD |
  DROP } SUBSOURCE` command.

<!-- mz-docs page: releases/v0.92 -->

# Materialize v0.92
## v0.92

#### SQL

* Adjust null handling in the [`to_jsonb`](https://materialize.com/docs/sql/functions/#to_jsonb)
  function to match PostgreSQL's behavior. The functin now returns `NULL` when
  its input is `NULL`, rather than returning the JSON `null` value.

* Add `timeline_id` to the `mz_internal.mz_postgres_sources` system catalog
  table. This column registers the PostgreSQL [timeline ID](https://www.postgresql.org/docs/current/continuous-archiving.html#BACKUP-TIMELINES)
  determined on source creation.

#### Bug fixes and other improvements

* Fix a panic when calling the [`to_jsonb`](https://materialize.com/docs/sql/functions/#to_jsonb)
  on a list containing `NULL` array values.

<!-- mz-docs page: releases/v0.93 -->

# Materialize v0.93
## v0.93

#### Sources and sinks

* Do not error if the `oid` or `typmod` of a column changes when using the `TEXT COLUMNS`
  option to ingest data as text in a [PostgreSQL source](/sql/create-source/postgres/).
  As an example, this allows evolving the structure of `enum` columns by using
  `ALTER TABLE <table> ALTER COLUMN <enum column> TYPE...`, which would
  previously have set the affected subsource into an errored state.

#### Bug fixes and other improvements

* Extend `pg_catalog` coverage with support for the [`obj_description()`](/sql/functions/#obj_description)
  and [`col_description`](https://materialize.com/docs/sql/functions/#col_description) functions.

<!-- mz-docs page: releases/v0.94 -->

# Materialize v0.94
## v0.94

#### Sources and sinks

* Set subsources into an errored state in the [PostgreSQL source](/sql/create-source/postgres/)
  if the corresponding table is dropped from the publication upstream.

* Add a `KEY VALUE` load generator source,
  which produces keyed data that can be passed through to [`ENVELOPE UPSERT`](/sql/create-source/kafka/).
  This is useful for internal testing.

<!-- mz-docs page: releases/v0.95 -->

# Materialize v0.95
## v0.95

#### Sources and sinks

* Improve the readability of the output of the [`SHOW CREATE SOURCE`](/sql/show-create-source/)
  command for PostgreSQL and MySQL sources ([#26376](https://github.com/MaterializeInc/materialize/issues/26376)).

#### SQL

* Make the [`max_query_result_size`](/sql/set/#other-configuration-parameters)
  configuration parameter user-configurable. This parameter allows tuning the
  maximum size in bytes for a single query’s result.

* Improve the performance of the [`ALTER SCHEMA...SWAP WITH...`](https://materialize.com/docs/sql/alter-swap/)
  command ([#26361](https://github.com/MaterializeInc/materialize/issues/26361)), which speeds up [blue/green deployments](https://materialize.com/docs/manage/blue-green/).

* Support using the [`min()`](/sql/functions/#min) and [`max()`](/sql/functions/#max)
  functions with `time` values.

#### Bug fixes and other improvements

* Add the [`mz_probe`](/sql/show-clusters/#mz_probe-system-cluster) and
  [`mz_support`](/sql/show-clusters/#mz_support-system-cluster) system clusters
  to support internal monitoring tasks. Users are **not billed** for these
  clusters.

<!-- mz-docs page: releases/v0.96 -->

# Materialize v0.96
## v0.96

#### SQL

* Support `FORMAT CSV` in the `COPY .. TO STDOUT`
  command.

* Add [`mz_role_parameters`](/sql/system-catalog/mz_catalog/#mz_role_parameters)
  to the system catalog. This table contains a row for each parameter whose default
value has been altered for a given role using [ALTER ROLE ... SET](/sql/alter-role/#syntax).

#### Bug fixes and other improvements

* Fix the behavior of the [`translate`](https://materialize.com/docs/sql/functions/#translate)
  function when used with multibyte chars ([#26585](https://github.com/MaterializeInc/materialize/issues/26585)).

* Avoid panicking in the presence of composite keys in [`SUBSCRIBE`](/sql/subscribe/)
  commands using `ENVELOPE UPSERT` ([#26567](https://github.com/MaterializeInc/materialize/issues/26567)).

* Remove the unstable introspection relations
  `mz_internal.mz_compute_delays_histogram`,
  `mz_internal.mz_compute_delays_histogram_per_worker`, and
  `mz_internal.mz_compute_delays_histogram_raw`.

<!-- mz-docs page: releases/v0.97 -->

# Materialize v0.97
## v0.97

#### Sources and sinks

* Optimize memory usage of large transaction processing in the [PostgreSQL](/sql/create-source/postgres/)
  and [MySQL](/sql/create-source/mysql/) sources.

#### SQL

* Add the [`initcap` function](/sql/functions/#initcap), which returns a given
  string with the first character of every word in upper case and all other
  characters in lower case.

  ```mzsql
  SELECT initcap('bye DrivEr');

    initcap
   ---------------------
    Bye Driver
   (1 row)
  ```

* Add [`mz_materialized_view_refresh_strategies`](/sql/system-catalog/mz_internal/#mz_materialized_view_refresh_strategies)
  and [`mz_cluster_schedules`](/sql/system-catalog/mz_internal/#mz_cluster_schedules)
  to the system catalog. These tables were added in support of ongoing feature
  development.

<!-- mz-docs page: releases/v0.98 -->

# Materialize v0.98
## v0.98

#### Sources and sinks

* Support writing metadata to Kafka message headers in [Kafka sinks](/sql/create-sink/kafka/)
  via the new [`HEADERS` option](/sql/create-sink/kafka/#headers).

* Allow dropping subsources in PostgreSQL sources using the [`DROP SOURCE`](/sql/drop-source/)
  command. The `ALTER SOURCE...DROP SUBSOURCE` command has been removed.

* Require the `CASCADE` option to drop PostgreSQL and MySQL sources with active
  subsources. Previously, dropping a PostgreSQL or MySQL source automatically
  dropped all the corresponding subsources.

* Allow changing the ownership of a subsource using the [`ALTER OWNER`](/sql/alter-owner/)
  command. Subsources may now have different owners to the parent source.

#### SQL

* Add [`mz_internal.mz_postgres_source_tables`](/sql/system-catalog/mz_internal/#mz_postgres_source_tables) and [`mz_internal.mz_mysql_source_tables`](/sql/system-catalog/mz_internal/#mz_mysql_source_tables)
to the system catalog. These tables .

<!-- mz-docs page: releases/v0.99 -->

# Materialize v0.99
## v0.99

#### Sources and sinks

* **Private preview.** Support exporting objects and query results to Amazon s3
    using the [`COPY TO`](/sql/copy-to/) command and [`AWS connections`](/sql/create-connection/#aws).
    Both CSV and Parquet are supported as file formats.

  **Syntax**

  ```mzsql
  CREATE CONNECTION s3_conn
   TO AWS (ASSUME ROLE ARN = 'arn:aws:iam::000000000000:role/Materializes3Exporter');

  COPY mv TO 's3://mz-to-s3/'
  WITH (
    AWS CONNECTION = aws_role_assumption,
    FORMAT = 'parquet'
  );
  ```

  It's important to note that this command isn't supported in the SQL Shell yet,
  but will be in the next release ([#27114](https://github.com/MaterializeInc/materialize/issues/27114)).

* Support ingesting datetime columns as text via the `TEXT COLUMNS` option in
  the [MySQL source](/sql/create-source/mysql/) to work around MySQL's _zero_
  value for datetime types (`0000-00-00`, `0000-00-00 00:00:00`), as well as
  other differences in the range of supported values between MySQL and
  PostgreSQL.

#### SQL

* **Private preview.** Support setting a history retention period for sources,
    tables, materialized views, and indexes via the new [`RETAIN HISTORY`](/serve-results/durable-subscriptions/#history-retention-period)
    option. This is useful to implement [durable subscriptions](/serve-results/durable-subscriptions/).

  **Syntax**

  ```mzsql
  ALTER MATERIALIZED VIEW winning_bids SET (RETAIN HISTORY FOR '2hr');
  ```

  ```mzsql
  ALTER MATERIALIZED VIEW winning_bids RESET (RETAIN HISTORY);
  ```

* Add [`mz_internal.mz_history_retention_strategies`](https://materialize.com/docs/sql/system-catalog/mz_internal/#mz_history_retention_strategies)
  to the system catalog. This table describes the history retention strategies
  for tables, sources, indexes, and materialized views that are configured with
  a history retention period.

* Add [`mz_internal.mz_materialized_view_refreshes`](https://materialize.com/docs/sql/system-catalog/mz_internal/#mz_materialized_view_refreshes)
  to the system catalog. This table shows the time of the last successfully
  completed refresh and the time of the next scheduled refresh for each
  materialized view with a refresh strategy other than `on-commit`.

#### Bug fixes and other improvements

* Allow `interval` types to be cast to `mz_timestamp` ([#26970](https://github.com/MaterializeInc/materialize/issues/26970)).

* Move the `mz_cluster_replica_sizes` system catalog table from the `mz_internal
  schema` to `mz_catalog`, making the table definition stable. Any queries
  referencing the `mz_internal.mz_cluster_replica_sizes` catalog table must be
  adjusted to use `mz_catalog.mz_cluster_replica_sizes` instead.

