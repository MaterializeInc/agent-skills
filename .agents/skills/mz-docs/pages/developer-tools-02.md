<!-- mz-docs page: developer-tools/mz-deploy/editor-setup -->

# Editor setup
Configure VS Code, Neovim, or Helix with the mz-deploy language server.
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

<!-- mz-docs page: developer-tools/mz-deploy/get-started -->

# Get started with mz-deploy
Set up mz-deploy and deploy your first project to Materialize.
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

Docker is required for `mz-deploy test` and `mz-deploy explain` (see [Local development](/developer-tools/mz-deploy/local-development/)).

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
[Project structure](/developer-tools/mz-deploy/project-structure/) for full details.

## Compile

```bash
mz-deploy compile
```

`mz-deploy compile` validates your SQL and dependencies locally without a
database connection. It catches parse errors, circular dependencies, and type
mismatches. See [Local development](/developer-tools/mz-deploy/local-development/) for
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

See [Deployments](/developer-tools/mz-deploy/deployments/) for flags, error handling, and
deployment management.

## Next steps

- [Project structure](/developer-tools/mz-deploy/project-structure/) — model files, companion statements, configuration
- [Infrastructure](/developer-tools/mz-deploy/infrastructure/) — secrets, connections, sources, tables
- [Local development](/developer-tools/mz-deploy/local-development/) — type checking, unit tests, query plans
- [Editor setup](/developer-tools/mz-deploy/editor-setup/) — VS Code, Neovim, Helix integration
- [AI agent setup](/developer-tools/mz-deploy/agent-setup/) — Claude Code, Codex, and other coding agents
- [Deployments](/developer-tools/mz-deploy/deployments/) — staging, hydration, promotion, management
- [Stable APIs](/developer-tools/mz-deploy/stable-apis/) — cross-team data products and data mesh
- [Profiles](/developer-tools/mz-deploy/profiles/) — multi-environment configuration

<!-- mz-docs page: developer-tools/mz-deploy/infrastructure -->

# Infrastructure
Manage clusters, roles, secrets, connections, sources, and tables with mz-deploy apply.
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

Before creating anything, `apply tables` checks each `REFERENCE` against what its source can currently read from the upstream system. A reference the source cannot read fails the command, and the error suggests any reference the source does expose that is spelled closely enough to be the one you meant. Tables reading from a source the same command is creating are not checked ahead of time, because the source does not exist yet; those references are resolved when the table is created.

The check runs in a dry run as well as a real apply, and it is not read-only. It refreshes each source's references first, which contacts the upstream system and updates what the source records. Refreshing requires owning the source, and one you do not own is checked against the references already recorded for it.

After `apply tables`, the table's column schema is automatically captured in `types.lock`. This is how `compile` knows what columns `orders` has when type-checking views that reference it. See [Local development — Lock types](/developer-tools/mz-deploy/local-development/#lock-types) for details.

<!-- mz-docs page: developer-tools/mz-deploy/local-development -->

