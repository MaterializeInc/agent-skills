# MCP Server

Learn how to integrate with Materialize's built-in MCP endpoints.

Materialize provides built-in Model Context Protocol (MCP) endpoints that AI
agents can use. The MCP interface is served directly by the database; no sidecar
process or external server is required. These endpoints use [JSON-RPC
 2.0](https://www.jsonrpc.org/specification) over HTTP POST (default port 6876)
and support the MCP `initialize`, `tools/list`, and `tools/call` methods.

## MCP endpoints overview

| Endpoint | Path | Description |
|----------|------|-------------|
| [**Developer**](/integrations/mcp-server/mcp-developer/) | `/api/mcp/developer` | Read `mz_*` system catalog tables for troubleshooting and observability. <br>For details, see [MCP Server for developer](/integrations/mcp-server/mcp-developer/).|

## See also

- [MCP Server
  Troubleshooting](/integrations/mcp-server/mcp-server-troubleshooting/)
- [Appendix: MCP Server (Python)](/integrations/mcp-server/llm) for locally-run,
  separate MCP Server.

---

## Appendix: MCP Server (Python)

> **Disambiguation:** This page provides information on the locally-run, separate MCP Server. For documentation on using the new built-in MCP Server endpoints, see: - [MCP Server for Developer](/integrations/mcp-server/mcp-developer/) 

The [Model Context Protocol (MCP) Server for Materialize](https://materialize.com/blog/materialize-turns-views-into-tools-for-agents/) lets large language models (LLMs) call your indexed views as real-time tools.
The MCP Server automatically turns any indexed view with a comment into a callable, typed interface that LLMs can use to fetch structured, up-to-date answers—directly from the database.

These tools behave like stable APIs.
They're governed by your SQL privileges, kept fresh by Materialize's incremental view maintenance, and ready to power applications that rely on live context instead of static embeddings or unpredictable prompt chains.

## Get Started

We recommend using [uv](https://docs.astral.sh/uv/) to install and run the server.
It provides fast, reliable Python environments with dependency resolution that matches pip.

If you don't have uv installed, you can install it first:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

To install and launch the MCP Server for Materialize:

```bash
uv venv
uv pip install mcp-materialize-agents
uv run mcp_materialize_agents
```

You can configure it using CLI flags or environment variables:

| Flag              | Env Var             | Default                                               | Description                                   |
| ----------------- | ------------------- | ----------------------------------------------------- | --------------------------------------------- |
| `--mz-dsn`        | `MZ_DSN`            | `postgres://materialize@localhost:6875/materialize`   | Materialize connection string                 |
| `--transport`     | `MCP_TRANSPORT`     | `stdio`                                               | Communication mode (`stdio`, `sse`, or `http`) |
| `--host`          | `MCP_HOST`          | `0.0.0.0`                                             | Host for `sse` and `http` modes               |
| `--port`          | `MCP_PORT`          | `3001` (sse), `8001` (http)                           | Port for `sse` and `http` modes               |
| `--pool-min-size` | `MCP_POOL_MIN_SIZE` | `1`                                                   | Minimum DB pool size                          |
| `--pool-max-size` | `MCP_POOL_MAX_SIZE` | `10`                                                  | Maximum DB pool size                          |
| `--log-level`     | `MCP_LOG_LEVEL`     | `INFO`                                                | Logging verbosity                             |

## Define Tools

Any view in Materialize can become a callable tool as long as it meets a few requirements to ensure that the tool is fast to query, safe to expose, and easy for language models to use correctly.

- [The view is indexed.](#1-define-and-index)
- [The view includes a top level comment.](#2-comment)
- [The role used to run the MCP Server must have required privileges.](#3-set-rbac-permissions)

### 1. Define and Index

You must create at least one [index](/concepts/indexes/) on the view. The columns in the index define the required input fields for the tool.

You can index a single column:

```mzsql
CREATE INDEX ON payment_status_summary (order_id);
```

Or multiple columns:

```mzsql
CREATE INDEX ON payment_status_summary (user_id, order_id);
```

Every indexed column becomes part of the tool's input schema.

### 2. Comment

The view must include a top-level comment that is used as the tool's description.
Comments should be descriptive as they help the model reason about what the tool does and when to use it.
You can optionally add a comment on any of the indexed columns to improve the tool's schema with descriptions for each field.

```mzsql
COMMENT ON VIEW payment_status_summary IS
  'Given a user ID and order ID, return the current payment status and last update time.
   Use this tool to drive user-facing payment tracking.';

COMMENT ON COLUMN payment_status_summary.user_id IS
  'The ID of the user who placed the order';

COMMENT ON COLUMN payment_status_summary.order_id IS
  'The unique identifier for the order';
```

### 3. Set RBAC Permissions

The database role used to run the MCP Server must:

* Have `USAGE` privileges on the database and schema the view is in.
* Have `SELECT` privileges on the view.
* Have `USAGE` privileges on the cluster where the index is installed.

```mzsql
GRANT USAGE on DATABASE materialize TO mcp_server_role;
GRANT USAGE on SCHEMA materialize.public TO mcp_server_role;
GRANT SELECT ON payment_status_summary TO mcp_server_role;
GRANT USAGE ON CLUSTER mcp_cluster TO mcp_server_role;
```

## Related Pages

* [Coding Agent Skills](/integrations/coding-agent-skills/)
* [CREATE VIEW](/sql/create-view)
* [CREATE INDEX](/sql/create-index)
* [COMMENT ON](/sql/comment-on)
* [CREATE ROLE](/sql/create-role)
* [GRANT PRIVILEGE](/sql/grant-privilege)

---

## Developer endpoint configuration

## Available configuration parameters

The following configurations are available for the `/api/mcp/developer`
endpoint:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `enable_mcp_developer` | `true` | Enable or disable the `/api/mcp/developer` endpoint. When the endpoint is disabled, requests return HTTP 503 (Service Unavailable). |
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

## Privileges

The privileges required to use this endpoint are:

  * `USAGE` on system catalog schemas and `SELECT` on system catalog objects. These privileges are granted by default.

  * If agents also need access to replica-specific metrics from
    `mz_introspection`, `USAGE` privileges on the corresponding cluster.

---

## MCP Server for Developers

> **Public Preview:** This feature is in public preview.

Materialize provides a built-in Model Context Protocol (MCP) endpoint
`/api/mcp/developer` (port 6876) for troubleshooting and observability. The MCP
interface is served directly by the database; no sidecar process or external
server is required.

## Overview

The `/api/mcp/developer` endpoint provides read-only access to the system
catalog (`mz_*` tables). You can connect an MCP-compatible AI agent (such as
Claude Code, Claude Desktop, or Cursor) to the `/api/mcp/developer` endpoint and
ask natural language questions like:

- *Why is my materialized view stale?*
- *How much memory is my cluster using?*.

## Connect to the MCP server

### Step 1. Get connection details

**Cloud:**

1. Log in to the [Materialize Console](https://console.materialize.com/).
1. Click the **Connect** link (lower-left corner) to open the **Connect** modal
   and click on the **MCP Server** tab.

   ![Image of MCP tab in the Console's Connect
modal](/images/console/console-connect-mcp.png "Materialize Connect modal, MCP
tab")

1. To get your base64-encoded token:
   - To use an existing personal app password, generate a base64-encoded token.
   MCP clients send credentials as a Base64-encoded `user:password` string.

     ```bash
     printf '<user>:<app_password>' | base64 -w0
     ```

   - To create a new personal app password to use, click on the **Generate
     personal MCP token** to generate a new token for MCP Server. **Copy the
     token**.

**Self-Managed:**

1. You can connect using either an existing or new login role with password.

   - To use an existing role, go to the next step.
   - To create a new login role with password:

     ```mzsql
     CREATE ROLE my_agent LOGIN PASSWORD 'your_password_here';
     ```

1. Encode your credentials in Base64. MCP clients send credentials as a
   Base64-encoded `user:password` string.

   ```bash
   printf '<user>:<password>' | base64 -w0
   ```

   For example:
   ```bash
   printf 'svc-mcp-agent@mycompany.com:my_app_password_here' | base64 -w0
   # Output: c3ZjLW1jcC1hZ2VudEBteWNvbXBhbnkuY29tOm15X2FwcF9wYXNzd29yZF9oZXJl
   ```

1. Find your deployment's host name to use in the MCP endpoint URL; that is,
   your MCP endpoint URL is:

   ```
   http://<host>:6876/api/mcp/developer
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

To connect to the MCP server for your Emulator, use the following endpoint
(based on your deployment's base URL of `http://localhost:6876`):

```
http://localhost:6876/api/mcp/developer
```

### Step 2. Configure your MCP client

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
   | **Cloud**        | Replace with your value (format: `https://<region-id>.materialize.cloud`)  | Replace with your value       |
   | **Self-Managed** | Replace with your value (format: `http://<host>:6876`) | Replace with your value       |
   | **Emulator**     | `http://localhost:6876` | Leave the placeholder as-is |

   > **Tip:** For **Cloud**, you can get the MCP URL directly from the Console's **Connect**
   > modal. The modal displays the correct `<baseURL>`.

1. Restart Claude Code to pick up the new setting.

**Claude Desktop:**

1. Add the `materialize-developer` MCP server entry to your Claude Desktop
   configuration (`claude_desktop_config.json`).
   - When merging into an existing `mcpServers` object, remember to add commas
     between entries.
   - If the `mcpServers` field does not already exist, add it as well.
   - For older Claude Desktop versions, you may need to include the transport
     `"type": "http",` as well as part of the `materialize-developer` entry.

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
   | **Cloud**        | Replace with your value (format: `https://<region-id>.materialize.cloud`)  | Replace with your value       |
   | **Self-Managed** | Replace with your value (format: `http://<host>:6876`) | Replace with your value       |
   | **Emulator**     | `http://localhost:6876` | Leave the placeholder as-is |

   > **Tip:** For **Cloud**, you can get the MCP URL directly from the Console's **Connect**
   > modal. The modal displays the correct `<baseURL>`.

1. Restart Claude Desktop to pick up the new setting.

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
   | **Cloud**        | Replace with your value (format: `https://<region-id>.materialize.cloud`)  | Replace with your value       |
   | **Self-Managed** | Replace with your value (format: `http://<host>:6876`) | Replace with your value       |
   | **Emulator**     | `http://localhost:6876` | Leave the placeholder as-is |

   > **Tip:** For **Cloud**, you can get the MCP URL directly from the Console's **Connect**
   > modal. The modal displays the correct `<baseURL>`.

1. Restart Cursor to pick up the new setting.

**Generic HTTP:**

Any MCP-compatible client can connect by sending JSON-RPC 2.0 requests; update the `<baseURL>` and `<mcp-token>` placeholders with your values:

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

## Start asking questions

Once connected, you can ask natural language questions like:

| Question | What the agent does |
|----------|---------------------|
| **Why is my materialized view stale?** | Checks materialization lag, hydration status, replica health, and source errors. |
| **Why is my cluster running out of memory?** | Checks replica utilization, identifies the largest dataflows, and finds optimization opportunities via the built-in index advisor. |
| **Has my source finished snapshotting yet?** | Checks source statistics and status. |
| **How much memory is my cluster using?** | Checks replica utilization metrics across all clusters. |
| **What's the health of my environment?** | Checks replica statuses, source and sink health, and resource utilization. |
| **What can I optimize to save costs?** | Queries the index advisor for materialized views that can be dematerialized and indexes that can be dropped. |

The agent translates natural language questions into the appropriate system
catalog queries, uses the `query_system_catalog` tool to run those queries, and
synthesizes the results.

## Tools

### `query_system_catalog`

Execute a read-only SQL query restricted to system catalog tables (`mz_*`,
`pg_catalog`, `information_schema`).

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

## Related pages

- [Developer endpoint
  configuration](/integrations/mcp-server/mcp-developer-config/)
- [Troubleshooting](/integrations/mcp-server/mcp-server-troubleshooting/)
- [Coding Agent Skills](/integrations/coding-agent-skills/)
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

