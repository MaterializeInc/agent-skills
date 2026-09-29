<!-- mz-docs page: developer-tools -->

# Developer tools

Tools for developing, deploying, and managing Materialize.

Use these tools to develop with Materialize and manage your deployments:

<div class="multilinkbox">
<div class="linkbox ">
  <div class="title">
    Deploy and manage
  </div>
  <ul>
<li><a href="/developer-tools/mz-deploy/" >mz-deploy</a></li>
<li><a href="/developer-tools/dbt/" >dbt</a></li>
<li><a href="/developer-tools/terraform/" >Terraform</a></li>
</ul>

</div>

<div class="linkbox ">
  <div class="title">
    Develop and connect
  </div>
  <ul>
<li><a href="/developer-tools/install-materialize-emulator/" >Materialize Emulator</a></li>
<li><a href="/developer-tools/console/" >Console</a></li>
</ul>

</div>

<div class="linkbox ">
  <div class="title">
    Agents and debugging
  </div>
  <ul>
<li><a href="/developer-tools/mcp-server/coding-agent-skills/" >Agent Skills</a></li>
<li><a href="/developer-tools/mcp-server/" >MCP servers</a></li>
<li><a href="/developer-tools/mz-debug/" >Troubleshoot with <code>mz-debug</code></a></li>
</ul>

</div>

</div>

<!-- mz-docs page: developer-tools/console -->

# Materialize console

Introduction to the Materialize Console, user interface for Materialize

The Materialize Console is a graphical user
interface for working with Materialize. From the Console, you can create and
manage your clusters and sources, issue SQL queries, explore your objects, and
view billing information.

![Image of the Materialize Console](/images/console/console.png
"Materialize Console")

