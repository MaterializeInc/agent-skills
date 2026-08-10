# MCP Servers and agent skills

This section contains guides for installing Materialize Agent skills and integrating with Materialize's built-in MCP servers.

## Agent skills

Materialize provides the following open-source [agent
skills](https://github.com/MaterializeInc/agent-skills) to help developers build
with Materialize.

| Skill | Description |
|-------|-------------|
| `mcp-developer-analysis` | Use for operational introspection and troubleshooting via the `materialize-developer` server. Covers exact catalog schemas, diagnostic workflows, remediation runbooks, and guardrails for known pitfalls (cluster-scoped queries, uint8 ID mismatches, etc.).<br><br>Examples: *"why is my materialized view stale?"*, *"what can I optimize to save costs?"*, *"is my source healthy?"* |
| `materialize-docs` | Use for authoring view definitions, learning concepts, and looking up patterns; useful with either MCP server. Covers comprehensive Materialize documentation, including SQL syntax, idiomatic patterns, data ingestion, concepts, and best practices (400+ reference files).<br><br>Examples: *"show me how to deduplicate a stream"*, *"what's the idiomatic top-K pattern?"*, *"how do I create a Kafka source?"* |
| `materialize-dbt` | Use for managing Materialize pipelines with dbt. Covers dbt-materialize adapter usage: materializations, profile configuration, index creation, blue/green deployments, and testing.<br><br>Examples: *"write a dbt model for a materialized view"*, *"how do I do a blue/green deployment with dbt?"* |
| `materialize-terraform-provider` | Use for managing Materialize resources declaratively with Terraform. Covers provider configuration for Cloud and self-managed, navigation into the provider's auto-generated resource reference, cross-resource patterns, import workflows, and gotchas.<br><br>Examples: *"create a Kafka source with Terraform"*, *"import my existing clusters into Terraform state"*, *"set up RBAC grants in Terraform"* |
| `materialize-terraform-self-managed` | Use for deploying or operating self-managed Materialize infrastructure with Terraform. Covers module layout and variables for deploying on AWS, Azure, and GCP: networking, Kubernetes, backend URL formats, instance sizing, upgrades, and gotchas.<br><br>Examples: *"deploy Materialize on EKS"*, *"what instance types should Materialize nodes use?"*, *"upgrade my self-managed Materialize"* |

## MCP servers

Materialize provides built-in Model Context Protocol (MCP) servers that AI
agents can use. The MCP interface is served directly by the database; no sidecar
process or external server is required. These endpoints use [JSON-RPC
 2.0](https://www.jsonrpc.org/specification) over HTTP POST (default port 6876)
and support the MCP `initialize`, `tools/list`, and `tools/call` methods.

| Endpoint | Path | Description |
|----------|------|-------------|
| **Agent** | `/api/mcp/agent` | Discover and query your real-time data products over HTTP. <br>For details, see [MCP Server for agents](/integrations/mcp-server/mcp-agent/).<br>*Available starting in v26.24*|
| **Developer** | `/api/mcp/developer` | Read `mz_*` system catalog tables for troubleshooting and observability. <br>For details, see [MCP Server for developer](/integrations/mcp-server/mcp-developer/).|

## See also

- [Use an ontology table](/architecture-patterns/ontology/) to curate join
  relationships that agents query through the `query` tool before writing
  multi-table SQL.
- [MCP Server
  Troubleshooting](/integrations/mcp-server/mcp-server-troubleshooting/)

---

## Agent endpoint configuration

## Available configuration parameters

The following configurations are available for the `/api/mcp/agent` endpoint:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `enable_mcp_agent` | `true` | Enable or disable the `/api/mcp/agent` endpoint. When disabled, requests return `HTTP 503 (Service Unavailable)`.|
| `enable_mcp_agent_query_tool` <a name="enable_mcp_agent_query_tool"></a> | `true` | Enable or disable the [`query` tool](/integrations/mcp-server/mcp-agent-tools/#query), which allows for queries with joins. Enabling the `query` tool can impact performance, leak information via query
execution errors, and, by default, allow catalog-level discovery of operational
metadata through system catalog access.  To prevent catalog-level discovery of operational metadata through system catalog access, you can [restrict `query` tool access to user objects only](/integrations/mcp-server/mcp-agent-tools/#restrict-to-user-objects). |
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

---

## Agent MCP server tools

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
>   configuration](/integrations/mcp-server/mcp-agent-config/#enable_mcp_agent_query_tool)
>   system parameter to `false`. Once disabled, you can only query data products
>   that are discoverable by [`get_data_products`](#get_data_products).

#### Restricting `query` tool access to user objects only {#restrict-to-user-objects}

When the [`query` tool](/integrations/mcp-server/mcp-agent-tools/#query) is
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
  error.
- Data product discovery (`get_data_products`, `get_data_product_details`,
  `read_data_product`) continues to work normally.
- The restriction cannot be bypassed by the role itself; only a superuser can
  change or remove it.

To remove the restriction for an agent, a superuser can reset the parameter (or
set it to `false`):

```mzsql
ALTER ROLE my_agent RESET restrict_to_user_objects;
```

---

## Developer endpoint configuration

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

---

## Developer MCP server tools

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
data](/reference/system-catalog/mz_introspection/) is replica-specific.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `cluster` | string | Yes | Exact cluster name the query should run on. |
| `cluster_replica` | string | No | Available starting in v26.33.0. Replica name (e.g. `r1`) to target one replica of the cluster. Required for `EXPLAIN ANALYZE` on clusters with more than one replica. Find replica names in `mz_catalog.mz_cluster_replicas`. |
| `sql_query` | string | Yes | `SELECT`, `SHOW`, or `EXPLAIN` statement. |

Only one statement per call is allowed. Write operations (`INSERT`, `UPDATE`,
`CREATE`, etc.) are rejected. To disable the tool, see
[`enable_mcp_developer_query_tool`](/integrations/mcp-server/mcp-developer-config/).

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

- [System catalog](/reference/system-catalog/)

---

## MCP Server for Agents

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
> tool](/integrations/mcp-server/mcp-agent-tools/#query) is **enabled by default**
> and can execute arbitrary `SELECT` queries (including joins) on **all** objects
> the agent can access (including system catalog objects), not just those
> discoverable by the [`get_data_products`
> tool](/integrations/mcp-server/mcp-agent-tools/#get_data_products).
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
   tool](/integrations/mcp-server/mcp-agent-tools/#query) cannot read system
   catalog objects. You must run the following as a **superuser**:

   ```mzsql
   ALTER ROLE mcp_agent SET restrict_to_user_objects = true;
   ```

   As mentioned before, role configurations are **not** inherited; you must also
   set it on each specific agent role. Setting the parameter on the functional
   role is recommended as a precaution in case the role is ever used directly to
   run queries.

   See also [Restrict `query` tool access to user objects
   only](/integrations/mcp-server/mcp-agent-tools/#restrict-to-user-objects).

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
>   enabling [index point-lookups](/concepts/indexes/#point-lookups) instead of
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
[`restrict_to_user_objects`](/integrations/mcp-server/mcp-agent-tools/#restrict-to-user-objects)
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
   configurations are stored in `~/.claude.json`):

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
   tool](/integrations/mcp-server/mcp-agent-tools/#query) cannot read system
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
   tool](/integrations/mcp-server/mcp-agent-tools/#query) cannot read system
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
   tool](/integrations/mcp-server/mcp-agent-tools/#query) cannot read system
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
   configurations are stored in `~/.claude.json`):

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

> **Warning:** By default, the [`query` tool](/integrations/mcp-server/mcp-agent-tools/#query)
> is **enabled**. This tool allows arbitrary `SELECT` queries (including joins) on
> **all** objects for which the agent has the appropriate privileges (`SELECT` on
> the object, `USAGE` on the object's schema).
> To disable it, set
> [`enable_mcp_agent_query_tool`](/integrations/mcp-server/mcp-agent-config/#enable_mcp_agent_query_tool)
> to `false`. See [Agent endpoint
> configuration](/integrations/mcp-server/mcp-agent-config/).

> **Tip:** Because the `query` tool can join across objects, consider maintaining an
> [ontology table](/architecture-patterns/ontology/): a curated catalog of the
> join relationships in your schema that the agent can query to confirm exact join
> keys before writing multi-table SQL.

Once connected to the MCP server, you can query your curated data products using
either natural language or SQL:

- *Via `materialize-agent`: What data products can I query?*
- *SELECT * FROM mcp_product_performance LIMIT 5;*
- *What's the `total_revenue` for product 42?*
- *Perform a Pareto analysis on my products.*

## Related pages

- [Use an ontology table](/architecture-patterns/ontology/)
- [`materialize-agent` MCP Server available
  tools](/integrations/mcp-server/mcp-agent-tools/)
- [`materialize-agent` MCP Server
  configuration](/integrations/mcp-server/mcp-agent-config/)
- [Agent Skills](/integrations/coding-agent-skills/)
- [CREATE INDEX](/sql/create-index)
- [COMMENT ON](/sql/comment-on)
- [CREATE ROLE](/sql/create-role)
- [GRANT PRIVILEGE](/sql/grant-privilege)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)

---

## MCP Server for Developers

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
   configurations are stored in `~/.claude.json`):

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
   client](/get-started/install-materialize-emulator/#materialize-emulator-connect-client)
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
   configurations are stored in `~/.claude.json`):

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

The [Materialize Emulator](/get-started/install-materialize-emulator/) does not
require authentication. Your MCP client only needs the `materialize-developer`
MCP server URL:

```
http://localhost:6876/api/mcp/developer
```

**Claude Code:**

1. Add the `materialize-developer` MCP server as [local-scoped
   server](https://code.claude.com/docs/en/mcp#local-scope) (i.e., the
   configurations are stored in `~/.claude.json`):

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
> table](/architecture-patterns/ontology/) of curated join relationships in your
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
[`query_system_catalog`](/integrations/mcp-server/mcp-developer-tools/#query_system_catalog);
[`query`](/integrations/mcp-server/mcp-developer-tools/#query) (available
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

- [Use an ontology table](/architecture-patterns/ontology/)
- [`materialize-developer` MCP Server available
  tools](/integrations/mcp-server/mcp-developer-tools/)
- [`materialize-developer` MCP Server
  configuration](/integrations/mcp-server/mcp-developer-config/)
- [Troubleshooting](/integrations/mcp-server/mcp-server-troubleshooting/)
- [Agent Skills](/integrations/coding-agent-skills/)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)

---

## MCP Server Troubleshooting

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
  configuration](/integrations/mcp-server/mcp-developer-config/)
- [Agents endpoint
  configuration](/integrations/mcp-server/mcp-developer-config/)

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