# Local development
Type-check, test, and inspect query plans locally before deploying.
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
[`dev`](/developer-tools/mz-deploy/deployments/#iterate-against-production-data)
to validate behavior against real production data. `dev` creates a
per-developer overlay database containing only your dirty views and
requires the `materialize_developer` role — no deployer permissions
needed.

<!-- mz-docs page: developer-tools/mz-deploy/profiles -->

# Profiles
Configure multiple environments with profiles, variables, and file overrides.
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
password = "<STAGING_PASSWORD>"

[production]
host = "production.example.com"
username = "deploy_bot"
password = "<PROD_PASSWORD>"
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
export <MZ_PROFILE_STAGING_PASSWORD>="my-secret"
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

<!-- mz-docs page: developer-tools/mz-deploy/project-structure -->

# Project structure
How mz-deploy projects are organized: directories, model files, and configuration.
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
  references but does not own. See [Local development](/developer-tools/mz-deploy/local-development/)
  for details.
- **Per-profile config sections** — override settings for specific environments.
  See [Profiles](/developer-tools/mz-deploy/profiles/) for multi-environment setup.

The active connection profile is resolved per-invocation from `--profile`,
`MZ_DEPLOY_PROFILE`, or the per-checkout default set by `mz-deploy profile
set`. See [Profiles](/developer-tools/mz-deploy/profiles/).

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

See [Profiles](/developer-tools/mz-deploy/profiles/) for multi-environment setup and
advanced configuration.

<!-- mz-docs page: developer-tools/mz-deploy/stable-apis -->

# Stable APIs
Build cross-team data products with stable API schemas that never break downstream consumers.
By default, when a materialized view changes, `mz-deploy` recreates it in a
staging schema and swaps the entire schema into production. This works well
within a single project — dependencies are tracked and redeployed
automatically. But consumers in **other** projects break, because the schema
swap drops and recreates the materialized view, severing any downstream
dependencies that reference it.

Stable API schemas solve this problem.

## Marking a schema as stable

Add `SET api = stable` to a [schema modifier](/developer-tools/mz-deploy/project-structure/#schema-modifiers):

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
  [external dependencies](/developer-tools/mz-deploy/local-development/#external-dependencies)
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

<!-- mz-docs page: developer-tools/terraform -->

# Use Terraform to manage Materialize

Create and manage Materialize resources with Terraform

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

<!-- mz-docs page: developer-tools/terraform/appendix-secret-stores -->

# Appendix: External secret stores
Materialize does not directly integrate with external secret stores, but it's possible to manage this integration via Terraform.

The [secret stores demo](https://github.com/MaterializeInc/demos/tree/main/integrations/terraform/secret-stores) shows how to handle [secrets](/sql/create-secret) and sensitive data with some popular secret stores. By utilizing Terraform's infrastructure-as-code model, you can automate and simplify both the initial setup and ongoing management of secret stores with Materialize.

A popular secret store is [HashiCorp Vault](https://www.vaultproject.io/). To use Vault with Materialize, you'll need to install the Terraform Vault provider:

```hcl
terraform {
  required_providers {
    vault = {
      source  = "hashicorp/vault"
      version = "~> 3.15"
    }
  }
}

provider "vault" {
  address = "https://vault.example.com"
  token   = "your-vault-token"
}
```

Next, fetch a secret from Vault and use it to create a new Materialize secret:

```hcl
data "vault_generic_secret" "materialize_password" {
  path = "secret/materialize"
}

resource "materialize_secret" "example_secret" {
  name  = "pgpass"
  value = data.vault_generic_secret.materialize_password.data["pgpass"]
}
```

In this example, the `vault_generic_secret` data source retrieves a secret from Vault, which is then used as the value for a new `materialize_secret` resource.

You can find examples of using other popular secret stores providers in the
[secret stores
demo](https://github.com/MaterializeInc/demos/tree/main/integrations/terraform/secret-stores).

<!-- mz-docs page: developer-tools/terraform/get-started -->

# Get started with the Materialize provider
Introductory setup with Materialize Terraform provider
The following guide provides an introduction to the Materialize Terraform
provider and setup.

## Terraform provider

The Materialize provider is hosted on the [Terraform provider registry](https://registry.terraform.io/providers/MaterializeInc/materialize/latest).

To use the Materialize provider, you create a new `main.tf` file and add the
required providers:

```hcl
terraform {
  required_providers {
    materialize = {
      source = "MaterializeInc/materialize"
    }
  }
}
```

## Authentication and Configuration

The provider auto-detects your deployment type based on the configuration you
provide:
- **Materialize Cloud**: Use `password` and `default_region`
- **Self-managed**: Use `host`, `username`, `password`, and other connection parameters

> **Warning:** Switching between Materialize Cloud and self-managed configuration **breaks your
> Terraform state file**. Ensure that your initial configuration
> matches your intended deployment type, and do not switch to a
> different deployment type afterward.

**Materialize Cloud:**
### Materialize Cloud

Configure the provider with your [app password](/security/cloud/users-service-accounts/create-service-accounts/)
and region. This provides access to all provider resources, including
organization-level resources (users, SSO, SCIM) and database resources.

To avoid checking secrets into source control, use environment variables for authentication. You have two options:

**Option 1: Using provider environment variables (recommended)**

The provider automatically reads the `MZ_PASSWORD` environment variable:

```shell
export <MZ_PASSWORD>=<app_password>
```

```hcl
provider "materialize" {
  default_region = <region>
  database       = <database>
}
```

**Option 2: Using Terraform input variables**

Use [Terraform environment variables](https://developer.hashicorp.com/terraform/cli/config/environment-variables#tf_var_name) with the `TF_VAR_` prefix:

```shell
export TF_VAR_materialize_password=<app_password>
```

```hcl
variable "materialize_password" {
  type      = string
  sensitive = true
}

provider "materialize" {
  password       = var.materialize_password
  default_region = <region>
  database       = <database>
}
```

#### Creating service accounts

**Minimum requirements:** `terraform-provider-materialize` v0.8.1+

As a best practice, we strongly recommend using [service accounts](/security/users-service-accounts/create-service-accounts/)
to connect external applications to Materialize. To create a
service account, create a new [`materialize_role`](https://registry.terraform.io/providers/MaterializeInc/materialize/latest/docs/resources/role)
and associate it with a new [`materialize_app_password`](https://registry.terraform.io/providers/MaterializeInc/materialize/latest/docs/resources/app_password)
of type `service`. More granular permissions for the service account can then
be configured using [role-based access control (RBAC)](/security/cloud/access-control/#role-based-access-control-rbac).

```hcl
# Create a service user in the aws/us-east-1 region.
resource "materialize_role" "production_dashboard" {
  name   = "svc_production_dashboard"
  region = "aws/us-east-1"
}

# Create an app password for the service user.
resource "materialize_app_password" "production_dashboard" {
  name = "production_dashboard_app_password"
  type = "service"
  user = materialize_role.production_dashboard.name
  roles = ["Member"]
}

# Allow the service user to use the "production_analytics" database.
resource "materialize_database_grant" "database_usage" {
  role_name     = materialize_role.production_dashboard.name
  privilege     = "USAGE"
  database_name = "production_analytics"
  region        = "aws/us-east-1"
}

# Export the user and password for use in the external tool.
output "production_dashboard_user" {
  value = materialize_role.production_dashboard.name
}
output "production_dashboard_password" {
  value = materialize_app_password.production_dashboard.password
}
```

**Self-managed Materialize:**
### Self-managed Materialize

Configure the provider with connection parameters similar to a standard
PostgreSQL connection. Only database resources are available (clusters, sources,
sinks, etc.). Organization-level resources like `materialize_app_password`,
`materialize_user`, and SSO/SCIM resources are not supported.

To avoid checking secrets into source control, use environment variables for authentication. You have two options:

**Option 1: Using provider environment variables (recommended)**

The provider automatically reads configuration from `MZ_*` environment variables:

```shell
export <MZ_PASSWORD>=<password>
export MZ_HOST=<host>
```

> **Warning:** `MZ_HOST` is intended for use with Self-Managed Materialize. If `MZ_HOST` is set,
> the provider connects directly to that host, using `MZ_USERNAME` and
> `MZ_PASSWORD`, instead of connecting through Materialize Cloud.
> If you leave `MZ_HOST` exported and then run Terraform against Materialize
> Cloud, the provider uses your self-managed settings instead, which usually
> results in an `invalid password` error.
> Unset `MZ_HOST` before working with Materialize Cloud.

```hcl
provider "materialize" {
  # Configuration will be read from MZ_HOST, MZ_PORT, MZ_USERNAME,
  # MZ_DATABASE, MZ_PASSWORD, MZ_SSLMODE environment variables
}
```

**Option 2: Using Terraform input variables**

Use [Terraform environment variables](https://developer.hashicorp.com/terraform/cli/config/environment-variables#tf_var_name) with the `TF_VAR_` prefix:

```shell
export TF_VAR_mz_password=<password>
```

```hcl
variable "mz_password" {
  type      = string
  sensitive = true
}

provider "materialize" {
  host     = "materialized"
  port     = 6875
  username = "materialize"
  database = "materialize"
  password = var.mz_password
  sslmode  = "disable"
}
```

#### Provider configuration parameters

| Parameter | Description | Environment Variable | Default |
|-----------|-------------|---------------------|---------|
| `host` | Materialize host address | `MZ_HOST` | - |
| `port` | Materialize port | `MZ_PORT` | `6875` |
| `username` | Database username | `MZ_USERNAME` | `materialize` |
| `database` | Database name | `MZ_DATABASE` | `materialize` |
| `password` | Database password | `MZ_PASSWORD` | - |
| `sslmode` | SSL mode (`disable`, `require`, `verify-ca`, `verify-full`) | `MZ_SSLMODE` | `require` |


<!-- mz-docs page: developer-tools/terraform/manage-cloud-modules -->

# Manage cloud resources
Use Terraform modules to set up cloud resources
The Terraform modules below provide the cloud infrastructure foundation
Materialize needs to communicate with components outside of Materialize itself.
The Materialize provider allows users to manage Materialize resources in the
same programmatic way.

You can use the modules to establish the underlying cloud
resources and then use the Materialize provider to build Materialize-specific
objects. A few use cases are captured in the sections below.

> **Note:** While Materialize offers support for its Terraform provider, Materialize does
> not offer support for these cloud resources modules.

### AWS PrivateLink

To get data into Materialize, you need a connection to allow your data source to
communicate with Materialize. One option to connect securely to Materialize is
AWS PrivateLink.

The [AWS MSK PrivateLink](https://github.com/MaterializeInc/terraform-aws-msk-privatelink), [AWS RDS PrivateLink](https://github.com/MaterializeInc/terraform-aws-rds-privatelink), and [AWS Kafka PrivateLink](https://github.com/MaterializeInc/terraform-aws-kafka-privatelink) modules allow you to manage
your connection to Materialize in a single configuration. The module builds
target groups for brokers, a network load balancer, a TCP listener, and a VPC endpoint within an existing VPC. These AWS resources are necessary components for creating a PrivateLink connection.

The Materialize provider uses [connection resource blocks](https://registry.terraform.io/providers/MaterializeInc/materialize/latest/docs/resources/connection_aws_privatelink) to allow
Materialize to communicate with the PrivateLink endpoint. After you deploy the
module, you can create a new Materialize connection with the AWS resource
information. The configuration below is an example of the Materialize provider,
performing the same necessary steps as the [`CREATE CONNECTION`](/sql/create-connection/#aws-privatelink) statement in SQL:

```hcl
resource "materialize_connection_aws_privatelink" "example_privatelink_connection" {
  service_name       = <vpc_endpoint_service_name>
  availability_zones = [<availability_zone_ids>]
}

resource "materialize_connection_kafka" "example_kafka_connection_multiple_brokers" {
  name = "example_kafka_connection_multiple_brokers"
  kafka_broker {
    broker            = "b-1.hostname-1:9096"
    target_group_port = "9001"
    availability_zone = <availability_zone_id>
    privatelink_connection {
      name          = example_aws_privatelink_connection"
      database_name = "materialize"
      schema_name   = "public"
    }
  }
}
```

For a complete example of the Amazon MSK module with the Materialize provider,
check out this [demo](https://github.com/MaterializeInc/demos/tree/main/integrations/terraform/msk-privatelink). The demo adds the Materialize provider configuration to the modules and bundles the entire deployment into one Terraform configuration file.

### EC2 SSH bastion host

Another method for source connection is to use a bastion host to allow SSH
communication to and from Materialize.

The [EC2 SSH bastion module](https://github.com/MaterializeInc/terraform-aws-ec2-ssh-bastion) allows
you to configure an EC2 instance with security groups and an SSH keypair. These
components form the foundation you need to have a secure, centralized access
point between your data source and Materialize.

After using the module, you can configure the [`materialize_connection_ssh_tunnel`](https://registry.terraform.io/providers/MaterializeInc/materialize/latest/docs/resources/connection_ssh_tunnel)
resource with the module output, allowing Materialize an end-to-end connection
to your source. The provider will configure the same Materialize objects as the
[`CREATE
CONNECTION`](/sql/create-connection/#ssh-tunnel)
statement.

### Amazon RDS for PostgreSQL

You can also create an RDS instance from which you can track and propagate
changes. The [AWS RDS Postgres module](https://github.com/MaterializeInc/terraform-aws-rds-postgres) creates a
VPC, security groups, and an RDS instance in AWS. You can use these AWS
components to create a database with data you want to process in Materialize.

After you run the module, you
can create a secret, connection, and source with the Materialize
provider for an end-to-end connection to this instance as a new source. The
Materialize provider will create these objects just like the [`CREATE
SECRET`](/sql/create-secret/), [`CREATE CONNECTION`](/sql/create-connection/#postgresql), and [`CREATE SOURCE`](/sql/create-source/postgres/) statements in SQL. The
secret, connection, and source resources would be similar to the example
Terraform configuration below with output from the module:

```hcl
resource "materialize_secret" "example_secret" {
  name  = "secret"
  value = <RDSpassword>
}

resource "materialize_connection_postgres" "example_postgres_connection" {
  name = "example_postgres_connection"
  host = <RDShostname>
  port = 5432
  user {
    secret {
      name          = "example"
      database_name = "database"
      schema_name   = "schema"
    }
  }
  password {
    name          = "example"
    database_name = "database"
    schema_name   = "schema"
  }
  database = "example"
}

resource "materialize_source_postgres" "example_source_postgres" {
  name        = "source_postgres"
  schema_name = "schema"
  cluster_name = "quickstart"
  postgres_connection {
    name = "pg_connection"
    # Optional parameters
    # database_name = "postgres"
    # schema_name = "public"
  }
  publication = "mz_source"
  table = {
    "schema1.table_1" = "s1_table_1"
    "schema2_table_1" = "s2_table_1"
  }
}
```

<!-- mz-docs page: developer-tools/terraform/manage-rbac -->

# Manage privileges
Add users, create roles, and assign privileges in Materialize with Terraform
This tutorial walks you through managing roles in Materialize with [Terraform](https://www.terraform.io/). By the end of this tutorial you will:

* Create two new roles in your Materialize
* Apply privileges to the new roles
* Assign a role to a user
* Modify and remove privileges on roles

In this scenario, you are a DevOps engineer responsible for managing your Materialize account with code. You recently hired a new developer who needs privileges in a non-production cluster. You will create specific privileges for the new role that align with your business needs and restrict the developer role from having access to your production cluster.

## Before you begin

* Make sure you have a [Materialize account](https://materialize.com/register/?utm_campaign=General&utm_source=documentation) and already have a password to connect with.

* You should be familiar with setting up a [Terraform project in Materialize](/developer-tools/terraform/).

* Have an understanding of permissions in Materialize.

## Step 1. Create Role

1. You can create a functional role with a set of object-specific privileges.
   First, we will create a role resource in Terraform.

    ```hcl
    resource "materialize_role" "dev_role" {
      name = "dev_role"
    }
    ```

2. We will run Terraform to create this role.

    ```shell
    terraform apply
    ```

    > **Note:** All of the resources in this tutorial can be run with a single terraform apply but we will add and apply resources incrementally to better illustrate grants.

3. Each role you create has default role attributes that determine how they can interact with Materialize objects. Let’s look at the role attributes of the role you created:

    ```mzsql
    SELECT * FROM mz_roles WHERE name = 'dev_role';
    ```

    <p></p>

    ```nofmt
    -[ RECORD 1 ]--+------
    id             | u8
    oid            | 50991
    name           | dev_role
    inherit        | t
    create_role    | f
    create_db      | f
    create_cluster | f
    ```
    Your `id` and `oid` values will look different.

## Step 2. Create example objects

Your `dev_role` has the default system-level permissions and needs object-level privileges. RBAC allows you to apply granular privileges to objects in the SQL hierarchy. Let's create some example objects in the system and determine what privileges the role needs.

1. In the Terraform project we will add a cluster, cluster replica, database, schema and table.

    ```hcl
    resource "materialize_cluster" "cluster" {
      name = "dev_cluster"
    }

    resource "materialize_cluster_replica" "cluster_replica" {
      name         = "devr1"
      cluster_name = materialize_cluster.cluster.name
      size         = "25cc"
    }

    resource "materialize_database" "database" {
      name = "dev_db"
    }

    resource "materialize_schema" "schema" {
      name          = "schema"
      database_name = materialize_database.database.name
    }

    resource "materialize_table" "table" {
      name          = "dev_table"
      schema_name   = materialize_schema.schema.name
      database_name = materialize_database.database.name

      column {
        name = "a"
        type = "int"
      }
      column {
        name     = "b"
        type     = "text"
        nullable = true
      }
    }
    ```

2. We will apply our Terraform project again to create the object resources.

    ```shell
    terraform apply
    ```

3. Now that our resources exist, we can query their privileges before they have been associated with our role created in step 1.

    ```mzsql
    SELECT name, privileges FROM mz_tables WHERE name = 'dev_table';
    ```

    <p></p>

    ```nofmt
    name|privileges
    dev_table|{u1=arwd/u1,u8=arw/u1}
    (1 row)
    ```

Currently, the `dev_role` has no permissions on the table `dev_table`.

## Step 3. Grant privileges on example objects

In this example, let's say your `dev_role` needs the following permissions:

* Read, write, and append privileges on the table
* Usage privileges on the schema
* All available privileges on the database
* Usage and create privileges on the cluster

1. We will add the grant resources to our Terraform project.

    ```hcl
    resource "materialize_table_grant" "dev_role_table_grant" {
      for_each = toset(["SELECT", "INSERT", "UPDATE"])

      role_name     = materialize_role.dev_role.name
      privilege     = each.value
      database_name = materialize_table.table.database_name
      schema_name   = materialize_table.table.schema_name
      table_name    = materialize_table.table.name
    }
    ```

    > **Note:** All of the grant resources are a 1:1 between a specific role, object and privilege. So adding three privileges to the `dev_role` will require three Terraform resources which can can be accomplished with the `for_each` meta-argument.

2. We will run Terraform to grant these privileges on the `dev_table` table.

    ```shell
    terraform apply
    ```

3. We can now check the privileges on our table again

    ```mzsql
    SELECT name, privileges FROM mz_tables WHERE name = 'dev_table';
    ```

    <p></p>

    ```nofmt
    name|privileges
    dev_table|{u1=arwd/u1,u8=arw/u1}
    (1 row)
    ```

4. Now we will include the additional grants for the schema, database and cluster.

    ```hcl
    resource "materialize_schema_grant" "dev_role_schema_grant_usage" {
      role_name     = materialize_role.dev_role.name
      privilege     = "USAGE"
      database_name = materialize_schema.schema.database_name
      schema_name   = materialize_schema.schema.name
    }

    resource "materialize_database_grant" "dev_role_database_grant" {
      for_each = toset(["USAGE", "CREATE"])

      role_name     = materialize_role.dev_role.name
      privilege     = each.value
      database_name = materialize_database.database.name
    }

    resource "materialize_cluster_grant" "dev_role_cluster_grant" {
      for_each = toset(["USAGE", "CREATE"])

      role_name    = materialize_role.dev_role.name
      privilege    = each.value
      cluster_name = materialize_cluster.cluster.name
    }
    ```

5. Run Terraform again to grant these additional privileges on the database, schema and cluster.

    ```shell
    terraform apply
    ```

## Step 4. Assign the role to a user

The dev_role now has the acceptable privileges it needs. Let’s apply this role to a user in your Materialize organization.

1. Include a Terraform resource that grants the role we have created in our Terraform project to a Materialize user.

    ```hcl
    resource "materialize_role_grant" "dev_role_grant_user" {
      role_name   = materialize_role.dev_role.name
      member_name = "<user>"
    }
    ```

2. Apply our Terraform change.

    ```shell
    terraform apply
    ```

3. To review the permissions a roles, you can view the object data:

    ```mzsql
    SELECT name, privileges FROM mz_tables WHERE name = 'dev_table';
    ```

    The output should return the object ID, the level of permission, and the assigning role ID.

    ```nofmt
    name|privileges
    dev_table|{u1=arwd/u1,u8=arw/u1}
    (1 row)
    ```
    In this example, role ID `u1` has append, read, write, and delete privileges on the table. Object ID `u8` is the `dev_role` and has append, read, and write privileges, which were assigned by the `u1` user.

## Step 5. Create a second role

Next, you will create a new role with different privileges to other objects. Then you will apply those privileges to the dev role and alter or drop privileges as needed.

1. Create a second role your Materialize account:

    ```hcl
    resource "materialize_role" "qa_role" {
      name = "qa_role"
    }
    ```

2. Apply `CREATEDB` privileges to the `qa_role`:

    ```hcl
    resource "materialize_grant_system_privilege" "qa_role_system_createdb" {
      role_name = materialize_role.qa_role.name
      privilege = "CREATEDB"
    }
    ```

3. Create a new `qa_db` database:

    ```hcl
    resource "materialize_database" "database" {
      name = "dev_db"
    }
    ```

4. Apply `USAGE` and `CREATE` privileges to the `qa_role` role for the new database:

    ```hcl
    resource "materialize_database_grant" "qa_role_database_grant" {
      for_each = toset(["USAGE", "CREATE"])

      role_name     = materialize_role.qa_role.name
      privilege     = each.value
      database_name = materialize_database.database.name
    }
    ```

## Step 6. Add inherited privileges

Your `dev_role` also needs access to `qa_db`. You can apply these privileges individually or you can choose to grant the `dev_role` the same permissions as the `qa_role`.

1. Add `dev_role` as a member of `qa_role`:

    ```hcl
    resource "materialize_role_grant" "qa_role_grant_dev_role" {
      role_name   = materialize_role.qa_role.name
      member_name = materialize_role.dev_role.name
    }
    ```

2. We will run Terraform to grant these the inherited privileges.

    ```shell
    terraform apply
    ```

3. Review the privileges of `qa_role` and `dev_role`:

   ```mzsql
   SELECT name, privileges FROM mz_databases WHERE name='qa_db';
   ```

   Your output will be similar to the example below:

   ```nofmt
   name|privileges
   qa_db|{u1=UC/u1,u9=UC/u1}
   (1 row)
   ```

   Both `dev_role` and `qa_role` have usage and create access to the `qa_db`. In the next section, you will edit role attributes for these roles and drop privileges.

## Step 7. Revoke privileges

You can revoke certain privileges for each role, even if they are inherited from another role.

1. Remove the resource `materialize_database_grant.qa_role_database_grant_create` from the Terraform project.

2. We will run Terraform to revoke privileges.

    ```shell
    terraform apply
    ```

    Because Terraform is responsible for maintaining the state of our project, removing this grant resource and running an `apply` is the equivalent of running a revoke statement:

    ```mzsql
    REVOKE CREATE ON DATABASE dev_table FROM dev_role;
    ```

## Next steps

To destroy the roles and objects you created, you can remove all resources from your Terraform project. Running a `terraform apply` will `DROP` all objects.

## Related pages

For more information on RBAC in Materialize, review the reference documentation:

* [`GRANT ROLE`](/sql/grant-role/)
* [`CREATE ROLE`](/sql/create-role/)
* [`GRANT PRIVILEGE`](/sql/grant-privilege/)
* [`ALTER ROLE`](/sql/alter-role/)
* [`REVOKE PRIVILEGE`](/sql/revoke-privilege/)
* [`DROP ROLE`](/sql/drop-role/)

<!-- mz-docs page: developer-tools/terraform/manage-resources -->

# Manage Materialize resources with the Materialize provider
The Materialize provider allows you to create several resource types in your
region. Resources correspond to Materialize objects and are configured
with the `resource` block in your Terraform configuration file.

### Create Materialize cluster

For example, to create a new cluster, you would use the `materialize_cluster`
resource:

```hcl
resource "materialize_cluster" "example_cluster" {
  name = "cluster"
}
```

You can find reference documentation for all the resources available in the
Materialize provider in the [Terraform registry](https://registry.terraform.io/providers/MaterializeInc/materialize/latest/docs).

### Retrieve Materialize data sources

The Materialize provider supports several data source types to retrieve
information about your existing Materialize resources. Data sources can return
information about objects defined outside of Terraform and can be used as
variables in your configuration with the `data` block.

For example, to return information about your current clusters, you would use the
`materialize_cluster` data source:

```hcl
data "materialize_cluster" "all" {}
```

This data source returns all cluster names and IDs which you can use as
variables for new resources.

### Import Materialize objects into Terraform state

Terraform allows you to import infrastructure into your current Terraform state
file. Importing objects allows you to keep track of infrastructure created
outside of the Terraform workflow. The `terraform import` command lets you
specify objects you want Terraform to manage and reduces potential configuration
drift. Importing objects allows you to keep related infrastructure in a
Terraform state file and let Terraform manage the configuration.

For instance, if you created a cluster in Materialize and wanted to manage that
resource with Terraform, you would add create resource block for the resource
you want to import in your Terraform configuration:

```hcl
resource "materialize_cluster.<cluster_name> {
    name = <cluster_name>
}
```

Next, you would use the `terraform import` command with the cluster name and ID
to associate the object with the resource block:

```shell
terraform import materialize_cluster.<cluster_name> <CLUSTER_ID>
```

Terraform will then manage the cluster and you can use Terraform as the source of
truth for your Materialize object.