- **Create New**: Shortcut menu to the following screens:

  - [**New cluster**](/developer-tools/console/create-new/#create-new-cluster) screens

  - [**New source**](/developer-tools/console/create-new/#create-new-source) screens

  - [**New app
    password**](/developer-tools/console/create-new/#create-new-app-password-cloud-only) screens
    (***Cloud-only***)

- [SQL Shell](/developer-tools/console/sql-shell/): Issue SQL queries.

- [Database object explorer](/developer-tools/console/data/): Explore your objects.

- [Clusters](/developer-tools/console/clusters/): Manage your Materialize clusters.

- [Integrations](/developer-tools/console/integrations/): Learn about the supported integrations.

- [Monitoring](/developer-tools/console/monitoring/): Monitor your environment as well as access your query history.

- [Admin](/developer-tools/console/admin/): Manage client credentials and billing information.
  (***Cloud-only***)

- [Connect](/developer-tools/console/connect/): View information needed to connect using service
  accounts. (***Cloud-only***)

- [User Profile](/developer-tools/console/user-profile/): Manage your user profile
  (***Cloud-only***), find links to links to the documentation, Materialize
  Community slack, and Help Center.

<!-- mz-docs page: developer-tools/console/admin -->

# Admin (Cloud-only)
Administration component of the Materialize console
The Materialize Console provides an **Admin** section where you can manage
client credentials and, for administrators, review your usage and billing
information.

The **Admin** section contains the following screens:

| Feature | Description |
|---------|-------------|
| **App Passwords** | View or delete client credentials that allow your applications and services to connect to Materialize. |
| **Billing** | Access detailed usage and billing information as well as your invoices. <br>**Available for administrators only.** |

### App Passwords

![Image of the Client Passwords](/images/console/console-passwords.png "Client passwords")

The **App Passwords** screen displays the various [client credentials
created](/developer-tools/console/create-new/#create-new-app-password-cloud-only) to allow your
applications and services to connect to Materialize.

- The [**Connect**](/developer-tools/console/connect/) button provides details needed to connect
to Materialize.

- The **trash can** button deletes the password.

See also [+Create New > App
Password](/developer-tools/console/create-new/#create-new-app-password-cloud-only) for steps to
create a new app password.

### Billing page

**Available for administrators only.**

![Image of the Billing](/images/console/console-billing.png "Usage and Billing")

<!-- mz-docs page: developer-tools/console/clusters -->

# Clusters
Manage the clusters from the Materialize console.
The Materialize Console provides a
**Clusters** section where you can manage your clusters.

![Image of Clusters page](/images/console/console-clusters.png "Clusters page
listing your clusters")

From the **Clusters** starting page, you can:

- **Alter or drop a cluster**

![Image of the menu to alter or drop the cluster](/images/console/console-clusters-menu.png "Open menu to alter or drop the cluster")

- **Select a cluster** to display cluster details:

![Image of the `quickstart` cluster details](/images/console/console-clusters-view.png "Details about the `quickstart` cluster")

<!-- mz-docs page: developer-tools/console/connect -->

# Connect (Cloud-only)
Displays details needed to connect clients to Materialize.
The **Connect** modal provides details needed to connect your [applications](/developer-tools/console/admin/) to Materialize.

![Image of the Connect modal](/images/console/console-connect-modal.png
"Materialize Connect modal")

<!-- mz-docs page: developer-tools/console/create-new -->

# Create new
Create new clusters, sources, and application passwords in the Materialize console
From the Console, you can create new [clusters](/fundamentals/concepts/clusters/ "Isolated
pools of compute resources (CPU, memory, and scratch disk space)"),
[sources](/fundamentals/concepts/sources/ "Upstream (i.e., external) systems you want
Materialize to read data from"), and, for Materialize Cloud, application passwords.

### Create new cluster

![Image of the Create New Cluster flow](/images/console/console-create-new/postgresql/create-new-cluster-flow.png "Create New Cluster flow")

From the Materialize Console:

1. Click **+ Create New** and select **Cluster** to open the **New cluster**
   screen.

1. In the **New cluster** screen,

   1. Specify the following cluster information:

      | Field | Description |
      | ----- | ----------- |
      | **Name** | A name for the cluster. | `
      | **Size** | The [size](/sql/create-cluster/#available-sizes) of the cluster. |
      | **Replica** | The [replication factor](/sql/create-cluster/#replication-factor) of the cluster. Default: `1` <br>Clusters that contain sources or sinks cannot have a replication factor greater than 1.|

   1. Click **Create cluster** to create the cluster.

1. Upon successful creation, you'll be redirected to the **Overview** page of
    the newly created cluster.

### Create new source

> **Tip:** - For PostgreSQL and MySQL, you must configure your upstream database first.
>   Refer to the [Ingest data](/ingest-data/) section for your data source.
> - For information about the snapshotting process that occurs when a new source
>   is created as well as some best practice guidelines, see [Ingest
>   data](/ingest-data/).

![Image of the Create New Source start for
PostgreSQL](/images/console/console-create-new/postgresql/create-new-source-start.png
"Create New Source start for PostgreSQL")

From the Materialize Console:

1. Click **+ Create New** and select **Source** to open the **New source**
   screen.

1. Choose the source type and follow the instructions to configure a new source.

    > **Tip:** For PostgreSQL and MySQL, you must configure your upstream database first. Refer
>     to the [Ingest data](/ingest-data/) section for your data source.

### Create new app password (Cloud-only)

![Image of the Create application
password](/images/console/console-create-new/create-app-password.png "Create
application password")

1. Click **+ Create New** and select **App Password** to open the **New app
   password** modal.

1. In the  **New app password** modal, specify the **Type** (either **Personal**
   or **Service**) and the associated details:

   > **Note:** - Only **Organization admins** can create a service account.
> - **Personal** apps are run under your user account.
> - **Service** apps are run under a Service account user. If the specified
>    Service account user does not exist, it will be automatically created the
>    **first time** the app password is used.

   **Personal:**

   For a personal app that you will run under your user account, specify the
   type and required field(s):

   | Type | Details |
   | ---- | ----------- |
   | **Type** | Select **Personal** |
   | **Name** | Specify a descriptive name. |

   **Service account:**

   For an app that you will run under a Service account, specify the
   type and required field(s):

   | Field | Details |
   | --- | --- |
   | <strong>Type</strong> | Select <strong>Service</strong> |
   | <strong>Name</strong> | Specify a descriptive name. |
   | <strong>User</strong> | Specify a service account user name. If the specified account user does not exist, it will be automatically created the <strong>first time</strong> the application connects with the user name and password. |
   | <strong>Roles</strong> | <p>Select the organization role:</p> <table>   <thead>       <tr>           <th>Organization role</th>           <th>Description</th>       </tr>   </thead>   <tbody>       <tr>           <td><strong>Organization Admin</strong></td>           <td><ul> <li> <p><strong>Console access</strong>: Has access to all Materialize console features, including administrative features (e.g., invite users, create service accounts, manage billing, and organization settings).</p> </li> <li> <p><strong>Database access</strong>: Has <red><strong>superuser</strong></red> privileges in the database.</p> </li> </ul></td>       </tr>       <tr>           <td><strong>Organization Member</strong></td>           <td><ul> <li> <p><strong>Console access</strong>: Has no access to Materialize console administrative features.</p> </li> <li> <p><strong>Database access</strong>: Inherits role-level privileges defined by the <code>PUBLIC</code> role; may also have additional privileges via grants or default privileges. See <a href="/security/cloud/access-control/#roles-and-privileges" >Access control control</a>.</p> </li> </ul></td>       </tr>   </tbody> </table> <blockquote> <p><strong>Note:</strong> - The first user for an organization is automatically assigned the <strong>Organization Admin</strong> role.</p> <ul> <li>An <a href="/security/cloud/users-service-accounts/#organization-roles" >Organization Admin</a> has <red><strong>superuser</strong></red> privileges in the database. Following the principle of least privilege, only assign <strong>Organization Admin</strong> role to those users who require superuser privileges.</li> <li>Users/service accounts can be granted additional database roles and privileges as needed.</li> </ul> </blockquote>  |

   See also [Create service
   accounts](/security/cloud/users-service-accounts/create-service-accounts/)
   for creating service accounts via Terraform.

1. Click **Create password** to generate the app password.

1. Store the new password securely.

   > **Note:** Do not reload or navigate away from the screen before storing the
>    password. This information is not displayed again.

1. **For a new service account only**.

   For a new service account, after creating the new app password, you must
   connect with the service account to complete the account creation. The first time the account connects, a database role with the same name as the
specified service account **User** is created, and the service account creation is complete.

   To connect:

   1. Find your new service account in the **App Passwords** table.

   1. Click on the **Connect** button to get details on connecting with the new
      account.

      **psql:**
If you have `psql` installed:

1. Click on the **Terminal** tab.
1. From a terminal, connect using the psql command displayed.
1. When prompted for the password, enter the app's password.

Once connected, the service account creation is complete and you can grant roles
to the new service account.

      **Other clients:**
To use a non-psql client to connect,

1. Click on the **External tools** tab to get the connection details.

1. Update the client to use these details and connect.

Once connected, the service account creation is complete and you can grant roles
to the new service account.

To view the created app accounts, go to [Admin > App
Passwords](/developer-tools/console/admin/).

<!-- mz-docs page: developer-tools/console/data -->

# Database object explorer
Explore the objects in your databases from the Materialize console.
Under **Data**, the Materialize Console
provides a database object explorer.

![Image of the Materialize Console Database Object
Explorer](/images/console/console-data-explorer.png "Materialize Console Database Object Explorer")

<span class="caption">
When you select <em>Data</em>, the left panel collapses to reveal the database
object explorer.
</span>

You can inspect the objects in your databases by navigating to the object.

|Object|Available information|
|---|---|
|Connections|<li>Details: The [`CREATE CONNECTION`](/sql/create-connection/) SQL statement.</li>|
|Indexes|<li>Details: The [`CREATE INDEX`](/sql/create-index/) SQL statement.</li><li>Workflow: Details about the index (e.g., status), freshness, upstream and downstream objects. </li><li>Visualize: Dataflow visualization.</li>|
|Materialized Views|<li>Details: The [`CREATE MATERIALIZED VIEW`](/sql/create-materialized-view/) SQL statement.</li><li>Workflow: Details about the materialized view (e.g., status), freshness, upstream and downstream objects.</li><li>Visualize: Dataflow visualization.</li>|
|Sinks|<li>Overview: View the sink metrics (e.g., messages/bytes produced) and details (e.g., Kafka topic).</li><li>Details: The [`CREATE SINK`](/sql/create-sink/) SQL statement.</li><li>Errors: Errors associated with the sink.</li><li>Workflow: Details about the sink (e.g., status), freshness, upstream and downstream objects.</li>|
|Sources|<li>Overview: View the ingestion metrics (e.g., Ingestion lag, messages/bytes received, Ingestion rate), Memory/CPU/Disk usage</li><li>Details: The [`CREATE SOURCE`](/sql/create-source/) SQL statement.</li><li>Errors: Errors associated with the source.</li><li>Subsources: List of associated subsources and their status.</li><li>Workflow: Details about the source (e.g.,status), freshness, upstream and downstream objects.</li><li>Indexes: Indexes on the source.</li>|
|Subsources|<li>Details: The `CREATE SUBSOURCE` SQL statement.</li><li>Columns: Column details.</li><li>Workflow: Details about the subsource (e.g.,status), freshness, upstream and downstream objects.</li><li>Indexes: Indexes on the subsource.</li>|
|Tables|<li>Details: The [`CREATE TABLE`](/sql/create-table/) SQL statement.</li><li>Workflow: Details about the table (e.g., status), freshness, upstream and downstream objects.</li><li>Columns: Column details.</li><li>Indexes: Indexes on the table.</li>|
|Views|<li>Details: The [`CREATE VIEW`](/sql/create-view/) SQL statement.</li><li>Columns: Column details.</li><li>Indexes: Indexes on the view. </li>|

#### Sample source overview

![Image of the Source Overview for auction_house
index](/images/console/console-data-explorer-source-overview.png "Source Overview for auction_house")

#### Sample index workflow

![Image of the Index Workflow for wins_by_item
index](/images/console/console-data-explorer-index-workflow.png "Index Workflow for wins_by_item index")

<!-- mz-docs page: developer-tools/console/integrations -->

# Integrations
Displays the various technologies supported by Materialize.
The Materialize Console provides an
**Integrations** page that lists the supported 3rd party integrations,
specifying:

- The level of support (Partner/Native/Compatible), and
- A link to the associated documentation in Materialize.

![Image of the Materialize Console Integrations page](/images/console/console-integrations.png "Materialize Console Integrations")

<!-- mz-docs page: developer-tools/console/monitoring -->

# Monitoring
Monitoring in the Materialize console
The Materialize Console provides a
**Monitoring** section where you can review the health of your environment and
access your query history.

![Image of the Environment Overview](/images/console/console-environment-overview.png "Environment overview")

The **Monitoring** section contains the following screens:

| Feature | Description |
|---------|-------------|
| **Environment Overview** | Review the health of your environment. |
| **Query History** | Access your query history. Query history is sampled. In self-managed deployments, the sample rate is configurable. See [Query History](/self-managed-deployments/query-history/). |
| **Sources** | Review your sources. You can select a source to go to its [Database object explorer page](/developer-tools/console/data/). |
| **Sinks** | Review your sinks. You can select a sink to go to its [Database object explorer page](/developer-tools/console/data/). |

<!-- mz-docs page: developer-tools/console/sql-shell -->

# SQL Shell
SQL Shell in the Materialize console
The Materialize Console provides a **SQL
Shell**, where you can issue your queries. Materialize follows the SQL standard
(SQL-92) implementation, and strives for compatibility with the PostgreSQL
dialect. If your query takes too long to complete, the SQL Shell provides
**Query Insights** listing some possible causes.

![Image of the Materialize Console SQL Shell](/images/console/console.png "Materialize Console SQL Shell")

The SQL Shell also includes:

- A top navigation panel, where you can select your cluster and database and
  schema.

- A [Quickstart](/get-started/quickstart/) tutorial. You can close the
  Quickstart by clicking the **Close Quickstart** button in the top-right
  corner.

<!-- mz-docs page: developer-tools/console/user-profile -->

# User profile
Manage your user profile and account settings from the Materialize console.
## Materialize Cloud

For Materialize Cloud, you can manage your user profile and account settings from the [Materialize
Console](/developer-tools/console/).

![Image of the user profile menu](/images/console/console-user-profile.png
"User profile menu")

## Materialize Self-Managed

For Materialize Self-Managed, you can find links to the documentation,
Materialize Community slack, and Help Center from the profile menu.

![Image of the user profile menu](/images/console/sm-console-user-profile.png
"User profile menu")

<!-- mz-docs page: developer-tools/dbt -->

# Use dbt to manage Materialize

How to use dbt and Materialize to transform streaming data in real time.

[dbt](https://docs.getdbt.com/docs/introduction) has become the standard for
data transformation ("the T in ELT"). It combines the accessibility of SQL with
software engineering best practices, allowing you to not only build reliable
data pipelines, but also document, test and version-control them.

Setting up a dbt project with Materialize is similar to setting it up with any
other database that requires a non-native adapter.

> **Note:** The `dbt-materialize` adapter can only be used with **dbt Core**. Making the
> adapter available in dbt Cloud depends on prioritization by dbt Labs. If you
> require dbt Cloud support, please [reach out to the dbt Labs team](https://www.getdbt.com/community/join-the-community/).

## Available guides

<div class="multilinkbox">
<div class="linkbox ">
  <div class="title">
    To get started
  </div>
  <a href="./get-started/" >Get started with dbt and Materialize</a>
</div>

<div class="linkbox ">
  <div class="title">
    Development guidelines
  </div>
  <a href="./development-workflows" >Development guidelines</a>
</div>

<div class="linkbox ">
  <div class="title">
    Deployment
  </div>
  <ul>
<li>
<p><a href="/developer-tools/dbt/blue-green-deployments/" >Blue-green deployment guide</a></p>
</li>
<li>
<p><a href="/developer-tools/dbt/slim-deployments/" >Slim deployment guide</a></p>
</li>
</ul>

</div>

</div>

## See also

As a tool primarily meant to manage your data model, the `dbt-materialize`
adapter does not expose all Materialize objects types. If there is a **clear
separation** between data modeling and **infrastructure management ownership**
in your team, and you want to manage objects like
[clusters](/fundamentals/concepts/clusters/), [connections](/sql/create-connection/), or
[secrets](/sql/create-secret/) as code, we recommend using the [Materialize
Terraform provider](/developer-tools/terraform/) as a complementary deployment tool.

<!-- mz-docs page: developer-tools/dbt/blue-green-deployments -->

# Blue-green deployment
How to use dbt for blue-green deployments.
> **Tip:** Once your dbt project is ready to move out of development, or as soon as you
> start managing multiple users and deployment environments, we recommend
> checking the code in to **version control** and setting up an **automated
> workflow** to control the deployment of changes.

The `dbt-materialize` adapter ships with helper macros to automate blue/green
deployments. We recommend using the blue/green pattern any time you need to
deploy changes to the definition of objects in Materialize in production
environments and **can't tolerate downtime**.

For development environments with no downtime considerations, you might prefer
to use the [slim deployment pattern](/developer-tools/dbt/slim-deployments/) instead for quicker
iteration and reduced CI costs.

## RBAC permissions requirements

When using blue/green deployments with [role-based access control (RBAC)](/security/cloud/access-control/#role-based-access-control-rbac), ensure that the role executing the deployment operations has sufficient privileges on the target objects:

* The role must have ownership privileges on the schemas being deployed
* The role must have ownership privileges on the clusters being deployed

These permissions are required because the blue/green deployment process needs to create, modify, and swap resources during the deployment lifecycle.

## Configuration and initialization

> **Warning:** If your dbt project includes [sinks](/developer-tools/dbt/get-started/#sinks), you
> **must** ensure that these are created in a **dedicated schema and cluster**.
> Unlike other objects, sinks must not be recreated in the process of a blue/green
> deployment, and must instead cut over to the new definition of their upstream
> dependencies after the environment swap.

In a blue/green deployment, you first deploy your code changes to a deployment
environment ("green") that is a clone of your production environment
("blue"), in order to validate the changes without causing unavailability.
These environments are later swapped transparently.

<br>

1. In `dbt_project.yml`, use the `deployment` variable to specify the cluster(s)
   and schema(s) that contain the changes you want to deploy. The dedicated schemas and clusters for sinks shouldn't be included in your deployment configuration.

    ```yaml
    vars:
      deployment:
        default:
          clusters:
            # To specify multiple clusters, use [<cluster1_name>, <cluster2_name>].
            - <cluster_name>
          schemas:
            # to specify multiple schemas, use [<schema1_name>, <schema2_name>].
            - <schema_name>
    ```

1. Use the [`run-operation`](https://docs.getdbt.com/reference/commands/run-operation)
   command to invoke the [`deploy_init`](https://github.com/MaterializeInc/materialize/blob/main/misc/dbt-materialize/dbt/include/materialize/macros/deploy/deploy_init.sql)
   macro:

    ```bash
    dbt run-operation deploy_init
    ```

    This macro spins up a new cluster named `<cluster_name>_dbt_deploy` and a new
    schema named `<schema_name>_dbt_deploy` using the same configuration
    as the current environment to swap with (including privileges).

    If the production cluster has an [autoscaling strategy](/sql/create-cluster/#autoscaling)
    configured, the deployment cluster inherits it, so the deployment
    environment temporarily bursts to the configured hydration size while it
    hydrates ahead of the cutover. To speed up blue/green deployments of a
    cluster without a strategy, you can configure one using the
    `alter_cluster_auto_scaling_strategy` operation before running `deploy_init`:

    ```bash
    dbt run-operation alter_cluster_auto_scaling_strategy --args '{cluster_name: <cluster_name>, auto_scaling_strategy: {on_hydration: {hydration_size: "<size>"}}}'
    ```

1. Run the dbt project containing the code changes against the new deployment
   environment.

    ```bash
    dbt run --vars 'deploy: True'
    ```

    The `deploy: True` variable instructs the adapter to append `_dbt_deploy` to
    the original schema or cluster specified for each model scoped for
    deployment, which transparently handles running that subset of models
    against the deployment environment.

    You must [exclude sources and sinks](/developer-tools/dbt/development-workflows/#exclude-sources-and-sinks) when running the dbt project.

    > If you encounter an error like `String 'deploy:' is not valid YAML`, you
>   might need to use an alternative syntax depending on your terminal environment.
>   Different terminals handle quotes differently, so try:
>   ```bash
>   dbt run --vars "{\"deploy\": true}"
>   ```
>   This alternative syntax is compatible with Windows terminals, PowerShell, or
>   PyCharm Terminal.

## Validation

[//]: # "TODO(morsapaes) Expand after we make dbt test more pliable to
deployment environments."

We **strongly** recommend validating the results of the deployed changes on the
deployment environment to ensure it's safe to [cutover](#cutover-and-cleanup).

<br>

1. After deploying the changes, the objects in the deployment cluster need to
   fully hydrate before you can safely cut over. Use the `run-operation` command
   to invoke the [`deploy_await`](https://github.com/MaterializeInc/materialize/blob/main/misc/dbt-materialize/dbt/include/materialize/macros/deploy/deploy_await.sql)
   macro, which periodically polls the cluster readiness status, and waits for all
   objects to meet a minimum lag threshold to return successfully.

    ```bash
    dbt run-operation deploy_await #--args '{poll_interval: 30, lag_threshold: "5s"}'
    ```

    By default, `deploy_await` polls for cluster readiness every **15 seconds**,
    and waits for all objects in the deployment environment to have a lag
    of **less than 1 second** before returning successfully. To override the
    default values, you can pass the following arguments to the macro:

    Argument                             | Default   | Description
    -------------------------------------|-----------|--------------------------------------------------
    `poll_interval`                      | `15s`     | The time (in seconds) between each cluster readiness check.
    `lag_threshold`                      | `1s`      | The maximum lag threshold, which determines when all objects in the environment are considered hydrated and it's safe to perform the cutover step. **We do not recommend** changing the default value, unless prompted by the Materialize team.

2. Once `deploy_await` returns successfully, you can manually run tests against
   the new deployment environment to validate the results.

## Cutover and cleanup

> **Warning:** To avoid breakages in your production environment, we recommend **carefully
> [validating](#validation)** the results of the deployed changes in the deployment
> environment before cutting over.

1. Once `deploy_await` returns successfully and you have [validated the results](#validation)
   of the deployed changes on the deployment environment, it is safe to push the
   changes to your production environment.

   Use the `run-operation` command to invoke the [`deploy_promote`](https://github.com/MaterializeInc/materialize/blob/main/misc/dbt-materialize/dbt/include/materialize/macros/deploy/deploy_promote.sql)
   macro, which (atomically) swaps the environments. To perform a dry run of the
   swap, and validate the sequence of commands that dbt will execute, you can
   pass the `dry_run: True` argument to the macro.

    ```bash
    # Do a dry run to validate the sequence of commands to execute
    dbt run-operation deploy_promote --args '{dry_run: true}'
    ```

    ```bash
    # Promote the deployment environment to production
    dbt run-operation deploy_promote #--args '{wait: true, poll_interval: 30, lag_threshold: "5s"}'
    ```

    By default, `deploy_promote` **does not** wait for all objects to be
    hydrated — we recommend carefully [validating](#validation) the results of
    the deployed changes in the deployment environment before running this
    operation, or setting `--args '{wait: true}'`. To override the default
    values, you can pass the following arguments to the macro:

    Argument                             | Default   | Description
    -------------------------------------|-----------|--------------------------------------------------
    `dry_run`                            | `false`   | Whether to print out the sequence of commands that dbt will execute without actually promoting the deployment, for validation.
    `wait`                               | `false`   | Whether to wait for all objects in the deployment environment to fully hydrate before promoting the deployment. We recommend setting this argument to `true` if you skip the [validation](#validation) step.
    `poll_interval`                      | `15s`     | When `wait` is set to `true`, the time (in seconds) between each cluster readiness check.
    `lag_threshold`                      | `1s`      | When `wait` is set to `true`, the maximum lag threshold, which determines when all objects in the environment are considered hydrated and it's safe to perform the cutover step.

    > **Note:** The `deploy_promote` operation might fail if objects are
>     concurrently modified by a different session. If this occurs, re-run the
>     operation.

    This macro ensures all deployment targets, including schemas and clusters,
    are deployed together as a **single atomic operation**, and that any sinks
    that depend on changed objects are automatically cut over to the new
    definition of their upstream dependencies. If any part of the deployment
    fails, the entire deployment is rolled back to guarantee consistency and
    prevent partial updates.

1. Use the run `run-operation` command to invoke the [`deploy_cleanup`](https://github.com/MaterializeInc/materialize/blob/main/misc/dbt-materialize/dbt/include/materialize/macros/deploy/deploy_cleanup.sql)
   macro, which (cascade) drops the `_dbt_deploy`-suffixed cluster(s) and schema(s):

    ```bash
    dbt run-operation deploy_cleanup
    ```

   > **Note:** Any **active `SUBSCRIBE` commands** attached to the swapped
>    cluster(s) **will break**. On retry, the client will automatically connect
>    to the newly deployed cluster


<!-- mz-docs page: developer-tools/dbt/development-workflows -->

# Development guidelines
How to use dbt to develop and test changes to your SQL code against Materialize.
When you're prototyping your use case and fine-tuning the underlying data model,
your priority is **iteration speed**. dbt has many features that can help speed
up development, like [node selection](#node-selection) and [model preview](#model-results-preview).
Before you start, we recommend getting familiar with how these features
work with the `dbt-materialize` adapter to make the most of your development
time.

## Node selection

By default, the `dbt-materialize` adapter drops and recreates **all** models on
each `dbt run` invocation. This can have unintended consequences, in particular
if you're managing sources and sinks as models in your dbt project. dbt allows
you to selectively run specific models and exclude specific materialization
types from each run using [node selection](https://docs.getdbt.com/reference/node-selection/syntax).

### Exclude sources and sinks

> **Note:** As you move towards productionizing your data model, we recommend managing
> sources and sinks [using Terraform](/developer-tools/terraform/) instead.

You can manually exclude specific materialization types using the
[`exclude` flag](https://docs.getdbt.com/reference/node-selection/exclude) in
your dbt run invocations. To exclude sources and sinks, use:

```bash
dbt run --exclude config.materialized:source config.materialized:sink
```

#### YAML selectors

Instead of manually specifying node selection on each run, you can create a
[YAML selector](https://docs.getdbt.com/reference/node-selection/yaml-selectors)
that makes this the default behavior when running dbt:

```yaml
# YAML selectors should be defined in a top-level file named selectors.yml
selectors:
  - name: exclude_sources_and_sinks
    description: >
      Exclude models that use source or sink materializations in the command
      invocation.
    default: true
    definition:
      union:
        # The fqn method combined with the "*" operator selects all nodes in the
        # dbt graph
        - method: fqn
          value: "*"
        - exclude:
            - 'config.materialized:source'
            - 'config.materialized:sink'
```

Because `default: true` is specified, dbt will use the selector's criteria
whenever you run an unqualified command (e.g. `dbt build`, `dbt run`). You can
still override this default by adding selection criteria to commands, or adjust
the value of `default` depending on the target environment. To learn more about
using the `default` and `exclude` properties with YAML selectors, check the
[dbt documentation](https://docs.getdbt.com/reference/node-selection/yaml-selectors).

### Run a subset of models

You can run individual models, or groups of models, using the [`select` flag](https://docs.getdbt.com/reference/node-selection/syntax#how-does-selection-work)
in your dbt run invocations:

```bash
dbt run --select "my_dbt_project_name"   # runs all models in your project
dbt run --select "my_dbt_model"          # runs a specific model
dbt run --select "my_model+"             # select my_model and all downstream dependencies
dbt run --select "path.to.my.models"     # runs all models in a specific directory
dbt run --select "my_package.some_model" # runs a specific model in a specific package
dbt run --select "tag:nightly"           # runs models with the "nightly" tag
dbt run --select "path/to/models"        # runs models contained in path/to/models
dbt run --select "path/to/my_model.sql"  # runs a specific model by its path
```

For a full rundown of selection logic options, check the [dbt documentation](https://docs.getdbt.com/reference/node-selection/syntax).

## Model results preview

> **Note:** The `dbt show` command uses a `LIMIT` clause under the hood, which has
> [known performance limitations](/serve-results/troubleshooting/#result-filtering)
> in Materialize.

To debug and preview the results of your models **without** materializing the
results, you can use the [`dbt show`](https://docs.getdbt.com/reference/commands/show)
command:

```bash
dbt show --select "model_name.sql"

23:02:20  Running with dbt=1.7.7
23:02:20  Registered adapter: materialize=1.7.3
23:02:20  Found 3 models, 1 test, 4 seeds, 1 source, 0 exposures, 0 metrics, 430 macros, 0 groups, 0 semantic models
23:02:20
23:02:23  Previewing node 'model_name':
| col                  |
| -------------------- |
| value1               |
| value2               |
| value3               |
| value4               |
| value5               |
```

By default, the `dbt show` command will return the first 5 rows from the query
result (i.e. `LIMIT 5`). You can adjust the number of rows returned using the
`--limit n` flag.

It's important to note that previewing results compiles the model and runs the
compiled SQL against Materialize; it doesn't query the already-materialized
database relation (see [`dbt-core` #7391](https://github.com/dbt-labs/dbt-core/issues/7391)).

## Unit tests

**Minimum requirements:** `dbt-materialize` v1.8.0+

> **Note:** Complex types like [`map`](/sql/types/map/) and [`list`](/sql/types/list/) are
> not supported in unit tests yet (see [`dbt-adapters` #113](https://github.com/dbt-labs/dbt-adapters/issues/113)).
> For an overview of other known limitations, check the [dbt documentation](https://docs.getdbt.com/docs/build/unit-tests#before-you-begin).

To validate your SQL logic without fully materializing a model, as well as
future-proof it against edge cases, you can use [unit tests](https://docs.getdbt.com/docs/build/unit-tests).
Unit tests can be a **quicker way to iterate on model development** in
comparison to re-running the models, since you don't need to wait for a model
to hydrate before you can validate that it produces the expected results.

1. As an example, imagine your dbt project includes the following models:

   **Filename:** _models/my_model_a.sql_
   ```mzsql
   SELECT
     1 AS a,
     1 AS id,
     2 AS not_testing,
     'a' AS string_a,
     DATE '2020-01-02' AS date_a
   ```

   **Filename:** _models/my_model_b.sql_
   ```mzsql
   SELECT
     2 as b,
     1 as id,
     2 as c,
     'b' as string_b
   ```

   **Filename:** models/my_model.sql
   ```mzsql
   SELECT
     a+b AS c,
     CONCAT(string_a, string_b) AS string_c,
     not_testing,
     date_a
   FROM {{ ref('my_model_a')}} my_model_a
   JOIN {{ ref('my_model_b' )}} my_model_b
   ON my_model_a.id = my_model_b.id
   ```

1. To add a unit test to `my_model`, create a `.yml` file under the `/models`
   directory, and use the [`unit_tests`](https://docs.getdbt.com/reference/resource-properties/unit-tests)
   property:

   **Filename:** _models/unit_tests.yml_
   ```yaml
   unit_tests:
     - name: test_my_model
       model: my_model
       given:
         - input: ref('my_model_a')
           rows:
             - {id: 1, a: 1}
         - input: ref('my_model_b')
           rows:
             - {id: 1, b: 2}
             - {id: 2, b: 2}
       expect:
         rows:
           - {c: 2}
   ```

   For simplicity, this example provides mock data using inline dictionary
   values, but other formats are supported. Check the [dbt documentation](https://docs.getdbt.com/reference/resource-properties/data-formats)
   for a full rundown of the available options.

1. Run the unit tests using `dbt test`:

    ```bash
    dbt test --select test_type:unit

    12:30:14  Running with dbt=1.8.0
    12:30:14  Registered adapter: materialize=1.8.0
    12:30:14  Found 6 models, 1 test, 4 seeds, 1 source, 471 macros, 1 unit test
    12:30:14
    12:30:16  Concurrency: 1 threads (target='dev')
    12:30:16
    12:30:16  1 of 1 START unit_test my_model::test_my_model ................................. [RUN]
    12:30:17  1 of 1 FAIL 1 my_model::test_my_model .......................................... [FAIL 1 in 1.51s]
    12:30:17
    12:30:17  Finished running 1 unit test in 0 hours 0 minutes and 2.77 seconds (2.77s).
    12:30:17
    12:30:17  Completed with 1 error and 0 warnings:
    12:30:17
    12:30:17  Failure in unit_test test_my_model (models/models/unit_tests.yml)
    12:30:17

    actual differs from expected:

    @@ ,c
    +++,3
    ---,2
    ```

    It's important to note that the **direct upstream dependencies** of the
    model that you're unit testing **must exist** in Materialize before you can
    execute the unit test via `dbt test`. To ensure these dependencies exist,
    you can use the `--empty` flag to build an empty version of the models:

    ```bash
    dbt run --select "my_model_a.sql" "my_model_b.sql" --empty
    ```

    Alternatively, you can execute unit tests as part of the `dbt build`
    command, which will ensure the upstream depdendencies are created before
    any unit tests are executed:

    ```bash
    dbt build --select "+my_model.sql"

    11:53:30  Running with dbt=1.8.0
    11:53:30  Registered adapter: materialize=1.8.0
    ...
    11:53:33  2 of 12 START sql view model public.my_model_a ................................. [RUN]
    11:53:34  2 of 12 OK created sql view model public.my_model_a ............................ [CREATE VIEW in 0.49s]
    11:53:34  3 of 12 START sql view model public.my_model_b ................................. [RUN]
    11:53:34  3 of 12 OK created sql view model public.my_model_b ............................ [CREATE VIEW in 0.45s]
    ...
    11:53:35  11 of 12 START unit_test my_model::test_my_model ............................... [RUN]
    11:53:36  11 of 12 FAIL 1 my_model::test_my_model ........................................ [FAIL 1 in 0.84s]
    11:53:36  Failure in unit_test test_my_model (models/models/unit_tests.yml)
    11:53:36

    actual differs from expected:

    @@ ,c
    +++,3
    ---,2
    ```

<!-- mz-docs page: developer-tools/dbt/get-started -->

# Get started with dbt and Materialize
How to use dbt and Materialize to transform streaming data in real time.
[dbt](https://docs.getdbt.com/docs/introduction) has become the standard for
data transformation ("the T in ELT"). It combines the accessibility of SQL with
software engineering best practices, allowing you to not only build reliable
data pipelines, but also document, test and version-control them.

In this guide, we'll cover how to use dbt and Materialize to transform streaming
data in real time — from model building to continuous testing.

## Setup

Setting up a dbt project with Materialize is similar to setting it up with any
other database that requires a non-native adapter. To get up and running, you
need to:

1. Install the [`dbt-materialize` plugin](https://pypi.org/project/dbt-materialize/)
   (optionally using a virtual environment):

   > **Note:** The `dbt-materialize` adapter can only be used with **dbt Core**. Making the
>     adapter available in dbt Cloud depends on prioritization by dbt Labs. If you
>     require dbt Cloud support, please [reach out to the dbt Labs team](https://www.getdbt.com/community/join-the-community/).

    ```bash
    python3 -m venv dbt-venv                  # create the virtual environment
    source dbt-venv/bin/activate              # activate the virtual environment
    pip install dbt-core dbt-materialize      # install dbt-core and the adapter
    ```

    The installation will include the `dbt-postgres` dependency. To check that
    the plugin was successfully installed, run:

    ```bash
    dbt --version
    ```

    `materialize` should be listed under "Plugins". If this is not the case,
    double-check that the virtual environment is activated!

1. To get started, make sure you have a Materialize account.

## Create and configure a dbt project

A [dbt project](https://docs.getdbt.com/docs/building-a-dbt-project/projects) is
a directory that contains all dbt needs to run and keep track of your
transformations. At a minimum, it must have a project file
(`dbt_project.yml`) and at least one [model](#build-and-run-dbt-models)
(`.sql`).

To create a new project, run:

```bash
dbt init <project_name>
```

This command will bootstrap a starter project with default configurations and
create a `profiles.yml` file, if it doesn't exist. To help you get started, the
`dbt init` project includes sample models to run the [Materialize quickstart](/get-started/quickstart/).

### Connect to Materialize

> **Note:** As a best practice, we strongly recommend using [service
> accounts](/security/cloud/users-service-accounts/create-service-accounts) to
> connect external applications, like dbt, to Materialize.

dbt manages all your connection configurations (or, profiles) in a file called
[`profiles.yml`](https://docs.getdbt.com/dbt-cli/configure-your-profile). By
default, this file is located under `~/.dbt/`.

1. Locate the `profiles.yml` file in your machine:

    ```bash
    dbt debug --config-dir
    ```

    **Note:** If you started from an existing project but it's your first time
      setting up dbt, it's possible that this file doesn't exist yet. You can
      manually create it in the suggested location.

1. Open `profiles.yml` and adapt it to connect to Materialize using the
   reference [profile configuration](https://docs.getdbt.com/reference/warehouse-profiles/materialize-profile#connecting-to-materialize-with-dbt-materialize).

    As an example, the following profile would allow you to connect to
    Materialize in two different environments: a developer environment
    (`dev`) and a production environment (`prod`).

    ```yaml
    default:
      outputs:

        prod:
          type: materialize
          threads: 1
          host: <host>
          port: 6875
          # Materialize user or service account (recommended)
          # to connect as
          user: <user@domain.com>
          pass: <password>
          database: materialize
          schema: public
          # optionally use the cluster connection
          # parameter to specify the default cluster
          # for the connection
          cluster: <prod_cluster>
          sslmode: require
        dev:
          type: materialize
          threads: 1
          host: <host>
          port: 6875
          user: <user@domain.com>
          pass: <password>
          database: <dev_database>
          schema: <dev_schema>
          cluster: <dev_cluster>
          sslmode: require

      target: dev
    ```

    The `target` parameter allows you to configure the [target environment](https://docs.getdbt.com/docs/guides/managing-environments#how-do-i-maintain-different-environments-with-dbt)
    that dbt will use to run your models.

1. To test the connection to Materialize, run:

    ```bash
    dbt debug
    ```

    If the output reads `All checks passed!`, you're good to go! The
    [dbt documentation](https://docs.getdbt.com/docs/guides/debugging-errors#types-of-errors)
    has some helpful pointers in case you run into errors.

## Build and run dbt models

For dbt to know how to persist (or not) a transformation, the model needs to be
associated with a [materialization](https://docs.getdbt.com/docs/building-a-dbt-project/building-models/materializations)
strategy. Because Materialize is optimized for real-time transformations of
streaming data and the core of dbt is built around batch, the `dbt-materialize`
adapter implements a few custom materialization types:

Type              | Details                                                                                                                                                         | Config options
------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------
source            | Creates a [source](/sql/create-source).                                                                                                                         | cluster, indexes
view              | Creates a [view](/sql/create-view).                                                                                                                             | indexes
materialized_view | Creates a [materialized view](/sql/create-materialized-view). The `materializedview` legacy materialization name is supported for backwards compatibility.                                                                                                  | cluster, indexes
table             | Creates a [materialized view](/sql/create-materialized-view) (actual table support pending [discussion#29633](https://github.com/MaterializeInc/materialize/discussions/29633)). | cluster, indexes
sink              | Creates a [sink](/sql/create-sink).                                                                                                                           |  cluster
ephemeral         | Executes queries using CTEs.

Create a materialization for each SQL statement you're planning to deploy. Each
individual materialization should be stored as a `.sql` file under the
directory defined by `model-paths` in `dbt_project.yml`.

### Sources

In Materialize, a [source](/sql/create-source) describes an **external** system
you want to read data from, and provides details about how to decode and
interpret that data. You can instruct dbt to create a source using the custom
`source` materialization. Once a source has been defined, it can be referenced
from another model using the dbt [`ref()`](https://docs.getdbt.com/reference/dbt-jinja-functions/ref)
or [`source()`](https://docs.getdbt.com/reference/dbt-jinja-functions/source) functions.

> **Note:** To create a source, you first need to [create a connection](/sql/create-connection)
> that specifies access and authentication parameters. Connections are **not
> exposed** in dbt, and need to exist before you run any `source` models.

**Kafka:**
Create a [Kafka source](/sql/create-source/kafka/).

**Filename:** sources/kafka_topic_a.sql
```mzsql
{{ config(materialized='source') }}

FROM KAFKA CONNECTION kafka_connection (TOPIC 'topic_a')
FORMAT AVRO USING CONFLUENT SCHEMA REGISTRY CONNECTION csr_connection
```

The source above would be compiled to:

```
database.schema.kafka_topic_a
```

**PostgreSQL:**
Create a [PostgreSQL source](/sql/create-source/postgres/).

**Filename:** sources/pg.sql
```mzsql
{{ config(materialized='source') }}

FROM POSTGRES CONNECTION pg_connection (PUBLICATION 'mz_source')
FOR ALL TABLES
```

Materialize will automatically create a **subsource** for each table in the
`mz_source` publication. Pulling subsources into the dbt context automatically
isn't supported yet. Follow the discussion in [dbt-core #6104](https://github.com/dbt-labs/dbt-core/discussions/6104#discussioncomment-3957001)
for updates!

A possible **workaround** is to define PostgreSQL sources as a [dbt source](https://docs.getdbt.com/docs/build/sources)
in a `.yml` file, nested under a `sources:` key, and list each subsource under
the `tables:` key.

```yaml
sources:
  - name: pg
    schema: "{{ target.schema }}"
    tables:
      - name: table_a
      - name: table_b
```

Once a subsource has been defined this way, it can be referenced from another
model using the dbt [`source()`](https://docs.getdbt.com/reference/dbt-jinja-functions/source)
function. To ensure that dbt is able to determine the proper order to run the
models in, you should additionally force a dependency on the parent source
model (`pg`), as described in the [dbt documentation](https://docs.getdbt.com/reference/dbt-jinja-functions/ref#forcing-dependencies).

**Filename:** staging/dep_subsources.sql
```mzsql
-- depends_on: {{ ref('pg') }}
{{ config(materialized='view') }}

SELECT
    table_a.foo AS foo,
    table_b.bar AS bar
FROM {{ source('pg','table_a') }}
INNER JOIN
     {{ source('pg','table_b') }}
    ON table_a.id = table_b.foo_id
```

The source and subsources above would be compiled to:

```
database.schema.pg
database.schema.table_a
database.schema.table_b
```

**MySQL:**
Create a [MySQL source](/sql/create-source/mysql/).

**Filename:** sources/mysql.sql
```mzsql
{{ config(materialized='source') }}

FROM MYSQL CONNECTION mysql_connection
FOR ALL TABLES;
```

Materialize will automatically create a **subsource** for each table in the
upstream database. Pulling subsources into the dbt context automatically
isn't supported yet. Follow the discussion in [dbt-core #6104](https://github.com/dbt-labs/dbt-core/discussions/6104#discussioncomment-3957001)
for updates!

A possible **workaround** is to define MySQL sources as a [dbt source](https://docs.getdbt.com/docs/build/sources)
in a `.yml` file, nested under a `sources:` key, and list each subsource under
the `tables:` key.

```yaml
sources:
  - name: mysql
    schema: "{{ target.schema }}"
    tables:
      - name: table_a
      - name: table_b
```

Once a subsource has been defined this way, it can be referenced from another
model using the dbt [`source()`](https://docs.getdbt.com/reference/dbt-jinja-functions/source)
function. To ensure that dbt is able to determine the proper order to run the
models in, you should additionally force a dependency on the parent source
model (`mysql`), as described in the [dbt documentation](https://docs.getdbt.com/reference/dbt-jinja-functions/ref#forcing-dependencies).

**Filename:** staging/dep_subsources.sql
```mzsql
-- depends_on: {{ ref('mysql') }}
{{ config(materialized='view') }}

SELECT
    table_a.foo AS foo,
    table_b.bar AS bar
FROM {{ source('mysql','table_a') }}
INNER JOIN
     {{ source('mysql','table_b') }}
    ON table_a.id = table_b.foo_id
```

The source and subsources above would be compiled to:

```
database.schema.mysql
database.schema.table_a
database.schema.table_b
```

**Webhooks:**
Create a [webhook source](/sql/create-source/webhook/).

**Filename:** sources/webhook.sql
```mzsql
{{ config(materialized='source') }}

FROM WEBHOOK
    BODY FORMAT JSON
    CHECK (
      WITH (
        HEADERS,
        BODY AS request_body,
        -- Make sure to fully qualify the secret if it isn't in the same
        -- namespace as the source!
        SECRET basic_hook_auth
      )
      constant_time_eq(headers->'authorization', basic_hook_auth)
    );
```

The source above would be compiled to:

```
database.schema.webhook
```

### Views and materialized views

In dbt, a [model](https://docs.getdbt.com/docs/building-a-dbt-project/building-models#getting-started)
is a `SELECT` statement that encapsulates a data transformation you want to run
on top of your database. When you use dbt with Materialize, **your models stay
up-to-date** without manual or configured refreshes. This allows you to
efficiently transform streaming data using the same thought process you'd use
for batch transformations against any other database.

Depending on your usage patterns, you can transform data using [`view`](#views)
or [`materialized_view`](#materialized-views) models. For guidance and best
practices on when to use views and materialized views in Materialize, see
[Indexed views vs. materialized views](/fundamentals/concepts/views/#indexed-views-vs-materialized-views).

#### Views

dbt models are materialized as [views](/sql/create-view) by default. Although
this means you can skip the `materialized` configuration in the model
definition to create views in Materialize, we recommend explicitly setting the
materialization type for maintainability.

**Filename:** models/view_a.sql
```mzsql
{{ config(materialized='view') }}

SELECT
    col_a, ...
-- Reference model dependencies using the dbt ref() function
FROM {{ ref('kafka_topic_a') }}
```

The model above will be compiled to the following SQL statement:

```mzsql
CREATE VIEW database.schema.view_a AS
SELECT
    col_a, ...
FROM database.schema.kafka_topic_a;
```

The resulting view **will not** keep results incrementally updated without an
index (see [Creating an index on a view](#creating-an-index-on-a-view)). Once a
`view` model has been defined, it can be referenced from another model using
the dbt [`ref()`](https://docs.getdbt.com/reference/dbt-jinja-functions/ref)
function.

##### Creating an index on a view

> **Tip:** For guidance and best practices on how to use indexes in Materialize, see
> [Indexes on views](/fundamentals/concepts/indexes/#indexes-on-views).

To keep results **up-to-date** in Materialize, you can create [indexes](/fundamentals/concepts/indexes/)
on view models using the [`index` configuration](#indexes). This
allows you to bypass the need for maintaining complex incremental logic or
re-running dbt to refresh your models.

**Filename:** models/view_a.sql
```mzsql
{{ config(materialized='view',
          indexes=[{'columns': ['col_a'], 'cluster': 'cluster_a'}]) }}

SELECT
    col_a, ...
FROM {{ ref('kafka_topic_a') }}
```

The model above will be compiled to the following SQL statements:

```mzsql
CREATE VIEW database.schema.view_a AS
SELECT
    col_a, ...
FROM database.schema.kafka_topic_a;

CREATE INDEX database.schema.view_a_idx IN CLUSTER cluster_a ON view_a (col_a);
```

As new data arrives, indexes keep view results **incrementally updated** in
memory within a [cluster](/fundamentals/concepts/clusters/). Indexes help optimize query
performance and make queries against views fast since the results are already calculated.

#### Materialized views

To materialize a model as a [materialized view](/fundamentals/concepts/views/#materialized-views),
set the `materialized` configuration to `materialized_view`.

**Filename:** models/materialized_view_a.sql
```mzsql
{{ config(materialized='materialized_view') }}

SELECT
    col_a, ...
-- Reference model dependencies using the dbt ref() function
FROM {{ ref('view_a') }}
```

The model above will be compiled to the following SQL statement:

```mzsql
CREATE MATERIALIZED VIEW database.schema.materialized_view_a AS
SELECT
    col_a, ...
FROM database.schema.view_a;
```

The resulting materialized view will keep results **incrementally updated** in
durable storage as new data arrives. Once a `materialized_view` model has been
defined, it can be referenced from another model using the dbt [`ref()`](https://docs.getdbt.com/reference/dbt-jinja-functions/ref)
function.

##### Creating an index on a materialized view

> **Tip:** For guidance and best practices on how to use indexes in Materialize, see
> [Indexes on materialized views](/fundamentals/concepts/views/#indexes-on-materialized-views).

With a materialized view, your models are kept **up-to-date** in Materialize as
new data arrives. This allows you to bypass the need for maintaining complex
incremental logic or re-run dbt to refresh your models.

These results are **incrementally updated** in durable storage — which makes
them available across clusters — but aren't optimized for performance. To make
results also available in memory within a [cluster](/fundamentals/concepts/clusters/), you
can create [indexes](/fundamentals/concepts/indexes/) on materialized view models using the
[`index` configuration](#indexes).

**Filename:** models/materialized_view_a.sql
```mzsql
{{ config(materialized='materialized_view')
          indexes=[{'columns': ['col_a'], 'cluster': 'cluster_b'}]) }}

SELECT
    col_a, ...
FROM {{ ref('view_a') }}
```

The model above will be compiled to the following SQL statements:

```mzsql
CREATE MATERIALIZED VIEW database.schema.materialized_view_a AS
SELECT
    col_a, ...
FROM database.schema.view_a;

CREATE INDEX database.schema.materialized_view_a_idx IN CLUSTER cluster_b ON materialized_view_a (col_a);
```

As new data arrives, results are **incrementally updated** in durable storage
and also accessible in memory within the [cluster](/fundamentals/concepts/clusters/) the
index is created in. Indexes help optimize query performance and make queries
against materialized views faster.

##### Using retain history

> **Tip:** For guidance and best practices on how to use retain history in Materialize,
> see [Retain history](/serve-results/durable-subscriptions/#set-history-retention-period).

To configure how long historical data is retained in a materialized view, use the
`retain_history` configuration. This is useful for maintaining a window of
historical data for time-based queries or for compliance requirements.

**Filename:** models/materialized_view_history.sql
```mzsql
{{ config(
    materialized='materialized_view',
    retain_history='1hr'
) }}

SELECT
    col_a,
    count(*) as count
FROM {{ ref('view_a') }}
GROUP BY col_a
```

The model above will be compiled to the following SQL statement:

```mzsql
CREATE MATERIALIZED VIEW database.schema.materialized_view_history
WITH (RETAIN HISTORY FOR '1hr')
AS
SELECT
    col_a,
    count(*) as count
FROM database.schema.view_a
GROUP BY col_a;
```

You can specify the retention period using common time units like:
- `'1hr'` for one hour
- `'1d'` for one day
- `'1w'` for one week

##### Using partition by

> **Tip:** For guidance and best practices on how to use `PARTITION BY` in Materialize,
> see [Partitioning and filter pushdown](/transform-data/patterns/partition-by/).

To declare the expected internal storage order for a materialized view, use the
`partition_by` configuration.

The `PARTITION BY` option that this compiles to is validated when the
materialized view is created, but it does not change how the data is stored.
Setting it therefore does not by itself change whether [filter
pushdown](/transform-data/patterns/partition-by/#filter-pushdown) is effective
for queries with selective filters on those columns.

**Filename:** models/materialized_view_partitioned.sql
```mzsql
{{ config(
    materialized='materialized_view',
    partition_by=['col_a']
) }}

SELECT
    col_a,
    col_b,
    col_c
FROM {{ ref('view_a') }}
```

The model above will be compiled to the following SQL statement:

```mzsql
CREATE MATERIALIZED VIEW database.schema.materialized_view_partitioned
WITH (PARTITION BY (col_a))
AS
SELECT
    col_a,
    col_b,
    col_c
FROM database.schema.view_a;
```

The listed columns must be a **prefix** of the relation's columns, and only
columns with order-preserving types are supported. See the
[`PARTITION BY` requirements](/transform-data/patterns/partition-by/#requirements)
for the full list.

### Sinks

In Materialize, a [sink](/sql/create-sink) describes an **external** system you
want to write data to, and provides details about how to encode that data. You
can instruct dbt to create a sink using the custom `sink` materialization.

**Kafka:**
Create a [Kafka sink](/sql/create-sink).

**Filename:** sinks/kafka_topic_c.sql
```mzsql
{{ config(materialized='sink') }}

FROM {{ ref('materialized_view_a') }}
INTO KAFKA CONNECTION kafka_connection (TOPIC 'topic_c')
FORMAT AVRO USING CONFLUENT SCHEMA REGISTRY CONNECTION csr_connection
ENVELOPE DEBEZIUM
```

The sink above would be compiled to:
```
database.schema.kafka_topic_c
```

### Configuration: clusters, databases and indexes {#configuration}

#### Clusters

Use the `cluster` option to specify the [cluster](/sql/create-cluster/ "pools of
compute resources (CPU, memory, and scratch disk space)") in which a
`materialized_view`, `source`, `sink` model, or `index` configuration is
created. If unspecified, the default cluster for the connection is used.

```mzsql
{{ config(materialized='materialized_view', cluster='cluster_a') }}
```

To dynamically generate the name of a cluster (e.g., based on the target
environment), you can override the `generate_cluster_name` macro with your
custom logic under the directory defined by [macro-paths](https://docs.getdbt.com/reference/project-configs/macro-paths)
in `dbt_project.yml`.

**Filename:** macros/generate_cluster_name.sql
```mzsql
{% macro generate_cluster_name(custom_cluster_name) -%}
    {%- if target.name == 'prod' -%}
        {{ custom_cluster_name }}
    {%- else -%}
        {{ target.name }}_{{ custom_cluster_name }}
    {%- endif -%}
{%- endmacro %}
```

#### Databases

Use the `database` option to specify the [database](/sql/namespaces/#database-details)
in which a `source`, `view`, `materialized_view` or `sink` is created. If
unspecified, the default database for the connection is used.

```mzsql
{{ config(materialized='materialized_view', database='database_a') }}
```

#### Indexes

Use the `indexes` configuration to define a list of [indexes](/fundamentals/concepts/indexes/) on
`source`, `view`, `table` or `materialized view` materializations. In
Materialize, [indexes](/fundamentals/concepts/indexes/) on a view maintain view results in
memory within a [cluster](/fundamentals/concepts/clusters/ "pools of compute resources (CPU,
memory, and scratch disk space)"). As the underlying data changes, indexes
**incrementally update** the view results in memory.

Each `index` configuration can have the following components:

Component                            | Value     | Description
-------------------------------------|-----------|--------------------------------------------------
`columns`                            | `list`    | One or more columns on which the index is defined. To create an index that uses _all_ columns, use the `default` component instead.
`name`                               | `string`  | The name for the index. If unspecified, Materialize will use the materialization name and column names provided.
`cluster`                            | `string`  | The cluster to use to create the index. If unspecified, indexes will be created in the cluster used to create the materialization.
`default`                            | `bool`    | Default: `False`. If set to `True`, creates a [default index](/sql/create-index/#syntax).

##### Creating a multi-column index

```mzsql
{{ config(materialized='view',
          indexes=[{'columns': ['col_a','col_b'], 'cluster': 'cluster_a'}]) }}
```

##### Creating a default index

```mzsql
{{ config(materialized='view',
    indexes=[{'default': True}]) }}
```

### Configuration: model contracts and constraints {#configuration-contracts}

#### Model contracts

**Minimum requirements:** `dbt-materialize` v1.6.0+

You can enforce [model contracts](https://docs.getdbt.com/docs/collaborate/govern/model-contracts)
for `view`, `materialized_view` and `table` materializations to guarantee that
there are no surprise breakages to your pipelines when the shape of the data
changes.

```yaml
    - name: model_with_contract
    config:
      contract:
        enforced: true
    columns:
      - name: col_with_constraints
        data_type: string
      - name: col_without_constraints
        data_type: int
```

Setting the `contract` configuration to `enforced: true` requires you to specify
a `name` and `data_type` for every column in your models. If there is a
mismatch between the defined contract and the model you're trying to run, dbt
will fail during compilation! Optionally, you can also configure column-level
[constraints](#constraints).

#### Constraints

**Minimum requirements:** `dbt-materialize` v1.6.1+

Materialize supports enforcing column-level `not_null` [constraints](https://docs.getdbt.com/reference/resource-properties/constraints)
for `materialized_view` materializations. No other constraint or materialization
types are supported.

```yaml
    - name: model_with_constraints
    config:
      contract:
        enforced: true
    columns:
      - name: col_with_constraints
        data_type: string
        constraints:
          - type: not_null
      - name: col_without_constraints
        data_type: int
```

A `not_null` constraint will be compiled to an [`ASSERT NOT NULL`](/sql/create-materialized-view/#non-null-assertions)
option for the specified columns of the materialize view.

```mzsql
CREATE MATERIALIZED VIEW model_with_constraints
WITH (
        ASSERT NOT NULL col_with_constraints
     )
AS
SELECT NULL AS col_with_constraints,
       2 AS col_without_constraints;
```

## Build and run dbt

1. [Run](https://docs.getdbt.com/reference/commands/run) the dbt models:

    ```
    dbt run
    ```

    This command generates **executable SQL code** from any model files under
    the specified directory and runs it in the target environment. You can find
    the compiled statements under `/target/run` and `target/compiled` in the
    dbt project folder.

1. Using the [SQL Shell](/developer-tools/console/), or your preferred
   SQL client connected to Materialize, double-check that all objects have been
   created:

    ```mzsql
    SHOW SOURCES [FROM database.schema];
    ```

    <p></p>

    ```nofmt
           name
    -------------------
     mysql_table_a
     mysql_table_b
     postgres_table_a
     postgres_table_b
     kafka_topic_a
    ```

    <p></p>

    ```mzsql
    SHOW VIEWS;
    ```

    <p></p>

    ```nofmt
           name
    -------------------
     view_a
    ```

    <p></p>

    ```mzsql
    SHOW MATERIALIZED VIEWS;
    ```

    <p></p>

    ```nofmt
           name
    -------------------
     materialized_view_a
    ```

That's it! From here on, Materialize makes sure that your models
are **incrementally updated** as new data streams in, and that you get **fresh
and correct results** with millisecond latency whenever you query your views.

## Test and document a dbt project

[//]: # "TODO(morsapaes) Call out the cluster configuration for tests and
store_failures_as once this page is rehashed."

### Configure continuous testing

Using dbt in a streaming context means that you're able to run data quality and
integrity [tests](https://docs.getdbt.com/docs/building-a-dbt-project/tests)
non-stop. This is useful to monitor failures as soon as they happen, and
trigger **real-time alerts** downstream.

1. To configure your project for continuous testing, add a `data_tests` property to
   `dbt_project.yml` with the `store_failures` configuration:

    ```yaml
    data_tests:
      dbt_project.name:
        models:
          +store_failures: true
          +schema: 'etl_failure'
    ```

    This will instruct dbt to create a materialized view for each configured
    test that can keep track of failures over time. By default, test views are
    created in a schema suffixed with `dbt_test__audit`. To specify a custom
    suffix, use the `schema` config.

    **Note:** As an alternative, you can specify the `--store-failures` flag
      when running `dbt test`.

1. Add tests to your models using the `data_tests` property in the model
   configuration `.yml` files:

    ```yaml
    models:
      - name: materialized_view_a
        description: 'materialized view a description'
        columns:
          - name: col_a
            description: 'column a description'
            data_tests:
              - not_null
              - unique
    ```

    The type of test and the columns being tested are used as a base for naming
    the test materialized views. For example, the configuration above would
    create views named `not_null_col_a` and `unique_col_a`.

1. Run the tests:

    ```bash
    dbt test # use --select test_type:data to only run data tests!
    ```

    When configured to `store_failures`, this command will create a materialized
    view for each test using the respective `SELECT` statements, instead of
    doing a one-off check for failures as part of its execution.

    This guarantees that your tests keep running in the background as views that
    are automatically updated as soon as an assertion fails.

1. Using the [SQL Shell](/developer-tools/console/), or your preferred
   SQL client connected to Materialize, that the schema storing the tests has been
   created, as well as the test materialized views:

    ```mzsql
    SHOW SCHEMAS;
    ```

    <p></p>

    ```nofmt
           name
    -------------------
     public
     public_etl_failure
    ```

    <p></p>

    ```mzsql
    SHOW MATERIALIZED VIEWS FROM public_etl_failure;
    ```

    <p></p>

    ```nofmt
           name
    -------------------
     not_null_col_a
     unique_col_a
    ```

With continuous testing in place, you can then build alerts off of the test
materialized views using any common PostgreSQL-compatible [client library](/serve-results/client-libraries/)
and [`SUBSCRIBE`](/sql/subscribe/)(see the [Python cheatsheet](/serve-results/client-libraries/python/#stream)
for a reference implementation).

### Generate documentation

[//]: # "TODO(morsapaes) Mention exposures and DAG costumization (e.g., colors)."

dbt can automatically generate [documentation](https://docs.getdbt.com/docs/building-a-dbt-project/documentation)
for your project as a shareable website. This brings **data governance** to your
streaming pipelines, speeding up life-saving processes like data discovery
(_where_ to find _what_ data) and lineage (the path data takes from source
(s) to sink(s), as well as the transformations that happen along the way).

If you've already created `.yml` files with helpful [properties](https://docs.getdbt.com/reference/configs-and-properties)
about your project resources (like model and column descriptions, or tests), you
are all set.

1. To generate documentation for your project, run:

    ```bash
    dbt docs generate
    ```

    dbt will grab any additional project information and Materialize catalog
    metadata, then compile it into `.json` files (`manifest.json` and
    `catalog.json`, respectively) that can be used to feed the documentation
    website. You can find the compiled files under `/target`, in the dbt
    project folder.

1. Launch the documentation website. By default, this command starts a web
   server on port 8000:

    ```bash
    dbt docs serve #--port <port>
    ```

1. In a browser, navigate to `localhost:8000`. There, you can find an overview
   of your dbt project, browse existing models and metadata, and in general keep
   track of what's going on.

    If you click **View Lineage Graph** in the lower right corner, you can even
    inspect the lineage of your streaming pipelines!

    ![dbt lineage graph](https://user-images.githubusercontent.com/23521087/138125450-cf33284f-2a33-4c1e-8bce-35f22685213d.png)

### Persist documentation

**Minimum requirements:** `dbt-materialize` v1.6.1+

To persist model- and column-level descriptions as [comments](/sql/comment-on/)
in Materialize, use the [`persist_docs`](https://docs.getdbt.com/reference/resource-configs/persist_docs)
configuration.

> **Note:** Documentation persistence is tightly coupled with `dbt run` command invocations.
> For "use-at-your-own-risk" workarounds, see [`dbt-core` #4226](https://github.com/dbt-labs/dbt-core/issues/4226). 👻

1. To enable docs persistence, add a `models` property to `dbt_project.yml` with
   the `persist-docs` configuration:

    ```yaml
    models:
      +persist_docs:
        relation: true
        columns: true
    ```

    As an alternative, you can configure `persist-docs` in the config block of your models:

    ```mzsql
    {{ config(
        materialized=materialized_view,
        persist_docs={"relation": true, "columns": true}
    ) }}
    ```

1. Once `persist-docs` is configured, any `description` defined in your `.yml`
  files is persisted to Materialize in the [mz_internal.mz_comments](/sql/system-catalog/mz_internal/#mz_comments)
  system catalog table on every `dbt run`:

    ```mzsql
      SELECT * FROM mz_internal.mz_comments;
    ```
    <p></p>

    ```nofmt

        id  |    object_type    | object_sub_id |              comment
      ------+-------------------+---------------+----------------------------------
       u622 | materialize-view  |               | materialized view a description
       u626 | materialized-view |             1 | column a description
       u626 | materialized-view |             2 | column b description
    ```

<!-- mz-docs page: developer-tools/dbt/slim-deployments -->

# Slim deployments
How to use dbt for slim deployments.
> **Tip:** Once your dbt project is ready to move out of development, or as soon as you
> start managing multiple users and deployment environments, we recommend
> checking the code in to **version control** and setting up an **automated
> workflow** to control the deployment of changes.

[//]: # "TODO(morsapaes) Consider moving demos to template repo."

On each run, dbt generates [artifacts](https://docs.getdbt.com/reference/artifacts/dbt-artifacts)
with metadata about your dbt project, including the [_manifest file_](https://docs.getdbt.com/reference/artifacts/manifest-json)
(`manifest.json`). This file contains a complete representation of the latest
state of your project, and you can use it to **avoid re-deploying resources
that didn't change** since the last run.

We recommend using the slim deployment pattern when you want to reduce
development idle time and CI costs in development environments. For
production deployments, you should prefer the [blue/green deployment pattern](/developer-tools/dbt/blue-green-deployments/).

> **Note:** Check [this demo](https://github.com/morsapaes/dbt-ci-templates) for a sample
> end-to-end workflow using GitHub and GitHub Actions.

1. Fetch the production `manifest.json` file into the CI environment:

    ```bash
          - name: Download production manifest from s3
            env:
              AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
              AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
              AWS_SESSION_TOKEN: ${{ secrets.AWS_SESSION_TOKEN }}
              AWS_REGION: us-east-1
            run: |
              aws s3 cp s3://mz-test-dbt/manifest.json ./manifest.json
    ```

1. Then, instruct dbt to run and test changed models and dependencies only:

    ```bash
          - name: Build dbt
            env:
              MZ_HOST: ${{ secrets.MZ_HOST }}
              MZ_USER: ${{ secrets.MZ_USER }}
              MZ_PASSWORD: ${{ secrets.MZ_PASSWORD }}
              CI_TAG: "${{ format('{0}_{1}', 'gh_ci', github.event.number ) }}"
            run: |
              source .venv/bin/activate
              dbt run-operation drop_environment
              dbt build --profiles-dir ./ --select state:modified+ --state ./ --target production
    ```

    In the example above, `--select state:modified+` instructs dbt to run all
    models that were modified (`state:modified`) and their downstream
    dependencies (`+`). Depending on your deployment requirements, you might
    want to use a different combination of state selectors, or go a step
    further and use the [`--defer`](https://docs.getdbt.com/reference/node-selection/defer)
    flag to reduce even more the number of models that need to be rebuilt.
    For a full rundown of the available [state modifier](https://docs.getdbt.com/reference/node-selection/methods#the-state-method)
    and [graph operator](https://docs.getdbt.com/reference/node-selection/graph-operators)
    options, check the [dbt documentation](https://docs.getdbt.com/reference/node-selection/syntax).

1. Every time you deploy to production, upload the new `manifest.json` file to
   blob storage (e.g. s3):

    ```bash
          - name: upload new manifest to s3
            env:
              AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
              AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
              AWS_SESSION_TOKEN: ${{ secrets.AWS_SESSION_TOKEN }}
              AWS_REGION: us-east-1
            run: |
              aws s3 cp ./target/manifest.json s3://mz-test-dbt
    ```

<!-- mz-docs page: developer-tools/install-materialize-emulator -->

# Download and run Materialize Emulator
The Materialize Emulator is an all-in-one Docker image available on Docker Hub, offering the fastest way to get hands-on experience with Materialize in a local environment.
The Materialize Emulator is an all-in-one Docker image available on Docker Hub
for testing and evaluation purposes. The Materialize Emulator is not
representative of Materialize's performance and full feature set.

> **Important:** The Materialize Emulator is <redb> not suitable for production workloads.</redb>.

### Materialize Emulator

Materialize Emulator is the easiest way to get started with Materialize, but is
not suitable for full feature set evaluations or production workloads.

| Materialize Emulator              | Details    |
|-----------------------------------|------------|
| **What is it**                    | A single Docker container version of Materialize. |
| **Best For**                       | Prototyping and CI jobs. |
| **Known Limitations**     | Not indicative of true Materialize performance. <br>Services are bundled in a single container. <br>No fault tolerance. <br>No data persistence. <br>No support for version upgrades. |
| **Evaluation Experience**          | Download from Docker Hub. |
| **Support**                        | [Materialize Community Slack channel](https://materialize.com/s/chat).|
| **License/legal arrangement**      | [BSL/Materialize's privacy policy](#license-and-privacy-policy) |

### Prerequisites

- Docker. If [Docker](https://www.docker.com/) is not installed, refer to its
[official documentation](https://docs.docker.com/get-docker/) to install.

### Install and run the Materialize Emulator

> **Note:** - Use of the Docker image is subject to Materialize's [BSL License](https://github.com/MaterializeInc/materialize/blob/main/LICENSE).
> - By downloading the Docker image, you are agreeing to Materialize's [privacy policy](https://materialize.com/privacy-policy/).

1. In a terminal, issue the following command to run a Docker container from the
   Materialize Emulator image. The command downloads the image, if one has not
   been already downloaded.

   ```sh
   docker run -d -p 127.0.0.1:6874:6874 -p 127.0.0.1:6875:6875 -p 127.0.0.1:6876:6876 -p 127.0.0.1:6877:6877 materialize/materialized:v26.43.0
   ```

   When running locally:

   - The Docker container binds exclusively to localhost for security reasons.
   - The [Materialize Console](/developer-tools/console/) is available on port `6874`.
   - The SQL interface is available on port `6875`.
   - Logs are available via `docker logs <container-id>`.
   - A default user `materialize` is created.
   - A default database `materialize` is created.

1. <a name="materialize-emulator-connect-client"></a>

   Open the Materialize Console in your browser at [http://localhost:6874](http://localhost:6874).

   To streamline development and troubleshooting, we recommend [setting up
   your coding agents](#setup-your-coding-agents).

   You can also connect to the Materialize Emulator using your
   preferred SQL client, using the following connection field values:

   | Field    | Value         |
   |----------|---------------|
   | Server   | `localhost`   |
   | Database | `materialize` |
   | Port     | `6875`        |
   | Username | `materialize` |

   For example, if using [`psql`](/serve-results/sql-clients/#psql):

   ```sh
   psql postgres://materialize@localhost:6875/materialize
   ```

1. Once connected, you can get started with the
   [Quickstart](/get-started/quickstart).

### Setup your coding agents

To streamline development and troubleshooting, you can set up coding agents
like [Claude Code](https://docs.anthropic.com/en/docs/claude-code),
[Codex](https://openai.com/index/codex/), and [Cursor](https://www.cursor.com/)
to work with your Materialize Emulator.

#### Install the Materialize agent skills

Materialize provides open-source [agent
skills](/developer-tools/mcp-server/coding-agent-skills/) that give your coding agent access
to Materialize documentation and reference material, so it can provide more
accurate assistance when writing queries, setting up sources, creating
materialized views, and more.

**Claude Code:**
In Claude Code, run the following commands to install the Materialize agent
skills as a plugin:

```
/plugin marketplace add MaterializeInc/agent-skills
/plugin install materialize@materialize
```

**Codex:**
In a terminal, run the following commands to install the Materialize agent
skills as a plugin:

```bash
codex plugin marketplace add MaterializeInc/agent-skills
codex plugin add materialize@materialize
```

**Other agents:**
1. If [Node.js](https://nodejs.org/) (v16 or later) is not installed, refer to
   its [official documentation](https://nodejs.org/en/download) to install.

1. In a terminal, issue the following command to install the Materialize agent
   skills:

   ```bash
   npx skills add MaterializeInc/agent-skills
   ```

For more details on the available skills, see [Agent
Skills](/developer-tools/mcp-server/coding-agent-skills/).

#### Connect to the MCP server

The Materialize Emulator includes a built-in `materialize-developer` [MCP
server](/developer-tools/mcp-server/mcp-developer/) for troubleshooting and
observability. The Emulator does not require authentication, so your MCP
client only needs the MCP server URL
`http://localhost:6876/api/mcp/developer`.

1. Configure your MCP client with the Emulator's MCP server URL. For example,
   if using [Claude Code](https://docs.anthropic.com/en/docs/claude-code):

   ```sh
   claude mcp add --transport http materialize-developer \
     http://localhost:6876/api/mcp/developer
   ```

1. Restart your MCP client to pick up the new setting. Once connected, you can
   ask questions like *Why is my materialized view stale?* or *How much memory
   is my cluster using?*

For more details, including instructions for other MCP clients, see [MCP Server
for Developers](/developer-tools/mcp-server/mcp-developer/).

### Next steps

- To start ingesting your own data from an external system like Kafka, MySQL or
  PostgreSQL, check the documentation for [sources](/sql/create-source/).

- Join the [Materialize Community on Slack](https://materialize.com/s/chat).

- To fully evaluate Materialize Cloud, sign up for a [free trial Materialize
  Cloud
  account](https://materialize.com/register/?utm_campaign=General&utm_source=documentation).
  The full experience of Materialize is also available as a self-managed
  offering. See [Self-managed Materialize](/self-managed-deployments/).

### Technical Support

For questions, discussions, or general technical support, join the [Materialize
Community on Slack](https://materialize.com/s/chat).

#### `mz-debug`

Materialize provides a [`mz-debug`]command-line debug tool called  that helps collect diagnostic information from your emulator environment. This tool can gather:
- Docker logs and resource information
- Snapshots of system catalog tables from your Materialize instance

To debug your emulator instance, you can use the following command:

```console
mz-debug emulator --docker-container-id <your-container-id>
```

This debug information can be particularly helpful when troubleshooting issues or when working with the Materialize support team.

For more detailed information about the debug tool, see the [`mz-debug` documentation](/developer-tools/mz-debug/).

### License and privacy policy

- Use of the Docker image is subject to Materialize's [BSL
  License](https://github.com/MaterializeInc/materialize/blob/main/LICENSE).

- By downloading the Docker image, you are agreeing to Materialize's
  [privacy policy](https://materialize.com/privacy-policy/).

#### Materialize Self-Managed Community Edition or the Materialize Emulator Privacy FAQ

When you use the Materialize Self-Managed Community Edition or the Materialize Emulator, we may collect the following information from the machine that runs the Materialize Self-Managed Community Edition or the Materialize Emulator software:

- The IP address of the machine running Materialize.

- If available, the cloud provider and region of the machine running
  Materialize.

- Usage data about your use of the product such as the types or quantity of
  commands you run, the number of clusters or indexes you are running, and
  similar feature usage information.

The collection of this data is subject to the [Materialize Privacy Policy](https://materialize.com/privacy-policy/).

Please note that if you visit our website or otherwise engage with us outside of
downloading the Materialize Self-Managed Community Edition or the Materialize
Emulator, we may collect additional information about you as further described
in our [Privacy Policy](https://materialize.com/privacy-policy/).

<style>
red { color: #d33902 }
redb { color: #d33902; font-weight: 500; }
</style>

<!-- mz-docs page: developer-tools/integrations -->

# Tools and integrations
Get details about third-party tools and integrations supported by Materialize

## Agent skills and MCP servers

For Materialize's open-source agent skills and built-in Model Context Protocol
(MCP) servers, see [AI & agents](/developer-tools/mcp-server/).

## SQL clients/client libraries

Materialize is **wire-compatible** with PostgreSQL and can integrate with many
SQL clients and other tools that support PostgreSQL. To help you connect to
Materialize using various clients and tools, the following references are
available:

- [SQL clients](/serve-results/sql-clients/)
- [Client Libraries](/serve-results/client-libraries/)
- [ADBC (Arrow Database Connectivity)](/serve-results/adbc/)

See also the following integration guides for BI tools:

- [Deepnote](/serve-results/bi-tools/deepnote/)
- [Excel](/serve-results/bi-tools/excel/)
- [Hex](/serve-results/bi-tools/hex/)
- [Metabase](/serve-results/bi-tools/metabase/)
- [Power BI](/serve-results/bi-tools/power-bi/)
- [Tableau](/serve-results/bi-tools/tableau/)
- [Looker](/serve-results/bi-tools/looker/)

## HTTP and WebSocket

- [Connect to Materialize via HTTP](/serve-results/http-api/)
- [Connect to Materialize via WebSocket](/serve-results/websocket-api/)

## Foreign data wrapper

- [Foreign data wrapper](/serve-results/fdw-setup/)

## Materialize Tools

- [mz-debug (Debug tool)](/developer-tools/mz-debug/)

<!-- mz-docs page: developer-tools/manage -->

# Manage Materialize
This section contains various resources for managing Materialize.

## Operational guides

| Guide | Description |
|-------|-------------|
| [Operational guidelines](/clusters/operational-guidelines/) | General operational guidelines |
| [Monitoring and alerting](/observability/) | Guides to set up monitoring and alerting |
| [Disaster Recovery](/materialize-cloud/disaster-recovery/) | Disaster recovery strategies for Materialize Cloud |

## Manage via dbt/Terraform

| Guide | Description |
|-------|-------------|
| [Using dbt to manage Materialize](/developer-tools/dbt/) | Guides for using dbt to manage Materialize |
| [Using Terraform to manage Materialize](/developer-tools/terraform/) | Guides for using Terraform to manage Materialize |
| [Using mz-deploy to manage Materialize](/developer-tools/mz-deploy/) | SQL-native CLI for zero-downtime blue/green deployments |

## Usage and billing

| Guide | Description |
|-------|-------------|
| [**Usage & billing**](/materialize-cloud/billing/) | Understand the billing model of Materialize |

<!-- mz-docs page: developer-tools/mcp-server -->

# MCP Servers and agent skills

This section contains guides for installing Materialize Agent skills and integrating with Materialize's built-in MCP servers.

## Agent skills

Materialize provides open-source [agent
skills](https://github.com/MaterializeInc/agent-skills) that give coding agents
like Claude Code, Codex, and Cursor access to Materialize documentation and
reference material. For the list of available skills and installation
instructions, see [Agent Skills](/developer-tools/mcp-server/coding-agent-skills/).

## MCP servers

Materialize provides built-in Model Context Protocol (MCP) servers that AI
agents can use. The MCP interface is served directly by the database; no sidecar
process or external server is required. These endpoints use [JSON-RPC
 2.0](https://www.jsonrpc.org/specification) over HTTP POST (default port 6876)
and support the MCP `initialize`, `tools/list`, and `tools/call` methods.

| Endpoint | Path | Description |
|----------|------|-------------|
| **Agent** | `/api/mcp/agent` | Discover and query your real-time data products over HTTP. <br>For details, see [MCP Server for agents](/developer-tools/mcp-server/mcp-agent/).<br>*Available starting in v26.24*|
| **Developer** | `/api/mcp/developer` | Read `mz_*` system catalog tables for troubleshooting and observability, and run queries on your objects. <br>For details, see [MCP Server for developer](/developer-tools/mcp-server/mcp-developer/). <br>*Available starting in v26.20*|

## See also

- [Use an ontology table](/transform-data/patterns/ontology/) to curate join
  relationships that agents query through the `query` tool before writing
  multi-table SQL.
- [MCP Server
  Troubleshooting](/developer-tools/mcp-server/mcp-server-troubleshooting/)

<!-- mz-docs page: developer-tools/mcp-server/coding-agent-skills -->

# Agent Skills
Add Materialize skills to coding agents like Claude Code, Codex, Cursor, and others.
Coding agents like [Claude
Code](https://docs.anthropic.com/en/docs/claude-code),
[Codex](https://openai.com/index/codex/), [Cursor](https://www.cursor.com/), and
others can work with Materialize using the open-source [Materialize agent
skills](https://github.com/MaterializeInc/agent-skills). These skills follow the
[Agent Skills Open Standard](https://agentskills.io/home) and work with any
coding agent that supports the standard. Once installed, these skills give your
coding agent access to Materialize documentation and reference material so it
can provide more accurate assistance when writing queries, setting up sources,
creating materialized views, and more.

## Installation

You can install the Materialize agent skills in one of two ways:

- [As a plugin](#install-as-a-plugin), if you use Claude Code or Codex. The
  plugin installs all the skills at once and can keep them updated
  automatically.
- [With `npx skills`](#install-with-npx), for any coding agent that supports
  the Agent Skills standard.

Choose one method. Installing the skills with both the plugin and `npx skills`
results in duplicate copies of each skill.

### Install as a plugin

When you install the skills as a plugin, they are namespaced under the plugin
name, for example `materialize:mz-dbt`.

If you already installed the skills with `npx skills`, remove them before you
install the plugin. The command lists both the current and the previous skill
names, and skips any you don't have. Run it in each project where you installed
them, or add `-g` if you installed them globally:

```bash
npx skills remove mz-docs mz-dbt mz-debug-freshness mz-deploy mz-health-check mz-ontology-design mz-optimize-memory mz-terraform-provider mz-terraform-self-managed materialize-docs materialize-dbt materialize-debug-freshness materialize-terraform-provider materialize-terraform-self-managed mcp-developer-analysis
```

#### Claude Code

To install the plugin, run:

```
/plugin marketplace add MaterializeInc/agent-skills
/plugin install materialize@materialize
```

Auto-update is off by default for this marketplace. To turn it on, run
`/plugin`, select **Marketplaces**, choose `materialize`, and select **Enable
auto-update**. Claude Code then checks for updates in the background and asks
you to run `/reload-plugins` when there is one.

To update by hand, run:

```
/plugin marketplace update materialize
/plugin update materialize@materialize
/reload-plugins
```

#### Codex

To install the plugin, run:

```bash
codex plugin marketplace add MaterializeInc/agent-skills
codex plugin add materialize@materialize
```

To update, run:

```bash
codex plugin marketplace upgrade materialize
```

### Install with npx

[Node.js](https://nodejs.org/) (v16 or later) must be installed to use `npx
skills`.

To install the skills, run:

```bash
npx skills add MaterializeInc/agent-skills
```

#### Upgrade skills

We publish upgrades to the Materialize agent skills weekly, so check back
regularly to pick up the latest documentation and reference material. To upgrade
the skills you already have installed:

```bash
npx skills update MaterializeInc/agent-skills
```

To upgrade every skill installed on your machine, regardless of source, omit the
repository:

```bash
npx skills update
```

#### Migrate from the previous skill names

All skills now use the `mz-` prefix: `materialize-docs` is now `mz-docs`, and
`mcp-developer-analysis` is now `mz-health-check`. If you installed the
skills before the rename, remove the old copies and install the skills again,
so each skill appears once under its new name. Run these in each project where
you installed them, or add `-g` to both commands if you installed them
globally:

```bash
npx skills remove materialize-docs materialize-dbt materialize-debug-freshness materialize-terraform-provider materialize-terraform-self-managed mcp-developer-analysis
npx skills add MaterializeInc/agent-skills
```

## Skills

| Skill | Description |
|-------|-------------|
| `mz-health-check` | Use for operational introspection and troubleshooting via the `materialize-developer` server. Covers exact catalog schemas, diagnostic workflows, remediation runbooks, and guardrails for known pitfalls (cluster-scoped queries, uint8 ID mismatches, etc.).<br><br>Examples: *"why is my materialized view stale?"*, *"what can I optimize to save costs?"*, *"is my source healthy?"* |
| `mz-debug-freshness` | Use for diagnosing why an object is behind wall-clock time, from the lag ranking down to the operator and the SQL responsible; pairs with the `materialize-developer` server. Covers reading `mz_wallclock_global_lag` as a distribution, the status sweep that catches a stalled source whose frontier still looks current, lag history, hop-by-hop attribution through `mz_materialization_lag`, hydration and replica selection before `EXPLAIN ANALYZE`, per-operator cost and worker skew, and mapping an operator back to the clause that produced it. Diagnosis only, not remediation.<br><br>Examples: *"which object is causing my freshness alert?"*, *"is this delay ingestion or compute?"*, *"why is this dataflow falling behind its input?"* |
| `mz-optimize-memory` | Use for reducing the memory footprint and cost of a compute cluster; works over SQL or the `materialize-developer` MCP server. Covers finding which objects hold the memory, choosing and sizing the fix (indexes to add or drop, `GROUP SIZE` hints, slimmer views, subquery rewrites), verifying each change by measurement on an experiment cluster, and sizing the replica afterwards.<br><br>Examples: *"why is this cluster using so much memory?"*, *"can I downsize this replica?"*, *"which of these indexes should I drop?"* |
| `mz-docs` | Use for authoring view definitions, learning concepts, and looking up patterns; useful with either MCP server. Covers comprehensive Materialize documentation, including SQL syntax, idiomatic patterns, data ingestion, concepts, and best practices (400+ reference files).<br><br>Examples: *"show me how to deduplicate a stream"*, *"what's the idiomatic top-K pattern?"*, *"how do I create a Kafka source?"* |
| `mz-dbt` | Use for managing Materialize pipelines with dbt. Covers dbt-materialize adapter usage: materializations, profile configuration, index creation, blue/green deployments, and testing.<br><br>Examples: *"write a dbt model for a materialized view"*, *"how do I do a blue/green deployment with dbt?"* |
| `mz-terraform-provider` | Use for managing Materialize resources declaratively with Terraform. Covers provider configuration for Cloud and self-managed, navigation into the provider's auto-generated resource reference, cross-resource patterns, import workflows, and gotchas.<br><br>Examples: *"create a Kafka source with Terraform"*, *"import my existing clusters into Terraform state"*, *"set up RBAC grants in Terraform"* |
| `mz-terraform-self-managed` | Use for deploying or operating self-managed Materialize infrastructure with Terraform. Covers module layout and variables for deploying on AWS, Azure, and GCP: networking, Kubernetes, backend URL formats, instance sizing, upgrades, and gotchas.<br><br>Examples: *"deploy Materialize on EKS"*, *"what instance types should Materialize nodes use?"*, *"upgrade my self-managed Materialize"* |
| `mz-deploy` | Use for managing a declarative SQL project and deploying changes to Materialize safely. Covers project layout, the compile → test → apply → stage → wait → promote lifecycle, hash-based change detection, atomic `ALTER ... SWAP` promotion, conflict detection, stable API schemas and replacement materialized views, offline type checking with `types.lock`, per-profile suffixes, variables, and file overrides, and the `EXECUTE UNIT TEST` syntax.<br><br>Examples: *"how do I deploy my sql changes safely?"*, *"what does mz-deploy stage do?"*, *"why did my promote fail with a conflict?"* |
| `mz-ontology-design` | Use for structuring and reviewing the semantic layer of a Materialize SQL code base as a canonical ontology. Covers the `raw` → `core` → use-case database layering and how to enforce it, the admission test for a public semantic object, the grain of entities, events, measurements, and relationship objects, cross-source identity and temporal semantics, reference edges versus relationship objects, the `core.public.relationships` registry, and the `COMMENT ON` documentation contract.<br><br>Examples: *"how should I organize my databases and schemas?"*, *"does this view belong in the shared layer or at the edge?"*, *"review my code base for leaked private schemas"* |

## SQL language server plugin

The `materialize` [Claude Code plugin
marketplace](https://code.claude.com/docs/en/plugin-marketplaces) also provides
the `mz-sql-lsp` plugin, which registers the
[`mz-deploy`](/developer-tools/mz-deploy/) language server for `.sql` files, so Claude
Code navigates your project instead of grepping it. See [AI agent
setup](/developer-tools/mz-deploy/agent-setup/#configuring-for-claude-code) for
installation and configuration.

## Reduce permission prompts (Claude Code)

Claude Code prompts before reading files outside your project, so it may ask
to approve reads each time the `mz-docs` skill opens a new
documentation subdirectory. To stop these prompts, grant read access to the
directory where the skill is installed in `~/.claude/settings.json`.

If you installed the skills [as a plugin](#install-as-a-plugin), grant the
plugin's cache directory. The directory below it changes with every plugin
update, so grant the parent:

```json
{
  "permissions": {
    "additionalDirectories": ["~/.claude/plugins/cache/materialize"]
  }
}
```

If you installed the skills globally [with `npx skills`](#install-with-npx),
they live under `~/.claude/skills/`. Grant the `mz-docs` skill's
directory:

```json
{
  "permissions": {
    "additionalDirectories": ["~/.claude/skills/mz-docs"]
  }
}
```

This grants access to just that one skill's directory. If you have multiple skills installed
and want to cover them all at once, you can broaden the path to
`~/.claude/skills`, though scoping to a single skill is the safer default.

Claude Code's `auto` permission mode also removes the prompts, but applies to
all tools rather than just this directory.

## Related Pages

- [MCP Server](/developer-tools/mcp-server/)
- [mz-deploy AI agent setup](/developer-tools/mz-deploy/agent-setup/)
- [GitHub: Materialize Agent Skills](https://github.com/MaterializeInc/agent-skills)

<!-- mz-docs page: developer-tools/mcp-server/mcp-agent -->

# MCP Server for Agents
Query data products via Materialize's built-in materialize-agent MCP Server.
> **Public Preview:** This feature is in public preview.

Starting in v26.24, Materialize provides a built-in `materialize-agent` Model
Context Protocol (MCP) server (`/api/mcp/agent`, port 6876) for querying data
products. The server is provided directly by Materialize; no sidecar process or
external server is required.

## Overview

The `materialize-agent` MCP server lets AI agents query business-facing data
products over HTTP. You can connect an MCP-compatible client (such as Claude
Code, Claude Cowork, or Cursor) to the MCP server and ask the agent to discover
and query your data products using either natural language or SQL:

- *SELECT * FROM mcp_product_performance LIMIT 5;*
- *What's the `total_revenue` for product 42?*
- *Perform a Pareto analysis on my products.*

## Connection methods

There are two ways to authenticate to the `materialize-agent` MCP server. Your
method determines whether you need to set up a dedicated agent query
environment:

- **OAuth**: Starting in v26.30, your MCP client can sign you in through your
  browser. The agent connects as **your user role** with your existing
  privileges. You can **skip the environment setup** and go to [Method 1:
  OAuth](#method-1-oauth). Available for **Cloud** and for **Self-Managed**
  using [SSO](/security/self-managed/sso/).

- **Token-based**: You provide Base64-encoded credentials (the MCP token) to the
  client. The agent connects as a dedicated, least-privilege **service account**
  (i.e., a separate login role acting as a service account). [Set up the agent
  query environment and data
  products](#set-up-the-agent-query-environment-and-data-products) first and
  then go to [Method 2: Token-based
  authentication](#method-2-token-based-authentication). Available for
  **Cloud**, **Self-Managed**, and the **Emulator**

## Set up the agent query environment and data products

*This setup is required only for the **token-based** connection method. If
you're using OAuth, you can skip to [Connect to the MCP
server](#connect-to-the-mcp-server).*

> **Note:** Starting in v26.27, the [`query`
> tool](/developer-tools/mcp-server/mcp-agent-tools/#query) is **enabled by default**
> and can execute arbitrary `SELECT` queries (including joins) on **all** objects
> the agent can access (including system catalog objects), not just those
> discoverable by the [`get_data_products`
> tool](/developer-tools/mcp-server/mcp-agent-tools/#get_data_products).
> To prevent agents from reading system catalog objects, set
> `restrict_to_user_objects` on each agent role.

In Materialize, querying data products (i.e., running [`SELECT`](/sql/select/))
requires:

- `SELECT` privileges on each directly referenced data product.
- `USAGE` privileges on the schemas that contain the data products.
- `USAGE` privileges on the cluster where the query runs.

To use the `materialize-agent` MCP server, we recommend:

1. Creating a dedicated query environment for agents.
1. Defining curated data products within that environment.

> **Note:** The examples below use the default `materialize` database.

### Create an agent query environment

In general, AI agents that access the `materialize-agent` MCP server should be
isolated to:

| Query environment | Granted privileges |
|---|---|
| Serving cluster dedicated to agents | `USAGE` on this cluster only |
| Schema dedicated to agents | `USAGE` on this schema only |

1. Create a dedicated cluster and schema:

   ```mzsql
   CREATE CLUSTER mcp_cluster SIZE '25cc';
   CREATE SCHEMA materialize.mcp_schema;
   ```

1. Create a functional role `mcp_agent` that can be assigned to individual
   agents:

   ```mzsql
   CREATE ROLE mcp_agent;
   ```

1. Grant privileges to the functional role:

   ```mzsql
   GRANT USAGE ON CLUSTER mcp_cluster TO mcp_agent;
   GRANT USAGE ON SCHEMA materialize.mcp_schema TO mcp_agent;
   ```

1. Set the default cluster and schema for `mcp_agent` to `mcp_cluster` and
   `mcp_schema`:

   ```mzsql
   ALTER ROLE mcp_agent SET cluster TO mcp_cluster;
   ALTER ROLE mcp_agent SET search_path TO mcp_schema;
   ```

   Later on, you will also set these role configurations on the specific agent
   roles since role configurations are **not** inherited; only privileges are
   inherited.

1. Recommended. Restrict the role to user objects only so that the [`query`
   tool](/developer-tools/mcp-server/mcp-agent-tools/#query) cannot read system
   catalog objects. You must run the following as a **superuser**:

   ```mzsql
   ALTER ROLE mcp_agent SET restrict_to_user_objects = true;
   ```

   As mentioned before, role configurations are **not** inherited; you must also
   set it on each specific agent role. Setting the parameter on the functional
   role is recommended as a precaution in case the role is ever used directly to
   run queries.

   See also [Restrict `query` tool access to user objects
   only](/developer-tools/mcp-server/mcp-agent-tools/#restrict-to-user-objects).

### Define data products and grant access

Once a dedicated agent environment is set up, create the curated data products
in the dedicated cluster and schema rather than granting access to existing
objects in other schemas; this allows you to:

- Project, mask, or filter their contents before exposing them to the agent.

- Restrict the agent's `USAGE` to the dedicated schema.

> **Tip:** - To expose an existing object (such as a table, view, or materialized view) to
>   the agent, create a view in `mcp_schema` that selects from it, then add an
>   index on that view `IN CLUSTER mcp_cluster`. If the existing object is a
>   materialized view, the index reuses the already-maintained result instead of
>   recomputing it.
> - When a view (regular view or materialized view) is indexed, the indexed
>   columns are surfaced in the tool input schema as preferred lookup keys,
>   enabling [index point-lookups](/fundamentals/concepts/indexes/#point-lookups) instead of
>   index scans.
> - Adding [comments](/sql/comment-on/) to the data product and its columns is
>   **optional but recommended**. Comments are surfaced to the agent to help it
>   better understand **when** and **how** to use the data products:
>   - Object-level comments: When a data product is indexed, if the index also has
>     a comment, the index's comment is surfaced to the agent. Otherwise, the view
>     or materialized view's comment is surfaced.
>   - Column comments: Column comments are made on the view or materialized view.
>     Indexes do not support comments on columns.

#### Define data products

The following example assumes a materialized view `sales.product_performance`
exists.

1. Create a view in the dedicated schema that selects from the existing
   materialized view:

   ```mzsql
   CREATE VIEW materialize.mcp_schema.mcp_product_performance AS
   SELECT * FROM sales.product_performance;
   ```

1. Index the view `IN CLUSTER mcp_cluster`. The indexed columns are surfaced to
   the agent as preferred lookup keys:

   ```mzsql
   CREATE INDEX mcp_product_performance_idx
   IN CLUSTER mcp_cluster
   ON materialize.mcp_schema.mcp_product_performance (product_id);
   ```

1. Optional but recommended. Add comments to the view and column(s):

   ```mzsql
   COMMENT ON VIEW materialize.mcp_schema.mcp_product_performance IS
   'Per-product performance metrics including stock status. Use this to answer
   questions about a specific product''s sales performance or inventory.';

   COMMENT ON COLUMN materialize.mcp_schema.mcp_product_performance.total_revenue IS
   'Lifetime gross revenue for this product, computed as SUM(quantity *
   unit_price) across all order_items. Returns 0 for products that have
   not been ordered yet.';

   COMMENT ON COLUMN materialize.mcp_schema.mcp_product_performance.stock_status IS
   'Derived inventory state: ''out_of_stock'' (stock_quantity = 0),
   ''low_stock'' (< 20), or ''in_stock'' (>= 20).';
   ```

   Comments are surfaced to the agent to help the agent better understand
   **when** and **how** to use the data products.

#### Grant access

1. Grant `SELECT` privilege on the data products. For each existing data
   product, grant `SELECT` to the `mcp_agent` functional role:

   ```mzsql
   GRANT SELECT ON materialize.mcp_schema.mcp_product_performance TO mcp_agent;
   ```

1. Optionally, set a [default privilege](/sql/alter-default-privileges/) to
   automatically grant `SELECT` to the `mcp_agent` functional role for future
   data products created in the `mcp_schema`:

   ```mzsql
   ALTER DEFAULT PRIVILEGES
     FOR ROLE <creator_role> -- creator of the object
     IN SCHEMA materialize.mcp_schema
     GRANT SELECT ON TABLES TO mcp_agent;
   ```

   - The `FOR ROLE <creator_role>` clause scopes the default privilege to those
     objects created by that role. Specify the role that will actually create
     your data products.

   - `TABLES` includes views and materialized views also.

   - [`ALTER DEFAULT PRIVILEGES`](/sql/alter-default-privileges/) only applies
     to objects created **after** the `ALTER DEFAULT PRIVILEGES` statement runs.
     For objects that already exist, use [`GRANT SELECT ON <object> TO
     mcp_agent`](/sql/grant-privilege/).

## Connect to the MCP server

Connect using [OAuth](#method-1-oauth) or [token-based
authentication](#method-2-token-based-authentication), as described in
[Connection methods](#connection-methods).

### Method 1: OAuth

*Available starting in v26.30*

> **Note:** The OAuth method is available for **Cloud** and for **Self-Managed** using
> [SSO](/security/self-managed/sso/).

With OAuth, the agent connects as **your user role** with your existing
privileges. It is **not** confined to a dedicated [agent query
environment](#set-up-the-agent-query-environment-and-data-products) and can read
anything your user can. You do **not** need to set up the agent query
environment to connect this way.

> **Tip:** If you have [set up the agent query environment and data
> products](#set-up-the-agent-query-environment-and-data-products), you can
> optionally grant the `mcp_agent` functional role to your user. This grants
> access to the curated data products if your user does not already have the
> necessary privileges.
> ```mzsql
> GRANT mcp_agent TO <your_user>;
> ```

To limit what the agent can reach, set
[`restrict_to_user_objects`](/developer-tools/mcp-server/mcp-agent-tools/#restrict-to-user-objects)
on your role (this excludes the system catalog only). For a confined,
least-privilege agent, use a token-based [service
account](#method-2-token-based-authentication) instead.

#### Step 1. Get your MCP server URL

To connect, the MCP-compatible client needs the `materialize-agent` MCP server
URL: `<baseURL>/api/mcp/agent`.

**Cloud:**

1. Log in to the [Materialize Console](https://console.materialize.com/).

1. Click the **Connect** link (lower-left corner) to open the **Connect** modal
   and click on the **MCP Server** tab.

1. In the **Connect your client** section, click on the **Agent** tab.

   You can find your `materialize-agent` MCP server URL
   `<baseURL>/api/mcp/agent` as part of the code block.

   If using Claude Code as your MCP-compatible client, you can copy the code
   block wholesale for the next step.

**Self-Managed:**

Self-Managed deployments using OAuth require SSO, which uses TLS. Your
identity provider may also need additional configuration for MCP clients, such
as a pre-registered OAuth client if your IdP does not support anonymous
dynamic client registration. See [Connecting MCP
clients](/security/self-managed/sso/#connecting-mcp-clients).

Get your MCP server URL from the Materialize Console:

1. Log in via the Materialize Console.

1. Click the **Connect** link (lower-left corner) to open the **Connect** modal
   and click on the **MCP Server** tab.

1. In the **Connect your client** section, click on the **Agent** tab.

   You can find your `materialize-agent` MCP server URL
   `<baseURL>/api/mcp/agent` as part of the code block.

   If using Claude Code as your MCP-compatible client, you can copy the code
   block wholesale for the next step.

#### Step 2. Configure your MCP client

In the following, replace `<baseURL>` with the MCP server URL from [Step
1](#step-1-get-your-mcp-server-url). For Cloud, the base URL has the format
`https://<region-id>.materialize.cloud`.

**Claude Code:**

1. Add the `materialize-agent` MCP server as [local-scoped
   server](https://code.claude.com/docs/en/mcp#local-scope) (i.e., the
   configurations are stored in `<CLAUDE_CONFIG_FILE>`):

   ```sh
   claude mcp add --transport http "materialize-agent" \
     "<baseURL>/api/mcp/agent"
   ```

   For Self-Managed deployments using OAuth with a pre-registered OIDC
   client, add `--client-id` and `--callback-port`:

   ```sh
   claude mcp add --transport http "materialize-agent" \
     "<baseURL>/api/mcp/agent" \
     --client-id <YOUR_CLIENT_ID> --callback-port 8080
   ```

   The `--callback-port` value must match the port in the
   `http://localhost:<port>/callback` redirect URI registered on the OIDC
   client. See [Connecting MCP
   clients](/security/self-managed/sso/#connecting-mcp-clients) for
   the full IdP configuration.

1. Restart Claude Code. On first connection, your browser opens to complete
   sign-in and connect.

1. Upon successful connection, you can [Start querying](#start-querying).

**Claude Cowork/Chrome:**

To configure Claude Cowork/Chrome, add a custom connector. The exact steps
depend on your Claude plan; for example:

- **Organization settings** → **Connectors** → **Add** → **Custom** → **Web**,
  or
- **Customize** → **Connectors** → **+** → **Add custom connector**.

Refer to the [Add a custom
connector](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp#h_3d1a65aded)
section of the [Get started with custom connectors using Remote
MCP](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp#h_3d1a65aded)
guide to get the exact steps for your plan. For the **Remote MCP server URL**
field, enter your `materialize-agent` MCP server URL.

For additional information, including network requirements and security and
privacy concerns, see the [Get started with custom connectors using Remote
MCP](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp)
article.

**Cursor:**

1. Add the `materialize-agent` MCP server entry to your local MCP settings
   file (`~/.cursor/mcp.json`).
   - When merging into an existing `mcpServers` object, remember to add commas
     between entries.
   - If the `mcpServers` field does not already exist, add it as well.

   ```json {hl_lines="3-5"}
   {
     "mcpServers": {
       "materialize-agent": {
         "url": "<baseURL>/api/mcp/agent"
       }
     }
   }
   ```

1. Restart Cursor. On first connection, your browser opens to complete sign-in
   and connect.

1. Upon successful connection, you can [Start querying](#start-querying).

### Method 2: Token-based authentication

#### Step 1. Create the specific agent role

For your specific agent, create the dedicated role with which the agent will
connect.

**Cloud:**

1. Log in to the [Materialize Console](https://console.materialize.com/).

1. Create a dedicated
   [service account](/security/cloud/users-service-accounts/create-service-accounts/)
   for your specific AI agent (only an Org admin can create service
   accounts).[^1]

   For example, to create a new `my_agent` service account:

   1. Click **+ Create New** and select **App Password** to open the **New app
      password** modal.

   1. In the **New app password** modal, specify:

      | Field      | Value        |
      | ---------- | -------------|
      | **Type**   | **Service**  |
      | **Name**   | **MCP**      |
      | **User**   | **my_agent** |
      | **Roles**  | **Organization Member** |

   1. Click **Create Password**. The **Password** and the **MCP Token** are
      created.

   1. Save the **MCP Token** in a secure place. Once you navigate away, the
      password and the MCP token will not display again. You will use the **MCP
      Token** to connect.

      ![Image of Create new service app
      flow](/images/console/console-create-new/create-app-password-mcp-token.png
      "Materialize Console Create New Service App Password Flow")

1. Ensure the corresponding database role has been created, either by:

   - Manually issuing the following commands in the SQL Shell:

     ```mzsql
     CREATE ROLE my_agent;
     ```

   - Or, connecting to Materialize (not the MCP server) using the new account.
     On first connection, Materialize automatically creates the corresponding
     database role if it does not exist.

1. Grant `mcp_agent` role to your agent:

   ```mzsql
   GRANT mcp_agent TO my_agent;
   ```

1. Set the default cluster and schema for `my_agent` to `mcp_cluster` and
   `mcp_schema`:

   ```mzsql
   ALTER ROLE my_agent SET cluster TO mcp_cluster;
   ALTER ROLE my_agent SET search_path TO mcp_schema;
   ```

   You set these role configurations on the individual roles as configurations are not inherited.

1. Recommended. Restrict the role to user objects only so that the [`query`
   tool](/developer-tools/mcp-server/mcp-agent-tools/#query) cannot read system
   catalog objects. You must run the following as a **superuser** (an
   Organization Admin):

   ```mzsql
   ALTER ROLE my_agent SET restrict_to_user_objects = true;
   ```

[^1]: Avoid using a personal app account instead of a service account as a
    personal app account would include all your roles and privileges as well.

**Self-Managed:**

1. Create a login role for your specific AI agent, replacing
   `<your_app_password>` with an actual password:

   ```mzsql
   CREATE ROLE my_agent LOGIN PASSWORD '<your_app_password>';
   ```

1. Grant `mcp_agent` role to your agent:

   ```mzsql
   GRANT mcp_agent TO my_agent;
   ```

1. Set the default cluster and schema for `my_agent` to `mcp_cluster` and
   `mcp_schema`:

   ```mzsql
   ALTER ROLE my_agent SET cluster TO mcp_cluster;
   ALTER ROLE my_agent SET search_path TO mcp_schema;
   ```

   You set these role configurations on the individual roles as configurations
   are not inherited.

1. Recommended. Restrict the role to user objects only so that the [`query`
   tool](/developer-tools/mcp-server/mcp-agent-tools/#query) cannot read system
   catalog objects. You must run the following as a **superuser**:

   ```mzsql
   ALTER ROLE my_agent SET restrict_to_user_objects = true;
   ```

**Emulator:**

1. Create a role for your specific AI agent (the Emulator does not support the
   `LOGIN PASSWORD` option):

   ```mzsql
   CREATE ROLE my_agent;
   ```

1. Grant `mcp_agent` role to your agent:

   ```mzsql
   GRANT mcp_agent TO my_agent;
   ```

1. Set the default cluster and schema for `my_agent` to `mcp_cluster` and
   `mcp_schema`:

   ```mzsql
   ALTER ROLE my_agent SET cluster TO mcp_cluster;
   ALTER ROLE my_agent SET search_path TO mcp_schema;
   ```

   You set these role configurations on the individual roles as configurations
   are not inherited.

1. Recommended. Restrict the role to user objects only so that the [`query`
   tool](/developer-tools/mcp-server/mcp-agent-tools/#query) cannot read system
   catalog objects. You must run the following as a **superuser**:

   ```mzsql
   ALTER ROLE my_agent SET restrict_to_user_objects = true;
   ```

#### Step 2. Get connection details

When connecting to the MCP server, the MCP-compatible client needs:

- The Base64-encoded `user:password` credentials (i.e., the MCP token) of your
  [agent](#step-1-create-the-specific-agent-role).

- The `materialize-agent` MCP server URL: `<baseURL>/api/mcp/agent`.

**Cloud:**

1. Log in to the Materialize Console.

1. Go to **App Passwords** and for the [service account created
   `my_agent`](#step-1-create-the-specific-agent-role), click
   **Connect**.

1. Click on the **MCP Server** tab.

1. In the **Get your MCP token** section[^1],
   - If using [`my_agent`](#step-1-create-the-specific-agent-role), use the **MCP
     Token** that was returned when you created the service account. You can
     skip to the next step.

   - Otherwise, you can:
     - [Create a different service account](#step-1-create-the-specific-agent-role) and
       use the generated MCP token; or

     - Use an existing service account, Base64 encoding the `role:password` to
       generate the MCP token. Ensure the existing account does not have more
       privileges than necessary.

1. In the **Connect your client** section, click on the **Agent** tab.

   You can find your `materialize-agent` MCP server URL
   `<baseURL>/api/mcp/agent` as part of the code block.

   If using Claude Code as your MCP-compatible client, you can copy the code
   block wholesale for the next step.

[^1]: Avoid using a personal app account instead of a service account as a
    personal app account would include all your roles and privileges as well.

**Self-Managed:**

1. Encode your agent role's credentials `<role>:<password>` in Base64 to create
   the MCP token, replacing `<your_app_password>` with the actual password:

   ```bash
   printf 'my_agent:<your_app_password>' | base64
   ```

1. Find your deployment's host name to determine your `materialize-agent` MCP
   URL:

   ```
   http://<host>:6876/api/mcp/agent
   ```

   - For your Self-Managed Materialize deployment in AWS/GCP/Azure, the `<host>`
     is the load balancer address. If [deployed via
     Terraform](/self-managed-deployments/installation/#install-using-terraform-modules),
     run the Terraform output command for your cloud provider:

     ```bash
     # AWS
     terraform output -raw nlb_dns_name

     # GCP
     terraform output -raw balancerd_load_balancer_ip

     # Azure
     terraform output -raw balancerd_load_balancer_ip
     ```

   - For local
     [kind](/self-managed-deployments/installation/install-on-local-kind/)
     clusters, use port forwarding and use `localhost` for `<host>`:

     ```bash
     kubectl port-forward svc/<instance-name>-balancerd 6876:6876 -n materialize-environment
     ```

**Emulator:**

1. Encode your agent role's credentials `<role>:<password>` in Base64 to create
   the MCP token (the Emulator does not support passwords):

   ```bash
   printf 'my_agent:' | base64
   ```

1. For the Emulator, you will use `http://localhost:6876` as the `<baseURL>`
   portion of the MCP URL:

   ```
   <baseURL>/api/mcp/agent
   ```

#### Step 3. Configure your MCP client

> **Warning:** When saving your credentials or other sensitive information in a config file, do
> **not** commit these files to version control or share them publicly.

**Claude Code:**

1. Add the `materialize-agent` MCP server as [local-scoped
   server](https://code.claude.com/docs/en/mcp#local-scope) (i.e., the
   configurations are stored in `<CLAUDE_CONFIG_FILE>`):

   ```sh
   claude mcp add --transport http "materialize-agent" \
     "<baseURL>/api/mcp/agent" \
     --header "Authorization: Basic <mcp-token>"
   ```

   Update the `<baseURL>` and `<mcp-token>` placeholders with your values:

   | Deployment   |  `<baseURL>`                                                     |  `<mcp-token>`              |
   |--------------| ------------------------------------------------------------------| -------------------------------|
   | **Cloud**        | Replace with your value | Replace with your value |
   | **Self-Managed** | Replace with your value | Replace with your value |
   | **Emulator**     | `http://localhost:6876` | Replace with your value |

1. Restart Claude Code to pick up the new setting.

**Claude Cowork:**

Claude Cowork's `claude_desktop_config.json` does not connect to a remote MCP
server directly. Use the
[`mcp-remote`](https://www.npmjs.com/package/mcp-remote) bridge, which runs
locally and forwards requests to the `materialize-agent` MCP server over HTTP.
`mcp-remote` is invoked with `npx` and requires [Node.js](https://nodejs.org/).

> **Note:** [`mcp-remote`](https://github.com/geelen/mcp-remote) is a third-party,
> community-maintained tool. It is not maintained by Anthropic or Materialize.
> Your MCP token is passed to it on each launch. The configuration below pins a
> specific version rather than pulling the latest release. Review the tool and
> update the pinned version as appropriate for your environment.

1. Add the `materialize-agent` MCP server entry to your Claude Cowork
   configuration (`claude_desktop_config.json`).
   - When merging into an existing `mcpServers` object, remember to add commas
     between entries.
   - If the `mcpServers` field does not already exist, add it as well.

   ```json {hl_lines="3-14"}
   {
     "mcpServers": {
       "materialize-agent": {
         "command": "npx",
         "args": [
           "-y", "mcp-remote@0.1.38",
           "<baseURL>/api/mcp/agent",
           "--header", "Authorization:${AUTH_HEADER}"
         ],
         "env": {
           "AUTH_HEADER": "Basic <mcp-token>"
         }
       }
     }
   }
   ```

   The `Authorization` header value is passed through the `AUTH_HEADER`
   environment variable. This avoids a known `mcp-remote` issue where a space in
   a `--header` argument (such as the space in `Basic <mcp-token>`) is
   mishandled on some platforms. The colon in `"Authorization:${AUTH_HEADER}"`
   has no trailing space.

   Update the `<baseURL>` and `<mcp-token>` placeholders with your values:

   | Deployment   |  `<baseURL>`                                                     |  `<mcp-token>`              |
   |--------------| ------------------------------------------------------------------| -------------------------------|
   | **Cloud**        | Replace with your value | Replace with your value |
   | **Self-Managed** | Replace with your value | Replace with your value |
   | **Emulator**     | `http://localhost:6876` | Replace with your value |

1. Restart Claude Cowork to pick up the new setting.

**Cursor:**

1. Add the `materialize-agent` MCP server entry to your local MCP settings
   file (`~/.cursor/mcp.json`).
   - When merging into an existing `mcpServers` object, remember to add commas
     between entries.
   - If the `mcpServers` field does not already exist, add it as well.

   ```json {hl_lines="3-8"}
   {
     "mcpServers": {
       "materialize-agent": {
         "url": "<baseURL>/api/mcp/agent",
         "headers": {
           "Authorization": "Basic <mcp-token>"
         }
       }
     }
   }
   ```

   Update the `<baseURL>` and `<mcp-token>` placeholders with your values:

   | Deployment   |  `<baseURL>`                                                     |  `<mcp-token>`              |
   |--------------| ------------------------------------------------------------------| -------------------------------|
   | **Cloud**        | Replace with your value | Replace with your value |
   | **Self-Managed** | Replace with your value | Replace with your value |
   | **Emulator**     | `http://localhost:6876` | Replace with your value |

1. Restart Cursor to pick up the new setting.

**Generic HTTP:**

Any MCP-compatible client can connect by sending JSON-RPC 2.0 requests; update
the `<baseURL>` and `<mcp-token>` placeholders with your values:

```bash
curl -X POST <baseURL>/api/mcp/agent \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic <mcp-token>" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }'
```

## Start querying

> **Warning:** By default, the [`query` tool](/developer-tools/mcp-server/mcp-agent-tools/#query)
> is **enabled**. This tool allows arbitrary `SELECT` queries (including joins) on
> **all** objects for which the agent has the appropriate privileges (`SELECT` on
> the object, `USAGE` on the object's schema).
> To disable it, set
> [`enable_mcp_agent_query_tool`](/developer-tools/mcp-server/mcp-agent-config/#enable_mcp_agent_query_tool)
> to `false`. See [Agent endpoint
> configuration](/developer-tools/mcp-server/mcp-agent-config/).

> **Tip:** Because the `query` tool can join across objects, consider maintaining an
> [ontology table](/transform-data/patterns/ontology/): a curated catalog of the
> join relationships in your schema that the agent can query to confirm exact join
> keys before writing multi-table SQL.

Once connected to the MCP server, you can query your curated data products using
either natural language or SQL:

- *Via `materialize-agent`: What data products can I query?*
- *SELECT * FROM mcp_product_performance LIMIT 5;*
- *What's the `total_revenue` for product 42?*
- *Perform a Pareto analysis on my products.*

## Related pages

- [Use an ontology table](/transform-data/patterns/ontology/)
- [`materialize-agent` MCP Server available
  tools](/developer-tools/mcp-server/mcp-agent-tools/)
- [`materialize-agent` MCP Server
  configuration](/developer-tools/mcp-server/mcp-agent-config/)
- [Agent Skills](/developer-tools/mcp-server/coding-agent-skills/)
- [CREATE INDEX](/sql/create-index)
- [COMMENT ON](/sql/comment-on)
- [CREATE ROLE](/sql/create-role)
- [GRANT PRIVILEGE](/sql/grant-privilege)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)

<!-- mz-docs page: developer-tools/mcp-server/mcp-agent-config -->

# Agent endpoint configuration
Configuration for /api/mcp/agent endpoint.
## Available configuration parameters

The following configurations are available for the `/api/mcp/agent` endpoint:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `enable_mcp_agent` | `true` | Enable or disable the `/api/mcp/agent` endpoint. When disabled, requests return `HTTP 503 (Service Unavailable)`.|
| `enable_mcp_agent_query_tool` <a name="enable_mcp_agent_query_tool"></a> | `true` | Enable or disable the [`query` tool](/developer-tools/mcp-server/mcp-agent-tools/#query), which allows for queries with joins. Enabling the `query` tool can impact performance, leak information via query
execution errors, and, by default, allow catalog-level discovery of operational
metadata through system catalog access.  To prevent catalog-level discovery of operational metadata through system catalog access, you can [restrict `query` tool access to user objects only](/developer-tools/mcp-server/mcp-agent-tools/#restrict-to-user-objects). |
| `mcp_max_response_size` | `1000000` | Maximum response size in bytes. Queries exceeding this limit return an error. |

## Disabling the endpoint

The `materialize-agent` endpoint is enabled by default. To disable it:

**Cloud:**

Contact [Materialize support](https://materialize.com/docs/support/) to
enable/disable the MCP agent endpoint for your environment.

**Self-Managed:**

Disable the endpoint using one of these methods:

**Option 1: Configuration file**

Set the parameter in your
[system parameters configuration file](/self-managed-deployments/configuration-system-parameters/):

```yaml
system_parameters:
  enable_mcp_agent: "false"
```

**Option 2: Terraform**

Set the parameter via the [Materialize Terraform module](https://github.com/MaterializeInc/materialize-terraform-self-managed):

```hcl
system_parameters = {
  enable_mcp_agent = "false"
}
```

**Option 3: SQL**

Connect as `mz_system` and run:

```mzsql
ALTER SYSTEM SET enable_mcp_agent = false;
```

> **Note:** These parameters are only accessible to the `mz_system` and `mz_support`
> roles. Regular database users cannot view or modify them.


<!-- mz-docs page: developer-tools/mcp-server/mcp-agent-tools -->

# Agent MCP server tools
Tools exposed by the `materialize-agent` MCP server.
## Tools

### `get_data_products`

Returns the list of data products discoverable by the tool. Materialized views
and indexed views are discoverable by `get_data_products`. Regular views must
have an index to be discoverable.

**Parameters:** None.

**Example response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "[\n  [\n    \"\\\"materialize\\\".\\\"mcp_schema\\\".\\\"payment_status\\\"\",\n    \"mcp_cluster\",\n    \"Given an order ID, return the current payment status.\"\n  ]\n]"
      }
    ],
    "isError": false
  }
}
```

### `get_data_product_details`

Returns the full details for a specific data product, including its JSON schema
with column names, types, and descriptions.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Exact name from the `get_data_products` list. |

**Example response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "[\n  [\n    \"\\\"materialize\\\".\\\"mcp_schema\\\".\\\"payment_status\\\"\",\n    \"mcp_cluster\",\n    \"Given an order ID, return the current payment status.\",\n    \"{\\\"order_id\\\": {\\\"type\\\": \\\"integer\\\", \\\"position\\\": 1}, \\\"status\\\": {\\\"type\\\": \\\"text\\\", \\\"position\\\": 3}}\"\n  ]\n]"
      }
    ],
    "isError": false
  }
}
```

### `read_data_product`

Reads rows from a data product.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Fully-qualified name, e.g. `"materialize"."public"."payment_status"`. |
| `limit` | integer | No | Maximum rows to return. Default: 500, max: 1000. |
| `cluster` | string | No | Cluster override. If omitted, uses the cluster from the catalog. |

**Example response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "[\n  [\n    1001,\n    42,\n    \"shipped\",\n    \"2026-03-26T10:30:00Z\"\n  ]\n]"
      }
    ],
    "isError": false
  }
}
```

### `query`

> **Warning:** Enabling the `query` tool can impact performance, leak information via query
> execution errors, and, by default, allow catalog-level discovery of operational
> metadata through system catalog access.

Allows the agent to run arbitrary `SELECT` statements (including joins) against
**any** object for which the agent has the appropriate privileges (`SELECT` on
the object, `USAGE` on the object's schema), not just the objects
discoverable by `get_data_products`. Starting in v26.27, it is enabled by
default.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `cluster` | string | Yes | Exact cluster name from the data product details. |
| `sql_query` | string | Yes | PostgreSQL-compatible `SELECT` statement. |

**Example response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "[\n  [\n    \"42\",\n    \"shipped\"\n  ]\n]"
      }
    ],
    "isError": false
  }
}
```

> **Note:** - *Recommended*. To prevent an agent from querying the system catalog objects
>   (`mz_catalog.*`, `mz_internal.*`, `pg_catalog.*`, and `information_schema.*`),
>   see [Restrict `query` tool access to user objects
>   only](#restrict-to-user-objects).
> - To disable the tool, set the [`enable_mcp_agent_query_tool`
>   configuration](/developer-tools/mcp-server/mcp-agent-config/#enable_mcp_agent_query_tool)
>   system parameter to `false`. Once disabled, you can only query data products
>   that are discoverable by [`get_data_products`](#get_data_products).

#### Restricting `query` tool access to user objects only {#restrict-to-user-objects}

When the [`query` tool](/developer-tools/mcp-server/mcp-agent-tools/#query) is
enabled, a role can, by default, query any object for which it has appropriate
privileges, including system catalog objects (`mz_catalog.*`, `mz_internal.*`,
`pg_catalog.*`, and `information_schema.*`).

To prevent an agent role from reading system catalog objects, a **superuser**
can set the `restrict_to_user_objects` parameter to `true` on both the
functional role and each individual agent role. Setting the parameter on the
functional role is recommended as a precaution in case the role is ever used
directly to run queries. Because role configuration in Materialize is not
inherited, the parameter must be set explicitly on each individual agent role:

```mzsql
ALTER ROLE mcp_agent SET restrict_to_user_objects = true;
ALTER ROLE my_agent SET restrict_to_user_objects = true;
```

This setting takes effect on the next connection. Once active:

- Queries referencing system catalog objects are rejected with a permission
  error. This includes `pg_has_role`, whose implementation depends on blocked
  system objects. Views that filter rows by the session's roles should use
  `mz_session_role_memberships()` instead. See [Fine-grained access
  control](/security/fine-grained-access-control/#resolve-the-sessions-roles).
- Data product discovery (`get_data_products`, `get_data_product_details`,
  `read_data_product`) continues to work normally.
- The restriction cannot be bypassed by the role itself; only a superuser can
  change or remove it.

To remove the restriction for an agent, a superuser can reset the parameter (or
set it to `false`):

```mzsql
ALTER ROLE my_agent RESET restrict_to_user_objects;
```

<!-- mz-docs page: developer-tools/mcp-server/mcp-developer -->

# MCP Server for Developers and Operators
Query Materialize system catalog tables for troubleshooting and observability via the built-in materialize-developer MCP server.
> **Public Preview:** This feature is in public preview.

Materialize provides a built-in `materialize-developer` Model Context Protocol
(MCP) server (`/api/mcp/developer`, port 6876) for troubleshooting and
observability. The server is provided directly by Materialize; no sidecar
process or external server is required.

## Overview

You can connect an MCP-compatible client (such as Claude Code, Claude Cowork,
or Cursor) to the MCP server to:

- Ask questions about the Materialize system
  - *Why is my materialized view stale?*
  - *How much memory is my cluster using?*
- Run queries on your objects (Available starting in v26.30)
  - *Using the quickstart cluster, SELECT * from my_mat_view;*
  - *Using the quickstart cluster, examine the memory usage of my_mat_view with skew.*

## Connect to the MCP server

There are two ways to authenticate to the `materialize-developer` MCP server:

- **OAuth**: Starting in v26.30, your MCP client can sign you in through your
  browser; no token to generate or store. Available for **Cloud** and for
  **Self-Managed** [using SSO](/security/self-managed/sso/).

- **Token-based**: You provide Base64-encoded credentials (the MCP token) to the
  client. Available for **Cloud**, **Self-Managed**, and the **Emulator**.

### Method 1: OAuth

*Available starting in v26.30*

> **Note:** The OAuth method is available for **Cloud** and for **Self-Managed** deployments
> using [SSO](/security/self-managed/sso/). For Self-Managed deployments not using
> SSO, use [Method 2: Token-based
> authentication](#method-2-token-based-authentication). For the **Emulator**, use
> [Method 3: No authentication](#method-3-no-authentication-emulator).

#### Step 1. Get your MCP server URL

To connect, the MCP-compatible client needs the `materialize-developer` MCP
server URL: `<baseURL>/api/mcp/developer`.

**Cloud:**

1. Log in to the [Materialize Console](https://console.materialize.com/).
1. Click the **Connect** link (lower-left corner) to open the **Connect** modal
   and click on the **MCP Server** tab.

1. In the **Connect your client** section, click on the **Developer** tab.

   You can find your `materialize-developer` MCP server URL
   `<baseURL>/api/mcp/developer` as part of the code block.

   If using Claude Code as your MCP-compatible client, you can copy the code
   block wholesale for the next step.

**Self-Managed:**

Self-Managed deployments using OAuth require SSO, which uses TLS. Your
identity provider may also need additional configuration for MCP clients, such
as a pre-registered OAuth client if your IdP does not support anonymous
dynamic client registration. See [Connecting MCP
clients](/security/self-managed/sso/#connecting-mcp-clients).

Get your MCP server URL from the Materialize Console:

1. Log in via the Materialize Console.
1. Click the **Connect** link (lower-left corner) to open the **Connect** modal
   and click on the **MCP Server** tab.

1. In the **Connect your client** section, click on the **Developer** tab.

   You can find your `materialize-developer` MCP server URL
   `<baseURL>/api/mcp/developer` as part of the code block.

   If using Claude Code as your MCP-compatible client, you can copy the code
   block wholesale for the next step.

#### Step 2. Configure your MCP client

Once you have your `materialize-developer` MCP server URL, you can configure
your MCP client. The `materialize-developer` MCP server URL has the form:
`<baseURL>/api/mcp/developer`.

**Claude Code:**

1. Add the `materialize-developer` MCP server as [local-scoped
   server](https://code.claude.com/docs/en/mcp#local-scope) (i.e., the
   configurations are stored in `<CLAUDE_CONFIG_FILE>`):

   ```sh
   claude mcp add --transport http materialize-developer \
     <baseURL>/api/mcp/developer
   ```

   For Self-Managed deployments using OAuth with a pre-registered OIDC
   client, add `--client-id` and `--callback-port`:

   ```sh
   claude mcp add --transport http materialize-developer \
     <baseURL>/api/mcp/developer \
     --client-id <YOUR_CLIENT_ID> --callback-port 8080
   ```

   The `--callback-port` value must match the port in the
   `http://localhost:<port>/callback` redirect URI registered on the OIDC
   client. See [Connecting MCP
   clients](/security/self-managed/sso/#connecting-mcp-clients) for
   the full IdP configuration.

   Update the `<baseURL>` placeholder with your value:

   | Deployment   |  `<baseURL>`                                                     |
   |--------------| ------------------------------------------------------------------|
   | **Cloud**        | Replace with your value |
   | **Self-Managed** | Replace with your value |

1. Restart Claude Code. On first connection, your browser opens to complete
   sign-in and connect.

1. Upon successful connection, you can [Start asking
   questions](#start-asking-questions).

**Claude Cowork/Chrome:**

To configure Claude Cowork/Chrome, add a custom connector. The exact steps
depend on your Claude plan; for example:

- **Organization settings** → **Connectors** → **Add** → **Custom** → **Web**,
  or
- **Customize** → **Connectors** → **+** → **Add custom connector**.

Refer to the [Add a custom
connector](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp#h_3d1a65aded)
section of the [Get started with custom connectors using Remote
MCP](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp#h_3d1a65aded)
guide to get the exact steps for your plan. For the **Remote MCP server URL**
field, enter your `materialize-developer` MCP server URL.

For additional information, including network requirements and security and
privacy concerns, see the [Get started with custom connectors using Remote
MCP](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp)
article.

**Cursor:**

1. Add the `materialize-developer` MCP server entry to your local MCP settings
   file (`~/.cursor/mcp.json`).
   - When merging into an existing `mcpServers` object, remember to add commas
     between entries.
   - If the `mcpServers` field does not already exist, add it as well.

   ```json {hl_lines="3-5"}
   {
     "mcpServers": {
       "materialize-developer": {
         "url": "<baseURL>/api/mcp/developer"
       }
     }
   }
   ```

   Update the `<baseURL>` placeholder with your value:

   | Deployment   |  `<baseURL>`                                                     |
   |--------------| ------------------------------------------------------------------|
   | **Cloud**        | Replace with your value |
   | **Self-Managed** | Replace with your value |

1. Restart Cursor. On first connection, your browser opens to complete sign-in
   and connect.

1. Upon successful connection, you can [Start asking
   questions](#start-asking-questions).

### Method 2: Token-based authentication

When connecting to the MCP server, the MCP-compatible client needs:

- The Base64-encoded credentials (i.e., the MCP token).

- The `materialize-developer` MCP server URL: `<baseURL>/api/mcp/developer`.

#### Step 1. Get your MCP token

**Cloud:**

The MCP token is your base64-encoded credentials. Prefer using a personal app
password over encoding your account credentials as the token is only
base64-encoded and not encrypted.

1. Log in to the [Materialize Console](https://console.materialize.com/).

1. Get your base64-encoded token for your personal app.

   - If you already have an MCP token for your personal app, copy the token.
   - If you want to create a new personal app password to use, the MCP token is
     generated when you create the new app password (**Create New** → **App
     Password**). **Copy the token** as you will use the token to connect.
     Once you navigate away, the token will not display again.

   - If using an existing personal app password, manually generate the
     base64-encoded token.

     ```bash
     printf '<user>:<app_password>' | base64 -w0
     ```

**Self-Managed:**

The MCP token is your base64-encoded credentials. Prefer using a separate role's
login credentials over encoding your own credentials as the token is only
base64-encoded and not encrypted.

1. For the MCP token, you can use either an existing or new app login role with
   password.

   - To use an existing login role with password, go to the next step.
   - To create a new login role with password:

     ```mzsql
     CREATE ROLE my_dev_agent LOGIN PASSWORD '<your_app_password>';
     ```

1. Encode your role's credentials `<role>:<password>` in Base64 to create the
   MCP token, replacing `<your_app_password>` with the actual password:

   ```bash
   printf 'my_dev_agent:<your_app_password>' | base64
   ```

**Emulator:**

The Emulator [does not require
authentication](#method-3-no-authentication-emulator). You can still pass a
role's credentials as an MCP token to run the agent's queries as that role:

1. Connect to the Emulator with a [SQL
   client](/developer-tools/install-materialize-emulator/#materialize-emulator-connect-client)
   and create the role, if it does not already exist:

   ```mzsql
   CREATE ROLE my_agent;
   ```

1. Base64-encode the role's credentials `<role>:` to create the MCP token.
   Unlike Materialize Cloud and Materialize Self-Managed, the Emulator does
   not support passwords, so the credentials do not include a password after
   the `:`:

   ```bash
   printf 'my_agent:' | base64
   ```

#### Step 2. Get your MCP server URL

To connect, the MCP-compatible client needs the `materialize-developer` MCP
server URL: `<baseURL>/api/mcp/developer`.

**Cloud:**

1. Log in to the [Materialize Console](https://console.materialize.com/).
1. Click the **Connect** link (lower-left corner) to open the **Connect** modal
   and click on the **MCP Server** tab.

1. In the **Connect your client** section, click on the **Developer** tab.

   You can find your `materialize-developer` MCP server URL
   `<baseURL>/api/mcp/developer` as part of the code block.

   If using Claude Code as your MCP-compatible client, you can copy the code
   block wholesale for the next step.

**Self-Managed:**

**Deployment using TLS:**
**If your Self-Managed deployment is using TLS**:

1. Log in via the Materialize Console.
1. Click the **Connect** link (lower-left corner) to open the **Connect** modal
   and click on the **MCP Server** tab.

1. In the **Connect your client** section, click on the **Developer** tab.

   You can find your `materialize-developer` MCP server URL
   `<baseURL>/api/mcp/developer` as part of the code block.

   If using Claude Code as your MCP-compatible client, you can copy the code
   block wholesale for the next step.

**Deployment not using TLS:**
**If your Self-Managed deployment is not using TLS**:

1. Find your deployment's host name to determine your `materialize-developer`
   MCP URL:

   - For your Self-Managed Materialize deployment in AWS/GCP/Azure, the hostname
     is the load balancer address. If [deployed via
     Terraform](/self-managed-deployments/installation/#install-using-terraform-modules),
     run the Terraform output command for your cloud provider:

     ```bash
     # AWS
     terraform output -raw nlb_dns_name

     # GCP
     terraform output -raw balancerd_load_balancer_ip

     # Azure
     terraform output -raw balancerd_load_balancer_ip
     ```

   - For local
     [kind](/self-managed-deployments/installation/install-on-local-kind/)
     clusters,
     use port forwarding and `localhost` is your hostname:

     ```bash
     kubectl port-forward svc/<instance-name>-balancerd 6876:6876 -n materialize-environment
     ```

1. Determine the value of your MCP URL using your hostname:

   ```
   http://<host>:6876/api/mcp/developer
   ```

   where `http://<host>:6876` is your base URL.

**Emulator:**

For the Emulator, your MCP URL is:

```
http://localhost:6876/api/mcp/developer
```

where `http://localhost:6876` is your base URL.

#### Step 3. Configure your MCP client

> **Warning:** When saving your credentials or other sensitive information in a config file, do
> **not** commit these files to version control or share them publicly.

**Claude Code:**

1. Add the `materialize-developer` MCP server as [local-scoped
   server](https://code.claude.com/docs/en/mcp#local-scope) (i.e., the
   configurations are stored in `<CLAUDE_CONFIG_FILE>`):

   ```sh
   claude mcp add --transport http materialize-developer \
     <baseURL>/api/mcp/developer \
     --header "Authorization: Basic <mcp-token>"
   ```

   Update the `<baseURL>` and `<mcp-token>` placeholders with your values:

   | Deployment   |  `<baseURL>`                                                     |  `<mcp-token>`              |
   |--------------| ------------------------------------------------------------------| -------------------------------|
   | **Cloud**        | Replace with your value | Replace with your value |
   | **Self-Managed** | Replace with your value | Replace with your value |
   | **Emulator**     | `http://localhost:6876` | Replace with your value |

1. Restart Claude Code to pick up the new setting.

1. Upon successful connection, you can [Start asking
   questions](#start-asking-questions).

**Claude Cowork:**

Claude Cowork's `claude_desktop_config.json` does not connect to a remote MCP
server directly. Use the
[`mcp-remote`](https://www.npmjs.com/package/mcp-remote) bridge, which runs
locally and forwards requests to the `materialize-developer` MCP server over
HTTP. `mcp-remote` is invoked with `npx` and requires
[Node.js](https://nodejs.org/).

> **Note:** [`mcp-remote`](https://github.com/geelen/mcp-remote) is a third-party,
> community-maintained tool. It is not maintained by Anthropic or Materialize.
> Your MCP token is passed to it on each launch. The configuration below pins a
> specific version rather than pulling the latest release. Review the tool and
> update the pinned version as appropriate for your environment.

1. Add the `materialize-developer` MCP server entry to your Claude Cowork
   configuration (`claude_desktop_config.json`).
   - When merging into an existing `mcpServers` object, remember to add commas
     between entries.
   - If the `mcpServers` field does not already exist, add it as well.

   ```json {hl_lines="3-14"}
   {
     "mcpServers": {
       "materialize-developer": {
         "command": "npx",
         "args": [
           "-y", "mcp-remote@0.1.38",
           "<baseURL>/api/mcp/developer",
           "--header", "Authorization:${AUTH_HEADER}"
         ],
         "env": {
           "AUTH_HEADER": "Basic <mcp-token>"
         }
       }
     }
   }
   ```

   The `Authorization` header value is passed through the `AUTH_HEADER`
   environment variable. This avoids a known `mcp-remote` issue where a space in
   a `--header` argument (such as the space in `Basic <mcp-token>`) is
   mishandled on some platforms. The colon in `"Authorization:${AUTH_HEADER}"`
   has no trailing space.

   Update the `<baseURL>` and `<mcp-token>` placeholders with your values:

   | Deployment   |  `<baseURL>`                                                     |  `<mcp-token>`              |
   |--------------| ------------------------------------------------------------------| -------------------------------|
   | **Cloud**        | Replace with your value | Replace with your value |
   | **Self-Managed** | Replace with your value | Replace with your value |
   | **Emulator**     | `http://localhost:6876` | Replace with your value |

1. Restart Claude Cowork to pick up the new setting.

1. Upon successful connection, you can [Start asking
   questions](#start-asking-questions).

**Cursor:**

1. Add the `materialize-developer` MCP server entry to your local MCP settings
   file (`~/.cursor/mcp.json`).
   - When merging into an existing `mcpServers` object, remember to add commas
     between entries.
   - If the `mcpServers` field does not already exist, add it as well.

   ```json {hl_lines="3-8"}
   {
     "mcpServers": {
       "materialize-developer": {
         "url": "<baseURL>/api/mcp/developer",
         "headers": {
           "Authorization": "Basic <mcp-token>"
         }
       }
     }
   }
   ```

   Update the `<baseURL>` and `<mcp-token>` placeholders with your values:

   | Deployment   |  `<baseURL>`                                                     |  `<mcp-token>`              |
   |--------------| ------------------------------------------------------------------| -------------------------------|
   | **Cloud**        | Replace with your value | Replace with your value |
   | **Self-Managed** | Replace with your value | Replace with your value |
   | **Emulator**     | `http://localhost:6876` | Replace with your value |

1. Restart Cursor to pick up the new setting.

1. Upon successful connection, you can [Start asking
   questions](#start-asking-questions).

**Generic HTTP:**

Any MCP-compatible client can connect by sending JSON-RPC 2.0 requests; update
the `<baseURL>` and `<mcp-token>` placeholders with your values:

```bash
curl -X POST <baseURL>/api/mcp/developer \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic <mcp-token>" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }'
```

### Method 3: No authentication (Emulator)

The [Materialize Emulator](/developer-tools/install-materialize-emulator/) does not
require authentication. Your MCP client only needs the `materialize-developer`
MCP server URL:

```
http://localhost:6876/api/mcp/developer
```

**Claude Code:**

1. Add the `materialize-developer` MCP server as [local-scoped
   server](https://code.claude.com/docs/en/mcp#local-scope) (i.e., the
   configurations are stored in `<CLAUDE_CONFIG_FILE>`):

   ```sh
   claude mcp add --transport http materialize-developer \
     http://localhost:6876/api/mcp/developer
   ```

1. Restart Claude Code to pick up the new setting.

1. Upon successful connection, you can [Start asking
   questions](#start-asking-questions).

**Cursor:**

1. Add the `materialize-developer` MCP server entry to your local MCP settings
   file (`~/.cursor/mcp.json`).
   - When merging into an existing `mcpServers` object, remember to add commas
     between entries.
   - If the `mcpServers` field does not already exist, add it as well.

   ```json {hl_lines="3-5"}
   {
     "mcpServers": {
       "materialize-developer": {
         "url": "http://localhost:6876/api/mcp/developer"
       }
     }
   }
   ```

1. Restart Cursor to pick up the new setting.

1. Upon successful connection, you can [Start asking
   questions](#start-asking-questions).

**Generic HTTP:**

Any MCP-compatible client can connect by sending JSON-RPC 2.0 requests:

```bash
curl -X POST http://localhost:6876/api/mcp/developer \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }'
```

Unauthenticated requests run as the `anonymous_http_user` role. To run the
agent's queries as a specific role instead, pass the role's credentials as an
MCP token, as described in [Method 2: Token-based
authentication](#method-2-token-based-authentication).

## Start asking questions

> **Tip:** When the agent reads your user objects with the `query` tool, an [ontology
> table](/transform-data/patterns/ontology/) of curated join relationships in your
> schema helps it confirm exact join keys before writing multi-table SQL.

Once connected to the MCP server, you can ask natural language questions like:

| Question | What the agent does | Tool |
|----------|---------------------|------|
| **Why is my materialized view stale?** | Checks materialization lag, hydration status, replica health, and source errors. Optionally runs `EXPLAIN ANALYZE MEMORY` on the materialized view. | `query_system_catalog`, plus `query` if the agent needs `EXPLAIN ANALYZE` |
| **Why is my cluster running out of memory?** | Checks replica utilization, identifies the largest dataflows, and finds optimization opportunities via the built-in index advisor. | `query_system_catalog`, plus `query` for `EXPLAIN ANALYZE MEMORY` |
| **Has my source finished snapshotting yet?** | Checks source statistics and status. | `query_system_catalog` |
| **How much memory is my cluster using?** | Checks replica utilization metrics across all clusters. | `query_system_catalog` |
| **What's the health of my environment?** | Checks replica statuses, source and sink health, and resource utilization. | `query_system_catalog` |
| **What can I optimize to save costs?** | Queries the index advisor for materialized views that can be dematerialized and indexes that can be dropped. | `query_system_catalog` |
| **Using the `quickstart` cluster, examine the memory usage of `my_mat_view` with skew.** | Runs `EXPLAIN ANALYZE MEMORY WITH SKEW` on the materialized view to report its memory usage and highlight data skew across workers. | `query` for `EXPLAIN ANALYZE MEMORY WITH SKEW` |

The agent picks the appropriate tool for each question. Most catalog lookups run
on the catalog server cluster via
[`query_system_catalog`](/developer-tools/mcp-server/mcp-developer-tools/#query_system_catalog);
[`query`](/developer-tools/mcp-server/mcp-developer-tools/#query) (available
starting in v26.30) is used when the question needs a specific cluster (for
example, `EXPLAIN ANALYZE` against a materialized view or index, or reading user
objects).

## Privileges

The privileges required to use the `materialize-developer` MCP server are:

* `USAGE` on system catalog schemas and `SELECT` on system catalog objects.
  These privileges are granted by default.

* If agents also need access to replica-specific metrics from
  `mz_introspection`, `USAGE` privileges on the corresponding cluster.

## Related pages

- [Use an ontology table](/transform-data/patterns/ontology/)
- [`materialize-developer` MCP Server available
  tools](/developer-tools/mcp-server/mcp-developer-tools/)
- [`materialize-developer` MCP Server
  configuration](/developer-tools/mcp-server/mcp-developer-config/)
- [Troubleshooting](/developer-tools/mcp-server/mcp-server-troubleshooting/)
- [Agent Skills](/developer-tools/mcp-server/coding-agent-skills/)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)

<!-- mz-docs page: developer-tools/mcp-server/mcp-developer-config -->

# Developer endpoint configuration
Configuration for /api/mcp/developer endpoint.
## Available configuration parameters

The following configurations are available for the `/api/mcp/developer`
endpoint:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `enable_mcp_developer` | `true` | Enable or disable the `/api/mcp/developer` endpoint. When the endpoint is disabled, requests return HTTP 503 (Service Unavailable). |
| `enable_mcp_developer_query_tool` | `true` | Available starting in v26.30. Enable or disable the `query` tool on the developer endpoint. When disabled, the tool is hidden from `tools/list` and calls return an error. `query_system_catalog` remains available. |
| `mcp_max_response_size` | `1000000` | Maximum response size in bytes. Queries exceeding this limit return an error. |

## Disabling the endpoint

The developer endpoint is enabled by default. To disable it:

**Cloud:**

Contact [Materialize support](https://materialize.com/docs/support/) to
disable the MCP developer endpoint for your environment.

**Self-Managed:**

Disable the endpoint using one of these methods:

**Option 1: Configuration file**

Set the parameter in your
[system parameters configuration file](/self-managed-deployments/configuration-system-parameters/):

```yaml
system_parameters:
  enable_mcp_developer: "false"
```

**Option 2: Terraform**

Set the parameter via the [Materialize Terraform module](https://github.com/MaterializeInc/materialize-terraform-self-managed):

```hcl
system_parameters = {
  enable_mcp_developer = "false"
}
```

**Option 3: SQL**

Connect as `mz_system` and run:

```mzsql
ALTER SYSTEM SET enable_mcp_developer = false;
```

> **Note:** These parameters are only accessible to the `mz_system` and `mz_support`
> roles. Regular database users cannot view or modify them.


<!-- mz-docs page: developer-tools/mcp-server/mcp-developer-tools -->

# Developer MCP server tools
Tools exposed by the `materialize-developer` MCP server.
## Tools

### `query_system_catalog`

Execute a read-only SQL query restricted to system catalog tables (`mz_*`,
`pg_catalog`, `information_schema`). The tool does not take a cluster argument;
the request runs on the catalog server cluster (`mz_catalog_server`).

> **Tip:** For system catalog lookups that can run on the `mz_catalog_server` cluster,
> prefer `query_system_catalog` over the
> [`query`](#query) tool.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `sql_query` | string | Yes | `SELECT`, `SHOW`, or `EXPLAIN` query using only system catalog tables. |

Only one statement per call is allowed. Write operations (`INSERT`, `UPDATE`,
`CREATE`, etc.) are rejected.

**Example response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "[\n  [\n    \"quickstart\",\n    \"ready\"\n  ],\n  [\n    \"mcp_cluster\",\n    \"ready\"\n  ]\n]"
      }
    ],
    "isError": false
  }
}
```

### `query`

Available starting in v26.30. Execute a read-only SQL query (`SELECT`, `SHOW`,
or `EXPLAIN`) against any object the role can access, including system catalog
and user objects. You must specify a cluster to run `EXPLAIN ANALYZE` and
queries against user objects. On clusters with more than one replica,
`EXPLAIN ANALYZE` additionally requires targeting a single replica via
`cluster_replica`, since [introspection
data](/sql/system-catalog/mz_introspection/) is replica-specific.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `cluster` | string | Yes | Exact cluster name the query should run on. |
| `cluster_replica` | string | No | Available starting in v26.33.0. Replica name (e.g. `r1`) to target one replica of the cluster. Required for `EXPLAIN ANALYZE` on clusters with more than one replica. Find replica names in `mz_catalog.mz_cluster_replicas`. |
| `sql_query` | string | Yes | `SELECT`, `SHOW`, or `EXPLAIN` statement. |

Only one statement per call is allowed. Write operations (`INSERT`, `UPDATE`,
`CREATE`, etc.) are rejected. To disable the tool, see
[`enable_mcp_developer_query_tool`](/developer-tools/mcp-server/mcp-developer-config/).

> **Tip:** For system catalog lookups that can run on the `mz_catalog_server` cluster,
> prefer [`query_system_catalog`](#query_system_catalog) over `query`.

**Example response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "[\n  [\n    \"Explained Query (fast path):\\n  →Constant (1 rows)\\n\\nTarget cluster: quickstart\\n\"\n  ]\n]"
      }
    ],
    "isError": false
  }
}
```

### Key system catalog tables

| Scenario | Tables |
|----------|--------|
| Freshness / lag | `mz_internal.mz_materialization_lag`, `mz_internal.mz_wallclock_global_lag_recent_history`, `mz_internal.mz_hydration_statuses` |
| Memory / resources | `mz_internal.mz_cluster_replica_utilization`, `mz_internal.mz_cluster_replica_metrics` |
| Cluster health | `mz_internal.mz_cluster_replica_statuses`, `mz_catalog.mz_cluster_replicas` |
| Source / Sink health | `mz_internal.mz_source_statuses`, `mz_internal.mz_sink_statuses`, `mz_internal.mz_source_statistics` |
| Object inventory | `mz_catalog.mz_materialized_views`, `mz_catalog.mz_sources`, `mz_catalog.mz_sinks`, `mz_catalog.mz_indexes` |
| Optimization | `mz_internal.mz_index_advice`, `mz_catalog.mz_cluster_replica_sizes` |

Use `SHOW TABLES FROM mz_internal` or `SHOW TABLES FROM mz_catalog` to
discover more tables.

## See also

- [System catalog](/sql/system-catalog/)

<!-- mz-docs page: developer-tools/mcp-server/mcp-server-troubleshooting -->

# MCP Server Troubleshooting
Troubleshooting guide for the MCP Server.
## `unable to verify the first certificate`

**Symptom:** Your MCP client (Claude Code, Cursor, etc.) returns an error like:

```
Error: SDK auth failed: unable to verify the first certificate
```

**Cause:** This error has two common causes:

1. **Wrong protocol:** You're using `http://` but your deployment has TLS
   enabled. Switch to `https://` in your MCP configuration.
2. **Self-signed certificate:** Your Materialize deployment uses a self-signed
   TLS certificate, which is the default for
   [self-managed installations](/self-managed-deployments/). MCP clients built
   on Node.js (including Claude Code) reject self-signed certificates by
   default.

**First, check your URL** — if you're using `http://`, try changing to
`https://`. If that resolves the error, update your MCP configuration.

**Fix:**

For **Claude Code**, start with TLS verification disabled:

```bash
NODE_TLS_REJECT_UNAUTHORIZED=0 claude
```

For **Cursor** or other Node.js-based clients, set the same environment variable
before launching:

```bash
export NODE_TLS_REJECT_UNAUTHORIZED=0
```

Alternatively, configure your deployment with a certificate from a trusted CA
(e.g., [Let's Encrypt](https://letsencrypt.org/)) to avoid this issue entirely.

## `HTTP 503 Service Unavailable`

**Symptom:** Requests to the MCP endpoint return HTTP 503.

**Cause:** The MCP endpoint is disabled.

**Fix:** Enable the endpoint. See
- [Developer endpoint
  configuration](/developer-tools/mcp-server/mcp-developer-config/)
- [Agents endpoint
  configuration](/developer-tools/mcp-server/mcp-developer-config/)

## `HTTP 401 Unauthorized`

**Symptom:** Requests return HTTP 401.

**Cause:** Invalid or missing credentials. The Base64 token may be incorrectly
encoded, or the user/password may be wrong.

**Fix:** Re-encode your credentials and verify:

```bash
# Encode
printf '<user>:<password>' | base64

# Verify by decoding
echo '<your-base64-token>' | base64 --decode
```

Make sure the decoded output matches `user:password` exactly.

## OAuth sign-in fails (Self-Managed)

**Symptom:** The browser sign-in fails at the identity provider (for example,
with a registration error or `invalid_scope`), or sign-in completes but the
client reports that the credentials were rejected on connect.

**Cause:** OAuth for Self-Managed deployments relies on your SSO identity
provider. Most enterprise IdPs need additional configuration for MCP clients,
such as a pre-registered OAuth client, an authentication claim in access
tokens, and the authorization server audience in `oidc_audience`.

**Fix:** See the [SSO troubleshooting
table](/security/self-managed/sso/#troubleshooting) for the specific symptoms
and resolutions, and the [Connecting MCP
clients](/security/self-managed/sso/#connecting-mcp-clients) section for the
full IdP configuration requirements.

<!-- mz-docs page: developer-tools/mz-debug -->

# mz-debug

Materialize debug tool for self-managed and emulator environments.

`mz-debug` is a command-line interface tool that collects debug information for self-managed and emulator Materialize environments. By default, the tool creates a compressed file (`.zip`) containing logs and a dump of the system catalog. You can then share this file with support teams when investigating issues.

## Install `mz-debug`

**macOS:**

```shell
sudo echo "Preparing to extract mz-debug..."
curl -L "https://binaries.materialize.com/mz-debug-latest-arm64-apple-darwin.tar.gz" \
| sudo tar -xzC /usr/local --strip-components=1
```

**Linux:**
```shell
ARCH=$(uname -m)
sudo echo "Preparing to extract mz-debug..."
curl -L "https://binaries.materialize.com/mz-debug-latest-$ARCH-unknown-linux-gnu.tar.gz" \
| sudo tar -xzC /usr/local --strip-components=1

### Get version and help

To see the version of `mz-debug`, specify the `--version` flag:

```shell
mz-debug --version
```

To see the options for running `mz-debug`,

```shell
mz-debug --help
```

## Next steps

To run `mz-debug`, see
- [`mz-debug self-managed`](./self-managed)
- [`mz-debug emulator`](./emulator)

<!-- mz-docs page: developer-tools/mz-debug/emulator -->

# mz-debug emulator
Use mz-debug to debug Materialize Emulator environments running in Docker.
`mz-debug emulator` debugs Docker-based Materialize deployments. It collects:

- Docker logs and resource information.
- Snapshots of system catalog tables from your Materialize instance.

## Requirements

- Docker installed and running. If [Docker](https://www.docker.com/) is not installed, refer to its
[official documentation](https://docs.docker.com/get-docker/) to install
- A valid Materialize SQL connection URL for your local emulator.

## Syntax

```shell
mz-debug emulator [OPTIONS]
```

## Options

### `mz-debug emulator` options

| Option | Description |
| --- | --- |
| <code>--docker-container-id &lt;ID&gt;</code> | <p><a name="docker-container-id"></a> The Docker container to dump.</p> <p>Required.</p>  |
| <code>--dump-docker &lt;boolean&gt;</code> | <p><a name="dump-docker"></a> If <code>true</code>, dump debug information from the Docker container.</p> <p>Defaults to <code>true</code>.</p>  |

### `mz-debug` global options

| Option | Description |
| --- | --- |
| <code>--dump-heap-profiles &lt;boolean&gt;</code> | <p><a name="dump-heap-profiles"></a> If <code>true</code>, dump heap profiles (.pprof.gz) from your Materialize instance.</p> <p>Defaults to <code>true</code>.</p>  |
| <code>--dump-prometheus-metrics &lt;boolean&gt;</code> | <p><a name="dump-prometheus-metrics"></a> If <code>true</code>, dump prometheus metrics from your Materialize instance.</p> <p>Defaults to <code>true</code>.</p>  |
| <code>--dump-system-catalog &lt;boolean&gt;</code> | <p><a name="dump-system-catalog"></a> If <code>true</code>, dump the system catalog from your Materialize instance.</p> <p>Defaults to <code>true</code>.</p>  |
| <code>--mz-username &lt;USERNAME&gt;</code> | <p><a name="mz-username"></a> The username to use to connect to Materialize.</p> <p>Can also be set via the <code>MZ_USERNAME</code> environment variable.</p>  |
| <code>--mz-password &lt;PASSWORD&gt;</code> | <p><a name="mz-password"></a> The password to use to connect to Materialize if password authentication is enabled.</p> <p>Can also be set via the <code>MZ_PASSWORD</code> environment variable.</p>  |
| <code>--mz-connection-url &lt;URL&gt;</code> | <p><a name="mz-connection-url"></a>The Materialize instance&rsquo;s <a href="https://www.postgresql.org/docs/14/libpq-connect.html#LIBPQ-CONNSTRING" >PostgreSQL connection URL</a>.</p> <p>Defaults to <code>postgres://127.0.0.1:6875/materialize?sslmode=prefer</code>.</p>  |

## Output

The `mz-debug` outputs its log file (`tracing.log`) and the generated debug
files into a directory named `mz_debug_YYYY-MM-DD-HH-TMM-SSZ/` as well as zips
the directory and its contents `mz_debug_YYYY-MM-DD-HH-TMM-SSZ.zip`.

The generated debug files are in two main categories: [Docker resource
files](#docker-resource-files) and [system catalog
files](#system-catalog-files).

### Docker resource files

In `mz_debug_YYYY-MM-DD-HH-TMM-SSZ/`, under the `docker/<CONTAINER-ID>`
sub-directory,  the following Docker resource debug files are generated:

| Resource Type | Files |
| --- | --- |
| Container Logs | <ul> <li><code>logs-stdout.txt</code></li> <li><code>logs-stderr.txt</code></li> </ul>  |
| Container Inspection | <ul> <li><code>inspect.txt</code></li> </ul>  |
| Container Stats | <ul> <li><code>stats.txt</code></li> </ul>  |
| Container Processes | <ul> <li><code>top.txt</code></li> </ul>  |

### System catalog files

`mz-debug` outputs system catalog files if
[`--dump-system-catalog`](#dump-system-catalog) is `true` (the default).

The generated files are in `system-catalog` sub-directory as `*.csv` files and
contains:

- Core catalog object definitions
- Cluster and compute-related information
- Data freshness and frontier metric
- Source and sink metrics
- Per-replica introspection metrics (under `{cluster_name}/{replica_name}/*.csv`)

For more information about each relation, view the [system
catalog](/sql/system-catalog/).

### Prometheus metrics

`mz-debug` outputs snapshots of prometheus metrics per service (i.e. environmentd) if
[`--dump-prometheus-metrics`](#dump-prometheus-metrics) is `true` (the default).
Each file is stored under `prom_metrics/{service}.txt`.

### Memory profiles

By default, `mz-debug` outputs heap profiles for each service in `profiles/{service}.memprof.pprof.gz`. To turn off this behavior, you can set [`--dump-heap-profiles`](#dump-heap-profiles) to false.

## Example

### Debug a running local emulator container
```console
mz-debug emulator \
    --docker-container-id 123abc456def
```

<!-- mz-docs page: developer-tools/mz-debug/self-managed -->

# mz-debug self-managed
Use mz-debug to debug Self-Managed Materialize Kubernetes environments.
`mz-debug self-managed` debugs Kubernetes-based Materialize deployments. It
collects:

- Logs and resource information from pods, daemonsets, and other Kubernetes
    resources.

- Snapshots of system catalog tables from your Materialize instance.

By default, the tool will automatically port-forward to collect system catalog information. You can disable this by specifying your own connection URL via `--mz-connection-url`.

## Requirements

`mz-debug` requires [`kubectl`](https://kubernetes.io/docs/tasks/tools/)
v1.32.3+. Install [kubectl](https://kubernetes.io/docs/tasks/tools/) if you do
not have it installed.

## Syntax

```console
mz-debug self-managed [OPTIONS]
```

## Options

## `mz-debug self-managed` options

| Option | Description |
| --- | --- |
| <code>--k8s-namespace &lt;NAMESPACE&gt;</code> | <a name="k8s-namespace"></a> <strong>Required</strong>. The Kubernetes namespace of the Materialize instance. |
| <code>--mz-instance-name &lt;MZ_INSTANCE_NAME&gt;</code> | <a name="mz-instance-name"></a> <strong>Required</strong>. The Materialize instance to target. |
| <code>--dump-k8s &lt;boolean&gt;</code> | <p><a name="dump-k8s"></a> If <code>true</code>, dump debug information from the Kubernetes cluster.</p> <p>Defaults to <code>true</code>.</p>  |
| <code>--additional-k8s-namespace &lt;NAMESPACE&gt;</code> | <a name="additional-k8s-namespace"></a> Additional k8s namespaces to dump. |
| <code>--k8s-context &lt;CONTEXT&gt;</code> | <p><a name="k8s-context"></a> The Kubernetes context to use.</p> <p>Defaults to the <code>KUBERNETES_CONTEXT</code> environment variable.</p>  |
| <code>-h</code>, <code>--help</code> | <a name="help"></a> Print help information. |

## `mz-debug` global options

| Option | Description |
| --- | --- |
| <code>--dump-heap-profiles &lt;boolean&gt;</code> | <p><a name="dump-heap-profiles"></a> If <code>true</code>, dump heap profiles (.pprof.gz) from your Materialize instance.</p> <p>Defaults to <code>true</code>.</p>  |
| <code>--dump-prometheus-metrics &lt;boolean&gt;</code> | <p><a name="dump-prometheus-metrics"></a> If <code>true</code>, dump prometheus metrics from your Materialize instance.</p> <p>Defaults to <code>true</code>.</p>  |
| <code>--dump-system-catalog &lt;boolean&gt;</code> | <p><a name="dump-system-catalog"></a> If <code>true</code>, dump the system catalog from your Materialize instance.</p> <p>Defaults to <code>true</code>.</p>  |
| <code>--mz-username &lt;USERNAME&gt;</code> | <p><a name="mz-username"></a> The username to use to connect to Materialize.</p> <p>Can also be set via the <code>MZ_USERNAME</code> environment variable.</p>  |
| <code>--mz-password &lt;PASSWORD&gt;</code> | <p><a name="mz-password"></a> The password to use to connect to Materialize if password authentication is enabled.</p> <p>Can also be set via the <code>MZ_PASSWORD</code> environment variable.</p>  |
| <code>--mz-connection-url &lt;URL&gt;</code> | <p><a name="mz-connection-url"></a>The Materialize instance&rsquo;s <a href="https://www.postgresql.org/docs/14/libpq-connect.html#LIBPQ-CONNSTRING" >PostgreSQL connection URL</a>.</p> <p>Defaults to <code>postgres://127.0.0.1:6875/materialize?sslmode=prefer</code>.</p>  |

## Output

The `mz-debug` outputs its log file (`tracing.log`) and the generated debug
files into a directory named `mz_debug_YYYY-MM-DD-HH-TMM-SSZ/` as well as zips
the directory and its contents `mz_debug_YYYY-MM-DD-HH-TMM-SSZ.zip`.

The generated debug files are in two main categories: [Kubernetes resource
files](#kubernetes-resource-files) and [system catalog
files](#system-catalog-files).

### Kubernetes resource files

Under `mz_debug_YYYY-MM-DD-HH-TMM-SSZ/`, the following Kubernetes resource debug
files are generated:

| Resource Type | Files |
| --- | --- |
| Workloads | <ul> <li><code>pods/{namespace}/*.yaml</code></li> <li><code>logs/{namespace}/{pod}.current.log</code></li> <li><code>logs/{namespace}/{pod}.previous.log</code></li> <li><code>deployments/{namespace}/*.yaml</code></li> <li><code>statefulsets/{namespace}/*.yaml</code></li> <li><code>replicasets/{namespace}/*.yaml</code></li> <li><code>events/{namespace}/*.yaml</code></li> <li><code>materializes/{namespace}/*.yaml</code></li> </ul>  |
| Networking | <ul> <li><code>services/{namespace}/*.yaml</code></li> <li><code>networkpolicies/{namespace}/*.yaml</code></li> <li><code>certificates/{namespace}/*.yaml</code></li> </ul>  |
| Storage | <ul> <li><code>persistentvolumes/*.yaml</code></li> <li><code>persistentvolumeclaims/{namespace}/*.yaml</code></li> <li><code>storageclasses/*.yaml</code></li> </ul>  |
| Configuration | <ul> <li><code>roles/{namespace}/*.yaml</code></li> <li><code>rolebinding/{namespace}/*.yaml</code></li> <li><code>configmaps/{namespace}/*.yaml</code></li> <li><code>serviceaccounts/{namespace}/*.yaml</code></li> </ul>  |
| Cluster-level | <ul> <li><code>nodes/*.yaml</code></li> <li><code>daemonsets/*.yaml</code></li> <li><code>mutatingwebhookconfigurations/{namespace}/*.yaml</code></li> <li><code>validatingwebhookconfigurations/{namespace}/*.yaml</code></li> <li><code>customresourcedefinitions/*.yaml</code></li> </ul>  |

Each resource type directory also contains a `describe.txt` file with the output of `kubectl describe` for that resource type.

### System catalog files

`mz-debug` outputs system catalog files if
[`--dump-system-catalog`](#dump-system-catalog) is `true` (the default).

The generated files are in `system-catalog` sub-directory as `*.csv` files and
contains:

- Core catalog object definitions
- Cluster and compute-related information
- Data freshness and frontier metric
- Source and sink metrics
- Per-replica introspection metrics (under `{cluster_name}/{replica_name}/*.csv`)

For more information about each relation, view the [system
catalog](/sql/system-catalog/).

### Prometheus metrics

`mz-debug` outputs snapshots of prometheus metrics per service (i.e. environmentd) if
[`--dump-prometheus-metrics`](#dump-prometheus-metrics) is `true` (the default).
Each file is stored under `prom_metrics/{service}.txt`.

### Memory profiles

By default, `mz-debug` outputs heap profiles for each service in `profiles/{service}.memprof.pprof.gz`. To turn off this behavior, you can set [`--dump-heap-profiles`](#dump-heap-profiles) to false.

## Prerequisite: Get the Materialize instance name

To use `mz-debug`, you need to specify the <a href="#k8s-namespace">Kubernetes namespace (`--k8s-namespace`)</a> and the <a href="#mz-instance-name">Materialize instance name (`--mz-instance-name`)</a>. To retrieve the Materialize instance name, you can use kubectl. For example, the following retrieves the name of the Materialize instance(s) running in the Kubernetes namespace `materialize-environment`:
```
kubectl --namespace materialize-environment get materializes.materialize.cloud
```
The command should return the NAME of the Materialize instance(s) in the namespace:
```
NAME
12345678-1234-1234-1234-123456789012
```

## Examples

### Debug a Materialize instance running in a namespace

The following example uses `mz-debug` to collect debug information for the Materialize instance (`12345678-1234-1234-1234-123456789012` obtained in the Prerequisite) running in the Kubernetes namespace `materialize-environment`:

```shell
mz-debug self-managed --k8s-namespace materialize-environment \
--mz-instance-name 12345678-1234-1234-1234-123456789012
```

### Include information from additional kubernetes namespaces

When debugging a Materialize instance, you can also include information from other namespaces via <a href="#additional-k8s-namespace">`--additional-k8s-namespace`</a>. The following example collects debug information for the Materialize instance running in the Kubernetes namespace `materialize-environment` as well as debug information for the namespace `materialize`:

```shell
mz-debug self-managed --k8s-namespace materialize-environment \
--mz-instance-name 12345678-1234-1234-1234-123456789012 \
--additional-k8s-namespace materialize
```

<!-- mz-docs page: developer-tools/mz-deploy -->

# Use mz-deploy to manage Materialize

Deploy and manage Materialize objects with mz-deploy, a SQL-native CLI for zero-downtime deployments.

`mz-deploy` is a CLI that manages your Materialize deployment from plain SQL
files in a git repository. It catches errors before they reach production, lets
you test view logic locally, and deploys changes without downtime.

## Installation

On macOS and Linux, we recommend installing `mz-deploy` with
[Homebrew](https://brew.sh/):

```shell
brew install materializeinc/materialize/mz-deploy
```

For direct downloads and other installation options, see
[Get started](/developer-tools/mz-deploy/get-started/#prerequisites-and-installation).

## Why mz-deploy

### Write plain SQL, deploy safely

Everything lives in `.sql` files — one object per file, organized by database
and schema. `mz-deploy` tracks dependencies between objects, diffs your project
against the live environment, and deploys only what changed. Durable objects
like secrets, connections, sources, and tables are converged in place (like
Terraform). Views, materialized views, indexes, and sinks go through a staged
deployment so changes can be validated before going live.

### Catch errors before deploying

`mz-deploy compile` type-checks every SQL statement against your dependency
schemas — locally, with no database connection required. Inline unit tests let
you mock dependencies and verify view logic with deterministic inputs before
anything touches a real environment. Changes that break types or dependencies
fail fast on your laptop or in CI, not in production.

### Ship without downtime

When you deploy, `mz-deploy` creates your changes in isolated staging schemas
alongside production. Once all materialized views finish computing their initial
results, a single atomic swap cuts traffic over to the new version. Running
queries are never interrupted, and if something goes wrong, the staging
deployment can be cleaned up without affecting production.

## When to use it

| Tool | Best for | Manages infrastructure | Zero-downtime deployments |
|------|----------|----------------------|--------------------------|
| **Plain SQL / psql scripts** | Manual execution. No dependency tracking, no diff, no rollback. Where most teams start. | No | No |
| **mz-deploy** | SQL-native, git-based workflow with offline type-checking, unit tests, and staged deployments. | Yes | Yes |
| **[dbt](/developer-tools/dbt/)** | Teams already invested in dbt. Manages views and materialized views. | No (clusters, connections, secrets are out of scope) | Yes (via `dbt-materialize` adapter macros) |
| **[Terraform](/developer-tools/terraform/)** | Teams managing Materialize alongside other cloud infrastructure. | Yes | No |

## Available guides

<div class="multilinkbox">
<div class="linkbox ">
  <div class="title">
    To get started
  </div>
  <a href="/developer-tools/mz-deploy/get-started/" >Get started with mz-deploy</a>
</div>

<div class="linkbox ">
  <div class="title">
    Develop
  </div>
  <ul>
<li><a href="/developer-tools/mz-deploy/project-structure/" >Project structure</a></li>
<li><a href="/developer-tools/mz-deploy/infrastructure/" >Infrastructure</a></li>
<li><a href="/developer-tools/mz-deploy/local-development/" >Local development</a></li>
<li><a href="/developer-tools/mz-deploy/editor-setup/" >Editor setup</a></li>
<li><a href="/developer-tools/mz-deploy/agent-setup/" >AI agent setup</a></li>
</ul>

</div>

<div class="linkbox ">
  <div class="title">
    Deploy
  </div>
  <ul>
<li><a href="/developer-tools/mz-deploy/deployments/" >Deployments</a></li>
<li><a href="/developer-tools/mz-deploy/stable-apis/" >Stable APIs</a></li>
<li><a href="/developer-tools/mz-deploy/profiles/" >Profiles</a></li>
</ul>

</div>

</div>

<!-- mz-docs page: developer-tools/mz-deploy/agent-setup -->

# AI agent setup
Configure AI coding agents like Claude Code and Codex to work with mz-deploy projects.
`mz-deploy` was built with AI coding agents in mind. Every new project ships
with agent-readable documentation, the CLI provides agent-optimized help, and
the language server gives agents real-time feedback on SQL correctness.

## Project skill

The community [MaterializeInc/agent-skills](https://github.com/MaterializeInc/agent-skills)
repo publishes an agent skill for `mz-deploy` that teaches agents your
project's conventions: one object per file, file paths map to qualified
names, how the deployment lifecycle works, unit test syntax, and how to get
detailed help with `mz-deploy help <command>`.

The skill is not installed by default. You can install it for yourself as a
plugin, or install it in the project so that everyone who works in the
repository gets it. Choose one, since installing both loads the skill twice.

### Install as a plugin

If you use Claude Code or Codex, install the Materialize agent skills plugin,
which includes the `mz-deploy` skill. The plugin is installed for your user
account and applies to all your projects.

**Claude Code:**
```
/plugin marketplace add MaterializeInc/agent-skills
/plugin install materialize@materialize
```

**Codex:**
```bash
codex plugin marketplace add MaterializeInc/agent-skills
codex plugin add materialize@materialize
```

To keep the plugin up to date, see [Agent
Skills](/developer-tools/mcp-server/coding-agent-skills/#install-as-a-plugin).

### Install in the project

To share the skill with everyone who works in the repository, install it in
the project with:

```sh
npx -y skills add MaterializeInc/agent-skills -a universal -a claude-code --project
```

This drops the skill into `.agents/skills/mz-deploy/` and wires up a
`.claude/skills/` symlink so Claude Code picks it up. Agents that consume
the universal skill format (Codex and others) load it from the same
location. You don't need to explain the project's conventions — the agent
already knows them.

Update to the latest version later with:

```sh
npx -y skills update
```

## Claude Code on the web

[Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web)
runs each session in a fresh, Anthropic-managed cloud sandbox. The sandbox
doesn't have `mz-deploy` installed, so install it with a **setup script** — a
Bash script that runs once, as root, before Claude Code starts.

In the cloud environment settings, set the **Setup script** field to:

```bash
#!/bin/bash
set -euo pipefail
ARCH=$(uname -m)
curl -L "https://binaries.materialize.com/mz-deploy-latest-$ARCH-unknown-linux-gnu.tar.gz" \
| tar -xzC /usr/local --strip-components=1
```

The sandbox runs Ubuntu on Linux, so this always uses the `unknown-linux-gnu`
build and resolves the architecture (`x86_64` or `aarch64`) at runtime. The
binary lands in `/usr/local/bin`, which is already on `PATH`. The script runs as
root, so no `sudo` is needed. Setup scripts have network access under the
default **Trusted** network mode; if your environment uses **None**, the
download will fail.

To configure the language server in the sandbox as well, set up the plugin as
described in [Configuring for Claude Code](#configuring-for-claude-code) and
commit your project's `.claude/settings.json` to your repository. It carries over
to cloud sessions automatically.

## Agent-optimized help

```bash
mz-deploy help <command>    # Detailed guide for a single command
mz-deploy help --all        # All command guides concatenated
```

Unlike `--help` (which prints brief CLI usage), `help` returns full guides
with behavior notes, examples, error recovery steps, and related commands.

## Language server

The mz-deploy language server gives agents the same benefits it gives human
editors: parse error diagnostics on every file change, go-to-definition across
your project, and column-aware completions scoped to actual dependencies.

For agents, this means fewer incorrect SQL suggestions — the agent sees real
column names and types from your `types.lock` rather than guessing.

### Configuring for Claude Code

Use the `mz-sql-lsp` plugin, published by the
[MaterializeInc/agent-skills](https://github.com/MaterializeInc/agent-skills)
repo, which also serves as a Claude Code plugin marketplace named `materialize`.
The plugin registers the language server for `.sql` files and bundles a skill
that tells Claude to use LSP navigation instead of grepping when it needs to
resolve an object reference, inspect a view's columns, or find dependents before
an edit.

`mz-deploy` must be on Claude Code's `PATH`. Then:

```
/plugin marketplace add MaterializeInc/agent-skills
/plugin install mz-sql-lsp@materialize
```

On enable, Claude Code prompts for one required setting, **mz-deploy project
directory**: the directory holding your `project.toml`, relative to the
repository root. Use `.` when `project.toml` sits at the root, or a subdirectory
name such as `mz` when the project is nested. The language server takes that
directory as its project root. You can change the value later from `/plugin`, in
the plugin's detail view.

<!-- mz-docs page: developer-tools/mz-deploy/deployments -->

# Deployments
Stage, test, and promote zero-downtime blue/green deployments.
`mz-deploy` gives you a complete lifecycle from local development through
production deployment:

```nofmt
compile ──▶ test ──▶ dev ──▶ stage ──▶ wait ──▶ promote
  local      local   real env  real env
```

[`compile`](/developer-tools/mz-deploy/local-development/#compile-and-validate) and
[`test`](/developer-tools/mz-deploy/local-development/#write-and-run-unit-tests) run
locally to catch errors fast.
[`dev`](#iterate-against-production-data) builds a per-developer overlay
against real production data so you can validate behavior before staging.
When ready, a deployer runs `stage`, `wait`, and `promote` to ship to
production with zero downtime.

## Set up deployment tracking

```bash
mz-deploy setup
```

This creates the `_mz_deploy` database, its tracking tables, three roles for
access control, and the deployment server cluster that every `mz-deploy`
connection runs against. The command is idempotent — you can safely run it
again without side effects.

When [RBAC is enabled](/security/self-managed/access-control/#enabling-rbac),
`setup` must be run by a **superuser**. It grants `CREATEDB` and
`CREATECLUSTER` on the system to the deploy roles, and only a superuser can
grant system privileges while RBAC is enforced. On clusters with RBAC
disabled, the check is skipped. Once setup completes, the deployer,
developer, and monitor roles use mz-deploy without any further superuser
involvement.

### Roles

`setup` creates three roles that control who can do what:

| Role | Commands |
|------|-------------|
| `materialize_deployer` | `delete`, `stage`, `promote`, `abort` — full write access |
| `materialize_developer` | `dev`, `list`, `describe`, `log` |
| `materialize_monitor` | `list`, `describe`, `log` — read-only deployment state |

Membership is enforced when the command connects: `stage`, `promote`,
`abort`, and `delete` require `materialize_deployer`; `dev` requires
`materialize_developer`; and `list`, `describe`, and `log` accept any of the
three roles. `apply` provisions infrastructure (clusters, secrets,
connections, sources, tables) and is not currently restricted by role.

Your database user must be a member of one of these roles to run commands
that connect to the database. Grant the appropriate role to each user:

```sql
GRANT materialize_deployer TO deploy_bot;
GRANT materialize_developer TO dev_user;
```

`compile` and `test` do not require an mz-deploy role because they run locally.

## Deploy to staging

```bash
mz-deploy stage
```

`stage` compiles the project, diffs against the last promoted snapshot, and
deploys only changed objects to staging schemas with suffixed names (for example,
`public_a1b2c3d`).

The deploy ID defaults to the current git SHA prefix. To override it:

```bash
mz-deploy stage --deploy-id my-feature
```

Preview what would be staged without making changes:

```bash
mz-deploy stage --dry-run
```

Allow staging with uncommitted changes:

```bash
mz-deploy stage --allow-dirty
```

> **Note:** Common errors during staging:
> - **Deploy ID already exists** — abort the existing deployment with
>   `mz-deploy abort <id>` or choose a different `--deploy-id`.
> - **Uncommitted changes** — commit your changes or pass `--allow-dirty`.

## Iterate against production data

`dev` deploys a personal, throwaway copy of your changes to your remote
Materialize so you can validate them against real production data. It
creates a per-developer overlay database (`<db>__<profile>`) containing
only the views and materialized views you've changed, with references
rewritten so unchanged dependencies resolve to production. External
dependencies pass through unchanged.

You pass the cluster every overlay materialized view and index runs on;
the `IN CLUSTER` clause in your source is rewritten to it. `dev` refuses
to target a cluster that hosts a promoted deployment, so provision a
dedicated dev cluster and reuse it:

```bash
mz-deploy dev <cluster>
```

Every run drops the overlay and rebuilds it from scratch, so there's no
state to manage.

Show the plan without executing any DDL:

```bash
mz-deploy dev <cluster> --dry-run
```

Tear down the overlay when you're done:

```bash
mz-deploy dev --down
```

`dev` requires the `materialize_developer` role. `setup` grants the
`CREATEDB` system privilege to that role, so members inherit it
automatically. Tables, sources, sinks, connections, and secrets are
silently skipped — `dev` only overlays views and materialized views.

| | `stage` | `dev` |
|--|---------|-------|
| Required role | `materialize_deployer` | `materialize_developer` |
| Target | Staging schemas alongside production | Per-developer overlay database |
| Git dirty check | Yes | No |
| Object types | All project objects | Views and materialized views only |
| Can be promoted | Yes | No |

## Wait for hydration

```bash
mz-deploy wait <deploy-id>
```

This monitors cluster hydration and displays a live dashboard. The possible
statuses are:

| Status | Meaning |
|--------|---------|
| **ready** | Fully hydrated and caught up |
| **hydrating** | Objects still being materialized |
| **lagging** | Hydrated but lag exceeds the `--allowed-lag` threshold |
| **failing** | No healthy replicas (possible OOM) |

Flags:

- `--timeout <seconds>` — maximum time to wait before exiting with an error.
- `--allowed-lag <seconds>` — lag threshold for the **lagging** status (default:
  300).

> **Note:** Common errors during hydration:
> - **Timeout** — increase `--timeout` or check cluster health.
> - **"failing" status** — check cluster sizing; replicas may need more resources.

## Promote to production

```bash
mz-deploy promote <deploy-id>
```

This atomically swaps staging schemas into production. `promote` automatically
runs a readiness check before proceeding.

Preview what would change:

```bash
mz-deploy promote <deploy-id> --dry-run
```

Flags:

- `--force` — skip conflict detection.
- `--no-ready-check` — skip the automatic readiness check.
- `--allowed-lag <SECONDS>` — maximum wallclock lag a cluster may have and
  still pass the readiness check. Clusters lagging further block promotion.
  Defaults to 300 (5 minutes).
- `--dry-run` — preview the promotion without applying changes.

> **Note:** If production changed since you staged, `promote` detects the conflict and
> aborts. Re-run `mz-deploy stage` to pick up the latest production state before
> promoting.

## Manage deployments

List active staging deployments (similar to `git branch`):

```bash
mz-deploy list
```

View promotion history (similar to `git log`):

```bash
mz-deploy log
```

Clean up a staging deployment:

```bash
mz-deploy abort <deploy-id>
```

View deployment details:

```bash
mz-deploy describe <deploy-id>
```

## Day-two operations

### Making changes

`mz-deploy` uses a diff-based model. When you change a SQL file and re-stage,
only the modified objects and their dependents are redeployed.

For example, to change `stalled_orders` from a 30-minute threshold to 1 hour,
update the SQL file:

```sql
-- models/materialize/public/stalled_orders.sql
CREATE MATERIALIZED VIEW stalled_orders
IN CLUSTER orders AS
SELECT
    id,
    customer,
    amount,
    created_at,
    updated_at,
    mz_now() - updated_at AS stalled_for
FROM orders
WHERE status = 'pending'
  AND updated_at < mz_now() - INTERVAL '1 hour';
```

When you re-stage, only `stalled_orders` and its dependents are redeployed.

### Deleting objects

Use `mz-deploy delete` to drop objects. The command drops without `CASCADE` and
requires confirmation:

```bash
mz-deploy delete cluster orders
```

Pass `--yes` to skip the confirmation prompt.

Supported types: `cluster`, `connection`, `network-policy`, `role`, `secret`,
`source`, `table`.

### Stable API schemas

If other teams depend on your materialized views, you can mark schemas as
stable API boundaries so that deployments never break downstream consumers.
See [Stable APIs](/developer-tools/mz-deploy/stable-apis/) for details.

