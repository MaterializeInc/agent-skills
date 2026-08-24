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
[Get started](/manage/mz-deploy/get-started/#prerequisites-and-installation).

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
| **[dbt](/manage/dbt/)** | Teams already invested in dbt. Manages views and materialized views. | No (clusters, connections, secrets are out of scope) | Yes (via `dbt-materialize` adapter macros) |
| **[Terraform](/manage/terraform/)** | Teams managing Materialize alongside other cloud infrastructure. | Yes | No |

## Available guides

<div class="multilinkbox">
<div class="linkbox ">
  <div class="title">
    To get started
  </div>
  <a href="/manage/mz-deploy/get-started/" >Get started with mz-deploy</a>
</div>

<div class="linkbox ">
  <div class="title">
    Develop
  </div>
  <ul>
<li><a href="/manage/mz-deploy/project-structure/" >Project structure</a></li>
<li><a href="/manage/mz-deploy/infrastructure/" >Infrastructure</a></li>
<li><a href="/manage/mz-deploy/local-development/" >Local development</a></li>
<li><a href="/manage/mz-deploy/editor-setup/" >Editor setup</a></li>
<li><a href="/manage/mz-deploy/agent-setup/" >AI agent setup</a></li>
</ul>

</div>

<div class="linkbox ">
  <div class="title">
    Deploy
  </div>
  <ul>
<li><a href="/manage/mz-deploy/deployments/" >Deployments</a></li>
<li><a href="/manage/mz-deploy/stable-apis/" >Stable APIs</a></li>
<li><a href="/manage/mz-deploy/profiles/" >Profiles</a></li>
</ul>

</div>

</div>

---

## AI agent setup

`mz-deploy` was built with AI coding agents in mind. Every new project ships
with agent-readable documentation, the CLI provides agent-optimized help, and
the language server gives agents real-time feedback on SQL correctness.

## Project skill

The community [MaterializeInc/agent-skills](https://github.com/MaterializeInc/agent-skills)
repo publishes an agent skill for `mz-deploy` that teaches agents your
project's conventions: one object per file, file paths map to qualified
names, how the deployment lifecycle works, unit test syntax, and how to get
detailed help with `mz-deploy help <command>`.

The skill is not installed by default. Install it in your project with:

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

---

## Deployments

`mz-deploy` gives you a complete lifecycle from local development through
production deployment:

```nofmt
compile ──▶ test ──▶ dev ──▶ stage ──▶ wait ──▶ promote
  local      local   real env  real env
```

[`compile`](/manage/mz-deploy/local-development/#compile-and-validate) and
[`test`](/manage/mz-deploy/local-development/#write-and-run-unit-tests) run
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
See [Stable APIs](/manage/mz-deploy/stable-apis/) for details.

---

## Editor setup

`mz-deploy` includes a language server that gives your editor deep
understanding of your project — not just SQL syntax, but cross-file
dependencies, column schemas, and Materialize-specific features.

## What the language server provides

- **Parse error diagnostics** — SQL syntax errors appear inline as you type.
- **Go-to-definition** — Click a table or view name to jump to the file that
  defines it, across your entire project.
- **Find references** — See every object that depends on the one under your
  cursor.
- **Completions** — Context-aware suggestions for column names, object names,
  functions, and keywords. Column completions are scoped to your file's actual
  dependencies.
- **Hover** — Hover over an object to see its column schema (names, types,
  nullability) pulled from `types.lock` or the internal type cache.
- **Document symbols** — Outline view showing the primary object, indexes,
  constraints, grants, and unit tests in each file.
- **Workspace symbols** — Fuzzy-find any object across your project by name.
- **Code lens** — Clickable "Run Test" above unit tests and "Explain" above
  materialized views.

## VS Code

Install the [Materialize mz-deploy extension](https://marketplace.visualstudio.com/items?itemName=MaterializeInc.mz-deploy)
from the VS Code Marketplace — search for **mz-deploy** in the Extensions view,
or install it from the command line:

```shell
code --install-extension MaterializeInc.mz-deploy
```

The extension activates automatically when your workspace contains a
`project.toml`.

The extension adds:

- All language server features listed above.
- A **data catalog sidebar** for browsing objects, columns, and metadata.
- A **dependency graph panel** for visualizing how objects relate.
- **Keyword highlighting** that understands SQL strings, comments, and
  identifiers.

To configure a custom binary path, add to your VS Code settings:

```json
{
  "mz-deploy.path": "/path/to/mz-deploy"
}
```

## Neovim

Using [nvim-lspconfig](https://github.com/neovim/nvim-lspconfig):

```lua
local lspconfig = require('lspconfig')
local configs = require('lspconfig.configs')

configs.mz_deploy = {
  default_config = {
    cmd = { 'mz-deploy', 'lsp', '-d', '.' },
    filetypes = { 'sql' },
    root_dir = lspconfig.util.root_pattern('project.toml'),
  },
}

lspconfig.mz_deploy.setup({})
```

## Helix

Add to your `languages.toml`:

```toml
[[language]]
name = "sql"
language-servers = ["mz-deploy"]

[language-server.mz-deploy]
command = "mz-deploy"
args = ["lsp", "-d", "."]
```

## How it works

The language server communicates over stdio using the standard LSP protocol.
Start it manually with:

```bash
mz-deploy lsp -d <project-root>
```

Diagnostics update on every keystroke. The project model (used for
go-to-definition, completions, and references) rebuilds on file save. If a
rebuild fails, the last successful model is kept so navigation continues
working.

---

## Get started with mz-deploy

> **Warning:** `mz-deploy` is a v0.2 release and is not yet recommended for production use.

`mz-deploy` is a deployment tool that gives you compile-time validation, unit
testing, and zero-downtime blue/green deployments for Materialize — all from
plain SQL files in a git repository. This quickstart walks you through creating
a project and deploying it.

## Prerequisites and installation

Before you begin, you need:

- A running Materialize instance ([Materialize Cloud](https://materialize.com/register/) or [self-managed](/self-managed-deployments/)).

On macOS and Linux, we recommend installing `mz-deploy` with
[Homebrew](https://brew.sh/):

```shell
brew install materializeinc/materialize/mz-deploy
```

Alternatively, download the latest release for your platform:

**macOS:**

```shell
ARCH=$(uname -m)
sudo -v
curl -L "https://binaries.materialize.com/mz-deploy-latest-$ARCH-apple-darwin.tar.gz" \
| sudo tar -xzC /usr/local --strip-components=1
```

**Linux:**

```shell
ARCH=$(uname -m)
sudo -v
curl -L "https://binaries.materialize.com/mz-deploy-latest-$ARCH-unknown-linux-gnu.tar.gz" \
| sudo tar -xzC /usr/local --strip-components=1
```

Verify the installation:

```shell
mz-deploy --version
```

Docker is required for `mz-deploy test` and `mz-deploy explain` (see [Local development](/manage/mz-deploy/local-development/)).

## Create a project

```bash
mz-deploy new order-monitoring
cd order-monitoring
```

This scaffolds the following directory structure:

```nofmt
order-monitoring/
├── models/
│   └── materialize/
│       └── public/        # SQL files → materialize.public.<filename>
├── clusters/              # Cluster definitions
├── roles/                 # Role definitions
├── network-policies/      # Network policy definitions
├── project.toml           # Project configuration
├── README.md
└── .gitignore
```

The path of each SQL file under `models/` determines the fully qualified object
name in Materialize: `models/<database>/<schema>/<object>.sql` maps to
`database.schema.object`. For example,
`models/materialize/public/stalled_orders.sql` creates the object
`materialize.public.stalled_orders`.

## Configure connection profiles

Create the file `~/.mz/profiles.toml` with your Materialize connection details:

```toml
[default]
host = "<your-materialize-host>"
port = 6875
username = "<your-username>"
password = "<your-password>"
```

Tell mz-deploy which profile to use for your checkout:

```bash
mz-deploy profile set default
```

The setting is local to your checkout — teammates can pick their own
default without affecting you. For one-off overrides, pass `--profile` or
set `MZ_DEPLOY_PROFILE`.

Verify the connection:

```bash
mz-deploy debug
```

This prints your active profile, Docker status, environment ID, and the
health of the deployment server cluster, confirming that `mz-deploy` can
reach your instance. For an interactive psql shell against the active
profile, use `mz-deploy sql` (requires `psql` on your `PATH`).

> **Tip:** As a best practice, we strongly recommend using [service accounts](/security/cloud/users-service-accounts/create-service-accounts) to connect external applications, like mz-deploy, to Materialize.

## Define a cluster

Create `clusters/orders.sql`:

```sql
-- clusters/orders.sql
CREATE CLUSTER orders (SIZE = '25cc');
```

## Define a view

Create `models/materialize/public/order_summary.sql`:

```sql
-- models/materialize/public/order_summary.sql
CREATE VIEW order_summary AS
SELECT
    status,
    COUNT(*) AS order_count,
    SUM(amount) AS total_amount
FROM orders
GROUP BY status;

CREATE INDEX order_summary_status_idx IN CLUSTER orders
ON order_summary (status);

COMMENT ON VIEW order_summary IS
    'Aggregated order counts and totals by status.';
```

Each model file contains one primary `CREATE` statement, plus optional companion
statements like `CREATE INDEX`, `COMMENT ON`, and `GRANT`. See
[Project structure](/manage/mz-deploy/project-structure/) for full details.

## Compile

```bash
mz-deploy compile
```

`mz-deploy compile` validates your SQL and dependencies locally without a
database connection. It catches parse errors, circular dependencies, and type
mismatches. See [Local development](/manage/mz-deploy/local-development/) for
the full compile, test, and explain workflow.

## Deploy

```bash
mz-deploy setup
mz-deploy stage
mz-deploy wait <deploy-id>
mz-deploy promote <deploy-id>
```

- `setup` creates the deployment tracking tables, the deployment server
  cluster that every connection runs against, and — when RBAC is enabled —
  the access-control roles. This is a one-time step.
- `stage` compiles the project, diffs against production, and deploys changed
  objects to staging schemas.
- `wait` monitors cluster hydration until all materialized views are ready.
- `promote` atomically swaps staging into production.

See [Deployments](/manage/mz-deploy/deployments/) for flags, error handling, and
deployment management.

## Next steps

- [Project structure](/manage/mz-deploy/project-structure/) — model files, companion statements, configuration
- [Infrastructure](/manage/mz-deploy/infrastructure/) — secrets, connections, sources, tables
- [Local development](/manage/mz-deploy/local-development/) — type checking, unit tests, query plans
- [Editor setup](/manage/mz-deploy/editor-setup/) — VS Code, Neovim, Helix integration
- [AI agent setup](/manage/mz-deploy/agent-setup/) — Claude Code, Codex, and other coding agents
- [Deployments](/manage/mz-deploy/deployments/) — staging, hydration, promotion, management
- [Stable APIs](/manage/mz-deploy/stable-apis/) — cross-team data products and data mesh
- [Profiles](/manage/mz-deploy/profiles/) — multi-environment configuration

---

## Infrastructure

`mz-deploy apply` converges your infrastructure objects declaratively — it creates what's missing and alters what has drifted. This page covers all object types managed by `apply`.

## Overview

`mz-deploy apply` applies all types in dependency order: clusters → roles → network policies → secrets → connections → sources → tables. Each step is idempotent — running `apply` multiple times converges to the same state.

Preview changes before applying:

```bash
mz-deploy apply --dry-run
```

Skip secrets (useful in CI where secret values aren't available):

```bash
mz-deploy apply --skip-secrets
```

You can also target individual object types with subcommands for granular control:

```bash
mz-deploy apply clusters
mz-deploy apply secrets
```

## Clusters

```sql
-- clusters/orders.sql
CREATE CLUSTER orders (SIZE = '25cc');
```

`apply` creates missing clusters and alters drifted configuration. Grants and comments are applied idempotently.

## Roles

```sql
-- roles/order_reader.sql
CREATE ROLE order_reader;
```

## Secrets

Secret values use client-side provider functions that are resolved at `apply` time. This means `compile` works without access to actual secret values.

Use `env_var()` to read values from environment variables:

```sql
-- models/materialize/public/pg_user.sql
CREATE SECRET pg_user AS env_var('PG_USER');
```

```sql
-- models/materialize/public/pg_password.sql
CREATE SECRET pg_password AS env_var('PG_PASSWORD');
```

Alternatively, use `aws_secret()` to pull values from AWS Secrets Manager:

```sql
-- models/materialize/public/pg_password.sql
CREATE SECRET pg_password AS aws_secret('prod/pg-password');
```

`aws_secret()` requires an `aws_profile` in your `project.toml`:

```toml
[profiles.default.security]
aws_profile = "my-aws-profile"
```

`apply secrets` is idempotent — it runs `CREATE SECRET IF NOT EXISTS` then `ALTER SECRET` to update the value.

## Connections

Postgres connection using secrets:

```sql
-- models/materialize/public/pg_conn.sql
CREATE CONNECTION pg_conn TO POSTGRES (
    HOST 'my-postgres.example.com',
    DATABASE 'app',
    USER SECRET pg_user,
    PASSWORD SECRET pg_password,
    SSL MODE 'require'
);
```

## Sources

Postgres source:

```sql
-- models/materialize/public/pg_source.sql
CREATE SOURCE pg_source
IN CLUSTER orders
FROM POSTGRES CONNECTION pg_conn
(PUBLICATION 'mz_source');
```

## Tables

```sql
-- models/materialize/public/orders.sql
CREATE TABLE orders FROM SOURCE pg_source
(REFERENCE public.orders);
```

After `apply tables`, the table's column schema is automatically captured in `types.lock`. This is how `compile` knows what columns `orders` has when type-checking views that reference it. See [Local development — Lock types](/manage/mz-deploy/local-development/#lock-types) for details.

---

## Local development

`mz-deploy` provides a local development workflow for validating SQL before
deploying: type-check with `compile`, test with `test`, and inspect query plans
with `explain`.

## External dependencies

Objects your project references but doesn't own must be declared in
`project.toml`:

```toml
dependencies = [
    "other_project.public.customers",
]
```

Tables and sources that your project manages (created via `apply`) are
auto-discovered and do not need to be declared.

## Lock types

`types.lock` captures column schemas (names, types, nullability) for tables,
sources, and external dependencies. It enables offline type-checking during
`compile` and schema validation during `test`.

Two categories of objects are tracked:

1. **Project-managed tables and sources** — auto-discovered. Running
   `apply tables` regenerates the lock file automatically.
2. **External dependencies** — declared in `project.toml`.

```bash
mz-deploy lock
```

This connects to your Materialize instance, fetches schemas, and writes
`types.lock`.

- Commit `types.lock` to version control.
- Re-run `mz-deploy lock` when external schemas change.
- Without `types.lock`, `compile` cannot verify column names and types.

## Compile and validate

```bash
mz-deploy compile
```

`compile` runs entirely locally with no database connection and no Docker. It:

- Parses all SQL files.
- Resolves inter-object dependencies (topological sort).
- Type-checks every statement using `types.lock`.
- Skips unchanged objects via incremental caching.

What it catches: parse errors, circular dependencies, type mismatches, and
missing dependencies.

```bash
mz-deploy compile -v
```

Verbose mode shows the dependency graph, deployment order, and full SQL plan.

Use `compile` as your inner development loop: edit, compile, fix, repeat.
Feedback is instant.

## Write and run unit tests

> **Note:** Docker must be running to execute tests. Tests use a local Materialize container
> and do not affect your remote database.

Tests use the [`EXECUTE UNIT TEST`](/sql/execute-unit-test/) syntax and live
inline in the same `.sql` file as the view they test.

Here is a full example appended to the stalled_orders model file:

```sql
-- models/materialize/public/stalled_orders.sql
EXECUTE UNIT TEST test_stalled_order_detected
FOR materialize.public.stalled_orders
AT TIME '2024-06-15T12:00:00Z'
MOCK materialize.public.orders(
    id bigint, customer text, status text,
    amount numeric, created_at timestamptz, updated_at timestamptz
) AS (
  SELECT * FROM VALUES
    (1, 'acme', 'pending', 99.99,
     '2024-06-15T10:00:00Z'::timestamptz,
     '2024-06-15T11:00:00Z'::timestamptz)
)
EXPECTED(
    id bigint, customer text, amount numeric,
    created_at timestamptz, updated_at timestamptz, stalled_for interval
) AS (
  SELECT * FROM VALUES
    (1, 'acme', 99.99,
     '2024-06-15T10:00:00Z'::timestamptz,
     '2024-06-15T11:00:00Z'::timestamptz,
     INTERVAL '1 hour')
);
```

Key concepts:

- Every dependency needs a `MOCK` clause with typed columns and sample data.
- `EXPECTED` defines the rows the view should produce.
- `AT TIME` sets `mz_now()` for deterministic testing of temporal filters.
- Tests run in an isolated local Docker container.

Run all tests:

```bash
mz-deploy test
```

Run a filtered subset:

```bash
mz-deploy test 'materialize.public.*'
```

Export results for CI:

```bash
mz-deploy test --junit-xml results.xml
```

## Explain query plans

> **Note:** Requires Docker; no live Materialize connection is needed. The command stages
> the target's dependencies in a temporary schema inside an ephemeral local
> Materialize container.

```bash
mz-deploy explain materialize.public.stalled_orders
```

`explain` compiles the project, stages the target and its dependencies in a
temporary schema, runs `EXPLAIN`, and then cleans up.

To explain an index, use the `#` separator:

```bash
mz-deploy explain materialize.public.stalled_orders#stalled_orders_customer_idx
```

All objects are created on the `quickstart` cluster regardless of your project's
cluster configuration.

## Next step: iterate against production data

Once your changes compile and pass tests locally, use
[`dev`](/manage/mz-deploy/deployments/#iterate-against-production-data)
to validate behavior against real production data. `dev` creates a
per-developer overlay database containing only your dirty views and
requires the `materialize_developer` role — no deployer permissions
needed.

---

## Profiles

Profiles let you target different Materialize environments (staging, production)
from the same project. Each profile defines connection details and can customize
cluster sizes, connection hosts, and secret resolution.

## Multiple profiles

Define profiles in `profiles.toml`. Each section header is a profile name:

```toml
[default]
host = "localhost"
port = 6875
username = "materialize"

[staging]
host = "staging.example.com"
username = "deploy_bot"
password = "${STAGING_PASSWORD}"

[production]
host = "production.example.com"
username = "deploy_bot"
password = "${PROD_PASSWORD}"
```

The active profile is resolved in this order:

1. The `--profile` flag on the command line.
2. The `MZ_DEPLOY_PROFILE` environment variable.
3. The per-checkout default recorded by `mz-deploy profile set`.

Each developer on a team sets their own default without touching shared
configuration:

```bash
mz-deploy profile list         # show every profile and which one is active
mz-deploy profile set staging  # record `staging` as the default for this checkout
mz-deploy profile current      # confirm what will be used and where it came from
```

## Built-in emulator profile

A profile named `emulator` is always available, even before you write a
`profiles.toml`. It connects to a local Materialize emulator on `localhost:6875`
as user `materialize`, so you can deploy against the emulator with no
configuration:

```bash
mz-deploy stage --profile emulator
```

Defining your own `emulator` profile in `profiles.toml` overrides the built-in.

## Password resolution

The `password` field in `profiles.toml` supports `${VAR_NAME}` substitution.
Variables are expanded at connection time, so you never need to store secrets in
the file itself.

You can also override the password for any profile with the environment variable
`MZ_PROFILE_<NAME>_PASSWORD`, where the profile name is uppercased. This takes
precedence over the value in `profiles.toml`.

```bash
export MZ_PROFILE_STAGING_PASSWORD="my-secret"
```

## Profile suffixes

Set `profile_suffix` in `project.toml` to rename databases and clusters when
deploying with a particular profile:

```toml
[profiles.staging]
profile_suffix = "_staging"
```

With this configuration, `materialize` becomes `materialize_staging` and `orders`
becomes `orders_staging`. The suffix also rewrites `IN CLUSTER` references in
views, sources, sinks, and indexes.

Note that the suffix includes the delimiter — write `"_staging"`, not
`"staging"`.

When you combine a profile suffix with the staging deploy suffix, the names
stack: `foo` becomes `foo_staging`, then `foo_staging_a1b2c3d`.

## Per-profile SQL variables

Variables parameterize values that differ across profiles. Define them in
`project.toml`:

```toml
[profiles.staging.variables]
compute_cluster = "staging_compute"

[profiles.production.variables]
compute_cluster = "production_compute"
```

Reference variables in SQL using psql-compatible syntax:

```sql
-- models/materialize/public/order_summary.sql
CREATE MATERIALIZED VIEW order_summary
    IN CLUSTER :"compute_cluster" AS
SELECT ...;
```

Three substitution forms are available:

- `:var` — raw value, inserted as-is.
- `:'var'` — single-quoted string with escaping.
- `:"var"` — double-quoted identifier with escaping.

Variables resolve before SQL parsing. If a SQL file references a variable that is
not defined for the active profile, compilation fails with an error.

## Per-profile file overrides

For objects that differ structurally across environments (for example, connections
pointing to different hosts), use file overrides. Name the variant file with a
double-underscore suffix: `name__<profile>.sql`.

```nofmt
models/materialize/public/pg_conn.sql
models/materialize/public/pg_conn__staging.sql
```

```sql
-- models/materialize/public/pg_conn.sql (production)
CREATE CONNECTION pg_conn TO POSTGRES (
    HOST 'prod-replica.internal',
    DATABASE 'app',
    USER SECRET pg_user,
    PASSWORD SECRET pg_password,
    SSL MODE 'require'
);
```

```sql
-- models/materialize/public/pg_conn__staging.sql
CREATE CONNECTION pg_conn TO POSTGRES (
    HOST 'staging-replica.internal',
    DATABASE 'app',
    USER SECRET pg_user,
    PASSWORD SECRET pg_password,
    SSL MODE 'require'
);
```

Resolution rules:

- All variants are validated at compile time, not just the active one.
- When the active profile matches a variant, that variant wins.
- All variants must share the same primary statement type.
- Views and materialized views cannot have overrides — use variables instead.

File overrides apply to: `models/` (sources, sinks, tables, connections),
`clusters/`, `roles/`, and `network-policies/`.

## Per-profile secret configuration

You can configure which AWS profile is used when resolving `aws_secret()`
providers:

```toml
[profiles.production.security]
aws_profile = "prod-account"

[profiles.staging.security]
aws_profile = "staging-account"
```

The `aws_profile` setting controls which AWS profile is used at secret-resolution
time. Different environments can pull secrets from different AWS accounts.

---

## Project structure

An `mz-deploy` project is a directory of SQL files and configuration. Directories
map to Materialize objects, and configuration files control connection and
deployment behavior.

## Directory layout

A typical project looks like this:

```nofmt
order-monitoring/
├── models/
│   └── materialize/
│       ├── public.sql             # Schema modifier
│       └── public/
│           ├── order_summary.sql  # View definition
│           └── stalled_orders.sql # Materialized view definition
├── clusters/
│   └── orders.sql                 # Cluster definition
├── roles/
│   └── order_reader.sql           # Role definition
├── network-policies/              # Network policy definitions
├── project.toml                   # Project configuration
├── types.lock                     # Column schemas (generated)
├── README.md
└── .gitignore
```

The `models/` directory contains all schema-scoped objects: views, materialized
views, sinks, tables, sources, connections, and secrets. These live under
`models/<database>/<schema>/` because they belong to a specific database and
schema.

The `clusters/`, `roles/`, and `network-policies/` directories have their own
top-level directories because these are **global objects** — they are not scoped
to any database or schema.

## File-path-to-object-name mapping

The path of each SQL file under `models/` determines the fully qualified object
name in Materialize:

```nofmt
models/<database>/<schema>/<object>.sql  →  database.schema.object
```

For example, `models/materialize/public/stalled_orders.sql` creates the object
`materialize.public.stalled_orders`.

## Model files

Each model file contains one primary `CREATE` statement that defines the object.
Supported primary statements are:

- `CREATE VIEW`
- `CREATE MATERIALIZED VIEW`
- `CREATE SINK`
- `CREATE TABLE` / `CREATE TABLE FROM SOURCE`
- `CREATE SOURCE`
- `CREATE CONNECTION`
- `CREATE SECRET`

You can include companion statements in the same file for related configuration:
`CREATE INDEX`, `COMMENT ON`, `GRANT`.

Here is a complete example:

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
  AND updated_at < mz_now() - INTERVAL '30 minutes';

CREATE INDEX stalled_orders_customer_idx IN CLUSTER orders
ON stalled_orders (customer);

COMMENT ON MATERIALIZED VIEW stalled_orders IS
    'Orders stuck in pending status for more than 30 minutes.';

GRANT SELECT ON stalled_orders TO order_reader;
```

## Schema modifiers

A file at `models/<database>/<schema>.sql` is a schema modifier. Use it for
schema-level statements that apply to the schema as a whole rather than to a
specific object. A schema modifier can contain:

- `SET api = stable`
- `COMMENT ON SCHEMA`
- `GRANT`
- `ALTER DEFAULT PRIVILEGES`

For example:

```sql
-- models/materialize/public.sql
COMMENT ON SCHEMA public IS 'Order monitoring data model.';

GRANT USAGE ON SCHEMA public TO order_reader;
```

## Database modifiers

A file at `models/<database>.sql` is a database modifier. Use it for
database-level statements:

- `COMMENT ON DATABASE`
- `GRANT`
- `ALTER DEFAULT PRIVILEGES`

## project.toml

The `project.toml` file in your project root controls project-wide settings:

- **`mz_version`** — the Materialize version used to run `test` and `explain`
  locally (it selects the Docker image). Set to `"cloud"` to use the latest
  cloud version.
- **`dependencies`** — external dependency declarations for objects your project
  references but does not own. See [Local development](/manage/mz-deploy/local-development/)
  for details.
- **Per-profile config sections** — override settings for specific environments.
  See [Profiles](/manage/mz-deploy/profiles/) for multi-environment setup.

The active connection profile is resolved per-invocation from `--profile`,
`MZ_DEPLOY_PROFILE`, or the per-checkout default set by `mz-deploy profile
set`. See [Profiles](/manage/mz-deploy/profiles/).

## profiles.toml

The `profiles.toml` file (typically at `~/.mz/profiles.toml`) stores your
Materialize connection details. Each section defines a named profile:

```toml
[default]
host = "<your-materialize-host>"
port = 6875
username = "<your-username>"
password = "<your-password>"
```

See [Profiles](/manage/mz-deploy/profiles/) for multi-environment setup and
advanced configuration.

---

## Stable APIs

By default, when a materialized view changes, `mz-deploy` recreates it in a
staging schema and swaps the entire schema into production. This works well
within a single project — dependencies are tracked and redeployed
automatically. But consumers in **other** projects break, because the schema
swap drops and recreates the materialized view, severing any downstream
dependencies that reference it.

Stable API schemas solve this problem.

## Marking a schema as stable

Add `SET api = stable` to a [schema modifier](/manage/mz-deploy/project-structure/#schema-modifiers):

```sql
-- models/materialize/ontology.sql
SET api = stable;
```

With this in place, changed materialized views in the `ontology` schema are no
longer dropped and recreated. Instead, `mz-deploy` uses Materialize's
replacement protocol:

```sql
ALTER MATERIALIZED VIEW ... APPLY REPLACEMENT ...
```

The materialized view's computation is updated in place and its identity is
preserved. Downstream consumers — whether in the same project or a different
one — do not need to be redeployed and do not need to know the update happened.

## How it works

You deploy the same way as always — `stage`, `wait`, `promote`. `mz-deploy`
automatically detects which schemas are marked stable and handles them
accordingly. Materialized views in stable schemas are updated in place while
preserving their identity. Everything else deploys normally.

Because the object identity is preserved, a changed stable MV does not
propagate dirtiness to its dependents. Objects that depend on a stable MV are
not redeployed, even if the MV's definition changed. This prevents cascading
redeployments across project boundaries.

## The two-schema pattern

The recommended way to build a stable API is with two schemas: an **internal**
schema for your transformation logic and a **stable** schema that exposes a
clean API surface.

```nofmt
models/materialize/
├── ontology.sql            # SET api = stable
├── ontology/
│   ├── customers.sql       # Thin MV — stable API surface
│   └── orders.sql          # Thin MV — stable API surface
├── internal/
│   ├── customers_cleaned.sql   # View + index — transformation logic
│   └── orders_enriched.sql     # View + index — transformation logic
```

The **internal** schema contains views with indexes that hold all your
transformation logic. These are regular objects deployed via the normal
schema-swap mechanism.

The **stable** schema contains thin materialized views that select from the
internal views. Each MV explicitly lists its columns (never `SELECT *`) and
includes a `COMMENT ON` describing its contract:

```sql
-- models/materialize/ontology/customers.sql
CREATE MATERIALIZED VIEW customers
IN CLUSTER ontology AS
SELECT
    id,
    name,
    email,
    status,
    created_at
FROM internal.customers_cleaned;

COMMENT ON MATERIALIZED VIEW customers IS
    'Canonical customer entity. Columns: id, name, email, status, created_at.';
```

```sql
-- models/materialize/internal/customers_cleaned.sql
CREATE VIEW customers_cleaned AS
SELECT
    id,
    trim(name) AS name,
    lower(email) AS email,
    CASE WHEN active THEN 'active' ELSE 'inactive' END AS status,
    created_at
FROM orders_db.public.raw_customers;

CREATE INDEX customers_cleaned_idx IN CLUSTER ontology
ON customers_cleaned (id);
```

This separation gives you:

- **All logic in the internal schema** — easy to change, tested with unit tests,
  deployed via normal schema swap.
- **A stable API surface** — thin MVs that preserve identity across deployments.
  Other teams depend on these and are never disrupted.
- **Explicit contracts** — column lists and comments define what consumers can
  rely on.

## Building a data mesh

Stable APIs are the foundation for a data mesh architecture in Materialize.
Multiple teams can maintain independent mz-deploy projects that depend on each
other's stable schemas:

```nofmt
Ontology project              Fulfillment project
========================      ========================

internal/                     internal/
  customers_cleaned             shipments_joined
  orders_enriched               delivery_tracking

ontology/ (stable)            references:
  customers          ──────▶    ontology.customers
  orders             ──────▶    ontology.orders
```

The **Ontology project** owns canonical business entities and exposes them
through a stable schema. The **Fulfillment project** builds domain-specific
views on top of the ontology. Each project:

- Has its own git repository and deployment lifecycle.
- Runs on its own cluster for independent scaling.
- Declares cross-project references as
  [external dependencies](/manage/mz-deploy/local-development/#external-dependencies)
  in `project.toml`.

When the Ontology team changes how `customers_cleaned` is computed, they deploy
normally. The `customers` MV in the stable schema is updated in place via the
replacement protocol. The Fulfillment project's views continue working without
redeployment or coordination.

## Constraints

- **Only materialized views** — stable schemas can only contain materialized
  views. Tables, views, sinks, and sources are not supported.
- **No dirtiness propagation** — a changed replacement MV does not mark its
  dependents as dirty. Dependent objects in the same project are not
  redeployed.
- **No new objects in existing stable schemas** — you cannot add a brand-new
  materialized view to a stable schema that already has production objects in a
  single deployment. Deploy the schema for the first time (or add objects when
  the schema is new), then update existing MVs in subsequent deployments.
- **Explicit column lists** — always list columns explicitly in stable MVs
  rather than using `SELECT *`. This makes the API contract visible and
  prevents accidental column additions from propagating to consumers.

