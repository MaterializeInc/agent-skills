<!-- mz-docs page: security/self-managed/access-control/manage-roles -->

# Manage database roles
Create and manage database roles and privileges in Materialize
In Materialize, role-based access control (RBAC) governs access to objects
through privileges granted to database roles.

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

## Required privileges for managing roles

> **Note:** Initially, only the `mz_system` user (which has superuser/administrator
> privileges) is available to manage roles.

| Role management operations | Required privileges |
| --- | --- |
| To create/revoke/grant roles | <ul> <li><code>CREATEROLE</code> privileges on the system. > **Warning:** Roles with the `CREATEROLE` privilege can obtain the privileges of any other > role in the system by granting themselves that role. Avoid granting > `CREATEROLE` unnecessarily. </li> </ul>  |
| To view privileges for a role | None |
| To grant/revoke role privileges | <ul> <li>Ownership of affected objects.</li> <li><code>USAGE</code> privileges on the containing database if the affected object is a schema.</li> <li><code>USAGE</code> privileges on the containing schema if the affected object is namespaced by a schema.</li> <li><em>superuser</em> status if the privilege is a system privilege.</li> </ul>  |
| To alter default privileges | <ul> <li>Role membership in <code>role_name</code>.</li> <li><code>USAGE</code> privileges on the containing database if <code>database_name</code> is specified.</li> <li><code>USAGE</code> privileges on the containing schema if <code>schema_name</code> is specified.</li> <li><em>superuser</em> status if the <em>target_role</em> is <code>PUBLIC</code> or <strong>ALL ROLES</strong> is specified.</li> </ul>  |

See also [Appendix: Privileges by
command](/security/appendix/appendix-command-privileges/)

## Create a role

In Materialize, you can create both:
- Individual user or service account roles; i.e., roles associated with a
  specific user or service account.
- Functional roles, not associated with any single user or service
  account, but typically used to define a set of shared
  privileges that can be granted to other user/service/functional roles.

Initially, only the `mz_system` user is available.

### Create individual user/service account roles

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

> **Privilege(s) required to run the command:** - `CREATEROLE` privileges on the system. 

For example, the following creates:

- A new user `blue.berry@example.com` (or more specifically, a new user role).
- A new service account `sales_report_app` (or more specifically, a new service
  account role).

**A new user role:**

