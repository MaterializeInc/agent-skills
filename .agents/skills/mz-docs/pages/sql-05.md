<!-- mz-docs page: sql/drop-owned -->

# DROP OWNED
`DROP OWNED` drops all the objects that are owned by one of the specified roles.
`DROP OWNED` drops all the objects that are owned by one of the specified roles.
Any privileges granted to the given roles on objects will also be revoked.

> **Note:** Unlike [PostgreSQL](https://www.postgresql.org/docs/current/sql-drop-owned.html), Materialize drops
> all objects across all databases, including the database itself.

## Syntax

```mzsql
DROP OWNED BY <role_name> [, ...] [RESTRICT|CASCADE];
```

Syntax element | Description
---------------|------------
`<role_name>`   | The role name whose owned objects will be dropped.
**CASCADE** | Optional. If specified, remove all dependent objects.
**RESTRICT**  | Optional. Do not drop anything if any non-index objects depencies exist. _(Default.)_

## Examples

```mzsql
DROP OWNED BY joe;
```

```mzsql
DROP OWNED BY joe, george CASCADE;
```

## Privileges

The privileges required to execute this statement are:

- Role membership in `role_name`.

## Related pages

- [`REVOKE PRIVILEGE`](../revoke-privilege)
- [`CREATE ROLE`](../create-role)
- [`REASSIGN OWNED`](../reassign-owned)
- [`DROP CLUSTER`](../drop-cluster)
- [`DROP CLUSTER REPLICA`](../drop-cluster-replica)
- [`DROP CONNECTION`](../drop-connection)
- [`DROP DATABASE`](../drop-database)
- [`DROP INDEX`](../drop-index)
- [`DROP MATERIALIZED VIEW`](../drop-materialized-view)
- [`DROP SCHEMA`](../drop-schema)
- [`DROP SECRET`](../drop-secret)
- [`DROP SINK`](../drop-sink)
- [`DROP SOURCE`](../drop-source)
- [`DROP TABLE`](../drop-table)
- [`DROP TYPE`](../drop-type)
- [`DROP VIEW`](../drop-view)

<!-- mz-docs page: sql/drop-role -->

# DROP ROLE
`DROP ROLE` removes a role from Materialize.
`DROP ROLE` removes a role from Materialize.

## Syntax

```mzsql
DROP ROLE [IF EXISTS] <role_name>;
```

Syntax element | Description
---------------|------------
**IF EXISTS** | Optional. If specified, do not return an error if the specified role does not exist.
`<role_name>` | The role you want to drop. For available roles, see [`mz_roles`](/sql/system-catalog/mz_catalog#mz_roles).

## Details

You cannot drop the current role.

## Privileges

The privileges required to execute this statement are:

- `CREATEROLE` privileges on the system.

## Related pages

- [`ALTER ROLE`](../alter-role)
- [`CREATE ROLE`](../create-role)
- [`DROP USER`](../drop-user)
- [`GRANT ROLE`](../grant-role)
- [`REVOKE ROLE`](../revoke-role)
- [`ALTER OWNER`](/sql/#rbac)
- [`GRANT PRIVILEGE`](../grant-privilege)
- [`REVOKE PRIVILEGE`](../revoke-privilege)

<!-- mz-docs page: sql/drop-schema -->

# DROP SCHEMA
`DROP SCHEMA` removes a schema from Materialize.
`DROP SCHEMA` removes a schema from Materialize.

## Syntax

```mzsql
DROP SCHEMA [IF EXISTS] <schema_name> [CASCADE|RESTRICT];
```

Syntax element | Description
---------------|------------
**IF EXISTS** | Optional. If specified, do not return an error if the named schema does not exist.
`<schema_name>` | The schema you want to remove. For available schemas, see [`SHOW SCHEMAS`](../show-schemas).
**CASCADE** | Remove the schema and its dependent objects.
**RESTRICT** | Do not remove this schema if it contains any sources or views. _(Default)_

## Details

Before you can drop a schema, you must [drop all sources](../drop-source) and
[views](../drop-view) it contains, or use the **CASCADE** option.

## Example

### Remove a schema with no dependent objects
```mzsql
SHOW SOURCES FROM my_schema;
```
```nofmt
my_file_source
```
```mzsql
DROP SCHEMA my_schema;
```

### Remove a schema with dependent objects
```mzsql
SHOW SOURCES FROM my_schema;
```
```nofmt
my_file_source
```
```mzsql
DROP SCHEMA my_schema CASCADE;
```

### Remove a schema only if it has no dependent objects

You can use either of the following commands:

- ```mzsql
  DROP SCHEMA my_schema;
  ```
- ```mzsql
  DROP SCHEMA my_schema RESTRICT;
  ```

### Do not issue an error if attempting to remove a nonexistent schema

```mzsql
DROP SCHEMA IF EXISTS my_schema;
```

## Privileges

The privileges required to execute this statement are:

- Ownership of the dropped schema.
- `USAGE` privileges on the containing database.

## Related pages

- [`SHOW SCHEMAS`](../show-schemas)
- [`CREATE SCHEMA`](../create-schema)
- [`DROP OWNED`](../drop-owned)

<!-- mz-docs page: sql/drop-secret -->

# DROP SECRET
`DROP SECRET` removes a secret from Materialize's secret management system.
`DROP SECRET` removes a secret from Materialize's secret management system. If
there are connections depending on the secret, you must explicitly drop them
first, or use the `CASCADE` option.

## Syntax

```mzsql
DROP SECRET [IF EXISTS] <secret_name> [CASCADE|RESTRICT];
```

Syntax element | Description
---------------|------------
**IF EXISTS** | Optional. If specified, do not return an error if the specified secret does not exist.
_secret&lowbar;name_ | The secret you want to drop. For available secrets, see [`SHOW SECRETS`](../show-secrets).
**CASCADE** | Optional. If specified, remove the secret and its dependent objects.
**RESTRICT** | Optional. Do not drop the secret if it has dependencies. _(Default)_

## Examples

### Dropping a secret with no dependencies

To drop an existing secret, run:

```mzsql
DROP SECRET kafka_sasl_password;
```

To avoid issuing an error if the specified secret does not exist, use the `IF EXISTS` option:

```mzsql
DROP SECRET IF EXISTS kafka_sasl_password;
```

### Dropping a secret with dependencies

If the secret has dependencies, Materialize will throw an error similar to:

```mzsql
DROP SECRET kafka_sasl_password;
```

```nofmt
ERROR:  cannot drop materialize.public.kafka_sasl_password: still depended upon by catalog
 item 'materialize.public.kafka_connection'
```

, and you'll have to explicitly ask to also remove any dependent objects using the `CASCADE` option:

```mzsql
DROP SECRET kafka_sasl_password CASCADE;
```

## Privileges

The privileges required to execute this statement are:

- Ownership of the dropped secret.
- `USAGE` privileges on the containing schema.

## Related pages

- [`SHOW SECRETS`](../show-secrets)
- [`DROP OWNED`](../drop-owned)

<!-- mz-docs page: sql/drop-sink -->

# DROP SINK
`DROP SINK` removes a sink from Materialize.
`DROP SINK` removes a sink from Materialize.

Dropping a Kafka sink doesn't drop the corresponding topic. For more information, see the [Kafka documentation](https://kafka.apache.org/documentation/).

## Syntax

```mzsql
DROP SINK [IF EXISTS] <sink_name>;
```

Syntax element | Description
---------------|------------
**IF EXISTS** | Optional. If specified, do not return an error if the specified sink does not exist.
`<sink_name>` | The sink you want to drop. You can find available sink names through [`SHOW SINKS`](../show-sinks).

## Examples

```mzsql
SHOW SINKS;
```
```nofmt
my_sink
```
```mzsql
DROP SINK my_sink;
```
```nofmt
DROP SINK
```

## Privileges

The privileges required to execute this statement are:

- Ownership of the dropped sink.
- `USAGE` privileges on the containing schema.

## Related pages

- [`SHOW SINKS`](../show-sinks)
- [`CREATE SINK`](../create-sink)
- [`DROP OWNED`](../drop-owned)

<!-- mz-docs page: sql/drop-source -->

# DROP SOURCE
`DROP SOURCE` removes a source from Materialize.
`DROP SOURCE` removes a source from Materialize. If there are objects depending
on the source, you must explicitly drop them first, or use the `CASCADE`
option.

## Syntax

```mzsql
DROP SOURCE [IF EXISTS] <source_name> [RESTRICT|CASCADE];
```

Syntax element | Description
---------------|------------
**IF EXISTS** | Optional. If specified, do not return an error if the named source does not exist.
`<source_name>` | The name of the source you want to remove.
**CASCADE** | Optional. If specified, remove the source and its dependent objects.
**RESTRICT** | Optional. Do not remove this source if it has dependent objects. _(Default.)_

## Examples

### Remove a source with no dependent objects

```mzsql
SHOW SOURCES;
```
```nofmt
...
my_source
```
```mzsql
DROP SOURCE my_source;
```

### Remove a source with dependent objects

```mzsql
SHOW SOURCES;
```
```nofmt
...
my_source
```
```mzsql
DROP SOURCE my_source CASCADE;
```

### Remove a source only if it has no dependent objects

You can use either of the following commands:

- ```mzsql
  DROP SOURCE my_source;
  ```
- ```mzsql
  DROP SOURCE my_source RESTRICT;
  ```

### Do not issue an error if attempting to remove a nonexistent source

```mzsql
DROP SOURCE IF EXISTS my_source;
```

## Privileges

The privileges required to execute this statement are:

- Ownership of the dropped source.
- `USAGE` privileges on the containing schema.

## Related pages

- [`CREATE SOURCE`](../create-source)
- [`SHOW SOURCES`](../show-sources)
- [`SHOW CREATE SOURCE`](../show-create-source)
- [`DROP OWNED`](../drop-owned)

<!-- mz-docs page: sql/drop-table -->

# DROP TABLE
`DROP TABLE` removes a table from Materialize.
`DROP TABLE` removes a table from Materialize.

## Syntax

```mzsql
DROP TABLE [IF EXISTS] <table_name> [RESTRICT|CASCADE];
```

Syntax element | Description
---------------|------------
**IF EXISTS**  | Optional. If specified, do not return an error if the named table doesn't exist.
`<table_name>` | The name of the table to remove.
**CASCADE** | Optional. If specified, remove the table and its dependent objects.
**RESTRICT**  | Optional. Don't remove the table if any non-index objects depend on it. _(Default.)_

## Examples

### Remove a table with no dependent objects
Create a table *t* and verify that it was created:

```mzsql
CREATE TABLE t (a int, b text NOT NULL);
SHOW TABLES;
```
```
TABLES
------
t
```

Remove the table:

```mzsql
DROP TABLE t;
```
### Remove a table with dependent objects

Create a table *t*:

```mzsql
CREATE TABLE t (a int, b text NOT NULL);
INSERT INTO t VALUES (1, 'yes'), (2, 'no'), (3, 'maybe');
SELECT * FROM t;
```
```
a |   b
---+-------
2 | no
1 | yes
3 | maybe
(3 rows)
```

Create a materialized view from *t*:

```mzsql
CREATE MATERIALIZED VIEW t_view AS SELECT sum(a) AS sum FROM t;
SHOW MATERIALIZED VIEWS;
```
```
name    | cluster
--------+---------
t_view  | default
(1 row)
```

Remove table *t*:

```mzsql
DROP TABLE t CASCADE;
```

### Remove a table only if it has no dependent objects

You can use either of the following commands:

- ```mzsql
  DROP TABLE t;
  ```
- ```mzsql
  DROP TABLE t RESTRICT;
  ```

### Do not issue an error if attempting to remove a nonexistent table

```mzsql
DROP TABLE IF EXISTS t;
```

## Privileges

The privileges required to execute this statement are:

- Ownership of the dropped table.
- `USAGE` privileges on the containing schema.

## Related pages

- [`CREATE TABLE`](../create-table)
- [`INSERT`](../insert)
- [`DROP OWNED`](../drop-owned)

<!-- mz-docs page: sql/drop-type -->

# DROP TYPE
`DROP TYPE` removes a user-defined data type.
`DROP TYPE` removes a [custom data type](../create-type). You cannot use it on default data types.

## Syntax

```mzsql
DROP TYPE [IF EXISTS] <data_type_name> [RESTRICT|CASCADE];
```

Syntax element | Description
---------------|------------
**IF EXISTS**  | Optional. If specified, do not return an error if the named type doesn't exist.
`<data_type_name>` | The name of the type to remove.
**CASCADE** | Optional. If specified, remove the type and its dependent objects, such as tables or other types.
**RESTRICT** | Optional. Don't remove the type if any objects depend on it. _(Default.)_

## Examples

### Remove a type with no dependent objects
```mzsql
CREATE TYPE int4_map AS MAP (KEY TYPE = text, VALUE TYPE = int4);

SHOW TYPES;
```
```
    name
--------------
  int4_map
(1 row)
```

```mzsql
DROP TYPE int4_map;

SHOW TYPES;
```
```
  name
--------------
(0 rows)
```

### Remove a type with dependent objects

By default, `DROP TYPE` will not remove a type with dependent objects. The **CASCADE** switch will remove both the specified type and *all its dependent objects*.

In the example below, the **CASCADE** switch removes `int4_list`, `int4_list_list` (which depends on `int4_list`), and the table *t*, which has a column of data type `int4_list`.

```mzsql
CREATE TYPE int4_list AS LIST (ELEMENT TYPE = int4);

CREATE TYPE int4_list_list AS LIST (ELEMENT TYPE = int4_list);

CREATE TABLE t (a int4_list);

SHOW TYPES;
```
```
      name
----------------
 int4_list
 int4_list_list
(2 rows)
```

```mzsql
DROP TYPE int4_list CASCADE;

SHOW TYPES;

SELECT * FROM t;
```
```
 name
------
(0 rows)
ERROR:  unknown catalog item 't'
```

### Remove a type only if it has no dependent objects

You can use either of the following commands:

- ```mzsql
  DROP TYPE int4_list;
  ```
- ```mzsql
  DROP TYPE int4_list RESTRICT;
  ```

### Do not issue an error if attempting to remove a nonexistent type

```mzsql
DROP TYPE IF EXISTS int4_list;
```

## Privileges

The privileges required to execute this statement are:

- Ownership of the dropped type.
- `USAGE` privileges on the containing schema.

## Related pages

* [`CREATE TYPE`](../create-type)
* [`SHOW TYPES`](../show-types)
* [`DROP OWNED`](../drop-owned)

<!-- mz-docs page: sql/drop-user -->

# DROP USER
`DROP USER` removes a role from Materialize.
`DROP USER` removes a role from Materialize. `DROP USER` is an alias for [`DROP ROLE`](../drop-role).

## Syntax

```mzsql
DROP USER [IF EXISTS] <role_name>;
```

Syntax element | Description
---------------|------------
**IF EXISTS** | Optional. If specified, do not return an error if the specified role does not exist.
`<role_name>` | The role you want to drop. For available roles, see [`mz_roles`](/sql/system-catalog/mz_catalog#mz_roles).

## Privileges

The privileges required to execute this statement are:

- `CREATEROLE` privileges on the system.

## Related pages

- [`ALTER ROLE`](../alter-role)
- [`CREATE ROLE`](../create-role)
- [`DROP ROLE`](../drop-role)
- [`GRANT ROLE`](../grant-role)
- [`REVOKE ROLE`](../revoke-role)
- [`GRANT PRIVILEGE`](../grant-privilege)
- [`REVOKE PRIVILEGE`](../revoke-privilege)

<!-- mz-docs page: sql/drop-view -->

# DROP VIEW
`DROP VIEW` removes a view from Materialize.
`DROP VIEW` removes a view from Materialize.

## Conceptual framework

Materialize maintains views after you create them. If you no longer need the
view, you can remove it.

Because views rely on receiving data from sources, you must drop all views that
rely on a source before you can [drop the source](../drop-source) itself. You can achieve this easily using **DROP SOURCE...CASCADE**.

## Syntax

```mzsql
DROP VIEW [IF EXISTS] <view_name> [RESTRICT|CASCADE];
```

Syntax element | Description
---------------|------------
**IF EXISTS** | Optional. If specified, do not return an error if the named view does not exist.
`<view_name>` | The view you want to drop. You can find available view names through [`SHOW VIEWS`](../show-views).
**RESTRICT** | Optional. Do not drop this view if any other views depend on it. _(Default)_
**CASCADE** | Optional. Drop all views that depend on this view.

## Examples

```mzsql
SHOW VIEWS;
```
```nofmt
  name
---------
 my_view
```
```mzsql
DROP VIEW my_view;
```
```nofmt
DROP VIEW
```

## Privileges

The privileges required to execute this statement are:

- Ownership of the dropped view.
- `USAGE` privileges on the containing schema.

## Related pages

- [`CREATE VIEW`](../create-view)
- [`SHOW VIEWS`](../show-views)
- [`SHOW CREATE VIEW`](../show-create-view)
- [`DROP OWNED`](../drop-owned)

<!-- mz-docs page: sql/execute -->

# EXECUTE
`EXECUTE`
`EXECUTE` plans and executes [prepared statements](../prepare). Since prepared statements only last the duration of a session, the statement must have been prepared during the current session.

If the `PREPARE` statement specified some parameters, you must pass values compatible with those parameters to `EXECUTE`. Values are considered compatible here when they can be [_assignment cast_](../../sql/functions/cast/#valid-casts). (This is the same category of casting that happens for `INSERT`.)

## Syntax

```mzsql
EXECUTE <name> [ ( <parameter> [, ...] ) ]

```

| Syntax element | Description |
| --- | --- |
| `<name>` | The name of the prepared statement to execute.  |
| `<parameter>` | The actual value of a parameter to the prepared statement.  |

## Example

The following example [prepares a statement](/sql/prepare/) `a` and runs it
using the `EXECUTE` statement:

```mzsql
PREPARE a AS SELECT 1 + $1;
EXECUTE a (2);
```

All prepared statements will be cleared at the end of a session. You can also
explicitly deallocate the statement using [`DEALLOCATE`].

## Related pages

- [`PREPARE`]
- [`DEALLOCATE`]

[`PREPARE`]:../prepare
[`DEALLOCATE`]:../deallocate

<!-- mz-docs page: sql/execute-unit-test -->

# EXECUTE UNIT TEST
`EXECUTE UNIT TEST` defines a unit test for a view, run by mz-deploy against mocked input data.
> **Public Preview:** This feature is in public preview.

`EXECUTE UNIT TEST` defines a unit test for a view or materialized view. A test
substitutes literal rows for the view's dependencies, runs the view against
that fixed input, and compares the result to a set of expected rows. Tests are
written inline in the same `.sql` file as the view they exercise.

> **Warning:** `EXECUTE UNIT TEST` is executed only by [`mz-deploy`](/developer-tools/mz-deploy/), not by
> Materialize itself. The Materialize SQL layer parses the statement but rejects
> it during planning, so running it through a SQL client such as `psql` returns an
> `EXECUTE UNIT TEST statement not yet supported` error. Use
> [`mz-deploy test`](/developer-tools/mz-deploy/local-development/#write-and-run-unit-tests)
> to discover and run these tests.

## Syntax

```mzsql
EXECUTE UNIT TEST <test_name>
FOR <target_view>
[AT TIME <timestamp_expr>]
[MOCK <dependency>(<col_name> <col_type>, ...) AS (<query>)[, ...]]
EXPECTED(<col_name> <col_type>, ...) AS (<query>);

```

| Syntax element | Description |
| --- | --- |
| `<test_name>` | A name for the test. It identifies the test in `mz-deploy test` output and in test filters.  |
| `FOR <target_view>` | The view or materialized view under test, given as a fully-qualified name (`<database>.<schema>.<view>`).  |
| `AT TIME <timestamp_expr>` | Optional. Sets the value [`mz_now()`](/sql/functions/now_and_mz_now/) returns while the test runs, so views with temporal filters produce deterministic results. If omitted, `mz_now()` is not pinned.  |
| `MOCK <dependency>(...) AS (<query>)` | Replaces a dependency of the target view with literal rows. Specify zero or more `MOCK` clauses, separated by commas; there is no comma before the trailing `EXPECTED` clause. Every object the target view depends on must have a corresponding `MOCK`. The dependency name may be unqualified (`orders`), schema-qualified (`public.orders`), or fully-qualified (`materialize.public.orders`), and is resolved relative to the target view. The column list declares the names and types of the mock; `<query>` supplies its rows, typically with [`VALUES`](/sql/values/).  |
| `EXPECTED(...) AS (<query>)` | Required. The rows the target view should produce. The column list must match the names and types of the target view's output columns, and `<query>` supplies the expected rows. The test passes when the view's output and the expected rows are equal as sets.  |

## Details

### Where tests run

`mz-deploy test` discovers every `EXECUTE UNIT TEST` statement in a project,
then runs each one in a local Materialize Docker container — your remote
database is never touched. For each test, `mz-deploy` creates temporary views
for the mocks and the expected rows, rewrites the target view to read from the
mocks instead of its real dependencies, and computes the symmetric difference
between the view's output and the expected rows. The test passes when that
difference is empty.

### Mocking dependencies

Every object the target view depends on must have a `MOCK` clause; an unmocked
dependency is a validation error. A mock's column names and types must match the
real object's schema, and the target view's output columns must match the
`EXPECTED` column list. Run [`mz-deploy lock`](/developer-tools/mz-deploy/local-development/#lock-types)
to refresh the schema information used for this validation when an external
dependency changes.

### Type normalization

Column types in `MOCK` and `EXPECTED` are normalized before comparison, so
common aliases are interchangeable — for example `int`/`int4`/`integer`,
`bigint`/`int8`, `text`/`varchar`/`string`,
`float`/`float8`/`double precision`, `numeric`/`decimal`, and `json`/`jsonb`.

### Testing temporal logic

Views that filter on [`mz_now()`](/sql/functions/now_and_mz_now/) depend on the
current time, which would make their output non-deterministic in a test. Set
`AT TIME` to pin the value `mz_now()` returns so the test result is stable.

## Examples

### Testing a join

```mzsql
CREATE VIEW user_order_summary AS
SELECT u.id AS user_id, u.name, count(*) AS total_orders
FROM users u
JOIN orders o ON o.user_id = u.id
GROUP BY u.id, u.name;

EXECUTE UNIT TEST test_single_user_single_order
FOR materialize.public.user_order_summary
MOCK materialize.public.users(id bigint, name text) AS (
  SELECT * FROM VALUES (1, 'alice')
),
MOCK materialize.public.orders(id bigint, user_id bigint) AS (
  SELECT * FROM VALUES (10, 1)
)
EXPECTED(user_id bigint, name text, total_orders bigint) AS (
  SELECT * FROM VALUES (1, 'alice', 1)
);
```

### Pinning `mz_now()`

```mzsql
EXECUTE UNIT TEST test_recent_events
FOR materialize.public.recent_events
AT TIME '2024-01-15T12:00:00Z'
MOCK materialize.public.events(id bigint, ts timestamptz) AS (
  SELECT * FROM VALUES
    (1, '2024-01-15T11:59:00Z'::timestamptz),
    (2, '2024-01-14T12:00:00Z'::timestamptz)
)
EXPECTED(id bigint, ts timestamptz) AS (
  SELECT * FROM VALUES (1, '2024-01-15T11:59:00Z'::timestamptz)
);
```

## Related pages

- [Local development with mz-deploy](/developer-tools/mz-deploy/local-development/#write-and-run-unit-tests)
- [`CREATE VIEW`](/sql/create-view/)
- [`CREATE MATERIALIZED VIEW`](/sql/create-materialized-view/)
- [`VALUES`](/sql/values/)

<!-- mz-docs page: sql/explain-analyze -->

# EXPLAIN ANALYZE
Reference page for `EXPLAIN ANALYZE`. `EXPLAIN ANALYZE` is used to understand the performance of indexes and materialized views.
`EXPLAIN ANALYZE`:

- Summarizes cluster status.
- Reports on the performance of indexes and materialized views.
- Provide the execution plan annotated with TopK hints. The TopK
  query pattern groups by some key and return the first K elements within each
  group according to some ordering.

> **Warning:** `EXPLAIN` is not part of Materialize's stable interface and is not subject to
> our backwards compatibility guarantee. The syntax and output of `EXPLAIN` may
> change arbitrarily in future versions of Materialize.

## Syntax

```mzsql
EXPLAIN ANALYZE
      CPU [, MEMORY] [WITH SKEW]
    | MEMORY [, CPU] [WITH SKEW]
    | HINTS
FOR INDEX <name> | MATERIALIZED VIEW <name>
[ AS SQL ]
;

EXPLAIN ANALYZE CLUSTER
      CPU [, MEMORY] [WITH SKEW]
    | MEMORY [, CPU] [WITH SKEW]
[ AS SQL ]
;
```
> **Tip:** If you want to specify both `CPU` or `MEMORY`, they may be listed in any order;
> however, each may appear only once.

Parameter    | Description
-------------|-----
**CPU**      | Reports consumed CPU time information `total_elapsed` for each operator (not inclusive of its child operators; `FOR INDEX`, `FOR MATERIALIZED VIEW`) or for each object in the current cluster (`CLUSTER`).
**MEMORY**   | Reports consumed memory information `total_memory` and number of records `total_records` for each operator (not including child operators; `FOR INDEX`, `FOR MATERIALIZED VIEW`) or for each object in the current cluster (`CLUSTER`).
**WITH SKEW** | *Optional.* If specified, includes additional information about average and per-worker consumption and ratios (of `CPU` and/or `MEMORY`).
**HINTS**    | Annotates the LIR plan with [TopK hints] (`FOR INDEX`, `FOR MATERIALIZED VIEW`).
**AS SQL**   | *Optional.* If specified, returns the SQL associated with the specified `EXPLAIN ANALYZE` command without executing it. You can modify this SQL as a starting point to create customized queries.

## Privileges

The privileges required to execute this statement are:

- `USAGE` privileges on the schemas that all relations in the explainee are
  contained in.

## Examples

`EXPLAIN ANALYZE` attributes runtime metrics to [`PHYSICAL PLAN` operators](/sql/explain-plan#reference-plan-operators).

The attribution examples in this
section reference the `wins_by_item` index (and the underlying `winning_bids`
view) from the [quickstart
guide](/get-started/#step-2-create-the-source):

```sql
CREATE SOURCE auction_house
FROM LOAD GENERATOR AUCTION
(TICK INTERVAL '1s', AS OF 100000)
FOR ALL TABLES;

CREATE VIEW winning_bids AS
  SELECT DISTINCT ON (a.id) b.*, a.item, a.seller
    FROM auctions AS a
    JOIN bids AS b
      ON a.id = b.auction_id
   WHERE b.bid_time < a.end_time
     AND mz_now() >= a.end_time
   ORDER BY a.id, b.amount DESC, b.bid_time, b.buyer;

CREATE INDEX wins_by_item ON winning_bids (item);
```

### `EXPLAIN ANALYZE MEMORY`

The following examples reports on the memory usage of the index `wins_by_item`:

```mzsql
EXPLAIN ANALYZE MEMORY FOR INDEX wins_by_item;
```

For the index, `EXPLAIN ANALYZE MEMORY` reports on the memory usage and the
number of records for each operator in the dataflow:

|         operator            | total_memory | total_records |
|-----------------------------|-------------:|--------------:|
| Arrange                     | 386 kB       |         15409 |
|   Stream u8                 |              |               |
| **Non-monotonic TopK**      | **36 MB**    |    **731975** |
|   Differential Join %0 » %1 |              |               |
|     Arrange                 | 2010 kB      |         84622 |
|       Stream u5             |              |               |
|     Arrange                 | 591 kB       |         15410 |
|       Read u4               |              |               |

The results show the `TopK` operator is overwhelmingly responsible for memory
usage.

### `EXPLAIN ANALYZE CPU`

The following examples reports on the cpu usage of the index `wins_by_item`:

```mzsql
EXPLAIN ANALYZE CPU FOR INDEX wins_by_item;
```

For the index, `EXPLAIN ANALYZE CPU` reports on total time spent in each
operator (not inclusive of its child operators) in the dataflow:

|         operator            |  total_elapsed  |
|:----------------------------|----------------:|
| Arrange                     | 00:00:00.161341 |
|   Stream u8                 |                 |
| Non-monotonic TopK          | 00:00:15.153963 |
|   Differential Join %0 » %1 | 00:00:00.978381 |
|     Arrange                 | 00:00:00.536282 |
|       Stream u5             |                 |
|     Arrange                 | 00:00:00.171586 |
|       Read u4               |                 |

### `EXPLAIN ANALYZE CPU, MEMORY`

You can report on both CPU and memory usage simultaneously:

```mzsql
EXPLAIN ANALYZE CPU, MEMORY FOR INDEX wins_by_item;
```

You can specify both `CPU` or `MEMORY` in any order; however, each may appear
only once. The order of `CPU` and `MEMORY` in the statement determines the order
of the output columns

For example, in the above example where the `CPU` was listed before `MEMORY`,
the CPU time (`total_elasped`) column is listed before the `MEMORY` information
`total_memory` and `total_records`.

|         operator            |  total_elapsed  | total_memory | total_records |
|:----------------------------|----------------:|-------------:|--------------:|
| Arrange                     | 00:00:00.190801 | 389 kB       |         15435 |
|   Stream u8                 |                 |              |               |
| Non-monotonic TopK          | 00:00:16.193381 | 36 MB        |        733457 |
|   Differential Join %0 » %1 | 00:00:01.107056 |              |               |
|     Arrange                 | 00:00:00.592818 | 2017 kB      |         84793 |
|       Stream u5             |                 |              |               |
|     Arrange                 | 00:00:00.214064 | 595 kB       |         15436 |
|       Read u4               |                 |              |               |

### `EXPLAIN ANALYZE ... WITH SKEW`

In clusters with more than one worker, [worker
skew](/transform-data/dataflow-troubleshooting/#is-work-distributed-equally-across-workers)
can occur when data is unevenly distributed across workers. Extreme cases of
skew can seriously impact performance. You can use `EXPLAIN ANALYZE ... WITH
SKEW` to identify this scenario. The `WITH SKEW` option includes the per worker
and average worker performance numbers for each operator, along with each
worker's ratio compared to the average.

For the below example, assume there are 2 workers in the cluster.

> **Tip:** To determine how many workers a given cluster size has, you can query
> [`mz_catalog.mz_cluster_replica_sizes`](/sql/system-catalog/mz_catalog/#mz_cluster_replica_sizes).

You can explain `MEMORY` and/or `CPU` with the `WITH SKEW` option. For example,
the following runs `EXPLAIN ANALYZE MEMORY WITH SKEW`:

```mzsql
EXPLAIN ANALYZE MEMORY WITH SKEW FOR INDEX wins_by_item;
```

The results include the per worker and average worker performance numbers for
each operator, along with each worker's ratio compared to the average:

|         operator            | worker_id | memory_ratio | worker_memory | avg_memory | total_memory | records_ratio | worker_records | avg_records | total_records |
|:----------------------------|----------:|-------------:|--------------:|-----------:|-------------:|--------------:|---------------:|------------:|--------------:|
| Arrange                     | 0         |          0.8 | 78 kB         | 97 kB      | 389 kB       |           0.8 |           3099 |        3862 |         15448 |
| Arrange                     | 1         |         1.59 | 154 kB        | 97 kB      | 389 kB       |          1.58 |           6113 |        3862 |         15448 |
| Arrange                     | 2         |         1.61 | 157 kB        | 97 kB      | 389 kB       |          1.61 |           6236 |        3862 |         15448 |
| **Arrange**                 | **3**     |        **0** | **272 bytes** | **97 kB**  | **389 kB**   |         **0** |          **0** |    **3862** |     **15448** |
|   Stream u8                 |           |              |               |            |              |               |                |             |               |
| Non-monotonic TopK          | 0         |            1 | 9225 kB       | 9261 kB    | 36 MB        |             1 |         183148 |   183486.75 |        733947 |
| Non-monotonic TopK          | 1         |            1 | 9222 kB       | 9261 kB    | 36 MB        |             1 |         183319 |   183486.75 |        733947 |
| Non-monotonic TopK          | 2         |            1 | 9301 kB       | 9261 kB    | 36 MB        |             1 |         183585 |   183486.75 |        733947 |
| Non-monotonic TopK          | 3         |            1 | 9293 kB       | 9261 kB    | 36 MB        |             1 |         183895 |   183486.75 |        733947 |
|   Differential Join %0 » %1 |           |              |               |            |              |               |                |             |               |
|     Arrange                 | 0         |         0.97 | 487 kB        | 505 kB     | 2019 kB      |             1 |          21165 |     21213.5 |         84854 |
|     Arrange                 | 1         |         0.97 | 489 kB        | 505 kB     | 2019 kB      |             1 |          21274 |     21213.5 |         84854 |
|     Arrange                 | 2         |          1.1 | 555 kB        | 505 kB     | 2019 kB      |             1 |          21298 |     21213.5 |         84854 |
|     Arrange                 | 3         |         0.96 | 487 kB        | 505 kB     | 2019 kB      |             1 |          21117 |     21213.5 |         84854 |
|       Stream u5             |           |              |               |            |              |               |                |             |               |
|     Arrange                 | 0         |            1 | 149 kB        | 149 kB     | 595 kB       |             1 |           3862 |      3862.5 |         15450 |
|     Arrange                 | 1         |            1 | 148 kB        | 149 kB     | 595 kB       |             1 |           3862 |      3862.5 |         15450 |
|     Arrange                 | 2         |            1 | 149 kB        | 149 kB     | 595 kB       |             1 |           3863 |      3862.5 |         15450 |
|     Arrange                 | 3         |            1 | 149 kB        | 149 kB     | 595 kB       |             1 |           3863 |      3862.5 |         15450 |
|       Read u4               |           |              |               |            |              |               |                |             |               |

The `ratio` column tells you whether a worker is particularly over- or
under-loaded:

- a `ratio` below 1 indicates a worker doing a below average amount of work.

- a `ratio` above 1 indicates a worker doing an above average amount of work.

While there will always be some amount of variation, very high ratios indicate a
skewed workload. Here the memory ratios are mostly close to 1, indicating there is very
little worker skew everywhere but at the top level arrangement, where worker 3 has no records.

### `EXPLAIN ANALYZE HINTS`

`EXPLAIN ANALYZE HINTS` can annotate your plan (specifically, each TopK
operator) with suggested [TopK hints]; i.e., [`DISTINCT ON INPUT GROUP SIZE=`
value](/transform-data/idiomatic-materialize-sql/top-k/#query-hints-1).

For example, the following runs `EXPLAIN ANALYZE HINTS` on the `wins_by_item`
index:

```mzsql
EXPLAIN ANALYZE HINTS FOR INDEX wins_by_item;
```

The result shows that the `wins_by_item` index has only one `TopK` operator and
suggests the hint (i.e, the `DISTINCT ON INPUT GROUP SIZE=` value) of `255.0`.

|         operator            | levels | to_cut | hint | savings |
|:----------------------------|-------:|-------:|-----:|--------:|
| Arrange                     |        |        |      |         |
|   Stream u8                 |        |        |      |         |
| Non-monotonic TopK          |      8 |      6 |  255 | 26 MB   |
|   Differential Join %0 » %1 |        |        |      |         |
|     Arrange                 |        |        |      |         |
|       Stream u5             |        |        |      |         |
|     Arrange                 |        |        |      |         |
|       Read u4               |        |        |      |         |

With the hint information, you can recreate the view and index to improve memory
usage:

```sql
DROP VIEW winning_bids CASCADE;

CREATE VIEW winning_bids AS
    SELECT DISTINCT ON (a.id) b.*, a.item, a.seller
      FROM auctions AS a
      JOIN bids AS b
        ON a.id = b.auction_id
     WHERE b.bid_time < a.end_time
       AND mz_now() >= a.end_time
   OPTIONS (DISTINCT ON INPUT GROUP SIZE = 255) -- use hint!
  ORDER BY a.id,
    b.amount DESC,
    b.bid_time,
    b.buyer;

CREATE INDEX wins_by_item ON winning_bids (item);
```

Re-running the `TopK`-hints query will show only `null` hints; i.e., there are
no hints because our `TopK` is now appropriately sized.

To see if the indexe's memory usage has improved with the hint, rerun the
following `EXPLAIN ANALYZE MEMORY` command:

```mzsql
EXPLAIN ANALYZE MEMORY FOR INDEX wins_by_item;
```

The results show that the `TopK` operator uses `11MB` of memory, less than a third of the
[~36MB of memory it was using before](#explain-analyze-memory):

|         operator            | total_memory | total_records |
|:----------------------------|-------------:|--------------:|
| Arrange                     | 391 kB       |         15501 |
|   Stream u10                |              |               |
| **Non-monotonic TopK**      | **11 MB**    |    **226706** |
|   Differential Join %0 » %1 |              |               |
|     Arrange                 | 1994 kB      |         85150 |
|       Stream u5             |              |               |
|     Arrange                 | 601 kB       |         15502 |
|       Read u4               |              |               |

### `EXPLAIN ANALYZE CLUSTER ...`

It is possible to look at overall cluster status, rather than individual indexes or materialized views. This is useful for quickly identifying skewed dataflows as well as which dataflows are taking up the most resources.

Running `EXPLAIN ANALYZE CLUSTER MEMORY, CPU` will identify which dataflows are using the most resources. Running this statement on a small cluster with 4 workers, we find:

|             object              | global_id |  total_elapsed  | total_memory | total_records |
|:--------------------------------|----------:|----------------:|-------------:|--------------:|
| materialize.public.wins_by_item | u8        | 00:00:50.731033 | 42 MB        |        861512 |
| materialize.public.wins_by_item | u9        | 00:00:00.992696 | 406 kB       |         15950 |

Note that the output is sorted by `total_elapsed`---the output is ordered by whichever property is listed first. Here it _also_ happens to be sorted by `total_memory` and `total_records`: the dataflows processing the most data took the most time. On a cluster with dozens of indexes and materialized views, `EXPLAIN ANALYZE CLUSTER` reveals which dataflows are consuming the most resources.

We can quickly find skewed dataflows on a cluster by running `EXPLAIN ANALYZE CLUSTER MEMORY WITH SKEW`; here is an example on a small cluster with 4 workers:

| object                          | global_id | worker_id | max_operator_memory_ratio | worker_memory | avg_memory | total_memory | max_operator_records_ratio | worker_records | avg_records | total_records |
|:--------------------------------|----------:|----------:|--------------------------:|--------------:|-----------:|-------------:|---------------------------:|---------------:|------------:|--------------:|
| materialize.public.wins_by_item | u9        | 2         |                      1.63 | 164 kB        | 101 kB     | 404 kB       |                       1.62 |           6411 |      3968.5 |         15874 |
| materialize.public.wins_by_item | u9        | 1         |                      1.58 | 159 kB        | 101 kB     | 404 kB       |                       1.58 |           6286 |      3968.5 |         15874 |
| materialize.public.wins_by_item | u8        | 1         |                      1.06 | 10 MB         | 10 MB      | 41 MB        |                          1 |         213718 |    214325.5 |        857302 |
| materialize.public.wins_by_item | u8        | 0         |                      1.01 | 10 MB         | 10 MB      | 41 MB        |                          1 |         215075 |    214325.5 |        857302 |
| materialize.public.wins_by_item | u8        | 3         |                      1.01 | 10 MB         | 10 MB      | 41 MB        |                          1 |         214020 |    214325.5 |        857302 |
| materialize.public.wins_by_item | u8        | 2         |                         1 | 10 MB         | 10 MB      | 41 MB        |                          1 |         214489 |    214325.5 |        857302 |
| materialize.public.wins_by_item | u9        | 0         |                      0.79 | 80 kB         | 101 kB     | 404 kB       |                        0.8 |           3177 |      3968.5 |         15874 |
| materialize.public.wins_by_item | u9        | 3         |                         0 | 272 bytes     | 101 kB     | 404 kB       |                            |                |      3968.5 |         15874 |

The `u9` and `u8` dataflows make up the `wins_by_item` dataflow (where `u8` does the work and `u9` arranges it).
Both dataflows run on all four workers.
We report the `max_operator_memory_ratio` for each worker on each dataflow: what is the ratio of that dataflow's memory usage to the average memory usage across all workers?
Note that the output results are sorted by `max_operator_memory_ratio`, making it easy to spot skew. Here, workers 1 and 2 hold most of the records; worker 0 has half as many, and worker 3 has none at all.

### `EXPLAIN ANALYZE ... AS SQL`

Under the hood:

- For returning Memory/CPU information, `EXPLAIN ANALYZE` runs SQL queries that
correlate [`mz_introspection` performance
information](https://materialize.com/docs/sql/system-catalog/mz_introspection/)
with the LIR operators in
[`mz_introspection.mz_lir_mapping`](/sql/system-catalog/mz_introspection/#mz_lir_mapping).
Its `lir_id` is the node ID that `EXPLAIN PHYSICAL PLAN WITH (node identifiers)`
prints, so a row of that SQL can be matched to a plan operator by ID rather
than by its text.

- For TopK hints, `EXPLAIN ANALYZE` uses
[`mz_introspection.mz_expected_group_size_advice`](/sql/system-catalog/mz_introspection/#mz_expected_group_size_advice)
introspection source to offer hints on sizing `TopK` operators.

You can append `AS SQL` to any `EXPLAIN ANALYZE` statement to see the SQL that
would be run (without running it). You can then customize this SQL to report
finer grained or other information. For example:

```mzsql
EXPLAIN ANALYZE HINTS FOR INDEX wins_by_item AS SQL;
```

The results show the SQL that `EXPLAIN ANALYZE` would run to get the TopK hints
for the `wins_by_items` index.

[TopK hints]: /transform-data/idiomatic-materialize-sql/top-k/#query-hints-1

<!-- mz-docs page: sql/explain-filter-pushdown -->

# EXPLAIN FILTER PUSHDOWN
`EXPLAIN FILTER PUSHDOWN` reports filter pushdown statistics for `SELECT` statements and materialized views.

> **Public Preview:** This feature is in public preview.

`EXPLAIN FILTER PUSHDOWN` reports filter pushdown statistics for `SELECT`
statements and materialized views.

## Syntax

```mzsql
EXPLAIN FILTER PUSHDOWN
FOR <select_stmt | MATERIALIZED VIEW <name>>

```

| Syntax element | Description |
| --- | --- |
| **FOR** `<select_stmt>` | Display statistics for an ad-hoc [`SELECT`](/sql/select) statement.  |
| **FOR MATERIALIZED VIEW** `<name>` | Display statistics for an existing materialized view.  |

## Details

Materialize's [filter pushdown optimization](../../transform-data/patterns/temporal-filters/#temporal-filter-pushdown)
can be critical for large or append-only collections, since queries with a short
temporal filter many only need to fetch a small number of recent updates
instead of the full history of the data over time. However, it can be hard to
predict how well this optimization will behave for a particular query and
dataset. The standard [`EXPLAIN PLAN`](../../sql/explain-plan/#output-modifiers)
command can give some guidance as to whether this optimization applies to a
query at all... but exactly how much data gets filtered out will depend on both
statistics about the data itself, as well as how the data is chunked into
parts.

`EXPLAIN FILTER PUSHDOWN` looks at the current durable state of the collection,
determines exactly which parts are necessary to answer a `SELECT` query or
rehydrate a materialized view, and reports the total number of parts and bytes
that the query has selected, along with the total number of parts and bytes in
the shard.

## Examples

For the following examples, assume that you have created [an auction house load
generator source](/sql/create-source/load-generator/#creating-an-auction-load-generator)
in your environment.

### Explaining a `SELECT` query

Suppose you're interested in checking the number of recent bids.

```mzsql
SELECT count(*) FROM bids WHERE bid_time + '5 minutes' > mz_now();
```

Over time, the number of bids will grow indefinitely, but the number of recent
bids should stay about the same. If the filter pushdown optimization can make
sure that this query only needs to fetch recent bids from the storage layer
instead of _all_ historical bids, that could have an extreme impact in
performance.

Explaining this query includes a `pushdown=` field under `Source materialize.public.bids`,
which indicates that this filter can be pushed down.

```mzsql
EXPLAIN
SELECT count(*) FROM bids WHERE bid_time + '5 minutes' > mz_now();
```

```nofmt
...

 Source materialize.public.bids
   filter=((timestamp_tz_to_mz_timestamp((#4{bid_time} + 00:05:00)) > mz_now()))
   pushdown=((timestamp_tz_to_mz_timestamp((#4{bid_time} + 00:05:00)) > mz_now()))
```

However, this doesn't suggest how effective filter pushdown will be. Suppose you
have two queries: one which filters to the last minute and one to the last
hour; both can be pushed down, but the second will probably fetch much more
data.

Suppose it's been \~1 hour since you set up the auction house load generator
source, and you'd like to get a sense of how much data your query would need to
fetch.

```mzsql
EXPLAIN FILTER PUSHDOWN FOR
SELECT count(*) FROM bids WHERE bid_time + '5 minutes' > mz_now();
```

```nofmt
         Source          | Total Bytes | Selected Bytes | Total Parts | Selected Parts
-------------------------+-------------+----------------+-------------+----------------
 materialize.public.bids | 146508      | 34621          | 19          | 11
```

It looks like Materialize is fetching about a fifth of the data in terms of
bytes, and about half of the individual parts (this is not unexpected:
Materialize stores older data in larger chunks). If you run this query again,
you'll see the numbers change as more data is ingested and Materialize compacts
it into more efficient representations in the background.

If you instead query for the last hour of data, you can see that since you only
created the auction house source \~1 hour ago, Materialize needs to fetch
almost everything.

```mzsql
EXPLAIN FILTER PUSHDOWN FOR
SELECT count(*) FROM bids WHERE bid_time + '1 hour' > mz_now();
```

```nofmt
         Source          | Total Bytes | Selected Bytes | Total Parts | Selected Parts
-------------------------+-------------+----------------+-------------+----------------
 materialize.public.bids | 162473      | 162473         | 17          | 17
```

## Privileges

The privileges required to execute this statement are:

- `USAGE` privileges on the schemas that all relations in the explainee are
  contained in.

<!-- mz-docs page: sql/explain-plan -->

# EXPLAIN PLAN
Reference page for `EXPLAIN PLAN`. `EXPLAIN PLAN` is used to inspect the plans of `SELECT` statements, `SUBSCRIBE` statements, indexes, and materialized views.
`EXPLAIN PLAN` displays the plans used for:

|                             |                       |
|-----------------------------|-----------------------|
| <ul><li>`SELECT` statements </li><li>`CREATE VIEW` statements</li><li>`CREATE INDEX` statements</li><li>`CREATE MATERIALIZED VIEW` statements</li><li>`SUBSCRIBE` statements</li></ul>|<ul><li>Existing views</li><li>Existing indexes</li><li>Existing materialized views</li></ul> |

> **Warning:** `EXPLAIN` is not part of Materialize's stable interface and is not subject to
> our backwards compatibility guarantee. The syntax and output of `EXPLAIN` may
> change arbitrarily in future versions of Materialize.

## Syntax

**FOR SELECT:**
```mzsql
EXPLAIN [ [ RAW | DECORRELATED | [LOCALLY] OPTIMIZED | PHYSICAL ] PLAN
    [ WITH (<output_modifier> [, <output_modifier> ...])]
    [ AS TEXT | AS JSON ]
FOR ]       -- The FOR keyword is required if the PLAN keyword is specified
    <SELECT ...>
;
```

**FOR CREATE VIEW:**

```mzsql
EXPLAIN <RAW | DECORRELATED | LOCALLY OPTIMIZED> PLAN
    [ WITH (<output_modifier> [, <output_modifier> ...]) ]
    [ AS TEXT | AS JSON ]
FOR
    <CREATE VIEW ...>
;
```

**FOR CREATE INDEX:**
```mzsql
EXPLAIN [ [ OPTIMIZED | PHYSICAL ] PLAN
    [ WITH (<output_modifier> [, <output_modifier> ...]) ]
    [ AS TEXT | AS JSON ]
FOR ]  -- The FOR keyword is required if the PLAN keyword is specified
    <CREATE INDEX ...>
;
```

**FOR CREATE MATERIALIZED VIEW:**
```mzsql
EXPLAIN [ [ RAW | DECORRELATED | [LOCALLY] OPTIMIZED | PHYSICAL ] PLAN
    [ WITH (<output_modifier> [, <output_modifier> ...])]
    [ AS TEXT | AS JSON ]
FOR ]          -- The FOR keyword is required if the PLAN keyword is specified
    <CREATE MATERIALIZED VIEW ...>
;
```

**FOR VIEW:**
```mzsql
EXPLAIN <RAW | LOCALLY OPTIMIZED> PLAN
    [ WITH (<output_modifier> [, <output_modifier> ...])]
    [ AS TEXT | AS JSON ]
FOR
  VIEW <name>
;
```

**FOR INDEX:**
```mzsql
EXPLAIN [ [ OPTIMIZED | PHYSICAL ] PLAN
      [ WITH (<output_modifier> [, <output_modifier> ...]) ]
      [ AS TEXT | AS JSON ]
FOR ]  -- The FOR keyword is required if the PLAN keyword is specified
  INDEX <name>
;
```

**FOR MATERIALIZED VIEW:**
```mzsql
EXPLAIN [[ RAW | [LOCALLY] OPTIMIZED | PHYSICAL ] PLAN
    [ WITH (<output_modifier> [, <output_modifier> ...]) ]
    [ AS TEXT | AS JSON ]
FOR ] -- The FOR keyword is required if the PLAN keyword is specified
  MATERIALIZED VIEW <name>
;
```

**FOR SUBSCRIBE:**
```mzsql
EXPLAIN [ [ OPTIMIZED | PHYSICAL ] PLAN
    [ WITH (<output_modifier> [, <output_modifier> ...]) ]
    [ AS TEXT | AS JSON ]
FOR ]  -- The FOR keyword is required if the PLAN keyword is specified
    <SUBSCRIBE ...>
;
```

Note that the `FOR` keyword is required if the `PLAN` keyword is present. The following three statements are equivalent:

```mzsql
EXPLAIN <explainee>;
EXPLAIN PLAN FOR <explainee>;
EXPLAIN PHYSICAL PLAN AS TEXT FOR <explainee>;
```

If `PHSYICAL PLAN` is specified without an `AS`-format, we will provide output similar to the above, but more verbose. The following two statements are equivalent (and produce the more verbose output):

```mzsql
EXPLAIN PHYSICAL PLAN FOR <explainee>;
EXPLAIN PHYSICAL PLAN AS VERBOSE TEXT FOR <explainee>;
```

### Explained object

The following object types can be explained.

Explained object | Description
------|-----
**select_stmt** | Display a plan for an ad-hoc [`SELECT` statement](../select).
**create_view** | Display a plan for a [`CREATE VIEW` statement](../create-view).
**create_index** | Display a plan for a [`CREATE INDEX` statement](../create-index).
**create_materialized_view** | Display a plan for a [`CREATE MATERIALIZED VIEW` statement](../create-materialized-view).
**subscribe_stmt** | Display an `OPTIMIZED` or `PHYSICAL` plan for a [`SUBSCRIBE` statement](../subscribe).
**VIEW name** | Display the `RAW` or `LOCALLY OPTIMIZED` plan for an existing view.
**INDEX name** | Display the `OPTIMIZED` or `PHYSICAL` plan for an existing index.
**MATERIALIZED VIEW name** | Display the `OPTIMIZED` or `PHYSICAL` plan for an existing materialized view.

### Output format

You can select between `JSON` and `TEXT` for the output format of `EXPLAIN PLAN`. Non-text
output is more machine-readable and can be parsed by common graph visualization libraries,
while formatted text is more human-readable.

Output type | Description
------|-----
**TEXT** | Format the explanation output as UTF-8 text.
**JSON** | Format the explanation output as a JSON object.

### Explained stage

This stage determines the query optimization stage at which the plan snapshot will be taken.

Plan Stage | Description
------|-----
**RAW PLAN** | Display the raw plan; this is closest to the original SQL.
**DECORRELATED PLAN** | Display the decorrelated but not-yet-optimized plan.
**LOCALLY OPTIMIZED** | Display the locally optimized plan (before view inlining and access path selection). This is the final stage for regular `CREATE VIEW` optimization.
**OPTIMIZED PLAN** | Display the optimized plan.
**PHYSICAL PLAN** |  Display the physical plan; this corresponds to the operators shown in [`mz_introspection.mz_lir_mapping`](/sql/system-catalog/mz_introspection/#mz_lir_mapping). _(Default)_

### Output modifiers

Output modifiers act as boolean toggles and can be combined in order to slightly tweak
the information and rendering style of the generated explanation output.

Modifier | Description
------|-----
**arity** | _(on by default)_ Annotate each subplan with its number of produced columns. This is useful due to the use of offset-based column names.
**cardinality** | Annotate each subplan with a symbolic estimate of its cardinality.
**join implementations** | Render details about the [implementation strategy of optimized MIR `Join` nodes](#explain-with-join-implementations).
**keys** | Annotates each subplan with a parenthesized list of unique keys. Each unique key is presented as a bracketed list of column identifiers. A list of column identifiers is reported as a unique key when for each setting of those columns to values there is at most one record in the collection. For example, `([0], [1,2])` is a list of two unique keys: column zero is a unique key, and columns 1 and 2 also form a unique key. Materialize only reports the most succinct form of keys, so for example while `[0]` and `[0, 1]` might both be unique keys, the latter is implied by the former and omitted. `()` indicates that the collection does not have any unique keys, while `([])` indicates that the empty projection is a unique key, meaning that the collection consists of 0 or 1 rows.
**node identifiers** | Annotate each subplan in a `PHYSICAL PLAN` with its node ID, which is the `lir_id` of the operator's row in [`mz_introspection.mz_lir_mapping`](/sql/system-catalog/mz_introspection/#mz_lir_mapping). Per-operator introspection, such as the SQL behind [`EXPLAIN ANALYZE`](/sql/explain-analyze/), can be matched to the plan by that ID instead of by operator text, which the two render differently.
**redacted** | Anonymize literals in the output.
**timing** | Annotate the output with the optimization time.
**types** | Annotate each subplan with its inferred type, as a _representation type_. These types, written with a `r_` prefix, reflect how the types in your SQL query are actually represented inside Materialize---don't be alarmed if you wrote `VARCHAR` or `CHAR` but see `r_string`.
**humanized expressions** | _(on by default)_ Add human-readable column names to column references. For example, `#0{id}` refers to column 0, whose name is `id`. Note that SQL-level aliasing is not considered when inferring column names, which means that the displayed column names can be ambiguous.
**filter pushdown** | _(on by default)_ For each source, include a `pushdown` field that explains which filters [can be pushed down to the storage layer](../../transform-data/patterns/temporal-filters/#temporal-filter-pushdown).

Note that most modifiers are currently only supported for the `AS TEXT` output.

## Details

To execute `SELECT` statements, Materialize generates a plan consisting of
operators that interface with our underlying Differential dataflow engine.
`EXPLAIN PLAN` lets you see the plan for a given query, which can provide insight
into Materialize's behavior for specific queries, e.g. performance.

### Query compilation pipeline

The job of the Materialize planner is to turn SQL code into a differential
dataflow program. We get there via a series of progressively lower-level plans:

```text
SQL ⇒ raw plan ⇒ decorrelated plan ⇒ optimized plan ⇒ physical plan ⇒ dataflow
```

#### From SQL to raw plan

In this stage, the planner:

- Replaces SQL variable names with column numbers.
- Infers the type of each expression.
- Chooses the correct overload for each function.

#### From raw plan to decorrelated plan

In this stage, the planner:

- Replaces subqueries and lateral joins with non-nested operations.
- Replaces `OUTER` joins with lower-level operations.
- Replaces global aggregate default values with lower-level operations.

#### From decorrelated plan to optimized plan

In this stage, the planner performs various optimizing rewrites:

- Coalesces joins.
- Chooses join order and implementation.
- Fuses adjacent operations.
- Removes redundant operations.
- Pushes down predicates.
- Evaluates any operations on constants.

#### From optimized plan to physical plan

In this stage, the planner:

- Decides on the exact execution details of each operator, and maps plan operators to differential dataflow operators.
- Makes the final choices about creating or reusing [arrangements](/fundamentals/concepts/arrangements/#arrangements).

#### From physical plan to dataflow

In the final stage, the planner:

- Renders an actual dataflow from the physical plan, and
- Installs the new dataflow into the running system.

The rendering step does not make any further optimization choices, as the physical plan is meant to
be a definitive and complete description of the rendered dataflow.

### Fast path queries

Queries are sometimes implemented using a _fast path_.
In this mode, the program that implements the query will just hit an existing index,
transform the results, and optionally apply a finishing action. For fast path queries,
all of these actions happen outside of the regular dataflow engine. The fast path is
indicated by an "Explained Query (fast path):" heading before the explained query in the `EXPLAIN`,
`EXPLAIN OPTIMIZED PLAN` and `EXPLAIN PHYSICAL PLAN` result.

```text
Explained Query (fast path):
  Project (#0, #1)
    ReadIndex on=materialize.public.t1 t1_x_idx=[lookup value=(5)]

Used Indexes:
  - materialize.public.t1_x_idx (lookup)
```

### Reading plans

Materialize plans are directed, potentially cyclic, graphs of operators. Each operator in the graph
receives inputs from zero or more other operators and produces a single output.
Sub-graphs where each output is consumed only once are rendered as tree-shaped fragments.
Sub-graphs consumed more than once are represented as common table expressions (CTEs).
In the example below, the CTE `l0` represents a linear sub-plan (a chain of `Read` from the table `t`)
which is used in both inputs of a self-join (`Differential Join`).

```text
> CREATE TABLE t(x INT NOT NULL, y INT NOT NULL);
CREATE TABLE
> EXPLAIN SELECT t1.x, t1.y
          FROM (SELECT * FROM t WHERE x > y) AS t1,
               (SELECT * FROM t where x > y) AS t2
          WHERE t1.y = t2.y;
                     Physical Plan
--------------------------------------------------------
 Explained Query:                                      +
   →With                                               +
     cte l0 =                                          +
       →Read materialize.public.t                      +
   →Return                                             +
     →Differential Join %0 » %1                        +
       Join stage %0: Lookup key #0{y} in %1           +
       →Arrange                                        +
         Keys: 1 arrangement available, plus raw stream+
           Arrangement 0: #1{y}                        +
         →Stream l0                                    +
       →Arrange                                        +
         Keys: 1 arrangement available, plus raw stream+
           Arrangement 0: #0{y}                        +
         →Read l0                                      +
                                                       +
 Source materialize.public.t                           +
   filter=((#0{x} > #1{y}))                            +
                                                       +
 Target cluster: quickstart                            +
```

Note that CTEs in optimized plans do not directly correspond to CTEs in your original SQL query: For example, CTEs might disappear due to inlining (i.e., when a CTE is used only once, its definition is copied to that usage site); new CTEs can appear due to the optimizer recognizing that a part of the query appears more than once (aka common subexpression elimination). Also, certain SQL-level concepts, such as outer joins or subqueries, do not have an explicit representation in optimized plans, and are instead expressed as a pattern of operators involving CTEs. CTE names are always `l0`, `l1`, `l2`, ..., and do not correspond to SQL-level CTE names.

<a name="explain-plan-columns"></a>

Many operators need to refer to columns in their input. These are displayed like
`#3` for column number 3. (Columns are numbered starting from column 0). To get a better sense of
columns assigned to `Map` operators, it might be useful to request [the `arity` output modifier](#output-modifiers).

Each operator can also be annotated with additional metadata. Some details are shown in the `EXPLAIN` output (`EXPLAIN PHYSICAL PLAN AS TEXT`), but are hidden elsewhere. <a
name="explain-with-join-implementations"></a>In `EXPLAIN OPTIMIZED
PLAN`, details about the implementation in the `Join` operator can be requested
with [the `join implementations` output modifier](#output-modifiers) (that is,
`EXPLAIN OPTIMIZED PLAN WITH (join implementations) FOR ...`).

```text
Join on=(#1 = #2 AND #3 = #4) type=delta
  implementation
    %0:t » %1:u[#0]K » %2:v[#0]K
    %1:u » %0:t[#1]K » %2:v[#0]K
    %2:v » %1:u[#1]K » %0:t[#1]K
  ArrangeBy keys=[[#1]]
    ReadStorage materialize.public.t
  ArrangeBy keys=[[#0], [#1]]
    ReadStorage materialize.public.u
  ArrangeBy keys=[[#0]]
    ReadStorage materialize.public.v
```
The `%0`, `%1`, etc. refer to each of the join inputs.
A *differential* join shows one join path, which is simply a sequence of binary
joins (each of whose results need to be maintained as state).
A [*delta* join](/transform-data/optimization/#optimize-multi-way-joins-with-delta-joins)
shows a join path for each of the inputs.
The expressions in
a bracket show the key for joining with that input. The letters after the brackets
indicate the input characteristics used for join ordering. `U` means unique, the
number of `K`s means the key length, `A` means already arranged (e.g., an index
exists). The small letters refer to filter characteristics:
**e**quality to a literal,
**l**ike,
is **n**ull,
**i**nequality to a literal,
any **f**ilter.

A plan can optionally end with a finishing action, which can sort, limit and
project the result data. This operator is special, as it can only occur at the
top of the plan. Finishing actions are executed outside the parallel dataflow
that implements the rest of the plan.

```
Finish order_by=[#1 asc nulls_last, #0 desc nulls_first] limit=5 output=[#0, #1]
  CrossJoin
    ReadStorage materialize.public.r
    ReadStorage materialize.public.s
```

Below the plan, a "Used indexes" section indicates which indexes will be used by the query, [and in what way](/transform-data/optimization/#use-explain-to-verify-index-usage).

### Reference: Plan operators

Materialize offers several output formats for `EXPLAIN` and debugging.
LIR plans as rendered in
[`mz_introspection.mz_lir_mapping`](/sql/system-catalog/mz_introspection/#mz_lir_mapping)
are deliberately succinct, while the plans in other formats give more
detail.

The decorrelated and optimized plans from `EXPLAIN DECORRELATED PLAN
FOR ...`, `EXPLAIN LOCALLY OPTIMIZED PLAN FOR ...`, and `EXPLAIN
OPTIMIZED PLAN FOR ...` are in a mid-level representation that is
closer to LIR than SQL. The raw plans from `EXPLAIN RAW PLAN FOR ...`
are closer to SQL (and therefore less indicative of how the query will
actually run).

**In fully optimized physical (LIR) plans (Default):**
The following table lists the operators that are available in the LIR plan.

- For those operators that require memory to maintain intermediate state, **Uses memory** is marked with **Yes**.
- For those operators that expand the data size (either rows or columns), **Can increase data size** is marked with **Yes**.| Operator | Description | Example |
| --- | --- | --- |
| **Constant** | Always produces the same collection of rows.  **Can increase data size:** No **Uses memory:** No | <code>→Constant (2 rows)</code> |
| **Stream, Arranged, Index Lookup, Read** | <p>Produces rows from either an existing relation (source/view/materialized view/table) or from a previous CTE in the same plan. A <code>Fused with Child Map/Filter/Project</code> line above this operator means that <code>Map/Filter/Project</code> runs inside it.</p> <p>There are four types of <code>Get</code>.</p> <ol> <li> <p><code>Stream</code> indicates that the results are not <a href="/fundamentals/concepts/arrangements/#arrangements" >arranged</a> in memory and will be streamed directly.</p> </li> <li> <p><code>Arranged</code> indicates that the results are <a href="/fundamentals/concepts/arrangements/#arrangements" >arranged</a> in memory.</p> </li> <li> <p><code>Index Lookup</code> indicates the results will be <em>looked up</em> in an existing <a href="/fundamentals/concepts/arrangements/#arrangements" >arrangement</a>.</p> </li> <li> <p><code>Read</code> indicates that the results are unarranged, and will be processed as they arrive.</p> </li> </ol>   **Can increase data size:** No **Uses memory:** No | <code>Arranged materialize.public.t</code> |
| **Map/Filter/Project** | <p>Computes new columns (maps), filters columns, and projects away columns. Works row-by-row. Maps and filters will be printed, but projects will not.</p> <p>A <code>Map/Filter/Project</code> fused into a neighboring operator is printed as <code>Fused with Child Map/Filter/Project</code> above that operator, or as <code>Fused with Parent Map/Filter/Project</code> below an <code>Arrange</code>, and runs inside that operator rather than on its own.</p> <p>A temporal filter, one whose predicate uses <a href="/sql/functions/now_and_mz_now/" ><code>mz_now()</code></a>, also schedules a retraction of each row for the moment it stops satisfying the predicate. Until then, the operator downstream holds that pending retraction in memory, one per live row.</p>   **Can increase data size:** Each row may have more data, from the <code>Map</code>. Each row may also have less data, from the <code>Project</code>. There may be fewer rows, from the <code>Filter</code>. **Uses memory:** No | <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="err">→</span><span class="k">Map</span><span class="o">/</span><span class="k">Filter</span><span class="o">/</span><span class="n">Project</span> </span></span><span class="line"><span class="cl">  <span class="k">Filter</span><span class="p">:</span> <span class="p">(</span><span class="o">#</span><span class="mf">0</span><span class="p">{</span><span class="n">a</span><span class="p">}</span> <span class="o">&lt;</span> <span class="mf">7</span><span class="p">)</span> </span></span><span class="line"><span class="cl">  <span class="k">Map</span><span class="p">:</span> <span class="p">(</span><span class="o">#</span><span class="mf">0</span><span class="p">{</span><span class="n">a</span><span class="p">}</span> <span class="o">+</span> <span class="o">#</span><span class="mf">1</span><span class="p">{</span><span class="n">b</span><span class="p">})</span> </span></span></code></pre></div> |
| **Table Function** | <p>Appends the result of some (one-to-many) <a href="/sql/functions/#table-functions" >table function</a> to each row in the input.</p> <p>A <code>Fused with Child Table Function unnest_list</code> line above a <code>Non-incremental GroupAggregate</code> means the <code>unnest_list</code> call runs inside that aggregation, which is part of how window functions are compiled to dataflows.</p> <p>A <code>Fused with Child Map/Filter/Project</code> line above this operator means that <code>Map/Filter/Project</code> runs inside it.</p>   **Can increase data size:** Depends on the <a href="/sql/functions/#table-functions" >table function</a> used. **Uses memory:** No | <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="err">→</span><span class="k">Table</span> <span class="k">Function</span> <span class="n">generate_series</span><span class="p">(</span><span class="o">#</span><span class="mf">0</span><span class="p">{</span><span class="n">a</span><span class="p">},</span> <span class="o">#</span><span class="mf">1</span><span class="p">{</span><span class="n">b</span><span class="p">},</span> <span class="mf">1</span><span class="p">)</span> </span></span><span class="line"><span class="cl">  <span class="k">Input</span> <span class="k">key</span><span class="p">:</span> <span class="p">(</span><span class="o">#</span><span class="mf">0</span><span class="p">{</span><span class="n">a</span><span class="p">})</span> </span></span></code></pre></div> |
| **Differential Join, Delta Join** | <p>Both join operators indicate the join ordering selected.</p> <p>Returns combinations of rows from each input whenever some equality predicates are <code>true</code>.</p> <p>Joins will indicate the join order of their children, starting from 0. For example, <code>Differential Join %1 » %0</code> will join its second child into its first.</p> <p>The <a href="/transform-data/optimization/#join" >two joins differ in performance characteristics</a>.</p> <p><code>Differential Cross Join</code> and <code>Delta Cross Join</code> mark a join with a stage that has no equality keys. <code>One-Shot Delta Join</code> marks the single-path plan of a one-shot <code>SELECT</code>; an index or materialized view over the same query uses the multi-path <code>Delta Join</code>.</p>   **Can increase data size:** Depends on the join order and facts about the joined collections. **Uses memory:** ✅ Uses memory for 3-way or more differential joins. | <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="err">→</span><span class="n">Differential</span> <span class="k">Join</span> <span class="o">%</span><span class="mf">1</span> <span class="err">»</span> <span class="o">%</span><span class="mf">0</span> </span></span><span class="line"><span class="cl">  <span class="k">Join</span> <span class="n">stage</span> <span class="o">%</span><span class="mf">0</span><span class="p">:</span> <span class="n">Lookup</span> <span class="k">key</span> <span class="o">#</span><span class="mf">0</span><span class="p">{</span><span class="n">a</span><span class="p">}</span> <span class="k">in</span> <span class="o">%</span><span class="mf">0</span> </span></span></code></pre></div> |
| **GroupAggregate** | <p>Groups the input rows by some scalar expressions, reduces each group using some aggregate functions, and produces rows containing the group key and aggregate outputs.</p> <p>There are four types of <code>GroupAggregate</code>, ordered by increasing complexity:</p> <ol> <li> <p><code>Distinct GroupAggregate</code> corresponds to the SQL <code>DISTINCT</code> operator.</p> </li> <li> <p><code>Accumulable GroupAggregate</code> (e.g., <code>SUM</code>, <code>COUNT</code>) corresponds to several easy to implement aggregations that can be executed efficiently.</p> </li> <li> <p>Hierarchical aggregations (e.g., <code>MIN</code>, <code>MAX</code>) require a tower of arrangements. They are printed as <code>Bucketed Hierarchical GroupAggregate</code>, or as the more efficient <code>Monotonic GroupAggregate</code> when the input never retracts data. Bucketed ones may benefit from a hint; <a href="/sql/system-catalog/mz_introspection/#mz_expected_group_size_advice" >see <code>mz_introspection.mz_expected_group_size_advice</code></a>. A <code>Consolidating</code> prefix means the operator consolidates its input first, which uses memory while the input is being consolidated, largely at hydration time.</p> </li> <li> <p><code>Non-incremental GroupAggregate</code> (e.g., window functions, <code>list_agg</code>) corresponds to a single non-incremental aggregation. These are the most computationally intensive reductions.</p> </li> </ol> <p>A query that mixes aggregations of different types is planned as one <code>GroupAggregate</code> per type, joined together on the group key.</p> <p>A <code>Temporally-Bucketed</code> prefix means the input carries future-dated updates from a temporal filter.</p> <p>A <code>Fused with Child Map/Filter/Project</code> line above this operator means that <code>Map/Filter/Project</code> runs inside it.</p>   **Can increase data size:** No **Uses memory:** ✅ <code>Distinct</code> and <code>Accumulable</code> aggregates use a moderate amount of memory (proportional to twice the output size). <code>MIN</code> and <code>MAX</code> aggregates can use significantly more memory. This can be improved by including group size hints in the query, see <a href="/sql/system-catalog/mz_introspection/#mz_expected_group_size_advice" ><code>mz_introspection.mz_expected_group_size_advice</code></a>. A hint shrinks the tower of intermediate arrangements (the <code>buckets</code> list of a <code>Bucketed Hierarchical GroupAggregate</code>); the input rows stay arranged either way, so a hint cannot bring a <code>MIN</code> or <code>MAX</code> below the size of its input. <code>Non-incremental</code> aggregates use memory proportional to the input + output size. A mix of aggregation types uses the memory of each <code>GroupAggregate</code> plus the arrangements of the join that combines them. | <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="err">→</span><span class="n">Accumulable</span> <span class="n">GroupAggregate</span> </span></span><span class="line"><span class="cl">  <span class="n">Simple</span> <span class="n">aggregates</span><span class="p">:</span> <span class="k">count</span><span class="p">(</span><span class="o">*</span><span class="p">)</span> </span></span><span class="line"><span class="cl">  <span class="n">Post</span><span class="o">-</span><span class="n">process</span> <span class="k">Map</span><span class="o">/</span><span class="k">Filter</span><span class="o">/</span><span class="n">Project</span> </span></span><span class="line"><span class="cl">    <span class="k">Filter</span><span class="p">:</span> <span class="p">(</span><span class="o">#</span><span class="mf">0</span> <span class="o">&gt;</span> <span class="mf">1</span><span class="p">)</span> </span></span></code></pre></div> |
| **TopK** | <p>Groups the input rows, sorts them according to some ordering, and returns at most <code>K</code> rows at some offset from the top of the list, where <code>K</code> is some (possibly computed) limit.</p> <p>There are three types of <code>TopK</code>. Two are special cased for monotonic inputs (i.e., inputs which never retract data).</p> <ol> <li><code>Monotonic Top1</code>.</li> <li><code>Monotonic TopK</code>, which may give an expression indicating the limit.</li> <li><code>Non-monotonic TopK</code>, a generic <code>TopK</code> plan.</li> </ol> <p>Each version of the <code>TopK</code> operator may include grouping, ordering, and limit directives. A <code>Consolidating</code> prefix means the operator consolidates its input first, and a <code>Temporally-Bucketed</code> prefix means the input carries future-dated updates from a temporal filter.</p>   **Can increase data size:** No **Uses memory:** ✅ <code>Monotonic Top1</code> and <code>Monotonic TopK</code> use a moderate amount of memory. <code>Non-monotonic TopK</code> uses significantly more memory as the operator can significantly overestimate the group sizes. Consult <a href="/sql/system-catalog/mz_introspection/#mz_expected_group_size_advice" ><code>mz_introspection.mz_expected_group_size_advice</code></a>. A <code>LIMIT INPUT GROUP SIZE</code> hint is not displayed in this plan; the optimized plan shows it as <code>exp_group_size</code>. | <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="err">→</span><span class="n">Consolidating</span> <span class="n">Monotonic</span> <span class="n">TopK</span> </span></span><span class="line"><span class="cl">  <span class="k">Order</span> <span class="k">By</span> <span class="o">#</span><span class="mf">1</span> <span class="k">asc</span> <span class="n">nulls_last</span><span class="p">,</span> <span class="o">#</span><span class="mf">0</span> <span class="k">desc</span> <span class="n">nulls_first</span> </span></span><span class="line"><span class="cl">  <span class="k">Limit</span> <span class="mf">5</span> </span></span></code></pre></div> |
| **Negate Diffs** | Negates the row counts of the input. This is usually used in combination with union to remove rows from the other union input.  **Can increase data size:** No **Uses memory:** No | <code>→Negate Diffs</code> |
| **Threshold Diffs** | Removes any rows with negative counts.  **Can increase data size:** No **Uses memory:** ✅ Arranges both its input and its output by the whole row, so it uses memory proportional to the input size plus the output size. | <code>→Threshold Diffs</code> |
| **Union** | Combines its inputs into a unified output, emitting one row for each row on any input. (Corresponds to <code>UNION ALL</code> rather than <code>UNION</code>/<code>UNION DISTINCT</code>.)  **Can increase data size:** No **Uses memory:** ✅ A <code>Consolidating Union</code> will make moderate use of memory, particularly at hydration time. A <code>Union</code> that is not <code>Consolidating</code> will not consume memory. | <code>→Consolidating Union</code> |
| **Arrange** | Indicates a point that will become an <a href="/fundamentals/concepts/arrangements/#arrangements" >arrangement</a> in the dataflow engine, i.e., it will consume memory to cache results.  **Can increase data size:** No **Uses memory:** ✅ Uses memory proportional to the input size. Note that in the LIR / physical plan, <code>Arrange</code>/<code>ArrangeBy</code> almost always means that an arrangement will actually be created. (This is in contrast to the &ldquo;optimized&rdquo; plan, where an <code>ArrangeBy</code> being present in the plan often does not mean that an arrangement will actually be created.) | <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="err">→</span><span class="n">Arrange</span> </span></span><span class="line"><span class="cl">    <span class="k">Keys</span><span class="p">:</span> <span class="mf">1</span> <span class="k">arrangement</span> <span class="n">available</span><span class="p">,</span> <span class="n">plus</span> <span class="k">raw</span> <span class="n">stream</span> </span></span><span class="line"><span class="cl">      <span class="k">Arrangement</span> <span class="mf">0</span><span class="p">:</span> <span class="o">#</span><span class="mf">0</span> </span></span></code></pre></div> |
| **Unarranged Raw Stream** | Indicates a point where data will be streamed (even if it is somehow already arranged).  **Can increase data size:** No **Uses memory:** No | <code>→Unarranged Raw Stream</code> |
| **With ... Return ...** | Introduces CTEs, i.e., makes it possible for sub-plans to be consumed multiple times by downstream operators.  **Can increase data size:** No **Uses memory:** No | <a href="/sql/explain-plan/#reading-plans" >See Reading plans</a> |
**Notes:**
- **Can increase data size:** Specifies whether the operator can increase the data size (can be the number of rows or the number of columns).
- **Uses memory:** Specifies whether the operator use memory to maintain state for its inputs.

**In decorrelated and optimized plans:**
The following table lists the operators that are available in the optimized plan.

- For those operators that require memory to maintain intermediate state, **Uses memory** is marked with **Yes**.
- For those operators that expand the data size (either rows or columns), **Can increase data size** is marked with **Yes**.| Operator | Description | Example |
| --- | --- | --- |
| **Constant** | Always produces the same collection of rows.  **Can increase data size:** No **Uses memory:** No | <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="n">Constant</span> </span></span><span class="line"><span class="cl"><span class="o">-</span> <span class="p">((</span><span class="mf">1</span><span class="p">,</span> <span class="mf">2</span><span class="p">)</span> <span class="n">x</span> <span class="mf">2</span><span class="p">)</span> </span></span><span class="line"><span class="cl"><span class="o">-</span> <span class="p">(</span><span class="mf">3</span><span class="p">,</span> <span class="mf">4</span><span class="p">)</span> </span></span></code></pre></div> |
| **Get** | Produces rows from either an existing relation (source/view/materialized view/table) or from a previous CTE in the same plan.  **Can increase data size:** No **Uses memory:** No | <code>Get materialize.public.ordered</code> |
| **Project** | Produces a subset of the <a href="/sql/explain-plan/#explain-plan-columns" >columns</a> in the input rows. See also <a href="/sql/explain-plan/#explain-plan-columns" >column numbering</a>.  **Can increase data size:** No **Uses memory:** No | <code>Project (#2, #3)</code> |
| **Map** | Appends the results of some scalar expressions to each row in the input.  **Can increase data size:** Each row has more data (i.e., longer rows but same number of rows). **Uses memory:** No | <code>Map (((#1 * 10000000dec) / #2) * 1000dec)</code> |
| **FlatMap** | Appends the result of some (one-to-many) <a href="/sql/functions/#table-functions" >table function</a> to each row in the input.  **Can increase data size:** Depends on the <a href="/sql/functions/#table-functions" >table function</a> used. **Uses memory:** No | <code>FlatMap jsonb_foreach(#3)</code> |
| **Filter** | <p>Removes rows of the input for which some scalar predicates return <code>false</code>.</p> <p>A temporal filter, one whose predicate uses <a href="/sql/functions/now_and_mz_now/" ><code>mz_now()</code></a>, also schedules a retraction of each row for the moment it stops satisfying the predicate. Until then, the operator downstream of the filter holds that pending retraction in memory, one per live row.</p>   **Can increase data size:** No **Uses memory:** No | <code>Filter (#20 &lt; #21)</code> |
| **Join** | Returns combinations of rows from each input whenever some equality predicates are <code>true</code>.  **Can increase data size:** Depends on the join order and facts about the joined collections. **Uses memory:** ✅ The <code>Join</code> operator itself uses memory only for <code>type=differential</code> with more than 2 inputs. However, <code>Join</code> operators need <a href="/fundamentals/concepts/arrangements/#arrangements" >arrangements</a> on their inputs (shown by the <code>ArrangeBy</code> operator). These arrangements use memory proportional to the input sizes. If an input has an <a href="/transform-data/optimization/#join" >appropriate index</a>, then the arrangement of the index will be reused. | <code>Join on=(#1 = #2) type=delta</code> |
| **CrossJoin** | An alias for a <code>Join</code> with an empty predicate (emits all combinations). Note that not all cross joins are marked as <code>CrossJoin</code>: In a join with more than 2 inputs, it can happen that there is a cross join between some of the inputs. You can recognize this case by <code>ArrangeBy</code> operators having empty keys, i.e., <code>ArrangeBy keys=[[]]</code>.  **Can increase data size:** Cartesian product of the inputs (\|N\| x \|M\|). **Uses memory:** ✅ Uses memory for 3-way or more differential joins. | <code>CrossJoin type=differential</code> |
| **Reduce** | Groups the input rows by some scalar expressions, reduces each group using some aggregate functions, and produces rows containing the group key and aggregate outputs.  **Can increase data size:** No **Uses memory:** ✅ <code>SUM</code>, <code>COUNT</code>, and most other aggregations use a moderate amount of memory (proportional either to twice the output size or to input size + output size). <code>MIN</code> and <code>MAX</code> aggregates can use significantly more memory. This can be improved by including group size hints in the query, see <a href="/sql/system-catalog/mz_introspection/#mz_expected_group_size_advice" ><code>mz_introspection.mz_expected_group_size_advice</code></a>. A hint shrinks the tower of intermediate arrangements, and shows in the optimized plan as <code>exp_group_size</code> and in the physical plan as the <code>buckets</code> list. The input rows stay arranged either way, so a hint cannot bring a <code>MIN</code> or <code>MAX</code> below the size of its input. | <code>Reduce group_by=[#0] aggregates=[max((#0 * #1))]</code> |
| **Distinct** | Alias for a <code>Reduce</code> with an empty aggregate list.  **Can increase data size:** No **Uses memory:** ✅ Uses memory proportional to twice the output size. | <code>Distinct</code> |
| **TopK** | Groups the input rows by some scalar expressions, sorts each group by the ordering expressions, removes the top <code>offset</code> rows in each group, and returns the next <code>limit</code> rows.  **Can increase data size:** No **Uses memory:** ✅ Can use significant amount as the operator can significantly overestimate the group sizes. Consult <a href="/sql/system-catalog/mz_introspection/#mz_expected_group_size_advice" ><code>mz_introspection.mz_expected_group_size_advice</code></a>. A <code>LIMIT INPUT GROUP SIZE</code> hint shows in the optimized plan as <code>exp_group_size</code>; the physical plan does not display it. | <code>TopK order_by=[#1 asc nulls_last, #0 desc nulls_first] limit=5</code> |
| **Negate** | Negates the row counts of the input. This is usually used in combination with union to remove rows from the other union input.  **Can increase data size:** No **Uses memory:** No | <code>Negate</code> |
| **Threshold** | Removes any rows with negative counts.  **Can increase data size:** No **Uses memory:** ✅ Arranges both its input and its output by the whole row, so it uses memory proportional to the input size plus the output size. | <code>Threshold</code> |
| **Union** | Sums the counts of each row of all inputs. (Corresponds to <code>UNION ALL</code> rather than <code>UNION</code>/<code>UNION DISTINCT</code>.)  **Can increase data size:** No **Uses memory:** ✅ A plain <code>Union</code> uses no memory of its own. A <code>Union</code> whose output must be consolidated holds updates while consolidating them, which shows as a memory spike largely at hydration time. | <code>Union</code> |
| **ArrangeBy** | Indicates a point that will become an <a href="/fundamentals/concepts/arrangements/#arrangements" >arrangement</a> in the dataflow engine (each <code>keys</code> element will be a different arrangement). Note that if an appropriate index already exists on the input or the output of the previous operator is already arranged with a key that is also requested here, then this operator will just pass on that existing arrangement instead of creating a new one.  **Can increase data size:** No **Uses memory:** ✅ Depends. If arrangements need to be created, they use memory proportional to the input size. | <code>ArrangeBy keys=[[#0]]</code> |
| **With ... Return ...** | Introduces CTEs, i.e., makes it possible for sub-plans to be consumed multiple times by downstream operators.  **Can increase data size:** No **Uses memory:** No | <a href="/sql/explain-plan/#reading-plans" >See Reading plans</a> |
**Notes:**
- **Can increase data size:** Specifies whether the operator can increase the data size (can be the number of rows or the number of columns).
- **Uses memory:** Specifies whether the operator use memory to maintain state for its inputs.

**In raw plans:**
The following table lists the operators that are available in the raw plan.

- For those operators that require memory to maintain intermediate state, **Uses memory** is marked with **Yes**.
- For those operators that expand the data size (either rows or columns), **Can increase data size** is marked with **Yes**.| Operator | Description | Example |
| --- | --- | --- |
| **Constant** | Always produces the same collection of rows.  **Can increase data size:** No **Uses memory:** No | <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="n">Constant</span> </span></span><span class="line"><span class="cl"><span class="o">-</span> <span class="p">((</span><span class="mf">1</span><span class="p">,</span> <span class="mf">2</span><span class="p">)</span> <span class="n">x</span> <span class="mf">2</span><span class="p">)</span> </span></span><span class="line"><span class="cl"><span class="o">-</span> <span class="p">(</span><span class="mf">3</span><span class="p">,</span> <span class="mf">4</span><span class="p">)</span> </span></span></code></pre></div> |
| **Get** | Produces rows from either an existing relation (source/view/materialized view/table) or from a previous CTE in the same plan.  **Can increase data size:** No **Uses memory:** No | <code>Get materialize.public.ordered</code> |
| **Project** | Produces a subset of the <a href="/sql/explain-plan/#explain-plan-columns" >columns</a> in the input rows. See also <a href="/sql/explain-plan/#explain-plan-columns" >column numbering</a>.  **Can increase data size:** No **Uses memory:** No | <code>Project (#2, #3)</code> |
| **Map** | Appends the results of some scalar expressions to each row in the input.  **Can increase data size:** Each row has more data (i.e., longer rows but same number of rows). **Uses memory:** No | <code>Map (((#1 * 10000000dec) / #2) * 1000dec)</code> |
| **CallTable** | Appends the result of some (one-to-many) <a href="/sql/functions/#table-functions" >table function</a> to each row in the input.  **Can increase data size:** Depends on the <a href="/sql/functions/#table-functions" >table function</a> used. **Uses memory:** No | <code>CallTable generate_series(1, 7, 1)</code> |
| **Filter** | <p>Removes rows of the input for which some scalar predicates return <code>false</code>.</p> <p>A temporal filter, one whose predicate uses <a href="/sql/functions/now_and_mz_now/" ><code>mz_now()</code></a>, also schedules a retraction of each row for the moment it stops satisfying the predicate. Until then, the operator downstream of the filter holds that pending retraction in memory, one per live row.</p>   **Can increase data size:** No **Uses memory:** No | <code>Filter (#20 &lt; #21)</code> |
| **~Join** | Performs one of <code>INNER</code> / <code>LEFT</code> / <code>RIGHT</code> / <code>FULL OUTER</code> / <code>CROSS</code> join on the two inputs, using the given predicate.  **Can increase data size:** For <code>CrossJoin</code>s, Cartesian product of the inputs (\|N\| x \|M\|). Note that, in many cases, a join that shows up as a cross join in the RAW PLAN will actually be turned into an inner join in the OPTIMIZED PLAN, by making use of an equality WHERE condition. For other join types, depends on the join order and facts about the joined collections. **Uses memory:** ✅ Uses memory proportional to the input sizes, unless <a href="/transform-data/optimization/#join" >the inputs have appropriate indexes</a>. Certain joins with more than 2 inputs use additional memory, see details in the optimized plan. | <code>InnerJoin (#0 = #2)</code> |
| **Reduce** | Groups the input rows by some scalar expressions, reduces each group using some aggregate functions, and produces rows containing the group key and aggregate outputs.  In the case where the group key is empty and the input is empty, returns a single row with the aggregate functions applied to the empty input collection.  **Can increase data size:** No **Uses memory:** ✅ <code>SUM</code>, <code>COUNT</code>, and most other aggregations use a moderate amount of memory (proportional either to twice the output size or to input size + output size). <code>MIN</code> and <code>MAX</code> aggregates can use significantly more memory. This can be improved by including group size hints in the query, see <a href="/sql/system-catalog/mz_introspection/#mz_expected_group_size_advice" ><code>mz_introspection.mz_expected_group_size_advice</code></a>. A hint shrinks the tower of intermediate arrangements, and shows in the optimized plan as <code>exp_group_size</code> and in the physical plan as the <code>buckets</code> list. The input rows stay arranged either way, so a hint cannot bring a <code>MIN</code> or <code>MAX</code> below the size of its input. | <code>Reduce group_by=[#0] aggregates=[max((#0 * #1))]</code> |
| **Distinct** | Removes duplicate copies of input rows.  **Can increase data size:** No **Uses memory:** ✅ Uses memory proportional to twice the output size. | <code>Distinct</code> |
| **TopK** | Groups the input rows by some scalar expressions, sorts each group by the ordering expressions, removes the top <code>offset</code> rows in each group, and returns the next <code>limit</code> rows.  **Can increase data size:** No **Uses memory:** ✅ Can use significant amount as the operator can significantly overestimate the group sizes. Consult <a href="/sql/system-catalog/mz_introspection/#mz_expected_group_size_advice" ><code>mz_introspection.mz_expected_group_size_advice</code></a>. A <code>LIMIT INPUT GROUP SIZE</code> hint shows in the optimized plan as <code>exp_group_size</code>; the physical plan does not display it. | <code>TopK order_by=[#1 asc nulls_last, #0 desc nulls_first] limit=5</code> |
| **Negate** | Negates the row counts of the input. This is usually used in combination with union to remove rows from the other union input.  **Can increase data size:** No **Uses memory:** No | <code>Negate</code> |
| **Threshold** | Removes any rows with negative counts.  **Can increase data size:** No **Uses memory:** ✅ Arranges both its input and its output by the whole row, so it uses memory proportional to the input size plus the output size. | <code>Threshold</code> |
| **Union** | Sums the counts of each row of all inputs. (Corresponds to <code>UNION ALL</code> rather than <code>UNION</code>/<code>UNION DISTINCT</code>.)  **Can increase data size:** No **Uses memory:** ✅ A plain <code>Union</code> uses no memory of its own. A <code>Union</code> whose output must be consolidated holds updates while consolidating them, which shows as a memory spike largely at hydration time. | <code>Union</code> |
| **With ... Return ...** | Introduces CTEs, i.e., makes it possible for sub-plans to be consumed multiple times by downstream operators.  **Can increase data size:** No **Uses memory:** No | <a href="/sql/explain-plan/#reading-plans" >See Reading plans</a> |
**Notes:**
- **Can increase data size:** Specifies whether the operator can increase the data size (can be the number of rows or the number of columns).
- **Uses memory:** Specifies whether the operator use memory to maintain state for its inputs.

Operators are sometimes marked as `Fused ...`. This indicates that the operator is fused with its input, i.e., the operator below it. That is, if you see a `Fused X` operator above a `Y` operator:

```
→Fused X
  →Y
```

Then the `X` and `Y` operators will be combined into a single, more efficient operator.

## Examples

For the following examples, let's assume that you have [the auction house load generator](/sql/create-source/load-generator/#creating-an-auction-load-generator) created in your current environment.

### Explaining a `SELECT` query

Let's start with a simple join query that lists the total amounts bid per buyer.

Explain the optimized plan as text:

```mzsql
EXPLAIN
SELECT a.id, sum(b.amount) FROM accounts a JOIN bids b ON(a.id = b.buyer) GROUP BY a.id;
```

Same explanation as above, but with the `EXPLAIN` expressed a bit more verbosely:

```mzsql
EXPLAIN PLAN FOR
SELECT a.id, sum(b.amount) FROM accounts a JOIN bids b ON(a.id = b.buyer) GROUP BY a.id;
```

Same explanation as above, but expressed even more verbosely:

```mzsql
EXPLAIN OPTIMIZED PLAN AS TEXT FOR
SELECT a.id, sum(b.amount) FROM accounts a JOIN bids b ON(a.id = b.buyer) GROUP BY a.id;
```

Same as above, but every sub-plan is annotated with its schema types:

```mzsql
EXPLAIN WITH(types) FOR
SELECT a.id, sum(b.amount) FROM accounts a JOIN bids b ON(a.id = b.buyer) GROUP BY a.id;
```

Explain the physical plan as verbose text (i.e., in complete detail):

```mzsql
EXPLAIN PHYSICAL PLAN FOR
SELECT a.id, sum(b.amount) FROM accounts a JOIN bids b ON(a.id = b.buyer) GROUP BY a.id;
```

### Explaining an index on a view

Let's create a view with an index for the above query.

```mzsql
-- create the view
CREATE VIEW my_view AS
SELECT a.id, sum(b.amount) FROM accounts a JOIN bids b ON(a.id = b.buyer) GROUP BY a.id;
-- create an index on the view
CREATE INDEX my_view_idx ON my_view(id);
```

You can inspect the plan of the dataflow that will maintain your index with the following statements.

Explain the optimized plan as text:

```mzsql
EXPLAIN
INDEX my_view_idx;
```

Same as above, but a bit more verbose:

```mzsql
EXPLAIN PLAN FOR
INDEX my_view_idx;
```

Same as above, but even more verbose:

```mzsql
EXPLAIN OPTIMIZED PLAN AS TEXT FOR
INDEX my_view_idx;
```

Same as above, but every sub-plan is annotated with its schema types:

```mzsql
EXPLAIN WITH(types) FOR
INDEX my_view_idx;
```

Explain the physical plan as verbose text:

```mzsql
EXPLAIN PHYSICAL PLAN FOR
INDEX my_view_idx;
```

### Explaining a materialized view

Let's create a materialized view for the above `SELECT` query.

```mzsql
CREATE MATERIALIZED VIEW my_mat_view AS
SELECT a.id, sum(b.amount) FROM accounts a JOIN bids b ON(a.id = b.buyer) GROUP BY a.id;
```

You can inspect the plan of the dataflow that will maintain your view with the following statements.

Explain the optimized plan as text:

```mzsql
EXPLAIN
MATERIALIZED VIEW my_mat_view;
```

Same as above, but a bit more verbose:

```mzsql
EXPLAIN PLAN FOR
MATERIALIZED VIEW my_mat_view;
```

Same as above, but even more verbose:

```mzsql
EXPLAIN OPTIMIZED PLAN AS TEXT FOR
MATERIALIZED VIEW my_mat_view;
```

Same as above, but every sub-plan is annotated with its schema types:

```mzsql
EXPLAIN WITH(types)
MATERIALIZED VIEW my_mat_view;
```

Explain the physical plan as verbose text:

```mzsql
EXPLAIN PHYSICAL PLAN FOR
MATERIALIZED VIEW my_mat_view;
```

### Explaining a `SUBSCRIBE` query

You can also explain `SUBSCRIBE` statements to understand how data changes will be streamed.

> **Note:** `SUBSCRIBE` only supports `OPTIMIZED PLAN` and `PHYSICAL PLAN` stages. The `RAW`, `DECORRELATED`, and `LOCALLY OPTIMIZED` stages are not available for `SUBSCRIBE` because it takes MIR (mid-level intermediate representation) directly rather than going through HIR lowering.

Explain the optimized plan for subscribing to a table:

```mzsql
EXPLAIN OPTIMIZED PLAN FOR
SUBSCRIBE accounts;
```

Explain the optimized plan for subscribing to a query:

```mzsql
EXPLAIN OPTIMIZED PLAN FOR
SUBSCRIBE (SELECT id, balance FROM accounts WHERE balance > 1000);
```

Explain the physical plan:

```mzsql
EXPLAIN PHYSICAL PLAN FOR
SUBSCRIBE accounts;
```

## Debugging running dataflows

The [`EXPLAIN ANALYZE`](/sql/explain-analyze/) statement will let you debug memory and cpu usage (optionally with information about worker skew) for existing indexes and materialized views in terms of their physical plan operators. It can also attribute [TopK hints](/transform-data/idiomatic-materialize-sql/top-k/#query-hints-1) to individual operators.

## Privileges

The privileges required to execute this statement are:

- `USAGE` privileges on the schemas that all relations in the explainee are
  contained in.

<!-- mz-docs page: sql/explain-plan-operators -->

# Explain plan operators
Materialize offers several output formats for [`EXPLAIN
PLAN`](/sql/explain-plan/) and debugging. LIR plans as rendered in
[`mz_introspection.mz_lir_mapping`](/sql/system-catalog/mz_introspection/#mz_lir_mapping)
are deliberately succinct, while the plans in other formats give more detail.

The decorrelated and optimized plans from `EXPLAIN DECORRELATED PLAN
FOR ...`, `EXPLAIN LOCALLY OPTIMIZED PLAN FOR ...`, and `EXPLAIN
OPTIMIZED PLAN FOR ...` are in a mid-level representation that is
closer to LIR than SQL. The raw plans from `EXPLAIN RAW PLAN FOR ...`
are closer to SQL (and therefore less indicative of how the query will
actually run).

**In fully optimized physical (LIR) plans (Default):**
The following table lists the operators that are available in the LIR plan.

- For those operators that require memory to maintain intermediate state, **Uses memory** is marked with **Yes**.
- For those operators that expand the data size (either rows or columns), **Can increase data size** is marked with **Yes**.| Operator | Description | Example |
| --- | --- | --- |
| **Constant** | Always produces the same collection of rows.  **Can increase data size:** No **Uses memory:** No | <code>→Constant (2 rows)</code> |
| **Stream, Arranged, Index Lookup, Read** | <p>Produces rows from either an existing relation (source/view/materialized view/table) or from a previous CTE in the same plan. A <code>Fused with Child Map/Filter/Project</code> line above this operator means that <code>Map/Filter/Project</code> runs inside it.</p> <p>There are four types of <code>Get</code>.</p> <ol> <li> <p><code>Stream</code> indicates that the results are not <a href="/fundamentals/concepts/arrangements/#arrangements" >arranged</a> in memory and will be streamed directly.</p> </li> <li> <p><code>Arranged</code> indicates that the results are <a href="/fundamentals/concepts/arrangements/#arrangements" >arranged</a> in memory.</p> </li> <li> <p><code>Index Lookup</code> indicates the results will be <em>looked up</em> in an existing <a href="/fundamentals/concepts/arrangements/#arrangements" >arrangement</a>.</p> </li> <li> <p><code>Read</code> indicates that the results are unarranged, and will be processed as they arrive.</p> </li> </ol>   **Can increase data size:** No **Uses memory:** No | <code>Arranged materialize.public.t</code> |
| **Map/Filter/Project** | <p>Computes new columns (maps), filters columns, and projects away columns. Works row-by-row. Maps and filters will be printed, but projects will not.</p> <p>A <code>Map/Filter/Project</code> fused into a neighboring operator is printed as <code>Fused with Child Map/Filter/Project</code> above that operator, or as <code>Fused with Parent Map/Filter/Project</code> below an <code>Arrange</code>, and runs inside that operator rather than on its own.</p> <p>A temporal filter, one whose predicate uses <a href="/sql/functions/now_and_mz_now/" ><code>mz_now()</code></a>, also schedules a retraction of each row for the moment it stops satisfying the predicate. Until then, the operator downstream holds that pending retraction in memory, one per live row.</p>   **Can increase data size:** Each row may have more data, from the <code>Map</code>. Each row may also have less data, from the <code>Project</code>. There may be fewer rows, from the <code>Filter</code>. **Uses memory:** No | <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="err">→</span><span class="k">Map</span><span class="o">/</span><span class="k">Filter</span><span class="o">/</span><span class="n">Project</span> </span></span><span class="line"><span class="cl">  <span class="k">Filter</span><span class="p">:</span> <span class="p">(</span><span class="o">#</span><span class="mf">0</span><span class="p">{</span><span class="n">a</span><span class="p">}</span> <span class="o">&lt;</span> <span class="mf">7</span><span class="p">)</span> </span></span><span class="line"><span class="cl">  <span class="k">Map</span><span class="p">:</span> <span class="p">(</span><span class="o">#</span><span class="mf">0</span><span class="p">{</span><span class="n">a</span><span class="p">}</span> <span class="o">+</span> <span class="o">#</span><span class="mf">1</span><span class="p">{</span><span class="n">b</span><span class="p">})</span> </span></span></code></pre></div> |
| **Table Function** | <p>Appends the result of some (one-to-many) <a href="/sql/functions/#table-functions" >table function</a> to each row in the input.</p> <p>A <code>Fused with Child Table Function unnest_list</code> line above a <code>Non-incremental GroupAggregate</code> means the <code>unnest_list</code> call runs inside that aggregation, which is part of how window functions are compiled to dataflows.</p> <p>A <code>Fused with Child Map/Filter/Project</code> line above this operator means that <code>Map/Filter/Project</code> runs inside it.</p>   **Can increase data size:** Depends on the <a href="/sql/functions/#table-functions" >table function</a> used. **Uses memory:** No | <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="err">→</span><span class="k">Table</span> <span class="k">Function</span> <span class="n">generate_series</span><span class="p">(</span><span class="o">#</span><span class="mf">0</span><span class="p">{</span><span class="n">a</span><span class="p">},</span> <span class="o">#</span><span class="mf">1</span><span class="p">{</span><span class="n">b</span><span class="p">},</span> <span class="mf">1</span><span class="p">)</span> </span></span><span class="line"><span class="cl">  <span class="k">Input</span> <span class="k">key</span><span class="p">:</span> <span class="p">(</span><span class="o">#</span><span class="mf">0</span><span class="p">{</span><span class="n">a</span><span class="p">})</span> </span></span></code></pre></div> |
| **Differential Join, Delta Join** | <p>Both join operators indicate the join ordering selected.</p> <p>Returns combinations of rows from each input whenever some equality predicates are <code>true</code>.</p> <p>Joins will indicate the join order of their children, starting from 0. For example, <code>Differential Join %1 » %0</code> will join its second child into its first.</p> <p>The <a href="/transform-data/optimization/#join" >two joins differ in performance characteristics</a>.</p> <p><code>Differential Cross Join</code> and <code>Delta Cross Join</code> mark a join with a stage that has no equality keys. <code>One-Shot Delta Join</code> marks the single-path plan of a one-shot <code>SELECT</code>; an index or materialized view over the same query uses the multi-path <code>Delta Join</code>.</p>   **Can increase data size:** Depends on the join order and facts about the joined collections. **Uses memory:** ✅ Uses memory for 3-way or more differential joins. | <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="err">→</span><span class="n">Differential</span> <span class="k">Join</span> <span class="o">%</span><span class="mf">1</span> <span class="err">»</span> <span class="o">%</span><span class="mf">0</span> </span></span><span class="line"><span class="cl">  <span class="k">Join</span> <span class="n">stage</span> <span class="o">%</span><span class="mf">0</span><span class="p">:</span> <span class="n">Lookup</span> <span class="k">key</span> <span class="o">#</span><span class="mf">0</span><span class="p">{</span><span class="n">a</span><span class="p">}</span> <span class="k">in</span> <span class="o">%</span><span class="mf">0</span> </span></span></code></pre></div> |
| **GroupAggregate** | <p>Groups the input rows by some scalar expressions, reduces each group using some aggregate functions, and produces rows containing the group key and aggregate outputs.</p> <p>There are four types of <code>GroupAggregate</code>, ordered by increasing complexity:</p> <ol> <li> <p><code>Distinct GroupAggregate</code> corresponds to the SQL <code>DISTINCT</code> operator.</p> </li> <li> <p><code>Accumulable GroupAggregate</code> (e.g., <code>SUM</code>, <code>COUNT</code>) corresponds to several easy to implement aggregations that can be executed efficiently.</p> </li> <li> <p>Hierarchical aggregations (e.g., <code>MIN</code>, <code>MAX</code>) require a tower of arrangements. They are printed as <code>Bucketed Hierarchical GroupAggregate</code>, or as the more efficient <code>Monotonic GroupAggregate</code> when the input never retracts data. Bucketed ones may benefit from a hint; <a href="/sql/system-catalog/mz_introspection/#mz_expected_group_size_advice" >see <code>mz_introspection.mz_expected_group_size_advice</code></a>. A <code>Consolidating</code> prefix means the operator consolidates its input first, which uses memory while the input is being consolidated, largely at hydration time.</p> </li> <li> <p><code>Non-incremental GroupAggregate</code> (e.g., window functions, <code>list_agg</code>) corresponds to a single non-incremental aggregation. These are the most computationally intensive reductions.</p> </li> </ol> <p>A query that mixes aggregations of different types is planned as one <code>GroupAggregate</code> per type, joined together on the group key.</p> <p>A <code>Temporally-Bucketed</code> prefix means the input carries future-dated updates from a temporal filter.</p> <p>A <code>Fused with Child Map/Filter/Project</code> line above this operator means that <code>Map/Filter/Project</code> runs inside it.</p>   **Can increase data size:** No **Uses memory:** ✅ <code>Distinct</code> and <code>Accumulable</code> aggregates use a moderate amount of memory (proportional to twice the output size). <code>MIN</code> and <code>MAX</code> aggregates can use significantly more memory. This can be improved by including group size hints in the query, see <a href="/sql/system-catalog/mz_introspection/#mz_expected_group_size_advice" ><code>mz_introspection.mz_expected_group_size_advice</code></a>. A hint shrinks the tower of intermediate arrangements (the <code>buckets</code> list of a <code>Bucketed Hierarchical GroupAggregate</code>); the input rows stay arranged either way, so a hint cannot bring a <code>MIN</code> or <code>MAX</code> below the size of its input. <code>Non-incremental</code> aggregates use memory proportional to the input + output size. A mix of aggregation types uses the memory of each <code>GroupAggregate</code> plus the arrangements of the join that combines them. | <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="err">→</span><span class="n">Accumulable</span> <span class="n">GroupAggregate</span> </span></span><span class="line"><span class="cl">  <span class="n">Simple</span> <span class="n">aggregates</span><span class="p">:</span> <span class="k">count</span><span class="p">(</span><span class="o">*</span><span class="p">)</span> </span></span><span class="line"><span class="cl">  <span class="n">Post</span><span class="o">-</span><span class="n">process</span> <span class="k">Map</span><span class="o">/</span><span class="k">Filter</span><span class="o">/</span><span class="n">Project</span> </span></span><span class="line"><span class="cl">    <span class="k">Filter</span><span class="p">:</span> <span class="p">(</span><span class="o">#</span><span class="mf">0</span> <span class="o">&gt;</span> <span class="mf">1</span><span class="p">)</span> </span></span></code></pre></div> |
| **TopK** | <p>Groups the input rows, sorts them according to some ordering, and returns at most <code>K</code> rows at some offset from the top of the list, where <code>K</code> is some (possibly computed) limit.</p> <p>There are three types of <code>TopK</code>. Two are special cased for monotonic inputs (i.e., inputs which never retract data).</p> <ol> <li><code>Monotonic Top1</code>.</li> <li><code>Monotonic TopK</code>, which may give an expression indicating the limit.</li> <li><code>Non-monotonic TopK</code>, a generic <code>TopK</code> plan.</li> </ol> <p>Each version of the <code>TopK</code> operator may include grouping, ordering, and limit directives. A <code>Consolidating</code> prefix means the operator consolidates its input first, and a <code>Temporally-Bucketed</code> prefix means the input carries future-dated updates from a temporal filter.</p>   **Can increase data size:** No **Uses memory:** ✅ <code>Monotonic Top1</code> and <code>Monotonic TopK</code> use a moderate amount of memory. <code>Non-monotonic TopK</code> uses significantly more memory as the operator can significantly overestimate the group sizes. Consult <a href="/sql/system-catalog/mz_introspection/#mz_expected_group_size_advice" ><code>mz_introspection.mz_expected_group_size_advice</code></a>. A <code>LIMIT INPUT GROUP SIZE</code> hint is not displayed in this plan; the optimized plan shows it as <code>exp_group_size</code>. | <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="err">→</span><span class="n">Consolidating</span> <span class="n">Monotonic</span> <span class="n">TopK</span> </span></span><span class="line"><span class="cl">  <span class="k">Order</span> <span class="k">By</span> <span class="o">#</span><span class="mf">1</span> <span class="k">asc</span> <span class="n">nulls_last</span><span class="p">,</span> <span class="o">#</span><span class="mf">0</span> <span class="k">desc</span> <span class="n">nulls_first</span> </span></span><span class="line"><span class="cl">  <span class="k">Limit</span> <span class="mf">5</span> </span></span></code></pre></div> |
| **Negate Diffs** | Negates the row counts of the input. This is usually used in combination with union to remove rows from the other union input.  **Can increase data size:** No **Uses memory:** No | <code>→Negate Diffs</code> |
| **Threshold Diffs** | Removes any rows with negative counts.  **Can increase data size:** No **Uses memory:** ✅ Arranges both its input and its output by the whole row, so it uses memory proportional to the input size plus the output size. | <code>→Threshold Diffs</code> |
| **Union** | Combines its inputs into a unified output, emitting one row for each row on any input. (Corresponds to <code>UNION ALL</code> rather than <code>UNION</code>/<code>UNION DISTINCT</code>.)  **Can increase data size:** No **Uses memory:** ✅ A <code>Consolidating Union</code> will make moderate use of memory, particularly at hydration time. A <code>Union</code> that is not <code>Consolidating</code> will not consume memory. | <code>→Consolidating Union</code> |
| **Arrange** | Indicates a point that will become an <a href="/fundamentals/concepts/arrangements/#arrangements" >arrangement</a> in the dataflow engine, i.e., it will consume memory to cache results.  **Can increase data size:** No **Uses memory:** ✅ Uses memory proportional to the input size. Note that in the LIR / physical plan, <code>Arrange</code>/<code>ArrangeBy</code> almost always means that an arrangement will actually be created. (This is in contrast to the &ldquo;optimized&rdquo; plan, where an <code>ArrangeBy</code> being present in the plan often does not mean that an arrangement will actually be created.) | <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="err">→</span><span class="n">Arrange</span> </span></span><span class="line"><span class="cl">    <span class="k">Keys</span><span class="p">:</span> <span class="mf">1</span> <span class="k">arrangement</span> <span class="n">available</span><span class="p">,</span> <span class="n">plus</span> <span class="k">raw</span> <span class="n">stream</span> </span></span><span class="line"><span class="cl">      <span class="k">Arrangement</span> <span class="mf">0</span><span class="p">:</span> <span class="o">#</span><span class="mf">0</span> </span></span></code></pre></div> |
| **Unarranged Raw Stream** | Indicates a point where data will be streamed (even if it is somehow already arranged).  **Can increase data size:** No **Uses memory:** No | <code>→Unarranged Raw Stream</code> |
| **With ... Return ...** | Introduces CTEs, i.e., makes it possible for sub-plans to be consumed multiple times by downstream operators.  **Can increase data size:** No **Uses memory:** No | <a href="/sql/explain-plan/#reading-plans" >See Reading plans</a> |
**Notes:**
- **Can increase data size:** Specifies whether the operator can increase the data size (can be the number of rows or the number of columns).
- **Uses memory:** Specifies whether the operator use memory to maintain state for its inputs.

**In decorrelated and optimized plans:**
The following table lists the operators that are available in the optimized plan.

- For those operators that require memory to maintain intermediate state, **Uses memory** is marked with **Yes**.
- For those operators that expand the data size (either rows or columns), **Can increase data size** is marked with **Yes**.| Operator | Description | Example |
| --- | --- | --- |
| **Constant** | Always produces the same collection of rows.  **Can increase data size:** No **Uses memory:** No | <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="n">Constant</span> </span></span><span class="line"><span class="cl"><span class="o">-</span> <span class="p">((</span><span class="mf">1</span><span class="p">,</span> <span class="mf">2</span><span class="p">)</span> <span class="n">x</span> <span class="mf">2</span><span class="p">)</span> </span></span><span class="line"><span class="cl"><span class="o">-</span> <span class="p">(</span><span class="mf">3</span><span class="p">,</span> <span class="mf">4</span><span class="p">)</span> </span></span></code></pre></div> |
| **Get** | Produces rows from either an existing relation (source/view/materialized view/table) or from a previous CTE in the same plan.  **Can increase data size:** No **Uses memory:** No | <code>Get materialize.public.ordered</code> |
| **Project** | Produces a subset of the <a href="/sql/explain-plan/#explain-plan-columns" >columns</a> in the input rows. See also <a href="/sql/explain-plan/#explain-plan-columns" >column numbering</a>.  **Can increase data size:** No **Uses memory:** No | <code>Project (#2, #3)</code> |
| **Map** | Appends the results of some scalar expressions to each row in the input.  **Can increase data size:** Each row has more data (i.e., longer rows but same number of rows). **Uses memory:** No | <code>Map (((#1 * 10000000dec) / #2) * 1000dec)</code> |
| **FlatMap** | Appends the result of some (one-to-many) <a href="/sql/functions/#table-functions" >table function</a> to each row in the input.  **Can increase data size:** Depends on the <a href="/sql/functions/#table-functions" >table function</a> used. **Uses memory:** No | <code>FlatMap jsonb_foreach(#3)</code> |
| **Filter** | <p>Removes rows of the input for which some scalar predicates return <code>false</code>.</p> <p>A temporal filter, one whose predicate uses <a href="/sql/functions/now_and_mz_now/" ><code>mz_now()</code></a>, also schedules a retraction of each row for the moment it stops satisfying the predicate. Until then, the operator downstream of the filter holds that pending retraction in memory, one per live row.</p>   **Can increase data size:** No **Uses memory:** No | <code>Filter (#20 &lt; #21)</code> |
| **Join** | Returns combinations of rows from each input whenever some equality predicates are <code>true</code>.  **Can increase data size:** Depends on the join order and facts about the joined collections. **Uses memory:** ✅ The <code>Join</code> operator itself uses memory only for <code>type=differential</code> with more than 2 inputs. However, <code>Join</code> operators need <a href="/fundamentals/concepts/arrangements/#arrangements" >arrangements</a> on their inputs (shown by the <code>ArrangeBy</code> operator). These arrangements use memory proportional to the input sizes. If an input has an <a href="/transform-data/optimization/#join" >appropriate index</a>, then the arrangement of the index will be reused. | <code>Join on=(#1 = #2) type=delta</code> |
| **CrossJoin** | An alias for a <code>Join</code> with an empty predicate (emits all combinations). Note that not all cross joins are marked as <code>CrossJoin</code>: In a join with more than 2 inputs, it can happen that there is a cross join between some of the inputs. You can recognize this case by <code>ArrangeBy</code> operators having empty keys, i.e., <code>ArrangeBy keys=[[]]</code>.  **Can increase data size:** Cartesian product of the inputs (\|N\| x \|M\|). **Uses memory:** ✅ Uses memory for 3-way or more differential joins. | <code>CrossJoin type=differential</code> |
| **Reduce** | Groups the input rows by some scalar expressions, reduces each group using some aggregate functions, and produces rows containing the group key and aggregate outputs.  **Can increase data size:** No **Uses memory:** ✅ <code>SUM</code>, <code>COUNT</code>, and most other aggregations use a moderate amount of memory (proportional either to twice the output size or to input size + output size). <code>MIN</code> and <code>MAX</code> aggregates can use significantly more memory. This can be improved by including group size hints in the query, see <a href="/sql/system-catalog/mz_introspection/#mz_expected_group_size_advice" ><code>mz_introspection.mz_expected_group_size_advice</code></a>. A hint shrinks the tower of intermediate arrangements, and shows in the optimized plan as <code>exp_group_size</code> and in the physical plan as the <code>buckets</code> list. The input rows stay arranged either way, so a hint cannot bring a <code>MIN</code> or <code>MAX</code> below the size of its input. | <code>Reduce group_by=[#0] aggregates=[max((#0 * #1))]</code> |
| **Distinct** | Alias for a <code>Reduce</code> with an empty aggregate list.  **Can increase data size:** No **Uses memory:** ✅ Uses memory proportional to twice the output size. | <code>Distinct</code> |
| **TopK** | Groups the input rows by some scalar expressions, sorts each group by the ordering expressions, removes the top <code>offset</code> rows in each group, and returns the next <code>limit</code> rows.  **Can increase data size:** No **Uses memory:** ✅ Can use significant amount as the operator can significantly overestimate the group sizes. Consult <a href="/sql/system-catalog/mz_introspection/#mz_expected_group_size_advice" ><code>mz_introspection.mz_expected_group_size_advice</code></a>. A <code>LIMIT INPUT GROUP SIZE</code> hint shows in the optimized plan as <code>exp_group_size</code>; the physical plan does not display it. | <code>TopK order_by=[#1 asc nulls_last, #0 desc nulls_first] limit=5</code> |
| **Negate** | Negates the row counts of the input. This is usually used in combination with union to remove rows from the other union input.  **Can increase data size:** No **Uses memory:** No | <code>Negate</code> |
| **Threshold** | Removes any rows with negative counts.  **Can increase data size:** No **Uses memory:** ✅ Arranges both its input and its output by the whole row, so it uses memory proportional to the input size plus the output size. | <code>Threshold</code> |
| **Union** | Sums the counts of each row of all inputs. (Corresponds to <code>UNION ALL</code> rather than <code>UNION</code>/<code>UNION DISTINCT</code>.)  **Can increase data size:** No **Uses memory:** ✅ A plain <code>Union</code> uses no memory of its own. A <code>Union</code> whose output must be consolidated holds updates while consolidating them, which shows as a memory spike largely at hydration time. | <code>Union</code> |
| **ArrangeBy** | Indicates a point that will become an <a href="/fundamentals/concepts/arrangements/#arrangements" >arrangement</a> in the dataflow engine (each <code>keys</code> element will be a different arrangement). Note that if an appropriate index already exists on the input or the output of the previous operator is already arranged with a key that is also requested here, then this operator will just pass on that existing arrangement instead of creating a new one.  **Can increase data size:** No **Uses memory:** ✅ Depends. If arrangements need to be created, they use memory proportional to the input size. | <code>ArrangeBy keys=[[#0]]</code> |
| **With ... Return ...** | Introduces CTEs, i.e., makes it possible for sub-plans to be consumed multiple times by downstream operators.  **Can increase data size:** No **Uses memory:** No | <a href="/sql/explain-plan/#reading-plans" >See Reading plans</a> |
**Notes:**
- **Can increase data size:** Specifies whether the operator can increase the data size (can be the number of rows or the number of columns).
- **Uses memory:** Specifies whether the operator use memory to maintain state for its inputs.

**In raw plans:**
The following table lists the operators that are available in the raw plan.

- For those operators that require memory to maintain intermediate state, **Uses memory** is marked with **Yes**.
- For those operators that expand the data size (either rows or columns), **Can increase data size** is marked with **Yes**.| Operator | Description | Example |
| --- | --- | --- |
| **Constant** | Always produces the same collection of rows.  **Can increase data size:** No **Uses memory:** No | <div class="highlight"><pre tabindex="0" class="chroma"><code class="language-mzsql" data-lang="mzsql"><span class="line"><span class="cl"><span class="n">Constant</span> </span></span><span class="line"><span class="cl"><span class="o">-</span> <span class="p">((</span><span class="mf">1</span><span class="p">,</span> <span class="mf">2</span><span class="p">)</span> <span class="n">x</span> <span class="mf">2</span><span class="p">)</span> </span></span><span class="line"><span class="cl"><span class="o">-</span> <span class="p">(</span><span class="mf">3</span><span class="p">,</span> <span class="mf">4</span><span class="p">)</span> </span></span></code></pre></div> |
| **Get** | Produces rows from either an existing relation (source/view/materialized view/table) or from a previous CTE in the same plan.  **Can increase data size:** No **Uses memory:** No | <code>Get materialize.public.ordered</code> |
| **Project** | Produces a subset of the <a href="/sql/explain-plan/#explain-plan-columns" >columns</a> in the input rows. See also <a href="/sql/explain-plan/#explain-plan-columns" >column numbering</a>.  **Can increase data size:** No **Uses memory:** No | <code>Project (#2, #3)</code> |
| **Map** | Appends the results of some scalar expressions to each row in the input.  **Can increase data size:** Each row has more data (i.e., longer rows but same number of rows). **Uses memory:** No | <code>Map (((#1 * 10000000dec) / #2) * 1000dec)</code> |
| **CallTable** | Appends the result of some (one-to-many) <a href="/sql/functions/#table-functions" >table function</a> to each row in the input.  **Can increase data size:** Depends on the <a href="/sql/functions/#table-functions" >table function</a> used. **Uses memory:** No | <code>CallTable generate_series(1, 7, 1)</code> |
| **Filter** | <p>Removes rows of the input for which some scalar predicates return <code>false</code>.</p> <p>A temporal filter, one whose predicate uses <a href="/sql/functions/now_and_mz_now/" ><code>mz_now()</code></a>, also schedules a retraction of each row for the moment it stops satisfying the predicate. Until then, the operator downstream of the filter holds that pending retraction in memory, one per live row.</p>   **Can increase data size:** No **Uses memory:** No | <code>Filter (#20 &lt; #21)</code> |
| **~Join** | Performs one of <code>INNER</code> / <code>LEFT</code> / <code>RIGHT</code> / <code>FULL OUTER</code> / <code>CROSS</code> join on the two inputs, using the given predicate.  **Can increase data size:** For <code>CrossJoin</code>s, Cartesian product of the inputs (\|N\| x \|M\|). Note that, in many cases, a join that shows up as a cross join in the RAW PLAN will actually be turned into an inner join in the OPTIMIZED PLAN, by making use of an equality WHERE condition. For other join types, depends on the join order and facts about the joined collections. **Uses memory:** ✅ Uses memory proportional to the input sizes, unless <a href="/transform-data/optimization/#join" >the inputs have appropriate indexes</a>. Certain joins with more than 2 inputs use additional memory, see details in the optimized plan. | <code>InnerJoin (#0 = #2)</code> |
| **Reduce** | Groups the input rows by some scalar expressions, reduces each group using some aggregate functions, and produces rows containing the group key and aggregate outputs.  In the case where the group key is empty and the input is empty, returns a single row with the aggregate functions applied to the empty input collection.  **Can increase data size:** No **Uses memory:** ✅ <code>SUM</code>, <code>COUNT</code>, and most other aggregations use a moderate amount of memory (proportional either to twice the output size or to input size + output size). <code>MIN</code> and <code>MAX</code> aggregates can use significantly more memory. This can be improved by including group size hints in the query, see <a href="/sql/system-catalog/mz_introspection/#mz_expected_group_size_advice" ><code>mz_introspection.mz_expected_group_size_advice</code></a>. A hint shrinks the tower of intermediate arrangements, and shows in the optimized plan as <code>exp_group_size</code> and in the physical plan as the <code>buckets</code> list. The input rows stay arranged either way, so a hint cannot bring a <code>MIN</code> or <code>MAX</code> below the size of its input. | <code>Reduce group_by=[#0] aggregates=[max((#0 * #1))]</code> |
| **Distinct** | Removes duplicate copies of input rows.  **Can increase data size:** No **Uses memory:** ✅ Uses memory proportional to twice the output size. | <code>Distinct</code> |
| **TopK** | Groups the input rows by some scalar expressions, sorts each group by the ordering expressions, removes the top <code>offset</code> rows in each group, and returns the next <code>limit</code> rows.  **Can increase data size:** No **Uses memory:** ✅ Can use significant amount as the operator can significantly overestimate the group sizes. Consult <a href="/sql/system-catalog/mz_introspection/#mz_expected_group_size_advice" ><code>mz_introspection.mz_expected_group_size_advice</code></a>. A <code>LIMIT INPUT GROUP SIZE</code> hint shows in the optimized plan as <code>exp_group_size</code>; the physical plan does not display it. | <code>TopK order_by=[#1 asc nulls_last, #0 desc nulls_first] limit=5</code> |
| **Negate** | Negates the row counts of the input. This is usually used in combination with union to remove rows from the other union input.  **Can increase data size:** No **Uses memory:** No | <code>Negate</code> |
| **Threshold** | Removes any rows with negative counts.  **Can increase data size:** No **Uses memory:** ✅ Arranges both its input and its output by the whole row, so it uses memory proportional to the input size plus the output size. | <code>Threshold</code> |
| **Union** | Sums the counts of each row of all inputs. (Corresponds to <code>UNION ALL</code> rather than <code>UNION</code>/<code>UNION DISTINCT</code>.)  **Can increase data size:** No **Uses memory:** ✅ A plain <code>Union</code> uses no memory of its own. A <code>Union</code> whose output must be consolidated holds updates while consolidating them, which shows as a memory spike largely at hydration time. | <code>Union</code> |
| **With ... Return ...** | Introduces CTEs, i.e., makes it possible for sub-plans to be consumed multiple times by downstream operators.  **Can increase data size:** No **Uses memory:** No | <a href="/sql/explain-plan/#reading-plans" >See Reading plans</a> |
**Notes:**
- **Can increase data size:** Specifies whether the operator can increase the data size (can be the number of rows or the number of columns).
- **Uses memory:** Specifies whether the operator use memory to maintain state for its inputs.

Operators are sometimes marked as `Fused ...`. This indicates that the operator is fused with its input, i.e., the operator below it. That is, if you see a `Fused X` operator above a `Y` operator:

```
→Fused X
  →Y
```

Then the `X` and `Y` operators will be combined into a single, more efficient operator.

See also:

- [`EXPLAIN PLAn`](/sql/explain-plan/)

<!-- mz-docs page: sql/explain-schema -->

# EXPLAIN SCHEMA
`EXPLAIN KEY SCHEMA` or `EXPLAIN VALUE SCHEMA` is used to see the generated schemas for a `CREATE SINK` statement
`EXPLAIN KEY SCHEMA` or `EXPLAIN VALUE SCHEMA` shows the generated schemas for a `CREATE SINK` statement without creating the sink.

> **Warning:** `EXPLAIN` is not part of Materialize's stable interface and is not subject to
> our backwards compatibility guarantee. The syntax and output of `EXPLAIN` may
> change arbitrarily in future versions of Materialize.

## Syntax

```mzsql
EXPLAIN (KEY | VALUE) SCHEMA [AS JSON]
FOR CREATE SINK [<sink_name>]
[IN CLUSTER <cluster_name>]
FROM <item_name>
INTO KAFKA CONNECTION <connection_name> (
  TOPIC '<topic>'
  [, COMPRESSION TYPE <compression_type>]
  [, TRANSACTIONAL ID PREFIX '<transactional_id_prefix>']
  [, PARTITION BY = <expression>]
  [, PROGRESS GROUP ID PREFIX '<progress_group_id_prefix>']
  [, TOPIC REPLICATION FACTOR <replication_factor>]
  [, TOPIC PARTITION COUNT <partition_count>]
  [, TOPIC CONFIG <topic_config>]
)
[KEY ( <key_column> [, ...] ) [NOT ENFORCED]]
[HEADERS <headers_column>]
[FORMAT <sink_format_spec> | KEY FORMAT <sink_format_spec> VALUE FORMAT <sink_format_spec>]
[ENVELOPE (DEBEZIUM | UPSERT)]
[WITH (<with_option> [, ...])]

```

| Syntax element | Description |
| --- | --- |
| **KEY** \| **VALUE** | Specifies whether to explain the key schema or value schema for the sink.  |
| **AS JSON** | Optional. Format the explanation output as a JSON object. If not specified, the output is formatted as text.  |
| **FOR CREATE SINK** `[<sink_name>]` | The `CREATE SINK` statement to explain. The sink name is optional.  |
| **IN CLUSTER** `<cluster_name>` | Optional. The [cluster](/sql/create-cluster) to maintain this sink.  |
| **FROM** `<item_name>` | The name of the source, table, or materialized view you want to send to the sink.  |
| **INTO KAFKA CONNECTION** `<connection_name>` | The name of the Kafka connection to use in the sink. For details on creating connections, check the [`CREATE CONNECTION`](/sql/create-connection) documentation page.  |
| **TOPIC** `'<topic>'` | The name of the Kafka topic to write to.  |
| **COMPRESSION TYPE** `<compression_type>` | Optional. The type of compression to apply to messages before they are sent to Kafka: `none`, `gzip`, `snappy`, `lz4`, or `zstd`.  |
| **TRANSACTIONAL ID PREFIX** `'<transactional_id_prefix>'` | Optional. The prefix of the transactional ID to use when producing to the Kafka topic.  |
| **PARTITION BY** `= <expression>` | Optional. A SQL expression returning a hash that can be used for partition assignment. See [Partitioning](/sql/create-sink/kafka/#partitioning) for details.  |
| **PROGRESS GROUP ID PREFIX** `'<progress_group_id_prefix>'` | Optional. The prefix of the consumer group ID to use when reading from the progress topic.  |
| **TOPIC REPLICATION FACTOR** `<replication_factor>` | Optional. The replication factor to use when creating the Kafka topic (if the Kafka topic does not already exist).  |
| **TOPIC PARTITION COUNT** `<partition_count>` | Optional. The partition count to use when creating the Kafka topic (if the Kafka topic does not already exist).  |
| **TOPIC CONFIG** `<topic_config>` | Optional. Any topic-level configs to use when creating the Kafka topic (if the Kafka topic does not already exist). See the [Kafka documentation](https://kafka.apache.org/documentation/#topicconfigs) for available configs.  |
| **KEY** ( `<key_column>` [, ...] ) [**NOT ENFORCED**] | Optional. A list of columns to use as the Kafka message key. If unspecified, the Kafka key is left unset. When using the upsert envelope, the key must be unique. Use **NOT ENFORCED** to disable validation of key uniqueness. See [Upsert key selection](/sql/create-sink/kafka/#upsert-key-selection) for details.  |
| **HEADERS** `<headers_column>` | Optional. A column containing headers to add to each Kafka message emitted by the sink. The column must be of type `map[text => text]` or `map[text => bytea]`. See [Headers](/sql/create-sink/kafka/#headers) for details.  |
| **FORMAT** `<sink_format_spec>` | Optional. Specifies the format to use for both keys and values: `AVRO USING CONFLUENT SCHEMA REGISTRY CONNECTION <csr_connection_name>`, `AVRO USING AWS GLUE SCHEMA REGISTRY CONNECTION <glue_connection_name>`, `JSON`, `TEXT`, or `BYTES`. See [Formats](/sql/create-sink/kafka/#formats) for details.  |
| **KEY FORMAT** `<sink_format_spec>` **VALUE FORMAT** `<sink_format_spec>` | Optional. Specifies the key format and value formats separately. See [Formats](/sql/create-sink/kafka/#formats) for details.  |
| **ENVELOPE** (`DEBEZIUM` \| `UPSERT`) | Optional. Specifies how changes to the sink's upstream relation are mapped to Kafka messages. Valid envelope types:  \| Envelope \| Description \| \|----------\|-------------\| \| `DEBEZIUM` \| The generated schemas have a [Debezium-style diff envelope](/sql/create-sink/kafka/#debezium) to capture changes in the input view or source. \| \| `UPSERT` \| The sink emits data with [upsert semantics](/sql/create-sink/kafka/#upsert). Requires a unique key specified using the `KEY` option. \|  |
| **WITH** (`<with_option>` [, ...]) | Optional. The following `<with_option>`s are supported:  \| Option \| Description \| \|--------\|-------------\| \| `SNAPSHOT = <snapshot>` \| Default: `true`. Whether to emit the consolidated results of the query before the sink was created at the start of the sink. To see only results after the sink is created, specify `WITH (SNAPSHOT = false)`. \|  |

## Details
When creating a an Avro-formatted Kafka sink, Materialize automatically generates Avro schemas for the message key and value and publishes them to a schema registry.
This command shows what the generated schemas would look like, without creating the sink.

## Examples

```mzsql
CREATE TABLE t (c1 int, c2 text);
COMMENT ON TABLE t IS 'materialize comment on t';
COMMENT ON COLUMN t.c2 IS 'materialize comment on t.c2';

EXPLAIN VALUE SCHEMA FOR
  CREATE SINK
  FROM t
  INTO KAFKA CONNECTION kafka_conn (TOPIC 'test_avro_topic')
  KEY (c1)
  FORMAT AVRO USING CONFLUENT SCHEMA REGISTRY CONNECTION csr_conn
  ENVELOPE UPSERT;
```

```
                   Schema
--------------------------------------------
 {                                         +
   "type": "record",                       +
   "name": "envelope",                     +
   "doc": "materialize comment on t",      +
   "fields": [                             +
     {                                     +
       "name": "c1",                       +
       "type": [                           +
         "null",                           +
         "int"                             +
       ]                                   +
     },                                    +
     {                                     +
       "name": "c2",                       +
       "type": [                           +
         "null",                           +
         "string"                          +
       ],                                  +
       "doc": "materialize comment on t.c2"+
     }                                     +
   ]                                       +
 }
```

## Privileges

The privileges required to execute this statement are:

- `USAGE` privileges on the schemas that all items in the query are contained
  in.

<!-- mz-docs page: sql/explain-timestamp -->

# EXPLAIN TIMESTAMP
`EXPLAIN TIMESTAMP` displays the timestamps used for a `SELECT` statement.
`EXPLAIN TIMESTAMP` displays the timestamps used for a `SELECT` statement -- valuable information to investigate query delays.

> **Warning:** `EXPLAIN` is not part of Materialize's stable interface and is not subject to
> our backwards compatibility guarantee. The syntax and output of `EXPLAIN` may
> change arbitrarily in future versions of Materialize.

## Syntax

```mzsql
EXPLAIN TIMESTAMP [AS (TEXT | JSON)]
FOR <select_stmt>

```

| Syntax element | Description |
| --- | --- |
| **AS** (`TEXT` \| `JSON`) | Optional. Specifies the output format of the explanation:  \| Format \| Description \| \|--------\|-------------\| \| `TEXT` \| Format the explanation output as UTF-8 text (default). \| \| `JSON` \| Format the explanation output as a JSON object. \|  |
| **FOR** `<select_stmt>` | The [`SELECT`](/sql/select) statement to explain.  |

## Details

The explanation is divided in two parts:

1. Determinations for a timestamp
2. Sources frontiers

Having a _query timestamp_ outside the _[read, write)_ frontier values of a source can explain the presence of delays. While in the middle, the space of processed but not yet compacted data, allows building and returning a correct result immediately.

### Determinations for a timestamp

Queries in Materialize have a logical timestamp, known as _query timestamp_. It plays a critical role to return a correct result. Returning a correct result implies retrieving data with the same logical time from each source present in a query.

In this case, sources are objects providing data: materialized views, views, indexes, tables, or sources. Each will have a pair of logical timestamps frontiers, denoted as _sources frontiers_.

This section contains the following fields:

Field | Meaning | Example
---------|---------|---------
**query timestamp** | The query timestamp value |`1673612424151 (2023-01-13 12:20:24.151)`
**oracle read** | The value of the timeline's oracle timestamp, if used. | `1673612424151 (2023-01-13 12:20:24.151)`
**largest not in advance of upper** | The largest timestamp not in advance of upper. | `1673612424151 (2023-01-13 12:20:24.151)`
**since** | The maximum read frontier of all involved sources. | `[1673612423000 (2023-01-13 12:20:23.000)]`
**upper** | The minimum write frontier of all involved sources | `[1673612424152 (2023-01-13 12:20:24.152)]`
**can respond immediately** | Returns true when the **query timestamp** is greater or equal to **since** and lower than **upper** | `true`
**timeline** | The type of timeline the query's timestamp belongs | `Some(EpochMilliseconds)`

A timeline value of `None` means the query is known to be constant across all timestamps.

### Sources frontiers

Every source has a beginning _read frontier_ and an ending _write frontier_.
They stand for a source’s limits to return a correct result immediately:

* Read frontier: Indicates the minimum logical timestamp to return a correct result (advanced by _compaction_)
* Write frontier: Indicates the maximum timestamp to build a correct result without waiting for unprocessed data.

Each source has its own output section consisting of the following fields:

Field | Meaning | Example
---------|---------|---------
**source** | Source’s identifiers | `source materialize.public.raw_users (u2014, storage)`
**read frontier** | Minimum logical timestamp. |`[1673612423000 (2023-01-13 12:20:23.000)]`
**write frontier** | Maximum logical timestamp. | `[1673612424152 (2023-01-13 12:20:24.152)]`

## Examples

```mzsql
EXPLAIN TIMESTAMP FOR SELECT * FROM users;
```
```
                                 Timestamp
---------------------------------------------------------------------------
                 query timestamp: 1673618185152 (2023-01-13 13:56:25.152) +
           oracle read timestamp: 1673618185152 (2023-01-13 13:56:25.152) +
 largest not in advance of upper: 1673618185152 (2023-01-13 13:56:25.152) +
                           upper:[1673618185153 (2023-01-13 13:56:25.153)]+
                           since:[1673618184000 (2023-01-13 13:56:24.000)]+
         can respond immediately: true                                    +
                        timeline: Some(EpochMilliseconds)                 +
                                                                          +
 source materialize.public.raw_users (u2014, storage):                    +
                   read frontier:[1673618184000 (2023-01-13 13:56:24.000)]+
                  write frontier:[1673618185153 (2023-01-13 13:56:25.153)]+
```

<!-- We think of `since` as the "read frontier": times not later than or equal to
`since` cannot be correctly read. We think of `upper` as the "write frontier":
times later than or equal to `upper` may still be written to the TVC. -->
<!-- Who is the oracle? -->
<!--
We maintain a timestamp oracle that returns strictly increasing timestamps
Mentions that this is inspired/similar to Percolator.

Timestamp oracle is periodically bumped up to the current system clock
We never revert oracle if system clock goes backwards.

https://tikv.org/deep-dive/distributed-transaction/timestamp-oracle/
-->
<!-- Materialize's objects request timestamp to the oracle, a timestamp provider. The oracle's timestamp bumps up periodically to match the current system clock, and never goes backwards.

It relies on an oracle, a timestamp provider, to handle them correctly.

The oracle it is a timestamp provider. It bumps up periodically internal value to the current system clock, never going backwards.

Issuing a select statement in Materialize
When a select statement runs, Materialize will pick a timestamp between all the sources:

`max(max(read_frontiers), min(write_frontiers) - 1)` -->

<!-- /// Information used when determining the timestamp for a query.
#[derive(Serialize, Deserialize)]
pub struct TimestampDetermination<T> {
    /// The chosen timestamp context from `determine_timestamp`.
    pub timestamp_context: TimestampContext<T>,
    /// The largest timestamp not in advance of upper.
    pub largest_not_in_advance_of_upper: T,
}

*Query timestamp: The timestamp in a timeline at which the query makes the read
oracle read: The value of the timeline's oracle timestamp, if used.
largest not in advance of upper: The largest timestamp not in advance of upper.
upper: The write frontier of all involved sources.
since: The read frontier of all involved sources.
can respond immediately: True when the write frontier is greater than the query timestamp.
timeline: The type of timeline the query's timestamp belongs:
      /// EpochMilliseconds means the timestamp is the number of milliseconds since
      /// the Unix epoch.
      EpochMilliseconds,
      /// External means the timestamp comes from an external data source and we
      /// don't know what the number means. The attached String is the source's name,
      /// which will result in different sources being incomparable.
      External(String),
      /// User means the user has manually specified a timeline. The attached
      /// String is specified by the user, allowing them to decide sources that are
      /// joinable.
      User(String),

Each source contains two frontiers:
  Read: At which time
  Write:

                 query timestamp: 1673612424151 (2023-01-13 12:20:24.151) +
           oracle read timestamp: 1673612424151 (2023-01-13 12:20:24.151) +
 largest not in advance of upper: 1673612424151 (2023-01-13 12:20:24.151) +
                           upper:[1673612424152 (2023-01-13 12:20:24.152)]+
                           since:[1673612423000 (2023-01-13 12:20:23.000)]+

                                 Timestamp
---------------------------------------------------------------------------
                 query timestamp: 1673612424151 (2023-01-13 12:20:24.151) +
           oracle read timestamp: 1673612424151 (2023-01-13 12:20:24.151) +
 largest not in advance of upper: 1673612424151 (2023-01-13 12:20:24.151) +
                           upper:[1673612424152 (2023-01-13 12:20:24.152)]+
                           since:[1673612423000 (2023-01-13 12:20:23.000)]+
         can respond immediately: true                                    +
                        timeline: Some(EpochMilliseconds)                 +
                                                                          +
 source materialize.public.a (u2014, storage):                            +
                   read frontier:[1673612423000 (2023-01-13 12:20:23.000)]+
                  write frontier:[1673612424152 (2023-01-13 12:20:24.152)]+ -->

## Privileges

The privileges required to execute this statement are:

- `USAGE` privileges on the schemas that all relations in the query are
  contained in.

<!-- mz-docs page: sql/fetch -->

# FETCH
`FETCH` retrieves rows from a cursor.
`FETCH` retrieves rows from a query using a cursor previously opened with [`DECLARE`](/sql/declare).

## Syntax

```mzsql
FETCH [ <count> | ALL ] [FROM] <cursor_name> [ WITH ( TIMEOUT = <interval> ) ]

```

| Syntax element | Description |
| --- | --- |
| `<count>` | The number of rows to retrieve. Defaults to `1` if unspecified.  |
| `ALL` | Indicates that there is no limit on the number of rows to be returned.  |
| `<cursor_name>` | The name of an open cursor.  |
| `TIMEOUT` | When fetching from a [`SUBSCRIBE`](/sql/subscribe) cursor, complete if there are no more rows ready after this timeout. The default will cause `FETCH` to wait for at least one row to be available.  |

## Details

`FETCH` will return at most the specified _count_ of available rows. Specifying a _count_ of `ALL` indicates that there is no limit on the number of
rows to be returned.

For [`SUBSCRIBE`](/sql/subscribe) queries, `FETCH` by default will wait for rows to be available before returning.
Specifying a _timeout_ of `0s` returns only rows that are immediately available.

