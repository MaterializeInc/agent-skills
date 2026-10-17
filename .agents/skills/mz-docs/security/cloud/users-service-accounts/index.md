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

## Pages in this section

- [Configure single sign-on (SSO)](/security/cloud/users-service-accounts/sso/index.md): Configure single sign-on (SSO) using SAML or Open ID Connect as an additional layer of account security.
- [Create service accounts](/security/cloud/users-service-accounts/create-service-accounts/index.md): Create a new service account (i.e., non-human user) to connect external applications and services to Materialize.
- [Invite users](/security/cloud/users-service-accounts/invite-users/index.md): How to invite new users to a Materialize organization.
- [Sync identity provider groups to database roles](/security/cloud/users-service-accounts/sync-idp-groups/index.md): Provision groups from your identity provider via SCIM and map them to Materialize database roles.
