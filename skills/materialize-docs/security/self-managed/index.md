# Self-managed

Authentication and authorization in Self-Managed Materialize.



This section covers security for Self-Managed Materialize.

| Guide | Description |
|-------|-------------|
| [Authentication](/security/self-managed/authentication/) | Enable authentication |
| [Access control](/security/self-managed/access-control/) | Reference for role-based access management (RBAC) |

See also

- [Appendix: Privileges](/security/appendix/appendix-privileges/)
- [Appendix: Privileges by commands](/security/appendix/appendix-command-privileges/)
- [Appendix: Built-in roles](/security/appendix/appendix-built-in-roles/)



---

## Access control (Role-based)


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
schemas](/reference/system-catalog/).
- `SELECT` on [system catalog objects](/reference/system-catalog/).
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




---

## Authentication


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


> **Warning:** Once enabled, ensure that the `authenticatorKind` field is set for any future version upgrades or rollouts of the Materialize CR. Having it undefined will reset `authenticationKind` to `None`.

### Configuring SASL/SCRAM authentication

> **Note:** SASL/SCRAM-SHA-256 authentication requires Materialize `v26.0.0` or later.


SASL authentication requires users to log in with a password.

When SASL authentication is enabled:
- **PostgreSQL connections** (e.g., `psql`, client libraries, [connection
  poolers](/integrations/connection-pooling/)) use SCRAM-SHA-256 authentication.
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
  environmentdImageRef: materialize/environmentd:v26.12.1
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
  environmentdImageRef: materialize/environmentd:v26.12.1
  backendSecretName: materialize-backend
  authenticatorKind: Password
```

> **Warning:** Once enabled, ensure that the `authenticatorKind` field is set for any future version upgrades or rollouts of the Materialize CR. Having it undefined will reset `authenticationKind` to `None`.

## Logging in and creating users

When authentication is enabled, only the `mz_system` user is initially
available. To create additional users:

1. Login as the `mz_system` user, using the `external_login_password_mz_system`
password. ![Image of Materialize Console login screen with mz_system
user](/images/mz_system_login.png "Materialize Console login screen with
mz_system user")

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

