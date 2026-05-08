# Connecting MCP Clients to the `materialize-developer` Server

This playbook covers **client-side configuration** for connecting an MCP-capable agentic coding tool (Claude Code, Cursor, VS Code, Zed, Continue, Windsurf, Claude Desktop) to a Materialize **`/api/mcp/developer`** endpoint. It does *not* cover authoring or hosting the server.

> **Living info — verify before relying.** MCP client config formats, CLI flags, and config file locations change frequently as products evolve. Each per-client subsection below links to the official docs for that client; **treat the linked doc as the source of truth and the snippets here as a starting point**. Likewise, Materialize's own MCP server docs at <https://materialize.com/docs/integrations/mcp-server/> may have updated guidance that supersedes anything here.

---

## What this connects to

| Deployment | URL pattern | Auth backend |
|---|---|---|
| **Materialize Emulator** (Docker) | `http://localhost:6876/api/mcp/developer` | None — Basic-auth username is the role; password is empty |
| **Materialize Cloud** | `https://<region-id>.materialize.cloud/api/mcp/developer` | Frontegg — Basic with `<email>:<app_password>` (or Bearer JWT) |
| **Self-managed (Password mode)** | `http(s)://<host>:6876/api/mcp/developer` | Internal password hashes — Basic with `<role>:<password>` |
| **Self-managed (OIDC mode)** | `https://<host>:6876/api/mcp/developer` | External IdP — Bearer JWT |

For deployment-specific details (where to find the URL, how to mint app passwords, how to set `enable_mcp_developer`, etc.), see the upstream docs at <https://materialize.com/docs/integrations/mcp-server/>:

- Endpoint overview: <https://materialize.com/docs/integrations/mcp-server/mcp-developer/>
- Server configuration: <https://materialize.com/docs/integrations/mcp-server/mcp-developer-config/>
- Troubleshooting: <https://materialize.com/docs/integrations/mcp-server/mcp-server-troubleshooting/>

---

## Authentication header — what to put where

The server reads either header type:

```
Authorization: Basic <base64(username:password)>
Authorization: Bearer <jwt>
```

The Basic password may be **empty** in the Emulator, but **must be non-empty** in any real deployment.

### Building the Basic token

```sh
# Materialize Emulator (no password)
printf 'my_dev_agent:' | base64

# Self-managed (Password mode)
printf 'my_agent:s3cret' | base64

# Materialize Cloud
printf 'svc-agent@example.com:<app_password>' | base64
```

> The README/docs sometimes show `base64 -w0`. That flag is GNU coreutils only; **macOS BSD `base64` rejects `-w0`** but produces single-line output by default, so just drop the flag.

### Roles vs. users by deployment

- **Emulator** — credentials *are* a role. `CREATE ROLE my_dev_agent` then encode `my_dev_agent:`.
- **Self-managed (Password)** — credentials are a login role with a password: `CREATE ROLE my_agent LOGIN PASSWORD '...'`.
- **Cloud** — credentials are a *user* (email) plus an **app password** generated from the Console (Connect modal → MCP Server tab). The user inherits the union of grants from all roles they're a member of; `SET ROLE` is **not** available through the MCP query tool, so to scope the agent's privileges you typically create a dedicated user with restricted role membership.

---

## Choosing the user/role at runtime — three patterns

These patterns are deployment-agnostic; only the *contents* of the auth token differ by deployment.

### Pattern A — env-var rotation (recommended)

Store the placeholder in the client config; populate the env var in the shell that launches the client:

```jsonc
"headers": { "Authorization": "Basic ${MCP_DEV_TOKEN}" }
```

```sh
# Helper for any deployment:
mcp_as_basic() { export MCP_DEV_TOKEN="$(printf '%s' "$1" | base64)"; }
mcp_as_bearer() { export MCP_DEV_TOKEN="$1"; }   # if you also flip the header to Bearer

# Examples:
mcp_as_basic 'my_dev_agent:'                       # Emulator
mcp_as_basic 'my_agent:s3cret'                     # Self-managed
mcp_as_basic 'svc-agent@example.com:<app_pw>'     # Cloud
```

In Claude Code you can rotate the value without losing your conversation: `^C^C` out, re-export, then `claude --continue`.

### Pattern B — multiple registrations, one per identity

Register the same URL multiple times under different names with literal Authorization headers:

```sh
claude mcp add-json materialize-as-readonly \
  '{"type":"http","url":"http://localhost:6876/api/mcp/developer","headers":{"Authorization":"Basic <base64-of-readonly>"}}'

claude mcp add-json materialize-as-admin \
  '{"type":"http","url":"http://localhost:6876/api/mcp/developer","headers":{"Authorization":"Basic <base64-of-admin>"}}'
```

Both connect simultaneously; tools from each are namespaced under the registration name. Useful for comparing what different identities can see.

### Pattern C — edit the client config JSON directly

Functionally identical to Pattern B but inside the existing registration's file. Use when you want to flip identity once without re-registering.

### Caveats

