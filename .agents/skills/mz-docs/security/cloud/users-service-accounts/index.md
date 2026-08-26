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
the [Materialize Console](/console/) or via
[Terraform](/manage/terraform/).

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
- [Manage with dbt](/manage/dbt/)
- [Manage with Terraform](/manage/terraform/)

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

* [Log in to the Materialize console](/console/).

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

1. [Log in to the Materialize Console](/console/).

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
resources in your region, see the [reference documentation](/manage/terraform/).

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

1. [Log in to the Materialize Console](/console/).

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

As an **administrator** of a Materialize organization, you can configure
[SCIM](https://scim.cloud/) to sync groups from your identity provider (IdP)
into Materialize and map them to database roles.

* Groups you forward from your IdP are provisioned into your Materialize
  organization via SCIM, along with their memberships.

* When a user authenticates with Materialize, their group memberships are
  included in the authentication exchange. Materialize uses this information
  to grant and revoke their membership in existing database roles with the
  same names.

This means you can manage who belongs to which database role from your IdP.
When a team member joins, leaves, or changes teams, updating their group
membership in the IdP updates their database role memberships, with no manual
`GRANT` or `REVOKE` statements required. Roles you grant manually with `GRANT`
are outside the scope of sync and are never revoked.

> **Important:** Group sync only **assigns and unassigns role membership**. It never creates or
> drops database roles. You must create the database role yourself before a group
> takes effect.

> **Note:** Materialize has two separate permission layers, and a group can affect both:
> * **Organization roles** (*Organization Admin*, *Organization Member*) control
>   access to Materialize and organization administration. A group can be
>   assigned an organization role, and members of the group receive that
>   organization role automatically. By default, groups are assigned the
>   *Organization Member* role. Assigning *Organization Admin* to a group makes
>   its members **superusers** in Materialize.
> * **Database roles** control access to database objects via [role-based access
>   control (RBAC)](/security/cloud/access-control/). Group sync, the subject of
>   this page, grants and revokes membership in the database role matching each
>   group's name.

## Before you begin

* Your Materialize organization must have an [SSO
  connection](/security/cloud/users-service-accounts/sso/) configured for your
  identity provider. Group sync builds on SSO, so set that up first. You can
  confirm your connection under **Account** > **Account Settings** > **SSO**.

  ![SSO connections in the Materialize Console](/images/console/console-account-settings-sso.png "SSO connections in the Materialize Console")

* You must have an identity provider that supports SCIM 2.0 provisioning
  (e.g., Okta or Microsoft Entra ID).
* Only users assigned the **Organization Admin** role can manage provisioning
  and groups.
* Group-to-role sync applies on **connection**, never mid-session. Materialize
  makes a best effort to apply group changes on the user's next connection,
  but it may take several minutes for changes to be reflected.

## Step 1. Create a SCIM connection

* [Log in to the Materialize Console](/console/).

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

> **Note:** Group names that collide with a reserved Materialize role name are skipped and
> never mapped to a role. Avoid these names when choosing which groups to push.
> See [Limitations](#limitations) for the full list.

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
SCIM badge. Groups pushed from your IdP are read-only in Materialize and must
be managed from the IdP.

**Other providers:**

Configure your identity provider's SCIM provisioning to push the users and
groups that should exist in Materialize. Most providers let you scope
provisioning to specific groups, so only those groups and their members are
synced.

## Step 3. Create matching database roles

For each group that should grant access, create a database role with the
**same name** as the group and grant it the privileges the group's members
need. Members of the group get their access through membership in this role:

```mzsql
CREATE ROLE materialize_admins;
GRANT ALL PRIVILEGES ON SCHEMA production TO materialize_admins;
```

The database role must already exist before the user connects. Group sync
only assigns and unassigns membership in existing roles. It never creates
roles, so a group with no matching role is skipped during sync. Group names
must match role names exactly, including case. The roles you create act as an
allowlist for which groups take effect.

To check the mapping status of your groups, navigate to **Account** >
**Account Settings** > **Groups**. Each group indicates whether it has a
corresponding database role and will work with group mapping.

![Groups in the Materialize Console](/images/console/console-account-settings-groups.png "Groups in the Materialize Console")

## Step 4. Verify

Have a user in a synced group connect to Materialize (e.g., via the [SQL
Shell](/console/sql-shell/) or `psql`). On their first login via SSO,
Materialize auto-provisions the user's own database role (named from their
identity claim). Group sync then grants them membership in the database roles
matching their groups. The user's own role is auto-created. The group roles
must already exist.

Role memberships granted by group sync are recorded with the grantor
`mz_jwt_sync`, so you can distinguish them from manual grants:

```mzsql
SELECT r.name AS role, m.name AS member, g.name AS grantor
FROM mz_role_members rm
JOIN mz_roles r ON rm.role_id = r.id
JOIN mz_roles m ON rm.member = m.id
JOIN mz_roles g ON rm.grantor = g.id;
```

All grants and revokes performed by group sync are also recorded in
[`mz_audit_events`](/reference/system-catalog/mz_catalog/#mz_audit_events).

## How sync works

* **Sync happens at connection time.** When a user connects, Materialize
  compares their current group memberships against their sync-managed role
  memberships and applies the difference. Materialize makes a best effort to
  apply changes made in the IdP on the user's next connection, but it may take
  several minutes for changes to be reflected. Changes are never applied to a
  session that is already connected.

* **Manual grants are never touched.** Group sync only manages memberships it
  granted itself (grantor `mz_jwt_sync`). A role granted manually with `GRANT`
  is never revoked by sync, even if the user leaves the corresponding group.
  Audit manual grants periodically to avoid users retaining access through
  stale manual grants.

* **Groups without a matching role are skipped.** The connection proceeds and
  Materialize sends the client a `NOTICE` for each unmatched group.

## Limitations

* **Reserved role names are never mapped.** Groups whose names collide with
  a reserved Materialize role name are always skipped during sync, so IdP
  groups cannot grant system-level privileges. Reserved names are:

  * Any name beginning with `mz_`, `pg_`, or `external_`.
  * The `PUBLIC` role.
  * The role-specification keywords `current_user`, `current_role`,
    `session_user`, `user`, and `none`.

  Matching against reserved names is case-insensitive.
* **Roles are never created or dropped.** Group sync only assigns and
  unassigns role membership. A group only takes effect once you [create a
  database role with a matching name](#step-3-create-matching-database-roles).
* **Changes are not applied in real time.** Group membership changes are only
  applied when a user connects, never to a session that is already connected.
  Materialize makes a best effort to apply changes on the next connection, but
  it may take several minutes for a change in your identity provider to be
  reflected.

## Manage with Terraform

Instead of the Console, you can manage SCIM connections and groups with the
[Materialize Terraform provider](/manage/terraform/):

| Resource | Description |
|----------|-------------|
| [`materialize_scim_config`](https://registry.terraform.io/providers/MaterializeInc/materialize/latest/docs/resources/scim_config) | Manage SCIM provisioning connections. |
| [`materialize_scim_group`](https://registry.terraform.io/providers/MaterializeInc/materialize/latest/docs/resources/scim_group) | Create and manage groups. |
| [`materialize_scim_group_users`](https://registry.terraform.io/providers/MaterializeInc/materialize/latest/docs/resources/scim_group_users) | Manage group membership. |
| [`materialize_scim_group_roles`](https://registry.terraform.io/providers/MaterializeInc/materialize/latest/docs/resources/scim_group_roles) | Assign organization roles to groups. |

## See also

- [Access control (RBAC)](/security/cloud/access-control/)
- [Configure single sign-on (SSO)](/security/cloud/users-service-accounts/sso/)
- [Invite users](/security/cloud/users-service-accounts/invite-users/)
- [Manage with Terraform](/manage/terraform/)

