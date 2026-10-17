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

## Pages in this section

- [Manage database roles](/security/cloud/access-control/manage-roles/index.md): Create and manage database roles and privileges in Materialize
