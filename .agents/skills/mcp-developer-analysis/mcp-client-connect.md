# Connecting MCP Clients to the `materialize-developer` Server

This playbook covers **client-side configuration** for connecting an MCP-capable agentic coding tool (Claude Code, Cursor, VS Code, Zed, Continue, Windsurf, Claude Desktop) to a Materialize **`/api/mcp/developer`** endpoint. It does *not* cover authoring or hosting the server.

> **Living info — verify before relying.** MCP client config formats, CLI flags, and config file locations change frequently as products evolve. Each per-client subsection below links to the official docs for that client; **treat the linked doc as the source of truth and the snippets here as a starting point**. Likewise, Materialize's own MCP server docs at <https://materialize.com/docs/integrations/mcp-server/> may have updated guidance that supersedes anything here.

---

## How to use this playbook (instructions for the agent)

This playbook is reference material. **Do not dump it in response to a general question.** The deep snippets, source citations, and per-deployment matrices below are for follow-up answers once the user has narrowed scope.

### Triage flow for a general "how do I connect" question

Examples that count as general: *"how do I connect to the Materialize developer MCP server?"*, *"what do you know about connecting?"*, *"how do I set up the Materialize MCP?"*, *"can you help me configure this?"*.

Keep the initial reply short (target ≤ 30 lines / one screen). Don't paste config snippets, source-code citations, or full deployment tables. Run this flow:

1. **One short sentence** stating what this skill helps with.

2. **List the help topics** as a bullet list — names only, no snippets:
   - Picking the right URL for the deployment (Emulator / Cloud / self-managed)
   - Building the auth header (Basic vs Bearer; role vs user)
   - Generating a config block for a specific MCP client
   - Selecting / switching the user or role at runtime
   - Verifying the connection (stateless curl probe)
   - Troubleshooting connection errors

3. **List the supported clients**, names only, on one line:

   *Claude Code · Claude Desktop · Cursor · VS Code (Copilot Chat) · Zed · Continue · Windsurf*

4. **List the three runtime patterns** for selecting the user/role, names only:
   1. Env-var rotation (placeholder in config + env var rotation)
   2. Multiple registrations (one per identity, each with its own literal `Authorization` header)
   3. Direct config edit (swap the literal token in the existing entry)

5. **Detect or ask which client the user wants help with:**
   - **If the user named a client in the prompt**, confirm that's the focus.
   - **If you can detect your runtime** — e.g. you were invoked via a Claude Code slash command, your environment shows `CLAUDE_*` vars, the working directory has `.claude/` or `claude_desktop_config.json` — name the inferred client (Claude Code or Claude Desktop) and ask the user to confirm. Important: detecting that the *harness running the agent* is Claude Code/Desktop does **not** imply the user wants help configuring that client; they may be using Claude Code to draft setup steps for a teammate using Cursor. Ask, don't assume.
   - **Otherwise**, ask the user which of the supported clients they are using (offer the list above).

6. **End with one open question:** *"What would you like help with?"*

### When the user has already narrowed scope

If the user already named a client, deployment, or specific topic (e.g., *"configure Cursor against my Cloud deployment"*, *"what's the URL for self-managed kind"*, *"why is my token rejected with 422"*), skip the triage and answer directly using the relevant section below.

**Special case — first-time setup against the Emulator with Claude Code.** If the user's request matches that pattern, route to the [Walkthrough](#walkthrough--first-time-setup-against-the-emulator-with-claude-code) section below instead of assembling steps from the deep reference content. Trigger phrases:

- *"walk me through first-time setup"*
- *"set up materialize-developer"* (with no other client/deployment named)
- *"connect Claude Code to materialize-developer"* (or *"to the Materialize MCP server"*)
- *"first-time setup"*
- Any prompt that names Claude Code + a local Emulator + the goal of getting connected, without specifying a competing identity pattern.

---

## Walkthrough — first-time setup against the Emulator with Claude Code

The canonical "minimum-drama" path for getting Claude Code talking to a local Materialize Emulator's `/api/mcp/developer` endpoint. **Scope:** Emulator (`http://localhost:6876`), Claude Code, the `my_dev_agent` role, and Pattern A (env-var rotation). For other deployments, clients, or auth patterns, use the deep reference content below this section instead.

### State-detection probes (run before each step; skip the step if state is already in place)

```sh
# 1. Emulator reachable, and is the endpoint actually enabled?
# Must be a POST: GET is answered 405 by the router before the feature flag is
# ever consulted, so it reads "up" whether or not the endpoint is enabled.
curl -sS -o /dev/null -w "%{http_code}\n" -X POST \
  http://localhost:6876/api/mcp/developer \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
# Expect: 200 (endpoint up and enabled). 503 = enable_mcp_developer is off.
# Connection refused / no response = Emulator not running; stop and direct user to environment-setup.

# 2. my_dev_agent role exists?
psql postgres://materialize@127.0.0.1:6875/materialize -tAc \
  "SELECT 1 FROM mz_roles WHERE name='my_dev_agent';"

# 3. materialize-developer registered in Claude Code?
claude mcp list 2>&1 | grep -E '^materialize-developer:'

# 4. ~/.claude.json entry uses the env-var placeholder form?
grep -A 3 '"materialize-developer"' ~/.claude.json | grep -q 'Basic ${MCP_DEV_TOKEN}'
```

### Steps

The walkthrough is **idempotent** — re-running on a partly-configured machine skips finished steps. State each skip out loud so the user sees what was already in place.

1. **Verify the Emulator is up** (probe 1). If it's not, stop with a pointer to `environment-setup/README.md` — the rest of the walkthrough cannot proceed without it.

