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

---

## Download and run Materialize Emulator

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

---

## Manage Materialize

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

---

## Materialize console

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

---

## MCP Servers and agent skills

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

---

## mz-debug

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

---

## Tools and integrations

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

---

## Use dbt to manage Materialize

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

---

## Use mz-deploy to manage Materialize

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

---

## Use Terraform to manage Materialize

[Terraform](https://www.terraform.io/) is an infrastructure-as-code tool that
allows you to manage your resources in a declarative configuration language.
Materialize maintains a [Terraform provider](https://registry.terraform.io/providers/MaterializeInc/materialize/latest/docs)
to help you safely and predictably provision and manage connections, sources,
and other database objects.

Materialize also maintains [several
modules](/developer-tools/terraform/manage-cloud-modules) that make it easier to manage
other cloud resources that Materialize depends on. Modules allow you to bypass
manually configuring cloud resources and are an efficient way of deploying
infrastructure with a single `terraform apply` command.

## Available guides

<div class="multilinkbox">
<div class="linkbox ">
  <div class="title">
    To get started
  </div>
  <a href="./get-started/" >Get started with Terraform and Materialize</a>
</div>

<div class="linkbox ">
  <div class="title">
    Manage resources
  </div>
  <p><a href="./manage-resources" >Manage Materialize resources</a></p>
<p><a href="./manage-cloud-modules/" >Manage cloud resources</a></p>

</div>

<div class="linkbox ">
  <div class="title">
    Additional modules
  </div>
  <ul>
<li><a href="./appendix-secret-stores/" >Appendix: Secret stores</a></li>
</ul>

</div>

</div>

## Contributing

If you want to help develop the Materialize provider, check out the [contribution guidelines](https://github.com/MaterializeInc/terraform-provider-materialize/blob/main/CONTRIBUTING.md).