- Cloud **app passwords are non-recoverable**. Lost ones must be regenerated from the Console.
- OIDC **Bearer tokens expire**. Pattern A makes refresh trivial (re-export + `claude --continue`); Pattern B/C are awkward for rotating tokens.
- The MCP query tool **blocks `SET` statements**, so post-auth role-switching does not work — pick the right principal at connect time.
- In Cloud, the role of record is the *user*, not a SQL role. To scope an agent narrowly, mint a dedicated user with restricted role membership rather than expecting `SET ROLE` to confine it.

---

## Per-client configuration

Each subsection points at the client's official docs. **Verify against the linked page** — these snippets reflect the state of each client at this writing and tend to drift.

### Claude Code

Official docs: <https://code.claude.com/docs/en/mcp>

- Wrapper key: `mcpServers`
- CLI-first; `~/.claude.json` (local/user scope) or `.mcp.json` at project root (project scope)
- Three scopes: `local` (default, per-user-per-project), `project` (committed `.mcp.json`, team-shared), `user` (per-user, all projects)

```sh
claude mcp add-json materialize-developer \
  '{"type":"http","url":"http://localhost:6876/api/mcp/developer","headers":{"Authorization":"Basic ${MCP_DEV_TOKEN}"}}'
```

Equivalent project-committed `.mcp.json`:

```json
{
  "mcpServers": {
    "materialize-developer": {
      "type": "http",
      "url": "http://localhost:6876/api/mcp/developer",
      "headers": { "Authorization": "Basic ${MCP_DEV_TOKEN}" }
    }
  }
}
```

Tools are discovered at session start. After registering a server or rotating `MCP_DEV_TOKEN`, either restart Claude Code or `^C^C` and `claude --continue` to keep your conversation context.

### Claude Desktop

Official docs: <https://modelcontextprotocol.io/quickstart/user>

- Wrapper key: `mcpServers`
- Config file:
  - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
  - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
  - Linux: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "materialize-developer": {
      "url": "http://localhost:6876/api/mcp/developer",
      "headers": { "Authorization": "Basic <base64-token>" }
    }
  }
}
```

Restart the app after editing. Settings → Developer also exposes a GUI editor.

### Cursor

Official docs: <https://docs.cursor.com/context/model-context-protocol>

- Wrapper key: `mcpServers`
- Config file: `.cursor/mcp.json` (project) or `~/.cursor/mcp.json` (global). Project overrides global on name collision.

```json
{
  "mcpServers": {
    "materialize-developer": {
      "type": "http",
      "url": "http://localhost:6876/api/mcp/developer",
      "headers": { "Authorization": "Basic <base64-token>" }
    }
  }
}
```

**Cursor reloads MCP config only on startup** — fully quit (including the menu-bar item, not just the window) and relaunch after editing. No first-class secret store for remote servers; the token sits in the config file.

### VS Code (GitHub Copilot Chat)

Official docs:
- <https://code.visualstudio.com/docs/copilot/customization/mcp-servers>
- Config reference: <https://code.visualstudio.com/docs/copilot/reference/mcp-configuration>

- Wrapper key: **`servers`** (not `mcpServers` — direct paste from other clients won't work)
- Config file: `.vscode/mcp.json` (workspace) or user profile (synced via Settings Sync)

```json
{
  "servers": {
    "materialize-developer": {
      "type": "http",
      "url": "http://localhost:6876/api/mcp/developer",
      "headers": { "Authorization": "Basic ${input:mz-dev-token}" }
    }
  },
  "inputs": [
    {
      "type": "promptString",
      "id": "mz-dev-token",
      "description": "base64 of <user>:<app_password> (or <role>: for Emulator)",
      "password": true
    }
  ]
}
```

`${input:...}` prompts on first use and stores the value in the OS keychain — preferred over inlining the token. VS Code also supports a per-server `sandbox` block (filesystem/network restrictions); see the config reference.

### Zed

Official docs: <https://zed.dev/docs/ai/mcp>

- Wrapper key: **`context_servers`** (not `mcpServers`)
- Config file: `.zed/settings.json` (project) or `~/.config/zed/settings.json` (global)

```json
{
  "context_servers": {
    "materialize-developer": {
      "url": "http://localhost:6876/api/mcp/developer",
      "headers": { "Authorization": "Basic <base64-token>" }
    }
  }
}
```

Zed supports MCP **Tools** and **Prompts** only; Discovery, Sampling, and Elicitation are not implemented as of late 2025 — verify current status against the linked doc. Tool permission default is set via `agent.tool_permissions.default` (`confirm` / `allow` / `deny`).

### Continue

Official docs: <https://docs.continue.dev/customization/mcp-tools>

- Wrapper key: `mcpServers` — but **as files in a directory**, one per server, each containing a JSON object with a `name` field
- Config location: `.continue/mcpServers/`

`.continue/mcpServers/materialize-developer.json`:

```json
{
  "name": "materialize-developer",
  "type": "http",
  "url": "http://localhost:6876/api/mcp/developer",
  "headers": { "Authorization": "Basic ${{ secrets.MZ_DEV_TOKEN }}" }
}
```

Use `${{ secrets.NAME }}` for credentials; secrets are stored separately from the config file. Continue auto-detects drops of Claude Desktop / Cursor / Cline configs into `.continue/mcpServers/` — no manual conversion needed.

### Windsurf

Official docs: <https://docs.windsurf.com/windsurf/mcp>

- Wrapper key: `mcpServers`
- Config file: `~/.codeium/windsurf/mcp_config.json`
- URL field: **`serverUrl`** (not `url`)

```json
{
  "mcpServers": {
    "materialize-developer": {
      "serverUrl": "http://localhost:6876/api/mcp/developer",
      "headers": { "Authorization": "Basic <base64-token>" }
    }
  }
}
```

The Cascade UI has a "Refresh" button that reloads MCP config without a full restart.

---

## Cross-client cheat sheet

| Client | Wrapper key | Primary config file | URL field |
|---|---|---|---|
| Claude Code | `mcpServers` | `~/.claude.json` (local/user), `.mcp.json` (project) | `url` |
| Claude Desktop | `mcpServers` | `claude_desktop_config.json` (per-OS path) | `url` |
| Cursor | `mcpServers` | `.cursor/mcp.json` or `~/.cursor/mcp.json` | `url` |
| VS Code | `servers` | `.vscode/mcp.json` | `url` |
| Zed | `context_servers` | `.zed/settings.json` or `~/.config/zed/settings.json` | `url` |
| Continue | `mcpServers` (files in dir) | `.continue/mcpServers/<name>.json` | `url` |
| Windsurf | `mcpServers` | `~/.codeium/windsurf/mcp_config.json` | `serverUrl` |

---

## Verifying the connection

Before launching the client, you can prove the URL + auth header pair work with a stateless JSON-RPC POST. The Materialize MCP server responds without requiring a session handshake.

```sh
# tools/list — proves auth + transport
curl -sS -X POST <baseURL>/api/mcp/developer \
  -H "Authorization: Basic <base64-token>" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'