2. **Create the role if missing** (probe 2 returned no rows):

   ```sh
   psql postgres://materialize@127.0.0.1:6875/materialize -c "CREATE ROLE my_dev_agent;"
   ```

   Expected output: `CREATE ROLE`. Materialize does not support `CREATE ROLE IF NOT EXISTS`, so probe 2 first; don't blindly retry.

3. **Register the MCP server if missing or in the wrong form** (probe 3 / probe 4):

   ```sh
   claude mcp add-json materialize-developer \
     '{"type":"http","url":"http://localhost:6876/api/mcp/developer","headers":{"Authorization":"Basic ${MCP_DEV_TOKEN}"}}'
   ```

   If a registration exists but uses a literal token (Pattern C variant), `claude mcp remove materialize-developer` first, then re-add in the placeholder form. The walkthrough is opinionated about Pattern A — the env var is the rotation point.

4. **PAUSE for the user to set the env var.** Show them, verbatim:

   ```sh
   read -s MCP_DEV_PASSWORD                                          # press Enter; Emulator user has no password
   export MCP_DEV_TOKEN="$(printf 'my_dev_agent:'"$MCP_DEV_PASSWORD" | base64)"
   unset MCP_DEV_PASSWORD
   echo "$MCP_DEV_TOKEN"                                             # expect: bXlfZGV2X2FnZW50Og==
   ```

   Wait for the user to confirm the echo matches before continuing. macOS reminder: do **not** add `-w0` to `base64`; that's GNU coreutils only.

5. **PAUSE for the user to restart Claude Code:**

   ```sh
   ^C^C
   claude --continue
   ```

   The conversation context is preserved. When the user returns ("back" / "ready" / similar), proceed.

6. **Smoke query** to prove the connection is live and identifies the right role:

   ```
   query_system_catalog: SELECT current_role FROM mz_catalog.mz_databases LIMIT 1
   ```

   Expected: `my_dev_agent`. The query needs to reference a system catalog table — a bare `SELECT current_role` is rejected with `Query must reference at least one system catalog table`.

7. **Confirm success** in one short sentence and offer a follow-up. Example: *"You're connected as `my_dev_agent`. Try `/mcp-developer-analysis what's the health of my environment?` next."*

### Failure handling

| Symptom | Likely cause | Fix |
|---|---|---|
| Smoke query returns a role other than `my_dev_agent` | The user's `MCP_DEV_TOKEN` was set to a different role's base64 | Repeat step 4 with the right `read`/`base64` invocation, then restart again. |
| Smoke query returns `anonymous_http_user` | No usable `Authorization` header reached the server: the env var was unset in the shell that launched `claude`, or the token is malformed. The Emulator downgrades both to anonymous rather than rejecting them. | Confirm `echo "$MCP_DEV_TOKEN"` in the launching shell shows `bXlfZGV2X2FnZW50Og==`; if it's empty, `export` was missed. |
| HTTP 422 on the smoke query | The request body failed to deserialize — a malformed JSON-RPC body, not a credential problem. (On Cloud and self-managed deployments a 422 can also mean unresolvable credentials.) | Check the JSON-RPC body shape, not the token. |
| HTTP 503 on the smoke query | `enable_mcp_developer` system parameter is `false` on this Emulator | See the [server config docs](https://materialize.com/docs/integrations/mcp-server/mcp-developer-config/). Not a walkthrough fix. |
| `claude mcp list` shows the server but the smoke query times out | Claude Code wasn't restarted after the env var was set | Step 5 again. |

### What the walkthrough does NOT cover

- **Cloud or self-managed setup** — different URLs, different credentials, possibly Bearer tokens. Use the deep reference content below.
- **Pattern B (multiple registrations)** or **Pattern C (literal-token edit)** — the walkthrough only sets up Pattern A. Cover those if the user explicitly asks to switch identities.
- **Skill installation** — `npx skills add MaterializeInc/agent-skills` is a terminal-side step done before the user can invoke the walkthrough at all. If the slash command isn't found, point the user there first.
- **RBAC tightening** — the walkthrough leaves `my_dev_agent` at `PUBLIC` defaults, which is appropriate for training but not for production. Direct the user to the Materialize RBAC docs for production scoping. Note that RBAC gates data, not the catalog: even a role with no object grants still reads the whole object inventory, every view and MV `definition`, and all of `mz_index_advice`. The analysis workflow therefore works for a narrowly-scoped agent role.

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
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'

# Identify the connected role/user — proves which principal the token resolves to
curl -sS -X POST <baseURL>/api/mcp/developer \
  -H "Authorization: Basic <base64-token>" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"query_system_catalog","arguments":{"sql_query":"SELECT current_role FROM mz_catalog.mz_databases LIMIT 1"}}}'
```

Note: `query_system_catalog` requires the SQL to **reference at least one `mz_*` / `pg_catalog` / `information_schema` table** — a bare `SELECT current_role` is rejected with `Query must reference at least one system catalog table`.

`tools/list` takes no `params`. Sending `"params":{}` is a type error and comes back as HTTP 422 `Failed to deserialize the JSON body ...`; drop the key entirely.

A 422 with a `Failed to deserialize` body is a malformed request, not a credential problem. On Cloud and self-managed deployments a 422 can also mean the credentials don't resolve to a known principal (typo in the role name, wrong app password, expired JWT); the Emulator never answers that way, because it auto-creates an unknown role and silently downgrades an unusable `Authorization` header to `anonymous_http_user`. So on the Emulator, read the *principal the smoke query reports*, not the status code. HTTP 503 means the `enable_mcp_developer` system parameter is `false` — see the [server config docs](https://materialize.com/docs/integrations/mcp-server/mcp-developer-config/).

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
