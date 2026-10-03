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

---

## Configure single sign-on (SSO)

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

---

## Create service accounts

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

---

## Invite users

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

---

## Sync identity provider groups to database roles

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
  connection proceeds without a `NOTICE`, since not every organization role is
  expected to have a corresponding database role.

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