# Identify the connected role/user — proves which principal the token resolves to
curl -sS -X POST <baseURL>/api/mcp/developer \
  -H "Authorization: Basic <base64-token>" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"query_system_catalog","arguments":{"sql_query":"SELECT current_role FROM mz_catalog.mz_databases LIMIT 1"}}}'
```

Note: `query_system_catalog` requires the SQL to **reference at least one `mz_*` / `pg_catalog` / `information_schema` table** — a bare `SELECT current_role` is rejected with `Query must reference at least one system catalog table`.

A 422 response indicates the credentials don't resolve to a known principal (typo in the role name, wrong app password, expired JWT). HTTP 503 means the `enable_mcp_developer` system parameter is `false` — see the [server config docs](https://materialize.com/docs/integrations/mcp-server/mcp-developer-config/).

---

## Common gotchas

- **Wrong wrapper key.** A Claude Code config pasted into VS Code (`mcpServers` vs `servers`) silently produces zero tools. Same for Zed (`context_servers`).
- **Wrong URL field.** Windsurf uses `serverUrl`, not `url`. Easy to miss when copying from another client.
- **Continue's directory format.** One JSON file per server inside `.continue/mcpServers/`, each with a `name` field — not a single config file with an array or object.
- **Cursor's startup-only loading.** Edits during a session don't take effect; users assume the config is wrong when it's just stale.
- **`base64 -w0` on macOS.** Drop the flag on Darwin.
- **Empty password is Emulator-only.** Real deployments will reject `<role>:` (empty password) with HTTP 422.
- **TLS redirect on Cloud / TLS-enabled self-managed.** Hitting plain `http://` returns a redirect to `https://`. Some clients follow it; some don't. Specify `https://` in the URL up front.
- **`SET` is blocked.** You cannot switch role/cluster after auth via `query_system_catalog`. Pick the right principal in the auth header, or use `mz_catalog_server` defaults.
- **Project-vs-global precedence.** Each client has its own rule; verify in the linked doc when configs collide.

---

## References

**Materialize:**
- MCP server overview — <https://materialize.com/docs/integrations/mcp-server/>
- `materialize-developer` endpoint — <https://materialize.com/docs/integrations/mcp-server/mcp-developer/>
- Developer endpoint configuration — <https://materialize.com/docs/integrations/mcp-server/mcp-developer-config/>
- MCP server troubleshooting — <https://materialize.com/docs/integrations/mcp-server/mcp-server-troubleshooting/>

**Per-client (official docs only):**
- Claude Code MCP — <https://code.claude.com/docs/en/mcp>
- Claude Desktop quickstart — <https://modelcontextprotocol.io/quickstart/user>
- Cursor MCP — <https://docs.cursor.com/context/model-context-protocol>
- VS Code MCP servers — <https://code.visualstudio.com/docs/copilot/customization/mcp-servers>
- VS Code MCP configuration reference — <https://code.visualstudio.com/docs/copilot/reference/mcp-configuration>
- Zed MCP — <https://zed.dev/docs/ai/mcp>
- Continue MCP — <https://docs.continue.dev/customization/mcp-tools>
- Windsurf MCP — <https://docs.windsurf.com/windsurf/mcp>

**Protocol:**
- Model Context Protocol specification — <https://modelcontextprotocol.io/specification>