The following creates a new user `blue.berry@example.com`, or more specifically, creates a role for a user `blue.berry@example.com` using [`CREATE ROLE ... WITH LOGIN PASSWORD`](/sql/create-role).
```mzsql
CREATE ROLE "blue.berry@example.com" WITH LOGIN PASSWORD '<password>';

```{{< note >}}
The role/user name `blue.berry@example.com` is enclosed in double quotes to
override the [naming restrictions](/sql/identifiers/#naming-restrictions).
{{</ note >}}

Once created, the user `blue.berry@example.com` can login using the
password.

**A new service account role:**

The following creates a new service account `sales_report_app`, or more
specifically, creates a role for a service account `sales_report_app` using
[`CREATE ROLE ... WITH LOGIN PASSWORD`](/sql/create-role).
```mzsql
CREATE ROLE "sales_report_app" WITH LOGIN PASSWORD '<password>';

```
Once created, the associated application can use the `sales_report_app`
service account to connect to Materialize.

In Materialize, a role is created with inheritance support. With inheritance,
when a role is granted to another role (i.e., the target role), the target role
inherits privileges (not role attributes and parameters) through the other role.
All roles in Materialize are automatically members of
[`PUBLIC`](/security/appendix/appendix-built-in-roles/#public-role). As
such, every role includes inherited privileges from `PUBLIC`.

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

See also:

- For a list of required privileges for specific operations, see [Appendix:
Privileges by command](/security/appendix/appendix-command-privileges/).

### Create functional roles

To create functional roles, login as the `mz_system` user,
using the `external_login_password_mz_system` password, and use [`CREATE ROLE`](/sql/create-role):

```mzsql
CREATE ROLE <role>;
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

See also:

- For a list of required privileges for specific operations, see [Appendix:
Privileges by command](/security/appendix/appendix-command-privileges/).

## Manage current privileges for a role

> **Note:** - The examples below assume the existence of a `mydb` database and a `sales`
> schema within the `mydb` database.
> - The examples below assume the roles only need privileges to objects in the
>   `mydb.sales` schema.

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

To view privileges for a user, run [`SHOW PRIVILEGES`](/sql/show-privileges)
on the user's role. For example, show the privileges for the `blue.berry@example.com` role created in the
[Create a role section](#create-individual-userservice-account-roles).
```mzsql
SHOW PRIVILEGES FOR "blue.berry@example.com";

```

The results show that the role currently has only the privileges inherited
through the `PUBLIC` role.

```none
| grantor   | grantee | database    | schema | name        | object_type | privilege_type |
| --------- | ------- | ----------- | ------ | ----------- | ----------- | -------------- |
| mz_system | PUBLIC  | materialize | null   | public      | schema      | USAGE          |
| mz_system | PUBLIC  | mydb        | null   | public      | schema      | USAGE          |
| mz_system | PUBLIC  | null        | null   | materialize | database    | USAGE          |
| mz_system | PUBLIC  | null        | null   | quickstart  | cluster     | USAGE          |
```

**Service account role:**

To view privileges for a service account, run [`SHOW
PRIVILEGES`](/sql/show-privileges) on the service account's role. For example, show the privileges for the `sales_report_app` role created in the
[Create a role section](#create-individual-userservice-account-roles).
```mzsql
SHOW PRIVILEGES FOR sales_report_app;

```

The results show that the role currently has only the privileges inherited
through the `PUBLIC` role.

```none
| grantor   | grantee | database    | schema | name        | object_type | privilege_type |
| --------- | ------- | ----------- | ------ | ----------- | ----------- | -------------- |
| mz_system | PUBLIC  | materialize | null   | public      | schema      | USAGE          |
| mz_system | PUBLIC  | mydb        | null   | public      | schema      | USAGE          |
| mz_system | PUBLIC  | null        | null   | materialize | database    | USAGE          |
| mz_system | PUBLIC  | null        | null   | quickstart  | cluster     | USAGE          |
```

**Functional roles:**

**View manager role:**

Show the privileges for the `view_manager` role created in the
[Create a role section](#create-a-role).
```mzsql
SHOW PRIVILEGES FOR view_manager;

```

The results show that the role currently has only the privileges inherited
through the `PUBLIC` role.

```none
| grantor   | grantee | database    | schema | name        | object_type | privilege_type |
| --------- | ------- | ----------- | ------ | ----------- | ----------- | -------------- |
| mz_system | PUBLIC  | materialize | null   | public      | schema      | USAGE          |
| mz_system | PUBLIC  | mydb        | null   | public      | schema      | USAGE          |
| mz_system | PUBLIC  | null        | null   | materialize | database    | USAGE          |
| mz_system | PUBLIC  | null        | null   | quickstart  | cluster     | USAGE          |
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
| grantor   | grantee | database    | schema | name        | object_type | privilege_type |
| --------- | ------- | ----------- | ------ | ----------- | ----------- | -------------- |
| mz_system | PUBLIC  | materialize | null   | public      | schema      | USAGE          |
| mz_system | PUBLIC  | mydb        | null   | public      | schema      | USAGE          |
| mz_system | PUBLIC  | null        | null   | materialize | database    | USAGE          |
| mz_system | PUBLIC  | null        | null   | quickstart  | cluster     | USAGE          |
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
| grantor   | grantee | database    | schema | name        | object_type | privilege_type |
| --------- | ------- | ----------- | ------ | ----------- | ----------- | -------------- |
| mz_system | PUBLIC  | materialize | null   | public      | schema      | USAGE          |
| mz_system | PUBLIC  | mydb        | null   | public      | schema      | USAGE          |
| mz_system | PUBLIC  | null        | null   | materialize | database    | USAGE          |
| mz_system | PUBLIC  | null        | null   | quickstart  | cluster     | USAGE          |
```

> **Tip:** For the `SHOW PRIVILEGES` command, you can add a `WHERE` clause to filter by the
> return fields; e.g., `SHOW PRIVILEGES FOR view_manager WHERE
> name='quickstart';`.

### Grant privileges to a role

To grant [privileges](/security/appendix/appendix-command-privileges/) to
a role, use the [`GRANT PRIVILEGE`](/sql/grant-privilege/) statement (see
[`GRANT PRIVILEGE`](/sql/grant-privilege/) for the full syntax)

> **Privilege(s) required to run the command:** - Ownership of affected objects. - `USAGE` privileges on the containing database if the affected object is a schema. - `USAGE` privileges on the containing schema if the affected object is namespaced by a schema. - _superuser_ status if the privilege is a system privilege. To override the **object ownership** requirements to grant privileges, run as a user with superuser privileges; e.g. `mz_system` user. 

```mzsql
GRANT <PRIVILEGE> ON <OBJECT_TYPE> <object_name> TO <role>;
```

When possible, avoid granting privileges directly to individual user or service
account roles. Instead, create reusable, functional roles (e.g., `data_reader`,
`view_manager`) with well-defined privileges, and grant these roles to the
individual user or service account roles. You can also grant functional roles to
other functional roles to compose more complex functional roles.

For example, the following grants privileges to the functional roles.

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
{{% include-headless "/headless/rbac-sm/select-views-privileges" %}}
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
| grantor   | grantee      | database    | schema | name                | object_type       | privilege_type |
| --------- | ------------ | ----------- | ------ | ------------------- | ----------------- | -------------- |
| mz_system | PUBLIC       | materialize | null   | public              | schema            | USAGE          |
| mz_system | PUBLIC       | mydb        | null   | public              | schema            | USAGE          |
| mz_system | PUBLIC       | null        | null   | materialize         | database          | USAGE          |
| mz_system | PUBLIC       | null        | null   | quickstart          | cluster           | USAGE          |
| mz_system | view_manager | mydb        | sales  | items               | table             | SELECT         |
| mz_system | view_manager | mydb        | sales  | orders              | table             | SELECT         |
| mz_system | view_manager | mydb        | sales  | orders_daily_totals | materialized-view | SELECT         |
| mz_system | view_manager | mydb        | sales  | orders_view         | view              | SELECT         |
| mz_system | view_manager | mydb        | sales  | sales_items         | table             | SELECT         |
| mz_system | view_manager | mydb        | null   | sales               | schema            | CREATE         |
| mz_system | view_manager | mydb        | null   | sales               | schema            | USAGE          |
| mz_system | view_manager | null        | null   | compute_cluster     | cluster           | CREATE         |
| mz_system | view_manager | null        | null   | compute_cluster     | cluster           | USAGE          |
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
privileges](/security/self-managed/access-control/manage-roles/#manage-future-privileges-for-a-role)
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
| grantor   | grantee               | database    | schema | name            | object_type | privilege_type |
| --------- | --------------------- | ----------- | ------ | --------------- | ----------- | -------------- |
| mz_system | PUBLIC                | materialize | null   | public          | schema      | USAGE          |
| mz_system | PUBLIC                | mydb        | null   | public          | schema      | USAGE          |
| mz_system | PUBLIC                | null        | null   | materialize     | database    | USAGE          |
| mz_system | PUBLIC                | null        | null   | quickstart      | cluster     | USAGE          |
| mz_system | serving_index_manager | mydb        | null   | sales           | schema      | CREATE         |
| mz_system | serving_index_manager | null        | null   | serving_cluster | cluster     | CREATE         |
| mz_system | serving_index_manager | null        | null   | serving_cluster | cluster     | USAGE          |
```

{{< note >}}

In addition to database privileges, a role must be the owner of the object
on which the index is created. In our examples, `view_manager` role has
privileges to create the various materialized views that will be indexed:

- See [Grant a role to another
role](/security/self-managed/access-control/manage-roles/#grant-a-role-to-another-role) for
details and example of granting `serving_cluster` role to `view_manager`.

- See [Change ownership of
objects](/security/self-managed/access-control/manage-roles/#change-ownership-of-objects)
for details and example of changing ownership of objects.

{{</ note >}}

**Data reader role:**
The following example grants the `data_reader` role privileges to run:

- [`SELECT`](/sql/select/#privileges) from all existing tables/materialized
  views/views/sources in the `mydb.sales` schema on the `serving_cluster`.

{{< note >}}
If a query directly references a view or materialized view:
{{% include-headless "/headless/rbac-sm/select-views-privileges" %}}
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
| grantor   | grantee     | database    | schema | name                | object_type       | privilege_type |
| --------- | ----------- | ----------- | ------ | ------------------- | ----------------- | -------------- |
| mz_system | PUBLIC      | materialize | null   | public              | schema            | USAGE          |
| mz_system | PUBLIC      | mydb        | null   | public              | schema            | USAGE          |
| mz_system | PUBLIC      | null        | null   | materialize         | database          | USAGE          |
| mz_system | PUBLIC      | null        | null   | quickstart          | cluster           | USAGE          |
| mz_system | data_reader | mydb        | sales  | items               | table             | SELECT         |
| mz_system | data_reader | mydb        | sales  | orders              | table             | SELECT         |
| mz_system | data_reader | mydb        | sales  | orders_daily_totals | materialized-view | SELECT         |
| mz_system | data_reader | mydb        | sales  | orders_view         | view              | SELECT         |
| mz_system | data_reader | mydb        | sales  | sales_items         | table             | SELECT         |
| mz_system | data_reader | mydb        | null   | sales               | schema            | USAGE          |
| mz_system | data_reader | null        | null   | serving_cluster     | cluster           | USAGE          |
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
privileges](/security/self-managed/access-control/manage-roles/#manage-future-privileges-for-a-role)
to automatically grant privileges on new objects.

{{</ important >}}

### Grant a role to another role

Once a role is created, you can modify its privileges either:

- Directly by [granting privileges for a role](#grant-privileges-to-a-role) or
  [revoking privileges from a role](#revoke-privileges-from-a-role).
- Indirectly (through inheritance) by granting other roles to the role or
  [revoking roles from the role](#revoke-a-role-from-another-role).

> **Tip:** When possible, avoid granting privileges directly to individual user or service
> account roles. Instead, create reusable, functional roles (e.g., `data_reader`,
> `view_manager`) with well-defined privileges, and grant these roles to the
> individual user or service account roles. You can also grant functional roles to
> other functional roles to compose more complex functional roles.

To grant a role to another role (where the role can be a user role/service
account role/functional role), use the [`GRANT ROLE`](/sql/grant-role/)
statement (see [`GRANT ROLE`](/sql/grant-role/) for full syntax):

> **Privilege(s) required to run the command:** - `CREATEROLE` privileges on the system. `mz_system` user has the required privileges on the system. 

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
| grantor   | grantee      | database    | schema | name            | object_type | privilege_type |
| --------- | ------------ | ----------- | ------ | --------------- | ----------- | -------------- |
| mz_system | PUBLIC       | materialize | null   | public          | schema      | USAGE          |
| mz_system | PUBLIC       | mydb        | null   | public          | schema      | USAGE          |
| mz_system | PUBLIC       | null        | null   | materialize     | database    | USAGE          |
| mz_system | PUBLIC       | null        | null   | quickstart      | cluster     | USAGE          |
| mz_system | view_manager | mydb        | sales  | items           | table       | SELECT         |
| mz_system | view_manager | mydb        | sales  | orders          | table       | SELECT         |
| mz_system | view_manager | mydb        | sales  | sales_items     | table       | SELECT         |
| mz_system | view_manager | mydb        | null   | sales           | schema      | CREATE         |
| mz_system | view_manager | mydb        | null   | sales           | schema      | USAGE          |
| mz_system | view_manager | null        | null   | compute_cluster | cluster     | CREATE         |
| mz_system | view_manager | null        | null   | compute_cluster | cluster     | USAGE          |
```

After the `view_manager` role is granted to `"blue.berry@example.com"`,
`"blue.berry@example.com"` can create objects in the `mydb.sales` schema on
the `compute_cluster`.
```mzsql
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
-- Requires SELECT on the materialized view and its underlying relations.
SELECT * FROM orders_daily_totals;

```
In Materialize, a role automatically gets all [applicable
privileges](/security/appendix/appendix-privileges/) for an
object they create; for example, the creator of a schema gets `CREATE` and
`USAGE`; the creator of a table gets `SELECT`, `INSERT`, `UPDATE`, and
`DELETE`.

For example, if you show privileges for `"blue.berry@example.com"` after
creating the view and materialized view, you will see that the role has
`SELECT` privileges on the `orders_daily_totals`  and `orders_view`.

```none
| grantor                | grantee                | database    | schema | name                | object_type       | privilege_type |
| ---------------------- | ---------------------- | ----------- | ------ | ------------------- | ----------------- | -------------- |
| blue.berry@example.com | blue.berry@example.com | mydb        | sales  | orders_daily_totals | materialized-view | SELECT         |
| blue.berry@example.com | blue.berry@example.com | mydb        | sales  | orders_view         | view              | SELECT         |
| mz_system              | PUBLIC                 | materialize | null   | public              | schema            | USAGE          |
| mz_system              | PUBLIC                 | mydb        | null   | public              | schema            | USAGE          |
... -- Rest omitted for brevity
```

{{< note >}}
If a query directly references a view or materialized view:
{{% include-headless "/headless/rbac-sm/select-views-privileges" %}}
{{</ note >}}

However, with the current privileges, `"blue.berry@example.com"` cannot
select from new views/materialized views created by **others** in
the schema and vice versa. For privileges on new objects, you can either:
- Manually grant privileges on new objects; or
- Use [default
privileges](/security/self-managed/access-control/manage-roles/#manage-future-privileges-for-a-role)
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
| grantor   | grantee               | database    | schema | name            | object_type | privilege_type |
| --------- | --------------------- | ----------- | ------ | --------------- | ----------- | -------------- |
| mz_system | PUBLIC                | materialize | null   | public          | schema      | USAGE          |
| mz_system | PUBLIC                | mydb        | null   | public          | schema      | USAGE          |
| mz_system | PUBLIC                | null        | null   | materialize     | database    | USAGE          |
| mz_system | PUBLIC                | null        | null   | quickstart      | cluster     | USAGE          |
| mz_system | serving_index_manager | mydb        | null   | sales           | schema      | CREATE         |
| mz_system | serving_index_manager | null        | null   | serving_cluster | cluster     | CREATE         |
| mz_system | serving_index_manager | null        | null   | serving_cluster | cluster     | USAGE          |
| mz_system | view_manager          | mydb        | sales  | items           | table       | SELECT         |
| mz_system | view_manager          | mydb        | sales  | orders          | table       | SELECT         |
| mz_system | view_manager          | mydb        | sales  | sales_items     | table       | SELECT         |
| mz_system | view_manager          | mydb        | null   | sales           | schema      | CREATE         |
| mz_system | view_manager          | mydb        | null   | sales           | schema      | USAGE          |
| mz_system | view_manager          | null        | null   | compute_cluster | cluster     | CREATE         |
| mz_system | view_manager          | null        | null   | compute_cluster | cluster     | USAGE          |
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
| grantor                | grantee                | database    | schema | name                | object_type       | privilege_type |
| ---------------------- | ---------------------- | ----------- | ------ | ------------------- | ----------------- | -------------- |
| blue.berry@example.com | blue.berry@example.com | mydb        | sales  | orders_daily_totals | materialized-view | SELECT         |
| blue.berry@example.com | blue.berry@example.com | mydb        | sales  | orders_view         | view              | SELECT         |
| mz_system              | PUBLIC                 | materialize | null   | public              | schema            | USAGE          |
| mz_system              | PUBLIC                 | mydb        | null   | public              | schema            | USAGE          |
| mz_system              | PUBLIC                 | null        | null   | materialize         | database          | USAGE          |
| mz_system              | PUBLIC                 | null        | null   | quickstart          | cluster           | USAGE          |
| mz_system              | serving_index_manager  | mydb        | null   | sales               | schema            | CREATE         |
| mz_system              | serving_index_manager  | null        | null   | serving_cluster     | cluster           | CREATE         |
| mz_system              | serving_index_manager  | null        | null   | serving_cluster     | cluster           | USAGE          |
| mz_system              | view_manager           | mydb        | sales  | items               | table             | SELECT         |
| mz_system              | view_manager           | mydb        | sales  | orders              | table             | SELECT         |
| mz_system              | view_manager           | mydb        | sales  | sales_items         | table             | SELECT         |
| mz_system              | view_manager           | mydb        | null   | sales               | schema            | CREATE         |
| mz_system              | view_manager           | mydb        | null   | sales               | schema            | USAGE          |
| mz_system              | view_manager           | null        | null   | compute_cluster     | cluster           | CREATE         |
| mz_system              | view_manager           | null        | null   | compute_cluster     | cluster           | USAGE          |
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
ownership of objects](/security/self-managed/access-control/manage-roles/#change-ownership-of-objects).

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
| grantor   | grantee     | database    | schema | name            | object_type | privilege_type |
| --------- | ----------- | ----------- | ------ | --------------- | ----------- | -------------- |
| mz_system | PUBLIC      | materialize | null   | public          | schema      | USAGE          |
| mz_system | PUBLIC      | mydb        | null   | public          | schema      | USAGE          |
| mz_system | PUBLIC      | null        | null   | materialize     | database    | USAGE          |
| mz_system | PUBLIC      | null        | null   | quickstart      | cluster     | USAGE          |
| mz_system | data_reader | mydb        | sales  | items           | table       | SELECT         |
| mz_system | data_reader | mydb        | sales  | orders          | table       | SELECT         |
| mz_system | data_reader | mydb        | sales  | sales_items     | table       | SELECT         |
| mz_system | data_reader | mydb        | null   | sales           | schema      | USAGE          |
| mz_system | data_reader | null        | null   | serving_cluster | cluster     | USAGE          |
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
privileges](/security/self-managed/access-control/manage-roles/#manage-future-privileges-for-a-role)
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

To view default privileges for a user, run [`SHOW DEFAULT
PRIVILEGES`](/sql/show-default-privileges) on the user's role. For example,
show the defaultprivileges for the `blue.berry@example.com` role created in
the [Create a role section](#create-individual-userservice-account-roles).
```mzsql
SHOW DEFAULT PRIVILEGES FOR "blue.berry@example.com";

```
The example results show that the default privileges for
`"blue.berry@example.com"` are the default privileges it has as a member of
the `PUBLIC` role.

{{% include-headless
"/headless/rbac-sm/show-default-privileges-new-roles" %}}

**Service account role:**

To view default privileges for a service account, run [`SHOW DEFAULT
PRIVILEGES`](/sql/show-default-privileges) on the service account's role. For example, show the default privileges for the `sales_report_app` role created in the
[Create a role section](#create-individual-userservice-account-roles).
```mzsql
SHOW DEFAULT PRIVILEGES FOR sales_report_app;

```
The example results show that the default privileges for `sales_report_app`
are the default privileges it has as a member of the `PUBLIC` role.

{{% include-headless
"/headless/rbac-sm/show-default-privileges-new-roles" %}}

**Functional roles:**

**View manager role:**

Show the default privileges for the `view_manager` role created in the
[Create a role section](#create-a-role).
```mzsql
SHOW DEFAULT PRIVILEGES FOR view_manager;

```
The example results show that the default privileges for `view_manager` are
the default privileges it has as a member of the `PUBLIC` role.

{{% include-headless
"/headless/rbac-sm/show-default-privileges-new-roles" %}}

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
"/headless/rbac-sm/show-default-privileges-new-roles" %}}

**Data reader role:**

Show the default privileges for the `data_reader` role created in the
[Create a role section](#create-a-role).
```mzsql
SHOW DEFAULT PRIVILEGES FOR data_reader;

```
The example results show that the default privileges for `data_reader` are
the default privileges it has as a member of the `PUBLIC` role.

{{% include-headless
"/headless/rbac-sm/show-default-privileges-new-roles" %}}

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

To illustrate, the following:
- creates a new user `lemon@example.com`,
- adds the user to the `view_manager` role, and
- creates a new default privilege, specifying `view_manager` as the
`<object_creator>`.
```mzsql
CREATE ROLE "lemon@example.com" WITH LOGIN PASSWORD '<password>';
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
{{% include-headless "/headless/rbac-sm/alter-role-tip" %}}
{{</ tip >}}

## Change ownership of objects

Certain [commands on an
object](/security/appendix/appendix-command-privileges/) (such as creating
an index on a materialized view or changing owner of an object) require
ownership of the object itself (or *superuser* privileges).

In Materialize, when a role creates an object, the role becomes the owner of the
object and is automatically  granted all [applicable
privileges](/security/appendix/appendix-privileges/) for the object. To
transfer ownership (and privileges) to another role (another user role/service
account role/functional role), you can use the [ALTER ... OWNER
TO](/sql/#rbac) command:

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
example](/security/self-managed/access-control/manage-roles/#alter-default-privileges)).

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
example](/security/self-managed/access-control/manage-roles/#alter-default-privileges)).

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

- [Access control best practices](/security/self-managed/access-control/#best-practices)
- [Manage privileges with Terraform](/developer-tools/terraform/manage-rbac/)

<!-- mz-docs page: security/self-managed/authentication -->

# Authentication
Authentication
## Configuring Authentication Type

To configure the authentication type used by Self-Managed Materialize, use the
`spec.authenticatorKind` setting in conjunction with any specific configuration
for the authentication method.

The `spec.authenticatorKind` setting determines which authentication method is
used:

| authenticatorKind Value | Description |
| --- | --- |
| <strong>None</strong> | Disables authentication. All users are trusted based on their claimed identity <strong>without</strong> any verification. <strong>Default</strong> |
| <strong>SASL/SCRAM</strong> | <p>Enables:</p> <ul> <li> <p><a href="#configuring-saslscram-authentication" >SASL/SCRAM-SHA-256 authentication</a> for <strong>PostgreSQL wire protocol connections</strong>. SASL/SCRAM-SHA-256 is a challenge-response authentication mechanism that provides enhanced security compared to simple password authentication.</p> </li> <li> <p>Standard password authentication for HTTP/Web Console connections.</p> </li> </ul> <p>When enabled, users must authenticate with their password.</p> > **Tip:** When enabled, you must also set the `mz_system` user password in > `external_login_password_mz_system`. See [Configuring SASL/SCRAM > authentication](#configuring-saslscram-authentication) for details.   |
| <strong>Password</strong> | <p>Enables <a href="#configuring-password-authentication" >password authentication</a> for users. When enabled, users must authenticate with their password.</p> > **Tip:** When enabled, you must also set the `mz_system` user password in > `external_login_password_mz_system`. See [Configuring password > authentication](#configuring-password-authentication) for details. |
| <strong>Oidc</strong> | <p>Enables <a href="/security/self-managed/sso/" >OIDC authentication</a> using JWT tokens from an external identity provider. Users authenticate via their organization&rsquo;s identity provider (e.g., Okta, Microsoft Entra ID).</p> > **Tip:** When enabled, you must also set the `mz_system` user password in > `external_login_password_mz_system`. See [Single sign-on (SSO)](/security/self-managed/sso/) for details. |

> **Warning:** Once enabled, ensure that the `authenticatorKind` field is set for any future version upgrades or rollouts of the Materialize CR. Having it undefined will reset `authenticationKind` to `None`.

### Configuring SASL/SCRAM authentication

> **Note:** SASL/SCRAM-SHA-256 authentication requires Materialize `v26.0.0` or later.

SASL authentication requires users to log in with a password.

When SASL authentication is enabled:
- **PostgreSQL connections** (e.g., `psql`, client libraries, [connection
  poolers](/serve-results/connection-pooling/)) use SCRAM-SHA-256 authentication.
- **HTTP/Web Console connections** use standard password authentication.

This hybrid approach provides maximum security for SQL connections while
maintaining compatibility with web-based tools.

To configure Self-Managed Materialize for SASL/SCRAM authentication, update the
following fields:

| Resource | Configuration | Description
|----------|---------------| ------------
| Materialize CR | `spec.authenticatorKind` | Set to `Sasl` to enable SASL/SCRAM-SHA-256 authentication for PostgreSQL connections.
| Kubernetes Secret | `external_login_password_mz_system` | Specify the password for the `mz_system` user, who is the only user initially available. Add `external_login_password_mz_system` to the Kubernetes Secret referenced in the Materialize CR's `spec.backendSecretName` field.

The following example Kubernetes manifest includes configuration for
SASL/SCRAM-SHA-256 authentication:

**v1alpha1:**

<p><code>v1alpha1</code> is the default CRD version for the Materialize Helm
chart. The Terraform modules default to <code>v1</code> starting in v4.0.0.
With <code>v1alpha1</code>, instance rollouts require manually rotating a
UUID.</p>

```hc {hl_lines="15 25"}
apiVersion: v1
kind: Namespace
metadata:
  name: materialize-environment
---
apiVersion: v1
kind: Secret
metadata:
  name: materialize-backend
  namespace: materialize-environment
stringData:
  metadata_backend_url: "..."
  persist_backend_url: "..."
  license_key: "..."
  external_login_password_mz_system: "enter_mz_system_password"
---
apiVersion: materialize.cloud/v1alpha1
kind: Materialize
metadata:
  name: 12345678-1234-1234-1234-123456789012
  namespace: materialize-environment
spec:
  environmentdImageRef: materialize/environmentd:v26.43.0
  backendSecretName: materialize-backend
  authenticatorKind: Sasl
  requestRollout: 00000000-0000-0000-0000-000000000003 # Enabling auth on an existing instance requires a rollout
```

**v1:**

<p>The <code>v1</code> CRD is available starting in v26.30. It is opt-in for the Helm chart and the default for the Terraform modules starting in v4.0.0. See <a href="/self-managed-deployments/upgrading/adopting-the-v1-crd/">Adopting the v1 CRD</a> to enable it.</p>

```hc {hl_lines="15 25"}
apiVersion: v1
kind: Namespace
metadata:
  name: materialize-environment
---
apiVersion: v1
kind: Secret
metadata:
  name: materialize-backend
  namespace: materialize-environment
stringData:
  metadata_backend_url: "..."
  persist_backend_url: "..."
  license_key: "..."
  external_login_password_mz_system: "enter_mz_system_password"
---
apiVersion: materialize.cloud/v1
kind: Materialize
metadata:
  name: 12345678-1234-1234-1234-123456789012
  namespace: materialize-environment
spec:
  environmentdImageRef: materialize/environmentd:v26.43.0
  backendSecretName: materialize-backend
  authenticatorKind: Sasl
```

> **Warning:** Once enabled, ensure that the `authenticatorKind` field is set for any future version upgrades or rollouts of the Materialize CR. Having it undefined will reset `authenticationKind` to `None`.

### Configuring password authentication

> **Public Preview:** This feature is in public preview.

Password authentication requires users to log in with a password.

To configure Self-Managed Materialize for password authentication, update the following fields:

| Resource | Configuration | Description
|----------|---------------| ------------
| Materialize CR | `spec.authenticatorKind` | Set to `Password` to enable password authentication.
| Kubernetes Secret | `external_login_password_mz_system` | Specify the password for the `mz_system` user, who is the only user initially available. Add `external_login_password_mz_system` to the Kubernetes Secret referenced in the Materialize CR's `spec.backendSecretName` field.

The following example Kubernetes manifest includes configuration for password
authentication:

**v1alpha1:**

<p><code>v1alpha1</code> is the default CRD version for the Materialize Helm
chart. The Terraform modules default to <code>v1</code> starting in v4.0.0.
With <code>v1alpha1</code>, instance rollouts require manually rotating a
UUID.</p>

```hc {hl_lines="15 25"}
apiVersion: v1
kind: Namespace
metadata:
  name: materialize-environment
---
apiVersion: v1
kind: Secret
metadata:
  name: materialize-backend
  namespace: materialize-environment
stringData:
  metadata_backend_url: "..."
  persist_backend_url: "..."
  license_key: "..."
  external_login_password_mz_system: "enter_mz_system_password"
---
apiVersion: materialize.cloud/v1alpha1
kind: Materialize
metadata:
  name: 12345678-1234-1234-1234-123456789012
  namespace: materialize-environment
spec:
  environmentdImageRef: materialize/environmentd:v26.43.0
  backendSecretName: materialize-backend
  authenticatorKind: Password
  requestRollout: 00000000-0000-0000-0000-000000000003 # Enabling auth on an existing instance requires a rollout
```

**v1:**

<p>The <code>v1</code> CRD is available starting in v26.30. It is opt-in for the Helm chart and the default for the Terraform modules starting in v4.0.0. See <a href="/self-managed-deployments/upgrading/adopting-the-v1-crd/">Adopting the v1 CRD</a> to enable it.</p>

```hc {hl_lines="15 25"}
apiVersion: v1
kind: Namespace
metadata:
  name: materialize-environment
---
apiVersion: v1
kind: Secret
metadata:
  name: materialize-backend
  namespace: materialize-environment
stringData:
  metadata_backend_url: "..."
  persist_backend_url: "..."
  license_key: "..."
  external_login_password_mz_system: "enter_mz_system_password"
---
apiVersion: materialize.cloud/v1
kind: Materialize
metadata:
  name: 12345678-1234-1234-1234-123456789012
  namespace: materialize-environment
spec:
  environmentdImageRef: materialize/environmentd:v26.43.0
  backendSecretName: materialize-backend
  authenticatorKind: Password
```

> **Warning:** Once enabled, ensure that the `authenticatorKind` field is set for any future version upgrades or rollouts of the Materialize CR. Having it undefined will reset `authenticationKind` to `None`.

### Configuring OIDC authentication

OIDC (OpenID Connect) authentication allows users to authenticate using JWT
tokens from an external identity provider such as Okta or Microsoft Entra ID.

For detailed setup instructions, including identity provider configuration and
system parameter settings, see [Single sign-on (SSO)](/security/self-managed/sso/).

## Logging in and creating users

> **Note:** With OIDC authentication, roles are [auto-provisioned](/security/self-managed/sso/#auto-provisioning-roles) when a
> user first [logs in through SSO](/security/self-managed/sso/#step-4-verify-the-configuration).

When authentication is enabled, only the `mz_system` user is initially
available. To create additional users:

1. Login as the `mz_system` user, using the `external_login_password_mz_system`
password. ![Image of Materialize Console login screen with mz_system
user](/images/mz_system_login.png "Materialize Console login screen with
mz_system user")
> **Note:** This login screen appears only for authenticator kinds Password and SASL/SCRAM.

1. Use [`CREATE ROLE ... WITH LOGIN PASSWORD ...`](/sql/create-role) to create
new users:

   ```mzsql
   CREATE ROLE <user> WITH LOGIN PASSWORD '<password>';
   ```

1. Log out as `mz_system` user.

   > **Important:** In general, other than the initial login to create new users, avoid using
>    `mz_system` since `mz_system` also used by the Materialize Operator for
>    upgrades and maintenance tasks.

1. Login as one of the created users.

## RBAC

For details on role-based access control (RBAC), including enabling RBAC, see
[Access Control](/security/self-managed/access-control/).

> **Warning:** If RBAC is not enabled, all users have <red>**superuser**</red> privileges.

## See also

- For all Materialize CR settings, see [Materialize CRD Field
Descriptions](/installation/appendix-materialize-crd-field-descriptions/).

<!-- mz-docs page: security/self-managed/sso -->

# Single sign-on (SSO)
Configure OIDC-based single sign-on (SSO) for Self-Managed Materialize.
> **Public Preview:** This feature is in public preview.

Single sign-on (SSO) allows users to authenticate to Self-Managed Materialize
using their organization's identity provider (IdP) via
[OpenID Connect (OIDC)](https://openid.net/developers/how-connect-works/).
Instead of managing passwords directly in Materialize, users sign in through
their IdP (e.g., Okta, Microsoft Entra ID) and receive a JWT token that
Materialize validates.

> **Note:** SSO handles **authentication** only. Permissions within the database are managed
> separately using [role-based access control (RBAC)](/security/self-managed/access-control/).

> **Note:** **Current limitations:**
> - **SAML** authentication is not supported. Materialize supports OIDC only.
> - **SCIM** is not supported. Users are auto-provisioned on first SSO login (see [Auto-provisioning roles](#auto-provisioning-roles)), but removing a user from your IdP does not automatically deprovision their Materialize role.
> - **IdP group-to-role mapping** is not supported. Each user maps 1:1 to a single Materialize role via a JWT claim; privileges and group-based assignment are managed via [RBAC](/security/self-managed/access-control/).

## Before you begin

Make sure you have:

- An OIDC-capable identity provider (e.g., Okta, Microsoft Entra ID, or any
  provider that supports OpenID Connect).
- Admin access to your Kubernetes cluster where Materialize is deployed.

## Step 1. Configure your identity provider

> **Note:** You will use the following values from your IdP configuration to [configure
> OIDC system parameters for Materialize](#step-3-configure-oidc-system-parameters):
> - The OIDC **issuer URL**
> - The **client ID** for the console application
> - If using service accounts, the client ID, client secret, and expected
>   audience for each service-account application

**Okta:**

The following steps create the OIDC application for the **Materialize Console**
(browser-based login). If you also need service accounts, you will create
additional applications in the [Service accounts](#service-accounts) section.

1. In the Okta Admin Console, go to **Applications** > **Applications** and
   click **Create App Integration**.

1. Select **OIDC - OpenID Connect** as the sign-in method and **Single-Page
   Application** as the application type. Click **Next**.

1. Configure the application:
   - **App integration name**: Enter a name (e.g., `Materialize`).
   - **Grant type**: Ensure **Authorization Code** is selected (PKCE is used
     automatically for single-page applications).
   - **Sign-in redirect URIs**: Enter
     `https://<your-console-domain>/auth/callback`. If you want to use the
     [CLI token flow](#get-a-token-using-cli-tools), also add
     `http://localhost:9876/callback`.
   - **Sign-out redirect URIs**: Optionally, enter
     `https://<your-console-domain>/account/login`.

1. Click **Save**.

1. On the application's **General** tab, note the **Client ID**.

   *Single-page applications use PKCE instead of a client secret. You do not
   need a client secret for the console application.*

1. Go to **Security** > **API** and note your **Issuer URI** from the
   authorization server you want to use (e.g.,
   `https://your-org.okta.com/oauth2/default`).

   **Custom domains:** When the authorization server **Issuer** is set to **Dynamic (based on Request Domain)**, Okta issues tokens whose `iss` claim uses your custom domain (for example, `https://sso.your-org.com/oauth2/default`) instead of the default Okta URL. Configure the `oidc_issuer` system parameter in Materialize to match that issuer value exactly.

   > **Warning:** Use a **custom authorization server** (e.g., `.../oauth2/default`), not the
   > Okta **org authorization server** (the bare org URL, without an
   > `/oauth2/...` path). Access tokens issued by the org authorization server
   > have a fixed `aud` claim and cannot carry custom claims or scopes, which
   > breaks the [Client Credentials flow](#client-credentials-flow) and
   > [MCP clients](#connecting-mcp-clients). Custom authorization servers,
   > including `default`, require Okta's API Access Management feature.

1. Go to the **Assignments** tab and assign the users or groups that should have
   access to Materialize.

   When a user authenticates via SSO, Materialize uses a JWT claim to determine
   the role name. See [Mapping IdP users to Materialize roles](#mapping-idp-users-to-materialize-roles) for more details.

1. Configure the authorization server. In the Okta Admin Console, go to
   **Security** > **API** and click on the authorization server you want to
   use (e.g., **default**).

   1. On the **Settings** tab, note the **Issuer** URI. This is the value you
      will use for the `oidc_issuer` system parameter.

   1. Go to the **Scopes** tab and ensure the `openid` and `email` scopes
      exist (they are present by default).

   1. Go to the **Access Policies** tab. You need at least one policy with a
      rule that allows the grant types you plan to use:

      - **Authorization Code**: Required for the console login.
      - **Resource Owner Password**: Required for the
        [ROPC service account flow](#resource-owner-password-flow).
      - **Client Credentials**: Required for the
        [Client Credentials service account flow](#client-credentials-flow).

      To add or edit a rule:

      1. Click **Add New Access Policy** (or select an existing policy).
      1. Click **Add Rule** within the policy.
      1. Under **Grant type is**, check the grant types you need.
      1. Under **Assigned to**, select the clients (applications) this rule
         applies to.
      1. Click **Create Rule**.

**Microsoft Entra ID:**

1. In the [Azure portal](https://portal.azure.com), go to **Microsoft Entra
   ID** > **App registrations** and click **New registration**.

1. Configure the registration:
   - **Name**: Enter a name (e.g., `Materialize`).
   - **Supported account types**: Select the appropriate option for your
     organization (typically **Accounts in this organizational directory only**).
   - **Redirect URI**: Select **Single-page application (SPA)** and enter
     `https://<your-console-domain>/auth/callback`. After registration, you
     can add `http://localhost:9876/callback` under **Authentication** if you
     want to use the [CLI token flow](#get-a-token-using-cli-tools).

1. Click **Register**.

1. On the application's **Overview** page, note the **Application (client) ID**
   and the **Directory (tenant) ID**.

1. Go to **Certificates & secrets** > **New client secret**. Add a description
   and expiration, then click **Add**. Note the secret **Value**.

   *A client secret is not required for the console login (which uses
   authorization code with PKCE), but is needed if you plan to use the
   [Client Credentials flow](#client-credentials-flow) for service accounts.*

1. Construct your issuer URL using your tenant ID:

   ```
   https://login.microsoftonline.com/<tenant-id>/v2.0
   ```

1. Go to **Enterprise applications** > select your application > **Users and
   groups** and assign the users or groups that should have access to
   Materialize.

   When a user authenticates via SSO, Materialize uses a JWT claim to determine
   the role name. See [Mapping IdP users to Materialize roles](#mapping-idp-users-to-materialize-roles) for more details.

**Generic OIDC:**

1. In your identity provider, create a new OIDC **public** client application
   (single-page application type) with the **Authorization Code** grant type
   and **PKCE** support.

1. Set the redirect URI to `https://<your-console-domain>/auth/callback`. If
   you want to use the [CLI token flow](#get-a-token-using-cli-tools), also
   add `http://localhost:9876/callback`.

1. Note the **client ID** and **issuer URL** provided by your identity provider.
   The issuer URL is typically the base URL of your identity provider's OIDC
   discovery endpoint (without `/.well-known/openid-configuration`).

1. Ensure the `openid` scope is available.

1. Assign users or groups that should have access to Materialize.

   When a user authenticates via SSO, Materialize uses a JWT claim to determine
   the role name. See [Mapping IdP users to Materialize roles](#mapping-idp-users-to-materialize-roles) for more details.

> **Note:** Once you have configured your IdP, you will need the following values to [configure
> OIDC system parameters for Materialize](#step-3-configure-oidc-system-parameters):
> - The OIDC **issuer URL**
> - The **client ID** for the console application
> - If using service accounts, the client ID, client secret, and expected
>   audience for each service-account application

## Step 2. Enable OIDC authentication

To configure Self-Managed Materialize for OIDC authentication, update the
following fields:

| Resource | Configuration | Description
|----------|---------------| ------------
| Materialize CR | `spec.authenticatorKind` | Set to `Oidc` to enable OIDC authentication.
| Kubernetes Secret | `external_login_password_mz_system` | Specify the password for the `mz_system` user. Add `external_login_password_mz_system` to the Kubernetes Secret referenced in the Materialize CR's `spec.backendSecretName` field. The `mz_system` user **always** authenticates with a password. This user is required by the Materialize Operator for upgrades and serves as an emergency administrative account.
| ConfigMap | `mz-system-params` | Create an empty system parameter ConfigMap and reference it from the Materialize CR's `spec.systemParameterConfigmapName` field. You will populate it with your OIDC parameters in [Step 3](#step-3-configure-oidc-system-parameters).

The following example Kubernetes manifest includes configuration for OIDC
authentication:

**v1alpha1:**

<p><code>v1alpha1</code> is the default CRD version for the Materialize Helm
chart. The Terraform modules default to <code>v1</code> starting in v4.0.0.
With <code>v1alpha1</code>, instance rollouts require manually rotating a
UUID.</p>

```yaml {hl_lines="6-15 26 36-38"}
apiVersion: v1
kind: Namespace
metadata:
  name: materialize-environment
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: mz-system-params
  namespace: materialize-environment
data:
  # Create an empty system parameter configmap for later steps
  system-params.json: |
    {
    }
---
apiVersion: v1
kind: Secret
metadata:
  name: materialize-backend
  namespace: materialize-environment
stringData:
  metadata_backend_url: "..."
  persist_backend_url: "..."
  license_key: "..."
  external_login_password_mz_system: "enter_mz_system_password"
---
apiVersion: materialize.cloud/v1alpha1
kind: Materialize
metadata:
  name: 12345678-1234-1234-1234-123456789012
  namespace: materialize-environment
spec:
  environmentdImageRef: materialize/environmentd:v26.43.0
  backendSecretName: materialize-backend
  authenticatorKind: Oidc
  requestRollout: 00000000-0000-0000-0000-000000000003 # Switching to Oidc requires a rollout
  systemParameterConfigmapName: mz-system-params # Adding a system parameter configmap requires a rollout
```

Apply the updated manifest to your Kubernetes cluster. See
[Upgrading](/self-managed-deployments/upgrading/#rollout-configuration) for
details on rollout configuration.

**v1:**

<p>The <code>v1</code> CRD is available starting in v26.30. It is opt-in for the Helm chart and the default for the Terraform modules starting in v4.0.0. See <a href="/self-managed-deployments/upgrading/adopting-the-v1-crd/">Adopting the v1 CRD</a> to enable it.</p>

```yaml {hl_lines="6-15 26 36-37"}
apiVersion: v1
kind: Namespace
metadata:
  name: materialize-environment
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: mz-system-params
  namespace: materialize-environment
data:
  # Create an empty system parameter configmap for later steps
  system-params.json: |
    {
    }
---
apiVersion: v1
kind: Secret
metadata:
  name: materialize-backend
  namespace: materialize-environment
stringData:
  metadata_backend_url: "..."
  persist_backend_url: "..."
  license_key: "..."
  external_login_password_mz_system: "enter_mz_system_password"
---
apiVersion: materialize.cloud/v1
kind: Materialize
metadata:
  name: 12345678-1234-1234-1234-123456789012
  namespace: materialize-environment
spec:
  environmentdImageRef: materialize/environmentd:v26.43.0
  backendSecretName: materialize-backend
  authenticatorKind: Oidc
  systemParameterConfigmapName: mz-system-params
```

Apply the updated manifest to your Kubernetes cluster. With the `v1` CRD,
rollouts trigger automatically when spec fields change, so no `requestRollout`
is needed. See
[Upgrading](/self-managed-deployments/upgrading/#rollout-configuration)
for details on rollout configuration.

> **Warning:** Once enabled, ensure that the `authenticatorKind` field is set for any future version upgrades or rollouts of the Materialize CR. Having it undefined will reset `authenticationKind` to `None`.

## Step 3. Configure OIDC system parameters

Configure the OIDC system parameters to connect Materialize to your identity
provider. You can use either a
[ConfigMap](/self-managed-deployments/configuration-system-parameters/#configure-system-parameters-via-configmap)
or SQL commands, but it is strongly recommended to use a ConfigMap. See [Configure via ConfigMap](#configure-via-configmap) for more details.

### OIDC system parameters

| Parameter | Description | Required | Default |
|-----------|-------------|----------|---------|
| `oidc_issuer` | The OIDC issuer URL (e.g., `https://your-org.okta.com/oauth2/default`). Materialize uses this to discover the JWKS endpoint for token validation. | Yes | None |
| `oidc_audience` | A JSON array of expected audience values for token validation (e.g., `["your-client-id"]`). Use the **client ID from [Step 1](#step-1-configure-your-identity-provider)**. Materialize checks that the JWT's `aud` claim contains at least one of these values. **By default, this is empty, and audience validation is skipped.**| No | `[]` |
| `oidc_authentication_claim` | The JWT claim to use as the Materialize username. For ID tokens (human users), a common claim is `email`. For access tokens from the [Client Credentials flow](#client-credentials-flow), ensure this claim exists in the token. See [Mapping IdP users to Materialize roles](#mapping-idp-users-to-materialize-roles) for details. | No | `sub` |
| `console_oidc_client_id` | The OIDC client ID used by the web console for the authorization code flow. | For console login | Empty |
| `console_oidc_scopes` | Space-separated OIDC scopes requested by the web console when obtaining a token. Scopes control which claims are included in the token. The `openid` scope is required to obtain an ID token. Add `email` to include the `email` claim, or `profile` to include name claims. If `oidc_authentication_claim` references a claim like `email`, you must request the corresponding scope here. | For console login | Empty |

> **Warning:** When `oidc_audience` is empty, audience validation is skipped. This means
> **any** valid token from the same identity provider can authenticate to
> Materialize, including tokens issued for other applications. **Always set
> `oidc_audience` in production environments.**

### Configure via ConfigMap

In [Step 2](#step-2-enable-oidc-authentication), you already created an empty
`mz-system-params` ConfigMap. Now, populate that ConfigMap with your
OIDC parameters. At this point, your manifest should look like:

```yaml {hl_lines="9-13"}
apiVersion: v1
kind: ConfigMap
metadata:
  name: mz-system-params
  namespace: materialize-environment
data:
  system-params.json: |
    {
      "oidc_issuer": "YOUR_OIDC_ISSUER",
      "oidc_audience": "[\"CONSOLE_CLIENT_ID\"]",
      "oidc_authentication_claim": "email",
      "console_oidc_client_id": "CONSOLE_CLIENT_ID",
      "console_oidc_scopes": "openid email"
    }
```

> **Note:** This example sets `oidc_authentication_claim` to `email` rather than the default
> `sub`, so each user's role name comes from their `email` claim. Because the
> authentication claim references `email`, `console_oidc_scopes` includes the
> `email` scope to ensure that claim is present in the token.

Apply the updated ConfigMap to your Kubernetes cluster. The changes could take
up to a minute to take effect. For more
on configuring system parameters via a ConfigMap, see [System parameters
configuration](/self-managed-deployments/configuration-system-parameters/#configure-system-parameters-via-configmap).

### Configure via SQL

Alternatively, connect as `mz_system` and set the parameters using
`ALTER SYSTEM SET`. The `mz_system` user always authenticates with a password,
even when OIDC is enabled.

```mzsql
ALTER SYSTEM SET oidc_issuer = 'https://your-org.okta.com/oauth2/default';
ALTER SYSTEM SET oidc_audience = '["CONSOLE_CLIENT_ID"]';
ALTER SYSTEM SET oidc_authentication_claim = 'email';
ALTER SYSTEM SET console_oidc_client_id = 'CONSOLE_CLIENT_ID';
ALTER SYSTEM SET console_oidc_scopes = 'openid email';
```

## Step 4. Verify the configuration

1. Navigate to your Materialize Console. You should see an option to **Use
   single sign-on**.

   ![Materialize Console login screen showing the SSO sign-in
   option](/images/console/console-self-managed-sso.png "Materialize Console login screen
   with SSO option")

1. Sign in through your IdP. After successful authentication, you are redirected
   back to the Materialize Console.

1. To confirm which role you've signed in as via SSO, open the [SQL Shell](/developer-tools/console/sql-shell/) in the Materialize Console. In the welcome message, you should see the role name labeled under "User". This is derived from the `oidc_authentication_claim` claim in your identity token:

![Materialize Console Shell](/images/console/console.png "Materialize Console Shell")

## Connecting via SQL clients

To connect to Materialize using a SQL client like `psql`, you need an OIDC ID token.

If your client doesn't support OAuth, you can
create a role with a SQL password instead. See [SQL password authentication](#sql-password-authentication-recommended-for-non-oauth-clients).

### Get a token using CLI tools

You can fetch an
ID token from the command line using [`oauth2c`](https://github.com/cloudentity/oauth2c).
This is useful when configuring a non-interactive client like dbt or Terraform.

1. **Confirm `http://localhost:9876/callback` is registered as a redirect URI**
   on the Materialize Console OIDC client (added in
   [Step 1](#step-1-configure-your-identity-provider)). `oauth2c` listens on
   this URL during the auth code exchange.

1. **Install `oauth2c`.** On macOS:

    ```shell
    brew install cloudentity/tap/oauth2c
    ```

    Other platforms: see the
    [`oauth2c` installation guide](https://github.com/cloudentity/oauth2c#installation).

1. **Run `oauth2c` to fetch the ID token:**

    ```shell
    oauth2c <ISSUER_URL> \
      --client-id <YOUR_CLIENT_ID> \
      --response-types code \
      --response-mode form_post \
      --grant-type authorization_code \
      --pkce \
      --scopes 'openid email' \
      --auth-method none \
      --silent | jq -r '.id_token'
    ```

    A browser window opens to complete the IdP login. After signing in,
    `oauth2c` prints the ID token to stdout.

ID tokens expire (typically within an hour). Re-run the command above when
your token expires.

### Get a token from the Materialize console

Clicking "Connect" in the Materialize Console will provide you with an ID token that you can use to connect.

![Materialize Console connect instructions for OIDC](/images/console/console-connect-oidc.png "Materialize Console connect screen for OIDC")

### Connect with psql

Use the ID token as your password:

```shell
<PGPASSWORD>="<your-id-token>" \
psql -h <materialize-host> -p 6875 -U <username> materialize
```

Replace `<username>` with the value of the authentication claim in your JWT
(e.g., your email address if `oidc_authentication_claim` is set to `email`).

> **Note:** Materialize validates the token at **connection time only**. Once a connection
> is established, it persists until disconnected, regardless of token expiry.

## Connecting MCP clients

*OAuth sign-in for MCP clients is available starting in v26.31.*

Materialize provides built-in [MCP servers](/developer-tools/mcp-server/) at
`/api/mcp/agent` and `/api/mcp/developer`. When SSO is enabled, MCP clients
can authenticate with OAuth instead of an [MCP
token](/developer-tools/mcp-server/mcp-agent/#method-2-token-based-authentication).
Materialize publishes OAuth 2.0 Protected Resource Metadata ([RFC
9728](https://datatracker.ietf.org/doc/html/rfc9728)) at
`/.well-known/oauth-protected-resource`, which MCP-aware clients use to
discover your identity provider automatically.

Unlike the Console, which authenticates with an ID token, MCP clients present an
OAuth **access token**. Access tokens have additional configuration
requirements:

### Configure your IdP

1. **Pre-register an OIDC client for MCP.** The MCP specification expects the
   IdP to support anonymous Dynamic Client Registration ([RFC
   7591](https://datatracker.ietf.org/doc/html/rfc7591)). Most enterprise IdPs,
   including Okta, do not allow anonymous registration, causing MCP clients to
   fail during registration (in Okta, with HTTP 403 `E0000005`). Instead, create
   or reuse a public OIDC client with PKCE, add
   `http://localhost:<port>/callback` as a sign-in redirect URI, and configure
   the MCP client with the client ID explicitly.

1. **Include the authentication claim in access tokens.** IdPs typically include
   claims like `email` only in ID tokens. If `oidc_authentication_claim` is set
   to `email`, configure your authorization server to add an `email` claim to
   access tokens (in Okta, a claim with value `user.email` included in the
   access token). Otherwise, Materialize rejects the token because it does not
   contain the configured authentication claim.

1. **Use a Materialize-dedicated audience.** Configure your IdP so that the
   access tokens carry an `aud` value specifically for Materialize (e.g., in
   Okta, create a custom authorization server; in Entra ID, an exposed-API
   Application ID URI). Note the audience value for the Materialize
   configuration step below.

1. **Optional. Define an `mcp.read` scope.** Materialize advertises the
   `mcp.read` scope in its resource metadata. Although Materialize does not
   enforce the scope (authorization happens through
   [RBAC](/security/self-managed/access-control/)), clients that request
   advertised scopes fail against IdPs (such as Okta) that reject unknown scopes
   unless the scope exists on the authorization server.

1. **Optional. Add the `offline_access` scope for refresh tokens.** MCP
   clients typically request `offline_access` so they can refresh access
   tokens without a new browser sign-in. Okta and most enterprise IdPs
   require this scope to exist on the authorization server. If the client
   fails to reconnect after the first access token expires, add
   `offline_access` to the authorization server's scopes.

### Configure Materialize

1. **Add the authorization server's audience value to `oidc_audience`.** For
   access tokens, the `aud` claim is the authorization server's configured
   audience. Use the Materialize-dedicated audience from the IdP step above.

   Materialize also validates ID tokens (browser sign-in), whose `aud` is the
   Console client ID, so both values must be present in `oidc_audience`. Add
   the audience values to the existing array, preserving any entries already
   present. For example:

   ```mzsql
   ALTER SYSTEM SET oidc_audience = '["<CONSOLE_CLIENT_ID>", "<MZ_SPECIFIC_AUDIENCE>"]';
   ```

### Configure your MCP client

1. **Connect.** For example, to connect Claude Code to the
   `materialize-agent` MCP server with a pre-registered client:

   ```shell
   claude mcp add --transport http materialize-agent \
     https://<host>:6876/api/mcp/agent \
     --client-id <YOUR_CLIENT_ID> --callback-port 8080
   ```

   The `--callback-port` value must match the port in the
   `http://localhost:<port>/callback` redirect URI registered on the OIDC
   client. For more information, see
   [MCP servers](/developer-tools/mcp-server/).

> **Note:** Deployments behind a load balancer or proxy that rewrites the `Host` header
> must set the `http_host_name` configuration so that the URLs Materialize
> publishes in its resource metadata are correct.

## Provisioning roles

### Mapping IdP users to Materialize roles

Each user or service account that authenticates via OIDC maps to a single
Materialize database role. When a user authenticates into Materialize, their role name is the value of the JWT claim keyed by `oidc_authentication_claim`.

For example, if `oidc_authentication_claim` is set to `email` and a user authenticates with the following JWT:

```json
{
  "sub": "auth0|abc123",
  "email": "alice@your-org.com",
  "name": "Alice",
  "iat": 1516239022
}
```

Their role name will be `alice@your-org.com`.

If a user logs in and no matching role exists, Materialize auto-provisions one,
as described in the next section.

### Auto-provisioning roles

When a user signs in and no role matching their `oidc_authentication_claim`
value exists, Materialize **automatically creates** a role for them.

Auto-provisioned roles:
- Have default privileges only.
- Must be granted additional privileges through
  [RBAC](/security/self-managed/access-control/manage-roles/).
- Are not automatically removed when the user is removed from the IdP. See
  [De-provisioning users](#de-provisioning-users) for cleanup instructions.

#### Auditing auto-provisioned roles

To view which roles were auto-provisioned via OIDC, query `mz_audit_events`:

```mzsql
SELECT details
FROM mz_audit_events
WHERE event_type = 'create' AND object_type = 'role' AND details ->> 'auto_provision_source' = 'oidc'
ORDER BY occurred_at DESC;
```

Roles created through OIDC authentication will have `auto_provision_source` set to
`oidc`.

### Pre-provisioning roles

An administrator can create roles before users login, rather than rely on
auto-provisioning. To pre-provision a role, connect as a superuser and create
the role with a name matching the expected JWT claim value:

```mzsql
CREATE ROLE "alice@your-org.com" WITH LOGIN;
```

Like auto-provisioned roles, pre-provisioned roles start with default privileges
only and must be granted additional privileges through
[RBAC](/security/self-managed/access-control/manage-roles/).

## Service accounts

For machine-to-machine access, you have three options:

- [SQL password authentication](#sql-password-authentication-recommended-for-non-oauth-clients):
  for clients that don't support OAuth flows.
- [Resource Owner Password flow](#resource-owner-password-flow): for service
  accounts that authenticate against your IdP with a username and password.
- [Client Credentials flow](#client-credentials-flow): for service accounts
  that authenticate against your IdP without a user context.

### SQL password authentication (recommended for non-OAuth clients)

Even with OIDC enabled, Materialize still accepts SQL password authentication.
This is required for clients that don't support OAuth flows. The simplest way to
give such a service or application access is to create a role with a SQL
password.

1. As a user with the `CREATEROLE` privilege, create the role with a password:

    ```mzsql
    CREATE ROLE "svc-dbt" WITH LOGIN PASSWORD 'a-strong-password';
    ```

1. Grant the privileges this service account needs. See
   [Manage database roles](/security/self-managed/access-control/manage-roles/)
   for the full privilege model.

1. Connect using the password directly:

    ```shell
    <PGPASSWORD>="a-strong-password" \
    psql -h <materialize-host> -p 6875 -U svc-dbt materialize
    ```

For dbt-specific setup, see [dbt connection profiles](/developer-tools/dbt/get-started/).
For Terraform, see [Terraform: get started](/developer-tools/terraform/get-started/).

### Resource Owner Password flow

Use this approach when you need a service account that authenticates with a
username and password to obtain an ID token.

**Okta:**

1. In the Okta Admin Console, go to **Applications** > **Applications** and
   click **Create App Integration**.

1. Select **OIDC - OpenID Connect** as the sign-in method and **Native
   Application** as the application type. Click **Next**.

1. Configure the application:
   - **App integration name**: Enter a name (e.g., `Materialize ROPC`).
   - **Grant type**: Enable **Resource Owner Password**.

1. Click **Save** and note the **Client ID** and **Client Secret**.

1. Go to the **Assignments** tab and assign the service account user.

1. Ensure your authorization server's access policy includes a rule that
   allows the **Resource Owner Password** grant type for this application.
   See the authorization server setup in
   [Step 1](#step-1-configure-your-identity-provider).

1. In Okta, create a new user to serve as the service account (e.g.,
   `svc-materialize@your-org.com`).

   *The Resource Owner Password flow does not support MFA in Okta. The service
   account user must not have MFA enabled.*

1. Fetch an ID token:

   ```shell
   curl -X POST https://your-org.okta.com/oauth2/default/v1/token \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -H "Accept: application/json" \
     --data-urlencode "grant_type=password" \
     --data-urlencode "username=svc-materialize@your-org.com" \
     --data-urlencode "password=YOUR_SERVICE_ACCOUNT_PASSWORD" \
     --data-urlencode "scope=openid email" \
     --data-urlencode "client_id=YOUR_ROPC_CLIENT_ID" \
     --data-urlencode "client_secret=YOUR_ROPC_CLIENT_SECRET"
   ```

1. Extract the `id_token` from the JSON response and use it to connect:

   ```shell
   <PGPASSWORD>="<id-token>" \
   psql -h <materialize-host> -p 6875 -U svc-materialize@your-org.com materialize
   ```

**Microsoft Entra ID:**

1. In the [Azure portal](https://portal.azure.com), go to **Microsoft Entra
   ID** > **App registrations** and click **New registration**. Create a
   dedicated registration for this flow rather than reusing the console
   application from [Step 1](#step-1-configure-your-identity-provider).

1. Configure the registration:
   - **Name**: Enter a name (e.g., `Materialize ROPC`).
   - **Supported account types**: Select the appropriate option for your
     organization.

1. Click **Register**.

1. Go to **Authentication** and set **Allow public client flows** to **Yes**.
   This is required for the Resource Owner Password flow.

1. On the application's **Overview** page, note the **Application (client) ID**
   and the **Directory (tenant) ID**.

1. Go to **Certificates & secrets** > **New client secret**. Add a description
   and expiration, then click **Add**. Note the secret **Value**.

1. Create a new user to serve as the service account, then assign it to this
   application under **Enterprise applications** > **Users and groups**.

1. Fetch an ID token:

   ```shell
   curl -X POST https://login.microsoftonline.com/<tenant-id>/oauth2/v2.0/token \
     -H "Content-Type: application/x-www-form-urlencoded" \
     --data-urlencode "grant_type=password" \
     --data-urlencode "username=svc-materialize@your-org.com" \
     --data-urlencode "password=YOUR_SERVICE_ACCOUNT_PASSWORD" \
     --data-urlencode "scope=openid email" \
      --data-urlencode "client_id=YOUR_CLIENT_ID"
     --data-urlencode "scope=openid" \
     --data-urlencode "client_id=YOUR_CLIENT_ID" \
     --data-urlencode "client_secret=YOUR_CLIENT_SECRET"
   ```

1. Extract the `id_token` from the JSON response and use it to connect:

   ```shell
   <PGPASSWORD>="<id-token>" \
   psql -h <materialize-host> -p 6875 -U svc-materialize@your-org.com materialize
   ```

**Generic OIDC:**

1. Create a service account user in your identity provider.

1. Assign the service account to your Materialize application.

1. Enable the Resource Owner Password Credentials grant for your application.

1. Fetch an ID token from your IdP's token endpoint:

   ```shell
   curl -X POST https://your-idp.com/oauth2/token \
     -H "Content-Type: application/x-www-form-urlencoded" \
     --data-urlencode "grant_type=password" \
     --data-urlencode "username=svc-materialize@your-org.com" \
     --data-urlencode "password=YOUR_SERVICE_ACCOUNT_PASSWORD" \
     --data-urlencode "scope=openid email" \
     --data-urlencode "client_id=YOUR_CLIENT_ID" \
     --data-urlencode "client_secret=YOUR_CLIENT_SECRET"
   ```

1. Extract the `id_token` from the JSON response and use it to connect:

   ```shell
   <PGPASSWORD>="<id-token>" \
   psql -h <materialize-host> -p 6875 -U svc-materialize@your-org.com materialize
   ```

### Client Credentials flow

Use this approach to treat an IdP client as a service account. This is useful
for automated systems that do not have a user context.

> **Note:** `oidc_audience` is an array of values. Before running the `ALTER SYSTEM SET
> oidc_audience` examples below, check the current value with `SHOW oidc_audience;`
> and **append** the new audience rather than overwriting it. Otherwise you may
> remove the Materialize Console's audience or other configured values.

**Okta:**

1. In the Okta Admin Console, go to **Applications** > **Applications** and
   click **Create App Integration**.

1. Select **OIDC - OpenID Connect** as the sign-in method and **Web
   Application** as the application type. Click **Next**.

1. Configure the application:
   - **App integration name**: Enter a name (e.g., `Materialize Service Account 1`).
   - **Grant type**: Enable **Client Credentials** (deselect other grant
     types).

1. Click **Save** and note the **Client ID** and **Client Secret**.

1. Ensure your authorization server's access policy includes a rule that
   allows the **Client Credentials** grant type for this application.
   See the authorization server setup in
   [Step 1](#step-1-configure-your-identity-provider).

1. **Configure a custom claim for the service account identity.**

   The `oidc_authentication_claim` setting is global — it applies to both
   human users (ID tokens) and service accounts (access tokens). If set to
   `email`, human users get readable role names (e.g., `alice@your-org.com`),
   but Client Credentials access tokens do not include an `email` claim by
   default. If set to `sub`, Client Credentials tokens work, but human users
   lose email-based role names and get opaque subject IDs instead.

   To solve this, create a custom claim (e.g., `sql_username`) in your
   authorization server that maps to `user.email` for ID tokens and to a
   configured value for access tokens:

   1. In the Okta Admin Console, go to **Security** > **API** and select your
      authorization server.

   1. Go to the **Claims** tab and click **Add Claim**.

   1. Configure the claim for **ID tokens** (human users):
      - **Name**: `sql_username`
      - **Include in token type**: **ID Token** (always).
      - **Value type**: **Expression**.
      - **Value**: `appuser.email`
      - **Include in**: **Any scope**.

   1. Click **Create**, then click **Add Claim** again.

   1. Configure the claim for **access tokens** (service accounts):
      - **Name**: `sql_username`
      - **Include in token type**: **Access Token** (always).
      - **Value type**: **Expression**.
      - **Value**: `app.sub`
      - **Include in**: **Any scope**.

   1. Click **Create**.

   1. Set the authentication claim in Materialize:

      ```mzsql
      ALTER SYSTEM SET oidc_authentication_claim = 'sql_username';
      ```

   *If you have multiple service accounts using Client Credentials, each needs
   its own Okta application.*

1. Fetch an access token:

   ```shell
   curl -X POST https://your-org.okta.com/oauth2/default/v1/token \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -H "Accept: application/json" \
     --data-urlencode "grant_type=client_credentials" \
     --data-urlencode "scope=openid" \
     --data-urlencode "client_id=YOUR_SERVICE_CLIENT_ID" \
     --data-urlencode "client_secret=YOUR_SERVICE_CLIENT_SECRET"
   ```

1. Ensure `oidc_audience` includes the expected audience value for tokens from
   your authorization server. In Okta, the `aud` claim is set to the
   authorization server's audience (configured in **Security** > **API** > your
   auth server > **Settings**), not the client ID:

   ```mzsql
   -- Make sure to add to the array if already set
   ALTER SYSTEM SET oidc_audience = '["<CONSOLE_CLIENT_ID>", "<YOUR_AUDIENCE_VALUE>"]';
   ```

1. Extract the `access_token` from the JSON response and use it to connect:

   ```shell
   <PGPASSWORD>="<access-token>" \
   psql -h <materialize-host> -p 6875 -U <service-account-name> materialize
   ```

   The `<service-account-name>` must match the value of the `sql_username`
   claim in the access token (e.g., `svc-my-service`).

**Microsoft Entra ID:**

1. In the [Azure portal](https://portal.azure.com), go to **Microsoft Entra
   ID** > **App registrations** and click **New registration**.

1. Configure the registration:
   - **Name**: Enter a name (e.g., `Materialize Service Account`).
   - **Supported account types**: Select the appropriate option for your
     organization.

1. Click **Register**.

1. On the application's **Overview** page, note the **Application (client) ID**.

1. Go to **Certificates & secrets** > **New client secret**. Add a description
   and expiration, then click **Add**. Note the secret **Value**.

1. Fetch an access token:

   ```shell
   curl -X POST https://login.microsoftonline.com/<tenant-id>/oauth2/v2.0/token \
     -H "Content-Type: application/x-www-form-urlencoded" \
     --data-urlencode "grant_type=client_credentials" \
     --data-urlencode "scope=YOUR_SERVICE_CLIENT_ID/.default" \
     --data-urlencode "client_id=YOUR_SERVICE_CLIENT_ID" \
     --data-urlencode "client_secret=YOUR_SERVICE_CLIENT_SECRET"
   ```

1. Ensure `oidc_audience` includes the expected audience value for Client
   Credentials tokens. In Entra, the `aud` claim is determined by the `scope`
   parameter in the token request. When using `YOUR_SERVICE_CLIENT_ID/.default`,
   the audience is the service client ID:

   ```mzsql
   -- Make sure to add to the array if already set
   ALTER SYSTEM SET oidc_audience = '["<CONSOLE_CLIENT_ID>","<YOUR_SERVICE_CLIENT_ID>"]';
   ```

1. Extract the `access_token` from the JSON response and use it to connect:

   ```shell
   <PGPASSWORD>="<access-token>" \
   psql -h <materialize-host> -p 6875 -U <service-account-name> materialize
   ```

   The `<service-account-name>` must match the value of the authentication
   claim in the access token.

**Generic OIDC:**

1. In your identity provider, create a new OIDC client application with the
   **Client Credentials** grant type.

1. Note the **Client ID** and **Client Secret**.

1. Fetch an access token from your IdP's token endpoint:

   ```shell
   curl -X POST https://your-idp.com/oauth2/token \
     -H "Content-Type: application/x-www-form-urlencoded" \
     --data-urlencode "grant_type=client_credentials" \
     --data-urlencode "scope=openid" \
     --data-urlencode "client_id=YOUR_SERVICE_CLIENT_ID" \
     --data-urlencode "client_secret=YOUR_SERVICE_CLIENT_SECRET"
   ```

1. Ensure `oidc_audience` includes the expected audience value for Client
   Credentials tokens. Check the `aud` claim in the token issued by your IdP
   to determine the correct value:

   ```mzsql
   -- Make sure to add to the array if already set
   ALTER SYSTEM SET oidc_audience = '["<CONSOLE_CLIENT_ID>", "<YOUR_AUDIENCE_VALUE>"]';
   ```

1. Extract the `access_token` from the JSON response and use it to connect:

   ```shell
   <PGPASSWORD>="<access-token>" \
   psql -h <materialize-host> -p 6875 -U <service-account-name> materialize
   ```

   The `<service-account-name>` must match the value of the authentication
   claim in the access token.

## De-provisioning users

When a user is removed from the identity provider, they can no longer
authenticate to Materialize because their JWT tokens will no longer be valid.
However, the corresponding Materialize role is **not automatically deleted**.
This is intentional to avoid disrupting ownership of database objects.

To remove the role after de-provisioning:

```mzsql
-- Reassign owned objects if needed
REASSIGN OWNED BY <username> TO <new-owner>;
-- Then drop the role
DROP ROLE <username>;
```

## Troubleshooting

| Symptom | Possible cause | Resolution |
|---------|---------------|------------|
| Console does not show SSO login option | `console_oidc_client_id` and `console_oidc_scopes` are not set | Set `console_oidc_client_id` to your OIDC client ID |
| SSO login redirects fail | Incorrect IdP configuration | Verify the redirect URI is set to `https://<your-console-domain>/auth/callback` and the IdP application type is set as a Single Page Application |
| SSO login redirects to login page | Materialize database is rejecting the token | Verify that the token generated by your IdP includes the required claims. |
| environmentd fails to upgrade | external_login_password_mz_system not set | Ensure the external_login_password_mz_system is configured |
| "Invalid token" error on psql connection | Wrong or expired JWT token | Obtain a fresh token; verify `oidc_issuer` matches the token's `iss` claim |
| "Audience validation failed" | Client ID not in `oidc_audience` | Add the client ID to `oidc_audience`: `ALTER SYSTEM SET oidc_audience = '["your-client-id"]'` |
| User gets wrong role name | `oidc_authentication_claim` set to wrong claim | Verify the claim name and check the JWT contents (e.g., using [jwt.io](https://jwt.io)) |
| MCP client fails during registration with the IdP (HTTP 403) | The IdP does not support anonymous Dynamic Client Registration | Pre-register an OIDC client and configure the MCP client with its client ID. See [Connecting MCP clients](#connecting-mcp-clients) |
| MCP client login fails with `invalid_scope` | The client requested the advertised `mcp.read` scope, which does not exist on the authorization server | Add an `mcp.read` scope to the authorization server, or configure the client to request only standard scopes |
| MCP client completes login but the connection is rejected | Access token `aud` is not in `oidc_audience`, or the authentication claim is missing from access tokens | See [Connecting MCP clients](#connecting-mcp-clients) |

To inspect the current OIDC configuration, login as `mz_system` and run the following SQL:

```mzsql
SHOW oidc_issuer;
SHOW oidc_audience;
SHOW oidc_authentication_claim;
SHOW console_oidc_client_id;
SHOW console_oidc_scopes;
```

## FAQ

### What happens during a blue/green deployment?

OIDC configuration (system parameters) and auto-provisioned roles are persisted
in the Materialize catalog. Blue/green deployments do not affect SSO
configuration or user roles. No additional action is required.

### What happens if I tear down my Materialize environment?

Role data and OIDC configuration are stored in the Materialize catalog, which is
persisted in your configured object storage (e.g., S3). If you delete the
Materialize instance in Kubernetes and re-apply the Materialize CR, the instance
rehydrates from the persisted catalog, recovering all roles and configuration.

If the underlying object storage is also deleted, the catalog and all role data
are lost. Use your cloud provider's disaster recovery policies to protect against this scenario.

## See also

- [Migrate to SSO](/security/self-managed/sso-migration/)
- [Authentication](/security/self-managed/authentication/)
- [Access control](/security/self-managed/access-control/)
- [Manage roles](/security/self-managed/access-control/manage-roles/)
- [System parameters configuration](/self-managed-deployments/configuration-system-parameters/)
- [Materialize CRD Field Descriptions](/installation/appendix-materialize-crd-field-descriptions/)

<!-- mz-docs page: security/self-managed/sso-migration -->

# Migrate to SSO
Migrate from password authentication to OIDC-based single sign-on (SSO) in Self-Managed Materialize.
If you have an existing Materialize deployment using Password/SASL-SCRAM authentication, you
can migrate to OIDC without losing access to existing roles and their owned
objects. The key is to configure `oidc_authentication_claim` so that the value
in the JWT matches the existing Materialize user or service account's role name.

## Step 1. Identify existing roles and choose an authentication claim

Identify the login roles in your Materialize deployment:

```mzsql
SELECT name FROM mz_roles WHERE name NOT LIKE 'mz_%' AND rolcanlogin = true;
```

Users and service accounts authenticate using ID or access tokens issued by their IdP. As the admin, you need to choose the claim in these tokens whose value matches the existing role names in Materialize. The `oidc_authentication_claim` parameter tells Materialize which JWT claim to use as the role name during OIDC authentication. For more details, see [Mapping IdP Users to Materialize Roles](/security/self-managed/sso/#mapping-idp-users-to-materialize-roles).

In most cases, this will work if your existing role names are **email
addresses** (e.g., `alice@your-org.com`), since the `email` claim in the JWT
naturally matches.

If no JWT claim maps to an existing role name, you will need to recreate the
role.

## Step 2. Configure Single sign-on (SSO)

Follow the steps in [Single sign-on (SSO)](/security/self-managed/sso/).

## Step 3. Verify the migration

After enabling OIDC, have each user sign in and verify their role name is the same as before.

## See also

- [Single sign-on (SSO)](/security/self-managed/sso/)
- [Authentication](/security/self-managed/authentication/)
- [Manage roles](/security/self-managed/access-control/manage-roles/)

